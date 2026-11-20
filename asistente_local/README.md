# Asistente Local de Normativa UdeC (`feat/asistente-local`)

Prototipo funcional en entorno local sobre **Ollama** (`qwen3:4b-instruct` o `qwen2.5:3b`) conectado a herramientas deterministas en Python y RAG híbrido (`intfloat/multilingual-e5-small` + búsqueda léxica + expansión automática de referencias) sobre el corpus limpio de [Deliverable 3](../Deliverable%203/Deliverable3/agentes/corpus.json).

## Estructura
- `config.py`: rutas al corpus, URL de Ollama y modelo activo (`qwen3:4b-instruct` por defecto).
- `buscador.py`: índice híbrido en memoria con caché de vectores `E5` en `~/.cache/udec_asistente_local`.
- `herramientas.py`: calculadora segura basada en `ast`, calendario real con `datetime.date` (`dias_entre`), `ver_calendario`, `leer_articulo`, `existe_articulo` y `buscar_reglamento`.
- `asistente.py`: orquestador sobre Ollama `/api/chat` con tool-calling nativo.
- `cli.py`: chat interactivo o consulta puntual desde terminal.
- `app.py`: interfaz web en Streamlit con trazabilidad de herramientas y citas literales.

## Cómo ejecutarlo

```bash
# 1. Tests unitarios (offline)
python3 -m unittest discover -s "asistente_local/tests" -v

# 2. Consulta puntual desde terminal
python3 -m asistente_local.cli --pregunta "Un estudiante aprobó 42 créditos al término de su cuarto semestre. ¿Está en baja académica según el Art. 14?"

# 3. Chat web local en Streamlit
streamlit run asistente_local/app.py
```
