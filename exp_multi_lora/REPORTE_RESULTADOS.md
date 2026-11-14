# Reporte de Resultados — Experimento Multi-LoRA (`exp_multi_lora`)

**Rama:** `exp/multi-lora-todos` · **Modelo base:** `Qwen/Qwen3-4B` (QLoRA NF4 4-bit, `torch.bfloat16`) · **Hardware:** `NVIDIA A100-SXM4-40GB` (`42.41 GB` VRAM)  
**Criterio de auditoría:** estricta contra el corpus fuente y [`LEEME_PAUTA.md`](../Deliverable%203/paquete_25_dificiles/LEEME_PAUTA.md) (reglas 1–8, incluyendo excepciones Regla 2 y precedentes Regla 3 / `P01`).

---

## 1. Resumen Ejecutivo

El experimento evaluó si entrenar adaptadores QLoRA independientes para los cuatro roles del sistema (`enrutador`, `recuperador`, `redactor` fijado al checkpoint D4 v2 y `verificador`) dentro de **una sola instancia NF4 de `Qwen/Qwen3-4B`** supera a `Solo Redactor D4` y a `Control Base D4` bajo idénticos prompts v6, parámetros de decodificación (`T=0.7`, `top_p=0.8`, `top_k=20`, `enable_thinking=False`) y semillas derivadas.

| Condición | `congelado_50` | `dificil_25` | **Benchmark `75` D3** | **`nuevas_20` (no vistas)** | **Consolidado `95`** | Llamadas totales (`75` / `N20`) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control Base D4** (0 LoRA) | **46/50 (92.0%)** | 16/25 (64.0%) | **62/75 (82.7%)** | 11/20 (55.0%) | **73/95 (76.8%)** | 658 / 254 |
| **Solo Redactor D4** (1 LoRA) | 43/50 (86.0%) | 17/25 (68.0%) | 60/75 (80.0%) | 10/20 (50.0%) | 70/95 (73.7%) | 648 / 212 |
| **Ablación Red+Ver** (2 LoRAs) | — | — | — | 9/20 (45.0%) | — | — / 190 |
| **Multi-LoRA (4 agentes)** | 40/50 (80.0%)\* | **18/25 (72.0%)** | 58/75 (77.3%)\* | **14/20 (70.0%)** | 72/95 (75.8%) | **493 / 138** |

> \* **Nota de transparencia (`congelado_50:8`):** el contenido jurídico y ambas citas inline (`[RG-ART-034] [RI-FI-ART-026]`) son correctos y evitan el fallo P01 de `Solo Redactor D4`, pero omiten la tercera línea literal `Fuente:` (`formato_3_lineas_ok=False`). Bajo exigencia estricta de las 3 líneas literales, la cifra pasaría a `39/50` (`78.0%`) y `57/75` (`76.0%`).

**Conclusiones principales:**

1. **Generalización difícil (`+20 pp` en `nuevas_20` vs `Solo Redactor` y máximo histórico en `dificil_25`):** Multi-LoRA alcanza **`14/20` (`70.0%`)** en `nuevas_20` (`+4` respecto a `Solo Redactor` y `+3` respecto a `Control Base`) y **`18/25` (`72.0%`)** en `dificil_25`. La ablación `Red+Ver` (`9/20 = 45.0%`) confirma que el salto de generalización proviene de **`enrutador` + `recuperador`** trabajando juntos.
2. **Eficiencia de recuperación sin fallbacks:** las llamadas del `Recuperador` bajan **`-51.2%`** en `75 D3` (`373 -> 182`) y **`-63.6%`** en `nuevas_20` (`132 -> 48`), los tokens de entrada caen **`-15.3%`** y **`-20.3%`**, y tanto los `fallbacks` del enrutador como las citas inexistentes o fuera de evidencia quedan en **`0`** sobre las `95` preguntas.
3. **El `Verificador` LoRA es el cuello de botella de precisión en `congelado_50` y de latencia:** su sobre-especialización (`eval_loss=0.0344`) introduce dos sesgos opuestos —rechazos innecesarios ante `Condiciones o límites: No aplica` (`17/17` rechazadas en `75 D3` eran ya correctas) y aprobaciones permisivas de borradores bien formateados con errores sutiles (`17/17` fallos en `75 D3` fueron aprobados). Además, conmutar 4 adaptadores reduce el throughput de salida de `8.93` (`Solo Redactor`) y `12.67` (`Control Base`) a `6.79 tok/s`.

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

### 2.3 Verificación de aislamiento cruzado entre los 4 adaptadores

La prueba de logits previa a la inferencia en A100 confirmó que `model.set_adapter(rol)` conmuta realmente los pesos activos sin fugas ni colapsos:

- **`max_abs_diff_vs_base`:** `enrutador=18.0`, `recuperador=16.375`, `redactor=19.125`, `verificador=16.625`.
- **`max_abs_diff_cruzada` (6 pares):** `4.5625` (`enrutador vs redactor`), `4.689034` (`enrutador vs recuperador`), `4.695312` (`redactor vs verificador`), `5.0625` (`enrutador vs verificador`), `5.15625` (`recuperador vs redactor`), `5.734375` (`recuperador vs verificador`).

---

## 3. Desempeño por Categoría y Comparativa Pareada

### 3.1 Desglose en `nuevas_20` (4 condiciones)

| Categoría | Total | Control Base D4 | Solo Redactor D4 | Ablación Red+Ver | Multi-LoRA (4 agentes) |
| --- | :---: | :---: | :---: | :---: | :---: |
| `factual` | 4 | 3 | **4** | 3 | 3 |
| `abstencion` | 2 | **2** | 1 | **2** | **2** |
| `calculo` | 2 | **1** | 0 | 0 | 0 |
| `condicional` | 4 | 1 | 2 | 1 | **3** |
| `cruce` | 3 | 2 | 2 | 2 | **3** |
| `multi_salto` | 1 | **1** | **1** | **1** | **1** |
| `colision_lexica` | 1 | 0 | 0 | 0 | 0 |
| `negacion_excepcion` | 1 | **1** | 0 | 0 | **1** |
| `sintesis` | 1 | 0 | 0 | 0 | **1** |
| `premisa_falsa` | 1 | 0 | 0 | 0 | 0 |
| **Total estricto** | **20** | **11 (55.0%)** | **10 (50.0%)** | **9 (45.0%)** | **14 (70.0%)** |
| **Núcleo (sin P01)** | **20** | — | — | **11 (55.0%)** | **15 (75.0%)** |

- **Pareado Multi-LoRA vs Solo Redactor D4 (`nuevas_20`):** balance neto **`+4`** (`gana Multi-LoRA`: `N05, N08, N12, N17, N18`; `gana Solo Redactor`: `N01`; `9` empates en acierto, `5` empates en fallo: `N06, N07, N10, N16, N19`).
- **Pareado Multi-LoRA vs Control Base D4 (`nuevas_20`):** balance neto **`+3`** (`gana Multi-LoRA`: `N09, N11, N12, N18`; `gana Control Base`: `N06`).

### 3.2 Desglose en el Benchmark `75` D3 (`congelado_50` + `dificil_25`)

| Categoría | Total | Control Base D4 | Solo Redactor D4 | Multi-LoRA (4 agentes) |
| --- | :---: | :---: | :---: | :---: |
| `factual` | 10 | **10** | 8 | 9 |
| `numerica` | 10 | 9 | **10** | 7 |
| `condicional` | 10 | **9** | 7 | 7 |
| `cruce` | 10 | 9 | 9 | **10** |
| `abstencion` | 10 | **9** | **9** | 7 |
| `multi_salto` | 4 | **3** | 1 | 2 |
| `calculo` | 4 | 2 | **3** | 1 |
| `colision_lexica` | 5 | 3 | **4** | 3 |
| `negacion_excepcion` | 3 | **3** | **3** | **3** |
| `sintesis` | 5 | 2 | 4 | **5** |
| `premisa_falsa` | 4 | 3 | 2 | **4** |
| **Total `75` D3** | **75** | **62 (82.7%)** | **60 (80.0%)** | **58 (77.3%)\*** |
| `congelado_50` | 50 | **46 (92.0%)** | 43 (86.0%) | 40 (80.0%)\* |
| `dificil_25` | 25 | 16 (64.0%) | 17 (68.0%) | **18 (72.0%)** |

- **Pareado Multi-LoRA vs Solo Redactor D4 (`75 D3`):** balance neto **`-2`** (`gana Multi-LoRA` en `8`: `congelado_50:{5, 8, 36, 45}`, `dificil_25:{H02, H21, H22, H25}`; `gana Solo Redactor` en `10`: `congelado_50:{6, 11, 12, 16, 46, 47, 48}`, `dificil_25:{H05, H07, H09}`).
- **Pareado Multi-LoRA vs Control Base D4 (`75 D3`):** balance neto **`-4`** (`gana Multi-LoRA` en `7`: `congelado_50:{36, 43}`, `dificil_25:{H18, H19, H22, H24, H25}`; `gana Control Base` en `11`).

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

### 4.2 El doble filo del `Verificador` LoRA (matriz de confusión interna)

| Corrida | Aprobadas (acierta / falla estricto) | Rechazadas tras 3 ciclos (acierta / falla) | Precisión cuando aprueba | Acierto en rechazadas |
| --- | :---: | :---: | :---: | :---: |
| **`Red+Ver` (`nuevas_20`)** | `18` (`7` / `11`) | `2` (`2` / `0`) | `38.9%` (`7/18`) | **`100.0%` (`2/2`)** |
| **`Multi-LoRA` (`nuevas_20`)** | `14` (`10` / `4`) | `6` (`4` / `2`) | `71.4%` (`10/14`) | `66.7%` (`4/6`) |
| **`Multi-LoRA` (`75 D3`)** | `58` (`41` / `17`) | `17` (`17` / `0`) | `70.7%` (`41/58`) | **`100.0%` (`17/17`)** |

La matriz revela una **inversión de señal** respecto al objetivo del Verificador:

1. **Sí corrige rechazos rígidos del Verificador base en umbrales/inexistencias:** en `dificil_25:H22` aprueba en 1 ciclo la refutación válida (`4,0` en lugar de `4,5`), superando a Control Base y Solo Redactor; lo mismo ocurre en `nuevas_20:N05` (abstención aprobada en 1 ciclo).
2. **Hipersensibilidad a `Condiciones o límites: No aplica`:** entrenado con baja entropía (`eval_loss=0.0344`) sobre ejemplos sintéticos donde `No aplica` suele señalizarse como omisión de excepción, rechaza borradores ya correctos (`17/17` en `75 D3`). Al forzar ciclos 2–3 para “añadir condiciones”, induce mutaciones dañinas del Redactor: en `Red+Ver` destruye `N01` y `N09` (causando el `9/20`), y en `Multi-LoRA 75` destruye `congelado_50:28` (que en ciclo 2 estaba correcto) e introduce ruido P01.
3. **Permisividad ante errores semánticos en borradores bien formateados:** en `75 D3`, **los `17` fallos estrictos (`17/17`) habían sido aprobados por el Verificador**. Deja pasar inversiones aritméticas (`H05`: pesos `40/60` invertidos), inversiones lógicas (`H06`: `9,5 < 10 -> "No cae en baja"`), atribuciones cruzadas `P01` (`N06`, `N10`, `congelado_50:12`, `H07`, `H12`) y respuestas que omiten refutar premisas inexistentes (`congelado_50:46, 47, 48`).

### 4.3 Causas raíz de fallo consolidadas

- **`Multi-LoRA nuevas_20` (`6` fallos):** `redactor: 4` (`N01`, `N06`, `N07`, `N10`), `recuperador: 2` (`N16`, `N19`).
- **`Ablación Red+Ver nuevas_20` (`11` fallos):** `redactor: 7` (`N06`, `N07`, `N08`, `N10`, `N16`, `N17`, `N18`), `verificador: 2` (`N01`, `N09`), `enrutador: 2` (`N12`, `N19`).
- **`Multi-LoRA 75 D3` (`17` fallos):** `redactor: 12` (`C50:{6,11,12,16,26,46}`, `H04, H05, H06, H07, H09, H12`), `recuperador: 2` (`C50:25`, `H03`), `enrutador: 2` (`C50:47, 48`), `verificador: 1` (`C50:28`).

*(Solo los fallos con `solo_condicion_p01=True`: `N06` en `Multi-LoRA nuevas_20`, `N17, N18` en `Red+Ver`, y `C50:12, C50:28, H07, H09` en `Multi-LoRA 75` tienen la respuesta central correcta pero violan la Regla 3/P01 en la línea `Condiciones o límites`.)*

---

## 5. Eficiencia, Telemetría y Paradoja de Latencia

| Métrica | `Control Base` (`75` / `N20`) | `Solo Redactor` (`75` / `N20`) | `Red+Ver` (`N20`) | `Multi-LoRA 4` (`75` / `N20`) |
| --- | :---: | :---: | :---: | :---: |
| Ciclos promedio | `1.31` / `1.80` | `1.33` / `1.50` | `1.40` | `1.57` / `1.75` |
| Llamadas totales | `658` / `254` | `648` / `212` | `190` | **`493`** / **`138`** |
| Llamadas `Recuperador` | `387` / `162` | `373` / `132` | `114` | **`182`** / **`48`** |
| Llamadas `Redactor` | `98` / `36` | `100` / `30` | `28` | `118` / `35` |
| Tokens entrada totales | `589,849` / `227,634` | `586,425` / `184,073` | `166,985` | **`496,739`** / **`146,735`** |
| Tokens salida totales | `55,627` / `24,971` | `39,496` / `13,427` | `13,040` | `43,043` / `14,912` |
| Tiempo total CSV (s) | `4520.5` / `1970.2` | `4541.2` / `1504.1` | `1692.9` | `6346.3` / `2197.9` |
| Throughput salida (`tok/s`) | **`12.31`** / **`12.67`** | `8.70` / `8.93` | `7.71` | `6.79` / `6.79` |

Aunque `Multi-LoRA` ahorra hasta **`-34.9%`** de llamadas y **`-20.3%`** de tokens de entrada en `nuevas_20` (`-23.9%` llamadas y `-15.3%` tokens entrada en `75 D3`), el tiempo de reloj crece **`+39.8%`** en `75 D3` y **`+46.1%`** en `nuevas_20` frente a `Solo Redactor`:

1. **Costo de conmutación Multi-LoRA (`set_adapter`):** mantener 4 adaptadores `r=16` en los 7 módulos lineales y alternar entre ellos en cada salto de agente hace descender progresivamente el throughput de salida de `12.31–12.67 tok/s` (0 LoRA) a `8.70–8.93` (1 LoRA), `7.71` (2 LoRAs) y `6.79 tok/s` (4 LoRAs).
2. **Ciclos extra inducidos por el Verificador:** aunque el `Recuperador` ahorra cientos de llamadas cortas (`182` vs `373`), el `Verificador` rechaza `17` preguntas válidas de `75 D3`, añadiendo `+18` llamadas del `Redactor` (`118` vs `100`), que es el rol con prompts más largos (`161,176` `in_tok` / `3399.89 s`, más de la mitad del tiempo total) y añadiendo además `11,922` `out_tok` de razonamiento `<pensar>` del propio Verificador (`~101 tok/llamada`).

---

## 6. Lecciones para una Eventual Iteración v2

1. **Evaluar la configuración sin `verificador` LoRA (`enrutador + recuperador + redactor`, `--agentes enrutador,recuperador,redactor`):** combina la ganancia demostrada en recuperación y cruces complejos (`N20: 70%`, `H25: 72%`, `-51%` a `-64%` llamadas de búsqueda) sin los falsos rechazos por `No aplica`, sin la regresión de `congelado_50` y con menor overhead de adaptadores y `<pensar>`.
2. **Recalibrar el dataset del `Verificador`:** añadir más ejemplos negativos realistas con `Condiciones o límites: No aplica` válido en artículos simples, pares con error `P01` sutil en `Condiciones` y ejemplos de inversión aritmética/lógica (`H05`, `H06`), evitando sobreajuste (`eval_loss` cerca de `0.03`).
3. **Refuerzo puntual en `Enrutador` y `Recuperador`:** incorporar casos de premisa falsa que mencionan un artículo real existente (`congelado_50:47, 48`) en el Enrutador, y trayectorias con búsqueda adicional previa a `suficiente` para fechas del Calendario (`N16`, `H03`) y requisitos cruzados (`C50:25`, `N19`) en el Recuperador.
4. **Guardrail determinista ligero para `Redactor`:** verificar antes de cerrar si la línea `Fuente:` está presente (`congelado_50:8`) cuando el borrador ya contiene citas `[...]`.

---

## 7. Artefactos Generados y Reproducibilidad

- Script de auditoría y consolidación: [`scripts/generar_auditoria_multi.py`](scripts/generar_auditoria_multi.py)
- Resumen comparativo global: [`evaluacion/resumen_comparativo_global.json`](evaluacion/resumen_comparativo_global.json)
- Auditorías y CSVs auditados (`SHA-256` verificados sobre CSVs crudos de Colab):
  - `Multi-LoRA nuevas_20`: [`auditoria_multi_lora_nuevas20.json`](evaluacion/auditoria_multi_lora_nuevas20.json) · [`resultados_multi_lora_nuevas20_auditados.csv`](evaluacion/resultados_multi_lora_nuevas20_auditados.csv)
  - `Ablación Red+Ver nuevas_20`: [`auditoria_ablacion_red_ver_nuevas20.json`](evaluacion/auditoria_ablacion_red_ver_nuevas20.json) · [`resultados_ablacion_red_ver_nuevas20_auditados.csv`](evaluacion/resultados_ablacion_red_ver_nuevas20_auditados.csv)
  - `Multi-LoRA 75 D3`: [`auditoria_multi_lora_75.json`](evaluacion/auditoria_multi_lora_75.json) · [`resultados_multi_lora_75_auditados.csv`](evaluacion/resultados_multi_lora_75_auditados.csv)
