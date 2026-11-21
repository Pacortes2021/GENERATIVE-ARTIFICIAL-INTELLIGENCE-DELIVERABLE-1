"""Validación estricta antifuga de datos y consistencia de esquemas para fine-tuning SFT."""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from ..benchmark import cargar_preguntas

# 40 unidades usadas en D3 (`congelado_50` + `dificil_25`) + 21 reservadas para `nuevas_20` + vecinas cruzadas
EVAL_40_UNIT_IDS: frozenset[str] = frozenset(
    {
        "CAL-2026-S1-02",
        "CAL-2026-S1-03",
        "CAL-2026-S2-01",
        "CAL-2026-S2-02",
        "CAL-2026-S2-03",
        "CAL-2026-S2-04",
        "CAL-2026-S2-05",
        "CAL-2026-S2-09",
        "RG-ART-016",
        "RG-ART-023",
        "RG-ART-024",
        "RG-ART-026",
        "RG-ART-028",
        "RG-ART-029",
        "RG-ART-030",
        "RG-ART-031",
        "RG-ART-049",
        "RI-FI-ART-005",
        "RI-FI-ART-008",
        "RI-FI-ART-009",
        "RI-FI-ART-010",
        "RI-FI-ART-011",
        "RI-FI-ART-012",
        "RI-FI-ART-013",
        "RI-FI-ART-014",
        "RI-FI-ART-016",
        "RI-FI-ART-017",
        "RI-FI-ART-018",
        "RI-FI-ART-019",
        "RI-FI-ART-020",
        "RI-FI-ART-021",
        "RI-FI-ART-022",
        "RI-FI-ART-023",
        "RI-FI-ART-025",
        "RI-FI-ART-026",
        "RI-FI-ART-027",
        "RI-FI-ART-029",
        "RI-FI-ART-030",
        "RI-FI-ART-031",
        "RI-FI-ART-034",
    }
)

HELDOUT_21_UNIT_IDS: frozenset[str] = frozenset(
    {
        "CAL-2026-S1-07",
        "CAL-2026-S1-08",
        "CAL-2026-S2-06",
        "CAL-2026-S2-07",
        "RG-ART-004",
        "RG-ART-005",
        "RG-ART-012",
        "RG-ART-017",
        "RG-ART-018",
        "RG-ART-036",
        "RG-ART-046",
        "RG-ART-047",
        "RG-ART-051",
        "RG-ART-053",
        "RG-ART-056",
        "RG-ART-057",
        "RG-ART-059",
        "RG-TRANS-002",
        "RI-FI-ART-003",
        "RI-FI-ART-006",
        "RI-FI-ART-035",
    }
)

# Unidades hermanas con solapamiento directo en respuestas/citas observadas en los 95 casos
EXTRA_ISOLATION_UNIT_IDS: frozenset[str] = frozenset(
    {
        "RG-ART-001",
        "RG-ART-002",
        "RG-ART-022",
        "RG-ART-034",
        "RG-ART-035",
    }
)

BLOCKED_UNIT_IDS: frozenset[str] = EVAL_40_UNIT_IDS | HELDOUT_21_UNIT_IDS | EXTRA_ISOLATION_UNIT_IDS

_UNIT_ID_RE = re.compile(
    r"\b(?:RI-FI|RG)-ART-\d{3}(?:-DEF-\d{2})?|RG-TRANS-\d{3}|CAL-2026-S[12]-\d{2}|PDF-[A-Z0-9]+-P\d{2}-\d{2}\b"
)
_PDF_CITE_RE = re.compile(r"\[([A-Z]+(?:-[A-Z0-9]+)+)\]")
_HERRAMIENTAS_VALIDAS = {
    "buscar_reglamento",
    "leer_articulo",
    "existe_articulo",
    "ver_calendario",
    "calcular",
    "dias_entre",
}


def cargar_preguntas_evaluacion_95() -> list[dict[str, str]]:
    """Reúne las 95 preguntas reservadas de evaluación (congelado_50, dificil_25, nuevas_20)."""
    filas: list[dict[str, str]] = []
    for ds in ("congelado_50", "dificil_25", "nuevas_20"):
        for r in cargar_preguntas(ds):
            filas.append({"dataset": ds, "id": r["id"], "pregunta": r["pregunta"]})
    return filas


def _serializar_mensajes_para_auditoria(messages: list[dict[str, Any]]) -> str:
    return json.dumps(messages, ensure_ascii=False)


def validar_registro_sft(
    registro: dict[str, Any],
    preguntas_95: list[dict[str, str]] | None = None,
    umbral_similitud: float = 0.72,
) -> list[str]:
    """Devuelve lista de errores si el ejemplo filtra unidades bloqueadas, preguntas o formato."""
    errores: list[str] = []
    rid = str(registro.get("id", "<sin-id>"))
    msgs = registro.get("messages") or []
    if len(msgs) < 3 or msgs[0].get("role") != "system" or msgs[-1].get("role") != "assistant":
        errores.append(f"{rid}: estructura de conversación inválida (debe iniciar system y terminar assistant)")
        return errores

    blob_sin_sistema = _serializar_mensajes_para_auditoria(msgs[1:])
    ids_en_blob = set(_UNIT_ID_RE.findall(blob_sin_sistema))
    fugas = sorted(ids_en_blob & BLOCKED_UNIT_IDS)
    if fugas:
        errores.append(f"{rid}: fuga de unidades bloqueadas {fugas}")

    # Validar tool_calls contra el esquema oficial
    for m in msgs:
        if m.get("role") == "assistant" and m.get("tool_calls"):
            for tc in m["tool_calls"]:
                fn = tc.get("function", {})
                nombre = fn.get("name")
                args = fn.get("arguments")
                if nombre not in _HERRAMIENTAS_VALIDAS:
                    errores.append(f"{rid}: tool_call desconocida '{nombre}'")
                if not isinstance(args, dict):
                    errores.append(f"{rid}: arguments en tool_call '{nombre}' debe ser dict JSON")

    # Verificar que toda cita [ID] generada tras el último turno `user` pertenezca a evidencia visible
    ultimo_user_idx = max((i for i, m in enumerate(msgs) if m.get("role") == "user"), default=0)
    evidencia_texto = "\n".join(
        str(m.get("content", "")) for m in msgs[: ultimo_user_idx + 1] if m.get("role") in {"user", "tool"}
    ) + "\n" + "\n".join(
        str(m.get("content", "")) for m in msgs[ultimo_user_idx + 1 :] if m.get("role") == "tool"
    )
    ids_visibles = set(_PDF_CITE_RE.findall(evidencia_texto)) | set(_UNIT_ID_RE.findall(evidencia_texto))
    for m in msgs[ultimo_user_idx + 1 :]:
        if m.get("role") == "assistant" and m.get("content"):
            citas_resp = set(_PDF_CITE_RE.findall(str(m["content"])))
            for cid in citas_resp:
                if cid not in ids_visibles:
                    errores.append(f"{rid}: cita [{cid}] no respaldada por evidencia del diálogo")

    # Similitud contra las 95 preguntas de evaluación
    if preguntas_95:
        for m in msgs:
            if m.get("role") != "user":
                continue
            q_txt = str(m.get("content", "")).split("\n\nContexto", 1)[0].split("\n\nVerificación", 1)[0].strip().lower()
            if len(q_txt) < 12:
                continue
            for p95 in preguntas_95:
                sim = SequenceMatcher(None, q_txt, p95["pregunta"].strip().lower()).ratio()
                if sim >= umbral_similitud:
                    errores.append(
                        f"{rid}: pregunta demasiado similar ({sim:.2f}) a {p95['dataset']}:{p95['id']}"
                    )
                    break

    return errores


def validar_dataset_completo(
    registros: list[dict[str, Any]],
    preguntas_95: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Audita todos los registros train/val asegurando 0 fugas y partición disjunta."""
    p95 = preguntas_95 if preguntas_95 is not None else cargar_preguntas_evaluacion_95()
    errores_totales: list[str] = []
    por_split: dict[str, int] = {}
    por_cat: dict[str, int] = {}
    preguntas_por_split: dict[str, set[str]] = {"train": set(), "val": set()}

    for r in registros:
        errs = validar_registro_sft(r, preguntas_95=p95)
        errores_totales.extend(errs)
        sp = str(r.get("split", "train"))
        cat = str(r.get("categoria", "desconocida"))
        por_split[sp] = por_split.get(sp, 0) + 1
        por_cat[cat] = por_cat.get(cat, 0) + 1
        for m in r.get("messages", []):
            if m.get("role") == "user":
                q_limpia = str(m.get("content", "")).split("\n\n", 1)[0].strip().lower()
                if sp in preguntas_por_split and q_limpia:
                    preguntas_por_split[sp].add(q_limpia)

    solape = sorted(preguntas_por_split["train"] & preguntas_por_split["val"])
    if solape:
        errores_totales.append(f"Solape de preguntas entre train y val: {len(solape)} ({solape[:2]})")

    return {
        "total": len(registros),
        "ok": len(errores_totales) == 0,
        "errores": errores_totales,
        "por_split": por_split,
        "por_categoria": por_cat,
    }
