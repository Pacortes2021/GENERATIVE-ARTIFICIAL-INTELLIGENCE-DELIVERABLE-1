# Video de Deliverable 2: grabación de pantalla sin cortes (máximo 3:00)

El enunciado pide **una grabación de pantalla del sistema ejecutándose**, con baseline visible sobre la misma entrada. Los resultados conservados y las capturas estáticas no sustituyen esa ejecución. Este guion usa el [cuaderno principal](../notebooks/Deliverable2_Sistema_RAG_Colab.ipynb) y el [fallo P25 ya auditado](../resultados/qwen3_4b_4adccec813c53d7f/DIAGNOSTICO_P25.md). Graba una sola toma; si debes hacer otra por un problema técnico, no ocultes en la edición partes de la ejecución.

## Antes de iniciar la grabación

1. Abre tu copia ejecutable del cuaderno en Colab con **GPU**. Ejecuta las secciones 1–4 y espera el mensaje `Qwen listo. Configuración fijada; modo sin thinking.` La carga de modelos puede tardar varios minutos y ocurre antes de la grabación. Deja Colab conectado.
2. Comprueba que en la sección 5 aparezca la celda `PREGUNTA = ""` y que la tabla resultante se verá completa con el zoom del navegador que elijas. Cierra ventanas con información privada.
3. Prepara en otra pestaña el [diagnóstico P25](../resultados/qwen3_4b_4adccec813c53d7f/DIAGNOSTICO_P25.md) o su página correspondiente en GitHub. Ahí están la pregunta, respuesta incorrecta, respuesta suficiente y artículos que recibió el modelo.
4. Usa una pregunta **nueva, no ejecutada literalmente antes** para que el cuaderno indique `generada ahora`, no `checkpoint conservado`. Propuesta concreta: `Terminé mi segundo semestre en Ingeniería con 14 créditos aprobados. ¿Quedo en baja académica? Indica la norma que lo establece.` No la pruebes para elegir una salida favorable: la primera ejecución se graba tal como resulte. Esta consulta ilustra el sistema; **no se suma al 80%**.
5. Graba la pantalla con la herramienta habitual de macOS o de tu equipo, con resolución legible y sin incluir micrófono si prefieres poner subtítulos. El archivo final debe durar **menos de 3:00**, porque solo se verán los primeros tres minutos.

## Secuencia sugerida (2:30–2:50)

| Tiempo | Mostrar en pantalla | Narración sugerida |
|---|---|---|
| 0:00–0:20 | URL del repositorio y título del cuaderno en Colab; GPU conectada y salida `Qwen listo`. | «Este es el cuaderno ejecutable desde nuestro repositorio. Usa Qwen3-4B en GPU y recupera artículos con E5.» |
| 0:20–1:15 | En sección 5, escribir la pregunta nueva y **ejecutar la celda ante la cámara**. Mantener visible el progreso `baseline_directo` / `rag_estructurado` y `generada ahora`. | «La misma pregunta entra a dos condiciones: prompt directo sin documentos y recuperación más prompt estructurado. Ambas generan ahora, con el mismo modelo.» |
| 1:15–1:55 | Mostrar la tabla de respuestas lado a lado. Abrir «Fragmentos exactos enviados únicamente a RAG» y señalar el artículo pertinente. | «La tabla deja comparar dato y cita. El panel inferior muestra la evidencia entregada solo a RAG; el baseline no recibe esos artículos.» Describe lo que realmente respondió el modelo, incluso si se equivoca. |
| 1:55–2:35 | Mostrar el diagnóstico P25 en el repositorio: pregunta, respuesta RAG «prioridades a) y b)» y explicación. | «La solución aún falla en P25. Recibió completos los artículos 7 y 9, pero no explicó qué asignaturas representan esas prioridades. Es un fallo de síntesis, no un fragmento cortado.» |
| 2:35–2:50 | Volver al cuaderno o abrir el reporte emparejado con 1/50 y 40/50. | «En 50 preguntas conocidas, la pauta común dio 1/50 al baseline nuevo y 40/50 a RAG. Las preguntas se usaron durante el desarrollo; no afirmamos generalización.» |

Si la consulta nueva sale mal, **muéstrala y explícalo**. No cambies la pregunta para seleccionar un éxito. El resultado agregado está respaldado por los [100 veredictos](../resultados/qwen3_4b_f0bff499766960f7/REPORTE.md), no por esta demostración individual.

## Comprobación antes de entregar

- Duración inferior a 3:00 y texto legible al reproducirlo.
- Se ve la celda ejecutándose y `generada ahora` en las dos condiciones; no solo salidas previamente guardadas.
- Pregunta idéntica y respuestas baseline/RAG visibles en una tabla.
- Se abre la evidencia recuperada y se muestra el fallo real P25 con su causa.
- Sube el archivo final a un servicio que genere un **enlace de acceso abierto** y pruébalo en una ventana privada. Incluye ese enlace en la entrega del curso; un archivo local o enlace que pida autorización no cumple el requisito.
