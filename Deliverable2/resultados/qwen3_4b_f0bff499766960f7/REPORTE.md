# Comparación emparejada: baseline directo y RAG estructurado

Corrida `f0bff499766960f7`, ejecutada en Colab con Tesla T4 e importada desde el ZIP descargado por el usuario. Contiene las **50 preguntas de Deliverable 1 en ambas condiciones**: 100 respuestas de Qwen3-4B. El baseline recibió la pregunta y el prompt directo de E1, sin documentos. RAG recuperó evidencia del corpus en cada consulta y usó el prompt estructurado. Las condiciones comparten revisión del modelo, cuantización NF4, parámetros de generación, modo sin thinking y semilla por pregunta.

| Condición | Correctas con pauta E2 | Generación media | Recuperación media |
|---|---:|---:|---:|
| Baseline directo, sin documentos | **1/50 (2%)** | 7,21 s | 0 s |
| RAG estructurado | **40/50 (80%)** | 16,13 s | 0,112 s |

La diferencia observada es **39 respuestas, o 78 puntos porcentuales**. En una pregunta acertaron ambos (P50); en 39 acertó solo RAG; en diez fallaron ambos. No hubo casos acertados solo por baseline. Los 100 archivos individuales terminaron con `eos`: cero salidas vacías, cero cortes indicados y cero thinking inesperado. El ZIP pasó las comprobaciones de hashes del generador; los CSV reproducen las respuestas de los checkpoints. La recuperación no omitió unidades por presupuesto.

## Aplicación de la misma pauta

La [pauta v2](../../evaluacion/criterios.md) exige el dato suficiente, citas que lo respalden y ausencia de afirmaciones falsas. Se revisaron las 50 respuestas nuevas del baseline en este chat, con un motivo y el hash de cada respuesta en [sus veredictos](evaluacion/baseline_directo/veredictos.json). Solo P50 fue correcta: negó, sin inventar otro umbral, que el art. 19 de RI-FI fije un promedio para una tercera carrera simultánea. Entre los errores ilustrativos, P01 inventó `14/20` frente al `4,0` de RI-FI art. 11; P24 sustituyó la baja académica y sus excepciones por una supuesta prohibición de repetir; P41–44 atribuyeron contenido a artículos inexistentes.

Las **50 respuestas RAG**, sus prompts, sus evidencias y hasta los tokens de salida coinciden exactamente con la [primera corrida](../qwen3_4b_4adccec813c53d7f/REPORTE.md). También son idénticos la pauta, los criterios y los PDFs. Se trasladaron, caso por caso y con hashes verificados, los [veredictos RAG previos](evaluacion/rag_estructurado/veredictos.json) al nuevo paquete de evaluación. Esto conserva el 40/50 ya revisado; no se fingió una segunda revisión semántica independiente. La igualdad de prompts y evidencia confirma que la recuperación en vivo reconstruyó, para estas 50 preguntas, las mismas entradas de la primera corrida.

| Categoría, diez preguntas cada una | Baseline | RAG |
|---|---:|---:|
| Factual | 0 | 9 |
| Numérica | 0 | 7 |
| Condicional | 0 | 6 |
| Cruce de fuentes | 0 | 8 |
| Premisa falsa o abstención | 1 | 10 |

Los diez errores RAG son P01, P11, P13, P15, P24, P25, P28, P30, P36 y P38. Los [motivos completos](evaluacion/rag_estructurado/reporte/evaluacion.csv) muestran fallos de cita, afirmaciones adicionales incorrectas y excepciones omitidas. En P25, los artículos 7 y 9 estaban en el contexto, pero el modelo solo dijo «prioridades a) y b)» sin identificar las asignaturas. En P38, citó RI-FI art. 6 para justificar la aplicación del Reglamento General, aunque ese artículo trata de cupos; el pertinente es RI-FI art. 2. La ejecución nueva no corrige esos fallos.

## Alcance de la comparación

El **4% de Deliverable 1 sigue siendo la cifra histórica** de otra ejecución y evaluación. El 2% de esta tabla es el baseline **nuevo y emparejado**, producido con los parámetros de inferencia de la condición RAG. Ambos resultados deben nombrarse con su protocolo; no se sustituyen entre sí.

La comparación enfrenta la **intervención completa**: evidencia recuperada y prompt estructurado frente a prompt directo sin documentos. No aísla estadísticamente el efecto del recuperador ni prueba superioridad en preguntas no vistas. Las 50 preguntas guiaron el desarrollo del corpus y la recuperación, hay una sola semilla por pregunta y los veredictos son una revisión asistida que el equipo puede auditar. No se modificaron prompts ni respuestas tras observar esta corrida.

## Archivos de auditoría

- [ZIP original](comparacion_f0bff499766960f7.zip), [huella de importación](importacion.json) y [configuración exacta](original/configuracion.json).
- [Baseline: pregunta, referencia, respuesta, veredicto y motivo](evaluacion/baseline_directo/reporte/evaluacion.csv).
- [RAG: pregunta, referencia, respuesta, veredicto y motivo](evaluacion/rag_estructurado/reporte/evaluacion.csv).
- [Métricas y cruce de decisiones](comparacion.json); ambos directorios de evaluación incluyen paquetes, veredictos y resúmenes verificables con `evaluar.py resumir`.
- [Prompts](original/prompts.json), [evidencia](original/evidencia.json) y los 100 JSON de respuesta se preservan tal como salieron de Colab.
