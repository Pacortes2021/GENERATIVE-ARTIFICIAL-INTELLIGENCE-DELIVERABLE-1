"""Métricas automáticas estilo RAGAS (fidelidad, relevancia y cobertura) 100% locales."""

from __future__ import annotations

import json
import re
from typing import Any, Callable

import requests

from .buscador import _tokens_clave, normalizar_texto

_GOLD_ID_RE = re.compile(r"[A-Z]+(?:-[A-Z0-9]+)+")


def _extraer_fuentes_gold(gold_fuente: str, dataset: str = "") -> list[str]:
    if not gold_fuente or "inexistente" in gold_fuente.lower():
        return []
    canon = _GOLD_ID_RE.findall(gold_fuente)
    if canon and dataset != "congelado_50":
        return list(dict.fromkeys(canon))
    out: list[str] = []
    doc = "RI-FI" if "RI-FI" in gold_fuente else ("RG" if "RG" in gold_fuente else None)
    for m in re.finditer(r"Art\.\s*(\d+)", gold_fuente):
        if doc:
            out.append(f"{doc}-ART-{int(m.group(1)):03d}")
    return list(dict.fromkeys(out))


def evaluar_caso_determinista(
    caso: dict[str, Any],
    unidades_por_id: dict[str, dict[str, Any]],
    dataset: str = "",
) -> dict[str, Any]:
    """Calcula métricas deterministas de recuperación, citas y respaldo léxico."""
    respuesta = str(caso.get("respuesta", ""))
    fuentes_ids = set(caso.get("fuentes_ids") or [])
    citas_validas = list(caso.get("citas_validas") or [])
    citas_inexistentes = list(caso.get("citas_inexistentes") or [])

    gold_ids = _extraer_fuentes_gold(str(caso.get("gold_fuente", "")), dataset=dataset)
    if gold_ids:
        recall_contexto = sum(1 for g in gold_ids if g in fuentes_ids) / len(gold_ids)
        recall_citas = sum(1 for g in gold_ids if g in citas_validas) / len(gold_ids)
    else:
        recall_contexto = 1.0
        recall_citas = 1.0

    # Groundedness léxico: proporción de palabras clave de la respuesta (sin [ID]) respaldadas en fuentes
    texto_sin_citas = _GOLD_ID_RE.sub(" ", respuesta)
    toks_resp = _tokens_clave(texto_sin_citas)
    toks_fuentes: set[str] = set()
    ids_ref = citas_validas or list(fuentes_ids)
    for uid in ids_ref:
        u = unidades_por_id.get(uid)
        if u:
            toks_fuentes |= _tokens_clave(u.get("texto", ""))
    toks_fuentes |= _tokens_clave(str(caso.get("pregunta", "")))
    respaldo_lexico = (
        len(toks_resp & toks_fuentes) / len(toks_resp) if toks_resp else 0.0
    )

    # Cobertura numérica contra gold_dato (si existe)
    nums_gold = set(re.findall(r"\b\d+(?:[.,]\d+)?\b", normalizar_texto(caso.get("gold_dato", ""))))
    nums_resp = set(re.findall(r"\b\d+(?:[.,]\d+)?\b", normalizar_texto(respuesta)))
    cobertura_numerica = (
        len(nums_gold & nums_resp) / len(nums_gold) if nums_gold else 1.0
    )

    return {
        "id": caso.get("id"),
        "citas_inexistentes": len(citas_inexistentes),
        "recall_contexto": round(recall_contexto, 3),
        "recall_citas": round(recall_citas, 3),
        "respaldo_lexico": round(respaldo_lexico, 3),
        "cobertura_numerica": round(cobertura_numerica, 3),
    }


def _parsear_json_juez(raw: str) -> tuple[dict[str, Any], bool]:
    """Parsea la salida JSON del juez RAGAS y rescata afirmaciones completas si se truncó."""
    try:
        return json.loads(raw), False
    except ValueError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0)), False
            except ValueError:
                pass
    patron_item = re.compile(
        r'\{\s*"texto"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"respaldada"\s*:\s*(true|false)\s*\}',
        re.IGNORECASE,
    )
    afirs: list[dict[str, Any]] = []
    no_resp: list[str] = []
    for texto_raw, flag in patron_item.findall(raw):
        texto = texto_raw.replace('\\"', '"')
        ok = flag.lower() == "true"
        afirs.append({"texto": texto, "respaldada": ok})
        if not ok:
            no_resp.append(texto)
    return {"afirmaciones": afirs, "no_respaldadas": no_resp}, True


def juzgar_fidelidad_llm(
    pregunta: str,
    contexto: str,
    respuesta: str,
    modelo: str = "qwen3:4b-instruct",
    ollama_url: str = "http://localhost:11434",
    cliente_chat: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Juez RAGAS-Faithfulness local: descompone afirmaciones y verifica soporte estricto."""
    prompt = (
        "Actúa como juez estricto de fidelidad (Faithfulness estilo RAGAS). "
        "Resume hasta 6 afirmaciones concretas y breves (máx. 15 palabras c/u) de la RESPUESTA "
        "y evalúa si CADA afirmación está respaldada directamente por la EVIDENCIA.\n"
        "Devuelve SOLO un JSON válido con este formato exacto:\n"
        '{"afirmaciones": [{"texto": "...", "respaldada": true}], "no_respaldadas": ["..."]}\n\n'
        f"PREGUNTA: {pregunta}\n\nEVIDENCIA:\n{contexto}\n\nRESPUESTA:\n{respuesta}"
    )
    payload = {
        "model": modelo,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": False,
        "format": "json",
        "options": {"temperature": 0.0, "num_ctx": 4096, "num_predict": 800, "repeat_penalty": 1.05},
    }
    if cliente_chat is not None:
        data = cliente_chat(payload)
    else:
        resp = requests.post(f"{ollama_url.rstrip('/')}/api/chat", json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()

    raw = str(data.get("message", {}).get("content", "")).strip()
    obj, incompleto = _parsear_json_juez(raw)

    afirs = obj.get("afirmaciones") or []
    total = len(afirs)
    apoyadas = sum(1 for a in afirs if isinstance(a, dict) and a.get("respaldada") is True)
    score = (apoyadas / total) if total else None
    return {
        "faithfulness_score": round(score, 3) if score is not None else None,
        "afirmaciones_totales": total,
        "afirmaciones_respaldadas": apoyadas,
        "no_respaldadas": list(obj.get("no_respaldadas") or []),
        "parse_incompleto": incompleto,
    }


def resumir_evaluacion_benchmark(
    casos: list[dict[str, Any]],
    unidades_por_id: dict[str, dict[str, Any]],
    dataset: str = "",
) -> dict[str, Any]:
    """Agrega métricas RAGAS-deterministas sobre todo un benchmark JSON."""
    if not casos:
        return {"total": 0}
    filas = [evaluar_caso_determinista(c, unidades_por_id, dataset=dataset) for c in casos]
    n = len(filas)
    return {
        "total": n,
        "citas_inexistentes_totales": sum(f["citas_inexistentes"] for f in filas),
        "recall_contexto_promedio": round(sum(f["recall_contexto"] for f in filas) / n, 3),
        "recall_citas_promedio": round(sum(f["recall_citas"] for f in filas) / n, 3),
        "respaldo_lexico_promedio": round(sum(f["respaldo_lexico"] for f in filas) / n, 3),
        "cobertura_numerica_promedio": round(sum(f["cobertura_numerica"] for f in filas) / n, 3),
        "segundos_promedio": round(sum(float(c.get("segundos", 0)) for c in casos) / n, 2),
    }


def main(argv: list[str] | None = None) -> int:
    """Evalúa un JSON de benchmark con métricas deterministas y opcionalmente juez LLM."""
    import argparse
    from pathlib import Path
    from .config import DEFAULT_CORPUS_PATH

    parser = argparse.ArgumentParser(description="Evaluador RAGAS-local para benchmarks UdeC")
    parser.add_argument("--archivo", required=True, type=Path)
    parser.add_argument("--dataset", default="")
    parser.add_argument("--juez-llm", action="store_true")
    parser.add_argument("--max-juez", type=int, default=10)
    args = parser.parse_args(argv)

    corpus = json.loads(DEFAULT_CORPUS_PATH.read_text(encoding="utf-8"))
    unidades = corpus.get("unidades", [])
    por_id = {u["id"]: u for u in (unidades if isinstance(unidades, list) else unidades.values())}

    data = json.loads(args.archivo.read_text(encoding="utf-8"))
    casos = data.get("casos", [])
    resumen = resumir_evaluacion_benchmark(casos, por_id, dataset=args.dataset or data.get("dataset", ""))

    if args.juez_llm and casos:
        muestras = casos[: max(1, args.max_juez)]
        puntajes: list[float] = []
        sin_parse = 0
        for c in muestras:
            ids_ordenados = list(dict.fromkeys(list(c.get("citas_validas") or []) + list(c.get("fuentes_ids") or [])))[:5]
            ctx = "\n\n".join(f"[{uid}] {por_id[uid]['texto']}" for uid in ids_ordenados if uid in por_id)
            j = juzgar_fidelidad_llm(c["pregunta"], ctx, c["respuesta"])
            if j["faithfulness_score"] is not None:
                puntajes.append(float(j["faithfulness_score"]))
            else:
                sin_parse += 1
        resumen["faithfulness_llm_promedio"] = round(sum(puntajes) / len(puntajes), 3) if puntajes else None
        resumen["faithfulness_muestras"] = len(puntajes)
        resumen["faithfulness_sin_parse"] = sin_parse

    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
