# Asistente de normativa de pregrado · Ingeniería UdeC

**Álvaro Contreras y Pablo Cortés** · Generative Artificial Intelligence (580694), 2026

Este proyecto responde preguntas en español sobre tres documentos de docencia de pregrado de la Universidad de Concepción: el Reglamento General, el Reglamento de la Facultad de Ingeniería y el Calendario de Docencia 2026. Una respuesta debe entregar el dato y una fuente que lo respalde; ante una premisa falsa o información ausente, debe indicarlo.

## Deliverable 2: por dónde empezar

1. Lee la [guía de Deliverable 2](Deliverable2/README.md) para conocer el sistema, los resultados y sus límites.
2. Abre el [cuaderno principal de Colab](Deliverable2/notebooks/Deliverable2_Sistema_RAG_Colab.ipynb) con GPU. Escribe una pregunta y observa en paralelo Qwen3-4B sin documentos y con RAG estructurado. El cuaderno incluye el corpus procesado y no requiere clonar el repositorio en Colab.
3. Consulta el [reporte de la primera corrida](Deliverable2/resultados/qwen3_4b_4adccec813c53d7f/REPORTE.md) para revisar respuestas, veredictos y un fallo explicado. La [guía del cuaderno](Deliverable2/notebooks/README.md) detalla la reproducción y la exportación.

[Abrir el cuaderno principal directamente en Google Colab](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable2/notebooks/Deliverable2_Sistema_RAG_Colab.ipynb)

| Evidencia disponible | Resultado | Alcance |
|---|---:|---|
| Baseline directo de Deliverable 1 | 2/50 (4%) | Cifra histórica con sus criterios y parámetros originales |
| RAG simple | 39/50 (78%) | Primera corrida de Colab; revisión asistida de dato y citas |
| RAG estructurado | 40/50 (80%) | Primera corrida de Colab; configuración elegida |
| RAG estructurado con ejemplos | 36/50 (72%) | Alternativa evaluada y descartada |

**Estas cifras no forman todavía una comparación emparejada entre baseline y RAG.** El cuaderno principal prepara una corrida adicional con el mismo modelo, parámetros y preguntas para ambos; su ejecución en Colab y la revisión de sus respuestas están pendientes. Las 50 preguntas se usaron durante el desarrollo de la recuperación, por lo que tampoco miden generalización a preguntas nuevas.

## Organización

| Ruta | Contenido |
|---|---|
| [Deliverable2](Deliverable2/README.md) | Sistema, corpus procesado, recuperación, evaluación y resultados |
| [Deliverable1](Deliverable1/README.md) | Informe, notebooks y salidas originales de la primera entrega; archivos preservados |
| [Corpus](Corpus/) | Los tres PDF normativos compartidos |
| [Archivo](Archivo/README.md) | Prototipos anteriores conservados para consulta; no son la implementación vigente |

El [enunciado de Deliverable 2](Deliverable2/enunciado.pdf) también exige un PDF técnico de una página compilado desde LaTeX y un video de ejecución de hasta tres minutos. **Esos materiales no figuran todavía como entregados en este repositorio.** La demostración final deberá usar el cuaderno principal y mostrar el baseline sobre la misma entrada.
