# Muestra de Revisión Manual — Dataset Redactor D4 (30 casos)

Muestra estratificada de **30 ejemplos** (`3 train + 2 val` por cada uno de los 6 bloques) extraída desde `redactor_train.jsonl` y `redactor_val.jsonl` para verificación humana previa al entrenamiento QLoRA (Paso 3).

Criterios a revisar en cada ejemplo:
1. La respuesta esperada se deduce íntegramente de los fragmentos literales mostrados en `<evidencia>`.
2. Todas las citas `[ID]` existen en la evidencia entregada y cubren cada afirmación relevante.
3. El bloque `<pensar>` razona sin saltos lógicos ni contradecir la salida final.
4. Cuando la evidencia falta o es parcial, el modelo no inventa datos y se abstiene honestamente.

---

## 01. `B1-T01` — bloque `citas_cruce` | split `train` | modo `cruce` | estado `suficiente`

**Pregunta:** ¿Qué requisito previo sobre docencia debe cumplir un alumno para inscribir asignaturas y en qué casos un profesor queda exento de ser evaluado en esa encuesta?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-007`, `RG-ART-042`, `RG-ART-019`, `RI-FI-ART-008`, `RI-FI-ART-007`, `RG-ART-010`
- Clave esperada: `RG-ART-042, RG-ART-007` | Distractores incluidos: `RG-ART-019, RI-FI-ART-008, RI-FI-ART-007, RG-ART-010`

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

**Pregunta:** ¿Qué feriados nacionales contempla el segundo semestre de 2026 en agosto, octubre y diciembre, y cuándo comienzan las Evaluaciones de Recuperación de ese mismo semestre?

**Evidencia ensamblada (6 unidades, orden barajado):** `CAL-2026-S2-04`, `CAL-2026-S2-11`, `CAL-2026-S2-10`, `CAL-2026-S2-09`, `CAL-2026-S2-05`, `CAL-2026-S2-08`
- Clave esperada: `CAL-2026-S2-08, CAL-2026-S2-10, CAL-2026-S2-11, CAL-2026-S2-05` | Distractores incluidos: `CAL-2026-S2-04, CAL-2026-S2-09`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[CAL-2026-S2-08]** Calendario de docencia de pregrado 2026. Segundo semestre. Feriado Nacional: jueves 20 de agosto.
- **[CAL-2026-S2-10]** Calendario de docencia de pregrado 2026. Segundo semestre. Feriado Nacional: lunes 12 de octubre.
- **[CAL-2026-S2-11]** Calendario de docencia de pregrado 2026. Segundo semestre. Feriado Nacional: martes 08 de diciembre.
- **[CAL-2026-S2-05]** Calendario de docencia de pregrado 2026. Segundo semestre. Evaluaciones de Recuperación: 14 – 23 de diciembre.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Feriados nacionales S2: [CAL-2026-S2-08] jueves 20 de agosto, [CAL-2026-S2-10] lunes 12 de octubre, [CAL-2026-S2-11] martes 08 de diciembre. Evaluaciones de Recuperación S2: [CAL-2026-S2-05] 14 – 23 de diciembre.
</pensar>
Respuesta: Los feriados nacionales en esos meses del segundo semestre de 2026 son el jueves 20 de agosto [CAL-2026-S2-08], lunes 12 de octubre [CAL-2026-S2-10] y martes 08 de diciembre [CAL-2026-S2-11]; las Evaluaciones de Recuperación se rinden del 14 al 23 de diciembre [CAL-2026-S2-05].
Condiciones o límites: Las fechas pertenecen al Segundo Semestre del Calendario de docencia de pregrado 2026 [CAL-2026-S2-05] [CAL-2026-S2-08] [CAL-2026-S2-10] [CAL-2026-S2-11].
Fuente: [CAL-2026-S2-05] [CAL-2026-S2-08] [CAL-2026-S2-10] [CAL-2026-S2-11]
```

## 04. `B1-V01` — bloque `citas_cruce` | split `val` | modo `cruce` | estado `suficiente`

**Pregunta:** ¿Qué facilidades académicas corresponden a dirigentes estudiantiles acreditados y qué deben hacer estudiantes con impedimentos religiosos o discapacidad al inscribir asignaturas?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-014`, `RG-ART-020`, `RG-ART-052`, `RG-ART-015`, `RG-ART-042`, `RI-FI-ART-013`
- Clave esperada: `RG-ART-052, RG-ART-020` | Distractores incluidos: `RG-ART-014, RG-ART-015, RG-ART-042, RI-FI-ART-013`

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

## 05. `B1-V05` — bloque `citas_cruce` | split `val` | modo `cruce` | estado `suficiente`

**Pregunta:** En el calendario del primer semestre de 2026, ¿en qué fechas son la pausa activa, las vacaciones de invierno y los feriados nacionales de mayo?

**Evidencia ensamblada (6 unidades, orden barajado):** `CAL-2026-S1-12`, `CAL-2026-S1-08`, `CAL-2026-S1-10`, `CAL-2026-S1-07`, `CAL-2026-S1-14`, `CAL-2026-S1-11`
- Clave esperada: `CAL-2026-S1-07, CAL-2026-S1-14, CAL-2026-S1-10, CAL-2026-S1-11` | Distractores incluidos: `CAL-2026-S1-12, CAL-2026-S1-08`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[CAL-2026-S1-07]** Calendario de docencia de pregrado 2026. Primer semestre. Pausa activa de docencia de pregrado: 11 – 15 de mayo.
- **[CAL-2026-S1-14]** Calendario de docencia de pregrado 2026. Primer semestre. Vacaciones de invierno (aprobación transitoria): 30 junio – 05 de julio.
- **[CAL-2026-S1-10]** Calendario de docencia de pregrado 2026. Primer semestre. Feriado Nacional: viernes 01 de mayo.
- **[CAL-2026-S1-11]** Calendario de docencia de pregrado 2026. Primer semestre. Feriado Nacional: jueves 21 de mayo.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[CAL-2026-S1-07]: pausa activa de docencia del 11 al 15 de mayo. [CAL-2026-S1-14]: vacaciones de invierno (aprobación transitoria) del 30 de junio al 05 de julio. Feriados de mayo: [CAL-2026-S1-10] viernes 01 de mayo y [CAL-2026-S1-11] jueves 21 de mayo.
</pensar>
Respuesta: En el primer semestre de 2026, la pausa activa de docencia ocurre del 11 al 15 de mayo [CAL-2026-S1-07], los feriados nacionales de mayo son el viernes 01 de mayo [CAL-2026-S1-10] y el jueves 21 de mayo [CAL-2026-S1-11], y las vacaciones de invierno (con aprobación transitoria) van del 30 de junio al 05 de julio [CAL-2026-S1-14].
Condiciones o límites: Además, el calendario establece que los días 18 y 19 de mayo no se realizarán evaluaciones [CAL-2026-S1-08].
Fuente: [CAL-2026-S1-07] [CAL-2026-S1-08] [CAL-2026-S1-10] [CAL-2026-S1-11] [CAL-2026-S1-14]
```

## 06. `B2-T01` — bloque `condiciones_excepciones` | split `train` | modo `condicional` | estado `suficiente`

**Pregunta:** ¿Qué condiciones, límites de tiempo y excepciones rigen el abandono de asignaturas sin especificación de motivos?

**Evidencia ensamblada (6 unidades, orden barajado):** `CAL-2026-S1-03`, `RI-FI-ART-008`, `RG-ART-042`, `RG-ART-045`, `RI-FI-ART-009`, `RG-ART-043`
- Clave esperada: `RG-ART-043` | Distractores incluidos: `CAL-2026-S1-03, RI-FI-ART-008, RG-ART-042, RG-ART-045, RI-FI-ART-009`

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

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-015`, `RG-ART-006`, `RG-ART-001`, `RG-ART-002`, `RG-ART-012`, `RG-ART-052`
- Clave esperada: `RG-ART-002` | Distractores incluidos: `RG-ART-015, RG-ART-006, RG-ART-001, RG-ART-012, RG-ART-052`

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

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-044`, `RG-ART-055`, `RI-FI-ART-017`, `RG-ART-054`, `RI-FI-ART-019`, `RI-FI-ART-018`
- Clave esperada: `RG-ART-054, RG-ART-055` | Distractores incluidos: `RG-ART-044, RI-FI-ART-017, RI-FI-ART-019, RI-FI-ART-018`

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

**Pregunta:** ¿Qué obligación de informe al término del semestre recae en el Profesor Encargado de una asignatura y cómo se distingue el modo de trabajo presencial del semipresencial?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-019`, `RG-ART-006`, `RG-ART-003-DEF-11`, `RG-ART-012`, `RG-ART-003-DEF-09`, `RG-ART-027`
- Clave esperada: `RG-ART-012, RG-ART-003-DEF-09` | Distractores incluidos: `RG-ART-019, RG-ART-006, RG-ART-003-DEF-11, RG-ART-027`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-012]** Artículo 12º En cada asignatura habrá al menos un Profesor Encargado cuyas funciones serán coordinar el trabajo de los profesores participantes, velar por el cumplimiento de los objetivos del programa respectivo, de las normas y plazos establecidos en los reglamentos correspondientes, y entregar el Acta de Notas Finales e informar por escrito al Director de Departamento, al final del período lectivo, sobre el desarrollo de la asignatura.
- **[RG-ART-003-DEF-09]** 3.9. ASIGNATURA: Asignatura es el conjunto de actividades de enseñanza-aprendizaje de un área del conocimiento conducentes a que el alumno adquiera y desarrolle, en una unidad de tiempo determinada, conocimientos, habilidades, destrezas, actitudes o valores. Las asignaturas adquieren, en el contexto de un plan de estudio, la calidad de obligatorias, electivas, complementarias o de libre elección. ASIGNATURAS OBLIGATORIAS: Son asignaturas esenciales para el logro del perfil de egreso de una carrera, que deben ser aprobadas para obtener el título o grado académico. ASIGNATURAS COMPLEMENTARIAS: Son asignaturas que permiten al alumno complementar su formación académico-profesional con temas o áreas que incrementan su acervo cultural o su formación personal. Son optativas dentro de un número de créditos preestablecidos en el plan de estudios. ASIGNATURAS ELECTIVAS: Son asignaturas del área académico-profesional correspondiente al plan de estudio, que profundizan o diversifican la formación en un área disciplinaria de la carrera. Son de carácter opcional para el alumno dentro de un número de créditos o asignaturas preestablecidas en el plan de estudios. ASIGNATURAS DE LIBRE ELECCIÓN: Son asignaturas que no siendo asignaturas obligatorias, electivas o complementarias del correspondiente plan de estudios, el alumno las cursa por iniciativa propia. El alumno puede elegir asignaturas impartidas en otras carreras de la propia universidad o en otras universidades, siempre que se haya establecido algún convenio y quedarán incorporadas a su currículum y constituirán carga académica del periodo lectivo correspondiente. Adicionalmente las asignaturas pueden, en el contexto de un plan de estudios, tener el carácter de fundamental, integradora o de formación general. ASIGNATURAS FUNDAMENTALES: Son asignaturas obligatorias, establecidas por la universidad, para lograr aprender los fundamentos de una disciplina. ASIGNATURAS INTEGRADORAS: Son asignaturas obligatorias establecidas para evidenciar el nivel de logro de competencias del perfil de egreso o de los perfiles intermedios, expresadas en el plan de estudios. Sus resultados de aprendizaje están referidos a la integración de distintos saberes: conceptuales, procedimentales y actitudinales. ASIGNATURAS DE FORMACIÓN INTEGRAL: Son asignaturas que contribuyen a dar una formación integral dentro del contexto de un plan de estudios aportando a la formación profesional de un alumno, con el propósito de proporcionarle valoración de la diversidad y la interdisciplina, desarrollar competencias genéricas y desarrollar un currículum adecuado a sus propios intereses. Las asignaturas de formación integral pueden tener la calidad de obligatorias, electivas o complementarias en un plan de estudios. Las asignaturas pueden dictarse en alguna de las siguientes modalidades: ASIGNATURAS PRESENCIALES: Modalidad en que el proceso de enseñanza – aprendizaje es conducido principalmente por el o los docentes con presencia física del alumno. ASIGNATURAS SEMIPRESENCIALES: Modalidad en que el proceso de enseñanza–aprendizaje, principalmente, otorga al alumno espacios para el trabajo autónomo orientado por los docentes.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-012]: el Profesor Encargado coordina a los docentes participantes, vela por objetivos del programa y plazos, entrega el Acta de Notas Finales e informa por escrito al Director de Departamento al final del período lectivo sobre el desarrollo de la asignatura. [RG-ART-003-DEF-09]: presencial es conducido principalmente por el o los docentes con presencia física del alumno; semipresencial otorga principalmente espacios para trabajo autónomo orientado por docentes.
</pensar>
Respuesta: Al final del período lectivo, el Profesor Encargado debe entregar el Acta de Notas Finales e informar por escrito al Director de Departamento sobre el desarrollo de la asignatura [RG-ART-012]. Respecto de las modalidades, la asignatura presencial es conducida principalmente por los docentes con presencia física del estudiante, mientras que la semipresencial otorga principalmente espacios para el trabajo autónomo orientado por los docentes [RG-ART-003-DEF-09].
Condiciones o límites: El Profesor Encargado también debe coordinar al equipo docente y velar por el cumplimiento de normas y plazos reglamentarios [RG-ART-012].
Fuente: [RG-ART-003-DEF-09] [RG-ART-012]
```

## 11. `B3-T01` — bloque `polares_y_lectura` | split `train` | modo `condicional` | estado `suficiente`

**Pregunta:** Si un estudiante inscribe una asignatura en el PLEV y luego decide retirarse dentro de las primeras tres semanas, ¿puede hacer abandono sin especificación de motivos?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-016`, `RI-FI-ART-009`, `RG-ART-042`, `CAL-2026-S1-03`, `RG-ART-045`, `RG-ART-043`
- Clave esperada: `RG-ART-043` | Distractores incluidos: `RG-ART-016, RI-FI-ART-009, RG-ART-042, CAL-2026-S1-03, RG-ART-045`

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

## 12. `B3-T16` — bloque `polares_y_lectura` | split `train` | modo `condicional` | estado `suficiente`

**Pregunta:** Si la Facultad de Ingeniería solicita al Decano resolver una contradicción entre su Reglamento Interno y el Reglamento General, ¿prevalece el Reglamento Interno por ser norma específica de la Facultad?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-001`, `RI-FI-ART-002`, `RI-FI-ART-034`, `RI-FI-ART-035`, `RG-TRANS-002`, `RG-ART-060`
- Clave esperada: `RI-FI-ART-034, RG-ART-060` | Distractores incluidos: `RG-ART-001, RI-FI-ART-002, RI-FI-ART-035, RG-TRANS-002`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RI-FI-ART-034]** Artículo 34°. Ante la situación de que disposiciones del presente reglamento no se concilien con aquellas contenidas en el Reglamento General de Docencia de Pregrado y en las Normas de Ingreso a las Carreras de Pregrado que imparte la Universidad de Concepción, prevalecerán siempre estas últimas, respecto de las primeras.
- **[RG-ART-060]** Artículo 60º Las normas del presente reglamento prevalecerán sobre cualesquiera otras que no se concilien con éstas, no importando de donde provengan.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Justo al revés: tanto [RI-FI-ART-034] como [RG-ART-060] señalan que ante inconciliabilidad prevalecen SIEMPRE el Reglamento General de Docencia de Pregrado (y las Normas de Ingreso según RI-FI art. 34), sin importar de dónde provenga la otra norma.
</pensar>
Respuesta: No, prevalecen siempre el Reglamento General de Docencia de Pregrado y las Normas de Ingreso a las Carreras de Pregrado de la Universidad sobre el Reglamento Interno de Ingeniería [RG-ART-060] [RI-FI-ART-034].
Condiciones o límites: La supremacía del Reglamento General rige sobre cualesquiera otras disposiciones que no se concilien con éste, sin importar de dónde provengan [RG-ART-060].
Fuente: [RG-ART-060] [RI-FI-ART-034]
```

## 13. `B3-T30` — bloque `polares_y_lectura` | split `train` | modo `premisa_falsa` | estado `suficiente`

**Pregunta:** Para pedir una modificación de un Acta de Notas ya ingresada en el SAC basta con que el Profesor Encargado la envíe dentro de los dos años siguientes al semestre calificado. ¿Es así?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-025`, `RG-ART-012`, `RG-ART-027`, `RG-ART-003-DEF-05`, `RG-ART-013`, `RG-ART-005`
- Clave esperada: `RG-ART-027` | Distractores incluidos: `RG-ART-025, RG-ART-012, RG-ART-003-DEF-05, RG-ART-013, RG-ART-005`

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

## 14. `B3-V01` — bloque `polares_y_lectura` | split `val` | modo `condicional` | estado `suficiente`

**Pregunta:** Si un estudiante entrega un informe grupal redactado fuera del aula en que copió gran parte del contenido de forma ilícita, ¿está obligado el reglamento a aplicarle solo un 1,0 o existe otra calificación posible?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-051`, `RG-ART-021`, `RG-ART-024`, `RI-FI-ART-011`, `RG-ART-023`, `RG-ART-013`
- Clave esperada: `RG-ART-023` | Distractores incluidos: `RG-ART-051, RG-ART-021, RG-ART-024, RI-FI-ART-011, RG-ART-013`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-023]** Artículo 23º La Nota Final deberá ser expresada en la escala numérica oficial de 1 a 7 hasta con un decimal de aproximación. En esta escala, las centésimas inferiores al dígito 5 no afectarán a la décima. Las centésimas iguales o superiores al dígito 5 se aproximarán a la décima superior. Los alumnos que obtengan Nota Final igual o superior a 4,0 (cuatro coma cero) en la escala de 1 a 7 aprobarán la asignatura. Cuando el alumno no cumpla alguno de los requisitos establecidos en el programa de la asignatura, será calificado con el concepto NCR (no cumple requisito). Reprobarán la asignatura, quienes obtengan Nota Final inferior a 4,0 y también los que no cumplan requisitos (NCR). El alumno que para rendir un instrumento de evaluación obtenga o facilite información en forma ilícita o por medios no autorizados por el profesor, podrá ser calificado con la nota mínima. Si dicha acción involucra gran parte de un instrumento desarrollado fuera del aula y que es requisito en la asignatura, tales como proyectos, trabajos grupales u otros, el alumno podrá ser calificado con NCR.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-023] párrafo final: quien obtenga o facilite información ilícita puede recibir nota mínima, pero si involucra gran parte de un instrumento desarrollado fuera del aula y requisito (como proyectos o trabajos grupales), el alumno podrá ser calificado con NCR.
</pensar>
Respuesta: Existe otra calificación posible: tratándose de gran parte de un instrumento desarrollado fuera del aula que sea requisito de la asignatura (como proyectos o trabajos grupales), el alumno puede ser calificado con NCR (no cumple requisito), además de la opción general de nota mínima [RG-ART-023].
Condiciones o límites: El concepto NCR (no cumple requisito) implica reprobar la asignatura; la nota mínima de la escala oficial (1 a 7) es 1,0 y también reprueban quienes obtengan Nota Final inferior a 4,0 [RG-ART-023].
Fuente: [RG-ART-023]
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

**Pregunta:** Un alumno cursó cuatro actividades: Cálculo I (6 créditos, nota 5,5), Física I (4 créditos, nota 3,2), Taller (5 créditos, NCR) y Deporte (3 créditos, APR). ¿Cuál es su Promedio Ponderado y cuál es su Promedio Curricular?

**Evidencia ensamblada (6 unidades, orden barajado):** `RI-FI-ART-030`, `RG-ART-021`, `RG-ART-024`, `RG-ART-023`, `RG-ART-046`, `RG-ART-003-DEF-07`
- Clave esperada: `RG-ART-024` | Distractores incluidos: `RI-FI-ART-030, RG-ART-021, RG-ART-023, RG-ART-046, RG-ART-003-DEF-07`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RG-ART-024]** Artículo 24° El registro académico del alumno deberá proporcionar, a lo menos, los siguientes dos tipos de promedios de notas: a) Promedio Ponderado (“Prom. Pond.”): Corresponde al promedio de las notas finales iguales o superiores a 4,0, ponderadas por el correspondiente número de créditos. b) Promedio Curricular (“Prom. Curr.”): Corresponde al promedio de las todas notas finales, ponderadas por el correspondiente número de créditos. Para efectos del cálculo de los promedios señalados, el concepto NCR (no cumple requisitos) equivaldrá a la nota final 1,0; y no se considerarán los conceptos APR (aprobado) y REP (reprobado).

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Aplico [RG-ART-024]: a) Promedio Ponderado usa solo notas >= 4,0 -> solo Cálculo I (6 cr, 5,5); APR se excluye. Prom. Pond. = (5,5 * 6) / 6 = 5,5. b) Promedio Curricular usa todas las notas finales ponderadas por créditos, con NCR = 1,0 y excluyendo APR/REP: suma = 5,5*6 + 3,2*4 + 1,0*5 = 33,0 + 12,8 + 5,0 = 50,8; créditos = 6 + 4 + 5 = 15. 50,8 / 15 = 3,3866... -> 3,4 con redondeo de [RG-ART-023] o 3,39 con dos decimales. Indicar valor exacto y aproximado según [RG-ART-024]!
</pensar>
Respuesta: Su Promedio Ponderado es 5,5 y su Promedio Curricular es 3,39 (50,8 / 15; aproximadamente 3,4 a un decimal) [RG-ART-024].
Condiciones o límites: Cálculo: el Promedio Ponderado incluye solo notas finales >= 4,0 y excluye APR, dando (5,5 × 6) / 6 = 5,5; el Promedio Curricular incluye todas las notas finales asignando 1,0 al NCR y excluyendo APR: (5,5 × 6 + 3,2 × 4 + 1,0 × 5) / (6 + 4 + 5) = 50,8 / 15 = 3,3867 [RG-ART-024].
Fuente: [RG-ART-024]
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

**Pregunta:** Si un estudiante postula por cambio de carrera desde otra Facultad hacia Ingeniería con un promedio ponderado de 4,48 y luego solicita convalidar una asignatura aprobada en su origen con nota 4,45, ¿cumple los requisitos numéricos mínimos en ambos trámites considerando la escala de notas?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-023`, `RG-ART-055`, `RI-FI-ART-017`, `RI-FI-ART-020`, `RI-FI-ART-021`, `RI-FI-ART-018`
- Clave esperada: `RI-FI-ART-017, RI-FI-ART-021, RG-ART-023` | Distractores incluidos: `RG-ART-055, RI-FI-ART-020, RI-FI-ART-018`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RI-FI-ART-017]** Artículo 17°. La y el estudiante que haya cursado estudios en carreras de otras Facultades de la Universidad de Concepción o en otra Universidad chilena, podrá solicitar ingresar a la Facultad de Ingeniería, siempre que, además de cumplir con los requisitos establecidos en el Reglamento General de Docencia de Pregrado y en las Normas de Ingreso a las Carreras de Pregrado de la Universidad de Concepción, haya obtenido un promedio ponderado mínimo de calificaciones, equivalente a 4,5 en la escala de 1 a 7, en la carrera de origen.
- **[RI-FI-ART-021]** Artículo 21°. La y el estudiante de especialidad podrá solicitar la convalidación de una asignatura de su Plan de Estudio por otra(s) aprobada(s), con calificación(es) mínima(s) equivalente(s) a 4,5 en la escala de notas 1 a 7, en esta u otra Institución de Educación Superior. La solicitud deberá ir acompañada de un certificado de calificaciones y de los programas debidamente acreditados de las asignaturas aprobadas. No se podrá convalidar una asignatura que haya sido previamente cursada y reprobada en el Plan de Estudio.
- **[RG-ART-023]** Artículo 23º La Nota Final deberá ser expresada en la escala numérica oficial de 1 a 7 hasta con un decimal de aproximación. En esta escala, las centésimas inferiores al dígito 5 no afectarán a la décima. Las centésimas iguales o superiores al dígito 5 se aproximarán a la décima superior. Los alumnos que obtengan Nota Final igual o superior a 4,0 (cuatro coma cero) en la escala de 1 a 7 aprobarán la asignatura. Cuando el alumno no cumpla alguno de los requisitos establecidos en el programa de la asignatura, será calificado con el concepto NCR (no cumple requisito). Reprobarán la asignatura, quienes obtengan Nota Final inferior a 4,0 y también los que no cumplan requisitos (NCR). El alumno que para rendir un instrumento de evaluación obtenga o facilite información en forma ilícita o por medios no autorizados por el profesor, podrá ser calificado con la nota mínima. Si dicha acción involucra gran parte de un instrumento desarrollado fuera del aula y que es requisito en la asignatura, tales como proyectos, trabajos grupales u otros, el alumno podrá ser calificado con NCR.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RI-FI-ART-017]: cambio desde otra Facultad UdeC exige promedio ponderado mínimo equivalente a 4,5 en escala 1 a 7. [RI-FI-ART-021]: convalidar exige calificación mínima equivalente a 4,5 en escala 1 a 7. En escala oficial ([RG-ART-023]), si una nota viene a dos decimales y se aproxima a un decimal (centésima >= 5 sube): 4,48 -> 4,5 (cumple si está expresada a un decimal), y 4,45 -> 4,5; sin embargo, si se comparan directamente sin aproximar (4,48 < 4,5 y 4,45 < 4,5), estarían bajo 4,5. Indicar la regla literal de ambos!
</pensar>
Respuesta: Sin aproximación a un decimal, ni 4,48 ni 4,45 alcanzan el mínimo de 4,5 exigido tanto para ingresar desde otra Facultad [RI-FI-ART-017] como para convalidar asignaturas [RI-FI-ART-021]; sin embargo, expresadas en la escala oficial de un decimal conforme a la regla de aproximación de centésimas iguales o superiores a 5, tanto 4,48 como 4,45 aproximan a 4,5 [RG-ART-023].
Condiciones o límites: La nota oficial se expresa con un decimal de aproximación (centésimas >= 5 suben a la décima superior) [RG-ART-023]; además, la convalidación solo procede para estudiantes de especialidad sobre asignaturas no reprobadas en el plan [RI-FI-ART-021].
Fuente: [RG-ART-023] [RI-FI-ART-017] [RI-FI-ART-021]
```

## 19. `B4-V01` — bloque `calculos_y_orden` | split `val` | modo `numerica` | estado `suficiente`

**Pregunta:** Un estudiante de Ingeniería Civil obtuvo promedio ponderado de su Plan de Estudio (sin Memoria) de 5,5 y calificación 6,0 en su Memoria de Título. Calcula su nota de titulación exacta y qué concepto correspondería en su Diploma.

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-023`, `RI-FI-ART-030`, `RI-FI-ART-029`, `RG-ART-024`, `RG-ART-047`, `RG-ART-048`
- Clave esperada: `RI-FI-ART-030, RG-ART-048` | Distractores incluidos: `RG-ART-023, RI-FI-ART-029, RG-ART-024, RG-ART-047`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RI-FI-ART-030]** Artículo 30°. La nota de graduación correspondiente al Grado de Licenciado en Ciencias de la Ingeniería se obtendrá como el promedio ponderado por los créditos de las asignaturas aprobadas del respectivo Plan de Estudio de la Licenciatura. La nota de titulación correspondiente al Título Profesional de las carreras de Ingeniería Civil se obtendrá ponderando en un 60% el promedio ponderado de las asignaturas del Plan de Estudio sin considerar la Memoria de Título, y en un 40% la nota de la Memoria de Título.
- **[RG-ART-048]** Artículo 48° El Diploma de Grado Académico que otorgue la Universidad de Concepción, indicará la Nota obtenida por el egresado. Cuando se trate del Diploma de Título Profesional indicará los conceptos de “Aprobado por Unanimidad”, “Aprobado con Distinción” o “Aprobado con Distinción Máxima”, según el caso y conforme a la pauta siguiente: Concepto Calificación/Nota Aprobado por Unanimidad 4,0 - 4,9 Aprobado con Distinción 5,0 - 5,6 Aprobado con Distinción Máxima 5,7 - 7,0 Esta última disposición será aplicable también a los Diplomas de Grado Académico de Licenciado en carreras terminales, esto es, carreras en las que la Universidad de Concepción no otorga un título profesional. Las Facultades deberán indicar en cada expediente en que se solicite el otorgamiento de un Título Profesional o un Grado Académico la nota correspondiente y, además, en el caso del Título Profesional o de un Grado Académico de Licenciado en carreras terminales, el concepto a expresarse en el Diploma que se otorgue, conforme a la escala precedente. La Nota de graduación o titulación se obtendrá en la forma que lo establezca el Reglamento Interno de Docencia de Pregrado de la Facultad respectiva.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RI-FI-ART-030]: 0,6 × 5,5 + 0,4 × 6,0 = 3,30 + 2,40 = 5,70 = 5,7. [RG-ART-048]: 5,7 cae en 5,7–7,0 -> 'Aprobado con Distinción Máxima'.
</pensar>
Respuesta: Su nota de titulación es 5,7 [RI-FI-ART-030] y en su Diploma de Título Profesional corresponderá el concepto 'Aprobado con Distinción Máxima' [RG-ART-048].
Condiciones o límites: Cálculo: (0,60 × 5,5) + (0,40 × 6,0) = 3,30 + 2,40 = 5,7 [RI-FI-ART-030]; el tramo 5,7–7,0 recibe Aprobado con Distinción Máxima [RG-ART-048].
Fuente: [RG-ART-048] [RI-FI-ART-030]
```

## 20. `B4-V05` — bloque `calculos_y_orden` | split `val` | modo `numerica` | estado `suficiente`

**Pregunta:** Un curso de 10 créditos transferibles (SCT) equivale exactamente a cuántas horas de trabajo académico total según el Reglamento General, y qué diferencia hay frente a un crédito UdeC de clase práctica semanal?

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-017`, `RG-ART-003-DEF-08`, `RG-ART-003-DEF-11`, `RG-ART-003-DEF-06`, `RG-ART-003-DEF-12`, `RG-ART-003-DEF-07`
- Clave esperada: `RG-ART-003-DEF-08, RG-ART-003-DEF-07` | Distractores incluidos: `RG-ART-017, RG-ART-003-DEF-11, RG-ART-003-DEF-06, RG-ART-003-DEF-12`

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

## 21. `B5-T01` — bloque `resiliencia_feedback` | split `train` | modo `condicional` | estado `suficiente`

**Pregunta:** ¿Qué documentos debe presentar un estudiante de Ingeniería que desea suspender estudios y hasta cuándo puede hacerlo?

**Observaciones del Verificador (entrada):** El borrador menciona el plazo de cuatro semanas antes del término del período lectivo citando solo [RI-FI-ART-025], pero ese plazo no aparece en [RI-FI-ART-025] sino en otra unidad de la evidencia.

**Evidencia ensamblada (6 unidades, orden barajado):** `RI-FI-ART-025`, `RG-ART-031`, `RG-ART-033`, `RI-FI-ART-027`, `RG-ART-035`, `CAL-2026-S1-03`
- Clave esperada: `RI-FI-ART-025, RG-ART-031` | Distractores incluidos: `RG-ART-033, RI-FI-ART-027, RG-ART-035, CAL-2026-S1-03`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RI-FI-ART-025]** Artículo 25°. La y el estudiante podrá solicitar a la Vicedecanatura suspender estudios dentro de los plazos establecidos en el calendario anual de docencia de pregrado de la Universidad de Concepción. La solicitud deberá ir acompañada de los siguientes documentos: a) Certificado de la División de Asistencia Financiera al Estudiante (DAFE) en que conste que el alumno no tiene deudas con la Universidad de Concepción por concepto de aranceles y préstamos o que el pago de dichas deudas ha sido debidamente garantizado. b) Certificado de la Dirección de Bibliotecas en que conste que no adeuda material bibliográfico.
- **[RG-ART-031]** Artículo 31º Los alumnos de pregrado podrán solicitar, al Vicedecano, suspender estudios hasta cuatro semanas antes del término del periodo lectivo respectivo. La suspensión de estudios deja sin efecto la inscripción de asignaturas e interrumpe la calidad de alumno de pregrado de la Universidad de Concepción. La solicitud y los antecedentes oficiales que justifiquen la suspensión de estudios, tales como, informe de la Dirección de Servicios Estudiantiles u otros fidedignos, deberán ser presentados al Vicedecano respectivo, que resolverá dicha solicitud antes de que finalice el periodo lectivo correspondiente. De lo resuelto por el Vicedecano podrá dentro de cinco días apelarse al Decano, siendo su decisión definitiva. El Vicedecano informará lo resuelto al Jefe de Carrera respectivo, al alumno y lo registrará en el Sistema de Administración Curricular. La suspensión de estudios no libera al alumno de las obligaciones que pudiere tener pendientes con la universidad.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Observación del verificador: el borrador anterior citó solo [RI-FI-ART-025], pero las 4 semanas antes del fin del período lectivo están en [RG-ART-031]. Al corregir, NO debo eliminar [RI-FI-ART-025] (donde están la Vicedecanatura y los certificados a y b), sino conservar [RI-FI-ART-025] y agregar [RG-ART-031].
</pensar>
Respuesta: Debe presentar la solicitud a la Vicedecanatura junto con los certificados de la División de Asistencia Financiera al Estudiante (DAFE) y de la Dirección de Bibliotecas [RI-FI-ART-025], dentro del plazo máximo de hasta cuatro semanas antes del término del período lectivo respectivo [RG-ART-031].
Condiciones o límites: Además debe acompañar antecedentes oficiales que justifiquen la suspensión (como informe de DISE) [RG-ART-031]; el certificado DAFE debe acreditar ausencia o debida garantía de deudas de aranceles y préstamos y el de Bibliotecas no adeudar material bibliográfico [RI-FI-ART-025].
Fuente: [RG-ART-031] [RI-FI-ART-025]
```

## 22. `B5-T13` — bloque `resiliencia_feedback` | split `train` | modo `numerica` | estado `suficiente`

**Pregunta:** En una asignatura de Ingeniería con 30 clases teóricas cuyo programa exige el tope máximo permitido para ese tipo de sesiones (80 %), ¿cumple el requisito un estudiante que asistió a 23 clases?

**Observaciones del Verificador (entrada):** El borrador afirmó que sí aprueba por asistencia sin calcular el porcentaje real de 23 de 30 ni compararlo con el límite reglamentario del artículo 13.

**Evidencia ensamblada (6 unidades, orden barajado):** `RI-FI-ART-013`, `RG-ART-026`, `RG-ART-023`, `RG-ART-022`, `RI-FI-ART-012`, `RI-FI-ART-011`
- Clave esperada: `RI-FI-ART-013` | Distractores incluidos: `RG-ART-026, RG-ART-023, RG-ART-022, RI-FI-ART-012, RI-FI-ART-011`

<details>
<summary>Textos literales de las unidades clave en corpus.json</summary>

- **[RI-FI-ART-013]** Artículo 13°. El/La Profesor/a Encargado/a de la asignatura podrá establecer como requisito de aprobación una asistencia mínima a clases, exigencia que no podrá ser superior a un 80% de las clases teóricas y prácticas, y que podrá llegar a un 100% en las actividades tales como seminarios, laboratorios, talleres, salidas a terreno u otras de naturaleza similar a las mencionadas.

</details>

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Según [RI-FI-ART-013], el Profesor Encargado puede exigir asistencia mínima de hasta un 80 % en clases teóricas y prácticas (y hasta 100 % en laboratorios, talleres, seminarios o salidas a terreno). Verifico las cifras: 80 % de 30 = 24 clases; 23 / 30 = 76,67 % (76,7 %). No alcanza las 24 sesiones requeridas.
</pensar>
Respuesta: No cumple con el requisito mínimo: un 80 % sobre 30 clases teóricas exige asistir al menos a 24 sesiones, mientras que 23 clases corresponden a un 76,7 % de asistencia [RI-FI-ART-013].
Condiciones o límites: Operación: 0,80 × 30 = 24 clases mínimas (23 / 30 = 76,7 % < 80 %). Para clases teóricas y prácticas la exigencia no puede superar el 80 %, pero puede llegar al 100 % en seminarios, laboratorios, talleres o salidas a terreno [RI-FI-ART-013].
Fuente: [RI-FI-ART-013]
```

## 23. `B5-T25` — bloque `resiliencia_feedback` | split `train` | modo `condicional` | estado `suficiente`

**Pregunta:** ¿Qué condiciones aplican cuando un alumno quiere inscribir asignaturas que requieren cumplimiento de prerrequisitos y además desea tomar dos cursos que coinciden el mismo día y hora?

**Observaciones del Verificador (entrada):** El borrador respondió solo sobre el choque horario y omitió las consecuencias de incumplir prerrequisitos y de no haber respondido la Encuesta Docente.

**Evidencia ensamblada (6 unidades, orden barajado):** `RI-FI-ART-007`, `RG-ART-014`, `RG-ART-003-DEF-13`, `RI-FI-ART-008`, `RG-ART-007`, `RG-ART-042`
- Clave esperada: `RG-ART-042, RG-ART-014` | Distractores incluidos: `RI-FI-ART-007, RG-ART-003-DEF-13, RI-FI-ART-008, RG-ART-007`

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

**Evidencia ensamblada (6 unidades, orden barajado):** `RI-FI-ART-010`, `RG-ART-025`, `RG-ART-014`, `RG-ART-005`, `RG-ART-012`, `RG-ART-006`
- Clave esperada: `RG-ART-014, RG-ART-025` | Distractores incluidos: `RI-FI-ART-010, RG-ART-005, RG-ART-012, RG-ART-006`

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

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-033`, `RG-ART-044`, `RG-ART-028`, `RG-ART-037`, `RI-FI-ART-020`, `RG-ART-047`
- Clave esperada: `RG-ART-044` | Distractores incluidos: `RG-ART-033, RG-ART-028, RG-ART-037, RI-FI-ART-020, RG-ART-047`

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

**Evidencia ensamblada (6 unidades, orden barajado):** `RG-ART-006`, `RI-FI-ART-032`, `RG-ART-008`, `RG-ART-010`, `RG-PREAMBULO`, `RG-ART-004`
- Clave esperada: `(ninguna)` | Distractores incluidos: `RG-ART-006, RI-FI-ART-032, RG-ART-008, RG-ART-010, RG-PREAMBULO, RG-ART-004`

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-010] menciona al pasar 'cautelando el cumplimiento de lo dispuesto en el primer párrafo del Artículo 57 de los Estatutos de la Corporación', pero el texto completo o contenido del Artículo 57 de los Estatutos NO está en la evidencia entregada. No debo inventarlo.
</pensar>
Respuesta: No es posible responder qué establece el Artículo 57 de los Estatutos de la Corporación porque su contenido no forma parte de la normativa consultada.
Condiciones o límites: La evidencia únicamente hace referencia a cautelar el primer párrafo de ese artículo al coordinar con Directores de Departamento [RG-ART-010], sin reproducir el texto de los Estatutos.
Fuente: sin respaldo en la normativa consultada
```

## 27. `B6-T13` — bloque `abstencion_honesta` | split `train` | modo `numerica` | estado `suficiente`

**Pregunta:** ¿Cuál es la nota mínima exigida en el examen de admisión para alumnos libres y visitantes?

**Evidencia ensamblada (5 unidades, orden barajado):** `RG-ART-053`, `RG-ART-002`, `RG-ART-003-DEF-16`, `RI-FI-ART-017`, `RG-ART-003-DEF-18`
- Clave esperada: `(ninguna)` | Distractores incluidos: `RG-ART-053, RG-ART-002, RG-ART-003-DEF-16, RI-FI-ART-017, RG-ART-003-DEF-18`

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-053] remite a un reglamento especial y a los convenios correspondientes; ni [RG-ART-003-DEF-16] ni [RG-ART-003-DEF-18] contienen nota mínima.
</pensar>
Respuesta: No hay respaldo en la normativa consultada acerca de una nota mínima de admisión para alumnos libres ni alumnos visitantes.
Condiciones o límites: La normativa general remite el régimen de requisitos, derechos y obligaciones de alumnos libres y visitantes a un reglamento especial y convenios que no constan en la evidencia [RG-ART-053].
Fuente: sin respaldo en la normativa consultada
```

## 28. `B6-T25` — bloque `abstencion_honesta` | split `train` | modo `factual` | estado `no_existe`

**Pregunta:** ¿Qué señala el Reglamento Interno de Ingeniería en su Artículo 38° sobre homologación automática de ramos?

**Artículos marcados como inexistentes:** RI-FI-ART-038

**Evidencia ensamblada (3 unidades, orden barajado):** `RG-ART-040`, `RG-ART-038`, `RI-FI-ART-035`
- Clave esperada: `(ninguna)` | Distractores incluidos: `RG-ART-040, RG-ART-038, RI-FI-ART-035`

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Estado: no_existe | RI-FI termina en el Artículo 35°. No confundirlo con [RG-ART-038] (reconocimiento en Reglamento General).
</pensar>
Respuesta: No existe el Artículo 38° en el Reglamento Interno de Docencia de Pregrado de la Facultad de Ingeniería, cuyo articulado termina en el Artículo 35°.
Condiciones o límites: La normativa consultada del RI-FI no incluye un Artículo 38°.
Fuente: sin respaldo en la normativa consultada
```

## 29. `B6-V01` — bloque `abstencion_honesta` | split `val` | modo `factual` | estado `suficiente`

**Pregunta:** ¿Qué nota mínima o exigencia de aprobación establece el reglamento de la Facultad cuando un egresado excedió el plazo de seis semestres para titularse?

**Evidencia ensamblada (6 unidades, orden barajado):** `RI-FI-ART-031`, `RG-ART-049`, `RI-FI-ART-030`, `RI-FI-ART-035`, `RG-ART-048`, `RI-FI-ART-029`
- Clave esperada: `(ninguna)` | Distractores incluidos: `RI-FI-ART-031, RG-ART-049, RI-FI-ART-030, RI-FI-ART-035, RG-ART-048, RI-FI-ART-029`

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
[RG-ART-049] remite las exigencias tras vencer los 6 semestres al Reglamento Interno de la Facultad; sin embargo, en todo el RI-FI solo está [RI-FI-ART-031] (suspensión > 3 años cuando solo faltaba Memoria), no un artículo sobre egresados con más de 6 semestres sin suspensión!
</pensar>
Respuesta: No existe respaldo en la normativa consultada sobre las exigencias específicas aplicables en Ingeniería cuando vence el plazo de seis semestres desde el egreso sin haberse titulado.
Condiciones o límites: El Reglamento General fija el límite de seis semestres y delega tales exigencias en el Reglamento Interno de la Facultad [RG-ART-049], pero dicho supuesto específico no aparece regulado en el Reglamento Interno de Ingeniería consultado.
Fuente: sin respaldo en la normativa consultada
```

## 30. `B6-V05` — bloque `abstencion_honesta` | split `val` | modo `cruce` | estado `insuficiente`

**Pregunta:** ¿Qué fecha límite del Calendario 2026 rige para inscribir cursos de verano PLEV y cuántas horas semanales máximas permite el Artículo 8 de Ingeniería?

**Evidencia ensamblada (5 unidades, orden barajado):** `RG-ART-045`, `CAL-2026-S1-01`, `RI-FI-ART-008`, `CAL-2026-S2-01`, `RG-ART-017`
- Clave esperada: `(ninguna)` | Distractores incluidos: `RG-ART-045, CAL-2026-S1-01, RI-FI-ART-008, CAL-2026-S2-01, RG-ART-017`

**Salida esperada del Redactor (`assistant`):**
```text
<pensar>
Ninguno de los dos datos pedidos existe: (1) el Calendario 2026 no tiene fechas de PLEV, y (2) [RI-FI-ART-008] fija mínimo de 8 créditos (no horas semanales máximas; el máximo de 54 horas semanales de Trabajo Académico es del Plan de Estudio en [RG-ART-017], no del Art. 8 RI-FI).
</pensar>
Respuesta: No existe respaldo en la normativa consultada sobre una fecha límite de inscripción para el PLEV 2026 ni sobre un máximo de horas semanales en el Artículo 8° del Reglamento Interno de Ingeniería.
Condiciones o límites: El Calendario 2026 disponible no contempla fechas del PLEV y el Artículo 8° de Ingeniería establece únicamente un mínimo de ocho créditos por período lectivo ordinario, sin tope de horas.
Fuente: sin respaldo en la normativa consultada
```
