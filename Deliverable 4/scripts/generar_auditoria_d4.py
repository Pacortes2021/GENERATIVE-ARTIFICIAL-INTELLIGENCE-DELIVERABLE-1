"""Genera la auditoría estricta de Deliverable 4 y empaqueta los casos de fallo.

Contrastando las 75 salidas evaluadas en `Deliverable 4/evaluacion/` contra
`corpus.json`, la pauta oficial (`Deliverable 3/paquete_25_dificiles/LEEME_PAUTA.md`)
y los veredictos históricos de D3 (`veredictos_exportados.json`), este script
produce de forma determinista y verificable:

- `resultados_agentes_D4_auditados.csv` (las 75 filas con `correcto` en `{0, 1}`)
- `auditoria_D4.json` (resumen global, desglose por categoría/transición, telemetría,
  aislamiento LoRA y auditoría de la comparativa pareada Base vs Fine-tuned)
- `casos_fallo_y_regresion.json` (trazas completas y diagnóstico causal de los
  fallos persistentes, regresiones inducidas por el Verificador base y desvíos P01)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DELIVERABLE4_DIR = REPO_ROOT / "Deliverable 4"
EVAL_DIR = DELIVERABLE4_DIR / "evaluacion"
DEFAULT_CORPUS_PATH = (
    REPO_ROOT / "Deliverable 3" / "Deliverable3" / "agentes" / "corpus.json"
)
DEFAULT_D3_VEREDICTOS_PATH = (
    REPO_ROOT / "Deliverable 3" / "auditoria" / "veredictos_exportados.json"
)
DEFAULT_D3_CSV_PATH = (
    REPO_ROOT
    / "Deliverable 3"
    / "Deliverable3"
    / "resultados_v6"
    / "resultados_agentes_D3.csv"
)
DEFAULT_DIAGNOSTICO_D3_PATH = (
    DELIVERABLE4_DIR / "diagnostico" / "diagnostico_d3.json"
)

CITE_RE = re.compile(r"\[([A-Z0-9-]+)\]")

# Fallos estrictos según LEEME_PAUTA.md (incluye Regla 3 / precedente P01).
FALLOS_ESTRICTOS_D4: dict[str, dict[str, Any]] = {
    "congelado_50:6": {
        "tipo": "cita_invalida_fuera_de_evidencia",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "El dato (al menos una semana) es correcto, pero cita tres veces [RG-ART-010] "
            "(sesiones del Consejo de Carrera, ni siquiera presente en fuentes_traidas) "
            "en lugar de [RI-FI-ART-010], que sí estaba en evidencia."
        ),
    },
    "congelado_50:7": {
        "tipo": "mezcla_condiciones_p01",
        "solo_condicion_p01": True,
        "causa_raiz": "redactor",
        "motivo": (
            "La respuesta principal es correcta [RI-FI-ART-016], pero Condiciones agrega "
            "que quienes están en Baja por no Inscripción pueden apelar al Vicedecano y al Decano "
            "[RG-ART-030]; en RG-ART-030 la apelación al Decano corresponde a Baja Académica, "
            "no a Baja por no Inscripción (Regla 3 / precedente H12)."
        ),
    },
    "congelado_50:10": {
        "tipo": "regla_mal_interpretada",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "Responde 'No' pero restringe falsamente la prohibición de Primer Año Común "
            "a 'durante las cuatro primeras semanas', malinterpretando [RI-FI-ART-022] "
            "(el plazo de 4 semanas rige para otras carreras; Primer Año Común no puede convalidar)."
        ),
    },
    "congelado_50:31": {
        "tipo": "mezcla_cita_condiciones_p01",
        "solo_condicion_p01": True,
        "causa_raiz": "redactor",
        "motivo": (
            "La respuesta principal acierta con [RI-FI-ART-034], pero Condiciones atribuye "
            "a [RI-FI-ART-002] la frase deformada 'y no se concilia directamente con él', "
            "proveniente de [RI-FI-ART-034] (Regla 3 / precedente P01)."
        ),
    },
    "congelado_50:36": {
        "tipo": "cambio_id_cita_p01",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "Corrige el contenido respecto a D3 al explicitar las excepciones al mínimo de "
            "8 créditos, pero atribuye tanto el mínimo de 8 créditos como sus excepciones "
            "a [CAL-2026-S2-04] (Término de Clases) en vez de [RI-FI-ART-008]."
        ),
    },
    "dificil_25:H02": {
        "tipo": "afirmacion_extra_mal_citada_p01",
        "solo_condicion_p01": True,
        "causa_raiz": "redactor",
        "motivo": (
            "Los promedios 4,2 y 5,0 son correctos [RI-FI-ART-018] [RI-FI-ART-019], "
            "pero Condiciones añade presentar la solicitud en el período de Dirección de "
            "Docencia en UDARAE citando solo [RI-FI-ART-018] [RI-FI-ART-019], omitiendo "
            "[RG-ART-054] / [RG-ART-055] que sí estaban en fuentes_traidas (precedente P01)."
        ),
    },
    "dificil_25:H03": {
        "tipo": "recuperacion_incompleta_y_sobreconfianza",
        "solo_condicion_p01": False,
        "causa_raiz": "recuperador_y_redactor",
        "motivo": (
            "Fallo persistente D1–D4: CAL-2026-S2-02 (inicio S2, 10 ago) no entra al top-6 del "
            "Recuperador (desplazado por CAL-2026-S2-04); en ciclo 3 el Redactor calcula 98 días "
            "entre 04 sep [CAL-2026-S2-03] y 11 dic [CAL-2026-S2-04] en lugar de abstenerse o "
            "reportar 25 días, mientras el Verificador base cuestiona la resta sin pedir S2 inicio."
        ),
    },
    "dificil_25:H04": {
        "tipo": "cita_sustituta_p01",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "Acierta el plazo máximo de 6 semestres [RG-ART-049], pero atribuye al glosario "
            "[RG-ART-003-DEF-10] (definición de Plan de Estudio) que el Reglamento Interno "
            "fija exigencias/términos al vencer el plazo, regla contenida en el párrafo 2 de "
            "[RG-ART-049] (Regla 3 / precedente P01)."
        ),
    },
    "dificil_25:H06": {
        "tipo": "regresion_verificador_base",
        "solo_condicion_p01": False,
        "causa_raiz": "verificador_base",
        "motivo": (
            "En el ciclo 1 el Redactor fine-tuned calcula correctamente 38 / 4 = 9,5 < 10 "
            "[RI-FI-ART-014] (aunque con prefijo 'No, 38 créditos... no alcanzan'); luego el "
            "Verificador base objeta falsamente que faltan semestres totales y en el ciclo 2 "
            "empuja al Redactor a negar validez al cálculo ('No, el cálculo... no es válido') y lo aprueba."
        ),
    },
    "dificil_25:H18": {
        "tipo": "afirmacion_extra_mal_citada_p01",
        "solo_condicion_p01": True,
        "causa_raiz": "redactor",
        "motivo": (
            "La respuesta principal (máximo 36 créditos + Memoria) acierta con [RI-FI-ART-031], "
            "pero Condiciones afirma 'La suspensión de estudios no libera al estudiante de las "
            "obligaciones pendientes' citando [RG-ART-003-DEF-19] (solo definición) en lugar de "
            "[RG-ART-031], presente en fuentes_traidas (espejo P01 de D3 en H18)."
        ),
    },
    "dificil_25:H19": {
        "tipo": "regresion_verificador_base",
        "solo_condicion_p01": False,
        "causa_raiz": "verificador_base",
        "motivo": (
            "En los ciclos 1 y 2 el Redactor fine-tuned responde íntegramente bien según "
            "[RG-ART-028] (promedio = créditos aprobados / semestres de permanencia); en dos "
            "rechazos consecutivos, el Verificador base exige los umbrales de 15 y 10 créditos "
            "del [RI-FI-ART-014], forzando en el ciclo 3 un cambio erróneo a [RI-FI-ART-014] y al "
            "inexistente 'Reglamento de Ingreso y Permanencia', que luego rechaza."
        ),
    },
}

CASOS_APROB_FALSE_CORRECTOS: dict[str, str] = {
    "congelado_50:47": "Rechaza la premisa falsa de máximo en [RI-FI-ART-008] (cita además [RI-FI-ART-031] válido); correcto pese a aprobado=False.",
    "congelado_50:50": "Se abstiene sin inventar sobre tercera carrera simultánea y describe [RI-FI-ART-019]; correcto pese a aprobado=False.",
    "dificil_25:H17": "Da topes 80% y 100% [RI-FI-ART-013] más régimen especial [RG-ART-020]; correcto pese a aprobado=False.",
    "dificil_25:H21": "Corrige la premisa falsa del Art. 8 (fija mínimo de 8, no máximo) [RI-FI-ART-008]; correcto pese a aprobado=False.",
}

AUDITORIA_COMPARATIVA_6: dict[str, dict[str, Any]] = {
    "congelado_50:13": {
        "base_correcto": 0,
        "base_motivo": "Da umbral 10 créditos pero agrega la fórmula del promedio citando solo [RI-FI-ART-014] (fórmula en [RG-ART-028]; P01).",
        "ft_correcto": 1,
        "ft_motivo": "Acierta umbral < 10 desde 4.º semestre [RI-FI-ART-014] y añade condición propia del mismo [RI-FI-ART-014].",
    },
    "congelado_50:24": {
        "base_correcto": 1,
        "base_motivo": "Explicita ambas excepciones (PLEV y primer año) citando [RI-FI-ART-014].",
        "ft_correcto": 1,
        "ft_motivo": "Explicita ambas excepciones con [RG-ART-028] [RI-FI-ART-014] (errata menor 'Re reprobar').",
    },
    "congelado_50:36": {
        "base_correcto": 0,
        "base_motivo": "Afirma 'No se aplican condiciones o límites adicionales', omitiendo excepciones del [RI-FI-ART-008] (Regla 2).",
        "ft_correcto": 0,
        "ft_motivo": "Mejora el contenido al incluir excepciones, pero cita [CAL-2026-S2-04] en vez de [RI-FI-ART-008] (Regla 3 / P01).",
    },
    "dificil_25:H03": {
        "base_correcto": 0,
        "base_motivo": "Se abstiene en el ciclo 3 por falta de fecha de inicio S2.",
        "ft_correcto": 0,
        "ft_motivo": "Calcula 24 días en S1, pero reemplaza el S2 faltante por 04 sep->11 dic = 98 días [CAL-2026-S2-04] en lugar de abstenerse.",
    },
    "dificil_25:H07": {
        "base_correcto": 0,
        "base_motivo": "Falla en 3 ciclos (227,68 s): falsa abstención alegando falta de semestres y créditos totales.",
        "ft_correcto": 1,
        "ft_motivo": "Resuelve en 1 ciclo (78,70 s): 42 / 4 = 10,5 > 10 con [RG-ART-028] [RI-FI-ART-014].",
    },
    "dificil_25:H14": {
        "base_correcto": 0,
        "base_motivo": "Contradicción polar: inicia afirmando 'Sí, el estudiante queda automáticamente en baja académica'.",
        "ft_correcto": 1,
        "ft_motivo": "Inicia correctamente 'No queda automáticamente en baja académica' con excepciones y apelación [RI-FI-ART-014] [RG-ART-028] [RG-ART-030].",
    },
}

CASOS_FALLO_SELECCIONADOS = [
    "dificil_25:H03",
    "dificil_25:H06",
    "dificil_25:H19",
    "congelado_50:6",
    "congelado_50:36",
    "congelado_50:7",
    "congelado_50:10",
    "congelado_50:31",
    "dificil_25:H02",
    "dificil_25:H04",
    "dificil_25:H18",
]


def _cargar_corpus_ids(corpus_path: Path) -> set[str]:
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    ids: set[str] = set()
    for seccion in ("padres", "unidades"):
        for item in data.get(seccion, []):
            if isinstance(item, dict) and "id" in item:
                ids.add(str(item["id"]))
    return ids


def _cargar_veredictos_d3(
    veredictos_path: Path,
    d3_csv_path: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    raw = json.loads(veredictos_path.read_text(encoding="utf-8"))
    casos_d3: dict[str, dict[str, Any]] = {}
    for caso in raw["completo"]["casos"]:
        cid = str(caso["id"])
        qid = f"dificil_25:{cid}" if cid.startswith("H") else f"congelado_50:{cid}"
        casos_d3[qid] = caso

    with d3_csv_path.open(encoding="utf-8", newline="") as f:
        d3_rows = list(csv.DictReader(f))
    d3_seconds = round(sum(float(r["segundos"]) for r in d3_rows), 2)
    d3_cycles_gt1 = sum(1 for r in d3_rows if int(r["ciclos"]) > 1)
    d3_events = sum(int(r["llamadas_modelo"]) for r in d3_rows)
    resumen_d3 = {
        "congelado_50_ok": sum(
            1 for q, c in casos_d3.items() if q.startswith("congelado_50:") and c["correcta"] == 1
        ),
        "dificil_25_ok": sum(
            1 for q, c in casos_d3.items() if q.startswith("dificil_25:") and c["correcta"] == 1
        ),
        "segundos_totales": d3_seconds,
        "minutos_totales": round(d3_seconds / 60.0, 2),
        "eventos_traza_totales": d3_events,
        "casos_ciclos_mayor_1": d3_cycles_gt1,
    }
    return casos_d3, resumen_d3


def _verificar_telemetria(
    telemetry: dict[str, list[dict[str, Any]]],
    rows: list[dict[str, str]],
) -> dict[str, Any]:
    by_agent: Counter[str] = Counter()
    violaciones: list[dict[str, Any]] = []
    tokens_in: Counter[str] = Counter()
    tokens_out: Counter[str] = Counter()
    for qid, calls in telemetry.items():
        for idx, c in enumerate(calls):
            ag = str(c["agente"])
            usa = bool(c["usa_adaptador"])
            esperado = ag == "redactor"
            if usa != esperado:
                violaciones.append(
                    {"qid": qid, "indice": idx, "agente": ag, "usa_adaptador": usa}
                )
            by_agent[ag] += 1
            tokens_in[ag] += int(c.get("input_tokens", 0))
            tokens_out[ag] += int(c.get("output_tokens", 0))

    total_calls = sum(by_agent.values())
    total_events = sum(int(r["eventos_traza"]) for r in rows)
    total_sec = round(sum(float(r["segundos"]) for r in rows), 2)
    return {
        "total_consultas": len(rows),
        "llamadas_modelo_totales": total_calls,
        "llamadas_por_pregunta": round(total_calls / len(rows), 2),
        "llamadas_por_agente": dict(by_agent),
        "tokens_entrada_por_agente": dict(tokens_in),
        "tokens_salida_por_agente": dict(tokens_out),
        "eventos_traza_totales": total_events,
        "fallbacks_totales": sum(int(r["fallbacks"]) for r in rows),
        "errores_ejecucion": sum(1 for r in rows if (r.get("error") or "").strip()),
        "segundos_totales": total_sec,
        "minutos_totales": round(total_sec / 60.0, 2),
        "segundos_promedio_congelado": round(
            sum(float(r["segundos"]) for r in rows if r["set"] == "congelado_50") / 50.0,
            2,
        ),
        "segundos_promedio_dificil": round(
            sum(float(r["segundos"]) for r in rows if r["set"] == "dificil_25") / 25.0,
            2,
        ),
        "casos_ciclos_mayor_1": {
            "congelado_50": sum(
                1 for r in rows if r["set"] == "congelado_50" and int(r["ciclos"]) > 1
            ),
            "dificil_25": sum(
                1 for r in rows if r["set"] == "dificil_25" and int(r["ciclos"]) > 1
            ),
            "total": sum(1 for r in rows if int(r["ciclos"]) > 1),
        },
        "violaciones_aislamiento_lora": len(violaciones),
        "detalle_violaciones_aislamiento": violaciones,
    }


def _clasificar_transicion(ok_d3: int, ok_d4: int) -> str:
    if ok_d3 == 1 and ok_d4 == 1:
        return "acierto_mantenido"
    if ok_d3 == 0 and ok_d4 == 1:
        return "corregido_en_d4"
    if ok_d3 == 0 and ok_d4 == 0:
        return "fallo_persistente"
    return "regresion_d4"


def _auditar_casos(
    rows: list[dict[str, str]],
    d3_casos: dict[str, dict[str, Any]],
    corpus_ids: set[str],
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    rows_auditados: list[dict[str, str]] = []
    veredictos: list[dict[str, Any]] = []

    for row in rows:
        qid = f"{row['set']}:{row['id']}"
        cites = sorted(set(CITE_RE.findall(row["respuesta_sistema"])))
        fuentes = {x.strip() for x in row["fuentes_traidas"].split(";") if x.strip()}
        citas_fuera_evidencia = [c for c in cites if c not in fuentes]
        citas_inexistentes = [c for c in cites if c not in corpus_ids]

        fallo = FALLOS_ESTRICTOS_D4.get(qid)
        ok_d4 = 0 if fallo else 1
        ok_d3 = int(d3_casos[qid]["correcta"])
        aprob_v = row["aprobado_verificador"] == "True"

        if fallo:
            motivo = fallo["motivo"]
            tipo_fallo = fallo["tipo"]
            causa_raiz = fallo["causa_raiz"]
            solo_p01 = bool(fallo["solo_condicion_p01"])
        else:
            motivo = CASOS_APROB_FALSE_CORRECTOS.get(
                qid,
                "Respuesta suficiente, coherente con las condiciones y respaldada por citas presentes en evidencia.",
            )
            tipo_fallo = None
            causa_raiz = None
            solo_p01 = False

        nuevo_row = dict(row)
        nuevo_row["correcto"] = str(ok_d4)
        rows_auditados.append(nuevo_row)

        veredictos.append(
            {
                "qid": qid,
                "set": row["set"],
                "id": row["id"],
                "categoria": row["categoria"],
                "pregunta": row["pregunta"],
                "correcto_d4_estricto": ok_d4,
                "correcto_d4_nucleo": 1 if (ok_d4 == 1 or solo_p01) else 0,
                "correcto_d3_v6": ok_d3,
                "transicion_d3_a_d4": _clasificar_transicion(ok_d3, ok_d4),
                "aprobado_verificador": aprob_v,
                "ciclos": int(row["ciclos"]),
                "llamadas_modelo": int(row["llamadas_modelo"]),
                "citas_en_respuesta": cites,
                "citas_fuera_de_evidencia": citas_fuera_evidencia,
                "citas_inexistentes_en_corpus": citas_inexistentes,
                "tipo_fallo": tipo_fallo,
                "causa_raiz": causa_raiz,
                "solo_condicion_p01": solo_p01,
                "motivo_auditoria": motivo,
            }
        )

    return rows_auditados, veredictos


def _construir_resumen_comparativa(
    comparativa: list[dict[str, Any]],
) -> dict[str, Any]:
    casos: list[dict[str, Any]] = []
    base_ok = 0
    ft_ok = 0
    for item in comparativa:
        qid = item["qid"]
        audit = AUDITORIA_COMPARATIVA_6[qid]
        base_ok += audit["base_correcto"]
        ft_ok += audit["ft_correcto"]
        casos.append(
            {
                "qid": qid,
                "categoria": item["categoria"],
                "pregunta": item["pregunta"],
                "base_correcto": audit["base_correcto"],
                "ft_correcto": audit["ft_correcto"],
                "base_ciclos": item["base"]["ciclos"],
                "ft_ciclos": item["finetuned_redactor"]["ciclos"],
                "base_segundos": item["base"]["segundos"],
                "ft_segundos": item["finetuned_redactor"]["segundos"],
                "base_motivo": audit["base_motivo"],
                "ft_motivo": audit["ft_motivo"],
            }
        )
    return {
        "total_pares": len(casos),
        "aciertos_base": base_ok,
        "aciertos_finetuned": ft_ok,
        "casos": casos,
    }


def _construir_casos_fallo(
    rows_by_qid: dict[str, dict[str, str]],
    veredictos_by_qid: dict[str, dict[str, Any]],
    trazas: dict[str, list[dict[str, Any]]],
    telemetria: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    casos: list[dict[str, Any]] = []
    for qid in CASOS_FALLO_SELECCIONADOS:
        row = rows_by_qid[qid]
        ver = veredictos_by_qid[qid]
        casos.append(
            {
                "qid": qid,
                "categoria": row["categoria"],
                "pregunta": row["pregunta"],
                "gold_dato": row["gold_dato"],
                "gold_fuente": row["gold_fuente"],
                "respuesta_final": row["respuesta_sistema"],
                "aprobado_verificador": row["aprobado_verificador"] == "True",
                "motivo_verificador": row["motivo_verificador"],
                "ciclos": int(row["ciclos"]),
                "llamadas_modelo": int(row["llamadas_modelo"]),
                "fuentes_traidas": [
                    x.strip() for x in row["fuentes_traidas"].split(";") if x.strip()
                ],
                "tipo_fallo": ver["tipo_fallo"],
                "causa_raiz": ver["causa_raiz"],
                "solo_condicion_p01": ver["solo_condicion_p01"],
                "transicion_d3_a_d4": ver["transicion_d3_a_d4"],
                "diagnostico_auditoria": ver["motivo_auditoria"],
                "telemetria": telemetria[qid],
                "traza_completa": trazas[qid],
            }
        )
    return {
        "descripcion": (
            "Trazas completas de los fallos estrictos de Deliverable 4 bajo LEEME_PAUTA.md, "
            "destacando H03 (fallo persistente D1–D4), H06/H19 (degradaciones provocadas por el "
            "Verificador base frente a borradores válidos/útiles del Redactor FT) y desvíos de cita P01."
        ),
        "total_casos_documentados": len(casos),
        "casos": casos,
    }


def generar_auditoria(
    eval_dir: Path = EVAL_DIR,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    d3_veredictos_path: Path = DEFAULT_D3_VEREDICTOS_PATH,
    d3_csv_path: Path = DEFAULT_D3_CSV_PATH,
    diagnostico_d3_path: Path = DEFAULT_DIAGNOSTICO_D3_PATH,
) -> dict[str, Any]:
    """Genera los tres artefactos de auditoría D4 y devuelve el resumen completo."""
    csv_in = eval_dir / "resultados_agentes_D4.csv"
    trazas_in = eval_dir / "trazas_D4.json"
    tele_in = eval_dir / "telemetria_llamadas.json"
    comp_in = eval_dir / "comparativa_base_vs_finetuned.json"
    config_in = eval_dir / "configuracion_evaluacion.json"

    with csv_in.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    trazas = json.loads(trazas_in.read_text(encoding="utf-8"))
    telemetria = json.loads(tele_in.read_text(encoding="utf-8"))
    comparativa = json.loads(comp_in.read_text(encoding="utf-8"))
    config_eval = json.loads(config_in.read_text(encoding="utf-8"))
    diag_d3 = json.loads(diagnostico_d3_path.read_text(encoding="utf-8"))
    corpus_ids = _cargar_corpus_ids(corpus_path)
    d3_casos, resumen_d3_csv = _cargar_veredictos_d3(d3_veredictos_path, d3_csv_path)

    telemetria_resumen = _verificar_telemetria(telemetria, rows)
    rows_auditados, veredictos = _auditar_casos(rows, d3_casos, corpus_ids)

    csv_out = eval_dir / "resultados_agentes_D4_auditados.csv"
    with csv_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_auditados)

    cong_v = [v for v in veredictos if v["set"] == "congelado_50"]
    dif_v = [v for v in veredictos if v["set"] == "dificil_25"]

    d3_llm_calls = int(diag_d3["resumen_global"]["llamadas_modelo_llm_total"])
    d3_llm_by_agent = dict(diag_d3["resumen_global"]["llamadas_llm_por_agente"])
    d4_llm_calls = int(telemetria_resumen["llamadas_modelo_totales"])
    d3_sec = float(resumen_d3_csv["segundos_totales"])
    d4_sec = float(telemetria_resumen["segundos_totales"])

    por_categoria: dict[str, dict[str, int]] = {}
    for v in veredictos:
        cat = v["categoria"]
        bucket = por_categoria.setdefault(
            cat, {"total": 0, "d4_estricto": 0, "d4_nucleo": 0, "d3_v6": 0}
        )
        bucket["total"] += 1
        bucket["d4_estricto"] += v["correcto_d4_estricto"]
        bucket["d4_nucleo"] += v["correcto_d4_nucleo"]
        bucket["d3_v6"] += v["correcto_d3_v6"]

    transiciones = dict(Counter(v["transicion_d3_a_d4"] for v in veredictos))
    fallos_d3_qids = sorted(q for q, c in d3_casos.items() if c["correcta"] != 1)
    corregidos_d3_qids = [
        v["qid"] for v in veredictos if v["transicion_d3_a_d4"] == "corregido_en_d4"
    ]
    ver_by_qid = {v["qid"]: v for v in veredictos}
    rows_by_qid = {f"{r['set']}:{r['id']}": r for r in rows}

    aprobaciones_true = [v for v in veredictos if v["aprobado_verificador"]]
    aprobaciones_false = [v for v in veredictos if not v["aprobado_verificador"]]

    auditoria = {
        "criterio": "Auditoría estricta según Deliverable 3/paquete_25_dificiles/LEEME_PAUTA.md (incluye Regla 3 / precedente P01).",
        "configuracion_runtime": config_eval,
        "resumen_global": {
            "congelado_50": {
                "aciertos_estrictos": sum(v["correcto_d4_estricto"] for v in cong_v),
                "total": len(cong_v),
                "porcentaje_estricto": round(
                    100.0 * sum(v["correcto_d4_estricto"] for v in cong_v) / len(cong_v), 1
                ),
                "aciertos_nucleo_sin_condicion_p01": sum(
                    v["correcto_d4_nucleo"] for v in cong_v
                ),
            },
            "dificil_25": {
                "aciertos_estrictos": sum(v["correcto_d4_estricto"] for v in dif_v),
                "total": len(dif_v),
                "porcentaje_estricto": round(
                    100.0 * sum(v["correcto_d4_estricto"] for v in dif_v) / len(dif_v), 1
                ),
                "aciertos_nucleo_sin_condicion_p01": sum(
                    v["correcto_d4_nucleo"] for v in dif_v
                ),
            },
            "global_75": {
                "aciertos_estrictos": sum(v["correcto_d4_estricto"] for v in veredictos),
                "total": len(veredictos),
                "porcentaje_estricto": round(
                    100.0 * sum(v["correcto_d4_estricto"] for v in veredictos) / len(veredictos),
                    1,
                ),
                "aciertos_nucleo_sin_condicion_p01": sum(
                    v["correcto_d4_nucleo"] for v in veredictos
                ),
                "porcentaje_nucleo": round(
                    100.0 * sum(v["correcto_d4_nucleo"] for v in veredictos) / len(veredictos),
                    1,
                ),
            },
            "aprobacion_interna_vs_exactitud": {
                "aprobadas_por_verificador": len(aprobaciones_true),
                "aprobadas_pero_incorrectas_estricto": sum(
                    1 for v in aprobaciones_true if v["correcto_d4_estricto"] == 0
                ),
                "rechazadas_por_verificador": len(aprobaciones_false),
                "rechazadas_pero_correctas": sum(
                    1 for v in aprobaciones_false if v["correcto_d4_estricto"] == 1
                ),
            },
        },
        "comparacion_d3_a_d4": {
            "d3_congelado_50": resumen_d3_csv["congelado_50_ok"],
            "d3_dificil_25": resumen_d3_csv["dificil_25_ok"],
            "d3_llamadas_reales_llm": d3_llm_calls,
            "d3_llamadas_llm_por_agente": d3_llm_by_agent,
            "d4_llamadas_reales_llm": d4_llm_calls,
            "d4_llamadas_llm_por_agente": telemetria_resumen["llamadas_por_agente"],
            "delta_llamadas_pct": round(100.0 * (d4_llm_calls - d3_llm_calls) / d3_llm_calls, 2),
            "d3_eventos_traza": resumen_d3_csv["eventos_traza_totales"],
            "d4_eventos_traza": telemetria_resumen["eventos_traza_totales"],
            "d3_segundos": d3_sec,
            "d4_segundos": d4_sec,
            "delta_tiempo_pct": round(100.0 * (d4_sec - d3_sec) / d3_sec, 2),
            "d3_ciclos_gt1": resumen_d3_csv["casos_ciclos_mayor_1"],
            "d4_ciclos_gt1": telemetria_resumen["casos_ciclos_mayor_1"]["total"],
            "transiciones_vs_d3": transiciones,
            "errores_d3_originales": fallos_d3_qids,
            "errores_d3_resueltos_estrictos_en_d4": corregidos_d3_qids,
            "errores_d3_resueltos_en_nucleo_p36_h18": [
                "congelado_50:36 (contenido corregido, cambia ID cita)",
                "dificil_25:H18 (contenido y RG-ART-033 corregidos; falla cita extra P01)",
            ],
        },
        "telemetria_y_aislamiento": telemetria_resumen,
        "desglose_por_categoria": por_categoria,
        "comparativa_controlada_6_casos": _construir_resumen_comparativa(comparativa),
        "veredictos": veredictos,
    }

    (eval_dir / "auditoria_D4.json").write_text(
        json.dumps(auditoria, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    casos_fallo = _construir_casos_fallo(rows_by_qid, ver_by_qid, trazas, telemetria)
    (eval_dir / "casos_fallo_y_regresion.json").write_text(
        json.dumps(casos_fallo, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return auditoria


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera auditoría y trazas de fallo D4.")
    parser.add_argument("--eval-dir", type=Path, default=EVAL_DIR)
    args = parser.parse_args()
    res = generar_auditoria(eval_dir=args.eval_dir)
    rg = res["resumen_global"]
    print(
        f"D4 estricto: {rg['congelado_50']['aciertos_estrictos']}/50 congelado, "
        f"{rg['dificil_25']['aciertos_estrictos']}/25 dificil "
        f"({rg['global_75']['aciertos_estrictos']}/75 = {rg['global_75']['porcentaje_estricto']}%) | "
        f"nucleo sin P01 condicion: {rg['global_75']['aciertos_nucleo_sin_condicion_p01']}/75 | "
        f"violaciones LoRA: {res['telemetria_y_aislamiento']['violaciones_aislamiento_lora']}"
    )


if __name__ == "__main__":
    main()
