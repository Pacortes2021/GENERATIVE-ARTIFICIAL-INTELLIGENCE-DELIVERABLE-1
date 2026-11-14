# Experimento Multi-LoRA (4 agentes especializados sobre `Qwen/Qwen3-4B`)

Esta rama (`exp/multi-lora-todos`) aísla en `exp_multi_lora/` el experimento de **fine-tuning QLoRA para los cuatro agentes** del sistema (`enrutador`, `recuperador`, `redactor` y `verificador`), manteniendo intactos `Deliverable 4/`, `main` y `deliverable-4`.

## Hipótesis del experimento

En Deliverable 4 se entrenó únicamente al **Redactor** (`60/75` en el benchmark de D3 y `10/20` en `nuevas_20`, frente a `62/75` y `11/20` del Control Base). Aunque el Redactor mejoró en cálculos y abstención, el análisis cualitativo mostró errores aguas arriba y aguas abajo:

1. **Enrutador base:** omite reglamentos necesarios o sub-consultas en preguntas de cruce multi-documento (`RI-FI` + `RG`, `CAL` + reglamentos) o falla en clasificar premisas falsas.
2. **Recuperador base:** no reformula con paso atrás (*step-back*) tras búsquedas pobres, repite acciones o deja incompleta la evidencia antes de cerrar el ciclo ReAct.
3. **Verificador base:** emite aprobaciones permisivas o rechaza borradores aritméticamente válidos (`H22`, `N05`) al revisar en modo base sin LoRA.

El objetivo de `exp_multi_lora/` es entrenar adaptadores QLoRA independientes para **`enrutador`**, **`recuperador`** y **`verificador`**, combinarlos en **una sola instancia NF4 4-bit de `Qwen/Qwen3-4B`** junto con el **Redactor D4 v2** (`Pablox0333/qwen3-4b-redactor-udec-d4`, revisión `739b031acbd5feef2c49f946b94722712209bce0`), y comparar **Solo Redactor D4** vs **Multi-LoRA completo** (y ablaciones parciales via `--agentes`) bajo las mismas semillas, prompts v6 y orquestador.

---

## Estructura de `exp_multi_lora/`

| Ruta | Propósito |
| --- | --- |
| `scripts/antifuga_multi.py` | Loader compartido de corpus limpio, bloqueo de `61` unidades (`40` D3 + `21` `nuevas_20`), auditoría antifuga y réplica exacta de `_numero_permitido` y `Orquestador.chequear_citas`. |
| `scripts/enrutador_bloques.py` | Generador de ejemplos SFT para el Agente 1 (`01_enrutador.txt` -> `{"tipo", "sub_consultas", "documentos"}`). |
| `scripts/recuperador_bloques.py` | Generador de trayectorias ReAct para el Agente 2 (`02_recuperador.txt` -> `buscar`, `traer`, `existe`, `suficiente`, más recuperación ante avisos y `feedback_verificador`). |
| `scripts/verificador_bloques.py` | Generador de críticas `<pensar>...</pensar>` + JSON `{aprobado, destino, motivo}` para el Agente 4 (`04_verificador.txt`), respetando el truncado `[:700]` y `chequear_citas` de `Orquestador.verificar()`. |
| `scripts/construir_datasets_agentes.py` | Construye los 6 JSONL (`train`/`val` por agente) y `datos/resumen_datasets_multi_lora.json` con auditoría antifuga integrada. |
| `scripts/entrenar_agente.py` | Script único de entrenamiento QLoRA (`r=16, alpha=32, completion_only_loss=True`) parametrizado con `--agente {enrutador,recuperador,verificador,redactor}`. |
| `scripts/evaluar_multi_lora.py` | Carga un único `Qwen/Qwen3-4B` NF4 y conmuta hasta 4 adaptadores por nombre mediante `model.set_adapter(rol)` / `model.disable_adapter()`, verifica aislamiento cruzado (`logits`) y permite comparativas pareadas (`--comparar-vs-solo-redactor`) o lotes completos (`ejecutar_evaluacion_lote`). |
| `scripts/resumir_comparativa.py` | Compara CSVs y telemetría (`Control Base D4`, `Solo Redactor D4`, `Multi-LoRA`). |
| `datos/` | Datasets deterministas (`*_train.jsonl`, `*_val.jsonl`) y resumen (`resumen_datasets_multi_lora.json`). |
| `Exp_MultiLoRA_Colab.ipynb` | Notebook listo para Google Colab (T4 / L4 / A100) que entrena los 3 adaptadores nuevos, valida aislamiento cruzado y evalúa `Solo Redactor` vs `Multi-LoRA`. |
| `tests/test_multi_lora.py` | Suite de pruebas unitarias offline (determinismo byte a byte, LF, antifuga, tokenización Qwen3 con 0 truncados, `MultiLoraGenerator` + `Orquestador` y validación del notebook). |

---

## Resumen de datasets (v1)

| Agente | Train | Val | Total | Unidades bloqueadas solapadas | Menciones QID eval | Solapamiento train/val | Distribución principal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `enrutador` | 210 | 36 | 246 | 0 | 0 | 0 | `condicional: 72`, `cruce: 58`, `numerica: 53`, `factual: 35`, `premisa_falsa: 28` |
| `recuperador` | 230 | 39 | 269 | 0 | 0 | 0 | `buscar: 111`, `suficiente: 88`, `traer: 61`, `existe: 9` |
| `verificador` | 305 | 68 | 373 | 0 | 0 | 0 | `fin: 155`, `redactor: 155`, `recuperador: 63` |

---

## Flujo de ejecución

### 1. Validación local (sin GPU)

```bash
python3 exp_multi_lora/scripts/construir_datasets_agentes.py
python3 -m unittest discover -s "exp_multi_lora/tests" -v
```

### 2. Entrenamiento en Colab (`Exp_MultiLoRA_Colab.ipynb`)

```bash
python3 exp_multi_lora/scripts/entrenar_agente.py --agente enrutador
python3 exp_multi_lora/scripts/entrenar_agente.py --agente recuperador
python3 exp_multi_lora/scripts/entrenar_agente.py --agente verificador
```

*(Opcional: añadir `--skip-smoke-test` para ahorrar tiempo de inferencia al final de cada entrenamiento y `--hf-repo <usuario>/<repo>` para subir automáticamente cada adaptador).*

### 3. Evaluación Multi-LoRA vs Solo Redactor D4

```bash
# Comparativa pareada en vivo sobre casos diagnósticos
python3 exp_multi_lora/scripts/evaluar_multi_lora.py \
  --agentes todos \
  --comparar-vs-solo-redactor H06,H07,H22 \
  --solo-comparativa \
  --verbose-pasos

# Evaluación completa en nuevas_20 y en las 75 de D3
python3 exp_multi_lora/scripts/evaluar_multi_lora.py \
  --agentes todos \
  --preguntas-csv "Deliverable 3/Deliverable3/agentes/nuevas_20.csv" \
  --nombre-set nuevas_20 \
  --output-prefix multi_lora_nuevas20

python3 exp_multi_lora/scripts/evaluar_multi_lora.py \
  --agentes todos \
  --output-prefix multi_lora_75

# Tabla comparativa contra Control Base D4 y Solo Redactor D4
python3 exp_multi_lora/scripts/resumir_comparativa.py \
  --benchmark 75 \
  --multi-csv exp_multi_lora/evaluacion/resultados_multi_lora_75.csv \
  --multi-telemetria exp_multi_lora/evaluacion/telemetria_multi_lora_75.json
```
