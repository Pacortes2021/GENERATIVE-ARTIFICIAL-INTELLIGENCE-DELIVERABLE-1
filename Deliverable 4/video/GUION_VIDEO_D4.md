# Guion y checklist de grabación — Video Deliverable 4 (≤ 3 minutos)

- **Duración objetivo:** `2:40 – 2:55` (límite estricto de la pauta: **≤ 3 min**, enlace abierto en Google Drive / YouTube sin restricciones).
- **Qué debe verse explícitamente en pantalla (rúbrica del Deliverable 4):**
  1. Qué agente fue ajustado (`Redactor`) sobre `Qwen/Qwen3-4B` con QLoRA (`Pablox0333/qwen3-4b-redactor-udec-d4`) y que los otros tres (`Enrutador`, `Recuperador`, `Verificador`) conservan pesos base vía `model.disable_adapter()`.
  2. El agente fine-tuned corriendo **en vivo** sobre **entradas reales**, mostrando **en tiempo real los mensajes intermedios entre agentes** (`Enrutador → Recuperador → Redactor → Verificador`).
  3. **Comparación lado a lado Base (`LoRA OFF` en los 4 roles) vs Fine-tuned (`LoRA ON` solo en `Redactor`) sobre exactamente la misma pregunta**, evidenciando mejora concreta y transparencia sobre casos de fallo.

---

## Modo obligatorio de grabación — Vivo en Google Colab GPU (≤ 3 min)

1. Abrir [`Deliverable 4/D4_colab_video_demo.ipynb`](../D4_colab_video_demo.ipynb) en Google Colab con **GPU A100 (`bf16`)** para reproducir exactamente los tiempos (`173,5 s` Base vs `89,0 s` FT) y la configuración oficial `greedy=False` / `semilla=2026` (también funciona en `T4`/`L4`, con mayor tiempo de espera y posible variación menor por `float16`).
2. **Antes de iniciar la grabación:** ejecutar las celdas de la **Sección 1** (dependencias fijadas, clonado de `deliverable-4` con respaldo `main`, carga única de `Qwen/Qwen3-4B`, E5 y el adaptador v2 `Pablox0333/qwen3-4b-redactor-udec-d4` fijado en `739b031`, más chequeo de aislamiento `max|Δlogits| = 13,56 > 0` en A100 `bf16`).
3. **Al iniciar la grabación de pantalla:** ejecutar en vivo la **Sección 2** sobre **`dificil_25:H07`** (corre Base `LoRA OFF` vs FT `Redactor LoRA ON` con **`verbose=True`**, imprimiendo en tiempo real cada paso y mensaje intermedio apenas responde cada agente, más la tarjeta HTML comparativa final). Para mantener el video **≤ 3 min**, acelerar en edición **solo** las esperas de inferencia con un rótulo explícito en pantalla (por ejemplo, `[x6 velocidad durante inferencia]`) sin recortar nunca los mensajes intermedios desplegados.
4. Cerrar mostrando la **Sección 3** (casos de fallo reales **`dificil_25:H06`** y **`dificil_25:H03`**) y el resumen en [`documento/main.pdf`](../documento/main.pdf).

> Nota: `video/mostrar_demo_d4.py` también ofrece modo `--live` desde terminal (`python3 video/mostrar_demo_d4.py --live --qid dificil_25:H07`, ya con `--verbose-pasos` activado); el modo offline solo debe usarse para inspeccionar fallos auditados (`H06`, `H03`), **nunca** para reemplazar la corrida en vivo exigida por la pauta.

---

## Guion minuto a minuto (2:45)

### `[0:00 – 0:25]` Arquitectura y aislamiento del adaptador
- **En pantalla:** [`documento/main.pdf`](../documento/main.pdf) (zoom en el grafo de Sección 2 y curva QLoRA v2 de Sección 4: `52,38 min` en T4, `eval_loss 1,6006 → 0,5164`) + salida de la Sección 1 del notebook.
- **Qué decir:**
  - *"En Deliverable 4 partimos de los 4 agentes de D3 sobre `Qwen/Qwen3-4B`. Al auditar D3 vimos que en 8 de los 9 errores finales la evidencia correcta ya llegaba al top-6 del Redactor, y en D3 intentar seguir tocando prompts empeoró el puntaje."*
  - *"Por eso ajustamos con QLoRA exclusivamente al agente `Redactor` con 210 pares supervisados verificados sin solapamiento de unidades (`180 train / 30 val`, `0%` fuga y balance `74/210` `No aplica`), mientras `Enrutador`, `Recuperador` y `Verificador` mantienen los pesos base con `model.disable_adapter()` (`0` violaciones LoRA)."*

### `[0:25 – 1:40]` Demo EN VIVO Base vs Fine-tuned con mensajes intermedios (`dificil_25:H07`)
- **En pantalla:** Ejecución en vivo de la **Sección 2** en `D4_colab_video_demo.ipynb` (acelerando únicamente la espera de generación con rótulo visible `[x6 inferencia]`) y despliegue de la tarjeta HTML **Mensajes intermedios**.
- **Qué mostrar y decir:**
  - Leer la pregunta real: *"Un estudiante aprobó 42 créditos al término de su cuarto semestre. ¿Está en baja académica por el criterio de promedio de créditos del Artículo 14?"*
  - Mostrar los mensajes intermedios reales en traza: `Enrutador [LoRA OFF]` clasifica `condicional` → `Recuperador ReAct [LoRA OFF]` ejecuta `buscar` y `traer` recuperando `RI-FI-ART-014` y `RG-ART-028` → `Redactor` → `Verificador [LoRA OFF]`.
  - **Contraste Base vs Fine-tuned sobre la misma entrada (en idéntico entorno A100 bf16 registrado / demo en vivo):**
    - **Control Base (`LoRA OFF` en los 4 agentes):** cae en `3 ciclos` (`173,54 s` en A100) y se abstiene erróneamente (*"No se puede determinar... no proporciona el número total de semestres"*), ignorando los `42` créditos y `cuarto semestre` presentes en la consulta.
    - **D4 v2 (`Redactor LoRA ON`):** en `2 ciclos` (`89,03 s` en A100) calcula exactamente `42 / 4 = 10,5 créditos semestrales > 10` con `[RI-FI-ART-014]` y `[RG-ART-028]`, concluyendo correctamente que **no** está en baja académica.

### `[1:40 – 2:10]` Comparación cuantitativa y análisis crítico (Sección 5 de `main.pdf`)
- **En pantalla:** Tabla comparativa v2 y desglose en [`documento/main.pdf`](../documento/main.pdf).
- **Qué decir:**
  - Mostrar los resultados completos v2 en A100 (`bf16`): en el benchmark oficial de 75 preguntas, `FT v2` corrige `5/9` fallos de D3 (`P13, P24, H07, H14, H18`), recupera `6` errores de v1 (`H19` incluido) y sube `No aplica` a `37/75`, alcanzando **`60/75` (`80,0%`; `62/75` núcleo)** con **`8,64` llamadas/pregunta (`-8,86%` vs D3)**. Frente al **Control Base (`--solo-base`, `62/75`, `82,7%`)** en idéntico entorno, FT gana en `6` preguntas y Control Base en `8` (`balance -2`), mientras en la submuestra pareada de `6` casos diagnósticos D3 marca `4/6 vs 2/6`.
  - Mostrar también el set ciego **`preguntas_nuevas_20.csv` (`0%` solapamiento de artículos):** `FT v2` obtiene **`10/20` (`50,0%`, `25,07 min`)** frente a **`11/20` (`55,0%`, `32,84 min`)** del Control Base (`-16,5%` llamadas, `-23,7%` latencia y `2/3 vs 1/3` en divergencias).

### `[2:10 – 2:45]` Transparencia: dónde falla o lo frena la arquitectura (`H06`, `H03`) y cierre
- **En pantalla:** Trazas de `dificil_25:H06` y `dificil_25:H03` (Sección 3 de `D4_colab_video_demo.ipynb`) y Sección 6 de `main.pdf`.
- **Qué decir:**
  - Mostrar **`H06`**: en ciclo 1, `Redactor FT v2` calcula bien `38 / 4 = 9,5 < 10 -> cae en Baja Académica [RI-FI-ART-014]`, **pero ya parte con polaridad contradictoria (`"Respuesta: No, ..."`)**; luego, el `Verificador base [LoRA OFF]` agrava el error rechazando falsamente la división `38 / 4 = 9,5` y empujando ciclo 2 a abstención y ciclo 3 a `"No, ... incumple el criterio"`. Señalar también los **2 casos puros** donde el `Verificador` base degradó borradores correctos (**`H22`** y **`N05`**, además de **`H21`** mixto/discutible; en las 75, `12/68` aprobaciones fallaron).
  - Señalar además el cuello de botella del **`Recuperador`** (**`H03`**: `CAL-2026-S2-02` sigue fuera del `top-6`) y del **`Enrutador`** en `N12`/`N19` (`RI-FI` excluye `RG`), más errores residuales de aritmética en fechas (`N06, N07`) y `Condiciones: No aplica` omitiendo excepciones (`P36, H25`).
  - Cerrar mostrando el adaptador público en Hugging Face (`Pablox0333/qwen3-4b-redactor-udec-d4`, revisión `739b031`), el repositorio GitHub y confirmando enlace abierto del video.
