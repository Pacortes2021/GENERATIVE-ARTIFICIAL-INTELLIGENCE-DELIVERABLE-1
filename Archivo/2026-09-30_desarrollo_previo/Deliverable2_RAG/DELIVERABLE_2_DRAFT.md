# Documento técnico de Deliverable 2

La fuente editable vigente es `deliverable2.tex`. La versión anterior se conserva en `evidencia_historica/borrador_original.md`.

El documento actual describe el experimento histórico Qwen3-4B y la revisión asistida por IA de sus 50 respuestas: RAG 44/50 (88%) y baseline 1/50 (2%), exigiendo que las fuentes citadas respalden todos los datos pedidos. E1 publicó 2/50 (4%); el cambio se explica en el documento y el protocolo. Estas decisiones requieren validación del equipo.

Se retiraron las afirmaciones no sustentadas de 98% estricto, Recall@5=98%, latencia de 0,5 s, optimalidad de k=5 y eliminación total de alucinaciones. El formato DATO/CITA se denomina prompt estructurado.

La base v2 corrige segmentación y contiene 169 fragmentos. No hay todavía una evaluación de generación de esa versión. Antes de entregar: elegir una versión, ejecutarla en T4, validar la revisión, actualizar el PDF si cambian resultados y añadir el enlace real del video. No mezclar resultados históricos y actuales.
