"""Construye y valida los 3 datasets antifuga para Multi-LoRA (`enrutador`, `recuperador`, `verificador`).

No modifica `Deliverable 4/` ni lee/escribe fuera de `exp_multi_lora/datos/` (salvo `--datos-dir`).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from antifuga_multi import (  # noqa: E402
    ACCIONES_VALIDAS,
    D4_PROMPTS_DIR,
    DESTINOS_VALIDOS,
    DOCS_VALIDOS,
    EXP_DATOS_DIR,
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
from verificador_bloques import construir_registros_verificador  # noqa: E402


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
        if not isinstance(subs, list) or not (1 <= len(subs) <= 4) or not all(isinstance(s, str) and s.strip() for s in subs):
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
                pool_ids.extend(item["id"] for item in u_obs if isinstance(item, dict) and item.get("id"))
            if not numero_permitido_orquestador(n, ctx["sub"], ctx.get("feedback_verificador") or "", pool_ids):
                raise ValueError(f"{rid}: número {n} viola `_numero_permitido` en {ctx}")
        elif accion == "buscar":
            if not isinstance(args.get("consulta"), str) or not args["consulta"].strip():
                raise ValueError(f"{rid}: consulta vacía en buscar: {args}")
        conteo_acciones[accion] += 1
    return {"splits": dict(conteo_splits), "acciones": dict(conteo_acciones)}


def _validar_esquema_verificador(registros: list[dict[str, Any]]) -> dict[str, Any]:
    conteo_destinos: Counter[str] = Counter()
    conteo_splits: Counter[str] = Counter()
    for reg in registros:
        rid = reg["id"]
        conteo_splits[reg["split"]] += 1
        raw = reg["messages"][1]["content"]
        m = re.match(r"^<pensar>(.+?)</pensar>\s*(\{.+\})$", raw, flags=re.DOTALL)
        if not m:
            raise ValueError(f"{rid}: formato <pensar>...</pensar> + JSON inválido")
        obj = json.loads(m.group(2))
        aprobado = obj.get("aprobado")
        destino = obj.get("destino")
        motivo = obj.get("motivo")
        if not isinstance(aprobado, bool) or destino not in DESTINOS_VALIDOS:
            raise ValueError(f"{rid}: veredicto inválido {obj}")
        if aprobado != (destino == "fin"):
            raise ValueError(f"{rid}: incoherencia aprobado={aprobado} con destino={destino}")
        if not isinstance(motivo, str) or not motivo.strip():
            raise ValueError(f"{rid}: motivo vacío en {obj}")
        conteo_destinos[destino] += 1
    return {"splits": dict(conteo_splits), "destinos": dict(conteo_destinos)}


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


def construir_todos_datasets(
    datos_dir: Path = EXP_DATOS_DIR,
    prompts_dir: Path = D4_PROMPTS_DIR,
    seed: int = 202604,
) -> dict[str, Any]:
    """Construye, audita antifuga y guarda train/val para los 3 agentes nuevos."""
    corpus_obj, corpus_by_id = cargar_corpus_limpio()
    prohibidas = cargar_preguntas_prohibidas()

    p_enr = cd.cargar_prompt_redactor(prompts_dir / "01_enrutador.txt")
    p_rec = cd.cargar_prompt_redactor(prompts_dir / "02_recuperador.txt")
    p_ver = cd.cargar_prompt_redactor(prompts_dir / "04_verificador.txt")

    reg_enr = construir_registros_enrutador(p_enr)
    reg_rec = construir_registros_recuperador(p_rec, corpus_obj, corpus_by_id)
    reg_ver = construir_registros_verificador(p_ver, corpus_obj, corpus_by_id, seed=seed)

    audit_enr = auditar_antifuga_agente("enrutador", reg_enr, prohibidas)
    audit_rec = auditar_antifuga_agente("recuperador", reg_rec, prohibidas)
    audit_ver = auditar_antifuga_agente("verificador", reg_ver, prohibidas)

    stats_enr = _validar_esquema_enrutador(reg_enr)
    stats_rec = _validar_esquema_recuperador(reg_rec)
    stats_ver = _validar_esquema_verificador(reg_ver)

    por_agente = {
        "enrutador": (reg_enr, audit_enr, stats_enr),
        "recuperador": (reg_rec, audit_rec, stats_rec),
        "verificador": (reg_ver, audit_ver, stats_ver),
    }

    resumen: dict[str, Any] = {
        "version": "exp_multi_lora_v1",
        "seed": seed,
        "agentes": {},
    }

    datos_dir.mkdir(parents=True, exist_ok=True)
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

    out_res = datos_dir / "resumen_datasets_multi_lora.json"
    out_res.write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return resumen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Construye datasets antifuga para Enrutador, Recuperador y Verificador.",
    )
    parser.add_argument("--datos-dir", type=Path, default=EXP_DATOS_DIR)
    parser.add_argument("--seed", type=int, default=202604)
    args = parser.parse_args(argv)

    resumen = construir_todos_datasets(datos_dir=args.datos_dir, seed=args.seed)
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
