# Muestra de Revisión Manual — Dataset Redactor D4 v2 (30 casos)

Muestra estratificada de **30 ejemplos** (`3 train + 2 val` por cada uno de los 6 bloques) extraída desde `redactor_train.jsonl` y `redactor_val.jsonl` para verificación humana previa al entrenamiento QLoRA (Paso 3).

## Autoría y Separación de Datos (v2)
- **Fuente normativa:** Fragmentos literales de `corpus.json` (reglamentos y calendario UdeC).
- **Autoría de los pares supervisados:** Especificaciones redactadas y curadas por el equipo con asistencia de **Antigravity (modelo asistente IA)** y verificadas programáticamente contra `corpus.json` (citas, cálculos aritméticos y fechas).
- **Separación estricta:** 0 de las 40 unidades de corpus evaluadas en las 75 preguntas de D3 y 0 de las 21 unidades reservadas para `preguntas_nuevas_20.csv` aparecen en `evidencia_clave`, `distractores` ni referencias textuales del dataset.

## Registro de Verificación Humana (30 casos)

> **Nota:** Complete esta tabla al revisar los casos antes de validar la entrega final (revisor, fecha y estado).

| # | ID | Bloque / Split | Revisor | Fecha | Resultado | Observaciones |
|---|---|---|---|:---:|---|---|
| 01 | `B1-T01` | `citas_cruce` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 02 | `B1-T18` | `citas_cruce` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 03 | `B1-T35` | `citas_cruce` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 04 | `B1-V01` | `citas_cruce` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 05 | `B1-V05` | `citas_cruce` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 06 | `B2-T01` | `condiciones_excepciones` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 07 | `B2-T18` | `condiciones_excepciones` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 08 | `B2-T35` | `condiciones_excepciones` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 09 | `B2-V01` | `condiciones_excepciones` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 10 | `B2-V05` | `condiciones_excepciones` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 11 | `B3-T01` | `polares_y_lectura` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 12 | `B3-T16` | `polares_y_lectura` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 13 | `B3-T30` | `polares_y_lectura` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 14 | `B3-V01` | `polares_y_lectura` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 15 | `B3-V05` | `polares_y_lectura` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 16 | `B4-T01` | `calculos_y_orden` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 17 | `B4-T16` | `calculos_y_orden` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 18 | `B4-T30` | `calculos_y_orden` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 19 | `B4-V01` | `calculos_y_orden` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 20 | `B4-V05` | `calculos_y_orden` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 21 | `B5-T01` | `resiliencia_feedback` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 22 | `B5-T13` | `resiliencia_feedback` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 23 | `B5-T25` | `resiliencia_feedback` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 24 | `B5-V01` | `resiliencia_feedback` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 25 | `B5-V05` | `resiliencia_feedback` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 26 | `B6-T01` | `abstencion_honesta` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 27 | `B6-T13` | `abstencion_honesta` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 28 | `B6-T25` | `abstencion_honesta` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 29 | `B6-V01` | `abstencion_honesta` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |
| 30 | `B6-V05` | `abstencion_honesta` / `val` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |

Criterios a revisar en cada ejemplo:
1. La respuesta esperada se deduce íntegramente de los fragmentos literales mostrados en `<evidencia>`.
2. Todas las citas `[ID]` existen en la evidencia entregada y cubren cada afirmación relevante.
3. El bloque `<pensar>` razona sin saltos lógicos ni contradecir la salida final.
4. Cuando la evidencia falta o es parcial, el modelo no inventa datos y se abstiene honestamente; si no hay salvedades extra aplicables, usa `Condiciones o límites: No aplica`.

---

## 01. `B1-T01` — bloque `citas_cruce` | split `train` | modo `cruce` | estado `suficiente`

**Pregunta:** ¿Qué requisito previo sobre docencia debe cumplir un alumno para inscribir asignaturas y en qué casos un profesor queda exento de ser evaluado en esa encuesta?

**Evidencia ensamblada (5 unidades, orden barajado):** `RG-ART-007`, `RG-ART-042`, `RG-ART-019`, `RI-FI-ART-007`, `RG-ART-010`
- Clave esperada: `RG-ART-042, RG-ART-007` | Distractores incluidos: `RG-ART-019, RI-FI-ART-007, RG-ART-010`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-042]** Artículo 42º La inscripción de asignaturas deberá realizarse en las fechas indicadas por el Calendario de Docencia de Pregrado. En el caso de los alumnos que ingresan a una carrera, la inscripción de asignaturas será parte del proceso de matrícula. El Vicedecano podrá autorizar, en casos justificados y excepcionales, modificaciones de inscripción o admitir las que estén fuera de plazo. El alumno deberá inscribir y cursar un número de créditos igual o superior al mínimo por semestre que indique el Reglamento Interno de la Facultad a la cual está adscrito. El Vicedecano podrá autorizar una inscripción menor cuando la oferta de créditos es inferior a ese mínimo, debido a la situación curricular personal del alumno y de los prerrequisitos de su plan de estudio. En el caso que el alumno que esté terminando sus estudios, podrá inscribir sólo las asignaturas que le falte cursar. Para inscribir una asignatura, el alumno deberá cumplir con los prerrequisitos y exigencias establecidas. En caso contrario la inscripción quedará sin efecto. Las Facultades cautelarán el cumplimiento de estas normas. Para inscribir asignaturas, el alumno deberá haber respondido la Encuesta de Evaluación de la Docencia de las asignaturas cursadas en el periodo lectivo anterior. El alumno no deberá inscribir asignaturas con actividades académicas obligatorias, que estén programadas en horarios coincidentes.
- **[RG-ART-007]** Artículo 7° En cada asignatura, los profesores deberán ser evaluados por sus alumnos a través de la Encuesta de Evaluación Docente de la universidad. La Encuesta de Evaluación Docente se aplica en cada periodo lectivo y afecta al conjunto de profesores y asignaturas dictadas. Se exceptuará de la aplicación de la encuesta a aquellos profesores que hayan impartido docencia en la asignatura por reemplazos u otras circunstancias. La aplicación de la Encuesta de Evaluación Docente es de responsabilidad de la Dirección de Docencia y las encuestas deberán realizarse en línea a través de la Plataforma Encuesta Docente, en el período establecido para la unidad académica respectiva.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Parte 1: [RG-ART-042] indica que para inscribir asignaturas el alumno debe haber respondido la Encuesta de Evaluación de la Docencia de las asignaturas cursadas en el período lectivo anterior. Parte 2: [RG-ART-007] señala que quedan exceptuados de la Encuesta de Evaluación Docente los profesores que hayan impartido docencia en la asignatura por reemplazos u otras circunstancias. Cada parte tiene su cita distinta y ambas están en la evidencia.
</pensar>
Respuesta: Para inscribir asignaturas el estudiante debe haber respondido la Encuesta de Evaluación de la Docencia de las asignaturas cursadas en el período lectivo anterior [RG-ART-042]; en cuanto a los profesores, se exceptúan de esta encuesta quienes hayan impartido docencia por reemplazos u otras circunstancias [RG-ART-007].
Condiciones o límites: La encuesta se aplica en línea mediante la Plataforma Encuesta Docente en el período fijado para cada unidad académica y bajo responsabilidad de la Dirección de Docencia [RG-ART-007]; además, la inscripción exige cumplir prerrequisitos y no inscribir horarios coincidentes en actividades obligatorias [RG-ART-042].
Fuente: [RG-ART-007] [RG-ART-042]
```

## 02. `B1-T18` — bloque `citas_cruce` | split `train` | modo `cruce` | estado `suficiente`

**Pregunta:** ¿Qué órgano preside el Jefe de Carrera en el Reglamento General y qué funciones específicas cumple el Comité de Docencia y Asuntos Estudiantiles en la Facultad de Ingeniería?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-009`, `RG-ART-011`, `RG-ART-010`, `RI-FI-ART-033`, `RG-ART-008`, `RI-FI-ART-032`
- Clave esperada: `RG-ART-008, RG-ART-011, RI-FI-ART-033` | Distractores incluidos: `RG-ART-009, RG-ART-010, RI-FI-ART-032`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-008]** Artículo 8º Habrá un Jefe de Carrera en cada campus en que ella se dicte, designado por el Decano respectivo, con conocimiento del Consejo de Carrera, debiendo cumplir el perfil que al efecto propondrá el mismo Consejo. Coordinará las actividades de docencia y velará por su buen desarrollo, según lo establezca la normativa universitaria vigente. Serán funciones del Jefe de Carrera: 1. Representar a la carrera al interior y exterior de la universidad. 2. Gestionar el currículum en lo relativo a la implementación del plan de estudio, al avance efectivo de cada uno de los alumnos y a los resultados obtenidos por cada cohorte. 3. Coordinar la programación de la docencia para la carrera en cada periodo lectivo. 4. Velar por la correcta ejecución de actividades docentes de la carrera así como el cumplimiento de las normas, informando oportunamente, al organismo que corresponda, sobre cualquier aspecto que afecte el normal desarrollo de estas actividades. 5. Supervisar el correcto funcionamiento del Sistema de Apoyo al Estudiante para alumnos de la carrera. 6. Velar por la pertinencia de la actividad final de titulación con relación al perfil de egreso de la carrera. 7. Participar en la definición de estrategias de vinculación con el medio de su Facultad, asociadas a promoción, captación, movilidad estudiantil, prácticas profesionales y seguimiento de egresados y velar por su implementación en la carrera, en coordinación con los organismos institucionales. 8. Conducir la aplicación del Modelo de Evaluación de Carrera, y supervisar la elaboración, actualización y cumplimiento del Plan de Desarrollo de la Carrera. 9. Liderar el proceso de acreditación de la carrera y participar en los procesos de autoevaluación. 10. Presidir y convocar el Consejo de Carrera y el Comité de Docencia y Asuntos Estudiantiles de la carrera, según lo establecido en la normativa institucional. 11. Propiciar una comunicación efectiva entre los alumnos, las autoridades y los organismos que correspondan e informar sobre las materias relacionadas con la carrera. Cada Programa de Formación Complementaria estará dirigido por un Jefe de Programa, designado por la autoridad máxima de la unidad académica responsable. Serán funciones del Jefe de Programa: Gestionar el currículum en lo relativo a la implementación del Plan de Formación, al avance efectivo de cada uno de los alumnos y a los resultados obtenidos por cada cohorte. 1. Coordinar, con las unidades académicas participantes, la programación de la docencia en cada periodo lectivo. 2. Velar por la correcta ejecución de actividades docentes del programa así como el cumplimiento de las normas, informando oportunamente, al organismo que corresponda, sobre cualquier aspecto que afecte el normal desarrollo de estas actividades.
- **[RG-ART-011]** Artículo 11° En cada carrera que se dicte en un campus habrá un Comité de Docencia y Asuntos Estudiantiles que cumplirá con las funciones que el Reglamento Interno de Docencia de Pregrado de la Facultad o el Consejo de Carrera le asigne. Estará integrado al menos por el respectivo Jefe de Carrera que lo preside, por dos docentes elegidos por el Consejo de Carrera de entre sus integrantes y por uno de los representantes estudiantiles del Consejo de Carrera con derecho a voz y voto.
- **[RI-FI-ART-033]** Artículo 33°. El Comité de Docencia y Asuntos Estudiantiles estará integrado por la Jefatura de Carrera, que lo presidirá, por dos docentes elegidos por el Consejo de Carrera de entre sus integrantes y por uno de los representantes estudiantiles del Consejo de Carrera, con derecho a voz y voto, designado por el Centro de Alumnos de la carrera respectiva. La constitución de este Comité coincidirá con el inicio del período de la dirección de Departamento al cual está adscrita la carrera, y sus integrantes durarán dos años en sus funciones. Este Comité se encargará de todos los asuntos que afecten al alumno en su vida académica, velando por el cumplimiento de sus derechos y deberes, y resolviendo las solicitudes relativas a su desempeño o situación académica.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-008] (función 10) y [RG-ART-011] indican que el Jefe de Carrera preside y convoca tanto al Consejo de Carrera como al Comité de Docencia y Asuntos Estudiantiles. [RI-FI-ART-033] detalla que en Ingeniería el Comité vela por derechos y deberes del alumno y resuelve solicitudes relativas a su desempeño o situación académica.
</pensar>
Respuesta: El Jefe de Carrera preside y convoca el Consejo de Carrera y el Comité de Docencia y Asuntos Estudiantiles [RG-ART-008] [RG-ART-011]; en la Facultad de Ingeniería, ese Comité se encarga de todos los asuntos que afecten al alumno en su vida académica, velando por sus derechos y deberes y resolviendo solicitudes sobre su desempeño o situación académica [RI-FI-ART-033].
Condiciones o límites: En Ingeniería sus integrantes duran 2 años y lo conforman la Jefatura de Carrera, 2 docentes elegidos por el Consejo de Carrera y 1 representante estudiantil de ese Consejo designado por el Centro de Alumnos [RG-ART-011] [RI-FI-ART-033].
Fuente: [RG-ART-008] [RG-ART-011] [RI-FI-ART-033]
```

## 03. `B1-T35` — bloque `citas_cruce` | split `train` | modo `cruce` | estado `suficiente`

**Pregunta:** En el primer semestre de 2026, ¿qué fechas corresponden a las vacaciones de invierno y a las Evaluaciones de Recuperación, y qué diferencia hay con el cierre de clases de asignaturas anuales?

**Evidencia ensamblada (6 unidades, orden barajado):** `CAL-2026-S1-13`, `CAL-2026-S1-05`, `CAL-2026-S1-06`, `CAL-2026-S1-01`, `CAL-2026-S1-04`, `CAL-2026-S1-14`
- Clave esperada: `CAL-2026-S1-14, CAL-2026-S1-06, CAL-2026-S1-05` | Distractores incluidos: `CAL-2026-S1-13, CAL-2026-S1-01, CAL-2026-S1-04`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[CAL-2026-S1-14]** Calendario de docencia de pregrado 2026. Primer semestre. Vacaciones de invierno (aprobación transitoria): 30 junio – 05 de julio.
- **[CAL-2026-S1-06]** Calendario de docencia de pregrado 2026. Primer semestre. Evaluaciones de Recuperación: 13 - 24 de julio.
- **[CAL-2026-S1-05]** Calendario de docencia de pregrado 2026. Primer semestre. Término de Clases asignaturas anuales: 24 de julio.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[CAL-2026-S1-14] señala Vacaciones de invierno (con aprobación transitoria) del 30 de junio al 05 de julio. [CAL-2026-S1-06] fija las Evaluaciones de Recuperación del 13 al 24 de julio. [CAL-2026-S1-05] fija el término de clases de asignaturas anuales el 24 de julio.
</pensar>
Respuesta: Las vacaciones de invierno se programan del 30 de junio al 05 de julio [CAL-2026-S1-14] y las Evaluaciones de Recuperación del 13 al 24 de julio [CAL-2026-S1-06], coincidiendo el fin de ese período (24 de julio) con el término de clases de las asignaturas anuales [CAL-2026-S1-05].
Condiciones o límites: Las vacaciones de invierno de 30 junio a 05 julio figuran con aprobación transitoria en el calendario [CAL-2026-S1-14].
Fuente: [CAL-2026-S1-05] [CAL-2026-S1-06] [CAL-2026-S1-14]
```

## 04. `B1-V01` — bloque `citas_cruce` | split `val` | modo `cruce` | estado `suficiente`

**Pregunta:** ¿Qué facilidades académicas corresponden a dirigentes estudiantiles acreditados y qué deben hacer estudiantes con impedimentos religiosos o discapacidad al inscribir asignaturas?

**Evidencia ensamblada (5 unidades, orden barajado):** `RG-ART-014`, `RG-ART-020`, `RG-ART-052`, `RG-ART-015`, `RG-ART-042`
- Clave esperada: `RG-ART-052, RG-ART-020` | Distractores incluidos: `RG-ART-014, RG-ART-015, RG-ART-042`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-052]** Artículo 52° A los alumnos que deban cumplir funciones de representación estudiantil reconocidas por la Universidad, se les otorgarán por el Vicedecano respectivo facilidades para el desempeño de tales funciones, flexibilizando para este efecto, los requisitos académicos correspondientes, cuando ello sea posible (clases teóricas, actividades prácticas). No obstante, deberán cumplir con los requisitos para aprobar las asignaturas. Lo anterior se aplicará a los Presidentes de Centros de Alumnos y a los Presidentes, Secretarios y Tesoreros de las Federaciones de Estudiantes de Concepción, Chillán y Los Ángeles. Esta disposición también será aplicable a los alumnos que deban participar, en representación oficial de la Universidad de Concepción, en actividades extraprogramáticas.
- **[RG-ART-020]** Artículo 20º La Facultad a la que está adscrita la asignatura, determinará el régimen de asistencia a clases y a otras actividades que tengan un propósito formativo. El alumno que, libremente estime dar a conocer que por razones religiosas, tiene impedimento para asistir a las actividades académicas programadas en los horarios definidos por las Facultades, deberá acreditarlo al momento de inscribir la o las asignaturas que se trate, con el objeto de que el Profesor Encargado considere esta circunstancia en la programación de tales actividades. Los alumnos que presenten algún tipo de discapacidad, debidamente acreditada, podrán solicitar un régimen especial de asistencia y facilidades para desarrollar sus actividades lectivas y rendir las evaluaciones estipuladas en el syllabus. La solicitud deberá presentarse al momento de inscribir asignaturas ante el Vicedecano de su Facultad, quien previa consulta al Programa INCLUDEC, resolverá la solicitud e informará de ello a los vicedecanos de las facultades que dictan las asignaturas.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-052]: el Vicedecano otorga facilidades flexibilizando requisitos en clases teóricas y prácticas a Presidentes de Centros de Alumnos, Presidentes/Secretarios/Tesoreros de Federaciones (Concepción, Chillán, Los Ángeles) y representantes oficiales en actividades extraprogramáticas, sin eximir de requisitos de aprobación. [RG-ART-020]: impedimento religioso debe acreditarse al inscribir ante consideración del Profesor Encargado; discapacidad acreditada se solicita al momento de inscribir ante el Vicedecano, quien consulta al Programa INCLUDEC.
</pensar>
Respuesta: A representantes estudiantiles reconocidos (Presidentes de Centros de Alumnos, Presidentes/Secretarios/Tesoreros de Federaciones de Concepción, Chillán y Los Ángeles, y delegados oficiales extraprogramáticos) el Vicedecano les otorga flexibilización en clases teóricas y prácticas cuando sea posible [RG-ART-052]. Por otro lado, los impedimentos religiosos deben acreditarse al inscribir para que el Profesor Encargado los considere, y en discapacidad acreditada la solicitud se presenta al inscribir ante el Vicedecano, quien resuelve previa consulta a INCLUDEC [RG-ART-020].
Condiciones o límites: Los dirigentes estudiantiles igualmente deben cumplir los requisitos para aprobar las asignaturas [RG-ART-052]; en caso de discapacidad, el Vicedecano informa lo resuelto a los vicedecanos de las facultades que dictan los cursos [RG-ART-020].
Fuente: [RG-ART-020] [RG-ART-052]
```

## 05. `B1-V05` — bloque `citas_cruce` | split `val` | modo `factual` | estado `suficiente`

**Pregunta:** ¿Qué define reglamentariamente al 'Alumno Autorizado a Matricularse' y hasta qué momento del período lectivo conserva su calidad quien ya es Alumno Regular?

**Evidencia ensamblada (5 unidades, orden barajado):** `RG-ART-003-DEF-14`, `RG-ART-033`, `RG-ART-003-DEF-21`, `RG-ART-050`, `RG-ART-003-DEF-15`
- Clave esperada: `RG-ART-003-DEF-21, RG-ART-050` | Distractores incluidos: `RG-ART-003-DEF-14, RG-ART-033, RG-ART-003-DEF-15`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-003-DEF-21]** 3.21. ALUMNO AUTORIZADO A MATRICULARSE: Alumno de pregrado perteneciente a una carrera de la Universidad que ha cumplido con las exigencias académicas para matricularse en el periodo académico siguiente.
- **[RG-ART-050]** Artículo 50º La calidad de alumno regular se mantendrá hasta el inicio del periodo de inscripción de asignaturas del Período Lectivo Ordinario siguiente.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-003-DEF-21] define al Alumno Autorizado a Matricularse como el alumno de pregrado perteneciente a una carrera de la UdeC que ha cumplido las exigencias académicas para matricularse en el período académico siguiente. [RG-ART-050] fija que la calidad de alumno regular se mantiene hasta el inicio del período de inscripción de asignaturas del Período Lectivo Ordinario siguiente. Pregunta directa sobre dos definiciones claras -> Condiciones: No aplica.
</pensar>
Respuesta: El Alumno Autorizado a Matricularse es el estudiante de pregrado perteneciente a una carrera que cumplió las exigencias académicas para matricularse en el período siguiente [RG-ART-003-DEF-21], y la calidad de alumno regular se conserva hasta el inicio de la inscripción de asignaturas del Período Lectivo Ordinario siguiente [RG-ART-050].
Condiciones o límites: No aplica
Fuente: [RG-ART-003-DEF-21] [RG-ART-050]
```

## 06. `B2-T01` — bloque `condiciones_excepciones` | split `train` | modo `condicional` | estado `suficiente`

**Pregunta:** ¿Qué condiciones, límites de tiempo y excepciones rigen el abandono de asignaturas sin especificación de motivos?

**Evidencia ensamblada (4 unidades, orden barajado):** `RG-ART-021`, `RG-ART-042`, `RG-ART-045`, `RG-ART-043`
- Clave esperada: `RG-ART-043` | Distractores incluidos: `RG-ART-021, RG-ART-042, RG-ART-045`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-043]** Artículo 43º El alumno podrá hacer abandono de asignaturas semestrales o anuales, sin especificación de motivos, para lo cual tendrá un plazo de cuatro semanas a contar de la fecha del inicio de clases establecida en el Calendario de Docencia de Pregrado. Esta facultad podrá ser utilizada por el alumno una sola vez en cada asignatura siempre que no quede con un número de créditos inferior al mínimo establecido. No obstante lo anterior, en el caso de asignaturas de duración menor a un semestre, la Facultad que dicta la asignatura establecerá el plazo de abandono. Los alumnos no podrán hacer abandono de asignaturas inscritas en el PLEV.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-043] contiene: 1) plazo de 4 semanas desde inicio de clases; 2) utilizable 1 sola vez por asignatura; 3) sin quedar bajo el mínimo de créditos; 4) excepción para asignaturas < 1 semestre (plazo lo fija la Facultad); 5) prohibición expresa para asignaturas inscritas en el PLEV.
</pensar>
Respuesta: El alumno puede hacer abandono de asignaturas semestrales o anuales sin especificar motivos dentro de las cuatro semanas siguientes al inicio de clases fijado en el Calendario de Docencia de Pregrado [RG-ART-043].
Condiciones o límites: Rigen cuatro condiciones y excepciones: (1) solo puede usarse una vez en cada asignatura; (2) no debe dejar al alumno con menos créditos que el mínimo establecido; (3) en asignaturas de duración menor a un semestre, el plazo de abandono lo fija la Facultad que las dicta; y (4) no se puede abandonar asignaturas inscritas en el PLEV [RG-ART-043].
Fuente: [RG-ART-043]
```

## 07. `B2-T18` — bloque `condiciones_excepciones` | split `train` | modo `condicional` | estado `suficiente`

**Pregunta:** ¿Qué condiciones regulan la participación de colaboradores externos o estudiantes en la docencia de pregrado?

**Evidencia ensamblada (5 unidades, orden barajado):** `RG-ART-052`, `RG-ART-006`, `RG-ART-001`, `RG-ART-002`, `RG-ART-015`
- Clave esperada: `RG-ART-002` | Distractores incluidos: `RG-ART-052, RG-ART-006, RG-ART-001, RG-ART-015`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-002]** Artículo 2° La docencia es una actividad fundamental y prioritaria en la Universidad de Concepción. La docencia de pregrado constituye el primer nivel de formación universitaria destinada a quienes estén en posesión de la Licencia de Educación Media o sus equivalentes legales y cumplan con las exigencias de admisión establecidas por la Universidad de Concepción. La formación de pregrado se articula con una especialización y perfeccionamiento en los niveles de postítulo y postgrado. La docencia de pregrado deberá propender a que el alumno tenga una participación responsable y protagónica en su proceso de enseñanza y aprendizaje, orientado al desarrollo de competencias genéricas y específicas declaradas en el Modelo Educativo Institucional y en el Plan de Estudios de cada carrera. Para ello, este proceso debe estimular la creatividad, el autoaprendizaje, el pensamiento crítico y tender a una formación integral. La docencia de pregrado será impartida por académicos de la Universidad de Concepción. Además, podrán participar expertos externos y colaborar alumnos de pregrado y postgrado de la Universidad de Concepción, debidamente calificados. Un reglamento especial regulará dicha participación y colaboración en la docencia.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-002]: la docencia de pregrado es impartida por académicos UdeC; además pueden participar expertos externos y colaborar alumnos de pregrado y postgrado UdeC, debidamente calificados, regulados por un reglamento especial. Destinatarios: poseedores de Licencia de Educación Media o equivalente que cumplan exigencias de admisión.
</pensar>
Respuesta: Aunque la docencia es impartida por académicos UdeC, pueden participar expertos externos y colaborar alumnos de pregrado y postgrado de la misma Universidad, siempre que estén debidamente calificados [RG-ART-002].
Condiciones o límites: Dicha participación y colaboración queda regulada por un reglamento especial [RG-ART-002].
Fuente: [RG-ART-002]
```

## 08. `B2-T35` — bloque `condiciones_excepciones` | split `train` | modo `condicional` | estado `suficiente`

**Pregunta:** ¿Qué requisitos y restricciones temporales aplican cuando se requiere cambiar una carrera por vía de cambio interno frente al ingreso a una carrera distinta?

**Evidencia ensamblada (5 unidades, orden barajado):** `RG-ART-037`, `RG-ART-055`, `RG-ART-044`, `RG-ART-054`, `RG-ART-035`
- Clave esperada: `RG-ART-054, RG-ART-055` | Distractores incluidos: `RG-ART-037, RG-ART-044, RG-ART-035`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-054]** Artículo 54° Los alumnos de la Universidad de Concepción, cualquiera sea carrera que cursen, podrán solicitar su cambio a otra carrera, siempre que cumplan con los siguientes requisitos: a) Ser alumno regular y conservar el derecho a continuar estudios en la carrera de origen. b) Haber obtenido en sus estudios, a lo menos, el promedio mínimo de calificaciones que se señale en el Reglamento Interno de Docencia de Pregrado de la Facultad a la cual postula. Cuando se trate de cambios entre carreras de una misma Facultad, el Reglamento Interno de Docencia de Pregrado de ésta, podrá establecer promedios o puntajes diferentes, respecto de los requisitos señalados en la letra b). Anualmente, las Facultades establecerán los cupos disponibles para los cambios de carrera, debiendo ofrecer al menos uno para cada carrera en el primer semestre. Las solicitudes, acompañadas de la documentación exigida deberán ser presentadas, dentro del periodo establecido por la Dirección de Docencia, en UDARAE la que recepcionará solamente aquellas solicitudes que cumplan con todos los requisitos. La resolución de las solicitudes corresponderá a una Comisión integrada por el Director de Docencia, el Decano de la Facultad, el Jefe de Carrera y deberá ser sancionada por el Rector de la Universidad de Concepción y registrada en el SAC por la Unidad de Admisión y Registro Académico Estudiantil.
- **[RG-ART-055]** Artículo 55° Los alumnos de la Universidad de Concepción, cualquiera sea la carrera que cursen, podrán solicitar su ingreso a otra carrera, siempre que cumplan con los siguientes requisitos: a) Ser alumno regular y conservar el derecho a continuar estudios en la carrera de origen. b) Haber obtenido en sus estudios, a lo menos, el promedio mínimo de calificaciones que se señale en el Reglamento Interno de Docencia de Pregrado de la Facultad a la cual postula. Anualmente, las Facultades establecerán los cupos disponibles para el mencionado ingreso. Las solicitudes, acompañadas de la documentación exigida deberán ser presentadas, dentro del período establecido por la Dirección de Docencia, en UDARAE la que recepcionará solamente aquellas solicitudes que cumplan con todos los requisitos. La resolución de las solicitudes corresponderá a una Comisión integrada por el Director de Docencia, el Decano de la Facultad, el Jefe de Carrera y deberá ser sancionada por el Rector de la Universidad de Concepción y registrada en el SAC por la Unidad de Admisión y Registro Académico Estudiantil.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-054] (cambio de carrera): ser alumno regular con derecho a continuar en origen, promedio mínimo de Facultad de destino (cuando es dentro de la misma Facultad, su Reglamento Interno puede fijar promedios o puntajes distintos); se debe ofrecer al menos 1 cupo por carrera en el primer semestre. [RG-ART-055] (ingreso a otra carrera): mismos requisitos y cupos anuales, sin regla especial de misma Facultad.
</pensar>
Respuesta: Tanto el cambio como el ingreso a otra carrera exigen ser alumno regular, conservar el derecho a continuar estudios en la carrera de origen, alcanzar al menos el promedio mínimo del Reglamento Interno de la Facultad receptora y postular dentro del período fijado por la Dirección de Docencia en UDARAE, sujeto a cupos anuales [RG-ART-054] [RG-ART-055].
Condiciones o límites: Para cambio de carrera, las Facultades deben ofrecer anualmente al menos un cupo para cada carrera en el primer semestre, y si el cambio ocurre dentro de la misma Facultad su reglamento puede establecer promedios o puntajes diferenciados; UDARAE solo recepciona solicitudes que cumplan todos los requisitos [RG-ART-054] [RG-ART-055].
Fuente: [RG-ART-054] [RG-ART-055]
```

## 09. `B2-V01` — bloque `condiciones_excepciones` | split `val` | modo `condicional` | estado `suficiente`

**Pregunta:** ¿Qué excepciones e información especial contempla el Reglamento General sobre cómo se asignan las asignaturas bajo un Programa de Bachillerato frente a una carrera de Licenciatura o Título?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-003-DEF-02`, `RG-ART-003-DEF-03`, `RG-ART-003-DEF-01`, `RG-ART-003-DEF-04`, `RG-ART-003-DEF-10`, `RG-ART-048`
- Clave esperada: `RG-ART-003-DEF-01, RG-ART-003-DEF-02` | Distractores incluidos: `RG-ART-003-DEF-03, RG-ART-003-DEF-04, RG-ART-003-DEF-10, RG-ART-048`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-003-DEF-01]** 3.1. CARRERA: La carrera es un programa de formación universitaria conducente a la obtención de un Grado Académico de Bachiller, de Licenciado o a un Título Profesional de acuerdo a un perfil de egreso establecido. Este programa comprende los objetivos, las competencias y las actividades de enseñanza-aprendizaje pertinentes que están contenidos en los respectivos Planes de Estudio de cada carrera. Las carreras podrán considerar en su estructura, Ciclos Básicos, Ciclos Disciplinarios conducentes a una Licenciatura y Ciclos Profesionales. Dos o más carreras pueden tener un Ciclo Básico Común. Una carrera tiene asociado siempre un Plan de Estudios. Una misma carrera puede dictarse en distintos campus, bajo distintas estructuras administrativas, pero deben garantizar competencias de egreso similares y sus Planes de Estudios deben ser similares. Para asegurar la pertinencia del Plan de Estudio es necesario que la carrera implemente los mecanismos de seguimiento de egresados y de vinculación con el medio, definidos por la Facultad, que permitan una efectiva retroalimentación desde la sociedad. El Bachillerato es un programa que permite lograr una formación universitaria básica, durante cuatro semestres, en las disciplinas que conforman una determinada área del conocimiento, desarrollando competencias tales como: la capacidad para organizar y planificar el tiempo, la capacidad de comunicación oral y escrita, y las habilidades en el uso de las tecnologías de la información y de la comunicación, en esa área del conocimiento.
- **[RG-ART-003-DEF-02]** 3.2. GRADO DE BACHILLER: Los estudios conducentes al grado de Bachiller permiten al alumno un desarrollo inicial general e integrado del conocimiento de diferentes campos del saber y su introducción en algunas disciplinas.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-003-DEF-01] define el Bachillerato como programa que logra formación universitaria básica durante cuatro semestres en disciplinas de un área del conocimiento (desarrollando organización del tiempo, comunicación oral/escrita y TIC). [RG-ART-003-DEF-02] señala que los estudios conducentes al grado de Bachiller permiten desarrollo inicial general e integrado e introducción en algunas disciplinas, mientras Licenciado/Título abarcan Ciclos Disciplinarios o Profesionales.
</pensar>
Respuesta: El Bachillerato es un programa de formación universitaria básica de cuatro semestres orientado a un desarrollo inicial general e integrado del conocimiento e introducción disciplinar, mientras las carreras conducentes a Licenciatura o Título Profesional pueden estructurarse además con Ciclos Disciplinarios y Ciclos Profesionales según su perfil de egreso [RG-ART-003-DEF-01] [RG-ART-003-DEF-02].
Condiciones o límites: Dos o más carreras pueden compartir un Ciclo Básico Común, y el Bachillerato debe desarrollar competencias en organización del tiempo, comunicación oral y escrita y uso de tecnologías de la información y comunicación en su área [RG-ART-003-DEF-01].
Fuente: [RG-ART-003-DEF-01] [RG-ART-003-DEF-02]
```

## 10. `B2-V05` — bloque `condiciones_excepciones` | split `val` | modo `condicional` | estado `suficiente`

**Pregunta:** ¿Qué diferencia las condiciones y documentación exigida para solicitar revalidación frente a convalidación de asignaturas aprobadas?

**Evidencia ensamblada (4 unidades, orden barajado):** `RG-ART-040`, `RG-ART-041`, `RG-ART-037`, `RI-FI-ART-015`
- Clave esperada: `RG-ART-037` | Distractores incluidos: `RG-ART-040, RG-ART-041, RI-FI-ART-015`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-037]** Artículo 37° Los alumnos regulares podrán solicitar la revalidación de una misma asignatura ya aprobada en otro plan de estudio de otra carrera de esta universidad. Los alumnos regulares podrán solicitar la convalidación de una asignatura de su plan de estudio por otra ya aprobada en ésta o en otra institución de educación superior. Esta solicitud deberá ir acompañada de un certificado completo de calificaciones y de los programas debidamente acreditados de las asignaturas aprobadas, salvo que se trate de asignaturas aprobadas en esta universidad. El Vicedecano, previo informe del Departamento a cargo de la asignatura, resolverá dentro de un plazo de quince días e informará de lo resuelto tanto al alumno como a la Facultad a la que éste pertenece.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-037]: la revalidación aplica a alumnos regulares para una misma asignatura ya aprobada en otro plan de otra carrera de la UdeC; la convalidación aplica a una asignatura del plan por otra aprobada en la UdeC u otra institución de educación superior. La convalidación exige certificado completo de calificaciones y programas debidamente acreditados, salvo asignaturas aprobadas en la UdeC. Resuelve el Vicedecano en 15 días previo informe del Departamento a cargo.
</pensar>
Respuesta: Solo pueden pedirlas alumnos regulares: la revalidación cubre una misma asignatura aprobada en otra carrera de la UdeC, mientras la convalidación cubre una equivalente cursada en la UdeC u otra institución superior, exigiendo certificado de calificaciones y programas acreditados [RG-ART-037].
Condiciones o límites: La acreditación de programas no se exige si las asignaturas se aprobaron en la propia UdeC; en todo caso el Vicedecano resuelve en 15 días previo informe del Departamento a cargo e informa al alumno y su Facultad [RG-ART-037].
Fuente: [RG-ART-037]
```

## 11. `B3-T01` — bloque `polares_y_lectura` | split `train` | modo `condicional` | estado `suficiente`

**Pregunta:** Si un estudiante inscribe una asignatura en el PLEV y luego decide retirarse dentro de las primeras tres semanas, ¿puede hacer abandono sin especificación de motivos?

**Evidencia ensamblada (4 unidades, orden barajado):** `RG-ART-045`, `RG-ART-042`, `RG-ART-022`, `RG-ART-043`
- Clave esperada: `RG-ART-043` | Distractores incluidos: `RG-ART-045, RG-ART-042, RG-ART-022`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-043]** Artículo 43º El alumno podrá hacer abandono de asignaturas semestrales o anuales, sin especificación de motivos, para lo cual tendrá un plazo de cuatro semanas a contar de la fecha del inicio de clases establecida en el Calendario de Docencia de Pregrado. Esta facultad podrá ser utilizada por el alumno una sola vez en cada asignatura siempre que no quede con un número de créditos inferior al mínimo establecido. No obstante lo anterior, en el caso de asignaturas de duración menor a un semestre, la Facultad que dicta la asignatura establecerá el plazo de abandono. Los alumnos no podrán hacer abandono de asignaturas inscritas en el PLEV.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Pregunta polar con excepción expresa en [RG-ART-043]. Aunque la regla general permite abandonar asignaturas semestrales o anuales en 4 semanas, el inciso final de [RG-ART-043] lo prohíbe expresamente para asignaturas inscritas en el PLEV. Debo responder directamente 'No' sin contradecirme.
</pensar>
Respuesta: No, el estudiante no puede hacer abandono de una asignatura inscrita en el PLEV [RG-ART-043].
Condiciones o límites: La facultad de abandono dentro de cuatro semanas desde el inicio de clases (por una sola vez y sin quedar bajo el mínimo de créditos) rige para asignaturas semestrales o anuales (o el plazo que fije la Facultad si duran menos de un semestre), pero excluye expresamente a las asignaturas inscritas en el PLEV [RG-ART-043].
Fuente: [RG-ART-043]
```

## 12. `B3-T16` — bloque `polares_y_lectura` | split `train` | modo `factual` | estado `suficiente`

**Pregunta:** ¿Por cuántos días hábiles como mínimo debe conservar el profesor las evaluaciones escritas realizadas después de terminado el período académico correspondiente?

**Evidencia ensamblada (4 unidades, orden barajado):** `RG-ART-027`, `RG-ART-019`, `RG-ART-025`, `RG-ART-013`
- Clave esperada: `RG-ART-025` | Distractores incluidos: `RG-ART-027, RG-ART-019, RG-ART-013`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-025]** Artículo 25º La evaluación forma parte del proceso de enseñanza - aprendizaje. Por ello los alumnos tendrán derecho a recibir sus instrumentos de evaluación escritos corregidos, a aclarar sus dudas ante el profesor y a conocer por medios escritos, electrónicos u otros las pautas de corrección de aquellos. Los profesores deberán dar a conocer las calificaciones y pautas de corrección a los alumnos en un plazo máximo de diez días hábiles y los alumnos tendrán un plazo de cinco días hábiles para ejercer el derecho señalado. Sin embargo, el Vicedecano por razones justificadas podrá ampliar dichos plazos. El profesor deberá conservar las evaluaciones escritas realizadas a lo menos por 30 días hábiles después de concluido el periodo académico correspondiente. En el momento de informar las calificaciones, el Profesor de la Asignatura, comunicará las fechas y el horario de la revisión de las evaluaciones. Si luego de la revisión existiera desacuerdo con la calificación, o en el caso de alguna situación de las señaladas en el artículo 13, el alumno podrá solicitar por escrito y fundamentadamente una nueva revisión ante el Vicedecano de la Facultad responsable de la asignatura. Lo anterior deberá efectuarse en un plazo máximo de cinco días hábiles, a contar de la fecha en que se realizó la revisión ante el profesor. El Vicedecano, si estima fundamentada la solicitud, nombrará una Comisión ad hoc, la que recopilará los antecedentes correspondientes y analizará la situación. Esta comisión deberá resolver en el plazo de 10 días corridos a contar desde aquél en que se presentó la reclamación, haciendo constar su decisión inapelable en un acta y comunicándola en forma personal al alumno, dejando constancia de ello a través de la firma de éste.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-025] párrafo tercero dispone literalmente: 'El profesor deberá conservar las evaluaciones escritas realizadas a lo menos por 30 días hábiles después de concluido el periodo académico correspondiente.' Pregunta factual sobre un único plazo sin excepciones en ese párrafo -> Condiciones o límites: No aplica.
</pensar>
Respuesta: El profesor debe conservar las evaluaciones escritas a lo menos por 30 días hábiles después de concluido el período académico correspondiente [RG-ART-025].
Condiciones o límites: No aplica
Fuente: [RG-ART-025]
```

## 13. `B3-T30` — bloque `polares_y_lectura` | split `train` | modo `premisa_falsa` | estado `suficiente`

**Pregunta:** Para pedir una modificación de un Acta de Notas ya ingresada en el SAC basta con que el Profesor Encargado la envíe dentro de los dos años siguientes al semestre calificado. ¿Es así?

**Evidencia ensamblada (4 unidades, orden barajado):** `RG-ART-013`, `RG-ART-027`, `RG-ART-025`, `RG-ART-003-DEF-05`
- Clave esperada: `RG-ART-027` | Distractores incluidos: `RG-ART-013, RG-ART-025, RG-ART-003-DEF-05`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-027]** Artículo 27º En el Acta de Notas de la asignatura se consignará la Nota Final, que corresponderá al Promedio Ponderado de las calificaciones obtenidas por el alumno, incluida la Evaluación de Recuperación cuando corresponda. Para generar el Acta de Notas en el SAC, las Notas Finales deberán ser registradas y grabadas por el Profesor Encargado de la Asignatura mediante el programa informático INFODA o cualquier otra aplicación informática que se desarrolle en el futuro en la universidad. Un ejemplar impreso de ésta será firmado por los miembros de la Comisión de Evaluación y el Director del Departamento correspondiente o el Vicedecano de la Facultad en el caso de asignaturas que no dependan de algún Departamento, quedando el original archivado en la Secretaría Académica de la Facultad. La solicitud de modificación de un Acta de Notas, requerirá del visto bueno del Vicedecano de la Facultad que dicta la asignatura. Una vez aprobada la modificación, los miembros de la Comisión de Evaluación y el Director del Departamento correspondiente firmarán un Acta de Modificación que será ingresada al SAC por la respectiva Secretaría Académica, a más tardar antes, del término del semestre siguiente al que calificó la asignatura

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-027] párrafo 3: requiere visto bueno del Vicedecano de la Facultad que dicta la asignatura, firma del Acta de Modificación por la Comisión de Evaluación y el Director de Departamento, e ingreso al SAC por Secretaría Académica a más tardar antes del término del semestre siguiente al que calificó la asignatura (no dos años).
</pensar>
Respuesta: No es así: modificar un Acta de Notas requiere visto bueno del Vicedecano de la Facultad que dicta la asignatura, firma de la Comisión de Evaluación y el Director de Departamento, y su ingreso al SAC por Secretaría Académica debe hacerse a más tardar antes del término del semestre siguiente al calificado [RG-ART-027].
Condiciones o límites: No basta con la sola gestión del Profesor Encargado ni rige un plazo de dos años [RG-ART-027].
Fuente: [RG-ART-027]
```

## 14. `B3-V01` — bloque `polares_y_lectura` | split `val` | modo `factual` | estado `suficiente`

**Pregunta:** Según las equivalencias del Anexo del Reglamento General, ¿a qué nota en escala 1,0 a 7,0 equivale el puntaje de aprobación mínimo 51 en la escala de 1 a 100?

**Evidencia ensamblada (4 unidades, orden barajado):** `RG-ART-021`, `RG-ANEXO-02`, `RG-ANEXO-01`, `RG-ANEXO-10`
- Clave esperada: `RG-ANEXO-01` | Distractores incluidos: `RG-ART-021, RG-ANEXO-02, RG-ANEXO-10`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ANEXO-01]** Anexo: equivalencia de escalas de notas. Reprobación: 1 en escala de 1 a 100 equivale a 1,0 en escala de 1,0 a 7,0. Aprobación: 51 en escala de 1 a 100 equivale a 4,0 en escala de 1,0 a 7,0. La celda de concepto está vacía en el documento.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ANEXO-01] señala literalmente: 'Aprobación: 51 en escala de 1 a 100 equivale a 4,0 en escala de 1,0 a 7,0. La celda de concepto está vacía en el documento.' No inventar concepto donde la celda está vacía ni agregar condiciones -> Condiciones o límites: No aplica.
</pensar>
Respuesta: El puntaje de aprobación 51 en la escala de 1 a 100 equivale a 4,0 en la escala de 1,0 a 7,0 [RG-ANEXO-01].
Condiciones o límites: No aplica
Fuente: [RG-ANEXO-01]
```

## 15. `B3-V05` — bloque `polares_y_lectura` | split `val` | modo `condicional` | estado `suficiente`

**Pregunta:** Si en una carrera no existen profesores de otras Facultades que puedan integrar su Consejo de Carrera, ¿queda ese Consejo con menos integrantes o debe sustituirse esos cupos?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-009`, `RI-FI-ART-033`, `RI-FI-ART-032`, `RG-ART-010`, `RG-ART-011`, `RG-ART-008`
- Clave esperada: `RG-ART-009` | Distractores incluidos: `RI-FI-ART-033, RI-FI-ART-032, RG-ART-010, RG-ART-011, RG-ART-008`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-009]** Artículo 9º En cada carrera que se dicte en cada campus de la universidad existirá un Consejo de Carrera que velará por el cumplimiento de los objetivos, evaluará los resultados y conocerá cualquier problema de funcionamiento de la carrera. Se encargará de diseñar las políticas de desarrollo de la carrera y de su proyección, así como de la pertinencia de los planes de estudios. También tendrá como misión velar por la calidad de la formación y participar en los procesos de acreditación. La constitución y la duración del Consejo de Carrera se establecerán en el Reglamento Interno de Docencia de Pregrado de cada Facultad. Estará integrado por el Jefe de Carrera, quien lo preside, por un mínimo de tres profesores de la Facultad adscritos a la carrera, un mínimo de dos profesores de otras Facultades que contribuyan significativamente al desarrollo de la carrera y por tres y hasta cuatro representantes estudiantiles de la carrera, con derecho a voz y voto. En aquellos casos en que no existan profesores de otras Facultades, lo integrarán, en su reemplazo, otros dos profesores de la propia Facultad. De acuerdo con la temática objeto de la reunión, el Jefe de Carrera podrá invitar a otros académicos, expertos en el tema, egresados o empleadores. En todos los casos, los invitados especiales tendrán derecho a voz, pero no a voto. Para efectos prácticos, en cada campus y en cada carrera, se constituirá un Consejo de Carrera, sin perjuicio de la existencia de un Consejo de Carrera a nivel de universidad en el caso de una misma carrera que se ofrece en más de un campus.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-009]: 'En aquellos casos en que no existan profesores de otras Facultades, lo integrarán, en su reemplazo, otros dos profesores de la propia Facultad'.
</pensar>
Respuesta: No queda incompleto: si no existen profesores de otras Facultades que contribuyan significativamente a la carrera, esos cupos deben integrarse en su reemplazo con otros dos profesores de la propia Facultad [RG-ART-009].
Condiciones o límites: Además del reemplazo indicado, la composición general incluye al Jefe de Carrera (presidente), al menos tres profesores de la Facultad y entre tres y cuatro representantes estudiantiles con voz y voto [RG-ART-009].
Fuente: [RG-ART-009]
```

## 16. `B4-T01` — bloque `calculos_y_orden` | split `train` | modo `numerica` | estado `suficiente`

**Pregunta:** Según el Calendario de Docencia de Pregrado 2026, ¿cuántos días corridos inclusive duran las actividades de Vinculación a la Vida Universitaria y cuántos días inclusive suman con las vacaciones de invierno del primer semestre?

**Evidencia ensamblada (5 unidades, orden barajado):** `CAL-2026-S1-05`, `CAL-2026-S1-14`, `CAL-2026-S1-01`, `CAL-2026-S1-04`, `CAL-2026-S1-06`
- Clave esperada: `CAL-2026-S1-01, CAL-2026-S1-14` | Distractores incluidos: `CAL-2026-S1-05, CAL-2026-S1-04, CAL-2026-S1-06`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[CAL-2026-S1-01]** Calendario de docencia de pregrado 2026. Primer semestre. Vinculación a la Vida Universitaria: "Actividades de bienvenida y de inducción a la UdeC": 02 – 06 de marzo.
- **[CAL-2026-S1-14]** Calendario de docencia de pregrado 2026. Primer semestre. Vacaciones de invierno (aprobación transitoria): 30 junio – 05 de julio.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[CAL-2026-S1-01] fija Vinculación a la Vida Universitaria del 02 al 06 de marzo: 6 - 2 + 1 = 5 días inclusive. [CAL-2026-S1-14] fija Vacaciones de invierno del 30 de junio al 05 de julio: 1 día de junio (30) + 5 días de julio (1 al 5) = 6 días inclusive. Suma total: 5 + 6 = 11 días. Nota sobre aprobación transitoria de vacaciones de invierno como único límite aplicable.
</pensar>
Respuesta: La Vinculación a la Vida Universitaria (02 al 06 de marzo) dura 5 días inclusive [CAL-2026-S1-01] y las vacaciones de invierno (30 de junio al 05 de julio) duran 6 días inclusive [CAL-2026-S1-14]; entre ambos suman 5 + 6 = 11 días.
Condiciones o límites: Las vacaciones de invierno de 30 de junio al 05 de julio se encuentran con aprobación transitoria en el calendario [CAL-2026-S1-14].
Fuente: [CAL-2026-S1-01] [CAL-2026-S1-14]
```

## 17. `B4-T16` — bloque `calculos_y_orden` | split `train` | modo `numerica` | estado `suficiente`

**Pregunta:** Un Consejo de Carrera de Ingeniería está compuesto por 13 integrantes en total. ¿Cuántos integrantes deben asistir como mínimo para poder sesionar y qué proporción mínima debe solicitar una sesión extraordinaria?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-008`, `RI-FI-ART-032`, `RG-ART-011`, `RG-ART-010`, `RI-FI-ART-033`, `RG-ART-009`
- Clave esperada: `RG-ART-010` | Distractores incluidos: `RG-ART-008, RI-FI-ART-032, RG-ART-011, RI-FI-ART-033, RG-ART-009`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-010]** Artículo 10° El Consejo de Carrera deberá sesionar al menos tres veces cada semestre, pudiendo existir reuniones extraordinarias solicitadas por acuerdo del 60% de los miembros, en horarios que faciliten la asistencia de los alumnos. Para sesionar se requerirá la presencia de al menos el 60% de los miembros y para tomar acuerdos se requerirá el voto conforme de la mayoría de los miembros asistentes, debiendo llevarse registro de la asistencia. Si un representante estudiantil tiene dos ausencias consecutivas sin justificación será reemplazado y si se trata de un académico recibirá un llamado de atención por escrito. La calendarización de estas reuniones se hará semestralmente por el Jefe de Carrera, quien la comunicará con la debida anticipación a cada miembro, al Vicedecano de la Facultad y al Director de Docencia. La convocatoria la hará el Jefe de Carrera, con al menos una semana de antelación, y en ésta se deberá incluir la Tabla de puntos a tratar. Los integrantes del Consejo, el Director de Docencia y el Vicedecano podrán pedir al Jefe de Carrera la incorporación de puntos a la tabla hasta el día previo al envío de la convocatoria. De las sesiones se levantará un Acta de Acuerdos, que el Jefe de Carrera deberá enviar a los integrantes, al Vicedecano y al Director de Docencia. El Consejo de Carrera podrá solicitar a la Dirección de Docencia participar o tomar medidas en algún tema en especial, relacionado con el funcionamiento de la carrera. Sus funciones específicas, sin perjuicio de otras que podrán incluirse en los Reglamentos Internos de Docencia de cada Facultad, serán las siguientes: a) Evaluar el cumplimiento del Plan de Estudios de la carrera. b) Verificar la actualización de los syllabus de las asignaturas. c) Actualizar la pertinencia de requisitos y correquisitos de las asignaturas. d) Evaluar los resultados obtenidos por los alumnos. e) Revisar las metodologías de aprendizaje utilizadas. f) Definir los criterios académicos para el reconocimiento de asignaturas a los alumnos provenientes de otras instituciones de educación superior. g) Pronunciarse, en primera instancia y participar en la modificación del Plan de Estudio de la carrera, para lo cual se podrá constituir una comisión especial. h) Participar en los Procesos de Autoevaluación de la carrera así como en los procesos de acreditación. i) Supervisar el cumplimiento de los objetivos estratégicos de la carrera informando de ello a las instancias correspondientes. j) Analizar los resultados de la Evaluación Docente de los profesores de la carrera realizada por los alumnos k) Nominar a los miembros del Comité de Docencia y Asuntos Estudiantiles de la carrera. Para el mejor desarrollo de estas funciones, el Jefe de Carrera requerirá, cuando corresponda, a través del Decano, la coordinación con los Directores de Departamento que participan en la carrera, cautelando el cumplimiento de lo dispuesto en el primer párrafo del Artículo 57 de los Estatutos de la Corporación.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-010]: quórum para sesionar >= 60 %; sesiones extraordinarias solicitadas por acuerdo del 60 %. Cálculo: 0,60 × 13 = 7,8. Como el número de miembros asistentes debe ser entero y al menos el 60 % (7 < 7,8 = 53,8 %), se necesitan al menos 8 miembros.
</pensar>
Respuesta: Deben asistir como mínimo 8 integrantes (60 % de 13 es 7,8, por lo que al menos 8 cumplen el mínimo) para sesionar, y las sesiones extraordinarias requieren acuerdo del 60 % de los miembros (igualmente al menos 8 de 13) [RG-ART-010].
Condiciones o límites: Cálculo: 13 × 0,60 = 7,8 -> mínimo entero >= 60 % es 8 miembros (8/13 = 61,5 %; 7/13 = 53,8 %); los acuerdos se toman por mayoría de los asistentes [RG-ART-010].
Fuente: [RG-ART-010]
```

## 18. `B4-T30` — bloque `calculos_y_orden` | split `train` | modo `numerica` | estado `suficiente`

**Pregunta:** En la escala de aprobación 1–100 del Anexo, ¿a qué nota de 1,0 a 7,0 y concepto equivalen 65, 85 y 95 puntos, y cuántas décimas de diferencia hay entre los dos primeros y entre los dos últimos?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ANEXO-45`, `RG-ANEXO-44`, `RG-ANEXO-15`, `RG-ANEXO-36`, `RG-ANEXO-35`, `RG-ANEXO-16`
- Clave esperada: `RG-ANEXO-15, RG-ANEXO-35, RG-ANEXO-45` | Distractores incluidos: `RG-ANEXO-44, RG-ANEXO-36, RG-ANEXO-16`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ANEXO-15]** Anexo: equivalencia de escalas de notas. Reprobación: 15 en escala de 1 a 100 equivale a 1,8 en escala de 1,0 a 7,0. Aprobación: 65 en escala de 1 a 100 equivale a 4,8 en escala de 1,0 a 7,0. Concepto en el título o grado: Aprobado por Unanimidad.
- **[RG-ANEXO-35]** Anexo: equivalencia de escalas de notas. Reprobación: 35 en escala de 1 a 100 equivale a 3,1 en escala de 1,0 a 7,0. Aprobación: 85 en escala de 1 a 100 equivale a 6,4 en escala de 1,0 a 7,0. Concepto en el título o grado: Aprobado con Distinción.
- **[RG-ANEXO-45]** Anexo: equivalencia de escalas de notas. Reprobación: 45 en escala de 1 a 100 equivale a 3,6 en escala de 1,0 a 7,0. Aprobación: 95 en escala de 1 a 100 equivale a 7,0 en escala de 1,0 a 7,0. Concepto en el título o grado: Aprobado con Distinción Máxima.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ANEXO-15]: 65 -> 4,8 ('Aprobado por Unanimidad'). [RG-ANEXO-35]: 85 -> 6,4 ('Aprobado con Distinción'). [RG-ANEXO-45]: 95 -> 7,0 ('Aprobado con Distinción Máxima'). Diferencias: 6,4 - 4,8 = 1,6 puntos (16 décimas); 7,0 - 6,4 = 0,6 puntos (6 décimas). Lectura y resta directas -> No aplica.
</pensar>
Respuesta: 65 equivale a 4,8 ('Aprobado por Unanimidad') [RG-ANEXO-15], 85 a 6,4 ('Aprobado con Distinción') [RG-ANEXO-35] y 95 a 7,0 ('Aprobado con Distinción Máxima') [RG-ANEXO-45]; entre 65 y 85 hay 1,6 puntos (16 décimas) y entre 85 y 95 hay 0,6 puntos (6 décimas).
Condiciones o límites: No aplica
Fuente: [RG-ANEXO-15] [RG-ANEXO-35] [RG-ANEXO-45]
```

## 19. `B4-V01` — bloque `calculos_y_orden` | split `val` | modo `numerica` | estado `suficiente`

**Pregunta:** En las filas de reprobación de la escala 1 a 100 del Anexo, ¿a qué calificaciones en escala 1,0 a 7,0 equivalen 5 y 31 puntos, y cuál es la diferencia entre ambas notas?

**Evidencia ensamblada (5 unidades, orden barajado):** `RG-ANEXO-30`, `RG-ANEXO-04`, `RG-ANEXO-05`, `RG-ANEXO-32`, `RG-ANEXO-31`
- Clave esperada: `RG-ANEXO-05, RG-ANEXO-31` | Distractores incluidos: `RG-ANEXO-30, RG-ANEXO-04, RG-ANEXO-32`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ANEXO-05]** Anexo: equivalencia de escalas de notas. Reprobación: 5 en escala de 1 a 100 equivale a 1,2 en escala de 1,0 a 7,0. Aprobación: 55 en escala de 1 a 100 equivale a 4,2 en escala de 1,0 a 7,0. La celda de concepto está vacía en el documento.
- **[RG-ANEXO-31]** Anexo: equivalencia de escalas de notas. Reprobación: 31 en escala de 1 a 100 equivale a 2,8 en escala de 1,0 a 7,0. Aprobación: 81 en escala de 1 a 100 equivale a 6,2 en escala de 1,0 a 7,0. Concepto en el título o grado: Aprobado con Distinción.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ANEXO-05]: reprobación 5 -> 1,2. [RG-ANEXO-31]: reprobación 31 -> 2,8. Diferencia: 2,8 - 1,2 = 1,6 puntos en escala 1,0 a 7,0. Cálculo directo sin condiciones adicionales -> No aplica.
</pensar>
Respuesta: En escala de reprobación, 5 puntos equivalen a 1,2 [RG-ANEXO-05] y 31 puntos a 2,8 [RG-ANEXO-31], lo que arroja una diferencia de 2,8 - 1,2 = 1,6 puntos en escala de 1,0 a 7,0.
Condiciones o límites: No aplica
Fuente: [RG-ANEXO-05] [RG-ANEXO-31]
```

## 20. `B4-V05` — bloque `calculos_y_orden` | split `val` | modo `numerica` | estado `suficiente`

**Pregunta:** Un curso de 10 créditos transferibles (SCT) equivale exactamente a cuántas horas de trabajo académico total según el Reglamento General, y qué diferencia hay frente a un crédito UdeC de clase práctica semanal?

**Evidencia ensamblada (5 unidades, orden barajado):** `RG-ART-003-DEF-12`, `RG-ART-003-DEF-08`, `RG-ART-003-DEF-11`, `RG-ART-003-DEF-06`, `RG-ART-003-DEF-07`
- Clave esperada: `RG-ART-003-DEF-08, RG-ART-003-DEF-07` | Distractores incluidos: `RG-ART-003-DEF-12, RG-ART-003-DEF-11, RG-ART-003-DEF-06`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-003-DEF-08]** 3.8. CRÉDITO TRANSFERIBLE (SCT): Crédito Transferible es la unidad de medida común y transferible entre instituciones de educación superior, que representa la carga de trabajo académico de un alumno, que incluye tanto las horas de docencia directa (o presenciales) como las horas de trabajo autónomo (no presenciales) para lograr los resultados de aprendizaje y el perfil de egreso de un plan de estudio. Se asigna (1 SCT) crédito transferible a 27 horas de trabajo, presencial y no presencial.
- **[RG-ART-003-DEF-07]** 3.7. CRÉDITO: Crédito es la unidad de medida de la docencia de una asignatura. Un crédito corresponde a una hora docente de clase teórica y a dos o tres horas docentes de prácticas, laboratorios o seminarios semanales por el período correspondiente a un semestre lectivo ordinario. Los créditos de las asignaturas que se dicten en un período inferior o superior al semestre, se determinarán proporcionalmente a éste, expresado en números enteros. La medida del Trabajo Académico de la asignatura corresponde a las horas de docencia directa más las correspondientes a las actividades indirectas o complementarias realizadas por el alumno fuera del horario programado para la docencia directa durante una semana. Un alumno a tiempo completo debe dedicar a su trabajo académico entre 45 y 54 horas semanales durante el periodo lectivo establecido en el Calendario de Docencia de Pregrado.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-003-DEF-08]: 1 SCT = 27 horas -> 10 × 27 = 270 horas (presencial y no presencial). [RG-ART-003-DEF-07]: un crédito UdeC corresponde a 1 hora docente de clase teórica o a 2 a 3 horas docentes de prácticas, laboratorios o seminarios semanales durante un semestre lectivo ordinario.
</pensar>
Respuesta: Un curso de 10 SCT equivale a 270 horas totales de trabajo presencial y no presencial [RG-ART-003-DEF-08]; en contraste, un crédito UdeC mide horas docentes semanales por semestre y equivale a una hora docente teórica o a dos o tres horas docentes de prácticas, laboratorios o seminarios [RG-ART-003-DEF-07].
Condiciones o límites: Cálculo: 10 SCT × 27 horas = 270 horas [RG-ART-003-DEF-08]; los créditos de asignaturas de duración distinta a un semestre se determinan proporcionalmente en números enteros [RG-ART-003-DEF-07].
Fuente: [RG-ART-003-DEF-07] [RG-ART-003-DEF-08]
```

## 21. `B5-T01` — bloque `resiliencia_feedback` | split `train` | modo `factual` | estado `suficiente`

**Pregunta:** ¿Cuántos minutos reales dura una Hora Docente en la Universidad de Concepción?

**Observaciones del Verificador (entrada):** El borrador anterior responde 45 minutos correctamente, pero agrega en 'Condiciones o límites' detalles sobre créditos teóricos y semanales que corresponden a otro artículo y no fueron consultados. Limítate al dato preguntado e indica 'No aplica' en condiciones.

**Evidencia ensamblada (4 unidades, orden barajado):** `RG-ART-003-DEF-06`, `RG-ART-003-DEF-07`, `RG-ART-019`, `RG-ART-003-DEF-08`
- Clave esperada: `RG-ART-003-DEF-06` | Distractores incluidos: `RG-ART-003-DEF-07, RG-ART-019, RG-ART-003-DEF-08`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-003-DEF-06]** 3.6. HORA DOCENTE: Una hora docente corresponde a una sesión de docencia de 45 minutos.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Atendiendo la observación del verificador, consulto únicamente [RG-ART-003-DEF-06]: 'Una hora docente corresponde a una sesión de docencia de 45 minutos.' No añado explicaciones de créditos ni carga semanal -> Condiciones o límites: No aplica.
</pensar>
Respuesta: Una hora docente corresponde a una sesión de docencia de 45 minutos [RG-ART-003-DEF-06].
Condiciones o límites: No aplica
Fuente: [RG-ART-003-DEF-06]
```

## 22. `B5-T13` — bloque `resiliencia_feedback` | split `train` | modo `factual` | estado `suficiente`

**Pregunta:** Según el Anexo de equivalencia de escalas de notas, ¿a qué calificación en escala de 1,0 a 7,0 equivale exactamente una nota de aprobación de 80 puntos en escala de 1 a 100?

**Observaciones del Verificador (entrada):** El borrador respondió '6,1' bien, pero inventó condiciones sobre promedio ponderado y recuperación que no aparecen en [RG-ANEXO-30]. Responde solo el dato y pon 'No aplica'.

**Evidencia ensamblada (4 unidades, orden barajado):** `RG-ANEXO-30`, `RG-ANEXO-31`, `RG-ART-048`, `RG-ANEXO-29`
- Clave esperada: `RG-ANEXO-30` | Distractores incluidos: `RG-ANEXO-31, RG-ART-048, RG-ANEXO-29`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ANEXO-30]** Anexo: equivalencia de escalas de notas. Reprobación: 30 en escala de 1 a 100 equivale a 2,7 en escala de 1,0 a 7,0. Aprobación: 80 en escala de 1 a 100 equivale a 6,1 en escala de 1,0 a 7,0. Concepto en el título o grado: Aprobado con Distinción.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ANEXO-30] dice literalmente: 'Aprobación: 80 en escala de 1 a 100 equivale a 6,1 en escala de 1,0 a 7,0. Concepto en el título o grado: Aprobado con Distinción.' La pregunta pide la calificación en escala 1,0 a 7,0: 6,1. No debo inventar reglas de promedio ni recuperación -> Condiciones o límites: No aplica.
</pensar>
Respuesta: Una calificación de aprobación de 80 en escala de 1 a 100 equivale a 6,1 en la escala de 1,0 a 7,0 [RG-ANEXO-30].
Condiciones o límites: No aplica
Fuente: [RG-ANEXO-30]
```

## 23. `B5-T25` — bloque `resiliencia_feedback` | split `train` | modo `condicional` | estado `suficiente`

**Pregunta:** ¿Qué condiciones aplican cuando un alumno quiere inscribir asignaturas que requieren cumplimiento de prerrequisitos y además desea tomar dos cursos que coinciden el mismo día y hora?

**Observaciones del Verificador (entrada):** El borrador respondió solo sobre el choque horario y omitió las consecuencias de incumplir prerrequisitos y de no haber respondido la Encuesta Docente.

**Evidencia ensamblada (5 unidades, orden barajado):** `RI-FI-ART-007`, `RG-ART-014`, `RG-ART-003-DEF-13`, `RG-ART-007`, `RG-ART-042`
- Clave esperada: `RG-ART-042, RG-ART-014` | Distractores incluidos: `RI-FI-ART-007, RG-ART-003-DEF-13, RG-ART-007`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-042]** Artículo 42º La inscripción de asignaturas deberá realizarse en las fechas indicadas por el Calendario de Docencia de Pregrado. En el caso de los alumnos que ingresan a una carrera, la inscripción de asignaturas será parte del proceso de matrícula. El Vicedecano podrá autorizar, en casos justificados y excepcionales, modificaciones de inscripción o admitir las que estén fuera de plazo. El alumno deberá inscribir y cursar un número de créditos igual o superior al mínimo por semestre que indique el Reglamento Interno de la Facultad a la cual está adscrito. El Vicedecano podrá autorizar una inscripción menor cuando la oferta de créditos es inferior a ese mínimo, debido a la situación curricular personal del alumno y de los prerrequisitos de su plan de estudio. En el caso que el alumno que esté terminando sus estudios, podrá inscribir sólo las asignaturas que le falte cursar. Para inscribir una asignatura, el alumno deberá cumplir con los prerrequisitos y exigencias establecidas. En caso contrario la inscripción quedará sin efecto. Las Facultades cautelarán el cumplimiento de estas normas. Para inscribir asignaturas, el alumno deberá haber respondido la Encuesta de Evaluación de la Docencia de las asignaturas cursadas en el periodo lectivo anterior. El alumno no deberá inscribir asignaturas con actividades académicas obligatorias, que estén programadas en horarios coincidentes.
- **[RG-ART-014]** Artículo 14º La función de coordinación de horarios consistirá en la confección de horarios, asignación y control del uso de salas y la coordinación con la Dirección de Docencia de la asignación de salas de uso centralizado. La Dirección de Docencia será responsable respecto de la utilización de las aulas de uso centralizadas. En el caso del Campus Chillán y del Campus Los Ángeles las atribuciones que se entregan en este artículo a la Dirección de Docencia, serán ejercidas por el Director General del campus correspondiente. Con este propósito y para anticipar la programación referida, previo al inicio de cada período lectivo, las Facultades, a través del Secretario Académico, deberán informar a la Dirección de Docencia sobre el uso de las aulas que administra cada Facultad y la disponibilidad de las mismas para su utilización por otras carreras, en el período siguiente. Si durante el desarrollo del período lectivo, a un alumno, por razones justificadas, se le programa en forma simultánea (mismo día y horario) actividades académicas que sean requisitos de alguna asignatura, éste deberá priorizar la actividad académica que no tiene posibilidad de ser recuperada y tendrá derecho a recuperar la no efectuada. El Jefe de Carrera velará por ello e informará a los profesores encargados involucrados.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-042] cubre todo lo de inscripción: cumplir prerrequisitos (de lo contrario la inscripción queda sin efecto), haber respondido Encuesta Docente del período anterior, y no inscribir asignaturas con actividades obligatorias programadas en horarios coincidentes. [RG-ART-014] además regula el caso excepcional posterior donde por razones justificadas se programan actividades simultáneas.
</pensar>
Respuesta: No puede inscribir asignaturas que tengan actividades obligatorias programadas en horarios coincidentes, y si incumple los prerrequisitos exigidos la inscripción queda sin efecto [RG-ART-042].
Condiciones o límites: Además debe haber respondido la Encuesta de Evaluación Docente del período lectivo anterior [RG-ART-042]; si ya inscritas las asignaturas se programaran por razones justificadas actividades simultáneas, debe priorizar la no recuperable y recuperar la otra [RG-ART-014].
Fuente: [RG-ART-014] [RG-ART-042]
```

## 24. `B5-V01` — bloque `resiliencia_feedback` | split `val` | modo `cruce` | estado `suficiente`

**Pregunta:** ¿Quién debe resguardar la coordinación de horarios y aulas centralizadas en Concepción y qué plazo o condición tiene un profesor para entregar notas y responder dudas?

**Observaciones del Verificador (entrada):** El borrador anterior mencionó los 10 días hábiles de entrega de notas citando únicamente [RG-ART-014], donde ese plazo no aparece.

**Evidencia ensamblada (5 unidades, orden barajado):** `RG-ART-034`, `RG-ART-025`, `RG-ART-014`, `RG-ART-006`, `RG-ART-033`
- Clave esperada: `RG-ART-014, RG-ART-025` | Distractores incluidos: `RG-ART-034, RG-ART-006, RG-ART-033`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-014]** Artículo 14º La función de coordinación de horarios consistirá en la confección de horarios, asignación y control del uso de salas y la coordinación con la Dirección de Docencia de la asignación de salas de uso centralizado. La Dirección de Docencia será responsable respecto de la utilización de las aulas de uso centralizadas. En el caso del Campus Chillán y del Campus Los Ángeles las atribuciones que se entregan en este artículo a la Dirección de Docencia, serán ejercidas por el Director General del campus correspondiente. Con este propósito y para anticipar la programación referida, previo al inicio de cada período lectivo, las Facultades, a través del Secretario Académico, deberán informar a la Dirección de Docencia sobre el uso de las aulas que administra cada Facultad y la disponibilidad de las mismas para su utilización por otras carreras, en el período siguiente. Si durante el desarrollo del período lectivo, a un alumno, por razones justificadas, se le programa en forma simultánea (mismo día y horario) actividades académicas que sean requisitos de alguna asignatura, éste deberá priorizar la actividad académica que no tiene posibilidad de ser recuperada y tendrá derecho a recuperar la no efectuada. El Jefe de Carrera velará por ello e informará a los profesores encargados involucrados.
- **[RG-ART-025]** Artículo 25º La evaluación forma parte del proceso de enseñanza - aprendizaje. Por ello los alumnos tendrán derecho a recibir sus instrumentos de evaluación escritos corregidos, a aclarar sus dudas ante el profesor y a conocer por medios escritos, electrónicos u otros las pautas de corrección de aquellos. Los profesores deberán dar a conocer las calificaciones y pautas de corrección a los alumnos en un plazo máximo de diez días hábiles y los alumnos tendrán un plazo de cinco días hábiles para ejercer el derecho señalado. Sin embargo, el Vicedecano por razones justificadas podrá ampliar dichos plazos. El profesor deberá conservar las evaluaciones escritas realizadas a lo menos por 30 días hábiles después de concluido el periodo académico correspondiente. En el momento de informar las calificaciones, el Profesor de la Asignatura, comunicará las fechas y el horario de la revisión de las evaluaciones. Si luego de la revisión existiera desacuerdo con la calificación, o en el caso de alguna situación de las señaladas en el artículo 13, el alumno podrá solicitar por escrito y fundamentadamente una nueva revisión ante el Vicedecano de la Facultad responsable de la asignatura. Lo anterior deberá efectuarse en un plazo máximo de cinco días hábiles, a contar de la fecha en que se realizó la revisión ante el profesor. El Vicedecano, si estima fundamentada la solicitud, nombrará una Comisión ad hoc, la que recopilará los antecedentes correspondientes y analizará la situación. Esta comisión deberá resolver en el plazo de 10 días corridos a contar desde aquél en que se presentó la reclamación, haciendo constar su decisión inapelable en un acta y comunicándola en forma personal al alumno, dejando constancia de ello a través de la firma de éste.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Conservo [RG-ART-014] para coordinación de horarios y aulas centralizadas por Dirección de Docencia (y aviso previo del Secretario Académico) y agrego [RG-ART-025] para los plazos de entrega de notas y pautas (10 días hábiles) y revisión ante el profesor (5 días hábiles).
</pensar>
Respuesta: La utilización de aulas de uso centralizado es responsabilidad de la Dirección de Docencia (en Chillán y Los Ángeles del Director General respectivo), previa información del Secretario Académico sobre aulas de cada Facultad [RG-ART-014]; en cuanto a evaluaciones, el profesor tiene máximo 10 días hábiles para informar notas y pautas y los alumnos 5 días hábiles para aclarar dudas y revisarlas [RG-ART-025].
Condiciones o límites: El Vicedecano puede ampliar dichos plazos de entrega y revisión por razones justificadas [RG-ART-025].
Fuente: [RG-ART-014] [RG-ART-025]
```

## 25. `B5-V05` — bloque `resiliencia_feedback` | split `val` | modo `condicional` | estado `suficiente`

**Pregunta:** ¿Tiene el alumno derecho a conservar sus evaluaciones ya rendidas al pedir un reingreso ordinario tras haber caído en pérdida de carrera?

**Observaciones del Verificador (entrada):** El borrador omitió distinguir entre quien reingresa sin pérdida de carrera y quien sí incurrió en pérdida de carrera.

**Evidencia ensamblada (4 unidades, orden barajado):** `RG-ART-037`, `RG-ART-044`, `RG-ART-033`, `RG-ART-038`
- Clave esperada: `RG-ART-044` | Distractores incluidos: `RG-ART-037, RG-ART-033, RG-ART-038`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-044]** Artículo 44° El alumno que decida reingresar a una misma carrera, deberá hacerlo a Primer Año de ésta, como alumno nuevo, sujeto a los requisitos y exigencias vigentes en dicha carrera al momento de su reingreso y no tendrá derecho a validar, revalidar, convalidar o reconocer asignaturas aprobadas. Si el alumno que reingresa a la misma carrera no incurrió en pérdida de carrera, podrá solicitar, dentro de los treinta primeros días del primer semestre de permanencia en la carrera, mantener su situación académica anterior.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-044]: si reingresa tras pérdida de carrera no cumple la excepción del inciso 2 (que solo favorece a quien NO incurrió en pérdida de carrera), por lo que ingresa a Primer Año como alumno nuevo sin validar, revalidar, convalidar ni reconocer aprobadas.
</pensar>
Respuesta: No: quien reingresa a la misma carrera habiendo incurrido en pérdida de carrera debe hacerlo a Primer Año como alumno nuevo, sujeto a las exigencias vigentes y sin derecho a validar, revalidar, convalidar ni reconocer asignaturas aprobadas [RG-ART-044].
Condiciones o límites: La única excepción de pedir mantener la situación académica anterior (dentro de los 30 primeros días del primer semestre) rige únicamente para quien reingresa sin haber incurrido en pérdida de carrera [RG-ART-044].
Fuente: [RG-ART-044]
```

## 26. `B6-T01` — bloque `abstencion_honesta` | split `train` | modo `factual` | estado `suficiente`

**Pregunta:** ¿Qué establece exactamente el Artículo 57 de los Estatutos de la Corporación respecto a la coordinación académica entre Departamentos?

**Evidencia ensamblada (5 unidades, orden barajado):** `RG-ART-006`, `RG-ART-008`, `RG-ART-010`, `RG-PREAMBULO`, `RI-FI-ART-032`
- Clave esperada: `(ninguna)` | Distractores incluidos: `RG-ART-006, RG-ART-008, RG-ART-010, RG-PREAMBULO, RI-FI-ART-032`

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-010] menciona al pasar 'cautelando el cumplimiento de lo dispuesto en el primer párrafo del Artículo 57 de los Estatutos de la Corporación', pero el texto completo o contenido del Artículo 57 de los Estatutos NO está en la evidencia entregada. No debo inventarlo.
</pensar>
Respuesta: No es posible responder qué establece el Artículo 57 de los Estatutos de la Corporación porque su contenido no forma parte de la normativa consultada.
Condiciones o límites: No aplica
Fuente: sin respaldo en la normativa consultada
```

## 27. `B6-T13` — bloque `abstencion_honesta` | split `train` | modo `numerica` | estado `insuficiente`

**Pregunta:** ¿Cuántos pesos cuesta el certificado emitido por DAFE o cuántos días antes debe pedirse el certificado de la Dirección de Bibliotecas en caso de renuncia?

**Evidencia ensamblada (3 unidades, orden barajado):** `RG-ART-035`, `RG-ART-033`, `RG-ART-034`
- Clave esperada: `(ninguna)` | Distractores incluidos: `RG-ART-035, RG-ART-033, RG-ART-034`

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-035] enumera ambos certificados (DAFE y Dirección de Bibliotecas) como documentos obligatorios para renunciar o suspender, pero no menciona costo monetario alguno ni antelación en días para solicitarlos.
</pensar>
Respuesta: No existe información en la normativa consultada sobre el costo monetario ni la antelación mínima en días para tramitar los certificados de DAFE o de la Dirección de Bibliotecas.
Condiciones o límites: No aplica
Fuente: sin respaldo en la normativa consultada
```

## 28. `B6-T25` — bloque `abstencion_honesta` | split `train` | modo `factual` | estado `no_existe`

**Pregunta:** ¿Qué señala el Reglamento Interno de Ingeniería en su Artículo 38° sobre homologación automática de ramos?

**Artículos marcados como inexistentes:** RI-FI-ART-038

**Evidencia ensamblada (3 unidades, orden barajado):** `RI-FI-ART-015`, `RG-ART-040`, `RG-ART-038`
- Clave esperada: `(ninguna)` | Distractores incluidos: `RI-FI-ART-015, RG-ART-040, RG-ART-038`

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Estado: no_existe | no existen en la normativa: RI-FI-ART-038. El Artículo 38° del Reglamento Interno de Ingeniería no existe en la normativa consultada (no confundirlo con [RG-ART-038] del Reglamento General).
</pensar>
Respuesta: No existe el Artículo 38° en el Reglamento Interno de Docencia de Pregrado de la Facultad de Ingeniería dentro de la normativa consultada.
Condiciones o límites: No aplica
Fuente: sin respaldo en la normativa consultada
```

## 29. `B6-V01` — bloque `abstencion_honesta` | split `val` | modo `factual` | estado `suficiente`

**Pregunta:** ¿Qué plazo exacto en años establece el Artículo 3°.10 del Reglamento General para rendir la defensa o examen final de titulación en cada Facultad?

**Evidencia ensamblada (4 unidades, orden barajado):** `RG-ART-003-DEF-12`, `RG-ART-003-DEF-10`, `RG-ART-048`, `RG-ART-003-DEF-22`
- Clave esperada: `RG-ART-003-DEF-10` | Distractores incluidos: `RG-ART-003-DEF-12, RG-ART-048, RG-ART-003-DEF-22`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-003-DEF-10]** 3.10. PLAN DE ESTUDIO: El plan de estudio de una carrera es el conjunto de asignaturas, módulos y demás actividades curriculares ordenadas en una secuencia preestablecida conducente a la obtención de un grado académico o un título profesional. Consecuentemente, cada carrera tendrá asociado, un plan de estudio y los alumnos quedarán adscritos al plan de estudio vigente en el momento de su ingreso a la carrera, el que deberán aprobar íntegramente para acceder al grado o título profesional que corresponda. Los Planes de Estudio de las carreras que imparta la universidad deberán contener: a) Descripción General; b) Grado o título que otorga; c) Objetivos de la carrera; d) Perfil de egreso del graduado o profesional con sus competencias; e) Ordenamiento de las asignaturas y de las otras actividades curriculares que lo forman; f) Distribución de los créditos en asignaturas obligatorias, fundamentales, integradoras, electivas y complementarias; g) Distribución de los créditos de asignaturas que contribuyen a la formación integral del alumno, los que deben ser al menos el 10% del total de créditos transferibles del plan de estudios. h) Actividades finales de graduación o titulación. Las actividades finales de graduación o titulación podrán consistir en Habilitación Profesional, Examen de Grado o Título, Defensa de Título, Proyecto de Grado o Título o Proposición Plástica. Las actividades de habilitación profesional o trabajo de fin de carrera podrán consistir en Memoria, Internado, Práctica Preprofesional, u otra. Estas actividades deberán estar normadas en el Reglamento Interno de Docencia de Pregrado de la Facultad. El Reglamento Interno de Docencia de Pregrado de las Facultades fijará los plazos o términos dentro de los cuales deberá cumplirse con los requisitos de las señaladas actividades finales de graduación y titulación, pudiendo considerar, además y previamente, revalidaciones de estudio. Los nuevos Planes de Estudios de una carrera o sus modificaciones se pondrán en práctica para los alumnos que ingresan al primer año de la carrera. Los alumnos afectos al plan antiguo podrán solicitar, sólo por una vez y durante el periodo de inscripción de asignaturas correspondiente al inicio del año académico en que se pone en vigencia el nuevo plan, al Vicedecano de su Facultad su adscripción al nuevo plan. Lo anterior, sin perjuicio de los planes transitorios de ajuste que se puedan establecer.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-003-DEF-10] señala explícitamente que 'El Reglamento Interno de Docencia de Pregrado de las Facultades fijará los plazos o términos dentro de los cuales deberá cumplirse con los requisitos de las señaladas actividades finales de graduación y titulación', sin fijar un plazo numérico en el propio Reglamento General.
</pensar>
Respuesta: No existe un plazo numérico único en el Artículo 3°.10 del Reglamento General: esa norma delega en el Reglamento Interno de Docencia de Pregrado de cada Facultad la fijación de los plazos para las actividades finales de graduación y titulación [RG-ART-003-DEF-10].
Condiciones o límites: No aplica
Fuente: [RG-ART-003-DEF-10]
```

## 30. `B6-V05` — bloque `abstencion_honesta` | split `val` | modo `cruce` | estado `insuficiente`

**Pregunta:** ¿Qué fecha límite del Calendario 2026 rige para inscribir cursos PLEV y qué porcentaje exacto de descuento se aplica al arancel al inscribir menos créditos en Ingeniería?

**Evidencia ensamblada (3 unidades, orden barajado):** `CAL-2026-S1-06`, `RI-FI-ART-007`, `RG-ART-045`
- Clave esperada: `(ninguna)` | Distractores incluidos: `CAL-2026-S1-06, RI-FI-ART-007, RG-ART-045`

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
En la evidencia no aparecen fechas de inscripción del PLEV 2026 en el Calendario ni tampoco ninguna disposición arancelaria sobre descuentos por inscribir menor carga de créditos.
</pensar>
Respuesta: No existe respaldo en la normativa consultada sobre una fecha límite de inscripción para el PLEV 2026 ni sobre porcentajes de descuento arancelario por inscribir menos créditos.
Condiciones o límites: No aplica
Fuente: sin respaldo en la normativa consultada
```

