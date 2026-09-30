La demostración de Deliverable 2 contenía un baseline fijo, dos celdas no ejecutables y un evaluador que aceptaba respuestas parciales como aciertos. La versión revisada ejecuta baseline y RAG sobre la misma entrada, guarda contextos y metadatos y separa la revisión semántica del recuento verificable.

Se preservan respuestas y notebook históricos. Una revisión asistida por IA, pendiente de validación del equipo, documenta cada decisión con hash y aplica el mismo criterio a ambos sistemas. La base corregida se publica separadamente y no hereda métricas históricas. Se actualizan README, documento técnico y guion de video.

Validación local: pruebas de integridad de evaluación, rechazo de resultados/revisiones desalineados o pendientes, segmentación de artículos, preservación del calendario y sintaxis de todas las celdas. La inferencia completa de Qwen3-4B en T4 y la grabación permanecen pendientes; no se presentan pruebas sin GPU como validación end-to-end.
