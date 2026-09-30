# Auditoría de las 50 preguntas: respuestas históricas

Revisión asistida por IA, pendiente de validación del equipo. Las respuestas originales no fueron modificadas. Convenciones: [protocolo](PROTOCOLO_EVALUACION.md). Recuento verificable: `python -m Deliverable2_RAG.auditoria`.

La evaluación conservadora resulta en 1/50 baseline y 44/50 RAG. E1 publicó 2/50; la diferencia es P49. No son resultados de la base v2 ni una nueva inferencia.

| ID | Categoría | Baseline | RAG |
| --- | --- | --- | --- |
| 1 | factual | 0 | 1 |
| 2 | factual | 0 | 1 |
| 3 | factual | 0 | 0 |
| 4 | factual | 0 | 1 |
| 5 | factual | 0 | 1 |
| 6 | factual | 0 | 1 |
| 7 | factual | 0 | 1 |
| 8 | factual | 0 | 1 |
| 9 | factual | 0 | 1 |
| 10 | factual | 0 | 1 |
| 11 | numerica | 0 | 1 |
| 12 | numerica | 0 | 1 |
| 13 | numerica | 0 | 1 |
| 14 | numerica | 0 | 1 |
| 15 | numerica | 0 | 1 |
| 16 | numerica | 0 | 1 |
| 17 | numerica | 0 | 1 |
| 18 | numerica | 0 | 1 |
| 19 | numerica | 0 | 1 |
| 20 | numerica | 0 | 1 |
| 21 | condicional | 0 | 1 |
| 22 | condicional | 0 | 1 |
| 23 | condicional | 0 | 1 |
| 24 | condicional | 0 | 0 |
| 25 | condicional | 0 | 0 |
| 26 | condicional | 0 | 1 |
| 27 | condicional | 0 | 1 |
| 28 | condicional | 0 | 1 |
| 29 | condicional | 0 | 1 |
| 30 | condicional | 0 | 1 |
| 31 | cruce | 0 | 1 |
| 32 | cruce | 0 | 1 |
| 33 | cruce | 0 | 1 |
| 34 | cruce | 0 | 1 |
| 35 | cruce | 0 | 1 |
| 36 | cruce | 0 | 0 |
| 37 | cruce | 0 | 1 |
| 38 | cruce | 0 | 0 |
| 39 | cruce | 0 | 1 |
| 40 | cruce | 0 | 0 |
| 41 | abstencion | 0 | 1 |
| 42 | abstencion | 0 | 1 |
| 43 | abstencion | 0 | 1 |
| 44 | abstencion | 0 | 1 |
| 45 | abstencion | 0 | 1 |
| 46 | abstencion | 0 | 1 |
| 47 | abstencion | 0 | 1 |
| 48 | abstencion | 0 | 1 |
| 49 | abstencion | 0 | 1 |
| 50 | abstencion | 1 | 1 |

## P1 · factual

¿Cuál es la nota mínima para aprobar una asignatura en la Facultad de Ingeniería?

**Referencia:** 4,0 · Art. 11, RI-FI

**Baseline (0):**

```text
La nota mínima para aprobar una asignatura en la Facultad de Ingeniería de la Universidad de Concepción es **4.0** (Art. 8).
```

Dato 4,0 correcto; cita Art. 8 en lugar de Art. 11 RI-FI.

**RAG (1):**

```text
DATO: 4,0
CITA: [Art. 11°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P2 · factual

¿Cuántas evaluaciones sumativas como mínimo debe tener una asignatura?

**Referencia:** al menos 3 (tres) · Art. 11, RI-FI

**Baseline (0):**

```text
La normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción no especifica un número mínimo de evaluaciones sumativas que debe tener una asignatura. Por lo tanto, esta información no está en la normativa.
```

Abstención indebida: el Art. 11 fija al menos tres evaluaciones.

**RAG (1):**

```text
DATO: 3
CITA: [Art. 11°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P3 · factual

¿A cuántas evaluaciones de recuperación tiene derecho el estudiante por asignatura?

**Referencia:** una (1) · Art. 12, RI-FI

**Baseline (0):**

```text
La normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción no especifica el número exacto de evaluaciones de recuperación que tiene derecho el estudiante por asignatura. Por lo tanto, **no está en la normativa**.
```

Abstención indebida: el Art. 12 reconoce una recuperación.

**RAG (0):**

```text
DATO: No está en la normativa
CITA: Ninguna
```

Abstención indebida: falta una recuperación y Art. 12 RI-FI; causa de recuperación no demostrada sin traza.


## P4 · factual

¿En qué escala se expresa la nota final de una asignatura?

**Referencia:** escala oficial de 1 a 7, con un decimal · Art. 23, RG

**Baseline (0):**

```text
La nota final de una asignatura se expresa en una escala de 0 a 7, según el **Art. 10** de la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción.
```

Escala 0–7 incorrecta y cita Art. 10 incorrecta.

**RAG (1):**

```text
DATO: Escala numérica oficial de 1 a 7 hasta con un decimal de aproximación.
CITA: [Art. 23, RG]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P5 · factual

¿Cuál es la actividad final de titulación en las carreras de Ingeniería?

**Referencia:** la Memoria de Título · Art. 29, RI-FI

**Baseline (0):**

```text
La actividad final de titulación en las carreras de Ingeniería es la **Tesis de Grado** (Art. 10).
```

Dice Tesis de Grado y cita Art. 10; se requiere Memoria de Título, Art. 29.

**RAG (1):**

```text
DATO: Memoria de Título
CITA: [Art. 29°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P6 · factual

¿Con cuánta anticipación mínima deben comunicarse las evaluaciones a los estudiantes?

**Referencia:** al menos una semana · Art. 10, RI-FI

**Baseline (0):**

```text
La normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción no establece específicamente la cantidad de anticipación mínima con la que deben comunicarse las evaluaciones a los estudiantes. Por lo tanto, **no está en la normativa**.
```

Abstención indebida: existe plazo de una semana.

**RAG (1):**

```text
DATO: Una semana
CITA: [Art. 10°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P7 · factual

¿Quién resuelve en primera instancia una solicitud de continuación de estudios?

**Referencia:** el Comité de Docencia y Asuntos Estudiantiles · Art. 16, RI-FI

**Baseline (0):**

```text
La solicitud de continuación de estudios se resuelve en primera instancia por el **director de carrera** (Art. 12).
```

Indica director de carrera y Art. 12 en vez del Comité y Art. 16.

**RAG (1):**

```text
DATO: Comité de Docencia y Asuntos Estudiantiles
CITA: [Art. 16°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P8 · factual

¿La renuncia a la carrera es revocable?

**Referencia:** No, es irrevocable · Art. 26, RI-FI

**Baseline (0):**

```text
La renuncia a la carrera no es revocable según el Art. 12 de la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción.
```

Irrevocabilidad correcta, pero cita Art. 12 en lugar del 26.

**RAG (1):**

```text
DATO: No
CITA: [Art. 26°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P9 · factual

¿Cuántos períodos lectivos ordinarios tiene el año académico y cuánto duran?

**Referencia:** dos, de 19 semanas cada uno · Art. 16, RG

**Baseline (0):**

```text
El año académico tiene **dos períodos lectivos ordinarios**, cada uno de **cuatro meses**.
Art. 10.
```

Duración de cuatro meses incorrecta y cita errónea.

**RAG (1):**

```text
DATO: Dos períodos lectivos ordinarios de diecinueve semanas cada uno
CITA: [Art. 16, RG]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P10 · factual

¿Los estudiantes de Primer Año Común pueden convalidar asignaturas?

**Referencia:** No · Art. 22, RI-FI

**Baseline (0):**

```text
Sí, los estudiantes de Primer Año Común pueden convalidar asignaturas, según el **Art. 12** de la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción.
```

Afirma que pueden convalidar y cita Art. 12; contradice la referencia.

**RAG (1):**

```text
DATO: No
CITA: [Art. 22°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P11 · numerica

¿Cuál es el mínimo de créditos que debo inscribir por período lectivo ordinario en Ingeniería?

**Referencia:** 8 créditos (igual o superior a 8) · Art. 8, RI-FI

**Baseline (0):**

```text
El mínimo de créditos que debe inscribirse por período lectivo ordinario en Ingeniería es **60 créditos**. Este requisito está establecido en el **Art. 8** de la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción.
```

Dice 60 créditos en vez de ocho; cita Art. 8.

**RAG (1):**

```text
DATO: ocho
CITA: [Art. 8°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P12 · numerica

¿Con menos de cuántos créditos aprobados al término del segundo semestre quedo en baja académica?

**Referencia:** menos de 15 créditos · Art. 14 a), RI-FI

**Baseline (0):**

```text
Art. 12. Queda en baja académica el estudiante que, al término del segundo semestre, no haya aprobado más de 12 créditos.
```

Umbral de 12 créditos y artículo incorrectos.

**RAG (1):**

```text
DATO: 15
CITA: [Art. 14°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P13 · numerica

¿Bajo qué promedio de créditos aprobados por semestre (desde el 4º) se cae en baja académica?

**Referencia:** inferior a 10 créditos semestrales · Art. 14 b), RI-FI

**Baseline (0):**

```text
La información solicitada no está contemplada en la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción.
```

Abstención indebida ante umbral de diez créditos.

**RAG (1):**

```text
DATO: inferior a diez créditos semestrales
CITA: [Art. 14°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P14 · numerica

¿Cuál es la asistencia mínima máxima que un profesor puede exigir en clases teóricas y prácticas?

**Referencia:** 80% · Art. 13, RI-FI

**Baseline (0):**

```text
La asistencia no está especificada en términos numéricos en la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción. Por lo tanto, no existe un límite definido por el artículo correspondiente.
```

Niega el límite de 80%.

**RAG (1):**

```text
DATO: 80%
CITA: [Art. 13°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P15 · numerica

¿Qué calificación mínima se exige para convalidar una asignatura?

**Referencia:** 4,5 · Art. 21, RI-FI

**Baseline (0):**

```text
La calificación mínima exigida para convalidar una asignatura es **3.0** (Art. 8).
```

Nota 3,0 y artículo incorrectos.

**RAG (1):**

```text
DATO: 4,5
CITA: [Art. 21°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P16 · numerica

¿Durante cuántas semanas iniciales se puede solicitar convalidación, revalidación o reconocimiento?

**Referencia:** las 4 primeras semanas · Art. 22, RI-FI

**Baseline (0):**

```text
Art. 12.
```

Solo entrega Art. 12: no responde cuatro semanas ni cita Art. 22.

**RAG (1):**

```text
DATO: cuatro
CITA: [Art. 22°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P17 · numerica

¿Dentro de cuántos días se puede solicitar el reconocimiento de asignaturas?

**Referencia:** los primeros 30 días · Art. 23, RI-FI

**Baseline (0):**

```text
La normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción no establece un plazo específico para la solicitud de reconocimiento de asignaturas. Por lo tanto, esta información no está en la normativa.
```

Abstención indebida ante plazo de treinta días.

**RAG (1):**

```text
DATO: Treinta días
CITA: [Art. 38°, RG] y [Art. 23°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P18 · numerica

Si suspendí más de 3 años y solo me faltaba la Memoria, ¿cuántos créditos adicionales máximo debo cursar?

**Referencia:** un máximo de 36 créditos · Art. 31, RI-FI

**Baseline (0):**

```text
La normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción no establece específicamente la cantidad de créditos adicionales que debe cursar un estudiante que ha sido suspendido más de 3 años y solo le falta la Memoria. Por lo tanto, **no está en la normativa**.
```

Abstención indebida ante máximo de 36 créditos.

**RAG (1):**

```text
DATO: 36
CITA: [Art. 31°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P19 · numerica

¿Cuántas semanas dura cada período lectivo ordinario (semestre)?

**Referencia:** 19 semanas · Art. 16, RG

**Baseline (0):**

```text
El período lectivo ordinario dura **18 semanas** (Art. 8).
```

Dice 18 semanas y Art. 8 en vez de 19 y Art. 16 RG.

**RAG (1):**

```text
DATO: Diecinueve
CITA: [Art. 16, RG]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P20 · numerica

¿Cuál es el plazo (en días hábiles) para regularizar una evaluación no rendida por causa justificada?

**Referencia:** 3 días hábiles · Art. 26, RG

**Baseline (0):**

```text
El plazo para regularizar una evaluación no rendida por causa justificada es de **15 días hábiles**, según el **Art. 12** de la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción.
```

Dice 15 días y Art. 12 en vez de tres y Art. 26 RG.

**RAG (1):**

```text
DATO: tres días hábiles
CITA: [Art. 26, RG]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P21 · condicional

Si vengo de otra universidad y quiero ingresar a Ingeniería, ¿qué promedio necesito? ¿Y para cambio dentro de Ingeniería?

**Referencia:** 4,5 desde otra universidad/facultad; 4,2 para cambio dentro de Ingeniería · Art. 17 y Art. 18, RI-FI

**Baseline (0):**

```text
La normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción no establece específicamente los promedios necesarios para ingreso o cambio dentro de la carrera, ya que estos requisitos suelen definirse por el Consejo Universitario o las normas generales de la Universidad. Por lo tanto, **no está en la normativa**.
```

Abstención indebida: omite ambos promedios y fuentes.

**RAG (1):**

```text
DATO: Para ingresar a la Facultad de Ingeniería desde otra universidad se necesita un promedio ponderado mínimo de 4,5 en la escala de 1 a 7, mientras que para cambiar dentro de la Facultad se necesita un promedio ponderado mínimo de 4,2 en la escala de 1 a 7.
CITA: [Art. 17°, RI-FI] y [Art. 18°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P22 · condicional

¿Qué promedio mínimo se exige para cursar una segunda carrera de forma simultánea?

**Referencia:** 5,0 · Art. 19, RI-FI

**Baseline (0):**

```text
La normativa de la Facultad de Ingeniería de la Universidad de Concepción no establece un promedio mínimo específico para cursar una segunda carrera de forma simultánea. Por lo tanto, esta información no está en la normativa.
```

Abstención indebida ante promedio 5,0.

**RAG (1):**

```text
DATO: 5,0 en la escala de 1 a 7
CITA: [Art. 19°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P23 · condicional

¿En qué caso NO se puede revalidar una asignatura?

**Referencia:** si fue previamente cursada y reprobada · Art. 20, RI-FI

**Baseline (0):**

```text
No se puede revalidar una asignatura en el caso en que no haya sido aprobada o no haya sido cursada con éxito, según el **Art. 12** de la normativa de pregrado.
```

Condición imprecisa y cita Art. 12 incorrecta.

**RAG (1):**

```text
DATO: No se podrá revalidar una asignatura que haya sido previamente cursada y reprobada en el Plan de Estudio.
CITA: [Art. 20°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P24 · condicional

Si repruebo por segunda vez una misma asignatura obligatoria, ¿qué ocurre?

**Referencia:** baja académica, salvo que la haya aprobado en el PLEV o esté en primer año · Art. 14 c), RI-FI

**Baseline (0):**

```text
Si repruebas por segunda vez una misma asignatura obligatoria, se considera que has incumplido el régimen académico y podrías ser inhabilitado para continuar en el programa de estudios, según el **Art. 12** de la normativa de pregrado.
```

Omite excepciones y cita Art. 12 incorrecta.

**RAG (0):**

```text
DATO: La y el estudiante perderá el derecho a continuar estudios y la calidad de alumno regular, quedando en situación de Baja Académica.
CITA: [Art. 14°, RI-FI]
```

Omite las excepciones PLEV y primer año; transforma una regla condicional en afirmación absoluta.


## P25 · condicional

Al modificar la inscripción, ¿qué asignaturas NO puedo eliminar?

**Referencia:** las atrasadas y las obligatorias reprobadas (prioridades a y b del Art. 7) · Art. 9, RI-FI

**Baseline (0):**

```text
No está en la normativa.
```

Abstención indebida ante asignaturas no eliminables.

**RAG (0):**

```text
DATO: Las asignaturas correspondientes a las prioridades a) y b) del
CITA: [Art. 9°, RI-FI]
```

Respuesta truncada en «prioridades a) y b) del»; no identifica atrasadas y obligatorias reprobadas.


## P26 · condicional

Si suspendí mis estudios, ¿qué debo hacer para volver?

**Referencia:** solicitar la reincorporación a la Vicedecanatura · Art. 27, RI-FI

**Baseline (0):**

```text
Si suspendiste tus estudios, debes presentar una solicitud de reingreso al Colegio de Estudios Superiores, según el Art. 12 de la Normativa de Pregrado. Esta solicitud debe incluir justificación y documentación relacionada con la suspensión.
```

Inventa órgano de reingreso y cita Art. 12.

**RAG (1):**

```text
DATO: Deberá solicitar su reincorporación al Vicedecano.
CITA: [Art. 27°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P27 · condicional

¿Qué documentos requiere la solicitud de suspensión de estudios?

**Referencia:** certificado de la DAFE (sin deudas) y de la Dirección de Bibliotecas · Art. 25, RI-FI

**Baseline (0):**

```text
La solicitud de suspensión de estudios requiere la presentación de los siguientes documentos, según el **Art. 12** de la normativa:
- Formulario de solicitud de suspensión de estudios.
- Justificación escrita de la situación que motiva la suspensión.
- Copia del acta de inscripción.
- Copia del certificado de matrícula.
- Copia del certificado de notas (si aplica).
```

Inventa documentación y cita Art. 12 incorrecta.

**RAG (1):**

```text
DATO: a) Certificado de la División de Asistencia Financiera al Estudiante en que conste que el alumno no tiene deudas con la universidad por concepto de aranceles y préstamos o que el pago de dichas deudas ha sido debidamente garantizado; y b) Certificado de la Dirección de Bibliotecas en que conste que no adeuda material bibliográfico.
CITA: [Art. 25°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P28 · condicional

Si estando habilitado no inscribo asignaturas en el período, ¿qué pasa?

**Referencia:** pierdo el derecho a continuar y la calidad de alumno (Baja por no Inscripción) · Art. 29, RG

**Baseline (0):**

```text
Si estando habilitado no inscribo asignaturas en el período, se considera que no se ha cumplido con el requisito de inscripción, y por lo tanto, no se podrá acceder a las evaluaciones o créditos correspondientes a dichas asignaturas. Art. 12.
```

No expresa baja y pérdida de calidad de alumno; cita Art. 12.

**RAG (1):**

```text
DATO: Perderá el derecho a continuar estudios como también la calidad de alumno de pregrado de la Universidad de Concepción, a menos que en el periodo lectivo anterior hayan inscrito una u más asignaturas anuales.
CITA: Art. 29°, RG
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P29 · condicional

Si no me presento a una evaluación por causa justificada, ¿qué puedo hacer?

**Referencia:** solicitar regularizar en un máximo de 3 días hábiles · Art. 26, RG

**Baseline (0):**

```text
Si no te presentas a una evaluación por causa justificada, debes comunicarte con el profesor o el área académica responsable para solicitar la extensión o el permiso correspondiente. Art. 12.
```

Omite plazo de tres días y cita Art. 12 incorrecta.

**RAG (1):**

```text
DATO: Solicitar al profesor encargado de la asignatura regularizar su situación en un plazo máximo de tres días hábiles posteriores a la aplicación de la evaluación, para lo cual deberá presentar los documentos que justifiquen su inasistencia.
CITA: [Art. 26, RG]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P30 · condicional

¿Cuánta asistencia puede exigir un profesor en un laboratorio, taller o salida a terreno?

**Referencia:** hasta un 100% · Art. 13, RI-FI

**Baseline (0):**

```text
La normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción no establece un límite específico de asistencia que puede exigir un profesor en un laboratorio, taller o salida a terreno. Por lo tanto, **no está en la normativa**.
```

Niega límite de asistencia de hasta 100%.

**RAG (1):**

```text
DATO: 100%
CITA: [Art. 13°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P31 · cruce

Si el Reglamento Interno de Ingeniería contradice al Reglamento General de Docencia, ¿cuál prevalece?

**Referencia:** prevalece el Reglamento General (y las Normas de Ingreso) · Art. 34, RI-FI

**Baseline (0):**

```text
Según el Art. 10 del Reglamento Interno de Ingeniería, los reglamentos internos de las facultades y escuelas son de aplicación general y tienen preferencia sobre los reglamentos generales de la Universidad, siempre que no contradigan normas universitarias básicas. Por lo tanto, el Reglamento Interno de Ingeniería prevalece sobre el Reglamento General de Docencia cuando exista contradicción.
```

Invierte la prelación y cita Art. 10 incorrecta.

**RAG (1):**

```text
DATO: El Reglamento General de Docencia de Pregrado y las Normas de Ingreso a las Carreras de Pregrado prevalecen sobre el presente Reglamento Interno de Docencia de Pregrado.
CITA: [Art. 34°, RI-FI]
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P32 · cruce

Quiero modificar las asignaturas inscritas este segundo semestre 2026. ¿Hasta qué fecha?

**Referencia:** hasta el 04 de septiembre de 2026 · CAL 2º sem 2026 (Art. 9, RI-FI)

**Baseline (0):**

```text
La fecha límite para modificar las asignaturas inscritas en el segundo semestre 2026 está establecida en el **Art. 12** de la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción. Según dicho artículo, la fecha límite es el **15 de enero**.
```

Fecha 15 de enero y Art. 12 incorrectos.

**RAG (1):**

```text
DATO: 04 de septiembre
CITA: [Calendario 2026, Segundo Semestre 2026]
```

La fecha y el calendario citados responden íntegramente la consulta; Art. 9 RI-FI entre paréntesis es contexto adicional, no fuente necesaria del dato pedido.


## P33 · cruce

¿Hasta qué fecha se pueden modificar asignaturas en el primer semestre 2026?

**Referencia:** hasta el 02 de abril de 2026 · CAL 1er sem 2026 (Art. 9, RI-FI)

**Baseline (0):**

```text
La normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción no establece específicamente la fecha límite para modificar asignaturas en el primer semestre 2026. Por lo tanto, **no está en la normativa**.
```

Abstención indebida ante fecha en calendario.

**RAG (1):**

```text
DATO: 02 de abril
CITA: [Calendario 2026, Primer Semestre 2026]
```

La fecha y el calendario citados responden íntegramente la consulta; Art. 9 RI-FI entre paréntesis es contexto adicional, no fuente necesaria del dato pedido.


## P34 · cruce

¿Tengo derecho a suspender estudios y hasta cuándo puedo hacerlo?

**Referencia:** sí; dentro de los plazos del calendario, a más tardar 4 semanas antes del término · Art. 25 RI-FI + Art. 31 RG

**Baseline (0):**

```text
La suspensión de estudios no está explícitamente regulada en el Reglamento General de la Facultad de Ingeniería de la Universidad de Concepción. Por lo tanto, no está en la normativa.
```

Niega derecho a suspender regulado en el corpus.

**RAG (1):**

```text
DATO: Los alumnos de pregrado podrán solicitar suspender estudios hasta cuatro semanas antes del término del periodo lectivo respectivo.
CITA: [Art. 31, RG]
```

El Art. 31 RG citado contiene tanto el derecho a suspender como el plazo máximo de cuatro semanas; Art. 25 RI-FI añade trámite, no exigido en la pregunta.


## P35 · cruce

¿Cuándo inician las clases del segundo semestre 2026?

**Referencia:** 10 de agosto de 2026 · CAL 2º sem 2026

**Baseline (0):**

```text
La normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción no especifica la fecha exacta en que inician las clases del segundo semestre 2026. Por lo tanto, **no está en la normativa**.
```

Abstención indebida ante fecha 10 de agosto.

**RAG (1):**

```text
DATO: 10 de agosto
CITA: [Calendario 2026, Segundo Semestre 2026]: Inicio de Clases — 10 de agosto
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P36 · cruce

¿En qué fechas se inscriben las asignaturas del segundo semestre 2026 y cuál es el mínimo de créditos?

**Referencia:** inscripción 03–07 de agosto de 2026; mínimo 8 créditos · CAL 2º sem 2026 + Art. 8, RI-FI

**Baseline (0):**

```text
La información sobre fechas de inscripción y créditos mínimos no está especificada en la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción.
```

Omite fechas, mínimo de créditos y fuentes.

**RAG (0):**

```text
DATO: [Calendario 2026, Segundo Semestre 2026]: Inscripción de Asignaturas — 03 – 07 de agosto
CITA: [Calendario 2026, Segundo Semestre 2026]
```

Responde fechas pero omite mínimo de ocho créditos y Art. 8 RI-FI.


## P37 · cruce

¿Cuándo termina el segundo semestre 2026 (término de clases)?

**Referencia:** 11 de diciembre de 2026 · CAL 2º sem 2026

**Baseline (0):**

```text
La fecha exacta del término de clases del segundo semestre 2026 no está especificada en la normativa proporcionada. Para obtener la información precisa, se debe consultar el calendario académico oficial de la Facultad de Ingeniería de la Universidad de Concepción.
```

Abstención indebida ante fecha 11 de diciembre.

**RAG (1):**

```text
DATO: 11 de diciembre
CITA: [Calendario 2026, Segundo Semestre 2026]: Término de Clases — 11 de diciembre
```

Dato completo (se aceptan paráfrasis y equivalencias numéricas) y todas las fuentes requeridas.


## P38 · cruce

La escala de notas del Reglamento General, ¿se aplica en Ingeniería, y cuál es la nota de aprobación?

**Referencia:** sí, escala 1 a 7 (Art. 23, RG); se aprueba con 4,0 (Art. 11, RI-FI) · Art. 23 RG + Art. 11 RI-FI

**Baseline (0):**

```text
La escala de notas del Reglamento General **no se aplica en la Facultad de Ingeniería** de la Universidad de Concepción. La nota de aprobación en la Facultad de Ingeniería es **4.0** (Art. 10 del Reglamento General).
```

Niega aplicación de escala y cita Art. 10; falta Art. 23 RG y Art. 11 RI-FI.

**RAG (0):**

```text
DATO: Sí, se aplica en Ingeniería. La nota de aprobación es 4,0 (cuatro coma cero).
CITA: [Art. 23, RG]
```

Omite escala 1–7 y Art. 11 RI-FI; Art. 23 RG no basta para las dos fuentes requeridas.


## P39 · cruce

¿Cuándo son las Evaluaciones de Recuperación del segundo semestre 2026?

**Referencia:** 14–23 de diciembre de 2026 · CAL 2º sem 2026 (Art. 12 RI-FI)

**Baseline (0):**

```text
La información sobre las fechas de las Evaluaciones de Recuperación del segundo semestre 2026 no está disponible en la normativa actual de pregrado de la Facultad de Ingeniería de la Universidad de Concepción.
```

Abstención indebida ante fechas de recuperación.

**RAG (1):**

```text
DATO: 14 – 23 de diciembre
CITA: [Calendario 2026, Segundo Semestre 2026]
```

El calendario citado da íntegramente las fechas pedidas; Art. 12 RI-FI regula el derecho a recuperación, no esas fechas.


## P40 · cruce

¿Qué reglamento rige la Memoria de Título y cuánto pondera en la nota de titulación?

**Referencia:** la rige el Reglamento de Memoria de Título de la FI (Art. 29); pondera un 40% (Art. 30) · Art. 29 y Art. 30, RI-FI

**Baseline (0):**

```text
La Memoria de Título está regida por el **Reglamento de Pregrado de la Facultad de Ingeniería**, específicamente por el **Art. 12**, que establece que la Memoria de Título es un componente obligatorio del trabajo de título.

En cuanto a su ponderación en la nota de titulación, según el **Art. 13**, la Memoria de Título representa **un 20%** de la calificación final del trabajo de título.
```

Reglamento, porcentaje 20% y artículos incorrectos.

**RAG (0):**

```text
DATO: El Reglamento de Memoria de Título de la Facultad de Ingeniería rige la Memoria de Título y pesa un 40% en la nota de titulación.
CITA: [Art. 29°, RI-FI]
```

Reglamento y 40% correctos; omite Art. 30 RI-FI que fundamenta la ponderación.


## P41 · abstencion

¿Qué establece el Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería?

**Referencia:** El artículo no existe: el RI-FI tiene solo 35 artículos -> debe indicarlo, no inventar · dato inexistente (RI-FI llega al Art. 35)

**Baseline (0):**

```text
El Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería establece que **el docente tiene la obligación de participar en la evaluación de los estudiantes**, incluyendo la elaboración de instrumentos de evaluación y la calificación de las actividades académicas.
```

Inventa contenido del inexistente Art. 90.

**RAG (1):**

```text
DATO: No está en la normativa
CITA: Ninguna
```

Abstención explícita sin añadir contenido inventado, aceptada según protocolo original.


## P42 · abstencion

¿Qué requisitos fija el Artículo 36 del Reglamento Interno de Docencia de Pregrado de Ingeniería?

**Referencia:** El artículo no existe: el reglamento termina en el Art. 35 -> debe indicarlo · dato inexistente (RI-FI llega al Art. 35)

**Baseline (0):**

```text
El Artículo 36 del Reglamento Interno de Docencia de Pregrado de Ingeniería fija que el estudiante debe presentar una **acta de inscripción** y una **acta de matrícula** para participar en actividades docentes.
```

Inventa requisitos del inexistente Art. 36 RI-FI.

**RAG (1):**

```text
DATO: No está en la normativa
CITA: Ninguna
```

Abstención explícita sin añadir contenido inventado, aceptada según protocolo original.


## P43 · abstencion

¿Qué dispone el Artículo 100 del Reglamento General de Docencia de Pregrado?

**Referencia:** El artículo no existe: el RG llega hasta el Art. 60 -> debe indicarlo · dato inexistente (RG llega al Art. 60)

**Baseline (0):**

```text
El Artículo 100 del Reglamento General de Docencia de Pregrado establece que **el profesor titular, en el caso de no haber sido designado como tutor, debe asumir la tutoría del estudiante**.
```

Inventa contenido del inexistente Art. 100 RG.

**RAG (1):**

```text
DATO: No está en la normativa
CITA: Ninguna
```

Abstención explícita sin añadir contenido inventado, aceptada según protocolo original.


## P44 · abstencion

¿Qué señala el Artículo 70 del Reglamento General de Docencia de Pregrado?

**Referencia:** El artículo no existe: el RG llega hasta el Art. 60 -> debe indicarlo · dato inexistente (RG llega al Art. 60)

**Baseline (0):**

```text
El Artículo 70 del Reglamento General de Docencia de Pregrado señala que **el docente tiene derecho a la remuneración por el trabajo docente, que se determinará en función de la carga horaria, el nivel de enseñanza y la calidad del trabajo docente**.
```

Inventa contenido del inexistente Art. 70 RG.

**RAG (1):**

```text
DATO: No está en la normativa
CITA: Ninguna
```

Abstención explícita sin añadir contenido inventado, aceptada según protocolo original.


## P45 · abstencion

¿Qué dice el inciso d) del Artículo 14 del RI-FI sobre las causales de baja académica?

**Referencia:** No existe el inciso d): el Art. 14 solo tiene a), b) y c) -> debe indicarlo · premisa falsa (Art. 14 solo a-c)

**Baseline (0):**

```text
El inciso d) del Artículo 14 del RI-FI establece que una de las causales de baja académica es **la falta de asistencia a las clases o actividades académicas, sin justificar, por un período de 30 (treinta) días consecutivos**.
```

Inventa inciso d) y plazo de treinta días.

**RAG (1):**

```text
DATO: No está en la normativa
CITA: Ninguna
```

Abstención explícita sin añadir contenido inventado, aceptada según protocolo original.


## P46 · abstencion

¿Qué establece el inciso c) del Artículo 25 del RI-FI sobre los documentos para suspender estudios?

**Referencia:** No existe el inciso c): el Art. 25 solo tiene a) y b) -> debe indicarlo · premisa falsa (Art. 25 solo a-b)

**Baseline (0):**

```text
El inciso c) del Artículo 25 del RI-FI establece que **se considera como documento para suspender estudios el certificado de nacimiento o de registro civil de la persona**.
```

Inventa inciso c) y certificado de nacimiento.

**RAG (1):**

```text
DATO: No está en la normativa
CITA: Ninguna
```

Abstención explícita sin añadir contenido inventado, aceptada según protocolo original.


## P47 · abstencion

Además del mínimo de créditos, ¿cuál es el número máximo de créditos que fija el Artículo 8 del RI-FI para inscribir por semestre?

**Referencia:** El Art. 8 no fija un máximo, solo un mínimo (8) -> debe indicarlo · premisa falsa (Art. 8 solo fija mínimo)

**Baseline (0):**

```text
Art. 8 del RI-FI: 60 créditos.
```

Inventa máximo de 60 créditos.

**RAG (1):**

```text
DATO: No está en la normativa
CITA: Ninguna
```

Abstención explícita sin añadir contenido inventado, aceptada según protocolo original.


## P48 · abstencion

¿Cuál es la nota mínima que fija el Artículo 12 del RI-FI para la Evaluación de Recuperación?

**Referencia:** El Art. 12 no fija una nota mínima; solo otorga el derecho a la recuperación -> debe indicarlo · premisa falsa (Art. 12 no fija nota)

**Baseline (0):**

```text
El Artículo 12 del RI-FI fija como nota mínima para la Evaluación de Recuperación la calificación **1,0**.
```

Inventa nota mínima de 1,0.

**RAG (1):**

```text
DATO: No está en la normativa
CITA: Ninguna
```

Abstención explícita sin añadir contenido inventado, aceptada según protocolo original.


## P49 · abstencion

Según el calendario de docencia 2026, ¿qué feriado nacional cae el 30 de septiembre?

**Referencia:** No hay feriado el 30 de septiembre; el feriado de septiembre 2026 es el día 18 -> debe indicarlo · dato inexistente (CAL 2026)

**Baseline (0):**

```text
El 30 de septiembre de 2026 no cae en un feriado nacional según el calendario oficial de feriados nacionales de Chile. Este día es un lunes y no corresponde a ningún feriado nacional establecido por la ley. Art. 13 del Reglamento de Feriados Nacionales.
```

Rechaza feriado, pero inventa Art. 13 de una fuente ajena y dice lunes (30-09-2026 es miércoles).

**RAG (1):**

```text
DATO: No está en la normativa
CITA: Ninguna
```

Abstención explícita sin añadir contenido inventado, aceptada según protocolo original.


## P50 · abstencion

El Artículo 19 del RI-FI exige promedio 5,0 para una segunda carrera simultánea; ¿qué promedio exige ese artículo para una tercera carrera simultánea?

**Referencia:** El Art. 19 no contempla una tercera carrera simultánea -> debe indicarlo · premisa falsa (Art. 19 no lo contempla)

**Baseline (1):**

```text
No está en la normativa.
```

Abstención explícita sin contenido inventado.

**RAG (1):**

```text
DATO: No está en la normativa
CITA: Ninguna
```

Abstención explícita sin añadir contenido inventado, aceptada según protocolo original.
