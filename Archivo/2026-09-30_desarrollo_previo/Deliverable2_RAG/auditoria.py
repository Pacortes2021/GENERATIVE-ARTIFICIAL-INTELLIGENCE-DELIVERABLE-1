"""Recuenta una revisión explícita; no confunde coincidencias léxicas con aciertos.

Uso desde la raíz: python -m Deliverable2_RAG.auditoria
Las decisiones están vinculadas por SHA-256 a la pregunta, gold y respuesta.
La revisión semántica fue asistida por IA y requiere validación del equipo.
"""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
CATEGORIES = ("factual", "numerica", "condicional", "cruce", "abstencion")


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fingerprint(question, prediction):
    value = {k: question[k] for k in ("id", "categoria", "pregunta", "gold_dato", "gold_fuente")}
    value["respuesta"] = prediction
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def aligned_predictions(questions, predictions, column):
    if len(questions) != len(predictions):
        raise ValueError("Cantidad de predicciones distinta del conjunto de evaluación")
    if len({q['id'] for q in questions}) != len(questions):
        raise ValueError("IDs duplicados")
    result = {}
    for q, p in zip(questions, predictions):
        for key in ("categoria", "pregunta", "gold_dato", "gold_fuente"):
            if q[key] != p[key]:
                raise ValueError(f"P{q['id']}: {key} no coincide; no se permite alinear por posición a ciegas")
        if "id" in p and q["id"] != p["id"]:
            raise ValueError("IDs desalineados")
        result[q["id"]] = p[column]
    return result


def score(questions, predictions, reviews, system):
    selected = [r for r in reviews if r["sistema"] == system]
    if len(selected) != len(questions) or len({r['id'] for r in selected}) != len(questions):
        raise ValueError(f"Revisión incompleta o duplicada: {system}")
    by_id = {r['id']: r for r in selected}
    totals = defaultdict(lambda: {"aciertos": 0, "n": 0})
    failures = []
    for q in questions:
        r = by_id[q["id"]]
        if r["huella_sha256"] != fingerprint(q, predictions[q["id"]]):
            raise ValueError(f"P{q['id']} {system}: cambió la respuesta o referencia; revisar de nuevo")
        if r["categoria"] != q["categoria"]:
            raise ValueError("Categoría de revisión incorrecta")
        keys = ("dato_completo", "fuentes_completas", "sin_contradicciones", "abstencion_valida")
        if any(r[k] not in {"0", "1", "NA"} for k in keys):
            raise ValueError("Veredicto inválido o pendiente")
        if not r["motivo"].strip():
            raise ValueError("Falta justificar el veredicto")
        if q["categoria"] == "abstencion":
            required = ("abstencion_valida", "sin_contradicciones")
        else:
            required = ("dato_completo", "fuentes_completas", "sin_contradicciones")
        if any(r[k] == "NA" for k in required):
            raise ValueError("Veredicto requerido marcado NA")
        ok = all(r[k] == "1" for k in required)
        totals[q["categoria"]]["n"] += 1
        totals[q["categoria"]]["aciertos"] += int(ok)
        if not ok:
            failures.append(int(q["id"]))
    total = sum(x["aciertos"] for x in totals.values())
    return {"aciertos": total, "n": len(questions), "exactitud_pct": 100 * total / len(questions),
            "categorias": dict(totals), "fallos": failures}


def run(directory=None, review_path=None):
    questions = read_csv(ROOT / "test_set_50.csv")
    if directory is not None:
        directory = Path(directory)
        raw = read_csv(directory / "predicciones.csv")
        if len(raw) != 2 * len(questions) or {r['sistema'] for r in raw} != {'baseline', 'rag'}:
            raise ValueError("Se requieren ambas inferencias para cada pregunta")
        reviews = read_csv(review_path or directory / "revision_pendiente.csv")
        results = {}
        for name in ('baseline', 'rag'):
            rows = [r for r in raw if r['sistema'] == name]
            predictions = aligned_predictions(questions, rows, 'respuesta')
            results[name] = score(questions, predictions, reviews, name)
        results['alcance'] = 'Recuento de la revisión suministrada; conservar responsables, decisiones y trazas.'
        return results
    base = read_csv(ROOT / "resultados_baseline.csv")
    rag = read_csv(HERE / "resultados_rag_qwen3_4b.csv")
    reviews = read_csv(HERE / "revision_historica.csv")
    results = {}
    for name, rows, column in [("baseline", base, "respuesta_modelo"), ("rag", rag, "prediccion_rag")]:
        predictions = aligned_predictions(questions, rows, column)
        results[name] = score(questions, predictions, reviews, name)
    times = [float(r["latencia_seg"]) for r in rag]
    results["latencia_rag_seg"] = {"media": mean(times), "mediana": median(times), "min": min(times), "max": max(times)}
    results["baseline_publicado_e1"] = {"aciertos": sum(r["correcto"] in {"si", "sí"} for r in base), "n": len(base)}
    results["alcance"] = "Revisión asistida por IA de salidas históricas; validar por el equipo. No es nueva inferencia."
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--run", type=Path, help="Carpeta de una corrida nueva")
    parser.add_argument("--review", type=Path, help="CSV de revisión completado")
    args = parser.parse_args()
    if args.review and not args.run:
        parser.error('--review requiere --run')
    result = run(args.run, args.review)
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    print(serialized)
    if args.output:
        args.output.write_text(serialized + "\n", encoding="utf-8")
