"""Bloque 5 (resiliencia_feedback: 25 train / 5 val) y Bloque 6 (abstencion_honesta: 25 train / 5 val)."""

from __future__ import annotations

from typing import Any

BLOQUE_5_RESILIENCIA_FEEDBACK: list[dict[str, Any]] = [
    # ---- TRAIN (25 ejemplos): subgrupos A (citas), B (calculo bajo duda), C (excepciones / honestidad) ----
    # Subgrupo A: conservar citas previas y completar citas faltantes sin borrar las validas (10 train)
    {
        "id": "B5-T01",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué documentos debe presentar un estudiante de Ingeniería que desea suspender estudios y hasta cuándo puede hacerlo?",
        "feedback": (
            "El borrador menciona el plazo de cuatro semanas antes del término del período lectivo citando solo [RI-FI-ART-025], "
            "pero ese plazo no aparece en [RI-FI-ART-025] sino en otra unidad de la evidencia."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-025", "RG-ART-031"],
        "distractores": ["RG-ART-035", "RI-FI-ART-027", "CAL-2026-S1-03", "RG-ART-033"],
        "pensar": (
            "Observación del verificador: el borrador anterior citó solo [RI-FI-ART-025], pero las 4 semanas antes del fin del "
            "período lectivo están en [RG-ART-031]. Al corregir, NO debo eliminar [RI-FI-ART-025] (donde están la Vicedecanatura "
            "y los certificados a y b), sino conservar [RI-FI-ART-025] y agregar [RG-ART-031]."
        ),
        "respuesta": (
            "Debe presentar la solicitud a la Vicedecanatura junto con los certificados de la División de Asistencia Financiera al "
            "Estudiante (DAFE) y de la Dirección de Bibliotecas [RI-FI-ART-025], dentro del plazo máximo de hasta cuatro semanas antes "
            "del término del período lectivo respectivo [RG-ART-031]."
        ),
        "condiciones": (
            "Además debe acompañar antecedentes oficiales que justifiquen la suspensión (como informe de DISE) [RG-ART-031]; el "
            "certificado DAFE debe acreditar ausencia o debida garantía de deudas de aranceles y préstamos y el de Bibliotecas no "
            "adeudar material bibliográfico [RI-FI-ART-025]."
        ),
        "fuente": "[RG-ART-031] [RI-FI-ART-025]",
    },
    {
        "id": "B5-T02",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué instancia resuelve en última instancia una solicitud de continuación de estudios dentro de Ingeniería y cuántas oportunidades totales contempla el Reglamento General para Baja Académica?",
        "feedback": (
            "El borrador anterior cita definiciones irrelevantes ([RG-ART-003-DEF-14]) y omite citar la norma del Reglamento General "
            "que establece el límite de tres oportunidades y el recurso ante el Vicerrector."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-016", "RG-ART-030"],
        "distractores": ["RG-ART-003-DEF-14", "RI-FI-ART-033", "RI-FI-ART-014", "RG-ART-028"],
        "pensar": (
            "Debo quitar la cita innecesaria [RG-ART-003-DEF-14], mantener [RI-FI-ART-016] para la última instancia dentro de la Facultad "
            "(Decanatura) y añadir [RG-ART-030] que respalda las 3 oportunidades dentro de 1 año y el recurso por gracia al Vicerrector."
        ),
        "respuesta": (
            "Dentro de la Facultad de Ingeniería la Decanatura resuelve en última instancia [RI-FI-ART-016]; en cuanto a oportunidades, "
            "el Reglamento General contempla solamente tres solicitudes en Baja Académica dentro del plazo máximo de un año (1ª Comité, "
            "2ª Vicedecano, 3ª Decano), además de un recurso excepcional por gracia ante el Vicerrector [RG-ART-030]."
        ),
        "condiciones": (
            "La primera y segunda instancia tienen apelación dentro de cinco días hábiles y el recurso excepcional ante el Vicerrector procede por única vez [RG-ART-030] [RI-FI-ART-016]."
        ),
        "fuente": "[RG-ART-030] [RI-FI-ART-016]",
    },
    {
        "id": "B5-T03",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿En qué casos se excluye la reprobación en el PLEV de afectar las becas o causales de baja, y qué exige cursar una asignatura en el PLEV?",
        "feedback": (
            "El borrador menciona el límite de una asignatura y la aprobación del Jefe de Carrera, pero cita solamente [RI-FI-ART-014] "
            "y omite la fuente que regula la inscripción en el PLEV y sus efectos sobre becas."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-045", "RI-FI-ART-014"],
        "distractores": ["RG-ART-028", "RG-ART-043", "RG-ART-016", "RG-ART-023"],
        "pensar": (
            "Conservo [RI-FI-ART-014] en cuanto al efecto sobre la baja por segunda reprobación (cuando se aprueba en el PLEV del mismo "
            "año académico) y agrego [RG-ART-045] que contiene el límite de una asignatura, la aprobación del Jefe de Carrera y la inocuidad de una reprobación en PLEV sobre beneficios como becas."
        ),
        "respuesta": (
            "Para cursar en el PLEV se debe ser alumno regular, contar con aprobación del Jefe de Carrera y solo puede cursarse una asignatura "
            "por período; reprobarla en el PLEV no afecta la situación curricular ni antecedentes para becas o préstamos, aunque queda en la "
            "hoja curricular [RG-ART-045]. Por su parte, aprobar en el PLEV del mismo año académico una asignatura obligatoria reprobada por segunda vez evita la Baja Académica [RI-FI-ART-014]."
        ),
        "condiciones": (
            "El PLEV es opcional y requiere además alcanzar el mínimo de inscritos fijado por la Facultad [RG-ART-045]."
        ),
        "fuente": "[RG-ART-045] [RI-FI-ART-014]",
    },
    {
        "id": "B5-T04",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué organismo evalúa las causas médicas de suspensión y ante quién se tramita la solicitud de suspensión o reincorporación por salud incompatible?",
        "feedback": (
            "Falta respaldar quién certifica la situación de salud en Chillán y Los Ángeles; no elimines la cita de la autoridad que resuelve."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-059", "RG-ART-032", "RG-ART-033"],
        "distractores": ["RI-FI-ART-025", "RI-FI-ART-027", "RG-ART-036"],
        "pensar": (
            "Mantengo [RG-ART-032] y [RG-ART-033] (Decano resuelve tanto la suspensión por salud incompatible como la reincorporación con "
            "antecedentes de cese de impedimentos) y sumo [RG-ART-059] que establece expresamente la certificación por DISE o la unidad equivalente en Chillán y Los Ángeles."
        ),
        "respuesta": (
            "Toda situación de salud debe ser evaluada y certificada por la Dirección de Servicios Estudiantiles o la unidad equivalente en "
            "Chillán y Los Ángeles [RG-ART-059]. Tanto la suspensión por salud o condición física incompatible [RG-ART-032] como la reincorporación "
            "posterior tras acreditar que cesaron los impedimentos [RG-ART-033] son resueltas por el Decano de la Facultad."
        ),
        "condiciones": (
            "La resolución inicial del Decano se informa al Vicerrector y a UDARAE para registro en SAC [RG-ART-032], y la reincorporación debe "
            "pedirse dentro del máximo de tres años calendario [RG-ART-033]."
        ),
        "fuente": "[RG-ART-032] [RG-ART-033] [RG-ART-059]",
    },
    {
        "id": "B5-T05",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué calificación mínima en escala 1 a 7 y qué documentación se requieren para convalidar en Ingeniería, y cuánto plazo tiene el Vicedecano para resolver?",
        "feedback": (
            "El borrador menciona los 15 días de resolución, pero cita solamente [RI-FI-ART-021], donde no aparece ese plazo de 15 días."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-021", "RG-ART-037"],
        "distractores": ["RI-FI-ART-020", "RI-FI-ART-022", "RG-ART-041", "RI-FI-ART-023"],
        "pensar": (
            "Conservo [RI-FI-ART-021] (nota mínima 4,5, certificado de calificaciones y programas acreditados, restricción de especialidad y no reprobada) "
            "y agrego [RG-ART-037] (plazo de 15 días del Vicedecano previo informe del Departamento, y exención de programas si es de la misma UdeC)."
        ),
        "respuesta": (
            "En Ingeniería se exige nota mínima equivalente a 4,5 en escala 1 a 7 junto con certificado de calificaciones y programas debidamente "
            "acreditados [RI-FI-ART-021]; el Vicedecano debe resolver dentro de un plazo de 15 días previo informe del Departamento a cargo de la asignatura [RG-ART-037]."
        ),
        "condiciones": (
            "Solo aplica a estudiantes de especialidad respecto de asignaturas no reprobadas previamente en el Plan de Estudio [RI-FI-ART-021], "
            "y no exige programas si se trata de asignaturas aprobadas dentro de la misma Universidad de Concepción [RG-ART-037]."
        ),
        "fuente": "[RG-ART-037] [RI-FI-ART-021]",
    },
    {
        "id": "B5-T06",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si un estudiante modifica su inscripción de asignaturas dentro de plazo en el segundo semestre de 2026, ¿hasta cuándo puede hacerlo y qué asignaturas no puede borrar?",
        "feedback": (
            "El borrador menciona la fecha 04 de septiembre, pero omite citar la unidad del Calendario 2026 y confunde los artículos de prioridades."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S2-03", "RI-FI-ART-009", "RI-FI-ART-007"],
        "distractores": ["CAL-2026-S2-01", "RI-FI-ART-008", "RG-ART-043"],
        "pensar": (
            "Necesito las tres fuentes precisas presentes en el top-6: fecha 04 de septiembre en [CAL-2026-S2-03], prohibición de eliminar "
            "prioridades a) y b) en [RI-FI-ART-009] y definición exacta de a) atrasadas y b) obligatorias reprobadas anteriormente en [RI-FI-ART-007]."
        ),
        "respuesta": (
            "En el segundo semestre de 2026 puede modificar asignaturas hasta el 04 de septiembre [CAL-2026-S2-03], pero no puede eliminar las "
            "asignaturas de prioridad a) (atrasadas respecto de su nivel de avance) ni de prioridad b) (obligatorias reprobadas anteriormente y aún no aprobadas) [RI-FI-ART-007] [RI-FI-ART-009]."
        ),
        "condiciones": (
            "Tampoco puede contravenir al modificar el mínimo de créditos establecido en el Art. 8° [RI-FI-ART-009]."
        ),
        "fuente": "[CAL-2026-S2-03] [RI-FI-ART-007] [RI-FI-ART-009]",
    },
    {
        "id": "B5-T07",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué diferencia hay entre convalidar/revalidar versus validar en intercambio respecto de su sigla y cómputo como carga académica en SAC?",
        "feedback": (
            "El borrador anterior atribuyó las siglas CON, REV, VAL y el cómputo de carga únicamente a [RI-FI-ART-024], donde no figuran CON ni REV."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-041", "RI-FI-ART-024", "RG-ART-039"],
        "distractores": ["RG-ART-037", "RG-ART-040", "RI-FI-ART-015"],
        "pensar": (
            "Debo conservar [RI-FI-ART-024] (y [RG-ART-039] si se cita) para el reconocimiento de carga académica de asignaturas validadas en "
            "intercambio y añadir [RG-ART-041] para las siglas VAL/CON/REV/HOM/REC y la exclusión de carga académica de CON, REV, HOM y REC."
        ),
        "respuesta": (
            "En el SAC se registran con sigla VAL (validadas), CON (convalidadas), REV (revalidadas), HOM (homologadas) y REC (reconocidas); "
            "mientras las asignaturas validadas por intercambio (VAL) sí se reconocen como carga académica del semestre en que se cursaron "
            "[RG-ART-039] [RI-FI-ART-024], las asignaturas CON, REV, HOM y REC no cuentan como carga académica del semestre [RG-ART-041]."
        ),
        "condiciones": (
            "Todas deben quedar registradas en el SAC con su Nota Final (incorporada en Escala Oficial UdeC para intercambio) [RG-ART-039] [RG-ART-041] [RI-FI-ART-024]."
        ),
        "fuente": "[RG-ART-039] [RG-ART-041] [RI-FI-ART-024]",
    },
    {
        "id": "B5-T08",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué reglas rigen la entrega y revisión de evaluaciones escritas en una Facultad y qué autoridad interviene si se filtra una prueba?",
        "feedback": (
            "El borrador respondió sobre la Comisión de Evaluación, pero omitió citar el artículo de entrega y apelación de evaluaciones y perdió esa información."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-025", "RG-ART-013"],
        "distractores": ["RG-ART-012", "RG-ART-026", "RI-FI-ART-010", "RG-ART-027"],
        "pensar": (
            "Conservo [RG-ART-013] para filtraciones (Director de Departamento convoca a Comisión de Evaluación e informa al Vicedecano) y "
            "completo todo lo de entrega/revisión/apelación desde [RG-ART-025]."
        ),
        "respuesta": (
            "El profesor debe entregar notas y pautas en máximo 10 días hábiles, otorgar 5 días hábiles para revisión (y conservar las pruebas "
            ">= 30 días hábiles tras el período); ante desacuerdo escrito dentro de 5 días hábiles, el Vicedecano puede nombrar una Comisión ad hoc "
            "que resuelve inapelablemente en 10 días corridos [RG-ART-025]. Si se filtra una evaluación o sus preguntas, el Director de Departamento "
            "convoca a la Comisión de Evaluación para que resuelva e informe al Vicedecano [RG-ART-013]."
        ),
        "condiciones": (
            "El Vicedecano puede ampliar por razones justificadas los plazos de entrega y revisión [RG-ART-025], y las reclamaciones por "
            "situaciones del Art. 13 también pueden elevarse ante el Vicedecano [RG-ART-013] [RG-ART-025]."
        ),
        "fuente": "[RG-ART-013] [RG-ART-025]",
    },
    {
        "id": "B5-T09",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Cuántos integrantes estudiantiles forman el Consejo de Carrera en Ingeniería y qué ocurre si uno falta injustificadamente dos sesiones seguidas?",
        "feedback": (
            "El borrador afirma que el representante estudiantil es reemplazado ante dos ausencias seguidas, pero solo cita [RI-FI-ART-032] donde no aparece esa sanción."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-032", "RG-ART-010"],
        "distractores": ["RG-ART-009", "RG-ART-011", "RI-FI-ART-033", "RG-ART-052"],
        "pensar": (
            "Mantengo [RI-FI-ART-032] (tres representantes estudiantiles elegidos por el Centro de Alumnos con voz y voto, por 1 año) y agrego [RG-ART-010] (reemplazo ante 2 ausencias injustificadas consecutivas)."
        ),
        "respuesta": (
            "En Ingeniería el Consejo de Carrera incluye tres representantes estudiantiles con voz y voto elegidos por el Centro de Alumnos, "
            "quienes duran un año en funciones [RI-FI-ART-032]; si un representante estudiantil incurre en dos ausencias consecutivas sin "
            "justificación, debe ser reemplazado [RG-ART-010]."
        ),
        "condiciones": (
            "Las sesiones ordinarias son al menos tres por semestre con quórum de asistencia mínima del 60 % de sus miembros [RG-ART-010]."
        ),
        "fuente": "[RG-ART-010] [RI-FI-ART-032]",
    },
    {
        "id": "B5-T10",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "cruce",
        "pregunta": "Si un estudiante desea presentar su renuncia irrevocable a la carrera de Ingeniería, ¿qué certificados adjunta y ante quién la entrega?",
        "feedback": (
            "Citaste [RI-FI-ART-025] y [RI-FI-ART-026] pero olvidaste respaldar el carácter irrevocable y la remisión a Dirección de Docencia del Reglamento General."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-026", "RI-FI-ART-025", "RG-ART-034"],
        "distractores": ["RG-ART-035", "RG-ART-031", "RG-ART-033"],
        "pensar": (
            "Mantengo [RI-FI-ART-026] y [RI-FI-ART-025] (solicitud escrita al Vicedecano + certificados DAFE y Bibliotecas de los incisos a y b) "
            "y agrego [RG-ART-034] (remisión a Dirección de Docencia y precisión de que no libera de obligaciones pendientes)."
        ),
        "respuesta": (
            "Debe entregarla por escrito ante la Vicedecanatura adjuntando los certificados DAFE y de Dirección de Bibliotecas señalados en el "
            "Art. 25 incisos a) y b); la renuncia es irrevocable e impide reincorporarse [RI-FI-ART-025] [RI-FI-ART-026], siendo remitida por el "
            "Vicedecano a la Dirección de Docencia para su registro [RG-ART-034]."
        ),
        "condiciones": (
            "La renuncia no libera al alumno de obligaciones que pueda tener pendientes con la Universidad [RG-ART-034]."
        ),
        "fuente": "[RG-ART-034] [RI-FI-ART-025] [RI-FI-ART-026]",
    },

    # Subgrupo B: Explicitar derivacion aritmetica o logica bajo duda del Verificador cuando los datos SI estan (8 train)
    {
        "id": "B5-T11",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un estudiante que cursó seis semestres en Ingeniería aprobó en total 54 créditos sin convalidaciones. ¿Está en situación de Baja Académica por el criterio de promedio de créditos?",
        "feedback": (
            "El borrador indica un promedio de 9,0 créditos, pero no muestra en la respuesta ni en condiciones cómo se obtuvo esa cifra a partir de la evidencia y la pregunta."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-014", "RG-ART-028"],
        "distractores": ["RI-FI-ART-015", "RG-ART-030", "RI-FI-ART-016", "RI-FI-ART-008"],
        "pensar": (
            "¡Cuidado! Es la trampa de H07: todos los datos están en la pregunta (54 créditos, 6 semestres) y la fórmula está en [RG-ART-028] a) "
            "(total créditos aprobados / semestres de permanencia) y umbral en [RI-FI-ART-014] b) (< 10 desde el 4° semestre). NO debo abstenerme: "
            "debo mostrar la operación paso a paso 54 / 6 = 9,0 < 10."
        ),
        "respuesta": (
            "Sí, está en situación de Baja Académica: 54 créditos aprobados divididos en 6 semestres de permanencia dan un promedio de 9,0 "
            "créditos por semestre, cifra inferior al mínimo de 10 créditos semestrales exigido a partir del cuarto semestre [RG-ART-028] [RI-FI-ART-014]."
        ),
        "condiciones": (
            "Cálculo explícito según la fórmula reglamentaria (créditos aprobados / semestres de permanencia): 54 / 6 = 9,0 créditos/semestre < 10,0; "
            "rige desde el cuarto semestre de permanencia en la carrera [RG-ART-028] [RI-FI-ART-014]."
        ),
        "fuente": "[RG-ART-028] [RI-FI-ART-014]",
    },
    {
        "id": "B5-T12",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Si un estudiante acumula 57 créditos aprobados al finalizar su sexto semestre de permanencia, ¿cumple con la exigencia semestral promedio del artículo 14 letra b) de Ingeniería?",
        "feedback": (
            "El borrador respondió que no alcanza el mínimo de 10 sin mostrar la división aritmética ni mencionar la regla de permanencia del Reglamento General."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-014", "RG-ART-028"],
        "distractores": ["RI-FI-ART-015", "RG-ART-030", "RI-FI-ART-008", "RI-FI-ART-016"],
        "pensar": (
            "Observación del verificador: falta explicitar la operación. El dato (57 créditos en 6 semestres de permanencia) está en la pregunta y la norma en "
            "[RG-ART-028] a) y [RI-FI-ART-014] b): desde el cuarto semestre el promedio mínimo es de 10 créditos por semestre. Calculo 57 / 6 = 9,5 < 10."
        ),
        "respuesta": (
            "No cumple: al dividir los 57 créditos aprobados entre sus 6 semestres de permanencia obtiene un promedio de 9,5 créditos por semestre, "
            "inferior al mínimo de 10 créditos semestrales exigido a partir del cuarto semestre, por lo que queda en situación de Baja Académica [RG-ART-028] [RI-FI-ART-014]."
        ),
        "condiciones": (
            "Operación: 57 créditos aprobados / 6 semestres = 9,5 créditos por semestre (< 10). La exigencia promedio rige a partir del cuarto semestre de permanencia [RG-ART-028] [RI-FI-ART-014]."
        ),
        "fuente": "[RG-ART-028] [RI-FI-ART-014]",
    },
    {
        "id": "B5-T13",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "numerica",
        "pregunta": "En una asignatura de Ingeniería con 30 clases teóricas cuyo programa exige el tope máximo permitido para ese tipo de sesiones (80 %), ¿cumple el requisito un estudiante que asistió a 23 clases?",
        "feedback": (
            "El borrador afirmó que sí aprueba por asistencia sin calcular el porcentaje real de 23 de 30 ni compararlo con el límite reglamentario del artículo 13."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-013"],
        "distractores": ["RI-FI-ART-011", "RI-FI-ART-012", "RG-ART-022", "RG-ART-023", "RG-ART-026"],
        "pensar": (
            "Según [RI-FI-ART-013], el Profesor Encargado puede exigir asistencia mínima de hasta un 80 % en clases teóricas y prácticas (y hasta 100 % en laboratorios, "
            "talleres, seminarios o salidas a terreno). Verifico las cifras: 80 % de 30 = 24 clases; 23 / 30 = 76,67 % (76,7 %). No alcanza las 24 sesiones requeridas."
        ),
        "respuesta": (
            "No cumple con el requisito mínimo: un 80 % sobre 30 clases teóricas exige asistir al menos a 24 sesiones, mientras que 23 clases corresponden a un 76,7 % de asistencia [RI-FI-ART-013]."
        ),
        "condiciones": (
            "Operación: 0,80 × 30 = 24 clases mínimas (23 / 30 = 76,7 % < 80 %). Para clases teóricas y prácticas la exigencia no puede superar el 80 %, pero puede llegar al 100 % en seminarios, laboratorios, talleres o salidas a terreno [RI-FI-ART-013]."
        ),
        "fuente": "[RI-FI-ART-013]",
    },
    {
        "id": "B5-T14",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "numerica",
        "pregunta": "En el segundo semestre 2026, ¿cuántos días corridos median entre el término de clases (11 de diciembre) y el fin de las Evaluaciones de Recuperación (23 de diciembre)?",
        "feedback": (
            "El borrador responde 12 días sin explicar la resta ni citar ambas unidades del calendario en la respuesta."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["CAL-2026-S2-04", "CAL-2026-S2-05"],
        "distractores": ["CAL-2026-S2-11", "CAL-2026-S2-03", "CAL-2026-S2-02", "CAL-2026-S1-06"],
        "pensar": (
            "Datos exactos en evidencia: [CAL-2026-S2-04] término de clases 11 de diciembre; [CAL-2026-S2-05] Evaluaciones de Recuperación 14–23 de diciembre. "
            "23 - 11 = 12 días corridos entre el término de clases y el último día de recuperación (y del 14 al 23 son 10 días de recuperación). "
            "Muestro la resta explícita 23 − 11 = 12."
        ),
        "respuesta": (
            "Median 12 días corridos desde el término de clases (11 de diciembre) hasta el cierre de las Evaluaciones de Recuperación (23 de diciembre) "
            "[CAL-2026-S2-04] [CAL-2026-S2-05]."
        ),
        "condiciones": (
            "Cálculo: 23 − 11 = 12 días (las Evaluaciones de Recuperación se desarrollan del 14 al 23 de diciembre) [CAL-2026-S2-04] [CAL-2026-S2-05]."
        ),
        "fuente": "[CAL-2026-S2-04] [CAL-2026-S2-05]",
    },
    {
        "id": "B5-T15",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un curso de formación complementaria de 27 créditos transferibles (SCT) equivale exactamente a cuántas horas de trabajo académico presencial y no presencial?",
        "feedback": (
            "El borrador indica 729 horas pero no detalla la multiplicación por la equivalencia reglamentaria de 1 SCT."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-08"],
        "distractores": ["RG-ART-003-DEF-12", "RG-ART-003-DEF-07", "RG-ART-003-DEF-06", "RG-ART-017", "RG-ART-056"],
        "pensar": (
            "[RG-ART-003-DEF-08]: 1 SCT = 27 horas de trabajo presencial y no presencial. 27 × 27 = 729 horas. Muestro 27 × 27 = 729."
        ),
        "respuesta": (
            "Un curso de 27 SCT equivale a 729 horas totales de trabajo presencial y no presencial [RG-ART-003-DEF-08]."
        ),
        "condiciones": (
            "Operación: cada crédito transferible (1 SCT) equivale a 27 horas [RG-ART-003-DEF-08], por lo tanto 27 × 27 = 729 horas."
        ),
        "fuente": "[RG-ART-003-DEF-08]",
    },
    {
        "id": "B5-T16",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "numerica",
        "pregunta": "En una carrera de un semestre con una asignatura de 4 créditos UdeC solo de clases teóricas, más 12 horas semanales de estudio autónomo indirecto, ¿cuántas horas semanales de Trabajo Académico representa esa asignatura?",
        "feedback": (
            "El borrador afirma 16 horas sin explicar la equivalencia entre créditos teóricos UdeC y horas docentes semanales ni citar la definición."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-003-DEF-07"],
        "distractores": ["RG-ART-003-DEF-06", "RG-ART-003-DEF-08", "RG-ART-017", "RG-ART-016", "RG-ART-003-DEF-09"],
        "pensar": (
            "[RG-ART-003-DEF-07]: 1 crédito = 1 hora docente de clase teórica semanal; Trabajo Académico = horas de docencia directa + "
            "horas de actividades indirectas o complementarias semanales. 4 + 12 = 16 horas semanales."
        ),
        "respuesta": (
            "Representa 16 horas semanales de Trabajo Académico (4 horas de docencia directa + 12 horas de trabajo indirecto) [RG-ART-003-DEF-07]."
        ),
        "condiciones": (
            "Operación: 4 créditos corresponden a 4 horas docentes semanales de clase teórica; sumadas las 12 horas indirectas se obtienen 4 + 12 = 16 horas semanales [RG-ART-003-DEF-07]."
        ),
        "fuente": "[RG-ART-003-DEF-07]",
    },
    {
        "id": "B5-T17",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Un estudiante aprobó 4 asignaturas con notas finales 5,1 (4 cr), 4,5 (4 cr), 3,8 (4 cr) y NCR (4 cr). ¿Cuál es su Promedio Curricular?",
        "feedback": (
            "El borrador dio 3,6 sin explicar qué nota reemplaza a NCR ni mostrar la suma ponderada y el divisor de créditos."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-024"],
        "distractores": ["RG-ART-023", "RG-ART-021", "RI-FI-ART-011", "RG-ART-027", "RG-ART-003-DEF-07"],
        "pensar": (
            "[RG-ART-024]: Promedio Curricular incluye todas las notas finales ponderadas por créditos, y NCR = 1,0. "
            "Suma = (5,1×4) + (4,5×4) + (3,8×4) + (1,0×4) = 20,4 + 18,0 + 15,2 + 4,0 = 57,6; total créditos = 16; 57,6 / 16 = 3,6."
        ),
        "respuesta": (
            "Su Promedio Curricular es exactamente 3,6 [RG-ART-024]."
        ),
        "condiciones": (
            "Operación: NCR equivale a 1,0 [RG-ART-024]; así, (5,1 × 4 + 4,5 × 4 + 3,8 × 4 + 1,0 × 4) / (4 + 4 + 4 + 4) = 57,6 / 16 = 3,6."
        ),
        "fuente": "[RG-ART-024]",
    },
    {
        "id": "B5-T18",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "numerica",
        "pregunta": "En un curso de 35 estudiantes que rindió un certamen, 17 obtuvieron nota inferior a 4,0. ¿Debe el Director de Departamento convocar obligatoriamente a la Comisión de Evaluación por la regla del 50 %?",
        "feedback": (
            "El borrador responde que no corresponde convocarla, pero no demuestra el porcentaje numérico calculado frente al umbral reglamentario."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-013"],
        "distractores": ["RG-ART-012", "RG-ART-023", "RG-ART-025", "RI-FI-ART-011", "RG-ART-006"],
        "pensar": (
            "[RG-ART-013]: se convoca 'cuando más del 50% los alumnos que rinden la evaluación obtienen nota inferior a 4.0'. "
            "17 / 35 = 0,4857... ≈ 48,6 %, que NO es mayor que 50 % (habrían sido necesarios 18 de 35 = 51,4 %). No se alcanza el umbral."
        ),
        "respuesta": (
            "No corresponde por esa causal: 17 de 35 equivale al 48,6 %, porcentaje que no supera el umbral de más del 50 % con nota inferior a 4,0 [RG-ART-013]."
        ),
        "condiciones": (
            "Operación: 17 / 35 = 48,57 % <= 50 % (la regla exige superar estrictamente el 50 %, salvo que exista otra situación anómala como filtración de preguntas) [RG-ART-013]."
        ),
        "fuente": "[RG-ART-013]",
    },

    # Subgrupo C: Completar excepciones omitidas o aceptar insuficiencia si falta evidencia en top-6 (7 train)
    {
        "id": "B5-T19",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Puede un estudiante eliminar durante el período de modificación de asignaturas una materia aprobada o cualquiera de su semestre anterior?",
        "feedback": (
            "El borrador indicó solo 'según las prioridades del artículo 7°', pero no enumeró explícitamente cuáles prioridades no pueden eliminarse ni el límite de créditos."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-009", "RI-FI-ART-007", "RI-FI-ART-008"],
        "distractores": ["RG-ART-042", "RG-ART-043", "CAL-2026-S1-03"],
        "pensar": (
            "Nunca aludir vagamente a 'prioridades del artículo 7°': enumero explícitamente qué es a) (asignaturas atrasadas respecto del nivel de avance) "
            "y qué es b) (asignaturas obligatorias reprobadas anteriormente y aún no aprobadas), más la prohibición de bajar de 8 créditos (y sus excepciones)."
        ),
        "respuesta": (
            "Durante la modificación puede agregar o eliminar asignaturas en las fechas del calendario, pero no puede eliminar asignaturas "
            "atrasadas respecto de su nivel de avance (prioridad a) ni asignaturas obligatorias reprobadas anteriormente y no aprobadas (prioridad b), "
            "ni quedar bajo el mínimo de ocho créditos [RI-FI-ART-007] [RI-FI-ART-008] [RI-FI-ART-009]."
        ),
        "condiciones": (
            "Solo se exceptúa del mínimo de ocho créditos a quien está terminando estudios o a quien por falta de requisitos no pueda completarlo [RI-FI-ART-008]."
        ),
        "fuente": "[RI-FI-ART-007] [RI-FI-ART-008] [RI-FI-ART-009]",
    },
    {
        "id": "B5-T20",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué ocurre si un estudiante con derecho a Evaluación de Recuperación falta por motivos graves a rendirla?",
        "feedback": (
            "El borrador dice 'se mantiene su Nota Final', omitiendo la excepción autorizada por el Vicedecano contemplada en la evidencia."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-022"],
        "distractores": ["RI-FI-ART-012", "RG-ART-026", "RG-ART-027", "RG-ART-023", "CAL-2026-S1-06"],
        "pensar": (
            "Agrego completa la excepción de [RG-ART-022]: salvo que el Vicedecano de la Facultad que dicta la asignatura autorice no "
            "presentarse por razones fundadas -> queda pendiente (PEN), nuevo plazo por resolución comunicada al Profesor Encargado y Jefe de Carrera."
        ),
        "respuesta": (
            "Por regla general mantiene su Nota Final, salvo que el Vicedecano de la Facultad que dicta la asignatura, por razones fundadas, "
            "autorice al alumno a no presentarse [RG-ART-022]."
        ),
        "condiciones": (
            "En ese caso excepcional queda con situación pendiente (consignándose PEN en el Acta de ser necesario) y dispone del plazo que "
            "establezca la resolución del Vicedecano, comunicada al Profesor Encargado y al Jefe de Carrera [RG-ART-022]."
        ),
        "fuente": "[RG-ART-022]",
    },
    {
        "id": "B5-T21",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "condicional",
        "pregunta": "Si un estudiante pierde la calidad de alumno por no inscribir asignaturas, ¿qué pasa si el alumno en realidad tenía inscrita una asignatura anual del período previo?",
        "feedback": (
            "El borrador afirmó que pierde automáticamente la carrera y luego citó la excepción al final; corrige la respuesta directa para no contradecirse."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-029"],
        "distractores": ["RG-ART-030", "RG-ART-050", "RG-ART-042", "RG-ART-018", "RI-FI-ART-008"],
        "pensar": (
            "Corrijo el error tipo H14: NO afirmar que pierde automáticamente si ya tiene una asignatura anual inscrita del período anterior! "
            "Debo comenzar directamente con 'No pierde... si en el período lectivo anterior inscribió una o más asignaturas anuales'."
        ),
        "respuesta": (
            "No pierde la calidad de alumno ni el derecho a continuar estudios si en el período lectivo anterior inscribió una o más asignaturas anuales [RG-ART-029]."
        ),
        "condiciones": (
            "La pérdida de la calidad de alumno de pregrado y del derecho a continuar estudios por no inscribir asignaturas estando habilitado "
            "solo ocurre cuando no se cumple dicha excepción de haber inscrito asignaturas anuales en el período lectivo anterior [RG-ART-029]."
        ),
        "fuente": "[RG-ART-029]",
    },
    {
        "id": "B5-T22",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "cruce",
        "pregunta": "Según el Calendario 2026 y el Reglamento General, ¿en qué fecha exacta comienza el PLEV de 2026 y cuántas semanas dura?",
        "feedback": (
            "El borrador inventó una fecha de enero para el PLEV que no aparece en ninguna unidad del calendario entregado. Verifica y abstente de esa fecha."
        ),
        "estado": "insuficiente",
        "evidencia_clave": ["RG-ART-016"],
        "distractores": ["RG-ART-045", "CAL-2026-S1-01", "CAL-2026-S1-02", "CAL-2026-S2-04", "CAL-2026-S2-05"],
        "pensar": (
            "Reviso las unidades: [RG-ART-016] sí indica la duración del PLEV ('un Período Lectivo Extraordinario de Verano (PLEV) de seis semanas'). "
            "Pero en las unidades del Calendario 2026 no existe ninguna fecha de inicio del PLEV! Por honestidad, respondo la duración citando [RG-ART-016] "
            "y declaro explícitamente que la fecha exacta de inicio del PLEV 2026 no consta en la evidencia consultada."
        ),
        "respuesta": (
            "Según el Reglamento General, el PLEV dura seis semanas [RG-ART-016]; sin embargo, no existe respaldo en la evidencia sobre la fecha "
            "exacta de inicio del PLEV en el Calendario 2026."
        ),
        "condiciones": (
            "La duración de seis semanas está fijada en el Reglamento General [RG-ART-016], mientras que la fecha de inicio concreta del PLEV 2026 "
            "no figura en los registros del calendario incluidos en la consulta."
        ),
        "fuente": "[RG-ART-016]",
    },
    {
        "id": "B5-T23",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿Cuál es la fecha exacta de término de envío de postulaciones a la Beca Articulación Pregrado-Postgrado en 2026?",
        "feedback": (
            "El borrador dedujo fechas de inscripción de asignaturas para la beca, pero la evidencia no contiene fechas de postulación a esa beca."
        ),
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-057", "CAL-2026-S1-01", "CAL-2026-S2-01", "CAL-2026-S1-04", "CAL-2026-S2-04"],
        "pensar": (
            "[RG-ART-057] solo indica que quien tenga Licenciatura y sea alumno regular puede ser aceptado simultáneamente en postgrado y recibir "
            "la Beca Articulación Pregrado-Postgrado a proposición de la Facultad. No trae ninguna fecha ni plazo límite de postulación para 2026. "
            "Debo abstenerme limpiamente."
        ),
        "respuesta": (
            "No existe información en la normativa consultada sobre la fecha límite de postulación en 2026 para la Beca Articulación Pregrado-Postgrado."
        ),
        "condiciones": (
            "La evidencia únicamente contempla la existencia de la beca para alumnos regulares con Grado de Licenciado aceptados simultáneamente en postgrado, sin fechas de convocatoria."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B5-T24",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿En qué casos se excluye del proceso de postulación de Ingreso Común a ciertas asignaturas y qué nota mínima o requisito de decimales rige el promedio curricular del desempate?",
        "feedback": (
            "El borrador resumió los criterios pero omitió la exclusión de asignaturas no obligatorias y la precisión de dos decimales e inclusión de reprobadas."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-005"],
        "distractores": ["RI-FI-ART-006", "RG-ART-024", "RG-ART-023", "RI-FI-ART-003", "RI-FI-ART-004"],
        "pensar": (
            "Agrego todas las condiciones exactas de [RI-FI-ART-005]: 1° créditos aprobados; 2° promedio curricular del Plan Común de Primer Año "
            "expresado con dos decimales (incluyendo asignaturas aprobadas y reprobadas); orden de preferencias y cupos; SOLO se consideran asignaturas obligatorias de Primer Año."
        ),
        "respuesta": (
            "Para la postulación de Ingreso Común solo se consideran las asignaturas obligatorias de Primer Año (excluyendo las demás); en igualdad "
            "de créditos aprobados, el promedio curricular de desempate se expresa con dos decimales ponderado por créditos e incluye tanto asignaturas aprobadas como reprobadas del Plan Común de Primer Año [RI-FI-ART-005]."
        ),
        "condiciones": (
            "La selección respeta orden estricto: primero créditos aprobados, luego promedio curricular con dos decimales, considerando orden de preferencias y cupos por carrera [RI-FI-ART-005]."
        ),
        "fuente": "[RI-FI-ART-005]",
    },
    {
        "id": "B5-T25",
        "bloque": "resiliencia_feedback",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué condiciones aplican cuando un alumno quiere inscribir asignaturas que requieren cumplimiento de prerrequisitos y además desea tomar dos cursos que coinciden el mismo día y hora?",
        "feedback": (
            "El borrador respondió solo sobre el choque horario y omitió las consecuencias de incumplir prerrequisitos y de no haber respondido la Encuesta Docente."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-042", "RG-ART-014"],
        "distractores": ["RI-FI-ART-007", "RI-FI-ART-008", "RG-ART-007", "RG-ART-003-DEF-13"],
        "pensar": (
            "[RG-ART-042] cubre todo lo de inscripción: cumplir prerrequisitos (de lo contrario la inscripción queda sin efecto), haber respondido "
            "Encuesta Docente del período anterior, y no inscribir asignaturas con actividades obligatorias programadas en horarios coincidentes. "
            "[RG-ART-014] además regula el caso excepcional posterior donde por razones justificadas se programan actividades simultáneas."
        ),
        "respuesta": (
            "No puede inscribir asignaturas que tengan actividades obligatorias programadas en horarios coincidentes, y si incumple los "
            "prerrequisitos exigidos la inscripción queda sin efecto [RG-ART-042]."
        ),
        "condiciones": (
            "Además debe haber respondido la Encuesta de Evaluación Docente del período lectivo anterior [RG-ART-042]; si ya inscritas las "
            "asignaturas se programaran por razones justificadas actividades simultáneas, debe priorizar la no recuperable y recuperar la otra [RG-ART-014]."
        ),
        "fuente": "[RG-ART-014] [RG-ART-042]",
    },

    # ---- VAL BLOQUE 5 (5 ejemplos) ----
    {
        "id": "B5-V01",
        "bloque": "resiliencia_feedback",
        "split": "val",
        "modo": "cruce",
        "pregunta": "¿Quién debe resguardar la coordinación de horarios y aulas centralizadas en Concepción y qué plazo o condición tiene un profesor para entregar notas y responder dudas?",
        "feedback": (
            "El borrador anterior mencionó los 10 días hábiles de entrega de notas citando únicamente [RG-ART-014], donde ese plazo no aparece."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-014", "RG-ART-025"],
        "distractores": ["RG-ART-005", "RG-ART-006", "RG-ART-012", "RI-FI-ART-010"],
        "pensar": (
            "Conservo [RG-ART-014] para coordinación de horarios y aulas centralizadas por Dirección de Docencia (y aviso previo del Secretario Académico) "
            "y agrego [RG-ART-025] para los plazos de entrega de notas y pautas (10 días hábiles) y revisión ante el profesor (5 días hábiles)."
        ),
        "respuesta": (
            "La utilización de aulas de uso centralizado es responsabilidad de la Dirección de Docencia (en Chillán y Los Ángeles del Director "
            "General respectivo), previa información del Secretario Académico sobre aulas de cada Facultad [RG-ART-014]; en cuanto a evaluaciones, "
            "el profesor tiene máximo 10 días hábiles para informar notas y pautas y los alumnos 5 días hábiles para aclarar dudas y revisarlas [RG-ART-025]."
        ),
        "condiciones": (
            "El Vicedecano puede ampliar dichos plazos de entrega y revisión por razones justificadas [RG-ART-025]."
        ),
        "fuente": "[RG-ART-014] [RG-ART-025]",
    },
    {
        "id": "B5-V02",
        "bloque": "resiliencia_feedback",
        "split": "val",
        "modo": "cruce",
        "pregunta": "¿Qué organismo evalúa el cumplimiento del Plan de Estudio de una carrera y quién preside e integra dicho Consejo en la Facultad de Ingeniería?",
        "feedback": (
            "El borrador omitió citar el artículo del Reglamento General que enumera la atribución de evaluar el cumplimiento del Plan de Estudios."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-010", "RI-FI-ART-032"],
        "distractores": ["RG-ART-009", "RG-ART-008", "RG-ART-011", "RI-FI-ART-033"],
        "pensar": (
            "Mantengo [RI-FI-ART-032] (composición e integración en Ingeniería presidida por la Jefatura de Carrera) y sumo [RG-ART-010] letra a) "
            "(función específica de evaluar el cumplimiento del Plan de Estudios de la carrera)."
        ),
        "respuesta": (
            "Corresponde al Consejo de Carrera evaluar el cumplimiento del Plan de Estudios [RG-ART-010]; en Ingeniería este Consejo es presidido "
            "por la Jefatura de Carrera y se integra por al menos 6 docentes adscritos del Departamento (plazo indefinido y media jornada o superior), "
            "1 o 2 docentes de otros Departamentos de la Facultad, 3 representantes estudiantiles y 2 académicos de otras Facultades [RI-FI-ART-032]."
        ),
        "condiciones": (
            "Los integrantes docentes duran dos años y los representantes estudiantiles un año [RI-FI-ART-032]; el Consejo sesiona al menos tres veces cada semestre [RG-ART-010]."
        ),
        "fuente": "[RG-ART-010] [RI-FI-ART-032]",
    },
    {
        "id": "B5-V03",
        "bloque": "resiliencia_feedback",
        "split": "val",
        "modo": "numerica",
        "pregunta": "Si un estudiante ingresa directamente a un nivel superior con 12 créditos convalidados y al término de su cuarto semestre suma 56 créditos totales registrados (incluyendo esos 12), ¿cumple el promedio de créditos exigido por el Artículo 14 b)?",
        "feedback": (
            "El borrador indicó '11 créditos por semestre' sin explicitar la resta de créditos convalidados ni la división por 4 semestres."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RI-FI-ART-015", "RI-FI-ART-014", "RG-ART-028"],
        "distractores": ["RG-ART-041", "RI-FI-ART-021", "RG-ART-030"],
        "pensar": (
            "Operación: 56 - 12 = 44 créditos válidos ([RI-FI-ART-015] excluye convalidados). Dividido por 4 semestres ([RG-ART-028] a): 44 / 4 = 11,0 >= 10 ([RI-FI-ART-014] b). "
            "¡El resultado numérico 11,0 es correcto incluso restando los 12 convalidados, porque 44/4 = 11! Debo mostrar ambos pasos."
        ),
        "respuesta": (
            "Sí cumple: descontados los 12 créditos convalidados, registra 44 créditos computables en 4 semestres, equivalentes a un promedio de 11,0 créditos por semestre, superior al mínimo de 10 [RG-ART-028] [RI-FI-ART-014] [RI-FI-ART-015]."
        ),
        "condiciones": (
            "Operación: créditos computables = 56 − 12 = 44 (no se contabilizan los convalidados) [RI-FI-ART-015]; promedio = 44 / 4 = 11,0 >= 10 a partir del cuarto semestre [RG-ART-028] [RI-FI-ART-014]."
        ),
        "fuente": "[RG-ART-028] [RI-FI-ART-014] [RI-FI-ART-015]",
    },
    {
        "id": "B5-V04",
        "bloque": "resiliencia_feedback",
        "split": "val",
        "modo": "numerica",
        "pregunta": "Una asignatura tiene una nota calculada exactamente en 4,44 y otra de otro estudiante en 4,45. ¿En qué nota final queda cada una según la regla de aproximación?",
        "feedback": (
            "El borrador afirmó 4,4 y 4,5 sin citar la regla exacta sobre dígitos menores o iguales/superiores a 5."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-023"],
        "distractores": ["RG-ART-024", "RG-ART-021", "RG-ANEXO-08", "RG-ANEXO-09", "RI-FI-ART-011"],
        "pensar": (
            "[RG-ART-023]: centésimas < 5 no afectan la décima; >= 5 suben a la décima superior. Para 4,44 la centésima es 4 (< 5) -> 4,4; para 4,45 la centésima es 5 (>= 5) -> 4,5."
        ),
        "respuesta": (
            "La nota 4,44 queda en 4,4 y la nota 4,45 se aproxima a 4,5 [RG-ART-023]."
        ),
        "condiciones": (
            "Regla: en la escala oficial de 1 a 7 con un decimal, las centésimas inferiores a 5 (como 4 en 4,44) no alteran la décima y las iguales o superiores a 5 (como 5 en 4,45) aproximan a la décima superior [RG-ART-023]."
        ),
        "fuente": "[RG-ART-023]",
    },
    {
        "id": "B5-V05",
        "bloque": "resiliencia_feedback",
        "split": "val",
        "modo": "condicional",
        "pregunta": "¿Tiene el alumno derecho a conservar sus evaluaciones ya rendidas al pedir un reingreso ordinario tras haber caído en pérdida de carrera?",
        "feedback": (
            "El borrador omitió distinguir entre quien reingresa sin pérdida de carrera y quien sí incurrió en pérdida de carrera."
        ),
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-044"],
        "distractores": ["RG-ART-033", "RG-ART-037", "RI-FI-ART-020", "RG-ART-028", "RG-ART-047"],
        "pensar": (
            "[RG-ART-044]: si reingresa tras pérdida de carrera no cumple la excepción del inciso 2 (que solo favorece a quien NO incurrió en "
            "pérdida de carrera), por lo que ingresa a Primer Año como alumno nuevo sin validar, revalidar, convalidar ni reconocer aprobadas."
        ),
        "respuesta": (
            "No: quien reingresa a la misma carrera habiendo incurrido en pérdida de carrera debe hacerlo a Primer Año como alumno nuevo, "
            "sujeto a las exigencias vigentes y sin derecho a validar, revalidar, convalidar ni reconocer asignaturas aprobadas [RG-ART-044]."
        ),
        "condiciones": (
            "La única excepción de pedir mantener la situación académica anterior (dentro de los 30 primeros días del primer semestre) rige "
            "únicamente para quien reingresa sin haber incurrido en pérdida de carrera [RG-ART-044]."
        ),
        "fuente": "[RG-ART-044]",
    },
]


BLOQUE_6_ABSTENCION_HONESTA: list[dict[str, Any]] = [
    # ---- TRAIN (25 ejemplos): combinan no_existe, insuficiente y suficiente-sin-dato-clave (trampa H03) ----
    {
        "id": "B6-T01",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿Qué establece exactamente el Artículo 57 de los Estatutos de la Corporación respecto a la coordinación académica entre Departamentos?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-010", "RG-ART-006", "RG-PREAMBULO", "RG-ART-004", "RI-FI-ART-032", "RG-ART-008"],
        "pensar": (
            "[RG-ART-010] menciona al pasar 'cautelando el cumplimiento de lo dispuesto en el primer párrafo del Artículo 57 de los Estatutos de "
            "la Corporación', pero el texto completo o contenido del Artículo 57 de los Estatutos NO está en la evidencia entregada. No debo inventarlo."
        ),
        "respuesta": (
            "No es posible responder qué establece el Artículo 57 de los Estatutos de la Corporación porque su contenido no forma parte de la normativa consultada."
        ),
        "condiciones": (
            "La evidencia únicamente hace referencia a cautelar el primer párrafo de ese artículo al coordinar con Directores de Departamento [RG-ART-010], "
            "sin reproducir el texto de los Estatutos."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T02",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿Qué sanciones específicas y grados de faltas disciplinares fija el Reglamento 'Normas de Conducta de los Estudiantes'?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-051", "RG-ART-003-DEF-20", "RG-ART-023", "RG-ART-060", "RI-FI-ART-035", "RG-ART-013"],
        "pensar": (
            "[RG-ART-051] solo remite a la pérdida de la condición de alumno por resolución adoptada bajo el Reglamento 'Normas de Conducta de "
            "los Estudiantes', pero el texto ni las sanciones de ese reglamento especial figuran en la evidencia."
        ),
        "respuesta": (
            "No se cuenta con información en la normativa consultada sobre las sanciones ni graduación de faltas del Reglamento 'Normas de Conducta de los Estudiantes'."
        ),
        "condiciones": (
            "La evidencia solo menciona que una resolución adoptada conforme a dicho reglamento produce la pérdida de la condición de alumno de pregrado, sin incluir su articulado."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T03",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "numerica",
        "pregunta": "¿Cuántos semestres de duración mínima o máxima y qué causales de reprobación rigen específicamente en el Reglamento de Memoria de Título de Ingeniería?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RI-FI-ART-029", "RI-FI-ART-030", "RI-FI-ART-031", "RG-ART-049", "RG-ART-003-DEF-10", "RG-ART-022"],
        "pensar": (
            "[RI-FI-ART-029] dice que la Memoria de Título dura un semestre y se rige por el Reglamento de Memoria de Título de Ingeniería, pero el "
            "texto de ese Reglamento de Memoria de Título (y sus causales de reprobación) NO está en la evidencia."
        ),
        "respuesta": (
            "No hay respaldo en la normativa consultada respecto de las causales de reprobación ni reglas internas del Reglamento de Memoria de Título de la Facultad de Ingeniería."
        ),
        "condiciones": (
            "Únicamente consta en la evidencia que la Memoria de Título tiene un semestre de duración en el plan y se rige por dicho reglamento especial [RI-FI-ART-029], cuyo contenido no fue proporcionado."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T04",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "numerica",
        "pregunta": "Para una asignatura semestral impartida por Ingeniería con duración intensiva menor a un semestre (por ejemplo, de 6 semanas fuera del PLEV), ¿cuál es exactamente el plazo de días para hacer abandono sin motivo?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-043", "RG-ART-018", "RG-ART-045", "RG-ART-016", "RI-FI-ART-009", "CAL-2026-S1-03"],
        "pensar": (
            "[RG-ART-043]: 'en el caso de asignaturas de duración menor a un semestre, la Facultad que dicta la asignatura establecerá el plazo de abandono'. "
            "En el Reglamento Interno de Ingeniería NO hay ninguna unidad que fije ese número de días o semanas. Debo abstenerme sin inventar."
        ),
        "respuesta": (
            "No es posible indicar el plazo exacto en la normativa consultada, ya que para asignaturas de duración menor a un semestre el plazo de "
            "abandono debe ser establecido por la Facultad que dicta la asignatura y dicho dato no figura en la evidencia."
        ),
        "condiciones": (
            "Consta únicamente que el plazo general de cuatro semanas aplica a asignaturas semestrales o anuales, remitiéndose las de duración inferior "
            "a la determinación de cada Facultad [RG-ART-043]."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T05",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "numerica",
        "pregunta": "En el calendario 2026, ¿cuántos días corridos hay entre el cierre del período de matrícula de primer año y la fecha límite de retiro total de asignaturas anuales?",
        "feedback": None,
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["CAL-2026-S1-01", "CAL-2026-S1-02", "CAL-2026-S1-03", "CAL-2026-S1-05", "RG-ART-042", "RG-ART-043"],
        "pensar": (
            "Reviso todas las unidades de CAL-2026: NO hay fecha de 'cierre del período de matrícula de primer año' ni de 'retiro total de asignaturas anuales'. "
            "Faltan ambas fechas: abstenerme sin inventar días."
        ),
        "respuesta": (
            "No es posible calcular esa diferencia de días porque en la normativa y calendario consultados no figuran las fechas de cierre de "
            "matrícula de primer año ni de retiro total de asignaturas anuales."
        ),
        "condiciones": (
            "La evidencia de calendario solo registra bienvenida (02–06 mar), inicio de clases (09 mar), modificación de asignaturas (02 abr) y término de clases anuales (24 jul), insuficientes para el cálculo pedido."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T06",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "Según el artículo 40 del RI-FI de Ingeniería, ¿cómo se evalúan y convalidan las prácticas profesionales de los estudiantes?",
        "feedback": None,
        "estado": "no_existe",
        "inexistentes": ["RI-FI-ART-040"],
        "evidencia_clave": [],
        "distractores": ["RI-FI-ART-035", "RI-FI-ART-029", "RG-ART-040"],
        "pensar": (
            "Estado: no_existe | no existen en la normativa: RI-FI-ART-040. El RI-FI llega hasta el Art. 35°. No confundirlo con [RG-ART-040]."
        ),
        "respuesta": (
            "No existe un Artículo 40 en el Reglamento Interno de Docencia de Pregrado de la Facultad de Ingeniería; este reglamento llega hasta el Artículo 35°."
        ),
        "condiciones": (
            "No hay respaldo en la normativa consultada para disposiciones sobre práctica profesional atribuidas a un inexistente Artículo 40° del RI-FI."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T07",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿Qué establece el Artículo 65 del Reglamento General de Docencia de Pregrado respecto al retiro temporal por motivos laborales?",
        "feedback": None,
        "estado": "no_existe",
        "inexistentes": ["RG-ART-065"],
        "evidencia_clave": [],
        "distractores": ["RG-ART-060", "RG-ART-031", "RG-ART-059"],
        "pensar": (
            "Estado: no_existe | RG llega hasta Art. 60 (luego transitorios). RG-ART-065 no existe en la normativa."
        ),
        "respuesta": (
            "No existe el Artículo 65 del Reglamento General de Docencia de Pregrado en la normativa consultada."
        ),
        "condiciones": (
            "El articulado permanente del Reglamento General llega hasta el Artículo 60°."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T08",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "premisa_falsa",
        "pregunta": "¿Qué establece el inciso d) del Artículo 3° del Reglamento Interno de Ingeniería sobre el ingreso especial deportivo?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RI-FI-ART-003", "RI-FI-ART-004", "RI-FI-ART-001", "RG-ART-046", "RG-ART-052", "RI-FI-ART-002"],
        "pensar": (
            "Leo [RI-FI-ART-003]: solo tiene una frase con Ingreso Directo e Ingreso Común, SIN ningún inciso d) ni referencia a ingreso especial deportivo."
        ),
        "respuesta": (
            "El Artículo 3° del Reglamento Interno de Ingeniería no contiene un inciso d) ni disposiciones sobre ingreso especial deportivo [RI-FI-ART-003]."
        ),
        "condiciones": (
            "Dicho artículo únicamente define el ingreso a Primer Año bajo modalidad mixta (Ingreso Directo e Ingreso Común), sin incisos ni ingreso deportivo [RI-FI-ART-003]; sobre ese inciso d) específico no hay respaldo en la normativa consultada."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T09",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "numerica",
        "pregunta": "¿Cuántos pesos o UTM cuesta el trámite de solicitud de reincorporación en la Universidad de Concepción?",
        "feedback": None,
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-033", "RI-FI-ART-027", "RG-ART-035", "RI-FI-ART-025"],
        "pensar": (
            "La evidencia regula requisitos académicos/administrativos y certificados DAFE/Biblioteca, pero no contiene ningún monto arancelario ni valor en pesos o UTM."
        ),
        "respuesta": (
            "No existe información en la normativa consultada sobre el costo monetario en pesos o UTM para tramitar la reincorporación."
        ),
        "condiciones": (
            "La normativa consultada regula únicamente las autoridades competentes, plazos y certificados requeridos, sin establecer tarifas ni aranceles."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T10",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué ponderación porcentual específica fijan los Reglamentos para la Evaluación de Recuperación de Ingeniería (por ejemplo 30 % o 40 % de la Nota Final)?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RI-FI-ART-012", "RG-ART-022", "RG-ART-027", "RI-FI-ART-010", "RI-FI-ART-011", "RG-ART-021"],
        "pensar": (
            "¡Ojo! En [RI-FI-ART-012] dice que el Profesor Encargado entregará por escrito en la primera semana la ponderación, incluyendo la "
            "Evaluación de Recuperación, y [RG-ART-022] dice que su modalidad de ponderación se indicará en el Reglamento Interno de la Facultad que "
            "dicta la asignatura — pero [RI-FI-ART-012] NO fija un porcentaje único! No debo inventar 30 % ni 40 %."
        ),
        "respuesta": (
            "No se indica un porcentaje único de ponderación en la normativa consultada: el reglamento remite la definición de la ponderación de la "
            "Evaluación de Recuperación a lo que el Profesor Encargado informe por escrito en la primera semana de clases."
        ),
        "condiciones": (
            "La evidencia solo indica que la ponderación se entrega por escrito al inicio de la asignatura [RI-FI-ART-012] y no fija una cifra porcentual fija en el Reglamento Interno de Ingeniería."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T11",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿En qué fecha del año 2027 comienzan las clases del primer semestre según el Calendario de Docencia de Pregrado?",
        "feedback": None,
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["CAL-2026-S1-01", "CAL-2026-S1-02", "CAL-2026-S2-02", "RG-ART-016"],
        "pensar": (
            "Solo disponemos del Calendario 2026 (`CAL-2026-*`); no existe ningún dato del calendario 2027."
        ),
        "respuesta": (
            "No hay respaldo en la normativa consultada sobre las fechas del calendario académico del año 2027; la evidencia disponible corresponde únicamente al Calendario de docencia de pregrado 2026."
        ),
        "condiciones": (
            "Faltan los registros del calendario correspondiente al año académico 2027."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T12",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿Qué requisitos académicos exige el reglamento especial para la participación de alumnos de postgrado como ayudantes o colaboradores docentes en pregrado?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-002", "RG-ART-006", "RG-ART-015", "RG-ART-057", "RI-FI-ART-002", "RG-ART-053"],
        "pensar": (
            "[RG-ART-002] menciona que un reglamento especial regulará dicha participación y colaboración en la docencia, pero ese reglamento especial no está incluido."
        ),
        "respuesta": (
            "No existe respaldo en la normativa consultada sobre los requisitos específicos de dicho reglamento especial para colaboradores o alumnos de postgrado en docencia."
        ),
        "condiciones": (
            "El Reglamento General únicamente establece que pueden colaborar estando debidamente calificados y remite los detalles a un reglamento especial no incluido en la evidencia [RG-ART-002]."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T13",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "numerica",
        "pregunta": "¿Cuál es la nota mínima exigida en el examen de admisión para alumnos libres y visitantes?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-053", "RG-ART-003-DEF-16", "RG-ART-003-DEF-18", "RI-FI-ART-017", "RG-ART-002"],
        "pensar": (
            "[RG-ART-053] remite a un reglamento especial y a los convenios correspondientes; ni [RG-ART-003-DEF-16] ni [RG-ART-003-DEF-18] contienen nota mínima."
        ),
        "respuesta": (
            "No hay respaldo en la normativa consultada acerca de una nota mínima de admisión para alumnos libres ni alumnos visitantes."
        ),
        "condiciones": (
            "La normativa general remite el régimen de requisitos, derechos y obligaciones de alumnos libres y visitantes a un reglamento especial y convenios que no constan en la evidencia [RG-ART-053]."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T14",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "cruce",
        "pregunta": "En el calendario 2026, ¿cuántos días transcurren desde la fecha límite de retiro de asignaturas del PLEV hasta el término de clases del PLEV?",
        "feedback": None,
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-043", "RG-ART-045", "RG-ART-016", "CAL-2026-S1-03", "CAL-2026-S2-03"],
        "pensar": (
            "Dos imposibilidades: (1) en [RG-ART-043] no se puede abandonar asignaturas inscritas en el PLEV, y (2) el calendario 2026 disponible no incluye fechas de inicio ni término del PLEV 2026."
        ),
        "respuesta": (
            "No es posible calcular ese plazo en días: por un lado, el reglamento prohíbe hacer abandono de asignaturas inscritas en el PLEV [RG-ART-043]; por otro, el calendario consultado no contiene fechas de inicio ni de término del PLEV 2026."
        ),
        "condiciones": (
            "Sin fechas del PLEV en el Calendario 2026 y existiendo prohibición normativa de abandono en el PLEV [RG-ART-043], no puede calcularse el intervalo consultado."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T15",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿Qué porcentaje de la ponderación de la Prueba de Acceso a la Educación Superior (PAES) usa la UdeC para el Ingreso Directo a Ingeniería Civil Informática?",
        "feedback": None,
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["RI-FI-ART-003", "RI-FI-ART-004", "RI-FI-ART-002", "RI-FI-ART-005", "RG-ART-002"],
        "pensar": (
            "Las Normas de Ingreso a las Carreras de Pregrado de la UdeC son solo mencionadas en [RI-FI-ART-002]; no constan porcentajes PAES ni carreras específicas como Informática."
        ),
        "respuesta": (
            "No existe información en la normativa consultada sobre ponderaciones PAES ni criterios de admisión específicos para Ingeniería Civil Informática."
        ),
        "condiciones": (
            "El Reglamento Interno de Ingeniería solo remite a las Normas de Ingreso UdeC vigentes sin reproducir ponderaciones de admisión [RI-FI-ART-002]."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T16",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué criterios numéricos de aprobación fija el Artículo 35° del Reglamento Interno de Ingeniería para el examen de grado oral?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RI-FI-ART-035", "RI-FI-ART-029", "RI-FI-ART-030", "RI-FI-ART-011", "RG-ART-003-DEF-10"],
        "pensar": (
            "[RI-FI-ART-035] dice únicamente: 'Las situaciones no previstas en el presente reglamento serán resueltas por el Decano de la Facultad de Ingeniería, en el ámbito de su competencia'. No trata ningún examen de grado oral."
        ),
        "respuesta": (
            "El Artículo 35° del Reglamento Interno de Ingeniería no regula ningún examen de grado oral ni fija criterios numéricos para él [RI-FI-ART-035]."
        ),
        "condiciones": (
            "Dicho artículo únicamente dispone que las situaciones no previstas en el reglamento serán resueltas por el Decano de Ingeniería dentro de su competencia [RI-FI-ART-035]; sobre el examen consultado no hay respaldo."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T17",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿Cuál es la fecha límite exacta del segundo semestre de 2026 para presentar las solicitudes de suspensión de estudios?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": ["RG-ART-031", "CAL-2026-S2-04", "RG-ART-016"],
        "distractores": ["RI-FI-ART-025", "CAL-2026-S2-03", "CAL-2026-S2-05"],
        "pensar": (
            "En [RG-ART-031] dice 'hasta cuatro semanas antes del término del periodo lectivo respectivo', "
            "y en [CAL-2026-S2-04] dice Término de Clases: 11 de diciembre. Sin embargo, [RG-ART-016] define que las actividades de docencia se extienden entre el inicio de clases "
            "y la entrega del Acta de Notas Finales, y el Calendario 2026 no fija explícitamente la fecha de cierre del período lectivo ni una fecha de cierre de suspensión de estudios. "
            "No debo adivinar ni restar cuatro semanas a un hito distinto sin fecha oficial del término del período lectivo."
        ),
        "respuesta": (
            "No es posible determinar una fecha calendario exacta sin ambigüedad en la evidencia: aunque el reglamento fija un plazo de hasta cuatro "
            "semanas antes del término del período lectivo respectivo [RG-ART-031], las clases del segundo semestre terminan el 11 de diciembre [CAL-2026-S2-04] "
            "y las actividades se extienden hasta la entrega del Acta de Notas Finales [RG-ART-016], el calendario disponible no indica la fecha exacta de cierre del período lectivo ni del trámite."
        ),
        "condiciones": (
            "Regla aplicable: debe solicitarse hasta cuatro semanas antes del término del período lectivo [RG-ART-031], cuyo desarrollo abarca hasta el Acta de Notas Finales [RG-ART-016], dato ausente junto al 11 de diciembre de término de clases [CAL-2026-S2-04]."
        ),
        "fuente": "[RG-ART-031] [CAL-2026-S2-04] [RG-ART-016]",
    },
    {
        "id": "B6-T18",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿Qué día feriado nacional cae el 15 de agosto de 2026 según el Calendario de Docencia de Pregrado?",
        "feedback": None,
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["CAL-2026-S2-08", "CAL-2026-S2-09", "CAL-2026-S2-10", "CAL-2026-S2-11"],
        "pensar": (
            "En CAL-2026-S2 los feriados listados son 20 ago, 18 sept, 12 oct y 08 dic. No aparece el 15 de agosto en el calendario del corpus."
        ),
        "respuesta": (
            "No figura ningún feriado el 15 de agosto en el Calendario de docencia de pregrado 2026 incluido en la evidencia."
        ),
        "condiciones": (
            "En agosto del segundo semestre de 2026 el calendario consultado registra únicamente el feriado nacional del jueves 20 de agosto."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T19",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "numerica",
        "pregunta": "¿Qué porcentaje exacto de descuento en aranceles otorga la Beca Articulación Pregrado-Postgrado a los estudiantes de Ingeniería?",
        "feedback": None,
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-057", "RG-ART-045", "RI-FI-ART-030", "RG-ART-035"],
        "pensar": (
            "[RG-ART-057] menciona que se concede la Beca Articulación Pregrado-Postgrado a proposición de la Facultad, pero no establece ningún porcentaje ni monto."
        ),
        "respuesta": (
            "No hay información en la normativa consultada sobre el porcentaje o monto de descuento otorgado por la Beca Articulación Pregrado-Postgrado."
        ),
        "condiciones": (
            "La normativa consultada solo establece su otorgamiento a alumnos regulares con Grado de Licenciado aceptados simultáneamente en postgrado, sin detallar beneficios porcentuales."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T20",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿Cómo regula la doble titulación internacional el artículo 120 de la normativa general universitaria (RG)?",
        "feedback": None,
        "estado": "no_existe",
        "inexistentes": ["RG-ART-120"],
        "evidencia_clave": [],
        "distractores": ["RG-ART-060", "RG-ART-039", "RG-ART-047"],
        "pensar": (
            "RG-ART-120 no existe (RG llega al Art. 60)."
        ),
        "respuesta": (
            "No existe el Artículo 120 en el Reglamento General de Docencia de Pregrado, el cual solo llega hasta el Artículo 60° más disposiciones transitorias."
        ),
        "condiciones": (
            "La normativa consultada no contempla disposiciones bajo ese número de artículo."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T21",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "condicional",
        "pregunta": "¿Qué indica el Reglamento Interno de Ingeniería en su Artículo 14° sobre el derecho del alumno a rendir un examen especial por quinta oportunidad en una asignatura?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RI-FI-ART-014", "RI-FI-ART-016", "RG-ART-028", "RG-ART-030", "RG-ART-022", "RI-FI-ART-012"],
        "pensar": (
            "[RI-FI-ART-014] solo enumera incisos a), b) y c) de causales de Baja Académica. No contempla ningún examen especial ni quinta oportunidad."
        ),
        "respuesta": (
            "El Artículo 14° del Reglamento Interno de Ingeniería no contempla ningún derecho a examen especial ni a quinta oportunidad [RI-FI-ART-014]."
        ),
        "condiciones": (
            "Ese artículo regula exclusivamente las causales de pérdida del derecho a continuar estudios y Baja Académica [RI-FI-ART-014]; sobre dicho examen especial no existe respaldo en la normativa consultada."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T22",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "numerica",
        "pregunta": "¿Cuántos cupos exactos ofreció la Facultad de Ingeniería para Ingreso Común versus Ingreso Directo en Ingeniería Civil Química en 2026?",
        "feedback": None,
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["RI-FI-ART-003", "RI-FI-ART-004", "RI-FI-ART-005", "RI-FI-ART-006"],
        "pensar": (
            "[RI-FI-ART-004] y [RI-FI-ART-006] indican que la Facultad definirá anualmente los cupos y distribución porcentual, pero no traen cifras de cupos ni mencionan Ingeniería Civil Química."
        ),
        "respuesta": (
            "No existen cifras en la normativa consultada sobre los cupos exactos de Ingreso Común o Ingreso Directo para Ingeniería Civil Química en 2026."
        ),
        "condiciones": (
            "El reglamento solo establece que la Facultad definirá anualmente dichos cupos y su distribución porcentual, sin publicar los números por carrera."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T23",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "cruce",
        "pregunta": "¿Qué dice el Reglamento Interno de Ingeniería sobre el mínimo de créditos en PLEV y la fecha límite de matrícula del segundo semestre 2026?",
        "feedback": None,
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["RI-FI-ART-008", "RG-ART-045", "CAL-2026-S2-01", "CAL-2026-S2-02"],
        "pensar": (
            "Ni [RI-FI-ART-008] (mínimo de 8 créditos en período lectivo ORDINARIO) ni [RG-ART-045] (máximo 1 asignatura en PLEV) fijan un mínimo "
            "de créditos en PLEV, y [CAL-2026-S2-01] fija Inscripción de Asignaturas (03–07 ago), no fecha límite de matrícula."
        ),
        "respuesta": (
            "No existe respaldo en la normativa consultada sobre un mínimo de créditos para el PLEV ni sobre la fecha límite de matrícula del segundo semestre 2026."
        ),
        "condiciones": (
            "El mínimo de ocho créditos rige para cada período lectivo ordinario [RI-FI-ART-008] (mientras el PLEV admite como máximo una asignatura), "
            "y el calendario registra inscripción de asignaturas del 03 al 07 de agosto, no fecha de matrícula."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T24",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿Cuáles son los requisitos específicos de postulación del Programa de Formación Complementaria en Innovación y Emprendimiento?",
        "feedback": None,
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-003-DEF-12", "RG-ART-056", "RG-ART-047", "RG-ART-046"],
        "pensar": (
            "[RG-ART-003-DEF-12] y [RG-ART-056] regulan en general los Programas de Formación Complementaria (>= 24 SCT, aprobar dos primeros años), pero no existe información sobre un programa específico de Innovación y Emprendimiento."
        ),
        "respuesta": (
            "No existe información en la normativa consultada sobre un Programa de Formación Complementaria específico en Innovación y Emprendimiento ni sus requisitos particulares."
        ),
        "condiciones": (
            "Solo constan los requisitos generales aplicables a cualquier Programa de Formación Complementaria (haber aprobado dos primeros años, mínimo 24 SCT y requisitos del respectivo plan)."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-T25",
        "bloque": "abstencion_honesta",
        "split": "train",
        "modo": "factual",
        "pregunta": "¿Qué señala el Reglamento Interno de Ingeniería en su Artículo 38° sobre homologación automática de ramos?",
        "feedback": None,
        "estado": "no_existe",
        "inexistentes": ["RI-FI-ART-038"],
        "evidencia_clave": [],
        "distractores": ["RI-FI-ART-035", "RG-ART-038", "RG-ART-040"],
        "pensar": (
            "Estado: no_existe | RI-FI termina en el Artículo 35°. No confundirlo con [RG-ART-038] (reconocimiento en Reglamento General)."
        ),
        "respuesta": (
            "No existe el Artículo 38° en el Reglamento Interno de Docencia de Pregrado de la Facultad de Ingeniería, cuyo articulado termina en el Artículo 35°."
        ),
        "condiciones": (
            "La normativa consultada del RI-FI no incluye un Artículo 38°."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },

    # ---- VAL BLOQUE 6 (5 ejemplos) ----
    {
        "id": "B6-V01",
        "bloque": "abstencion_honesta",
        "split": "val",
        "modo": "factual",
        "pregunta": "¿Qué nota mínima o exigencia de aprobación establece el reglamento de la Facultad cuando un egresado excedió el plazo de seis semestres para titularse?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-049", "RI-FI-ART-029", "RI-FI-ART-030", "RI-FI-ART-031", "RG-ART-048", "RI-FI-ART-035"],
        "pensar": (
            "[RG-ART-049] remite las exigencias tras vencer los 6 semestres al Reglamento Interno de la Facultad; sin embargo, en todo el RI-FI "
            "solo está [RI-FI-ART-031] (suspensión > 3 años cuando solo faltaba Memoria), no un artículo sobre egresados con más de 6 semestres sin suspensión!"
        ),
        "respuesta": (
            "No existe respaldo en la normativa consultada sobre las exigencias específicas aplicables en Ingeniería cuando vence el plazo de seis "
            "semestres desde el egreso sin haberse titulado."
        ),
        "condiciones": (
            "El Reglamento General fija el límite de seis semestres y delega tales exigencias en el Reglamento Interno de la Facultad [RG-ART-049], "
            "pero dicho supuesto específico no aparece regulado en el Reglamento Interno de Ingeniería consultado."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-V02",
        "bloque": "abstencion_honesta",
        "split": "val",
        "modo": "factual",
        "pregunta": "¿Qué dispone el Artículo 15° del Reglamento General respecto a la remuneración económica de los Tutores Académicos y Monitores Estudiantiles?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ART-015", "RG-ART-002", "RG-ART-052", "RG-ART-008", "RG-ART-059"],
        "pensar": (
            "Leo literalmente [RG-ART-015]: define el sistema de tutorías y monitores y sus roles, pero NO menciona remuneración ni pago económico."
        ),
        "respuesta": (
            "El Artículo 15° del Reglamento General no contiene ninguna disposición sobre remuneración económica de Tutores Académicos ni Monitores Estudiantiles [RG-ART-015]."
        ),
        "condiciones": (
            "Dicho artículo únicamente describe los objetivos y funciones de orientación, inducción y apoyo remedial de ambos sistemas [RG-ART-015]; "
            "respecto a su remuneración no hay respaldo en la normativa consultada."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-V03",
        "bloque": "abstencion_honesta",
        "split": "val",
        "modo": "numerica",
        "pregunta": "En la equivalencia de escalas de notas, ¿a qué nota decimal exacta en la escala de 1,0 a 7,0 corresponde un puntaje de 50,5 en la escala de 1 a 100?",
        "feedback": None,
        "estado": "suficiente",
        "evidencia_clave": [],
        "distractores": ["RG-ANEXO-50", "RG-ANEXO-01", "RG-ART-023", "RG-ART-024", "RI-FI-ART-011"],
        "pensar": (
            "[RG-ANEXO-50] da puntaje entero 50 -> 3,9 (reprobación) y [RG-ANEXO-01] da puntaje entero 51 -> 4,0 (aprobación). No existe regla "
            "para decimales intermedios (50,5) en la escala 1 a 100 ni fórmula de interpolación en el reglamento."
        ),
        "respuesta": (
            "No existe respaldo en la normativa consultada para convertir un puntaje fraccionario de 50,5 en escala de 1 a 100 a la escala de 1,0 a 7,0."
        ),
        "condiciones": (
            "La tabla del Anexo consulta únicamente valores enteros (50 equivale a 3,9 en reprobación y 51 a 4,0 en aprobación) y no contempla fórmula de interpolación intermedia."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-V04",
        "bloque": "abstencion_honesta",
        "split": "val",
        "modo": "factual",
        "pregunta": "¿De qué manera aplica la vigencia diferida descrita en el tercer artículo transitorio del Reglamento General?",
        "feedback": None,
        "estado": "no_existe",
        "inexistentes": ["RG-TRANS-003"],
        "evidencia_clave": [],
        "distractores": ["RG-TRANS-001", "RG-TRANS-002", "RG-PREAMBULO", "RG-ART-060"],
        "pensar": (
            "Los artículos transitorios en el corpus llegan solo hasta RG-TRANS-002."
        ),
        "respuesta": (
            "No existe un Artículo 3° transitorio del Reglamento General de Docencia de Pregrado en la normativa consultada; las disposiciones transitorias solo llegan al Artículo 2°."
        ),
        "condiciones": (
            "Falta respaldo en la normativa consultada para un inexistente Artículo 3° transitorio."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
    {
        "id": "B6-V05",
        "bloque": "abstencion_honesta",
        "split": "val",
        "modo": "cruce",
        "pregunta": "¿Qué fecha límite del Calendario 2026 rige para inscribir cursos de verano PLEV y cuántas horas semanales máximas permite el Artículo 8 de Ingeniería?",
        "feedback": None,
        "estado": "insuficiente",
        "evidencia_clave": [],
        "distractores": ["RI-FI-ART-008", "RG-ART-017", "RG-ART-045", "CAL-2026-S1-01", "CAL-2026-S2-01"],
        "pensar": (
            "Ninguno de los dos datos pedidos existe: (1) el Calendario 2026 no tiene fechas de PLEV, y (2) [RI-FI-ART-008] fija mínimo de 8 créditos "
            "(no horas semanales máximas; el máximo de 54 horas semanales de Trabajo Académico es del Plan de Estudio en [RG-ART-017], no del Art. 8 RI-FI)."
        ),
        "respuesta": (
            "No existe respaldo en la normativa consultada sobre una fecha límite de inscripción para el PLEV 2026 ni sobre un máximo de horas semanales en el Artículo 8° del Reglamento Interno de Ingeniería."
        ),
        "condiciones": (
            "El Calendario 2026 disponible no contempla fechas del PLEV y el Artículo 8° de Ingeniería establece únicamente un mínimo de ocho créditos por período lectivo ordinario, sin tope de horas."
        ),
        "fuente": "sin respaldo en la normativa consultada",
    },
]
