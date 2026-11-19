# Guion de Video Demostrativo — Deliverable 4 (<= 3 minutos)

**Proyecto:** Especializacion Multi-LoRA por rol (`Enrutador + Recuperador + Redactor` + `Verificador` en Base) sobre `Qwen/Qwen3-4B` en normativa academica UdeC.  
**Participantes:** Alvaro Contreras y Pablo Cortes.  
**Notebook de ejecucion en vivo (Colab):** `Deliverable 4/D4_colab_video_demo.ipynb` (respaldo offline en `video/mostrar_demo_d4.py`).

---

## Estructura cronometrada (objetivo 2:45 – 2:55)

### 0:00 – 0:25 | Contexto, evolucion D1->D3 y por que entrenamos 3 adaptadores LoRA
- **En pantalla:** Pagina 1 de `documento/main.pdf` (Seccion 1 + grafo TikZ de la Seccion 2).
- **Que decir (lenguaje directo):**
  - En D3 teniamos 4 agentes usando todos `Qwen/Qwen3-4B` sin entrenar (`66/75` en T4, con `711` llamadas al modelo).
  - En A100 `bf16`, ese mismo sistema Control Base marco **`62/75`** (`658` llamadas) y entrenar **solo al Redactor (`v2`)** bajo a **`60/75`** (`648` llamadas) porque las trazas mostraban un cuello de botella de **eficiencia** en el pipeline previo (`373` llamadas solo en el Recuperador).
  - Por eso armamos **D4 `3-LoRA`**: un **unico modelo base en 4 bits (NF4)** con `3` adaptadores especializados (`Enrutador`, `Recuperador`, `Redactor`) activados segun turno con `set_adapter()`, manteniendo al **Verificador** con pesos base limpios via `disable_adapter()`.

### 0:25 – 0:50 | Datos antifuga y entrenamiento separado de los 3 roles
- **En pantalla:** Tabla de datasets + grafica `entrenamiento/loss_curves_3agentes.png` en el PDF.
- **Que decir:**
  - `725` ejemplos independientes (`620` train / `105` val) sobre articulos completamente disjuntos de las `75` preguntas oficiales y las `20` nuevas (`0%` fuga de datos).
  - Los 3 adaptadores convergieron con **0 ejemplos truncados**: Enrutador (`eval_loss 1,066 -> 0,123`), Recuperador (`1,729 -> 0,186`) y Redactor (`1,601 -> 0,516`).

### 0:50 – 1:55 | Demostracion en vivo: Control Base (`LoRA OFF`) vs D4 `3-LoRA` (`H07`)
- **En pantalla:** Celdas 2 y 3 de `Deliverable 4/D4_colab_video_demo.ipynb` ejecutando `H07` en vivo desde Hugging Face (mostrando arriba `verificar_aislamiento_multi_lora()`).
- **Pregunta H07:** *"Un estudiante aprobo 42 creditos al termino de su cuarto semestre. ¿Esta en baja academica por el criterio de promedio de creditos del Articulo 14?"*
- **Lo que se ve en la ejecucion:**
  - **Control Base (`LoRA OFF` en los 4 agentes):** cae en **3 ciclos**, **13 llamadas LLM** y **`177,4 s`**. En el ciclo 2 el Redactor Base incluso llega a responder bien (`10,5 > 10`), **pero el Verificador Base lo rechaza falsamente** (*"la evidencia no respalda este calculo"*) y empuja el ciclo 3 a una **abstencion falsa**.
  - **D4 `3-LoRA`:**
    1. `[Enrutador · LoRA ON]` clasifica como `numerica`.
    2. `[Recuperador · LoRA ON]` evalua los 5 hits iniciales (`RI-FI-ART-014`, `RG-ART-028`, ...) y decide `suficiente` de inmediato.
    3. `[Redactor · LoRA ON]` calcula `42 / 4 = 10,5 > 10` y responde directo que **no** esta en baja academica citando `[RI-FI-ART-014]`.
    4. `[Verificador · LoRA OFF (Base)]` aprueba en **1 ciclo / 4 llamadas / `53,8 s`**.

### 1:55 – 2:30 | Resultados globales, ahorro de llamadas y por que Verificador queda en Base
- **En pantalla:** Tabla de resultados en `documento/main.pdf`.
- **Que decir:**
  - En el mismo A100 `bf16`, **D4 `3-LoRA`** iguala/sostiene la exactitud del Control Base dentro de la variabilidad entre corridas (**`64/75`** vs `62/75` en `75`, `McNemar p=0,73`; **`10/20`** vs `11/20` en `nuevas_20`; **`74/95`** vs `73/95` global), pero recortando las llamadas totales un **`41,0%`** (`658 -> 388`, y `-53,5%` en `nuevas_20`), sobre todo porque el Recuperador aprendio cuando detenerse (`suficiente` al primer turno en `65/75`, bajando sus llamadas `-69,8%`: `387 -> 117`).
  - Tambien probamos entrenar al Verificador (`4-LoRA v1: 58/75` y `v2: 56/75`), pero en las `75` oficiales empeoro por sobre-rechazo, validando dejarlo en Base.

### 2:30 – 2:55 | Transparencia de errores reales y cierre
- **En pantalla:** Ultima celda del notebook (`casos_fallo_y_regresion_3lora.json`: `H03`, `H17`, `H06`).
- **Que decir:**
  - Mostramos sin maquillar las limitaciones del sistema:
    - **`H03` (Recuperador):** al aprender a detenerse rapido, en algunas preguntas compuestas corta antes de buscar el segundo documento (`CAL-2026-S1-02/S2-02`).
    - **`H17` (Verificador Base):** ciclo 1 tenia redaccion ambigua (`"asistencia minima de 80% (maximo 80%)"`), y 3 rechazos alucinados del Verificador Base lo llevaron a invertir la regla en ciclo 3.
    - **`H06` (Redactor):** errores puntuales de polaridad y calculo.
  - Todo el codigo, manifiesto de hashes SHA-256, trazas y 30+ tests offline quedan reproducibles en `Deliverable 4/`.
