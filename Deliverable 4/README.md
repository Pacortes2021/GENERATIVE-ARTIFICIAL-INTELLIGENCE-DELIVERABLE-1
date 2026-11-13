# Deliverable 4 — Especialización QLoRA del Agente Redactor (`Qwen/Qwen3-4B`)

Continuación directa de Deliverables 1–3 sobre normativa de pregrado de Ingeniería UdeC (`corpus.json`: 173 unidades padre, 197 unidades y 201 fragmentos de búsqueda; evaluación oficial sobre 75 preguntas: `congelado_50` + `dificil_25`), manteniendo `Qwen/Qwen3-4B` (4 bits NF4) y el sistema de cuatro agentes de Deliverable 3.

- **Informe técnico (1 página, LaTeX):** [`documento/main.pdf`](documento/main.pdf) (fuente: [`documento/main.tex`](documento/main.tex) y grafo [`documento/grafo_d4.tex`](documento/grafo_d4.tex))
- **Enunciado / Pauta oficial:** [`enunciado.pdf`](enunciado.pdf)
- **Adaptador público en Hugging Face:** [`Pablox0333/qwen3-4b-redactor-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4) *(pesos v1 actuales; actualizar tras re-entrenar dataset v2 en Colab)*
- **Video demostrativo (≤ 3 min, enlace abierto):** `[Pendiente: pegar enlace público tras grabar en vivo]` — guía y notebook en vivo en [`video/GUION_VIDEO_D4.md`](video/GUION_VIDEO_D4.md), [`video/mostrar_demo_d4.py`](video/mostrar_demo_d4.py) y [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb)

> **Estado actual del repositorio (rama `deliverable-4`):** Los artefactos numéricos en `entrenamiento/` y `evaluacion/` corresponden a la **corrida v1 archivada**, mientras que `datos/`, `scripts/`, `tests/` y los notebooks Colab ya incorporan el **pipeline v2 completo** (dataset v2 antifuga con balance `No aplica`, control `--solo-base` en el mismo entorno y set ciego `preguntas_nuevas_20.csv`) listo para ejecutar en Colab GPU.

---

## Resumen de resultados (corrida v1 archivada sobre 75 preguntas)

Evaluación bajo la pauta estricta heredada de D2/D3 ([`LEEME_PAUTA.md`](../Deliverable%203/paquete_25_dificiles/LEEME_PAUTA.md), incluyendo Regla 3 / precedente `P01`). En la corrida v1, `Enrutador`, `Recuperador` y `Verificador` ejecutaron con `model.disable_adapter()` (`0` violaciones LoRA en `101/101` Redactor ON y `565/565` Base OFF; `max_abs_logit_diff = 14.0625`).

| Sistema / Control (v1 archivada) | Originales (50) | Difíciles (25) | Total (75) | Llam./preg | Nota de entorno |
|---|---:|---:|---:|---:|---|
| Directo D1 (referencia 0-shot) | 1 (2,0%) | 0 (0,0%) | 1 (1,3%) | 1,0 | Mismo modelo base |
| RAG D2 (E5) | 40 (80,0%) | 16 (64,0%) | 56 (74,7%) | 1,0 | Misma recuperación |
| Multi-agente D3 Base (v6) | **46 (92,0%)** | **20 (80,0%)** | **66 (88,0%)** | 9,5 (`711`) | Sesión Colab D3 (`137,6 min`) |
| **Multi-agente D4 (`Redactor` FT QLoRA v1)** | 45 (90,0%) | 19 (76,0%) | 64 (85,3%) | **8,9 (`666`)** | Sesión Colab D4 v1 (`114,4 min`) |

> **Por qué se retiró la fila *"D4 núcleo 68/75"*:** Al aplicar la misma regla relajada sin `P01` en Condiciones a D3 v6 (`P13` y `H18` eran fallos `P01` en D3), D3 también subiría al menos a `68/75`, por lo que esa fila no era comparable de forma justa. Asimismo, la diferencia de tiempo (`-16,88%`) compara sesiones de Colab T4 distintas y requiere verificación pareada.

- **Balance neto y todas las categorías (D4 v1 vs D3 v6):** **`+6` corregidas** (`P13, P24, P26, H07, H14, H25`) y **`-8` regresiones** (`P6, P7, P10, P31, P36, H02, H04, H06`):
  - **Mejoras:** `condicional` (`8 → 10/10`), `numerica` (`9 → 10/10`), `negacion_excepcion` (`2 → 3/3`).
  - **Mantiene 100%:** `abstencion` (`10/10`), `colision_lexica` (`5/5`), `premisa_falsa` (`4/4`).
  - **Retrocesos y empates:** **`factual` bajó de `10/10 → 7/10`**, **`multi_salto` bajó de `3/4 → 1/4`**, `cruce` bajó de `9/10 → 8/10`; sin cambio neto en `calculo` (`3/4`) ni `sintesis` (`3/5`).
- **Comparativa pareada Base vs Fine-tuned (6 casos D3 en mismo entorno):** En [`evaluacion/comparativa_base_vs_finetuned.json`](evaluacion/comparativa_base_vs_finetuned.json), D4 v1 gana **4/6 vs 1/6** del Base (`dificil_25:H07`: FT `42/4 = 10,5` en `1` ciclo / `78,7 s` vs Base `3` ciclos / `227,68 s`; `H14` corrige polaridad). Como D3 original usó otra sesión y estos 6 casos eran todos fallos D3, en v2 incorporamos el flag **`--solo-base`** para evaluar el **Control Base completo** en el mismo entorno.
- **Auditoría de fallos v1 y causa raíz (`0/210` `"No aplica"`):**
  - **Sobre-agregado en Condiciones (`P01`):** En el dataset v1, `0/210` ejemplos tenían `"Condiciones o límites: No aplica"`, induciendo al Redactor a agregar cláusulas extra mal citadas o sustituir IDs (`P6, P7, P10, P31, P36, H02, H04, H18`).
  - **`H19` y `H06` (`Verificador base`):** En `H19`, Redactor FT acierta `[RG-ART-028]` en ciclos 1–2, pero el Verificador base pide umbrales de `RI-FI-ART-014` y empuja un ciclo 3 erróneo. En `H06`, el primer borrador del Redactor ya parte con `"No, 38 créditos..."` pese a calcular `38/4 = 9,5`; el Verificador objeta semestres totales y aprueba la retracción en ciclo 2. En total, `8/68` aprobaciones fueron incorrectas y **`4 de 7` respuestas rechazadas eran borradores válidos**.
  - **`H03` (`Recuperador`):** `CAL-2026-S2-02` sigue fuera del `top-6` y FT calcula `04 sep → 11 dic = 98 días` en vez de abstenerse.

---

## Estructura del entregable (actualizada a v2)

- `prompts/`: prompts versionados por agente heredados bit a bit desde Deliverable 3 v6 (`01_enrutador.txt`, `02_recuperador.txt`, `03_redactor.txt`, `04_verificador.txt`).
- `scripts/`:
  - `diagnostico_d3.py`: diagnostica `top-6` y origen de los 9 errores de D3 (`diagnostico/`).
  - `dataset_blocks/` (`reglas_v2.py`, `bloques_1_2.py`, `bloques_3_4.py`, `bloques_5_6.py`) y `construir_dataset.py`: generan el **dataset v2 (`180 train / 30 val`)** desde fragmentos literales de `corpus.json` con **asistencia de Antigravity (IA)**, imponiendo `0` solapamiento con las `40` unidades eval D3 y las `21` unidades de `preguntas_nuevas_20.csv`, `0` menciones a QIDs/trampas y `74/210` ejemplos con `No aplica`.
  - `entrenar_redactor.py`: entrenamiento QLoRA reproducible en Colab T4 (`NF4`, `r=16`, `alpha=32`, `3,0` épocas, `~33,03M` parámetros entrenables = `1,48%` de `2,24B` cuantizados / `~0,82%` de ~`4,0B` nominales).
  - `evaluar_d4.py`: orquestador multi-agente con `--solo-base` (control en mismo entorno), `--preguntas-csv` / `--nombre-set` y `--output-prefix`.
  - `generar_auditoria_d4.py`: auditoría v1 archivada + auditoría general sin diccionarios fijos (`auditar_fila_determinista`, soporte `--resultados-csv` y `--control-csv`).
- `datos/`: `redactor_train.jsonl`, `redactor_val.jsonl`, `preguntas_nuevas_20.csv` (20 preguntas inéditas ciegas sobre 21 unidades reservadas), `dataset_resumen.json` y `MUESTRA_REVISION_MANUAL.md` (bitácora estratificada de 30 casos con estado de revisión).
- `entrenamiento/`: métricas/curvas de corrida v1 (`training_metrics.json`, `loss_curve.*`, `smoke_test_val.json`, `adapter/README.md`).
- `evaluacion/`: registros v1 archivados (`resultados_agentes_D4*.csv`, `trazas_D4.json`, `auditoria_D4.json`, `casos_fallo_y_regresion.json`, `comparativa_base_vs_finetuned.json`, etc.).
- `documento/`: `main.tex`, `grafo_d4.tex`, `grafo_d4.pdf` y `main.pdf` (reporte vertical de **1 página** en LaTeX).
- `video/`: `GUION_VIDEO_D4.md` (solo modo en vivo) y `mostrar_demo_d4.py` (`--live` en GPU o visor de trazas).
- Notebooks Colab: [`D4_colab_entrenamiento.ipynb`](D4_colab_entrenamiento.ipynb), [`D4_colab_evaluacion.ipynb`](D4_colab_evaluacion.ipynb) y [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb).
- `tests/`: pruebas unitarias en `test_diagnostico_d3.py`, `test_dataset.py`, `test_entrenamiento.py` y `test_evaluar_d4.py`.

---

## Cómo reproducir y pasos pendientes antes de la entrega final (30 de noviembre)

Desde la raíz del repositorio (`Proyecto_Git`):

```bash
# 1. Reconstruir diagnóstico y dataset v2 (antifuga dual + LF)
python3 "Deliverable 4/scripts/diagnostico_d3.py"
python3 "Deliverable 4/scripts/construir_dataset.py"

# 2. Correr pruebas sin GPU (en Linux/Mac o Windows con LF en .gitattributes)
python3 -m unittest discover -s "Deliverable 4/tests" -v

# 3. Recompilar informe técnico de 1 página en LaTeX
cd "Deliverable 4/documento" && tectonic grafo_d4.tex && tectonic main.tex
```

**Checklist pendiente tras este push a `deliverable-4`:**
1. **Re-entrenar sobre dataset v2 (Colab T4, ~55 min):** Ejecutar [`D4_colab_entrenamiento.ipynb`](D4_colab_entrenamiento.ipynb), subir el adaptador v2 a `Pablox0333/qwen3-4b-redactor-udec-d4` y actualizar `Deliverable 4/entrenamiento/` (`D4_resultados_paso3.zip`) para sincronizar `train_sha256` en `test_entrenamiento.py`.
2. **Evaluar v2 + Control Base + 20 Nuevas (Colab T4):** Ejecutar [`D4_colab_evaluacion.ipynb`](D4_colab_evaluacion.ipynb) (`FT 75`, `--solo-base` Control Base 75 en el mismo entorno y `preguntas_nuevas_20.csv`), auditar manualmente y firmar `datos/MUESTRA_REVISION_MANUAL.md`. *(Recomendado: confirmar con el profesor la definición esperada de `"control"` en la tabla comparativa).*
3. **Grabar video en vivo (≤ 3 min):** Usar [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb) con GPU y pegarlo en este README, `README.md` y `main.tex`.
4. **Antes del merge a `main`:** Actualizar los enlaces de `tree/deliverable-4` a `main` en `main.tex` y notebooks (o conservar la rama `deliverable-4`), recompilar `main.pdf` y correr `unittest` tras los artefactos finales v2.
