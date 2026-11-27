# Guion de Video Demostrativo — Deliverable 4 (<= 3 minutos)

**Proyecto:** Especialización Multi-LoRA por rol (`Enrutador + Recuperador + Redactor` + `Verificador` en Base) sobre `Qwen/Qwen3-4B` en normativa académica UdeC.  
**Participantes:** Álvaro Contreras y Pablo Cortés.  
**Notebook de ejecución en vivo (Colab):** `Deliverable 4/D4_colab_video_demo.ipynb` (respaldo offline en `video/mostrar_demo_d4.py`).

---

## Preparación rápida antes de grabar (objetivo corte final: `2:40 – 2:50`)

1. Abre dos pestañas limpias:
   - **Pestaña 1:** `Deliverable 4/documento/main.pdf` (página única, zoom cómodo para ver cabecera, grafo TikZ, curvas y tabla).
   - **Pestaña 2:** Google Colab (GPU A100) con `Deliverable 4/D4_colab_video_demo.ipynb` (`MONTAR_DRIVE = False`).
2. **Pre-ejecuta antes de apretar Rec:** **Paso 1** (`pip install` + `git clone`) y **Paso 2** (carga única NF4 + `e5` + 3 adaptadores desde Hugging Face + `verificar_aislamiento_multi_lora()`).
3. **Al grabar en vivo el Paso 3 (`dificil_25:H07`):**
   - Lanza el **Paso 3** con `verbose=True` para mostrar los mensajes intermedios entre agentes (`[1] enrutador` ... `[5] verificador`) y las tarjetas HTML finales lado a lado.
   - En A100, `Control Base` tarda `~173–177 s` (3 ciclos) y `D4 3-LoRA` tarda `~54–60 s` (1 ciclo), `~3m50s` solo en inferencia. **Acelera en edición (`4x–6x`) la espera de generación de Control Base** dejando legibles los logs clave de ciclos 1–3, manteniendo la ejecución real completa bajo **3 minutos**.
   - Respaldo offline solo en caso de caída de Colab: `python3 "Deliverable 4/video/mostrar_demo_d4.py" --qid dificil_25:H07 --mostrar-fallos`.

---

## Guion hablado cronometrado (~350 palabras · ~2:35 locución + transiciones = ~2:45)

> Pueden leerlo de corrido o repartirse los bloques (ej. Bloques 1–2 Álvaro, Bloques 3–5 Pablo).

### 0:00 – 0:25 | Contexto D1–D3 y arquitectura Multi-LoRA (`main.pdf` · Secciones 1 y 2)
- **En pantalla:** Página 1 de `documento/main.pdf` (cabecera y grafo TikZ).
- **Locución:**
  > Hola, somos Álvaro Contreras y Pablo Cortés. En Deliverable 3 armamos cuatro agentes sobre `Qwen/Qwen3-4B` sin entrenar; en A100 ese Control Base logró `62/75` con `658` llamadas, y entrenar solo al Redactor (`60/75`) dejaba intacto el cuello de botella del Recuperador (`373` llamadas). Por eso en D4 creamos **3-LoRA**: un único modelo en 4 bits con tres adaptadores QLoRA por turno (**Enrutador, Recuperador, Redactor** con `set_adapter()`) y el **Verificador** en Base vía `disable_adapter()`.

### 0:25 – 0:45 | Datos antifuga y entrenamiento (`main.pdf` · Sección 3 y curvas)
- **En pantalla:** Tabla de datasets y gráfica `loss_curves_3agentes.png` en `main.pdf`.
- **Locución:**
  > Construimos `725` ejemplos (`620` train, `105` val) sobre artículos disjuntos de las `75` preguntas y las `20` nuevas, garantizando `0%` fuga de datos. Los tres roles convergieron sin truncamientos, bajando la pérdida de validación a `0,123` en Enrutador, `0,186` en Recuperador y `0,516` en Redactor.

### 0:45 – 1:45 | Demostración en vivo: Control Base vs D4 `3-LoRA` en `H07` (`Colab` · Pasos 2 y 3)
- **En pantalla:** Cambia a Colab; muestra `verificar_aislamiento_multi_lora()` del **Paso 2** y ejecuta **Paso 3** (`dificil_25:H07`), mostrando los mensajes intermedios y luego las tarjetas HTML.
- **Pregunta `H07`:** *"Un estudiante aprobó 42 créditos al término de su cuarto semestre. ¿Está en baja académica por el criterio de promedio de créditos del Artículo 14?"*
- **Locución:**
  > Pasemos a Colab cargando los pesos desde Hugging Face. Con el aislamiento verificado, ejecutamos en vivo el caso `H07`: un alumno aprobó 42 créditos al cuarto semestre y consultamos si entra en baja académica.
  > En **Control Base (`LoRA OFF`)**, cae en **3 ciclos, 13 llamadas y `177` segundos**: el Redactor acierta en ciclo 2, pero el Verificador Base lo rechaza (*"la evidencia no respalda este cálculo"*) y provoca una falsa abstención.
  > En **D4 `3-LoRA`**, vemos los mensajes intermedios: **Enrutador** clasifica `numerica`, **Recuperador** decide `suficiente` con los primeros cinco fragmentos sin iterar, **Redactor** calcula `42 / 4 = 10,5 > 10` citando `[RI-FI-ART-014]`, y **Verificador Base** aprueba en **1 ciclo, 4 llamadas y `54` segundos**.

### 1:45 – 2:20 | Resultados globales y por qué Verificador queda en Base (`main.pdf` · Tabla)
- **En pantalla:** Tabla de resultados en `documento/main.pdf`.
- **Locución:**
  > Sobre todo el banco en A100, **3-LoRA** sostiene la exactitud del Control Base —**`64/75`** vs `62/75` (`McNemar p = 0,73`), **`10/20`** nuevas y **`74/95`** global—, recortando un **`41,0%`** las llamadas (`658` a `388`) y **`53,5%`** en las nuevas. El Recuperador bajó **`69,8%`** (`387` a `117`), deteniéndose al paso uno en `65/75`. Además probamos entrenar al Verificador (`4-LoRA v1: 58/75`, `v2: 56/75`), pero sobre-rechazó y validó dejarlo en Base.

### 2:20 – 2:45 | Transparencia de errores reales y cierre (`Colab` · Paso 4)
- **En pantalla:** Ejecuta **Paso 4** en Colab (`casos_fallo_y_regresion_3lora.json`: `H03`, `H17`, `H06`).
- **Locución:**
  > Cerramos con transparencia revisando tres fallos reales: en `H03`, el Recuperador corta antes de traer todo el calendario; en `H17`, el Verificador Base fuerza una inversión en ciclo 3; y en `H06`, el Redactor invierte la polaridad. Código, hashes SHA-256, trazas y `31` pruebas offline quedan reproducibles en `Deliverable 4/`. Gracias.
