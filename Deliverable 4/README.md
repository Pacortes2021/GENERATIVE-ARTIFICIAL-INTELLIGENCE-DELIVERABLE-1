# Deliverable 4 — Especialización Multi-LoRA por rol (`Qwen/Qwen3-4B`)

Continuación directa de Deliverables 1–3 sobre normativa de pregrado de Ingeniería UdeC (`corpus.json`: `173` unidades padre, `197` unidades y `201` fragmentos de búsqueda; evaluación oficial sobre `75` preguntas: `congelado_50` + `dificil_25`, más set ciego `preguntas_nuevas_20.csv`), manteniendo **un único modelo base `Qwen/Qwen3-4B` cuantizado en 4 bits (NF4)** y el grafo multi-agente de Deliverable 3.

**Arquitectura oficial entregada (`3-LoRA`):**
- **Conmutación dinámica Multi-LoRA (`model.set_adapter()`):** `Enrutador`, `Recuperador` y `Redactor` activan su propio adaptador QLoRA (`r=16`, `alpha=32`) especializado por rol dentro del mismo modelo NF4.
- **Verificador aislado en Base (`model.disable_adapter()`):** se mantiene con pesos base íntegros (`98/98` llamadas OFF en las `75` oficiales, `32/32` OFF en `nuevas_20`, **`0` violaciones**), decisión respaldada empíricamente por las ablaciones `4-LoRA v1` (`58/75`) y `v2` (`56/75`).
- **Respaldo de variante previa:** el enfoque anterior de `Solo Redactor FT v2` (`60/75`) quedó respaldado íntegramente en la rama `backup/d4-solo-redactor`.

**Enlaces clave:**
- **Informe técnico (1 página, LaTeX):** [`documento/main.pdf`](documento/main.pdf) ([`main.tex`](documento/main.tex) + [`grafo_d4.tex`](documento/grafo_d4.tex))
- **Enunciado / Pauta oficial:** [`enunciado.pdf`](enunciado.pdf)
- **Adaptadores Hugging Face:**
  - `Redactor` (ya publicado): [`Pablox0333/qwen3-4b-redactor-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4) (commit [`739b031`](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4/commit/739b031acbd5feef2c49f946b94722712209bce0))
  - `Enrutador` y `Recuperador`: entrenados y respaldados en Google Drive (`/content/drive/MyDrive/UdeC_GenIA_Exp_MultiLoRA/entrenamiento`); se publican a `Pablox0333/qwen3-4b-enrutador-udec-d4` y `Pablox0333/qwen3-4b-recuperador-udec-d4` con un solo comando mediante [`scripts/publicar_adaptadores_hf.py`](scripts/publicar_adaptadores_hf.py) (o el Paso 5 de `D4_colab_entrenamiento.ipynb`) sin reentrenar.
- **Video demostrativo (≤ 3 min):** `[Pendiente: grabar con D4_colab_video_demo.ipynb y pegar enlace]` — guion en [`video/GUION_VIDEO_D4.md`](video/GUION_VIDEO_D4.md) y visor en [`video/mostrar_demo_d4.py`](video/mostrar_demo_d4.py).

---

## Resumen de resultados (A100 `bf16` pareado: `75` oficiales + `20` nuevas)

Evaluación bajo la pauta estricta heredada de D2/D3 ([`LEEME_PAUTA.md`](../Deliverable%203/paquete_25_dificiles/LEEME_PAUTA.md), incluyendo Regla 2 y Regla 3 / `P01`). Todas las comparativas D4 comparten el mismo binario, pesos base NF4, índice E5, GPU A100 40 GB `bf16` y semillas `2026`.

| Sistema / Control | Entorno | Orig. (50) | Dif. (25) | D3 (75) | Nuevas (20) | Global (95) | Llamadas (`75 / 20`) | Tiempo (`75 / 20`) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Directo D1 (0-shot) | T4 `fp16` | 1 (2,0%) | 0 (0,0%) | 1 (1,3%) | --- | --- | 75 / --- | --- |
| RAG D2 (E5) | T4 `fp16` | 40 (80,0%) | 16 (64,0%) | 56 (74,7%) | --- | --- | 75 / --- | --- |
| Multi-agente D3 Base (v6) | T4 `fp16` | **46 (92,0%)** | **20 (80,0%)** | **66 (88,0%)** | --- | --- | 711 / --- | 137,6 min / --- |
| Control Base D4 (`LoRA OFF`) | A100 `bf16` | **46 (92,0%)** | 16 (64,0%) | 62 (82,7%) | **11 (55,0%)** | 73 (76,8%) | 658 / 254 | 75,3 min / 32,8 min |
| Solo Redactor v2 (`1-LoRA`) | A100 `bf16` | 43 (86,0%) | 17 (68,0%) | 60 (80,0%) | 10 (50,0%) | 70 (73,7%) | 648 / 212 | 75,7 min / 25,1 min |
| **D4 Oficial (`3-LoRA`: Enr+Rec+Red FT, Ver Base)** | **A100 `bf16`** | **46 (92,0%)** | **18 (72,0%)** | **64 (85,3%)** | 10 (50,0%) | **74 (77,9%)** | **388 / 118** | **72,6 min / 30,2 min** |
| *Ablación 4-LoRA v1 (Verificador FT)* | A100 `bf16` | 40 (80,0%) | 18 (72,0%) | 58 (77,3%) | **14 (70,0%)** | 72 (75,8%) | 493 / 138 | --- |
| *Ablación 4-LoRA v2 (Verificador FT)* | A100 `bf16` | 40 (80,0%) | 16 (64,0%) | 56 (74,7%) | 12 (60,0%) | 68 (71,6%) | 486 / 147 | --- |

**Principales hallazgos (`evaluacion/resumen_comparativo_d4.json`):**
- **Recorte masivo de llamadas sin perder cobertura:** El `Recuperador` QLoRA redujo sus llamadas de `387 -> 117` en las `75` (`-69,8%`) y `162 -> 34` en `nuevas_20`, bajando el total global de **`658 -> 388` (`-41,0%`)** en las `75` y **`254 -> 118` (`-53,5%`)** en `nuevas_20`, con `0` fallbacks, `0` citas inexistentes/fuera de evidencia y `0` violaciones LoRA.
- **Mejora neta sobre Control Base y Solo Redactor:** `D4 3-LoRA` sube **`+2`** frente a `Control Base` (`64/75` vs `62/75`) y **`+4`** frente a `Solo Redactor` (`60/75`), alcanzando **`74/95` (`77,9%`)** global (`65/75` y `11/20` en núcleo sin precedente `P01`). En `dificil_25:H07` (`42` créditos / `4.o` semestre), `Control Base` falla por falsa abstención en `3` ciclos (`177,44 s`), mientras `3-LoRA` resuelve en `1` ciclo / `4` llamadas (`53,84 s`).
- **Auditoría transparente de fallos (`evaluacion/casos_fallo_y_regresion_3lora.json`):** `11` fallos estrictos en las `75` (`Redactor: 6`, `Recuperador: 3`, `Verificador Base: 2`) y `10` en `nuevas_20` (`4 / 3 / 3`):
  1. *Corte prematuro del Recuperador* (`H03`, `P25`, `P36`; `N16`, `N18`, `N19`): declara `suficiente` demasiado pronto en preguntas de dos partes.
  2. *Sobre-rechazo del Verificador Base* (`H17`, `H19`; `N05`, `N11`, `N20`): p. ej. `H17` respondía bien en ciclo 1, pero `3` rechazos del Verificador lo obligaron a invertir el sentido en ciclo 3; entrenar al Verificador empeoró aún más por sobre-rechazo (`58/75` y `56/75`).
  3. *Errores residuales del Redactor* (`H06`, `H12`, `H22`, `H25`, `P24`, `P26`; `N01`, `N06`, `N07`, `N10`).

---

## Datasets antifuga (725 pares) y entrenamiento QLoRA por rol

Generados determinísticamente (`seed=202604`) con [`scripts/construir_datasets_agentes.py`](scripts/construir_datasets_agentes.py) + [`scripts/antifuga_multi.py`](scripts/antifuga_multi.py), con **`0` unidades compartidas** con `D3-75` (`40` unidades) ni con `preguntas_nuevas_20.csv` (`21` unidades), `0` cruces train/val y `0` alertas léxicas (Jaccard `>= 0,80`).

| Agente | Train / Val | Unidades únicas | Hiperparámetros clave | Entrenamiento y mejor `eval_loss` |
|---|---:|---:|---|---|
| **Enrutador** | `210 / 36` (`246`) | `97 / 197` | `max_len=2048`, `eval_steps=10`, `r=16, alpha=32` | A100 `bf16`: `9,88 min` (`105` pasos) · `1,066 -> 0,123` (`step 80`) |
| **Recuperador** | `230 / 39` (`269`) | `109 / 197` | `max_len=2048`, `eval_steps=15`, `r=16, alpha=32` | A100 `bf16`: `10,43 min` (`117` pasos) · `1,729 -> 0,186` (`step 117`) |
| **Redactor** | `180 / 30` (`210`) | `112 / 197` | `max_len=4096`, `eval_steps=15`, `r=16, alpha=32` | T4 `fp16`: `52,38 min` (`90` pasos) · `1,601 -> 0,516` (`step 90`) |
| **Total D4** | **`620 / 105` (`725`)** | **`0%` fuga** | `completion_only_loss=True`, `0` truncados | Gráfica combinada en [`entrenamiento/loss_curves_3agentes.png`](entrenamiento/loss_curves_3agentes.png) |

Muestras de revisión manual: [`datos/MUESTRA_REVISION_MANUAL.md`](datos/MUESTRA_REVISION_MANUAL.md) (`30` casos del Redactor) + [`datos/MUESTRA_REVISION_MANUAL_ENRUTADOR_RECUPERADOR.md`](datos/MUESTRA_REVISION_MANUAL_ENRUTADOR_RECUPERADOR.md) (`20` casos de Enrutador/Recuperador).

---

## Estructura de `Deliverable 4/`

- `prompts/`: prompts originales heredados bit a bit de D3 v6 (`01_enrutador.txt`..`04_verificador.txt`).
- `scripts/`:
  - `construir_datasets_agentes.py`, `enrutador_bloques.py`, `recuperador_bloques.py`, `antifuga_multi.py` (y `construir_dataset.py` + `dataset_blocks/` para los 6 bloques del Redactor).
  - `entrenar_agente.py` (QLoRA parametrizable por `--agente {enrutador,recuperador,redactor}`) + `publicar_adaptadores_hf.py` (subida desde Drive/local a HF).
  - `evaluar_multi_lora.py` (conmutación `set_adapter()` / `disable_adapter()` + `verificar_aislamiento_multi_lora`), `resumir_comparativa.py`, `generar_reporte_3lora.py`, `generar_auditoria_d4.py`, `diagnostico_d3.py`.
- `datos/`: `{enrutador,recuperador,redactor}_{train,val}.jsonl`, `resumen_datasets_3_agentes.json`, `preguntas_nuevas_20.csv`, y muestras manuales.
- `entrenamiento/`: métricas/curvas de los 3 adaptadores (`loss_curves_3agentes.{pdf,png}`, `enrutador/`, `recuperador/` y resultados del Redactor en la raíz de `entrenamiento/`).
- `evaluacion/`: corridas `3lora_75`, `3lora_nuevas20`, `control_base_D4`, `resumen_comparativo_d4.json`, `comparativa_base_vs_3lora.json` (`7` casos A100) y `casos_fallo_y_regresion_3lora.json` (`11` fallos).
- `documento/`: `grafo_d4.{tex,pdf}` y `main.{tex,pdf}` (1 página en LaTeX).
- `video/`: `GUION_VIDEO_D4.md` y `mostrar_demo_d4.py`.
- Notebooks Colab: [`D4_colab_entrenamiento.ipynb`](D4_colab_entrenamiento.ipynb), [`D4_colab_evaluacion.ipynb`](D4_colab_evaluacion.ipynb), [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb).
- `tests/`: suite offline (`test_diagnostico_d3.py`, `test_dataset.py`, `test_entrenamiento.py`, `test_evaluar_d4.py`, `test_multi_lora_d4.py`).

---

## Comandos de reproducción offline y checklist final

```bash
# 1. Reconstruir y verificar datasets antifuga de los 3 agentes (725 pares)
python3 "Deliverable 4/scripts/construir_datasets_agentes.py"

# 2. Regenerar curvas combinadas, comparativa A100, fallos y resumen consolidado
python3 "Deliverable 4/scripts/generar_reporte_3lora.py"

# 3. Ejecutar suite completa de tests offline
python3 -m unittest discover -s "Deliverable 4/tests" -v

# 4. Compilar grafo TikZ e informe técnico de 1 página
cd "Deliverable 4/documento" && tectonic grafo_d4.tex && tectonic main.tex
```

**Pasos manuales pendientes antes de entregar / fusionar a `main`:**
1. **Publicar `Enrutador` y `Recuperador` en Hugging Face:** abrir [`D4_colab_entrenamiento.ipynb`](D4_colab_entrenamiento.ipynb) y correr el Paso 5 (o `python3 "Deliverable 4/scripts/publicar_adaptadores_hf.py" --hf-username Pablox0333`) con Drive montado y `HF_TOKEN`.
2. **Revisión manual de par (Álvaro Contreras):** revisar y firmar las `20` muestras en [`MUESTRA_REVISION_MANUAL_ENRUTADOR_RECUPERADOR.md`](datos/MUESTRA_REVISION_MANUAL_ENRUTADOR_RECUPERADOR.md) y los veredictos en `MUESTRA_REVISION_MANUAL.md`.
3. **Grabar video demo (≤ 3 min):** correr [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb) mostrando `dificil_25:H07` en vivo (`Base` vs `3-LoRA`) y los fallos reales, y pegar el enlace público en `README.md` y `documento/main.tex`.
