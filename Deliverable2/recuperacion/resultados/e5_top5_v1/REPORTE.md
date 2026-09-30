# Primera prueba de recuperación E5

Se recuperaron los **5 fragmentos** más cercanos de cada pregunta, se expandieron a su unidad completa y se eliminaron duplicados. No se ejecutó Qwen ni se reescribieron consultas.

**40/45** preguntas tienen todas las fuentes de la pauta en el contexto; **5** tienen cobertura incompleta. Otras **5** requieren verificar ausencia en el inventario completo y quedan pendientes.

Esta es una métrica de cobertura de fuentes, no el porcentaje de respuestas correctas. La pauta no enumera todas las alternativas válidas: una fuente no recuperada merece revisión, no convierte automáticamente una respuesta futura en incorrecta.

Contexto medio: 2881 caracteres; máximo: 7716. Aún no se han medido tokens con Qwen.

## Diagnóstico por cantidad de fragmentos

El valor principal k=5 se fijó antes de revisar resultados. Los otros cortes muestran sensibilidad al presupuesto; no se eligió después el que más aciertos daba.

| Fragmentos | Cobertura completa | Porcentaje sobre 45 preguntas evaluables |
|---:|---:|---:|
| 1 | 29/45 | 64.44% |
| 3 | 37/45 | 82.22% |
| 5 | 40/45 | 88.89% |
| 10 | 43/45 | 95.56% |

## Casos que requieren revisión

### P25: Al modificar la inscripción, ¿qué asignaturas NO puedo eliminar?

Recuperado: RI-FI-ART-009, RG-ART-042, RG-ART-003-DEF-13, RG-ART-003-DEF-09, RG-ART-003-DEF-10.

Fuentes de la pauta ausentes: RI-FI-ART-007.

- RI-FI-ART-009: primer fragmento en posición 1.
- RI-FI-ART-007: primer fragmento en posición 8.

### P34: ¿Tengo derecho a suspender estudios y hasta cuándo puedo hacerlo?

Recuperado: RG-ART-031, RG-ART-032, RI-FI-ART-027, RG-ART-035, RI-FI-ART-031.

Fuentes de la pauta ausentes: RI-FI-ART-025.

- RG-ART-031: primer fragmento en posición 1.
- RI-FI-ART-025: primer fragmento en posición 8.

### P36: ¿En qué fechas se inscriben las asignaturas del segundo semestre 2026 y cuál es el mínimo de créditos?

Recuperado: CAL-2026-S2-01, CAL-2026-S2-03, CAL-2026-S2-04, CAL-2026-S2-07, CAL-2026-S2-09.

Fuentes de la pauta ausentes: RI-FI-ART-008.

- CAL-2026-S2-01: primer fragmento en posición 1.
- RI-FI-ART-008: primer fragmento en posición 27.

### P38: La escala de notas del Reglamento General, ¿se aplica en Ingeniería, y cuál es la nota de aprobación?

Recuperado: RG-ART-023, RG-ANEXO-08, RG-ANEXO-35, RG-ANEXO-15, RG-ANEXO-18.

Fuentes de la pauta ausentes: RI-FI-ART-002.

- RI-FI-ART-002: primer fragmento en posición 94.
- RG-ART-023: primer fragmento en posición 1.

### P41: ¿Qué establece el Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería?

Recuperado: RI-FI-ART-002, RG-TRANS-002, RG-ART-049, RG-ART-001, RG-ART-038.

Requiere comprobar el inventario completo del articulado o de los eventos; no se puede demostrar ausencia con top-k.

### P42: ¿Qué requisitos fija el Artículo 36 del Reglamento Interno de Docencia de Pregrado de Ingeniería?

Recuperado: RG-TRANS-002, RG-ART-049, RI-FI-ART-002, RG-ART-001, RG-ART-011.

Requiere comprobar el inventario completo del articulado o de los eventos; no se puede demostrar ausencia con top-k.

### P43: ¿Qué dispone el Artículo 100 del Reglamento General de Docencia de Pregrado?

Recuperado: RG-ART-001, RG-ART-011, RG-ART-004, RG-ART-049, RG-TRANS-002.

Requiere comprobar el inventario completo del articulado o de los eventos; no se puede demostrar ausencia con top-k.

### P44: ¿Qué señala el Artículo 70 del Reglamento General de Docencia de Pregrado?

Recuperado: RG-ART-004, RG-ART-001, RG-PREAMBULO, RG-ART-051, RG-ART-042.

Requiere comprobar el inventario completo del articulado o de los eventos; no se puede demostrar ausencia con top-k.

### P49: Según el calendario de docencia 2026, ¿qué feriado nacional cae el 30 de septiembre?

Recuperado: CAL-2026-S2-09, CAL-2026-S1-12, CAL-2026-S1-13, CAL-2026-S1-11, CAL-2026-S1-10.

Requiere comprobar el inventario completo del articulado o de los eventos; no se puede demostrar ausencia con top-k.

### P50: El Artículo 19 del RI-FI exige promedio 5,0 para una segunda carrera simultánea; ¿qué promedio exige ese artículo para una tercera carrera simultánea?

Recuperado: RG-ART-028, RI-FI-ART-018, RI-FI-ART-014, RI-FI-ART-015, RI-FI-ART-005.

Fuentes de la pauta ausentes: RI-FI-ART-019.

- RI-FI-ART-019: primer fragmento en posición 8.

## Las 50 preguntas

| Nº | Pregunta | Cobertura de pauta | Unidades recuperadas |
|---:|---|---|---|
| 1 | ¿Cuál es la nota mínima para aprobar una asignatura en la Facultad de Ingeniería? | Completa | RI-FI-ART-011, RI-FI-ART-017, RG-ART-027, RI-FI-ART-005, RI-FI-ART-030 |
| 2 | ¿Cuántas evaluaciones sumativas como mínimo debe tener una asignatura? | Completa | RI-FI-ART-011, RG-ART-013, RI-FI-ART-013, RG-ART-007, RI-FI-ART-010 |
| 3 | ¿A cuántas evaluaciones de recuperación tiene derecho el estudiante por asignatura? | Completa | RI-FI-ART-012, RG-ART-022, RG-ART-026, RI-FI-ART-010, RG-ART-025 |
| 4 | ¿En qué escala se expresa la nota final de una asignatura? | Completa | RG-ART-023, RG-ART-027, RG-ART-041, RG-ANEXO-44, RG-ANEXO-45 |
| 5 | ¿Cuál es la actividad final de titulación en las carreras de Ingeniería? | Completa | RI-FI-ART-029, RI-FI-ART-006, RG-ART-003-DEF-10, RI-FI-ART-005, RI-FI-ART-030 |
| 6 | ¿Con cuánta anticipación mínima deben comunicarse las evaluaciones a los estudiantes? | Completa | RG-ART-023, RI-FI-ART-011, RG-ART-025, RI-FI-ART-010, RG-ART-013 |
| 7 | ¿Quién resuelve en primera instancia una solicitud de continuación de estudios? | Completa | RI-FI-ART-016, RG-ART-030, RG-ART-037, RI-FI-ART-027, RI-FI-ART-028 |
| 8 | ¿La renuncia a la carrera es revocable? | Completa | RG-ART-034, RI-FI-ART-026, RG-ART-044, RG-ART-032, RI-FI-ART-022 |
| 9 | ¿Cuántos períodos lectivos ordinarios tiene el año académico y cuánto duran? | Completa | RG-ART-016, RG-ART-050, RI-FI-ART-007, RG-ART-003-DEF-07, RI-FI-ART-008 |
| 10 | ¿Los estudiantes de Primer Año Común pueden convalidar asignaturas? | Completa | RI-FI-ART-022, RG-ART-044, RG-ART-029, RG-ART-037, RG-ART-039 |
| 11 | ¿Cuál es el mínimo de créditos que debo inscribir por período lectivo ordinario en Ingeniería? | Completa | RI-FI-ART-008, RG-ART-003-DEF-07, RI-FI-ART-017, RI-FI-ART-005, RI-FI-ART-030 |
| 12 | ¿Con menos de cuántos créditos aprobados al término del segundo semestre quedo en baja académica? | Completa | RI-FI-ART-014, RG-ART-028, RG-ART-043, RG-ART-003-DEF-07, RI-FI-ART-031 |
| 13 | ¿Bajo qué promedio de créditos aprobados por semestre (desde el 4º) se cae en baja académica? | Completa | RI-FI-ART-014, RG-ART-028, RG-ART-043, RG-ART-003-DEF-07, RG-ART-024 |
| 14 | ¿Cuál es la asistencia mínima máxima que un profesor puede exigir en clases teóricas y prácticas? | Completa | RI-FI-ART-013, RG-ART-020, RG-ART-026, RG-ART-023, RG-ART-049 |
| 15 | ¿Qué calificación mínima se exige para convalidar una asignatura? | Completa | RI-FI-ART-021, RI-FI-ART-011, RG-ART-039, RI-FI-ART-024, RI-FI-ART-013 |
| 16 | ¿Durante cuántas semanas iniciales se puede solicitar convalidación, revalidación o reconocimiento? | Completa | RI-FI-ART-022, RG-ART-025, RI-FI-ART-015, RI-FI-ART-023, RG-ART-044 |
| 17 | ¿Dentro de cuántos días se puede solicitar el reconocimiento de asignaturas? | Completa | RG-ART-038, RI-FI-ART-023, RG-ART-025, RG-ART-037, RI-FI-ART-022 |
| 18 | Si suspendí más de 3 años y solo me faltaba la Memoria, ¿cuántos créditos adicionales máximo debo cursar? | Completa | RI-FI-ART-031, RI-FI-ART-008, RI-FI-ART-014, RG-ART-028, RG-ART-035 |
| 19 | ¿Cuántas semanas dura cada período lectivo ordinario (semestre)? | Completa | RG-ART-016, RG-ART-003-DEF-07, RI-FI-ART-008, RG-ART-043, RG-ART-050 |
| 20 | ¿Cuál es el plazo (en días hábiles) para regularizar una evaluación no rendida por causa justificada? | Completa | RG-ART-026, RG-ART-025, RG-ART-030, RG-ART-038, RG-ART-013 |
| 21 | Si vengo de otra universidad y quiero ingresar a Ingeniería, ¿qué promedio necesito? ¿Y para cambio dentro de Ingeniería? | Completa | RI-FI-ART-018, RI-FI-ART-017, RI-FI-ART-030, RI-FI-ART-001, RI-FI-ART-006 |
| 22 | ¿Qué promedio mínimo se exige para cursar una segunda carrera de forma simultánea? | Completa | RI-FI-ART-018, RI-FI-ART-019, RG-ART-028, RI-FI-ART-005, RI-FI-ART-014 |
| 23 | ¿En qué caso NO se puede revalidar una asignatura? | Completa | RI-FI-ART-020, RG-ART-037, RI-FI-ART-022, RG-ART-041, RG-ART-044 |
| 24 | Si repruebo por segunda vez una misma asignatura obligatoria, ¿qué ocurre? | Completa | RI-FI-ART-020, RG-ART-028, RG-ART-037, RI-FI-ART-014, RG-ART-044 |
| 25 | Al modificar la inscripción, ¿qué asignaturas NO puedo eliminar? | Incompleta | RI-FI-ART-009, RG-ART-042, RG-ART-003-DEF-13, RG-ART-003-DEF-09, RG-ART-003-DEF-10 |
| 26 | Si suspendí mis estudios, ¿qué debo hacer para volver? | Completa | RG-ART-035, RI-FI-ART-027, RG-ART-032, RI-FI-ART-028, RG-ART-033 |
| 27 | ¿Qué documentos requiere la solicitud de suspensión de estudios? | Completa | RG-ART-035, RI-FI-ART-025, RI-FI-ART-027, RG-ART-033, RG-ART-032 |
| 28 | Si estando habilitado no inscribo asignaturas en el período, ¿qué pasa? | Completa | RG-ART-029, RG-ART-042, RG-ART-020, RI-FI-ART-007, RG-ART-043 |
| 29 | Si no me presento a una evaluación por causa justificada, ¿qué puedo hacer? | Completa | RG-ART-026, RG-ART-020, RG-ART-038, RG-ART-025, RI-FI-ART-023 |
| 30 | ¿Cuánta asistencia puede exigir un profesor en un laboratorio, taller o salida a terreno? | Completa | RI-FI-ART-013, RG-ART-020, RG-ART-010, RG-ART-026, RG-ART-003-DEF-07 |
| 31 | Si el Reglamento Interno de Ingeniería contradice al Reglamento General de Docencia, ¿cuál prevalece? | Completa | RI-FI-ART-002, RG-TRANS-002, RI-FI-ART-034, RG-ART-001, RI-FI-ART-018 |
| 32 | Quiero modificar las asignaturas inscritas este segundo semestre 2026. ¿Hasta qué fecha? | Completa | CAL-2026-S2-03, CAL-2026-S2-01, CAL-2026-S1-03, CAL-2026-S2-04, CAL-2026-S2-11 |
| 33 | ¿Hasta qué fecha se pueden modificar asignaturas en el primer semestre 2026? | Completa | CAL-2026-S1-03, CAL-2026-S2-03, CAL-2026-S1-05, CAL-2026-S1-04, CAL-2026-S2-01 |
| 34 | ¿Tengo derecho a suspender estudios y hasta cuándo puedo hacerlo? | Incompleta | RG-ART-031, RG-ART-032, RI-FI-ART-027, RG-ART-035, RI-FI-ART-031 |
| 35 | ¿Cuándo inician las clases del segundo semestre 2026? | Completa | CAL-2026-S2-02, CAL-2026-S2-04, CAL-2026-S2-01, CAL-2026-S2-09, CAL-2026-S2-07 |
| 36 | ¿En qué fechas se inscriben las asignaturas del segundo semestre 2026 y cuál es el mínimo de créditos? | Incompleta | CAL-2026-S2-01, CAL-2026-S2-03, CAL-2026-S2-04, CAL-2026-S2-07, CAL-2026-S2-09 |
| 37 | ¿Cuándo termina el segundo semestre 2026 (término de clases)? | Completa | CAL-2026-S2-04, CAL-2026-S1-04, CAL-2026-S1-05, CAL-2026-S2-03, CAL-2026-S2-07 |
| 38 | La escala de notas del Reglamento General, ¿se aplica en Ingeniería, y cuál es la nota de aprobación? | Incompleta | RG-ART-023, RG-ANEXO-08, RG-ANEXO-35, RG-ANEXO-15, RG-ANEXO-18 |
| 39 | ¿Cuándo son las Evaluaciones de Recuperación del segundo semestre 2026? | Completa | CAL-2026-S2-05, CAL-2026-S1-06, CAL-2026-S2-07, CAL-2026-S2-04, CAL-2026-S2-09 |
| 40 | ¿Qué reglamento rige la Memoria de Título y cuánto pondera en la nota de titulación? | Completa | RI-FI-ART-030, RI-FI-ART-031, RI-FI-ART-029, RG-ART-024, RG-ART-048 |
| 41 | ¿Qué establece el Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería? | Pendiente: ausencia global | RI-FI-ART-002, RG-TRANS-002, RG-ART-049, RG-ART-001, RG-ART-038 |
| 42 | ¿Qué requisitos fija el Artículo 36 del Reglamento Interno de Docencia de Pregrado de Ingeniería? | Pendiente: ausencia global | RG-TRANS-002, RG-ART-049, RI-FI-ART-002, RG-ART-001, RG-ART-011 |
| 43 | ¿Qué dispone el Artículo 100 del Reglamento General de Docencia de Pregrado? | Pendiente: ausencia global | RG-ART-001, RG-ART-011, RG-ART-004, RG-ART-049, RG-TRANS-002 |
| 44 | ¿Qué señala el Artículo 70 del Reglamento General de Docencia de Pregrado? | Pendiente: ausencia global | RG-ART-004, RG-ART-001, RG-PREAMBULO, RG-ART-051, RG-ART-042 |
| 45 | ¿Qué dice el inciso d) del Artículo 14 del RI-FI sobre las causales de baja académica? | Completa | RI-FI-ART-014, RI-FI-ART-027, RI-FI-ART-026, RI-FI-ART-015, RI-FI-ART-013 |
| 46 | ¿Qué establece el inciso c) del Artículo 25 del RI-FI sobre los documentos para suspender estudios? | Completa | RI-FI-ART-027, RI-FI-ART-025, RG-ART-035, RI-FI-ART-031, RI-FI-ART-026 |
| 47 | Además del mínimo de créditos, ¿cuál es el número máximo de créditos que fija el Artículo 8 del RI-FI para inscribir por semestre? | Completa | RI-FI-ART-008, RI-FI-ART-014, RI-FI-ART-031, RI-FI-ART-015, RI-FI-ART-009 |
| 48 | ¿Cuál es la nota mínima que fija el Artículo 12 del RI-FI para la Evaluación de Recuperación? | Completa | RI-FI-ART-012, RG-ART-023, RI-FI-ART-011, RG-ART-022, RG-ART-027 |
| 49 | Según el calendario de docencia 2026, ¿qué feriado nacional cae el 30 de septiembre? | Pendiente: ausencia global | CAL-2026-S2-09, CAL-2026-S1-12, CAL-2026-S1-13, CAL-2026-S1-11, CAL-2026-S1-10 |
| 50 | El Artículo 19 del RI-FI exige promedio 5,0 para una segunda carrera simultánea; ¿qué promedio exige ese artículo para una tercera carrera simultánea? | Incompleta | RG-ART-028, RI-FI-ART-018, RI-FI-ART-014, RI-FI-ART-015, RI-FI-ART-005 |

El texto íntegro de cada contexto y todos los rankings están en `recuperacion.json`. Los hashes de fuentes y vectores están en `manifiesto.json`. Las etiquetas de este reporte se calcularon por pertenencia de IDs; no son juicios manuales sobre respuestas.
