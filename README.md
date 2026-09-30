# Asistente de normativa de pregrado · Ingeniería UdeC

**Álvaro Contreras y Pablo Cortés** · Generative Artificial Intelligence (580694), 2026

Este proyecto responde preguntas en español sobre tres documentos de docencia de pregrado de la Universidad de Concepción: el Reglamento General, el Reglamento de la Facultad de Ingeniería y el Calendario de Docencia 2026. Una respuesta debe entregar el dato y una fuente que lo respalde; ante una premisa falsa o información ausente, debe indicarlo.

## Deliverable 2: por dónde empezar

1. Lee la [guía de Deliverable 2](Deliverable2/README.md) para conocer el sistema, los resultados y sus límites.
2. Abre el [cuaderno principal de Colab](Deliverable2/notebooks/Deliverable2_Sistema_RAG_Colab.ipynb) con GPU. Escribe una pregunta y observa en paralelo Qwen3-4B sin documentos y con RAG estructurado. El cuaderno incluye el corpus procesado y no requiere clonar el repositorio en Colab.
3. Consulta la [comparación emparejada](Deliverable2/resultados/qwen3_4b_f0bff499766960f7/REPORTE.md) para revisar las 100 respuestas, veredictos y motivos. La [guía del cuaderno](Deliverable2/notebooks/README.md) detalla la reproducción y la exportación.

[Abrir el cuaderno principal directamente en Google Colab](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable2/notebooks/Deliverable2_Sistema_RAG_Colab.ipynb)

| Evidencia disponible | Resultado | Alcance |
|---|---:|---|
| Baseline directo de Deliverable 1 | 2/50 (4%) | Cifra histórica con sus criterios y parámetros originales |
| Baseline directo emparejado | 1/50 (2%) | Nueva corrida de Colab; mismos parámetros de inferencia que RAG |
| RAG simple | 39/50 (78%) | Primera corrida de Colab; revisión asistida de dato y citas |
| RAG estructurado | 40/50 (80%) | Respuestas idénticas en la primera corrida y en la comparación emparejada |
| RAG estructurado con ejemplos | 36/50 (72%) | Alternativa evaluada y descartada |

**El 2% y el 80% de la nueva corrida sí forman una comparación emparejada** sobre las mismas 50 preguntas, modelo, configuración de inferencia y pauta de evaluación. El 4% histórico de E1 se mantiene separado. La intervención compara evidencia recuperada más prompt estructurado frente a prompt directo sin documentos; las 50 preguntas se usaron durante el desarrollo y no miden generalización a preguntas nuevas. El [piloto consultable](Deliverable2/resultados/piloto_consulta_882da178b0514f0d/REPORTE.md) prueba una pregunta adicional sin convertirla en porcentaje.

## Organización

| Ruta | Contenido |
|---|---|
| [Deliverable2](Deliverable2/README.md) | Sistema, corpus procesado, recuperación, evaluación y resultados |
| [Deliverable1](Deliverable1/README.md) | Informe, notebooks y salidas originales de la primera entrega; archivos preservados |
| [Corpus](Corpus/) | Los tres PDF normativos compartidos |
| [Archivo](Archivo/README.md) | Prototipos anteriores conservados para consulta; no son la implementación vigente |

El [enunciado de Deliverable 2](Deliverable2/enunciado.pdf) exige un PDF técnico de una página compilado desde LaTeX y un video de ejecución de hasta tres minutos. El [PDF, su fuente y el video de 2:44](Deliverable2/entrega/README.md) están en la carpeta de entrega. La grabación muestra una consulta real en Colab con baseline y RAG sobre la misma entrada; el reporte y el caso P25 completan la demostración.
