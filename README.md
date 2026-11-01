# Asistente de normativa de pregrado · Ingeniería UdeC

**Álvaro Contreras y Pablo Cortés** · Generative Artificial Intelligence (580694), 2026  
Repositorio oficial: [github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1](https://github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1)

---

## Estado vigente (30 de octubre de 2026)

**Entregable 3 finalizado, auditado y respaldado al 100%**:
1. **450 respuestas en el diseño factorial controlado de GPU (más corridas de validación focalizada)**:
   - **Lote base de 50 preguntas (300 inferencias)**: 6 condiciones experimentales (`baseline_directo`, `rag_d2`, `agentes_completo`, `sin_descomposicion`, `sin_completitud`, `sin_verificacion`).
   - **Conjunto difícil de 25 preguntas H01–H25 (150 inferencias)**: Evaluación factorial completa de las 6 condiciones bajo la misma versión inicial del controlador.
   - **Corridas adicionales de validación**: Ajustes focalizados de consenso semántico (premisas falsas P41–P50) y normalización tipográfica de extractos (H01–H25).
2. **Documento Técnico A4 de 1 página compilado en LaTeX**:
   - PDF oficial: [`Deliverable3_Agentes/entrega/main.pdf`](Deliverable3_Agentes/entrega/main.pdf) (y copia [`Informe_tecnico_D3.pdf`](Deliverable3_Agentes/entrega/Informe_tecnico_D3.pdf)).
   - Fuentes LaTeX: [`Deliverable3_Agentes/entrega/main.tex`](Deliverable3_Agentes/entrega/main.tex) (compilado con Tectonic / pdfLaTeX).
3. **Reproducibilidad y respaldo inmutable**:
   - 25 snapshots ZIP secuenciales preservados en [`Deliverable3_Agentes/conjunto_dificil_25/resultados/`](Deliverable3_Agentes/conjunto_dificil_25/resultados/) y [`Deliverable3_Agentes/resultados/`](Deliverable3_Agentes/resultados/).
   - Cuadernos reproducibles en Google Colab con ejecución por bloques y verificación SHA-256.

---

## Deliverable 3: Arquitectura Multi-Agente y Estudio de Ablación

El Entregable 3 transforma la solución RAG del E2 en un sistema de **tres agentes con decisiones observables**:
- **Investigador**: Descompone preguntas complejas, planifica y recupera evidencia mediante herramientas de lectura (`leer_articulo`), búsqueda densa (`buscar_normativa` con E5) e inventario (`inventario`).
- **Redactor**: Elabora borradores estructurados con citas oficiales ancladas exclusivamente en la evidencia recuperada.
- **Auditor**: Verifica afirmación por afirmación que los extractos coincidan literalmente con la normativa. Si detecta discrepancias, devuelve objeciones al Redactor o solicita investigar; aprueba solo con respaldo riguroso.

### Resultados Empíricos Consolidados (450 respuestas evaluadas)

Evaluación bajo la pauta estricta oficial (`LEEME_PAUTA.md` y criterios D2 en GPU Tesla T4):

| Condición Experimental | Set Base (50) | Sustantivas (P01–40) | Set Difícil (25) | Coste (Llam./q) | Latencia Media |
|---|:---:|:---:|:---:|:---:|:---:|
| **`baseline_directo` (E1)** | 1 / 50 (2,0%) | 1 / 40 (2,5%) | 0 / 25 (0,0%) | 1,0 llam. | 6,7 s |
| **`rag_d2` (E2)** | 40 / 50 (80,0%) | 30 / 40 (75,0%) | 16 / 25 (64,0%) | 1,0 llam. | 15,1 s |
| **`agentes_completo` (Final Normalizado)** | **43 / 50 (86,0%)** | **34 / 40 (85,0%)** | **18 / 25 (72,0%)\*** | **4,5 llam.** | **133,0 s** |
| \quad -- Preliminar (auditor estricto) | 34 / 50 (68,0%) | 34 / 40 (85,0%) | 11 / 25 (44,0%) | 5,1 llam. | 152,3 s |
| **`sin_descomposicion`** | 34 / 50 (68,0%) | 32 / 40 (80,0%) | 14 / 25 (56,0%) | 5,4 llam. | 161,5 s |
| **`sin_completitud`** | 34 / 50 (68,0%) | 33 / 40 (82,5%) | 12 / 25 (48,0%) | 5,2 llam. | 142,1 s |
| **`sin_verificacion`** | 32 / 50 (64,0%) | 31 / 40 (77,5%) | 14 / 25 (56,0%) | 4,9 llam. | 139,2 s |

*Nota metodológica:* En la corrida preliminar factorial, el validador estricto provocó livelock en premisas falsas (0/10) y sobre-cautela léxica en consultas complejas (11/25). Tras implementar la *alineación de parada* y el *consenso semántico* para premisas falsas (alcanzando 9/10 y 43/50 global) junto con la normalización tipográfica del validador de extractos en el conjunto difícil, el sistema multi-agente emitió 21 respuestas aceptadas internamente por el Auditor (84,0%). Bajo la pauta de corrección externa estricta (`LEEME_PAUTA.md`), alcanza un definitivo **18/25 (72,0%)\***, superando a RAG D2 (16/25, 64,0%) por +8,0 pp en razonamiento multi-regla. Las 3 respuestas penalizadas externamente pese a la aceptación interna corresponden a razonamiento aritmético sin división (H07), adición de un plazo no aplicable (H12) y confirmación de fecha engañosa en calendario (H23).

### Hallazgos Clave y Desempeño Comparativo:
1. **Evolución en el Banco Base (Normativa Vigente y Resolución de Premisas Falsas)**: En las 40 preguntas sobre normativa vigente (P01–P40), los agentes superan a RAG D2 por **+10,0 pp (85,0% vs. 75,0%)**, resolviendo 9 de las 10 fallas históricas de D2 (omisiones en P11, P15, P24, P25, P36 y colisiones léxicas en P01, P28, P30, P38). En la corrida preliminar factorial, las 10 preguntas con premisas falsas o artículos inexistentes (P41–P50) fallaban (0/10) debido al bloqueo de reintentos (*livelock*) del Auditor ante hechos negativos, situando el total preliminar en 34/50 (68,0%). Tras implementar la *alineación de parada* (inventario de artículos) y el *consenso semántico* en el orquestador, se resolvieron 9 de las 10 consultas engañosas, elevando el desempeño del sistema completo a **43/50 (86,0%)**.
2. **Resolución de Casos Límite en el Conjunto Difícil**:
   - **H05 y H08 — Cómputo Aritmético de Titulación 60/40 (RI-FI Art. 30)**: RAG D2 falló ambos (0/2) por ausencia de cálculo algebraico ($5,6$ y $4,8$); los agentes **acertaron ambos (2/2)** con cómputo exacto ($5{,}72$ y $4{,}0$).
   - **H01, H14 y H19 — Integración Normativa y Excepciones**: Los agentes resolvieron las 3 consultas (3/3) recuperando la normativa completa frente a fallas de RAG D2 (0/3), que omitió excepciones en H14 y el criterio de pérdida de calidad en H19.
   - **H18 y H25 — Síntesis Normativa y Prelación**: Tanto RAG D2 como los agentes articularon los 36 créditos en H18 y la jerarquía de prelación en H25 (1/1 en ambos), superando al prototipo previo de Álvaro v6 (0/2).
3. **Diagnóstico del Trade-off de Verificación y Distinción Interno vs. Externo**: En la evaluación factorial inicial de las 25 difíciles, cuando `agentes_completo` emitía una respuesta definitiva, su exactitud era del **78,6% (11 de 14)**. Sin embargo, en 11 consultas la rigidez léxica del Auditor provocó ciclos de objeción que agotaron el presupuesto operativo (6 por `limite_salidas_invalidas` y 5 por `limite_llamadas`), forzando abstenciones técnicas y situando el resultado preliminar en **11/25 (44,0%)**. Al retirar la verificación estricta (`sin_verificacion`), el sistema aumentó la emisión y alcanzó **14/25 aciertos (56,0%)**, al igual que `sin_descomposicion` (14/25, 56%). Posteriormente, con la normalización del validador de extractos en la corrida final ajustada, el Auditor aceptó internamente **21/25 respuestas (84,0%)** con 4 abstenciones técnicas presupuestarias. Al contrastar con la pauta externa estricta, se consolidan **18/25 aciertos (72,0%)**, evidenciando que la deliberación multi-agente supera a RAG D2 (64,0%) reduciendo alucinaciones complejas pero requiriendo supervisión en la inferencia de plazos cruzados.

Para más detalles, consultar el [Reporte Final del Conjunto Difícil de 25](Deliverable3_Agentes/conjunto_dificil_25/resultados/reporte_final_dificiles_25.md).

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

## Organización del Repositorio

| Directorio | Descripción |
|---|---|
| [`Deliverable3_Agentes/`](Deliverable3_Agentes/) | Implementación vigente de agentes: controlador, prompts versionados, herramientas, cuadernos y resultados. |
| [`Deliverable3_Agentes/entrega/`](Deliverable3_Agentes/entrega/) | **Documento técnico oficial de 1 página**: [`main.pdf`](Deliverable3_Agentes/entrega/main.pdf) / [`main.tex`](Deliverable3_Agentes/entrega/main.tex), guion de video y trazas. |
| [`Deliverable3_Agentes/conjunto_dificil_25/`](Deliverable3_Agentes/conjunto_dificil_25/) | Set de 25 preguntas difíciles: [`reporte_final_dificiles_25.md`](Deliverable3_Agentes/conjunto_dificil_25/resultados/reporte_final_dificiles_25.md), 150 JSONs y 25 respaldos ZIP. |
| [`Deliverable2/`](Deliverable2/) | Solución RAG del Entregable 2: corpus procesado, índice E5, informe técnico y evaluaciones. |
| [`Deliverable1/`](Deliverable1/) | Archivos originales del Entregable 1: diagnóstico, selección y evaluación zero-shot. |
| [`Corpus/`](Corpus/) | Los tres documentos PDF normativos oficiales de la Universidad de Concepción. |
| [`Archivo/`](Archivo/) | Prototipos históricos conservados con fines de trazabilidad. |
