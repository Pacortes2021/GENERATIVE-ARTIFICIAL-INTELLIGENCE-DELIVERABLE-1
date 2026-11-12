"""Bloque 1 (citas_cruce: 35 train / 5 val) y Bloque 2 (condiciones_excepciones: 35 train / 5 val)."""

from __future__ import annotations

from typing import Any

# Cada entrada define el caso base que luego construir_dataset.py ensambla con textos literales
# de corpus.json y 03_redactor.txt, barajando el orden de las unidades en <evidencia>.
BLOQUE_1_CITAS_CRUCE: list[dict[str, Any]] = [
    # ---- TRAIN (35 ejemplos) ----
    {
        "id": "B1-T01",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué requisito previo sobre docencia debe cumplir un alumno para inscribir asignaturas y en qué casos un profesor queda exento de ser evaluado en esa encuesta?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-042", "RG-ART-007"],
        "distractores": ["RG-ART-019", "RG-ART-010", "RI-FI-ART-007", "RI-FI-ART-008"],
        "pensar": (
            "Parte 1: [RG-ART-042] indica que para inscribir asignaturas el alumno debe haber respondido "
            "la Encuesta de Evaluación de la Docencia de las asignaturas cursadas en el período lectivo anterior. "
            "Parte 2: [RG-ART-007] señala que quedan exceptuados de la Encuesta de Evaluación Docente los "
            "profesores que hayan impartido docencia en la asignatura por reemplazos u otras circunstancias. "
            "Cada parte tiene su cita distinta y ambas están en la evidencia."
        ),
        "respuesta": (
            "Para inscribir asignaturas el estudiante debe haber respondido la Encuesta de Evaluación de la "
            "Docencia de las asignaturas cursadas en el período lectivo anterior [RG-ART-042]; en cuanto a los "
            "profesores, se exceptúan de esta encuesta quienes hayan impartido docencia por reemplazos u otras circunstancias [RG-ART-007]."
        ),
        "condiciones": (
            "La encuesta se aplica en línea mediante la Plataforma Encuesta Docente en el período fijado para "
            "cada unidad académica y bajo responsabilidad de la Dirección de Docencia [RG-ART-007]; además, la "
            "inscripción exige cumplir prerrequisitos y no inscribir horarios coincidentes en actividades obligatorias [RG-ART-042]."
        ),
        "fuente": "[RG-ART-007] [RG-ART-042]",
    },
    {
        "id": "B1-T02",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "Si un estudiante aprueba una asignatura durante un intercambio académico en el extranjero, ¿qué documentos debe presentar al Vicedecano y cómo incide esa asignatura en su carga académica del semestre frente a una asignatura revalidada?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-024", "RG-ART-039", "RG-ART-041"],
        "distractores": ["RG-ART-037", "RI-FI-ART-020", "RI-FI-ART-021"],
        "pensar": (
            "[RI-FI-ART-024] y [RG-ART-039] establecen que para validar una asignatura cursada en intercambio "
            "en el marco de convenios de movilidad, debe presentar al Vicedecano el programa de la asignatura y "
            "la calificación obtenida debidamente certificadas, y la asignatura validada se reconoce como carga "
            "académica en el semestre en que fue cursada (registrada como VAL en SAC según [RG-ART-041]). En cambio, "
            "[RG-ART-041] establece que las asignaturas revalidadas (REV) no se consideran carga académica del semestre."
        ),
        "respuesta": (
            "Debe presentar al Vicedecano el programa de la asignatura y la calificación obtenida debidamente "
            "certificadas; esa asignatura validada sí se reconoce como carga académica en el semestre en que fue "
            "cursada [RI-FI-ART-024] [RG-ART-039], a diferencia de una asignatura revalidada (REV), que no se "
            "considera carga académica del semestre [RG-ART-041]."
        ),
        "condiciones": (
            "El intercambio debe haberse realizado en el marco de convenios de movilidad suscritos por la UdeC "
            "y la nota validada (sigla VAL) se incorpora al SAC en la Escala Oficial de la Universidad [RI-FI-ART-024] [RG-ART-039] [RG-ART-041]."
        ),
        "fuente": "[RG-ART-039] [RG-ART-041] [RI-FI-ART-024]",
    },
    {
        "id": "B1-T03",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Cuántos créditos transferibles mínimos exige un Programa de Formación Complementaria y qué autoridades integran la comisión que resuelve las postulaciones de ingreso?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-12", "RG-ART-056"],
        "distractores": ["RG-ART-008", "RG-ART-046", "RG-ART-054", "RI-FI-ART-033"],
        "pensar": (
            "La carga mínima (>= 24 créditos transferibles) y el requisito de haber aprobado los dos primeros años "
            "están en [RG-ART-003-DEF-12]. La comisión que resuelve el ingreso (Director de Docencia, Decano de la "
            "Facultad o Director de Escuela y Jefe del Programa de Formación Complementaria) está en [RG-ART-056]."
        ),
        "respuesta": (
            "Un Programa de Formación Complementaria debe tener una carga académica no inferior a 24 créditos "
            "transferibles [RG-ART-003-DEF-12], y las solicitudes de ingreso son resueltas por una Comisión integrada "
            "por el Director de Docencia, el Decano de la Facultad o Director de Escuela y el Jefe del Programa de "
            "Formación Complementaria [RG-ART-056]."
        ),
        "condiciones": (
            "Está dirigido a alumnos regulares de distintas carreras que hayan aprobado los dos primeros años y "
            "cumplan los requisitos de admisión del programa; al ser aceptados quedan adscritos a su Plan de Formación "
            "y deben aprobarlo íntegramente para obtener la certificación [RG-ART-003-DEF-12] [RG-ART-056]."
        ),
        "fuente": "[RG-ART-003-DEF-12] [RG-ART-056]",
    },
    {
        "id": "B1-T04",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "En las carreras de la Facultad de Ingeniería, ¿cómo difiere la composición del Consejo de Carrera respecto del mínimo general establecido para la Universidad y cuál norma prevalece si hubiera desacuerdo?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-032", "RG-ART-009", "RI-FI-ART-034"],
        "distractores": ["RI-FI-ART-033", "RG-ART-010", "RG-ART-011"],
        "pensar": (
            "[RG-ART-009] fija en general: Jefe de Carrera, mínimo 3 profesores de la Facultad, mínimo 2 profesores "
            "de otras Facultades y entre 3 y 4 representantes estudiantiles. [RI-FI-ART-032] en Ingeniería precisa: "
            "Jefatura de Carrera, mínimo 6 docentes del Departamento (plazo indefinido y media jornada o superior), "
            "1 o 2 docentes de otros Departamentos de la Facultad, 3 representantes estudiantiles y 2 académicos de "
            "otras Facultades. Ante inconciliabilidad con el Reglamento General, [RI-FI-ART-034] indica que prevalece el Reglamento General."
        ),
        "respuesta": (
            "En la regla general el Consejo incluye al Jefe de Carrera, al menos 3 profesores de la Facultad, al menos "
            "2 de otras Facultades y de 3 a 4 estudiantes [RG-ART-009]; en Ingeniería se integra por la Jefatura de "
            "Carrera, un mínimo de 6 docentes del Departamento (contrato indefinido y media jornada o superior), 1 o 2 "
            "docentes de otros Departamentos de la Facultad, exactamente 3 representantes estudiantiles y 2 académicos "
            "de otras Facultades [RI-FI-ART-032]. Si disposiciones de ambos reglamentos no se concilian, prevalece siempre el Reglamento General [RI-FI-ART-034]."
        ),
        "condiciones": (
            "En Ingeniería los docentes y académicos de otras Facultades duran 2 años y los representantes estudiantiles "
            "1 año en funciones [RI-FI-ART-032]; en la norma general si no existen profesores de otras Facultades los "
            "reemplazan 2 de la propia Facultad, y los invitados tienen voz pero no voto [RG-ART-009]."
        ),
        "fuente": "[RG-ART-009] [RI-FI-ART-032] [RI-FI-ART-034]",
    },
    {
        "id": "B1-T05",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "Si un estudiante cursó una asignatura en el PLEV y la reprueba, ¿afecta su situación curricular o sus becas? Además, ¿puede haberla abandonado sin dar motivos?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-045", "RG-ART-043"],
        "distractores": ["RG-ART-016", "RG-ART-028", "RI-FI-ART-014", "RI-FI-ART-008"],
        "pensar": (
            "[RG-ART-045] indica que reprobar en el PLEV no afecta la situación curricular ni becas/préstamos, aunque "
            "queda registrado en su hoja curricular. [RG-ART-043] prohíbe expresamente abandonar asignaturas inscritas en el PLEV."
        ),
        "respuesta": (
            "Reprobar una asignatura en el PLEV no afecta la situación curricular del estudiante ni sus antecedentes "
            "para beneficios como becas o préstamos, aunque queda registrado en su hoja curricular [RG-ART-045]; por "
            "otra parte, no está permitido hacer abandono de asignaturas inscritas en el PLEV [RG-ART-043]."
        ),
        "condiciones": (
            "Solo se puede cursar una asignatura en cada PLEV, siendo alumno regular y contando con aprobación del Jefe de Carrera [RG-ART-045]."
        ),
        "fuente": "[RG-ART-043] [RG-ART-045]",
    },
    {
        "id": "B1-T06",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué beneficio económico-académico contempla el Reglamento General para quienes obtuvieron el Grado de Licenciado y desean cursar un postgrado simultáneamente, y qué diferencia formal existe entre Grado de Licenciado y Título Profesional?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-057", "RG-ART-003-DEF-03", "RG-ART-003-DEF-04"],
        "distractores": ["RI-FI-ART-030", "RG-ART-047", "RG-ART-048"],
        "pensar": (
            "[RG-ART-057] señala que alumnos regulares en posesión del Grado Académico de Licenciado pueden ingresar a "
            "postgrado simultáneamente y recibir, a proposición de su Facultad, la Beca Articulación Pregrado-Postgrado. "
            "[RG-ART-003-DEF-03] define Licenciado (aspectos esenciales conceptuales/metodológicos de un área) y "
            "[RG-ART-003-DEF-04] define Título Profesional (formación para desempeño profesional, habilitado por licenciatura cuando se requiera)."
        ),
        "respuesta": (
            "Quienes sean alumnos regulares con Grado Académico de Licenciado pueden ser aceptados simultáneamente en "
            "programas de postgrado y recibir, a proposición de su Facultad, la Beca Articulación Pregrado-Postgrado [RG-ART-057]. "
            "Respecto de la diferencia, el Grado de Licenciado abarca los aspectos esenciales, conceptuales, metodológicos "
            "y de investigación de una disciplina [RG-ART-003-DEF-03], mientras que el Título Profesional entrega la formación "
            "general y científica aplicada para el desempeño profesional, requiriendo la licenciatura previa en las carreras que así lo establezcan [RG-ART-003-DEF-04]."
        ),
        "condiciones": (
            "El otorgamiento de la beca requiere proposición de la Facultad respectiva y mantener calidad de alumno regular de pregrado [RG-ART-057]."
        ),
        "fuente": "[RG-ART-003-DEF-03] [RG-ART-003-DEF-04] [RG-ART-057]",
    },
    {
        "id": "B1-T07",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "Si más de la mitad de los alumnos que rinden una evaluación obtienen nota inferior a 4,0 y un estudiante revisa su prueba pero persiste en desacuerdo con su nota, ¿qué instancias actúan en cada situación?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-013", "RG-ART-025"],
        "distractores": ["RG-ART-012", "RG-ART-021", "RG-ART-026", "RI-FI-ART-011"],
        "pensar": (
            "[RG-ART-013]: cuando más del 50% obtiene nota inferior a 4,0 (o hay situación anómala), el Director de "
            "Departamento convoca a la Comisión de Evaluación (Profesor Encargado + 2 profesores), la que resuelve e "
            "informa al Vicedecano. [RG-ART-025]: ante desacuerdo tras revisión con el profesor, o situaciones del art. 13, "
            "el alumno puede solicitar por escrito y fundamentadamente una nueva revisión al Vicedecano (dentro de 5 días hábiles), "
            "quien si la estima fundamentada nombra una Comisión ad hoc que resuelve inapelablemente en 10 días corridos."
        ),
        "respuesta": (
            "Cuando más del 50 % de quienes rinden obtiene nota inferior a 4,0, el Director del Departamento convoca a "
            "la Comisión de Evaluación para estudiar, resolver e informar al Vicedecano [RG-ART-013]. Si tras revisar la "
            "prueba con el profesor el estudiante sigue en desacuerdo (incluso en situaciones del Art. 13), puede pedir "
            "por escrito una nueva revisión al Vicedecano, quien puede designar una Comisión ad hoc cuya resolución es inapelable [RG-ART-025]."
        ),
        "condiciones": (
            "La Comisión de Evaluación debe formarse al ofertar la asignatura y conocer instrumentos un día antes [RG-ART-013]; "
            "la solicitud al Vicedecano debe presentarse en un máximo de 5 días hábiles tras la revisión con el profesor y "
            "la Comisión ad hoc resuelve en 10 días corridos [RG-ART-025]."
        ),
        "fuente": "[RG-ART-013] [RG-ART-025]",
    },
    {
        "id": "B1-T08",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué organismo universitario debe certificar el fallecimiento de un familiar directo o una enfermedad de un hijo, y ante quién presenta la solicitud el estudiante de Ingeniería si pide suspender sus estudios por ese motivo?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-059", "RI-FI-ART-025", "RG-ART-031"],
        "distractores": ["RG-ART-035", "RG-ART-036", "RG-ART-032"],
        "pensar": (
            "[RG-ART-059] establece que toda situación de salud, socioeconómica, enfermedad de un hijo o fallecimiento "
            "de un familiar directo debe ser evaluada y certificada por la Dirección de Servicios Estudiantiles (o "
            "unidad equivalente en Chillán y Los Ángeles). [RI-FI-ART-025] y [RG-ART-031] señalan que la solicitud de "
            "suspensión de estudios se presenta al Vicedecano dentro de los plazos del calendario (hasta 4 semanas antes del fin del período)."
        ),
        "respuesta": (
            "Debe ser evaluado y certificado por la Dirección de Servicios Estudiantiles o la unidad equivalente en "
            "los campus Chillán y Los Ángeles [RG-ART-059]; con los antecedentes fidedignos y documentos exigidos, la "
            "solicitud de suspensión de estudios se presenta al Vicedecano de la Facultad [RI-FI-ART-025] [RG-ART-031]."
        ),
        "condiciones": (
            "La solicitud debe realizarse hasta 4 semanas antes del término del período lectivo respectivo [RG-ART-031] "
            "y adjuntar los certificados de no deuda de DAFE y Dirección de Bibliotecas [RI-FI-ART-025]."
        ),
        "fuente": "[RG-ART-031] [RG-ART-059] [RI-FI-ART-025]",
    },
    {
        "id": "B1-T09",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "Si una facultad modifica el Plan de Estudio de una carrera y un estudiante antiguo pide cambiarse al plan nuevo, ¿cuántas veces y cuándo puede pedirlo, y cómo se tratan sus asignaturas de la carrera que cambian de código?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-10", "RG-ART-040"],
        "distractores": ["RG-ART-037", "RG-ART-041", "RI-FI-ART-020", "RI-FI-ART-028"],
        "pensar": (
            "[RG-ART-003-DEF-10] (párrafo final): los alumnos afectos al plan antiguo pueden solicitar su adscripción al "
            "nuevo plan al Vicedecano solo por una vez y durante el período de inscripción de asignaturas correspondiente "
            "al inicio del año académico en que entra en vigencia (sin perjuicio de planes transitorios). "
            "[RG-ART-040]: las asignaturas aprobadas en una versión anterior del plan de la misma carrera con otro código "
            "en SAC se traspasan mediante homologación según la tabla establecida por el Vicedecano."
        ),
        "respuesta": (
            "El estudiante afecto al plan antiguo puede solicitar su adscripción al plan nuevo al Vicedecano por una única "
            "vez durante el período de inscripción de asignaturas de inicio del año académico en que entra en vigencia [RG-ART-003-DEF-10]; "
            "las asignaturas ya aprobadas con otro código de una versión anterior del plan de su misma carrera se traspasan mediante homologación [RG-ART-040]."
        ),
        "condiciones": (
            "La tabla de asignaturas homologables la fija el Vicedecano de la carrera, con visto bueno del Vicedecano "
            "que dicta la asignatura, y la registra UDARAE en el SAC [RG-ART-040]; ello sin perjuicio de los planes transitorios de ajuste [RG-ART-003-DEF-10]."
        ),
        "fuente": "[RG-ART-003-DEF-10] [RG-ART-040]",
    },
    {
        "id": "B1-T10",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "Un estudiante ya titulado en una carrera que ofrece dos menciones o títulos distintos quiere volver a optar al segundo título. ¿Cuándo puede pedir su reingreso y cómo se anota esa nueva solicitud frente al reingreso ordinario del Artículo 44?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-047", "RG-ART-044"],
        "distractores": ["RG-ART-048", "RG-ART-049", "RI-FI-ART-028", "RG-ART-033"],
        "pensar": (
            "[RG-ART-047] indica que en carreras que ofrecen más de un grado, título o mención, los ya graduados o titulados "
            "pueden solicitar su reingreso en el semestre siguiente a su egreso para optar a otro grado, título o mención. "
            "[RG-ART-044] regula el reingreso general a una misma carrera: entra a Primer Año como alumno nuevo sin "
            "derecho a validar, revalidar, convalidar ni reconocer aprobadas (salvo que no haya incurrido en pérdida de carrera y lo pida en 30 días)."
        ),
        "respuesta": (
            "En carreras que ofrecen más de un grado, título o mención, los ya graduados o titulados pueden solicitar reingreso "
            "en el semestre siguiente a su egreso para cumplir las exigencias del nuevo grado, título o mención [RG-ART-047]; "
            "en cambio, el reingreso ordinario a una misma carrera obliga a entrar a Primer Año como alumno nuevo sin validar, "
            "revalidar, convalidar ni reconocer asignaturas aprobadas [RG-ART-044]."
        ),
        "condiciones": (
            "En el reingreso ordinario, si el estudiante no incurrió en pérdida de carrera, puede pedir dentro de los "
            "30 primeros días del primer semestre mantener su situación académica anterior [RG-ART-044]."
        ),
        "fuente": "[RG-ART-044] [RG-ART-047]",
    },
    {
        "id": "B1-T11",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué plazo tiene el Vicedecano en el Reglamento General para resolver una convalidación o revalidación y en qué plazo máximo desde el ingreso debe pedirla el estudiante en Ingeniería?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-037", "RI-FI-ART-022"],
        "distractores": ["RI-FI-ART-020", "RI-FI-ART-021", "RI-FI-ART-023", "RG-ART-038"],
        "pensar": (
            "[RG-ART-037] establece que el Vicedecano, previo informe del Departamento a cargo, resuelve dentro de "
            "un plazo de quince días. [RI-FI-ART-022] señala que en Ingeniería el estudiante puede solicitar convalidación, "
            "revalidación y reconocimiento por única vez durante las cuatro primeras semanas de ingreso a la nueva carrera "
            "(excepto Primer Año Común)."
        ),
        "respuesta": (
            "El Vicedecano resuelve dentro de un plazo de 15 días previo informe del Departamento a cargo de la asignatura [RG-ART-037], "
            "y el estudiante de Ingeniería debe presentar la solicitud por única vez durante las cuatro primeras semanas de ingreso a la nueva carrera [RI-FI-ART-022]."
        ),
        "condiciones": (
            "Los estudiantes de Primer Año Común no pueden revalidar ni convalidar asignaturas [RI-FI-ART-022]; las "
            "convalidaciones provenientes de otra institución requieren certificado de calificaciones y programas acreditados [RG-ART-037]."
        ),
        "fuente": "[RG-ART-037] [RI-FI-ART-022]",
    },
    {
        "id": "B1-T12",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "Si un estudiante ingresa directamente a segundo o tercer año de Ingeniería por convalidaciones o revalidaciones, ¿qué asignaturas se excluyen al verificar el requisito de créditos aprobados del Art. 14 b) y qué pasa con su carga semestral?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-015", "RG-ART-041"],
        "distractores": ["RI-FI-ART-014", "RG-ART-028", "RG-ART-037", "RI-FI-ART-022"],
        "pensar": (
            "[RI-FI-ART-015] indica que para aplicar el Art. 14° inciso b) queda sometido a aprobar los créditos del nivel "
            "al que ingresa y no se contabilizan los créditos revalidados, convalidados o reconocidos. [RG-ART-041] añade "
            "que las asignaturas convalidadas (CON), revalidadas (REV), homologadas (HOM) o reconocidas (REC) no se consideran carga académica del semestre."
        ),
        "respuesta": (
            "Al aplicar el inciso b) del Art. 14°, el estudiante debe aprobar los créditos correspondientes al nivel al que "
            "ingresa y no se contabilizan los créditos revalidados, convalidados o reconocidos [RI-FI-ART-015]; además, "
            "ninguna asignatura convalidada, revalidada, homologada o reconocida cuenta como carga académica del semestre [RG-ART-041]."
        ),
        "condiciones": (
            "Todas esas asignaturas deben quedar registradas en el SAC con Nota Final y su sigla respectiva: CON, REV, HOM o REC [RG-ART-041]."
        ),
        "fuente": "[RG-ART-041] [RI-FI-ART-015]",
    },
    {
        "id": "B1-T13",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "En el primer semestre de 2026, ¿qué fechas corresponden a las actividades de bienvenida UdeC y hasta cuándo tienen clases las asignaturas anuales respecto de las semestrales?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S1-01", "CAL-2026-S1-04", "CAL-2026-S1-05"],
        "distractores": ["CAL-2026-S1-02", "CAL-2026-S1-03", "CAL-2026-S1-06"],
        "pensar": (
            "[CAL-2026-S1-01] fija Vinculación a la Vida Universitaria del 02 al 06 de marzo. [CAL-2026-S1-04] fija el "
            "término de clases de asignaturas semestrales el 10 de julio, y [CAL-2026-S1-05] el de asignaturas anuales el 24 de julio."
        ),
        "respuesta": (
            "Las actividades de bienvenida e inducción (Vinculación a la Vida Universitaria) se realizan del 02 al 06 de "
            "marzo de 2026 [CAL-2026-S1-01]; mientras las asignaturas semestrales terminan sus clases el 10 de julio [CAL-2026-S1-04], "
            "las asignaturas anuales terminan el primer semestre el 24 de julio [CAL-2026-S1-05]."
        ),
        "condiciones": (
            "Las fechas corresponden al Primer Semestre del Calendario de Docencia de Pregrado 2026 [CAL-2026-S1-01] [CAL-2026-S1-04] [CAL-2026-S1-05]."
        ),
        "fuente": "[CAL-2026-S1-01] [CAL-2026-S1-04] [CAL-2026-S1-05]",
    },
    {
        "id": "B1-T14",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué documentos respaldan un Alumno Libre y qué efectos tiene su condición sobre el título o la certificación de asignaturas aprobadas?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-18", "RG-ART-053"],
        "distractores": ["RG-ART-003-DEF-16", "RG-ART-003-DEF-14", "RG-ART-003-DEF-15", "RG-ART-058"],
        "pensar": (
            "[RG-ART-003-DEF-18] define al Alumno Libre (posee Título Profesional o Grado Académico, no es alumno de pregrado "
            "ni opta a título/grado, pero sí puede solicitar certificación de asignaturas aprobadas). [RG-ART-053] precisa que "
            "sus requisitos, derechos y obligaciones se rigen por un reglamento especial de la Universidad y convenios aplicables."
        ),
        "respuesta": (
            "El Alumno Libre es quien posee un Título Profesional o Grado Académico y es aceptado para cursar asignaturas; "
            "no adquiere calidad de alumno de pregrado, no queda adscrito a una carrera y no puede optar a un grado ni título "
            "por esas asignaturas, aunque sí puede pedir certificación de las aprobadas [RG-ART-003-DEF-18]. Su régimen completo "
            "se rige por un reglamento especial y los convenios correspondientes [RG-ART-053]."
        ),
        "condiciones": (
            "Estas normas delimitan al Alumno Libre frente al alumno regular de pregrado [RG-ART-003-DEF-18] [RG-ART-053]."
        ),
        "fuente": "[RG-ART-003-DEF-18] [RG-ART-053]",
    },
    {
        "id": "B1-T15",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Cuándo se considera que un alumno es 'egresado' frente a 'regular en proceso de titulación' y cuánto tiempo máximo le otorga el Reglamento General tras egresar para completar su titulación?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-22", "RG-ART-003-DEF-23", "RG-ART-049"],
        "distractores": ["RG-ART-003-DEF-15", "RI-FI-ART-029", "RI-FI-ART-031"],
        "pensar": (
            "[RG-ART-003-DEF-22]: alumno egresado aprobó todas las actividades académicas del plan y solo le faltan actividades "
            "finales de graduación/titulación. [RG-ART-003-DEF-23]: alumno regular en proceso de titulación es el egresado que "
            "ya está realizando dichas actividades finales. [RG-ART-049]: dispone de un plazo máximo de seis semestres."
        ),
        "respuesta": (
            "Es alumno egresado quien aprobó todas las actividades académicas de su plan y solo le resta cumplir sus actividades "
            "finales de graduación o titulación [RG-ART-003-DEF-22], y pasa a ser alumno regular en proceso de titulación cuando se "
            "encuentra realizando efectivamente esas actividades finales [RG-ART-003-DEF-23]. Dispone de un plazo máximo de seis "
            "semestres para completarlas [RG-ART-049]."
        ),
        "condiciones": (
            "Vencido el plazo de seis semestres, las exigencias aplicables para obtener el título o grado las fija el Reglamento "
            "Interno de Docencia de Pregrado de cada Facultad [RG-ART-049]."
        ),
        "fuente": "[RG-ART-003-DEF-22] [RG-ART-003-DEF-23] [RG-ART-049]",
    },
    {
        "id": "B1-T16",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿En qué documento normativo debe indicarse si un estudiante cursó un Programa de Formación Complementaria al egresar, y qué concepto aparecería en un Diploma de Título si obtuvo promedio 5,5?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-047", "RG-ART-048"],
        "distractores": ["RG-ART-056", "RG-ART-003-DEF-12", "RI-FI-ART-030", "RG-ANEXO-23"],
        "pensar": (
            "[RG-ART-047] exige que las Facultades o Escuelas indiquen en cada expediente de solicitud de Título o Grado "
            "el Programa de Formación Complementaria aprobado para su certificación. [RG-ART-048] establece que un promedio "
            "de 5,5 cae en el rango 5,0 - 5,6: 'Aprobado con Distinción'."
        ),
        "respuesta": (
            "El Programa de Formación Complementaria aprobado debe indicarse en el expediente con que la Facultad o Escuela "
            "solicita el otorgamiento del Título o Grado [RG-ART-047]; además, con nota 5,5 en el Título Profesional corresponde "
            "consignar el concepto 'Aprobado con Distinción' (rango 5,0 a 5,6) [RG-ART-048]."
        ),
        "condiciones": (
            "En carreras no terminales el Diploma de Grado indica la nota numérica, mientras el concepto aplica al Diploma de "
            "Título Profesional y a Diplomas de Licenciado en carreras terminales [RG-ART-048]."
        ),
        "fuente": "[RG-ART-047] [RG-ART-048]",
    },
    {
        "id": "B1-T17",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Cuál es la diferencia en atribuciones entre el Decano y el Vicedecano dentro de una Facultad según el Reglamento General, y qué pasa en Ingeniería con materias no previstas en su reglamento interno?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-004", "RI-FI-ART-035"],
        "distractores": ["RG-ART-005", "RG-ART-006", "RI-FI-ART-033", "RI-FI-ART-034"],
        "pensar": (
            "[RG-ART-004] asigna al Decano la responsabilidad máxima de la docencia de pregrado en la Facultad, mientras el "
            "Vicedecano asume la administración general de los estudios de pregrado y el cumplimiento de plazos docentes. "
            "[RI-FI-ART-035] asigna al Decano de Ingeniería resolver las situaciones no previstas en el reglamento interno."
        ),
        "respuesta": (
            "El Decano es el responsable máximo de la docencia de pregrado en la Facultad, en tanto el Vicedecano asume la "
            "administración general de los estudios de pregrado y la responsabilidad por el cumplimiento de los plazos docentes [RG-ART-004]; "
            "en Ingeniería, además, las situaciones no previstas en el Reglamento Interno las resuelve el Decano en el ámbito de su competencia [RI-FI-ART-035]."
        ),
        "condiciones": (
            "Para disciplinas fuera de las Facultades existentes, el Consejo Académico puede hacerlas depender temporalmente "
            "de otra unidad académica [RG-ART-004]."
        ),
        "fuente": "[RG-ART-004] [RI-FI-ART-035]",
    },
    {
        "id": "B1-T18",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué órgano preside el Jefe de Carrera en el Reglamento General y qué funciones específicas cumple el Comité de Docencia y Asuntos Estudiantiles en la Facultad de Ingeniería?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-008", "RG-ART-011", "RI-FI-ART-033"],
        "distractores": ["RG-ART-009", "RG-ART-010", "RI-FI-ART-032"],
        "pensar": (
            "[RG-ART-008] (función 10) y [RG-ART-011] indican que el Jefe de Carrera preside y convoca tanto al Consejo de Carrera "
            "como al Comité de Docencia y Asuntos Estudiantiles. [RI-FI-ART-033] detalla que en Ingeniería el Comité vela por "
            "derechos y deberes del alumno y resuelve solicitudes relativas a su desempeño o situación académica."
        ),
        "respuesta": (
            "El Jefe de Carrera preside y convoca el Consejo de Carrera y el Comité de Docencia y Asuntos Estudiantiles [RG-ART-008] [RG-ART-011]; "
            "en la Facultad de Ingeniería, ese Comité se encarga de todos los asuntos que afecten al alumno en su vida académica, "
            "velando por sus derechos y deberes y resolviendo solicitudes sobre su desempeño o situación académica [RI-FI-ART-033]."
        ),
        "condiciones": (
            "En Ingeniería sus integrantes duran 2 años y lo conforman la Jefatura de Carrera, 2 docentes elegidos por el Consejo "
            "de Carrera y 1 representante estudiantil de ese Consejo designado por el Centro de Alumnos [RG-ART-011] [RI-FI-ART-033]."
        ),
        "fuente": "[RG-ART-008] [RG-ART-011] [RI-FI-ART-033]",
    },
    {
        "id": "B1-T19",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Cuándo pierde vigencia el estado de alumno regular entre períodos académicos y qué ocurre si un alumno regular que no inscribió asignaturas tenía una asignatura anual del período anterior?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-050", "RG-ART-029"],
        "distractores": ["RG-ART-030", "RG-ART-003-DEF-15", "RG-ART-003-DEF-19", "RG-ART-042"],
        "pensar": (
            "[RG-ART-050] señala que la calidad de alumno regular se mantiene hasta el inicio del período de inscripción de "
            "asignaturas del Período Lectivo Ordinario siguiente. [RG-ART-029] indica que quien estando habilitado no inscribe "
            "asignaturas pierde el derecho a continuar estudios y la calidad de alumno, a menos que en el período lectivo anterior haya inscrito una o más asignaturas anuales."
        ),
        "respuesta": (
            "La calidad de alumno regular se mantiene hasta el inicio del período de inscripción de asignaturas del Período Lectivo "
            "Ordinario siguiente [RG-ART-050]; si un estudiante habilitado no inscribe asignaturas en ese período no pierde la calidad "
            "de alumno ni el derecho a continuar estudios siempre que en el período lectivo anterior haya inscrito una o más asignaturas anuales [RG-ART-029]."
        ),
        "condiciones": (
            "De no haber inscrito asignaturas anuales en el período previo, la falta de inscripción estando habilitado implica "
            "pérdida del derecho a continuar estudios y de la calidad de alumno de pregrado [RG-ART-029]."
        ),
        "fuente": "[RG-ART-029] [RG-ART-050]",
    },
    {
        "id": "B1-T20",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué diferencia hay entre el mecanismo de Inicio Adelantado y el examen regular de reconocimiento de contenidos del Artículo 23 de Ingeniería?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-038", "RI-FI-ART-023"],
        "distractores": ["RG-ART-041", "RI-FI-ART-022", "RG-ART-037"],
        "pensar": (
            "[RI-FI-ART-023]: el reconocimiento ordinario en Ingeniería se solicita a la Vicedecanatura dentro de los primeros 30 días "
            "del período lectivo, con informe del Departamento, y rinde un examen exhaustivo ante Comisión departamental. "
            "[RG-ART-038]: además del reconocimiento general dentro de los 30 primeros días, define el Inicio Adelantado para "
            "alumnos regulares de nuevo ingreso que obtengan > 5,7 en la Evaluación Diagnóstica de una asignatura fundamental, habilitándolos para rendir una evaluación específica."
        ),
        "respuesta": (
            "En el reconocimiento ordinario de Ingeniería el estudiante pide ante la Vicedecanatura, dentro de los primeros 30 días "
            "del período lectivo, rendir un examen exhaustivo evaluado por una Comisión del Departamento previo informe de éste [RI-FI-ART-023]; "
            "en cambio, el Inicio Adelantado es exclusivo para alumnos regulares de nuevo ingreso en asignaturas fundamentales que superen 5,7 en la Evaluación Diagnóstica y rindan una evaluación específica sin cursar la asignatura [RG-ART-038]."
        ),
        "condiciones": (
            "En Inicio Adelantado, la nota obtenida en la evaluación específica pasa a ser la nota final si se aprueba [RG-ART-038]; "
            "en ambos casos el reconocimiento requiere existir en el Reglamento Interno de la Facultad [RG-ART-038]."
        ),
        "fuente": "[RG-ART-038] [RI-FI-ART-023]",
    },
    {
        "id": "B1-T21",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "Durante el segundo semestre de 2026, ¿en qué fechas se suspenden las actividades de docencia de pregrado, en qué días está prohibido hacer evaluaciones y qué feriado nacional cae inmediatamente después de esa suspensión?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S2-06", "CAL-2026-S2-07", "CAL-2026-S2-09"],
        "distractores": ["CAL-2026-S2-08", "CAL-2026-S2-10", "CAL-2026-S1-07"],
        "pensar": (
            "[CAL-2026-S2-06] fija suspensión de actividades de docencia del 14 al 17 de septiembre; [CAL-2026-S2-09] fija feriado nacional "
            "el viernes 18 de septiembre; y [CAL-2026-S2-07] indica que no se realizarán evaluaciones el 21 y 22 de septiembre."
        ),
        "respuesta": (
            "En el segundo semestre de 2026 las actividades de docencia se suspenden del 14 al 17 de septiembre [CAL-2026-S2-06], "
            "el feriado nacional inmediato es el viernes 18 de septiembre [CAL-2026-S2-09], y no se realizarán evaluaciones los días 21 y 22 de septiembre [CAL-2026-S2-07]."
        ),
        "condiciones": (
            "Todas las fechas corresponden al Segundo Semestre del Calendario de Docencia de Pregrado 2026 [CAL-2026-S2-06] [CAL-2026-S2-07] [CAL-2026-S2-09]."
        ),
        "fuente": "[CAL-2026-S2-06] [CAL-2026-S2-07] [CAL-2026-S2-09]",
    },
    {
        "id": "B1-T22",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué entidad resuelve los cambios o ingresos de carrera solicitados en UDARAE según el Reglamento General y qué promedio mínimo exige Ingeniería si un alumno viene de otra carrera de la misma Facultad frente a otra Facultad?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-054", "RG-ART-055", "RI-FI-ART-018", "RI-FI-ART-017"],
        "distractores": ["RI-FI-ART-019", "RG-ART-005"],
        "pensar": (
            "En [RG-ART-054] y [RG-ART-055], las solicitudes ingresadas en UDARAE las resuelve una Comisión integrada por "
            "el Director de Docencia, el Decano de la Facultad y el Jefe de Carrera, sancionada por el Rector y registrada en SAC por UDARAE. "
            "Para promedios mínimos: [RI-FI-ART-018] fija 4,2 dentro de la misma Facultad y [RI-FI-ART-017] fija 4,5 desde otra Facultad u otra Universidad chilena."
        ),
        "respuesta": (
            "Las solicitudes recepcionadas por UDARAE las resuelve una Comisión integrada por el Director de Docencia, el Decano "
            "de la Facultad y el Jefe de Carrera, con sanción del Rector y registro en SAC por UDARAE [RG-ART-054] [RG-ART-055]. "
            "En Ingeniería se exige promedio ponderado mínimo de 4,2 para cambio dentro de la misma Facultad [RI-FI-ART-018] y de 4,5 para ingresar desde otra Facultad UdeC u otra Universidad chilena [RI-FI-ART-017]."
        ),
        "condiciones": (
            "En todos los casos el solicitante debe ser alumno regular, conservar el derecho a continuar estudios en su carrera de origen y sujetarse a los cupos anuales disponibles [RG-ART-054] [RG-ART-055] [RI-FI-ART-017] [RI-FI-ART-018]."
        ),
        "fuente": "[RG-ART-054] [RG-ART-055] [RI-FI-ART-017] [RI-FI-ART-018]",
    },
    {
        "id": "B1-T23",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Quién designa al Jefe de Carrera y cómo se estructura la Comisión de Evaluación de cada asignatura?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-008", "RG-ART-013"],
        "distractores": ["RG-ART-006", "RG-ART-012", "RI-FI-ART-032", "RI-FI-ART-033"],
        "pensar": (
            "[RG-ART-008]: el Jefe de Carrera es designado por el Decano respectivo con conocimiento del Consejo de Carrera, "
            "cumpliendo el perfil propuesto por dicho Consejo. [RG-ART-013]: la Comisión de Evaluación se conforma por el "
            "Profesor Encargado más dos profesores designados por el Director de Departamento que ofrece la asignatura."
        ),
        "respuesta": (
            "El Jefe de Carrera es designado por el Decano respectivo, con conocimiento del Consejo de Carrera [RG-ART-008], "
            "mientras que la Comisión de Evaluación de cada asignatura se integra por el Profesor Encargado más dos profesores designados por el Director del Departamento que ofrece la asignatura [RG-ART-013]."
        ),
        "condiciones": (
            "El Jefe de Carrera debe cumplir el perfil propuesto por el Consejo de Carrera [RG-ART-008], y la Comisión de Evaluación debe conformarse al ofertar la asignatura y conocer instrumentos y pautas al menos un día antes de su aplicación [RG-ART-013]."
        ),
        "fuente": "[RG-ART-008] [RG-ART-013]",
    },
    {
        "id": "B1-T24",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué sistema computacional registra la carga académica y notas de los alumnos, y con qué aplicación se graban las Notas Finales del Acta?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-05", "RG-ART-027"],
        "distractores": ["RG-ART-006", "RG-ART-041", "RG-ART-012", "RI-FI-ART-024"],
        "pensar": (
            "[RG-ART-003-DEF-05] define el Sistema de Administración Curricular (SAC) que centraliza información curricular, "
            "controla planes, registra inscripción y situación académica. [RG-ART-027] señala que para generar el Acta de "
            "Notas en el SAC, las Notas Finales se registran y graban por el Profesor Encargado mediante INFODA (o aplicación informática futura)."
        ),
        "respuesta": (
            "La información curricular e inscripción se centralizan en el Sistema de Administración Curricular (SAC) [RG-ART-003-DEF-05], "
            "y el Profesor Encargado registra y graba las Notas Finales mediante la aplicación informática INFODA (u otra equivalente futura) para generar el Acta en el SAC [RG-ART-027]."
        ),
        "condiciones": (
            "Un ejemplar impreso del Acta lo firman los miembros de la Comisión de Evaluación y el Director de Departamento "
            "(o Vicedecano si no depende de un Departamento), archivándose en la Secretaría Académica; las modificaciones posteriores requieren visto bueno del Vicedecano antes del término del semestre siguiente [RG-ART-027]."
        ),
        "fuente": "[RG-ART-003-DEF-05] [RG-ART-027]",
    },
    {
        "id": "B1-T25",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué diferencia existe en la forma de comunicar evaluaciones ordinarias frente a los certámenes y evaluación de recuperación en Ingeniería, y qué información obligatoria entrega el profesor en la primera semana?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-010", "RI-FI-ART-012"],
        "distractores": ["RG-ART-019", "RI-FI-ART-011", "RG-ART-022", "RG-ART-025"],
        "pensar": (
            "[RI-FI-ART-010]: las evaluaciones deben programarse y comunicarse con al menos una semana de anticipación, "
            "pero en Ingeniería las fechas de certámenes y evaluación de recuperación deben informarse en el syllabus. "
            "[RI-FI-ART-012]: en la primera semana de clases el Profesor Encargado entrega por escrito requisitos, "
            "actividades, instrumentos de evaluación y ponderación (incluyendo la evaluación de recuperación)."
        ),
        "respuesta": (
            "Toda evaluación debe comunicarse al menos con una semana de anticipación, pero para asignaturas impartidas por la "
            "Facultad de Ingeniería las fechas de certámenes y evaluación de recuperación deben figurar en el syllabus [RI-FI-ART-010]; "
            "además, en la primera semana de clases el Profesor Encargado debe entregar por escrito requisitos, actividades, instrumentos y ponderaciones, incluida la evaluación de recuperación [RI-FI-ART-012]."
        ),
        "condiciones": (
            "Los instrumentos pueden incluir certámenes, proyectos, informes, tareas, test, prácticas, laboratorios, exámenes u otros según la naturaleza del curso [RI-FI-ART-010]."
        ),
        "fuente": "[RI-FI-ART-010] [RI-FI-ART-012]",
    },
    {
        "id": "B1-T26",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué pasa cuando a un estudiante ya se le aprobó la reincorporación tras suspender estudios en relación con el reconocimiento de su Licenciatura y el Plan de Estudio aplicable?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-028", "RG-ART-033"],
        "distractores": ["RI-FI-ART-027", "RI-FI-ART-031", "RG-ART-003-DEF-10", "RG-ART-044"],
        "pensar": (
            "[RG-ART-033] establece que quien solicita su reincorporación debe adscribirse al Plan de Estudio que se esté impartiendo "
            "a la fecha de reincorporación (salvo alumnos en intercambio). [RI-FI-ART-028] agrega que en Ingeniería si al suspender "
            "había cumplido los requisitos de la Licenciatura en Ciencias de la Ingeniería, ésta se le reconoce y las asignaturas posteriores se reconocen por equivalencia con el plan vigente."
        ),
        "respuesta": (
            "Quienes se reincorporan deben adscribirse al Plan de Estudio vigente a la fecha de su reincorporación [RG-ART-033]; "
            "no obstante, si al suspender en Ingeniería ya habían cumplido los requisitos de la Licenciatura en Ciencias de la Ingeniería, "
            "ésta les será reconocida y las asignaturas cursadas después se reconocerán según su equivalencia con el Plan de Estudio vigente [RI-FI-ART-028]."
        ),
        "condiciones": (
            "La obligación de adscribirse al plan vigente exceptúa a los alumnos en intercambio, quienes conservan su mismo plan [RG-ART-033]."
        ),
        "fuente": "[RG-ART-033] [RI-FI-ART-028]",
    },
    {
        "id": "B1-T27",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿En qué consiste la diferencia entre un Alumno Visitante y un Alumno en Intercambio según el Artículo 3° del Reglamento General, y qué pasa con las fechas en SAC cuando el alumno de intercambio valida asignaturas?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-16", "RG-ART-003-DEF-17", "RG-ART-039"],
        "distractores": ["RG-ART-003-DEF-18", "RI-FI-ART-024", "RG-ART-053"],
        "pensar": (
            "[RG-ART-003-DEF-16]: Alumno Visitante proviene de otra universidad chilena o extranjera e ingresa temporalmente a UdeC. "
            "[RG-ART-003-DEF-17]: Alumno en Intercambio es alumno de pregrado de la UdeC que realiza estadías externas bajo convenios de movilidad. "
            "[RG-ART-039]: al validarlas, la nota se registra en SAC en la Escala Oficial y se reconoce como carga académica en el semestre en que fue cursada."
        ),
        "respuesta": (
            "El Alumno Visitante viene de otra universidad chilena o extranjera para estudiar temporalmente en la UdeC [RG-ART-003-DEF-16], "
            "mientras que el Alumno en Intercambio es un estudiante de pregrado de la UdeC que realiza estadías en otras instituciones bajo convenios de movilidad [RG-ART-003-DEF-17]. "
            "Sus asignaturas aprobadas y validadas se incorporan al SAC en la Escala Oficial y se reconocen como carga académica del semestre en que se cursaron [RG-ART-039]."
        ),
        "condiciones": (
            "Ambos regímenes requieren autorización/patrocinio o convenios de movilidad y certificación formal de programa y notas [RG-ART-003-DEF-16] [RG-ART-003-DEF-17] [RG-ART-039]."
        ),
        "fuente": "[RG-ART-003-DEF-16] [RG-ART-003-DEF-17] [RG-ART-039]",
    },
    {
        "id": "B1-T28",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué dos componentes integran el sistema de apoyo al estudiante de una Facultad y qué ocurre cuando un estudiante realiza actividades extracurriculares deportivas bajo tuición institucional?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-015", "RG-ART-046"],
        "distractores": ["RG-ART-008", "RG-ART-052", "RG-ART-003-DEF-09"],
        "pensar": (
            "[RG-ART-015] detalla los dos componentes mínimos del sistema de apoyo: Tutorías Académicas (Tutor Académico) "
            "y Monitores Estudiantiles. [RG-ART-046] establece que actividades artísticas, culturales, deportivas o recreativas "
            "bajo tuición/patrocinio de organismos UdeC con programa aprobado por Dirección de Docencia y unidad respectiva se reconocen como asignaturas complementarias."
        ),
        "respuesta": (
            "El sistema de apoyo contempla al menos un Sistema de Tutorías Académicas (orientación académica y derivación) y "
            "un Sistema de Monitores Estudiantiles (inducción, adaptación y apoyo remedial) [RG-ART-015]. Por su parte, las actividades "
            "deportivas, culturales o artísticas bajo tuición o patrocinio de la Universidad pueden reconocerse en el currículum como asignaturas complementarias [RG-ART-046]."
        ),
        "condiciones": (
            "El reconocimiento como asignatura complementaria exige contar con un programa de actividades aprobado por la Dirección de Docencia y la unidad respectiva [RG-ART-046]."
        ),
        "fuente": "[RG-ART-015] [RG-ART-046]",
    },
    {
        "id": "B1-T29",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Cómo se clasifican las asignaturas según su función en el Plan de Estudio (obligatorias, electivas, complementarias, libre elección) y cuánto porcentaje mínimo de créditos SCT debe dedicarse a formación integral?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-09", "RG-ART-003-DEF-10"],
        "distractores": ["RG-ART-003-DEF-08", "RG-ART-003-DEF-11", "RG-ART-017"],
        "pensar": (
            "[RG-ART-003-DEF-09] enumera: obligatorias, electivas, complementarias y de libre elección (y adicionalmente carácter "
            "fundamental, integradora o formación integral). [RG-ART-003-DEF-10] letra g) exige que los créditos de asignaturas "
            "que contribuyen a la formación integral sean al menos el 10% del total de créditos transferibles del plan de estudios."
        ),
        "respuesta": (
            "En un plan de estudio las asignaturas adquieren la calidad de obligatorias, electivas, complementarias o de libre elección [RG-ART-003-DEF-09], "
            "y las que contribuyen a la formación integral del alumno deben representar al menos el 10 % del total de créditos transferibles del plan de estudios [RG-ART-003-DEF-10]."
        ),
        "condiciones": (
            "Adicionalmente pueden tener carácter fundamental, integrador o de formación integral, y dictarse de modo presencial o semipresencial [RG-ART-003-DEF-09]."
        ),
        "fuente": "[RG-ART-003-DEF-09] [RG-ART-003-DEF-10]",
    },
    {
        "id": "B1-T30",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué diferencia hay entre el Programa de Asignatura y el Syllabus respecto a quién los aprueba o confecciona y qué ocurre cuando cambian los requisitos reglamentarios antes de una resolución?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-11", "RG-ART-019", "RG-TRANS-001"],
        "distractores": ["RI-FI-ART-010", "RI-FI-ART-012", "RG-ART-010"],
        "pensar": (
            "[RG-ART-003-DEF-11]: el Programa de Asignatura lo aprueba la Facultad de la carrera a proposición de la que dicta "
            "(y debe revisarse en período no superior a la duración de la carrera), mientras el Syllabus es una guía docente "
            "confeccionada por el profesor de la asignatura. [RG-ART-019] exige al Profesor Encargado dar a conocer ambos al inicio "
            "y [RG-TRANS-001] señala que situaciones pendientes se rigen por la norma vigente al ocurrir, salvo que el nuevo reglamento mejore la condición del alumno."
        ),
        "respuesta": (
            "El Programa de Asignatura es aprobado por la Facultad de la carrera a proposición de la que imparte el curso, mientras "
            "que el Syllabus es la guía docente de planificación confeccionada por el profesor para facilitar el aprendizaje [RG-ART-003-DEF-11]; "
            "ambos deben darse a conocer al inicio de la dictación por escrito u otro canal oficial que permita almacenarlos o imprimirlos [RG-ART-019]. "
            "Respecto a cambios reglamentarios, las situaciones pendientes siguen la norma vigente al ocurrir, salvo que el nuevo texto mejore la condición del alumno [RG-TRANS-001]."
        ),
        "condiciones": (
            "Los Programas deben revisarse en un plazo no superior a los años de duración de la carrera [RG-ART-003-DEF-11]."
        ),
        "fuente": "[RG-ART-003-DEF-11] [RG-ART-019] [RG-TRANS-001]",
    },
    {
        "id": "B1-T31",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "Si un estudiante pierde su condición de alumno por faltas disciplinarias versus por no pedir reincorporación después de suspender estudios, ¿qué normas regulan cada causal?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-051", "RG-ART-033"],
        "distractores": ["RG-ART-003-DEF-20", "RG-ART-028", "RG-ART-034", "RG-ART-029"],
        "pensar": (
            "[RG-ART-051]: se pierde la condición de alumno de pregrado por resolución adoptada conforme al Reglamento 'Normas de Conducta de los Estudiantes'. "
            "[RG-ART-033]: la suspensión de estudios puede durar máximo 3 años calendario y si el alumno no solicita reincorporación dentro de ese plazo pierde la calidad de alumno de pregrado."
        ),
        "respuesta": (
            "La pérdida disciplinaria procede por resolución dictada en aplicación del Reglamento 'Normas de Conducta de los Estudiantes' [RG-ART-051]; "
            "en cambio, tras suspender estudios el alumno pierde esa calidad si no solicita su reincorporación dentro del plazo máximo de tres años calendario [RG-ART-033]."
        ),
        "condiciones": (
            "Si la suspensión fue por salud, la reincorporación exige antecedentes oficiales que acrediten el cese de los impedimentos y resuelve el Decano [RG-ART-033]."
        ),
        "fuente": "[RG-ART-033] [RG-ART-051]",
    },
    {
        "id": "B1-T32",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué funciones específicas tiene la Secretaría Académica de una Facultad en relación con las asignaturas dictadas por varios Departamentos o Facultades?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-005", "RG-ART-006"],
        "distractores": ["RG-ART-004", "RG-ART-014", "RG-ART-027", "RG-ART-012"],
        "pensar": (
            "[RG-ART-005]: la Secretaría Académica depende del Vicedecano y coordina horarios, registra y archiva información "
            "de alumnos, verifica normas, confecciona informes/certificados y tramita solicitudes. [RG-ART-006]: si una asignatura "
            "se dicta con varios Departamentos o Facultades, su administración recae en el Vicedecano de la Facultad a la cual está adscrita la asignatura."
        ),
        "respuesta": (
            "La Secretaría Académica, dependiente del Vicedecano, coordina horarios, registra y archiva antecedentes de alumnos, "
            "verifica cumplimiento normativo, emite informes/certificados y tramita solicitudes [RG-ART-005]; cuando participan varios "
            "Departamentos o Facultades en una asignatura, su administración corresponde al Vicedecano de la Facultad a la cual está adscrita la asignatura [RG-ART-006]."
        ),
        "condiciones": (
            "La carga docente de los profesores que participan debe ser asignada por cada Director de Departamento y registrada en el SAC [RG-ART-006]."
        ),
        "fuente": "[RG-ART-005] [RG-ART-006]",
    },
    {
        "id": "B1-T33",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué dos modalidades de ingreso existen en el Primer Año de Ingeniería y cuándo postulan al plan de especialidad quienes entran sin especialidad?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-003", "RI-FI-ART-004", "RI-FI-ART-005"],
        "distractores": ["RI-FI-ART-006", "RI-FI-ART-001", "RI-FI-ART-002"],
        "pensar": (
            "[RI-FI-ART-003]: modalidad mixta con Ingreso Directo a una carrera e Ingreso Común sin especialidad. "
            "[RI-FI-ART-004]: la Facultad define anualmente los cupos de ambos ingresos y algunas carreras pueden tener cupos solo vía Ingreso Directo. "
            "[RI-FI-ART-005]: los estudiantes de Ingreso Común postulan al término de su segundo semestre de permanencia."
        ),
        "respuesta": (
            "Existe una modalidad mixta compuesta por Ingreso Directo a una carrera e Ingreso Común sin especialidad [RI-FI-ART-003], "
            "definiendo la Facultad cada año los cupos respectivos (pudiendo ciertas carreras ofrecer cupos únicamente vía Ingreso Directo) [RI-FI-ART-004]. "
            "Quienes ingresan por Ingreso Común postulan a las carreras al término de su segundo semestre de permanencia [RI-FI-ART-005]."
        ),
        "condiciones": (
            "Para la postulación de Ingreso Común solo se consideran las asignaturas obligatorias de Primer Año [RI-FI-ART-005]."
        ),
        "fuente": "[RI-FI-ART-003] [RI-FI-ART-004] [RI-FI-ART-005]",
    },
    {
        "id": "B1-T34",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "En caso de filtrarse preguntas de una prueba en la UdeC y comprobarse que un alumno obtuvo ilícitamente información antes de rendir un proyecto obligatorio grupal fuera del aula, ¿cómo proceden el Director de Departamento y el profesor?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-013", "RG-ART-023"],
        "distractores": ["RG-ART-025", "RG-ART-026", "RG-ART-051", "RI-FI-ART-010"],
        "pensar": (
            "[RG-ART-013]: frente a filtración de preguntas o de la prueba completa, el Director de Departamento convoca a la "
            "Comisión de Evaluación, que estudia la situación, resuelve e informa al Vicedecano. [RG-ART-023]: el alumno que "
            "obtenga o facilite información ilícita puede ser calificado con la nota mínima, o con NCR si afecta gran parte de un instrumento requisito fuera del aula (como proyectos o trabajos grupales)."
        ),
        "respuesta": (
            "Ante filtración de preguntas o pruebas, el Director del Departamento convoca a la Comisión de Evaluación para que estudie "
            "el caso, resuelva e informe al Vicedecano [RG-ART-013]; en paralelo, el alumno que obtenga o facilite información de forma "
            "ilícita puede ser calificado con la nota mínima o, tratándose de gran parte de un proyecto o trabajo grupal requisito fuera del aula, con NCR (no cumple requisito) [RG-ART-023]."
        ),
        "condiciones": (
            "Tanto obtener nota final inferior a 4,0 como recibir el concepto NCR implica reprobar la asignatura [RG-ART-023]."
        ),
        "fuente": "[RG-ART-013] [RG-ART-023]",
    },
    {
        "id": "B1-T35",
        "bloque": "citas_cruce",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué feriados nacionales contempla el segundo semestre de 2026 en agosto, octubre y diciembre, y cuándo comienzan las Evaluaciones de Recuperación de ese mismo semestre?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S2-08", "CAL-2026-S2-10", "CAL-2026-S2-11", "CAL-2026-S2-05"],
        "distractores": ["CAL-2026-S2-09", "CAL-2026-S2-04"],
        "pensar": (
            "Feriados nacionales S2: [CAL-2026-S2-08] jueves 20 de agosto, [CAL-2026-S2-10] lunes 12 de octubre, [CAL-2026-S2-11] martes 08 de diciembre. "
            "Evaluaciones de Recuperación S2: [CAL-2026-S2-05] 14 – 23 de diciembre."
        ),
        "respuesta": (
            "Los feriados nacionales en esos meses del segundo semestre de 2026 son el jueves 20 de agosto [CAL-2026-S2-08], "
            "lunes 12 de octubre [CAL-2026-S2-10] y martes 08 de diciembre [CAL-2026-S2-11]; las Evaluaciones de Recuperación "
            "se rinden del 14 al 23 de diciembre [CAL-2026-S2-05]."
        ),
        "condiciones": (
            "Las fechas pertenecen al Segundo Semestre del Calendario de docencia de pregrado 2026 [CAL-2026-S2-05] [CAL-2026-S2-08] [CAL-2026-S2-10] [CAL-2026-S2-11]."
        ),
        "fuente": "[CAL-2026-S2-05] [CAL-2026-S2-08] [CAL-2026-S2-10] [CAL-2026-S2-11]",
    },

    # ---- VAL BLOQUE 1 (5 ejemplos con combinaciones distintas) ----
    {
        "id": "B1-V01",
        "bloque": "citas_cruce",
        "split": "val",
        "modo": "cruce",
        "pregunta": "¿Qué facilidades académicas corresponden a dirigentes estudiantiles acreditados y qué deben hacer estudiantes con impedimentos religiosos o discapacidad al inscribir asignaturas?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-052", "RG-ART-020"],
        "distractores": ["RG-ART-014", "RG-ART-015", "RG-ART-042", "RI-FI-ART-013"],
        "pensar": (
            "[RG-ART-052]: el Vicedecano otorga facilidades flexibilizando requisitos en clases teóricas y prácticas a "
            "Presidentes de Centros de Alumnos, Presidentes/Secretarios/Tesoreros de Federaciones (Concepción, Chillán, Los Ángeles) "
            "y representantes oficiales en actividades extraprogramáticas, sin eximir de requisitos de aprobación. "
            "[RG-ART-020]: impedimento religioso debe acreditarse al inscribir ante consideración del Profesor Encargado; discapacidad acreditada "
            "se solicita al momento de inscribir ante el Vicedecano, quien consulta al Programa INCLUDEC."
        ),
        "respuesta": (
            "A representantes estudiantiles reconocidos (Presidentes de Centros de Alumnos, Presidentes/Secretarios/Tesoreros de "
            "Federaciones de Concepción, Chillán y Los Ángeles, y delegados oficiales extraprogramáticos) el Vicedecano les otorga "
            "flexibilización en clases teóricas y prácticas cuando sea posible [RG-ART-052]. Por otro lado, los impedimentos religiosos "
            "deben acreditarse al inscribir para que el Profesor Encargado los considere, y en discapacidad acreditada la solicitud se "
            "presenta al inscribir ante el Vicedecano, quien resuelve previa consulta a INCLUDEC [RG-ART-020]."
        ),
        "condiciones": (
            "Los dirigentes estudiantiles igualmente deben cumplir los requisitos para aprobar las asignaturas [RG-ART-052]; en caso "
            "de discapacidad, el Vicedecano informa lo resuelto a los vicedecanos de las facultades que dictan los cursos [RG-ART-020]."
        ),
        "fuente": "[RG-ART-020] [RG-ART-052]",
    },
    {
        "id": "B1-V02",
        "bloque": "citas_cruce",
        "split": "val",
        "modo": "cruce",
        "pregunta": "¿En qué año comenzó a regir la modificación orgánica del Reglamento General, dentro de qué plazo debieron adecuar sus reglamentos internos las Facultades y qué dice el Reglamento Interno de Ingeniería sobre su propia relación con el Reglamento General?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-PREAMBULO", "RG-TRANS-002", "RI-FI-ART-002"],
        "distractores": ["RG-ART-001", "RG-ART-060", "RG-TRANS-001"],
        "pensar": (
            "[RG-PREAMBULO]: la modificación orgánica aprobada el 18 de enero de 2018 comienza a regir a contar del año académico 2018. "
            "[RG-TRANS-002]: las Facultades debieron adecuar sus Reglamentos Internos en plazo no superior a 90 días hábiles desde la vigencia. "
            "[RI-FI-ART-002]: señala que el Reglamento Interno de Docencia de Pregrado de Ingeniería complementa al Reglamento General, a las Normas de Ingreso y al Reglamento Interno de la Facultad."
        ),
        "respuesta": (
            "La modificación orgánica comenzó a regir desde el año académico 2018 [RG-PREAMBULO] y otorgó a las Facultades un plazo "
            "máximo de 90 días hábiles desde su vigencia para adecuar sus Reglamentos Internos [RG-TRANS-002]; en Ingeniería, su "
            "Reglamento Interno complementa al Reglamento General de Docencia de Pregrado, las Normas de Ingreso y el Reglamento Interno de la Facultad [RI-FI-ART-002]."
        ),
        "condiciones": (
            "Además, cada Facultad debe contar obligatoriamente con su propio Reglamento Interno de Docencia de Pregrado [RG-PREAMBULO] [RG-TRANS-002]."
        ),
        "fuente": "[RG-PREAMBULO] [RG-TRANS-002] [RI-FI-ART-002]",
    },
    {
        "id": "B1-V03",
        "bloque": "citas_cruce",
        "split": "val",
        "modo": "cruce",
        "pregunta": "¿Qué requisitos generales exige el Reglamento General de Docencia de Pregrado para definir un 'Programa de Asignatura' frente a la regla de duración de cada período en que se organizan las asignaturas?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-11", "RG-ART-018"],
        "distractores": ["RG-ART-003-DEF-09", "RG-ART-016", "RG-ART-017", "RG-ART-019"],
        "pensar": (
            "[RG-ART-003-DEF-11] fija el contenido del Programa (identificación, descripción, resultados de aprendizaje, calidad, "
            "carácter, modalidad, prerrequisitos, duración, créditos UdeC y SCT, horas de trabajo académico, unidades, metodología, evaluaciones y bibliografía). "
            "[RG-ART-018] establece que las asignaturas pueden organizarse en forma continua durante dos semestres, durante un semestre o durante un período distinto a un semestre según el plan de estudio."
        ),
        "respuesta": (
            "El Programa de Asignatura debe contener identificación, descripción, resultados de aprendizaje, calidad, carácter, modalidad, "
            "prerrequisitos, duración, créditos UdeC y SCT, horas de trabajo académico, unidades temáticas, metodología, evaluaciones/ponderación y bibliografía [RG-ART-003-DEF-11]; "
            "en cuanto a su organización temporal, las asignaturas pueden dictarse durante dos semestres continuos, un semestre o un período distinto a un semestre [RG-ART-018]."
        ),
        "condiciones": (
            "La duración específica de la asignatura debe quedar establecida en el Plan de Estudio y figurar en el respectivo Programa de Asignatura [RG-ART-003-DEF-11] [RG-ART-018]."
        ),
        "fuente": "[RG-ART-003-DEF-11] [RG-ART-018]",
    },
    {
        "id": "B1-V04",
        "bloque": "citas_cruce",
        "split": "val",
        "modo": "cruce",
        "pregunta": "¿Qué autoridad asume la administración centralizada de aulas en los campus Chillán y Los Ángeles frente a Concepción, y quién declara la salud incompatible de un alumno?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-014", "RG-ART-032"],
        "distractores": ["RG-ART-059", "RG-ART-004", "RG-ART-005", "RG-ART-033"],
        "pensar": (
            "[RG-ART-014]: las aulas centralizadas las administra la Dirección de Docencia en general, pero en Chillán y Los Ángeles "
            "esas atribuciones las ejerce el Director General del campus respectivo. [RG-ART-032]: la suspensión por salud o condición "
            "física incompatible la decide el Decano en resolución fundada previo informe de DISE (o unidad equivalente en Chillán/Los Ángeles)."
        ),
        "respuesta": (
            "Las atribuciones sobre utilización de aulas centralizadas corresponden a la Dirección de Docencia, pero en los campus "
            "Chillán y Los Ángeles son ejercidas por el Director General del campus correspondiente [RG-ART-014]; en cuanto a salud "
            "o condición física incompatible con la carrera, la suspensión la decide el Decano mediante resolución fundada previo informe de la Dirección de Servicios Estudiantiles o unidad de campus equivalente [RG-ART-032]."
        ),
        "condiciones": (
            "El Decano debe informar dicha resolución al Vicerrector y a UDARAE para su registro en el SAC [RG-ART-032]."
        ),
        "fuente": "[RG-ART-014] [RG-ART-032]",
    },
    {
        "id": "B1-V05",
        "bloque": "citas_cruce",
        "split": "val",
        "modo": "cruce",
        "pregunta": "En el calendario 2026, ¿cuántos feriados nacionales hay entre marzo y julio (primer semestre) y en qué fechas caen la pausa activa y las vacaciones de invierno?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S1-07", "CAL-2026-S1-09", "CAL-2026-S1-10", "CAL-2026-S1-11", "CAL-2026-S1-12", "CAL-2026-S1-13", "CAL-2026-S1-14"],
        "distractores": [],
        "pensar": (
            "Wait: aquí hay 7 IDs si incluimos todos los feriados S1 + pausa + vacaciones, pero MAX_EVIDENCIA es 6! "
            "Ojo: si usamos solo 6 evidencias en <evidencia>, ajustemos la pregunta a pausa activa, vacaciones de invierno y los feriados de mayo a julio (que caben exactos en 6 unidades!)."
        ),
    },
]

# Reemplazamos B1-V05 con <= 6 unidades reales para respetar MAX_EVIDENCIA = 6 sin saturar!
BLOQUE_1_CITAS_CRUCE[-1] = {
    "id": "B1-V05",
    "bloque": "citas_cruce",
    "split": "val",
    "modo": "cruce",
    "pregunta": "En el calendario del primer semestre de 2026, ¿en qué fechas son la pausa activa, las vacaciones de invierno y los feriados nacionales de mayo?",
    "feedback": None,
    "estado": "suficiente",
    "evidencia_clave": ["CAL-2026-S1-07", "CAL-2026-S1-14", "CAL-2026-S1-10", "CAL-2026-S1-11"],
    "distractores": ["CAL-2026-S1-08", "CAL-2026-S1-12"],
    "pensar": (
        "[CAL-2026-S1-07]: pausa activa de docencia del 11 al 15 de mayo. "
        "[CAL-2026-S1-14]: vacaciones de invierno (aprobación transitoria) del 30 de junio al 05 de julio. "
        "Feriados de mayo: [CAL-2026-S1-10] viernes 01 de mayo y [CAL-2026-S1-11] jueves 21 de mayo."
    ),
    "respuesta": (
        "En el primer semestre de 2026, la pausa activa de docencia ocurre del 11 al 15 de mayo [CAL-2026-S1-07], "
        "los feriados nacionales de mayo son el viernes 01 de mayo [CAL-2026-S1-10] y el jueves 21 de mayo [CAL-2026-S1-11], "
        "y las vacaciones de invierno (con aprobación transitoria) van del 30 de junio al 05 de julio [CAL-2026-S1-14]."
    ),
    "condiciones": (
        "Además, el calendario establece que los días 18 y 19 de mayo no se realizarán evaluaciones [CAL-2026-S1-08]."
    ),
    "fuente": "[CAL-2026-S1-07] [CAL-2026-S1-08] [CAL-2026-S1-10] [CAL-2026-S1-11] [CAL-2026-S1-14]",
}


BLOQUE_2_CONDICIONES_EXCEPCIONES: list[dict[str, Any]] = [
    # ---- TRAIN (35 ejemplos) ----
    {
        "id": "B2-T01",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones, límites de tiempo y excepciones rigen el abandono de asignaturas sin especificación de motivos?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-043"],
        "distractores": ["RG-ART-042", "RG-ART-045", "RI-FI-ART-008", "RI-FI-ART-009", "CAL-2026-S1-03"],
        "pensar": (
            "[RG-ART-043] contiene: 1) plazo de 4 semanas desde inicio de clases; 2) utilizable 1 sola vez por asignatura; "
            "3) sin quedar bajo el mínimo de créditos; 4) excepción para asignaturas < 1 semestre (plazo lo fija la Facultad); "
            "5) prohibición expresa para asignaturas inscritas en el PLEV."
        ),
        "respuesta": (
            "El alumno puede hacer abandono de asignaturas semestrales o anuales sin especificar motivos dentro de las "
            "cuatro semanas siguientes al inicio de clases fijado en el Calendario de Docencia de Pregrado [RG-ART-043]."
        ),
        "condiciones": (
            "Rigen cuatro condiciones y excepciones: (1) solo puede usarse una vez en cada asignatura; (2) no debe dejar al "
            "alumno con menos créditos que el mínimo establecido; (3) en asignaturas de duración menor a un semestre, el plazo "
            "de abandono lo fija la Facultad que las dicta; y (4) no se puede abandonar asignaturas inscritas en el PLEV [RG-ART-043]."
        ),
        "fuente": "[RG-ART-043]",
    },
    {
        "id": "B2-T02",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿En qué condiciones queda un estudiante que decide reingresar a la misma carrera y qué excepción contempla la normativa si no perdió la carrera?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-044"],
        "distractores": ["RG-ART-033", "RG-ART-034", "RG-ART-047", "RI-FI-ART-027", "RI-FI-ART-028"],
        "pensar": (
            "[RG-ART-044]: ingresa a Primer Año como alumno nuevo, sujeto a exigencias vigentes al reingreso, sin derecho a "
            "validar, revalidar, convalidar ni reconocer aprobadas. Excepción inciso 2: si no incurrió en pérdida de carrera, "
            "puede solicitar dentro de los 30 primeros días del primer semestre mantener su situación académica anterior."
        ),
        "respuesta": (
            "Quien reingresa a la misma carrera debe hacerlo a Primer Año como alumno nuevo, sujeto a los requisitos vigentes "
            "al reingreso y sin derecho a validar, revalidar, convalidar o reconocer asignaturas aprobadas [RG-ART-044]."
        ),
        "condiciones": (
            "Excepción: si el alumno no incurrió en pérdida de carrera, puede solicitar dentro de los treinta primeros días del "
            "primer semestre de permanencia mantener su situación académica anterior [RG-ART-044]."
        ),
        "fuente": "[RG-ART-044]",
    },
    {
        "id": "B2-T03",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué actividades académicas quedan excluidas de la Evaluación de Recuperación y en qué situación excepcional puede un alumno no rendirla sin mantener automáticamente su nota?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-022"],
        "distractores": ["RI-FI-ART-012", "RG-ART-026", "RG-ART-023", "CAL-2026-S1-06", "CAL-2026-S2-05"],
        "pensar": (
            "[RG-ART-022] excluye de Evaluación de Recuperación: laboratorios, talleres, proyectos, memorias, seminarios, "
            "actividades clínicas u otras que requieran tiempo prolongado de ejecución. Quien tiene derecho y no se presenta "
            "mantiene su Nota Final, salvo que el Vicedecano de la Facultad que dicta la asignatura, por razones fundadas, autorice "
            "ausentarse: queda pendiente (PEN) con nuevo plazo fijado por resolución del Vicedecano."
        ),
        "respuesta": (
            "No son objeto de Evaluación de Recuperación las actividades que por sus características exigen tiempo prolongado "
            "de ejecución, tales como laboratorios, talleres, proyectos, memorias, seminarios o actividades clínicas [RG-ART-022]."
        ),
        "condiciones": (
            "Si un alumno con derecho no se presenta mantiene su Nota Final, salvo autorización por razones fundadas del Vicedecano "
            "de la Facultad que dicta la asignatura; en ese caso queda con situación pendiente (consignando PEN si corresponde) "
            "y dispone del plazo que fije la resolución del Vicedecano, comunicada al Profesor Encargado y al Jefe de Carrera [RG-ART-022]."
        ),
        "fuente": "[RG-ART-022]",
    },
    {
        "id": "B2-T04",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué plazos y condiciones rigen el derecho del estudiante a conocer pautas, revisar evaluaciones escritas y apelar una calificación ante desacuerdo?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-025"],
        "distractores": ["RG-ART-013", "RG-ART-026", "RG-ART-021", "RI-FI-ART-010", "RI-FI-ART-011"],
        "pensar": (
            "[RG-ART-025]: profesor informa notas y pautas máx 10 días hábiles; alumno tiene 5 días hábiles para revisar; "
            "Vicedecano puede ampliar plazos por razones justificadas; profesor conserva evaluaciones >= 30 días hábiles tras "
            "el período; si persiste desacuerdo, apelación escrita y fundada al Vicedecano en máx 5 días hábiles desde revisión "
            "con profesor; Comisión ad hoc nombrada por Vicedecano resuelve en 10 días corridos con acta inapelable firmada por alumno."
        ),
        "respuesta": (
            "Los profesores deben entregar calificaciones y pautas en un máximo de 10 días hábiles y los alumnos disponen de 5 días "
            "hábiles para revisar sus evaluaciones; ante desacuerdo tras esa revisión, pueden apelar por escrito y fundamentadamente "
            "al Vicedecano dentro de 5 días hábiles, resolviendo luego una Comisión ad hoc de manera inapelable en 10 días corridos [RG-ART-025]."
        ),
        "condiciones": (
            "El Vicedecano puede ampliar por razones justificadas los plazos iniciales de 10 y 5 días hábiles; el profesor debe "
            "comunicar fechas y horario de revisión al entregar notas y conservar las evaluaciones escritas al menos 30 días hábiles "
            "después de concluido el período; el Vicedecano solo nombra la Comisión ad hoc si estima fundamentada la solicitud [RG-ART-025]."
        ),
        "fuente": "[RG-ART-025]",
    },
    {
        "id": "B2-T05",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué derechos, plazos y requisitos tiene una estudiante embarazada que interrumpe temporalmente sus estudios?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-036"],
        "distractores": ["RG-ART-031", "RG-ART-033", "RG-ART-059", "RI-FI-ART-025", "RI-FI-ART-027"],
        "pensar": (
            "[RG-ART-036]: durante embarazo y hasta dos meses después del nacimiento; conserva calidad de alumna regular, derechos "
            "y obligaciones; requiere certificado de médico o matrona visado por DISE (o equivalente Chillán/Los Ángeles); al concluir, "
            "el Comité de Docencia y Asuntos Estudiantiles decide facilidades (nuevos plazos o derivar pendientes al próximo período)."
        ),
        "respuesta": (
            "Tiene derecho a interrumpir temporalmente sus estudios durante el embarazo y hasta dos meses después del nacimiento, "
            "conservando su calidad de alumna regular y manteniendo todos sus derechos y obligaciones [RG-ART-036]."
        ),
        "condiciones": (
            "Debe presentar certificado del médico o matrona tratante visado por la Dirección de Servicios Estudiantiles (o equivalente "
            "en Chillán y Los Ángeles); al terminar la interrupción, el Comité de Docencia y Asuntos Estudiantiles define las facilidades "
            "para finalizar asignaturas (nuevos plazos o derivación al período lectivo siguiente) [RG-ART-036]."
        ),
        "fuente": "[RG-ART-036]",
    },
    {
        "id": "B2-T06",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿En qué condiciones e instancias puede solicitar continuación de estudios un alumno en Baja Académica frente a uno en Baja por no Inscripción?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-030", "RI-FI-ART-016"],
        "distractores": ["RG-ART-028", "RG-ART-029", "RI-FI-ART-014", "RI-FI-ART-033"],
        "pensar": (
            "[RG-ART-030]: Baja por no Inscripción -> máx 1 año ante Comité de Docencia y Asuntos Estudiantiles, recurrible al "
            "Vicedecano dentro de 5º día hábil. Baja Académica -> solo en 3 oportunidades y dentro de 1 año: 1ª ante Comité "
            "(resuelve <= 10 días, apelable 5 días hábiles al Vicedecano y luego Decano), 2ª ante Vicedecano (<= 10 días hábiles, "
            "apelable al Decano en 5 días hábiles), 3ª ante Decano (<= 10 días hábiles) y excepcionalmente por única vez por gracia ante Vicerrector (5 días hábiles)."
        ),
        "respuesta": (
            "En Baja por no Inscripción puede solicitar continuación de estudios dentro de un año al Comité de Docencia y Asuntos "
            "Estudiantiles (apelable al Vicedecano dentro del quinto día hábil). En Baja Académica solo dispone de tres oportunidades, "
            "siempre dentro del plazo de un año: la 1ª ante el Comité, la 2ª ante el Vicedecano y la 3ª ante el Decano [RG-ART-030]."
        ),
        "condiciones": (
            "Los plazos de respuesta son máximo 10 días (1ª solicitud) o 10 días hábiles (2ª y 3ª), con apelación dentro de 5 días hábiles "
            "ante la autoridad superior; excepcionalmente y por única vez se puede recurrir por gracia al Vicerrector dentro de 5 días hábiles "
            "de lo resuelto por el Decano [RG-ART-030]. En Ingeniería se explicita Comité (1ª), Vicedecanatura (2ª) y Decanatura (última dentro de Facultad) [RI-FI-ART-016]."
        ),
        "fuente": "[RG-ART-030] [RI-FI-ART-016]",
    },
    {
        "id": "B2-T07",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué causales permiten autorizar una inscripción bajo el mínimo de créditos en la Universidad y qué otras exigencias bloquean o anulan la inscripción de asignaturas?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-042", "RI-FI-ART-008"],
        "distractores": ["RI-FI-ART-007", "RI-FI-ART-009", "RG-ART-043", "RG-ART-029"],
        "pensar": (
            "[RI-FI-ART-008] + [RG-ART-042]: mínimo 8 créditos en Ingeniería, salvo quienes estén terminando estudios (solo las que "
            "faltan) o quienes por oferta inferior / falta de requisitos se vean impedidos (en [RG-ART-042] autorizado por Vicedecano). "
            "Además [RG-ART-042]: cumplir prerrequisitos (si no queda sin efecto), haber respondido Encuesta de Evaluación Docente del "
            "período previo, no inscribir actividades obligatorias con horarios coincidentes y realizarlo en fechas del calendario."
        ),
        "respuesta": (
            "Se permite inscribir menos del mínimo de 8 créditos únicamente a quienes estén terminando sus estudios (inscribiendo las "
            "asignaturas que les falten) y cuando la oferta de créditos sea menor al mínimo por situación curricular y falta de prerrequisitos "
            "(autorizado por el Vicedecano) [RG-ART-042] [RI-FI-ART-008]."
        ),
        "condiciones": (
            "Además la inscripción exige: realizarse en fechas del Calendario (salvo autorización excepcional del Vicedecano fuera de plazo), "
            "cumplir prerrequisitos —de lo contrario queda sin efecto—, haber respondido la Encuesta Docente del período anterior y evitar "
            "horarios coincidentes en actividades obligatorias [RG-ART-042]."
        ),
        "fuente": "[RG-ART-042] [RI-FI-ART-008]",
    },
    {
        "id": "B2-T08",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué requisitos de quórum, frecuencia de sesiones y sanciones por inasistencia rigen el funcionamiento del Consejo de Carrera en el Reglamento General?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-010"],
        "distractores": ["RG-ART-009", "RG-ART-011", "RI-FI-ART-032", "RI-FI-ART-033", "RG-ART-008"],
        "pensar": (
            "[RG-ART-010]: sesionar >= 3 veces/semestre; extraordinarias con acuerdo del 60 % de miembros en horarios compatibles con "
            "alumnos; quórum para sesionar >= 60 %; acuerdos por mayoría de asistentes; 2 ausencias injustificadas consecutivas -> "
            "representante estudiantil reemplazado y académico llamado de atención por escrito; convocatoria >= 1 semana con tabla."
        ),
        "respuesta": (
            "El Consejo de Carrera debe sesionar al menos 3 veces por semestre, con quórum mínimo del 60 % de sus miembros para sesionar "
            "y voto conforme de la mayoría de los asistentes para tomar acuerdos [RG-ART-010]."
        ),
        "condiciones": (
            "Las extraordinarias requieren acuerdo del 60 % y horario que facilite asistencia estudiantil; la convocatoria debe enviarse al menos "
            "una semana antes con tabla (agregando puntos hasta el día previo); y dos ausencias consecutivas injustificadas implican reemplazo "
            "para un representante estudiantil o llamado de atención escrito para un académico [RG-ART-010]."
        ),
        "fuente": "[RG-ART-010]",
    },
    {
        "id": "B2-T09",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿En qué casos se aplica la pauta de conceptos del Diploma ('Aprobado por Unanimidad', 'con Distinción', 'con Distinción Máxima') y en cuáles NO corresponde incluir concepto?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-048"],
        "distractores": ["RG-ART-047", "RI-FI-ART-030", "RG-ART-003-DEF-03", "RG-ART-003-DEF-04", "RG-ANEXO-20"],
        "pensar": (
            "[RG-ART-048]: la pauta (4,0-4,9 Unanimidad; 5,0-5,6 Distinción; 5,7-7,0 Distinción Máxima) se aplica a Diplomas de "
            "Título Profesional y a Diplomas de Grado Académico de Licenciado en carreras terminales (donde UdeC no otorga título profesional). "
            "En Diplomas de Grado Académico no terminales se indica la Nota obtenida, no el concepto."
        ),
        "respuesta": (
            "La escala de conceptos (4,0–4,9 Aprobado por Unanimidad; 5,0–5,6 Aprobado con Distinción; 5,7–7,0 Aprobado con Distinción Máxima) "
            "aplica únicamente al Diploma de Título Profesional y al Diploma de Grado Académico de Licenciado en carreras terminales, es decir, "
            "aquellas donde la UdeC no otorga título profesional [RG-ART-048]."
        ),
        "condiciones": (
            "En los demás Diplomas de Grado Académico (carreras no terminales) se consigna únicamente la nota obtenida; la forma de calcular "
            "la nota depende del Reglamento Interno de la Facultad respectiva [RG-ART-048]."
        ),
        "fuente": "[RG-ART-048]",
    },
    {
        "id": "B2-T10",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones limitan el derecho a cursar asignaturas en el Período Lectivo Extraordinario de Verano (PLEV)?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-045"],
        "distractores": ["RG-ART-016", "RG-ART-043", "RI-FI-ART-014", "RG-ART-028", "RG-ART-042"],
        "pensar": (
            "[RG-ART-045]: opcional; solo una asignatura por cada PLEV; ser alumno regular UdeC; aprobación del Jefe de Carrera "
            "(también en especial para adelantar secuencia); para dictar una asignatura la Facultad fija mínimo de inscritos."
        ),
        "respuesta": (
            "El PLEV es opcional, permite cursar una única asignatura por período y exige ser alumno regular de la Universidad de Concepción "
            "junto con la aprobación del Jefe de Carrera [RG-ART-045]."
        ),
        "condiciones": (
            "La aprobación del Jefe de Carrera también aplica para usar el PLEV con el fin de adelantar secuencia curricular; las Facultades fijan "
            "el número mínimo de inscritos para dictarlo y una eventual reprobación queda en la hoja curricular sin afectar situación académica ni beneficios [RG-ART-045]."
        ),
        "fuente": "[RG-ART-045]",
    },
    {
        "id": "B2-T11",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué debe ocurrir si a un estudiante se le programan simultáneamente el mismo día y horario dos actividades académicas obligatorias que son requisito de asignaturas?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-014"],
        "distractores": ["RG-ART-042", "RG-ART-026", "RG-ART-020", "RI-FI-ART-009"],
        "pensar": (
            "[RG-ART-014] párrafo final: si por razones justificadas se programan en el mismo día y horario actividades requisitos, "
            "el alumno debe priorizar la actividad académica que no tiene posibilidad de ser recuperada y tendrá derecho a recuperar la no efectuada; "
            "el Jefe de Carrera vela por ello e informa a los profesores encargados."
        ),
        "respuesta": (
            "Si la programación simultánea ocurre por razones justificadas, el alumno debe priorizar la actividad académica que no tiene "
            "posibilidad de ser recuperada y tiene derecho a recuperar la actividad no efectuada [RG-ART-014]."
        ),
        "condiciones": (
            "El Jefe de Carrera debe velar por el cumplimiento de este derecho e informar a los Profesores Encargados involucrados [RG-ART-014]."
        ),
        "fuente": "[RG-ART-014]",
    },
    {
        "id": "B2-T12",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones y prohibiciones rigen la renuncia a la carrera en Ingeniería y qué obligaciones no extingue?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-026", "RG-ART-034", "RG-ART-035"],
        "distractores": ["RI-FI-ART-025", "RG-ART-031", "RG-ART-033"],
        "pensar": (
            "[RI-FI-ART-026] + [RG-ART-034]: por escrito al Vicedecano (quien remite a Dirección de Docencia); es irrevocable e "
            "impide reincorporarse a la carrera; adjunta certificados de DAFE y Biblioteca ([RI-FI-ART-025] / [RG-ART-035]); y "
            "[RG-ART-034] precisa que la renuncia no libera al alumno de obligaciones pendientes con la Universidad."
        ),
        "respuesta": (
            "La renuncia se presenta por escrito ante el Vicedecano (quien la remite a Dirección de Docencia para registro), es irrevocable "
            "e impide volver a reincorporarse a la carrera [RG-ART-034] [RI-FI-ART-026]."
        ),
        "condiciones": (
            "Debe adjuntar certificado DAFE de no deudas (o garantía debida) y certificado de la Dirección de Bibliotecas de no adeudar material "
            "[RG-ART-035] [RI-FI-ART-026]; además, renunciar no libera al estudiante de las obligaciones pendientes con la Universidad [RG-ART-034]."
        ),
        "fuente": "[RG-ART-034] [RG-ART-035] [RI-FI-ART-026]",
    },
    {
        "id": "B2-T13",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué reglas, excepciones y efectos sobre el promedio rigen las calificaciones NCR, APR y REP y el sistema de aproximación decimal?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-021", "RG-ART-023", "RG-ART-024"],
        "distractores": ["RI-FI-ART-011", "RG-ART-027", "RG-ART-048"],
        "pensar": (
            "[RG-ART-023]: escala 1 a 7 con un decimal; centésimas < 5 no afectan, >= 5 suben a décima superior; aprueba >= 4,0; "
            "si incumple requisitos del programa se califica NCR y reprueba. [RG-ART-021]: cursos cualitativos usan APR/REP. "
            "[RG-ART-024]: al calcular Prom. Pond. o Prom. Curr., NCR equivale a 1,0 mientras que APR y REP no se consideran."
        ),
        "respuesta": (
            "Las notas numéricas van de 1 a 7 con un decimal (centésimas < 5 mantienen la décima y >= 5 la aproximan al alza) y aprueban "
            "desde 4,0; incumplir un requisito del programa se califica con NCR y reprueba la asignatura [RG-ART-023], mientras en cursos "
            "cualitativos se consigna APR o REP [RG-ART-021]. En el cálculo de promedios del registro académico, NCR equivale a 1,0 y APR/REP se excluyen [RG-ART-024]."
        ),
        "condiciones": (
            "El Promedio Ponderado considera solo notas finales >= 4,0 y el Promedio Curricular todas las notas finales, ponderadas por créditos [RG-ART-024]."
        ),
        "fuente": "[RG-ART-021] [RG-ART-023] [RG-ART-024]",
    },
    {
        "id": "B2-T14",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿En qué casos se exige documentación adicional para convalidar una asignatura y qué documentos nunca permiten convalidar ni revalidar en Ingeniería?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-037", "RI-FI-ART-020", "RI-FI-ART-021", "RI-FI-ART-022"],
        "distractores": ["RG-ART-040", "RG-ART-041"],
        "pensar": (
            "[RG-ART-037] + [RI-FI-ART-021]: certificado completo de calificaciones y programas debidamente acreditados (salvo asignaturas "
            "aprobadas en la misma UdeC según [RG-ART-037]). Restricciones en Ingeniería: [RI-FI-ART-020]/[RI-FI-ART-021] prohíben "
            "revalidar o convalidar una asignatura previamente cursada y reprobada en el Plan de Estudio, y [RI-FI-ART-022] excluye a Primer Año Común."
        ),
        "respuesta": (
            "Para convalidar se debe acompañar certificado de calificaciones y programas debidamente acreditados de las asignaturas aprobadas, "
            "eximiéndose esos documentos si fueron aprobadas en la propia UdeC [RG-ART-037] [RI-FI-ART-021]."
        ),
        "condiciones": (
            "En Ingeniería rigen cuatro límites adicionales: (1) solo pueden pedirlo estudiantes de especialidad, no de Primer Año Común "
            "[RI-FI-ART-020] [RI-FI-ART-021] [RI-FI-ART-022]; (2) la nota mínima equivalente para convalidar es 4,5 [RI-FI-ART-021]; "
            "(3) no se puede convalidar ni revalidar una asignatura previamente cursada y reprobada en el Plan de Estudio [RI-FI-ART-020] [RI-FI-ART-021]; y (4) debe pedirse en las 4 primeras semanas [RI-FI-ART-022]."
        ),
        "fuente": "[RG-ART-037] [RI-FI-ART-020] [RI-FI-ART-021] [RI-FI-ART-022]",
    },
    {
        "id": "B2-T15",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué requisitos deben cumplirse al asignar y modificar la docencia y el Acta de Notas Finales de una asignatura?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-006", "RG-ART-027"],
        "distractores": ["RG-ART-012", "RG-ART-013", "RG-ART-005", "RG-ART-025"],
        "pensar": (
            "[RG-ART-006]: Director de Departamento asigna carga docente, Profesor Encargado y alterno eventual, comunicando al Vicedecano "
            "(y éste al Vicedecano/Jefe de Carrera solicitante) y registrando en SAC. [RG-ART-027]: Acta firmada por Comisión de Evaluación y "
            "Director de Departamento (o Vicedecano si no depende de Departamento) queda en Secretaría Académica; modificar el Acta exige "
            "visto bueno del Vicedecano que dicta la asignatura, acta de modificación firmada e ingreso al SAC antes del término del semestre siguiente."
        ),
        "respuesta": (
            "La carga docente y el Profesor Encargado son asignados por el Director de Departamento y registrados en el SAC [RG-ART-006]; "
            "el Acta de Notas impresa requiere firma de la Comisión de Evaluación y el Director de Departamento (o Vicedecano si corresponde), "
            "y cualquier modificación posterior exige visto bueno del Vicedecano de la Facultad que dicta la asignatura [RG-ART-027]."
        ),
        "condiciones": (
            "El Acta de Modificación también debe ser firmada por la Comisión de Evaluación y el Director de Departamento, e ingresada al SAC "
            "por Secretaría Académica a más tardar antes del término del semestre siguiente al calificado [RG-ART-027]."
        ),
        "fuente": "[RG-ART-006] [RG-ART-027]",
    },
    {
        "id": "B2-T16",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones y prioridades limitan la modificación de inscripción de asignaturas en Ingeniería?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-007", "RI-FI-ART-008", "RI-FI-ART-009"],
        "distractores": ["RG-ART-042", "RG-ART-043", "CAL-2026-S1-03"],
        "pensar": (
            "[RI-FI-ART-009]: debe hacerse en fechas del calendario; permite agregar o eliminar asignaturas, pero NO permite "
            "eliminar asignaturas de prioridades a) atrasadas ni b) obligatorias reprobadas anteriormente del [RI-FI-ART-007], ni "
            "bajar del mínimo de 8 créditos de [RI-FI-ART-008] (salvo excepciones del art. 8)."
        ),
        "respuesta": (
            "La modificación solo puede realizarse en las fechas del calendario anual de docencia y no permite eliminar asignaturas "
            "atrasadas ni asignaturas obligatorias reprobadas anteriormente, ni tampoco bajar del mínimo de ocho créditos [RI-FI-ART-007] [RI-FI-ART-008] [RI-FI-ART-009]."
        ),
        "condiciones": (
            "Las únicas excepciones al mínimo de 8 créditos son quienes estén terminando sus estudios (inscriben al menos las que les faltan) "
            "o quienes por falta de requisitos estén impedidos de alcanzarlo [RI-FI-ART-008]."
        ),
        "fuente": "[RI-FI-ART-007] [RI-FI-ART-008] [RI-FI-ART-009]",
    },
    {
        "id": "B2-T17",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué pasa con las situaciones administrativas pendientes cuando entra a regir una nueva versión del Reglamento General de Docencia de Pregrado?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-TRANS-001"],
        "distractores": ["RG-ART-060", "RG-TRANS-002", "RG-PREAMBULO", "RI-FI-ART-034", "RI-FI-ART-035"],
        "pensar": (
            "[RG-TRANS-001]: se resuelven aplicando las normas vigentes al momento de su formulación u ocurrencia; "
            "excepción: pueden resolverse con el nuevo reglamento cuando su aplicación mejore la condición del alumno."
        ),
        "respuesta": (
            "Las situaciones pendientes al entrar en vigencia el reglamento se resuelven aplicando las normas vigentes al momento de "
            "su formulación u ocurrencia [RG-TRANS-001]."
        ),
        "condiciones": (
            "Excepción: se resolverán conforme al nuevo reglamento siempre que su aplicación mejore la condición del alumno [RG-TRANS-001]."
        ),
        "fuente": "[RG-TRANS-001]",
    },
    {
        "id": "B2-T18",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones regulan la participación de colaboradores externos o estudiantes en la docencia de pregrado?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-002"],
        "distractores": ["RG-ART-001", "RG-ART-006", "RG-ART-012", "RG-ART-015", "RG-ART-052"],
        "pensar": (
            "[RG-ART-002]: la docencia de pregrado es impartida por académicos UdeC; además pueden participar expertos externos y "
            "colaborar alumnos de pregrado y postgrado UdeC, debidamente calificados, regulados por un reglamento especial. "
            "Destinatarios: poseedores de Licencia de Educación Media o equivalente que cumplan exigencias de admisión."
        ),
        "respuesta": (
            "Aunque la docencia es impartida por académicos UdeC, pueden participar expertos externos y colaborar alumnos de pregrado "
            "y postgrado de la misma Universidad, siempre que estén debidamente calificados [RG-ART-002]."
        ),
        "condiciones": (
            "Dicha participación y colaboración queda regulada por un reglamento especial [RG-ART-002]."
        ),
        "fuente": "[RG-ART-002]",
    },
    {
        "id": "B2-T19",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué exigencias debe cumplir un alumno para mantener su calidad de Alumno Regular según el Artículo 3° y qué límites la interrumpen transitoriamente?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-15", "RG-ART-003-DEF-19", "RG-ART-003-DEF-20"],
        "distractores": ["RG-ART-003-DEF-14", "RG-ART-003-DEF-21", "RG-ART-050"],
        "pensar": (
            "[RG-ART-003-DEF-15]: a) aceptado por admisión UdeC, b) inscrito asignaturas en el período, c) cumplir reglamentos "
            "de matrícula y Fondo Solidario de Crédito Universitario (o sistema que lo reemplace). "
            "[RG-ART-003-DEF-19] / [RG-ART-003-DEF-20]: pierde transitoriamente la condición al no inscribir asignaturas, suspender estudios o recibir sanción disciplinaria de suspensión."
        ),
        "respuesta": (
            "Debe cumplir tres requisitos copulativos: haber sido aceptado por un proceso de admisión reconocido, haber inscrito "
            "asignaturas en el período académico respectivo y cumplir los reglamentos de matrícula y del Fondo Solidario de Crédito "
            "Universitario (o equivalente) [RG-ART-003-DEF-15]."
        ),
        "condiciones": (
            "La condición se pierde transitoriamente si el alumno perteneciente a una carrera no inscribe asignaturas, suspende "
            "estudios [RG-ART-003-DEF-19] o es sancionado disciplinariamente con suspensión de estudios [RG-ART-003-DEF-20]."
        ),
        "fuente": "[RG-ART-003-DEF-15] [RG-ART-003-DEF-19] [RG-ART-003-DEF-20]",
    },
    {
        "id": "B2-T20",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones permiten cursar asignaturas de libre elección fuera de la propia carrera o incluso en otra universidad?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-09"],
        "distractores": ["RG-ART-003-DEF-10", "RG-ART-039", "RG-ART-046", "RG-ART-056", "RI-FI-ART-024"],
        "pensar": (
            "[RG-ART-003-DEF-09] bajo ASIGNATURAS DE LIBRE ELECCIÓN: las cursa por iniciativa propia sin ser obligatorias, electivas ni "
            "complementarias; puede cursarlas en otras carreras de la UdeC o en otras universidades siempre que se haya establecido algún convenio, "
            "quedando incorporadas a su currículum y constituyendo carga académica del período lectivo."
        ),
        "respuesta": (
            "Las asignaturas de libre elección pueden cursarse por iniciativa propia en otras carreras de la UdeC o en otras universidades, "
            "siempre que exista algún convenio establecido [RG-ART-003-DEF-09]."
        ),
        "condiciones": (
            "Una vez cursadas bajo esa condición, quedan incorporadas al currículum del estudiante y constituyen carga académica del período lectivo correspondiente [RG-ART-003-DEF-09]."
        ),
        "fuente": "[RG-ART-003-DEF-09]",
    },
    {
        "id": "B2-T21",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones regulan que las evaluaciones se apliquen por medios orales o escritos en Ingeniería y cuándo deben anunciarse?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-010", "RI-FI-ART-011"],
        "distractores": ["RG-ART-021", "RG-ART-025", "RI-FI-ART-012", "RI-FI-ART-013"],
        "pensar": (
            "[RI-FI-ART-010]: los test, certámenes y exámenes pueden ser orales o escritos; las evaluaciones son obligatorias y "
            "deben programarse y comunicarse con plazo no inferior a una semana, salvo certámenes y evaluación de recuperación "
            "cuyas fechas deben ir en el syllabus. [RI-FI-ART-011]: al menos 3 evaluaciones sumativas y nota mínima 4,0."
        ),
        "respuesta": (
            "En la Facultad de Ingeniería los test, certámenes y exámenes pueden ser orales o escritos, son obligatorios y deben "
            "comunicarse con al menos una semana de anticipación, debiendo figurar las fechas de certámenes y evaluación de recuperación en el syllabus [RI-FI-ART-010]."
        ),
        "condiciones": (
            "Cada asignatura debe contar al menos con tres evaluaciones sumativas y requiere nota final mínima de 4,0 más el cumplimiento de los requisitos del curso [RI-FI-ART-011]."
        ),
        "fuente": "[RI-FI-ART-010] [RI-FI-ART-011]",
    },
    {
        "id": "B2-T22",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones y pasos debe seguir un alumno para apelar cuando solicita suspender estudios o cuando es denegada su solicitud ante el Vicedecano?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-031", "RG-ART-035", "RI-FI-ART-025"],
        "distractores": ["RG-ART-033", "RI-FI-ART-027", "RG-ART-059"],
        "pensar": (
            "[RG-ART-031]: presentar solicitud y antecedentes fidedignos (p. ej. informe DISE) al Vicedecano hasta 4 semanas antes "
            "del término del período lectivo; Vicedecano resuelve antes que finalice el período; apelación al Decano dentro de 5 días, "
            "siendo su decisión definitiva. [RG-ART-035]/[RI-FI-ART-025]: adjuntar certificados DAFE y Bibliotecas."
        ),
        "respuesta": (
            "Debe presentar al Vicedecano la solicitud fundada con antecedentes oficiales (como informe de DISE) hasta cuatro semanas "
            "antes del fin del período lectivo; si el Vicedecano resuelve desfavorablemente, puede apelar al Decano dentro de cinco días, "
            "siendo su decisión definitiva [RG-ART-031]."
        ),
        "condiciones": (
            "Debe adjuntar certificados DAFE (sin deudas de aranceles/préstamos o garantizadas) y de Bibliotecas (sin material adeudado) "
            "[RG-ART-035] [RI-FI-ART-025]; la suspensión deja sin efecto la inscripción de asignaturas pero no libera al estudiante de obligaciones pendientes con la Universidad [RG-ART-031]."
        ),
        "fuente": "[RG-ART-031] [RG-ART-035] [RI-FI-ART-025]",
    },
    {
        "id": "B2-T23",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿En qué condiciones conserva una alumna o un alumno el mismo Plan de Estudio tras ausentarse o cambiar planes?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-033", "RG-ART-003-DEF-10"],
        "distractores": ["RG-ART-040", "RG-ART-044", "RI-FI-ART-028", "RG-ART-036"],
        "pensar": (
            "[RG-ART-003-DEF-10]: los alumnos quedan adscritos al plan vigente al ingresar; los planes nuevos rigen para quienes "
            "ingresan a primer año y los del plan antiguo conservan su plan salvo que soliciten por única vez cambiar al plan nuevo "
            "al inicio del año académico ante el Vicedecano. [RG-ART-033]: quien se reincorpora tras suspensión pasa al plan vigente, "
            "EXCEPTUANDO a los alumnos en intercambio, quienes se mantienen en su mismo plan."
        ),
        "respuesta": (
            "Por regla general el alumno permanece adscrito al plan vigente al ingresar salvo que pida por única vez cambiarse al plan "
            "nuevo [RG-ART-003-DEF-10]; si suspende estudios y luego se reincorpora pasa al plan vigente a la fecha de reincorporación, "
            "excepto tratándose de alumnos en intercambio, quienes conservan su mismo plan de estudio [RG-ART-033]."
        ),
        "condiciones": (
            "El cambio voluntario al plan nuevo debe solicitarse al Vicedecano durante la inscripción de asignaturas de inicio del año "
            "académico en que entra en vigencia, sin perjuicio de planes transitorios de ajuste [RG-ART-003-DEF-10]."
        ),
        "fuente": "[RG-ART-003-DEF-10] [RG-ART-033]",
    },
    {
        "id": "B2-T24",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué requisitos deben cumplirse para reconocer asignaturas de carácter cultural o deportivo dentro del currículum?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-046"],
        "distractores": ["RG-ART-003-DEF-09", "RG-ART-052", "RG-ART-056", "RG-ART-015", "RG-ART-002"],
        "pensar": (
            "[RG-ART-046]: actividades artísticas, culturales, deportivas, sociales o recreativas reconocidas como asignaturas "
            "complementarias si (1) se efectúan bajo tuición o patrocinio de organismos dependientes de la UdeC y (2) cuentan "
            "con un programa de actividades aprobado por la Dirección de Docencia y la respectiva unidad."
        ),
        "respuesta": (
            "Las actividades artísticas, culturales, deportivas, sociales o recreativas pueden reconocerse en el currículum como "
            "asignaturas complementarias cumpliendo requisitos institucionales específicos [RG-ART-046]."
        ),
        "condiciones": (
            "Se requiere que: (1) se desarrollen bajo tuición o patrocinio de organismos dependientes de la Universidad de Concepción, "
            "y (2) cuenten con un programa de actividades aprobado tanto por la Dirección de Docencia como por la unidad respectiva [RG-ART-046]."
        ),
        "fuente": "[RG-ART-046]",
    },
    {
        "id": "B2-T25",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué limitaciones o excepciones enfrenta un alumno de primer año frente a las causales de baja académica del Artículo 14 de Ingeniería y del Artículo 28 del Reglamento General?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-014", "RG-ART-028"],
        "distractores": ["RI-FI-ART-015", "RI-FI-ART-016", "RG-ART-030", "RG-ART-045"],
        "pensar": (
            "Tanto [RI-FI-ART-014] como [RG-ART-028]: (1) el promedio mínimo de créditos de Ingeniería aplica a partir del cuarto "
            "semestre (b) y el de 15 créditos al término del segundo semestre (a); (2) la causal de reprobar por segunda vez una "
            "asignatura obligatoria EXCEPTÚA a estudiantes que se encuentren en el primer año de permanencia en la carrera, así como "
            "cuando la asignatura haya sido aprobada en el PLEV del año académico correspondiente."
        ),
        "respuesta": (
            "Durante el primer año de permanencia en la carrera no se aplica la baja académica por reprobar una asignatura obligatoria "
            "por segunda vez; además, la exigencia mínima de 15 créditos acumulados rige recién al término del segundo semestre y la de "
            "promedio de 10 créditos semestrales aplica a partir del cuarto semestre [RI-FI-ART-014] [RG-ART-028]."
        ),
        "condiciones": (
            "En cualquier nivel, la causal de segunda reprobación obligatoria tampoco produce baja si la asignatura se aprueba en el PLEV "
            "del año académico correspondiente [RI-FI-ART-014] [RG-ART-028]."
        ),
        "fuente": "[RG-ART-028] [RI-FI-ART-014]",
    },
    {
        "id": "B2-T26",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones exige la Universidad para aprobar las asignaturas cuando el Profesor Encargado define la asistencia y qué ocurre ante una enfermedad o accidente justificado en evaluaciones?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-013", "RG-ART-026"],
        "distractores": ["RG-ART-020", "RG-ART-023", "RI-FI-ART-011", "RG-ART-059"],
        "pensar": (
            "[RI-FI-ART-013]: tope 80 % clases teóricas/prácticas y hasta 100 % en seminarios, laboratorios, talleres, salidas a terreno "
            "u otras similares. [RG-ART-026]: inasistencia justificada a evaluación se solicita al Profesor Encargado en máx 3 días hábiles "
            "con documentos justificativos; apelable ante Vicedecano; si no se presenta en plazo -> nota mínima o NCR."
        ),
        "respuesta": (
            "El Profesor Encargado puede exigir hasta un 80 % de asistencia mínima en clases teóricas y prácticas y hasta un 100 % en "
            "seminarios, laboratorios, talleres o salidas a terreno [RI-FI-ART-013]; ante inasistencia justificada a una evaluación, "
            "el alumno debe pedir regularización al Profesor Encargado dentro de 3 días hábiles posteriores presentando los documentos que la acrediten [RG-ART-026]."
        ),
        "condiciones": (
            "De lo resuelto por el Profesor Encargado se puede apelar al Vicedecano; quien no solicite dentro del plazo de 3 días hábiles "
            "recibirá la nota mínima o NCR según corresponda; la evaluación recuperativa se aplica de inmediato tras superar la causal o en otra modalidad/período distinto a la Evaluación de Recuperación [RG-ART-026]."
        ),
        "fuente": "[RG-ART-026] [RI-FI-ART-013]",
    },
    {
        "id": "B2-T27",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué características y requisitos formales distinguen a un 'Programa de Estudio' / 'Carrera' cuando se dicta simultáneamente en más de un campus de la Universidad de Concepción?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-01", "RG-ART-009", "RG-ART-008"],
        "distractores": ["RG-ART-014", "RG-ART-004", "RG-ART-040"],
        "pensar": (
            "[RG-ART-003-DEF-01]: puede dictarse en distintos campus bajo distintas estructuras administrativas, pero deben garantizar "
            "competencias de egreso similares y Planes de Estudios similares. [RG-ART-008]: habrá un Jefe de Carrera en cada campus. "
            "[RG-ART-009]: se constituye un Consejo de Carrera en cada campus y cada carrera, sin perjuicio de un Consejo a nivel de universidad."
        ),
        "respuesta": (
            "Una misma carrera dictada en más de un campus puede funcionar bajo estructuras administrativas diferentes, pero debe garantizar "
            "competencias de egreso y Planes de Estudios similares [RG-ART-003-DEF-01], contar con un Jefe de Carrera en cada campus [RG-ART-008] "
            "y constituir un Consejo de Carrera en cada campus sin perjuicio de un Consejo de Carrera a nivel de universidad [RG-ART-009]."
        ),
        "condiciones": (
            "Toda carrera tiene siempre asociado un Plan de Estudios y debe implementar mecanismos de seguimiento de egresados y vinculación "
            "con el medio definidos por su Facultad [RG-ART-003-DEF-01]."
        ),
        "fuente": "[RG-ART-003-DEF-01] [RG-ART-008] [RG-ART-009]",
    },
    {
        "id": "B2-T28",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones exige la Universidad cuando varias carreras dictan asignaturas con contenidos similares en un PLEV?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-045"],
        "distractores": ["RG-ART-037", "RG-ART-040", "RG-ART-043", "RG-ART-016", "RG-ART-006"],
        "pensar": (
            "[RG-ART-045] párrafo 2: distintas asignaturas con contenidos similares pero no idénticos dictadas para diversas carreras "
            "pueden reunirse en una sola en el PLEV, siempre que las Facultades y carreras involucradas lo acuerden en conjunto y establezcan las convalidaciones correspondientes."
        ),
        "respuesta": (
            "Las asignaturas de distintas carreras con contenidos similares pero no idénticos pueden agruparse en un único curso en el PLEV "
            "siempre que exista acuerdo conjunto previo y convalidaciones definidas [RG-ART-045]."
        ),
        "condiciones": (
            "Para ello las Facultades y carreras involucradas deben acordar la medida conjuntamente, establecer las convalidaciones que "
            "correspondan y alcanzar el número mínimo de alumnos inscritos fijado por la Facultad [RG-ART-045]."
        ),
        "fuente": "[RG-ART-045]",
    },
    {
        "id": "B2-T29",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones limitan el cálculo y el uso de la nota obtenida en la Evaluación Diagnóstica para acogerse a Inicio Adelantado?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-038"],
        "distractores": ["RG-ART-023", "RI-FI-ART-023", "RI-FI-ART-022", "RG-ART-041", "RI-FI-ART-003"],
        "pensar": (
            "[RG-ART-038] párrafo 3: Inicio Adelantado aplica solo a alumnos regulares de nuevo ingreso, respecto de asignaturas "
            "fundamentales, exige obtener un resultado superior a 5,7 (estrictamente > 5,7) en la Evaluación Diagnóstica asociada y "
            "luego rendir y aprobar una evaluación específica; la nota obtenida en esa evaluación específica será la nota final (de aprobarla); requiere además estar contemplado en el Reglamento Interno de la Facultad."
        ),
        "respuesta": (
            "Solo pueden acceder al Inicio Adelantado alumnos regulares de nuevo ingreso que obtengan un resultado superior a 5,7 en la "
            "Evaluación Diagnóstica de una asignatura fundamental, quedando habilitados para rendir una evaluación específica sin cursarla [RG-ART-038]."
        ),
        "condiciones": (
            "La nota obtenida en la evaluación específica pasa a ser la nota final en caso de aprobarla, y el reconocimiento de contenidos "
            "requiere estar establecido en el Reglamento Interno de Docencia de Pregrado de la Facultad correspondiente [RG-ART-038]."
        ),
        "fuente": "[RG-ART-038]",
    },
    {
        "id": "B2-T30",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones regulan la participación de las Unidades Académicas frente a las atribuciones de los Directores de Departamento cuando el Consejo de Carrera de Ingeniería solicita coordinación?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-010", "RG-ART-006"],
        "distractores": ["RI-FI-ART-032", "RG-ART-008", "RG-ART-009", "RG-ART-004"],
        "pensar": (
            "[RG-ART-010] párrafo final: para cumplir sus funciones, el Jefe de Carrera requiere coordinación con los Directores de "
            "Departamento que participan en la carrera a través del Decano, cautelando el Art. 57 inciso 1° de los Estatutos de la Corporación. "
            "[RG-ART-006]: el Director de Departamento asigna carga docente y Profesor Encargado y comunica a su Vicedecano, quien informa al Vicedecano y Jefe de Carrera solicitante."
        ),
        "respuesta": (
            "Cuando el Consejo de Carrera requiere coordinación con los Directores de Departamento que participan en la carrera, el Jefe de "
            "Carrera debe canalizarla a través del Decano cautelando el primer párrafo del Artículo 57 de los Estatutos [RG-ART-010]; la "
            "asignación concreta de carga docente y Profesores Encargados compete al Director de Departamento, comunicándola vía Vicedecano [RG-ART-006]."
        ),
        "condiciones": (
            "Dicha coordinación no sustituye las competencias de cada Departamento en la dictación de sus asignaturas ni la necesidad de registrar la carga docente en el SAC [RG-ART-006] [RG-ART-010]."
        ),
        "fuente": "[RG-ART-006] [RG-ART-010]",
    },
    {
        "id": "B2-T31",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué exigencias rigen la postulación desde el Ingreso Común a las carreras de Ingeniería Civil y qué ocurre con las asignaturas electivas o complementarias cursadas en Primer Año?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-005", "RI-FI-ART-006"],
        "distractores": ["RI-FI-ART-003", "RI-FI-ART-004", "RG-ART-024", "RI-FI-ART-022"],
        "pensar": (
            "[RI-FI-ART-005]: postulan al término del 2° semestre; prelación 1° por número de créditos aprobados, 2° a igual créditos "
            "por promedio curricular de asignaturas del Plan Común de Primer Año con dos decimales (aprobadas y reprobadas), considerando "
            "orden de preferencias y cupos disponibles; PARA EL PROCESO SOLO SE CONSIDERAN LAS ASIGNATURAS OBLIGATORIAS DE PRIMER AÑO. "
            "[RI-FI-ART-006]: se realiza al final del año académico con distribución porcentual de cupos por carrera fijada por la Facultad."
        ),
        "respuesta": (
            "La postulación ocurre al final del año académico (término del segundo semestre de permanencia), y para el proceso únicamente "
            "se consideran las asignaturas obligatorias de Primer Año, excluyendo asignaturas fuera de ese grupo [RI-FI-ART-005] [RI-FI-ART-006]."
        ),
        "condiciones": (
            "La selección sigue orden estricto: primero mayor cantidad de créditos aprobados y, en empate, mayor promedio curricular "
            "ponderado por créditos del Plan Común de Primer Año (con dos decimales, incluyendo aprobadas y reprobadas), sujeto al orden "
            "de preferencias y a la distribución porcentual de cupos definida por la Facultad [RI-FI-ART-005] [RI-FI-ART-006]."
        ),
        "fuente": "[RI-FI-ART-005] [RI-FI-ART-006]",
    },
    {
        "id": "B2-T32",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones diferencian las obligaciones de los alumnos que ingresan a primer año al inscribir asignaturas frente a los estudiantes de cursos superiores?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-042", "RI-FI-ART-007"],
        "distractores": ["RI-FI-ART-008", "RI-FI-ART-009", "RI-FI-ART-003", "RG-ART-003-DEF-13"],
        "pensar": (
            "[RG-ART-042]: para los alumnos que ingresan a una carrera, la inscripción de asignaturas forma parte del proceso de matrícula, "
            "mientras en general debe hacerse en las fechas del Calendario, cumplir prerrequisitos, haber respondido la Encuesta Docente "
            "del período anterior y respetar mínimos de créditos y prioridades de [RI-FI-ART-007]."
        ),
        "respuesta": (
            "Para los estudiantes que ingresan a una carrera, la inscripción de asignaturas forma parte del proceso de matrícula; en los "
            "demás períodos debe realizarse en las fechas indicadas en el Calendario de Docencia de Pregrado siguiendo el orden de prioridades correspondiente [RG-ART-042] [RI-FI-ART-007]."
        ),
        "condiciones": (
            "Para cursos posteriores se exige además haber contestado la Encuesta de Evaluación Docente del período anterior, cumplir "
            "prerrequisitos, respetar horarios sin tope en actividades obligatorias e inscribir el mínimo de créditos [RG-ART-042]."
        ),
        "fuente": "[RG-ART-042] [RI-FI-ART-007]",
    },
    {
        "id": "B2-T33",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué límite máximo establece el Reglamento General para las horas semanales de Trabajo Académico del plan de estudios y qué abarca exactamente ese concepto?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-017", "RG-ART-003-DEF-07"],
        "distractores": ["RG-ART-003-DEF-06", "RG-ART-003-DEF-08", "RI-FI-ART-008", "RG-ART-016"],
        "pensar": (
            "[RG-ART-017]: el plan de estudios no debería exceder las 54 horas semanales de Trabajo Académico. "
            "[RG-ART-003-DEF-07]: el Trabajo Académico suma las horas de docencia directa más las actividades indirectas o complementarias "
            "realizadas fuera del horario programado durante una semana, y un alumno a tiempo completo debe dedicar entre 45 y 54 horas semanales."
        ),
        "respuesta": (
            "El plan de estudios no debería exceder las 54 horas semanales de Trabajo Académico [RG-ART-017], mientras que un estudiante a "
            "tiempo completo debe dedicar entre 45 y 54 horas semanales durante el período lectivo [RG-ART-003-DEF-07]."
        ),
        "condiciones": (
            "El Trabajo Académico comprende tanto las horas de docencia directa como las horas dedicadas a actividades indirectas o "
            "complementarias realizadas fuera del horario programado cada semana [RG-ART-003-DEF-07] [RG-ART-017]."
        ),
        "fuente": "[RG-ART-003-DEF-07] [RG-ART-017]",
    },
    {
        "id": "B2-T34",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿En qué condiciones queda la salud o condición física incompatible con la carrera y qué pasos son necesarios si el estudiante posteriormente quiere volver?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-032", "RG-ART-033"],
        "distractores": ["RG-ART-059", "RG-ART-031", "RI-FI-ART-025", "RI-FI-ART-027"],
        "pensar": (
            "[RG-ART-032]: si presenta salud o condición física incompatible con la Carrera, se le suspende el derecho a continuar estudios; "
            "decide el Decano en resolución fundada previo informe DISE e informa a Vicerrector y UDARAE. [RG-ART-033]: para reincorporarse "
            "si la suspensión se fundó en razones de salud, debe acompañar informe DISE (u otro fidedigno) que demuestre que cesaron los impedimentos, "
            "resolviendo el Decano, siempre dentro del máximo de 3 años calendario."
        ),
        "respuesta": (
            "Ante salud o condición física incompatible, el Decano suspende el derecho a continuar estudios mediante resolución fundada "
            "previo informe de la Dirección de Servicios Estudiantiles [RG-ART-032]; para reincorporarse, el alumno debe demostrar mediante "
            "antecedentes oficiales (informe DISE u otros fidedignos) que cesaron los impedimentos, resolviendo también el Decano [RG-ART-033]."
        ),
        "condiciones": (
            "La resolución inicial se informa al Vicerrector y a UDARAE para registro en SAC [RG-ART-032]; toda suspensión dura máximo tres años "
            "calendario, pasados los cuales sin solicitar reincorporación se pierde la calidad de alumno de pregrado [RG-ART-033]."
        ),
        "fuente": "[RG-ART-032] [RG-ART-033]",
    },
    {
        "id": "B2-T35",
        "bloque": "condiciones_excepciones",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué requisitos y restricciones temporales aplican cuando se requiere cambiar una carrera por vía de cambio interno frente al ingreso a una carrera distinta?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-054", "RG-ART-055"],
        "distractores": ["RI-FI-ART-017", "RI-FI-ART-018", "RI-FI-ART-019", "RG-ART-044"],
        "pensar": (
            "[RG-ART-054] (cambio de carrera): ser alumno regular con derecho a continuar en origen, promedio mínimo de Facultad de destino "
            "(cuando es dentro de la misma Facultad, su Reglamento Interno puede fijar promedios o puntajes distintos); se debe ofrecer al "
            "menos 1 cupo por carrera en el primer semestre. [RG-ART-055] (ingreso a otra carrera): mismos requisitos y cupos anuales, sin regla especial de misma Facultad."
        ),
        "respuesta": (
            "Tanto el cambio como el ingreso a otra carrera exigen ser alumno regular, conservar el derecho a continuar estudios en la carrera "
            "de origen, alcanzar al menos el promedio mínimo del Reglamento Interno de la Facultad receptora y postular dentro del período fijado "
            "por la Dirección de Docencia en UDARAE, sujeto a cupos anuales [RG-ART-054] [RG-ART-055]."
        ),
        "condiciones": (
            "Para cambio de carrera, las Facultades deben ofrecer anualmente al menos un cupo para cada carrera en el primer semestre, y si "
            "el cambio ocurre dentro de la misma Facultad su reglamento puede establecer promedios o puntajes diferenciados; UDARAE solo "
            "recepciona solicitudes que cumplan todos los requisitos [RG-ART-054] [RG-ART-055]."
        ),
        "fuente": "[RG-ART-054] [RG-ART-055]",
    },

    # ---- VAL BLOQUE 2 (5 ejemplos con artículos / ángulos distintos de train) ----
    {
        "id": "B2-V01",
        "bloque": "condiciones_excepciones",
        "split": "val",
        "modo": "condicional",
        "pregunta": "¿Qué excepciones e información especial contempla el Reglamento General sobre cómo se asignan las asignaturas bajo un Programa de Bachillerato frente a una carrera de Licenciatura o Título?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-01", "RG-ART-003-DEF-02"],
        "distractores": ["RG-ART-003-DEF-03", "RG-ART-003-DEF-04", "RG-ART-003-DEF-10", "RG-ART-048"],
        "pensar": (
            "[RG-ART-003-DEF-01] define el Bachillerato como programa que logra formación universitaria básica durante cuatro semestres en "
            "disciplinas de un área del conocimiento (desarrollando organización del tiempo, comunicación oral/escrita y TIC). "
            "[RG-ART-003-DEF-02] señala que los estudios conducentes al grado de Bachiller permiten desarrollo inicial general e integrado "
            "e introducción en algunas disciplinas, mientras Licenciado/Título abarcan Ciclos Disciplinarios o Profesionales."
        ),
        "respuesta": (
            "El Bachillerato es un programa de formación universitaria básica de cuatro semestres orientado a un desarrollo inicial general "
            "e integrado del conocimiento e introducción disciplinar, mientras las carreras conducentes a Licenciatura o Título Profesional "
            "pueden estructurarse además con Ciclos Disciplinarios y Ciclos Profesionales según su perfil de egreso [RG-ART-003-DEF-01] [RG-ART-003-DEF-02]."
        ),
        "condiciones": (
            "Dos o más carreras pueden compartir un Ciclo Básico Común, y el Bachillerato debe desarrollar competencias en organización del "
            "tiempo, comunicación oral y escrita y uso de tecnologías de la información y comunicación en su área [RG-ART-003-DEF-01]."
        ),
        "fuente": "[RG-ART-003-DEF-01] [RG-ART-003-DEF-02]",
    },
    {
        "id": "B2-V02",
        "bloque": "condiciones_excepciones",
        "split": "val",
        "modo": "condicional",
        "pregunta": "¿Qué limitaciones rigen para que un alumno de una carrera de la Facultad sea elegido en el Consejo de Carrera de Ingeniería y cuánto tiempo puede permanecer allí sin ser reemplazado?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-032", "RG-ART-010"],
        "distractores": ["RI-FI-ART-033", "RG-ART-009", "RG-ART-011", "RG-ART-008"],
        "pensar": (
            "[RI-FI-ART-032]: los tres representantes estudiantiles son elegidos por el Centro de Alumnos de la carrera respectiva, "
            "tienen derecho a voz y voto, y duran un año en sus funciones (a diferencia de los docentes que duran dos años). "
            "[RG-ART-010]: si un representante estudiantil acumula dos ausencias consecutivas sin justificación, será reemplazado."
        ),
        "respuesta": (
            "Los tres representantes estudiantiles del Consejo de Carrera en Ingeniería son elegidos por el Centro de Alumnos de la carrera "
            "con derecho a voz y voto y duran un año en sus funciones [RI-FI-ART-032], pero pueden ser reemplazados anticipadamente si incurren "
            "en dos ausencias consecutivas sin justificación [RG-ART-010]."
        ),
        "condiciones": (
            "Por contraste, los integrantes académicos del Consejo en Ingeniería duran dos años (requiriendo contrato indefinido y al menos "
            "media jornada en el caso de los docentes adscritos del Departamento) y ante dos inasistencias injustificadas consecutivas reciben un llamado de atención escrito [RG-ART-010] [RI-FI-ART-032]."
        ),
        "fuente": "[RG-ART-010] [RI-FI-ART-032]",
    },
    {
        "id": "B2-V03",
        "bloque": "condiciones_excepciones",
        "split": "val",
        "modo": "condicional",
        "pregunta": "¿Qué requisitos de difusión debe cumplir el Reglamento Interno frente a los alumnos matriculados y qué jerarquía tienen las normas del Reglamento General?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-058", "RG-ART-060"],
        "distractores": ["RG-ART-001", "RG-TRANS-002", "RI-FI-ART-002", "RI-FI-ART-034"],
        "pensar": (
            "[RG-ART-058]: tanto el Reglamento General como los Reglamentos Internos de cada Facultad son de dominio público por un "
            "sistema actualizado de información y se consideran conocidos por el alumno al formalizar su matrícula. "
            "[RG-ART-060]: las normas del Reglamento General prevalecen sobre cualesquiera otras inconciliables, sin importar de dónde provengan."
        ),
        "respuesta": (
            "Tanto el Reglamento General como los Reglamentos Internos de Facultad deben estar disponibles como dominio público en un sistema "
            "actualizado de información y se entienden conocidos por el estudiante al formalizar su matrícula [RG-ART-058]; además, el Reglamento "
            "General prevalece sobre toda otra norma que no se concilie con él, sin importar su origen [RG-ART-060]."
        ),
        "condiciones": (
            "El conocimiento presunto opera al momento de formalizar la matrícula y la supremacía del Reglamento General rige sin excepción frente a cualquier disposición contradictoria [RG-ART-058] [RG-ART-060]."
        ),
        "fuente": "[RG-ART-058] [RG-ART-060]",
    },
    {
        "id": "B2-V04",
        "bloque": "condiciones_excepciones",
        "split": "val",
        "modo": "condicional",
        "pregunta": "¿Qué exigencias específicas deben cumplir los alumnos autorizados a matricularse para ser efectivamente Alumnos de Pregrado y cuál es el rol de la Unidad de Admisión y Registro Académico (UDARAE) en cambios de carrera?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-14", "RG-ART-003-DEF-21", "RG-ART-054"],
        "distractores": ["RG-ART-003-DEF-15", "RG-ART-003-DEF-05", "RG-ART-055"],
        "pensar": (
            "[RG-ART-003-DEF-21]: Alumno autorizado a matricularse cumplió exigencias académicas para matricularse en el período siguiente. "
            "[RG-ART-003-DEF-14]: Alumno de Pregrado fue aceptado por admisión UdeC y mantiene derecho a calidad de regular o egresado. "
            "[RG-ART-054]: en cambios de carrera, UDARAE recepciona únicamente solicitudes que cumplan todos los requisitos y registra en SAC las sancionadas por el Rector."
        ),
        "respuesta": (
            "Un Alumno Autorizado a Matricularse es quien ha cumplido las exigencias académicas para matricularse en el período siguiente [RG-ART-003-DEF-21], "
            "siendo Alumno de Pregrado quien fue aceptado mediante un proceso de admisión reconocido y conserva derecho a ser alumno regular o egresado [RG-ART-003-DEF-14]. "
            "En cambios de carrera, UDARAE recepciona solo solicitudes completas y registra en el SAC la resolución sancionada por el Rector [RG-ART-054]."
        ),
        "condiciones": (
            "Para convertirse en alumno regular efectivo se requiere además inscribir asignaturas y cumplir las normas de matrícula vigentes [RG-ART-003-DEF-14] [RG-ART-003-DEF-21]; "
            "en cambios de carrera UDARAE rechaza solicitudes que no reúnan todos los requisitos [RG-ART-054]."
        ),
        "fuente": "[RG-ART-003-DEF-14] [RG-ART-003-DEF-21] [RG-ART-054]",
    },
    {
        "id": "B2-V05",
        "bloque": "condiciones_excepciones",
        "split": "val",
        "modo": "condicional",
        "pregunta": "¿Qué obligación de informe al término del semestre recae en el Profesor Encargado de una asignatura y cómo se distingue el modo de trabajo presencial del semipresencial?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-012", "RG-ART-003-DEF-09"],
        "distractores": ["RG-ART-006", "RG-ART-027", "RG-ART-003-DEF-11", "RG-ART-019"],
        "pensar": (
            "[RG-ART-012]: el Profesor Encargado coordina a los docentes participantes, vela por objetivos del programa y plazos, "
            "entrega el Acta de Notas Finales e informa por escrito al Director de Departamento al final del período lectivo sobre el desarrollo de la asignatura. "
            "[RG-ART-003-DEF-09]: presencial es conducido principalmente por el o los docentes con presencia física del alumno; semipresencial otorga principalmente espacios para trabajo autónomo orientado por docentes."
        ),
        "respuesta": (
            "Al final del período lectivo, el Profesor Encargado debe entregar el Acta de Notas Finales e informar por escrito al Director "
            "de Departamento sobre el desarrollo de la asignatura [RG-ART-012]. Respecto de las modalidades, la asignatura presencial es "
            "conducida principalmente por los docentes con presencia física del estudiante, mientras que la semipresencial otorga principalmente "
            "espacios para el trabajo autónomo orientado por los docentes [RG-ART-003-DEF-09]."
        ),
        "condiciones": (
            "El Profesor Encargado también debe coordinar al equipo docente y velar por el cumplimiento de normas y plazos reglamentarios [RG-ART-012]."
        ),
        "fuente": "[RG-ART-003-DEF-09] [RG-ART-012]",
    },
]
