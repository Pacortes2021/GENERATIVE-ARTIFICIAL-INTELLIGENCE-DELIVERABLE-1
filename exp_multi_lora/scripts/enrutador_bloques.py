"""Generador de pares supervisados para el Agente 1 (Enrutador) — Multi-LoRA.

Replica exactamente el formato de entrada/salida de `prompts/01_enrutador.txt`:
- Entrada (`user`): plantilla `01_enrutador.txt` con `{{PREGUNTA}}`
- Salida (`assistant`): JSON compacto `{"tipo": ..., "sub_consultas": [...], "documentos": [...]}`
"""

from __future__ import annotations

import json
import re
from typing import Any

from antifuga_multi import DOCS_VALIDOS, TIPOS_VALIDOS, cd, doc_de_unidad

# Ejemplos adicionales curados sobre unidades limpias (fuera de BLOCKED_UNIT_IDS)
# para reforzar cruces multi-reglamento (`RG` + `RI-FI`, `CAL` + reglamentos) y
# premisas falsas con y sin número de artículo explícito.
EJEMPLOS_ENRUTADOR_EXTRA: list[dict[str, Any]] = [
    # ---- TRAIN (30 ejemplos) ----
    {
        "id": "ENR-X-T01",
        "split": "train",
        "pregunta": "En Ingeniería, ¿cuál es la relación entre el Reglamento Interno FI y el Reglamento General ante materias no previstas en la facultad, y quién preside el Consejo de Carrera?",
        "tipo": "cruce",
        "sub_consultas": [
            "aplicación supletoria del Reglamento General en materias no previstas en Ingeniería",
            "quién preside y cómo se integra el Consejo de Carrera en Ingeniería y RG",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-001", "RI-FI-ART-032", "RG-ART-010"],
    },
    {
        "id": "ENR-X-T02",
        "split": "train",
        "pregunta": "Si repruebo una asignatura por inasistencia justificada o por bajo rendimiento, ¿cómo se gestiona la validación de cursos tomados en intercambio internacional según el Reglamento de Ingeniería y el General?",
        "tipo": "cruce",
        "sub_consultas": [
            "requisitos y trámite ante Vicedecano para validar cursos de intercambio en Ingeniería",
            "registro como carga académica VAL y escala de notas en Reglamento General",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-024", "RG-ART-039", "RG-ART-041"],
    },
    {
        "id": "ENR-X-T03",
        "split": "train",
        "pregunta": "¿Qué organismo designa a los integrantes del Consejo de Carrera en Ingeniería y cuántos representantes estudiantiles incorpora en contraste con la definición general del Reglamento de Pregrado?",
        "tipo": "cruce",
        "sub_consultas": [
            "composición y representantes estudiantiles del Consejo de Carrera en Reglamento Interno FI",
            "funciones y atribuciones generales del Consejo de Carrera en Reglamento General",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-032", "RG-ART-010"],
    },
    {
        "id": "ENR-X-T04",
        "split": "train",
        "pregunta": "¿Qué función cumple el Director de Docencia de la Facultad de Ingeniería respecto de la oferta académica anual y cómo se coordina con la Dirección de Docencia institucional?",
        "tipo": "cruce",
        "sub_consultas": [
            "funciones del Director de Docencia FI y coordinación de oferta académica",
            "rol de la Dirección de Docencia en el Reglamento General",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-033", "RG-ART-007"],
    },
    {
        "id": "ENR-X-T05",
        "split": "train",
        "pregunta": "¿En qué fecha cierra la matrícula para alumnos rezagados del primer semestre 2026 y qué pasa con la inscripción si el estudiante no respondió la Encuesta de Evaluación Docente?",
        "tipo": "cruce",
        "sub_consultas": [
            "fecha cierre de matrícula estudiantes rezagados primer semestre 2026",
            "requisito de Encuesta de Evaluación Docente para inscribir asignaturas",
        ],
        "documentos": ["CAL", "RG"],
        "unidades_referenciadas": ["CAL-2026-S1-01", "RG-ART-042"],
    },
    {
        "id": "ENR-X-T06",
        "split": "train",
        "pregunta": "Cuando un estudiante solicita cambio interno de carrera dentro de Ingeniería o entre facultades UdeC, ¿ante qué autoridad de la facultad se formaliza y cómo se homologan sus ramos?",
        "tipo": "cruce",
        "sub_consultas": [
            "requisitos y trámite en Facultad de Ingeniería para cambio de carrera y homologación",
            "normas de homologación y convalidación en el Reglamento General",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-024", "RG-ART-040", "RG-ART-041"],
    },
    {
        "id": "ENR-X-T07",
        "split": "train",
        "pregunta": "Si el calendario académico fija las vacaciones de invierno del primer semestre 2026, ¿cuántos días corridos duran y se computan para los plazos hábiles de entrega de evaluaciones escritas?",
        "tipo": "cruce",
        "sub_consultas": [
            "fechas de vacaciones de invierno primer semestre 2026 calendario académico",
            "plazos en días hábiles para entrega de evaluaciones escritas y recesos",
        ],
        "documentos": ["CAL", "RG"],
        "unidades_referenciadas": ["CAL-2026-S1-14", "RG-ART-025"],
    },
    {
        "id": "ENR-X-T08",
        "split": "train",
        "pregunta": "¿Es verdad que el Artículo 47° del Reglamento Interno de Ingeniería exige promedio 5,5 para postular a movilidad estudiantil?",
        "tipo": "premisa_falsa",
        "sub_consultas": [
            "verificar existencia del artículo 47 en RI-FI",
            "contenido del artículo 47 RI-FI y normas de movilidad estudiantil",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-024", "RG-ART-039"],
    },
    {
        "id": "ENR-X-T09",
        "split": "train",
        "pregunta": "Me dijeron que el Artículo 82 del Reglamento General autoriza a cursar el PLEV con más de tres asignaturas simultáneas; ¿qué establece realmente ese artículo?",
        "tipo": "premisa_falsa",
        "sub_consultas": [
            "verificar existencia del artículo 82 en RG",
            "contenido del artículo 82 RG",
        ],
        "documentos": ["RG"],
        "unidades_referenciadas": [],
    },
    {
        "id": "ENR-X-T10",
        "split": "train",
        "pregunta": "Un compañero aseguró que en el Período Lectivo Extraordinario de Verano (PLEV) está permitido abandonar asignaturas inscritas dentro de las primeras dos semanas. ¿Eso es correcto?",
        "tipo": "premisa_falsa",
        "sub_consultas": [
            "prohibición o permiso de abandono de asignaturas inscritas en el PLEV",
        ],
        "documentos": ["RG"],
        "unidades_referenciadas": ["RG-ART-043"],
    },
    {
        "id": "ENR-X-T11",
        "split": "train",
        "pregunta": "Según el Anexo de equivalencia de notas, un puntaje de 50 en escala de 1 a 100 permite aprobar la asignatura con nota 4,0. ¿Es cierto?",
        "tipo": "premisa_falsa",
        "sub_consultas": [
            "equivalencia en escala 1,0 a 7,0 para 50 puntos en escala 1 a 100 y nota mínima de aprobación",
        ],
        "documentos": ["RG"],
        "unidades_referenciadas": ["RG-ANEXO-50", "RG-ANEXO-01"],
    },
    {
        "id": "ENR-X-T12",
        "split": "train",
        "pregunta": "En una carrera de Ingeniería con un bloque de 3 ramos que suman 14 SCT, ¿cuántas horas totales de dedicación semestral representan si cada crédito SCT equivale a 27 horas?",
        "tipo": "numerica",
        "sub_consultas": [
            "equivalencia en horas totales por crédito transferible SCT según el glosario del Reglamento General",
        ],
        "documentos": ["RG"],
        "unidades_referenciadas": ["RG-ART-003-DEF-07", "RG-ART-003-DEF-08"],
    },
    {
        "id": "ENR-X-T13",
        "split": "train",
        "pregunta": "Si la entrega de actas del segundo semestre 2026 vence en enero de 2027 según el calendario, ¿cuántos días corridos median entre el término de evaluaciones finales y esa fecha límite?",
        "tipo": "numerica",
        "sub_consultas": [
            "fecha término de evaluaciones finales segundo semestre 2026 calendario",
            "fecha entrega de actas segundo semestre 2026 calendario",
        ],
        "documentos": ["CAL"],
        "unidades_referenciadas": ["CAL-2026-S2-08", "CAL-2026-S2-10"],
    },
    {
        "id": "ENR-X-T14",
        "split": "train",
        "pregunta": "¿Quién designa a los integrantes del Tribunal Calificador o Comisión de Docencia en la Facultad de Ingeniería según su reglamento interno?",
        "tipo": "factual",
        "sub_consultas": [
            "designación e integración de autoridades y comisiones docentes en Reglamento Interno FI",
        ],
        "documentos": ["RI-FI"],
        "unidades_referenciadas": ["RI-FI-ART-032", "RI-FI-ART-033"],
    },
    {
        "id": "ENR-X-T15",
        "split": "train",
        "pregunta": "¿Qué establece el Reglamento Interno de Ingeniería respecto de la validez y alcance de sus disposiciones frente a las facultades del Decano y Consejo Directivo?",
        "tipo": "condicional",
        "sub_consultas": [
            "alcance, ámbito de aplicación y autoridades en Reglamento Interno FI",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-001", "RI-FI-ART-002"],
    },
    {
        "id": "ENR-X-T16",
        "split": "train",
        "pregunta": "Si un estudiante de Ingeniería necesita solicitar revalidación de una asignatura aprobada en el extranjero, ¿qué plazo o criterio general rige en la universidad y qué papel cumple el Vicedecano?",
        "tipo": "cruce",
        "sub_consultas": [
            "trámite ante Vicedecano para validación y revalidación en Reglamento Interno FI",
            "criterios de revalidación y convalidación en Reglamento General",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-024", "RG-ART-039", "RG-ART-040", "RG-ART-041"],
    },
    {
        "id": "ENR-X-T17",
        "split": "train",
        "pregunta": "¿Cuándo se conmemora el Día del Trabajo, el Día de las Glorias Navales y San Pedro y San Pablo en el primer semestre según el Calendario Académico 2026?",
        "tipo": "factual",
        "sub_consultas": [
            "fechas de feriados nacionales de mayo y junio en el primer semestre 2026",
        ],
        "documentos": ["CAL"],
        "unidades_referenciadas": ["CAL-2026-S1-10", "CAL-2026-S1-12", "CAL-2026-S1-13"],
    },
    {
        "id": "ENR-X-T18",
        "split": "train",
        "pregunta": "Cuando un estudiante presenta un impedimento por razones religiosas para asistir a evaluaciones obligatorias, ¿ante quién debe acreditar su pertenencia y qué obligaciones mantiene?",
        "tipo": "condicional",
        "sub_consultas": [
            "impedimento religioso acreditación y condiciones para evaluaciones obligatorias",
        ],
        "documentos": ["RG"],
        "unidades_referenciadas": ["RG-ART-020"],
    },
    {
        "id": "ENR-X-T19",
        "split": "train",
        "pregunta": "Según el Calendario 2026, ¿cuál es el último día de clases del segundo semestre de carreras anuales vs semestrales y cuánto duran las vacaciones de verano?",
        "tipo": "cruce",
        "sub_consultas": [
            "último día de clases segundo semestre 2026 y período de evaluaciones",
            "fechas de receso y vacaciones segundo semestre 2026 en calendario",
        ],
        "documentos": ["CAL"],
        "unidades_referenciadas": ["CAL-2026-S2-08", "CAL-2026-S2-11"],
    },
    {
        "id": "ENR-X-T20",
        "split": "train",
        "pregunta": "Un estudiante afirma que en la escala de títulos de 1,0 a 7,0, una nota 5,0 corresponde al concepto 'Aprobado con Distinción Máxima'. ¿Es correcta esa afirmación?",
        "tipo": "premisa_falsa",
        "sub_consultas": [
            "conceptos y tramos de calificación de títulos para nota 5,0 en Reglamento General",
        ],
        "documentos": ["RG"],
        "unidades_referenciadas": ["RG-ART-048"],
    },
    {
        "id": "ENR-X-T21",
        "split": "train",
        "pregunta": "¿Qué requisitos deben cumplirse para otorgar el grado académico o título profesional en la Facultad de Ingeniería y cómo se ponderan las notas finales en la UdeC?",
        "tipo": "cruce",
        "sub_consultas": [
            "normas de titulación y requisitos en Reglamento Interno FI",
            "normas generales de obtención de grado, título y calificación final en RG",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-028", "RG-ART-048"],
    },
    {
        "id": "ENR-X-T22",
        "split": "train",
        "pregunta": "En el Reglamento Interno de Ingeniería, ¿cómo se regula la permanencia en asignaturas de primer año y qué remisión hace al Reglamento General sobre causales de eliminación?",
        "tipo": "cruce",
        "sub_consultas": [
            "normas de permanencia y deberes del estudiante en Reglamento Interno FI",
            "normas generales sobre matrícula y permanencia en el Reglamento General",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-004", "RI-FI-ART-007"],
    },
    {
        "id": "ENR-X-T23",
        "split": "train",
        "pregunta": "Si un estudiante obtiene 37 puntos sobre 100 en escala de reprobación y 65 puntos en otra evaluación de la escala aprobada, ¿a qué notas en escala 1,0 a 7,0 corresponden?",
        "tipo": "numerica",
        "sub_consultas": [
            "equivalencia en escala 1,0 a 7,0 para 37 puntos reprobados y 65 puntos aprobados en Anexo RG",
        ],
        "documentos": ["RG"],
        "unidades_referenciadas": ["RG-ANEXO-37", "RG-ANEXO-15"],
    },
    {
        "id": "ENR-X-T24",
        "split": "train",
        "pregunta": "¿Qué autoridad debe coordinar las evaluaciones en horario protegido o extraordinario en Ingeniería y qué margen de días hábiles tiene el profesor para entregar los resultados?",
        "tipo": "cruce",
        "sub_consultas": [
            "coordinación de evaluaciones y horarios en Reglamento Interno FI",
            "plazo en días hábiles para entrega y revisión de evaluaciones en Reglamento General",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-015", "RG-ART-025"],
    },
    {
        "id": "ENR-X-T25",
        "split": "train",
        "pregunta": "¿Qué señala el Artículo 52 del Reglamento Interno de Ingeniería respecto de la doble matrícula?",
        "tipo": "premisa_falsa",
        "sub_consultas": [
            "verificar existencia del artículo 52 en RI-FI",
            "contenido del artículo 52 RI-FI",
        ],
        "documentos": ["RI-FI"],
        "unidades_referenciadas": [],
    },
    {
        "id": "ENR-X-T26",
        "split": "train",
        "pregunta": "Cuando el Reglamento General define el Programa de Asignatura y el Programa de Formación Complementaria, ¿qué elementos obligatorios exige incluir y con qué periodicidad se revisan?",
        "tipo": "condicional",
        "sub_consultas": [
            "elementos y revisión periódica del Programa de Asignatura en glosario RG",
            "definición y carga mínima del Programa de Formación Complementaria",
        ],
        "documentos": ["RG"],
        "unidades_referenciadas": ["RG-ART-003-DEF-11", "RG-ART-003-DEF-12", "RG-ART-008"],
    },
    {
        "id": "ENR-X-T27",
        "split": "train",
        "pregunta": "¿Qué días corresponden al feriado del Aniversario de la Universidad de Concepción y a Semana Santa en el Calendario Académico 2026?",
        "tipo": "factual",
        "sub_consultas": [
            "fecha feriado Semana Santa 2026 en calendario",
            "fecha feriado Aniversario de la Universidad de Concepción 2026 en calendario",
        ],
        "documentos": ["CAL"],
        "unidades_referenciadas": ["CAL-2026-S1-09", "CAL-2026-S1-11"],
    },
    {
        "id": "ENR-X-T28",
        "split": "train",
        "pregunta": "Si un estudiante cursa 4 semestres y lleva acumulados 110 SCT, ¿cuántas horas totales equivalen según la definición de horas por crédito del glosario general?",
        "tipo": "numerica",
        "sub_consultas": [
            "equivalencia horaria mínima por crédito SCT en el glosario del Reglamento General",
        ],
        "documentos": ["RG"],
        "unidades_referenciadas": ["RG-ART-003-DEF-08"],
    },
    {
        "id": "ENR-X-T29",
        "split": "train",
        "pregunta": "¿Cómo se articula el Consejo de Carrera con el Jefe de Carrera cuando se propone modificar el plan de estudios en Ingeniería?",
        "tipo": "cruce",
        "sub_consultas": [
            "atribuciones del Consejo de Carrera y Jefatura de Carrera en Reglamento Interno FI",
            "rol del Consejo de Carrera y plan de estudios en Reglamento General",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-032", "RG-ART-010"],
    },
    {
        "id": "ENR-X-T30",
        "split": "train",
        "pregunta": "Me indicaron que el Artículo 95 del Reglamento General prohíbe reincorporarse más de una vez en la carrera; ¿qué dice ese artículo exactamente?",
        "tipo": "premisa_falsa",
        "sub_consultas": [
            "verificar existencia del artículo 95 en RG",
            "contenido del artículo 95 RG",
        ],
        "documentos": ["RG"],
        "unidades_referenciadas": [],
    },
    # ---- VAL (6 ejemplos) ----
    {
        "id": "ENR-X-V01",
        "split": "val",
        "pregunta": "¿Qué organismo evalúa el Plan de Estudio en una carrera y qué representación estudiantil tiene el Consejo de Carrera específico en la Facultad de Ingeniería?",
        "tipo": "cruce",
        "sub_consultas": [
            "organismo que evalúa el Plan de Estudio en el Reglamento General",
            "composición y representación estudiantil del Consejo de Carrera en RI-FI",
        ],
        "documentos": ["RG", "RI-FI"],
        "unidades_referenciadas": ["RG-ART-010", "RI-FI-ART-032"],
    },
    {
        "id": "ENR-X-V02",
        "split": "val",
        "pregunta": "Si un estudiante de Ingeniería aprueba un ramo en intercambio internacional y otro ramo por revalidación externa, ¿qué documentos exige el Vicedecano FI y cuál suma a la carga semestral en el Reglamento General?",
        "tipo": "cruce",
        "sub_consultas": [
            "documentos exigidos por Vicedecano para validar intercambio en RI-FI",
            "diferencia de carga académica entre asignatura validada VAL y revalidada REV en RG",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RI-FI-ART-024", "RG-ART-039", "RG-ART-041"],
    },
    {
        "id": "ENR-X-V03",
        "split": "val",
        "pregunta": "¿En qué fecha terminan las clases de asignaturas anuales en el primer semestre 2026 y cuántos días después comienzan las vacaciones de invierno?",
        "tipo": "numerica",
        "sub_consultas": [
            "término de clases asignaturas anuales primer semestre 2026 calendario",
            "inicio de vacaciones de invierno primer semestre 2026 calendario",
        ],
        "documentos": ["CAL"],
        "unidades_referenciadas": ["CAL-2026-S1-05", "CAL-2026-S1-14"],
    },
    {
        "id": "ENR-X-V04",
        "split": "val",
        "pregunta": "Entiendo que el Artículo 41 del Reglamento Interno de Ingeniería permite convalidar asignaturas cursadas hace más de 15 años sin revisión de programa. ¿Es así?",
        "tipo": "premisa_falsa",
        "sub_consultas": [
            "verificar existencia del artículo 41 en RI-FI",
            "contenido del artículo 41 RI-FI y normas de convalidación en RG",
        ],
        "documentos": ["RI-FI", "RG"],
        "unidades_referenciadas": ["RG-ART-040"],
    },
    {
        "id": "ENR-X-V05",
        "split": "val",
        "pregunta": "En la Facultad de Ingeniería, ¿cómo se regula la asistencia a actividades prácticas o de laboratorio y qué autoridades participan en las solicitudes académicas?",
        "tipo": "condicional",
        "sub_consultas": [
            "normas de asistencia a actividades prácticas y autoridades en Reglamento Interno FI",
        ],
        "documentos": ["RI-FI"],
        "unidades_referenciadas": ["RI-FI-ART-007", "RI-FI-ART-015"],
    },
    {
        "id": "ENR-X-V06",
        "split": "val",
        "pregunta": "¿En qué fecha del año 2027 abre la matrícula de estudiantes nuevos según el Calendario de Docencia 2026?",
        "tipo": "factual",
        "sub_consultas": [
            "fecha de matrícula estudiantes nuevos 2027 en Calendario de Docencia 2026",
        ],
        "documentos": ["CAL"],
        "unidades_referenciadas": [],
    },
]


def _limpiar_subconsulta(texto: str) -> str:
    limpio = re.sub(r"[¿?]+", "", texto).strip(" ,.;:-")
    limpio = re.sub(r"\s+", " ", limpio)
    return limpio


def inferir_documentos_spec(spec: dict[str, Any]) -> list[str]:
    """Determina los documentos probables del plan desde `evidencia_clave` y la pregunta."""
    vistos: list[str] = []
    for uid in spec.get("evidencia_clave") or []:
        d = doc_de_unidad(uid)
        if d not in vistos:
            vistos.append(d)

    p_low = spec["pregunta"].lower()
    for uid in spec.get("inexistentes") or []:
        d = doc_de_unidad(uid)
        if d not in vistos:
            vistos.append(d)

    if any(w in p_low for w in ("calendario", "feriado", "vacaciones", "2026", "2027", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")) and "CAL" not in vistos:
        if spec["estado"] != "suficiente" or not vistos:
            vistos.append("CAL")
    if any(w in p_low for w in ("ingeniería", "ingenieria", "vicedecano", "reglamento interno")) and "RI-FI" not in vistos:
        vistos.append("RI-FI")
    if any(w in p_low for w in ("reglamento general", "plev", "anexo", "escala", "crédito transferible", "credito transferible", "sct", "título", "titulo")) and "RG" not in vistos:
        vistos.append("RG")

    if not vistos:
        vistos = ["RG", "RI-FI"] if any(w in p_low for w in ("dafe", "sancion", "sanción", "duración", "examen")) else ["RG"]

    orden = [d for d in DOCS_VALIDOS if d in vistos]
    return orden or ["RG"]


def inferir_tipo_y_subconsultas_spec(spec: dict[str, Any]) -> tuple[str, list[str]]:
    """Deriva `(tipo, sub_consultas)` atómicas y limpias para un spec de D4."""
    pregunta = spec["pregunta"].strip()
    inexistentes = spec.get("inexistentes") or []

    # Caso explícito de artículo citado que no existe -> rama `premisa_falsa`
    if inexistentes:
        m_art = re.search(r"art[íi]culo\s*(\d+)", pregunta, re.IGNORECASE)
        if m_art:
            n_art = int(m_art.group(1))
            doc = doc_de_unidad(inexistentes[0])
            return "premisa_falsa", [
                f"verificar existencia del artículo {n_art} en {doc}",
                f"contenido del artículo {n_art} {doc}",
            ]
        if "transitorio" in pregunta.lower():
            return "premisa_falsa", [
                "verificar existencia del tercer artículo transitorio en RG",
                "artículos transitorios del Reglamento General",
            ]

    tipo = spec["modo"]
    if tipo not in TIPOS_VALIDOS:
        tipo = "factual"

    # Descomposición limpia para preguntas compuestas (`cruce` o doble pregunta)
    subs: list[str] = []
    trozos_interrog = [t for t in re.split(r"\?\s*", pregunta) if t.strip()]
    if len(trozos_interrog) >= 2:
        for t in trozos_interrog[:4]:
            limpia = _limpiar_subconsulta(t)
            if len(limpia) >= 12:
                subs.append(limpia)
    elif tipo == "cruce" or len(spec.get("evidencia_clave") or []) >= 2:
        # Intentar dividir por separadores compuestos naturales en español
        partes = re.split(
            r"\s*(?:;\s*|,\s+y\s+(?=qué|cuál|cuáles|cuándo|cuántos|cuántas|quién|cómo|en qué)|"
            r"\s+y\s+(?=qué|cuál|cuáles|cuándo|cuántos|cuántas|quién|cómo|en qué))\s*",
            pregunta,
            maxsplit=3,
            flags=re.IGNORECASE,
        )
        for p in partes:
            limpia = _limpiar_subconsulta(p)
            if len(limpia) >= 14:
                subs.append(limpia)

    if not subs:
        subs = [_limpiar_subconsulta(pregunta)]

    return tipo, subs[:4]


def construir_registros_enrutador(prompt_template: str) -> list[dict[str, Any]]:
    """Genera el dataset train/val completo para el Agente 1 (Enrutador)."""
    registros: list[dict[str, Any]] = []

    for spec in cd.todas_las_especificaciones():
        tipo, subs = inferir_tipo_y_subconsultas_spec(spec)
        docs = inferir_documentos_spec(spec)
        plan = {
            "tipo": tipo,
            "sub_consultas": subs,
            "documentos": docs,
        }
        prompt = prompt_template.replace("{{PREGUNTA}}", spec["pregunta"])
        registros.append(
            {
                "id": f"ENR-{spec['id']}",
                "origen_id": spec["id"],
                "agente": "enrutador",
                "split": spec["split"],
                "tipo": tipo,
                "documentos": docs,
                "pregunta_base": spec["pregunta"],
                "unidades_referenciadas": list(spec.get("evidencia_clave") or []),
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": json.dumps(plan, ensure_ascii=False)},
                ],
            }
        )

    for extra in EJEMPLOS_ENRUTADOR_EXTRA:
        plan = {
            "tipo": extra["tipo"],
            "sub_consultas": list(extra["sub_consultas"]),
            "documentos": list(extra["documentos"]),
        }
        prompt = prompt_template.replace("{{PREGUNTA}}", extra["pregunta"])
        registros.append(
            {
                "id": extra["id"],
                "origen_id": extra["id"],
                "agente": "enrutador",
                "split": extra["split"],
                "tipo": extra["tipo"],
                "documentos": list(extra["documentos"]),
                "pregunta_base": extra["pregunta"],
                "unidades_referenciadas": list(extra["unidades_referenciadas"]),
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": json.dumps(plan, ensure_ascii=False)},
                ],
            }
        )

    return registros
