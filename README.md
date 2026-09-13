# Asistente de Normativa de Pregrado (Ingeniería UdeC)

Proyecto semestral de **Generative Artificial Intelligence (580694)**, segundo semestre 2026, Universidad de Concepción.  
**Equipo:** Álvaro Contreras y Pablo Cortés  
**Repositorio:** [https://github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1](https://github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1)

---

## 📌 1. Definición de la Tarea y Corpus

El objetivo del sistema es responder consultas en español sobre la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción (FI-UdeC), entregando **(i) el dato exacto** y **(ii) la cita estricta del artículo o fuente** que lo respalda. Ante preguntas con premisas falsas o información ausente en el corpus, la respuesta correcta es **abstenerse explícitamente**.

### Corpus Cerrado (Documentos Oficiales):
1. **Reglamento General de Docencia de Pregrado (RG):** 60 artículos.
2. **Reglamento Interno de Docencia de Pregrado, Facultad de Ingeniería (RI-FI):** 35 artículos.
3. **Calendario de Docencia de Pregrado 2026 (CAL):** Hitos académicos y feriados del 1er y 2º semestre 2026.

**Métrica de Evaluación:** Exactitud estricta (se cuenta como acierto solo si tanto el dato como el artículo/fuente son correctos), evaluada sobre un conjunto de prueba de **50 preguntas oficiales** (`test_set_50.csv`), distribuidas equitativamente en 5 categorías:
* Factual (10)
* Numérica (10)
* Condicional (10)
* Cruce de documentos (10)
* Abstención / Premisa falsa (10)

---

## 🔬 2. Entregable 1: Diagnóstico de la Falla y Línea Base

En el Entregable 1 se evaluó el modelo mediante *prompting* directo (Zero-Shot) sin acceso a los documentos, utilizando decodificación determinista (`temperature=0.0`).

### Hallazgo Central (Ausencia Paramétrica):
* **Exactitud Global:** **2 / 50 (4%)**.
* **Preguntas con respuesta en corpus:** **0 / 40 (0%)**.
* El modelo demostró *Ausencia Paramétrica*: inventó cifras inexistentes (e.g., 60 créditos en lugar de 8; escala de 0 a 100 en lugar de 1 a 7), citó artículos al azar y fabricó contenido para artículos ficticios en el 80% de los casos.
* La duplicación de tamaño a 8B arrojó el mismo 4%, demostrando que la solución requería ingeniería de contexto (RAG) y no un modelo mayor.

---

## 🚀 3. Entregable 2: Arquitectura RAG Local (Edge AI)

Para el Entregable 2, implementamos una solución integral que combate la falla diagnosticada mediante **Retrieval-Augmented Generation (RAG)** y **Decodificación Restringida (Structural Forcing)**, ejecutada de manera 100% offline sobre arquitectura Apple Silicon (MacBook Neo, A18) mediante la API local de Ollama.

### Componentes de la Arquitectura:

```
[PDFs Oficiales: RG, RI-FI, CAL]
              │
              ▼
    1. ETL & Context-Aware Chunking (paso1_extractor_final.py)
       - Segmentación estricta por artículo (Art. 1 al 35 en RI-FI, 1 al 60 en RG)
       - Parser tabular de calendario (Pares: Evento — Fecha — Semestre)
              │
              ▼
    2. Dense Retrieval Vectorization (paso2_vectorizador.py)
       - Modelo: intfloat/multilingual-e5-small (CPU, float32)
       - Almacenamiento: Matrices NumPy ultraestables (.npy)
              │
              ▼
    3. Similarity Search & Ranking
       - Scikit-Learn Cosine Similarity (top_k=5)
              │
              ▼
    4. Generación Restringida (paso4_evaluacion_rag.py)
       - Modelo: Qwen2.5-3B-Instruct (Ollama local, temp=0.0)
       - Structural Forcing: Formato rígido (DATO: [...] // CITA: [...])
              │
              ▼
[Respuestas Tabuladas: resultados_rag_qwen2.5.csv] (82% Exactitud)
```

### Innovaciones Técnicas Clave:
1. **Context-Aware Chunking (Segmentación por Artículo):** Se eliminó el empaquetamiento ciego de texto. Cada uno de los artículos fue segmentado con expresiones regulares (`(?i)\n(?=art[íi]culo\s+\d+°?)`), inyectando su número y origen (`[Art. X, RI-FI]: ...`) de forma persistente en cada bloque.
2. **Vinculación Semántica del Calendario:** Los eventos y sus fechas se agruparon en pares semánticos consolidados (`[Calendario 2026, Segundo Semestre 2026]: Inicio de Clases — 10 de agosto`), resolviendo las fallas en preguntas temporales.
3. **Structural Forcing:** Ante la tendencia de los modelos compactos (3B) a sobre-comprimir las salidas bajo prompts breves (omitiendo el dato y entregando solo la cita), se diseñó un *system prompt* estructurado que obliga al generador a completar los campos `DATO:` y `CITA:` de forma independiente.
4. **Economía de Hardware:** Se compite con un modelo de **3 Billones de parámetros**, demostrando viabilidad en dispositivos de borde con menos de 3.5 GB de RAM y cero costo de nube.

---

## 📊 4. Evidencia Experimental de Mejora (Resultados Cuantitativos)

Ambos sistemas (Baseline Zero-Shot y Solución RAG) fueron evaluados de forma automatizada sobre el conjunto idéntico de 50 preguntas bajo el mismo modelo (`qwen2.5:3b`) a temperatura 0.0:

| Categoría | Baseline Zero-Shot (`qwen2.5:3b`) | Solución RAG (`qwen2.5:3b`) | Mejora Absoluta |
| :--- | :---: | :---: | :---: |
| **Factual** (10) | 0 / 10 (0%) | **8 / 10 (80%)** | **+80%** |
| **Numérica** (10) | 0 / 10 (0%) | **8 / 10 (80%)** | **+80%** |
| **Condicional** (10) | 0 / 10 (0%) | **9 / 10 (90%)** | **+90%** |
| **Cruce de Documentos** (10) | 0 / 10 (0%) | **6 / 10 (60%)** | **+60%** |
| **Abstención / Premisa Falsa** (10) | 2 / 10 (20%) | **10 / 10 (100%)** | **+80%** |
| **Exactitud Global Estricta** | **2 / 50 (4%)** | **41 / 50 (82%)** | **+78%** |

* **Impacto en Abstención:** 100% de precisión ante preguntas trampa o artículos inexistentes (Art. 90, Art. 100, feriados inventados), absteniéndose de forma determinista con `"No está en la normativa"`.
* **Impacto en Citación:** Erradicación total de citas inventadas.

---

## 🔍 5. Lectura de Límites (Caso de Fallo Real)

A pesar del salto al 82%, la arquitectura evidencia una limitación intrínseca de razonamiento en modelos de 3B: **Alucinación por Proximidad Semántica**.

* **Caso testigo (Pregunta 3):** *¿A cuántas evaluaciones de recuperación tiene derecho el estudiante por asignatura?* (Gold: *1 recuperación*, Art. 12 RI-FI).
* **Comportamiento observado:** El Retriever recupera el fragmento del **Artículo 11**, el cual establece: *"deberá contar con al menos tres evaluaciones sumativas..."* y menciona el derecho a la evaluación de recuperación.
* **Mecanismo del fallo:** El modelo pequeño correlaciona erróneamente el numeral "tres" (propio de las pruebas sumativas) con el concepto de recuperación, respondiendo: `DATO: 3 // CITA: Art. 11°`.
* **Conclusión:** El RAG garantiza la recuperación del contexto (*Recall*), pero el modelo pequeño presenta dificultades para desacoplar sintácticamente cláusulas densas dentro de un mismo fragmento normativo.

---

## 📁 6. Estructura del Repositorio y Reproducibilidad

El repositorio está organizado en dos módulos de trabajo:

```text
├── Corpus/                                      # PDFs normativos oficiales
│   ├── Calendario-Academico-Pregrado-2026.pdf
│   ├── Reglamento_General_de_Docencia_de_Pregrado.pdf
│   └── Reglamento_de_Docencia_de_Pregrado-FI.pdf
├── Deliverable2_RAG/                            # Motor RAG y Harness de Evaluación
│   ├── paso0_baseline_ollama.py                 # Evaluador automatizado Baseline Zero-Shot
│   ├── paso1_extractor_final.py                 # ETL, Chunking por Artículo y Calendario
│   ├── paso2_vectorizador.py                    # Generador de embeddings (.npy) en CPU
│   ├── paso3_asistente_rag.py                   # Chat interactivo por terminal
│   ├── paso4_evaluacion_rag.py                  # Evaluador masivo RAG sobre test set
│   ├── base_conocimiento_udec.json              # Base estructurada (198 chunks indexados)
│   ├── vectores_udec.npy                        # Vectores precalculados en formato NumPy
│   ├── resultados_baseline_qwen2.5.csv          # Respuestas crudas del Baseline Zero-Shot
│   ├── resultados_rag_qwen2.5.csv               # Respuestas crudas de la Solución RAG
│   ├── DELIVERABLE_2_DRAFT.md                   # Borrador técnico de 1 página para LaTeX
│   ├── PR_DESCRIPTION.md                        # Memoria descriptiva técnica para Pull Request
│   └── Arquitectura_RAG_Deliverable2.md         # Bitácora de diseño y decisiones de hardware
├── baseline_normativa_ingenieria.ipynb           # Cuaderno original Deliverable 1 (Colab T4)
├── test_set_50.csv                              # Conjunto de 50 preguntas oficiales
└── README.md                                    # Documentación integral del proyecto
```

---

## ⚡ 7. Instrucciones de Reproducción Local

Para reproducir la evaluación completa de forma local en macOS / Linux:

### Requisitos:
1. Python 3.9+ con paquetes: `sentence-transformers`, `scikit-learn`, `requests`, `numpy`, `PyMuPDF` (o `pdftotext`).
2. Ollama instalado y corriendo con el modelo:
   ```bash
   ollama run qwen2.5:3b
   ```

### Ejecución del Pipeline:
```bash
cd Deliverable2_RAG

# 1. Extraer y estructurar el corpus por artículo
python3 paso1_extractor_final.py

# 2. Generar la base vectorial en CPU
python3 paso2_vectorizador.py

# 3. (Opcional) Evaluar el Baseline Zero-Shot
python3 paso0_baseline_ollama.py

# 4. Evaluar la Solución RAG completa sobre las 50 preguntas
python3 paso4_evaluacion_rag.py
```

Las respuestas generadas se exportarán a `resultados_rag_qwen2.5.csv` con el formato tabulado `DATO:` y `CITA:`, alcanzando el 82% de exactitud comprobable.
