"""Contrasta una corrida terminada con la pauta; no modifica la recuperación."""
import argparse
from pathlib import Path

from probar_recuperacion import ROOT, read, require, sha, write


def coverage(groups, unit_ids):
    require(bool(groups) and all(groups), "La evidencia local requiere grupos no vacíos")
    recovered = set(unit_ids)
    hits = [bool(recovered.intersection(group)) for group in groups]
    return {"completa": all(hits), "grupos_cubiertos": sum(hits), "total_grupos": len(hits),
            "grupos_faltantes": [g for g, found in zip(groups, hits) if not found]}


def evaluate(run, rubric):
    require(run["fuentes_sha256"]["corpus"] == rubric["corpus_sha256"], "La pauta y la corrida usan corpus distintos")
    require([c["id"] for c in run["casos"]] == [c["id"] for c in rubric["casos"]], "Casos distintos/desordenados")
    cases = []
    k = run["configuracion"]["k_fragmentos"]
    for found, expected in zip(run["casos"], rubric["casos"]):
        require(found["pregunta"] == expected["pregunta"], "Cambió la pregunta")
        units = [c["unidad_id"] for c in found["contextos"]]
        require(set(units) == {r["unidad_id"] for r in found["ranking"][:k]}, "Contexto no coincide con ranking top-k")
        record = {"id": found["id"], "pregunta": found["pregunta"], "categoria": found["categoria"],
                  "tipo": expected["tipo"], "unidades_recuperadas": units, "caracteres_contexto": found["caracteres_contexto"]}
        if expected["tipo"] == "ausencia_global":
            record.update(estado="pendiente_verificacion_global", motivo=expected["motivo"], completa=None)
        else:
            result = coverage(expected["grupos"], units)
            positions = [{"alternativas": group, "primer_fragmento_posicion": next((r["posicion"] for r in found["ranking"] if r["unidad_id"] in group), None)} for group in expected["grupos"]]
            record.update(**result, grupos_esperados=expected["grupos"], posiciones_evidencia=positions,
                          estado="cobertura_completa" if result["completa"] else "cobertura_incompleta")
        cases.append(record)
    local = [c for c in cases if c["tipo"] == "evidencia_local"]
    require(bool(local), "No hay preguntas con evidencia local evaluable")
    metrics = []
    for cutoff in sorted({1, 3, 5, 10, k}):
        successes = 0
        for found, expected in zip(run["casos"], rubric["casos"]):
            if expected["tipo"] != "evidencia_local":
                continue
            successes += coverage(expected["grupos"], [r["unidad_id"] for r in found["ranking"][:cutoff]])["completa"]
        metrics.append({"k_fragmentos": cutoff, "preguntas_con_toda_evidencia_pauta": successes,
                        "preguntas_evaluables": len(local), "porcentaje": round(100 * successes / len(local), 2)})
    return {"version": 1, "alcance": "Cobertura de fuentes de la pauta. No mide exactitud de respuestas ni demuestra suficiencia de todas las fuentes alternativas.",
            "configuracion": run["configuracion"], "resumen": {"preguntas": len(cases), "evaluables_cobertura_local": len(local),
            "cobertura_completa": sum(c["completa"] for c in local), "cobertura_incompleta": sum(not c["completa"] for c in local),
            "pendientes_verificacion_global": len(cases) - len(local),
            "promedio_caracteres_contexto": round(sum(c["caracteres_contexto"] for c in cases) / len(cases)),
            "max_caracteres_contexto": max(c["caracteres_contexto"] for c in cases)},
            "diagnostico_por_k": metrics, "casos": cases}


def markdown(report):
    s = report["resumen"]
    k = report["configuracion"]["k_fragmentos"]
    text = ["# Primera prueba de recuperación E5", "",
            f"Se recuperaron los **{k} fragmentos** más cercanos de cada pregunta, se expandieron a su unidad completa y se eliminaron duplicados. No se ejecutó Qwen ni se reescribieron consultas.", "",
            f"**{s['cobertura_completa']}/{s['evaluables_cobertura_local']}** preguntas tienen todas las fuentes de la pauta en el contexto; **{s['cobertura_incompleta']}** tienen cobertura incompleta. Otras **{s['pendientes_verificacion_global']}** requieren verificar ausencia en el inventario completo y quedan pendientes.", "",
            "Esta es una métrica de cobertura de fuentes, no el porcentaje de respuestas correctas. La pauta no enumera todas las alternativas válidas: una fuente no recuperada merece revisión, no convierte automáticamente una respuesta futura en incorrecta.", "",
            f"Contexto medio: {s['promedio_caracteres_contexto']} caracteres; máximo: {s['max_caracteres_contexto']}. Aún no se han medido tokens con Qwen.", "",
            "## Diagnóstico por cantidad de fragmentos", "",
            "El valor principal k=5 se fijó antes de revisar resultados. Los otros cortes muestran sensibilidad al presupuesto; no se eligió después el que más aciertos daba.", "",
            "| Fragmentos | Cobertura completa | Porcentaje sobre 45 preguntas evaluables |", "|---:|---:|---:|"]
    for row in report["diagnostico_por_k"]:
        text.append(f"| {row['k_fragmentos']} | {row['preguntas_con_toda_evidencia_pauta']}/{row['preguntas_evaluables']} | {row['porcentaje']}% |")
    text += ["", "## Casos que requieren revisión", ""]
    for c in report["casos"]:
        if c["completa"] is True:
            continue
        text += [f"### P{c['id']:02}: {c['pregunta']}", "", "Recuperado: " + ", ".join(c["unidades_recuperadas"]) + ".", ""]
        if c["completa"] is None:
            text += [c["motivo"], ""]
        else:
            text += ["Fuentes de la pauta ausentes: " + "; ".join(" o ".join(g) for g in c["grupos_faltantes"]) + ".", ""]
            for g in c["posiciones_evidencia"]:
                text.append("- " + " o ".join(g["alternativas"]) + f": primer fragmento en posición {g['primer_fragmento_posicion']}.")
            text.append("")
    text += ["## Las 50 preguntas", "", "| Nº | Pregunta | Cobertura de pauta | Unidades recuperadas |", "|---:|---|---|---|"]
    for c in report["casos"]:
        label = "Completa" if c["completa"] is True else "Incompleta" if c["completa"] is False else "Pendiente: ausencia global"
        text.append(f"| {c['id']} | {c['pregunta']} | {label} | {', '.join(c['unidades_recuperadas'])} |")
    text += ["", "El texto íntegro de cada contexto y todos los rankings están en `recuperacion.json`. Los hashes de fuentes y vectores están en `manifiesto.json`. Las etiquetas de este reporte se calcularon por pertenencia de IDs; no son juicios manuales sobre respuestas.", ""]
    return "\n".join(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corrida", type=Path, default=Path(__file__).parent / "resultados/e5_top5_v1")
    parser.add_argument("--pauta", type=Path, default=Path(__file__).parent / "pauta_evidencia.json")
    args = parser.parse_args()
    manifest = read(args.corrida / "manifiesto.json")
    for name, expected in manifest["artefactos_sha256"].items():
        require(sha(args.corrida / name) == expected, "Se modificó un artefacto de la corrida: " + name)
    rubric = read(args.pauta)
    require(rubric["referencias_sha256"] == sha(ROOT / "Deliverable2/evaluacion/referencias.json"), "Cambió la pauta de respuestas")
    run = read(args.corrida / "recuperacion.json")
    report = evaluate(run, rubric)
    report["procedencia_sha256"] = {"corrida": sha(args.corrida / "recuperacion.json"), "pauta": sha(args.pauta), "script_evaluador": sha(__file__)}
    write(args.corrida / "evaluacion_recuperacion.json", report)
    (args.corrida / "REPORTE.md").write_text(markdown(report), encoding="utf-8")
    print(report["resumen"])


if __name__ == "__main__":
    main()
