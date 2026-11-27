# Reporte de Experimentos y Descubrimientos — Asistente Local UdeC (`8 GB RAM`)

Este documento consolida todas las iteraciones, técnicas probadas, experimentos descartados y mediciones empíricas sobre las **95 preguntas** (`congelado_50`, `dificil_25` y `nuevas_20`) realizadas fuera de la pauta multi-agente de los Deliverables oficiales, respetando siempre el límite de **8 GB de RAM** del Mac (`Qwen3-4B-Instruct-2507` `Q4_K_M`, `num_ctx=4096`, `num_predict=1024`, `repeat_penalty=1.05`, ejecución secuencial en Ollama).

> [!NOTE]
> Las ramas oficiales de entrega (`deliverable-4` @ `cbac0bd`, `main` @ `3c3b97c`) permanecieron **100 % intactas** durante toda esta exploración.

---

## 1. Mapa de ramas y evolución cronológica

| Rama | Commit | Estado | Qué aporta |
| :--- | :--- | :--- | :--- |
| `deliverable-4` | `cbac0bd` | Intacta 🔒 | Entrega oficial D4 (`3-LoRA` multi-agente en Colab A100: `74/95 = 77,9%`). |
| `feat/asistente-local` | `9ab3d6e` | Estable 🔒 | Primer agente único local en Ollama con herramientas Python (`calcular`, `dias_entre`), `Top-p (85%)` y fusión lineal E5+léxico. |
| `exp/rag-avanzado` | `2d636a2` | Verificada ✅ | Investigación open-source aplicada: `BM25 + E5` con **`RRF`**, descomposición determinista de subconsultas, reescritura multi-turno, reparación de `solo_citas`, evaluador RAGAS local. |
| `exp/asistente-pro` | `4ee5896` | Verificada ✅ | Producto Streamlit (PDFs propios en caliente en caché SHA-256, historial persistente + export `.md`, botón Self-RAG opcional) + verificación determinista previa de artículos inexistentes por documento (`C50 #42`). |
| *`exp/reranker`* | *(eliminada)* | ❌ Descartado | Prueba controlada de Cross-Encoder (`mmarco-mMiniLMv2-L12-H384-v1`); causó OOM en MPS, `683,9 ms/q` en CPU vs `15,4 ms/q` RRF y peor MRR (`0.8476` vs `0.8974`). |
| `exp/finetune-agente` | `dd7ae56` | ❌ SFT superado | QLoRA SFT (`udec-agente:4b-ft`, 92 ejemplos antifuga en T4). Duplicó velocidad (~17 s/q) pero sobreajustó tool-calling (`H03`: `calcular("42 / 4")`, `H06`: `9,5 > 10`) bajando a `14/20 (70%)` en `nuevas_20`. |
| **`exp/dpo-agente`** | **Actual 🌟** | **Ganador 🏆** | **DPO Split-Backward QLoRA (`udec-agente:4b-dpo`, 62 pares antifuga `chosen` vs `rejected` en T4).** Recuperó 100% las herramientas y alcanzó **`90/95 (94,7%)`** y **`0.833`** promedio en RAGAS Faithfulness (`+10,8 pts` vs Base). |

---

## 2. Comparativa Única: Deliverables (`D1–D4`) vs. Asistente Local (`95 preguntas`)

Las columnas de aciertos corresponden a revisión directa respuesta por respuesta contra la pauta oficial (`gold_dato` + `gold_fuente`, sin inventar citas). Los archivos fuente de las corridas locales viven en [`asistente_local/resultados/`](./resultados).

| Etapa / Sistema | Entorno | Congelado (50) | Difíciles (25) | Nuevas ciegas (20) | **Total Global (95)** | Velocidad promedio |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **D1 Baseline original** *(sin docs)* | Colab T4 | `2 / 50` (4,0%) | — | — | — | — |
| **D2 RAG básico (E5, T=0.7)** | Colab T4 | `40 / 50` (80,0%) | `16 / 25` (64,0%) | — | — | `~16,9 s/preg` *(en 75)* |
| **D3 Multi-agente v6 Base** *(4 agentes)* | Colab T4 | `46 / 50` (92,0%) | `20 / 25` (80,0%) | — | — | `110,1 s/preg` *(en 75)* |
| **D4 Control Base** *(= D3 v6, LoRA OFF)* | Colab A100 | `46 / 50` (92,0%) | `16 / 25` (64,0%) | `11 / 20` (55,0%) | `73 / 95` (76,8%) | `68,3 s/preg` |
| **D4 Oficial (`3-LoRA`)** | Colab A100 | `46 / 50` (92,0%) | `18 / 25` (72,0%) | `10 / 20` (50,0%) | `74 / 95` (77,9%) | `64,9 s/preg` |
| Local **SFT** (`udec-agente:4b-ft`) | Mac 8 GB | — | `21 / 25` (84,0%) | `14 / 20` (70,0%) | — | `17,2 s/preg` *(en 45)* |
| Local **Base** (`qwen3:4b-instruct` + `RRF`) | Mac 8 GB | `46 / 50` (92,0%) | `24 / 25` (96,0%) | `18 / 20` (90,0%) | `88 / 95` (92,6%) | `26,1 s/preg` |
| **🏆 Local DPO (`udec-agente:4b-dpo`)** | **Mac 8 GB** | **`48 / 50` (96,0%)** | **`24 / 25` (96,0%)** | **`18 / 20` (90,0%)** | **`90 / 95` (94,7%)** | **`24,8 s/preg`** |

> [!NOTE]
> Si en `dificil_25:H17` se penaliza la cita secundaria de apoyo (`Art. 20° RI-FI` en Base y `[RI-FI-ART-013]` al citar INCLUDEC en DPO, aunque ambos aciertan la regla principal del 80%/100%), el resultado estricto queda en `23/25` (`87/95 = 91,6%` Base y **`89/95 = 93,7%` DPO**). Además, la corrida `final_congelado50` del Base ocurrió justo antes del parche `4ee5896` para `C50 #42`; ya con DPO las 4 trampas inexistentes `#41–#44` llamaron correctamente `existe_articulo`.

### ¿Por qué el Local DPO superó por `+21,3 pts` a D2 (`74,7% → 96,0%` en 75) y por `+16,8 pts` a D4 (`77,9% → 94,7%`)?
1. **Cero aritmética/fechas "al ojo":** En D2, el modelo sacó **`0/5`** en cálculos y fechas de `dificil_25` (`H03` inventó fechas `01 feb / 01 jul`; `H05` respondió `5,6` en vez de `5,72`; `H08` respondió `4,8` en vez de `4,0`; `H07` comparó `42` contra `10` sin dividir por 4). Con `calcular` + `dias_entre`, el local pasó a `4/5` en DPO.
2. **Arquitectura de 1 solo agente con búsqueda limpia (`BM25 + E5 RRF + Top-p 85%`):** Eliminó el efecto "teléfono descompuesto" entre 4 agentes (donde el Verificador base rechazaba cálculos correctos como `H07` en D4 o los cortes prematuros del Recuperador cortaban preguntas compuestas).
3. **Modelo `Instruct-2507` determinista (`T=0.0`) + alineamiento DPO:** Dejó atrás el `T=0.7` ruidoso y la plantilla rígida de 3 líneas de D2 que forzaba alucinaciones en `P15, P24, P25, P28, P30, P38`.

---

## 3. Métricas Automáticas y Juez RAGAS (`evaluador.py`)

| Experimento / Modelo | Dataset | Recall Contexto | Recall Citas | Respaldo Léxico | Cob. Numérica | Citas Falsas | **Faithfulness LLM** *(10 m.)* | Seg/preg | Archivo en `resultados/` |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `9ab3d6e` (`Top-p 85%` lineal) | `nuevas_20` | — | `0.867` | `0.654` | `0.796` | `0` | — | `40.50 s` | `benchmark_nuevas_20_topp85_lineal_9ab3d6e.json` |
| `exp/rag-avanzado` (`RRF`) | `nuevas_20` | `1.000` | **`0.983`** | `0.681` | **`0.892`** | `0` | `0.793` | `36.92 s` | `benchmark_nuevas_20_rrf_qwen3_4b-instruct.json` |
| `abl2_verif` (Base + Verif. auto) | `nuevas_20` | `1.000` | `0.933` | `0.673` | **`0.892`** | `0` | **`0.810`** | `36.92 s` *(+111.3s tot)* | `benchmark_nuevas_20_abl_verificador_4b.json` |
| SFT (`udec-agente:4b-ft`) | `nuevas_20` | `1.000` | `0.938` | **`0.844`** | `0.687` | `0` | `0.617` | **`18.06 s`** | `benchmark_nuevas_20_udec-agente_4b-ft.json` |
| **DPO (`udec-agente:4b-dpo`)** | `nuevas_20` | `1.000` | `0.921` | `0.736` | `0.779` | `0` | `0.750` | `32.77 s` | `benchmark_nuevas_20_udec-agente_4b-dpo.json` |
| `exp/rag-avanzado` (`RRF`) | `dificil_25` | `1.000` | `0.880` | `0.667` | `0.625` | `0` | — | `28.65 s` | `benchmark_dificil_25_rrf_qwen3_4b-instruct.json` |
| `abl2_verif` (Base + Verif. auto) | `dificil_25` | `1.000` | `0.880` | `0.677` | `0.625` | `0` | `0.683` | `28.65 s` *(+122.1s tot)* | `benchmark_dificil_25_abl_verificador_4b.json` |
| SFT (`udec-agente:4b-ft`) | `dificil_25` | `1.000` | **`0.900`** | **`0.797`** | `0.386` | `0` | `0.796` *(9/10 parse)* | **`16.43 s`** | `benchmark_dificil_25_udec-agente_4b-ft.json` |
| **DPO (`udec-agente:4b-dpo`)** | `dificil_25` | `1.000` | `0.880` | `0.729` | **`0.644`** | `0` | **`0.933`** | `30.25 s` | `benchmark_dificil_25_udec-agente_4b-dpo.json` |
| Base (`qwen3:4b-instruct` `RRF`) | `congelado_50` | `0.910` | `0.880` | `0.692` | `0.752` | `0` | `0.683` | `20.43 s` | `benchmark_congelado_50_rrf_qwen3_4b-instruct.json` |
| **DPO (`udec-agente:4b-dpo`)** | `congelado_50` | `0.910` | **`0.890`** | **`0.714`** | **`0.798`** | `0` | **`0.817`** | **`18.88 s`** | `benchmark_congelado_50_udec-agente_4b-dpo.json` |

---

## 4. Qué probamos, qué funcionó y qué falló (lecciones técnicas)

### Lo que SÍ ganó y se conserva
1. **`BM25 + E5` con `RRF` (`k_rrf = 10`) + `Top-p (85%)`:** Reemplazó la suma lineal (`0.65 E5 + 0.35 léxico`) que sufría de escalas descalibradas. Sube la recuperación a `100%` en `dificil_25` y `nuevas_20`, y baja la latencia porque el modelo no duda haciendo búsquedas redundantes.
2. **Descomposición determinista (`descomponer_subconsultas`) + reescritura multi-turno:** Divide preguntas 2-en-1 por conectores en Python (`0 s` extra de LLM) y resuelve `N19` (`RG-ART-018` + `RG-ART-036`) al 100%.
3. **Verificación determinista previa (`verificar_articulos_mencionados`) + reparación `solo_citas`:** Previene falsas atribuciones cuando el usuario consulta por un artículo fuera del rango del documento (`C50 #42`).
4. **DPO Split-Backward QLoRA (`udec-agente:4b-dpo`):**
   - *Por qué venció al SFT:* En lugar de forzar imitación ciega sobre respuestas sueltas, entrenó 62 pares contrastivos (`chosen` vs `rejected`, `beta=0.1`, `lambda_nll=0.05`, `lr=1e-5`, 3 épocas, 0 fugas respecto a las 61 unidades y 95 preguntas evaluadas).
   - *Ingeniería en T4 (15 GB):* Precomputa `ref_logps` en una pasada `no_grad` inicial (`0 MB` extra de modelo de referencia en VRAM) y desacopla los `.backward()` de `chosen` y `rejected` conservando el gradiente matemático exacto (verificado en CPU en `test_paridad_exacta_gradiente_split_backward_vs_simultaneo`).
   - *Ganancias reales sobre Base local:* Rescató `P25` (identifica asignaturas atrasadas y reprobadas), `N08` (`RG-ART-046`), `N09` (respuesta completa vs solo cita), `H07` (`42/4 = 10.5` donde Base dividía `42/1`), y las 4 trampas `#41–#44`.

### Lo que NO ganó (descartado con evidencia)
1. **Verificador automático 4B (`CRAG / Self-RAG`):** Corregía 1 caso (`H04`), pero introducía falsos positivos de corrección de un juez del mismo tamaño (rompió `N08`) sumando `+111–122 s` extra por lote. Se conservó únicamente como **botón bajo demanda en Streamlit** (`🔎 Verificar fidelidad`).
2. **Cross-Encoder Reranker (`mmarco-mMiniLMv2-L12-H384-v1`):**
   - Causó **OOM en Apple MPS** (`6.09 GB + 3.04 GB > 9.07 GB` en Mac 8 GB).
   - En CPU tardó **`683,9 ms/consulta`** frente a **`15,4 ms/consulta`** de `RRF`.
   - Degradó recuperación sobre 82 consultas: `RRF Top-p` (`R@3 = 72/82`, `R@k = 76/82`, `MRR = 0.8974`) venció a `mmarco` (`R@3 = 67/82`, `R@k = 70/82`, `MRR = 0.8476`).
3. **SFT puro (`udec-agente:4b-ft`):** Logró `eval_loss: 1.5326 -> 0.5158` en 54 pasos (`~17 s/preg`), pero provocó colapso de tool-calling en fechas (`H03`: `calcular("42 / 4")`), inversión de desigualdades (`H06`: `9.5 > 10`) y caída en RAGAS Faithfulness (`0.617` en `nuevas_20`).

### Los 5 tropiezos residuales de `udec-agente:4b-dpo` (de 95)
1. **`H06` *(contradicción con `think=False`)*:** Respondió *"No."* en la primera línea antes de dividir `38 / 4 = 9.5`, corrigiéndose al final del mismo texto (*"sí cae en baja académica"*).
2. **`N16`:** Confundió los días `18–19 de mayo` (*sin evaluaciones*) con *feriado nacional*.
3. **`N05`:** Explicó correctamente el Art. 6° pero citó `[RI-FI-ART-005]` al cierre en lugar de `[RI-FI-ART-006]`.
4. **`#40`:** Citó `RI-FI-ART-029` y el `40%`, omitiendo el nombre literal *"Reglamento de Memoria de Título"*.
5. **`#49`:** Confirmó que el 18 de septiembre es feriado y el 30 no, pero contradijo brevemente diciendo *"el único feriado es el 20 de agosto"*.

---

## 5. Siguientes pasos recomendados en producto
- **`config.py` / `app.py`:** actualmente `ConfigAsistente.modelo` sigue en `"qwen3:4b-instruct"`. Para usar al campeón en la web basta promover `"udec-agente:4b-dpo"` como predeterminado (o añadir selector en la barra lateral).
- **Aplicaciones reales locales en 8 GB:** más allá de visión/OCR (donde un modelo en la nube como Gemini es superior), el sistema local destaca en un **Simulador de Situación Académica UdeC** (diagnóstico de baja/titulación/plazos reales en Python + DPO), búsqueda permanente en **carpetas privadas de tesis/ramos** 100% offline, o **CLI / bot** sin costo por token.
