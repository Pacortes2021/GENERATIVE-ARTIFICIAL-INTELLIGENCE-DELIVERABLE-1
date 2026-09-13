# Arquitectura RAG - Proyecto GenIA (Deliverable 2)

Este documento sirve como bitácora y manual técnico de la arquitectura RAG construida localmente, resolviendo los problemas del Deliverable 1.

## 📁 Archivos del Motor RAG

El sistema se dividió en scripts modulares que forman una tubería de datos completa y un *Harness* de evaluación.

### 0. `paso0_baseline_ollama.py` (Evaluación Desnuda)
Evalúa las 50 preguntas del test set contra el modelo `qwen2.5:3b` puro sin contexto adicional, generando el Baseline ("Antes") para comparar.
* **Output:** `resultados_baseline_qwen2.5.csv`

### 1. `paso1_extractor_final.py` (Data Engineering & Context-Aware Chunking)
Resuelve la pérdida de citas y el ruido. 
* **Retención de Contexto:** Usa expresiones regulares para capturar el "Artículo N°" de cada párrafo y lo inyecta como prefijo en todos los chunks derivados de él. Esto garantiza que el LLM siempre pueda citar correctamente.
* **Filtro de Calendario:** Limpia el ruido manteniendo solo filas útiles (meses y feriados).
* **Output:** `base_conocimiento_udec.json`

### 2. `paso2_vectorizador.py` (Embedding)
* Convierte texto a coordenadas espaciales con `intfloat/multilingual-e5-small`.
* Forzamos `device="cpu"` para evitar tensores corruptos (bug MPS en Mac).
* **Output:** `vectores_udec.npy`

### 3. `paso3_asistente_rag.py` (Modo Chat Interactivo)
Permite hacer preguntas interactivas por consola al sistema. El modelo está configurado para abstenerse estrictamente con la frase `"No está en la normativa"`.

### 4. `paso4_evaluacion_rag.py` (Harness Automático)
Script crucial que itera sobre las 50 preguntas oficiales, busca el contexto, llama al LLM, y consolida todo en una planilla, generando los números del "Después".
* **Output:** `resultados_rag_qwen2.5.csv`

## 🚀 Cómo Ejecutar el Sistema (Evaluación Científica 100% Offline)

A diferencia del Baseline original que requería Colab, toda nuestra arquitectura corre localmente sobre Apple Silicon usando la API de Ollama, demostrando factibilidad técnica en el borde (Edge AI).

En la terminal, corre la evaluación completa:
1. `python3 paso0_baseline_ollama.py`
2. `python3 paso1_extractor_final.py`
3. `python3 paso2_vectorizador.py`
4. `python3 paso4_evaluacion_rag.py`

Las tablas `.csv` resultantes pueden ser comparadas de inmediato en Excel/Pandas para medir el delta de exactitud que aportó el sistema RAG.
