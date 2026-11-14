# Experimento Multi-LoRA (`exp/multi-lora-todos` y `exp/multi-lora-sin-verificador`)

Esta carpeta (`exp_multi_lora/`) aísla los experimentos de **fine-tuning QLoRA multi-agente sobre `Qwen/Qwen3-4B`**, manteniendo intactos `Deliverable 4/`, `main` y `deliverable-4`:
- **`exp/multi-lora-todos`:** los cuatro roles (`enrutador`, `recuperador`, `redactor` y `verificador`) usan adaptadores QLoRA independientes.
- **`exp/multi-lora-sin-verificador` (rama actual):** `enrutador`, `recuperador` y `redactor` usan QLoRA, mientras **`verificador` corre en el modelo base** (`model.disable_adapter()`).

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
| `scripts/generar_auditoria_multi.py` | Auditoría estricta bajo `LEEME_PAUTA.md` (`*_auditados.csv`, `auditoria_*.json`, `resumen_comparativo_global.json`). |
| `datos/` | Datasets deterministas (`*_train.jsonl`, `*_val.jsonl`) y resumen (`resumen_datasets_multi_lora.json`). |
| `entrenamiento/` | Métricas (`training_metrics.json`), curvas (`loss_curve.png/pdf`), smoke tests (`smoke_test_val.json`) y tarjetas de adaptador de `enrutador`, `recuperador` y `verificador`. |
| `evaluacion/` | Resultados crudos/auditados de `4-LoRA`, ablación `Red+Ver` y `3-LoRA sin Verificador` (`nuevas_20` y `75` D3), telemetrías, trazas y `resumen_comparativo_global.json`. |
| `REPORTE_RESULTADOS.md` | Análisis completo de entrenamiento, aislamiento, matriz del Verificador (LoRA vs Base), causas raíz y latencia. |
| `Exp_MultiLoRA_Colab.ipynb` | Notebook Colab (T4 / L4 / A100) que entrena los 3 adaptadores nuevos, valida aislamiento cruzado y evalúa `4-LoRA`. |
| `Exp_SinVerificador_Colab.ipynb` | Notebook Colab que carga únicamente `enrutador + recuperador + redactor` y evalúa `verificador` en base (`--agentes enrutador,recuperador,redactor`) sobre `nuevas_20` y `75` D3. |
| `tests/test_multi_lora.py` | Suite de pruebas unitarias offline (determinismo byte a byte, LF, antifuga, tokenización Qwen3 con 0 truncados, `MultiLoraGenerator` + `Orquestador`, auditoría estricta y validación del notebook). |

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
  --preguntas-csv "Deliverable 4/datos/preguntas_nuevas_20.csv" \
  --nombre-set nuevas_20 \
  --output-prefix multi_lora_nuevas20

python3 exp_multi_lora/scripts/evaluar_multi_lora.py \
  --agentes todos \
  --output-prefix multi_lora_75

# Evaluación 3-LoRA sin Verificador (verificador en modo base)
python3 exp_multi_lora/scripts/evaluar_multi_lora.py \
  --agentes enrutador,recuperador,redactor \
  --preguntas-csv "Deliverable 4/datos/preguntas_nuevas_20.csv" \
  --nombre-set nuevas_20 \
  --output-prefix sin_verificador_nuevas20

python3 exp_multi_lora/scripts/evaluar_multi_lora.py \
  --agentes enrutador,recuperador,redactor \
  --output-prefix sin_verificador_75

# Tabla comparativa contra Control Base D4 y Solo Redactor D4
python3 exp_multi_lora/scripts/resumir_comparativa.py \
  --benchmark 75 \
  --multi-csv exp_multi_lora/evaluacion/resultados_sin_verificador_75_auditados.csv \
  --multi-telemetria exp_multi_lora/evaluacion/telemetria_sin_verificador_75.json \
  --etiqueta-multi "3-LoRA Sin Verificador"

# Auditoría estricta completa (genera *_auditados.csv, auditoria_*.json y resumen_comparativo_global.json)
python3 exp_multi_lora/scripts/generar_auditoria_multi.py
```

---

## Resultados obtenidos (resumen)

Los detalles completos de entrenamiento, aislamiento, matriz de confusión del Verificador (LoRA vs Base) y análisis causal por pregunta se encuentran en [`REPORTE_RESULTADOS.md`](REPORTE_RESULTADOS.md).

| Condición | `congelado_50` | `dificil_25` | `75` D3 | `nuevas_20` | Consolidado `95` | Llamadas (`75` / `N20`) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control Base D4** | **46/50 (92.0%)** | 16/25 (64.0%) | 62/75 (82.7%) | 11/20 (55.0%) | 73/95 (76.8%) | 658 / 254 |
| **Solo Redactor D4** | 43/50 (86.0%) | 17/25 (68.0%) | 60/75 (80.0%) | 10/20 (50.0%) | 70/95 (73.7%) | 648 / 212 |
| **Ablación Red+Ver** | — | — | — | 9/20 (45.0%) | — | — / 190 |
| **Multi-LoRA (4 agentes)** | 40/50 (80.0%)\* | **18/25 (72.0%)** | 58/75 (77.3%)\* | **14/20 (70.0%)** | 72/95 (75.8%) | 493 / 138 |
| **3-LoRA sin Verificador** | **46/50 (92.0%)**\*\* | **18/25 (72.0%)** | **64/75 (85.3%)**\*\* | 10/20 (50.0%) | **74/95 (77.9%)** | **388 / 118** |

> \* En `4-LoRA`, `congelado_50:8` acierta contenido y citas inline (`[RG-ART-034] [RI-FI-ART-026]`) pero omite la tercera línea literal `Fuente:` (`39/50` / `57/75` estricto en 3 líneas).  
> \*\* En `3-LoRA sin Verificador`, `congelado_50:7` (`[RI-FI-ART-016]`) y `congelado_50:8` (`[RG-ART-034] [RI-FI-ART-026]`) aciertan contenido y citas inline pero omiten la tercera línea literal `Fuente:` (`44/50` / `62/75` estricto en 3 líneas).

### Hallazgos clave

1. **Salto de generalización por `Enrutador` + `Recuperador` LoRA:** `Multi-LoRA (4)` sube **`+20 pp`** frente a `Solo Redactor D4` en `nuevas_20` (`70.0%` vs `50.0%`), ambas variantes (`4` y `3` LoRAs) marcan **`18/25` (`72.0%`)** en `dificil_25` (máximo histórico), y en `3-LoRA sin Verificador` las llamadas del `Recuperador` bajan **`-68.6%`** (`75` D3) y **`-74.2%`** (`nuevas_20`) con `0` fallbacks y `0` citas fuera de evidencia.
2. **Doble disociación al dejar el `Verificador` en base (`3-LoRA` vs `4-LoRA`):** en `75 D3`, quitar el `Verificador` LoRA alcanza **`64/75` (`85.3%`, máximo histórico)** y lidera el consolidado de `95` preguntas (`74/95 = 77.9%`), eliminando falsos rechazos por `No aplica` (`congelado_50:28`) y logrando rescates en ciclo 2 (`congelado_50:6, 47`, `H04`); sin embargo, en `nuevas_20` vuelve a **`10/20` (`50.0%`)** porque el `Verificador` base rechaza con objeciones alucinadas borradores ya correctos (`N05`, `N11`, `N20` y en `75 D3` `H17`, `H19`).
3. **Eficiencia de latencia sin `Verificador` LoRA:** bajar de `4` a `3` adaptadores recorta el tiempo total en `75 D3` **`-31.4%`** (`4354.4 s` vs `6346.3 s`), sube el throughput de `6.79` a `7.32–7.39 tok/s` y reduce llamadas totales a `388` (`-40.1%` vs `Solo Redactor`), con conclusión clara para v2: conservar `enrutador + recuperador + redactor` y recalibrar un `Verificador` LoRA v2.
