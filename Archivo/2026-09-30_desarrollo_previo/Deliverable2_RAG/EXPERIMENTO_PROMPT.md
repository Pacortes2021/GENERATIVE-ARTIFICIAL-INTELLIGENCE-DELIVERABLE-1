# Experimento de completitud de respuestas

Estado: implementado y pendiente de inferencia en T4. No cambia las calificaciones históricas.

## Hipótesis y límites

El prompt `completo_v1` solicita responder todas las partes, conservar excepciones, vincular cada dato con una fuente y explicar referencias entre artículos cuando su contenido esté en el contexto. No contiene las respuestas del test ni instrucciones particulares por ID.

Se prueban primero P24, P25, P36, P38 y P40 porque fueron los casos revisados durante desarrollo. Son una prueba dirigida de regresión; una mejora en estos cinco casos no permite estimar la exactitud global. Después se ejecutan las 50 preguntas y, si es posible, preguntas nuevas reservadas.

| Caso | Qué se espera mejorar | Evidencia necesaria en el contexto |
| --- | --- | --- |
| P24 | Preservar las excepciones a la baja académica | Art. 14 RI-FI completo, incluidas PLEV y primer año |
| P25 | Explicar qué asignaturas no pueden eliminarse | Art. 9 sin corte y contenido de prioridades a) y b) del Art. 7 RI-FI |
| P36 | Responder fechas y mínimo de créditos | Calendario del semestre y Art. 8 RI-FI |
| P38 | Respaldar aplicación de escala y nota de aprobación | Art. 23 RG y Art. 11 RI-FI |
| P40 | Citar tanto la regulación de la Memoria como su ponderación | Arts. 29 y 30 RI-FI |

El prompt no puede completar evidencia ausente sin arriesgar invenciones. Si un artículo necesario no está en los fragmentos, la siguiente intervención debe ser sobre recuperación. La base corregida v2 repara el corte del Art. 9, pero no garantiza que Art. 7 entre al top-5.

## Por qué se cortó P25

El extractor antiguo dividía texto ante cualquier línea que empezara con «Artículo» y un número. En el PDF, la referencia «Artículo 7°, ni contravenir…» aparece al inicio de una línea **dentro del Art. 9**. El extractor la interpretó como otro encabezado. El bloque etiquetado Art. 9 quedó terminado en «prioridades a) y b) del», y la respuesta histórica reproduce ese corte.

Es un defecto comprobado en el corpus. La corrida histórica no guarda el contexto completo ni los tokens generados, por lo que no se atribuye con certeza toda la conducta a ese defecto ni se afirma que se alcanzó el límite de salida. La nueva ejecución guarda ambas cosas.

## Comparación controlada

1. Conservar el corpus histórico para medir inicialmente solo el cambio de prompt.
2. Ejecutar la celda «Comparación de prompts» del notebook. Recupera una sola vez por pregunta y envía exactamente los mismos fragmentos a `historico` y `completo_v1`, con el mismo modelo, k=5, generación greedy y 256 tokens máximos.
3. Leer ambas respuestas con sus trazas. Comprobar si el artículo necesario estaba, si se respondió cada parte y si se llegó al límite de salida. No hay calificación automática por palabras clave.
4. Seleccionar `completo_v1` para la evaluación de 50 preguntas. Las respuestas y veredictos nuevos se guardan aparte de los históricos.
5. Repetir con corpus v2 para medir el efecto adicional del extractor. Para atribuir efectos con mayor claridad, comparar ambos prompts en ambas bases. No sumar mejoras que no se hayan observado.

Los resultados de la comparación dirigida se guardan en `comparacion_prompts.jsonl`, junto con el texto de ambos prompts y los metadatos. Las latencias de esa comparación miden solo generación: la recuperación es compartida y se excluye. No compararlas directamente con la latencia de extremo a extremo histórica.

El prompt nuevo permite respuestas parciales explícitas. En una pregunta con respuesta completa disponible en el corpus, declarar una parte sin evidencia sigue contando como fallo de completitud. Una abstención prudente no se convierte automáticamente en acierto.
