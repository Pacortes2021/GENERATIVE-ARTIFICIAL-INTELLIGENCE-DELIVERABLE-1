# Guion de Video Demostrativo — Deliverable 4 (<= 3 minutos)

**Proyecto:** Especialización Multi-LoRA por rol (`Enrutador + Recuperador + Redactor` + `Verificador` en Base) sobre `Qwen/Qwen3-4B` en normativa académica UdeC.  
**Participantes:** Álvaro Contreras y Pablo Cortés.  
**Notebook de ejecución en vivo (Colab, rama `main`):** `Deliverable 4/D4_colab_video_demo.ipynb` (respaldo offline en `video/mostrar_demo_d4.py`).

---

## Preparación y tiempos reales de esta toma (corte final `~2:50`)

- **Entorno en vivo:** Google Colab **`GPU T4` (`torch.float16`)**, pesos cargados desde Hugging Face (`Pablox0333`, `SHA-256 OK`, `Aislamiento Multi-LoRA Verificado`) sobre `main@04c22a1`.
- **Resultados exactos capturados en Paso 3 (`48 → 20` llamadas totales, `-58,3%`, `9 → 3` ciclos):**
  - `dificil_25:H07`: Base `3` ciclos / `13` llam. (`216,1 s`, `RECHAZO`) vs `3-LoRA` `1` ciclo / `4` llam. (`88,1 s`, `APROBADO`, `-69,2%`; citó `RI-FI-ART-014`; pauta pide además `RG Art. 28 a)`).
  - `demo_alumno:A01` *(inasistencia a certamen por salud)*: Base `3` ciclos / `19` llam. (`301,1 s`, `RECHAZO`) vs `3-LoRA` `1` ciclo / `10` llam. (`105,3 s`, `APROBADO`, `-47,4%`; citó `RG-ART-026`, omitió `RG-ART-059` de DISE).
  - `demo_alumno:A02` *(2.ª reprobación de ramo obligatorio en 2.º año)*: Base `3` ciclos / `16` llam. (`265,6 s`, `APROBADO` en ciclo 3) vs `3-LoRA` `1` ciclo / `6` llam. (`88,1 s`, `APROBADO` en ciclo 1, `-62,5%`; citó `RI-FI-ART-014` y `RG-ART-030`).

---

## Guion hablado por bloques (~320 palabras · corte final `<= 2:55`)

### Bloque 1 | Continuidad D1–D3 y por qué `3-LoRA` (`main.pdf` · Sec. 1 y Grafo)
- **En pantalla:** Lámina HD de `documento/main.pdf` (Cabecera, Sección 1, tarjeta KPI y Figura 1).
- **Locución:**
  > Hola, somos Álvaro Contreras y Pablo Cortés. En D1, Qwen 3 de cuatro mil millones de parámetros sin corpus acertó dos de cincuenta; en D3 con cuatro agentes subimos a sesenta y seis de setenta y cinco, donde seguir editando prompts ya causaba regresiones. Ocho de nueve fallos tenían evidencia en el Redactor, pero entrenarlo solo bajó a sesenta de setenta y cinco dejando trescientas setenta y tres llamadas en el Recuperador. Por eso adaptamos Enrutador, Recuperador y Redactor en un único modelo NF4, manteniendo al Verificador en Base como árbitro neutral.

### Bloque 2 | Datos, revisión humana y alcance antifuga (`main.pdf` · Sec. 3–4 y Fig. 2)
- **En pantalla:** Lámina HD de `documento/main.pdf` (Secciones 3–4 y Figura 2 con curvas de pérdida).
- **Locución:**
  > Construimos setecientos veinticinco pares, seiscientos veinte de entrenamiento y ciento cinco de validación, excluyendo sesenta y un unidades normativas de evaluación, con cincuenta muestras firmadas a mano y cero truncamientos. Solo conservamos el prompt original de D3 en el Enrutador, que mantiene el ejemplo de P36 donde aún falla.

### Bloque 3 | Demo en vivo en Colab `GPU T4`: `H07` + `A01` + `A02` (Paso 2 y Paso 3)
- **En pantalla:** Tarjeta `Paso 2 listo` -> clic en Ejecutar **Paso 3** -> avance acelerado en `GPU T4` -> log `verbose` (`Base` vs `3-LoRA`) -> tarjetas de **`H07`**, **`A01`** y **`A02`**.
- **Locución:**
  > Reproducimos en vivo los mismos pesos de Hugging Face en Colab T4 con aislamiento verificado, ejecutando tres consultas seguidas. Primero H07, cuarenta y dos créditos al cuarto semestre: Base hace trece llamadas en tres ciclos y es rechazado por el Verificador, mientras Tres-LoRA resuelve en un ciclo y cuatro llamadas aprobado con R-I-F-I catorce, aunque la pauta pide además R-G veintiocho a. Sumamos dos consultas reales de alumno sobre normas excluidas del entrenamiento: faltar enfermo a un certamen, donde Tres-LoRA baja de diecinueve a diez llamadas y acierta plazo y apelación pero omite la certificación D-I-S-E; y reprobar por segunda vez un obligatorio en segundo año, bajando de dieciséis a seis llamadas en un solo ciclo con ambas citas correctas. En conjunto, recortamos de cuarenta y ocho a veinte llamadas.

### Bloque 4 | Tabla oficial A100 y ablación del Verificador (`main.pdf` · Sec. 5)
- **En pantalla:** Lámina HD de `documento/main.pdf` (Sección 5 completa y Sección 6).
- **Locución:**
  > En la evaluación completa en A100, Tres-LoRA logró sesenta y cuatro de setenta y cinco frente a sesenta y dos del Control Base, sin diferencia en McNemar, y diez frente a once en las veinte preguntas nuevas, reduciendo llamadas en cuarenta y uno por ciento gracias al Recuperador. Entrenar al Verificador cayó a cincuenta y ocho y cincuenta y seis por sobre-rechazo, validando dejarlo en Base.

### Bloque 5 | Fallo real (`H03`) y cierre reproducible (`Colab` · Paso 4)
- **En pantalla:** Ejecución del **Paso 4** en Colab mostrando `dificil_25:H03` y la tabla resumen A100.
- **Locución:**
  > Cerramos con H03: el Recuperador cortó antes de traer las fechas de inicio y el Redactor restó las fechas límite entre sí. Código, hashes SHA-256, trazas y treinta y dos pruebas quedan en Deliverable 4 de main. Gracias.
