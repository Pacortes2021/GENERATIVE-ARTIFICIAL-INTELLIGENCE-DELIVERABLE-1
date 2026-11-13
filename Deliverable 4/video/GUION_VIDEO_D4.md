# Guion y checklist de grabación — Video Deliverable 4 (≤ 3 minutos)

- **Duración objetivo:** `2:40 – 2:55` (límite estricto de la pauta: **≤ 3 min**, enlace abierto en Google Drive / YouTube sin restricciones).
- **Qué debe verse explícitamente en pantalla (rúbrica del Deliverable 4):**
  1. Qué agente fue ajustado (`Redactor`) sobre `Qwen/Qwen3-4B` con QLoRA (`Pablox0333/qwen3-4b-redactor-udec-d4`) y que los otros tres (`Enrutador`, `Recuperador`, `Verificador`) conservan pesos base vía `model.disable_adapter()`.
  2. El agente fine-tuned corriendo **en vivo** sobre **entradas reales**, mostrando **en tiempo real los mensajes intermedios entre agentes** (`Enrutador → Recuperador → Redactor → Verificador`).
  3. **Comparación lado a lado Base (`LoRA OFF` en los 4 roles) vs Fine-tuned (`LoRA ON` solo en `Redactor`) sobre exactamente la misma pregunta**, evidenciando mejora concreta y transparencia sobre casos de fallo.

---

## Modo obligatorio de grabación — Vivo en Google Colab GPU (≤ 3 min)

1. Abrir [`Deliverable 4/D4_colab_video_demo.ipynb`](../D4_colab_video_demo.ipynb) en Google Colab con GPU T4 o L4.
2. **Antes de iniciar la grabación:** ejecutar las celdas de la **Sección 1** (instalación, clonado de `deliverable-4`, carga única de `Qwen/Qwen3-4B`, E5 y el adaptador `Pablox0333/qwen3-4b-redactor-udec-d4`, más chequeo de aislamiento `max|Δlogits| > 0`).
3. **Al iniciar la grabación de pantalla:** ejecutar en vivo la **Sección 2** sobre **`dificil_25:H07`** (corre Base `LoRA OFF` vs FT `Redactor LoRA ON` en directo ~4–5 min en T4). Para mantener el video **≤ 3 min**, acelerar en edición **solo** las esperas de inferencia con un rótulo explícito en pantalla (por ejemplo, `[x6 velocidad durante inferencia en T4]`) sin recortar nunca los mensajes intermedios desplegados.
4. Cerrar mostrando la **Sección 3** (caso de fallo real **`dificil_25:H19`**) y el resumen en [`documento/main.pdf`](../documento/main.pdf).

> Nota: `video/mostrar_demo_d4.py` también ofrece modo `--live` desde terminal (`python3 video/mostrar_demo_d4.py --live --qid dificil_25:H07`); el modo offline solo debe usarse para inspeccionar fallos históricos (`H19`), **nunca** para reemplazar la corrida en vivo exigida por la pauta.

---

## Guion minuto a minuto (2:45)

### `[0:00 – 0:25]` Arquitectura y aislamiento del adaptador
- **En pantalla:** [`documento/main.pdf`](../documento/main.pdf) (zoom en el grafo de Sección 2 y curva QLoRA de Sección 4) + salida de la Sección 1 del notebook.
- **Qué decir:**
  - *"En Deliverable 4 partimos de los 4 agentes de D3 sobre `Qwen/Qwen3-4B`. Al auditar D3 vimos que en 8 de los 9 errores finales la evidencia correcta ya llegaba al top-6 del Redactor, y en D3 intentar seguir tocando prompts empeoró el puntaje."*
  - *"Por eso ajustamos con QLoRA exclusivamente al agente `Redactor` con 210 pares supervisados verificados sin solapamiento de unidades (`180/30`), mientras `Enrutador`, `Recuperador` y `Verificador` mantienen los pesos base con `model.disable_adapter()`."*

### `[0:25 – 1:40]` Demo EN VIVO Base vs Fine-tuned con mensajes intermedios (`dificil_25:H07`)
- **En pantalla:** Ejecución en vivo de la **Sección 2** en `D4_colab_video_demo.ipynb` (acelerando únicamente la espera de generación con rótulo visible `[x6 inferencia T4]`) y despliegue de la tarjeta HTML **Mensajes intermedios**.
- **Qué mostrar y decir:**
  - Leer la pregunta real: *"Un estudiante aprobó 42 créditos al término de su cuarto semestre. ¿Está en baja académica por el criterio de promedio de créditos del Artículo 14?"*
  - Mostrar los mensajes intermedios reales en traza: `Enrutador [LoRA OFF]` clasifica `condicional` → `Recuperador ReAct [LoRA OFF]` ejecuta `buscar` y `traer_articulo` recuperando `RI-FI-ART-014` y `RG-ART-028` → `Redactor` → `Verificador [LoRA OFF]`.
  - **Contraste Base vs Fine-tuned sobre la misma entrada (en el mismo entorno):**
    - **Control Base (`LoRA OFF` en los 4 agentes):** cae en `3 ciclos` y se abstiene erróneamente (*"No se puede determinar... falta de información"*), ignorando los `42` créditos y `4` semestres presentes en la consulta.
    - **D4 (`Redactor LoRA ON`):** en **1 solo ciclo** calcula `42 / 4 = 10,5 créditos semestrales >= 10` con `[RI-FI-ART-014]` `[RG-ART-028]` y concluye correctamente que **no** está en baja académica.

### `[1:40 – 2:10]` Comparación cuantitativa y análisis crítico (Sección 5 de `main.pdf`)
- **En pantalla:** Tabla comparativa y desglose en [`documento/main.pdf`](../documento/main.pdf).
- **Qué decir (actualizando según tus resultados finales v2 tras re-correr Colab):**
  - Mostrar el balance completo frente al control Base en el mismo entorno, señalando tanto las mejoras en `calculo`/`condicional` como cualquier regresión por citas o cláusulas extra, más las métricas del set ciego de `20` preguntas nuevas (`nuevas_20`).

### `[2:10 – 2:45]` Transparencia: dónde falla o lo frena la arquitectura (`H19` / `H03`) y cierre
- **En pantalla:** Traza de `dificil_25:H19` (Sección 3 de `D4_colab_video_demo.ipynb`) y Sección 6 de `main.pdf`.
- **Qué decir:**
  - Mostrar `H19`: en ciclos 1 y 2 el `Redactor FT` acierta la fórmula `[RG-ART-028]`, pero el `Verificador base` la rechaza exigiendo umbrales de `[RI-FI-ART-014]` y empuja un ciclo 3 erróneo (en v1, `8/68` aprobaciones del Verificador fueron incorrectas y `4 de 7` rechazos recayeron sobre borradores correctos). Mencionar también `H03` donde `CAL-2026-S2-02` sigue fuera del `top-6` del Recuperador.
  - Cerrar mostrando el adaptador público en Hugging Face (`Pablox0333/qwen3-4b-redactor-udec-d4`), el repositorio GitHub y confirmando enlace abierto del video.
