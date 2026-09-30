# Guion de demostración · máximo 3:00

## Preparar antes de grabar

Usar el notebook actualizado en Colab T4. Ejecutar instalación, carga e indexación antes de iniciar la grabación. Ejecutar también las 50 comparaciones, conservar las trazas y revisar resultados. Tener visibles la GPU, modelo, versión de corpus, k y commit/hash. No usar los números históricos como si fueran una nueva evaluación.

Elegir la versión que efectivamente se entregará. Si se usa la base v2, hay que medirla primero. No publicar una cifra provisional sin que el equipo valide la revisión. Mantener el terminal/celda y su ejecución visibles: no editar para esconder latencia o fallos.

## Secuencia sugerida

| Tiempo | Pantalla | Narración orientativa |
| --- | --- | --- |
| 0:00–0:20 | Notebook, hardware y configuración | «Respondemos preguntas de normativa de Ingeniería UdeC. Exigimos dato completo y fuente correcta. En E1, el prompting directo fallaba en conocimiento específico y citación. Usamos el mismo Qwen3-4B en T4.» |
| 0:20–0:40 | Diagrama y metadatos | «Recuperamos cinco fragmentos con E5 multilingüe y los entregamos al modelo. El prompt pide dato y cita. La versión de corpus y los pesos utilizados quedan registrados.» |
| 0:40–1:30 | Ejecutar la celda de demo | Sortear una pregunta al ejecutar o usar una propuesta por otra persona, sin revisar primero la salida. «Esta misma entrada pasa primero por baseline y después por RAG. Ambas respuestas se generan ahora.» Mostrar la respuesta, la latencia y el contexto efectivamente utilizado. Describir lo observado, aunque falle. |
| 1:30–1:55 | Tabla de la corrida ya revisada | «Evaluamos las mismas 50 preguntas bajo el mismo criterio.» Indicar número exacto de aciertos, revisión y tamaño; mencionar si el resultado es histórico o de la nueva corrida. Si se usa la auditoría actual: «Revisamos las salidas históricas y encontramos 44/50 en RAG. La cifra anterior de 98% aceptaba respuestas parciales.» |
| 1:55–2:35 | Fallo real y fragmentos | Mostrar un fallo de la corrida final. En la base histórica, P25 produce una respuesta incompleta: enseñar el Art. 9 cortado ante la referencia al Art. 7 y contrastar con el PDF. Separar recuperación, extracción y generación; no atribuir causas sin ver contexto. |
| 2:35–2:55 | Repositorio y archivos de evidencia | «El repositorio incluye instrucciones, respuestas, contextos y revisión. RAG mejora el acceso a evidencia, pero aún puede omitir condiciones y fuentes. Los datos no son un test externo de generalización.» |
| 2:55–3:00 | Enlace/repositorio | Dejar cinco segundos de margen y terminar. |

## Si el caso histórico ya no falla

No alterar la respuesta ni presentar una salida antigua como ejecución en vivo. Identificarla como histórica y mostrar una falla real de la nueva evaluación, junto con su traza. Si el conjunto actual no contiene fallos, probar nuevas preguntas realistas y documentar la búsqueda; no afirmar que el sistema es infalible.

## Entrega

Subir el video con acceso abierto, comprobar el enlace sin iniciar sesión y colocarlo en el PDF. El enlace todavía no está creado. Conservar el notebook ejecutado y los metadatos de la corrida mostrada.
