# Reporte de Resultados — Experimento Multi-LoRA (`exp_multi_lora`)

**Ramas:** `exp/multi-lora-todos` (`4` LoRAs) y `exp/multi-lora-sin-verificador` (`3` LoRAs, `verificador` en base) · **Modelo base:** `Qwen/Qwen3-4B` (QLoRA NF4 4-bit, `torch.bfloat16`) · **Hardware:** `NVIDIA A100-SXM4-40GB` (`42.41 GB` VRAM)  
**Criterio de auditoría:** estricta contra el corpus fuente y [`LEEME_PAUTA.md`](../Deliverable%203/paquete_25_dificiles/LEEME_PAUTA.md) (reglas 1–8, incluyendo excepciones Regla 2 y precedentes Regla 3 / `P01`).

---

## 1. Resumen Ejecutivo

El experimento evaluó en dos ramas complementarias cómo escala el sistema multi-agente sobre **una sola instancia NF4 de `Qwen/Qwen3-4B`** bajo idénticos prompts v6, parámetros de decodificación (`T=0.7`, `top_p=0.8`, `top_k=20`, `enable_thinking=False`) y semillas derivadas: primero entrenando adaptadores QLoRA independientes para los cuatro roles (`enrutador`, `recuperador`, `redactor` D4 v2 y `verificador`), y luego evaluando la configuración **3-LoRA sin Verificador** (`enrutador + recuperador + redactor` con LoRA, y `verificador` en modo base mediante `model.disable_adapter()`).

| Condición | `congelado_50` | `dificil_25` | **Benchmark `75` D3** | **`nuevas_20` (no vistas)** | **Consolidado `95`** | Llamadas totales (`75` / `N20`) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control Base D4** (0 LoRA) | **46/50 (92.0%)** | 16/25 (64.0%) | 62/75 (82.7%) | 11/20 (55.0%) | 73/95 (76.8%) | 658 / 254 |
| **Solo Redactor D4** (1 LoRA) | 43/50 (86.0%) | 17/25 (68.0%) | 60/75 (80.0%) | 10/20 (50.0%) | 70/95 (73.7%) | 648 / 212 |
| **Ablación Red+Ver** (2 LoRAs) | — | — | — | 9/20 (45.0%) | — | — / 190 |
| **Multi-LoRA (4 agentes)** | 40/50 (80.0%)\* | **18/25 (72.0%)** | 58/75 (77.3%)\* | **14/20 (70.0%)** | 72/95 (75.8%) | 493 / 138 |
| **3-LoRA sin Verificador** (`verificador` base) | **46/50 (92.0%)**\*\* | **18/25 (72.0%)** | **64/75 (85.3%)**\*\* | 10/20 (50.0%) | **74/95 (77.9%)** | **388 / 118** |

> \* **Nota de transparencia (`Multi-LoRA 4 agentes`, `congelado_50:8`):** el contenido jurídico y ambas citas inline (`[RG-ART-034] [RI-FI-ART-026]`) son correctos y evitan el fallo P01 de `Solo Redactor D4`, pero omiten la tercera línea literal `Fuente:` (`formato_3_lineas_ok=False`). Bajo exigencia estricta de 3 líneas literales, la cifra pasaría a `39/50` (`78.0%`) y `57/75` (`76.0%`).  
> \*\* **Nota de transparencia (`3-LoRA sin Verificador`, `congelado_50:7` y `congelado_50:8`):** ambos aciertan el contenido jurídico y citan inline los artículos exactos (`[RI-FI-ART-016]` y `[RG-ART-034] [RI-FI-ART-026]`), pero omiten la línea final literal `Fuente:` (`formato_3_lineas_ok=73/75`). Bajo exigencia estricta de 3 líneas literales, sería `44/50` (`88.0%`) y `62/75` (`82.7%`).

**Conclusiones principales:**

1. **Generalización difícil (`Enrutador` + `Recuperador` LoRA):** en `Multi-LoRA (4 agentes)` sube a **`14/20` (`70.0%`)** en `nuevas_20` y en ambas configuraciones de `3`/`4` LoRAs marca **`18/25` (`72.0%`)** en `dificil_25` (máximo histórico). La ablación `Red+Ver` (`9/20 = 45.0%`) confirma que el salto de generalización en casos complejos proviene de **`enrutador` + `recuperador`** trabajando juntos.
2. **Eficiencia récord de recuperación sin fallbacks (`3-LoRA sin Verificador`):** frente a `Solo Redactor D4`, las llamadas del `Recuperador` caen **`-68.6%`** en `75 D3` (`373 -> 117`) y **`-74.2%`** en `nuevas_20` (`132 -> 34`), con `-40.1%` / `-44.3%` llamadas totales, `-31.4%` de tiempo total en `75 D3` frente a `4-LoRA` (`4354.4 s` vs `6346.3 s`) y **`0`** fallbacks o citas fuera de evidencia en todas las corridas (`190` respuestas auditadas).
3. **Doble disociación al quitar el LoRA del `Verificador` (`3-LoRA` vs `4-LoRA`):**
   - **En `75 D3` y consolidado `95`**, quitar el `Verificador` LoRA dispara los aciertos a **`64/75` (`85.3%`, máximo histórico)** recuperando **`46/50` (`92.0%`)** en `congelado_50`, y dejando a **`3-LoRA sin Verificador`** como el mejor sistema acumulado en **`95` preguntas (`74/95 = 77.9%`)**. Evita la hipersensibilidad del `Verificador` LoRA ante `Condiciones o límites: No aplica` (`congelado_50:28`) y logra rescates genuinos en ciclo 2 (`congelado_50:6, 47` y `dificil_25:H04`).
   - **En `nuevas_20`**, sin embargo, volver al `Verificador` base revierte la marca a **`10/20` (`50.0%`, vs `14/20` en `4-LoRA`)**: el `Verificador` base rechaza borradores ya correctos del ciclo 1–2 con objeciones alucinadas (`N05`, `N11`, `N20` en `nuevas_20`; `H17`, `H19` y agravamiento de `H06` en `75 D3`) que el `Verificador` LoRA sí aprobaba. En consecuencia, **ni el `Verificador` LoRA v1 ni el `Verificador` base son suficientes por sí solos**; la solución óptima requiere conservar `enrutador + recuperador + redactor` y recalibrar un **`Verificador` LoRA v2**.

---

## 2. Entrenamiento QLoRA y Paridad Experimental

### 2.1 Entorno y paridad con Deliverable 4

- **Software en Colab A100:** `torch 2.14.1+cu130`, `transformers 5.23.0`, `peft 0.21.3`, `bitsandbytes 0.50.2`, `accelerate 1.15.0`, `huggingface_hub 1.33.0`, `sentence-transformers 6.3.0`.
- **Prompts v6 idénticos (SHA-256 verificado):** `01_enrutador.txt` (`cc0d5e40...`), `02_recuperador.txt` (`2fe9b0af...`), `03_redactor.txt` (`6b3e4ac3...`), `04_verificador.txt` (`c141fe36...`).
- **Adaptadores cargados en un único `Qwen/Qwen3-4B` NF4:**
  - `enrutador`: adaptador entrenado localmente (`exp_multi_lora/entrenamiento/enrutador/adapter`).
  - `recuperador`: adaptador entrenado localmente (`exp_multi_lora/entrenamiento/recuperador/adapter`).
  - `redactor`: `Pablox0333/qwen3-4b-redactor-udec-d4` fijado en la revisión `739b031acbd5feef2c49f946b94722712209bce0`.
  - `verificador`: adaptador entrenado localmente (`exp_multi_lora/entrenamiento/verificador/adapter`).
- *(Nota de repositorio: igual que en `Deliverable 4/entrenamiento/adapter/`, en Git se versionan la tarjeta `README.md`, `training_metrics.json`, `smoke_test_val.json` y `loss_curve.{png,pdf}`, manteniendo fuera los pesos binarios `.safetensors`.)*

### 2.2 Métricas de entrenamiento de los 3 nuevos adaptadores

Todos usaron LoRA `r=16`, `lora_alpha=32`, `lora_dropout=0.05` sobre las 7 proyecciones (`q,k,v,o,gate,up,down_proj`), `33,030,144` parámetros entrenables (`1.4753%` de `2,238,840,320`), `lr=1e-4` coseno, `3` épocas, `effective_batch_size=6`, `completion_only_loss=True`, `enable_thinking=False` y `seed=2026`.

| Agente | Train / Val | Truncados | `max_seq_len` (máx. real) | Pasos | Duración | `eval_loss` inicial | Mejor `eval_loss` | `train_loss` final | Curva |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| `enrutador` | `210` / `36` | `0` / `0` | `2048` (`799`) | `105` | `9.88 min` | `1.066113` | `0.122786` (@ step `80`) | `0.167022` | [loss_curve.png](entrenamiento/enrutador/loss_curve.png) |
| `recuperador` | `230` / `39` | `0` / `0` | `2048` (`918`) | `117` | `10.43 min` | `1.729132` | `0.185810` (@ step `117`) | `0.334458` | [loss_curve.png](entrenamiento/recuperador/loss_curve.png) |
| `verificador` | `305` / `68` | `0` / `0` | `4096` (`1995`) | `153` | `15.19 min` | `2.833926` | `0.034402` (@ step `150`) | `0.322560` | [loss_curve.png](entrenamiento/verificador/loss_curve.png) |

Tiempo total de entrenamiento en A100 para los tres nuevos adaptadores: **`35.51 min`** (`2130.36 s`).

### 2.3 Verificación de aislamiento cruzado entre los adaptadores

La prueba de logits previa a la inferencia en A100 confirmó que `model.set_adapter(rol)` y `model.disable_adapter()` conmutan realmente los pesos activos sin fugas ni colapsos:

- **`Multi-LoRA (4 agentes)`:** `max_abs_diff_vs_base` = `enrutador: 18.0`, `recuperador: 16.375`, `redactor: 19.125`, `verificador: 16.625`; `max_abs_diff_cruzada` (`6` pares) entre `4.5625` (`enrutador vs redactor`) y `5.734375` (`recuperador vs verificador`).
- **`3-LoRA sin Verificador` (`verificador` en base vía `disable_adapter()`):** `max_abs_diff_vs_base` = `enrutador: 17.875`, `recuperador: 16.375`, `redactor: 19.125`; `max_abs_diff_cruzada` (`3` pares) = `4.525879` (`enrutador vs recuperador`), `4.609375` (`enrutador vs redactor`), `5.189453` (`recuperador vs redactor`).

---

## 3. Desempeño por Categoría y Comparativa Pareada

### 3.1 Desglose en `nuevas_20` (5 condiciones)

| Categoría | Total | Control Base D4 | Solo Redactor D4 | Ablación Red+Ver | Multi-LoRA (4 agentes) | 3-LoRA sin Verificador |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| `factual` | 4 | 3 | **4** | 3 | 3 | 3 |
| `abstencion` | 2 | **2** | 1 | **2** | **2** | 0 |
| `calculo` | 2 | **1** | 0 | 0 | 0 | 0 |
| `condicional` | 4 | 1 | 2 | 1 | **3** | 2 |
| `cruce` | 3 | 2 | 2 | 2 | **3** | **3** |
| `multi_salto` | 1 | **1** | **1** | **1** | **1** | **1** |
| `colision_lexica` | 1 | 0 | 0 | 0 | 0 | 0 |
| `negacion_excepcion` | 1 | **1** | 0 | 0 | **1** | **1** |
| `sintesis` | 1 | 0 | 0 | 0 | **1** | 0 |
| `premisa_falsa` | 1 | 0 | 0 | 0 | 0 | 0 |
| **Total estricto** | **20** | **11 (55.0%)** | **10 (50.0%)** | **9 (45.0%)** | **14 (70.0%)** | **10 (50.0%)** |
| **Núcleo (sin P01)** | **20** | — | — | **11 (55.0%)** | **15 (75.0%)** | **11 (55.0%)** |

- **Pareado Multi-LoRA (4 agentes) (`nuevas_20`):** vs `Solo Redactor D4` balance neto **`+4`** (`gana 4-LoRA`: `N05, N08, N12, N17, N18`; `gana Solo Redactor`: `N01`); vs `Control Base D4` **`+3`** (`gana 4-LoRA`: `N09, N11, N12, N18`; `gana Control Base`: `N06`).
- **Pareado 3-LoRA sin Verificador (`nuevas_20`):** vs `Multi-LoRA (4 agentes)` **`-4`** (`gana 3-LoRA(SV)`: ninguno; `gana 4-LoRA`: `N05, N11, N18, N20`; `10` empates en acierto, `6` en fallo); vs `Solo Redactor D4` **`0`** (`gana SV`: `N08, N12, N17`; `gana Solo Redactor`: `N01, N11, N20`); vs `Control Base D4` **`-1`** (`gana SV`: `N09, N12`; `gana Base`: `N05, N06, N20`); vs `Ablación Red+Ver` **`+1`** (`gana SV`: `N08, N09, N12, N17`; `gana Red+Ver`: `N05, N11, N20`).

### 3.2 Desglose en el Benchmark `75` D3 (`congelado_50` + `dificil_25`)

| Categoría | Total | Control Base D4 | Solo Redactor D4 | Multi-LoRA (4 agentes) | 3-LoRA sin Verificador |
| --- | :---: | :---: | :---: | :---: | :---: |
| `factual` | 10 | **10** | 8 | 9 | **10** |
| `numerica` | 10 | 9 | **10** | 7 | **10** |
| `condicional` | 10 | **9** | 7 | 7 | 7 |
| `cruce` | 10 | 9 | 9 | **10** | 9 |
| `abstencion` | 10 | 9 | 9 | 7 | **10** |
| `multi_salto` | 4 | **3** | 1 | 2 | **3** |
| `calculo` | 4 | 2 | **3** | 1 | **3** |
| `colision_lexica` | 5 | 3 | **4** | 3 | **4** |
| `negacion_excepcion` | 3 | **3** | **3** | **3** | **3** |
| `sintesis` | 5 | 2 | 4 | **5** | 2 |
| `premisa_falsa` | 4 | 3 | 2 | **4** | 3 |
| **Total `75` D3** | **75** | **62 (82.7%)** | **60 (80.0%)** | **58 (77.3%)\*** | **64 (85.3%)\*\*** |
| `congelado_50` | 50 | **46 (92.0%)** | 43 (86.0%) | 40 (80.0%)\* | **46 (92.0%)\*\*** |
| `dificil_25` | 25 | 16 (64.0%) | 17 (68.0%) | **18 (72.0%)** | **18 (72.0%)** |

- **Pareado Multi-LoRA (4 agentes) (`75 D3`):** vs `Solo Redactor D4` balance neto **`-2`** (`gana 4-LoRA` en `8`: `congelado_50:{5, 8, 36, 45}`, `dificil_25:{H02, H21, H22, H25}`; `gana Solo Redactor` en `10`: `congelado_50:{6, 11, 12, 16, 46, 47, 48}`, `dificil_25:{H05, H07, H09}`); vs `Control Base D4` **`-4`** (`gana 4-LoRA`: `7`; `gana Control Base`: `11`).
- **Pareado 3-LoRA sin Verificador (`75 D3`):** vs `Multi-LoRA (4 agentes)` **`+6`** (`gana SV` en `12`: `congelado_50:{6, 11, 12, 16, 28, 46, 47, 48}`, `dificil_25:{H04, H05, H07, H09}`; `gana 4-LoRA` en `6`: `congelado_50:{24, 36}`, `dificil_25:{H17, H19, H22, H25}`); vs `Solo Redactor D4` **`+4`** (`gana SV` en `7`: `congelado_50:{5, 8, 28, 45}`, `dificil_25:{H02, H04, H21}`; `gana Solo Redactor` en `3`: `congelado_50:24`, `dificil_25:{H17, H19}`); vs `Control Base D4` **`+2`** (`gana SV` en `5`: `congelado_50:{11, 43}`, `dificil_25:{H07, H18, H24}`; `gana Base` en `3`: `congelado_50:{24, 26}`, `dificil_25:H17`).

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

### 4.2 El doble filo del `Verificador` (LoRA v1 vs Base en matriz de confusión)

| Corrida | Aprobadas (acierta / falla estricto) | Rechazadas tras 3 ciclos (acierta / falla) | Precisión cuando aprueba | Acierto en rechazadas |
| --- | :---: | :---: | :---: | :---: |
| **`Red+Ver` (`nuevas_20`)** | `18` (`7` / `11`) | `2` (`2` / `0`) | `38.9%` (`7/18`) | **`100.0%` (`2/2`)** |
| **`Multi-LoRA 4` (`nuevas_20`)** | `14` (`10` / `4`) | `6` (`4` / `2`) | `71.4%` (`10/14`) | `66.7%` (`4/6`) |
| **`Multi-LoRA 4` (`75 D3`)** | `58` (`41` / `17`) | `17` (`17` / `0`) | `70.7%` (`41/58`) | **`100.0%` (`17/17`)** |
| **`3-LoRA sin Verificador` (`nuevas_20`)** | `16` (`10` / `6`) | `4` (`0` / `4`) | `62.5%` (`10/16`) | `0.0%` (`0/4`) |
| **`3-LoRA sin Verificador` (`75 D3`)** | `69` (`62` / `7`) | `6` (`2` / `4`) | **`89.9%` (`62/69`)** | `33.3%` (`2/6`) |

La comparación directa entre **`Verificador` LoRA** y **`Verificador` base (`3-LoRA sin Verificador`)** aclara exactamente qué gana y qué pierde cada uno:

1. **Qué corrige quitar el `Verificador` LoRA (`3-LoRA` en `75 D3`: `+6` netos, `64/75`):**
   - **Elimina falsos rechazos sobre `Condiciones o límites: No aplica`:** el `Verificador` LoRA (`eval_loss=0.0344`) rechazaba `17/17` borradores ya correctos en `75 D3`; al usar el `Verificador` base, las rechazadas caen de `17` a `6` (`congelado_50:28` se aprueba en 1 ciclo sin sufrir mutación P01 en ciclo 3) y la precisión al aprobar sube de `70.7%` (`41/58`) a **`89.9%` (`62/69`)**.
   - **Rescates causales del `Verificador` base en ciclo 2:** corrige borradores defectuosos que el `Verificador` LoRA había aprobado en ciclo 1 en **`congelado_50:6`** (rechaza `[RG-ART-025]` de 10 días y envía al Recuperador para traer `[RI-FI-ART-010]`), **`congelado_50:47`** (exige refutar el máximo inexistente en Art. 8° RI-FI aunque el Enrutador lo marcó `factual`), **`congelado_50:48`** y **`dificil_25:H04`** (`[RG-ART-049]`). *(Además, variaciones bajo `T=0.7` con `3` vs `4` adaptadores en `bfloat16` resolvieron en ciclo 1 `congelado_50:{11,12,16,46}`, `H05, H07, H09` frente a `congelado_50:{24,36}`, `H22, H25` y `N18`.)*
2. **Qué rompe volver al `Verificador` base (`5` regresiones causales + `1` agravamiento):**
   - En **`nuevas_20`** (`10/20` vs `14/20`), **3 de las 4 diferencias (`N05`, `N11`, `N20`)** son borradores ya válidos generados por el `Redactor` LoRA en ciclos 1–2 que el `Verificador` LoRA aprobaba sin problemas, pero que el `Verificador` base rechaza con objeciones alucinadas: en `N05` fuerza a mezclar `[RI-FI-ART-017]`; en `N11` y `N20` fuerza a suprimir la aceptación en postgrado / proposición de la Facultad de `[RG-ART-057]`.
   - En **`75 D3`**, el `Verificador` base produce dos regresiones causales limpias en `sintesis` (`dificil_25:H17`, tras 3 rechazos invierte el tope `máximo 80%` en `asistencia mínima entre el 80% y el 100%`; `dificil_25:H19`, borra la condición de pérdida de calidad de alumno de `[RG-ART-028]`) y empuja `H06` a una falsa abstención al rechazar falsamente `38 / 4 = 9,5`.

### 4.3 Causas raíz de fallo consolidadas

- **`Multi-LoRA 4 nuevas_20` (`6` fallos):** `redactor: 4` (`N01`, `N06`, `N07`, `N10`), `recuperador: 2` (`N16`, `N19`).
- **`Ablación Red+Ver nuevas_20` (`11` fallos):** `redactor: 7` (`N06`, `N07`, `N08`, `N10`, `N16`, `N17`, `N18`), `verificador: 2` (`N01`, `N09`), `enrutador: 2` (`N12`, `N19`).
- **`Multi-LoRA 4 75 D3` (`17` fallos):** `redactor: 12` (`C50:{6,11,12,16,26,46}`, `H04, H05, H06, H07, H09, H12`), `recuperador: 2` (`C50:25`, `H03`), `enrutador: 2` (`C50:47, 48`), `verificador: 1` (`C50:28`).
- **`3-LoRA sin Verificador nuevas_20` (`10` fallos):** `redactor: 4` (`N01`, `N06`, `N07`, `N10`), `verificador: 3` (`N05`, `N11`, `N20`), `recuperador: 3` (`N16`, `N18`, `N19`).
- **`3-LoRA sin Verificador 75 D3` (`11` fallos):** `redactor: 6` (`C50:24`, `C50:26`, `H06`, `H12`, `H22`, `H25`), `recuperador: 3` (`C50:25`, `C50:36`, `H03`), `verificador: 2` (`H17`, `H19`).

*(Solo los fallos con `solo_condicion_p01=True`: `N06` en `4-LoRA nuevas_20` y `3-LoRA(SV) nuevas_20`, `N17, N18` en `Red+Ver`, `C50:12, C50:28, H07, H09` en `4-LoRA 75`, y `H22` en `3-LoRA(SV) 75` tienen la respuesta central correcta pero violan la Regla 3/P01 en la línea `Condiciones o límites`.)*

---

## 5. Eficiencia, Telemetría y Latencia Comparada

| Métrica | `Control Base` (`75` / `N20`) | `Solo Redactor` (`75` / `N20`) | `Red+Ver` (`N20`) | `Multi-LoRA 4` (`75` / `N20`) | **`3-LoRA Sin Verificador`** (`75` / `N20`) |
| --- | :---: | :---: | :---: | :---: | :---: |
| Ciclos promedio | `1.31` / `1.80` | `1.33` / `1.50` | `1.40` | `1.57` / `1.75` | **`1.31` / `1.60`** |
| Llamadas totales | `658` / `254` | `648` / `212` | `190` | `493` / `138` | **`388`** / **`118`** |
| Llamadas `Recuperador` | `387` / `162` | `373` / `132` | `114` | `182` / `48` | **`117`** / **`34`** |
| Llamadas `Redactor` | `98` / `36` | `100` / `30` | `28` | `118` / `35` | **`98`** / **`32`** |
| Tokens entrada totales | `589,849` / `227,634` | `586,425` / `184,073` | `166,985` | `496,739` / `146,735` | **`370,790`** / **`121,979`** |
| Tokens salida totales | `55,627` / `24,971` | `39,496` / `13,427` | `13,040` | `43,043` / `14,912` | **`31,832`** / **`13,404`** |
| Tiempo total CSV (s) | `4520.5` / `1970.2` | `4541.2` / `1504.1` | `1692.9` | `6346.3` / `2197.9` | **`4354.4`** / `1814.1` |
| Throughput salida (`tok/s` tel.) | **`12.31`** / **`12.67`** | `8.70` / `8.93` | `7.71` | `6.79` / `6.79` | `7.32` / `7.39` |

La rama `exp/multi-lora-sin-verificador` confirma el diagnóstico de latencia de la sección anterior:

1. **Reducción drástica de tiempo al eliminar el `Verificador` LoRA:** en `75 D3`, bajar de `4` a `3` adaptadores (con `verificador` vía `disable_adapter()`) recorta los tokens de salida del `Verificador` a menos de la mitad (`5,654` vs `11,922 tok` de `<pensar>`), evita `20` ciclos de reintento (`98` vs `118` llamadas del `Redactor`), sube el throughput de `6.79` a **`7.32–7.39 tok/s`**, y logra en **`4354.4 s`** un tiempo **`-31.4%` menor que `Multi-LoRA 4` (`6346.3 s`)** y hasta ligeramente inferior al de `Solo Redactor` (`4541.2 s`) y `Control Base` (`4520.5 s`).
2. **Costo residual de conmutación Multi-LoRA (`3` LoRAs):** aunque el volumen de tokens es el menor de todo el estudio (`370,790` / `121,979` `in_tok`), mantener `3` adaptadores `r=16` en los 7 módulos lineales sigue situando el throughput (`7.32–7.39 tok/s`) por debajo de `Solo Redactor` (`8.70–8.93 tok/s`) y `Control Base` (`12.31–12.67 tok/s`), casi equiparado por el ahorro masivo de tokens y llamadas (`-40.1%` llamadas en `75 D3`).

---

## 6. Lecciones para una Eventual Iteración v2

1. **Resultado confirmado sobre `3-LoRA sin Verificador` (`enrutador + recuperador + redactor`):** ya ejecutado y auditado en la rama `exp/multi-lora-sin-verificador`, alcanza el **máximo histórico en `75 D3` (`64/75 = 85.3%`)** y en el **consolidado de `95` preguntas (`74/95 = 77.9%`)** siendo **`31.4%` más rápido** que `4-LoRA`, pero demuestra que el `Verificador` base por sí solo rompe borradores correctos en `nuevas_20` (`N05`, `N11`, `N20`) y `sintesis` (`H17`, `H19`). No basta con apagar el LoRA del `Verificador`: hace falta un **`Verificador` LoRA v2 recalibrado**.
2. **Cómo recalibrar el dataset del `Verificador` v2:** combinar los aciertos del `Verificador` v1 en `N05`/`N11`/`N20`/`H22` (respetar abstenciones y borradores ya completos sin alucinar requisitos inexistentes) con ejemplos realistas de `Condiciones o límites: No aplica` válido en artículos simples, pares con error `P01` sutil en `Condiciones` y ejemplos de inversión aritmética/lógica (`H05`, `H06`), evitando el sobreajuste extremo (`eval_loss` cerca de `0.03`) y limitando la longitud de `<pensar>`.
3. **Refuerzo puntual en `Enrutador` y `Recuperador`:** incorporar casos de premisa falsa que mencionan un artículo real existente (`congelado_50:47, 48`) en el Enrutador, y trayectorias con búsqueda adicional previa a `suficiente` para fechas del Calendario (`N16`, `H03`), artículos transitorios (`N18`: `[RG-TRANS-002]` vs `[RG-ART-002]`) y requisitos cruzados (`C50:25`, `C50:36`, `N19`) en el Recuperador.
4. **Guardrail determinista ligero para `Redactor`:** verificar antes de cerrar si la línea literal `Fuente:` está presente (`congelado_50:7`, `congelado_50:8`) cuando el borrador ya contiene citas `[...]`.

---

## 7. Artefactos Generados y Reproducibilidad

- Script de auditoría y consolidación: [`scripts/generar_auditoria_multi.py`](scripts/generar_auditoria_multi.py)
- Resumen comparativo global: [`evaluacion/resumen_comparativo_global.json`](evaluacion/resumen_comparativo_global.json)
- Auditorías y CSVs auditados (`SHA-256` verificados sobre CSVs crudos de Colab):
  - `Multi-LoRA (4 agentes) nuevas_20`: [`auditoria_multi_lora_nuevas20.json`](evaluacion/auditoria_multi_lora_nuevas20.json) · [`resultados_multi_lora_nuevas20_auditados.csv`](evaluacion/resultados_multi_lora_nuevas20_auditados.csv)
  - `Ablación Red+Ver nuevas_20`: [`auditoria_ablacion_red_ver_nuevas20.json`](evaluacion/auditoria_ablacion_red_ver_nuevas20.json) · [`resultados_ablacion_red_ver_nuevas20_auditados.csv`](evaluacion/resultados_ablacion_red_ver_nuevas20_auditados.csv)
  - `Multi-LoRA (4 agentes) 75 D3`: [`auditoria_multi_lora_75.json`](evaluacion/auditoria_multi_lora_75.json) · [`resultados_multi_lora_75_auditados.csv`](evaluacion/resultados_multi_lora_75_auditados.csv)
  - `3-LoRA sin Verificador nuevas_20`: [`auditoria_sin_verificador_nuevas20.json`](evaluacion/auditoria_sin_verificador_nuevas20.json) · [`resultados_sin_verificador_nuevas20_auditados.csv`](evaluacion/resultados_sin_verificador_nuevas20_auditados.csv)
  - `3-LoRA sin Verificador 75 D3`: [`auditoria_sin_verificador_75.json`](evaluacion/auditoria_sin_verificador_75.json) · [`resultados_sin_verificador_75_auditados.csv`](evaluacion/resultados_sin_verificador_75_auditados.csv)
