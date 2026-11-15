# Guion de Video Demostrativo — Deliverable 4 (<= 3 minutos)

**Proyecto:** Especializacion Multi-LoRA por rol (`Enrutador + Recuperador + Redactor` + `Verificador` en Base) sobre `Qwen/Qwen3-4B` en normativa academica UdeC.  
**Participantes:** Alvaro Contreras y Pablo Cortes.  
**Notebook de ejecucion en vivo (Colab):** `Deliverable 4/D4_colab_video_demo.ipynb` (respaldo offline en `video/mostrar_demo_d4.py`).

---

## Estructura cronometrada (objetivo 2:45 – 2:55)

### 0:00 – 0:25 | Contexto, evolucion D1->D3 y por que entrenamos 3 LoRAs (y no solo Redactor)
- **En pantalla:** Pagina 1 de `documento/main.pdf` (Seccion 1 + grafo TikZ de la Seccion 2).
- **Que decir (lenguaje directo):**
  - En D3 teniamos 4 agentes usando todos exactamente el mismo `Qwen/Qwen3-4B` sin entrenar (`66/75`, pero con `711` llamadas al modelo).
  - Probamos entrenar **solo al Redactor**, pero no basto (`60/75` en Control A100 bf16): seguia haciendo `373` busquedas en el Recuperador y arrastraba errores de ruta.
  - Por eso construimos **D4 3-LoRA**: un **unico modelo base en 4 bits (NF4)** donde cargamos 3 adaptadores ligeros especializados por rol (**Enrutador, Recuperador y Redactor**) y los encendemos segun el turno con `set_adapter()`, mientras el **Verificador** corre con el modelo base limpio usando `disable_adapter()`.

### 0:25 – 0:50 | Datos antifuga y entrenamiento separado de los 3 roles
- **En pantalla:** Tabla de datasets + figura `entrenamiento/loss_curves_3agentes.png` en el PDF.
- **Que decir:**
  - `725` ejemplos en total (`620` entrenamiento / `105` validacion), usando **articulos completamente distintos** a las `75` preguntas oficiales y a las `20` preguntas nuevas (`0%` fuga de datos).
  - Los 3 adaptadores convergieron con **0 ejemplos truncados**: Enrutador (`eval_loss 1,066 -> 0,123`), Recuperador (`1,729 -> 0,186`) y Redactor (`1,601 -> 0,516`).

### 0:50 – 1:55 | Demostracion en vivo: Base (LoRA OFF) vs D4 3-LoRA (H07)
- **En pantalla:** Celda 3 y Celda 4 de `Deliverable 4/D4_colab_video_demo.ipynb` ejecutando `H07` en vivo (con verificacion automatica `verificar_aislamiento_multi_lora` impresa arriba).
- **Pregunta H07:** *"Un estudiante aprobo 42 creditos al termino de su cuarto semestre. ¿Esta en baja academica por el criterio de promedio de creditos del Articulo 14?"*
- **Lo que se ve en la ejecucion:**
  - **Control Base (`LoRA OFF` en los 4 agentes):** cae en **3 ciclos**, **13 llamadas LLM** y **`177,4 s`**, trayendo `12` articulos para terminar absteniendose falsamente (*"la normativa no proporciona el numero total de semestres"*).
  - **D4 3-LoRA:**
    1. `[Enrutador · LoRA ON]` clasifica directo como `numerica` en 1 subconsulta.
    2. `[Recuperador · LoRA ON]` ve los 5 hits iniciales (`RI-FI-ART-014`, `RG-ART-028`, ...) y decide `suficiente` de inmediato.
    3. `[Redactor · LoRA ON]` calcula `42 / 4 = 10,5 > 10` y responde que **no** esta en baja academica citando `[RI-FI-ART-014]`.
    4. `[Verificador · LoRA OFF (Base)]` valida en **1 ciclo / 4 llamadas / `53,8 s`**.

### 1:55 – 2:30 | Resultados globales y por que dejamos al Verificador en Base
- **En pantalla:** Tabla 3 de `documento/main.pdf`.
- **Que decir:**
  - En el mismo A100 bf16, `Control Base` logra `62/75` (`73/95` global) con `658` llamadas, `Solo Redactor` baja a `60/75`, y nuestro **D4 3-LoRA** sube a **`64/75 (85,3%)`** y **`74/95 (77,9%)`** recortando las llamadas totales un **`41,0%`** (`658 -> 388`, y `-69,8%` en el Recuperador) y **`0` violaciones** de conmutacion LoRA.
  - Tambien probamos entrenar al Verificador (`v1` y `v2`), pero se volvio demasiado estricto y rechazo borradores buenos (`58/75` y `56/75`), asi que los experimentos confirman dejarlo en Base.

### 2:30 – 2:55 | Transparencia de errores reales y cierre
- **En pantalla:** Ultima celda del notebook / salida de `casos_fallo_y_regresion_3lora.json` (`H03`, `H17`, `H06`).
- **Que decir:**
  - Mostramos sin maquillar los `11` fallos de las `75` preguntas:
    - **`H03` (Recuperador):** por parar tan rapido a veces le falta traer un articulo en preguntas dobles (`CAL-2026-S1-02/S2-02`).
    - **`H17` (Verificador Base):** el ciclo 1 del Redactor estaba perfecto, pero 3 rechazos inventados del Verificador lo forzaron a invertir la respuesta.
    - **`H06` (Redactor):** errores puntuales de redaccion/calculo cuando la pregunta requiere una comparacion negativa.
  - Todo el codigo, trazas, auditoria y tests automatizados quedan reproducibles en `Deliverable 4/`.
