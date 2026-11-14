"""Utilidades compartidas de carga de corpus y validación antifuga para Multi-LoRA.

Reutiliza sin modificar las fuentes oficiales de Deliverable 3 y Deliverable 4:
- `Corpus` y prompts v6 de `Deliverable 4/prompts/`
- `BLOCKED_UNIT_IDS` (40 unidades D3 + 21 unidades `nuevas_20`), `LEAK_QID_RE` y `UNIT_ID_REF_RE`
- Lógica exacta de `Orquestador.chequear_citas` y `_numero_permitido`
"""

from __future__ import annotations

import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
D4_DIR = REPO_ROOT / "Deliverable 4"
D4_SCRIPTS_DIR = D4_DIR / "scripts"
D4_PROMPTS_DIR = D4_DIR / "prompts"
D3_AGENTES_DIR = REPO_ROOT / "Deliverable 3" / "Deliverable3" / "agentes"
EXP_DIR = REPO_ROOT / "exp_multi_lora"
EXP_DATOS_DIR = EXP_DIR / "datos"

for _p in (D4_SCRIPTS_DIR, D3_AGENTES_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import construir_dataset as cd  # noqa: E402
from dataset_blocks.reglas_v2 import (  # noqa: E402
    BLOCKED_UNIT_IDS,
    DISTRACTORES_LIMPIOS,
    EVAL_40_UNIT_IDS,
    HELDOUT_21_UNIT_IDS,
    LEAK_QID_RE,
    UNIT_ID_REF_RE,
)
from tools import Corpus  # noqa: E402

CITA_ORQ_RE = re.compile(r"(?:RI-FI|RG)-ART-\d{3}|CAL-2026-S[12]-\d{2}")
CITA_COMPLETA_RE = re.compile(r"\[([A-Z0-9-]+)\]")

TIPOS_VALIDOS = ("factual", "numerica", "condicional", "cruce", "premisa_falsa")
DOCS_VALIDOS = ("RI-FI", "RG", "CAL")
ACCIONES_VALIDAS = ("buscar", "traer", "existe", "suficiente")
DESTINOS_VALIDOS = ("fin", "redactor", "recuperador")


def cargar_corpus_limpio() -> tuple[Corpus, dict[str, str]]:
    """Carga `Corpus` completo (para inventarios reales) y el mapa `{uid: texto}`."""
    corpus_obj = Corpus(D3_AGENTES_DIR)
    corpus_by_id = cd.cargar_unidades_corpus(cd.DEFAULT_CORPUS_PATH)
    return corpus_obj, corpus_by_id


def cargar_preguntas_prohibidas() -> list[dict[str, str]]:
    """Carga las 75 preguntas de D3 y las 20 preguntas ciegas de `nuevas_20`."""
    eval_rows = cd.cargar_preguntas_eval(cd.DEFAULT_EVAL_CSV_PATH)
    nuevas_rows = cd.cargar_preguntas_nuevas(cd.DEFAULT_NUEVAS_CSV_PATH)
    return eval_rows + nuevas_rows


def doc_de_unidad(uid: str) -> str:
    """Devuelve 'RI-FI', 'RG' o 'CAL' según el identificador de unidad."""
    if uid.startswith("RI-FI"):
        return "RI-FI"
    if uid.startswith("CAL"):
        return "CAL"
    return "RG"


def extraer_citas_texto(texto: str) -> set[str]:
    """Extrae todos los identificadores de unidad mencionados en corchetes o texto."""
    encontradas = set(UNIT_ID_REF_RE.findall(texto))
    encontradas.update(CITA_COMPLETA_RE.findall(texto))
    return encontradas


def numero_permitido_orquestador(
    n: int,
    sub: str,
    pregunta_o_feedback: str,
    pool_ids: list[str] | set[str],
) -> bool:
    """Replica `_numero_permitido` de `orquestador.py` para traer/existe."""
    texto = f"{pregunta_o_feedback} {sub}"
    if re.search(rf"(?<!\d){n}(?!\d)", texto):
        return True
    return any(re.search(rf"-ART-0*{n}$", uid) for uid in pool_ids)


def chequear_citas_orquestador(
    corpus_obj: Corpus,
    borrador: str,
    evidencia_ids: list[str],
) -> dict[str, Any]:
    """Replica byte a byte `Orquestador.chequear_citas` (`orquestador.py` L320-329)."""
    citados = sorted(set(CITA_ORQ_RE.findall(borrador)))
    en_ev = set(evidencia_ids)
    out = []
    for cid in citados:
        m = re.match(r"(RI-FI|RG)-ART-(\d+)", cid)
        existe = (
            corpus_obj.existe_articulo(m.group(1), int(m.group(2)))
            if m
            else cid in corpus_obj.por_id
        )
        out.append({"id": cid, "existe": bool(existe), "en_evidencia": cid in en_ev})
    return {"citas": out, "sin_citas": not citados}


def _tiene_alta_similitud_eval(
    pregunta: str,
    eval_norm: list[tuple[str, str, set[str]]],
) -> str | None:
    """Comprueba si `pregunta` coincide o es casi idéntica a alguna pregunta de eval."""
    p_norm = cd.normalizar_texto(pregunta)
    if not p_norm:
        return None
    p_toks = cd.tokens_contenido(pregunta)
    for qid, q_norm, q_toks in eval_norm:
        if p_norm == q_norm:
            return f"coincidencia exacta con {qid}"
        if SequenceMatcher(None, p_norm, q_norm).ratio() >= 0.85:
            return f"alta similitud (>=0.85) con {qid}"
        if len(p_toks) >= 5 and len(q_toks) >= 5:
            inter = len(p_toks & q_toks)
            union = len(p_toks | q_toks)
            if union > 0 and (inter / union) >= 0.80:
                return f"solapamiento léxico (>=0.80) con {qid}"
    return None


def auditar_antifuga_agente(
    agente: str,
    registros: list[dict[str, Any]],
    prohibidas: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Valida 0% fuga de unidades bloqueadas, QIDs de eval y preguntas reservadas."""
    if prohibidas is None:
        prohibidas = cargar_preguntas_prohibidas()

    eval_norm = [
        (
            f"{r.get('set', 'eval')}:{r['id']}",
            cd.normalizar_texto(r["pregunta"]),
            cd.tokens_contenido(r["pregunta"]),
        )
        for r in prohibidas
    ]

    errores: list[str] = []
    unidades_usadas: set[str] = set()
    orig_train: set[str] = set()
    orig_val: set[str] = set()

    for reg in registros:
        rid = str(reg.get("id", ""))
        split = reg.get("split")
        orig = str(reg.get("origen_id") or rid)
        if split == "train":
            orig_train.add(orig)
        elif split == "val":
            orig_val.add(orig)

        msgs = reg.get("messages") or []
        if len(msgs) != 2 or msgs[0].get("role") != "user" or msgs[1].get("role") != "assistant":
            errores.append(f"{rid}: formato messages inválido")
            continue

        user_txt = msgs[0]["content"]
        asst_txt = msgs[1]["content"]
        full_txt = f"{user_txt}\n{asst_txt}"

        for uid in extraer_citas_texto(full_txt):
            if uid in BLOCKED_UNIT_IDS:
                errores.append(f"{rid}: contiene unidad bloqueada {uid}")
            unidades_usadas.add(uid)

        for uid in reg.get("unidades_referenciadas", []):
            if uid in BLOCKED_UNIT_IDS:
                errores.append(f"{rid}: unidades_referenciadas contiene bloqueada {uid}")
            unidades_usadas.add(uid)

        m_qid = LEAK_QID_RE.search(full_txt)
        if m_qid:
            errores.append(f"{rid}: posible QID de evaluación en texto: {m_qid.group(0)}")

        pregunta = str(reg.get("pregunta_base") or "")
        if pregunta:
            sim_err = _tiene_alta_similitud_eval(pregunta, eval_norm)
            if sim_err:
                errores.append(f"{rid}: pregunta similar a evaluación ({sim_err})")

    cruce_splits = sorted(orig_train & orig_val)
    if cruce_splits:
        errores.append(f"Fuga train/val en mismo origen_id: {cruce_splits[:5]}")

    if errores:
        raise ValueError(
            f"Fallo antifuga en agente `{agente}` ({len(errores)} errores): "
            + " | ".join(errores[:10])
        )

    return {
        "agente": agente,
        "total": len(registros),
        "unidades_bloqueadas_solapadas": 0,
        "menciones_qid_eval": 0,
        "solapamiento_train_val": 0,
        "unidades_distintas_usadas": len(unidades_usadas),
    }


def escribir_jsonl_lf(path: Path, registros: list[dict[str, Any]]) -> None:
    """Escribe una lista de objetos JSON como líneas JSONL con fin de línea LF."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
