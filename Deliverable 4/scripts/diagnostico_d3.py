#!/usr/bin/env python3
"""Diagnostico empirico de las trazas v6 de Deliverable 3 para Deliverable 4.

Reconstruye el pool y top-6 exactos de evidencia vistos por el agente Redactor
siguiendo la misma regla de puntaje de ``orquestador.py`` y cruza los 75 casos
con la auditoria oficial de ``veredictos_exportados.json`` para cuantificar
dónde se originan los errores restantes y justificar el fine-tuning del Redactor.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

MAX_EVIDENCIA = 6

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_D3_DIR = REPO_ROOT / "Deliverable 3" / "Deliverable3"
DEFAULT_AUDIT_FILE = REPO_ROOT / "Deliverable 3" / "auditoria" / "veredictos_exportados.json"
DEFAULT_OUT_JSON = REPO_ROOT / "Deliverable 4" / "diagnostico" / "diagnostico_d3.json"

# Mapeo verificado contra corpus.json y gold_fuente/motivos de auditoria en los 9 errores D3 v6.
# "requeridas": unidades minimas que exige la pregunta gold.
# "requeridas_cita_extra": unidades adicionales necesarias para respaldar afirmaciones
# que el propio Redactor introdujo en su respuesta.
GOLD_UNIDADES_ERRORES: dict[str, dict[str, Any]] = {
    "congelado_50:13": {
        "requeridas": ["RI-FI-ART-014"],
        "requeridas_cita_extra": ["RG-ART-028"],
        "categoria_fallo": "redactor_cita_incompleta_afirmacion_extra",
        "explicacion": (
            "Responde el umbral de 10 creditos, pero agrega la formula del promedio "
            "citando solo [RI-FI-ART-014] cuando esa formula pertenece a [RG-ART-028]."
        ),
    },
    "congelado_50:24": {
        "requeridas": ["RI-FI-ART-014"],
        "requeridas_cita_extra": ["RG-ART-028"],
        "categoria_fallo": "redactor_omision_excepciones",
        "explicacion": (
            "Alude genericamente a 'las excepciones mencionadas en el articulo', "
            "sin enumerar PLEV ni estudiantes en su primer ano de permanencia."
        ),
    },
    "congelado_50:26": {
        "requeridas": ["RI-FI-ART-027"],
        "requeridas_cita_extra": ["RG-ART-031", "RG-ART-033"],
        "categoria_fallo": "redactor_distorsion_lectura",
        "explicacion": (
            "Confunde sujeto y plazo de la evidencia: afirma que 'la reincorporacion puede "
            "extenderse por un maximo de tres anos', cuando el plazo de 3 anos aplica a la suspension."
        ),
    },
    "congelado_50:36": {
        "requeridas": ["CAL-2026-S2-01", "RI-FI-ART-008"],
        "requeridas_cita_extra": [],
        "categoria_fallo": "redactor_omision_condiciones_y_excepciones",
        "explicacion": (
            "Declara falsamente 'No se aplican condiciones o limites adicionales' y "
            "omite las excepciones del minimo de 8 creditos establecidas en [RI-FI-ART-008]."
        ),
    },
    "dificil_25:H03": {
        "requeridas": ["CAL-2026-S1-02", "CAL-2026-S1-03", "CAL-2026-S2-02", "CAL-2026-S2-03"],
        "requeridas_cita_extra": [],
        "categoria_fallo": "recuperador_evidencia_faltante",
        "explicacion": (
            "El Recuperador no incorpora al top-6 las unidades de inicio de clases "
            "([CAL-2026-S1-02] y [CAL-2026-S2-02]). En el ciclo 1 el Redactor alucina "
            "conteos de dias y en ciclos 2-3 se abstiene por falta de fechas."
        ),
    },
    "dificil_25:H07": {
        "requeridas": ["RI-FI-ART-014", "RG-ART-028"],
        "requeridas_cita_extra": [],
        "categoria_fallo": "redactor_derivacion_implicita_y_colapso_feedback",
        "explicacion": (
            "Ciclo 1 concluye bien (10,5 > 10) pero sin explicitar el paso aritmetico "
            "(42 / 4 = 10,5); el Verificador rechaza falsamente y el Redactor colapsa "
            "en ciclos 2-3 hacia una falsa abstencion pese a estar todos los datos en la pregunta."
        ),
    },
    "dificil_25:H14": {
        "requeridas": ["RI-FI-ART-014", "RG-ART-028"],
        "requeridas_cita_extra": [],
        "categoria_fallo": "redactor_contradiccion_polar_excepciones",
        "explicacion": (
            "Ante una pregunta cerrada ('¿Queda automaticamente...?'), responde primero "
            "'Si, el estudiante queda automaticamente' y luego enumera excepciones que lo contradicen."
        ),
    },
    "dificil_25:H18": {
        "requeridas": ["RI-FI-ART-031"],
        "requeridas_cita_extra": ["RG-ART-033"],
        "categoria_fallo": "redactor_perdida_cita_bajo_feedback",
        "explicacion": (
            "Ciclo 1 acierta los 36 creditos y cita [RG-ART-033] para los 3 anos, pero "
            "arrastra citas de definiciones y el Verificador rechaza; en ciclo 2 conserva "
            "la afirmacion de los 3 anos y borra la cita [RG-ART-033], dejando solo [RI-FI-ART-031]."
        ),
    },
    "dificil_25:H25": {
        "requeridas": ["RI-FI-ART-005"],
        "requeridas_cita_extra": [],
        "categoria_fallo": "redactor_sintesis_incompleta_desempate",
        "explicacion": (
            "Enumera factores de seleccion teniendo [RI-FI-ART-005] en el puesto #1, pero "
            "omite el orden de prelacion y el criterio de desempate (mayor numero de creditos "
            "aprobados y, en caso de igualdad, mayor promedio curricular)."
        ),
    },
}


def cargar_datos_d3(
    d3_dir: Path = DEFAULT_D3_DIR,
    audit_file: Path = DEFAULT_AUDIT_FILE,
) -> tuple[list[dict[str, str]], dict[str, list[dict[str, Any]]], dict[str, Any], dict[str, dict[str, Any]]]:
    """Carga CSV de resultados, trazas v6, veredictos auditados y corpus D3."""
    csv_path = d3_dir / "resultados_v6" / "resultados_agentes_D3.csv"
    trazas_path = d3_dir / "resultados_v6" / "trazas_D3.json"
    corpus_path = d3_dir / "agentes" / "corpus.json"

    with csv_path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    trazas = json.loads(trazas_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_file.read_text(encoding="utf-8"))
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    unidades = {u["id"]: u for u in corpus["unidades"]}

    casos_audit = audit["completo"]["casos"]
    if len(rows) != len(casos_audit) or len(rows) != len(trazas):
        raise ValueError(
            f"Desalineacion entre fuentes D3: csv={len(rows)}, "
            f"audit={len(casos_audit)}, trazas={len(trazas)}"
        )
    for row, verdict in zip(rows, casos_audit):
        if row["id"] != verdict["id"]:
            raise ValueError(f"ID desalineado entre CSV ({row['id']}) y auditoria ({verdict['id']})")

    return rows, trazas, audit, unidades


def reconstruir_evidencia_top6(
    steps: list[dict[str, Any]],
    max_evidencia: int = MAX_EVIDENCIA,
) -> dict[str, Any]:
    """Reconstruye puntaje acumulado, pool completo y seleccion top-K del Redactor.

    Replica exactamente ``Orquestador._sumar``, ``_buscar`` y ``_seleccion`` en
    ``Deliverable 3/Deliverable3/agentes/orquestador.py``:
    - Busqueda base (``rama == 'busqueda_base'``): ``2.0 / (r + 1)`` por rango ``r``.
    - Busqueda ReAct (``accion == 'buscar'``): ``1.0 / (r + 1)`` por rango ``r``.
    - Lectura directa (``traido`` en ``observacion``): ``+3.0``.
    La ordenacion conserva el orden de insercion en Python al desempatar puntajes.
    """
    puntajes: dict[str, float] = {}

    def sumar(uid: str, puntos: float) -> None:
        puntajes[uid] = puntajes.get(uid, 0.0) + puntos

    for step in steps:
        if step.get("agente") != "recuperador":
            continue
        entrada = step.get("entrada") or {}
        salida = step.get("salida") or {}
        obs = step.get("observacion")
        if not isinstance(obs, dict):
            continue

        if "hits" in obs:
            es_base = entrada.get("rama") == "busqueda_base"
            peso = 2.0 if es_base else 1.0
            for rank, uid in enumerate(obs["hits"]):
                sumar(uid, peso / (rank + 1))

        if "traido" in obs and obs["traido"]:
            # Si 'traer' o 'existe' trajeron una unidad existente, orquestador.py suma +3.0.
            accion = salida.get("accion") if isinstance(salida, dict) else None
            if accion in ("traer", "existe", None):
                sumar(obs["traido"], 3.0)

    ordenado = sorted(puntajes.keys(), key=lambda uid: -puntajes[uid])
    return {
        "top6": ordenado[:max_evidencia],
        "pool_ordenado": ordenado,
        "puntajes": {uid: round(puntajes[uid], 4) for uid in ordenado},
    }


def analizar_caso(
    row: dict[str, str],
    verdict: dict[str, Any],
    steps: list[dict[str, Any]],
    corpus_ids: set[str],
) -> dict[str, Any]:
    """Analiza una traza individual y clasifica donde fallo si correcta == 0."""
    case_key = f"{row['set']}:{row['id']}"
    evidencia = reconstruir_evidencia_top6(steps)
    top6 = evidencia["top6"]
    pool_set = set(evidencia["pool_ordenado"])

    borradores = [s.get("salida", "") for s in steps if s.get("agente") == "redactor"]
    verificaciones = [s for s in steps if s.get("agente") == "verificador"]
    rechazos_redactor = sum(
        1
        for s in verificaciones
        if isinstance(s.get("salida"), dict)
        and s["salida"].get("aprobado") is False
        and s["salida"].get("destino") == "redactor"
    )
    rechazos_recuperador = sum(
        1
        for s in verificaciones
        if isinstance(s.get("salida"), dict)
        and s["salida"].get("aprobado") is False
        and s["salida"].get("destino") == "recuperador"
    )
    fallbacks = [s.get("agente") for s in steps if s.get("fallback")]
    llamadas_llm_por_agente: dict[str, int] = {}
    for s in steps:
        if not s.get("decidido_por"):
            ag = str(s.get("agente"))
            llamadas_llm_por_agente[ag] = llamadas_llm_por_agente.get(ag, 0) + 1
    llamadas_llm = sum(llamadas_llm_por_agente.values())

    correcta = int(verdict["correcta"]) == 1
    info_error: dict[str, Any] | None = None

    if not correcta:
        spec = GOLD_UNIDADES_ERRORES.get(case_key)
        if spec is None:
            raise KeyError(f"Falta especificacion GOLD_UNIDADES_ERRORES para {case_key}")
        for uid in spec["requeridas"] + spec["requeridas_cita_extra"]:
            if uid not in corpus_ids:
                raise ValueError(f"ID inexistente en corpus.json: {uid} ({case_key})")

        req_faltantes_top6 = [u for u in spec["requeridas"] if u not in top6]
        extra_faltantes_top6 = [u for u in spec["requeridas_cita_extra"] if u not in top6]
        req_faltantes_pool = [u for u in spec["requeridas"] if u not in pool_set]

        primer_borrador = borradores[0] if borradores else ""
        ultimo_verificador = verificaciones[-1]["salida"] if verificaciones else {}

        info_error = {
            "gold_fuente_csv": row["gold_fuente"],
            "requeridas": spec["requeridas"],
            "requeridas_cita_extra": spec["requeridas_cita_extra"],
            "todas_requeridas_en_top6": len(req_faltantes_top6) == 0,
            "todas_con_extra_en_top6": (len(req_faltantes_top6) + len(extra_faltantes_top6)) == 0,
            "requeridas_faltantes_top6": req_faltantes_top6,
            "extra_faltantes_top6": extra_faltantes_top6,
            "requeridas_faltantes_pool": req_faltantes_pool,
            "agente_origen": "recuperador" if req_faltantes_top6 else "redactor",
            "categoria_fallo": spec["categoria_fallo"],
            "explicacion": spec["explicacion"],
            "motivo_auditoria": verdict["motivo"],
            "aprobado_verificador_final": bool(ultimo_verificador.get("aprobado")),
            "motivo_verificador_final": ultimo_verificador.get("motivo", ""),
            "primer_borrador": primer_borrador,
            "respuesta_final": row["respuesta_sistema"],
        }

    return {
        "case_key": case_key,
        "set": row["set"],
        "id": row["id"],
        "categoria": row["categoria"],
        "tipo_enrutador": row["tipo_enrutador"],
        "correcta": correcta,
        "ciclos": int(row["ciclos"]),
        "llamadas_modelo_llm": llamadas_llm,
        "llamadas_llm_por_agente": llamadas_llm_por_agente,
        "eventos_traza": len(steps),
        "rechazos_redactor": rechazos_redactor,
        "rechazos_recuperador": rechazos_recuperador,
        "fallbacks": fallbacks,
        "top6": top6,
        "pool_ordenado": evidencia["pool_ordenado"],
        "error_detalle": info_error,
    }


def _resumen_split(casos: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(casos)
    correctos = sum(1 for c in casos if c["correcta"])
    errores = [c for c in casos if not c["correcta"]]
    return {
        "total": total,
        "correctos": correctos,
        "incorrectos": len(errores),
        "accuracy_pct": round(100.0 * correctos / total, 2) if total else 0.0,
        "ids_incorrectos": [c["case_key"] for c in errores],
    }


def generar_diagnostico(
    d3_dir: Path = DEFAULT_D3_DIR,
    audit_file: Path = DEFAULT_AUDIT_FILE,
) -> dict[str, Any]:
    """Ejecuta el diagnostico completo sobre las 75 preguntas de D3 v6."""
    rows, trazas, audit, unidades = cargar_datos_d3(d3_dir=d3_dir, audit_file=audit_file)
    corpus_ids = set(unidades.keys())

    casos = [
        analizar_caso(row, verdict, trazas[f"{row['set']}:{row['id']}"], corpus_ids)
        for row, verdict in zip(rows, audit["completo"]["casos"])
    ]

    congelado = [c for c in casos if c["set"] == "congelado_50"]
    dificil = [c for c in casos if c["set"] == "dificil_25"]
    errores = [c for c in casos if not c["correcta"]]

    err_redactor = [c for c in errores if c["error_detalle"]["agente_origen"] == "redactor"]
    err_recuperador = [c for c in errores if c["error_detalle"]["agente_origen"] == "recuperador"]

    ciclos_dist: dict[str, int] = {}
    for c in casos:
        key = str(c["ciclos"])
        ciclos_dist[key] = ciclos_dist.get(key, 0) + 1

    # Estadisticas de ablaciones publicadas en D3 para contrastar limites del prompting
    ablaciones_d3 = {
        split_name: {
            "total": len(data["casos"]),
            "correctos": sum(int(x["correcta"]) for x in data["casos"]),
        }
        for split_name, data in audit.items()
    }

    llamadas_llm_por_agente_total: dict[str, int] = {}
    for c in casos:
        for ag, cnt in c["llamadas_llm_por_agente"].items():
            llamadas_llm_por_agente_total[ag] = llamadas_llm_por_agente_total.get(ag, 0) + cnt

    return {
        "fuentes": {
            "csv": str((d3_dir / "resultados_v6" / "resultados_agentes_D3.csv").relative_to(REPO_ROOT)),
            "trazas": str((d3_dir / "resultados_v6" / "trazas_D3.json").relative_to(REPO_ROOT)),
            "auditoria": str(audit_file.relative_to(REPO_ROOT)),
            "corpus_unidades": len(unidades),
        },
        "resumen_global": {
            "total": _resumen_split(casos),
            "congelado_50": _resumen_split(congelado),
            "dificil_25": _resumen_split(dificil),
            "llamadas_modelo_llm_total": sum(c["llamadas_modelo_llm"] for c in casos),
            "llamadas_modelo_llm_promedio": round(sum(c["llamadas_modelo_llm"] for c in casos) / len(casos), 2),
            "llamadas_llm_por_agente": dict(sorted(llamadas_llm_por_agente_total.items())),
            "eventos_traza_total": sum(c["eventos_traza"] for c in casos),
            "fallbacks_total": sum(len(c["fallbacks"]) for c in casos),
            "distribucion_ciclos": dict(sorted(ciclos_dist.items())),
            "casos_correctos_con_reintento": sum(
                1 for c in casos if c["correcta"] and c["ciclos"] > 1
            ),
            "rechazos_verificador_a_redactor": sum(c["rechazos_redactor"] for c in casos),
            "rechazos_verificador_a_recuperador": sum(c["rechazos_recuperador"] for c in casos),
        },
        "desglose_errores": {
            "total_errores": len(errores),
            "origen_redactor_con_evidencia_top6": len(err_redactor),
            "origen_recuperador_evidencia_faltante": len(err_recuperador),
            "ids_origen_redactor": [c["case_key"] for c in err_redactor],
            "ids_origen_recuperador": [c["case_key"] for c in err_recuperador],
            "casos": [
                {
                    "case_key": c["case_key"],
                    "categoria": c["categoria"],
                    "tipo_enrutador": c["tipo_enrutador"],
                    "ciclos": c["ciclos"],
                    "top6": c["top6"],
                    **c["error_detalle"],
                }
                for c in errores
            ],
        },
        "ablaciones_auditoria_d3": ablaciones_d3,
        "casos": casos,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnostico cuantitativo de trazas D3 v6.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_JSON, help="Ruta JSON de salida.")
    args = parser.parse_args()

    diag = generar_diagnostico()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(diag, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rg = diag["resumen_global"]
    de = diag["desglose_errores"]
    print(
        f"D3 v6 auditado: {rg['total']['correctos']}/{rg['total']['total']} "
        f"({rg['total']['accuracy_pct']}%) | "
        f"congelado_50={rg['congelado_50']['correctos']}/50 | "
        f"dificil_25={rg['dificil_25']['correctos']}/25"
    )
    print(
        f"Errores={de['total_errores']} -> "
        f"Redactor con evidencia completa en top-6: {de['origen_redactor_con_evidencia_top6']} "
        f"({de['ids_origen_redactor']}) | "
        f"Recuperador (faltante en top-6): {de['origen_recuperador_evidencia_faltante']} "
        f"({de['ids_origen_recuperador']})"
    )
    print(
        f"Ciclos: {rg['distribucion_ciclos']} | Reintentos exitosos: "
        f"{rg['casos_correctos_con_reintento']} | Rechazos Verificador->Redactor: "
        f"{rg['rechazos_verificador_a_redactor']}"
    )
    print(f"Escrito en: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
