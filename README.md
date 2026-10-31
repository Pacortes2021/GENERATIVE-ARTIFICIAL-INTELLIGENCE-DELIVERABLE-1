# Asistente de normativa de pregrado · Ingeniería UdeC

**Álvaro Contreras y Pablo Cortés** · Generative Artificial Intelligence (580694), 2026  
Repositorio oficial: [github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1](https://github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1)

---

## Estado vigente (30 de octubre de 2026)

**Entregable 3 finalizado, auditado y respaldado al 100%**:
1. **450 respuestas evaluadas en GPU Tesla T4 (Qwen/Qwen3-4B en NF4)**:
   - **Lote base de 50 preguntas (300 inferencias)**: 6 condiciones experimentales (`baseline_directo`, `rag_d2`, `agentes_completo`, `sin_descomposicion`, `sin_completitud`, `sin_verificacion`).
   - **Conjunto difícil de 25 preguntas H01–H25 (150 inferencias)**: Evaluación factorial completa y auditoría de casos complejos de borde.
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

Evaluación bajo la pauta estricta oficial (`LEEME_PAUTA.md` y criterios D2):

| Condición Experimental | Set Base (50) | Sustantivas (P01–40) | Set Difícil (25) | Coste (Llam./q) | Latencia Media |
|---|:---:|:---:|:---:|:---:|:---:|
| **`baseline_directo` (E1)** | 1 / 50 (2,0%) | 1 / 40 (2,5%) | 0 / 25 (0,0%) | 1,0 llam. | 6,7 s |
| **`rag_d2` (E2)** | 40 / 50 (80,0%) | 30 / 40 (75,0%) | 16 / 25 (64,0%) | 1,0 llam. | 15,1 s |
| **`agentes_completo`** | **34 / 50 (68,0%)** | **34 / 40 (85,0%)** | **11 / 25 (44,0%)** | 5,1 llam. | 152,3 s |
| **`sin_descomposicion`** | 34 / 50 (68,0%) | 32 / 40 (80,0%) | 14 / 25 (56,0%) | 5,4 llam. | 161,5 s |
| **`sin_completitud`** | 34 / 50 (68,0%) | 33 / 40 (82,5%) | 12 / 25 (48,0%) | 5,2 llam. | 142,1 s |
| **`sin_verificacion`** | 32 / 50 (64,0%) | 31 / 40 (77,5%) | 14 / 25 (56,0%) | 4,9 llam. | 139,2 s |

### Hallazgos Clave y Desempeño Comparativo:
1. **Compensación en el Banco Base (Normativa Vigente vs. Premisas Falsas)**: En las 40 preguntas sobre normativa vigente (P01–P40), los agentes superan a RAG D2 por **+10,0 pp (85,0% vs. 75,0%)**, resolviendo 9 de las 10 fallas históricas de D2 (omisiones en P11, P15, P24, P25, P36 y colisiones léxicas en P01, P28, P30, P38). En cambio, en las 10 preguntas con premisas falsas o artículos inexistentes (P41–P50), los agentes fallan en todas (0/10 vs. 10/10 en D2) debido al sesgo exploratorio del bucle deliberativo que intenta responder forzando asociaciones en vez de aplicar una abstención temprana como el filtro estático de D2, situando el total del banco base en 34/50 (68,0%).
2. **Resolución de Casos Límite en el Conjunto Difícil**:
   - **H18 (P118) — Suspensión > 3 años en memoristas (RI-FI Art. 31)**: Identifica con precisión la excepción del tope de 36 créditos en asignaturas fijadas por el Comité (1/1).
   - **H25 (P125) — Criterios de prelación en Plan Común (RI-FI Art. 5)**: Articula la prelación jerárquica completa (1° créditos aprobados $\rightarrow$ 2° promedio curricular ponderado con dos decimales $\rightarrow$ 3° cupos y preferencias).
   - **H05 y H08 — Cómputo Aritmético de Titulación 60/40 (RI-FI Art. 30)**: RAG D2 falló ambos (0/2) por ausencia de cálculo; los agentes **acertaron ambos (2/2)** con desglose algebraico exacto ($0{,}6 \times \text{plan} + 0{,}4 \times \text{memoria}$).
3. **Diagnóstico del Trade-off de Verificación**: Cuando `agentes_completo` emite una respuesta definitiva, su exactitud es del **78,6% (11 de 14)**. Sin embargo, en 11 consultas la rigidez léxica del Auditor frente a las limitaciones de paráfrasis del modelo 4B provocó ciclos de objeción que agotaron el presupuesto operativo (6 por `limite_salidas_invalidas` y 5 por `limite_llamadas`), forzando abstenciones técnicas con puntaje 0. Al retirar la verificación estricta (`sin_verificacion`), el sistema aumentó la emisión y alcanzó **14/25 aciertos (56,0%)**, al igual que `sin_descomposicion` (14/25, 56%).

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
