# Arquitectura RAG - Proyecto GenIA (Deliverable 2)

Este documento sirve como bitácora y manual técnico de la arquitectura RAG construida localmente, resolviendo los errores de "Ausencia Paramétrica" del Deliverable 1.

## 📁 Archivos del Motor RAG

El sistema se dividió en 3 scripts modulares que forman una tubería de datos (Pipeline ETL) completa:

### 1. `paso1_extractor_final.py` (Data Engineering & Chunking)
El paso más crítico del proyecto. Resuelve el problema de que los PDFs rompen oraciones por la mitad.
* **Técnica:** Chunking Semántico + Recursive Text Splitter.
* **Cómo funciona:** Usa expresiones regulares (`Regex`) para unir oraciones cortadas por márgenes físicos. Separa el procesamiento del Calendario (que es tabla) y los Reglamentos (que son prosa). 
* **Seguridad:** Agrupa las oraciones, pero incluye una guillotina semántica que asegura que ningún bloque supere los 800 caracteres para evitar desbordar la memoria del modelo (límite de 512 tokens).
* **Output:** `base_conocimiento_udec.json`

### 2. `paso2_vectorizador.py` (Embedding & Vector Database)
Convierte el texto humano limpio a coordenadas espaciales.
* **Modelo Matemático:** `intfloat/multilingual-e5-small` (Especializado en español).
* **Parche de Hardware:** Fuerzo el uso de `device="cpu"` para evitar un bug nativo de Apple Silicon (MPS) que generaba tensores corruptos (`NaN`) y errores de división por cero.
* **Técnica E5:** Se añade obligatoriamente el prefijo `passage: ` a los documentos para calibrar el modelo.
* **Output:** `vectores_udec.npy` (Formato nativo de NumPy, hiperestable).

### 3. `paso3_asistente_rag.py` (Retriever & Generator)
El pegamento final que une la base de datos con el Cerebro (LLM).
* **Búsqueda (Retriever):** Convierte la pregunta del usuario a vector (con prefijo `query: `) y usa Similitud Coseno (`scikit-learn`) para extraer el **Top 5** de fragmentos (`top_k=5`) de la base de datos de NumPy.
* **Generación (LLM):** En lugar de sobrecargar la memoria de 8GB del Mac, se conecta mediante API local (`requests`) al servidor oculto de **Ollama** que corre `qwen2.5:3b`.
* **Prompt Engineering:** Se le da la instrucción estricta de abstenerse de responder si la respuesta no está en el contexto entregado (Cero Alucinaciones).

## 🚀 Cómo Ejecutar el Sistema (Desde Cero)

En la terminal, dentro de la carpeta `Workshops`:
1. `python3 paso1_extractor_final.py`
2. `python3 paso2_vectorizador.py`
3. `python3 paso3_asistente_rag.py`

## 🧠 Lecciones Aprendidas (El "Por Qué")
* **El costo del Bono:** Se usó un modelo pequeño (3B) para ganar el bono del curso, lo que implica que el modelo pierde capacidad de razonamiento lógico duro (ej. fechas cruzadas).
* **Solución Estructural vs Parches:** Para corregir los errores lógicos, en lugar de usar "Prompt Engineering" (un parche), la industria avanza hacia "Agentic AI y Tool Calling" (Semana 7 y 8).
* **Garbage In, Garbage Out:** Si cortas mal un PDF, la IA jamás encontrará la respuesta. El Chunking es el 90% del éxito.
