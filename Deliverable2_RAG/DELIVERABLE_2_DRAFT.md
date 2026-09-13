# Borrador Técnico - Deliverable 2
*(Usa este texto para rellenar tu plantilla de LaTeX)*

---

**Model Commitment**
El equipo seleccionó el modelo **Qwen2.5 de 3B parámetros** (corriendo localmente vía Ollama) por sobre las alternativas de mayor peso (e.g., Llama-3 8B). La justificación obedece al criterio de **economía de hardware** de la rúbrica. Buscamos maximizar el rendimiento en inferencia (velocidad y bajo consumo de RAM) sobre un procesador Apple Silicon (A18), demostrando que es posible construir una tubería de IA en el *Edge* sin dependencia de recursos en la nube (como Google Colab).

**First Solution**
La intervención diseñada para combatir la falla del modelo base (Ausencia Paramétrica de conocimiento institucional) fue una combinación de **Retrieval-Augmented Generation (RAG)** y **Constrained Decoding** mediante *Structural Forcing*. 
Se desarrolló un sistema RAG de 3 etapas. La innovación principal es el *Context-Aware Chunking*: durante la extracción del texto de los PDFs normativos, se implementó una expresión regular que atrapa y memoriza el número del artículo, inyectándolo como prefijo en cada bloque semántico derivado. Esto resolvió el problema crítico del LLM al no poder citar correctamente el origen de la información. Adicionalmente, se forzó al modelo mediante su *System Prompt* a responder en una estructura estática de formulario (`DATO:` y `CITA:`) para evitar la sobre-compresión de respuestas inherente a los modelos de 3B.

**Baseline Comparison**
Para asegurar consistencia científica ("apples to apples"), el experimento se midió aislando el modelo. Se desarrolló un *harness* de evaluación automático que sometió las 50 preguntas oficiales (`test_set_50.csv`) al modelo `qwen2.5:3b` mediante *prompting* directo (Baseline). Luego, se evaluaron las mismas 50 preguntas utilizando la tubería RAG. Los resultados de ambos *pipelines* se exportaron en planillas CSV. El incremento en precisión de extracción (Dato + Cita) es evidente y dramático al incorporar el contexto.

**Failure Case & Known Limits**
A pesar del éxito del sistema de recuperación, la arquitectura presenta un límite inherente a la cantidad de parámetros del modelo Generador (3B).
Un caso de fallo claro ocurre en preguntas que requieren desambiguación lógica de un mismo párrafo (Ejemplo: Pregunta sobre cuántas *evaluaciones de recuperación* existen). El Retriever logra extraer y proveer el **Artículo 11** perfecto (el cual menciona tanto evaluaciones sumativas como de recuperación). Sin embargo, el LLM sufre de "Alucinación por Proximidad Semántica", cruzando el número "tres" de las pruebas sumativas y respondiendo incorrectamente *"3 evaluaciones de recuperación"*. Esto demuestra que, aunque el RAG soluciona la ausencia de información (Recall), no puede subsanar la falta de razonamiento profundo (Reasoning) del modelo pequeño, el cual se confunde ante sintaxis densa.

---
*(Nota: Recuerda añadir el diagrama de la arquitectura dibujado por ti en la versión de LaTeX)*
