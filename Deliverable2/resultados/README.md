# Corridas de generación y evaluación

| Corrida | Modelo | Respuestas | Simple | Estructurado | Few-shot |
|---|---|---:|---:|---:|---:|
| [4adccec813c53d7f](qwen3_4b_4adccec813c53d7f/REPORTE.md) | Qwen3-4B NF4, sin thinking | 150 | 39/50 (78%) | 40/50 (80%) | 36/50 (72%) |

Porcentajes de revisión asistida en chat con la pauta de contenido y citas. Se conservan el ZIP original, los prompts, las respuestas, los veredictos y sus motivos. No hay cortes por límite de tokens. El reporte explica los errores de few-shot y los límites de comparar una sola corrida sobre preguntas usadas durante el desarrollo.

El [piloto del sistema consultable](piloto_consulta_882da178b0514f0d/REPORTE.md) conserva una pregunta nueva respondida en Colab por baseline directo y RAG estructurado. Demuestra la ejecución real de ambas condiciones, pero sus dos respuestas no se incluyen en los porcentajes de la tabla ni sustituyen el lote emparejado de 50 preguntas.
