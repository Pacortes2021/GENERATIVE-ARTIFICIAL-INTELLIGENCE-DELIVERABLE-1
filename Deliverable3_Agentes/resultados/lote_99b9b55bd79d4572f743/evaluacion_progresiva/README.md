# Evaluación progresiva mientras continúa la inferencia

Se revisan respuestas ya terminadas e inmutables del **mismo lote v4**, sin alterar el sistema generativo ni seleccionar nuevos intentos. Los paquetes y veredictos se preparan con el evaluador D2 y conservan hashes. No se calculan resultados finales con un lote parcial.

`snapshot_012/`: P01 y P02 en las seis condiciones (12 respuestas nuevas), revisadas directamente contra la pauta y fuentes completas el 27-10-2026. Para añadidos se consultaron RI-FI arts. 11–13 y RG arts. 3.11, 20–25, además de revisar menciones a evaluaciones en el corpus RG. Ninguna etiqueta procede de D1/D2 ni de los pilotos.

Antes de integrar estos juicios en la evaluación final de 300 respuestas, verificar que cada pregunta, respuesta SHA-256, corpus, criterio y versión de referencias coincide exactamente. Si cambió una respuesta o la pauta, volver a evaluarla y conservar el juicio anterior. Los hashes de paquetes parciales no se sustituyen por los de paquetes finales; conservar ambas etapas y documentar la integración. Hasta entonces, estos son juicios progresivos del snapshot, no una comparación completa.

`snapshot_039_p03_p05/`: 18 respuestas de P03–P05 en todas las condiciones, extraídas del snapshot íntegro de 39 con procedencia y SHA-256 registrados. Revisión nueva contra pauta D2 y RG arts. 22, 27 y 3.10 completos. P04 incluye una atribución errónea a RG art. 27 en tres condiciones de agentes; no se considera correcta por contener también la escala correcta. En P03 RAG se distingue el derecho garantizado a una recuperación de un máximo absoluto no expresamente formulado; no afirma derecho a múltiples recuperaciones. No se publican métricas finales de lote.

`snapshot_039_p06/`: P06 revisada en las seis condiciones (seis juicios), con RG art. 25 completo como fuente adicional. Se distingue anticipación de evaluaciones de comunicación posterior de calificaciones. Incluye la primera respuesta pendiente completada después de restaurar el respaldo. Las 36 respuestas de P01–P06 ya tienen juicios progresivos, sin comparación final.

`snapshot_060_p07_p10/`: P07 a P10 revisadas en las seis condiciones (24 respuestas) del snapshot de 60. `agentes_completo`, `rag_d2` y `sin_completitud` obtienen 4/4; `sin_descomposicion` y `sin_verificacion` obtienen 3/4 (fallan P07 por límite de salidas inválidas en la validación literal de citas en el auditor); `baseline_directo` 0/4. El acumulado consolidado para las primeras 10 preguntas (60 respuestas) sitúa a `rag_d2` en 9/10 (90%) y a `agentes_completo` en 8/10 (80%).
