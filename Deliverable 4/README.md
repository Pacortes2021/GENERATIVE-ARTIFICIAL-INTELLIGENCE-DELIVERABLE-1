# Deliverable 4 — Especialización QLoRA del Agente Redactor (`Qwen/Qwen3-4B`)

Continuación directa de Deliverables 1–3 sobre normativa de pregrado de Ingeniería UdeC (`corpus.json`: 173 unidades padre, 197 unidades y 201 fragmentos de búsqueda; evaluación oficial sobre 75 preguntas: `congelado_50` + `dificil_25`), manteniendo `Qwen/Qwen3-4B` (4 bits NF4) y el sistema de cuatro agentes de Deliverable 3.

- **Informe técnico (1 página vertical, LaTeX):** [`documento/main.pdf`](documento/main.pdf) (fuente: [`documento/main.tex`](documento/main.tex) y grafo [`documento/grafo_d4.tex`](documento/grafo_d4.tex))
- **Adaptador público en Hugging Face:** [`Pablox0333/qwen3-4b-redactor-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4)
- **Video demostrativo (≤ 3 min, enlace abierto):** `[Pendiente: pegar enlace público tras grabar con la guía]` — guion y visor listos en [`video/GUION_VIDEO_D4.md`](video/GUION_VIDEO_D4.md), [`video/mostrar_demo_d4.py`](video/mostrar_demo_d4.py) y [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb)

---

## Resumen de resultados (75 preguntas oficiales)

Evaluación bajo la pauta estricta heredada de D2/D3 ([`LEEME_PAUTA.md`](../Deliverable%203/paquete_25_dificiles/LEEME_PAUTA.md), incluyendo Regla 3 / precedente `P01`). Todas las llamadas de `Enrutador`, `Recuperador` y `Verificador` ejecutaron con `model.disable_adapter()` (`0` violaciones de aislamiento LoRA en `101/101` llamadas del `Redactor` con adaptador ON y `565/565` llamadas de otros agentes con adaptador OFF; `max_abs_logit_diff = 14.0625`).

| Sistema / Control | Originales (50) | Difíciles (25) | Total (75) | Llam./preg | Tiempo T4 |
|---|---:|---:|---:|---:|---:|
| Directo D1 (control) | 1 (2,0%) | 0 (0,0%) | 1 (1,3%) | 1,0 | — |
| RAG D2 (E5) | 40 (80,0%) | 16 (64,0%) | 56 (74,7%) | 1,0 | — |
| Multi-agente D3 Base (v6) | **46 (92,0%)** | **20 (80,0%)** | **66 (88,0%)** | 9,5 (`711`) | `137,6 min` (`8257,8 s`) |
| **Multi-agente D4 (`Redactor` FT QLoRA)** | 45 (90,0%) | 19 (76,0%) | 64 (85,3%) | **8,9 (`666`)** | **`114,4 min` (`6864,1 s`)** |
| *D4 núcleo (sin P01 en Condiciones)* | *47 (94,0%)* | *21 (84,0%)* | *68 (90,7%)* | *8,9* | *`114,4 min`* |

- **Mejora en fallos previos y eficiencia:** D4 resuelve **6/9 fallos estrictos de D3** (`congelado_50:13, 24, 26` y `dificil_25:H07, H14, H25`) y corrige el núcleo de `congelado_50:36` y `dificil_25:H18`; alcanza `100%` en `numerica (10/10)`, `condicional (10/10)`, `negacion_excepcion (3/3)`, `abstencion (10/10)`, `colision_lexica (5/5)` y `premisa_falsa (4/4)`; reduce llamadas LLM reales en `-6,33%` (`711 → 666`), reescrituras multi-ciclo en `-28,6%` (`21 → 15`), eventos de traza en `-6,14%` (`798 → 749`) y tiempo T4 en `-16,88%` (`0` fallbacks).
- **Comparativa controlada Base vs Fine-tuned (6 casos idénticos en mismo entorno):** En [`evaluacion/comparativa_base_vs_finetuned.json`](evaluacion/comparativa_base_vs_finetuned.json), D4 gana **4/6 vs 1/6** del sistema Base (ej. `dificil_25:H07`: FT resuelve `42/4 = 10,5` en `1` ciclo / `78,7 s`, mientras Base cae en abstención falsa tras `3` ciclos / `227,68 s`; `dificil_25:H14`: FT corrige la contradicción polar `"Sí, queda automáticamente..."` → `"No queda automáticamente..."`).
- **Auditoría de fallos y cuello de botella:** Documentados con traza completa en [`evaluacion/casos_fallo_y_regresion.json`](evaluacion/casos_fallo_y_regresion.json):
  - `H03`: fallo persistente D1–D4 (`CAL-2026-S2-02` sigue fuera del `top-6` del Recuperador y FT calcula mal el intervalo en ciclo 3 en vez de abstenerse).
  - `H19` y `H06`: degradación causada por el **Verificador base** (en `H19`, el Redactor FT acierta `[RG-ART-028]` en ciclos 1–2, pero el Verificador lo rechaza pidiendo reglas de `RI-FI-ART-014`; en total `8/68` aprobaciones del Verificador fueron incorrectas y `4/7` rechazos eran válidos).
  - Desvíos puntuales de cita `[ID]` / mezcla en Condiciones (`P01`): `P6`, `P7`, `P10`, `P31`, `P36`, `H02`, `H04`, `H18`.

---

## Estructura del entregable

- `prompts/`: prompts versionados por agente heredados bit a bit desde Deliverable 3 v6 (`01_enrutador.txt`, `02_recuperador.txt`, `03_redactor.txt`, `04_verificador.txt`).
- `scripts/`:
  - `diagnostico_d3.py`: diagnostica `top-6` y origen de los 9 errores de D3 (`diagnostico/`).
  - `dataset_blocks/` y `construir_dataset.py`: genera determinísticamente los `210` pares híbridos (`180 train / 30 val`) desde fragmentos literales de `corpus.json` y audita separación antifuga frente a las 75 preguntas (`datos/`).
  - `entrenar_redactor.py`: entrenamiento QLoRA reproducible en Colab T4 (`NF4`, `r=16`, `alpha=32`, `90` pasos / `3,0` épocas, `54,75 min`, `eval_loss: 1,6195 → 0,5753`) y generación de curvas/smoke test (`entrenamiento/`).
  - `evaluar_d4.py`: orquestador multi-agente con aislamiento LoRA solo en `redactor` (`disable_adapter()` en el resto) y comparativa Base vs Fine-tuned.
  - `generar_auditoria_d4.py`: audita los 75 resultados contra `corpus.json` y `LEEME_PAUTA.md`, generando `evaluacion/resultados_agentes_D4_auditados.csv`, `evaluacion/auditoria_D4.json` y `evaluacion/casos_fallo_y_regresion.json`.
- `datos/`: `redactor_train.jsonl`, `redactor_val.jsonl`, `dataset_resumen.json` y `MUESTRA_REVISION_MANUAL.md` (30 ejemplos revisados manualmente).
- `entrenamiento/`: `training_metrics.json`, `loss_curve.png`, `loss_curve.pdf`, `smoke_test_val.json` y `adapter/README.md`.
- `evaluacion/`: `resultados_agentes_D4.csv`, `resultados_agentes_D4_auditados.csv`, `trazas_D4.json`, `telemetria_llamadas.json`, `comparativa_base_vs_finetuned.json`, `configuracion_evaluacion.json`, `auditoria_D4.json` y `casos_fallo_y_regresion.json`.
- `documento/`: `main.tex`, `grafo_d4.tex`, `grafo_d4.pdf` y `main.pdf` (reporte vertical de **1 página** en LaTeX).
- `video/`: `GUION_VIDEO_D4.md` y `mostrar_demo_d4.py` para exhibir mensajes intermedios entre agentes y comparación Base vs FT sobre la misma entrada (offline o `--live` en GPU).
- Notebooks Colab: [`D4_colab_entrenamiento.ipynb`](D4_colab_entrenamiento.ipynb), [`D4_colab_evaluacion.ipynb`](D4_colab_evaluacion.ipynb) y [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb).
- `tests/`: 21 pruebas automáticas (`test_diagnostico_d3.py`, `test_dataset.py`, `test_entrenamiento.py`, `test_evaluar_d4.py`).

---

## Cómo reproducir

Desde la raíz del repositorio (`Proyecto_Git`):

```bash
# 1. Reconstruir diagnóstico, dataset y auditoría antifuga + auditoría de resultados D4
python3 "Deliverable 4/scripts/diagnostico_d3.py"
python3 "Deliverable 4/scripts/construir_dataset.py"
python3 "Deliverable 4/scripts/generar_auditoria_d4.py"

# 2. Verificar suite completa sin necesidad de GPU
python3 -m unittest discover -s "Deliverable 4/tests" -v

# 3. Visualizar comparativa Base vs FT con mensajes intermedios entre agentes (para video/revisión)
python3 "Deliverable 4/video/mostrar_demo_d4.py" --qid dificil_25:H07 --qid dificil_25:H14 --fallo dificil_25:H19

# 4. Recompilar informe técnico de 1 página en LaTeX (con Tectonic / XeLaTeX + TikZ)
cd "Deliverable 4/documento" && tectonic grafo_d4.tex && tectonic main.tex
```

Para repetir entrenamiento o inferencia en GPU T4 de Colab, usa [`D4_colab_entrenamiento.ipynb`](D4_colab_entrenamiento.ipynb), [`D4_colab_evaluacion.ipynb`](D4_colab_evaluacion.ipynb) o el modo `--live` en [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb).

---

## Estado de la entrega (`Paso 1`–`Paso 6`)

1. **Paso 1 (completado):** Diagnóstico empírico de D3 v6 (`DIAGNOSTICO_D3.md`) y prompts base v6 preservados.
2. **Paso 2 (completado):** Corpus supervisado del `Redactor` (`180/30`), validación manual de `30` casos y verificación `0` fugas.
3. **Paso 3 (completado):** Entrenamiento QLoRA en `Tesla T4` (`eval_loss: 1,6195 → 0,5753`) y adaptador abierto en Hugging Face.
4. **Paso 4 (completado):** Evaluación completa de 75 preguntas (`64/75` estricto, `68/75` núcleo, `6/9` errores D3 resueltos, `-16,88%` tiempo), comparativa pareada (`4/6 vs 1/6`) y auditoría completa de fallos (`casos_fallo_y_regresion.json`).
5. **Paso 5 (completado):** Informe técnico vertical de 1 página en LaTeX ([`documento/main.pdf`](documento/main.pdf)) con grafo, datos, curvas, tabla de resultados y traza de fallo.
6. **Paso 6 (tooling listo / falta grabación del equipo):** Guion temporizado ([`video/GUION_VIDEO_D4.md`](video/GUION_VIDEO_D4.md)), CLI de demostración ([`video/mostrar_demo_d4.py`](video/mostrar_demo_d4.py)) y notebook [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb); solo falta grabar el video ≤ 3 min y pegar el enlace abierto arriba y en el envío final.
