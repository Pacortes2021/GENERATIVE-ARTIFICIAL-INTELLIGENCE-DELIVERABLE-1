# Asistente de normativa de pregrado · Ingeniería UdeC

**Álvaro Contreras y Pablo Cortés** · Generative Artificial Intelligence (580694), segundo semestre 2026

El sistema responde preguntas en español sobre la normativa de pregrado de la Facultad de Ingeniería de la UdeC
(Reglamento General, Reglamento Interno FI y Calendario 2026) con el dato exacto y la cita que lo respalda, y se
abstiene cuando la información no existe o la pregunta parte de una premisa falsa. Todas las entregas usan
**Qwen/Qwen3-4B** (cuantizado a 4 bits NF4 desde el Deliverable 2; T4 `float16` en D1–D3 y entrenamiento D4, y **A100 `bf16`** en la evaluación comparativa v2 de D4).

| Entrega | Carpeta | Informe | Resultado principal |
|---|---|---|---|
| **Deliverable 4 · fine-tuning del Redactor** | [`Deliverable 4/`](Deliverable%204/README.md) | [PDF](Deliverable%204/documento/main.pdf) | Corrida v2 (A100 `bf16`): `43/50` + `17/25` (`60/75`) vs Control Base `62/75` (`46+16`); `10/20` vs `11/20` en `nuevas_20` |
| Deliverable 3 · sistema de agentes | [`Deliverable 3/`](Deliverable%203/README.md) | [PDF](Deliverable%203/Deliverable3/documento/main.pdf) | 46/50 y 20/25 (RAG del E2: 40/50 y 16/25) |
| Deliverable 2 · RAG estructurado | [`Deliverable2/`](Deliverable2/README.md) | [PDF](Deliverable2/entrega/Informe_tecnico_D2.pdf) | 40/50 (baseline directo con la misma configuración: 1/50) |
| Deliverable 1 · diagnóstico y modelo | [`Deliverable1/`](Deliverable1/README.md) | [PDF](Deliverable1/informe/deliverable1.pdf) | Baseline directo 2/50 (decodificación greedy): ausencia paramétrica |

---

## Deliverable 4: especialización QLoRA del agente Redactor

- **Informe técnico (1 página, LaTeX):** [`Deliverable 4/documento/main.pdf`](Deliverable%204/documento/main.pdf)
- **Adaptador público en Hugging Face:** [`Pablox0333/qwen3-4b-redactor-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4) *(pesos v2, commit [`739b031`](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4/commit/739b031acbd5feef2c49f946b94722712209bce0), entrenados en T4 `float16`: `52,38 min`, `eval_loss 1,6006 -> 0,5164`, `0` ejemplos truncados)*
- **Video en vivo (≤ 3 min):** `[Pendiente: enlace público tras grabación]` · guía y notebook en vivo en [`Deliverable 4/video/GUION_VIDEO_D4.md`](Deliverable%204/video/GUION_VIDEO_D4.md) y [`Deliverable 4/D4_colab_video_demo.ipynb`](Deliverable%204/D4_colab_video_demo.ipynb)
- **Guía completa, datos v2 y resultados finales:** [`Deliverable 4/README.md`](Deliverable%204/README.md)

Se entrena un adaptador QLoRA (`NF4`, `r=16`, `alpha=32`, 210 pares supervisados `180 train / 30 val`, `74/210` ejemplos `"No aplica"` curados con asistencia de Antigravity y `0%` solapamiento de unidades frente a evaluación y al set ciego `preguntas_nuevas_20.csv`) **solo para el agente `Redactor`**, manteniendo congelado a `Qwen/Qwen3-4B` vía `model.disable_adapter()` en `Enrutador`, `Recuperador` y `Verificador` (`0` violaciones LoRA en `100` llamadas ON / `548` OFF, `max_abs_logit_diff = 13.5625`). En la evaluación completa sobre A100 `bf16` con auditoría estricta y simétrica bajo [`LEEME_PAUTA.md`](Deliverable%203/paquete_25_dificiles/LEEME_PAUTA.md), el pipeline FT v2 obtiene **`60/75` (`80,0%`; `62/75 = 82,7%` en núcleo de respuesta)** con **`-8,86%` llamadas LLM (`648` vs `711` en D3)** y **`0` fallbacks** frente a **`62/75` (`82,7%`, `658` llamadas)** del Control Base A100 (`FT` vence en `6` casos y Control Base en `8`, balance neto **`-2`**, aunque en la submuestra pareada de `6` casos diagnósticos D3 `FT` marca **`4/6 vs 2/6`**); en `nuevas_20` marca **`10/20` (`50,0%`) vs `11/20` (`55,0%`)** (`2/3 vs 1/3` en divergencias directas, con `-16,5%` llamadas y `-23,7%` latencia). El análisis de causa raíz —incluyendo la degradación de borradores válidos por el `Verificador` base (`H22` en las 75 y `N05` en `nuevas_20`, más `H21` mixto) y los fallos mixtos `Redactor + Verificador` (`H04, H06`)— se documenta en [`Deliverable 4/evaluacion/casos_fallo_y_regresion.json`](Deliverable%204/evaluacion/casos_fallo_y_regresion.json) (75 oficiales) y [`Deliverable 4/evaluacion/casos_revision_nuevas20_ft_D4.json`](Deliverable%204/evaluacion/casos_revision_nuevas20_ft_D4.json) (`nuevas_20`). Pendiente únicamente registrar las firmas humanas en `datos/revision_manual_firmas.csv` + VoBo de auditoría de Álvaro Contreras y grabar el video antes del merge final a `main`.

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
| [`Deliverable 4/`](Deliverable%204/README.md) | **Entrega oficial del Deliverable 4**: fine-tuning QLoRA exclusivo del agente `Redactor`, dataset antifuga, adaptador Hugging Face, evaluación aislada sobre 75 preguntas, auditoría de fallos, informe LaTeX y demo Base vs Fine-tuned. |
| [`Deliverable 3/`](Deliverable%203/README.md) | Entrega del Deliverable 3: arquitectura de 4 agentes, prompts versionados, resultados, ablaciones, informe técnico en LaTeX, cuadernos de Colab y demostración en video. |
| [`Deliverable2/`](Deliverable2/) | Solución RAG del Entregable 2: corpus procesado, índice E5, informe técnico y evaluaciones. |
| [`Deliverable1/`](Deliverable1/) | Entregable 1: diagnóstico, selección de modelo y evaluación zero-shot. |
| [`Corpus/`](Corpus/) | Los tres documentos PDF normativos oficiales de la Universidad de Concepción. |
| [`Archivo/`](Archivo/) | Prototipos históricos conservados con fines de trazabilidad. |

*Nota:* La exploración paralela previa de tres agentes desarrollada durante la investigación se encuentra preservada íntegramente en la rama [`backup/deliverable3_agentes_exploracion`](https://github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/tree/backup/deliverable3_agentes_exploracion).
