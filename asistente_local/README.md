# Asistente Local de Normativa UdeC (`exp/dpo-agente`)

Evolución experimental del asistente normativo ejecutándose **100 % local en Mac de 8 GB de RAM** sobre **Ollama** (`qwen3:4b-instruct` o `udec-agente:4b-dpo` entrenado con DPO), conectado a búsqueda híbrida `BM25 + E5` con `RRF`, descomposición de subconsultas, verificación determinista de artículos y herramientas reales en Python sobre el corpus de [Deliverable 3](../Deliverable%203/Deliverable3/agentes/corpus.json).

> Ver informe completo de iteraciones, ablaciones, experimentos descartados y tabla comparativa sobre las 95 preguntas (incluyendo comparación directa contra Deliverables 1–4) en [`REPORTE_EXPERIMENTOS.md`](./REPORTE_EXPERIMENTOS.md).

## Estructura
- `config.py`: rutas al corpus, hiperparámetros (`num_ctx=4096`, `num_predict=1024`, `repeat_penalty=1.05`), fusión `rrf` + `top_p_inicial=0.85` y modelo activo (`qwen3:4b-instruct` por defecto hasta promover `udec-agente:4b-dpo`).
- `buscador.py`: índice híbrido `BM25 + intfloat/multilingual-e5-small` fusionado con `RRF`, descomposición determinista de preguntas compuestas y verificación previa de existencia de artículos por documento.
- `herramientas.py`: calculadora segura (`ast`), calendario real (`dias_entre`, `ver_calendario`), `leer_articulo`, `existe_articulo` y `buscar_reglamento`.
- `asistente.py`: orquestador multi-turno sobre Ollama `/api/chat` con reescritura conversacional, reparación de salidas `solo_citas` y soporte para PDFs dinámicos.
- `pdfs.py` y `historial.py`: extracción/vectorización en caché SHA-256 de PDFs propios en caliente y persistencia/exportación `.md` de chats.
- `verificador.py` y `evaluador.py`: compuerta opcional estilo Self-RAG bajo demanda en UI y evaluador determinista + juez `RAGAS-Faithfulness` local.
- `finetune/`: pipeline SFT y DPO Split-Backward antifuga (`construir_dataset.py`, `construir_dataset_dpo.py`, `entrenar_agente_sft.py`, `entrenar_agente_dpo.py`, `exportar_ollama.py`, notebooks Colab y resultados).
- `resultados/`: archivos JSON reproducibles de todas las corridas locales sobre `congelado_50`, `dificil_25` y `nuevas_20`.
- `app.py` / `cli.py`: interfaz web en Streamlit (con streaming) y CLI de terminal.

## Cómo ejecutarlo

```bash
# 1. Suite completa de pruebas unitarias offline (33 tests)
python3 -m unittest discover -s "asistente_local/tests" -v

# 2. Consulta puntual desde terminal (con modelo base o DPO)
python3 -m asistente_local.cli --modelo udec-agente:4b-dpo --pregunta "Un estudiante aprobó 42 créditos al término de su cuarto semestre. ¿Está en baja académica según el Art. 14?"

# 3. Benchmark reproducible + evaluador local
python3 -m asistente_local.benchmark --dataset nuevas_20 --modelo udec-agente:4b-dpo
python3 -m asistente_local.evaluador --archivo asistente_local/resultados/benchmark_nuevas_20_udec-agente_4b-dpo.json --juez-llm --max-juez 10

# 4. Chat web local en Streamlit
streamlit run asistente_local/app.py
```
