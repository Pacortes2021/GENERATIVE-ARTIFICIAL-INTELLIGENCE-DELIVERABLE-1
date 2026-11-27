# Guion de Video Demostrativo — Deliverable 4 (<= 3 minutos)

**Proyecto:** Especialización Multi-LoRA por rol (`Enrutador + Recuperador + Redactor` + `Verificador` en Base) sobre `Qwen/Qwen3-4B` en normativa académica UdeC.  
**Participantes:** Álvaro Contreras y Pablo Cortés.  
**Notebook de ejecución en vivo (Colab, rama `main`):** `Deliverable 4/D4_colab_video_demo.ipynb` (respaldo offline en `video/mostrar_demo_d4.py`).

---

## Preparación rápida antes de grabar (objetivo corte final: `2:50`)

1. Abre dos pestañas limpias en Chrome/Brave (zoom navegador **`110%–125%`** para lectura nítida a 1080p):
   - **Pestaña 1:** `Deliverable 4/documento/main.pdf` (página única A4, zoom cómodo para encuadrar grafo, datos/curvas y tabla A100).
   - **Pestaña 2:** Google Colab (GPU A100) con `Deliverable 4/D4_colab_video_demo.ipynb` (`MONTAR_DRIVE = False`). Colapsa la barra lateral izquierda de Colab y la salida de instalación del Paso 1.
2. **Pre-ejecuta antes de apretar Rec:** **Paso 1** (`pip install` + `git clone` de `main`) y **Paso 2** (deja visible la tarjeta HTML compacta `Paso 2 listo · Único modelo NF4` con `SHA-256 OK`, `ΔBase > 0`, `Verificador OFF` y `Aislamiento Multi-LoRA Verificado`).
3. **Al grabar en vivo el Paso 3 (`dificil_25:H07`):**
   - Muestra en cámara el **clic en Ejecutar del Paso 3** (`verbose=True` muestra el banner de la pregunta arriba y separa `Ciclo 1`, `Ciclo 2`, etc., mostrando `Respuesta:` directo sin truncar dentro de `<pensar>`).
   - Deja a velocidad `1x` al menos un mensaje legible por rol en ambos lados y luego haz scroll suave hacia abajo para encuadrar la **Hero Strip (`Llamadas`, `Ciclos`, `Tiempo`, `Verificador Base`)** y las **dos respuestas finales alineadas arriba de las trazas**.
   - **Edición (`<= 3:00`):** acelera (`6x–8x`) las esperas de generación en AMBOS lados (con aviso visible en pantalla) para ajustar este bloque a **`~80 s`** y narra siempre con los **contadores reales de esa toma** (benchmark A100: `4` llamadas / `53,84 s`; ensayo `--solo-hf`: `6` llamadas / `59,91 s`).
   - **Precisión normativa en `H07`:** `RG Art. 28 a)` define la fórmula del promedio (`42 / 4 = 10,5`) y `RI-FI Art. 14 b)` fija el umbral `< 10` desde el 4.º semestre. Si el modelo en vivo cita solo `RI-FI-ART-014`, muéstralo tal cual y distingue la aprobación interna del Verificador frente a la auditoría externa contra la pauta.

---

## Guion hablado cronometrado (~325 palabras · corte final `2:50`)

### 0:00 – 0:22 | Continuidad D1–D3 y por qué `3-LoRA` (`main.pdf` · Sec. 1 y Grafo)
- **En pantalla:** Página 1 de `documento/main.pdf` (Sección 1, tarjeta KPI y Figura 1).
- **Locución:**
  > Hola, somos Álvaro Contreras y Pablo Cortés. En D1, `Qwen/Qwen3-4B` sin corpus acertó `2/50`; en D3 con cuatro agentes subimos a `66/75`, donde editar prompts ya provocaba regresiones. Ocho de nueve fallos tenían evidencia en el Redactor, pero entrenarlo solo bajó a `60/75` en A100 dejando `373` llamadas en el Recuperador. Por eso adaptamos **Enrutador, Recuperador y Redactor** en un único modelo NF4, manteniendo al **Verificador** en Base como árbitro neutral.

### 0:22 – 0:42 | Datos, revisión humana y alcance antifuga (`main.pdf` · Sec. 3 y Fig. 2)
- **En pantalla:** Tablas de Sección 3–4 y Figura 2 (`loss_curves_3agentes.pdf`).
- **Locución:**
  > Armamos `725` pares (`620` train, `105` validación) excluyendo las `61` unidades normativas de evaluación, con `50` muestras firmadas a mano y `0` truncamientos. Aquí vemos la convergencia de los tres roles; solo conservamos el prompt original de D3 en el Enrutador, que incluía el ejemplo equivalente a `P36` donde aún falla.

### 0:42 – 2:02 | Demo en vivo `H07`: Base vs `3-LoRA` (`Colab` · Pasos 2 y 3 · **80 s**)
- **En pantalla:** Cambia a Colab; muestra la tarjeta de **Paso 2 listo**, haz **clic en Ejecutar Paso 3 (`dificil_25:H07`)**, deja leer mensajes por rol a `1x` y encuadra Hero Strip + tarjetas finales.
- **Locución:**
  > Cargamos modelo base y tres adaptadores desde Hugging Face con aislamiento verificado, y ejecutamos `H07`: si `42` créditos al cuarto semestre implican baja académica.
  > *(Acelera esperas dejando legible un mensaje por rol)*: Ambos sistemas reciben `H07`. Vemos plan, búsqueda, borrador y veredicto: Base hizo `[ciclos y llamadas de esta toma]` hasta abstenerse, mientras `3-LoRA` hizo `[ciclos y llamadas de esta toma]` (`42 / 4 = 10,5 > 10`) aprobado por Verificador (`SIN CALIFICAR` es auditoría externa aparte; esta toma citó `[citas emitidas]`, la pauta pide `RG 28 a)` y `RI-FI 14 b)`).

### 2:02 – 2:30 | Tabla A100 y ablación del Verificador (`main.pdf` · Sec. 5)
- **En pantalla:** Tabla y bullets de Sección 5 en `main.pdf`.
- **Locución:**
  > En A100, `3-LoRA` marcó `64/75` frente a `62/75` del Control Base —sin diferencia en McNemar— y redujo llamadas de `658` a `388` (`-41%`) porque el Recuperador aprendió cuándo detenerse (`-69,8%`). El tiempo pasó de `75,3` a `72,6` minutos y en las `20` nuevas obtuvimos `10` frente a `11`. Entrenar al Verificador cayó a `58` y `56` por sobre-rechazo, validando dejarlo en Base.

### 2:30 – 2:50 | Fallo real (`H03`) y cierre (`Colab` · Paso 4)
- **En pantalla:** Ejecuta **Paso 4** en Colab mostrando la tarjeta destacada de `dificil_25:H03` (traza del Recuperador + respuesta vs pauta) y la tabla HTML compacta A100.
- **Locución:**
  > Cerramos mostrando `H03`: el Recuperador cortó antes de traer las fechas de inicio y el Redactor comparó las fechas límite entre sí. Código, hashes SHA-256, trazas y `31` pruebas quedan reproducibles en `Deliverable 4/` de `main`. Gracias.
