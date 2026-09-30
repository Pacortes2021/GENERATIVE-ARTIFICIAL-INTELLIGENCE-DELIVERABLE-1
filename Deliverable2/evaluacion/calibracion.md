# Muestra para calibrar el evaluador

**Diez ejemplos para revisar juntos, sin nueva ejecución de Qwen ni medición de su rendimiento.** Seis respuestas son históricas de Qwen3-4B; cuatro son ejemplos sintéticos escritos por el asistente para mostrar casos que el baseline casi no produce.

Los veredictos de abajo son propuestas del asistente, pendientes de validación humana. No son resultados de un juez por API ni etiquetas humanas independientes. El 4% de E1 permanece sin cambios.

Al revisarlos, interesa comprobar si compartimos el criterio: un dato correcto con cita equivocada falla; omitir una parte solicitada falla; una paráfrasis completa y respaldada pasa. No se exige información que la pregunta no solicita.

## Caso 1 · P1 · salida histórica de Qwen3-4B

**Pregunta:** ¿Cuál es la nota mínima para aprobar una asignatura en la Facultad de Ingeniería?

**Respuesta guardada:** La nota mínima para aprobar una asignatura en la Facultad de Ingeniería de la Universidad de Concepción es **4.0** (Art. 8).

**Referencia E1:** 4,0 — Art. 11, RI-FI.

**Veredicto propuesto: Incorrecta.** El 4,0 es correcto, pero RI-FI art. 8 regula créditos, no aprobación. La fuente pertinente es RI-FI art. 11 (también RG art. 23).

**Evidencia consultada:** RI-FI arts. 8 y 11; RG art. 23.

## Caso 2 · P11 · salida histórica de Qwen3-4B

**Pregunta:** ¿Cuál es el mínimo de créditos que debo inscribir por período lectivo ordinario en Ingeniería?

**Respuesta guardada:** El mínimo de créditos que debe inscribirse por período lectivo ordinario en Ingeniería es **60 créditos**. Este requisito está establecido en el **Art. 8** de la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción.

**Referencia E1:** 8 créditos (igual o superior a 8) — Art. 8, RI-FI.

**Veredicto propuesto: Incorrecta.** Dice 60 créditos; la regla general establece ocho. Citar el artículo correcto no salva un dato equivocado.

**Evidencia consultada:** RI-FI art. 8.

## Caso 3 · P24 · salida histórica de Qwen3-4B

**Pregunta:** Si repruebo por segunda vez una misma asignatura obligatoria, ¿qué ocurre?

**Respuesta guardada:** Si repruebas por segunda vez una misma asignatura obligatoria, se considera que has incumplido el régimen académico y podrías ser inhabilitado para continuar en el programa de estudios, según el **Art. 12** de la normativa de pregrado.

**Referencia E1:** baja académica, salvo que la haya aprobado en el PLEV o esté en primer año — Art. 14 c), RI-FI.

**Veredicto propuesto: Incorrecta.** Omite las excepciones del PLEV y primer año de permanencia y cita el art. 12, que trata recuperación.

**Evidencia consultada:** RI-FI arts. 12 y 14 c).

## Caso 4 · P25 · salida histórica de Qwen3-4B

**Pregunta:** Al modificar la inscripción, ¿qué asignaturas NO puedo eliminar?

**Respuesta guardada:** No está en la normativa.

**Referencia E1:** las atrasadas y las obligatorias reprobadas (prioridades a y b del Art. 7) — Art. 9, RI-FI.

**Veredicto propuesto: Incorrecta.** Se abstiene aunque RI-FI art. 9, mediante las prioridades del art. 7 a–b, permite responder.

**Evidencia consultada:** RI-FI arts. 7 y 9.

## Caso 5 · P36 · salida histórica de Qwen3-4B

**Pregunta:** ¿En qué fechas se inscriben las asignaturas del segundo semestre 2026 y cuál es el mínimo de créditos?

**Respuesta guardada:** La información sobre fechas de inscripción y créditos mínimos no está especificada en la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción.

**Referencia E1:** inscripción 03–07 de agosto de 2026; mínimo 8 créditos — CAL 2º sem 2026 + Art. 8, RI-FI.

**Veredicto propuesto: Incorrecta.** Se abstiene aunque el calendario da 03–07 de agosto y RI-FI art. 8 da el mínimo general de ocho créditos.

**Evidencia consultada:** CAL segundo semestre, página 2; RI-FI art. 8.

## Caso 6 · P50 · salida histórica de Qwen3-4B

**Pregunta:** El Artículo 19 del RI-FI exige promedio 5,0 para una segunda carrera simultánea; ¿qué promedio exige ese artículo para una tercera carrera simultánea?

**Respuesta guardada:** No está en la normativa.

**Referencia E1:** El Art. 19 no contempla una tercera carrera simultánea -> debe indicarlo — premisa falsa (Art. 19 no lo contempla).

**Veredicto propuesto: Correcta.** La negativa evita inventar un promedio para una tercera carrera, que ese artículo no especifica. Se acepta una negativa genérica inequívoca para mantener el criterio histórico; una explicación explícita sería más informativa.

**Evidencia consultada:** RI-FI art. 19.

## Caso 7 · P36 · ejemplo sintético, no generado por Qwen

**Pregunta:** ¿En qué fechas se inscriben las asignaturas del segundo semestre 2026 y cuál es el mínimo de créditos?

**Respuesta didáctica:** La inscripción es del 3 al 7 de agosto de 2026 (Calendario 2026, segundo semestre). El mínimo general es de 8 créditos (art. 8, RI-FI).

**Referencia E1:** inscripción 03–07 de agosto de 2026; mínimo 8 créditos — CAL 2º sem 2026 + Art. 8, RI-FI.

**Veredicto propuesto: Correcta.** Responde las dos partes y respalda cada una. Se admite expresar el mínimo como regla general sin exigir una transcripción completa del artículo.

**Evidencia consultada:** CAL página 2; RI-FI art. 8.

## Caso 8 · P36 · ejemplo sintético, no generado por Qwen

**Pregunta:** ¿En qué fechas se inscriben las asignaturas del segundo semestre 2026 y cuál es el mínimo de créditos?

**Respuesta didáctica:** La inscripción es del 3 al 7 de agosto de 2026 (Calendario 2026, segundo semestre).

**Referencia E1:** inscripción 03–07 de agosto de 2026; mínimo 8 créditos — CAL 2º sem 2026 + Art. 8, RI-FI.

**Veredicto propuesto: Incorrecta.** La fecha y su fuente son correctas, pero falta el mínimo de créditos que la pregunta también solicita.

**Evidencia consultada:** CAL página 2; RI-FI art. 8.

## Caso 9 · P38 · ejemplo sintético, no generado por Qwen

**Pregunta:** La escala de notas del Reglamento General, ¿se aplica en Ingeniería, y cuál es la nota de aprobación?

**Respuesta didáctica:** Sí, se aplica el Reglamento General en Ingeniería (art. 2, RI-FI). La nota mínima de aprobación es 4,0 (art. 23, RG; art. 11, RI-FI).

**Referencia E1:** sí, escala 1 a 7 (Art. 23, RG); se aprueba con 4,0 (Art. 11, RI-FI) — Art. 23 RG + Art. 11 RI-FI.

**Veredicto propuesto: Correcta.** Responde aplicabilidad y nota, con respaldo. La pregunta no exige repetir el rango 1–7 ni usar las mismas palabras del gold.

**Evidencia consultada:** RI-FI arts. 2 y 11; RG art. 23.

## Caso 10 · P40 · ejemplo sintético, no generado por Qwen

**Pregunta:** ¿Qué reglamento rige la Memoria de Título y cuánto pondera en la nota de titulación?

**Respuesta didáctica:** La Memoria se rige por el Reglamento de Memoria de Título de la Facultad de Ingeniería y pondera 40% en la nota de titulación (art. 29, RI-FI).

**Referencia E1:** la rige el Reglamento de Memoria de Título de la FI (Art. 29); pondera un 40% (Art. 30) — Art. 29 y Art. 30, RI-FI.

**Veredicto propuesto: Incorrecta.** Los dos datos son correctos, pero el art. 29 solo respalda qué reglamento la rige. La ponderación está en el art. 30 y falta ese respaldo.

**Evidencia consultada:** RI-FI arts. 29 y 30.

## Cómo seguiremos

Resolveremos los desacuerdos antes de fijar los criterios. Luego podremos evaluar una corrida real mediante `paquete.json` y guardar sus veredictos. Para comprobar la calidad del juez se revisará otra muestra independiente; coincidir con estos ejemplos ya explicados no basta para afirmar que el juez está validado.
