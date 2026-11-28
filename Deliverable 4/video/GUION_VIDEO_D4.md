# Guion de Video Demostrativo — Deliverable 4 (<= 3 minutos)

**Proyecto:** Especialización Multi-LoRA por rol (`Enrutador + Recuperador + Redactor` + `Verificador` en Base) sobre `Qwen/Qwen3-4B` en normativa académica UdeC.  
**Participantes:** Álvaro Contreras y Pablo Cortés.  
**Notebook de ejecución en vivo (Colab, rama `main`):** `Deliverable 4/D4_colab_video_demo.ipynb` (respaldo offline en `video/mostrar_demo_d4.py`).

---

## Preparación rápida antes de grabar (objetivo corte final: `2:55`)

1. Abre dos pestañas limpias en Chrome/Brave (zoom navegador **`110%–125%`** para lectura nítida a 1080p):
   - **Pestaña 1:** `Deliverable 4/documento/main.pdf` (página única A4, zoom cómodo para encuadrar grafo, datos/curvas y tabla A100).
   - **Pestaña 2:** Google Colab (**GPU A100 o T4**) con `Deliverable 4/D4_colab_video_demo.ipynb` (`MONTAR_DRIVE = False`). Colapsa la barra lateral izquierda de Colab y la salida de instalación del Paso 1.
2. **Pre-ejecuta antes de apretar Rec:** **Paso 1** (`pip install` + `git clone` de `main`) y **Paso 2** (deja visible la tarjeta HTML compacta `Paso 2 listo · Único modelo NF4` con `SHA-256 OK`, `ΔBase > 0`, `Verificador OFF` y `Aislamiento Multi-LoRA Verificado`).
3. **Al grabar en vivo el Paso 3 (`dificil_25:H07` + `demo_alumno:A01` y `demo_alumno:A02`):**
   - Muestra en cámara el **clic en Ejecutar del Paso 3** (`verbose=True` muestra los banners de las 3 preguntas arriba y separa `Ciclo 1`, `Ciclo 2`, etc., mostrando `Respuesta:` directo sin truncar dentro de `<pensar>`).
   - Deja a velocidad `1x` al menos un mensaje legible por rol en `H07`, luego acelera las esperas (`8x–12x` con aviso visible en pantalla) hasta que terminen las 3 comparativas y haz scroll suave por las tarjetas finales (**Hero Strip + Base vs `3-LoRA`**) de **`H07`**, **`A01`** (inasistencia a certamen por salud) y **`A02`** (2.ª reprobación de ramo obligatorio en 2.º año).
   - **Edición (`<= 3:00`):** dedica **`~55 s`** a `H07` y **`~35 s`** en conjunto a `A01 + A02` (**`~90 s`** para todo Paso 3). Narra siempre con los **contadores reales de esa toma** e indica con naturalidad la GPU en uso si grabaste en `T4 float16` (aclarando que la evaluación completa del PDF corrió en `A100 bf16`).
   - **Precisión normativa:** en `H07`, la pauta exige `RG Art. 28 a)` (`42 / 4 = 10,5`) y `RI-FI Art. 14 b)` (`< 10`); si el modelo cita solo `RI-FI-ART-014`, dilo tal cual y distingue la aprobación interna del Verificador frente a `SIN CALIFICAR` (auditoría externa). En `A01` y `A02`, destaca que son preguntas cotidianas sobre artículos excluidos del entrenamiento.

---

## Guion hablado cronometrado (~330 palabras · corte final `2:55`)

### 0:00 – 0:20 | Continuidad D1–D3 y por qué `3-LoRA` (`main.pdf` · Sec. 1 y Grafo)
- **En pantalla:** Página 1 de `documento/main.pdf` (Sección 1, tarjeta KPI y Figura 1).
- **Locución:**
  > Hola, somos Álvaro Contreras y Pablo Cortés. En D1, `Qwen/Qwen3-4B` sin corpus acertó `2/50`; en D3 con cuatro agentes subimos a `66/75`, donde editar prompts ya causaba regresiones. Ocho de nueve fallos tenían evidencia en el Redactor, pero entrenarlo solo bajó a `60/75` dejando `373` llamadas en el Recuperador. Por eso adaptamos **Enrutador, Recuperador y Redactor** en un único modelo NF4, manteniendo al **Verificador** en Base.

### 0:20 – 0:38 | Datos, revisión humana y alcance antifuga (`main.pdf` · Sec. 3 y Fig. 2)
- **En pantalla:** Tablas de Sección 3–4 y Figura 2 (`loss_curves_3agentes.pdf`).
- **Locución:**
  > Construimos `725` pares (`620` train, `105` validación) excluyendo las `61` unidades normativas de evaluación, con `50` muestras firmadas a mano y `0` truncamientos. Solo mantuvimos el prompt original de D3 en el Enrutador, que conserva el ejemplo de `P36` donde aún falla.

### 0:38 – 2:12 | Demo en vivo: `H07` + 2 consultas naturales (`Colab` · Pasos 2 y 3 · **94 s**)
- **En pantalla:** Cambia a Colab; muestra la tarjeta **Paso 2 listo**, haz **clic en Ejecutar Paso 3** (`H07`, `A01`, `A02`), deja leer mensajes por rol a `1x` y recorre Hero Strip + tarjetas de las 3 preguntas.
- **Locución:**
  > Cargamos desde Hugging Face con aislamiento verificado [en GPU T4 `float16` / A100] y lanzamos en vivo tres consultas: primero `H07` (`42` créditos al 4.º semestre). Vemos plan, búsqueda, borrador y veredicto: Base hace `[ciclos y llamadas]` hasta rechazarse, mientras `3-LoRA` resuelve en `[ciclos y llamadas]` aprobado por el Verificador (`SIN CALIFICAR` es auditoría externa; esta toma citó `[citas emitidas]`).
  > *(Scroll a `A01` y `A02`)*: Sumamos además dos dudas naturales de alumno, sobre normas excluidas del entrenamiento: faltar enfermo a un certamen (`3` días hábiles, certificación DISE y apelación al Vicedecano) y reprobar por segunda vez un obligatorio en 2.º año (`baja` pese al buen promedio, `1` año para pedir continuación y `10` días de respuesta). Aquí ven el contraste real en llamadas y respuestas entre Base y `3-LoRA`: `[contadores reales de A01 y A02]`.

### 2:12 – 2:37 | Tabla oficial A100 y ablación del Verificador (`main.pdf` · Sec. 5)
- **En pantalla:** Tabla y bullets de Sección 5 en `main.pdf`.
- **Locución:**
  > En la evaluación completa en A100, `3-LoRA` marcó `64/75` frente a `62/75` del Control Base —sin diferencia en McNemar— y recortó llamadas de `658` a `388` (`-41%`) gracias al Recuperador (`-69,8%`), con `10/20` frente a `11/20` en preguntas nuevas. Entrenar al Verificador cayó a `58` y `56` por sobre-rechazo, validando dejarlo en Base.

### 2:37 – 2:55 | Fallo real (`H03`) y cierre (`Colab` · Paso 4)
- **En pantalla:** Ejecuta **Paso 4** en Colab mostrando `dificil_25:H03` (traza del Recuperador + respuesta vs pauta) y la tabla HTML compacta A100.
- **Locución:**
  > Cerramos con `H03`: el Recuperador cortó antes de traer las fechas de inicio y el Redactor restó las fechas límite entre sí. Todo queda reproducible con hashes SHA-256 y `32` pruebas en `Deliverable 4/` de `main`. Gracias.
