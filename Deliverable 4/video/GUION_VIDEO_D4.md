# Guion de Video Demostrativo — Deliverable 4 (<= 3 minutos)

**Proyecto:** Especialización Multi-LoRA por rol (`Enrutador + Recuperador + Redactor` + `Verificador` en Base) sobre `Qwen/Qwen3-4B` en normativa académica UdeC.  
**Participantes:** Álvaro Contreras y Pablo Cortés.  
**Notebook de ejecución en vivo (Colab, rama `main`):** `Deliverable 4/D4_colab_video_demo.ipynb` (respaldo offline en `video/mostrar_demo_d4.py`).

---

## Preparación rápida antes de grabar (objetivo corte final: `2:50`)

1. Abre dos pestañas limpias:
   - **Pestaña 1:** `Deliverable 4/documento/main.pdf` (página única, zoom cómodo para ver grafo TikZ, tabla de datos, curvas y tabla de resultados).
   - **Pestaña 2:** Google Colab (GPU A100) con `Deliverable 4/D4_colab_video_demo.ipynb` (`MONTAR_DRIVE = False`).
2. **Pre-ejecuta antes de apretar Rec:** **Paso 1** (`pip install` + `git clone` de `main`, verificando que el commit ya incluya los arreglos del visor) y **Paso 2** (carga NF4 + verificación SHA-256 + `e5` + 3 adaptadores HF + `verificar_aislamiento_multi_lora()`).
3. **Al grabar en vivo el Paso 3 (`dificil_25:H07`):**
   - Muestra el **clic en Ejecutar del Paso 3** (`verbose=True`) para que se lean ambos planes del Enrutador, acción del Recuperador, borrador y veredicto Base, cerrando con las tarjetas HTML (`Verificador: APROBADO/RECHAZO` · `SIN CALIFICAR` con llamadas reales).
   - **Tiempos y edición:** en A100, `Base` (~173–177 s) + `3-LoRA` (~54–60 s) toman ~3m50s en vivo. **Acelera (`6x–8x`) las esperas de generación en AMBOS lados** (con aviso en pantalla) para ajustar este bloque a **`~80 s`** y narra siempre con los **contadores exactos de esa toma** (benchmark: `4` llamadas / `53,84 s`; ensayo `--solo-hf`: `6` llamadas / `59,91 s`).
   - **Precisión normativa en `H07`:** `RG Art. 28 a)` define la fórmula del promedio (`42 / 4 = 10,5`) y `RI-FI Art. 14 b)` fija el umbral `< 10` desde el 4.º semestre. Si el modelo en vivo cita solo `RI-FI-ART-014`, muéstralo tal cual y distingue la aprobación interna del Verificador frente a la evaluación completa de citas.

---

## Guion hablado cronometrado (~330 palabras · corte final `2:50`)

### 0:00 – 0:21 | Continuidad D1–D3 y arquitectura `3-LoRA` (`main.pdf` · Grafo)
- **En pantalla:** Página 1 de `documento/main.pdf` (cabecera y grafo TikZ).
- **Locución:**
  > Hola, somos Álvaro Contreras y Pablo Cortés. En D1, `Qwen/Qwen3-4B` sin corpus acertó `2/50`. En D3, tras saturar prompting en cuatro agentes, `8/9` fallos ya tenían evidencia en el Redactor, y entrenar solo al Redactor dejó `373` llamadas en el Recuperador. En D4 conservamos los prompts y adaptamos **Enrutador, Recuperador y Redactor** con `set_adapter()`, dejando al **Verificador** en Base vía `disable_adapter()`.

### 0:21 – 0:42 | Datos, revisión humana y alcance antifuga (`main.pdf` · Sección 3 y curvas)
- **En pantalla:** Tabla de datasets y curvas `loss_curves_3agentes.png` en `main.pdf`.
- **Locución:**
  > Armamos `725` pares (`620` entrenamiento, `105` validación) con `0` truncamientos y revisamos `50` ejemplos a mano con firmas. Comprobamos `0` coincidencias con las `61` unidades excluidas de evaluación, y declaramos que `P36` aparece como ejemplo *few-shot* heredado en el Enrutador, donde `3-LoRA` sigue fallando.

### 0:42 – 2:02 | Demo en vivo `H07`: Base vs `3-LoRA` (`Colab` · Pasos 2 y 3 · **80 s**)
- **En pantalla:** Cambia a Colab; muestra el **Paso 2** listo, haz **clic en Ejecutar Paso 3 (`dificil_25:H07`)**, deja leer ambos planes, una acción del Recuperador, borrador y veredicto, y muestra las tarjetas HTML lado a lado.
- **Locución:**
  > Con los adaptadores cargados desde Hugging Face y su aislamiento verificado, ejecutamos en vivo `H07` sobre si un alumno con 42 créditos en cuarto semestre cae en baja académica.
  > *(Acelera las esperas en ambos lados)*: Los dos Enrutadores reciben la misma pregunta. Aquí se ven ambos planes, la recuperación, el borrador y el veredicto. Control Base entra en `3` ciclos y `13` llamadas hasta abstenerse falsamente, mientras `3-LoRA` aprueba en `1` ciclo: `42 / 4 = 10,5 > 10`, cumpliendo con el umbral de RI-FI 14 b) según RG 28 a). Estos son los contadores reales de la toma.

### 2:02 – 2:30 | Tabla A100 y por qué Verificador queda en Base (`main.pdf` · Tabla)
- **En pantalla:** Tabla de resultados en `main.pdf`.
- **Locución:**
  > En A100, `3-LoRA` logró `64/75` frente a `62/75` del Control Base —McNemar no detectó diferencia— y recortó las llamadas de `658` a `388` (`-41%`). El tiempo bajó de `75,3` a `72,6` minutos, y en las `20` nuevas marcamos `10` frente a `11`. Entrenar también al Verificador cayó a `58` y `56` en las `75`, validando dejarlo en Base.

### 2:30 – 2:50 | Fallo real (`H03`) y cierre (`Colab` · Paso 4)
- **En pantalla:** Ejecuta **Paso 4** mostrando `dificil_25:H03` (`casos_fallo_y_regresion_3lora.json`).
- **Locución:**
  > Cerramos con la traza archivada de `H03`: el Recuperador se detuvo sin traer las fechas de inicio y el Redactor comparó las dos fechas límite entre sí. Código, hashes SHA-256, trazas y `31` pruebas offline quedan reproducibles en `Deliverable 4/` de `main`. Gracias.
