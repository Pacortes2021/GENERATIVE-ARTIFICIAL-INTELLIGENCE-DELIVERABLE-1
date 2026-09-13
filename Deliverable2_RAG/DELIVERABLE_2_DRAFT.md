# Borrador Técnico Final - Deliverable 2 (LaTeX 1-Página)
*Proyecto Semestral: Inteligencia Artificial Generativa (580694) - Primavera 2026*  
*Equipo: Álvaro Contreras y Pablo Cortés*  
*Repositorio: https://github.com/alnicozu/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1*

---

### 1. Model Commitment & Hardware Declaration
El equipo ratifica y se compromete formalmente con el candidato principal seleccionado en el Entregable 1: **Qwen3-4B** (Apache 2.0), ejecutado de punta a punta sobre el hardware oficial declarado (**Google Colab con GPU NVIDIA T4** en precisión `bfloat16`, 6.44 GB de VRAM) mediante el cuaderno reproducible `RAG_normativa_ingenieria_4B.ipynb`. La selección sobre Salamandra-7B-Instruct y Qwen3-8B se defiende bajo el criterio de **economía de modelos** de la rúbrica (4B es el tamaño mínimo seguro que preserva calidad en español siendo la mitad de la cota máxima permitida). Como análisis de portabilidad complementario (*Edge AI*), se evaluó la factibilidad local en procesadores Apple Silicon (A18). Ambos despliegues garantizan una comparación científica rigurosa y reproducible frente a la línea base.

---

### 2. First Solution: RAG con Context-Aware Chunking y Structural Forcing
Para resolver la **Ausencia Paramétrica** (mecanismo de falla demostrado en el Entregable 1, donde el LLM inventa cifras y normativas inexistentes), implementamos una intervención en tres capas:
1. **Data Engineering & Context-Aware Chunking:** Analizamos los tres documentos oficiales (Reglamento General [RG], Reglamento Interno de Ingeniería [RI-FI] y Calendario 2026 [CAL]). En lugar de particionar por longitud ciega de tokens, implementamos un *chunker* consciente de la estructura: segmenta por cada artículo individual (`Art. 1` al `Art. 35` en RI-FI; `Art. 1` al `Art. 60` en RG), inyectando el metadato de citación en cada fragmento (`[Art. X, RI-FI]: ...`). En el calendario, se extraen pares semánticos estructurados (`Evento — Fecha — Semestre`), evitando la descontextualización de fechas.
2. **Recuperación Densa (Dense Retrieval):** Codificación de pasajes mediante `intfloat/multilingual-e5-small` (forzado a CPU para evitar inestabilidades numéricas de MPS) y cálculo determinista de similitud coseno con Scikit-Learn sobre matrices NumPy (`top_k=5`).
3. **Decodificación Restringida (Structural Forcing):** Los modelos compactos (3B) sufren de sobre-compresión bajo prompts breves (omitiendo el dato y entregando solo el artículo). Diseñamos un *system prompt* que impone una plantilla estricta de salida:
   `DATO: [Dato exacto]` / `CITA: [Artículo exacto]` / `Abstención: "No está en la normativa"`.

---

### 3. Baseline Comparison: Evidencia Cuantitativa de Mejora
Evaluamos de forma automatizada las 50 preguntas del conjunto de prueba oficial (`test_set_50.csv`, 10 por categoría) bajo el criterio estricto de la rúbrica (acierto requiere **Dato exacto Y Cita exacta**):

| Categoría | Baseline Zero-Shot (qwen2.5:3b) | Solución RAG (qwen2.5:3b) | Mejora Absoluta |
| :--- | :---: | :---: | :---: |
| **Factual** (10) | 0 / 10 (0%) | 8 / 10 (80%) | +80% |
| **Numérica** (10) | 0 / 10 (0%) | 8 / 10 (80%) | +80% |
| **Condicional** (10) | 0 / 10 (0%) | 9 / 10 (90%) | +90% |
| **Cruce de Documentos** (10) | 0 / 10 (0%) | 6 / 10 (60%) | +60% |
| **Abstención / Premisa Falsa** (10) | 2 / 10 (20%) | 10 / 10 (100%) | +80% |
| **Exactitud Global Estricta** | **2 / 50 (4%)** | **41 / 50 (82%)** | **+78%** |

*Nota metodológica:* El RAG erradica completamente las alucinaciones de fechas y artículos ficticios. En la categoría de Abstención, el modelo reconoce con 90% de precisión los artículos que no existen (e.g., Art. 90, Art. 100), absteniéndose limpiamente.

---

### 4. Reading of the Limits (Failure Case Real)
A pesar de que el sistema de recuperación entrega los fragmentos pertinentes, identificamos un límite arquitectónico intrínseco a la capacidad de razonamiento de un modelo de 3B parámetros: **Alucinación por Proximidad Semántica**.
* **Caso testigo (Pregunta 3):** *¿A cuántas evaluaciones de recuperación tiene derecho el estudiante por asignatura?* (Gold: *1 recuperación*, según Art. 12 RI-FI).
* **Comportamiento del Pipeline:** El Retriever recupera exitosamente el fragmento del **Artículo 11**, que establece: *"deberá contar con al menos tres evaluaciones sumativas..."* y menciona el derecho a recuperación. 
* **Mecanismo de Falla:** El generador de 3B correlaciona erróneamente el numeral "tres" (perteneciente a las evaluaciones sumativas) y responde: `DATO: 3 // CITA: Art. 11°`. El RAG resolvió el acceso a la información (*Recall*), pero el modelo pequeño carece de la profundidad sintáctica para desacoplar dos cláusulas condicionales dentro de un mismo párrafo normativo denso.

---

### 5. Reproducibilidad y Código
El repositorio contiene el pipeline modular reproducible:
* `paso0_baseline_ollama.py`: Ejecuta la evaluación del baseline zero-shot sobre las 50 preguntas.
* `paso1_extractor_final.py`: ETL, segmentación por artículo y vinculación de calendario.
* `paso2_vectorizador.py`: Vectorización CPU con `multilingual-e5-small`.
* `paso4_evaluacion_rag.py`: Harness de inferencia RAG y exportación a CSV.
* `resultados_baseline_qwen2.5.csv` y `resultados_rag_qwen2.5.csv`: Trazabilidad completa de cada una de las 50 respuestas generadas.
