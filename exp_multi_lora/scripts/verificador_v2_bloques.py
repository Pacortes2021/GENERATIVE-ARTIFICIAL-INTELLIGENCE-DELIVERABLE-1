"""Generador v2 recalibrado para el Agente 4 (Verificador / Self-Refine).

Resuelve los dos sesgos observados en la v1 de `verificador` y en el modelo base:
1. Elimina el atajo espurio contra `Condiciones o límites: No aplica`:
   - Incluye el 100 % de los ejemplos positivos reales (incluyendo `No aplica` válidos).
   - Evita insertar `"No aplica"` dentro de fallos no relacionados (`cruce` incompleto o
     mutaciones de `recuperador`).
   - Añade pares contrastivos `No aplica` válido vs inválido con distractores reales en
     `<evidencia>`.
2. Agrega cobertura contrastiva (en unidades 100 % limpias, fuera de `BLOCKED_UNIT_IDS`)
   para los errores que la v1 dejaba pasar y para las regresiones del Verificador base:
   - Atribución cruzada o alucinación en `Condiciones o límites` (Regla 3 / `P01`).
   - Pesos invertidos, sumas/divisiones erróneas, polaridad invertida y conteo de fechas.
   - Premisas sobre umbrales/incisos inexistentes: rechazar si no refuta vs aprobar si
     aclara honestamente que el artículo no fija dicho requisito.
   - Sustitución por artículo distractor sobre un tema diferente aunque tenga cita válida.
   - `<pensar>` variado y específico por caso para reducir el sobreajuste memorizado.
"""

from __future__ import annotations

import re
from typing import Any

from antifuga_multi import BLOCKED_UNIT_IDS, cd, doc_de_unidad
from verificador_bloques import (
    CASOS_ARITMETICOS_EXTRA,
    _crear_registro_ver,
    _formatear_borrador,
    _tiene_datos_en_700,
)

# Variaciones naturales de razonamiento positivo para evitar memorizar un único texto fijo
_PLANTILLAS_PENSAR_ABSTENCION = (
    "La evidencia está en estado '{estado}'; el borrador declara explícitamente la falta de respaldo en los artículos consultados sin inventar cifras ni excepciones y cierra sin respaldo.",
    "Los fragmentos en <evidencia> ({estado}) no contienen el dato consultado; la respuesta se abstiene con honestidad, mantiene Condiciones en 'No aplica' y no extrapola de otros artículos.",
)

_PLANTILLAS_PENSAR_NO_APLICA = (
    "Los artículos citados ({citas}) responden íntegramente lo consultado y no fijan excepciones o límites aplicables en <evidencia>; 'No aplica' es fiel a la norma pese a los distractores presentes.",
    "Cumple todos los criterios: datos coincidentes con {citas}, citas presentes en <evidencia>/<chequeo_citas> y 'Condiciones o límites: No aplica' coherente porque la regla consultada no trae salvedades adicionales.",
    "La respuesta usa exactamente la evidencia pertinente ({citas}), las citas están respaldadas y el texto consultado no agrega restricciones para este punto, validando 'No aplica'.",
)

_PLANTILLAS_PENSAR_CON_COND = (
    "Cumple los cinco criterios: responde todas las partes usando {citas}, preserva fielmente las condiciones y excepciones del texto entregado y sus citas constan en <evidencia>.",
    "Los datos, citas ({citas}) y salvedades de Condiciones o límites coinciden literalmente con los fragmentos de <evidencia> sin atribuir requisitos de artículos distintos.",
    "Verificado: cubre la consulta completa con respaldo de {citas}, conserva las condiciones aplicables descritas en la evidencia y no presenta contradicciones internas.",
)

# Pares contrastivos v2 curados sobre unidades limpias del corpus (fuera de BLOCKED_UNIT_IDS).
# Cada entrada usa `origen_id` propio por tópico y split estricto (`train` vs `val`).
CASOS_CURADOS_V2: list[dict[str, Any]] = [
    # ------------------------------------------------------------------
    # GRUPO A: `No aplica` válido vs inválido en presencia de distractores
    # ------------------------------------------------------------------
    {
        "id": "V2-NA-T01",
        "origen_id": "V2-TOP-NA-01",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Qué integrantes componen el Comité de Docencia y Asuntos Estudiantiles de una carrera en la Facultad de Ingeniería según el Artículo 33°?",
        "evidencia_ids": ["RI-FI-ART-033", "RI-FI-ART-032", "RG-ART-043"],
        "borrador": _formatear_borrador(
            "Está integrado por la Jefatura de Carrera (quien lo preside), dos docentes elegidos por el Consejo de Carrera entre sus integrantes y un representante estudiantil del Consejo de Carrera designado por el Centro de Alumnos, con derecho a voz y voto [RI-FI-ART-033].",
            "No aplica",
            "[RI-FI-ART-033]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "integración completa fiel a [RI-FI-ART-033] sin límites extra aplicables a la composición",
        "pensar": "La pregunta pide únicamente quiénes integran el Comité según [RI-FI-ART-033]; el borrador detalla todos los cargos y quórums indicados y 'No aplica' es adecuado porque [RI-FI-ART-032] y [RG-ART-043] son distractores.",
    },
    {
        "id": "V2-NA-T02",
        "origen_id": "V2-TOP-NA-02",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Cómo se define cada año la cantidad de cupos para Ingreso Directo e Ingreso Común en la Facultad de Ingeniería?",
        "evidencia_ids": ["RI-FI-ART-004", "RG-ART-044", "RG-ART-035"],
        "borrador": _formatear_borrador(
            "La Facultad de Ingeniería define cada año el número de cupos de Ingreso Directo a cada carrera y el número de cupos al Ingreso Común, pudiendo establecer para algunas carreras cupos únicamente mediante Ingreso Directo [RI-FI-ART-004].",
            "No aplica",
            "[RI-FI-ART-004]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "regla anual completa y fiel a [RI-FI-ART-004]; no corresponde exigir requisitos de otros artículos",
        "pensar": "[RI-FI-ART-004] consta en <chequeo_citas> y <evidencia>; resume la facultad anual y la posibilidad de cupos solo por Ingreso Directo sin que el artículo contenga restricciones adicionales aplicables.",
    },
    {
        "id": "V2-NA-T03",
        "origen_id": "V2-TOP-NA-03",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Qué es la Nota Final consignada en el Acta de Notas de una asignatura según el Artículo 27° del Reglamento General?",
        "evidencia_ids": ["RG-ART-027", "RG-ART-025", "RG-ART-043"],
        "borrador": _formatear_borrador(
            "Corresponde al Promedio Ponderado de las calificaciones obtenidas por el alumno en la asignatura, incluida la Evaluación de Recuperación cuando corresponda [RG-ART-027].",
            "No aplica",
            "[RG-ART-027]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "definición exacta según [RG-ART-027] sin condiciones extra aplicables a la consulta",
        "pensar": "El borrador reproduce fielmente el primer párrafo de [RG-ART-027] incluyendo la salvedad de Evaluación de Recuperación en la respuesta misma; los plazos de [RG-ART-025] y [RG-ART-043] pertenecen a distractores.",
    },
    {
        "id": "V2-NA-T04",
        "origen_id": "V2-TOP-NA-04",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Qué fecha establece el Calendario de Docencia de Pregrado 2026 para el término de clases de las asignaturas anuales del primer semestre?",
        "evidencia_ids": ["CAL-2026-S1-05", "RG-ART-043", "RG-ART-025"],
        "borrador": _formatear_borrador(
            "Las clases de asignaturas anuales del primer semestre 2026 terminan el 24 de julio [CAL-2026-S1-05].",
            "No aplica",
            "[CAL-2026-S1-05]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "fecha exacta y cita válida del calendario",
        "pensar": "[CAL-2026-S1-05] figura en <chequeo_citas> y <evidencia> con la fecha literal 24 de julio sin condiciones adicionales.",
    },
    {
        "id": "V2-NA-T05",
        "origen_id": "V2-TOP-NA-05",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Cuál es el plazo ordinario para abandonar asignaturas semestrales o anuales según el Artículo 43° del Reglamento General?",
        "evidencia_ids": ["RG-ART-043", "RG-ART-044"],
        "borrador": _formatear_borrador(
            "El alumno dispone de un plazo de cuatro semanas contado desde la fecha de inicio de clases del Calendario de Docencia de Pregrado [RG-ART-043].",
            "No aplica",
            "[RG-ART-043]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "omite en Condiciones las restricciones explícitas de [RG-ART-043]: una sola vez por asignatura, no bajar del mínimo de créditos, duración menor a un semestre y prohibición en PLEV",
        "pensar": "Aunque las cuatro semanas son exactas, el mismo [RG-ART-043] impone cuatro límites explícitos (una vez, mínimo de créditos, asignaturas menores a un semestre y exclusión del PLEV) que no pueden resumirse como 'No aplica'.",
    },
    {
        "id": "V2-NA-V01",
        "origen_id": "V2-TOP-NA-VAL1",
        "split": "val",
        "estado": "suficiente",
        "pregunta": "¿En qué fechas del primer semestre 2026 están fijadas las Evaluaciones de Recuperación y el feriado de abril?",
        "evidencia_ids": ["CAL-2026-S1-06", "CAL-2026-S1-09", "RG-ART-025"],
        "borrador": _formatear_borrador(
            "Las Evaluaciones de Recuperación del primer semestre 2026 son del 13 al 24 de julio [CAL-2026-S1-06], y el feriado nacional de abril es el viernes 03 de abril [CAL-2026-S1-09].",
            "No aplica",
            "[CAL-2026-S1-06] [CAL-2026-S1-09]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "fechas exactas respaldadas en ambas unidades del calendario",
        "pensar": "Ambas citas [CAL-2026-S1-06] y [CAL-2026-S1-09] están validadas en <chequeo_citas> y contienen las fechas exactas sin condiciones adicionales.",
    },
    {
        "id": "V2-NA-V02",
        "origen_id": "V2-TOP-NA-VAL2",
        "split": "val",
        "estado": "suficiente",
        "pregunta": "¿En qué consiste la homologación de asignaturas y quién aprueba la tabla de homologables según el Artículo 40° RG?",
        "evidencia_ids": ["RG-ART-040", "RG-ART-037"],
        "borrador": _formatear_borrador(
            "La homologación traspasa toda la información registrada en una asignatura aprobada en otra versión del Plan de Estudio de la misma carrera, cuya tabla fija el Vicedecano de la Facultad correspondiente [RG-ART-040].",
            "No aplica",
            "[RG-ART-040]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "omite condiciones explícitas de [RG-ART-040] (calidad de alumno regular, otro código en SAC por sede o versión anterior y requisito de consulta al Comité/Consejo indicado en el artículo)",
        "pensar": "[RG-ART-040] exige explícitamente tratarse de alumnos regulares y que la asignatura figure con otro código en SAC por cambio de sede o versión anterior; responder 'No aplica' omite esos requisitos del mismo artículo.",
    },
    # ------------------------------------------------------------------
    # GRUPO B: Pares contrastivos de Regla 3 / P01 (atribución cruzada o falsa)
    # ------------------------------------------------------------------
    {
        "id": "V2-P01-T01-OK",
        "origen_id": "V2-TOP-P01-01",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Qué ocurre si un alumno presenta salud incompatible con la carrera y ante quién solicita su reincorporación si suspende por salud?",
        "evidencia_ids": ["RG-ART-032", "RG-ART-033"],
        "borrador": _formatear_borrador(
            "Si presenta salud o condición física incompatible con la carrera se le suspende el derecho a continuar estudios [RG-ART-032]; para continuarlos tras una suspensión deberá solicitar reincorporación al Vicedecano acompañando antecedentes que acrediten el cese de los impedimentos, decidiendo en ese caso el Decano [RG-ART-033].",
            "En [RG-ART-033] para suspensiones por salud debe acompañarse informe de la Dirección de Servicios Estudiantiles u otra unidad fidedigna y la decisión corresponde al Decano.",
            "[RG-ART-032] [RG-ART-033]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "atribución exacta de [RG-ART-032] y [RG-ART-033] sin contradecir el texto",
        "pensar": "Cada regla cita exactamente su artículo en Respuesta y Condiciones: suspensión por salud incompatible en [RG-ART-032] e informe + decisión del Decano al reincorporarse en [RG-ART-033].",
    },
    {
        "id": "V2-P01-T01-BAD",
        "origen_id": "V2-TOP-P01-01",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Qué ocurre si un alumno presenta salud incompatible con la carrera y ante quién solicita su reincorporación si suspende por salud?",
        "evidencia_ids": ["RG-ART-032", "RG-ART-033"],
        "borrador": _formatear_borrador(
            "Si presenta salud incompatible con la carrera se le suspende el derecho a continuar estudios [RG-ART-032]; para continuarlos deberá solicitar reincorporación al Vicedecano acreditando que cesaron los impedimentos, con decisión del Decano [RG-ART-033].",
            "La suspensión por salud incompatible opera de forma automática sin requerir informe médico ni trámite previo [RG-ART-032]; en [RG-ART-033] decide el Decano.",
            "[RG-ART-032] [RG-ART-033]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "Condiciones introduce una afirmación falsa sobre suspensión automática sin informe previo bajo [RG-ART-032]",
        "pensar": "Aunque ambas citas constan en <chequeo_citas>, la línea Condiciones o límites inventa bajo [RG-ART-032] que la suspensión es 'automática sin requerir informe médico', lo cual no consta en el fragmento entregado.",
    },
    {
        "id": "V2-P01-T02-OK",
        "origen_id": "V2-TOP-P01-02",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿En qué condiciones reingresa un estudiante a la misma carrera y cuál es el plazo para pedir mantener su situación académica previa?",
        "evidencia_ids": ["RG-ART-044", "RG-ART-043"],
        "borrador": _formatear_borrador(
            "Quien reingresa a la misma carrera debe hacerlo a Primer Año como alumno nuevo, sujeto al plan y requisitos vigentes al reingreso y sin derecho a validar, revalidar, convalidar ni reconocer asignaturas aprobadas [RG-ART-044]; si no incurrió en pérdida de carrera puede solicitar dentro de los primeros 30 días del primer semestre mantener su situación académica anterior [RG-ART-044].",
            "La prohibición de validar asignaturas aplica al reingreso a Primer Año [RG-ART-044]; el derecho a mantener la situación académica previa exige no haber perdido la carrera y pedirlo dentro de los primeros 30 días [RG-ART-044].",
            "[RG-ART-044]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "condiciones y citas fieles únicamente a [RG-ART-044] sin mezclar [RG-ART-043]",
        "pensar": "Responde ambas partes según [RG-ART-044] sin confundir con [RG-ART-043] y respeta la prohibición de validar junto con el plazo de 30 días.",
    },
    {
        "id": "V2-P01-T02-BAD",
        "origen_id": "V2-TOP-P01-02",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿En qué condiciones reingresa un estudiante a la misma carrera y cuál es el plazo para pedir mantener su situación académica previa?",
        "evidencia_ids": ["RG-ART-044", "RG-ART-043"],
        "borrador": _formatear_borrador(
            "Quien reingresa a la misma carrera lo hace a Primer Año como alumno nuevo sin validar ni reconocer asignaturas aprobadas [RG-ART-044], pudiendo pedir dentro de los primeros 30 días mantener su situación académica anterior si no perdió la carrera [RG-ART-044].",
            "Además, el estudiante no puede abandonar asignaturas inscritas en el PLEV y en cursos de duración menor a un semestre la Facultad fija el plazo de abandono [RG-ART-044].",
            "[RG-ART-044]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "Condiciones atribuye erróneamente a [RG-ART-044] las reglas de abandono del PLEV y asignaturas breves que pertenecen a [RG-ART-043]",
        "pensar": "Error de atribución cruzada en Condiciones o límites: la restricción sobre el PLEV y cursos menores a un semestre pertenece a [RG-ART-043], no a [RG-ART-044].",
    },
    {
        "id": "V2-P01-T03-BAD",
        "origen_id": "V2-TOP-P01-03",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Qué requisitos deben acompañarse al solicitar la convalidación de una asignatura cursada en otra institución y quién resuelve el trámite?",
        "evidencia_ids": ["RG-ART-037", "RG-ART-040"],
        "borrador": _formatear_borrador(
            "Debe acompañarse certificado completo de calificaciones y programas debidamente acreditados de las asignaturas aprobadas; resuelve el Vicedecano previo informe del Departamento a cargo dentro de 15 días [RG-ART-037].",
            "Para esta convalidación el Vicedecano aplica la tabla de asignaturas homologables por cambio de código o sede en el SAC [RG-ART-037] y se exceptúan las aprobadas en la UdeC [RG-ART-037].",
            "[RG-ART-037] [RG-ART-040]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "Condiciones mezcla la tabla de asignaturas homologables de [RG-ART-040] atribuyéndola erróneamente a [RG-ART-037]",
        "pensar": "La Respuesta está correcta, pero en Condiciones atribuye a [RG-ART-037] la tabla de asignaturas homologables y cambios de código en SAC que pertenecen a [RG-ART-040].",
    },
    {
        "id": "V2-P01-T04-OK",
        "origen_id": "V2-TOP-P01-04",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Quién debe informar al inicio de la asignatura el Programa y modalidades de evaluación y de qué plazo disponen los profesores para entregar las notas?",
        "evidencia_ids": ["RG-ART-019", "RG-ART-025"],
        "borrador": _formatear_borrador(
            "Al inicio de la dictación, el Profesor Encargado debe comunicar por escrito o canal oficial el Programa, Syllabus, régimen de asistencia, actividades, evaluaciones y modalidad de Nota Final [RG-ART-019]; una vez corregidas las evaluaciones escritas, los profesores tienen un plazo máximo de diez días hábiles para dar a conocer las calificaciones y pautas [RG-ART-025].",
            "El medio usado al inicio debe permitir acceso claro e impresión/almacenamiento [RG-ART-019]; respecto a las calificaciones, el Vicedecano puede ampliar el plazo de 10 días hábiles por razones justificadas [RG-ART-025].",
            "[RG-ART-019] [RG-ART-025]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "cruce preciso entre [RG-ART-019] y [RG-ART-025] con condiciones correctamente separadas",
        "pensar": "Cada parte de Respuesta y Condiciones conserva fielmente la separación entre [RG-ART-019] (comunicación inicial) y [RG-ART-025] (plazo máximo de 10 días hábiles ampliable por el Vicedecano).",
    },
    {
        "id": "V2-P01-V01-OK",
        "origen_id": "V2-TOP-P01-VAL1",
        "split": "val",
        "estado": "suficiente",
        "pregunta": "¿En qué casos se registra una asignatura con sigla VAL en el SAC y qué documentos requiere la Facultad de Ingeniería para validar un intercambio?",
        "evidencia_ids": ["RG-ART-041", "RI-FI-ART-024"],
        "borrador": _formatear_borrador(
            "Se registra con la sigla VAL la validación de asignaturas cursadas en programas de intercambio estudiantil dentro del SAC [RG-ART-041]; en la Facultad de Ingeniería se debe presentar al Vicedecano el programa y calificación debidamente certificados [RI-FI-ART-024].",
            "Las asignaturas aprobadas en intercambio bajo convenios vigentes pueden ser reconocidas como carga académica del semestre [RI-FI-ART-024], a diferencia de las asignaturas CON, HOM o REC [RG-ART-041].",
            "[RG-ART-041] [RI-FI-ART-024]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "atribución exacta de carga académica VAL a [RI-FI-ART-024] y de CON/HOM/REC a [RG-ART-041]",
        "pensar": "Ambas citas constan en <chequeo_citas> y <evidencia>; Condiciones distingue correctamente qué norma regula la carga académica del intercambio ([RI-FI-ART-024]) y cuál las siglas CON/HOM/REC ([RG-ART-041]).",
    },
    {
        "id": "V2-P01-V01-BAD",
        "origen_id": "V2-TOP-P01-VAL1",
        "split": "val",
        "estado": "suficiente",
        "pregunta": "¿En qué casos se registra una asignatura con sigla VAL en el SAC y qué documentos requiere la Facultad de Ingeniería para validar un intercambio?",
        "evidencia_ids": ["RG-ART-041", "RI-FI-ART-024"],
        "borrador": _formatear_borrador(
            "Se registra con sigla VAL la validación por intercambio estudiantil [RG-ART-041] y en Ingeniería se presenta al Vicedecano el programa y calificación certificados [RI-FI-ART-024].",
            "Las asignaturas revalidadas (REV) de otra institución también cuentan como carga académica del semestre en que se cursaron según [RG-ART-041].",
            "[RG-ART-041] [RI-FI-ART-024]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "Condiciones afirma erróneamente bajo [RG-ART-041] que REV cuenta como carga académica del semestre, cuando [RG-ART-041] lo excluye",
        "pensar": "Aunque ambas citas son válidas, Condiciones o límites contradice [RG-ART-041] afirmando que las revalidadas REV cuentan como carga académica del semestre.",
    },
    # ------------------------------------------------------------------
    # GRUPO C: Aritmética ponderada, conteo de fechas y desigualdades
    # ------------------------------------------------------------------
    {
        "id": "V2-ARIT-T01-BAD",
        "origen_id": "V2-TOP-ARIT-01",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "Si según el Artículo 27° RG la Nota Final resulta de un Promedio Ponderado y un programa de asignatura asigna 70 % al promedio de certámenes (nota 5,0) y 30 % a un proyecto final (nota 6,0), ¿cuál es la Nota Final?",
        "evidencia_ids": ["RG-ART-027", "RG-ART-021"],
        "borrador": _formatear_borrador(
            "La Nota Final ponderada es 5,0 × 0,30 + 6,0 × 0,70 = 1,50 + 4,20 = 5,70 [RG-ART-027].",
            "La Nota Final corresponde al Promedio Ponderado de las evaluaciones según las ponderaciones del programa [RG-ART-027] [RG-ART-021].",
            "[RG-ART-027] [RG-ART-021]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "invierte los pesos del promedio ponderado (aplica 30 % a certámenes y 70 % a proyecto en lugar de 70 % y 30 %)",
        "pensar": "Las citas existen, pero el cálculo invierte los factores dados en la pregunta: debía ser 5,0 × 0,70 + 6,0 × 0,30 = 5,30 y el borrador calculó 5,0 × 0,30 + 6,0 × 0,70 = 5,70.",
    },
    {
        "id": "V2-ARIT-T01-OK",
        "origen_id": "V2-TOP-ARIT-01",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "Si según el Artículo 27° RG la Nota Final resulta de un Promedio Ponderado y un programa de asignatura asigna 70 % al promedio de certámenes (nota 5,0) y 30 % a un proyecto final (nota 6,0), ¿cuál es la Nota Final?",
        "evidencia_ids": ["RG-ART-027", "RG-ART-021"],
        "borrador": _formatear_borrador(
            "Aplicando el Promedio Ponderado fijado en el programa [RG-ART-021] [RG-ART-027], la Nota Final es 5,0 × 0,70 + 6,0 × 0,30 = 3,50 + 1,80 = 5,30.",
            "En el Acta de Notas se consigna el Promedio Ponderado incluyendo Evaluación de Recuperación si corresponde [RG-ART-027].",
            "[RG-ART-021] [RG-ART-027]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "ponderación 70/30 y aritmética exactas",
        "pensar": "Cada factor coincide exactamente con el enunciado (5,0 × 0,70 + 6,0 × 0,30 = 5,30) y ambas citas están en <evidencia> y <chequeo_citas>.",
    },
    {
        "id": "V2-ARIT-T02-OK",
        "origen_id": "V2-TOP-ARIT-02",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Cuántos días corridos median entre el feriado nacional del viernes 03 de abril y el inicio de las vacaciones de invierno del 30 de junio de 2026?",
        "evidencia_ids": ["CAL-2026-S1-09", "CAL-2026-S1-14"],
        "borrador": _formatear_borrador(
            "Entre el 03 de abril [CAL-2026-S1-09] y el 30 de junio de 2026 [CAL-2026-S1-14] transcurren 27 días restantes de abril + 31 días de mayo + 30 días de junio = 88 días corridos.",
            "No aplica",
            "[CAL-2026-S1-09] [CAL-2026-S1-14]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "conteo calendario exacto (27 + 31 + 30 = 88 días) con fechas reales de <evidencia>",
        "pensar": "Las fechas 03 de abril y 30 de junio coinciden con [CAL-2026-S1-09] y [CAL-2026-S1-14], y la suma calendario 27 + 31 + 30 = 88 días es aritméticamente exacta.",
    },
    {
        "id": "V2-ARIT-T02-BAD",
        "origen_id": "V2-TOP-ARIT-02",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Cuántos días corridos median entre el feriado nacional del viernes 03 de abril y el inicio de las vacaciones de invierno del 30 de junio de 2026?",
        "evidencia_ids": ["CAL-2026-S1-09", "CAL-2026-S1-14"],
        "borrador": _formatear_borrador(
            "Entre el 03 de abril [CAL-2026-S1-09] y el 30 de junio [CAL-2026-S1-14] median 95 días corridos (contando abril de 30 días, mayo de 31 y del 30 al 30 de junio).",
            "No aplica",
            "[CAL-2026-S1-09] [CAL-2026-S1-14]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "error aritmético en el conteo de días corridos (entre 03 de abril y 30 de junio hay 88 días, no 95) y redacción errónea 'del 30 al 30'",
        "pensar": "Aunque las fechas citadas son reales, el cálculo de días corridos es incorrecto (27 + 31 + 30 = 88 días, no 95) y contiene la incongruencia 'del 30 al 30'.",
    },
    {
        "id": "V2-ARIT-V01-BAD",
        "origen_id": "V2-TOP-ARIT-VAL1",
        "split": "val",
        "estado": "suficiente",
        "pregunta": "Si un estudiante obtuvo una nota final de título de 5,6 en su carrera, ¿qué concepto le corresponde según la pauta del Artículo 48° RG?",
        "evidencia_ids": ["RG-ART-048", "RG-ANEXO-06"],
        "borrador": _formatear_borrador(
            "Con 5,6 le corresponde el concepto 'Aprobado con Distinción Máxima' porque supera el rango de 5,0 [RG-ART-048].",
            "Aplica a Diplomas de Título Profesional y Licenciaturas terminales [RG-ART-048].",
            "[RG-ART-048]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "error en el tramo de calificación de [RG-ART-048]: 5,6 pertenece a 'Aprobado con Distinción' (5,0 - 5,6), no a 'Distinción Máxima' (5,7 - 7,0)",
        "pensar": "La pauta explícita de [RG-ART-048] fija 'Aprobado con Distinción' para el intervalo 5,0 - 5,6 y reserva 'Distinción Máxima' desde 5,7; el borrador clasifica mal 5,6.",
    },
    # ------------------------------------------------------------------
    # GRUPO D: Umbral/inciso inexistente -> rechazar si no refuta vs aprobar si aclara
    # ------------------------------------------------------------------
    {
        "id": "V2-PREM-T01-BAD",
        "origen_id": "V2-TOP-PREM-01",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "Además de exigir los certificados de la letra a) y b), ¿qué tercer documento obligatorio exige la letra c) del Artículo 35° RG para suspender estudios?",
        "evidencia_ids": ["RG-ART-035", "RG-ART-033"],
        "borrador": _formatear_borrador(
            "Para suspender estudios se deben cumplir los requisitos que fije la Facultad y adjuntar certificado de la División de Asistencia Financiera al Estudiante sin deudas y certificado de la Dirección de Bibliotecas sin material adeudado [RG-ART-035].",
            "No aplica",
            "[RG-ART-035]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "no refuta la premisa falsa sobre una letra c): [RG-ART-035] solo contempla las letras a) y b) y no existe inciso c)",
        "pensar": "El usuario preguntó por una inexistente letra c) en [RG-ART-035]; aunque describe correctamente a) y b), el borrador omite aclarar expresamente que el artículo no contiene un inciso c).",
    },
    {
        "id": "V2-PREM-T01-OK",
        "origen_id": "V2-TOP-PREM-01",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "Además de exigir los certificados de la letra a) y b), ¿qué tercer documento obligatorio exige la letra c) del Artículo 35° RG para suspender estudios?",
        "evidencia_ids": ["RG-ART-035", "RG-ART-033"],
        "borrador": _formatear_borrador(
            "El Artículo 35° del Reglamento General no contempla una letra c); únicamente exige cumplir los requisitos que establezca la Facultad y adjuntar los certificados indicados en sus letras a) División de Asistencia Financiera al Estudiante y b) Dirección de Bibliotecas [RG-ART-035].",
            "Adicionalmente deben cumplirse los requisitos que establezca la respectiva Facultad [RG-ART-035].",
            "[RG-ART-035]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "refuta explícitamente la letra c) inexistente y detalla las letras a) y b) reales",
        "pensar": "El borrador desmiente claramente que exista una letra c) en [RG-ART-035] y expone con exactitud las letras a) y b) junto con la exigencia de la Facultad.",
    },
    {
        "id": "V2-PREM-T02-BAD",
        "origen_id": "V2-TOP-PREM-02",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Qué porcentaje máximo de cupos de Ingreso Directo impone el Artículo 4° del RI-FI a las carreras de Ingeniería?",
        "evidencia_ids": ["RI-FI-ART-004", "RG-ART-044"],
        "borrador": _formatear_borrador(
            "La Facultad de Ingeniería define cada año el número de cupos de Ingreso Directo y de Ingreso Común, pudiendo establecer en algunas carreras solo cupos de Ingreso Directo [RI-FI-ART-004].",
            "No aplica",
            "[RI-FI-ART-004]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "no aclara que [RI-FI-ART-004] no fija ningún porcentaje máximo de cupos de Ingreso Directo",
        "pensar": "La pregunta presupone un porcentaje máximo inexistente en [RI-FI-ART-004]; el borrador repite la facultad anual sin declarar que dicho límite porcentual máximo no existe en el artículo.",
    },
    {
        "id": "V2-PREM-T02-OK",
        "origen_id": "V2-TOP-PREM-02",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Qué porcentaje máximo de cupos de Ingreso Directo impone el Artículo 4° del RI-FI a las carreras de Ingeniería?",
        "evidencia_ids": ["RI-FI-ART-004", "RG-ART-044"],
        "borrador": _formatear_borrador(
            "El Artículo 4° del RI-FI no fija ningún porcentaje máximo de cupos para Ingreso Directo; únicamente señala que la Facultad definirá anualmente los cupos de Ingreso Directo y de Ingreso Común, pudiendo fijar en algunas carreras solo Ingreso Directo [RI-FI-ART-004].",
            "No aplica",
            "[RI-FI-ART-004]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "aclara honestamente la ausencia de porcentaje máximo sin inventar reglas de distractores",
        "pensar": "El borrador responde exactamente aclarando que [RI-FI-ART-004] no establece porcentaje máximo alguno y reproduce la regla anual; no corresponde exigir otros artículos distractores.",
    },
    {
        "id": "V2-PREM-V01-OK",
        "origen_id": "V2-TOP-PREM-VAL1",
        "split": "val",
        "estado": "suficiente",
        "pregunta": "¿Qué promedio mínimo de notas exige el Artículo 33° del RI-FI a los docentes elegidos para integrar el Comité de Docencia y Asuntos Estudiantiles?",
        "evidencia_ids": ["RI-FI-ART-033", "RI-FI-ART-032", "RG-ART-054"],
        "borrador": _formatear_borrador(
            "El Artículo 33° del RI-FI no establece ningún requisito de promedio de notas para integrar el Comité de Docencia y Asuntos Estudiantiles; solo exige que los dos docentes sean elegidos por el Consejo de Carrera entre sus integrantes [RI-FI-ART-033].",
            "No aplica",
            "[RI-FI-ART-033]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "declara con precisión que [RI-FI-ART-033] no fija promedio y no exige condiciones ajenas",
        "pensar": "Aunque [RG-ART-054] en <evidencia> habla de promedios para cambio de carrera, la consulta es específicamente sobre el Artículo 33° RI-FI, que no fija promedio alguno; la respuesta lo aclara bien y debe aprobarse.",
    },
    {
        "id": "V2-PREM-V01-BAD",
        "origen_id": "V2-TOP-PREM-VAL1",
        "split": "val",
        "estado": "suficiente",
        "pregunta": "¿Qué promedio mínimo de notas exige el Artículo 33° del RI-FI a los docentes elegidos para integrar el Comité de Docencia y Asuntos Estudiantiles?",
        "evidencia_ids": ["RI-FI-ART-033", "RI-FI-ART-032", "RG-ART-054"],
        "borrador": _formatear_borrador(
            "El Comité de Docencia y Asuntos Estudiantiles se compone de la Jefatura de Carrera, dos docentes elegidos por el Consejo de Carrera y un representante estudiantil designado por el Centro de Alumnos [RI-FI-ART-033].",
            "No aplica",
            "[RI-FI-ART-033]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "omite señalar explícitamente que [RI-FI-ART-033] no fija promedio mínimo de notas para los docentes del Comité",
        "pensar": "El usuario preguntó por un promedio mínimo inexistente en el Art. 33° RI-FI; el borrador enumera la composición sin aclarar que dicho requisito de promedio no existe en el artículo.",
    },
    # ------------------------------------------------------------------
    # GRUPO E: Sustitución por distractor temático + Suficiencia acotada
    # ------------------------------------------------------------------
    {
        "id": "V2-TEMA-T01-REC",
        "origen_id": "V2-TOP-TEMA-01",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿Qué documentos debe acompañar un alumno para solicitar su reincorporación tras una suspensión de estudios por motivos de salud?",
        "evidencia_ids": ["RG-ART-035", "RG-ART-032"],
        "borrador": _formatear_borrador(
            "Debe presentar certificado de la División de Asistencia Financiera al Estudiante sin deudas y certificado de la Dirección de Bibliotecas sin deuda bibliográfica [RG-ART-035].",
            "Además debe cumplir los requisitos que establezca la Facultad [RG-ART-035].",
            "[RG-ART-035]",
        ),
        "aprobado": False,
        "destino": "recuperador",
        "motivo": "el borrador responde con los requisitos de suspensión/renuncia ([RG-ART-035]) en vez de recuperar el artículo específico de reincorporación por salud ([RG-ART-033])",
        "pensar": "[RG-ART-035] regula suspender estudios o renunciar a la carrera, no la reincorporación tras suspensión por salud; en <evidencia> falta el artículo de reincorporación y debe buscarse en el Recuperador.",
    },
    {
        "id": "V2-TEMA-T02-RED",
        "origen_id": "V2-TOP-TEMA-02",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "¿En cuántos días máximo debe resolver el Vicedecano una solicitud de convalidación de asignaturas aprobadas en otra institución?",
        "evidencia_ids": ["RG-ART-025", "RG-ART-037"],
        "borrador": _formatear_borrador(
            "El plazo máximo es de diez días hábiles, prorrogable por el Vicedecano por razones justificadas [RG-ART-025].",
            "El estudiante dispone además de 5 días hábiles para ejercer su derecho a revisión [RG-ART-025].",
            "[RG-ART-025]",
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "usa el plazo de entrega de evaluaciones escritas ([RG-ART-025]: 10 días hábiles) en vez del plazo de resolución de convalidación presente en [RG-ART-037] (15 días)",
        "pensar": "Aunque [RG-ART-025] está en <chequeo_citas>, responde sobre entrega de notas y pautas; el artículo pertinente ya está en <evidencia> ([RG-ART-037]: quince días, previo informe del Departamento).",
    },
    {
        "id": "V2-ACOT-T01-OK",
        "origen_id": "V2-TOP-ACOT-01",
        "split": "train",
        "estado": "suficiente",
        "pregunta": "Según el Artículo 19° del Reglamento General, ¿qué elementos debe informar el Profesor Encargado al inicio de la dictación de una asignatura?",
        "evidencia_ids": ["RG-ART-019", "RG-ART-020", "RG-ART-025"],
        "borrador": _formatear_borrador(
            "Al inicio de la asignatura, el Profesor Encargado debe comunicar el Programa y Syllabus aprobados por la Facultad, el régimen de asistencia, la metodología de trabajo, las actividades, las formas de evaluación, la modalidad para determinar la Nota Final y las normas o exigencias de la Facultad [RG-ART-019].",
            "La comunicación debe efectuarse por escrito o canal oficial de la universidad que permita acceso claro, almacenamiento o impresión [RG-ART-019].",
            "[RG-ART-019]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "cubre exhaustivamente todo lo pedido sobre [RG-ART-019] sin exigir citar distractores",
        "pensar": "La consulta pregunta exclusivamente por la información inicial del Art. 19° RG; el borrador incluye todos sus elementos y la exigencia del canal oficial sin necesitar citar [RG-ART-020] ni [RG-ART-025].",
    },
    {
        "id": "V2-ACOT-V01-OK",
        "origen_id": "V2-TOP-ACOT-VAL1",
        "split": "val",
        "estado": "suficiente",
        "pregunta": "¿Qué requisitos establece el Artículo 54° RG para que un alumno solicite cambio a otra carrera en la Universidad?",
        "evidencia_ids": ["RG-ART-054", "RG-ART-044", "RG-ART-055"],
        "borrador": _formatear_borrador(
            "Debe cumplir dos requisitos: a) ser alumno regular y conservar el derecho a continuar estudios en la carrera de origen; y b) haber obtenido al menos el promedio mínimo de calificaciones que indique el Reglamento Interno de la Facultad a la cual postula [RG-ART-054].",
            "Si el cambio es entre carreras de una misma Facultad, su Reglamento Interno podrá fijar promedios o puntajes distintos respecto del requisito b) [RG-ART-054].",
            "[RG-ART-054]",
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "incluye letras a) y b) completas más la salvedad de cambio interno en [RG-ART-054]",
        "pensar": "Responde completamente los requisitos del Art. 54° RG y conserva la salvedad de cambios dentro de una misma Facultad sin exigir reglas ajenas de [RG-ART-044] o [RG-ART-055].",
    },
]


def _pensar_positivo_v2(spec: dict[str, Any], idx: int) -> str:
    """Construye un razonamiento positivo diverso según el tipo real de respuesta."""
    claves = list(spec.get("evidencia_clave") or [])
    citas_txt = ", ".join(f"[{u}]" for u in claves) if claves else spec.get("fuente", "la evidencia")
    cond_na = spec["condiciones"].strip().lower() == "no aplica"

    if spec["estado"] != "suficiente":
        tpl = _PLANTILLAS_PENSAR_ABSTENCION[idx % len(_PLANTILLAS_PENSAR_ABSTENCION)]
        return tpl.format(estado=spec["estado"])

    if cond_na:
        tpl = _PLANTILLAS_PENSAR_NO_APLICA[idx % len(_PLANTILLAS_PENSAR_NO_APLICA)]
        return tpl.format(citas=citas_txt)

    tpl = _PLANTILLAS_PENSAR_CON_COND[idx % len(_PLANTILLAS_PENSAR_CON_COND)]
    return tpl.format(citas=citas_txt)


def _mutar_a_redactor_v2(
    spec: dict[str, Any],
    evidencia_ids: list[str],
    idx: int,
) -> tuple[str, str, str] | None:
    """Genera defectos reales de `redactor` sin contaminar artificialmente con `'No aplica'`."""
    resp = spec["respuesta"]
    cond = spec["condiciones"]
    fuente = spec["fuente"]
    claves = list(spec.get("evidencia_clave") or [])
    cond_no_vacia = cond if cond.strip().lower() != "no aplica" else "Aplican las exigencias reglamentarias de la unidad consultada."

    # 1) Omisión real de condiciones: solo cuando el artículo sí fija salvedades (>= 35 chars)
    if spec["estado"] == "suficiente" and cond.strip().lower() != "no aplica" and len(cond) >= 35 and idx % 4 == 0:
        borrador = _formatear_borrador(resp, "No aplica", fuente)
        resumen_cond = cond[:85].rstrip(" ,.;:")
        pensar = (
            f"Las citas ({fuente}) existen en <evidencia>, pero el borrador escribe 'No aplica' "
            f"omitiendo una restricción explícita del artículo ({resumen_cond}...)."
        )
        motivo = "omite condiciones y salvedades explícitas del artículo bajo 'Condiciones o límites: No aplica'"
        return borrador, pensar, motivo

    # 2) Confirmación indebida de premisa falsa
    if spec["modo"] == "premisa_falsa" and spec["estado"] == "suficiente":
        borrador = _formatear_borrador(
            f"Sí, es correcto tal como indica la pregunta {fuente}.",
            cond,
            fuente,
        )
        pensar = (
            "La consulta introduce un supuesto falso desmentido por <evidencia>, "
            "pero el borrador lo valida en lugar de refutarlo."
        )
        motivo = "confirma una premisa falsa que la evidencia entregada desmiente"
        return borrador, pensar, motivo

    # 3) Invertir mínimo / máximo preservando condiciones originales
    if re.search(r"\bm[íi]nim[oa]|no inferior a|al menos\b", resp, re.IGNORECASE):
        resp_inv = re.sub(r"\bm[íi]nimo\b", "máximo", resp, count=1, flags=re.IGNORECASE)
        if resp_inv == resp:
            resp_inv = re.sub(r"\bm[íi]nima\b", "máxima", resp, count=1, flags=re.IGNORECASE)
        if resp_inv == resp:
            resp_inv = re.sub(r"\bno inferior a\b", "como máximo de", resp, count=1, flags=re.IGNORECASE)
        if resp_inv == resp:
            resp_inv = re.sub(r"\bal menos\b", "como máximo", resp, count=1, flags=re.IGNORECASE)
        if resp_inv != resp:
            borrador = _formatear_borrador(resp_inv, cond, fuente)
            pensar = (
                "La evidencia establece un mínimo o piso obligatorio, pero el borrador lo convierte "
                "en máximo, invirtiendo el sentido normativo."
            )
            motivo = "convierte un mínimo de la evidencia en un máximo en la respuesta"
            return borrador, pensar, motivo

    # 4) Pregunta de cruce respondida a medias (preserva una condición realista, nunca inserta 'No aplica' falso)
    if len(claves) >= 2 and ";" in resp:
        primera_parte = resp.split(";", 1)[0].strip() + "."
        cond_parcial = (
            cond
            if cond.strip().lower() == "no aplica"
            else f"Sujeto a lo dispuesto en [{claves[0]}]."
        )
        borrador = _formatear_borrador(primera_parte, cond_parcial, f"[{claves[0]}]")
        pensar = (
            f"La evidencia contiene [{claves[0]}] y [{claves[1]}], pero el borrador responde solo "
            f"el punto de [{claves[0]}] y deja incompleta la segunda parte."
        )
        motivo = f"responde solo una parte de la pregunta de cruce pese a contar con [{claves[1]}] en la evidencia"
        return borrador, pensar, motivo

    # 5) Respuesta polar contradictoria ("No, ..." antes de afirmar la regla)
    if resp.startswith(("Sí", "Si ", "Para ", "El ", "La ", "Un ", "Una ")) and idx % 2 == 1 and spec["estado"] == "suficiente":
        resp_contra = f"No, {resp[0].lower()}{resp[1:]}"
        borrador = _formatear_borrador(resp_contra, cond, fuente)
        pensar = (
            "El borrador abre negando ('No,') y contradice de inmediato la afirmación normativa "
            "que expone a continuación."
        )
        motivo = "contradicción lógica entre el 'No' inicial y el desarrollo posterior de la respuesta"
        return borrador, pensar, motivo

    # 6) Falta total de citas en evidencia suficiente (`sin_citas: true`)
    if spec["estado"] == "suficiente" and claves:
        resp_sin = re.sub(r"\s*\[[A-Z0-9-]+\]", "", resp).strip()
        cond_sin = re.sub(r"\s*\[[A-Z0-9-]+\]", "", cond).strip() or cond_no_vacia
        borrador = _formatear_borrador(resp_sin, cond_sin, "Normativa universitaria UdeC")
        pensar = (
            "<chequeo_citas> indica sin_citas=true: faltan los identificadores [ID] de los artículos "
            "utilizados en la respuesta y en la línea Fuente."
        )
        motivo = "omite los identificadores de cita [ID] exigidos tanto en el texto como en Fuente"
        return borrador, pensar, motivo

    return None


def _mutar_a_recuperador_v2(
    spec: dict[str, Any],
    evidencia_ids: list[str],
    idx: int,
) -> tuple[list[str], str, str, str] | None:
    """Genera defectos de `recuperador` sin contaminar con `'No aplica'` artificial."""
    claves = list(spec.get("evidencia_clave") or [])
    resp = spec["respuesta"]
    cond = spec["condiciones"]
    fuente = spec["fuente"]

    citas_std = [u for u in claves if re.match(r"^(?:RI-FI|RG)-ART-\d{3}$|^CAL-2026-S[12]-\d{2}$", u)]
    if citas_std and idx % 2 == 0:
        quitada = citas_std[-1]
        ev_sin = [u for u in evidencia_ids if u != quitada]
        borrador = _formatear_borrador(resp, cond, fuente)
        m_art = re.match(r"^(RI-FI|RG)-ART-(\d{3})$", quitada)
        desc_cita = f"el Artículo {int(m_art.group(2))} de {m_art.group(1)} ({quitada})" if m_art else quitada
        pensar = (
            f"Según <chequeo_citas>, la cita [{quitada}] aparece con en_evidencia=false y falta en <evidencia>. "
            f"Corresponde devolver al Recuperador para traer [{quitada}]."
        )
        motivo = f"falta recuperar {desc_cita} en la evidencia (figura en_evidencia=false en chequeo de citas)"
        return ev_sin, borrador, pensar, motivo

    if len(claves) >= 2:
        faltante = claves[-1]
        ev_parcial = [u for u in evidencia_ids if u != faltante]
        doc_f = doc_de_unidad(faltante)
        borrador = _formatear_borrador(
            f"Con lo recuperado solo consta la parte regulada en [{claves[0]}], faltando la normativa de {doc_f}.",
            f"Sujeto a completar la evidencia faltante de {doc_f} respecto de [{claves[0]}].",
            f"[{claves[0]}]",
        )
        pensar = (
            f"Falta en <evidencia> la unidad {faltante} ({doc_f}) necesaria para responder toda la consulta; "
            "debe volver al Recuperador."
        )
        motivo = f"falta recuperar evidencia de {doc_f} para responder de forma completa"
        return ev_parcial, borrador, pensar, motivo

    if spec["estado"] == "suficiente" and evidencia_ids:
        doc_fake = "RI-FI" if idx % 2 == 0 else "RG"
        fake_id = f"{doc_fake}-ART-098"
        borrador = _formatear_borrador(
            f"Según el artículo consultado, aplica la regla indicada [{fake_id}].",
            f"Debe contrastarse la cita real del reglamento {doc_fake} tras reemplazar [{fake_id}].",
            f"[{fake_id}]",
        )
        pensar = (
            f"<chequeo_citas> reporta que [{fake_id}] tiene existe=false y en_evidencia=false; "
            "el Recuperador debe localizar el artículo existente."
        )
        motivo = f"la cita [{fake_id}] no existe en la normativa; el Recuperador debe buscar la fuente real"
        return evidencia_ids, borrador, pensar, motivo

    return None


def construir_registros_verificador_v2(
    prompt_template: str,
    corpus_obj: Any,
    corpus_by_id: dict[str, str],
    seed: int = 202604,
) -> list[dict[str, Any]]:
    """Genera el dataset v2 balanceado y contrastivo para `verificador_v2`."""
    registros: list[dict[str, Any]] = []
    specs = cd.todas_las_especificaciones()

    for idx, spec in enumerate(specs):
        sid = spec["id"]
        split = spec["split"]
        if not _tiene_datos_en_700(spec, corpus_by_id):
            continue

        evidencia_ids = cd.ensamblar_evidencia_ids(spec, corpus_by_id, seed=seed)
        evidencia_ids = [u for u in evidencia_ids if u not in BLOCKED_UNIT_IDS]

        # 1) Ejemplo positivo verdadero para EL 100 % de los specs D4 (`train` y `val`)
        borrador_ok = _formatear_borrador(spec["respuesta"], spec["condiciones"], spec["fuente"])
        pensar_ok = _pensar_positivo_v2(spec, idx)
        motivo_ok = (
            "abstención honesta fiel a la ausencia de evidencia"
            if spec["estado"] != "suficiente"
            else "respuesta completa, citas válidas en <evidencia> y condiciones fieles"
        )
        registros.append(
            _crear_registro_ver(
                prompt_template,
                corpus_obj,
                corpus_by_id,
                f"VER2-{sid}-OK",
                sid,
                split,
                spec["pregunta"],
                spec["estado"],
                evidencia_ids,
                borrador_ok,
                pensar_ok,
                True,
                "fin",
                motivo_ok,
                evidencia_ids,
            )
        )

        # 2) Ejemplo negativo -> `redactor` (mantiene balance entre omisión real y errores semánticos)
        mut_red = _mutar_a_redactor_v2(spec, evidencia_ids, idx)
        if mut_red is not None and (split == "val" or idx % 3 != 2 or spec["bloque"] in ("condiciones_excepciones", "polares_y_lectura", "calculos_y_orden")):
            b_malo, p_red, m_red = mut_red
            registros.append(
                _crear_registro_ver(
                    prompt_template,
                    corpus_obj,
                    corpus_by_id,
                    f"VER2-{sid}-RED",
                    sid,
                    split,
                    spec["pregunta"],
                    spec["estado"],
                    evidencia_ids,
                    b_malo,
                    p_red,
                    False,
                    "redactor",
                    m_red,
                    evidencia_ids,
                )
            )

        # 3) Ejemplo negativo -> `recuperador`
        if idx % 4 == 1:
            mut_rec = _mutar_a_recuperador_v2(spec, evidencia_ids, idx)
            if mut_rec is not None:
                ev_sub, b_rec, p_rec, m_rec = mut_rec
                estado_sub = "suficiente" if ev_sub else "insuficiente"
                registros.append(
                    _crear_registro_ver(
                        prompt_template,
                        corpus_obj,
                        corpus_by_id,
                        f"VER2-{sid}-REC",
                        sid,
                        split,
                        spec["pregunta"],
                        estado_sub,
                        ev_sub,
                        b_rec,
                        p_rec,
                        False,
                        "recuperador",
                        m_rec,
                        ev_sub,
                    )
                )

    # 4) Sumar los casos aritméticos anti-falso-rechazo heredados + casos curados v2
    for caso in CASOS_ARITMETICOS_EXTRA:
        ev_ids = [u for u in caso["evidencia_ids"] if u not in BLOCKED_UNIT_IDS]
        registros.append(
            _crear_registro_ver(
                prompt_template,
                corpus_obj,
                corpus_by_id,
                f"VER2-{caso['id']}",
                caso["id"],
                caso["split"],
                caso["pregunta"],
                "suficiente",
                ev_ids,
                caso["borrador"],
                caso["pensar"],
                caso["aprobado"],
                caso["destino"],
                caso["motivo"],
                ev_ids,
            )
        )

    for caso in CASOS_CURADOS_V2:
        ev_ids = [u for u in caso["evidencia_ids"] if u not in BLOCKED_UNIT_IDS]
        registros.append(
            _crear_registro_ver(
                prompt_template,
                corpus_obj,
                corpus_by_id,
                caso["id"],
                caso["origen_id"],
                caso["split"],
                caso["pregunta"],
                caso["estado"],
                ev_ids,
                caso["borrador"],
                caso["pensar"],
                caso["aprobado"],
                caso["destino"],
                caso["motivo"],
                ev_ids,
            )
        )

    return registros
