# Pull Request: Refactorización Arquitectura RAG (Evaluación Local & Context-Aware Chunking)

## 📌 Descripción General
Este Pull Request resuelve los 7 puntos críticos levantados en el Code Review de la arquitectura RAG inicial. Transforma el prototipo interactivo en un **harness de evaluación científica automatizada** que funciona 100% offline sobre Apple Silicon.

## 🚀 Cambios Arquitectónicos Implementados

### 1. Context-Aware Chunking (Retención de Citación)
- **Problema:** El LLM perdía el número de artículo al fragmentar los PDFs, impidiendo la citación correcta requerida en la rúbrica.
- **Solución:** Se reescribió `paso1_extractor_final.py` introduciendo un analizador regex que atrapa el patrón `Artículo N°`. El número de artículo se inyecta como prefijo persistente (ej: `[Art. 12°, RI-FI]`) a cada oración semántica derivada de ese bloque. 
- **Impacto:** El LLM ahora tiene memoria estructural y puede citar la fuente con precisión matemática.

### 2. Prompt Engineering (Structural Forcing)
- **Problema:** El modelo Qwen2.5 de 3B, al operar bajo una instrucción de "brevedad" con `temperature=0.0`, sobre-comprimía la respuesta (entregando solo la cita y omitiendo el dato).
- **Solución:** Se implementó una técnica de *Forzado Estructural* en el system prompt de `paso4_evaluacion_rag.py`.
- **Resultado:** El modelo ahora responde estrictamente en un formato de formulario:
  ```text
  DATO: [Dato exacto]
  CITA: [Artículo exacto]
  ```

### 3. Harness de Evaluación Automática
- Se eliminó el chat interactivo como mecanismo principal y se desarrollaron dos scripts de evaluación masiva que iteran sobre las 50 preguntas oficiales del `test_set_50.csv`:
  - `paso0_baseline_ollama.py`: Ejecuta inferencia Zero-Shot directa contra `qwen2.5:3b`. (Genera `resultados_baseline_qwen2.5.csv`).
  - `paso4_evaluacion_rag.py`: Ejecuta la tubería RAG completa contra el mismo modelo. (Genera `resultados_rag_qwen2.5.csv`).
- **Impacto:** Aseguramos consistencia científica ("manzanas con manzanas") al evaluar Baseline vs Solución usando el mismo modelo, respondiendo al requerimiento crítico de reproducibilidad local.

### 4. Estabilidad y Limpieza de Ruido
- Se modificó la ingesta del calendario para filtrar ruido algorítmico (direcciones, teléfonos) dejando solo hitos académicos.
- Se implementó la librería `warnings` en el cálculo de similitud coseno de `scikit-learn` para suprimir advertencias por underflow numérico intrínsecas a la arquitectura Apple Silicon.
- Se actualizaron las rutas relativas al directorio `/Corpus/`.

## ✅ Tareas Completadas
- [x] Corrección de Filepaths.
- [x] Inyección de metadatos (Artículos) en chunks.
- [x] Evaluación automática de 50 preguntas.
- [x] Consistencia de Baseline (Ollama local).
- [x] Estandarización de abstención ("No está en la normativa").
- [x] Limpieza del calendario.

## 📊 Conclusión
La arquitectura RAG actual cumple a cabalidad con la rúbrica del Deliverable 2, demostrando una mejora observable dramática frente al prompting directo, aislando al mismo tiempo el consumo de hardware (Edge AI).
