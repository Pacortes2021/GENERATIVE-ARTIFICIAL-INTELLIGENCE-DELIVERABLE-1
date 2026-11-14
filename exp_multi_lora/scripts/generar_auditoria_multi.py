#!/usr/bin/env python3
"""Auditoría estricta y determinista de las evaluaciones Multi-LoRA y Ablación Red+Ver.

Replica exactamente la metodología de ``Deliverable 4/scripts/generar_auditoria_d4.py``
bajo las reglas de ``Deliverable 3/paquete_25_dificiles/LEEME_PAUTA.md`` (incluyendo
Regla 2 sobre excepciones y Regla 3 / precedente P01 sobre atribuciones en Condiciones):

1. Valida la integridad SHA-256 de los tres CSV crudos emitidos por Colab A100.
2. Verifica cada cita contra ``corpus.json`` y contra ``fuentes_traidas`` (evidencia).
3. Aplica los veredictos auditados pregunta por pregunta para:
   - ``multi_lora_nuevas20`` (20 preguntas nuevas)
   - ``ablacion_red_ver_nuevas20`` (20 preguntas nuevas)
   - ``multi_lora_75`` (``congelado_50`` + ``dificil_25`` = 75 preguntas)
4. Emite los ``resultados_*_auditados.csv``, ``auditoria_*.json`` y
   ``resumen_comparativo_global.json`` consolidando Control Base D4, Solo Redactor D4 v2,
   Ablación Red+Ver y Multi-LoRA (4 agentes).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
EXP_ROOT = SCRIPT_DIR.parent
REPO_ROOT = EXP_ROOT.parent
D3_CORPUS_PATH = REPO_ROOT / "Deliverable 3" / "Deliverable3" / "agentes" / "corpus.json"
D4_EVAL_DIR = REPO_ROOT / "Deliverable 4" / "evaluacion"
DEFAULT_EVAL_DIR = EXP_ROOT / "evaluacion"
ENTRENAMIENTO_DIR = EXP_ROOT / "entrenamiento"

REVISOR_ETIQUETA = (
    "Pablo Cortés + auditoría sistemática asistida por IA "
    "(LEEME_PAUTA.md v2 / D4 estricta)"
)

SHA256_CRUDOS: dict[str, str] = {
    "resultados_multi_lora_nuevas20.csv": (
        "431f5867c60b5c697cf1b08013e11246bd5418034c1a4b21ad488e85de51cc58"
    ),
    "resultados_ablacion_red_ver_nuevas20.csv": (
        "519df03a30ad415271f72d5fee8e4cd5dc07b3e6f243d48d3293fdd914854e3e"
    ),
    "resultados_multi_lora_75.csv": (
        "a47da7a66a1fd1ccdf1d0d29c5b6ceb1ef25c04d109caa391465cc56ff947459"
    ),
}

CITAS_RE = re.compile(r"\[([A-Z0-9-]+)\]")
ABSTENCION_RE = re.compile(
    r"\b(?:no existe|no hay (?:evidencia|información|respaldo)|sin respaldo|"
    r"no se menciona|no figura|no contempla|no establece)\b",
    re.IGNORECASE,
)


def _fallo(
    tipo_fallo: str,
    causa_raiz: str,
    motivo_auditoria: str,
    *,
    solo_condicion_p01: bool = False,
) -> dict[str, Any]:
    """Construye la ficha estándar de un veredicto incorrecto (=0)."""
    return {
        "correcto": 0,
        "solo_condicion_p01": solo_condicion_p01,
        "tipo_fallo": tipo_fallo,
        "causa_raiz": causa_raiz,
        "motivo_auditoria": motivo_auditoria,
    }


def _ok(
    motivo: str = (
        "Respuesta correcta, completa y respaldada por la evidencia bajo LEEME_PAUTA.md."
    ),
) -> dict[str, Any]:
    """Construye la ficha estándar de un veredicto correcto (=1)."""
    return {
        "correcto": 1,
        "solo_condicion_p01": False,
        "tipo_fallo": None,
        "causa_raiz": None,
        "motivo_auditoria": motivo,
    }


# ---------------------------------------------------------------------------
# Veredictos auditados pregunta por pregunta contra corpus.json
# ---------------------------------------------------------------------------

VEREDICTOS_MULTI_LORA_NUEVAS20: dict[tuple[str, str], dict[str, Any]] = {
    ("nuevas_20", "N01"): _fallo(
        "respuesta_incompleta_y_cita_cruzada",
        "redactor",
        "Omite 'los créditos' al responder qué deben establecer los programas de asignaturas en [RG-ART-017] y atribuye la cláusula de horas únicamente a [RG-ART-003-DEF-11] (Regla 5).",
    ),
    ("nuevas_20", "N02"): _ok(),
    ("nuevas_20", "N03"): _ok(
        "Correcta con [RG-ART-053] pese a 3 rechazos falsos del Verificador LoRA por 'No aplica'."
    ),
    ("nuevas_20", "N04"): _ok(),
    ("nuevas_20", "N05"): _ok(
        "Abstención honesta en 1 ciclo declarando que el Art. 6° RI-FI no fija puntaje mínimo; corrige el fallo de Solo Redactor D4."
    ),
    ("nuevas_20", "N06"): _fallo(
        "alucinacion_condicion_p01",
        "redactor",
        "Acierta fechas [CAL-2026-S1-08]/[CAL-2026-S2-07] y suma '2 + 2 = 4 días', pero en Condiciones atribuye a [CAL-2026-S2-04] (Término de Clases: 11 de diciembre) que esos días 'no equivalen a vacaciones escolares ni días de evaluación por cálculo automático' (Regla 3 / P01).",
        solo_condicion_p01=True,
    ),
    ("nuevas_20", "N07"): _fallo(
        "error_aritmetico_fechas",
        "redactor",
        "Suma erróneamente duraciones de los bloques ('5 + 4 = 9 días corridos') en lugar de calcular los 126 días corridos entre el 11 de mayo y el 14 de septiembre.",
    ),
    ("nuevas_20", "N08"): _ok(
        "Acierta con [RG-ART-046] evitando la confusión con Programa de Formación Complementaria (>=24 SCT) que afectó a Solo Redactor D4."
    ),
    ("nuevas_20", "N09"): _ok(),
    ("nuevas_20", "N10"): _fallo(
        "mezcla_normativa_p01",
        "redactor",
        "Atribuye a [RG-ART-047] reglas de [RG-ART-044] sobre reingreso a Primer Año sin validar/convalidar ni reconocer asignaturas y mantener situación en 30 días, y mezcla requisitos de cambio a otra carrera [RG-ART-054] (Regla 3 / P01).",
    ),
    ("nuevas_20", "N11"): _ok(),
    ("nuevas_20", "N12"): _ok(
        "Enrutador LoRA corrige filtro a ['RG'], recupera [RG-ART-036] y [RG-ART-059] en 2 llamadas y responde exactamente Dirección de Servicios Estudiantiles; corrige el fallo persistente de Base, Solo Redactor y Red+Ver."
    ),
    ("nuevas_20", "N13"): _ok(),
    ("nuevas_20", "N14"): _ok(),
    ("nuevas_20", "N15"): _ok(),
    ("nuevas_20", "N16"): _fallo(
        "recuperacion_incompleta_y_autocontradiccion",
        "recuperador",
        "Recuperador LoRA no recupera [CAL-2026-S1-07], [CAL-2026-S1-08] ni [CAL-2026-S2-07]; responde solo feriados nacionales y en Condiciones declara inexistencia para 14–17 de septiembre mientras cita [CAL-2026-S2-06] en el mismo paréntesis.",
    ),
    ("nuevas_20", "N17"): _ok(
        "Enrutador LoRA filtra limpiamente a ['RG'] eliminando el distractor de RI-FI y evita el error P01 [RG-ART-011]/[RI-FI-ART-002] de Solo Redactor D4."
    ),
    ("nuevas_20", "N18"): _ok(
        "Cubre los roles de Secretaría Académica [RG-ART-005], Profesor Encargado al final del período lectivo [RG-ART-012] y plazo transitorio de 90 días hábiles [RG-TRANS-002] sin el error en Condiciones de Solo Redactor D4."
    ),
    ("nuevas_20", "N19"): _fallo(
        "recuperacion_incompleta_regla_5",
        "recuperador",
        "Enrutador LoRA corrige el filtro a ['RI-FI', 'RG'], pero Recuperador LoRA no trae [RG-ART-018]; refuta embarazo [RG-ART-036] pero desvía la segunda parte a abandono de asignaturas [RG-ART-043] sin abordar ni refutar la regla de duración del Art. 18°.",
    ),
    ("nuevas_20", "N20"): _ok(),
}


VEREDICTOS_ABLACION_RED_VER_NUEVAS20: dict[tuple[str, str], dict[str, Any]] = {
    ("nuevas_20", "N01"): _fallo(
        "regresion_verificador_no_aplica",
        "verificador",
        "Ciclo 1 respondía exactamente 'los créditos y las horas de trabajo académico' [RG-ART-017], pero el Verificador LoRA rechaza falsamente por 'Condiciones o límites: No aplica' y en ciclo 2 el Redactor omite 'los créditos' (Regla 5).",
    ),
    ("nuevas_20", "N02"): _ok(),
    ("nuevas_20", "N03"): _ok(
        "Correcta con [RG-ART-053] pese a 3 rechazos falsos del Verificador LoRA por 'No aplica'."
    ),
    ("nuevas_20", "N04"): _ok(),
    ("nuevas_20", "N05"): _ok(
        "Rechaza correctamente la existencia de puntaje mínimo de notas en el Art. 6° RI-FI [RI-FI-ART-006] corrigiendo el fallo de Solo Redactor D4."
    ),
    ("nuevas_20", "N06"): _fallo(
        "error_aritmetico_fechas",
        "redactor",
        "Acierta las 4 fechas pero calcula erróneamente 'sumando 4 + 4 = 8 días en total' en lugar de 4 días (Regla 6).",
    ),
    ("nuevas_20", "N07"): _fallo(
        "error_aritmetico_y_falsa_abstencion",
        "redactor",
        "Calcula erróneamente '4 días inclusive' y '3 días inclusive' (en lugar de 5 y 4) y declara no poder calcular el período entre mayo y septiembre (Reglas 6 y 8).",
    ),
    ("nuevas_20", "N08"): _fallo(
        "confusion_conceptos_p01",
        "redactor",
        "Confunde asignatura complementaria [RG-ART-046] con Programa de Formación Complementaria (>=24 créditos transferibles) [RG-ART-003-DEF-12] exigiendo este último como condición.",
    ),
    ("nuevas_20", "N09"): _fallo(
        "regresion_verificador_no_aplica",
        "verificador",
        "Ciclo 1 respondía correctamente solo con [RG-ART-051]; tras falso rechazo del Verificador LoRA por 'No aplica', en ciclo 2 equipara la suspensión transitoria de alumno regular [RG-ART-003-DEF-20] con la pérdida de condición de alumno de pregrado.",
    ),
    ("nuevas_20", "N10"): _fallo(
        "regla_incompleta_y_mezcla",
        "redactor",
        "Reproduce el fallo de Solo Redactor D4: alude al Programa de Formación Complementaria bajo [RG-ART-047] y mezcla reingreso a Primer Año de [RG-ART-044].",
    ),
    ("nuevas_20", "N11"): _ok(),
    ("nuevas_20", "N12"): _fallo(
        "enrutador_filtro_documento",
        "enrutador",
        "Enrutador base restringe el filtro a ['RI-FI'], dejando 0 fuentes y provocando falsa abstención sobre [RG-ART-036]/[RG-ART-059].",
    ),
    ("nuevas_20", "N13"): _ok(),
    ("nuevas_20", "N14"): _ok(),
    ("nuevas_20", "N15"): _ok(),
    ("nuevas_20", "N16"): _fallo(
        "falsa_abstencion_parcial_regla_8",
        "redactor",
        "Pese a tener [CAL-2026-S1-07] y [CAL-2026-S2-07] en evidencia, declara inexistencia para el 11–15 de mayo y contesta fechas de feriado nacional (21 mayo, 18 sept).",
    ),
    ("nuevas_20", "N17"): _fallo(
        "afirmacion_extra_mal_citada_p01",
        "redactor",
        "Refuta bien [RG-ART-004], pero Condiciones atribuye el texto íntegro de [RI-FI-ART-002] a [RG-ART-011] (Regla 3 / P01).",
        solo_condicion_p01=True,
    ),
    ("nuevas_20", "N18"): _fallo(
        "error_factual_condiciones_p01",
        "redactor",
        "Cubre los tres roles principales, pero Condiciones afirma erróneamente bajo [RG-ART-026] que el Vicedecano resuelve la regularización (resuelve el Profesor Encargado; el Vicedecano conoce la apelación).",
        solo_condicion_p01=True,
    ),
    ("nuevas_20", "N19"): _fallo(
        "enrutador_y_cita_cruzada_p01",
        "enrutador",
        "Enrutador base restringe a ['RI-FI'] excluyendo [RG-ART-018]; además el Redactor atribuye la duración semestral de la Memoria de Título ([RI-FI-ART-029]) al artículo [RG-ART-029] (pérdida por no inscripción).",
    ),
    ("nuevas_20", "N20"): _ok(
        "Abstención correcta con [RG-ART-057] aprobada en 1 ciclo por el Verificador LoRA (corrige el bucle de 3 ciclos de Solo Redactor D4)."
    ),
}


VEREDICTOS_MULTI_LORA_75: dict[tuple[str, str], dict[str, Any]] = {
    ("congelado_50", "1"): _ok(),
    ("congelado_50", "2"): _ok(),
    ("congelado_50", "3"): _ok(),
    ("congelado_50", "4"): _ok(),
    ("congelado_50", "5"): _ok(
        "Identifica la Memoria de Título [RI-FI-ART-029] y las actividades de [RG-ART-003-DEF-10] sin el error P01 en [RI-FI-ART-030] que cometió Solo Redactor D4."
    ),
    ("congelado_50", "6"): _fallo(
        "pregunta_respondida_erronea",
        "redactor",
        "Responde el plazo máximo para entregar calificaciones y pautas (10 días hábiles, [RG-ART-025]) en vez de la anticipación mínima para comunicar evaluaciones (al menos una semana, [RI-FI-ART-010]).",
    ),
    ("congelado_50", "7"): _ok(),
    ("congelado_50", "8"): _ok(
        "Responde exactamente que la renuncia es irrevocable con citas inline [RG-ART-034] y [RI-FI-ART-026] evitando el fallo P01 de [RG-ART-044] de Solo Redactor D4; presenta alerta de formato por omitir la tercera línea literal 'Fuente:' (alerta_formato_sin_fuente)."
    ),
    ("congelado_50", "9"): _ok(),
    ("congelado_50", "10"): _ok(),
    ("congelado_50", "11"): _fallo(
        "omision_excepciones_regla_2",
        "redactor",
        "Acierta el mínimo de 8 créditos [RI-FI-ART-008], pero escribe 'Condiciones o límites: No aplica' omitiendo las excepciones explícitas de término de carrera o falta de requisitos (Regla 2 / precedente P36).",
    ),
    ("congelado_50", "12"): _fallo(
        "mezcla_cita_condiciones_p01",
        "redactor",
        "Acierta menos de 15 créditos al término del 2° semestre [RI-FI-ART-014], pero en Condiciones atribuye a [RI-FI-ART-014] que 'en asignaturas de duración menor a un semestre la Facultad establece el plazo de abandono', regla perteneciente a [RG-ART-043] (Regla 3 / P01).",
        solo_condicion_p01=True,
    ),
    ("congelado_50", "13"): _ok(),
    ("congelado_50", "14"): _ok(),
    ("congelado_50", "15"): _ok(),
    ("congelado_50", "16"): _fallo(
        "inversion_normativa_art_44",
        "redactor",
        "Invierte [RG-ART-044] al afirmar 'salvo que reingrese a la misma carrera sin pérdida de carrera, en cuyo caso no tendrá derecho a validar...', cuando la prohibición de validar rige para todo reingreso a la misma carrera y la ausencia de pérdida solo habilita mantener la situación académica previa; además omite excepción de Primer Año Común bajo 'No aplica'.",
    ),
    ("congelado_50", "17"): _ok(),
    ("congelado_50", "18"): _ok(),
    ("congelado_50", "19"): _ok(),
    ("congelado_50", "20"): _ok(),
    ("congelado_50", "21"): _ok(),
    ("congelado_50", "22"): _ok(),
    ("congelado_50", "23"): _ok(),
    ("congelado_50", "24"): _ok(),
    ("congelado_50", "25"): _fallo(
        "respuesta_incompleta_y_alucinacion_p01",
        "recuperador",
        "No recupera [RI-FI-ART-007] y repite 'prioridades a) y b) del Artículo 7°' [RI-FI-ART-009] sin desglosar atrasadas ni obligatorias reprobadas; además Condiciones inventa una regla de 'horarios coincidentes' atribuida a [RG-ART-003-DEF-13] (Regla 3 / P01).",
    ),
    ("congelado_50", "26"): _fallo(
        "regla_mal_aplicada_art_35",
        "redactor",
        "Exige certificados DAFE y Dirección de Bibliotecas [RG-ART-035] para solicitar reincorporación, cuando [RG-ART-035] rige suspensión y renuncia mientras la reincorporación se rige por [RG-ART-033].",
    ),
    ("congelado_50", "27"): _ok(),
    ("congelado_50", "28"): _fallo(
        "alucinacion_condiciones_tras_ciclo",
        "verificador",
        "En ciclo 2 respondía sin errores usando [RG-ART-029], pero el Verificador LoRA rechaza por 'No aplica' y en ciclo 3 el Redactor añade bajo [RI-FI-ART-007] reglas inexistentes ('no exceder el mínimo de créditos ni atrasarse más del nivel de avance') (Regla 3 / P01).",
        solo_condicion_p01=True,
    ),
    ("congelado_50", "29"): _ok(),
    ("congelado_50", "30"): _ok(),
    ("congelado_50", "31"): _ok(),
    ("congelado_50", "32"): _ok(),
    ("congelado_50", "33"): _ok(),
    ("congelado_50", "34"): _ok(),
    ("congelado_50", "35"): _ok(),
    ("congelado_50", "36"): _ok(
        "Acierta fechas [CAL-2026-S2-01] y mínimo 8 créditos [RI-FI-ART-008] e incorpora excepciones autorizadas por el Vicedecano [RG-ART-042] evitando el falso 'No aplica' de Base y Solo Redactor D4."
    ),
    ("congelado_50", "37"): _ok(),
    ("congelado_50", "38"): _ok(),
    ("congelado_50", "39"): _ok(),
    ("congelado_50", "40"): _ok(),
    ("congelado_50", "41"): _ok(),
    ("congelado_50", "42"): _ok(),
    ("congelado_50", "43"): _ok(),
    ("congelado_50", "44"): _ok(),
    ("congelado_50", "45"): _ok(
        "Rechaza limpiamente la existencia del inciso d) citando a), b) y c) de [RI-FI-ART-014], corrigiendo el título inventado y la mezcla de fuentes de Solo Redactor D4."
    ),
    ("congelado_50", "46"): _fallo(
        "premisa_falsa_no_refutada",
        "redactor",
        "Describe los incisos a) y b) de [RI-FI-ART-025] pero omite declarar que el inciso c) consultado no existe; el Verificador LoRA aprueba el borrador sin exigir refutar la premisa (Regla 7).",
    ),
    ("congelado_50", "47"): _fallo(
        "premisa_falsa_no_refutada",
        "enrutador",
        "Enrutador clasifica como 'factual' en vez de 'premisa_falsa'; el Redactor responde solo el mínimo de 8 créditos [RI-FI-ART-008] sin señalar que el artículo no fija ningún máximo y el Verificador LoRA aprueba indebidamente (Regla 7).",
    ),
    ("congelado_50", "48"): _fallo(
        "premisa_falsa_confundida_con_nota_final",
        "enrutador",
        "Enrutador clasifica como 'factual'; el Redactor responde con la nota final mínima de aprobación general (4,0 en [RG-ART-023]) sin indicar que el Art. 12° RI-FI no fija nota mínima para la Evaluación de Recuperación (Regla 7).",
    ),
    ("congelado_50", "49"): _ok(),
    ("congelado_50", "50"): _ok(),
    ("dificil_25", "H01"): _ok(),
    ("dificil_25", "H02"): _ok(
        "Responde exactamente 4,2 [RI-FI-ART-018] y 5,0 [RI-FI-ART-019] en formato completo corrigiendo la alucinación 'simulink' y omisión de Fuente de Solo Redactor D4."
    ),
    ("dificil_25", "H03"): _fallo(
        "recuperacion_incompleta_y_aritmetica",
        "recuperador",
        "Recuperador LoRA deja fuera [CAL-2026-S2-02] (10 ago) pese a filtro ['CAL']; el Redactor sustituye por 10 de julio [CAL-2026-S1-04] y resta solo los días sin mes ('02 - 09 = -7 días', '04 - 10 = -6 días').",
    ),
    ("dificil_25", "H04"): _fallo(
        "distorsion_y_cita_glosario_p01",
        "redactor",
        "Habla erróneamente de 'seis semestres máximos de permanencia en la carrera' en vez de plazo de egresado para actividades finales [RG-ART-049], y atribuye el párrafo 2 de [RG-ART-049] a la definición [RG-ART-003-DEF-22] (Regla 3 / P01).",
    ),
    ("dificil_25", "H05"): _fallo(
        "ponderacion_invertida",
        "redactor",
        "Invierte los pesos de [RI-FI-ART-030] usando 40 % al promedio del plan y 60 % a la Memoria ('0,4*5,2 + 0,6*6,5 = 5,98 ≈ 6,0' en lugar de 5,72) y el Verificador LoRA lo aprueba.",
    ),
    ("dificil_25", "H06"): _fallo(
        "polaridad_invertida",
        "redactor",
        "Calcula bien 38/4 = 9,5 < 10 pero concluye con polaridad invertida 'No cae en baja académica' [RI-FI-ART-014], aprobado indebidamente por el Verificador LoRA.",
    ),
    ("dificil_25", "H07"): _fallo(
        "cita_formula_p01",
        "redactor",
        "Calcula bien 42/4 = 10,5 > 10 [RI-FI-ART-014], pero en Condiciones atribuye únicamente a [RI-FI-ART-014] la fórmula de cálculo ('totalidad de créditos aprobados por el número de semestres de permanencia') que pertenece a [RG-ART-028] (Regla 3 / P01).",
        solo_condicion_p01=True,
    ),
    ("dificil_25", "H08"): _ok(),
    ("dificil_25", "H09"): _fallo(
        "contradiccion_condiciones_art_32",
        "redactor",
        "Acierta los certificados DAFE y Bibliotecas en Respuesta [RG-ART-035] [RI-FI-ART-025], pero Condiciones afirma falsamente que por salud incompatible 'se suspende automáticamente sin presentar informe [RG-ART-032]', contradiciendo el requisito explícito de informe previo y resolución fundada del Decano.",
        solo_condicion_p01=True,
    ),
    ("dificil_25", "H10"): _ok(),
    ("dificil_25", "H11"): _ok(),
    ("dificil_25", "H12"): _fallo(
        "mezcla_baja_academica_y_no_inscripcion_h12",
        "redactor",
        "Acierta 1 año ante el Comité y apelación al Vicedecano [RG-ART-030], pero agrega apelación negativa ante el Decano que rige Baja Académica y no Baja por no Inscripción (Regla 3 / precedente H12).",
    ),
    ("dificil_25", "H13"): _ok(),
    ("dificil_25", "H14"): _ok(),
    ("dificil_25", "H15"): _ok(),
    ("dificil_25", "H16"): _ok(),
    ("dificil_25", "H17"): _ok(),
    ("dificil_25", "H18"): _ok(),
    ("dificil_25", "H19"): _ok(),
    ("dificil_25", "H20"): _ok(),
    ("dificil_25", "H21"): _ok(
        "Rechaza expresamente la existencia de un máximo fijo y entrega tanto el mínimo (>=8 créditos) como ambas excepciones de [RI-FI-ART-008], superando el fallo de Solo Redactor D4."
    ),
    ("dificil_25", "H22"): _ok(
        "Verificador LoRA aprueba en 1 ciclo la refutación 'No es 4,5: la nota mínima para aprobar es 4,0 [RG-ART-023]', eliminando el rechazo falso del Verificador base que había hecho fallar a Control Base y Solo Redactor D4."
    ),
    ("dificil_25", "H23"): _ok(),
    ("dificil_25", "H24"): _ok(),
    ("dificil_25", "H25"): _ok(
        "Incluye prioridad por créditos aprobados, promedio curricular de Plan Común (2 decimales), orden de preferencias, cupos disponibles, solo asignaturas obligatorias de Primer Año y proceso anual [RI-FI-ART-005] [RI-FI-ART-006], superando a Control Base y Solo Redactor D4."
    ),
}


def sha256_archivo(path: Path) -> str:
    """Calcula el SHA-256 hexadecimal de un archivo."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cargar_corpus_ids(corpus_path: Path = D3_CORPUS_PATH) -> set[str]:
    """Devuelve los IDs válidos del corpus limpio."""
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    return {str(u["id"]) for u in data["unidades"]}


def analizar_fila_determinista(
    fila: dict[str, str],
    corpus_ids: set[str],
    traza_q: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calcula chequeos deterministas de citas, formato, abstención y fallbacks."""
    texto = fila.get("respuesta_sistema") or ""
    citas = CITAS_RE.findall(texto)
    fuentes_set = {
        x.strip() for x in (fila.get("fuentes_traidas") or "").split(";") if x.strip()
    }
    inexistentes = sorted({c for c in citas if c not in corpus_ids})
    fuera_evidencia = sorted({c for c in citas if c in corpus_ids and c not in fuentes_set})

    tiene_resp = "Respuesta:" in texto
    tiene_cond = "Condiciones o límites:" in texto
    tiene_fuente = "Fuente:" in texto
    formato_3_ok = bool(tiene_resp and tiene_cond and tiene_fuente)
    tiene_no_aplica = bool(
        re.search(r"Condiciones o límites:\s*No aplica", texto, re.IGNORECASE)
    )
    es_abstencion = bool(ABSTENCION_RE.search(texto))
    aprobado = str(fila.get("aprobado_verificador", "")).strip().lower() == "true"
    fallbacks = int(float(fila.get("fallbacks") or 0))
    enr_fallback = any(
        s.get("agente") == "enrutador" and bool(s.get("fallback")) for s in traza_q
    )

    alertas: list[str] = []
    if not tiene_fuente:
        alertas.append("formato_sin_linea_fuente")
    if inexistentes:
        alertas.append("cita_inexistente_en_corpus")
    if fuera_evidencia:
        alertas.append("cita_fuera_de_evidencia")
    if not aprobado:
        alertas.append("verificador_aprobado_false")
    if fallbacks > 0 or enr_fallback:
        alertas.append("fallback_enrutamiento")

    return {
        "citas_en_respuesta": citas,
        "citas_inexistentes_en_corpus": inexistentes,
        "citas_fuera_de_evidencia": fuera_evidencia,
        "formato_3_lineas_ok": formato_3_ok,
        "tiene_condicion_no_aplica": tiene_no_aplica,
        "es_abstencion": es_abstencion,
        "enrutador_fallback": enr_fallback,
        "alertas_automaticas": alertas,
    }


def agregar_telemetria(telemetria: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Resume llamadas, tokens y segundos totales y por agente desde telemetría."""
    llamadas_ag: dict[str, int] = defaultdict(int)
    in_tok_ag: dict[str, int] = defaultdict(int)
    out_tok_ag: dict[str, int] = defaultdict(int)
    segs_ag: dict[str, float] = defaultdict(float)

    for eventos in telemetria.values():
        for ev in eventos:
            ag = str(ev["agente"])
            llamadas_ag[ag] += 1
            in_tok_ag[ag] += int(ev.get("input_tokens") or 0)
            out_tok_ag[ag] += int(ev.get("output_tokens") or 0)
            segs_ag[ag] += float(ev.get("segundos") or 0.0)

    total_llamadas = sum(llamadas_ag.values())
    total_segs = round(sum(segs_ag.values()), 2)
    n_q = len(telemetria)
    return {
        "total_consultas": n_q,
        "llamadas_modelo_totales": total_llamadas,
        "llamadas_por_pregunta": round(total_llamadas / n_q, 2) if n_q else 0.0,
        "llamadas_por_agente": dict(llamadas_ag),
        "tokens_entrada_por_agente": dict(in_tok_ag),
        "tokens_salida_por_agente": dict(out_tok_ag),
        "tokens_entrada_totales": sum(in_tok_ag.values()),
        "tokens_salida_totales": sum(out_tok_ag.values()),
        "segundos_por_agente": {k: round(v, 2) for k, v in segs_ag.items()},
        "segundos_totales_telemetria": total_segs,
    }


def _bloque_grupo(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcula estadísticas de exactitud, ciclos y tiempos para un subconjunto."""
    total = len(items)
    aciertos = sum(x["correcto_estricto"] for x in items)
    nucleo = sum(x["correcto_nucleo"] for x in items)
    segs = round(sum(x["segundos"] for x in items), 2)
    return {
        "total": total,
        "aciertos_estrictos": aciertos,
        "porcentaje_estricto": round(100.0 * aciertos / total, 1) if total else 0.0,
        "aciertos_nucleo_sin_condicion_p01": nucleo,
        "porcentaje_nucleo": round(100.0 * nucleo / total, 1) if total else 0.0,
        "aprobadas_verificador": sum(1 for x in items if x["aprobado_verificador"]),
        "formato_3_lineas_ok": sum(1 for x in items if x["formato_3_lineas_ok"]),
        "con_no_aplica": sum(1 for x in items if x["tiene_condicion_no_aplica"]),
        "ciclos_promedio": round(sum(x["ciclos"] for x in items) / total, 2) if total else 0.0,
        "ciclos_gt1": sum(1 for x in items if x["ciclos"] > 1),
        "segundos_totales": segs,
        "segundos_promedio": round(segs / total, 2) if total else 0.0,
    }


def _matriz_verificador(items: list[dict[str, Any]]) -> dict[str, int]:
    """Calcula la alineación del Verificador respecto a la exactitud estricta."""
    return {
        "aprobadas_por_verificador": sum(1 for x in items if x["aprobado_verificador"]),
        "aprobadas_y_correctas": sum(
            1 for x in items if x["aprobado_verificador"] and x["correcto_estricto"] == 1
        ),
        "aprobadas_pero_incorrectas_estricto": sum(
            1 for x in items if x["aprobado_verificador"] and x["correcto_estricto"] == 0
        ),
        "rechazadas_por_verificador": sum(
            1 for x in items if not x["aprobado_verificador"]
        ),
        "rechazadas_pero_correctas": sum(
            1 for x in items if (not x["aprobado_verificador"]) and x["correcto_estricto"] == 1
        ),
        "rechazadas_e_incorrectas": sum(
            1 for x in items if (not x["aprobado_verificador"]) and x["correcto_estricto"] == 0
        ),
    }


def _comparar_contra_referencia(
    veredictos: list[dict[str, Any]],
    ref_csv_path: Path,
    nombre_ref: str,
) -> dict[str, Any]:
    """Calcula emparejamiento pregunta a pregunta contra una corrida de referencia D4."""
    with ref_csv_path.open("r", encoding="utf-8", newline="") as f:
        ref_map = {(r["set"], r["id"]): r for r in csv.DictReader(f)}

    gana_exp: list[str] = []
    pierde_exp: list[str] = []
    empate_1: list[str] = []
    empate_0: list[str] = []

    for item in veredictos:
        key = (item["set"], item["id"])
        ref_row = ref_map[key]
        ref_ok = int(ref_row["correcto"])
        exp_ok = item["correcto_estricto"]
        qid = item["qid"]
        if exp_ok == 1 and ref_ok == 0:
            gana_exp.append(qid)
        elif exp_ok == 0 and ref_ok == 1:
            pierde_exp.append(qid)
        elif exp_ok == 1 and ref_ok == 1:
            empate_1.append(qid)
        else:
            empate_0.append(qid)

    ref_aciertos = sum(
        int(ref_map[(x["set"], x["id"])]["correcto"]) for x in veredictos
    )
    exp_aciertos = sum(x["correcto_estricto"] for x in veredictos)
    return {
        "referencia": nombre_ref,
        "fuente_referencia": str(ref_csv_path.relative_to(REPO_ROOT)),
        "total_emparejadas": len(veredictos),
        "aciertos_referencia": ref_aciertos,
        "aciertos_experimento": exp_aciertos,
        "balance_neto_experimento_menos_ref": exp_aciertos - ref_aciertos,
        "gana_experimento_qids": gana_exp,
        "gana_referencia_qids": pierde_exp,
        "empate_ambos_aciertan": len(empate_1),
        "empate_ambos_fallan_qids": empate_0,
    }


def auditar_corrida(
    *,
    nombre_corrida: str,
    raw_csv_path: Path,
    raw_sha256_esperado: str,
    config_path: Path,
    telemetria_path: Path,
    trazas_path: Path,
    out_csv_path: Path,
    out_json_path: Path,
    veredictos_dict: dict[tuple[str, str], dict[str, Any]],
    corpus_ids: set[str],
    refs_comparacion: dict[str, Path],
    nota_especial: str | None = None,
) -> dict[str, Any]:
    """Ejecuta la auditoría completa de una corrida y escribe CSV/JSON auditados."""
    sha_actual = sha256_archivo(raw_csv_path)
    if sha_actual != raw_sha256_esperado:
        raise ValueError(
            f"SHA-256 inesperado para {raw_csv_path.name}: {sha_actual} != {raw_sha256_esperado}"
        )

    with raw_csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        filas = list(reader)

    claves_csv = {(r["set"], r["id"]) for r in filas}
    claves_reg = set(veredictos_dict.keys())
    if claves_csv != claves_reg:
        raise ValueError(
            f"Desajuste de claves en {raw_csv_path.name}: faltan={sorted(claves_csv - claves_reg)}, "
            f"sobran={sorted(claves_reg - claves_csv)}"
        )

    config = json.loads(config_path.read_text(encoding="utf-8"))
    telemetria = json.loads(telemetria_path.read_text(encoding="utf-8"))
    trazas = json.loads(trazas_path.read_text(encoding="utf-8"))

    filas_auditadas: list[dict[str, str]] = []
    veredictos_lista: list[dict[str, Any]] = []

    for r in filas:
        key = (r["set"], r["id"])
        qid = f"{r['set']}:{r['id']}"
        v = veredictos_dict[key]
        det = analizar_fila_determinista(r, corpus_ids, trazas.get(qid, []))

        fila_out = dict(r)
        fila_out["correcto"] = str(v["correcto"])
        filas_auditadas.append(fila_out)

        veredictos_lista.append(
            {
                "qid": qid,
                "set": r["set"],
                "id": r["id"],
                "categoria": r["categoria"],
                "pregunta": r["pregunta"],
                "correcto_estricto": v["correcto"],
                "correcto_nucleo": 1 if (v["correcto"] == 1 or v["solo_condicion_p01"]) else 0,
                "solo_condicion_p01": v["solo_condicion_p01"],
                "tipo_enrutador": r["tipo_enrutador"],
                "aprobado_verificador": str(r["aprobado_verificador"]).lower() == "true",
                "ciclos": int(float(r["ciclos"])),
                "llamadas_modelo": int(float(r["llamadas_modelo"])),
                "segundos": round(float(r["segundos"]), 2),
                "tipo_fallo": v["tipo_fallo"],
                "causa_raiz": v["causa_raiz"],
                "motivo_auditoria": v["motivo_auditoria"],
                **det,
            }
        )

    out_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with out_csv_path.open("w", encoding="utf-8", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(filas_auditadas)

    por_set: dict[str, list[dict[str, Any]]] = defaultdict(list)
    por_cat: dict[str, list[dict[str, Any]]] = defaultdict(list)
    fallos_por_causa: dict[str, int] = defaultdict(int)
    for item in veredictos_lista:
        por_set[item["set"]].append(item)
        por_cat[item["categoria"]].append(item)
        if item["correcto_estricto"] == 0 and item["causa_raiz"]:
            fallos_por_causa[str(item["causa_raiz"])] += 1

    tel_resumen = agregar_telemetria(telemetria)
    comparativas = {
        k: _comparar_contra_referencia(veredictos_lista, p, k)
        for k, p in refs_comparacion.items()
    }

    payload = {
        "experimento": nombre_corrida,
        "criterio": (
            "Auditoría estricta según Deliverable 3/paquete_25_dificiles/LEEME_PAUTA.md "
            "(incluye Regla 2 excepciones y Regla 3 / precedente P01)."
        ),
        "revisor": REVISOR_ETIQUETA,
        "fuente_csv_crudo": raw_csv_path.name,
        "sha256_csv_crudo": sha_actual,
        "fuente_csv_auditado": out_csv_path.name,
        "configuracion_runtime": config,
        "resumen_global": _bloque_grupo(veredictos_lista),
        "resumen_por_set": {k: _bloque_grupo(v) for k, v in por_set.items()},
        "resumen_por_categoria": {k: _bloque_grupo(v) for k, v in por_cat.items()},
        "aprobacion_interna_vs_exactitud": _matriz_verificador(veredictos_lista),
        "fallos_por_causa_raiz": dict(fallos_por_causa),
        "chequeos_deterministas": {
            "total_con_citas_inexistentes": sum(
                1 for x in veredictos_lista if x["citas_inexistentes_en_corpus"]
            ),
            "total_con_citas_fuera_de_evidencia": sum(
                1 for x in veredictos_lista if x["citas_fuera_de_evidencia"]
            ),
            "total_formato_3_lineas_ok": sum(
                1 for x in veredictos_lista if x["formato_3_lineas_ok"]
            ),
            "total_con_no_aplica": sum(
                1 for x in veredictos_lista if x["tiene_condicion_no_aplica"]
            ),
            "total_abstenciones_detectadas": sum(
                1 for x in veredictos_lista if x["es_abstencion"]
            ),
            "total_fallbacks_enrutador": sum(
                1 for x in veredictos_lista if x["enrutador_fallback"]
            ),
        },
        "telemetria": tel_resumen,
        "comparativas_d4": comparativas,
        "nota_especial": nota_especial,
        "veredictos": veredictos_lista,
    }
    out_json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return payload


def cargar_resumen_entrenamientos(
    entrenamiento_dir: Path = ENTRENAMIENTO_DIR,
) -> dict[str, Any]:
    """Extrae hiperparámetros, tokens y pérdidas finales de los 3 adaptadores nuevos."""
    resumen: dict[str, Any] = {}
    for ag in ("enrutador", "recuperador", "verificador"):
        p = entrenamiento_dir / ag / "training_metrics.json"
        if not p.exists():
            continue
        tm = json.loads(p.read_text(encoding="utf-8"))
        resumen[ag] = {
            "train_ejemplos": tm["datos"]["train_ejemplos"],
            "val_ejemplos": tm["datos"]["val_ejemplos"],
            "truncados_train": tm["datos"]["tokens_train"]["truncados"],
            "truncados_val": tm["datos"]["tokens_val"]["truncados"],
            "pasos_totales": tm["resultados"]["pasos_totales"],
            "tiempo_entrenamiento_min": tm["resultados"]["tiempo_entrenamiento_min"],
            "eval_loss_inicial": tm["resultados"]["eval_loss_inicial"],
            "mejor_eval_loss": tm["resultados"]["mejor_eval_loss"],
            "mejor_step": tm["resultados"]["mejor_step"],
            "train_loss_final_agregada": tm["resultados"]["train_loss_final_agregada"],
            "trainable_params": tm["parametros"]["entrenables_lora"],
            "trainable_pct": tm["parametros"]["porcentaje_entrenable"],
        }
    return resumen


def _resumen_referencia_d4(
    csv_path: Path, tel_path: Path
) -> dict[str, Any]:
    """Calcula métricas resumidas de un CSV auditado de D4 y su telemetría."""
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    por_set: dict[str, dict[str, Any]] = defaultdict(lambda: {"ok": 0, "n": 0})
    for r in rows:
        por_set[r["set"]]["n"] += 1
        por_set[r["set"]]["ok"] += int(r["correcto"])
    for v in por_set.values():
        v["pct"] = round(100.0 * v["ok"] / v["n"], 1) if v["n"] else 0.0

    tel_raw = json.loads(tel_path.read_text(encoding="utf-8"))
    calls_ag: dict[str, int] = defaultdict(int)
    in_tok = 0
    out_tok = 0
    for evs in tel_raw.values():
        if isinstance(evs, list):
            for ev in evs:
                calls_ag[str(ev["agente"])] += 1
                in_tok += int(ev.get("input_tokens") or 0)
                out_tok += int(ev.get("output_tokens") or 0)

    total_calls = sum(calls_ag.values())
    segs = round(sum(float(r["segundos"]) for r in rows), 2)
    return {
        "n": len(rows),
        "aciertos": sum(int(r["correcto"]) for r in rows),
        "porcentaje": round(100.0 * sum(int(r["correcto"]) for r in rows) / len(rows), 1),
        "por_set": dict(por_set),
        "aprobacion_verificador": sum(
            1 for r in rows if str(r["aprobado_verificador"]).lower() == "true"
        ),
        "ciclos_promedio": round(sum(float(r["ciclos"]) for r in rows) / len(rows), 2),
        "llamadas_totales": total_calls,
        "llamadas_por_agente": dict(calls_ag),
        "tokens_entrada_totales": in_tok,
        "tokens_salida_totales": out_tok,
        "segundos_totales": segs,
        "tokens_out_por_segundo": round(out_tok / segs, 2) if segs else 0.0,
    }


def ejecutar_auditoria(
    eval_dir: Path = DEFAULT_EVAL_DIR,
    corpus_path: Path = D3_CORPUS_PATH,
    d4_eval_dir: Path = D4_EVAL_DIR,
    entrenamiento_dir: Path = ENTRENAMIENTO_DIR,
) -> dict[str, Any]:
    """Ejecuta las tres auditorías y genera el resumen comparativo global."""
    corpus_ids = cargar_corpus_ids(corpus_path)

    aud_ml_n20 = auditar_corrida(
        nombre_corrida="multi_lora_4_agentes_nuevas20",
        raw_csv_path=eval_dir / "resultados_multi_lora_nuevas20.csv",
        raw_sha256_esperado=SHA256_CRUDOS["resultados_multi_lora_nuevas20.csv"],
        config_path=eval_dir / "configuracion_multi_lora_nuevas20.json",
        telemetria_path=eval_dir / "telemetria_multi_lora_nuevas20.json",
        trazas_path=eval_dir / "trazas_multi_lora_nuevas20.json",
        out_csv_path=eval_dir / "resultados_multi_lora_nuevas20_auditados.csv",
        out_json_path=eval_dir / "auditoria_multi_lora_nuevas20.json",
        veredictos_dict=VEREDICTOS_MULTI_LORA_NUEVAS20,
        corpus_ids=corpus_ids,
        refs_comparacion={
            "control_base_d4": d4_eval_dir / "resultados_nuevas20_base_D4_auditados.csv",
            "solo_redactor_d4": d4_eval_dir / "resultados_nuevas20_ft_D4_auditados.csv",
        },
    )

    aud_rv_n20 = auditar_corrida(
        nombre_corrida="ablacion_redactor_verificador_nuevas20",
        raw_csv_path=eval_dir / "resultados_ablacion_red_ver_nuevas20.csv",
        raw_sha256_esperado=SHA256_CRUDOS["resultados_ablacion_red_ver_nuevas20.csv"],
        config_path=eval_dir / "configuracion_ablacion_red_ver_nuevas20.json",
        telemetria_path=eval_dir / "telemetria_ablacion_red_ver_nuevas20.json",
        trazas_path=eval_dir / "trazas_ablacion_red_ver_nuevas20.json",
        out_csv_path=eval_dir / "resultados_ablacion_red_ver_nuevas20_auditados.csv",
        out_json_path=eval_dir / "auditoria_ablacion_red_ver_nuevas20.json",
        veredictos_dict=VEREDICTOS_ABLACION_RED_VER_NUEVAS20,
        corpus_ids=corpus_ids,
        refs_comparacion={
            "control_base_d4": d4_eval_dir / "resultados_nuevas20_base_D4_auditados.csv",
            "solo_redactor_d4": d4_eval_dir / "resultados_nuevas20_ft_D4_auditados.csv",
        },
    )

    aud_ml_75 = auditar_corrida(
        nombre_corrida="multi_lora_4_agentes_75",
        raw_csv_path=eval_dir / "resultados_multi_lora_75.csv",
        raw_sha256_esperado=SHA256_CRUDOS["resultados_multi_lora_75.csv"],
        config_path=eval_dir / "configuracion_multi_lora_75.json",
        telemetria_path=eval_dir / "telemetria_multi_lora_75.json",
        trazas_path=eval_dir / "trazas_multi_lora_75.json",
        out_csv_path=eval_dir / "resultados_multi_lora_75_auditados.csv",
        out_json_path=eval_dir / "auditoria_multi_lora_75.json",
        veredictos_dict=VEREDICTOS_MULTI_LORA_75,
        corpus_ids=corpus_ids,
        refs_comparacion={
            "control_base_d4": d4_eval_dir / "resultados_control_base_D4_auditados.csv",
            "solo_redactor_d4": d4_eval_dir / "resultados_agentes_D4_auditados.csv",
        },
        nota_especial=(
            "En congelado_50:8 el contenido y las citas inline ([RG-ART-034] [RI-FI-ART-026]) son correctos "
            "bajo LEEME_PAUTA.md (40/50 en congelado_50, 58/75 global), aunque omite la tercera línea literal "
            "'Fuente:' (formato_3_lineas_ok=False; bajo exigencia estricta de 3 líneas sería 39/50 y 57/75)."
        ),
    )

    d4_base_75 = _resumen_referencia_d4(
        d4_eval_dir / "resultados_control_base_D4_auditados.csv",
        d4_eval_dir / "telemetria_control_base_D4.json",
    )
    d4_red_75 = _resumen_referencia_d4(
        d4_eval_dir / "resultados_agentes_D4_auditados.csv",
        d4_eval_dir / "telemetria_llamadas.json",
    )
    d4_base_n20 = _resumen_referencia_d4(
        d4_eval_dir / "resultados_nuevas20_base_D4_auditados.csv",
        d4_eval_dir / "telemetria_nuevas20_base_D4.json",
    )
    d4_red_n20 = _resumen_referencia_d4(
        d4_eval_dir / "resultados_nuevas20_ft_D4_auditados.csv",
        d4_eval_dir / "telemetria_nuevas20_ft_D4.json",
    )

    global_95 = {
        "control_base_d4": {
            "aciertos": d4_base_75["aciertos"] + d4_base_n20["aciertos"],
            "total": 95,
            "porcentaje": round(
                100.0 * (d4_base_75["aciertos"] + d4_base_n20["aciertos"]) / 95, 1
            ),
        },
        "solo_redactor_d4": {
            "aciertos": d4_red_75["aciertos"] + d4_red_n20["aciertos"],
            "total": 95,
            "porcentaje": round(
                100.0 * (d4_red_75["aciertos"] + d4_red_n20["aciertos"]) / 95, 1
            ),
        },
        "multi_lora_4_agentes": {
            "aciertos": (
                aud_ml_75["resumen_global"]["aciertos_estrictos"]
                + aud_ml_n20["resumen_global"]["aciertos_estrictos"]
            ),
            "total": 95,
            "porcentaje": round(
                100.0
                * (
                    aud_ml_75["resumen_global"]["aciertos_estrictos"]
                    + aud_ml_n20["resumen_global"]["aciertos_estrictos"]
                )
                / 95,
                1,
            ),
        },
    }

    resumen_global = {
        "criterio": aud_ml_75["criterio"],
        "entrenamientos_nuevos": cargar_resumen_entrenamientos(entrenamiento_dir),
        "nuevas_20": {
            "control_base_d4": d4_base_n20,
            "solo_redactor_d4": d4_red_n20,
            "ablacion_red_ver": {
                "aciertos": aud_rv_n20["resumen_global"]["aciertos_estrictos"],
                "n": 20,
                "porcentaje": aud_rv_n20["resumen_global"]["porcentaje_estricto"],
                "telemetria": aud_rv_n20["telemetria"],
                "aprobacion_interna_vs_exactitud": aud_rv_n20[
                    "aprobacion_interna_vs_exactitud"
                ],
                "comparativas_d4": aud_rv_n20["comparativas_d4"],
            },
            "multi_lora_4_agentes": {
                "aciertos": aud_ml_n20["resumen_global"]["aciertos_estrictos"],
                "n": 20,
                "porcentaje": aud_ml_n20["resumen_global"]["porcentaje_estricto"],
                "telemetria": aud_ml_n20["telemetria"],
                "aprobacion_interna_vs_exactitud": aud_ml_n20[
                    "aprobacion_interna_vs_exactitud"
                ],
                "comparativas_d4": aud_ml_n20["comparativas_d4"],
            },
        },
        "benchmark_75_d3": {
            "control_base_d4": d4_base_75,
            "solo_redactor_d4": d4_red_75,
            "multi_lora_4_agentes": {
                "aciertos": aud_ml_75["resumen_global"]["aciertos_estrictos"],
                "n": 75,
                "porcentaje": aud_ml_75["resumen_global"]["porcentaje_estricto"],
                "por_set": aud_ml_75["resumen_por_set"],
                "telemetria": aud_ml_75["telemetria"],
                "aprobacion_interna_vs_exactitud": aud_ml_75[
                    "aprobacion_interna_vs_exactitud"
                ],
                "comparativas_d4": aud_ml_75["comparativas_d4"],
                "nota_especial": aud_ml_75["nota_especial"],
            },
        },
        "consolidado_95_preguntas": global_95,
    }
    (eval_dir / "resumen_comparativo_global.json").write_text(
        json.dumps(resumen_global, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return resumen_global


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera los CSV auditados y reportes JSON de exp_multi_lora."
    )
    parser.add_argument(
        "--evaluacion-dir",
        type=Path,
        default=DEFAULT_EVAL_DIR,
        help="Directorio que contiene los artefactos crudos de evaluación.",
    )
    args = parser.parse_args()
    resumen = ejecutar_auditoria(eval_dir=args.evaluacion_dir.resolve())
    n20 = resumen["nuevas_20"]
    b75 = resumen["benchmark_75_d3"]
    print(
        f"nuevas_20 -> Base={n20['control_base_d4']['aciertos']}/20 | "
        f"SoloRed={n20['solo_redactor_d4']['aciertos']}/20 | "
        f"Red+Ver={n20['ablacion_red_ver']['aciertos']}/20 | "
        f"4-LoRA={n20['multi_lora_4_agentes']['aciertos']}/20"
    )
    print(
        f"75 D3     -> Base={b75['control_base_d4']['aciertos']}/75 | "
        f"SoloRed={b75['solo_redactor_d4']['aciertos']}/75 | "
        f"4-LoRA={b75['multi_lora_4_agentes']['aciertos']}/75 "
        f"(C50={b75['multi_lora_4_agentes']['por_set']['congelado_50']['aciertos_estrictos']}/50, "
        f"H25={b75['multi_lora_4_agentes']['por_set']['dificil_25']['aciertos_estrictos']}/25)"
    )


if __name__ == "__main__":
    main()
