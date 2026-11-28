# Asistente de normativa de pregrado · Ingeniería UdeC

**Álvaro Contreras y Pablo Cortés** · Generative Artificial Intelligence (580694), segundo semestre 2026

Asistente en español sobre normativa de pregrado de la Facultad de Ingeniería UdeC ([Corpus/`](Corpus/): *Reglamento General*, *Reglamento Interno FI* y *Calendario 2026*). Responde con dato exacto y cita verificable, o se abstiene si no existe respaldo normativo. Desde Deliverable 2 usa un único modelo **`Qwen/Qwen3-4B`** cuantizado en 4 bits (NF4), evolucionando de RAG a sistema multi-agente y finalmente a especialización **Multi-LoRA (`3-LoRA`)**.

---

## Empieza aquí · Deliverable 4 (Entrega actual: `3-LoRA`)

| Qué revisar (`enunciado.pdf`) | Acceso directo (rama `main`) |
|---|---|
| **Documento técnico (1 pág. A4, LaTeX)** | [`Deliverable 4/documento/main.pdf`](Deliverable%204/documento/main.pdf) · [fuente `main.tex`](Deliverable%204/documento/main.tex) + [grafo TikZ](Deliverable%204/documento/grafo_d4.tex) |
| **Video demostrativo (≤ 3 min)** | `[Pendiente: enlace público tras ensayo H07 y grabación]` · [Guion cronometrado](Deliverable%204/video/GUION_VIDEO_D4.md) · [Visor demo](Deliverable%204/video/mostrar_demo_d4.py) |
| **Colab Demo en vivo (`H07`, Base vs `3-LoRA`)** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%204/D4_colab_video_demo.ipynb) · [`D4_colab_video_demo.ipynb`](Deliverable%204/D4_colab_video_demo.ipynb) |
| **Colab Evaluación (`--solo-hf`, sin Drive)** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%204/D4_colab_evaluacion.ipynb) · [`D4_colab_evaluacion.ipynb`](Deliverable%204/D4_colab_evaluacion.ipynb) |
| **Pesos públicos Hugging Face (`SHA-256` verificado)** | [Enrutador](https://huggingface.co/Pablox0333/qwen3-4b-enrutador-udec-d4) · [Recuperador](https://huggingface.co/Pablox0333/qwen3-4b-recuperador-udec-d4) · [Redactor](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4) · [`manifest_adaptadores_hf.json`](Deliverable%204/entrenamiento/manifest_adaptadores_hf.json) |
| **Diagnóstico D3 y elección de agentes** | [`Deliverable 4/diagnostico/DIAGNOSTICO_D3.md`](Deliverable%204/diagnostico/DIAGNOSTICO_D3.md) |
| **Datasets (`725` pares) y revisión manual (`50/50`)** | [`Deliverable 4/datos/`](Deliverable%204/datos/) · [Firmas Redactor (30)](Deliverable%204/datos/revision_manual_firmas.csv) · [Firmas Enr./Rec. (20)](Deliverable%204/datos/revision_manual_firmas_agentes.csv) |
| **Prompts versionados (congelados de D3 v6)** | [`01_enrutador`](Deliverable%204/prompts/01_enrutador.txt) · [`02_recuperador`](Deliverable%204/prompts/02_recuperador.txt) · [`03_redactor`](Deliverable%204/prompts/03_redactor.txt) · [`04_verificador`](Deliverable%204/prompts/04_verificador.txt) |
| **Trazas de fallos reales y reproducibilidad** | [`casos_fallo_y_regresion_3lora.json`](Deliverable%204/evaluacion/casos_fallo_y_regresion_3lora.json) (`75`) · [`trazas_3lora_nuevas20.json`](Deliverable%204/evaluacion/trazas_3lora_nuevas20.json) (`N20`) · [`Deliverable 4/README.md`](Deliverable%204/README.md) |

---

## Evolución completa del proyecto (D1 → D4)

| Entrega | Carpeta / Informe | Arquitectura y entorno | Resultado principal |
|---|---|---|---|
| **D4 · Multi-LoRA por rol (`3-LoRA`)** | [`Deliverable 4/`](Deliverable%204/README.md) · [PDF](Deliverable%204/documento/main.pdf) | 1 NF4 (`Qwen3-4B`) + 3 QLoRA (`set_adapter`) + Verif. Base (`disable_adapter`) · Eval A100 `bf16` | **`64/75` (85,3%)** y **`74/95` (77,9%)** vs Control Base (`62/75`, `73/95`; McNemar `p=0,73`/`1,0`) con **`-41,0%` llamadas** (`388` vs `658`) |
| D3 · Sistema de 4 agentes | [`Deliverable 3/`](Deliverable%203/README.md) · [PDF](Deliverable%203/Deliverable3/documento/main.pdf) | Enrutador + Recuperador + Redactor + Verificador en `Qwen3-4B` Base · T4 | `46/50 + 20/25 = 66/75` (`711` llamadas LLM) |
| D2 · RAG estructurado | [`Deliverable2/`](Deliverable2/README.md) · [PDF](Deliverable2/entrega/Informe_tecnico_D2.pdf) | Embeddings Multilingual-E5 + expansión padre/unidad + remisiones · T4 `bf16` | `40/50` (`16/25` difíciles; baseline directo: `1/50`) |
| D1 · Línea base paramétrica | [`Deliverable1/`](Deliverable1/README.md) · [PDF](Deliverable1/informe/deliverable1.pdf) | `Qwen3-4B` sin corpus (`greedy`) · T4 | `2/50` (solo abstenciones; ausencia paramétrica) |

---

## Resumen ejecutivo de Deliverable 4 (`Deliverable 4/README.md` tiene el detalle completo)

- **Por qué `1-LoRA` → `3-LoRA`:** en D3 v6 (`66/75`), editar prompts tocó techo (`v5` cayó `58→55/75` y hubo que revertir a `v4`; quitar CoT dio `65/75`), y **8 de 9 errores** ocurrían con la evidencia ya presente en el Redactor. Al entrenar solo al **Redactor (`1-LoRA`)** en A100 `bf16`, la exactitud no subió (`60/75` vs `62/75` Control Base) y el **Recuperador** concentraba `373/648` llamadas (`132` en 20 nuevas). Adaptamos los 3 roles previos (**Enrutador, Recuperador, Redactor**) en un único modelo NF4 y dejamos al **Verificador en Base** como árbitro imparcial.
- **Ganancia real medida (`A100 bf16`):** en exactitud, McNemar no detectó diferencia (`64/75` vs `62/75`, `p=0,73`; `10/20` vs `11/20` en preguntas nuevas; `74/95` vs `73/95`, `p=1,0`). El salto real es **eficiencia operativa: `-41,0%` llamadas** (`658 → 388` en las `75` y `-53,5%` en `N20`), localizado en el Recuperador (`387 → 117`, `-69,8%`), con `-3,7%` de tiempo total (`75,3 → 72,6 min`) porque el Redactor domina la generación.
- **Por qué el Verificador quedó en Base:** entrenarlo también (`4-LoRA v1` y `v2`) empeoró el conjunto a **`58/75`** y **`56/75`** por exceso de rechazos sobre borradores válidos (`v1` penalizó respuestas con `No aplica`, pese a subir a `14/20` en `N20`).
- **Datos, alcance antifuga y trazabilidad:** `725` pares (`620` entrenamiento en `A100 bf16` para Enr/Rec y `T4 fp16` para Redactor; `105` validación; `0` truncados), `50/50` muestras revisadas y firmadas (`2026-11-19`), asistencia de **Gemini 4 Argon** (vía Antigravity) validada con `corpus.json`, **`0` coincidencias con las `61` unidades bloqueadas** de evaluación (`01_enrutador.txt` heredado de D3 conserva a `P36` como ejemplo few-shot donde `3-LoRA` aún falla), reproducción `--solo-hf` archivada ([`comparativa_reproduccion_hf.json`](Deliverable%204/evaluacion/comparativa_reproduccion_hf.json)) y **`32` pruebas offline en verde**.

---

## Entregas anteriores (D1–D3) y mapa del repositorio

- **Deliverable 3 (4 agentes base):** [`Deliverable 3/README.md`](Deliverable%203/README.md) · [PDF](Deliverable%203/Deliverable3/documento/main.pdf) · [Video (Drive)](https://drive.google.com/drive/folders/1tkhRhI4_G7ArWNHW7zNoeZi8lL9RyPf2?usp=sharing) · [![Colab D3](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%203/Deliverable3/Demo_D3.ipynb)
<details>
<summary>Ver desglose de ablaciones D3 (`66/75`) y detalles de D1–D2</summary>

| Configuración D3 (`Qwen3-4B` Base, T4) | 50 originales | 25 difíciles |
|---|---:|---:|
| Prompting directo / RAG E2 | 1 / 40 | 0 / 16 |
| **Agentes D3 v6 (completo)** | **46** | **20** |
| Sin few-shot / Sin ReAct | 44 / 45 | 19 / 18 |
| Sin CoT Redactor / Sin Verificador (1.er borrador) | 46 / 44 | 19 / 19 |

- **D2:** [`Deliverable2/README.md`](Deliverable2/README.md) · [`Informe_tecnico_D2.pdf`](Deliverable2/entrega/Informe_tecnico_D2.pdf) · [`REPORTE.md`](Deliverable2/resultados/qwen3_4b_f0bff499766960f7/REPORTE.md).
- **D1:** [`Deliverable1/README.md`](Deliverable1/README.md) · [`deliverable1.pdf`](Deliverable1/informe/deliverable1.pdf).
</details>

| Directorio | Contenido en `main` |
|---|---|
| [`Deliverable 4/`](Deliverable%204/README.md) | **Entrega oficial D4 (`3-LoRA`, `118` archivos)**: notebooks Colab, informe LaTeX, prompts congelados, `725` pares + firmas, scripts de entrenamiento/auditoría, trazas A100 y demo en video. |
| [`Deliverable 3/`](Deliverable%203/README.md) | Entrega D3 (los agentes, prompts, datos y PDF oficial viven dentro de [`Deliverable 3/Deliverable3/`](Deliverable%203/Deliverable3/)). |
| [`Deliverable2/`](Deliverable2/) | RAG estructurado E5, corpus curado y evaluaciones D2. |
| [`Deliverable1/`](Deliverable1/) | Diagnóstico zero-shot inicial y selección de `Qwen/Qwen3-4B`. |
| [`Corpus/`](Corpus/) | Los 3 PDF oficiales de normativa UdeC (`RG`, `RI-FI`, `Calendario 2026`). |
| [`Archivo/`](Archivo/) | Prototipos históricos de trazabilidad. *(Exploración previa en rama `backup/deliverable3_agentes_exploracion` y `Solo Redactor v2` en `backup/d4-solo-redactor`)*. |
