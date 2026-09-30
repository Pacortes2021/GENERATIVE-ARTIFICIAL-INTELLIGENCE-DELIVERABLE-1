# Deliverable 2 · Sistema RAG para normativa de Ingeniería UdeC

El sistema usa **Qwen3-4B** para responder preguntas sobre el Reglamento General de Docencia de Pregrado, el Reglamento de Docencia de la Facultad de Ingeniería y el Calendario de Docencia 2026. La intervención aporta evidencia recuperada del corpus y un prompt que pide dato, condiciones y citas. El [enunciado](enunciado.pdf) exige mostrarlo funcionando junto a un baseline directo sobre las mismas entradas.

## Ejecutar el sistema

El archivo principal es [Deliverable2_Sistema_RAG_Colab.ipynb](notebooks/Deliverable2_Sistema_RAG_Colab.ipynb). Es autocontenido: incluye el corpus procesado, reconstruye el índice E5 y hace la recuperación para cada consulta nueva. Requiere una sesión de Google Colab con GPU y conexión para descargar los modelos públicos.

[Abrir el sistema directamente en Google Colab](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable2/notebooks/Deliverable2_Sistema_RAG_Colab.ipynb)

1. Sube el cuaderno a Colab, activa GPU, reinicia la sesión si habías abierto una versión anterior y ejecuta las secciones 1–4.
2. En la sección 5 escribe una pregunta en `PREGUNTA` y ejecuta la celda. Muestra **baseline sin documentos y RAG estructurado** sobre la misma entrada, con los fragmentos consultables.
3. Descarga el ZIP de esa consulta. Para generar una comparación adicional sobre las 50 preguntas de E1, usa `EJECUTAR_LOTE_50 = True` e `IDS_LOTE = None` en la sección 6; después vuelve a ejecutar la celda de descarga anterior para obtener el ZIP del lote.
4. Evalúa los dos CSV nuevos con la [misma pauta de contenido y citas](evaluacion/README.md). La evaluación semántica se hace fuera del cuaderno; no se calcula a partir de palabras clave.

La [guía del cuaderno](notebooks/README.md) explica la configuración, los checkpoints, la exportación y el diagnóstico de Colab. El código que genera el notebook está en [crear_sistema.py](notebooks/crear_sistema.py); las funciones de consulta e inferencia están en [sistema.py](notebooks/sistema.py).

## Modelo e intervención

Deliverable 1 propuso Qwen3-4B, Salamandra-7B y Qwen3-8B. Se eligió **Qwen3-4B** por ser el menor de los tres y porque el conocimiento específico de la tarea se puede aportar desde un corpus recuperable. El 8B se probó en E1 como comparación histórica y también obtuvo 2/50; Salamandra no se ejecutó. La [configuración elegida](CONFIGURACION_ELEGIDA.md) registra revisión, cuantización, generación y límites.

La tubería consulta los fragmentos con `intfloat/multilingual-e5-small`, expande cada coincidencia a la unidad normativa completa, añade remisiones e inventarios cuando corresponde y envía la evidencia seleccionada a Qwen3-4B. El baseline recibe únicamente la pregunta y la instrucción directa de E1. Ambas condiciones de la comparación adicional comparten pesos, parámetros y semilla por pregunta. El corpus y los prompts se guardan con hashes; las respuestas de referencia quedan fuera de la generación.

```text
Pregunta ──┬──> Qwen3-4B sin documentos ───────────────────> Respuesta baseline
           └──> E5 → fragmentos → unidades/citas → Qwen3-4B ──> Respuesta RAG
```

La [preparación del corpus](corpus/README.md) explica la extracción de los tres PDF, las 197 unidades y los 201 fragmentos; la [recuperación](recuperacion/README.md) describe su política y cobertura. Los tres documentos originales están en [Corpus](../Corpus/).

## Resultados medidos

La [primera corrida de Colab](resultados/qwen3_4b_4adccec813c53d7f/REPORTE.md) generó 150 respuestas sobre las mismas 50 preguntas con evidencia congelada. Las 150 terminaron normalmente. La IA de este chat aplicó la pauta de dato suficiente, cita pertinente y ausencia de afirmaciones falsas; cada decisión y motivo se conservan.

| Condición | Correctas | Observación |
|---|---:|---|
| RAG simple | 39/50 (78%) | Instrucción breve |
| RAG estructurado | 40/50 (80%) | Configuración de trabajo elegida |
| RAG estructurado + ejemplos | 36/50 (72%) | Los ejemplos ficticios contaminaron algunas citas; se retiró de la configuración de trabajo |

La diferencia de **una respuesta** entre simple y estructurado no demuestra superioridad general. Las 50 preguntas guiaron el desarrollo del recuperador. El [fallo P25](resultados/qwen3_4b_4adccec813c53d7f/DIAGNOSTICO_P25.md) muestra que el estructurado recibió completos los artículos 7 y 9 pero respondió solo «prioridades a) y b)», sin explicar cuáles eran. Se conserva también la limitación de recuperación de P38.

El **4% de Deliverable 1** se conserva como resultado histórico. Esa corrida utilizó otra configuración de inferencia y su evaluación original; no debe restarse del 80% como si fuese un experimento controlado. La [nueva comparación emparejada](resultados/qwen3_4b_f0bff499766960f7/REPORTE.md) produjo **1/50 (2%) para baseline y 40/50 (80%) para RAG** con la misma pauta E2. El 2% no reemplaza la cifra histórica. La intervención combina recuperación y cambio de prompt, y las preguntas conocidas no prueban generalización.

Un [piloto de una consulta nueva](resultados/piloto_consulta_882da178b0514f0d/REPORTE.md) ya ejecutó las dos condiciones en Colab. El baseline negó erróneamente la revalidación; RAG halló los artículos pertinentes y respondió «sí», pero omitió condiciones presentes en la evidencia. Este caso documenta el funcionamiento y un límite del generador; no es una estimación de precisión.

## Estado de la entrega

| Elemento | Estado |
|---|---|
| Modelo elegido, corpus, recuperador y primera corrida RAG | Realizados y documentados |
| Sistema consultable con baseline visible | Implementado; piloto de una pregunta ejecutado en Colab con Tesla T4 |
| Ejecución del lote emparejado de 50 preguntas en GPU Colab | Realizada; 100 respuestas verificadas |
| Evaluación emparejada baseline/RAG | Realizada con pauta E2 y motivos por respuesta; pendiente de revisión del equipo |
| PDF técnico vertical de una página compilado en LaTeX | [Preparado y verificado](entrega/README.md) |
| Video de pantalla ≤3 minutos y enlace abierto | [Guía para grabar la versión definitiva](entrega/Como_grabar_video_D2.md); grabación pendiente. El video anterior se conserva solo como borrador. |

Los [resultados completos](resultados/README.md) incluyen ZIP original, prompts, respuestas, veredictos y reportes. El código de [evaluación](evaluacion/README.md) prepara casos y calcula porcentajes a partir de decisiones trazables. Los prototipos anteriores están en [Archivo](../Archivo/README.md) y no se usan en la ejecución actual.
