# Asistente de normativa de pregrado · Ingeniería UdeC

**Álvaro Contreras y Pablo Cortés** · Generative Artificial Intelligence (580694), segundo semestre 2026

El sistema responde preguntas en español sobre la normativa de pregrado de la Facultad de Ingeniería de la UdeC
(Reglamento General, Reglamento Interno FI y Calendario 2026) con el dato exacto y la cita que lo respalda, y se
abstiene cuando la información no existe o la pregunta parte de una premisa falsa. Todas las entregas usan
**Qwen/Qwen3-4B** (cuantizado a 4 bits NF4 desde el Deliverable 2; T4 `float16` en D1–D3 y entrenamiento D4, y **A100 `bf16`** en la evaluación comparativa v2 de D4).

| Entrega | Carpeta | Informe | Resultado principal |
|---|---|---|---|
| **Deliverable 4 · Multi-LoRA por rol (`3-LoRA`)** | [`Deliverable 4/`](Deliverable%204/README.md) | [PDF](Deliverable%204/documento/main.pdf) | **A100 `bf16`**: `64/75` (`85,3%`) y `74/95` (`77,9%`) vs Control Base (`62/75`, `73/95`; McNemar no detectó diferencia: `p=0,73`/`1,0`) con **`-41,0%` llamadas** (`388` vs `658`) |
| Deliverable 3 · sistema de agentes | [`Deliverable 3/`](Deliverable%203/README.md) | [PDF](Deliverable%203/Deliverable3/documento/main.pdf) | 46/50 y 20/25 (RAG del E2: 40/50 y 16/25) |
| Deliverable 2 · RAG estructurado | [`Deliverable2/`](Deliverable2/README.md) | [PDF](Deliverable2/entrega/Informe_tecnico_D2.pdf) | 40/50 (baseline directo con la misma configuración: 1/50) |
| Deliverable 1 · diagnóstico y modelo | [`Deliverable1/`](Deliverable1/README.md) | [PDF](Deliverable1/informe/deliverable1.pdf) | Baseline directo 2/50 (decodificación greedy): ausencia paramétrica |

---

## Deliverable 4: especialización Multi-LoRA por rol (`Enrutador + Recuperador + Redactor`)

- **Informe técnico (1 página, LaTeX):** [`Deliverable 4/documento/main.pdf`](Deliverable%204/documento/main.pdf)
- **Adaptadores QLoRA públicos en Hugging Face (`Qwen/Qwen3-4B`, 4-bit NF4, SHA-256 verificado en [`manifest_adaptadores_hf.json`](Deliverable%204/entrenamiento/manifest_adaptadores_hf.json)):**
  - `Enrutador`: [`Pablox0333/qwen3-4b-enrutador-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-enrutador-udec-d4) · rev. `ab65a4f` (A100 `bf16`: `9,88 min`, `eval_loss 1,066 -> 0,123`)
  - `Recuperador`: [`Pablox0333/qwen3-4b-recuperador-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-recuperador-udec-d4) · rev. `6bd665a` (A100 `bf16`: `10,43 min`, `eval_loss 1,729 -> 0,186`)
  - `Redactor`: [`Pablox0333/qwen3-4b-redactor-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4) · rev. [`739b031`](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4/commit/739b031acbd5feef2c49f946b94722712209bce0) (T4 `fp16`: `52,38 min`, `eval_loss 1,601 -> 0,516`)
- **Reproducción limpia (`--solo-hf`) y revisión humana (`50/50`):** verificado en Colab A100 descargando solo desde HF sin Drive ([`comparativa_reproduccion_hf.json`](Deliverable%204/evaluacion/comparativa_reproduccion_hf.json), `7` casos con `H07` en `1` ciclo / `59,91 s`); muestra manual de `50` ejemplos (`30` Redactor + `20` Enr./Rec.) aprobada y firmada el `2026-11-19` en `Deliverable 4/datos/revision_manual_firmas*.csv`.
- **Video en vivo (≤ 3 min):** `[Pendiente: enlace público tras ensayo H07 y grabación]` · guía y notebook en vivo en [`Deliverable 4/video/GUION_VIDEO_D4.md`](Deliverable%204/video/GUION_VIDEO_D4.md) y [`Deliverable 4/D4_colab_video_demo.ipynb`](Deliverable%204/D4_colab_video_demo.ipynb) · [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%204/D4_colab_video_demo.ipynb)
- **Guía completa, datasets antifuga y resultados finales:** [`Deliverable 4/README.md`](Deliverable%204/README.md) · *(la variante previa `Solo Redactor FT v2` quedó respaldada en `backup/d4-solo-redactor`)*

Sobre un único `Qwen/Qwen3-4B` NF4 se conmutan `3` adaptadores QLoRA (`set_adapter()`) entrenados sobre `725` pares (`620 train / 105 val`, `0` coincidencias con las `61` unidades bloqueadas de `D3-75` y `preguntas_nuevas_20.csv`; nota: `01_enrutador.txt` congelado de D3 conserva a `P36` como ejemplo *few-shot* literal donde `3-LoRA` aún falla; asistidos por **Gemini 4 Argon** vía Antigravity / reglas y trayectorias deterministas), manteniendo al `Verificador` aislado con pesos base (`disable_adapter()`, `0` violaciones LoRA en `98/98` llamadas en las `75` y `32/32` en `nuevas_20`). Frente al `Control Base` re-ejecutado en A100 `bf16` (`62/75` en `75`, `11/20` en `nuevas_20`, `73/95` global, `658` / `254` llamadas) y `Solo Redactor v2` (`60/75`, `70/95`), en **`D4 3-LoRA`** McNemar no detectó diferencia de exactitud (**`64/75`** y **`74/95`**, `p=0,73` y `p=1,0`; `-1` en `nuevas_20` con `10/20`) reduciendo las llamadas totales un **`41,0%`** (`658 -> 388`, con `Recuperador` `-69,8%` emitiendo `suficiente` tras la búsqueda inicial en `65/75`, `66/75` incluyendo `P50`) y `53,5%` en `nuevas_20` (`254 -> 118`), aunque solo `-3,7%` en tiempo por el peso del Redactor; las ablaciones `4-LoRA` entrenando al Verificador (`58/75` y `56/75`, aunque `v1` marcó `14/20` en `N20`) confirmaron empíricamente dejarlo en Base. Las trazas de los `11` fallos de `75` están en [`Deliverable 4/evaluacion/casos_fallo_y_regresion_3lora.json`](Deliverable%204/evaluacion/casos_fallo_y_regresion_3lora.json) y las de `nuevas_20` en [`Deliverable 4/evaluacion/trazas_3lora_nuevas20.json`](Deliverable%204/evaluacion/trazas_3lora_nuevas20.json).

---

## Deliverable 3: sistema de cuatro agentes

- **Informe técnico (1 página, LaTeX):** [`Deliverable 3/Deliverable3/documento/main.pdf`](Deliverable%203/Deliverable3/documento/main.pdf)
- **Video (≤ 3 min):** [carpeta pública en Google Drive](https://drive.google.com/drive/folders/1tkhRhI4_G7ArWNHW7zNoeZi8lL9RyPf2?usp=sharing)
- **Demostración en Colab (GPU T4):** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%203/Deliverable3/Demo_D3.ipynb)
- **Guía completa (reproducción, ablaciones, verificación sin GPU):** [`Deliverable 3/README.md`](Deliverable%203/README.md)

El RAG del E2 se reconstruye como cuatro agentes que comparten el mismo Qwen3-4B, cada uno con su prompt versionado
en [`prompts/`](Deliverable%203/Deliverable3/prompts):

| Agente | Decide | Técnica |
|---|---|---|
| Enrutador | Tipo de pregunta y sub-consultas; las premisas falsas con artículo explícito van directo a verificar su existencia | Few-shot |
| Recuperador | En cada turno: buscar, traer un artículo, comprobar si existe o declarar evidencia suficiente | ReAct |
| Redactor | Respuesta, condiciones y fuente a partir de la evidencia; se abstiene si no hay respaldo | Cadena de pensamiento |
| Verificador | Aprobar, devolver al Redactor o pedir al Recuperador que vuelva a buscar | Auto-refinamiento con criterios |

Resultados sobre las mismas 75 entradas y con el mismo criterio de corrección en todas las filas:

| Configuración | 50 originales | 25 difíciles |
|---|---:|---:|
| Prompting directo | 1 | 0 |
| RAG del E2 | 40 | 16 |
| **Agentes (completo)** | **46** | **20** |
| sin few-shot | 44 | 19 |
| sin ReAct | 45 | 18 |
| sin cadena de pensamiento | 46 | 19 |
| sin Verificador | 44 | 19 |

Las diferencias entre ablaciones (como máximo dos preguntas por conjunto) no son estadísticamente significativas.
Las limitaciones conocidas están en [`Deliverable 3/AUDITORIA.md`](Deliverable%203/AUDITORIA.md).

---

## Deliverable 2: Solución RAG Estructurada

- [Guía y documentación de Deliverable 2](Deliverable2/README.md)
- [Informe técnico entregado (1 página LaTeX)](Deliverable2/entrega/Informe_tecnico_D2.pdf) y [fuente](Deliverable2/entrega/Informe_tecnico_D2.tex)
- Cuaderno en Colab: [`Deliverable2_Sistema_RAG_Colab.ipynb`](Deliverable2/notebooks/Deliverable2_Sistema_RAG_Colab.ipynb)
- [Resultados emparejados (100 respuestas evaluadas)](Deliverable2/resultados/qwen3_4b_f0bff499766960f7/REPORTE.md): Baseline 2% vs. RAG estructurado 80%.

---

## Deliverable 1: Diagnóstico y Selección de Modelo

- [Documentación de Deliverable 1](Deliverable1/README.md)
- [Informe técnico entregado](Deliverable1/informe/deliverable1.pdf)
- Diagnóstico de ausencia paramétrica y selección de Qwen/Qwen3-4B frente a modelos alternativos.

---

## Organización del repositorio

| Directorio | Descripción |
|---|---|
| [`Deliverable 4/`](Deliverable%204/README.md) | **Entrega oficial del Deliverable 4 (`3-LoRA`)**: especialización Multi-LoRA (`Enrutador + Recuperador + Redactor`) + `Verificador` en Base, `725` pares antifuga, evaluación pareada A100 (`75` + `20` nuevas), auditoría de fallos, informe LaTeX y demo en vivo. |
| [`Deliverable 3/`](Deliverable%203/README.md) | Entrega del Deliverable 3: arquitectura de 4 agentes, prompts versionados, resultados, ablaciones, informe técnico en LaTeX, cuadernos de Colab y demostración en video. |
| [`Deliverable2/`](Deliverable2/) | Solución RAG del Entregable 2: corpus procesado, índice E5, informe técnico y evaluaciones. |
| [`Deliverable1/`](Deliverable1/) | Entregable 1: diagnóstico, selección de modelo y evaluación zero-shot. |
| [`Corpus/`](Corpus/) | Los tres documentos PDF normativos oficiales de la Universidad de Concepción. |
| [`Archivo/`](Archivo/) | Prototipos históricos conservados con fines de trazabilidad. |

*Nota:* La exploración paralela previa de tres agentes desarrollada durante la investigación se encuentra preservada íntegramente en la rama [`backup/deliverable3_agentes_exploracion`](https://github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/tree/backup/deliverable3_agentes_exploracion).
