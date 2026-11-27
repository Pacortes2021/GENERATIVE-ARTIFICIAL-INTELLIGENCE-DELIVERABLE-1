# Paso 1: Diagnóstico empírico de Deliverable 3 y elección del agente

## 1. Marco de continuidad (D1 → D3 → D4)

En cumplimiento de la rúbrica de Deliverable 4, se mantiene exactamente la misma configuración base heredada de Deliverable 1–3:

- **Tarea:** Preguntas y respuestas normativas sobre el reglamento de pregrado de la Universidad de Concepción / Facultad de Ingeniería (`corpus.json`: `173` padres, `197` unidades y `201` fragmentos de búsqueda).
- **Conjunto de evaluación:** `75` preguntas oficiales distribuidas en `congelado_50` (`50` preguntas) y `dificil_25` (`25` preguntas).
- **Modelo base:** `Qwen/Qwen3-4B` cuantizado en NF4 sobre GPU T4, orquestado en la arquitectura de 4 agentes de D3 (`Enrutador`, `Recuperador`, `Redactor`, `Verificador`).
- **Prompts de partida (`Deliverable 4/prompts/`):** copias verificadas bit a bit de la versión estable v6 de Deliverable 3 (`01_enrutador.txt`, `02_recuperador.txt`, `03_redactor.txt`, `04_verificador.txt`).

Todos los conteos de este documento se reproducen directamente desde las trazas reales mediante [diagnostico_d3.py](../scripts/diagnostico_d3.py) y quedan serializados en [diagnostico_d3.json](./diagnostico_d3.json).

---

## 2. Métricas base de Deliverable 3 (v6)

Sobre las `75` preguntas evaluadas y auditadas manualmente en [veredictos_exportados.json](../../Deliverable%203/auditoria/veredictos_exportados.json):

| Métrica | Valor observado (v6) |
|---|---|
| Exactitud `congelado_50` | **46 / 50 (92,0 %)** |
| Exactitud `dificil_25` | **20 / 25 (80,0 %)** |
| Exactitud global | **66 / 75 (88,0 %)** |
| Primer borrador (`sin_verificador`) | **44 / 50 y 19 / 25 → 63 / 75 (84,0 %)** |
| Llamadas reales al LLM (`decidido_por` vacío) | **711** (**9,48** por pregunta) |
| Desglose de llamadas LLM por agente | `enrutador`: 75 · `recuperador`: 416 · `redactor`: 110 · `verificador`: 110 |
| Eventos totales de traza | **798** (incluye acciones automáticas de código; 0 fallbacks) |
| Distribución de ciclos por consulta | 1 ciclo: **54** · 2 ciclos: **7** · 3 ciclos: **14** |
| Consultas correctas que requirieron reintento (`>1` ciclo) | **17** |
| Rechazos emitidos por el Verificador | **25** hacia `redactor` · **21** hacia `recuperador` |

---

## 3. Radiografía de los 9 errores restantes en D3 v6

Al reconstruir exactamente el ordenamiento de evidencia (`MAX_EVIDENCIA = 6`, pesos `2.0/(r+1)` en búsqueda base, `1.0/(r+1)` en ReAct y `+3.0` por `traer`/`existe`) tal como lo ejecuta [orquestador.py](../../Deliverable%203/Deliverable3/agentes/orquestador.py), verificamos qué unidades estaban presentes en el **top-6** entregado al Redactor en cada fallo:

| Caso | Categoría | ¿Evidencia requerida en top-6? | ¿Unidades de afirmaciones extra en top-6? | Ciclos | Origen raíz | Patrón de fallo observado |
|---|---|---|---|---|---|---|
| `congelado_50:13` | `numerica` | **Sí** (`RI-FI-ART-014`) | **Sí** (`RG-ART-028`) | 1 | **Redactor** | Acierta el umbral (10 créditos), agrega la fórmula del promedio pero cita solo `[RI-FI-ART-014]`; la fórmula está en `[RG-ART-028]`. |
| `congelado_50:24` | `condicional` | **Sí** (`RI-FI-ART-014`) | **Sí** (`RG-ART-028`) | 1 | **Redactor** | Alude vagamente a *"las excepciones mencionadas en el artículo"* sin explicitar PLEV ni primer año de permanencia. |
| `congelado_50:26` | `condicional` | **Sí** (`RI-FI-ART-027`) | **Sí** (`RG-ART-031`, `RG-ART-033`) | 1 | **Redactor** | Confunde el sujeto del plazo de 3 años: afirma que *"la reincorporación puede extenderse por un máximo de tres años"*, cuando ese límite corresponde a la suspensión. |
| `congelado_50:36` | `cruce` | **Sí** (`CAL-2026-S2-01`, `RI-FI-ART-008`) | — | 1 | **Redactor** | Afirma *"No se aplican condiciones o límites adicionales"* y omite las excepciones del mínimo de 8 créditos de `[RI-FI-ART-008]`. |
| `dificil_25:H03` | `multi_salto` | **No** (faltan `CAL-2026-S1-02`, `CAL-2026-S2-02` en top-6) | — | 3 | **Recuperador** | `CAL-2026-S1-02` quedó en el pool fuera del top-6 y `CAL-2026-S2-02` nunca se recuperó. En el ciclo 1 el Redactor alucinó conteos de días; en ciclos 2–3 se abstuvo. |
| `dificil_25:H07` | `calculo` | **Sí** (`RI-FI-ART-014`, `RG-ART-028`) | — | 3 | **Redactor** (+ falso rechazo Verificador) | En el ciclo 1 concluye bien (`10,5 > 10`) pero omite mostrar el cálculo `42 / 4 = 10,5`; el Verificador rechaza y en ciclos 2–3 el Redactor colapsa a una falsa abstención. |
| `dificil_25:H14` | `negacion_excepcion` | **Sí** (`RI-FI-ART-014`, `RG-ART-028`) | — | 2 | **Redactor** | Contradice la respuesta principal frente a pregunta polar: inicia afirmando *"Sí, queda automáticamente en baja académica"* y luego agrega excepciones que niegan el automatismo. |
| `dificil_25:H18` | `sintesis` | **Sí** (`RI-FI-ART-031`) | **Sí** (`RG-ART-033`) | 2 | **Redactor** | En ciclo 1 cita `[RG-ART-033]` y `[RG-ART-003-DEF-19/20]` (truncables por regex), recibe rechazo y en ciclo 2 conserva la condición de 3 años borrando `[RG-ART-033]`. |
| `dificil_25:H25` | `sintesis` | **Sí** (`RI-FI-ART-005`) | — | 1 | **Redactor** | Enumera criterios de selección con `[RI-FI-ART-005]` en puesto #1, pero omite el orden de prelación y el mecanismo de desempate (créditos aprobados y luego promedio curricular). |

### Resumen del cuello de botella

- **8 de los 9 errores finales (88,9 %)** ocurrieron **teniendo toda la evidencia requerida ya cargada en el top-6** del `Redactor`: `congelado_50:13`, `24`, `26`, `36`, `dificil_25:H07`, `H14`, `H18` y `H25`.
- Si observamos además el **primer borrador** sin el bucle de verificación ([ablacion_sin_verificador.md](../../Deliverable%203/Deliverable3/resultados_v6/ablacion_sin_verificador.md)), el Redactor cometió **11 fallos iniciales** (`P25`, `P40`, `H08`, `H12` que el Verificador logró corregir, más `13`, `24`, `26`, `36`, `H14`, `H18`, `H25` que persistieron) y **1 colapso posterior bajo feedback** (`H07`), además de provocar **25 rechazos `Verificador -> Redactor`** y **17 preguntas correctas que necesitaron 2–3 ciclos** para estabilizarse.
- Solo **1 de 9 errores finales (11,1 %, `dificil_25:H03`)** corresponde a evidencia faltante del **Recuperador**. Este caso delimita de antemano qué problema **no** puede resolver por sí solo el fine-tuning del Redactor (si falta una fecha en el contexto, el Redactor debe abstenerse sin inventarla).

---

## 4. ¿Por qué fine-tunear al `Redactor` en vez de seguir ajustando prompts?

La decisión de elegir al agente **`Redactor`** para fine-tuning (manteniendo a `Enrutador`, `Recuperador` y `Verificador` con el modelo base `Qwen/Qwen3-4B`) está respaldada por tres hechos empíricos medidos en D3:

1. **Regresión documentada del prompt v5 sobre el Redactor:** según [prompts/CHANGELOG.md](../../Deliverable%203/Deliverable3/prompts/CHANGELOG.md) y [observaciones_corrida_v5.md](../../Deliverable%203/Deliverable3/resultados_v5/observaciones_corrida_v5.md), cuando en **v5** se editaron `03_redactor.txt` y `04_verificador.txt` intentando corregir exactamente estas fallas (citas precisas, negación de excepciones, desempate), la exactitud **cayó** respecto a v4 (`41/50 → 39/50` en congelado y `17/25 → 16/25` en difícil, bajando de `58/75` a `55/75`), introduciendo regresiones en `P14`, `P27`, `P47–P50`, `H04`, `H12` y `H18`. En **v6** fue necesario **revertir ambos prompts al texto exacto de v4**, y la subida a `66/75` provino únicamente de mejoras de recuperación y orquestación en código.
2. **Techo de instrucciones en 4B (`sin_cot`):** en las ablaciones oficiales sobre las mismas 75 preguntas (`veredictos_exportados.json`), desactivar el razonamiento explícito en el prompt (`sin_cot`: `65/75`) rindió casi igual que el sistema completo (`66/75`). El límite no es falta de reglas escritas en `03_redactor.txt`, sino la fidelidad con que un modelo de 4B parámetros ejecuta simultáneamente lectura estricta, derivación aritmética explícita, enumeración de excepciones y alineación exacta de citas por afirmación.
3. **Impacto directo esperado sobre el sistema completo:** entrenando al `Redactor` mediante QLoRA/LoRA sobre pares `(pregunta, modo, feedback, top-6 de evidencia) -> respuesta rigurosa` atacamos las cinco familias de fallo que concentran **8 de 9 errores finales** y los **reintentos evitables en primer borrador**, dejando intacta la arquitectura multi-agente de D3 para aislar limpiamente el efecto del fine-tuning en el reporte final (D1 vs D2 vs D3 vs D4 + control directo).

> **Nota arquitectónica sobre el `Verificador`:** [AUDITORIA.md](../../Deliverable%203/AUDITORIA.md) registra que el Verificador recibe únicamente los primeros 700 caracteres de cada unidad en `top-6` y no siempre detecta omisiones (`7` aprobaciones incorrectas de `64`), mientras en otros casos rechaza borradores válidos (`H07`). Fortalecer el primer borrador del `Redactor` (mostrando cálculos paso a paso como `42 / 4 = 10,5`, citando cada afirmación en la evidencia exacta y evitando citas de definiciones truncables) reduce tanto errores directos como rechazos evitables del Verificador sin alterar los demás agentes.
