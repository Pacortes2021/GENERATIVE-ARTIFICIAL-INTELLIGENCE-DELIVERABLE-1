# Pull Request: Refactorización Integral Arquitectura RAG (Segmentación por Artículo y Calendario Estructurado)

## 📌 Resumen Ejecutivo
Este Pull Request implementa la solución completa para el **Entregable 2**, subsanando de raíz los defectos de chunking, extracción de artículos y consistencia experimental detectados en las revisiones previas. Transforma el sistema en un pipeline de evaluación cuantitativa formal que opera 100% offline sobre Apple Silicon.

---

## 🛠️ Modificaciones Técnicas Principales

### 1. Data Engineering: Segmentación Estricta por Artículo (`paso1_extractor_final.py`)
- **Problema Previo:** La limpieza de saltos de línea fusionaba los textos normativos de la Facultad de Ingeniería en un único bloque, causando que el 100% de los fragmentos quedaran erróneamente etiquetados como `[Art. 1°, RI-FI]`.
- **Solución Implementada:** Se refactorizó la extracción utilizando detección por expresión regular del inicio de cada artículo (`(?i)\n(?=art[íi]culo\s+\d+°?|art\.\s*\d+°?)`). 
- **Resultado:** Se indexaron de forma independiente los 35 artículos del Reglamento Interno de Ingeniería y los 60 artículos del Reglamento General. Cada chunk lleva como prefijo su artículo real (ej. `[Art. 8°, RI-FI]: ...`, `[Art. 14°, RI-FI]: ...`), habilitando al generador a citar la fuente con precisión matemática.

### 2. Estructuración Semántica del Calendario Académico
- **Problema Previo:** El parsing por líneas separaba el nombre de los hitos académicos de sus fechas correspondientes, dejando eventos como "Inicio de Clases" huérfanos de su fecha "10 de agosto".
- **Solución Implementada:** Se reconstruyó el parser para extraer pares semánticos consolidados (`Evento — Fecha — Semestre`) preservando el alineamiento espacial.
- **Resultado:** Preguntas de cruce y calendario (segundo semestre 2026) ahora recuperan el contexto temporal exacto.

### 3. Decodificación Restringida (Structural Forcing en `paso4_evaluacion_rag.py`)
- Se implementó un *system prompt* estructurado con forzado de plantilla:
  ```text
  DATO: [Dato exacto]
  CITA: [Artículo exacto]
  ```
- Erradicó la sobre-compresión en el modelo `qwen2.5:3b`, asegurando respuestas tabuladas y parseables.

### 4. Harness de Evaluación Automática (`paso0` y `paso4`)
- **Consistencia Experimental:** Se evaluó el conjunto completo de 50 preguntas oficiales (`test_set_50.csv`) en modo Zero-Shot (Baseline) y en modo RAG sobre el mismo modelo (`qwen2.5:3b`) a temperatura 0.0.
- Los resultados se encuentran exportados y versionados en `resultados_baseline_qwen2.5.csv` y `resultados_rag_qwen2.5.csv`.

---

## 📁 Archivos Incluidos en este PR
- `paso0_baseline_ollama.py`: Evaluador de la línea base directa (sin RAG).
- `paso1_extractor_final.py`: ETL, segmentación por artículo y estructuración del calendario.
- `paso2_vectorizador.py`: Generador de embeddings con `multilingual-e5-small` en CPU (estabilidad NumPy).
- `paso3_asistente_rag.py`: Interfaz de chat interactivo por consola.
- `paso4_evaluacion_rag.py`: Harness de evaluación masiva sobre las 50 preguntas.
- `base_conocimiento_udec.json`: Base de conocimiento con metadatos de citación por artículo.
- `DELIVERABLE_2_DRAFT.md`: Borrador técnico de 1 página en formato LaTeX alineado con la pauta oficial.
- `Arquitectura_RAG_Deliverable2.md`: Documentación de arquitectura y decisiones de hardware.

## ✅ Checklist de Validación
- [x] Los 35 artículos de Ingeniería y 60 de Reglamento General están etiquetados de forma individual.
- [x] Los eventos del calendario incluyen explícitamente su fecha y semestre en cada chunk.
- [x] El pipeline corre end-to-end de forma reproducible.
- [x] Resultados cuantitativos de 50 preguntas generados y respaldados en CSV.
