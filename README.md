# Asistente de normativa de pregrado · Ingeniería UdeC

**Álvaro Contreras y Pablo Cortés** · Generative Artificial Intelligence (580694), segundo semestre 2026

El sistema responde preguntas en español sobre la normativa de pregrado de la Facultad de Ingeniería de la UdeC
(Reglamento General, Reglamento Interno FI y Calendario 2026) con el dato exacto y la cita que lo respalda, y se
abstiene cuando la información no existe o la pregunta parte de una premisa falsa. Todas las entregas usan
**Qwen/Qwen3-4B** en 4 bits sobre una GPU T4 de Google Colab.

| Entrega | Carpeta | Informe | Resultado principal |
|---|---|---|---|
| Deliverable 3 · sistema de agentes | [`Deliverable 3/`](Deliverable%203/README.md) | [PDF](Deliverable%203/Deliverable3/documento/main.pdf) | 46/50 y 20/25 (RAG del E2: 40/50 y 16/25) |
| Deliverable 2 · RAG estructurado | [`Deliverable2/`](Deliverable2/README.md) | [PDF](Deliverable2/entrega/Informe_tecnico_D2.pdf) | 40/50 (baseline directo: 1/50) |
| Deliverable 1 · diagnóstico y modelo | [`Deliverable1/`](Deliverable1/README.md) | [PDF](Deliverable1/informe/deliverable1.pdf) | Baseline directo 2/50: ausencia paramétrica |

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
| [`Deliverable 3/`](Deliverable%203/README.md) | **Entrega del Deliverable 3**: agentes, prompts, resultados, ablaciones, informe, cuadernos de Colab y evidencia del video. |
| [`Deliverable2/`](Deliverable2/) | Solución RAG del Entregable 2: corpus procesado, índice E5, informe técnico y evaluaciones. |
| [`Deliverable1/`](Deliverable1/) | Entregable 1: diagnóstico, selección de modelo y evaluación zero-shot. |
| [`Corpus/`](Corpus/) | Los tres documentos PDF normativos oficiales de la Universidad de Concepción. |
| [`Deliverable3_Agentes/`](Deliverable3_Agentes/README.md) | Exploración alternativa de tres agentes desarrollada en paralelo. **No es la versión entregada**; se conserva con sus resultados como registro. |
| [`Archivo/`](Archivo/) | Prototipos históricos conservados con fines de trazabilidad. |
