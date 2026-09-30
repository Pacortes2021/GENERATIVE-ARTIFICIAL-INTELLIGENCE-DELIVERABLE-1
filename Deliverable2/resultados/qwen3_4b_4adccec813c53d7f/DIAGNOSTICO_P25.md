# P25: la evidencia estaba completa

Pregunta: **Al modificar la inscripción, ¿qué asignaturas NO puedo eliminar?**

Se comparó el texto íntegro de las unidades del corpus con los prompts originales guardados del ZIP, sin regenerar respuestas. Los artículos 7 y 9 están completos en los mensajes de RAG simple y estructurado.

## RI-FI-ART-007

Artículo 7°. En cada periodo lectivo ordinario, las y los estudiantes podrán inscribir las asignaturas para las cuales cumplan requisito, en las fechas que se indiquen en el calendario anual de docencia de pregrado, con las siguientes prioridades: a) Las asignaturas atrasadas con respecto a su nivel de avance en el Plan de Estudio. b) Las asignaturas obligatorias reprobadas anteriormente y no aprobadas a la fecha. c) Las asignaturas correspondientes a su nivel de avance en el Plan de Estudio. d) Las asignaturas que desee adelantar con respecto a su nivel de avance en el plan de Estudio.

## RI-FI-ART-009

Artículo 9°. La modificación de la inscripción de asignaturas deberá hacerse en las fechas que se indiquen en el calendario anual de docencia y en ella se podrá agregar o eliminar asignaturas. No obstante, no se podrá eliminar las asignaturas correspondientes a las prioridades a) y b) del Artículo 7°, ni contravenir el número mínimo de créditos exigidos en el Artículo 8°.

## rag_simple

Al modificar la inscripción, no puedes eliminar las asignaturas correspondientes a las prioridades a) y b) del Artículo 7°, según lo establecido en el artículo 9°. Estas prioridades son: a) Las asignaturas atrasadas con respecto a su nivel de avance en el Plan de Estudio, y b) Las asignaturas obligatorias reprobadas anteriormente y no aprobadas a la fecha. Por lo tanto, estas asignaturas no pueden ser eliminadas durante la modificación de la inscripción.

Motivo de parada: `eos`. Hash del prompt: `06b4653e90a1930ccfc9ebeeadc4b4ea699fa784a166525efbbc4f4b8df4a84f`.

## rag_estructurado

Respuesta: No se podrá eliminar las asignaturas correspondientes a las prioridades a) y b) del Artículo 7°.  
Condiciones o límites: Las asignaturas que no se pueden eliminar son las que corresponden a las prioridades a) y b) del Artículo 7°.  
Fuente: [RI-FI-ART-009]

Motivo de parada: `eos`. Hash del prompt: `20f21ae1f0efebfb138868ddac7ecb65c42a0ce965ec4650b979b1289d8c85d6`.

## Diagnóstico

El artículo 9 prohíbe eliminar prioridades a) y b) del artículo 7. El artículo 7 las define como asignaturas atrasadas y obligatorias reprobadas aún no aprobadas. El estructurado repitió la remisión sin explicar esas categorías, pese a tenerlas disponibles. El simple sí las identificó con la misma evidencia. Ambas respuestas terminaron con EOS.

La evidencia observada descarta un corte de esos artículos o de la salida como causa de este caso. Se clasifica como respuesta incompleta por uso insuficiente de evidencia disponible. No podemos determinar el mecanismo interno del modelo ni afirmar que más instrucciones vayan a resolverlo. Esto no demuestra que todo el corpus sea perfecto; el diagnóstico se limita a P25 en esta corrida.
