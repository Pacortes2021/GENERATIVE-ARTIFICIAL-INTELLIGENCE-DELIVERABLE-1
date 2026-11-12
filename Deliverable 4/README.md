# Deliverable 4 — Fine-tuning del Agente Redactor (`Qwen/Qwen3-4B`)

Continuación directa de Deliverables 1–3 sobre consultas normativas de pregrado UdeC / Facultad de Ingeniería (`corpus.json`: 173 unidades padre, 197 unidades y 201 fragmentos de búsqueda; evaluación oficial sobre 75 preguntas: `congelado_50` + `dificil_25`), manteniendo el modelo base `Qwen/Qwen3-4B` (NF4, T4) y la arquitectura de 4 agentes de Deliverable 3.

## Estructura actual (`Paso 1`, `Paso 2` y preparación de `Paso 3`)

- `prompts/`: prompts versionados por agente heredados bit a bit desde Deliverable 3 v6 (`01_enrutador.txt`, `02_recuperador.txt`, `03_redactor.txt`, `04_verificador.txt`).
- `scripts/diagnostico_d3.py`: reconstruye desde `Deliverable 3/Deliverable3/resultados_v6/trazas_D3.json` y `Deliverable 3/auditoria/veredictos_exportados.json` qué evidencia (`top-6`) vio el Redactor y dónde se originaron los fallos.
- `diagnostico/diagnostico_d3.json` y `diagnostico/DIAGNOSTICO_D3.md`: evidencia empírica que justifica fine-tunear al **Redactor** (`8/9` errores finales ya tenían toda la evidencia en su `top-6`, y el prompting del Redactor alcanzó techo/regresión en v5).
- `scripts/dataset_blocks/` y `scripts/construir_dataset.py`: especificaciones híbridas curadas en 6 bloques (`210` pares: `180` entrenamiento / `30` validación) ensambladas determinísticamente con textos literales de `corpus.json` y la plantilla exacta `prompts/03_redactor.txt`, con auditoría automática antifuga frente a las 75 preguntas de evaluación D3.
- `datos/`: `redactor_train.jsonl` (`180`), `redactor_val.jsonl` (`30`), `dataset_resumen.json` y `MUESTRA_REVISION_MANUAL.md` (muestra estratificada de `30` casos para inspección humana).
- `scripts/entrenar_redactor.py` y `D4_colab_entrenamiento.ipynb`: entrenamiento reproducible QLoRA (NF4, `r=16`, `alpha=32`, pérdida enmascarada solo sobre el asistente con `enable_thinking=False`, `max_seq_length=4096`), registro de métricas/curvas (`PNG`/`PDF`), smoke test sobre validación y subida pública a Hugging Face.
- `tests/`: pruebas automáticas de integridad, antifuga y tokenización/curvas (`test_diagnostico_d3.py`, `test_dataset.py`, `test_entrenamiento.py`).

## Cómo reproducir (`Paso 1`–`Paso 3`)

Desde la raíz de `Proyecto_Git` (validación local de diagnóstico, dataset y pipeline de tokenización):

```bash
python3 "Deliverable 4/scripts/diagnostico_d3.py"
python3 "Deliverable 4/scripts/construir_dataset.py"
python3 -m unittest discover -s "Deliverable 4/tests" -v
```

*(Si tienes `pytest` instalado en tu entorno virtual, también es compatible: `pytest -v "Deliverable 4/tests"`.)*

Para ejecutar el entrenamiento QLoRA en GPU (T4 16 GB o superior), abre `Deliverable 4/D4_colab_entrenamiento.ipynb` en Google Colab y descarga `D4_resultados_paso3.zip` hacia `Deliverable 4/entrenamiento/`.

## Hoja de ruta

1. **Paso 1 (completado):** Diagnóstico empírico de D3 v6, justificación del agente `Redactor` y prompts versionados base.
2. **Paso 2 (aprobado):** Dataset híbrido del `Redactor` (`180 train / 30 val`) en formato chat exacto de `03_redactor.txt`, validado contra `corpus.json` y completamente separado de las 75 preguntas de evaluación.
3. **Paso 3 (código listo y verificado en local; pendiente de corrida en GPU Colab):** Entrenamiento QLoRA de `Qwen/Qwen3-4B` para el `Redactor`, registro de curvas de pérdida, tiempo, hardware y publicación del adaptador en Hugging Face.
4. **Paso 4:** Integración del adaptador solo en el agente `Redactor` dentro del sistema multi-agente y evaluación completa sobre las 75 preguntas (D1, D2, D3, D4 + control directo), más análisis de caso de falla persistente.
5. **Paso 5–6:** Reporte LaTeX vertical de 1 página y video demostrativo (≤ 3 min) comparando modelo base vs fine-tuned con mensajes intermedios visibles.
