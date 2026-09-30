# Video de Deliverable 2

[Video_D2.mp4](Video_D2.mp4) dura **2:44**. Tiene video H.264 a 2816 × 1762 y narración sintética en español.

## Qué se ve realmente

| Tiempo | Contenido |
|---|---|
| 0:00–0:43 | Grabación de la sesión original de Brave/Colab: código y salidas ya ejecutadas de preparación del corpus, índice E5 y carga de Qwen3-4B. No se repite la carga del modelo. |
| 0:43–1:18 | Se escribe y ejecuta **una vez** una pregunta en la sección 5, con baseline directo y RAG estructurado sobre la misma entrada. Ambos estados aparecen como `generada ahora`. |
| 1:18–1:46 | Se muestran las dos respuestas y el panel de evidencia. El baseline dice equivocadamente que no hay baja académica con 14 créditos; RAG responde que sí y cita RI-FI art. 14. |
| 1:46–2:04 | Se muestra la sección 6 y la salida ya terminada del lote previo de 100 respuestas, sin volver a ejecutarlo. |
| 2:04–2:19 | Imagen fija de la página pública del reporte emparejado: baseline 1/50 y RAG estructurado 40/50. |
| 2:19–2:44 | Grabación de pantalla de la página pública del diagnóstico P25: respuesta estructurada incompleta aunque recibió los artículos 7 y 9 completos. |

La pregunta ejecutada en vivo fue: «Terminé mi segundo semestre en Ingeniería con 14 créditos aprobados. ¿Quedo en baja académica? Indica la norma que lo establece». Es una formulación nueva sobre un umbral tratado en las 50 preguntas conocidas. **No se sumó al 80 % ni se usa para afirmar generalización.** El artículo [RI-FI-ART-014](../corpus/generado/corpus.md) establece la baja al aprobar menos de 15 créditos al término del segundo semestre.

La primera parte es una captura real continua. Solo se recortó el tramo posterior en que se abrió otra ventana. Los dos tramos finales muestran resultados ya publicados; la tabla es una captura fija y P25 es otra grabación de pantalla. La voz se sintetizó después para explicar las imágenes, sin modificar ninguna respuesta del modelo.

## Transcripción de la voz

1. «Este cuaderno de Colab es el sistema RAG del Deliverable dos. Las salidas iniciales ya estaban calculadas en esta sesión; ahora mostraremos una consulta nueva sin repetir la carga del modelo».
2. «El corpus combina tres documentos. La segmentación conserva ciento noventa y siete unidades normativas completas y doscientos un fragmentos de búsqueda. E cinco recupera la evidencia, y Qwen tres, de cuatro mil millones de parámetros, responde en la GPU».
3. «En la sección cinco escribimos una pregunta que no formó parte de las cincuenta de evaluación: si catorce créditos aprobados al segundo semestre de Ingeniería causan baja académica. La misma entrada se ejecuta con baseline directo y con RAG estructurado».
4. «La ejecución terminó en ambas condiciones. Sin documentos, el modelo dijo que no habría baja y citó una norma equivocada. Con RAG respondió que sí, porque el artículo catorce exige al menos quince créditos al término del segundo semestre, y entregó su cita».
5. «La sección seis conserva el lote anterior: cincuenta preguntas en ambas condiciones, cien respuestas generadas. Estas respuestas quedan guardadas en un ZIP y se evalúan fuera de Colab con una misma pauta».
6. «El reporte público muestra los resultados emparejados: una de cincuenta correctas sin documentos, y cuarenta de cincuenta con RAG. Son preguntas conocidas; la consulta nueva no se agregó a ese porcentaje».
7. «Un caso fallido documentado es P veinticinco. Aunque el contexto contenía los artículos siete y nueve, la respuesta estructurada solo remitió a las prioridades a y b. No explicó que eran asignaturas atrasadas y obligatorias reprobadas sin aprobar. Fue una respuesta incompleta, no un corte del texto».
