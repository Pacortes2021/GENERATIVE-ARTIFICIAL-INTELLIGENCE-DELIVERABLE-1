# Deliverable 4 — Especialización Multi-LoRA por rol (`Qwen/Qwen3-4B`)

Continuación directa de Deliverables 1–3 sobre normativa de pregrado de Ingeniería UdeC (`corpus.json`: `173` unidades padre, `197` unidades y `201` fragmentos de búsqueda; evaluación sobre `75` preguntas oficiales: `congelado_50` + `dificil_25`, más `20` preguntas nuevas en `preguntas_nuevas_20.csv`), manteniendo **un único modelo base `Qwen/Qwen3-4B` cuantizado en 4 bits (NF4)** y el grafo multi-agente de Deliverable 3.

**Arquitectura oficial entregada (`3-LoRA`):**
- **Conmutación dinámica Multi-LoRA (`model.set_adapter()`):** `Enrutador`, `Recuperador` y `Redactor` activan su propio adaptador QLoRA (`r=16`, `alpha=32`) especializado por rol dentro del mismo modelo NF4.
- **Verificador aislado en Base (`model.disable_adapter()`):** mantiene pesos base íntegros (`98/98` llamadas OFF en las `75`, `32/32` OFF en `N20`, **`0` violaciones**), decisión respaldada empíricamente por las ablaciones `4-LoRA v1` (`58/75`) y `v2` (`56/75`).
- **Elección de agentes (`Choice of agent`):** En el diagnóstico de D3, `8/9` errores ya tenían evidencia `top-6` en el Redactor tras haber iterado `prompts/01--04` hasta saturar el prompting base en D3 v6 ([`RESUMEN_ABLACIONES.md`](../Deliverable%203/Deliverable3/resultados_ablaciones/RESUMEN_ABLACIONES.md)). Sin embargo, al fine-tunear **solo al Redactor** en D4 v2 (`60/75` en A100 `bf16` vs `62/75` Control Base), las trazas evidenciaron un cuello de botella de **eficiencia** previo (`373` llamadas en `75` y `132` en `N20` solo en el Recuperador). Incorporar adaptadores al `Enrutador` y al `Recuperador` responde a ese hallazgo y el ahorro medido (`-41,0%` llamadas) se atribuye al sistema conjunto **`3-LoRA`** (localizado en el rol Recuperador).
- **Respaldo de variante previa:** el enfoque anterior `Solo Redactor FT v2` (`60/75`) quedó respaldado íntegramente en la rama `backup/d4-solo-redactor` (`fdca700`).

**Reproducción rápida en Colab (`--solo-hf`, Pasos 1–4 en rama `main`):**
- **Demo en vivo (`H07`, Base vs `3-LoRA`):** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%204/D4_colab_video_demo.ipynb) · ejecuta Paso 1 (dependencias/clon), Paso 2 (verificación de manifiesto SHA-256 en HF y aislamiento Multi-LoRA), Paso 3 (`dificil_25:H07` lado a lado con `verbose=True`) y Paso 4 (auditoría de fallos `H03`, `H17`, `H06`).
- **Evaluación completa (`75` + `N20`):** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%204/D4_colab_evaluacion.ipynb) (`SOLO_HF = True`).

**Enlaces clave y adaptadores públicos verificados (`entrenamiento/manifest_adaptadores_hf.json`):**
- **Informe técnico (1 página, LaTeX):** [`documento/main.pdf`](documento/main.pdf) ([`main.tex`](documento/main.tex) + [`grafo_d4.tex`](documento/grafo_d4.tex))
- **Enunciado / Pauta oficial:** [`enunciado.pdf`](enunciado.pdf)
- **Adaptadores Hugging Face (acceso abierto, SHA-256 verificado contra los pesos evaluados):**
  - **Enrutador:** [`Pablox0333/qwen3-4b-enrutador-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-enrutador-udec-d4) · rev. `ab65a4f0b0e969d8e9c0d3975d06d6e1791afec7` · `sha256: 16fe1e460c6c4ced20e79a248d168702c3961647352ed29bcdb803f1d27946ff`
  - **Recuperador:** [`Pablox0333/qwen3-4b-recuperador-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-recuperador-udec-d4) · rev. `6bd665a314663f224ef3eb17823febbd9bc1d10c` · `sha256: 03e3d6e614f19021e2540ec0a586d710b339d5409d05363ed1a9f5ac3fb9e40b`
  - **Redactor:** [`Pablox0333/qwen3-4b-redactor-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4) · rev. `739b031acbd5feef2c49f946b94722712209bce0` · `sha256: 438a23664aab0457b060a42fb0eea77d6db82949459aa33280c36dcdb755b3c1`
- **Video demostrativo (≤ 3 min):** `[Pendiente: ensayar H07 y grabar con D4_colab_video_demo.ipynb]` — guion en [`video/GUION_VIDEO_D4.md`](video/GUION_VIDEO_D4.md) y visor en [`video/mostrar_demo_d4.py`](video/mostrar_demo_d4.py).

---

## Resumen de resultados (A100 `bf16` pareado vs corridas históricas T4)

Evaluación bajo la pauta estricta heredada de D2/D3 ([`LEEME_PAUTA.md`](../Deliverable%203/paquete_25_dificiles/LEEME_PAUTA.md), incluyendo Regla 2 y Regla 3 / `P01`). **Comparabilidad:** `Control Base (A100)` es exactamente el mismo sistema D3 v6 (código, prompts y pesos base) re-ejecutado en idéntico entorno **A100 40 GB `bf16`** y semillas `2026`; las filas `D1`–`D3` corresponden a corridas históricas en `Tesla T4 fp16`.

| Sistema / Control | Entorno | Orig. (50) | Dif. (25) | Tot. (75) | Nuevas (20) | Global (95) | Llamadas (`75 / 20`) | Tiempo (`75 / 20`) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| D1 Original (`greedy`, solo abst.) | T4 | 2 (4,0%) | --- | --- | --- | --- | --- | --- |
| Bas. Directo D2/D3 (`T=0,7`) | T4 `fp16` | 1 (2,0%) | 0 (0,0%) | 1 (1,3%) | --- | --- | 75 / --- | --- |
| RAG D2 (E5) | T4 `fp16` | 40 (80,0%) | 16 (64,0%) | 56 (74,7%) | --- | --- | 75 / --- | --- |
| Multi-agente D3 Base (v6) | T4 `fp16` | **46 (92,0%)** | **20 (80,0%)** | **66 (88,0%)** | --- | --- | 711 / --- | 137,6 min / --- |
| Control Base D4 (`= D3 v6`, `LoRA OFF`) | A100 `bf16` | **46 (92,0%)** | 16 (64,0%) | 62 (82,7%) | **11 (55,0%)** | 73 (76,8%) | 658 / 254 | 75,3 min / 32,8 min |
| Solo Redactor v2 (`1-LoRA`) | A100 `bf16` | 43 (86,0%) | 17 (68,0%) | 60 (80,0%) | 10 (50,0%) | 70 (73,7%) | 648 / 212 | 75,7 min / 25,1 min |
| **D4 Oficial (`3-LoRA`: Enr+Rec+Red FT, Ver Base)** | **A100 `bf16`** | **46 (92,0%)** | **18 (72,0%)** | **64 (85,3%)** | 10 (50,0%) | **74 (77,9%)** | **388 / 118** | **72,6 min / 30,2 min** |
| *Ablación 4-LoRA v1 (Verificador FT)* | A100 `bf16` | 40 (80,0%) | 18 (72,0%) | 58 (77,3%) | **14 (70,0%)** | 72 (75,8%) | 493 / 138 | --- |
| *Ablación 4-LoRA v2 (Verificador FT)* | A100 `bf16` | 40 (80,0%) | 16 (64,0%) | 56 (74,7%) | 12 (60,0%) | 68 (71,6%) | 486 / 147 | --- |

**Lectura estadística y operativa honesta (`evaluacion/resumen_comparativo_d4.json`):**
- **McNemar no detectó diferencia de exactitud frente al Control Base:** el propio sistema base varía `66/75 -> 62/75` entre T4 y A100 (mayor que la diferencia `+2` observada). Frente a `Control Base A100`, `3-LoRA` gana `5` / pierde `3` en `75` (`McNemar p = 0,7266`), pierde **`-1`** en `nuevas_20` (`10/20` vs `11/20`: gana `N09, N12`; pierde `N05, N06, N20`), y marca `74/95` vs `73/95` (`7/6`, `McNemar p = 1,0`). Además, `4-LoRA v1` alcanzó `14/20` en `nuevas_20` (aunque cayó a `58/75` por sesgo anti-`"No aplica"`), y dado que `3-LoRA` se seleccionó entre `5` variantes observando estas `95` preguntas, `nuevas_20` ya no actúa como test ciego estricto entre arquitecturas (sí quedó fuera de los datos de entrenamiento). Todos los `P7` y `P8` cumplen bien `LEEME_PAUTA.md` (`64/75`, con omisión menor de la línea literal `Fuente:` manteniendo citas inline válidas).
- **Ahorro real de llamadas (`-41,0%` en `75`, `-53,5%` en `N20`) y mecanismos reales:**
  - **`Recuperador` LoRA:** el recorte se atribuye al sistema `3-LoRA` y se localiza en el rol Recuperador, que aprendió **cuándo detenerse** tras la búsqueda base automática: emite `suficiente` como primera acción en **`65/75`** preguntas (`traza[2]`; o **`66/75`** tomando la primera llamada LLM real incluyendo `P50`, que realiza un chequeo `existe` previo del Enrutador), con `21` búsquedas propias frente a `157` del Control Base, recortando sus llamadas **`387 -> 117` (`-69,8%`)**. Como contrapartida, provoca **`6` cortes prematuros** en preguntas compuestas (`P25, P36, H03; N16, N18, N19`). El tiempo total baja solo `-3,7%` (`75,3 -> 72,6 min`) porque el Redactor domina la generación de tokens.
  - **`Enrutador` LoRA:** el campo `documentos` no filtra `Orquestador.recuperar()` (solo pasa como contexto en el prompt del Recuperador), y el `62,4%` (`131/210`) del train marca solo `["RG"]` (`49/75` en evaluación), por lo que no se atribuye corrección de rutas por filtrado documental.
  - **Comparativa concreta en `dificil_25:H07`:** en el **benchmark A100 archivado** (`comparativa_base_vs_3lora.json`), Control Base cae en `3` ciclos / `13` llamadas (`177,44 s`): en el ciclo 2 el Redactor Base llegó a calcular bien `10,5 > 10`, pero el **Verificador Base lo rechazó falsamente** (*"la evidencia no respalda este cálculo"*) forzando la abstención en el ciclo 3; `Solo Redactor` tarda `2` ciclos (`89,37 s` en eval / `89,03 s` pareado); `3-LoRA` resuelve en **`1` ciclo / `4` llamadas (`53,84 s`)**. En la **reproducción independiente `--solo-hf`** (`comparativa_reproduccion_hf.json`), Base mantuvo `3` ciclos / `13` llamadas (`172,56 s`) y `3-LoRA` resolvió en **`1` ciclo / `6` llamadas (`59,91 s`)** (fórmula en `RG-ART-028` a) y umbral en `RI-FI-ART-014` b)).
- **Auditoría transparente de fallos:**
  - Los **`11` fallos de `75`** (`Redactor: 6`, `Recuperador: 3`, `Verificador Base: 2`) están documentados con trazas completas en [`evaluacion/casos_fallo_y_regresion_3lora.json`](evaluacion/casos_fallo_y_regresion_3lora.json) (incluyendo `H17`, donde ciclo 1 tenía redacción ambigua `"mínima de 80% ... (máximo 80%)"` que `3` rechazos del Verificador Base empujaron a invertir en ciclo 3, y `H06`).
  - Las trazas completas de los **`10` fallos de `nuevas_20`** (`Redactor: 4`, `Verificador Base: 3`, `Recuperador: 3`) se almacenan en [`evaluacion/trazas_3lora_nuevas20.json`](evaluacion/trazas_3lora_nuevas20.json) y [`evaluacion/auditoria_3lora_nuevas20.json`](evaluacion/auditoria_3lora_nuevas20.json).

---

## Datasets por rol (`725` pares), alcance antifuga, autoría y entrenamiento QLoRA

Construidos por rol (`seed=202604`) respetando `prompts/01--03` bit a bit con **`0` coincidencias** con las `61` unidades excluidas (`D3-75`: `40`, `preguntas_nuevas_20.csv`: `21`), `0` QIDs y `0` ejemplos truncados *(nota transparente: el prompt `01_enrutador.txt` heredado bit a bit desde D3 v6 incluye literalmente a `P36` como ejemplo few-shot, caso en el que `3-LoRA` aún falla)*:

| Agente | Train / Val | Unid. | Procedencia exacta de cada salida correcta | Entrenamiento y `eval_loss` |
|---|---:|---:|---|---|
| **Enrutador** | `210 / 36` (`246`) | `97/197` | `30` train + `6` val escritos a mano en `enrutador_bloques.py` (asistido por **Gemini 4 Argon** vía Antigravity), más `210` etiquetas por reglas (`inferir_tipo_y_subconsultas_spec`, `inferir_documentos_spec`). | A100 `bf16`: `9,88 min / 105` pasos · `1,066 -> 0,123` (`step 80`) |
| **Recuperador** | `230 / 39` (`269`) | `109/197` | Trayectorias ReAct sintetizadas determinísticamente por `recuperador_bloques.py` replicando a `Orquestador.recuperar()` (`_numero_permitido`). | A100 `bf16`: `10,43 min / 117` pasos · `1,729 -> 0,186` (`step 117`) |
| **Redactor** | `180 / 30` (`210`) | `112/197` | Especificaciones curadas a mano por el equipo en `dataset_blocks/` con asistencia de **Gemini 4 Argon** (vía Antigravity), validadas contra `corpus.json` (`74/210` con `No aplica`). | T4 `fp16`: `52,38 min / 90` pasos · `1,601 -> 0,516` (`step 90`) |
| **Total D4** | **`620 / 105` (`725`)** | **`0/61` excl.** | Revisión manual (`50/50` **aprobados y firmados el `2026-11-19`** por Álvaro Contreras y Pablo Cortés): `30` en [`MUESTRA_REVISION_MANUAL.md`](datos/MUESTRA_REVISION_MANUAL.md) ([firmas](datos/revision_manual_firmas.csv)) + `20` en [`MUESTRA_REVISION_MANUAL_ENRUTADOR_RECUPERADOR.md`](datos/MUESTRA_REVISION_MANUAL_ENRUTADOR_RECUPERADOR.md) ([firmas](datos/revision_manual_firmas_agentes.csv)). | Gráfica en [`entrenamiento/loss_curves_3agentes.png`](entrenamiento/loss_curves_3agentes.png) |

---

## Comandos de reproducción offline y pasos finales de cierre

```bash
# 1. Verificar hashes publicados en Hugging Face Hub vs manifest_adaptadores_hf.json
python3 "Deliverable 4/scripts/publicar_adaptadores_hf.py" --verificar-manifest

# 2. Reconstruir datasets antifuga (725 pares) y reporte consolidado
python3 "Deliverable 4/scripts/construir_dataset.py"
python3 "Deliverable 4/scripts/construir_datasets_agentes.py"
python3 "Deliverable 4/scripts/generar_reporte_3lora.py"

# 3. Suite completa de tests offline
python3 -m unittest discover -s "Deliverable 4/tests" -v

# 4. Compilar grafo TikZ e informe técnico de 1 página
cd "Deliverable 4/documento" && tectonic grafo_d4.tex && tectonic main.tex
```

**Estado de verificación y único paso pendiente de cierre en `main`:**
1. **Reproducido desde Hugging Face en Colab A100 (`--solo-hf`, sin Drive) — Completado:** corrida de verificación en [`D4_colab_evaluacion.ipynb`](D4_colab_evaluacion.ipynb) archivada en [`evaluacion/comparativa_reproduccion_hf.json`](evaluacion/comparativa_reproduccion_hf.json) (`7` casos pareados Base vs `3-LoRA`, confirmando descarga limpia de los `3` adaptadores y `H07` resuelto en `1` ciclo / `6` llamadas / `59,91 s` frente a `3` ciclos / `13` llamadas / `172,56 s` en Base).
2. **Firmas humanas (`50/50` casos) — Completado (`2026-11-19`):** `30` casos del Redactor en [`datos/revision_manual_firmas.csv`](datos/revision_manual_firmas.csv) y `20` del Enrutador/Recuperador en [`datos/revision_manual_firmas_agentes.csv`](datos/revision_manual_firmas_agentes.csv) aprobados y firmados por **Álvaro Contreras y Pablo Cortés** (`0` pendientes).
3. **Ensayar y grabar video (≤ 3 min) — Único pendiente:** probar `H07` en [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb) (`MONTAR_DRIVE = False`, rama `main`), grabar y pegar el enlace público en los READMEs y `main.tex` (recompilando `main.pdf`).
