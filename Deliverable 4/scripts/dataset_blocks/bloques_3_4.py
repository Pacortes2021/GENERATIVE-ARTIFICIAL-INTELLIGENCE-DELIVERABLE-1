"""Bloque 3 (polares_y_lectura: 30 train / 5 val) y Bloque 4 (calculos_y_orden: 30 train / 5 val)."""

from __future__ import annotations

from typing import Any

BLOQUE_3_POLARES_Y_LECTURA: list[dict[str, Any]] = [
    # ---- TRAIN (30 ejemplos) ----
    {
        "id": "B3-T01",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si un estudiante inscribe una asignatura en el PLEV y luego decide retirarse dentro de las primeras tres semanas, ¿puede hacer abandono sin especificación de motivos?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-043"],
        "distractores": ["RG-ART-045", "RG-ART-016", "RI-FI-ART-009", "CAL-2026-S1-03", "RG-ART-042"],
        "pensar": (
            "Pregunta polar con excepción expresa en [RG-ART-043]. Aunque la regla general permite abandonar asignaturas "
            "semestrales o anuales en 4 semanas, el inciso final de [RG-ART-043] lo prohíbe expresamente para asignaturas "
            "inscritas en el PLEV. Debo responder directamente 'No' sin contradecirme."
        ),
        "respuesta": (
            "No, el estudiante no puede hacer abandono de una asignatura inscrita en el PLEV [RG-ART-043]."
        ),
        "condiciones": (
            "La facultad de abandono dentro de cuatro semanas desde el inicio de clases (por una sola vez y sin quedar bajo "
            "el mínimo de créditos) rige para asignaturas semestrales o anuales (o el plazo que fije la Facultad si duran menos "
            "de un semestre), pero excluye expresamente a las asignaturas inscritas en el PLEV [RG-ART-043]."
        ),
        "fuente": "[RG-ART-043]",
    },
    {
        "id": "B3-T02",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si un alumno habilitado para inscribir asignaturas no inscribe ninguna en el período lectivo, ¿pierde automáticamente la calidad de alumno y el derecho a continuar estudios?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-029"],
        "distractores": ["RG-ART-030", "RG-ART-050", "RG-ART-042", "RG-ART-003-DEF-19", "RI-FI-ART-008"],
        "pensar": (
            "Pregunta polar estilo H14 sobre [RG-ART-029]. NO pierde automáticamente siempre, porque hay una excepción explícita: "
            "'a menos que en el periodo lectivo anterior hayan inscrito una u más asignaturas anuales'. Debo responder 'No "
            "necesariamente' / 'No automáticamente' y explicar regla y excepción sin contradicción."
        ),
        "respuesta": (
            "No automáticamente: aunque por regla general quien estando habilitado no inscribe asignaturas en el período pierde "
            "el derecho a continuar estudios y la calidad de alumno de pregrado, no los pierde si en el período lectivo anterior "
            "inscribió una o más asignaturas anuales [RG-ART-029]."
        ),
        "condiciones": (
            "Solo cuando no haya inscrito una o más asignaturas anuales en el período lectivo anterior se configura la Baja por no "
            "Inscripción (pérdida de estudios y calidad de alumno) [RG-ART-029]."
        ),
        "fuente": "[RG-ART-029]",
    },
    {
        "id": "B3-T03",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "Me dijeron que el plazo máximo de tres años calendario mencionado en el reglamento corresponde al tiempo que dura la reincorporación una vez aprobada. ¿Es cierto?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-033", "RI-FI-ART-027"],
        "distractores": ["RG-ART-031", "RG-ART-035", "RG-ART-034", "RI-FI-ART-028"],
        "pensar": (
            "Falsa atribución sujeto/plazo (como P26). En [RG-ART-033], los tres años calendario son la duración máxima de la "
            "suspensión de estudios: 'En todo caso la suspensión de estudios podrá extenderse por un período máximo de tres años "
            "calendario'. Si no pide reincorporación dentro de ese plazo, pierde la calidad de alumno de pregrado."
        ),
        "respuesta": (
            "No es cierto: el límite máximo de tres años calendario corresponde a la extensión de la suspensión de estudios, "
            "no a la duración de la reincorporación [RG-ART-033]."
        ),
        "condiciones": (
            "La reincorporación debe solicitarse al Vicedecano (o al Decano con antecedentes oficiales si la suspensión fue por salud); "
            "si el estudiante no pide su reincorporación dentro de ese plazo máximo de tres años calendario, pierde la calidad de alumno "
            "de pregrado de la Universidad [RG-ART-033] [RI-FI-ART-027]."
        ),
        "fuente": "[RG-ART-033] [RI-FI-ART-027]",
    },
    {
        "id": "B3-T04",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si un estudiante reprueba una asignatura durante el Período Lectivo Extraordinario de Verano (PLEV), ¿cae en causal de baja o pierde sus becas?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-045"],
        "distractores": ["RG-ART-028", "RI-FI-ART-014", "RG-ART-043", "RG-ART-016", "RG-ART-023"],
        "pensar": (
            "[RG-ART-045]: 'La reprobación de una asignatura en el PLEV no afectará la situación curricular del alumno, ni se verán "
            "afectados sus antecedentes para el otorgamiento de beneficios tales como becas y/o préstamos. Sin embargo quedará registrado "
            "en su hoja curricular'."
        ),
        "respuesta": (
            "No, reprobar una asignatura en el PLEV no afecta la situación curricular del estudiante ni sus antecedentes para acceder "
            "a beneficios como becas o préstamos [RG-ART-045]."
        ),
        "condiciones": (
            "Sin perjuicio de ello, la reprobación queda registrada en su hoja curricular [RG-ART-045]."
        ),
        "fuente": "[RG-ART-045]",
    },
    {
        "id": "B3-T05",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si un alumno ya se inscribió en un taller o laboratorio semestral y obtiene mala nota final, ¿tiene siempre derecho a rendir Evaluación de Recuperación en esa actividad?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-022"],
        "distractores": ["RI-FI-ART-012", "CAL-2026-S1-06", "CAL-2026-S2-05", "RG-ART-023", "RI-FI-ART-013"],
        "pensar": (
            "[RG-ART-022]: aunque en general existe derecho a Evaluación de Recuperación, 'no serán objeto de una Evaluación de "
            "Recuperación las actividades académicas que por sus características requieran de un tiempo prolongado para su ejecución, "
            "tales como: laboratorios, talleres, proyectos, memorias, seminarios, actividades clínicas, etc.'."
        ),
        "respuesta": (
            "No, los laboratorios y talleres están excluidos de la Evaluación de Recuperación [RG-ART-022]."
        ),
        "condiciones": (
            "La exclusión alcanza a todas las actividades académicas que por sus características exigen tiempo prolongado de ejecución, "
            "incluyendo laboratorios, talleres, proyectos, memorias, seminarios y actividades clínicas [RG-ART-022]."
        ),
        "fuente": "[RG-ART-022]",
    },
    {
        "id": "B3-T06",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "Como las asignaturas revalidadas e inscritas en intercambio se validan en el SAC, ¿ambas cuentan por igual como carga académica del semestre del alumno?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-039", "RG-ART-041", "RI-FI-ART-024"],
        "distractores": ["RG-ART-037", "RG-ART-040", "RI-FI-ART-020"],
        "pensar": (
            "Premisa falsa sobre equivalencia entre VAL y REV. [RG-ART-039] y [RI-FI-ART-024]: las asignaturas validadas de intercambio "
            "SÍ se reconocen como carga académica en el semestre cursado. [RG-ART-041]: las asignaturas convalidadas (CON), revalidadas (REV), "
            "homologadas (HOM) o reconocidas (REC) NO se consideran carga académica del semestre."
        ),
        "respuesta": (
            "No, no cuentan por igual: las asignaturas validadas por intercambio (VAL) sí son reconocidas como carga académica del semestre "
            "en que se cursaron [RG-ART-039] [RI-FI-ART-024], mientras que las asignaturas revalidadas (REV) no se consideran carga académica del semestre [RG-ART-041]."
        ),
        "condiciones": (
            "La misma exclusión de carga académica semestral aplica a asignaturas convalidadas (CON), homologadas (HOM) y reconocidas (REC), "
            "aunque todas se registran en el SAC con su Nota Final y sigla [RG-ART-041]."
        ),
        "fuente": "[RG-ART-039] [RG-ART-041] [RI-FI-ART-024]",
    },
    {
        "id": "B3-T07",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Puede un alumno solicitar por su propia cuenta cambiar el código de una asignatura aprobada en un plan antiguo usando 'revalidación' y elegir libremente qué asignaturas homologar?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-040", "RG-ART-037"],
        "distractores": ["RI-FI-ART-020", "RI-FI-ART-028", "RG-ART-003-DEF-10", "RG-ART-041"],
        "pensar": (
            "[RG-ART-040]: asignaturas de una versión anterior del plan de la misma carrera o de otra sede que cambian de código "
            "se tramitan mediante homologación, no revalidación ([RG-ART-037] es para otra carrera de la UdeC), y la tabla de "
            "homologables la establece el Vicedecano de la carrera con visto bueno del Vicedecano que dicta y registro UDARAE en SAC."
        ),
        "respuesta": (
            "No mediante revalidación ni a elección discrecional del estudiante: las asignaturas aprobadas en una versión anterior del "
            "plan de estudio de la misma carrera (o en otra sede con distinto código) se traspasan mediante homologación [RG-ART-040], "
            "según la tabla establecida por los Vicedecanos respectivos y registrada en el SAC por UDARAE [RG-ART-040]."
        ),
        "condiciones": (
            "La revalidación corresponde a una misma asignatura aprobada en otro plan de estudio de otra carrera de la Universidad [RG-ART-037]; "
            "la tabla de homologación exige visto bueno del Vicedecano de la Facultad que dicta la asignatura [RG-ART-040]."
        ),
        "fuente": "[RG-ART-037] [RG-ART-040]",
    },
    {
        "id": "B3-T08",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "El reglamento establece que para la apelación de una nota ante la Comisión ad hoc el estudiante tiene diez días hábiles y la comisión cinco días corridos para resolver. ¿Es correcto?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-025"],
        "distractores": ["RG-ART-026", "RG-ART-013", "RG-ART-027", "RI-FI-ART-010", "RI-FI-ART-011"],
        "pensar": (
            "Están invertidos los plazos de [RG-ART-025]. Profesor informa notas/pautas en máx 10 días hábiles; alumno pide revisión "
            "con profesor en 5 días hábiles; si persiste desacuerdo solicita por escrito al Vicedecano en máx 5 días hábiles; y la "
            "Comisión ad hoc resuelve en 10 días corridos."
        ),
        "respuesta": (
            "No es correcto, los plazos están invertidos: el estudiante dispone de un máximo de cinco días hábiles (desde la revisión con "
            "el profesor) para solicitar la nueva revisión al Vicedecano, y es la Comisión ad hoc la que debe resolver en un plazo de diez "
            "días corridos desde presentada la reclamación [RG-ART-025]."
        ),
        "condiciones": (
            "Previamente el profesor tiene hasta 10 días hábiles para entregar notas y pautas y el alumno 5 días hábiles para revisar ante él "
            "(plazos ampliables por el Vicedecano por razones justificadas); la decisión de la Comisión ad hoc es inapelable [RG-ART-025]."
        ),
        "fuente": "[RG-ART-025]",
    },
    {
        "id": "B3-T09",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si un alumno libre que ya posee título profesional aprueba todas las asignaturas de un plan de estudio cursándolas en esa calidad, ¿puede pedir el título profesional correspondiente?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-18"],
        "distractores": ["RG-ART-053", "RG-ART-047", "RG-ART-003-DEF-14", "RG-ART-003-DEF-04", "RG-ART-003-DEF-15"],
        "pensar": (
            "[RG-ART-003-DEF-18] lo prohíbe explícitamente: los alumnos libres no tienen calidad de alumno de pregrado, no quedan "
            "adscritos a una carrera de pregrado y no pueden optar a la obtención de un grado académico o título profesional por las asignaturas cursadas."
        ),
        "respuesta": (
            "No, un alumno libre no puede optar a la obtención de un grado académico ni de un título profesional por las asignaturas "
            "cursadas bajo esa condición [RG-ART-003-DEF-18]."
        ),
        "condiciones": (
            "No adquiere calidad de alumno de pregrado ni queda adscrito a carrera alguna, aunque sí puede solicitar certificación de las "
            "asignaturas aprobadas [RG-ART-003-DEF-18]."
        ),
        "fuente": "[RG-ART-003-DEF-18]",
    },
    {
        "id": "B3-T10",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si un estudiante reprueba por segunda vez una asignatura obligatoria durante su tercer semestre, ¿cae invariablemente en Baja Académica sin ninguna salvedad?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-014", "RG-ART-028"],
        "distractores": ["RG-ART-045", "RG-ART-030", "RI-FI-ART-016", "RG-ART-016"],
        "pensar": (
            "Misma lógica polar sin contradicción: 'No invariablemente' porque aunque ya no está en el primer año de permanencia, existe "
            "la segunda excepción de [RI-FI-ART-014] c) y [RG-ART-028] b): que la asignatura haya sido aprobada en el PLEV del año académico correspondiente."
        ),
        "respuesta": (
            "No invariablemente: si bien al cursar su tercer semestre ya no opera la excepción de primer año, el estudiante no queda en "
            "Baja Académica si aprueba esa asignatura obligatoria en el PLEV del año académico correspondiente [RG-ART-028] [RI-FI-ART-014]."
        ),
        "condiciones": (
            "Las dos salvedades a la segunda reprobación de asignatura obligatoria son: aprobarla en el PLEV de ese año académico o estar "
            "en el primer año de permanencia en la carrera [RG-ART-028] [RI-FI-ART-014]."
        ),
        "fuente": "[RG-ART-028] [RI-FI-ART-014]",
    },
    {
        "id": "B3-T11",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "Tengo entendido que cualquier estudiante con un promedio ponderado igual o superior a 5,7 en Ingeniería puede acogerse directamente a Inicio Adelantado en todas sus asignaturas de primer año sin dar evaluación extra. ¿Es así?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-038"],
        "distractores": ["RI-FI-ART-023", "RI-FI-ART-019", "RG-ART-048", "RI-FI-ART-022", "RG-ART-024"],
        "pensar": (
            "Tres errores en la premisa contra [RG-ART-038]: (1) el 5,7 (> 5,7, es decir estrictamente superior a 5,7) no es promedio "
            "ponderado sino el resultado en la Evaluación Diagnóstica asociada a una asignatura fundamental; (2) aplica solo a alumnos "
            "regulares de nuevo ingreso en asignaturas fundamentales contempladas en el Reglamento Interno; y (3) deben rendir y aprobar una evaluación específica."
        ),
        "respuesta": (
            "No es así: el requisito no es un promedio ponderado sino obtener un resultado estrictamente superior a 5,7 en la Evaluación "
            "Diagnóstica asociada a una asignatura fundamental (para alumnos regulares de nuevo ingreso), y además deben rendir y aprobar "
            "una evaluación específica para eximirse de cursarla [RG-ART-038]."
        ),
        "condiciones": (
            "Requiere estar previsto en el Reglamento Interno de la Facultad; si aprueban la evaluación específica, la calificación obtenida "
            "en ella queda como nota final de la asignatura [RG-ART-038]."
        ),
        "fuente": "[RG-ART-038]",
    },
    {
        "id": "B3-T12",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Puede un representante estudiantil o académico del Consejo de Carrera faltar dos veces seguidas sin excusa y seguir conservando su puesto sin consecuencias?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-010"],
        "distractores": ["RG-ART-009", "RI-FI-ART-032", "RG-ART-052", "RG-ART-011", "RG-ART-008"],
        "pensar": (
            "[RG-ART-010]: 'Si un representante estudiantil tiene dos ausencias consecutivas sin justificación será reemplazado y si "
            "se trata de un académico recibirá un llamado de atención por escrito'. No sigue sin consecuencias, pero las consecuencias difieren según estamento."
        ),
        "respuesta": (
            "No: dos ausencias consecutivas sin justificación acarrea consecuencias distintas según el estamento: un representante "
            "estudiantil será reemplazado en su cargo, mientras que un académico recibirá un llamado de atención por escrito [RG-ART-010]."
        ),
        "condiciones": (
            "Debe llevarse registro de asistencia en cada sesión del Consejo de Carrera [RG-ART-010]."
        ),
        "fuente": "[RG-ART-010]",
    },
    {
        "id": "B3-T13",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "Como la Encuesta de Evaluación Docente se aplica a todo el cuerpo docente en cada período lectivo, ¿deben ser evaluados incluso los profesores que solo cubrieron un reemplazo?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-007"],
        "distractores": ["RG-ART-042", "RG-ART-006", "RG-ART-012", "RG-ART-010", "RG-ART-019"],
        "pensar": (
            "[RG-ART-007]: 'Se exceptuará de la aplicación de la encuesta a aquellos profesores que hayan impartido docencia en la "
            "asignatura por reemplazos u otras circunstancias'."
        ),
        "respuesta": (
            "No, el reglamento exceptúa expresamente de la Encuesta de Evaluación Docente a los profesores que impartieron docencia por "
            "reemplazos u otras circunstancias [RG-ART-007]."
        ),
        "condiciones": (
            "Para los demás profesores y asignaturas dictadas la aplicación es obligatoria en cada período lectivo en línea vía Plataforma Encuesta Docente [RG-ART-007]."
        ),
        "fuente": "[RG-ART-007]",
    },
    {
        "id": "B3-T14",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si a un estudiante le faltan solo 6 créditos para completar su carrera, ¿está obligado a inscribir otras asignaturas hasta completar el mínimo de 8 créditos de Ingeniería?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-008", "RG-ART-042"],
        "distractores": ["RI-FI-ART-009", "RI-FI-ART-007", "RG-ART-043", "RG-ART-029"],
        "pensar": (
            "[RI-FI-ART-008] y [RG-ART-042] contemplan expresamente la excepción para quienes están terminando sus estudios: inscribirán "
            "al menos / solo las asignaturas que les falte cursar."
        ),
        "respuesta": (
            "No, no está obligado a completar 8 créditos: quienes están terminando sus estudios están exceptuados del mínimo general e "
            "inscriben únicamente (al menos) las asignaturas que les falten cursar [RG-ART-042] [RI-FI-ART-008]."
        ),
        "condiciones": (
            "La otra excepción al mínimo ocurre cuando por falta de requisitos u oferta inferior a 8 créditos derivada de la situación "
            "curricular personal el alumno se ve impedido de alcanzarlo, con autorización del Vicedecano en el marco del Reglamento General [RG-ART-042] [RI-FI-ART-008]."
        ),
        "fuente": "[RG-ART-042] [RI-FI-ART-008]",
    },
    {
        "id": "B3-T15",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "El Reglamento General fija la aprobación de la renuncia ante el Decano y señala que el alumno puede pedir revocarla dentro de cinco días hábiles si se arrepiente. ¿Es verdadero?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-034", "RI-FI-ART-026"],
        "distractores": ["RG-ART-035", "RG-ART-031", "RG-ART-030", "RI-FI-ART-025"],
        "pensar": (
            "Dos errores en la premisa contra [RG-ART-034] y [RI-FI-ART-026]: (1) se presenta ante el Vicedecano (quien remite a Dirección "
            "de Docencia), no ante el Decano; (2) es irrevocable e impide reincorporarse, no existe revocación en 5 días."
        ),
        "respuesta": (
            "Es falso en ambos puntos: la renuncia escrita se presenta ante el Vicedecano (quien la remite a la Dirección de Docencia para su "
            "registro), no ante el Decano, y es irrevocable, impidiendo solicitar reincorporación a la carrera [RG-ART-034] [RI-FI-ART-026]."
        ),
        "condiciones": (
            "Además exige presentar certificados de DAFE y de Bibliotecas, y no libera al alumno de obligaciones pendientes con la Universidad [RG-ART-034] [RI-FI-ART-026]."
        ),
        "fuente": "[RG-ART-034] [RI-FI-ART-026]",
    },
    {
        "id": "B3-T16",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si la Facultad de Ingeniería solicita al Decano resolver una contradicción entre su Reglamento Interno y el Reglamento General, ¿prevalece el Reglamento Interno por ser norma específica de la Facultad?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-034", "RG-ART-060"],
        "distractores": ["RI-FI-ART-002", "RI-FI-ART-035", "RG-ART-001", "RG-TRANS-002"],
        "pensar": (
            "Justo al revés: tanto [RI-FI-ART-034] como [RG-ART-060] señalan que ante inconciliabilidad prevalecen SIEMPRE el Reglamento "
            "General de Docencia de Pregrado (y las Normas de Ingreso según RI-FI art. 34), sin importar de dónde provenga la otra norma."
        ),
        "respuesta": (
            "No, prevalecen siempre el Reglamento General de Docencia de Pregrado y las Normas de Ingreso a las Carreras de Pregrado de "
            "la Universidad sobre el Reglamento Interno de Ingeniería [RG-ART-060] [RI-FI-ART-034]."
        ),
        "condiciones": (
            "La supremacía del Reglamento General rige sobre cualesquiera otras disposiciones que no se concilien con éste, sin importar de dónde provengan [RG-ART-060]."
        ),
        "fuente": "[RG-ART-060] [RI-FI-ART-034]",
    },
    {
        "id": "B3-T17",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "En Ingeniería, como el estudiante reprobó hace dos semestres una asignatura obligatoria en su plan, ahora aprobó exactamente esa asignatura en otra carrera de la UdeC y pide revalidarla en su especialidad. ¿Puede hacerlo?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-020"],
        "distractores": ["RI-FI-ART-021", "RI-FI-ART-022", "RG-ART-037", "RI-FI-ART-014", "RG-ART-041"],
        "pensar": (
            "[RI-FI-ART-020] lo prohíbe expresamente: 'No se podrá revalidar una asignatura que haya sido previamente cursada y reprobada en el Plan de Estudio'."
        ),
        "respuesta": (
            "No, no puede hacerlo: el Reglamento Interno de Ingeniería prohíbe revalidar una asignatura que haya sido previamente cursada "
            "y reprobada dentro del Plan de Estudio [RI-FI-ART-020]."
        ),
        "condiciones": (
            "La revalidación de asignaturas de igual código aprobadas en otra carrera UdeC solo procede para estudiantes de especialidad "
            "respecto de asignaturas que no hayan cursado y reprobado previamente en su plan [RI-FI-ART-020]."
        ),
        "fuente": "[RI-FI-ART-020]",
    },
    {
        "id": "B3-T18",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Cuando un alumno pide continuar estudios tras caer por primera vez en Baja Académica, ¿debe dirigirse directamente al Decano de la Facultad?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-030", "RI-FI-ART-016"],
        "distractores": ["RI-FI-ART-033", "RI-FI-ART-035", "RG-ART-004", "RG-ART-028"],
        "pensar": (
            "No ante el Decano en primera solicitud: según [RG-ART-030] y [RI-FI-ART-016], la primera solicitud de continuación de estudios "
            "por Baja Académica se presenta ante el Comité de Docencia y Asuntos Estudiantiles (1ª instancia), no ante el Decano (que "
            "resuelve en 3ª oportunidad o por apelación de lo resuelto por el Vicedecano)."
        ),
        "respuesta": (
            "No en primera solicitud: la primera solicitud de continuación de estudios debe presentarse ante el Comité de Docencia y Asuntos "
            "Estudiantiles respectivo (primera instancia), no directamente ante el Decano [RG-ART-030] [RI-FI-ART-016]."
        ),
        "condiciones": (
            "El Decano resuelve en última instancia dentro de la Facultad ante apelaciones de lo resuelto por el Vicedecano, o como autoridad "
            "directa recién en la tercera y última oportunidad ordinaria (con recurso excepcional por gracia al Vicerrector); todas dentro de un año [RG-ART-030] [RI-FI-ART-016]."
        ),
        "fuente": "[RG-ART-030] [RI-FI-ART-016]",
    },
    {
        "id": "B3-T19",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Tiene un estudiante en Baja por no Inscripción las mismas tres oportunidades ante Comité, Vicedecano y Decano que un estudiante en Baja Académica?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-030"],
        "distractores": ["RG-ART-029", "RG-ART-028", "RI-FI-ART-016", "RI-FI-ART-014", "RG-ART-033"],
        "pensar": (
            "Diferencia clave dentro de [RG-ART-030]: párrafo 1 (Baja por no Inscripción) -> solicitud dentro de máx 1 año al Comité de "
            "Docencia y Asuntos Estudiantiles, con recurso al Vicedecano dentro del 5° día hábil; NO menciona las tres oportunidades ni "
            "al Vicerrector por gracia, que están en el párrafo 2 exclusivamente para 'los alumnos en situación de Baja Académica'."
        ),
        "respuesta": (
            "No en los mismos términos: el procedimiento de tres oportunidades (Comité, Vicedecano, Decano y recurso excepcional al "
            "Vicerrector) está establecido específicamente para la Baja Académica, mientras que en Baja por no Inscripción el reglamento "
            "contempla solicitar continuación dentro de un año al Comité de Docencia y Asuntos Estudiantiles, con recurso al Vicedecano dentro del quinto día hábil [RG-ART-030]."
        ),
        "condiciones": (
            "En Baja por no Inscripción la solicitud también está sujeta al plazo máximo de un año [RG-ART-030]."
        ),
        "fuente": "[RG-ART-030]",
    },
    {
        "id": "B3-T20",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "Como todos los estudiantes tienen derecho a revisar sus evaluaciones escritas, un profesor puede botar las pruebas corregidas apenas cierra el semestre y sube las notas al SAC. ¿Es cierto?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-025"],
        "distractores": ["RG-ART-027", "RG-ART-012", "RG-ART-021", "RG-ART-013", "RG-ART-026"],
        "pensar": (
            "Premisa falsa frente a [RG-ART-025] párrafo 3: 'El profesor deberá conservar las evaluaciones escritas realizadas a lo menos "
            "por 30 días hábiles después de concluido el periodo académico correspondiente'."
        ),
        "respuesta": (
            "Es falso: el profesor está obligado a conservar las evaluaciones escritas realizadas durante al menos 30 días hábiles "
            "después de concluido el período académico correspondiente [RG-ART-025]."
        ),
        "condiciones": (
            "Además debe entregar calificaciones y pautas de corrección en un máximo de 10 días hábiles y comunicar fechas y horario de revisión [RG-ART-025]."
        ),
        "fuente": "[RG-ART-025]",
    },
    {
        "id": "B3-T21",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si la nota final promedio de un alumno da exactamente 3,95 antes de aproximar, ¿aprueba o reprueba la asignatura según la regla de aproximación?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-023", "RI-FI-ART-011"],
        "distractores": ["RG-ART-021", "RG-ART-024", "RG-ANEXO-50", "RG-ART-027"],
        "pensar": (
            "[RG-ART-023]: 'Las centésimas iguales o superiores al dígito 5 se aproximarán a la décima superior'. En 3,95 la centésima "
            "es 5 (>= 5), luego aproxima a 4,0. Con 4,0 y cumplimiento de requisitos del curso aprueba según [RG-ART-023] y [RI-FI-ART-011]."
        ),
        "respuesta": (
            "Aprueba (siempre que cumpla los demás requisitos de la asignatura), porque una centésima igual a 5 se aproxima a la décima "
            "superior, elevando 3,95 a 4,0, nota mínima de aprobación [RG-ART-023] [RI-FI-ART-011]."
        ),
        "condiciones": (
            "La aprobación requiere además haber cumplido todos los requisitos establecidos en el programa de la asignatura (de lo contrario "
            "se consigna NCR y reprueba) [RG-ART-023] [RI-FI-ART-011]."
        ),
        "fuente": "[RG-ART-023] [RI-FI-ART-011]",
    },
    {
        "id": "B3-T22",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "La tabla del Anexo de equivalencia indica que en la escala de 1 a 100 el puntaje 50 ya equivale a 4,0 (aprobación mínima). ¿Es correcto?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ANEXO-50", "RG-ANEXO-01"],
        "distractores": ["RG-ANEXO-49", "RG-ART-023", "RI-FI-ART-011", "RG-ART-048"],
        "pensar": (
            "Revisando literalmente [RG-ANEXO-50] y [RG-ANEXO-01]: en [RG-ANEXO-50] 'Reprobación: 50 en escala de 1 a 100 equivale a 3,9 "
            "en escala de 1,0 a 7,0'. En [RG-ANEXO-01] 'Aprobación: 51 en escala de 1 a 100 equivale a 4,0 en escala de 1,0 a 7,0'."
        ),
        "respuesta": (
            "No es correcto: en la tabla oficial, el puntaje 50 en escala de 1 a 100 corresponde a Reprobación y equivale a 3,9 [RG-ANEXO-50]; "
            "la aprobación (4,0) comienza recién en 51 puntos [RG-ANEXO-01]."
        ),
        "condiciones": (
            "Estas equivalencias rigen directamente según el Anexo de escalas de notas del Reglamento General [RG-ANEXO-01] [RG-ANEXO-50]."
        ),
        "fuente": "[RG-ANEXO-01] [RG-ANEXO-50]",
    },
    {
        "id": "B3-T23",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Cuando el Presidente de un Centro de Alumnos recibe facilidades de asistencia por representación estudiantil, ¿queda eximido de aprobar las evaluaciones o requisitos de las asignaturas?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-052"],
        "distractores": ["RG-ART-020", "RI-FI-ART-013", "RG-ART-023", "RG-ART-010", "RI-FI-ART-032"],
        "pensar": (
            "[RG-ART-052]: se otorgan facilidades por el Vicedecano flexibilizando requisitos en clases teóricas y prácticas cuando es posible, "
            "'No obstante, deberán cumplir con los requisitos para aprobar las asignaturas'."
        ),
        "respuesta": (
            "No queda eximido: aunque el Vicedecano otorgue flexibilizaciones en clases teóricas y prácticas cuando sea posible, el dirigente "
            "igualmente debe cumplir con los requisitos para aprobar las asignaturas [RG-ART-052]."
        ),
        "condiciones": (
            "El beneficio aplica a Presidentes de Centros de Alumnos, Presidentes, Secretarios y Tesoreros de Federaciones (Concepción, "
            "Chillán y Los Ángeles) y representantes oficiales de la Universidad en actividades extraprogramáticas [RG-ART-052]."
        ),
        "fuente": "[RG-ART-052]",
    },
    {
        "id": "B3-T24",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "En el segundo semestre de 2026, el período de inscripción de asignaturas y la fecha límite de modificación de asignaturas ocurren exactamente la misma semana (del 03 al 07 de agosto). ¿Es así?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S2-01", "CAL-2026-S2-03"],
        "distractores": ["CAL-2026-S2-02", "CAL-2026-S1-03", "RI-FI-ART-009", "RG-ART-042"],
        "pensar": (
            "[CAL-2026-S2-01]: Inscripción de Asignaturas 03–07 de agosto. [CAL-2026-S2-03]: Modificación de asignaturas fecha límite 04 de septiembre. "
            "No ocurren la misma semana: hay casi un mes entre ambas."
        ),
        "respuesta": (
            "No es así: del 03 al 07 de agosto de 2026 corresponde a la Inscripción de Asignaturas [CAL-2026-S2-01], mientras que la fecha "
            "límite para Modificación de asignaturas en el segundo semestre es el 04 de septiembre [CAL-2026-S2-03]."
        ),
        "condiciones": (
            "Las clases del segundo semestre comienzan entre medio, el 10 de agosto [CAL-2026-S2-02]."
        ),
        "fuente": "[CAL-2026-S2-01] [CAL-2026-S2-02] [CAL-2026-S2-03]",
    },
    {
        "id": "B3-T25",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Al hacer modificación de inscripción de asignaturas dentro del plazo, ¿puede un estudiante eliminar una asignatura atrasada respecto de su nivel de avance si de todas formas queda con 12 créditos inscritos?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-009", "RI-FI-ART-007"],
        "distractores": ["RI-FI-ART-008", "RG-ART-043", "RG-ART-042", "CAL-2026-S1-03"],
        "pensar": (
            "[RI-FI-ART-009] prohíbe DOS cosas de forma independiente: no eliminar prioridades a) (atrasadas respecto a su nivel de avance) "
            "y b) (obligatorias reprobadas anteriormente) del [RI-FI-ART-007], NI contravenir el mínimo de créditos de [RI-FI-ART-008]. "
            "Aunque supere los 8 créditos mínimos, sigue prohibido eliminar una asignatura de prioridad a)."
        ),
        "respuesta": (
            "No puede eliminarla: en Ingeniería está prohibido eliminar durante la modificación de inscripción las asignaturas de prioridad a) "
            "(atrasadas respecto del nivel de avance en el Plan de Estudio), aun cuando mantenga un número de créditos superior al mínimo [RI-FI-ART-007] [RI-FI-ART-009]."
        ),
        "condiciones": (
            "La misma prohibición aplica a las asignaturas de prioridad b) (obligatorias reprobadas anteriormente y no aprobadas a la fecha) "
            "y a bajar del mínimo de ocho créditos del Art. 8° [RI-FI-ART-007] [RI-FI-ART-009]."
        ),
        "fuente": "[RI-FI-ART-007] [RI-FI-ART-009]",
    },
    {
        "id": "B3-T26",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "¿Es verdad que el Reglamento General exige como mínimo un 50% de asistencia de los miembros del Consejo de Carrera para sesionar y al menos 4 sesiones ordinarias por semestre?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-010"],
        "distractores": ["RG-ART-009", "RI-FI-ART-032", "RG-ART-011", "RG-ART-008", "RI-FI-ART-033"],
        "pensar": (
            "[RG-ART-010] establece cifras mayores y menores respectivamente: 'deberá sesionar al menos tres veces cada semestre' (no 4) "
            "y 'Para sesionar se requerirá la presencia de al menos el 60% de los miembros' (no 50%)."
        ),
        "respuesta": (
            "No es verdad: el Consejo de Carrera debe sesionar al menos tres veces cada semestre (no cuatro) y requiere la presencia de al "
            "menos el 60 % de sus miembros para sesionar (no el 50 %) [RG-ART-010]."
        ),
        "condiciones": (
            "Los acuerdos se adoptan por voto conforme de la mayoría de los asistentes, y las sesiones extraordinarias requieren acuerdo del 60 % de los miembros [RG-ART-010]."
        ),
        "fuente": "[RG-ART-010]",
    },
    {
        "id": "B3-T27",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si un estudiante de la UdeC quiere revalidar una asignatura aprobada en un plan de estudios de otra universidad externa a la UdeC, ¿corresponde tramitarlo como 'revalidación'?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-037", "RI-FI-ART-020", "RI-FI-ART-021"],
        "distractores": ["RG-ART-040", "RG-ART-041", "RI-FI-ART-022"],
        "pensar": (
            "Distinción legal entre revalidación y convalidación en [RG-ART-037] y [RI-FI-ART-020]/[RI-FI-ART-021]: 'revalidación' es una "
            "misma asignatura (igual código en FI) ya aprobada en otro plan de otra carrera DE ESTA UNIVERSIDAD. Cuando viene de otra institución "
            "de educación superior (o distinta asignatura de UdeC) corresponde 'convalidación'."
        ),
        "respuesta": (
            "No corresponde como revalidación sino como convalidación: la revalidación aplica únicamente a una misma asignatura ya aprobada "
            "en otro plan de estudio de la Universidad de Concepción, mientras que las aprobadas en otra institución de educación superior "
            "se tramitan mediante convalidación [RG-ART-037] [RI-FI-ART-020] [RI-FI-ART-021]."
        ),
        "condiciones": (
            "La convalidación en Ingeniería exige ser estudiante de especialidad, calificación mínima equivalente a 4,5, acompañar certificado "
            "de notas y programas acreditados, no haberla reprobado antes en el plan y solicitarla dentro de las 4 primeras semanas [RG-ART-037] [RI-FI-ART-021]."
        ),
        "fuente": "[RG-ART-037] [RI-FI-ART-020] [RI-FI-ART-021]",
    },
    {
        "id": "B3-T28",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "Me indicaron que el Plan de Estudio de un alumno antiguo se actualiza obligatoria y automáticamente al nuevo plan apenas la Facultad modifica la malla. ¿Es correcto?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-10"],
        "distractores": ["RG-ART-040", "RG-TRANS-001", "RI-FI-ART-028", "RG-ART-033"],
        "pensar": (
            "[RG-ART-003-DEF-10]: los alumnos quedan adscritos al plan vigente al ingresar; los nuevos planes se ponen en práctica para "
            "quienes ingresan al primer año; los afectos al plan antiguo PUEDEN SOLICITAR al Vicedecano, solo por una vez y durante la inscripción "
            "del inicio del año académico de vigencia, su adscripción al nuevo plan (sin perjuicio de planes transitorios de ajuste). No es automático."
        ),
        "respuesta": (
            "No es correcto: el cambio no es automático; los estudiantes permanecen adscritos al plan vigente al momento de su ingreso, aunque "
            "quienes estén en el plan antiguo pueden solicitar voluntariamente al Vicedecano su adscripción al nuevo plan [RG-ART-003-DEF-10]."
        ),
        "condiciones": (
            "Esa solicitud puede hacerse por una única vez durante el período de inscripción de asignaturas correspondiente al inicio del año "
            "académico en que entra en vigencia el nuevo plan, sin perjuicio de planes transitorios de ajuste que puedan establecerse [RG-ART-003-DEF-10]."
        ),
        "fuente": "[RG-ART-003-DEF-10]",
    },
    {
        "id": "B3-T29",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si un estudiante reingresa a su misma carrera sin haber caído en pérdida de carrera, ¿pierde irremediablemente su situación académica anterior?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-044"],
        "distractores": ["RG-ART-033", "RG-ART-034", "RG-ART-047", "RI-FI-ART-028", "RG-ART-028"],
        "pensar": (
            "[RG-ART-044] párrafo 2: 'Si el alumno que reingresa a la misma carrera no incurrió en pérdida de carrera, podrá solicitar, "
            "dentro de los treinta primeros días del primer semestre de permanencia en la carrera, mantener su situación académica anterior'."
        ),
        "respuesta": (
            "No irremediablemente: si no incurrió en pérdida de carrera, puede solicitar dentro de los treinta primeros días del primer "
            "semestre de permanencia mantener su situación académica anterior [RG-ART-044]."
        ),
        "condiciones": (
            "De no cumplir esa excepción o vencer el plazo, el reingreso a la misma carrera obliga a entrar a Primer Año como alumno nuevo "
            "sin validar, revalidar, convalidar ni reconocer asignaturas aprobadas [RG-ART-044]."
        ),
        "fuente": "[RG-ART-044]",
    },
    {
        "id": "B3-T30",
        "bloque": "polares_y_lectura",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "Para pedir una modificación de un Acta de Notas ya ingresada en el SAC basta con que el Profesor Encargado la envíe dentro de los dos años siguientes al semestre calificado. ¿Es así?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-027"],
        "distractores": ["RG-ART-025", "RG-ART-012", "RG-ART-013", "RG-ART-005", "RG-ART-003-DEF-05"],
        "pensar": (
            "[RG-ART-027] párrafo 3: requiere visto bueno del Vicedecano de la Facultad que dicta la asignatura, firma del Acta de "
            "Modificación por la Comisión de Evaluación y el Director de Departamento, e ingreso al SAC por Secretaría Académica a más tardar "
            "antes del término del semestre siguiente al que calificó la asignatura (no dos años)."
        ),
        "respuesta": (
            "No es así: modificar un Acta de Notas requiere visto bueno del Vicedecano de la Facultad que dicta la asignatura, firma de la "
            "Comisión de Evaluación y el Director de Departamento, y su ingreso al SAC por Secretaría Académica debe hacerse a más tardar "
            "antes del término del semestre siguiente al calificado [RG-ART-027]."
        ),
        "condiciones": (
            "No basta con la sola gestión del Profesor Encargado ni rige un plazo de dos años [RG-ART-027]."
        ),
        "fuente": "[RG-ART-027]",
    },

    # ---- VAL BLOQUE 3 (5 ejemplos) ----
    {
        "id": "B3-V01",
        "bloque": "polares_y_lectura",
        "split": "val",
        "modo": "condicional",
        "pregunta": "Si un estudiante entrega un informe grupal redactado fuera del aula en que copió gran parte del contenido de forma ilícita, ¿está obligado el reglamento a aplicarle solo un 1,0 o existe otra calificación posible?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-023"],
        "distractores": ["RG-ART-051", "RG-ART-013", "RG-ART-021", "RG-ART-024", "RI-FI-ART-011"],
        "pensar": (
            "[RG-ART-023] párrafo final: quien obtenga o facilite información ilícita puede recibir nota mínima, pero si involucra gran "
            "parte de un instrumento desarrollado fuera del aula y requisito (como proyectos o trabajos grupales), el alumno podrá ser calificado con NCR."
        ),
        "respuesta": (
            "Existe otra calificación posible: tratándose de gran parte de un instrumento desarrollado fuera del aula que sea requisito de la "
            "asignatura (como proyectos o trabajos grupales), el alumno puede ser calificado con NCR (no cumple requisito), además de la opción "
            "general de nota mínima [RG-ART-023]."
        ),
        "condiciones": (
            "El concepto NCR (no cumple requisito) implica reprobar la asignatura; la nota mínima de la escala oficial (1 a 7) es 1,0 y también reprueban quienes obtengan Nota Final inferior a 4,0 [RG-ART-023]."
        ),
        "fuente": "[RG-ART-023]",
    },
    {
        "id": "B3-V02",
        "bloque": "polares_y_lectura",
        "split": "val",
        "modo": "premisa_falsa",
        "pregunta": "El calendario 2026 dispone que todas las clases del primer semestre —incluidas las asignaturas anuales— finalizan el 10 de julio. ¿Es correcto?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S1-04", "CAL-2026-S1-05"],
        "distractores": ["CAL-2026-S1-06", "CAL-2026-S1-14", "CAL-2026-S1-02", "CAL-2026-S2-04"],
        "pensar": (
            "[CAL-2026-S1-04] es el término de clases de asignaturas semestrales (10 de julio), mientras [CAL-2026-S1-05] fija el término "
            "de clases de asignaturas anuales en el primer semestre el 24 de julio."
        ),
        "respuesta": (
            "No es correcto: el 10 de julio de 2026 terminan las clases únicamente de las asignaturas semestrales [CAL-2026-S1-04]; las "
            "asignaturas anuales concluyen sus clases del primer semestre el 24 de julio [CAL-2026-S1-05]."
        ),
        "condiciones": (
            "Las Evaluaciones de Recuperación del primer semestre están programadas del 13 al 24 de julio [CAL-2026-S1-06]."
        ),
        "fuente": "[CAL-2026-S1-04] [CAL-2026-S1-05] [CAL-2026-S1-06]",
    },
    {
        "id": "B3-V03",
        "bloque": "polares_y_lectura",
        "split": "val",
        "modo": "condicional",
        "pregunta": "Cuando un estudiante está sancionado disciplinariamente con suspensión de estudios o bien suspende voluntariamente estudios, ¿mantiene intacta su calidad de alumno regular durante la suspensión?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-19", "RG-ART-003-DEF-20", "RG-ART-031"],
        "distractores": ["RG-ART-003-DEF-15", "RG-ART-036", "RG-ART-051"],
        "pensar": (
            "[RG-ART-003-DEF-19], [RG-ART-003-DEF-20] y [RG-ART-031]: en ambos casos pierde transitoriamente la condición/calidad de "
            "alumno regular e interrumpe la calidad de alumno de pregrado (a diferencia de la interrupción por embarazo del Art. 36, donde sí conserva calidad de regular)."
        ),
        "respuesta": (
            "No: tanto en la suspensión de estudios voluntaria o por no inscribir asignaturas [RG-ART-003-DEF-19] [RG-ART-031] como en la "
            "suspensión por sanción disciplinaria [RG-ART-003-DEF-20], el estudiante pierde transitoriamente la condición de alumno regular."
        ),
        "condiciones": (
            "La suspensión voluntaria deja sin efecto la inscripción de asignaturas y tampoco libera al alumno de obligaciones pendientes con la Universidad [RG-ART-031]."
        ),
        "fuente": "[RG-ART-003-DEF-19] [RG-ART-003-DEF-20] [RG-ART-031]",
    },
    {
        "id": "B3-V04",
        "bloque": "polares_y_lectura",
        "split": "val",
        "modo": "premisa_falsa",
        "pregunta": "Un profesor me comentó que si un estudiante tiene un impedimento religioso para asistir a actividades los sábados, puede avisarlo a mitad de semestre cuando salga la fecha del certamen. ¿Es verdadero?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-020"],
        "distractores": ["RI-FI-ART-010", "RI-FI-ART-013", "RG-ART-026", "RG-ART-042", "RG-ART-052"],
        "pensar": (
            "[RG-ART-020] párrafo 2 exige oportunidad exacta: 'deberá acreditarlo al momento de inscribir la o las asignaturas que se trate, "
            "con el objeto de que el Profesor Encargado considere esta circunstancia en la programación de tales actividades'."
        ),
        "respuesta": (
            "No es verdadero: el alumno que estime tener impedimento por razones religiosas debe acreditarlo al momento de inscribir la o las "
            "asignaturas, no a mitad de semestre [RG-ART-020]."
        ),
        "condiciones": (
            "La acreditación oportuna permite que el Profesor Encargado considere esa circunstancia al programar las actividades académicas [RG-ART-020]."
        ),
        "fuente": "[RG-ART-020]",
    },
    {
        "id": "B3-V05",
        "bloque": "polares_y_lectura",
        "split": "val",
        "modo": "condicional",
        "pregunta": "Si en una carrera no existen profesores de otras Facultades que puedan integrar su Consejo de Carrera, ¿queda ese Consejo con menos integrantes o debe sustituirse esos cupos?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-009"],
        "distractores": ["RG-ART-010", "RI-FI-ART-032", "RG-ART-011", "RG-ART-008", "RI-FI-ART-033"],
        "pensar": (
            "[RG-ART-009]: 'En aquellos casos en que no existan profesores de otras Facultades, lo integrarán, en su reemplazo, otros dos profesores de la propia Facultad'."
        ),
        "respuesta": (
            "No queda incompleto: si no existen profesores de otras Facultades que contribuyan significativamente a la carrera, esos cupos "
            "deben integrarse en su reemplazo con otros dos profesores de la propia Facultad [RG-ART-009]."
        ),
        "condiciones": (
            "Además del reemplazo indicado, la composición general incluye al Jefe de Carrera (presidente), al menos tres profesores de la Facultad "
            "y entre tres y cuatro representantes estudiantiles con voz y voto [RG-ART-009]."
        ),
        "fuente": "[RG-ART-009]",
    },
]


BLOQUE_4_CALCULOS_Y_ORDEN: list[dict[str, Any]] = [
    # ---- TRAIN (30 ejemplos) ----
    {
        "id": "B4-T01",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un alumno cursó cuatro actividades: Cálculo I (6 créditos, nota 5,5), Física I (4 créditos, nota 3,2), Taller (5 créditos, NCR) y Deporte (3 créditos, APR). ¿Cuál es su Promedio Ponderado y cuál es su Promedio Curricular?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-024"],
        "distractores": ["RG-ART-021", "RG-ART-023", "RI-FI-ART-030", "RG-ART-046", "RG-ART-003-DEF-07"],
        "pensar": (
            "Aplico [RG-ART-024]: a) Promedio Ponderado usa solo notas >= 4,0 -> solo Cálculo I (6 cr, 5,5); APR se excluye. "
            "Prom. Pond. = (5,5 * 6) / 6 = 5,5. b) Promedio Curricular usa todas las notas finales ponderadas por créditos, "
            "con NCR = 1,0 y excluyendo APR/REP: suma = 5,5*6 + 3,2*4 + 1,0*5 = 33,0 + 12,8 + 5,0 = 50,8; créditos = 6 + 4 + 5 = 15. "
            "50,8 / 15 = 3,3866... -> 3,4 con redondeo de [RG-ART-023] o 3,39 con dos decimales. Indicar valor exacto y aproximado según [RG-ART-024]!"
        ),
        "respuesta": (
            "Su Promedio Ponderado es 5,5 y su Promedio Curricular es 3,39 (50,8 / 15; aproximadamente 3,4 a un decimal) [RG-ART-024]."
        ),
        "condiciones": (
            "Cálculo: el Promedio Ponderado incluye solo notas finales >= 4,0 y excluye APR, dando (5,5 × 6) / 6 = 5,5; el Promedio Curricular "
            "incluye todas las notas finales asignando 1,0 al NCR y excluyendo APR: (5,5 × 6 + 3,2 × 4 + 1,0 × 5) / (6 + 4 + 5) = 50,8 / 15 = 3,3867 [RG-ART-024]."
        ),
        "fuente": "[RG-ART-024]",
    },
    {
        "id": "B4-T02",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un estudiante aprobó Química (5 créditos, 5,0) e Introducción (5 créditos, 4,2), reprobó Álgebra (4 créditos, 2,5) y obtuvo REP en Inglés (2 créditos). Calcula su Promedio Ponderado y su Promedio Curricular.",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-024"],
        "distractores": ["RG-ART-021", "RG-ART-023", "RI-FI-ART-005", "RG-ART-041", "RG-ART-003-DEF-07"],
        "pensar": (
            "[RG-ART-024]: REP no se considera en ningún promedio. "
            "Prom. Pond. (>= 4,0): (5,0*5 + 4,2*5) / (5 + 5) = (25,0 + 21,0) / 10 = 46,0 / 10 = 4,6. "
            "Prom. Curr. (todas las notas numéricas): (5,0*5 + 4,2*5 + 2,5*4) / (5 + 5 + 4) = (25,0 + 21,0 + 10,0) / 14 = 56,0 / 14 = 4,0."
        ),
        "respuesta": (
            "El Promedio Ponderado es 4,6 y el Promedio Curricular es 4,0 [RG-ART-024]."
        ),
        "condiciones": (
            "Cálculo excluyendo REP (2 créditos): Promedio Ponderado = (5,0 × 5 + 4,2 × 5) / 10 = 46,0 / 10 = 4,6; Promedio Curricular = "
            "(5,0 × 5 + 4,2 × 5 + 2,5 × 4) / (5 + 5 + 4) = 56,0 / 14 = 4,0 [RG-ART-024]."
        ),
        "fuente": "[RG-ART-024]",
    },
    {
        "id": "B4-T03",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un egresado de Ingeniería Civil tuvo un promedio ponderado del Plan de Estudio (sin Memoria) de 4,8 y obtuvo un 6,3 en su Memoria de Título. ¿Cuál es su nota de titulación y qué concepto irá en su Diploma?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-030", "RG-ART-048"],
        "distractores": ["RI-FI-ART-029", "RG-ART-023", "RG-ART-024", "RG-ART-047"],
        "pensar": (
            "[RI-FI-ART-030]: 60 % plan sin Memoria + 40 % Memoria. 0,6 × 4,8 + 0,4 × 6,3 = 2,88 + 2,52 = 5,40 = 5,4. "
            "[RG-ART-048]: 5,4 cae en el rango 5,0 - 5,6 -> 'Aprobado con Distinción'."
        ),
        "respuesta": (
            "Su nota de titulación es 5,4 [RI-FI-ART-030] y en su Diploma de Título Profesional corresponderá el concepto 'Aprobado con Distinción' [RG-ART-048]."
        ),
        "condiciones": (
            "Cálculo: (0,60 × 4,8) + (0,40 × 6,3) = 2,88 + 2,52 = 5,4 [RI-FI-ART-030]; el rango 5,0 a 5,6 corresponde a Aprobado con Distinción [RG-ART-048]."
        ),
        "fuente": "[RG-ART-048] [RI-FI-ART-030]",
    },
    {
        "id": "B4-T04",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Si un estudiante de Ingeniería Civil obtuvo 4,6 en su plan de estudios (sin Memoria) y 5,2 en su Memoria de Título, ¿cuál es su nota de titulación redondeada a la décima y qué concepto lleva su Diploma?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-030", "RG-ART-023", "RG-ART-048"],
        "distractores": ["RG-ART-024", "RI-FI-ART-029", "RG-ANEXO-16"],
        "pensar": (
            "[RI-FI-ART-030]: 0,6 × 4,6 + 0,4 × 5,2 = 2,76 + 2,08 = 4,84. "
            "[RG-ART-023]: escala con un decimal; centésima 4 < 5 no afecta a la décima -> 4,8. "
            "[RG-ART-048]: 4,8 en rango 4,0 - 4,9 -> 'Aprobado por Unanimidad'."
        ),
        "respuesta": (
            "La nota exacta ponderada es 4,84, que se aproxima a 4,8 [RG-ART-023] [RI-FI-ART-030], correspondiendo el concepto 'Aprobado por Unanimidad' en el Diploma [RG-ART-048]."
        ),
        "condiciones": (
            "Cálculo: (0,60 × 4,6) + (0,40 × 5,2) = 2,76 + 2,08 = 4,84 [RI-FI-ART-030]; como la centésima 4 es inferior a 5, se mantiene en 4,8 [RG-ART-023], ubicado en el tramo 4,0–4,9 [RG-ART-048]."
        ),
        "fuente": "[RG-ART-023] [RG-ART-048] [RI-FI-ART-030]",
    },
    {
        "id": "B4-T05",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un estudiante ingresó directamente a nivel superior por convalidaciones y al término de su quinto semestre registra 62 créditos aprobados en total en su historial, de los cuales 18 corresponden a asignaturas convalidadas. ¿Cumple el promedio mínimo de 10 créditos del Art. 14 b)?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-015", "RI-FI-ART-014", "RG-ART-028"],
        "distractores": ["RG-ART-041", "RI-FI-ART-021", "RI-FI-ART-016"],
        "pensar": (
            "[RI-FI-ART-015]: para aplicar Art. 14° b) NO se contabilizan créditos convalidados/revalidados/reconocidos. "
            "Créditos computables = 62 - 18 = 44. Promedio sobre 5 semestres ([RG-ART-028] a / [RI-FI-ART-014] b): 44 / 5 = 8,8 créditos/semestre. "
            "Como 8,8 < 10, NO cumple y cae en Baja Académica."
        ),
        "respuesta": (
            "No cumple: queda en situación de Baja Académica porque su promedio computable de créditos aprobados es 8,8 créditos por semestre, inferior al mínimo de 10 [RG-ART-028] [RI-FI-ART-014] [RI-FI-ART-015]."
        ),
        "condiciones": (
            "Cálculo: no se contabilizan los 18 créditos convalidados [RI-FI-ART-015], por lo que computan 62 − 18 = 44 créditos en 5 semestres: 44 / 5 = 8,8 < 10 [RG-ART-028] [RI-FI-ART-014]."
        ),
        "fuente": "[RG-ART-028] [RI-FI-ART-014] [RI-FI-ART-015]",
    },
    {
        "id": "B4-T06",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Otro alumno en situación equivalente al término de su quinto semestre registra 68 créditos aprobados, incluidos 13 reconocidos por examen. ¿Cae en Baja Académica por promedio de créditos?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-015", "RI-FI-ART-014", "RG-ART-028"],
        "distractores": ["RG-ART-041", "RG-ART-038", "RI-FI-ART-023"],
        "pensar": (
            "Créditos computables = 68 - 13 = 55 ([RI-FI-ART-015]). Dividido en 5 semestres: 55 / 5 = 11,0 créditos/semestre. "
            "Como 11,0 >= 10, NO cae en baja académica."
        ),
        "respuesta": (
            "No cae en Baja Académica por ese criterio, pues su promedio computable es 11,0 créditos por semestre, superior al mínimo de 10 [RG-ART-028] [RI-FI-ART-014] [RI-FI-ART-015]."
        ),
        "condiciones": (
            "Cálculo: descontando los 13 créditos reconocidos [RI-FI-ART-015] quedan 68 − 13 = 55 créditos aprobados en 5 semestres: 55 / 5 = 11,0 >= 10 [RG-ART-028] [RI-FI-ART-014]."
        ),
        "fuente": "[RG-ART-028] [RI-FI-ART-014] [RI-FI-ART-015]",
    },
    {
        "id": "B4-T07",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "En el calendario 2026, ¿cuántos días corridos transcurren entre el inicio de clases del primer semestre y el término de clases de las asignaturas semestrales, y cuántos días más duran las clases de asignaturas anuales en ese mismo semestre?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S1-02", "CAL-2026-S1-04", "CAL-2026-S1-05"],
        "distractores": ["CAL-2026-S1-03", "CAL-2026-S1-06", "CAL-2026-S1-01"],
        "pensar": (
            "[CAL-2026-S1-02]: inicio 09 de marzo. [CAL-2026-S1-04]: término semestrales 10 de julio. "
            "Conteo: marzo (31 - 9 = 22) + abril (30) + mayo (31) + junio (30) + julio (10) = 123 días de diferencia. "
            "[CAL-2026-S1-05]: término anuales 24 de julio. Diferencia extra: 24 - 10 = 14 días adicionales."
        ),
        "respuesta": (
            "Transcurren 123 días desde el inicio de clases (09 de marzo) hasta el término de las asignaturas semestrales (10 de julio) "
            "[CAL-2026-S1-02] [CAL-2026-S1-04], y las asignaturas anuales extienden su período de clases del primer semestre 14 días más (hasta el 24 de julio) [CAL-2026-S1-05]."
        ),
        "condiciones": (
            "Cálculo: marzo (31 − 9 = 22) + abril (30) + mayo (31) + junio (30) + julio (10) = 123 días; extensión anual: 24 − 10 = 14 días adicionales [CAL-2026-S1-02] [CAL-2026-S1-04] [CAL-2026-S1-05]."
        ),
        "fuente": "[CAL-2026-S1-02] [CAL-2026-S1-04] [CAL-2026-S1-05]",
    },
    {
        "id": "B4-T08",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Compara cuántos días corridos hay desde el inicio hasta el término de clases entre el primer semestre (asignaturas semestrales) y el segundo semestre de 2026.",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S1-02", "CAL-2026-S1-04", "CAL-2026-S2-02", "CAL-2026-S2-04"],
        "distractores": ["CAL-2026-S1-05", "CAL-2026-S2-01"],
        "pensar": (
            "S1: 09 de marzo ([CAL-2026-S1-02]) al 10 de julio ([CAL-2026-S1-04]) = 22 + 30 + 31 + 30 + 10 = 123 días. "
            "S2: 10 de agosto ([CAL-2026-S2-02]) al 11 de diciembre ([CAL-2026-S2-04]) = agosto (31 - 10 = 21) + sept (30) + oct (31) + nov (30) + dic (11) = 123 días. "
            "Ambos tienen exactamente 123 días de diferencia."
        ),
        "respuesta": (
            "Ambos períodos tienen exactamente la misma duración entre inicio y término de clases semestrales: 123 días cada uno [CAL-2026-S1-02] [CAL-2026-S1-04] [CAL-2026-S2-02] [CAL-2026-S2-04]."
        ),
        "condiciones": (
            "Cálculo: Primer semestre (09 mar a 10 jul) = 22 + 30 + 31 + 30 + 10 = 123 días [CAL-2026-S1-02] [CAL-2026-S1-04]; Segundo semestre "
            "(10 ago a 11 dic) = 21 + 30 + 31 + 30 + 11 = 123 días [CAL-2026-S2-02] [CAL-2026-S2-04]."
        ),
        "fuente": "[CAL-2026-S1-02] [CAL-2026-S1-04] [CAL-2026-S2-02] [CAL-2026-S2-04]",
    },
    {
        "id": "B4-T09",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Si un estudiante aprueba un Programa de Formación Complementaria con la carga mínima exigida en Créditos Transferibles (SCT), ¿a cuántas horas totales de trabajo presencial y no presencial equivale como mínimo?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-12", "RG-ART-003-DEF-08"],
        "distractores": ["RG-ART-056", "RG-ART-003-DEF-07", "RG-ART-017", "RG-ART-003-DEF-10"],
        "pensar": (
            "[RG-ART-003-DEF-12]: carga mínima no inferior a 24 créditos transferibles. [RG-ART-003-DEF-08]: 1 SCT equivale a 27 horas de "
            "trabajo presencial y no presencial. Cálculo: 24 × 27 = 648 horas."
        ),
        "respuesta": (
            "Equivale como mínimo a 648 horas de trabajo académico (presencial y no presencial) [RG-ART-003-DEF-08] [RG-ART-003-DEF-12]."
        ),
        "condiciones": (
            "Cálculo: el programa exige al menos 24 créditos transferibles [RG-ART-003-DEF-12] y cada SCT equivale a 27 horas [RG-ART-003-DEF-08]: 24 × 27 = 648 horas."
        ),
        "fuente": "[RG-ART-003-DEF-08] [RG-ART-003-DEF-12]",
    },
    {
        "id": "B4-T10",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Según el Reglamento General, ¿cuántos minutos reales de clase equivalen a 6 horas docentes?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-06"],
        "distractores": ["RG-ART-003-DEF-07", "RG-ART-003-DEF-08", "RG-ART-017", "RG-ART-016", "RG-ART-003-DEF-09"],
        "pensar": (
            "[RG-ART-003-DEF-06]: una hora docente corresponde a una sesión de docencia de 45 minutos. 6 × 45 = 270 minutos (4 horas y 30 minutos)."
        ),
        "respuesta": (
            "Equivalen a 270 minutos (4 horas y 30 minutos) [RG-ART-003-DEF-06]."
        ),
        "condiciones": (
            "Cálculo: cada hora docente dura 45 minutos [RG-ART-003-DEF-06], por lo que 6 × 45 = 270 minutos."
        ),
        "fuente": "[RG-ART-003-DEF-06]",
    },
    {
        "id": "B4-T11",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un alumno obtuvo 70 puntos sobre 100 en escala porcentual de 1 a 100, mientras un compañero obtuvo 69 puntos. ¿Qué nota equivalente (1,0 a 7,0) y qué concepto en el título o grado corresponden a cada uno?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ANEXO-19", "RG-ANEXO-20"],
        "distractores": ["RG-ANEXO-18", "RG-ANEXO-21", "RG-ART-048", "RG-ART-023"],
        "pensar": (
            "Verifico textualmente [RG-ANEXO-19] y [RG-ANEXO-20]: 69 -> 5,1, 'Aprobado por Unanimidad'; 70 -> 5,2, 'Aprobado con Distinción'."
        ),
        "respuesta": (
            "69 puntos equivalen a 5,1 ('Aprobado por Unanimidad') [RG-ANEXO-19] y 70 puntos equivalen a 5,2 ('Aprobado con Distinción') [RG-ANEXO-20]."
        ),
        "condiciones": (
            "Valores exactos según el Anexo de equivalencia de escalas de notas en escala de aprobación 1–100 a 1,0–7,0 [RG-ANEXO-19] [RG-ANEXO-20]."
        ),
        "fuente": "[RG-ANEXO-19] [RG-ANEXO-20]",
    },
    {
        "id": "B4-T12",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "En la escala 1 a 100 del Anexo, ¿con qué puntaje mínimo de aprobación se alcanza el concepto 'Aprobado con Distinción Máxima' y a qué nota de 1,0 a 7,0 equivale frente al puntaje inmediatamente anterior?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ANEXO-36", "RG-ANEXO-37"],
        "distractores": ["RG-ANEXO-35", "RG-ANEXO-38", "RG-ART-048", "RG-ART-023"],
        "pensar": (
            "[RG-ANEXO-36]: Aprobación 86 -> 6,5 ('Aprobado con Distinción'). [RG-ANEXO-37]: Aprobación 87 -> 6,5 ('Aprobado con Distinción Máxima'). "
            "¡Ojo! Ambos equivalen a 6,5 en 1,0 a 7,0, pero en 86 dice 'Aprobado con Distinción' y recién en 87 pasa a 'Aprobado con Distinción Máxima'!"
        ),
        "respuesta": (
            "El concepto 'Aprobado con Distinción Máxima' comienza en 87 puntos en la escala de 1 a 100, equivalente a 6,5 [RG-ANEXO-37]; "
            "el puntaje inmediatamente anterior (86 puntos) también equivale a 6,5, pero corresponde al concepto 'Aprobado con Distinción' [RG-ANEXO-36]."
        ),
        "condiciones": (
            "Diferencia exacta registrada en la tabla del Anexo de equivalencias de notas [RG-ANEXO-36] [RG-ANEXO-37]."
        ),
        "fuente": "[RG-ANEXO-36] [RG-ANEXO-37]",
    },
    {
        "id": "B4-T13",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Dos estudiantes del Ingreso Común postulan a la misma carrera de Ingeniería Civil con un solo cupo disponible: el alumno A aprobó 30 créditos y tiene promedio curricular 5,80 en el Plan Común de Primer Año; el alumno B aprobó 32 créditos y tiene promedio curricular 5,20. ¿Quién tiene prioridad de selección y qué ocurre si hubiesen empatado en créditos?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-005"],
        "distractores": ["RI-FI-ART-006", "RI-FI-ART-003", "RI-FI-ART-004", "RG-ART-024", "RI-FI-ART-018"],
        "pensar": (
            "[RI-FI-ART-005]: orden estricto -> 1° número de créditos aprobados; 2° a igual número de créditos, promedio curricular de "
            "asignaturas ponderadas por créditos del Plan Común de Primer Año con dos decimales (incluyendo aprobadas y reprobadas), "
            "considerando orden de preferencias y cupos; solo asignaturas obligatorias de Primer Año. Aquí B tiene 32 > 30 créditos, gana B aunque A tenga mayor nota."
        ),
        "respuesta": (
            "Tiene prioridad el alumno B (32 créditos frente a 30), porque la selección se ordena en primer lugar por número de créditos "
            "aprobados; recién a igual número de créditos aprobados se desempata por el promedio curricular del Plan Común de Primer Año con dos decimales [RI-FI-ART-005]."
        ),
        "condiciones": (
            "El promedio de desempate pondera asignaturas aprobadas y reprobadas del Plan Común de Primer Año (solo obligatorias), y la "
            "asignación considera también el orden de preferencias del estudiante y los cupos disponibles [RI-FI-ART-005]."
        ),
        "fuente": "[RI-FI-ART-005]",
    },
    {
        "id": "B4-T14",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Cuál es el orden exacto de prioridad que rige la inscripción de asignaturas al inicio de un período lectivo ordinario en la Facultad de Ingeniería?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-007"],
        "distractores": ["RI-FI-ART-008", "RI-FI-ART-009", "RG-ART-042", "CAL-2026-S2-01", "RI-FI-ART-005"],
        "pensar": (
            "[RI-FI-ART-007] fija el orden exacto a->b->c->d: a) atrasadas con respecto a su nivel de avance; b) obligatorias reprobadas "
            "anteriormente y no aprobadas a la fecha; c) correspondientes a su nivel de avance; d) asignaturas que desee adelantar."
        ),
        "respuesta": (
            "El orden estricto de prioridades para inscribir asignaturas es: (1) asignaturas atrasadas respecto del nivel de avance en el "
            "Plan de Estudio; (2) asignaturas obligatorias reprobadas anteriormente y aún no aprobadas; (3) asignaturas del propio nivel de avance; "
            "y (4) asignaturas que desee adelantar [RI-FI-ART-007]."
        ),
        "condiciones": (
            "La inscripción está sujeta a cumplir los requisitos de cada asignatura y realizarse dentro de las fechas del calendario anual de docencia [RI-FI-ART-007]."
        ),
        "fuente": "[RI-FI-ART-007]",
    },
    {
        "id": "B4-T15",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Describe paso a paso la secuencia jerárquica completa de instancias ordinarias, apelaciones y recurso extraordinario que puede recorrer un estudiante en Baja Académica.",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-030", "RI-FI-ART-016"],
        "distractores": ["RG-ART-028", "RI-FI-ART-014", "RI-FI-ART-033", "RG-ART-004"],
        "pensar": (
            "[RG-ART-030]: hasta 3 oportunidades dentro de 1 año: 1ª solicitud -> Comité de Docencia y Asuntos Estudiantiles (<= 10 días), "
            "apelable 5 días hábiles al Vicedecano y de su resolución al Decano; 2ª solicitud -> Vicedecano (<= 10 días hábiles), apelable "
            "al Decano (5 días hábiles); 3ª solicitud -> Decano (<= 10 días hábiles); excepcional y por única vez dentro de 5 días hábiles "
            "de lo resuelto por Decano -> recurso fundado por gracia ante Vicerrector."
        ),
        "respuesta": (
            "Dispone de tres oportunidades dentro de un año en orden escalonado: (1) primera solicitud ante el Comité de Docencia y Asuntos "
            "Estudiantiles (apelable al Vicedecano y luego al Decano); (2) segunda solicitud ante el Vicedecano (apelable al Decano); "
            "y (3) tercera solicitud ante el Decano [RG-ART-030] [RI-FI-ART-016]. Excepcionalmente y por única vez puede recurrir por gracia ante el Vicerrector [RG-ART-030]."
        ),
        "condiciones": (
            "Plazos: resolución en hasta 10 días (1ª) o 10 días hábiles (2ª y 3ª), y todas las apelaciones (incluida la solicitud al Vicerrector) "
            "deben interponerse dentro del quinto día hábil de notificada la resolución [RG-ART-030]."
        ),
        "fuente": "[RG-ART-030] [RI-FI-ART-016]",
    },
    {
        "id": "B4-T16",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un Consejo de Carrera de Ingeniería está compuesto por 13 integrantes en total. ¿Cuántos integrantes deben asistir como mínimo para poder sesionar y qué proporción mínima debe solicitar una sesión extraordinaria?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-010"],
        "distractores": ["RI-FI-ART-032", "RG-ART-009", "RG-ART-011", "RI-FI-ART-033", "RG-ART-008"],
        "pensar": (
            "[RG-ART-010]: quórum para sesionar >= 60 %; sesiones extraordinarias solicitadas por acuerdo del 60 %. "
            "Cálculo: 0,60 × 13 = 7,8. Como el número de miembros asistentes debe ser entero y al menos el 60 % (7 < 7,8 = 53,8 %), se necesitan al menos 8 miembros."
        ),
        "respuesta": (
            "Deben asistir como mínimo 8 integrantes (60 % de 13 es 7,8, por lo que al menos 8 cumplen el mínimo) para sesionar, y las sesiones "
            "extraordinarias requieren acuerdo del 60 % de los miembros (igualmente al menos 8 de 13) [RG-ART-010]."
        ),
        "condiciones": (
            "Cálculo: 13 × 0,60 = 7,8 -> mínimo entero >= 60 % es 8 miembros (8/13 = 61,5 %; 7/13 = 53,8 %); los acuerdos se toman por mayoría de los asistentes [RG-ART-010]."
        ),
        "fuente": "[RG-ART-010]",
    },
    {
        "id": "B4-T17",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Si un plan de estudios completo exige 300 créditos transferibles (SCT), ¿cuál es el número mínimo de SCT que deben corresponder a asignaturas que contribuyen a la formación integral del alumno?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-10"],
        "distractores": ["RG-ART-003-DEF-08", "RG-ART-003-DEF-09", "RG-ART-003-DEF-12", "RG-ART-017", "RG-ART-046"],
        "pensar": (
            "[RG-ART-003-DEF-10] letra g): al menos el 10 % del total de créditos transferibles del plan de estudios. "
            "Cálculo: 10 % de 300 = 0,10 × 300 = 30 SCT."
        ),
        "respuesta": (
            "Deben destinarse al menos 30 créditos transferibles (SCT) a asignaturas que contribuyen a la formación integral [RG-ART-003-DEF-10]."
        ),
        "condiciones": (
            "Cálculo: el plan debe asignar al menos el 10 % del total de SCT a formación integral: 300 × 0,10 = 30 SCT [RG-ART-003-DEF-10]."
        ),
        "fuente": "[RG-ART-003-DEF-10]",
    },
    {
        "id": "B4-T18",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un estudiante rindió una asignatura de 4 evaluaciones ponderadas cuyo cálculo preliminar exacto fue 5,64; otro compañero en el mismo caso obtuvo 5,65. Según las reglas de aproximación y diploma, ¿cuál nota final obtiene cada uno y en qué concepto de título quedarían con esa nota?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-023", "RG-ART-048"],
        "distractores": ["RG-ART-021", "RG-ART-024", "RI-FI-ART-030", "RG-ANEXO-24"],
        "pensar": (
            "[RG-ART-023]: centésimas < 5 no afectan la décima; >= 5 suben a décima superior. "
            "5,64 -> centésima 4 < 5 -> 5,6. 5,65 -> centésima 5 >= 5 -> 5,7. "
            "[RG-ART-048]: 5,6 está en 5,0–5,6 ('Aprobado con Distinción') y 5,7 está en 5,7–7,0 ('Aprobado con Distinción Máxima')."
        ),
        "respuesta": (
            "El promedio 5,64 queda en 5,6 (tramo 'Aprobado con Distinción'), mientras que 5,65 se aproxima a 5,7 (tramo 'Aprobado con Distinción Máxima') [RG-ART-023] [RG-ART-048]."
        ),
        "condiciones": (
            "Regla: las centésimas inferiores a 5 mantienen la décima y las iguales o superiores a 5 aproximan a la décima superior [RG-ART-023]; "
            "el concepto rige en Diplomas de Título Profesional y Licenciados en carreras terminales [RG-ART-048]."
        ),
        "fuente": "[RG-ART-023] [RG-ART-048]",
    },
    {
        "id": "B4-T19",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "¿Cuántos días corridos dura el período de vacaciones de invierno (aprobación transitoria) y cuántos días dura la pausa activa de docencia del primer semestre de 2026?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S1-14", "CAL-2026-S1-07"],
        "distractores": ["CAL-2026-S1-08", "CAL-2026-S2-06", "CAL-2026-S1-12", "CAL-2026-S1-11"],
        "pensar": (
            "[CAL-2026-S1-14]: 30 junio – 05 de julio (junio tiene 30 días): 30 jun (1) + 1 al 5 jul (5) = 6 días corridos inclusivos (diferencia 5 días). "
            "[CAL-2026-S1-07]: 11 – 15 de mayo = 15 - 11 + 1 = 5 días corridos (lunes a viernes)."
        ),
        "respuesta": (
            "Las vacaciones de invierno (30 de junio al 05 de julio) abarcan 6 días inclusive (diferencia de 5 días) [CAL-2026-S1-14], y la "
            "pausa activa de docencia (11 al 15 de mayo) abarca 5 días inclusive (diferencia de 4 días) [CAL-2026-S1-07]."
        ),
        "condiciones": (
            "Cálculo: 30 de junio (1 día) más 01 al 05 de julio (5 días) = 6 días (2026, junio tiene 30 días) [CAL-2026-S1-14]; del 11 al 15 de mayo son 5 días corridos inclusive [CAL-2026-S1-07]."
        ),
        "fuente": "[CAL-2026-S1-07] [CAL-2026-S1-14]",
    },
    {
        "id": "B4-T20",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "En un curso universitario con 18 créditos semanales asignados según el Reglamento General y 36 horas de trabajo indirecto autónomo fuera de horario en la semana, ¿cuántas horas de Trabajo Académico semanal total tiene un alumno que cursa solo docencia teórica y excede o no el tope reglamentario?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-07", "RG-ART-017"],
        "distractores": ["RG-ART-003-DEF-06", "RG-ART-003-DEF-08", "RI-FI-ART-008", "RG-ART-003-DEF-10"],
        "pensar": (
            "[RG-ART-003-DEF-07]: 1 crédito = 1 hora docente de clase teórica semanal. Trabajo Académico = horas de docencia directa + "
            "horas indirectas o complementarias fuera de horario = 18 + 36 = 54 horas semanales. "
            "[RG-ART-017]: el plan de estudios no debería exceder las 54 horas semanales (y [RG-ART-003-DEF-07]: tiempo completo 45–54 horas). No excede el tope: está justo en el límite de 54 horas."
        ),
        "respuesta": (
            "Suma exactamente 54 horas semanales de Trabajo Académico (18 de docencia directa + 36 indirectas), por lo que se ubica en el límite "
            "máximo sin exceder el tope de 54 horas semanales [RG-ART-003-DEF-07] [RG-ART-017]."
        ),
        "condiciones": (
            "Cálculo: 1 crédito corresponde a 1 hora docente de clase teórica semanal, sumado a las 36 horas indirectas da 18 + 36 = 54 horas "
            "semanales, dentro del rango de tiempo completo de 45 a 54 horas [RG-ART-003-DEF-07] [RG-ART-017]."
        ),
        "fuente": "[RG-ART-003-DEF-07] [RG-ART-017]",
    },
    {
        "id": "B4-T21",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Según el Calendario 2026, ¿cuántos días corridos median entre el inicio de la Inscripción de Asignaturas del segundo semestre y el inicio de clases del mismo semestre, y cuántos días dura la ventana de Evaluaciones de Recuperación del segundo semestre?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S2-01", "CAL-2026-S2-02", "CAL-2026-S2-05"],
        "distractores": ["CAL-2026-S2-03", "CAL-2026-S2-04", "CAL-2026-S1-06"],
        "pensar": (
            "[CAL-2026-S2-01]: inscripción 03–07 de agosto; [CAL-2026-S2-02]: inicio clases 10 de agosto -> 10 - 3 = 7 días desde el inicio "
            "de la inscripción (o 3 días después de cerrar el 07 de agosto). [CAL-2026-S2-05]: Evaluaciones de Recuperación 14–23 de diciembre "
            "= 23 - 14 + 1 = 10 días corridos inclusive (9 días de diferencia)."
        ),
        "respuesta": (
            "Median 7 días desde la apertura de inscripción (03 de agosto) hasta el inicio de clases (10 de agosto) —y 3 días desde su cierre "
            "el 07 de agosto— [CAL-2026-S2-01] [CAL-2026-S2-02]; el período de Evaluaciones de Recuperación (14 al 23 de diciembre) abarca "
            "10 días corridos inclusive (diferencia de 9 días) [CAL-2026-S2-05]."
        ),
        "condiciones": (
            "Cálculo sobre el Segundo Semestre 2026: 10 − 3 = 7 días (10 − 7 = 3 días desde el cierre) y 23 − 14 + 1 = 10 días inclusive [CAL-2026-S2-01] [CAL-2026-S2-02] [CAL-2026-S2-05]."
        ),
        "fuente": "[CAL-2026-S2-01] [CAL-2026-S2-02] [CAL-2026-S2-05]",
    },
    {
        "id": "B4-T22",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "En un certamen rindieron 40 estudiantes y 22 de ellos obtuvieron nota inferior a 4,0. ¿Supera el umbral que obliga a convocar a la Comisión de Evaluación y qué autoridad la convoca?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-013"],
        "distractores": ["RG-ART-012", "RG-ART-025", "RG-ART-023", "RI-FI-ART-011", "RG-ART-006"],
        "pensar": (
            "[RG-ART-013]: 'cuando más del 50 % los alumnos que rinden la evaluación obtienen nota inferior a 4.0, el Director del "
            "Departamento al que está adscrita la asignatura convocará a esta Comisión de Evaluación'. 22 / 40 = 0,55 = 55 % > 50 %. Sí supera el umbral."
        ),
        "respuesta": (
            "Sí supera el umbral (22 de 40 equivale al 55 %, mayor que 50 %), por lo que el Director del Departamento al que está adscrita "
            "la asignatura debe convocar a la Comisión de Evaluación [RG-ART-013]."
        ),
        "condiciones": (
            "Cálculo: 22 / 40 = 55 % > 50 %; la Comisión de Evaluación (Profesor Encargado + dos profesores designados) estudia la situación, "
            "resuelve e informa al Vicedecano de la Facultad [RG-ART-013]."
        ),
        "fuente": "[RG-ART-013]",
    },
    {
        "id": "B4-T23",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Si un año académico tiene dos Períodos Lectivos Ordinarios completos más un PLEV completo, ¿cuántas semanas suman en total los períodos fijados en el Artículo 16 del Reglamento General?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-016"],
        "distractores": ["RG-ART-045", "RG-ART-018", "CAL-2026-S1-02", "CAL-2026-S2-02", "CAL-2026-S1-04"],
        "pensar": (
            "[RG-ART-016]: dos Períodos Lectivos Ordinarios de 19 semanas cada uno y un PLEV de 6 semanas. 2 × 19 + 6 = 38 + 6 = 44 semanas."
        ),
        "respuesta": (
            "Suman 44 semanas en total: 38 semanas de los dos Períodos Lectivos Ordinarios más 6 semanas del PLEV [RG-ART-016]."
        ),
        "condiciones": (
            "Cálculo: (2 × 19) + 6 = 38 + 6 = 44 semanas; su programación anual queda fijada por el Calendario Anual de Docencia de Pregrado [RG-ART-016]."
        ),
        "fuente": "[RG-ART-016]",
    },
    {
        "id": "B4-T24",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un estudiante aprobó su sexto semestre acumulando 63 créditos aprobados en una carrera donde el mínimo semestral exigido es 10 créditos. ¿Cumple la exigencia de promedio de créditos?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-028", "RI-FI-ART-014"],
        "distractores": ["RI-FI-ART-015", "RG-ART-030", "RG-ART-024", "RI-FI-ART-008"],
        "pensar": (
            "[RG-ART-028] a) / [RI-FI-ART-014] b): promedio = créditos aprobados / semestres de permanencia = 63 / 6 = 10,5 créditos/semestre. "
            "Como 10,5 >= 10, sí cumple y no cae en baja académica."
        ),
        "respuesta": (
            "Sí cumple: su promedio es 10,5 créditos aprobados por semestre, igual o superior al mínimo exigido de 10 [RG-ART-028] [RI-FI-ART-014]."
        ),
        "condiciones": (
            "Cálculo: 63 créditos aprobados / 6 semestres de permanencia = 10,5 >= 10 créditos semestrales [RG-ART-028] [RI-FI-ART-014]."
        ),
        "fuente": "[RG-ART-028] [RI-FI-ART-014]",
    },
    {
        "id": "B4-T25",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "¿Cuál es la diferencia en días corridos entre el plazo máximo que tiene un alumno para presentar una reclamación ante el Vicedecano tras revisar su prueba y el plazo máximo de la Comisión ad hoc para resolverla?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-025"],
        "distractores": ["RG-ART-026", "RG-ART-013", "RG-ART-030", "RG-ART-037", "RI-FI-ART-023"],
        "pensar": (
            "[RG-ART-025]: apelación al Vicedecano = máximo 5 días hábiles; resolución Comisión ad hoc = 10 días corridos. "
            "¡Atención! Uno está expresado en días HÁBILES (5 días hábiles) y el otro en días CORRIDOS (10 días corridos); no se deben restar "
            "como si fueran de la misma unidad sin explicitar esa diferencia reglamentaria!"
        ),
        "respuesta": (
            "El plazo para reclamar al Vicedecano es de 5 días hábiles y el de la Comisión ad hoc para resolver es de 10 días corridos, por lo "
            "que difieren tanto en magnitud (5 vs. 10) como en tipo de cómputo (días hábiles frente a días corridos) [RG-ART-025]."
        ),
        "condiciones": (
            "Los 5 días hábiles corren desde la fecha de revisión ante el profesor y los 10 días corridos desde la presentación de la reclamación, "
            "resolviendo la Comisión ad hoc mediante acta inapelable [RG-ART-025]."
        ),
        "fuente": "[RG-ART-025]",
    },
    {
        "id": "B4-T26",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "En la escala 1 a 100 del Anexo, ¿qué nota en escala 1,0 a 7,0 y qué concepto corresponden a un puntaje de reprobación de 25 puntos frente a un puntaje de aprobación de 75 puntos?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ANEXO-25"],
        "distractores": ["RG-ANEXO-24", "RG-ANEXO-26", "RG-ANEXO-01", "RG-ART-023", "RG-ART-048"],
        "pensar": (
            "[RG-ANEXO-25] contiene exactamente ambas cifras: Reprobación 25 -> 2,4; Aprobación 75 -> 5,7 ('Aprobado con Distinción'). "
            "Ojo con un detalle increíble en [RG-ANEXO-25] que leímos literal en rg_dump.txt: aunque 5,7 en RG-ART-048 es Distinción Máxima, "
            "la unidad [RG-ANEXO-25] dice textualmente: 'Aprobación: 75 en escala de 1 a 100 equivale a 5,7 en escala de 1,0 a 7,0. Concepto en el título o grado: Aprobado con Distinción'! "
            "Debo reproducir fielmente lo que dice [RG-ANEXO-25]."
        ),
        "respuesta": (
            "En el Anexo, 25 puntos en reprobación equivalen a 2,4 en escala 1,0 a 7,0, mientras 75 puntos en aprobación equivalen a 5,7 "
            "con el concepto consignado de 'Aprobado con Distinción' [RG-ANEXO-25]."
        ),
        "condiciones": (
            "Equivalencia literal indicada en la fila correspondiente del Anexo de escalas de notas [RG-ANEXO-25]."
        ),
        "fuente": "[RG-ANEXO-25]",
    },
    {
        "id": "B4-T27",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un egresado de Ingeniería Civil obtuvo 6,0 de promedio ponderado en su Plan de Estudio (sin Memoria) y 5,0 en su Memoria de Título. Calcula su nota de titulación y su concepto.",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-030", "RG-ART-048"],
        "distractores": ["RI-FI-ART-029", "RG-ART-023", "RG-ART-024", "RG-ART-049"],
        "pensar": (
            "0,6 × 6,0 + 0,4 × 5,0 = 3,60 + 2,00 = 5,6. En [RG-ART-048], 5,6 corresponde a 'Aprobado con Distinción' (5,0 - 5,6)."
        ),
        "respuesta": (
            "Su nota de titulación es 5,6 [RI-FI-ART-030] y su Diploma llevará el concepto 'Aprobado con Distinción' [RG-ART-048]."
        ),
        "condiciones": (
            "Cálculo: (0,60 × 6,0) + (0,40 × 5,0) = 3,60 + 2,00 = 5,6 [RI-FI-ART-030]; el rango 5,0–5,6 recibe Aprobado con Distinción [RG-ART-048]."
        ),
        "fuente": "[RG-ART-048] [RI-FI-ART-030]",
    },
    {
        "id": "B4-T28",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si hay conflicto normativo entre un Reglamento Interno de Facultad, el Reglamento General de Docencia de Pregrado y los Estatutos o normas no conciliables citadas en el Artículo 60, ¿qué orden jerárquico rige?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-060", "RI-FI-ART-034", "RI-FI-ART-002"],
        "distractores": ["RG-ART-001", "RG-TRANS-002", "RI-FI-ART-035"],
        "pensar": (
            "[RG-ART-060]: las normas del Reglamento General prevalecen sobre cualesquiera otras inconciliables, sin importar de dónde provengan. "
            "[RI-FI-ART-034]: si disposiciones del Reglamento Interno de Ingeniería no se concilian con el Reglamento General o las Normas de Ingreso, "
            "prevalecen siempre el Reglamento General y las Normas de Ingreso."
        ),
        "respuesta": (
            "Prevalece en primer lugar el Reglamento General de Docencia de Pregrado (junto con las Normas de Ingreso respecto del Reglamento "
            "Interno de Ingeniería) sobre cualquier otra disposición que no se concilie con él [RG-ART-060] [RI-FI-ART-034]."
        ),
        "condiciones": (
            "El Reglamento Interno de Docencia de Pregrado de Ingeniería tiene carácter complementario respecto de esas normas universitarias superiores [RI-FI-ART-002]."
        ),
        "fuente": "[RG-ART-060] [RI-FI-ART-002] [RI-FI-ART-034]",
    },
    {
        "id": "B4-T29",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un estudiante de Ingeniería en su quinto semestre tiene asignaturas que suman 14 semanas de semestre en el calendario vs ¿cuántos días dura la suspensión de actividades docentes de septiembre 2026 (14 al 17 de septiembre)?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S2-06", "CAL-2026-S2-09"],
        "distractores": ["CAL-2026-S2-07", "CAL-2026-S1-07", "CAL-2026-S2-08", "CAL-2026-S2-10"],
        "pensar": (
            "[CAL-2026-S2-06]: Suspensión de actividades de docencia de pregrado 14 - 17 de septiembre = 17 - 14 + 1 = 4 días (lunes 14 a jueves 17), "
            "seguido del feriado nacional viernes 18 de septiembre ([CAL-2026-S2-09]). No se asume 14 semanas porque [CAL-2026-S2-06] solo da 14–17 de septiembre."
        ),
        "respuesta": (
            "La suspensión de actividades de docencia de pregrado (14 al 17 de septiembre de 2026) dura 4 días inclusive (diferencia de 3 días), "
            "empalmando con el feriado nacional del viernes 18 de septiembre [CAL-2026-S2-06] [CAL-2026-S2-09]."
        ),
        "condiciones": (
            "Cálculo: del 14 al 17 de septiembre son 17 − 14 + 1 = 4 días de suspensión académica en el segundo semestre 2026 [CAL-2026-S2-06]."
        ),
        "fuente": "[CAL-2026-S2-06] [CAL-2026-S2-09]",
    },
    {
        "id": "B4-T30",
        "bloque": "calculos_y_orden",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Si un estudiante postula por cambio de carrera desde otra Facultad hacia Ingeniería con un promedio ponderado de 4,48 y luego solicita convalidar una asignatura aprobada en su origen con nota 4,45, ¿cumple los requisitos numéricos mínimos en ambos trámites considerando la escala de notas?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-017", "RI-FI-ART-021", "RG-ART-023"],
        "distractores": ["RI-FI-ART-018", "RI-FI-ART-020", "RG-ART-055"],
        "pensar": (
            "[RI-FI-ART-017]: cambio desde otra Facultad UdeC exige promedio ponderado mínimo equivalente a 4,5 en escala 1 a 7. "
            "[RI-FI-ART-021]: convalidar exige calificación mínima equivalente a 4,5 en escala 1 a 7. "
            "En escala oficial ([RG-ART-023]), si una nota viene a dos decimales y se aproxima a un decimal (centésima >= 5 sube): 4,48 -> 4,5 (cumple si está expresada a un decimal), "
            "y 4,45 -> 4,5; sin embargo, si se comparan directamente sin aproximar (4,48 < 4,5 y 4,45 < 4,5), estarían bajo 4,5. Indicar la regla literal de ambos!"
        ),
        "respuesta": (
            "Sin aproximación a un decimal, ni 4,48 ni 4,45 alcanzan el mínimo de 4,5 exigido tanto para ingresar desde otra Facultad [RI-FI-ART-017] "
            "como para convalidar asignaturas [RI-FI-ART-021]; sin embargo, expresadas en la escala oficial de un decimal conforme a la regla de "
            "aproximación de centésimas iguales o superiores a 5, tanto 4,48 como 4,45 aproximan a 4,5 [RG-ART-023]."
        ),
        "condiciones": (
            "La nota oficial se expresa con un decimal de aproximación (centésimas >= 5 suben a la décima superior) [RG-ART-023]; además, "
            "la convalidación solo procede para estudiantes de especialidad sobre asignaturas no reprobadas en el plan [RI-FI-ART-021]."
        ),
        "fuente": "[RG-ART-023] [RI-FI-ART-017] [RI-FI-ART-021]",
    },

    # ---- VAL BLOQUE 4 (5 ejemplos) ----
    {
        "id": "B4-V01",
        "bloque": "calculos_y_orden",
        "split": "val",
        "modo": "numerica",
        "pregunta": "Un estudiante de Ingeniería Civil obtuvo promedio ponderado de su Plan de Estudio (sin Memoria) de 5,5 y calificación 6,0 en su Memoria de Título. Calcula su nota de titulación exacta y qué concepto correspondería en su Diploma.",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-030", "RG-ART-048"],
        "distractores": ["RI-FI-ART-029", "RG-ART-023", "RG-ART-024", "RG-ART-047"],
        "pensar": (
            "[RI-FI-ART-030]: 0,6 × 5,5 + 0,4 × 6,0 = 3,30 + 2,40 = 5,70 = 5,7. "
            "[RG-ART-048]: 5,7 cae en 5,7–7,0 -> 'Aprobado con Distinción Máxima'."
        ),
        "respuesta": (
            "Su nota de titulación es 5,7 [RI-FI-ART-030] y en su Diploma de Título Profesional corresponderá el concepto 'Aprobado con Distinción Máxima' [RG-ART-048]."
        ),
        "condiciones": (
            "Cálculo: (0,60 × 5,5) + (0,40 × 6,0) = 3,30 + 2,40 = 5,7 [RI-FI-ART-030]; el tramo 5,7–7,0 recibe Aprobado con Distinción Máxima [RG-ART-048]."
        ),
        "fuente": "[RG-ART-048] [RI-FI-ART-030]",
    },
    {
        "id": "B4-V02",
        "bloque": "calculos_y_orden",
        "split": "val",
        "modo": "numerica",
        "pregunta": "¿Cuántos días corridos de diferencia hay entre el término de clases de las asignaturas semestrales del primer semestre y el inicio de clases del segundo semestre de 2026?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S1-04", "CAL-2026-S2-02"],
        "distractores": ["CAL-2026-S1-05", "CAL-2026-S2-01", "CAL-2026-S1-06", "CAL-2026-S1-14"],
        "pensar": (
            "[CAL-2026-S1-04]: 10 de julio. [CAL-2026-S2-02]: 10 de agosto. Como julio tiene 31 días: (31 − 10) + 10 = 21 + 10 = 31 días."
        ),
        "respuesta": (
            "Hay exactamente 31 días corridos entre el término de clases semestrales del primer semestre (10 de julio) y el inicio de clases del segundo semestre (10 de agosto) [CAL-2026-S1-04] [CAL-2026-S2-02]."
        ),
        "condiciones": (
            "Cálculo: días restantes de julio (31 − 10 = 21) + 10 días de agosto = 31 días [CAL-2026-S1-04] [CAL-2026-S2-02]."
        ),
        "fuente": "[CAL-2026-S1-04] [CAL-2026-S2-02]",
    },
    {
        "id": "B4-V03",
        "bloque": "calculos_y_orden",
        "split": "val",
        "modo": "numerica",
        "pregunta": "En la escala del Anexo, ¿qué nota en escala 1,0 a 7,0 se obtiene con 10 puntos de reprobación y qué nota y concepto se obtienen con 60 puntos de aprobación?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ANEXO-10"],
        "distractores": ["RG-ANEXO-09", "RG-ANEXO-11", "RG-ART-023", "RG-ART-048", "RG-ANEXO-01"],
        "pensar": (
            "[RG-ANEXO-10]: Reprobación 10 -> 1,5; Aprobación 60 -> 4,5, Concepto 'Aprobado por Unanimidad'."
        ),
        "respuesta": (
            "Según el Anexo, 10 puntos en reprobación equivalen a 1,5 en escala 1,0 a 7,0, y 60 puntos en aprobación equivalen a 4,5 con concepto 'Aprobado por Unanimidad' [RG-ANEXO-10]."
        ),
        "condiciones": (
            "Equivalencia directa consignada en el Anexo de escalas de notas del Reglamento General [RG-ANEXO-10]."
        ),
        "fuente": "[RG-ANEXO-10]",
    },
    {
        "id": "B4-V04",
        "bloque": "calculos_y_orden",
        "split": "val",
        "modo": "numerica",
        "pregunta": "Dos candidatos en Ingreso Común compiten por el último cupo: el postulante X tiene 28 créditos aprobados con promedio curricular 6,15 en asignaturas obligatorias del Plan Común y 6,80 en un electivo; el postulante Y tiene 28 créditos aprobados con promedio curricular 6,22 en las obligatorias del Plan Común y sin electivos. ¿Quién obtiene el cupo y por qué?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-005"],
        "distractores": ["RI-FI-ART-006", "RG-ART-024", "RI-FI-ART-003", "RI-FI-ART-004", "RG-ART-003-DEF-09"],
        "pensar": (
            "[RI-FI-ART-005]: 1° igual número de créditos aprobados (28 == 28); 2° desempate por promedio curricular de asignaturas del "
            "Plan Común de Primer Año (2 decimales), y 'Para el proceso de postulación sólo se considerarán las asignaturas obligatorias de Primer Año'. "
            "Luego el electivo 6,80 de X NO cuenta; gana Y porque 6,22 > 6,15."
        ),
        "respuesta": (
            "Obtiene el cupo el postulante Y, porque están empatados en créditos aprobados (28 = 28) y en el desempate solo se consideran las "
            "asignaturas obligatorias de Primer Año, donde Y tiene mayor promedio curricular (6,22 frente a 6,15 de X) sin contar el electivo [RI-FI-ART-005]."
        ),
        "condiciones": (
            "La selección considera además las preferencias postuladas y los cupos por carrera; el promedio del Plan Común incluye asignaturas "
            "obligatorias aprobadas y reprobadas expresado con dos decimales [RI-FI-ART-005]."
        ),
        "fuente": "[RI-FI-ART-005]",
    },
    {
        "id": "B4-V05",
        "bloque": "calculos_y_orden",
        "split": "val",
        "modo": "numerica",
        "pregunta": "Un curso de 10 créditos transferibles (SCT) equivale exactamente a cuántas horas de trabajo académico total según el Reglamento General, y qué diferencia hay frente a un crédito UdeC de clase práctica semanal?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-08", "RG-ART-003-DEF-07"],
        "distractores": ["RG-ART-003-DEF-06", "RG-ART-017", "RG-ART-003-DEF-12", "RG-ART-003-DEF-11"],
        "pensar": (
            "[RG-ART-003-DEF-08]: 1 SCT = 27 horas -> 10 × 27 = 270 horas (presencial y no presencial). "
            "[RG-ART-003-DEF-07]: un crédito UdeC corresponde a 1 hora docente de clase teórica o a 2 a 3 horas docentes de prácticas, laboratorios o seminarios semanales durante un semestre lectivo ordinario."
        ),
        "respuesta": (
            "Un curso de 10 SCT equivale a 270 horas totales de trabajo presencial y no presencial [RG-ART-003-DEF-08]; en contraste, un crédito "
            "UdeC mide horas docentes semanales por semestre y equivale a una hora docente teórica o a dos o tres horas docentes de prácticas, laboratorios o seminarios [RG-ART-003-DEF-07]."
        ),
        "condiciones": (
            "Cálculo: 10 SCT × 27 horas = 270 horas [RG-ART-003-DEF-08]; los créditos de asignaturas de duración distinta a un semestre se determinan proporcionalmente en números enteros [RG-ART-003-DEF-07]."
        ),
        "fuente": "[RG-ART-003-DEF-07] [RG-ART-003-DEF-08]",
    },
]
