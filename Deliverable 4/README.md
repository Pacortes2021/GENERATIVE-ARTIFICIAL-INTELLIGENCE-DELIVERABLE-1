# Deliverable 4 — Especialización QLoRA del Agente Redactor (`Qwen/Qwen3-4B`)

Continuación directa de Deliverables 1–3 sobre normativa de pregrado de Ingeniería UdeC (`corpus.json`: 173 unidades padre, 197 unidades y 201 fragmentos de búsqueda; evaluación oficial sobre 75 preguntas: `congelado_50` + `dificil_25`), manteniendo `Qwen/Qwen3-4B` (4 bits NF4) y el sistema de cuatro agentes de Deliverable 3.

- **Informe técnico (1 página, LaTeX):** [`documento/main.pdf`](documento/main.pdf) (fuente: [`documento/main.tex`](documento/main.tex) y grafo [`documento/grafo_d4.tex`](documento/grafo_d4.tex))
- **Enunciado / Pauta oficial:** [`enunciado.pdf`](enunciado.pdf)
- **Adaptador público en Hugging Face:** [`Pablox0333/qwen3-4b-redactor-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4) *(pesos QLoRA v2 publicados tras re-entrenar en T4)*
- **Video demostrativo (≤ 3 min, enlace abierto):** `[Pendiente: pegar enlace público tras revisión de Álvaro y grabación en vivo]` — guía y notebook en vivo en [`video/GUION_VIDEO_D4.md`](video/GUION_VIDEO_D4.md), [`video/mostrar_demo_d4.py`](video/mostrar_demo_d4.py) y [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb)

> **Estado actual del repositorio (rama `deliverable-4`):** Entrenamiento **v2 (`Tesla T4`)**, evaluación **v2 completa (`A100-SXM4-40GB bf16`, 4 corridas)** y auditoría v2 sincronizadas para revisión par de Álvaro Contreras y grabación del video en vivo antes del merge a `main`.

---

## Resumen de resultados (corrida v2 en A100 `bf16` sobre 75 oficiales + 20 nuevas)

Evaluación bajo la pauta estricta heredada de D2/D3 ([`LEEME_PAUTA.md`](../Deliverable%203/paquete_25_dificiles/LEEME_PAUTA.md), incluyendo Regla 3 / precedente `P01`). En la corrida **v2** (`FT` y `--solo-base` en idéntico entorno A100 `bf16`), `Enrutador`, `Recuperador` y `Verificador` ejecutaron con `model.disable_adapter()` (`0` violaciones LoRA en `100/100` Redactor ON y `548/548` Base OFF en las 75 oficiales, y `30/30` ON / `182/182` OFF en `nuevas_20`; `max_abs_logit_diff = 13.5625`).

| Sistema / Control | Orig. (50) | Dif. (25) | Total (75) | Nuevas (20) | Llam./q (75 / 20) | Entorno |
|---|---:|---:|---:|---:|---:|---|
| Directo D1 (referencia 0-shot) | 1 (2,0%) | 0 (0,0%) | 1 (1,3%) | --- | 1,0 | Mismo modelo base (T4) |
| RAG D2 (E5) | 40 (80,0%) | 16 (64,0%) | 56 (74,7%) | --- | 1,0 | Misma recuperación (T4) |
| Multi-agente D3 Base (v6) | **46 (92,0%)** | **20 (80,0%)** | **66 (88,0%)** | --- | 9,5 (`711`) | Sesión Colab D3 (T4, `137,6 min`) |
| Control Base D4 (`--solo-base`) | **46 (92,0%)** | 16 (64,0%) | 62 (82,7%) | **11 (55,0%)** | 8,77 (`658`) / 12,70 (`254`) | A100 `bf16` (`75,34 min` / `32,84 min`) |
| **Multi-agente D4 (`Redactor` FT v2)** | 43 (86,0%) | 17 (68,0%) | 60 (80,0%) | 10 (50,0%) | **8,64 (`648`) / 10,60 (`212`)** | A100 `bf16` (`75,69 min` / `25,07 min`) |

> **Criterio simétrico:** Excluyendo únicamente desvíos `P01` en Condiciones (`congelado_50:5` y `:8`), `FT v2` marca `62/75` (`82,7%`) de núcleo. En `nuevas_20` (20 preguntas inéditas con `0%` solapamiento de unidades), `FT v2` reduce llamadas en **`-16,5%`** (`212` vs `254`) y latencia total en **`-23,7%`** (`25,07 min` vs `32,84 min`), con `1` fallback y `0` citas inexistentes/fuera de evidencia.

- **Entrenamiento QLoRA v2 (`entrenamiento/`):** `Tesla T4` (`15,64 GB` VRAM, `float16`), `52,38 min` (`3142,78 s`, `90` pasos, `3,0` épocas, `0` ejemplos truncados a `4096` tokens): `eval_loss` bajó de `1,6006` (paso 0) a **`0,5164`** (paso 90), `train_loss` final agregada = **`0,6261`**.
- **Balance v2 frente a D3 v6, v1 y Control Base (`75` oficiales):**
  - Corrige **`5/9` fallos de D3** (`P13, P24, H07, H14, H18`) y recupera **`6` errores de v1** (`P6, P7, P10, P31, H18, H19`).
  - Eleva `Condiciones o límites: No aplica` de `0/75` (v1) a **`37/75`** (`Control Base: 12/75`) y **`12/20`** en `nuevas_20` (`Control Base: 0/20`).
  - Frente a **Control Base A100** en el mismo entorno, `FT v2` gana **`6` casos** (`P11, P43, H07, H18, H19, H24`, `+1` en `dificil_25`), **`4/6 vs 2/6`** en [`evaluacion/comparativa_base_vs_finetuned.json`](evaluacion/comparativa_base_vs_finetuned.json) (`dificil_25:H07`: `42/4 = 10,5` en `2` ciclos / `89,03 s` vs Base abstención `3` ciclos / `173,54 s`; `H14` en `1` ciclo / `58,51 s`) y **`2/3 vs 1/3`** en [`evaluacion/comparativa_nuevas20.json`](evaluacion/comparativa_nuevas20.json) (`N01`).
  - **Por categoría vs D3 v6:** mejora `numerica` (`9 → 10/10`), `negacion_excepcion` (`2 → 3/3`) y `sintesis` (`3 → 4/5`); mantiene `cruce` (`9/10`) y `calculo` (`3/4`); retrocede en `multi_salto` (`3 → 1/4`), `premisa_falsa` (`4 → 2/4`), `factual` (`10 → 8/10`, `10/10` en núcleo), `condicional` (`8 → 7/10`), `abstencion` (`10 → 9/10`) y `colision_lexica` (`5 → 4/5`).
- **Auditoría de fallos v2 y cuello de botella ([`evaluacion/casos_fallo_y_regresion.json`](evaluacion/casos_fallo_y_regresion.json)):**
  - **`Verificador` base degrada borradores válidos (`H04, H06, H21, H22` y `N05`):** En los **5 casos**, `Redactor FT v2` acertó en el ciclo 1 (`38/4 = 9,5` en `H06`, `4,0` en `H22`, `[RG-ART-049]` en `H04`, mínimo 8 en `H21`, Art. 6° en `N05`), pero el `Verificador` base (`LoRA OFF`) rechazó el borrador e indujo errores en ciclos 2–3. En las 75 preguntas, `12/68` aprobaciones fueron incorrectas y **`4/7` rechazos** recayeron sobre salidas válidas (`P38, P47, P48, P50`).
  - **`Recuperador` y `Enrutador` base (`H03, N12, N19`):** `CAL-2026-S2-02` sigue fuera del `top-6` en `H03`; en `nuevas_20`, el `Enrutador` filtra solo `['RI-FI']` excluyendo `RG` en `N12` (`0` fuentes) y `N19`.
  - **Residuales del Redactor:** `No aplica` omite excepciones requeridas en `P36`/`H25`; `P25`/`P26`/`P28` y `H12` (`10 días` de Baja Académica); alucinación `"simulink"` + omisión de `Fuente:` en `H02`; aritmética de fechas en `N06`/`N07` y desvíos `P01`/lectura en `P5, P8, P45, N08, N10, N16, N17, N18`.

---

## Estructura del entregable (v2 completa)

- `prompts/`: prompts versionados por agente heredados bit a bit desde Deliverable 3 v6 (`01_enrutador.txt`, `02_recuperador.txt`, `03_redactor.txt`, `04_verificador.txt`).
- `scripts/`:
  - `diagnostico_d3.py`: diagnostica `top-6` y origen de los 9 errores de D3 (`diagnostico/`).
  - `dataset_blocks/` (`reglas_v2.py`, `bloques_1_2.py`, `bloques_3_4.py`, `bloques_5_6.py`) y `construir_dataset.py`: generan el **dataset v2 (`180 train / 30 val`)** desde fragmentos literales de `corpus.json` con **asistencia de Antigravity (IA)**, imponiendo `0` solapamiento con las `40` unidades eval D3 y las `21` unidades de `preguntas_nuevas_20.csv`, `0` menciones a QIDs/trampas y `74/210` ejemplos con `No aplica`.
  - `entrenar_redactor.py`: entrenamiento QLoRA reproducible en Colab T4 (`NF4`, `r=16`, `alpha=32`, `3,0` épocas, `~33,03M` parámetros entrenables = `1,48%` de `2,24B` cuantizados / `~0,82%` de ~`4,0B` nominales).
  - `evaluar_d4.py`: orquestador multi-agente con `--solo-base` (control en mismo entorno), `--preguntas-csv` / `--nombre-set` y `--output-prefix`.
  - `generar_auditoria_d4.py`: auditoría estricta reproducible por SHA-256 para **v2 completa** (`FT 75`, `Control Base 75`, `Nuevas 20 FT` y `Nuevas 20 Base`) + compatibilidad con archivo v1 y auditoría general (`auditar_fila_determinista`).
- `datos/`: `redactor_train.jsonl`, `redactor_val.jsonl`, `preguntas_nuevas_20.csv` (20 preguntas inéditas ciegas sobre 21 unidades reservadas), `dataset_resumen.json` y `MUESTRA_REVISION_MANUAL.md` (bitácora estratificada de 30 casos lista para firma humana).
- `entrenamiento/`: métricas/curvas de **corrida v2 en T4** (`training_metrics.json`, `loss_curve.*`, `smoke_test_val.json`, `adapter/README.md`).
- `evaluacion/`: registros completos de **corrida v2 en A100 `bf16`** (`resultados_agentes_D4*.csv`, `resultados_control_base_D4*.csv`, `resultados_nuevas20_ft_D4*.csv`, `resultados_nuevas20_base_D4*.csv`, trazas, telemetría, auditorías `auditoria_*.json`, `casos_fallo_y_regresion.json`, `comparativa_base_vs_finetuned.json`, `comparativa_nuevas20.json`).
- `documento/`: `main.tex`, `grafo_d4.tex`, `grafo_d4.pdf` y `main.pdf` (reporte vertical de **1 página** en LaTeX).
- `video/`: `GUION_VIDEO_D4.md` (guion v2 para grabación en vivo) y `mostrar_demo_d4.py` (`--live` en GPU o visor de trazas).
- Notebooks Colab: [`D4_colab_entrenamiento.ipynb`](D4_colab_entrenamiento.ipynb), [`D4_colab_evaluacion.ipynb`](D4_colab_evaluacion.ipynb) y [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb).
- `tests/`: pruebas unitarias en `test_diagnostico_d3.py`, `test_dataset.py`, `test_entrenamiento.py` y `test_evaluar_d4.py`.

---

## Cómo reproducir y pasos finales antes del merge a `main`

Desde la raíz del repositorio (`Proyecto_Git`):

```bash
# 1. Reconstruir diagnóstico y dataset v2 (antifuga dual + LF)
python3 "Deliverable 4/scripts/diagnostico_d3.py"
python3 "Deliverable 4/scripts/construir_dataset.py"

# 2. Regenerar auditorías y verificación determinista v2
python3 "Deliverable 4/scripts/generar_auditoria_d4.py"

# 3. Correr pruebas sin GPU (en Linux/Mac o Windows con LF en .gitattributes)
python3 -m unittest discover -s "Deliverable 4/tests" -v

# 4. Recompilar informe técnico de 1 página en LaTeX
cd "Deliverable 4/documento" && tectonic grafo_d4.tex && tectonic main.tex
```

**Checklist pendiente tras revisión de Álvaro en `deliverable-4`:**
1. **Revisión par (Álvaro Contreras):** Revisar los artefactos v2, los fallos documentados y firmar los 30 casos en `datos/MUESTRA_REVISION_MANUAL.md`.
2. **Grabar video en vivo (≤ 3 min):** Ejecutar [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb) con GPU (`H07` en vivo Base vs FT + traza de fallo `H06`/`H03`) y pegar el enlace público en este README, `README.md` y `main.tex`.
3. **Antes del merge a `main`:** Actualizar enlaces `tree/deliverable-4` → `main` si corresponde, recompilar `main.pdf` y correr `unittest` final.
