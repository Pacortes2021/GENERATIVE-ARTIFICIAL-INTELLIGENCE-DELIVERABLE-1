# Reporte de Resultados — Experimento Multi-LoRA (`exp_multi_lora`)

**Ramas:** `exp/multi-lora-todos` (`4` LoRAs v1), `exp/multi-lora-sin-verificador` (**Opción A:** `3` LoRAs, `verificador` en base) y `exp/multi-lora-verificador-v2` (**Opción B:** `4` LoRAs con `verificador_v2` recalibrado) · **Modelo base:** `Qwen/Qwen3-4B` (QLoRA NF4 4-bit, `torch.bfloat16`) · **Hardware:** `NVIDIA A100-SXM4-40GB` (`42.41 GB` VRAM)  
**Criterio de auditoría:** estricta contra el corpus fuente y [`LEEME_PAUTA.md`](../Deliverable%203/paquete_25_dificiles/LEEME_PAUTA.md) (reglas 1–8, incluyendo excepciones Regla 2 y precedentes Regla 3 / `P01`).

---

## 1. Resumen Ejecutivo

El experimento evaluó en tres ramas complementarias cómo escala el sistema multi-agente sobre **una sola instancia NF4 de `Qwen/Qwen3-4B`** bajo idénticos prompts v6, parámetros de decodificación (`T=0.7`, `top_p=0.8`, `top_k=20`, `enable_thinking=False`) y semillas derivadas: (1) entrenando adaptadores QLoRA independientes para los cuatro roles (`enrutador`, `recuperador`, `redactor` D4 v2 y `verificador` v1), (2) evaluando la **Opción A (`3-LoRA sin Verificador`)** dejando `verificador` en modo base mediante `model.disable_adapter()`, y (3) evaluando la **Opción B (`4-LoRA Verificador v2`)** con un adaptador `verificador_v2` rebalanceado (`389` ejemplos train, `2.0` épocas, `lr=5e-5`, `eval_loss=0.264956`).

| Condición | `congelado_50` | `dificil_25` | **Benchmark `75` D3** | **`nuevas_20` (no vistas)** | **Consolidado `95`** | Llamadas totales (`75` / `N20`) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control Base D4** (0 LoRA) | **46/50 (92.0%)** | 16/25 (64.0%) | 62/75 (82.7%) | 11/20 (55.0%) | 73/95 (76.8%) | 658 / 254 |
| **Solo Redactor D4** (1 LoRA) | 43/50 (86.0%) | 17/25 (68.0%) | 60/75 (80.0%) | 10/20 (50.0%) | 70/95 (73.7%) | 648 / 212 |
| **Ablación Red+Ver** (2 LoRAs) | — | — | — | 9/20 (45.0%) | — | — / 190 |
| **Multi-LoRA (4 agentes v1)** | 40/50 (80.0%)\* | **18/25 (72.0%)** | 58/75 (77.3%)\* | **14/20 (70.0%)** | 72/95 (75.8%) | 493 / 138 |
| **Opción A — 3-LoRA sin Verificador** (`verificador` base) | **46/50 (92.0%)**\*\* | **18/25 (72.0%)** | **64/75 (85.3%)**\*\* | 10/20 (50.0%) | **74/95 (77.9%)** | **388 / 118** |
| **Opción B — 4-LoRA (`verificador_v2`)** | 40/50 (80.0%)\*\*\* | 16/25 (64.0%) | 56/75 (74.7%)\*\*\* | 12/20 (60.0%) | 68/95 (71.6%) | 486 / 147 |

> \* **Nota de transparencia (`Multi-LoRA 4 agentes`, `congelado_50:8`):** el contenido jurídico y ambas citas inline (`[RG-ART-034] [RI-FI-ART-026]`) son correctos y evitan el fallo P01 de `Solo Redactor D4`, pero omiten la tercera línea literal `Fuente:` (`formato_3_lineas_ok=False`). Bajo exigencia estricta de 3 líneas literales, la cifra pasaría a `39/50` (`78.0%`) y `57/75` (`76.0%`).  
> \*\* **Nota de transparencia (`3-LoRA sin Verificador`, `congelado_50:7` y `congelado_50:8`):** ambos aciertan el contenido jurídico y citan inline los artículos exactos (`[RI-FI-ART-016]` y `[RG-ART-034] [RI-FI-ART-026]`), pero omiten la línea final literal `Fuente:` (`formato_3_lineas_ok=73/75`). Bajo exigencia estricta de 3 líneas literales, sería `44/50` (`88.0%`) y `62/75` (`82.7%`).  
> \*\*\* **Nota de transparencia (`4-LoRA Verificador v2`, `congelado_50:8` y `dificil_25:H15`):** `congelado_50:8` acierta contenido y citas inline omitiendo `Fuente:` (bajo exigencia estricta de 3 líneas literales sería `39/50` y `55/75`), mientras `dificil_25:H15` falla con respuesta vacía tras un bucle degenerativo de `<pensar>` en ciclo 3 (`formato_3_lineas_ok=73/75`).

**Conclusiones principales:**

1. **Opción A (`3-LoRA sin Verificador`) es la ganadora empírica global (`74/95 = 77.9%`):** lidera el benchmark `75 D3` con **`64/75` (`85.3%`)** (`46/50` en `congelado_50` y `18/25` en `dificil_25`) con el menor consumo de llamadas (**`388`** en `75`, **`118`** en `N20`), menor promedio de ciclos (**`1.31`**) y menor latencia (`4354.4 s` en `75 D3`).
2. **Eficiencia récord de recuperación sin fallbacks (`Enrutador` + `Recuperador` LoRA):** frente a `Solo Redactor D4`, las llamadas del `Recuperador` caen **`-68.6%`** en `75 D3` (`373 -> 117` en Opción A) y **`-74.2%`** en `nuevas_20` (`132 -> 34` en Opción A), con `0/285` fallbacks de enrutamiento acumulados en las tres ramas.
3. **Resultado de la Opción B (`Verificador LoRA v2` -> `68/95 = 71.6%`):** aunque el reentrenamiento con `No aplica` balanceado mejoró `nuevas_20` frente a Opción A (`12/20 = 60.0%` vs `10/20`, logrando el primer acierto histórico en `H12` y rescatando `N01`, `C50:6, 12, 28`, `H05`), mantuvo dos fallas estructurales propias de SFT en `Qwen3-4B` para un rol crítico:
   - **Sobre-rechazo dañino (`7` fallos directos del `verificador` en `95` preguntas):** destruye borradores ya correctos del ciclo 1–2 (`N17`, `N20`, `C50:16`, `C50:49`, `H18`, `H21`) y provoca en `H15` un bucle infinito en `<pensar>` que trunca sin emitir respuesta.
   - **Falsa aprobación persistente (`23` falsas aprobaciones en `95` preguntas):** aprueba errores `P01`, aritméticos o de inversión lógica (`N07`, `C50:3, 5, 48`, `H03, H04, H06, H07, H09, H13`), por lo que la recalibración v2 no supera al `Verificador` base de Opción A ni al `Verificador` v1 en `95` preguntas.

---

## 2. Entrenamiento QLoRA y Paridad Experimental

### 2.1 Entorno y paridad con Deliverable 4

- **Software en Colab A100:** `torch 2.14.1+cu130`, `transformers 5.23.0`, `peft 0.21.3`, `bitsandbytes 0.50.2`, `accelerate 1.15.0`, `huggingface_hub 1.33.0`, `sentence-transformers 6.3.0`.
- **Prompts v6 idénticos (SHA-256 verificado):** `01_enrutador.txt` (`cc0d5e40...`), `02_recuperador.txt` (`2fe9b0af...`), `03_redactor.txt` (`6b3e4ac3...`), `04_verificador.txt` (`c141fe36...`).
- **Adaptadores cargados en un único `Qwen/Qwen3-4B` NF4:**
  - `enrutador`: adaptador entrenado localmente (`exp_multi_lora/entrenamiento/enrutador/adapter`).
  - `recuperador`: adaptador entrenado localmente (`exp_multi_lora/entrenamiento/recuperador/adapter`).
  - `redactor`: `Pablox0333/qwen3-4b-redactor-udec-d4` fijado en la revisión `739b031acbd5feef2c49f946b94722712209bce0`.
  - `verificador`: adaptador v1 (`exp_multi_lora/entrenamiento/verificador/adapter`) y adaptador recalibrado v2 en Opción B (`exp_multi_lora/entrenamiento/verificador_v2/adapter`).
- *(Nota de repositorio: en Git se versionan la tarjeta `README.md`, `adapter_config.json`, `training_metrics.json` y —en la corrida v1— `smoke_test_val.json` y `loss_curve.{png,pdf}`, manteniendo fuera los pesos binarios `.safetensors`.)*

### 2.2 Métricas de entrenamiento de los adaptadores nuevos

Los 3 adaptadores iniciales usaron LoRA `r=16`, `lora_alpha=32`, `lora_dropout=0.05` sobre las 7 proyecciones (`q,k,v,o,gate,up,down_proj`), `33,030,144` parámetros entrenables (`1.4753%` de `2,238,840,320`), `lr=1e-4` coseno, `3` épocas, `effective_batch_size=6`, `completion_only_loss=True`, `enable_thinking=False` y `seed=2026`. Para **`verificador_v2`** (Opción B) se amplió el balance de ejemplos y se redujo la intensidad para mitigar sobreajuste (`epochs=2.0`, `lr=5e-5`, `lora_dropout=0.1`, `weight_decay=0.05`).

| Agente | Train / Val | Truncados | `max_seq_len` (máx. real) | Pasos | Duración | `eval_loss` inicial | Mejor `eval_loss` | `train_loss` final | Artefactos / Curva |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| `enrutador` | `210` / `36` | `0` / `0` | `2048` (`799`) | `105` | `9.88 min` | `1.066113` | `0.122786` (@ step `80`) | `0.167022` | [loss_curve.png](entrenamiento/enrutador/loss_curve.png) |
| `recuperador` | `230` / `39` | `0` / `0` | `2048` (`918`) | `117` | `10.43 min` | `1.729132` | `0.185810` (@ step `117`) | `0.334458` | [loss_curve.png](entrenamiento/recuperador/loss_curve.png) |
| `verificador` (v1) | `305` / `68` | `0` / `0` | `4096` (`1995`) | `153` | `15.19 min` | `2.833926` | `0.034402` (@ step `150`) | `0.322560` | [loss_curve.png](entrenamiento/verificador/loss_curve.png) |
| `verificador_v2` (Opción B) | `389` / `74` | `0` / `0` | `4096` (`2011`) | `130` | `14.34 min` | `2.739193` | `0.264956` (@ step `130`) | `0.660723` | [training_metrics.json](entrenamiento/verificador_v2/training_metrics.json) |

Tiempo total de entrenamiento en A100 para los tres adaptadores v1: **`35.51 min`** (`2130.36 s`), más **`14.34 min`** (`860.5 s`) de `verificador_v2`.

### 2.3 Verificación de aislamiento cruzado entre los adaptadores

La prueba de logits previa a la inferencia en A100 confirmó que `model.set_adapter(rol)` y `model.disable_adapter()` conmutan realmente los pesos activos sin fugas ni colapsos:

- **`Multi-LoRA (4 agentes v1)`:** `max_abs_diff_vs_base` = `enrutador: 18.0`, `recuperador: 16.375`, `redactor: 19.125`, `verificador: 16.625`; `max_abs_diff_cruzada` (`6` pares) entre `4.5625` (`enrutador vs redactor`) y `5.734375` (`recuperador vs verificador`).
- **`3-LoRA sin Verificador` (`verificador` en base vía `disable_adapter()`):** `max_abs_diff_vs_base` = `enrutador: 17.875`, `recuperador: 16.375`, `redactor: 19.125`; `max_abs_diff_cruzada` (`3` pares) = `4.525879` (`enrutador vs recuperador`), `4.609375` (`enrutador vs redactor`), `5.189453` (`recuperador vs redactor`).
- **`Opción B — 4-LoRA (verificador_v2)`:** `max_abs_diff_vs_base` = `enrutador: 18.0`, `recuperador: 16.375`, `redactor: 19.125`, `verificador: 17.25`; `max_abs_diff_cruzada` (`6` pares) entre `3.796875` (`redactor vs verificador`) y `5.15625` (`recuperador vs redactor`).

---

## 3. Desempeño por Categoría y Comparativa Pareada

### 3.1 Desglose en `nuevas_20` (6 condiciones)

| Categoría | Total | Control Base D4 | Solo Redactor D4 | Ablación Red+Ver | Multi-LoRA (4 v1) | Opción A: 3-LoRA (SV) | Opción B: 4-LoRA (V2) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `factual` | 4 | 3 | **4** | 3 | 3 | 3 | **4** |
| `abstencion` | 2 | **2** | 1 | **2** | **2** | 0 | 0 |
| `calculo` | 2 | **1** | 0 | 0 | 0 | 0 | 0 |
| `condicional` | 4 | 1 | 2 | 1 | **3** | 2 | **3** |
| `cruce` | 3 | 2 | 2 | 2 | **3** | **3** | **3** |
| `multi_salto` | 1 | **1** | **1** | **1** | **1** | **1** | **1** |
| `colision_lexica` | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `negacion_excepcion` | 1 | **1** | 0 | 0 | **1** | **1** | 0 |
| `sintesis` | 1 | 0 | 0 | 0 | **1** | 0 | **1** |
| `premisa_falsa` | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Total estricto** | **20** | **11 (55.0%)** | **10 (50.0%)** | **9 (45.0%)** | **14 (70.0%)** | **10 (50.0%)** | **12 (60.0%)** |
| **Núcleo (sin P01)** | **20** | — | — | **11 (55.0%)** | **15 (75.0%)** | **11 (55.0%)** | **13 (65.0%)** |

- **Pareado Multi-LoRA (4 agentes v1) (`nuevas_20`):** vs `Solo Redactor D4` balance neto **`+4`** (`gana 4-LoRA`: `N05, N08, N12, N17, N18`; `gana Solo Redactor`: `N01`); vs `Control Base D4` **`+3`** (`gana 4-LoRA`: `N09, N11, N12, N18`; `gana Control Base`: `N06`).
- **Pareado 3-LoRA sin Verificador (`nuevas_20`):** vs `Multi-LoRA (4 agentes)` **`-4`** (`gana 3-LoRA(SV)`: ninguno; `gana 4-LoRA`: `N05, N11, N18, N20`; `10` empates en acierto, `6` en fallo); vs `Solo Redactor D4` **`0`** (`gana SV`: `N08, N12, N17`; `gana Solo Redactor`: `N01, N11, N20`); vs `Control Base D4` **`-1`** (`gana SV`: `N09, N12`; `gana Base`: `N05, N06, N20`); vs `Ablación Red+Ver` **`+1`** (`gana SV`: `N08, N09, N12, N17`; `gana Red+Ver`: `N05, N11, N20`).
- **Pareado Opción B `4-LoRA (V2)` (`nuevas_20`):** vs `Opción A 3-LoRA(SV)` **`+2`** (`gana V2`: `N01, N11, N18`; `gana SV`: `N17`); vs `Multi-LoRA (4 agentes v1)` **`-2`** (`gana V2`: `N01`; `gana v1`: `N05, N17, N20`); vs `Solo Redactor D4` **`+2`** (`gana V2`: `N08, N12, N18`; `gana SoloRed`: `N20`); vs `Control Base D4` **`+1`** (`gana V2`: `N01, N09, N11, N12, N18`; `gana Base`: `N05, N06, N17, N20`).

### 3.2 Desglose en el Benchmark `75` D3 (`congelado_50` + `dificil_25`)

| Categoría | Total | Control Base D4 | Solo Redactor D4 | Multi-LoRA (4 v1) | Opción A: 3-LoRA (SV) | Opción B: 4-LoRA (V2) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| `factual` | 10 | **10** | 8 | 9 | **10** | 8 |
| `numerica` | 10 | 9 | **10** | 7 | **10** | 8 |
| `condicional` | 10 | **9** | 7 | 7 | 7 | 8 |
| `cruce` | 10 | 9 | 9 | **10** | 9 | **10** |
| `abstencion` | 10 | 9 | 9 | 7 | **10** | 6 |
| `multi_salto` | 4 | **3** | 1 | 2 | **3** | 2 |
| `calculo` | 4 | 2 | **3** | 1 | **3** | 2 |
| `colision_lexica` | 5 | 3 | **4** | 3 | **4** | **4** |
| `negacion_excepcion` | 3 | **3** | **3** | **3** | **3** | 1 |
| `sintesis` | 5 | 2 | 4 | **5** | 2 | 4 |
| `premisa_falsa` | 4 | 3 | 2 | **4** | 3 | 3 |
| **Total `75` D3** | **75** | **62 (82.7%)** | **60 (80.0%)** | **58 (77.3%)\*** | **64 (85.3%)\*\*** | **56 (74.7%)\*\*\*** |
| `congelado_50` | 50 | **46 (92.0%)** | 43 (86.0%) | 40 (80.0%)\* | **46 (92.0%)\*\*** | 40 (80.0%)\*\*\* |
| `dificil_25` | 25 | 16 (64.0%) | 17 (68.0%) | **18 (72.0%)** | **18 (72.0%)** | 16 (64.0%) |

- **Pareado Multi-LoRA (4 agentes v1) (`75 D3`):** vs `Solo Redactor D4` balance neto **`-2`** (`gana 4-LoRA` en `8`: `congelado_50:{5, 8, 36, 45}`, `dificil_25:{H02, H21, H22, H25}`; `gana Solo Redactor` en `10`: `congelado_50:{6, 11, 12, 16, 46, 47, 48}`, `dificil_25:{H05, H07, H09}`); vs `Control Base D4` **`-4`** (`gana 4-LoRA`: `7`; `gana Control Base`: `11`).
- **Pareado 3-LoRA sin Verificador (`75 D3`):** vs `Multi-LoRA (4 agentes)` **`+6`** (`gana SV` en `12`: `congelado_50:{6, 11, 12, 16, 28, 46, 47, 48}`, `dificil_25:{H04, H05, H07, H09}`; `gana 4-LoRA` en `6`: `congelado_50:{24, 36}`, `dificil_25:{H17, H19, H22, H25}`); vs `Solo Redactor D4` **`+4`** (`gana SV` en `7`: `congelado_50:{5, 8, 28, 45}`, `dificil_25:{H02, H04, H21}`; `gana Solo Redactor` en `3`: `congelado_50:24`, `dificil_25:{H17, H19}`); vs `Control Base D4` **`+2`** (`gana SV` en `5`: `congelado_50:{11, 43}`, `dificil_25:{H07, H18, H24}`; `gana Base` en `3`: `congelado_50:{24, 26}`, `dificil_25:H17`).
- **Pareado Opción B `4-LoRA (V2)` (`75 D3`):** vs `Opción A 3-LoRA(SV)` **`-8`** (`gana V2` en `7`: `congelado_50:{24, 36}`, `dificil_25:{H12, H17, H19, H22, H25}`; `gana SV` en `15`: `congelado_50:{3, 5, 11, 16, 46, 47, 48, 49}`, `dificil_25:{H04, H07, H09, H13, H15, H18, H21}`); vs `Multi-LoRA (4 agentes v1)` **`-2`** (`gana V2` en `5`: `congelado_50:{6, 12, 28}`, `dificil_25:{H05, H12}`; `gana v1` en `7`: `congelado_50:{3, 5, 49}`, `dificil_25:{H13, H15, H18, H21}`); vs `Solo Redactor D4` **`-4`** (`gana V2`: `8`; `gana SoloRed`: `12`); vs `Control Base D4` **`-6`** (`gana V2`: `7`; `gana Base`: `13`). Destaca que **`verificador_v2` logró el primer acierto histórico en `dificil_25:H12`** en ciclo 2.

---

## 4. Análisis Causal por Agente y Ablaciones

### 4.1 Por qué `Enrutador` + `Recuperador` LoRA mejoran los casos más difíciles

La comparación entre `Red+Ver` (`9/20 = 45.0%`) y `Multi-LoRA 4 agentes` (`14/20 = 70.0%`) aísla el aporte conjunto de `enrutador` + `recuperador`:

- **Filtros documentales precisos en cruces y exclusiones (`0/95` fallbacks):**
  - En `nuevas_20:N12`, el `Enrutador` base restringía a `['RI-FI']`, dejando `0` fuentes útiles y forzando una falsa abstención en Base, Solo Redactor y Red+Ver. El `Enrutador` LoRA enruta limpiamente a `['RG']`, y el `Recuperador` LoRA trae `[RG-ART-036]` + `[RG-ART-059]` en 2 llamadas (`4` llamadas totales en 1 ciclo), acertando por primera vez.
  - En `nuevas_20:N17`, el `Enrutador` LoRA restringe a `['RG']`, eliminando el ruido de `RI-FI` que provocaba contaminación cruzada `P01` entre `[RG-ART-011]` y `[RI-FI-ART-002]`.
  - En `75 D3`, logra `10/10` en `cruce`, `5/5` en `sintesis` y `4/4` en `premisa_falsa` (destacando `H21`, `H22`, `H25` y `congelado_50:36, 45`).
- **Debilidades puntuales aguas arriba:**
  - **Enrutador (`2` fallos en `75 D3`):** en `congelado_50:47` y `congelado_50:48` clasifica como `factual` preguntas trampa sobre artículos existentes (`RI-FI Art. 8°` y `Art. 12°`) que preguntan por un umbral inexistente (máximo de créditos o nota mínima en Evaluación de Recuperación), facilitando respuestas sin refutación de premisa.
  - **Recuperador (`2` fallos en `N20`, `2` en `75 D3`):** ocasiones en que dispara `suficiente` demasiado pronto y omite evidencia clave (`N16`: feriados CAL `[CAL-2026-S1-07/08]`, `[CAL-2026-S2-07]`; `N19`: `[RG-ART-018]`; `congelado_50:25`: `[RI-FI-ART-007]`; `dificil_25:H03`: `[CAL-2026-S2-02]`).

### 4.2 El doble filo del `Verificador` (LoRA v1 vs Base vs LoRA v2 en matriz de confusión)

| Corrida | Aprobadas (acierta / falla estricto) | Rechazadas tras 3 ciclos (acierta / falla) | Precisión cuando aprueba | Acierto en rechazadas |
| --- | :---: | :---: | :---: | :---: |
| **`Red+Ver` (`nuevas_20`)** | `18` (`7` / `11`) | `2` (`2` / `0`) | `38.9%` (`7/18`) | **`100.0%` (`2/2`)** |
| **`Multi-LoRA 4 v1` (`nuevas_20`)** | `14` (`10` / `4`) | `6` (`4` / `2`) | `71.4%` (`10/14`) | `66.7%` (`4/6`) |
| **`Multi-LoRA 4 v1` (`75 D3`)** | `58` (`41` / `17`) | `17` (`17` / `0`) | `70.7%` (`41/58`) | **`100.0%` (`17/17`)** |
| **`Opción A — 3-LoRA sin Verificador` (`nuevas_20`)** | `16` (`10` / `6`) | `4` (`0` / `4`) | `62.5%` (`10/16`) | `0.0%` (`0/4`) |
| **`Opción A — 3-LoRA sin Verificador` (`75 D3`)** | `69` (`62` / `7`) | `6` (`2` / `4`) | **`89.9%` (`62/69`)** | `33.3%` (`2/6`) |
| **`Opción B — 4-LoRA Verificador v2` (`nuevas_20`)** | `18` (`11` / `7`) | `2` (`1` / `1`) | `61.1%` (`11/18`) | `50.0%` (`1/2`) |
| **`Opción B — 4-LoRA Verificador v2` (`75 D3`)** | `66` (`50` / `16`) | `9` (`6` / `3`) | `75.8%` (`50/66`) | `33.3%` (`3/9`) |

La comparación directa entre **`Verificador` LoRA v1**, **`Verificador` base (`3-LoRA sin Verificador`)** y **`Verificador` LoRA v2 (Opción B)** aclara qué gana y qué rompe cada enfoque:

1. **Qué corrige quitar el `Verificador` LoRA (`Opción A` en `75 D3`: `64/75`):**
   - **Elimina falsos rechazos sobre `Condiciones o límites: No aplica`:** el `Verificador` LoRA v1 (`eval_loss=0.0344`) rechazaba `17/17` borradores ya correctos en `75 D3`; al usar el `Verificador` base, las rechazadas caen de `17` a `6` (`congelado_50:28` se aprueba en 1 ciclo sin sufrir mutación P01 en ciclo 3) y la precisión al aprobar sube de `70.7%` (`41/58`) a **`89.9%` (`62/69`)**.
   - **Rescates causales del `Verificador` base en ciclo 2:** corrige borradores defectuosos que el `Verificador` LoRA v1 había aprobado en ciclo 1 en **`congelado_50:6`** (rechaza `[RG-ART-025]` de 10 días y envía al Recuperador para traer `[RI-FI-ART-010]`), **`congelado_50:47`** (exige refutar el máximo inexistente en Art. 8° RI-FI aunque el Enrutador lo marcó `factual`), **`congelado_50:48`** y **`dificil_25:H04`** (`[RG-ART-049]`).
2. **Qué rompe volver al `Verificador` base (`Opción A`, `5` regresiones causales + `1` agravamiento):**
   - En **`nuevas_20`** (`10/20` vs `14/20`), **3 de las 4 diferencias (`N05`, `N11`, `N20`)** son borradores ya válidos generados por el `Redactor` LoRA en ciclos 1–2 que el `Verificador` LoRA v1 aprobaba, pero que el `Verificador` base rechaza con objeciones alucinadas.
   - En **`75 D3`**, el `Verificador` base produce dos regresiones causales limpias en `sintesis` (`dificil_25:H17`, `dificil_25:H19`) y empuja `H06` a una falsa abstención.
3. **Qué aportó y por qué no bastó `Verificador LoRA v2` (`Opción B`: `12/20` y `56/75`, `68/95 = 71.6%`):**
   - **Rescates reales en ciclo 2:** redujo rechazos de borradores correctos en `75 D3` de `17` a `6` (y de `4` a `1` en `nuevas_20`), aprobó limpiamente `N03` y `congelado_50:28` en 1 ciclo, rescató `N01`, `congelado_50:6, 12`, `dificil_25:H05`, y logró **el primer acierto histórico en `dificil_25:H12`** al rechazar la mezcla con Baja Académica en ciclo 1.
   - **Límites persistentes (sobre-rechazo + falsa aprobación):** pese a rebalancear `No aplica`, el `Verificador` LoRA v2 siguió provocando **`7` regresiones causales directas** por rechazos indebidos en `nuevas_20` (`N17`: reduce excepción a "salvo excepciones"; `N20`: fuerza a negar requisitos de `[RG-ART-057]`) y `75 D3` (`congelado_50:16`, `congelado_50:49`, `H18`, `H21`, y un bucle repetitivo de `<pensar>` en `H15` que trunca con **respuesta vacía**). Simultáneamente dejó pasar **`23` falsas aprobaciones** en `95` preguntas (aritmética en `N07`, `H03`, `H06`; `P01` y omisiones en `C50:3, 5, 11, 47, 48`, `H04, H07, H09, H13`).

### 4.3 Causas raíz de fallo consolidadas

- **`Multi-LoRA 4 v1 nuevas_20` (`6` fallos):** `redactor: 4` (`N01`, `N06`, `N07`, `N10`), `recuperador: 2` (`N16`, `N19`).
- **`Ablación Red+Ver nuevas_20` (`11` fallos):** `redactor: 7` (`N06`, `N07`, `N08`, `N10`, `N16`, `N17`, `N18`), `verificador: 2` (`N01`, `N09`), `enrutador: 2` (`N12`, `N19`).
- **`Multi-LoRA 4 v1 75 D3` (`17` fallos):** `redactor: 12` (`C50:{6,11,12,16,26,46}`, `H04, H05, H06, H07, H09, H12`), `recuperador: 2` (`C50:25`, `H03`), `enrutador: 2` (`C50:47, 48`), `verificador: 1` (`C50:28`).
- **`3-LoRA sin Verificador nuevas_20` (`10` fallos):** `redactor: 4` (`N01`, `N06`, `N07`, `N10`), `verificador: 3` (`N05`, `N11`, `N20`), `recuperador: 3` (`N16`, `N18`, `N19`).
- **`3-LoRA sin Verificador 75 D3` (`11` fallos):** `redactor: 6` (`C50:24`, `C50:26`, `H06`, `H12`, `H22`, `H25`), `recuperador: 3` (`C50:25`, `C50:36`, `H03`), `verificador: 2` (`H17`, `H19`).
- **`4-LoRA Verificador v2 nuevas_20` (`8` fallos):** `redactor: 4` (`N05`, `N06`, `N07`, `N10`), `recuperador: 2` (`N16`, `N19`), `verificador: 2` (`N17`, `N20`).
- **`4-LoRA Verificador v2 75 D3` (`19` fallos):** `redactor: 11` (`C50:{3,5,11,26,46,48}`, `H04, H06, H07, H09, H13`), `verificador: 5` (`C50:{16,49}`, `H15, H18, H21`), `recuperador: 2` (`C50:25`, `H03`), `enrutador: 1` (`C50:47`). *(En `C50:46` además el Redactor cita `[RI-FI-ART-035]` fuera de evidencia antes de concluir sin respaldo.)*

*(Solo los fallos con `solo_condicion_p01=True`: `N06` en `4-LoRA v1`, `3-LoRA(SV)` y `4-LoRA(V2) nuevas_20`; `N17, N18` en `Red+Ver`; `C50:12, C50:28, H07, H09` en `4-LoRA v1 75`; `H22` en `3-LoRA(SV) 75`; y `C50:3, C50:5, H07, H09, H13, H18` en `4-LoRA(V2) 75` tienen la respuesta central correcta pero violan la Regla 3/P01 en la línea `Condiciones o límites`.)*

---

## 5. Eficiencia, Telemetría y Latencia Comparada

| Métrica | `Control Base` (`75` / `N20`) | `Solo Redactor` (`75` / `N20`) | `Red+Ver` (`N20`) | `Multi-LoRA 4 v1` (`75` / `N20`) | **`3-LoRA SV` (Opción A)** (`75` / `N20`) | `4-LoRA V2` (Opción B) (`75` / `N20`) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| Ciclos promedio | `1.31` / `1.80` | `1.33` / `1.50` | `1.40` | `1.57` / `1.75` | **`1.31` / `1.60`** | `1.51` / `1.90` |
| Llamadas totales | `658` / `254` | `648` / `212` | `190` | `493` / `138` | **`388`** / **`118`** | `486` / `147` |
| Llamadas `Recuperador` | `387` / `162` | `373` / `132` | `114` | `182` / `48` | **`117`** / **`34`** | `185` / `51` |
| Llamadas `Redactor` | `98` / `36` | `100` / `30` | `28` | `118` / `35` | **`98`** / **`32`** | `113` / `38` |
| Tokens entrada totales | `589,849` / `227,634` | `586,425` / `184,073` | `166,985` | `496,739` / `146,735` | **`370,790`** / **`121,979`** | `481,919` / `164,089` |
| Tokens salida totales | `55,627` / `24,971` | `39,496` / `13,427` | `13,040` | `43,043` / `14,912` | **`31,832`** / **`13,404`** | `43,960` / `16,938` |
| Tiempo total CSV (s) | `4520.5` / `1970.2` | `4541.2` / `1504.1` | `1692.9` | `6346.3` / `2197.9` | **`4354.4`** / `1814.1` | `6491.7` / `2492.2` |
| Throughput salida (`tok/s` tel.) | **`12.31`** / **`12.67`** | `8.70` / `8.93` | `7.71` | `6.79` / `6.79` | `7.32` / `7.39` | `6.78` / `6.80` |

La comparación de telemetría entre las tres ramas multi-LoRA confirma que:

1. **Opción A (`3-LoRA sin Verificador`) domina en velocidad y economía de tokens:** con `verificador` en base vía `disable_adapter()`, reduce los ciclos a `1.31` en `75 D3`, recorta las llamadas totales a `388` (`-21.3%` vs `4-LoRA v1`, `-20.2%` vs `4-LoRA V2`) y termina `75 D3` en **`4354.4 s`** (`72.6 min`), un **`-32.9%`** respecto a `4-LoRA V2` (`6491.7 s` = `108.2 min`).
2. **Costo de reintentos y bucles con 4 adaptadores (`Opción B`):** aunque `verificador_v2` redujo levemente las llamadas frente a `v1` en `75 D3` (`486` vs `493`), el bucle degenerativo de `dificil_25:H15` y los ciclos extra en `nuevas_20` (`1.90` ciclos, `2492.2 s`) elevaron el volumen total de tokens generados (`43,960` / `16,938`), manteniendo el throughput efectivo en `6.78–6.80 tok/s`.

---

## 6. Síntesis Arquitectónica y Decisión Experimental

1. **Configuración recomendada hoy (`Opción A: 3-LoRA sin Verificador`):** combina `enrutador` + `recuperador` + `redactor` en QLoRA con `verificador` en modelo base (`Qwen/Qwen3-4B` sin adaptador). Logra el **máximo histórico en `75 D3` (`64/75 = 85.3%`)** y en el **consolidado de `95` preguntas (`74/95 = 77.9%`)** siendo **`31.4%–32.9%` más rápida** que las variantes con `Verificador` LoRA.
2. **Por qué la Opción B (`Verificador` LoRA SFT v2 a escala `4B`) no resolvió el cuello de botella:** un clasificador/crítico en `4B` entrenado con SFT puro sobre trazas sintéticas alterna entre *sobre-rechazo* (romper borradores válidos en ciclo 2–3) y *falsa aprobación* de errores sutiles `P01`/aritméticos. Seguir agregando datos SFT al mismo crítico `4B` exhibe rendimientos decrecientes (`72/95 -> 68/95`).
3. **Líneas prometedoras si se retoma una fase posterior:** (a) **chequeos deterministas híbridos** (verificador programático de línea `Fuente:`, citas dentro de `<evidencia>` y verificación aritmética antes de devolver a ciclo 2); (b) refuerzo específico de **`Enrutador`** en falsas premisas sobre artículos reales (`congelado_50:47, 48`) y **`Recuperador`** en fechas de calendario (`N16`, `H03`), transitorios (`N18`) y prerrequisitos (`C50:25`, `N19`); o (c) usar un crítico de mayor capacidad / DPO de preferencias para el rol de `Verificador`.

---

## 7. Artefactos Generados y Reproducibilidad

- Script de auditoría y consolidación: [`scripts/generar_auditoria_multi.py`](scripts/generar_auditoria_multi.py)
- Resumen comparativo global: [`evaluacion/resumen_comparativo_global.json`](evaluacion/resumen_comparativo_global.json)
- Auditorías y CSVs auditados (`SHA-256` verificados sobre CSVs crudos de Colab):
  - `Multi-LoRA (4 agentes v1) nuevas_20`: [`auditoria_multi_lora_nuevas20.json`](evaluacion/auditoria_multi_lora_nuevas20.json) · [`resultados_multi_lora_nuevas20_auditados.csv`](evaluacion/resultados_multi_lora_nuevas20_auditados.csv)
  - `Ablación Red+Ver nuevas_20`: [`auditoria_ablacion_red_ver_nuevas20.json`](evaluacion/auditoria_ablacion_red_ver_nuevas20.json) · [`resultados_ablacion_red_ver_nuevas20_auditados.csv`](evaluacion/resultados_ablacion_red_ver_nuevas20_auditados.csv)
  - `Multi-LoRA (4 agentes v1) 75 D3`: [`auditoria_multi_lora_75.json`](evaluacion/auditoria_multi_lora_75.json) · [`resultados_multi_lora_75_auditados.csv`](evaluacion/resultados_multi_lora_75_auditados.csv)
  - `Opción A — 3-LoRA sin Verificador nuevas_20`: [`auditoria_sin_verificador_nuevas20.json`](evaluacion/auditoria_sin_verificador_nuevas20.json) · [`resultados_sin_verificador_nuevas20_auditados.csv`](evaluacion/resultados_sin_verificador_nuevas20_auditados.csv)
  - `Opción A — 3-LoRA sin Verificador 75 D3`: [`auditoria_sin_verificador_75.json`](evaluacion/auditoria_sin_verificador_75.json) · [`resultados_sin_verificador_75_auditados.csv`](evaluacion/resultados_sin_verificador_75_auditados.csv)
  - `Opción B — 4-LoRA Verificador v2 nuevas_20`: [`auditoria_verificador_v2_nuevas20.json`](evaluacion/auditoria_verificador_v2_nuevas20.json) · [`resultados_verificador_v2_nuevas20_auditados.csv`](evaluacion/resultados_verificador_v2_nuevas20_auditados.csv)
  - `Opción B — 4-LoRA Verificador v2 75 D3`: [`auditoria_verificador_v2_75.json`](evaluacion/auditoria_verificador_v2_75.json) · [`resultados_verificador_v2_75_auditados.csv`](evaluacion/resultados_verificador_v2_75_auditados.csv)
