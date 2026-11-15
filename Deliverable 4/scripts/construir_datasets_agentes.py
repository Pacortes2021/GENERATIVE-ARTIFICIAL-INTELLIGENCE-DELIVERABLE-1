"""Construye y valida los datasets antifuga de `Enrutador` y `Recuperador` en Deliverable 4.

Complementa a `construir_dataset.py` (Redactor) para completar los 3 agentes fine-tuned
del sistema oficial de Deliverable 4 (`enrutador`, `recuperador`, `redactor`), produciendo
también la muestra estratificada de revisión manual para Enrutador y Recuperador.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from antifuga_multi import (  # noqa: E402
    ACCIONES_VALIDAS,
    D4_DATOS_DIR,
    D4_PROMPTS_DIR,
    DOCS_VALIDOS,
    TIPOS_VALIDOS,
    auditar_antifuga_agente,
    cargar_corpus_limpio,
    cargar_preguntas_prohibidas,
    cd,
    escribir_jsonl_lf,
    numero_permitido_orquestador,
)
from enrutador_bloques import construir_registros_enrutador  # noqa: E402
from recuperador_bloques import construir_registros_recuperador  # noqa: E402


def _validar_esquema_enrutador(registros: list[dict[str, Any]]) -> dict[str, Any]:
    conteo_tipos: Counter[str] = Counter()
    conteo_splits: Counter[str] = Counter()
    for reg in registros:
        rid = reg["id"]
        conteo_splits[reg["split"]] += 1
        raw = reg["messages"][1]["content"]
        obj = json.loads(raw)
        if obj.get("tipo") not in TIPOS_VALIDOS:
            raise ValueError(f"{rid}: tipo inválido {obj.get('tipo')}")
        subs = obj.get("sub_consultas")
        if (
            not isinstance(subs, list)
            or not (1 <= len(subs) <= 4)
            or not all(isinstance(s, str) and s.strip() for s in subs)
        ):
            raise ValueError(f"{rid}: sub_consultas inválidas: {subs}")
        docs = obj.get("documentos")
        if not isinstance(docs, list) or not docs or any(d not in DOCS_VALIDOS for d in docs):
            raise ValueError(f"{rid}: documentos inválidos: {docs}")
        conteo_tipos[obj["tipo"]] += 1
    return {"splits": dict(conteo_splits), "tipos": dict(conteo_tipos)}


def _validar_esquema_recuperador(registros: list[dict[str, Any]]) -> dict[str, Any]:
    conteo_acciones: Counter[str] = Counter()
    conteo_splits: Counter[str] = Counter()
    for reg in registros:
        rid = reg["id"]
        conteo_splits[reg["split"]] += 1
        obj = json.loads(reg["messages"][1]["content"])
        accion = obj.get("accion")
        args = obj.get("args")
        if accion not in ACCIONES_VALIDAS or not isinstance(args, dict):
            raise ValueError(f"{rid}: acción inválida {obj}")
        if accion in ("traer", "existe"):
            doc = args.get("doc")
            n = args.get("n")
            if doc not in ("RI-FI", "RG") or not isinstance(n, int):
                raise ValueError(f"{rid}: args inválidos para {accion}: {args}")
            ctx = reg["ctx"]
            pool_ids = list(ctx.get("evidencia_reunida") or [])
            u_obs = ctx.get("ultima_observacion")
            if isinstance(u_obs, list):
                pool_ids.extend(
                    item["id"] for item in u_obs if isinstance(item, dict) and item.get("id")
                )
            if not numero_permitido_orquestador(
                n, ctx["sub"], ctx.get("feedback_verificador") or "", pool_ids
            ):
                raise ValueError(f"{rid}: número {n} viola `_numero_permitido` en {ctx}")
        elif accion == "buscar":
            if not isinstance(args.get("consulta"), str) or not args["consulta"].strip():
                raise ValueError(f"{rid}: consulta vacía en buscar: {args}")
        conteo_acciones[accion] += 1
    return {"splits": dict(conteo_splits), "acciones": dict(conteo_acciones)}


def _limpiar_para_jsonl(reg: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": reg["id"],
        "origen_id": reg["origen_id"],
        "agente": reg["agente"],
        "split": reg["split"],
        "pregunta_base": reg.get("pregunta_base", ""),
        "unidades_referenciadas": reg.get("unidades_referenciadas", []),
        "messages": reg["messages"],
    }


def _cargar_firmas_manuales(firmas_csv_path: Path | None) -> dict[str, dict[str, str]]:
    if firmas_csv_path is None or not firmas_csv_path.is_file():
        return {}
    out: dict[str, dict[str, str]] = {}
    with firmas_csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            sid = str(row.get("sample_id") or "").strip()
            if sid:
                out[sid] = {
                    "revisor": str(row.get("revisor") or "").strip() or "[Pendiente revisor]",
                    "fecha": str(row.get("fecha") or "").strip() or "[YYYY-MM-DD]",
                    "veredicto": str(row.get("veredicto") or "").strip() or "[Pendiente]",
                    "observacion": str(row.get("observacion") or "").strip(),
                }
    return out


def _seleccionar_muestra_enrutador(reg_enr: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Selecciona 10 casos estratificados de Enrutador (2 por cada tipo, 1 train + 1 val)."""
    muestra: list[dict[str, Any]] = []
    for tipo in TIPOS_VALIDOS:
        del_tipo_train = [
            r for r in reg_enr if r["split"] == "train" and json.loads(r["messages"][1]["content"])["tipo"] == tipo
        ]
        del_tipo_val = [
            r for r in reg_enr if r["split"] == "val" and json.loads(r["messages"][1]["content"])["tipo"] == tipo
        ]
        if del_tipo_train:
            muestra.append(del_tipo_train[0])
        if del_tipo_val:
            muestra.append(del_tipo_val[0])
    return muestra


def _seleccionar_muestra_recuperador(reg_rec: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Selecciona 10 casos estratificados de Recuperador cubriendo las 4 acciones y feedback."""
    objetivos = [
        ("suficiente", "train"),
        ("suficiente", "val"),
        ("buscar", "train"),
        ("buscar", "train"),
        ("buscar", "val"),
        ("traer", "train"),
        ("traer", "train"),
        ("traer", "val"),
        ("existe", "train"),
        ("existe", "val"),
    ]
    usados: set[str] = set()
    muestra: list[dict[str, Any]] = []
    for idx, (accion, split) in enumerate(objetivos):
        candidatos = [
            r
            for r in reg_rec
            if r["id"] not in usados
            and r["split"] == split
            and json.loads(r["messages"][1]["content"])["accion"] == accion
        ]
        if candidatos:
            elegido = candidatos[min(idx, len(candidatos) - 1)]
            usados.add(elegido["id"])
            muestra.append(elegido)
    return muestra


def generar_muestra_manual_agentes(
    reg_enr: list[dict[str, Any]],
    reg_rec: list[dict[str, Any]],
    output_md: Path,
    firmas_csv_path: Path | None = None,
) -> list[str]:
    """Escribe la muestra estratificada de 20 casos (10 Enrutador + 10 Recuperador)."""
    firmas = _cargar_firmas_manuales(firmas_csv_path)
    sel_enr = _seleccionar_muestra_enrutador(reg_enr)
    sel_rec = _seleccionar_muestra_recuperador(reg_rec)
    todos = sel_enr + sel_rec

    lineas: list[str] = [
        "# Muestra de Revisión Manual — Enrutador y Recuperador D4 (20 casos)",
        "",
        "Complementa la muestra de **30 casos del Redactor** en [`MUESTRA_REVISION_MANUAL.md`](MUESTRA_REVISION_MANUAL.md) para completar **50 casos revisables manualmente** a través de los 3 agentes fine-tuneados de Deliverable 4.",
        "",
        "- **Enrutador (`10` casos):** 2 por cada `tipo` (`factual`, `numerica`, `condicional`, `cruce`, `premisa_falsa`; 1 `train` + 1 `val`).",
        "- **Recuperador (`10` casos):** cobertura estratificada de las 4 acciones (`suficiente`, `buscar`, `traer`, `existe`) en `train` y `val`.",
        "- **Antifuga:** 0 unidades bloqueadas (`D3` + `nuevas_20`), 0 menciones a QIDs de evaluación y 0 solapamiento train/val.",
        "",
        "## Registro de Verificación Humana (20 casos)",
        "",
        "| # | ID | Agente / Categoría / Split | Revisor | Fecha | Resultado | Observaciones |",
        "|---|---|---|---|:---:|---|---|",
    ]

    for idx, reg in enumerate(todos, start=1):
        sid = reg["id"]
        split = reg["split"]
        asst = json.loads(reg["messages"][1]["content"])
        cat = asst.get("tipo") or asst.get("accion") or "-"
        f = firmas.get(sid, {})
        rev = f.get("revisor", "[Pendiente revisor]")
        fec = f.get("fecha", "[YYYY-MM-DD]")
        ver = f.get("veredicto", "[Pendiente]")
        obs = f.get("observacion", "")
        obs_cell = f" {obs} " if obs else " "
        lineas.append(
            f"| {idx:02d} | `{sid}` | `{reg['agente']}` / `{cat}` / `{split}` | {rev} | {fec} | {ver} |{obs_cell}|"
        )

    lineas.extend(
        [
            "",
            "Criterios de revisión:",
            "1. **Enrutador:** `tipo` coherente con la pregunta, `sub_consultas` mínimas sin redundancia y `documentos` correctos (`RI-FI`, `RG`, `CAL`).",
            "2. **Recuperador:** usa `suficiente` cuando la evidencia ya cubre todas las sub-consultas; solo invoca `traer`/`existe` sobre artículos permitidos; consulta léxica limpia cuando usa `buscar`.",
            "",
            "---",
        ]
    )

    for idx, reg in enumerate(todos, start=1):
        sid = reg["id"]
        asst_raw = reg["messages"][1]["content"]
        asst_obj = json.loads(asst_raw)
        cat = asst_obj.get("tipo") or asst_obj.get("accion") or "-"
        lineas.append("")
        lineas.append(f"## {idx:02d}. `{sid}` — `{reg['agente']}` | `{cat}` | split `{reg['split']}`")
        if reg.get("pregunta_base"):
            lineas.append(f"**Pregunta base:** {reg['pregunta_base']}")
        if reg.get("unidades_referenciadas"):
            lineas.append(
                f"**Unidades referenciadas:** {', '.join(f'`{u}`' for u in reg['unidades_referenciadas'])}"
            )
        user_txt = reg["messages"][0]["content"]
        contexto_usr = user_txt.split("\n\n")[-1]
        lineas.extend(
            [
                "",
                "<details>",
                "<summary>Entrada al agente (extracto contextual del prompt)</summary>",
                "",
                "```text",
                contexto_usr.strip(),
                "```",
                "",
                "</details>",
                "",
                f"**Salida esperada (`assistant`):**",
                "```json",
                json.dumps(asst_obj, ensure_ascii=False, indent=2),
                "```",
            ]
        )

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lineas).rstrip() + "\n", encoding="utf-8")
    return [r["id"] for r in todos]


def construir_datasets_agentes_d4(
    datos_dir: Path = D4_DATOS_DIR,
    prompts_dir: Path = D4_PROMPTS_DIR,
    seed: int = 202604,
) -> dict[str, Any]:
    """Construye, audita antifuga y guarda train/val para `enrutador` y `recuperador` en D4."""
    corpus_obj, corpus_by_id = cargar_corpus_limpio()
    prohibidas = cargar_preguntas_prohibidas()

    p_enr = cd.cargar_prompt_redactor(prompts_dir / "01_enrutador.txt")
    p_rec = cd.cargar_prompt_redactor(prompts_dir / "02_recuperador.txt")

    reg_enr = construir_registros_enrutador(p_enr)
    reg_rec = construir_registros_recuperador(p_rec, corpus_obj, corpus_by_id)

    audit_enr = auditar_antifuga_agente("enrutador", reg_enr, prohibidas)
    audit_rec = auditar_antifuga_agente("recuperador", reg_rec, prohibidas)

    stats_enr = _validar_esquema_enrutador(reg_enr)
    stats_rec = _validar_esquema_recuperador(reg_rec)

    por_agente = {
        "enrutador": (reg_enr, audit_enr, stats_enr),
        "recuperador": (reg_rec, audit_rec, stats_rec),
    }

    datos_dir.mkdir(parents=True, exist_ok=True)
    resumen: dict[str, Any] = {
        "version": "deliverable4_3_agentes_v1",
        "seed": seed,
        "agentes": {},
    }

    for agente, (regs, audit, stats) in por_agente.items():
        train_rows = [_limpiar_para_jsonl(r) for r in regs if r["split"] == "train"]
        val_rows = [_limpiar_para_jsonl(r) for r in regs if r["split"] == "val"]
        escribir_jsonl_lf(datos_dir / f"{agente}_train.jsonl", train_rows)
        escribir_jsonl_lf(datos_dir / f"{agente}_val.jsonl", val_rows)
        resumen["agentes"][agente] = {
            "train": len(train_rows),
            "val": len(val_rows),
            "total": len(regs),
            "antifuga": audit,
            "distribucion": stats,
        }

    # Integrar resumen del Redactor desde dataset_resumen.json si existe
    red_res_path = datos_dir / "dataset_resumen.json"
    if red_res_path.is_file():
        red_res = json.loads(red_res_path.read_text(encoding="utf-8"))
        splits_red = red_res.get("splits") or {}
        resumen["agentes"]["redactor"] = {
            "train": splits_red.get("train", 180),
            "val": splits_red.get("val", 30),
            "total": red_res.get("total_ejemplos", 210),
            "fuente": "dataset_resumen.json",
        }

    total_train = sum(v["train"] for v in resumen["agentes"].values())
    total_val = sum(v["val"] for v in resumen["agentes"].values())
    resumen["totales_3_agentes"] = {
        "train": total_train,
        "val": total_val,
        "total": total_train + total_val,
    }

    firmas_csv = datos_dir / "revision_manual_firmas_agentes.csv"
    muestra_ids = generar_muestra_manual_agentes(
        reg_enr,
        reg_rec,
        datos_dir / "MUESTRA_REVISION_MANUAL_ENRUTADOR_RECUPERADOR.md",
        firmas_csv_path=firmas_csv if firmas_csv.is_file() else None,
    )
    resumen["muestra_manual_enrutador_recuperador_ids"] = muestra_ids

    out_res = datos_dir / "resumen_datasets_3_agentes.json"
    out_res.write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return resumen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Construye datasets antifuga para Enrutador y Recuperador en Deliverable 4.",
    )
    parser.add_argument("--datos-dir", type=Path, default=D4_DATOS_DIR)
    parser.add_argument("--seed", type=int, default=202604)
    args = parser.parse_args(argv)

    resumen = construir_datasets_agentes_d4(datos_dir=args.datos_dir, seed=args.seed)
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
