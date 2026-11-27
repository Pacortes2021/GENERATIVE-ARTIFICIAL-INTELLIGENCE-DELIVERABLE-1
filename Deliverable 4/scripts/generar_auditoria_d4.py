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
import hashlib
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

V1_LEGACY_CSV_LF_SHA256 = (
    "8958abdb15cb37f5947e34bcb59dd151cf5a05ed567bf71612c79a9d9c733cb8"
)
V2_FT_75_CSV_LF_SHA256 = (
    "f57981031f069c38f4046892625a662a8d90724cc1273031b2abcf3764804de6"
)
V2_BASE_75_CSV_LF_SHA256 = (
    "5e3a6d74fe0cdb4c8633ada6583239917bb82c9825f9856ba12297428573060f"
)
V2_FT_N20_CSV_LF_SHA256 = (
    "f2470f1670bca5c750f836fcc86df793301c8ee054433c646b1f02c55cf61b7b"
)
V2_BASE_N20_CSV_LF_SHA256 = (
    "f019768c6662bbe2bcc35c688ff9771079bcd8ace7323b33b939e33d225e1a1a"
)

# Fallos estrictos v1 archivados (64/75) según LEEME_PAUTA.md.
FALLOS_ESTRICTOS_D4_V1: dict[str, dict[str, Any]] = {
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

CASOS_APROB_FALSE_CORRECTOS_V1: dict[str, str] = {
    "congelado_50:47": "Rechaza la premisa falsa de máximo en [RI-FI-ART-008] (cita además [RI-FI-ART-031] válido); correcto pese a aprobado=False.",
    "congelado_50:50": "Se abstiene sin inventar sobre tercera carrera simultánea y describe [RI-FI-ART-019]; correcto pese a aprobado=False.",
    "dificil_25:H17": "Da topes 80% y 100% [RI-FI-ART-013] más régimen especial [RG-ART-020]; correcto pese a aprobado=False.",
    "dificil_25:H21": "Corrige la premisa falsa del Art. 8 (fija mínimo de 8, no máximo) [RI-FI-ART-008]; correcto pese a aprobado=False.",
}

AUDITORIA_COMPARATIVA_6_V1: dict[str, dict[str, Any]] = {
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

CASOS_FALLO_SELECCIONADOS_V1 = [
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

# Fallos estrictos v2 (A100 bf16, 60/75 = 43/50 + 17/25) bajo LEEME_PAUTA.md.
FALLOS_ESTRICTOS_D4_V2: dict[str, dict[str, Any]] = {
    "congelado_50:5": {
        "tipo": "mezcla_cita_condiciones_p01",
        "solo_condicion_p01": True,
        "causa_raiz": "redactor",
        "motivo": (
            "Identifica la Memoria de Título [RI-FI-ART-029], pero Condiciones atribuye a "
            "[RI-FI-ART-030] (que solo define ponderación 60%/40%) la exigencia de aprobarla "
            "íntegramente para acceder al título profesional, regla ubicada en [RG-ART-003-DEF-10] "
            "y [RG-ART-047] (Regla 3 / precedente P01)."
        ),
    },
    "congelado_50:8": {
        "tipo": "extrapolacion_condiciones_p01",
        "solo_condicion_p01": True,
        "causa_raiz": "redactor",
        "motivo": (
            "La respuesta principal acierta que la renuncia es irrevocable e impide reincorporarse "
            "[RI-FI-ART-026] [RG-ART-034], pero Condiciones afirma que quienes renuncien pueden "
            "reingresar como alumnos nuevos en Primer Año citando [RG-ART-044], artículo que regula "
            "el reingreso sin aludir ni habilitar expresamente el caso de renuncia (Regla 3 / P01)."
        ),
    },
    "congelado_50:25": {
        "tipo": "respuesta_incompleta_sin_desglose",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "Solo indica que no pueden eliminarse las asignaturas 'de prioridades a) y b) del "
            "Artículo 7°' [RI-FI-ART-009], sin explicitar que corresponden a las asignaturas "
            "atrasadas y las obligatorias reprobadas pese a tener [RI-FI-ART-007] en fuentes_traidas."
        ),
    },
    "congelado_50:26": {
        "tipo": "regla_mal_aplicada_art_35",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "Exige certificados DAFE (no deudas) y Dirección de Bibliotecas de [RG-ART-035] "
            "para solicitar reincorporación, cuando [RG-ART-035] rige únicamente para suspender "
            "estudios o renunciar a la carrera (la reincorporación se rige por [RG-ART-033])."
        ),
    },
    "congelado_50:28": {
        "tipo": "deformacion_normativa_art_29_42",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "Fusiona erróneamente [RG-ART-029] y [RG-ART-042] al afirmar que la autorización "
            "excepcional del Vicedecano procede solo si en el período anterior el alumno inscribió "
            "asignaturas anuales."
        ),
    },
    "congelado_50:36": {
        "tipo": "omision_excepciones_regla_2",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "Acierta fechas de inscripción [CAL-2026-S2-01] y mínimo de 8 créditos [RI-FI-ART-008], "
            "pero escribe 'Condiciones o límites: No aplica', omitiendo las excepciones al mínimo "
            "del Art. 8 RI-FI (Regla 2 / precedente P36)."
        ),
    },
    "congelado_50:45": {
        "tipo": "nombre_reglamento_inventado",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "Rechaza el inexistente inciso d), pero inventa el título 'Reglamento Integral de "
            "Formación de Ingeniería' en lugar de Reglamento Interno de Docencia de Pregrado de "
            "la Facultad de Ingeniería y mezcla cita [RI-FI-ART-014] con 'Fuente: sin respaldo'."
        ),
    },
    "dificil_25:H02": {
        "tipo": "alucinacion_y_formato_sin_fuente",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "Los promedios 4,2 [RI-FI-ART-018] y 5,0 [RI-FI-ART-019] son correctos, pero "
            "Condiciones alucina el término 'simulink' y omite por completo la línea 'Fuente:'."
        ),
    },
    "dificil_25:H03": {
        "tipo": "recuperacion_incompleta_y_aritmetica",
        "solo_condicion_p01": False,
        "causa_raiz": "recuperador_y_redactor",
        "motivo": (
            "Fallo persistente D1–D4: CAL-2026-S2-02 (10 ago) sigue fuera del top-6 del "
            "Recuperador; en ciclo 3 el Redactor calcula 22 y 19 días usando fechas erradas "
            "(02 abr->24 jul y 04 sep->14 dic) y concluye erróneamente primer semestre."
        ),
    },
    "dificil_25:H04": {
        "tipo": "cita_glosario_y_rechazo_verificador",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor_y_verificador_base",
        "motivo": (
            "En el ciclo 1 el Redactor FT acierta plazo de 6 semestres [RG-ART-049] pero ya "
            "incluye la cita [RG-ART-003-DEF-10] (patrón reforzado por 8 ejemplos del corpus); "
            "el chequeo de citas normaliza esa referencia a RG-ART-003 (en_evidencia=false) "
            "y el Verificador base rechaza los borradores hasta la salida final, que omite el "
            "párrafo 2 de [RG-ART-049] sobre las exigencias al vencer dicho plazo."
        ),
    },
    "dificil_25:H06": {
        "tipo": "polaridad_invertida_y_verificador_base",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor_y_verificador_base",
        "motivo": (
            "En el ciclo 1 el Redactor FT calcula bien '38 / 4 = 9,5 < 10 -> cae en Baja "
            "Académica [RI-FI-ART-014]', pero ya arranca con polaridad contradictoria "
            "('Respuesta: No, ...'); luego el Verificador base agrava el fallo al objetar "
            "falsamente 'El cálculo de 38 / 4 = 9,5 es incorrecto' y empujar el ciclo 2 a "
            "abstención y el ciclo 3 a 'No, al aprobar 38 créditos... incumple el criterio' "
            "sin citar [RG-ART-028]."
        ),
    },
    "dificil_25:H12": {
        "tipo": "mezcla_baja_academica_y_no_inscripcion_h12",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "Responde 'Sí' y 1 año ante el Comité [RG-ART-030], pero mezcla en la respuesta "
            "principal y condiciones el plazo de 10 días hábiles de resolución y la apelación al "
            "quinto día ante el Vicedecano, que en [RG-ART-030] rigen Baja Académica y no Baja "
            "por no Inscripción (Regla 3 / precedente H12)."
        ),
    },
    "dificil_25:H21": {
        "tipo": "respuesta_parcial_y_verificador_base",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor_y_verificador_base",
        "motivo": (
            "Caso mixto/discutible: en el ciclo 1 el Redactor FT responde el mínimo de 8 créditos "
            "de [RI-FI-ART-008] sin explicitar aún que el artículo no fija tope máximo; tras el "
            "rechazo del Verificador base exigiendo responder por el máximo, los ciclos 2 y 3 "
            "se limitan a 'No existe información sobre el máximo' sin reportar el mínimo de 8 "
            "ni corregir la premisa falsa del tope."
        ),
    },
    "dificil_25:H22": {
        "tipo": "regresion_verificador_base",
        "solo_condicion_p01": False,
        "causa_raiz": "verificador_base",
        "motivo": (
            "En el ciclo 1 el Redactor FT refuta bien 4,5 -> 4,0 con [RI-FI-ART-011]; el "
            "Verificador base objeta que 'según la evidencia es 4,5, no 4,0', induciendo en ciclo "
            "2 la inserción de asistencia mínima 80%/100% (regla de [RI-FI-ART-013]) citada como "
            "[RI-FI-ART-011] (Regla 3 / P01)."
        ),
    },
    "dificil_25:H25": {
        "tipo": "sintesis_incompleta_no_aplica",
        "solo_condicion_p01": False,
        "causa_raiz": "redactor",
        "motivo": (
            "Ordena créditos y luego promedio curricular de Plan Común [RI-FI-ART-005], pero "
            "coloca 'Condiciones o límites: No aplica' omitiendo orden de preferencias, cupos por "
            "carrera y que solo cuentan asignaturas obligatorias de Primer Año (Reglas 2 y 5)."
        ),
    },
}

CASOS_APROB_FALSE_CORRECTOS_V2: dict[str, str] = {
    "congelado_50:38": "Aplica escala 1 a 7 y nota mínima 4,0 de [RG-ART-023]; correcto pese a aprobado=False.",
    "congelado_50:47": "Indica correctamente que no existe máximo de créditos fijado en Art. 8 RI-FI (Regla 7); correcto pese a aprobado=False.",
    "congelado_50:48": "Indica correctamente que Art. 12 RI-FI no fija nota mínima en Evaluación de Recuperación; correcto pese a aprobado=False.",
    "congelado_50:50": "Indica que no existe norma sobre tercera carrera simultánea sin inventar; correcto pese a aprobado=False.",
}

AUDITORIA_COMPARATIVA_6_V2: dict[str, dict[str, Any]] = {
    "congelado_50:13": {
        "base_correcto": 1,
        "base_motivo": "Acierta umbral < 10 desde cuarto semestre con [RI-FI-ART-014].",
        "ft_correcto": 1,
        "ft_motivo": "Acierta umbral < 10 [RI-FI-ART-014] y agrega correctamente la fórmula [RG-ART-028].",
    },
    "congelado_50:24": {
        "base_correcto": 1,
        "base_motivo": "Explicita segunda reprobación obligatoria y ambas excepciones (PLEV y primer año) [RI-FI-ART-014] [RG-ART-028].",
        "ft_correcto": 1,
        "ft_motivo": "Responde correctamente con ambas excepciones y paso a Baja Académica [RI-FI-ART-014].",
    },
    "congelado_50:36": {
        "base_correcto": 0,
        "base_motivo": "Dice 'Condiciones o límites: No se aplican', omitiendo excepciones al mínimo de 8 créditos (Regla 2).",
        "ft_correcto": 0,
        "ft_motivo": "Dice 'Condiciones o límites: No aplica', omitiendo excepciones del [RI-FI-ART-008] (Regla 2).",
    },
    "dificil_25:H03": {
        "base_correcto": 0,
        "base_motivo": "Falsa abstención tras 3 ciclos (160,39 s) pese a que las fechas están en CAL 2026 (Regla 8).",
        "ft_correcto": 0,
        "ft_motivo": "Calcula mal (22 y 19 días con fechas erradas) al quedar CAL-2026-S2-02 fuera del top-6 (180,35 s).",
    },
    "dificil_25:H07": {
        "base_correcto": 0,
        "base_motivo": "Falsa abstención tras 3 ciclos (173,54 s) alegando que faltan semestres de permanencia.",
        "ft_correcto": 1,
        "ft_motivo": "Resuelve en 2 ciclos (89,03 s): '42 / 4 = 10,5 > 10' con [RI-FI-ART-014] y [RG-ART-028].",
    },
    "dificil_25:H14": {
        "base_correcto": 0,
        "base_motivo": "Contradicción polar ('Sí, el estudiante queda en baja académica si no cumple...') tras 2 ciclos (92,32 s).",
        "ft_correcto": 1,
        "ft_motivo": "Resuelve en 1 ciclo (58,51 s): 'No queda automáticamente...' con excepciones y apelación [RI-FI-ART-014] [RG-ART-028] [RG-ART-030].",
    },
}

CASOS_FALLO_SELECCIONADOS_V2 = [
    "dificil_25:H06",
    "dificil_25:H03",
    "dificil_25:H04",
    "dificil_25:H21",
    "dificil_25:H22",
    "dificil_25:H02",
    "dificil_25:H12",
    "dificil_25:H25",
    "congelado_50:36",
    "congelado_50:25",
    "congelado_50:26",
    "congelado_50:28",
    "congelado_50:45",
    "congelado_50:5",
    "congelado_50:8",
]

# Fallos estrictos Control Base A100 (bf16) sobre 75 preguntas (62/75 = 46/50 + 16/25).
FALLOS_CONTROL_BASE_75_V2: dict[str, dict[str, Any]] = {
    "congelado_50:11": {
        "tipo": "omision_excepciones_regla_2",
        "causa_raiz": "redactor_base",
        "motivo": "Dice 'Condiciones o límites: No aplicables', omitiendo las excepciones del [RI-FI-ART-008] (Regla 2).",
    },
    "congelado_50:25": {
        "tipo": "falsa_abstencion_regla_8",
        "causa_raiz": "recuperador_y_redactor_base",
        "motivo": "Se abstiene falsamente ('No hay evidencia suficiente') pese a existir [RI-FI-ART-007] y [RI-FI-ART-009].",
    },
    "congelado_50:36": {
        "tipo": "omision_excepciones_regla_2",
        "causa_raiz": "redactor_base",
        "motivo": "Dice 'Condiciones o límites: No se aplican', omitiendo las excepciones del [RI-FI-ART-008] (Regla 2).",
    },
    "congelado_50:43": {
        "tipo": "formato_fuente_placeholder",
        "causa_raiz": "redactor_base",
        "motivo": "Acierta que Art. 100 RG no existe, pero deja 'Condiciones o límites:' vacío y emite 'Fuente: [evidencia]'.",
    },
    "dificil_25:H03": {
        "tipo": "falsa_abstencion_regla_8",
        "causa_raiz": "recuperador_base",
        "motivo": "Se abstiene falsamente en ciclo 3 por ausencia de CAL-2026-S2-02 en top-6.",
    },
    "dificil_25:H06": {
        "tipo": "falsa_abstencion_regla_8",
        "causa_raiz": "redactor_y_verificador_base",
        "motivo": "Falsa abstención tras 3 ciclos alegando que la norma no entrega la fórmula.",
    },
    "dificil_25:H07": {
        "tipo": "falsa_abstencion_regla_8",
        "causa_raiz": "redactor_y_verificador_base",
        "motivo": "Falsa abstención tras 3 ciclos alegando falta de semestres totales pese a 'cuarto semestre'.",
    },
    "dificil_25:H12": {
        "tipo": "mezcla_baja_academica_y_no_inscripcion_h12",
        "causa_raiz": "redactor_base",
        "motivo": "Mezcla resolución en 10 días hábiles y apelación de Baja Académica en Baja por no Inscripción [RG-ART-030] (Regla 3 / H12).",
    },
    "dificil_25:H18": {
        "tipo": "afirmacion_extra_mal_citada_p01",
        "causa_raiz": "redactor_base",
        "motivo": "Exige certificados DAFE/Bibliotecas [RG-ART-035] para reincorporación y contradice la prórroga de [RI-FI-ART-031] citando pérdida a los 3 años [RG-ART-033].",
    },
    "dificil_25:H19": {
        "tipo": "afirmacion_extra_mal_citada_p01",
        "causa_raiz": "redactor_base",
        "motivo": "Acierta fórmula en [RG-ART-028], pero Condiciones atribuye a [RG-ART-028] la mantención de calidad de alumno regular de [RG-ART-050] (Regla 3 / P01).",
    },
    "dificil_25:H22": {
        "tipo": "falsa_abstencion_premisa_falsa",
        "causa_raiz": "recuperador_y_redactor_base",
        "motivo": "Se abstiene falsamente sin corregir 4,5 -> 4,0 pese a existir [RI-FI-ART-011].",
    },
    "dificil_25:H24": {
        "tipo": "respuesta_incompleta_regla_5",
        "causa_raiz": "redactor_base",
        "motivo": "Da plazo de 3 días hábiles [RG-ART-026], pero omite por completo ante quién solicitarlo (Profesor Encargado / apelación Vicedecano).",
    },
    "dificil_25:H25": {
        "tipo": "sintesis_incompleta_p01",
        "causa_raiz": "redactor_base",
        "motivo": "Omite que solo cuentan asignaturas obligatorias de Primer Año [RI-FI-ART-005] y atribuye a [RI-FI-ART-005] frase 'al final del año académico' de [RI-FI-ART-006].",
    },
}

# Fallos estrictos Nuevas 20 FT v2 (10/20 = 50,0%) y Nuevas 20 Control Base (11/20 = 55,0%).
FALLOS_NUEVAS20_FT_V2: dict[str, dict[str, Any]] = {
    "nuevas_20:N05": {
        "tipo": "regresion_verificador_base",
        "causa_raiz": "verificador_base",
        "motivo": "Ciclos 1–2 refutan bien la premisa con [RI-FI-ART-006], pero el Verificador base rechaza exigiendo puntaje mínimo ponderado y empuja ciclo 3 a [RI-FI-ART-005] sin [RI-FI-ART-006].",
    },
    "nuevas_20:N06": {
        "tipo": "error_aritmetico_fechas",
        "causa_raiz": "redactor",
        "motivo": "Suma incorrectamente los tramos de [CAL-2026-S1-05]/[CAL-2026-S1-12] dando '4 + 4 = 8 días'.",
    },
    "nuevas_20:N07": {
        "tipo": "error_aritmetico_fechas",
        "causa_raiz": "redactor",
        "motivo": "Suma incorrectamente las diferencias de fechas dando '5 + 4 = 9 días' en lugar de 126.",
    },
    "nuevas_20:N08": {
        "tipo": "confusion_conceptos_p01",
        "causa_raiz": "redactor",
        "motivo": "Confunde asignatura complementaria [RG-ART-046] con Programa de Formación Complementaria (>=24 SCT) [RG-ART-003-DEF-12] exigiendo este último como requisito.",
    },
    "nuevas_20:N10": {
        "tipo": "regla_incompleta_reingreso",
        "causa_raiz": "redactor",
        "motivo": "Omite el mecanismo explícito de reingreso al semestre siguiente tras titularse/graduarse [RG-ART-047] y mezcla regla de Primer Año de [RG-ART-044].",
    },
    "nuevas_20:N12": {
        "tipo": "enrutador_filtro_documento",
        "causa_raiz": "enrutador_base",
        "motivo": "El Enrutador base restringe documentos a ['RI-FI'], dejando 0 fuentes de [RG-ART-036]/[RG-ART-059] y provocando falsa abstención.",
    },
    "nuevas_20:N16": {
        "tipo": "falsa_abstencion_regla_8",
        "causa_raiz": "redactor_y_verificador",
        "motivo": "Tiene los 4 eventos CAL-2026-S1/S2 en evidencia pero omite fechas en ciclo 1 y luego se abstiene falsamente en ciclos 2–3.",
    },
    "nuevas_20:N17": {
        "tipo": "afirmacion_extra_mal_citada_p01",
        "causa_raiz": "redactor",
        "motivo": "Refuta bien [RG-ART-004], pero en Condiciones atribuye el texto de [RI-FI-ART-002] a [RG-ART-011] (Regla 3 / P01).",
    },
    "nuevas_20:N18": {
        "tipo": "error_factual_condiciones_p01",
        "causa_raiz": "redactor",
        "motivo": "Cumple los 3 roles principales, pero en Condiciones afirma erróneamente bajo [RG-ART-026] que el Vicedecano resuelve la regularización (resuelve el Profesor Encargado; Vicedecano solo atiende apelación).",
    },
    "nuevas_20:N19": {
        "tipo": "enrutador_filtro_documento",
        "causa_raiz": "enrutador_base_y_redactor",
        "motivo": "El Enrutador restringe a ['RI-FI'] dejando fuera [RG-ART-018]; el Redactor acierta parte 1 [RG-ART-036] pero sustituye [RG-ART-018] por [RI-FI-ART-029].",
    },
}

FALLOS_NUEVAS20_BASE_V2: dict[str, dict[str, Any]] = {
    "nuevas_20:N01": {
        "tipo": "alucinacion_condicion",
        "causa_raiz": "redactor_base",
        "motivo": "Agrega que el tope de 54 horas semanales 'aplica a los alumnos a tiempo completo' [RG-ART-017] [RG-ART-003-DEF-11], restricción ausente en ambos textos.",
    },
    "nuevas_20:N07": {
        "tipo": "falsa_abstencion_regla_8",
        "causa_raiz": "recuperador_base",
        "motivo": "Falsa abstención sobre el plazo S1–S2 de evaluación pese a existir las entradas CAL 2026.",
    },
    "nuevas_20:N09": {
        "tipo": "autocontradiccion",
        "causa_raiz": "redactor_base",
        "motivo": "Se contradice al afirmar que no pierde la calidad pero al mismo tiempo la pierde si incurre en causales sin distinguir suspensión vs pérdida [RI-FI-ART-028] [RG-ART-033].",
    },
    "nuevas_20:N10": {
        "tipo": "mezcla_normativa",
        "causa_raiz": "redactor_base",
        "motivo": "Mezcla reingreso por segundo grado/título [RG-ART-047] con Primer Año [RG-ART-044] y cambio de carrera [RG-ART-054].",
    },
    "nuevas_20:N11": {
        "tipo": "respuesta_incompleta_regla_5",
        "causa_raiz": "redactor_base",
        "motivo": "Omite 2 de las 4 condiciones de [RG-ART-021] para evaluación global única.",
    },
    "nuevas_20:N12": {
        "tipo": "enrutador_filtro_documento",
        "causa_raiz": "enrutador_base",
        "motivo": "El Enrutador filtra a ['RI-FI'] (0 fuentes) y provoca falsa abstención sobre [RG-ART-036]/[RG-ART-059].",
    },
    "nuevas_20:N16": {
        "tipo": "falsa_abstencion_regla_8",
        "causa_raiz": "recuperador_base",
        "motivo": "Falsa abstención parcial sobre las cuatro ventanas de receso CAL 2026.",
    },
    "nuevas_20:N18": {
        "tipo": "negacion_falsa_parte",
        "causa_raiz": "recuperador_y_redactor_base",
        "motivo": "Niega falsamente las funciones de Secretaría Académica [RG-ART-005] pese a existir en el corpus.",
    },
    "nuevas_20:N19": {
        "tipo": "falsa_abstencion_parcial",
        "causa_raiz": "enrutador_base",
        "motivo": "Falsa abstención en la segunda parte al no recuperarse [RG-ART-018].",
    },
}

AUDITORIA_COMPARATIVA_N20_V2: dict[str, dict[str, Any]] = {
    "nuevas_20:N01": {
        "base_correcto": 0,
        "base_motivo": "Agrega restricción inexistente 'alumnos a tiempo completo' en Condiciones.",
        "ft_correcto": 1,
        "ft_motivo": "Cita literal 54 horas semanales y programas de asignatura [RG-ART-017] con 'Condiciones: No aplica'.",
    },
    "nuevas_20:N15": {
        "base_correcto": 1,
        "base_motivo": "Acierta Comité de Docencia [RG-ART-036] y Secretaría Académica [RG-ART-005].",
        "ft_correcto": 1,
        "ft_motivo": "Acierta ambos órganos con detalle completo de facilidades y citas [RG-ART-005] [RG-ART-036].",
    },
    "nuevas_20:N19": {
        "base_correcto": 0,
        "base_motivo": "Acierta embarazo pero se abstiene en duración distinta a un semestre por ausencia de [RG-ART-018].",
        "ft_correcto": 0,
        "ft_motivo": "Acierta embarazo [RG-ART-036], pero sustituye [RG-ART-018] faltante por [RI-FI-ART-029].",
    },
}

_REGISTRO_AUDITORIA_GENERAL_POR_SHA: dict[str, tuple[dict[str, dict[str, Any]], str]] = {
    V2_FT_75_CSV_LF_SHA256: (
        FALLOS_ESTRICTOS_D4_V2,
        "Pablo Cortés + auditoría sistemática asistida por IA (LEEME_PAUTA.md v2; pendiente VoBo Álvaro Contreras)",
    ),
    V2_BASE_75_CSV_LF_SHA256: (
        FALLOS_CONTROL_BASE_75_V2,
        "Pablo Cortés + auditoría sistemática asistida por IA (LEEME_PAUTA.md v2; pendiente VoBo Álvaro Contreras)",
    ),
    V2_FT_N20_CSV_LF_SHA256: (
        FALLOS_NUEVAS20_FT_V2,
        "Pablo Cortés + auditoría sistemática asistida por IA (LEEME_PAUTA.md v2; pendiente VoBo Álvaro Contreras)",
    ),
    V2_BASE_N20_CSV_LF_SHA256: (
        FALLOS_NUEVAS20_BASE_V2,
        "Pablo Cortés + auditoría sistemática asistida por IA (LEEME_PAUTA.md v2; pendiente VoBo Álvaro Contreras)",
    ),
}

# Alias activos apuntando a la corrida oficial vigente (v2 A100 bf16).
FALLOS_ESTRICTOS_D4 = FALLOS_ESTRICTOS_D4_V2
CASOS_APROB_FALSE_CORRECTOS = CASOS_APROB_FALSE_CORRECTOS_V2
AUDITORIA_COMPARATIVA_6 = AUDITORIA_COMPARATIVA_6_V2
CASOS_FALLO_SELECCIONADOS = CASOS_FALLO_SELECCIONADOS_V2


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
    solo_base: bool | None = None,
) -> dict[str, Any]:
    if solo_base is None:
        solo_base = bool(rows and rows[0].get("condicion") == "control_base_lora_apagado")
    by_agent: Counter[str] = Counter()
    violaciones: list[dict[str, Any]] = []
    tokens_in: Counter[str] = Counter()
    tokens_out: Counter[str] = Counter()
    for qid, calls in telemetry.items():
        for idx, c in enumerate(calls):
            ag = str(c["agente"])
            usa = bool(c["usa_adaptador"])
            esperado = False if solo_base else (ag == "redactor")
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
        "llamadas_por_pregunta": round(total_calls / max(1, len(rows)), 2),
        "llamadas_por_agente": dict(by_agent),
        "tokens_entrada_por_agente": dict(tokens_in),
        "tokens_salida_por_agente": dict(tokens_out),
        "eventos_traza_totales": total_events,
        "fallbacks_totales": sum(int(r["fallbacks"]) for r in rows),
        "errores_ejecucion": sum(1 for r in rows if (r.get("error") or "").strip()),
        "segundos_totales": total_sec,
        "minutos_totales": round(total_sec / 60.0, 2),
        "segundos_promedio_congelado": round(
            sum(float(r["segundos"]) for r in rows if r["set"] == "congelado_50")
            / max(1, sum(1 for r in rows if r["set"] == "congelado_50")),
            2,
        )
        if any(r["set"] == "congelado_50" for r in rows)
        else 0.0,
        "segundos_promedio_dificil": round(
            sum(float(r["segundos"]) for r in rows if r["set"] == "dificil_25")
            / max(1, sum(1 for r in rows if r["set"] == "dificil_25")),
            2,
        )
        if any(r["set"] == "dificil_25" for r in rows)
        else 0.0,
        "segundos_promedio_por_set": {
            nombre_set: round(
                sum(float(r["segundos"]) for r in rows if r["set"] == nombre_set)
                / sum(1 for r in rows if r["set"] == nombre_set),
                2,
            )
            for nombre_set in sorted({str(r["set"]) for r in rows})
        },
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


def _extraer_traza_lista(traza_raw: Any) -> list[dict[str, Any]]:
    if isinstance(traza_raw, dict):
        return list(traza_raw.get("traza", []))
    if isinstance(traza_raw, list):
        return list(traza_raw)
    return []


def _auditar_casos(
    rows: list[dict[str, str]],
    d3_casos: dict[str, dict[str, Any]],
    corpus_ids: set[str],
    fallos_dict: dict[str, dict[str, Any]] | None = None,
    aprob_false_ok: dict[str, str] | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    fallos_map = FALLOS_ESTRICTOS_D4 if fallos_dict is None else fallos_dict
    aprob_ok_map = CASOS_APROB_FALSE_CORRECTOS if aprob_false_ok is None else aprob_false_ok
    rows_auditados: list[dict[str, str]] = []
    veredictos: list[dict[str, Any]] = []

    for row in rows:
        qid = f"{row['set']}:{row['id']}"
        cites = sorted(set(CITE_RE.findall(row["respuesta_sistema"])))
        fuentes = {x.strip() for x in row["fuentes_traidas"].split(";") if x.strip()}
        citas_fuera_evidencia = [c for c in cites if c not in fuentes]
        citas_inexistentes = [c for c in cites if c not in corpus_ids]

        fallo = fallos_map.get(qid)
        ok_d4 = 0 if fallo else 1
        ok_d3 = int(d3_casos[qid]["correcta"])
        aprob_v = row["aprobado_verificador"] == "True"

        if fallo:
            motivo = fallo["motivo"]
            tipo_fallo = fallo["tipo"]
            causa_raiz = fallo["causa_raiz"]
            solo_p01 = bool(fallo["solo_condicion_p01"])
        else:
            motivo = aprob_ok_map.get(
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
    comp_map: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    audit_map = AUDITORIA_COMPARATIVA_6 if comp_map is None else comp_map
    casos: list[dict[str, Any]] = []
    base_ok = 0
    ft_ok = 0
    for item in comparativa:
        qid = item["qid"]
        audit = audit_map.get(qid, {})
        b_ok = audit.get("base_correcto")
        f_ok = audit.get("ft_correcto")
        if b_ok is not None:
            base_ok += int(b_ok)
        if f_ok is not None:
            ft_ok += int(f_ok)
        casos.append(
            {
                "qid": qid,
                "categoria": item["categoria"],
                "pregunta": item["pregunta"],
                "base_correcto": b_ok,
                "ft_correcto": f_ok,
                "base_ciclos": item["base"]["ciclos"],
                "ft_ciclos": item["finetuned_redactor"]["ciclos"],
                "base_segundos": item["base"]["segundos"],
                "ft_segundos": item["finetuned_redactor"]["segundos"],
                "base_motivo": audit.get("base_motivo", "[Pendiente revisión]"),
                "ft_motivo": audit.get("ft_motivo", "[Pendiente revisión]"),
            }
        )
    return {
        "total_pares": len(casos),
        "aciertos_base": base_ok if all(c["base_correcto"] is not None for c in casos) else None,
        "aciertos_finetuned": ft_ok if all(c["ft_correcto"] is not None for c in casos) else None,
        "casos": casos,
    }


def _construir_casos_fallo(
    rows_by_qid: dict[str, dict[str, str]],
    veredictos_by_qid: dict[str, dict[str, Any]],
    trazas: dict[str, Any],
    telemetria: dict[str, list[dict[str, Any]]],
    casos_seleccionados: list[str] | None = None,
    descripcion: str | None = None,
) -> dict[str, Any]:
    sel = CASOS_FALLO_SELECCIONADOS if casos_seleccionados is None else casos_seleccionados
    casos: list[dict[str, Any]] = []
    for qid in sel:
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
                "telemetria": telemetria.get(qid, []),
                "traza_completa": _extraer_traza_lista(trazas.get(qid, [])),
            }
        )
    return {
        "descripcion": descripcion
        or (
            "Trazas completas de los 15 fallos estrictos de Deliverable 4 v2 (A100 bf16) bajo "
            "LEEME_PAUTA.md, destacando H03 (CAL-2026-S2-02 fuera del top-6), degradación pura "
            "del Verificador base (H22; además N05 en casos_revision_nuevas20_ft_D4.json) y fallos "
            "mixtos Redactor + Verificador (H04, H06, H21)."
        ),
        "total_casos_documentados": len(casos),
        "casos": casos,
    }


def _escribir_texto_lf(path: Path, contenido: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(contenido)


def _extraer_fuentes_lista(fuentes_str: str) -> list[str]:
    tokens = [tok.strip(" []") for tok in str(fuentes_str or "").replace(",", ";").split(";")]
    return [tok for tok in tokens if tok]


UNIT_CITE_RE = re.compile(r"\[([A-Z]+(?:-[A-Z0-9]+)+)\]")


def auditar_fila_determinista(row: dict[str, Any], corpus_ids: set[str]) -> dict[str, Any]:
    """Ejecuta comprobaciones automáticas y reproducibles sobre una salida del sistema."""
    resp = str(row.get("respuesta_sistema", "") or "")
    citas = UNIT_CITE_RE.findall(resp)
    fuentes_traidas = _extraer_fuentes_lista(row.get("fuentes_traidas", ""))
    fuentes_set = set(fuentes_traidas)

    citas_inexistentes = sorted({c for c in citas if c not in corpus_ids})
    citas_fuera_evidencia = sorted(
        {c for c in citas if c in corpus_ids and fuentes_set and c not in fuentes_set}
    )
    formato_ok = all(
        etq in resp for etq in ("Respuesta:", "Condiciones o límites:", "Fuente:")
    )
    tiene_no_aplica = bool(
        re.search(r"Condiciones o l[íi]mites:\s*No aplica", resp, flags=re.IGNORECASE)
    )
    resp_lower = resp.lower()
    es_abstencion = any(
        frase in resp_lower
        for frase in (
            "no se puede determinar",
            "no es posible determinar",
            "no existe en la normativa",
            "no está regulad",
            "no se encuentra regulad",
            "información insuficiente",
            "premisa falsa",
            "no contiene información",
        )
    )
    error_ejecucion = bool(str(row.get("error", "")).strip()) or (not resp.strip())
    alertas: list[str] = []
    if citas_inexistentes:
        alertas.append("cita_inexistente_corpus")
    if citas_fuera_evidencia:
        alertas.append("cita_fuera_de_evidencia")
    if not citas and not es_abstencion:
        alertas.append("sin_citas")
    if not formato_ok:
        alertas.append("formato_incompleto")
    if error_ejecucion:
        alertas.append("error_ejecucion")
    if str(row.get("aprobado_verificador", "")).strip() == "False":
        alertas.append("verificador_aprobado_false")

    return {
        "citas_respuesta": citas,
        "citas_inexistentes_en_corpus": citas_inexistentes,
        "citas_fuera_de_evidencia": citas_fuera_evidencia,
        "formato_3_lineas_ok": formato_ok,
        "tiene_condicion_no_aplica": tiene_no_aplica,
        "es_abstencion": es_abstencion,
        "error_ejecucion": error_ejecucion,
        "alertas_automaticas": alertas,
    }


def _resolver_rutas_por_csv(eval_dir: Path, csv_path: Path) -> tuple[Path, Path, Path, str]:
    stem = csv_path.stem
    if stem == "resultados_agentes_D4":
        return (
            eval_dir / "trazas_D4.json",
            eval_dir / "telemetria_llamadas.json",
            eval_dir / "comparativa_base_vs_finetuned.json",
            "D4",
        )
    sufijo = stem[len("resultados_") :] if stem.startswith("resultados_") else stem
    return (
        eval_dir / f"trazas_{sufijo}.json",
        eval_dir / f"telemetria_{sufijo}.json",
        eval_dir / f"comparativa_{sufijo}.json",
        sufijo,
    )


def generar_auditoria_general(
    eval_dir: Path = EVAL_DIR,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    resultados_csv: Path | None = None,
    trazas_json: Path | None = None,
    telemetria_json: Path | None = None,
    comparativa_json: Path | None = None,
    control_csv: Path | None = None,
    prefijo_salida: str = "",
    revisor: str = "[Pendiente revisor]",
) -> dict[str, Any]:
    """Audita cualquier corrida (v2 FT, Control Base 75 o Nuevas 20) sin veredictos fijos."""
    csv_in = resultados_csv or (eval_dir / "resultados_agentes_D4.csv")
    if not csv_in.is_file():
        raise FileNotFoundError(f"No existe CSV de resultados: {csv_in}")

    trazas_def, tel_def, comp_def, sufijo_def = _resolver_rutas_por_csv(eval_dir, csv_in)
    trazas_path = trazas_json or trazas_def
    tel_path = telemetria_json or tel_def
    comp_path = comparativa_json or comp_def
    sufijo = prefijo_salida.strip().rstrip("_") or sufijo_def

    corpus_ids = _cargar_corpus_ids(corpus_path)
    csv_raw_lf = csv_in.read_bytes().replace(b"\r\n", b"\n")
    csv_lf_sha = hashlib.sha256(csv_raw_lf).hexdigest()
    audit_reg = _REGISTRO_AUDITORIA_GENERAL_POR_SHA.get(csv_lf_sha)
    fallos_reg: dict[str, dict[str, Any]] | None = audit_reg[0] if audit_reg else None
    revisor_efectivo = (
        audit_reg[1]
        if (audit_reg and revisor == "[Pendiente revisor]")
        else revisor
    )

    with csv_in.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    trazas = (
        json.loads(trazas_path.read_text(encoding="utf-8"))
        if trazas_path.is_file()
        else {}
    )
    telemetria = (
        json.loads(tel_path.read_text(encoding="utf-8"))
        if tel_path.is_file()
        else {}
    )
    comparativa = (
        json.loads(comp_path.read_text(encoding="utf-8"))
        if comp_path.is_file()
        else []
    )

    telemetria_resumen = (
        _verificar_telemetria(telemetria, rows)
        if telemetria
        else {
            "total_consultas": len(rows),
            "llamadas_modelo_totales": sum(int(r.get("llamadas_modelo") or 0) for r in rows),
            "llamadas_por_pregunta": round(
                sum(int(r.get("llamadas_modelo") or 0) for r in rows) / max(1, len(rows)),
                2,
            ),
            "violaciones_aislamiento_lora": 0,
            "segundos_totales": round(sum(float(r.get("segundos") or 0.0) for r in rows), 2),
        }
    )

    rows_auditados: list[dict[str, Any]] = []
    detalles_por_qid: list[dict[str, Any]] = []
    por_set: dict[str, dict[str, Any]] = {}
    por_cat: dict[str, dict[str, Any]] = {}
    casos_revisar: list[dict[str, Any]] = []

    for row in rows:
        qid = f"{row['set']}:{row['id']}"
        det = auditar_fila_determinista(row, corpus_ids)
        corr_raw = str(row.get("correcto", "")).strip()
        corr_val: int | None = int(corr_raw) if corr_raw in {"0", "1"} else None
        reg_fallo = fallos_reg.get(qid) if fallos_reg is not None else None
        if corr_val is None and fallos_reg is not None:
            corr_val = 0 if reg_fallo is not None else 1
            corr_raw = str(corr_val)

        nuevo_row = dict(row)
        nuevo_row["correcto"] = corr_raw if corr_val is not None else ""
        rows_auditados.append(nuevo_row)

        for grupo, mapa in ((row["set"], por_set), (row.get("categoria", "sin_cat"), por_cat)):
            b = mapa.setdefault(
                grupo,
                {
                    "total": 0,
                    "evaluadas_humanamente": 0,
                    "pendientes_revision_humana": 0,
                    "aciertos": 0,
                    "alertas_citas": 0,
                    "formato_3_lineas_ok": 0,
                    "con_no_aplica": 0,
                    "ciclos_gt1": 0,
                    "segundos_totales": 0.0,
                },
            )
            b["total"] += 1
            if corr_val is None:
                b["pendientes_revision_humana"] += 1
            else:
                b["evaluadas_humanamente"] += 1
                b["aciertos"] += corr_val
            if det["citas_inexistentes_en_corpus"] or det["citas_fuera_de_evidencia"]:
                b["alertas_citas"] += 1
            if det["formato_3_lineas_ok"]:
                b["formato_3_lineas_ok"] += 1
            if det["tiene_condicion_no_aplica"]:
                b["con_no_aplica"] += 1
            if int(row.get("ciclos") or 0) > 1:
                b["ciclos_gt1"] += 1
            b["segundos_totales"] = round(b["segundos_totales"] + float(row.get("segundos") or 0.0), 2)

        traza_obj = trazas.get(qid, {}) if isinstance(trazas, dict) else {}
        traza_lista = _extraer_traza_lista(traza_obj)
        det_item = {
            "qid": qid,
            "set": row["set"],
            "id": row["id"],
            "categoria": row.get("categoria", ""),
            "correcto_humano": corr_val,
            "revision_humana_pendiente": corr_val is None,
            "revisor": revisor_efectivo if corr_val is not None else "[Pendiente revisor]",
            "aprobado_verificador": row.get("aprobado_verificador") == "True",
            "ciclos": int(row.get("ciclos") or 0),
            "segundos": float(row.get("segundos") or 0.0),
            "tipo_fallo": reg_fallo.get("tipo") if reg_fallo else None,
            "causa_raiz": reg_fallo.get("causa_raiz") if reg_fallo else None,
            "motivo_auditoria": (
                reg_fallo["motivo"]
                if reg_fallo
                else (
                    "Respuesta correcta y respaldada por la evidencia bajo LEEME_PAUTA.md."
                    if corr_val == 1
                    else None
                )
            ),
            **det,
        }
        detalles_por_qid.append(det_item)
        if corr_val == 0 or det["alertas_automaticas"]:
            casos_revisar.append(
                {
                    **det_item,
                    "pregunta": row.get("pregunta", ""),
                    "gold_dato": row.get("gold_dato", ""),
                    "gold_fuente": row.get("gold_fuente", ""),
                    "respuesta_final": row.get("respuesta_sistema", ""),
                    "traza_completa": traza_lista,
                    "telemetria": telemetria.get(qid, []) if isinstance(telemetria, dict) else [],
                }
            )

    for mapa in (por_set, por_cat):
        for b in mapa.values():
            ev = b["evaluadas_humanamente"]
            b["porcentaje_humano"] = round(100.0 * b["aciertos"] / ev, 1) if ev > 0 else None
            b["segundos_promedio"] = round(b["segundos_totales"] / max(1, b["total"]), 2)

    comparativa_control = None
    if control_csv is not None and control_csv.is_file():
        ctrl_lf_sha = hashlib.sha256(control_csv.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        ctrl_reg = _REGISTRO_AUDITORIA_GENERAL_POR_SHA.get(ctrl_lf_sha)
        ctrl_fallos = ctrl_reg[0] if ctrl_reg else None
        with control_csv.open("r", encoding="utf-8", newline="") as f:
            ctrl_rows = list(csv.DictReader(f))
        ctrl_by_qid = {f"{r['set']}:{r['id']}": r for r in ctrl_rows}
        pares = []
        cambios = 0
        ctrl_llam = 0
        ctrl_seg = 0.0
        ctrl_citas_mal = 0
        ctrl_no_aplica = 0
        ctrl_ok = 0
        ctrl_eval = 0
        ft_eval_pares = 0
        ft_ok_pares = 0
        det_by_qid = {d["qid"]: d for d in detalles_por_qid}
        for row in rows:
            qid = f"{row['set']}:{row['id']}"
            cr = ctrl_by_qid.get(qid)
            if cr is None:
                continue
            det_c = auditar_fila_determinista(cr, corpus_ids)
            det_ft = det_by_qid[qid]
            ctrl_llam += int(cr.get("llamadas_modelo") or 0)
            ctrl_seg += float(cr.get("segundos") or 0.0)
            if det_c["citas_inexistentes_en_corpus"] or det_c["citas_fuera_de_evidencia"]:
                ctrl_citas_mal += 1
            if det_c["tiene_condicion_no_aplica"]:
                ctrl_no_aplica += 1
            cc_raw = str(cr.get("correcto", "")).strip()
            ctrl_val: int | None = int(cc_raw) if cc_raw in {"0", "1"} else None
            if ctrl_val is None and ctrl_fallos is not None:
                ctrl_val = 0 if qid in ctrl_fallos else 1
            if ctrl_val is not None:
                ctrl_eval += 1
                ctrl_ok += ctrl_val
            if det_ft["correcto_humano"] is not None:
                ft_eval_pares += 1
                ft_ok_pares += int(det_ft["correcto_humano"])
            distinta = str(row.get("respuesta_sistema", "")).strip() != str(
                cr.get("respuesta_sistema", "")
            ).strip()
            if distinta:
                cambios += 1
            pares.append(
                {
                    "qid": qid,
                    "categoria": row.get("categoria", ""),
                    "respuesta_distinta": distinta,
                    "control_correcto": ctrl_val,
                    "ft_correcto": det_ft["correcto_humano"],
                    "control_ciclos": int(cr.get("ciclos") or 0),
                    "ft_ciclos": int(row.get("ciclos") or 0),
                    "control_llamadas": int(cr.get("llamadas_modelo") or 0),
                    "ft_llamadas": int(row.get("llamadas_modelo") or 0),
                    "control_alertas": det_c["alertas_automaticas"],
                    "ft_alertas": det_ft["alertas_automaticas"],
                }
            )
        comparativa_control = {
            "control_csv": control_csv.name,
            "preguntas_emparejadas": len(pares),
            "respuestas_distintas_ft_vs_control": cambios,
            "control_llamadas_totales": ctrl_llam,
            "ft_llamadas_totales": sum(int(r.get("llamadas_modelo") or 0) for r in rows),
            "control_segundos_totales": round(ctrl_seg, 2),
            "ft_segundos_totales": round(sum(float(r.get("segundos") or 0.0) for r in rows), 2),
            "control_alertas_citas": ctrl_citas_mal,
            "ft_alertas_citas": sum(
                1
                for d in detalles_por_qid
                if d["citas_inexistentes_en_corpus"] or d["citas_fuera_de_evidencia"]
            ),
            "control_no_aplica": ctrl_no_aplica,
            "ft_no_aplica": sum(1 for d in detalles_por_qid if d["tiene_condicion_no_aplica"]),
            "control_evaluadas_humanamente": ctrl_eval,
            "control_aciertos_humanos": ctrl_ok if ctrl_eval > 0 else None,
            "ft_evaluadas_humanamente": ft_eval_pares,
            "ft_aciertos_humanos": ft_ok_pares if ft_eval_pares > 0 else None,
            "pares": pares,
        }

    if sufijo == "D4":
        csv_out = eval_dir / "resultados_agentes_D4_auditados.csv"
        aud_out = eval_dir / "auditoria_D4.json"
        fallos_out = eval_dir / "casos_fallo_y_regresion.json"
    else:
        csv_out = eval_dir / f"resultados_{sufijo}_auditados.csv"
        aud_out = eval_dir / f"auditoria_{sufijo}.json"
        fallos_out = eval_dir / f"casos_revision_{sufijo}.json"

    with csv_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows_auditados)

    eval_humanas = sum(b["evaluadas_humanamente"] for b in por_set.values())
    aciertos_tot = sum(b["aciertos"] for b in por_set.values())
    comp_inline_resumen = (
        _construir_resumen_comparativa(comparativa, comp_map=AUDITORIA_COMPARATIVA_N20_V2)
        if (isinstance(comparativa, list) and comparativa and all(c.get("qid") in AUDITORIA_COMPARATIVA_N20_V2 for c in comparativa))
        else None
    )
    auditoria = {
        "modo": "auditoria_v2_pauta_estricta" if fallos_reg is not None else "auditoria_general_sin_dict_fijo",
        "fuente_csv": csv_in.name,
        "condicion": rows[0].get("condicion", "") if rows else "",
        "total_preguntas": len(rows),
        "evaluadas_humanamente": eval_humanas,
        "pendientes_revision_humana": len(rows) - eval_humanas,
        "aciertos_humanos": aciertos_tot if eval_humanas > 0 else None,
        "porcentaje_humano": round(100.0 * aciertos_tot / eval_humanas, 1)
        if eval_humanas > 0
        else None,
        "revisor": revisor_efectivo if eval_humanas > 0 else revisor,
        "resumen_por_set": por_set,
        "resumen_por_categoria": por_cat,
        "chequeos_deterministas": {
            "total_con_citas_inexistentes": sum(
                1 for d in detalles_por_qid if d["citas_inexistentes_en_corpus"]
            ),
            "total_con_citas_fuera_de_evidencia": sum(
                1 for d in detalles_por_qid if d["citas_fuera_de_evidencia"]
            ),
            "total_formato_3_lineas_ok": sum(
                1 for d in detalles_por_qid if d["formato_3_lineas_ok"]
            ),
            "total_con_no_aplica": sum(
                1 for d in detalles_por_qid if d["tiene_condicion_no_aplica"]
            ),
            "total_abstenciones_detectadas": sum(
                1 for d in detalles_por_qid if d["es_abstencion"]
            ),
            "total_errores_ejecucion": sum(
                1 for d in detalles_por_qid if d["error_ejecucion"]
            ),
        },
        "telemetria_y_aislamiento": telemetria_resumen,
        "comparativa_control_base_vs_ft": comparativa_control,
        "comparativa_inline": comparativa if isinstance(comparativa, list) else [],
        "comparativa_inline_auditada": comp_inline_resumen,
        "detalles": detalles_por_qid,
    }
    _escribir_texto_lf(aud_out, json.dumps(auditoria, ensure_ascii=False, indent=2) + "\n")
    _escribir_texto_lf(
        fallos_out,
        json.dumps(
            {
                "total_casos_con_alerta_o_fallo": len(casos_revisar),
                "casos": casos_revisar,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    return auditoria


_REGISTRO_AUDITORIA_75: dict[str, dict[str, Any]] = {
    V1_LEGACY_CSV_LF_SHA256: {
        "version_corrida": "v1_archivada",
        "fallos": FALLOS_ESTRICTOS_D4_V1,
        "aprob_false_ok": CASOS_APROB_FALSE_CORRECTOS_V1,
        "comp6": AUDITORIA_COMPARATIVA_6_V1,
        "casos_fallo": CASOS_FALLO_SELECCIONADOS_V1,
        "evaluadores": "Álvaro Contreras y Pablo Cortés (criterios LEEME_PAUTA.md) con auditoría externa de par",
        "errores_d3_resueltos_nucleo": [
            "congelado_50:36 (contenido corregido, cambia ID cita)",
            "dificil_25:H18 (contenido y RG-ART-033 corregidos; falla cita extra P01)",
        ],
        "descripcion_fallos": (
            "Trazas completas de los fallos estrictos de Deliverable 4 (v1 archivada) bajo LEEME_PAUTA.md."
        ),
    },
    V2_FT_75_CSV_LF_SHA256: {
        "version_corrida": "v2_a100_bf16",
        "fallos": FALLOS_ESTRICTOS_D4_V2,
        "aprob_false_ok": CASOS_APROB_FALSE_CORRECTOS_V2,
        "comp6": AUDITORIA_COMPARATIVA_6_V2,
        "casos_fallo": CASOS_FALLO_SELECCIONADOS_V2,
        "evaluadores": (
            "Pablo Cortés + auditoría sistemática asistida por IA (LEEME_PAUTA.md v2; "
            "pendiente revisión par y VoBo de Álvaro Contreras)"
        ),
        "errores_d3_resueltos_nucleo": [],
        "descripcion_fallos": (
            "Trazas completas de los 15 fallos estrictos de Deliverable 4 v2 (A100 bf16, 60/75) "
            "bajo LEEME_PAUTA.md, destacando H03 (CAL-2026-S2-02 fuera del top-6), degradación pura "
            "del Verificador base (H22; además N05 en casos_revision_nuevas20_ft_D4.json) y fallos "
            "mixtos Redactor + Verificador (H04, H06, H21)."
        ),
    },
}


def generar_auditoria(
    eval_dir: Path = EVAL_DIR,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    d3_veredictos_path: Path = DEFAULT_D3_VEREDICTOS_PATH,
    d3_csv_path: Path = DEFAULT_D3_CSV_PATH,
    diagnostico_d3_path: Path = DEFAULT_DIAGNOSTICO_D3_PATH,
) -> dict[str, Any]:
    """Genera auditoría estricta para corridas v1/v2 conocidas o delega a auditoría general."""
    csv_in = eval_dir / "resultados_agentes_D4.csv"
    cfg_reg: dict[str, Any] | None = None
    if csv_in.is_file():
        sha_actual = hashlib.sha256(
            csv_in.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        cfg_reg = _REGISTRO_AUDITORIA_75.get(sha_actual)
        if cfg_reg is None:
            return generar_auditoria_general(eval_dir=eval_dir, corpus_path=corpus_path)
    else:
        cfg_reg = _REGISTRO_AUDITORIA_75[V2_FT_75_CSV_LF_SHA256]

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
    rows_auditados, veredictos = _auditar_casos(
        rows,
        d3_casos,
        corpus_ids,
        fallos_dict=cfg_reg["fallos"],
        aprob_false_ok=cfg_reg["aprob_false_ok"],
    )

    csv_out = eval_dir / "resultados_agentes_D4_auditados.csv"
    with csv_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
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

    control_csv_path = eval_dir / "resultados_control_base_D4.csv"
    comparativa_control_75: dict[str, Any] | None = None
    if control_csv_path.is_file():
        ctrl_lf_sha = hashlib.sha256(
            control_csv_path.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        ctrl_reg = _REGISTRO_AUDITORIA_GENERAL_POR_SHA.get(ctrl_lf_sha)
        ctrl_fallos = ctrl_reg[0] if ctrl_reg else None
        with control_csv_path.open("r", encoding="utf-8", newline="") as f:
            ctrl_rows = list(csv.DictReader(f))
        ctrl_by_qid = {f"{r['set']}:{r['id']}": r for r in ctrl_rows}
        ctrl_cong_ok = 0
        ctrl_dif_ok = 0
        ctrl_eval = 0
        solo_base_gana: list[str] = []
        solo_ft_gana: list[str] = []
        for r in rows_auditados:
            qid = f"{r['set']}:{r['id']}"
            cr = ctrl_by_qid.get(qid)
            if cr is None:
                continue
            cc_raw = str(cr.get("correcto", "")).strip()
            c_ok: int | None = int(cc_raw) if cc_raw in {"0", "1"} else None
            if c_ok is None and ctrl_fallos is not None:
                c_ok = 0 if qid in ctrl_fallos else 1
            if c_ok is not None:
                ctrl_eval += 1
                if r["set"] == "congelado_50":
                    ctrl_cong_ok += c_ok
                else:
                    ctrl_dif_ok += c_ok
                ft_ok_row = int(r["correcto"])
                if ft_ok_row == 1 and c_ok == 0:
                    solo_ft_gana.append(qid)
                elif ft_ok_row == 0 and c_ok == 1:
                    solo_base_gana.append(qid)
        comparativa_control_75 = {
            "control_csv": control_csv_path.name,
            "control_llamadas_totales": sum(int(cr.get("llamadas_modelo") or 0) for cr in ctrl_rows),
            "control_segundos_totales": round(sum(float(cr.get("segundos") or 0.0) for cr in ctrl_rows), 2),
            "control_ciclos_gt1": sum(1 for cr in ctrl_rows if int(cr.get("ciclos") or 0) > 1),
            "control_congelado_50_ok": ctrl_cong_ok if ctrl_eval > 0 else None,
            "control_dificil_25_ok": ctrl_dif_ok if ctrl_eval > 0 else None,
            "control_global_75_ok": (ctrl_cong_ok + ctrl_dif_ok) if ctrl_eval > 0 else None,
            "ft_gana_a_control_qids": solo_ft_gana,
            "control_gana_a_ft_qids": solo_base_gana,
            "balance_neto_ft_menos_control": (len(solo_ft_gana) - len(solo_base_gana)) if ctrl_eval > 0 else None,
        }

    auditoria = {
        "version_corrida": cfg_reg["version_corrida"],
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
            "errores_d3_resueltos_en_nucleo_p36_h18": cfg_reg["errores_d3_resueltos_nucleo"],
        },
        "comparativa_control_base_vs_ft": comparativa_control_75,
        "telemetria_y_aislamiento": telemetria_resumen,
        "desglose_por_categoria": por_categoria,
        "trazabilidad_calificacion": {
            "evaluadores": cfg_reg["evaluadores"],
            "nota_nucleo_equivalente": (
                "El criterio relajado sin Regla 3/P01 también elevaría a D3 v6 "
                "(congelado_50:13 y dificil_25:H18 eran fallos P01 en D3: 66+2 = 68/75), "
                "por lo que no debe usarse como ventaja unilateral de D4 sobre D3."
            ),
        },
        "comparativa_controlada_6_casos": _construir_resumen_comparativa(
            comparativa, comp_map=cfg_reg["comp6"]
        ),
        "veredictos": veredictos,
    }

    _escribir_texto_lf(
        eval_dir / "auditoria_D4.json",
        json.dumps(auditoria, ensure_ascii=False, indent=2) + "\n",
    )

    casos_fallo = _construir_casos_fallo(
        rows_by_qid,
        ver_by_qid,
        trazas,
        telemetria,
        casos_seleccionados=cfg_reg["casos_fallo"],
        descripcion=cfg_reg["descripcion_fallos"],
    )
    _escribir_texto_lf(
        eval_dir / "casos_fallo_y_regresion.json",
        json.dumps(casos_fallo, ensure_ascii=False, indent=2) + "\n",
    )
    return auditoria


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera auditoría y trazas de fallo D4.")
    parser.add_argument("--eval-dir", type=Path, default=EVAL_DIR)
    parser.add_argument("--resultados-csv", type=Path, default=None)
    parser.add_argument("--control-csv", type=Path, default=None)
    parser.add_argument("--trazas-json", type=Path, default=None)
    parser.add_argument("--telemetria-json", type=Path, default=None)
    parser.add_argument("--comparativa-json", type=Path, default=None)
    parser.add_argument("--prefijo-salida", type=str, default="")
    parser.add_argument("--revisor", type=str, default="[Pendiente revisor]")
    parser.add_argument("--todos-v2", action="store_true")
    args = parser.parse_args()

    if args.resultados_csv or args.control_csv or args.prefijo_salida:
        res = generar_auditoria_general(
            eval_dir=args.eval_dir,
            resultados_csv=args.resultados_csv,
            trazas_json=args.trazas_json,
            telemetria_json=args.telemetria_json,
            comparativa_json=args.comparativa_json,
            control_csv=args.control_csv,
            prefijo_salida=args.prefijo_salida,
            revisor=args.revisor,
        )
    else:
        res = generar_auditoria(eval_dir=args.eval_dir)
        corridas_extra = (
            ("resultados_control_base_D4.csv", None, "control_base_D4"),
            ("resultados_nuevas20_ft_D4.csv", "resultados_nuevas20_base_D4.csv", "nuevas20_ft_D4"),
            ("resultados_nuevas20_base_D4.csv", None, "nuevas20_base_D4"),
        )
        for csv_name, ctrl_name, pref in corridas_extra:
            csv_p = args.eval_dir / csv_name
            if csv_p.is_file():
                ctrl_p = (args.eval_dir / ctrl_name) if ctrl_name else None
                generar_auditoria_general(
                    eval_dir=args.eval_dir,
                    resultados_csv=csv_p,
                    control_csv=ctrl_p if (ctrl_p and ctrl_p.is_file()) else None,
                    prefijo_salida=pref,
                    revisor=args.revisor,
                )

    if "resumen_global" in res:
        rg = res["resumen_global"]
        ver = res.get("version_corrida", "D4")
        print(
            f"D4 estricto ({ver}): {rg['congelado_50']['aciertos_estrictos']}/50 congelado, "
            f"{rg['dificil_25']['aciertos_estrictos']}/25 dificil "
            f"({rg['global_75']['aciertos_estrictos']}/75 = {rg['global_75']['porcentaje_estricto']}%) | "
            f"violaciones LoRA: {res['telemetria_y_aislamiento']['violaciones_aislamiento_lora']}"
        )
    else:
        ch = res["chequeos_deterministas"]
        print(
            f"Auditoría general ({res['fuente_csv']}): {res['total_preguntas']} preguntas | "
            f"pendientes revisión humana: {res['pendientes_revision_humana']} | "
            f"citas inexistentes={ch['total_con_citas_inexistentes']} | "
            f"citas fuera evidencia={ch['total_con_citas_fuera_de_evidencia']} | "
            f"No aplica={ch['total_con_no_aplica']} | "
            f"violaciones LoRA={res['telemetria_y_aislamiento']['violaciones_aislamiento_lora']}"
        )


if __name__ == "__main__":
    main()
