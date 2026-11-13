# Guion y checklist de grabación — Video Deliverable 4 (≤ 3 minutos)

- **Duración objetivo:** `2:40 – 2:55` (límite estricto de la pauta: **≤ 3 min**, enlace abierto en Google Drive / YouTube sin restricciones).
- **Qué debe verse explícitamente en pantalla (rúbrica del Deliverable 4):**
  1. Qué agente fue ajustado (`Redactor`) sobre `Qwen/Qwen3-4B` con QLoRA (`Pablox0333/qwen3-4b-redactor-udec-d4`) y que los otros tres (`Enrutador`, `Recuperador`, `Verificador`) conservan pesos base vía `model.disable_adapter()`.
  2. El agente fine-tuned corriendo sobre **entradas reales**, mostrando **en vivo o en traza real los mensajes intermedios entre agentes** (`Enrutador → Recuperador → Redactor → Verificador`).
  3. **Comparación lado a lado Base vs Fine-tuned sobre exactamente la misma pregunta**, evidenciando mejora concreta (y transparencia sobre casos de fallo).

---

## Dos modos listos para grabar

### Opción A — Vivo en Google Colab GPU (recomendado si tienen T4/L4 libre, ~4–5 min precalentado antes de grabar)
1. Abrir [`Deliverable 4/D4_colab_video_demo.ipynb`](../D4_colab_video_demo.ipynb) en Colab con GPU T4.
2. Ejecutar las celdas de instalación, clonado y carga del modelo **antes** de empezar a grabar.
3. Iniciar grabación de pantalla y ejecutar la celda de comparación en vivo sobre **`dificil_25:H07`** (tarda ~1,3 min con FT y ~3,8 min Base; pueden pre-ejecutar la corrida antes del corte o grabar `H07` FT en vivo ~78 s y desplegar la tarjeta HTML lado a lado Base vs FT con los intercambios completos).

### Opción B — Replay inmediato desde terminal o Colab sin GPU (0,1 s, cero riesgo en vivo)
Desde la carpeta `Deliverable 4/` (o en el mismo notebook [`D4_colab_video_demo.ipynb`](../D4_colab_video_demo.ipynb)):

```bash
python3 video/mostrar_demo_d4.py \
  --qid dificil_25:H07 \
  --qid dificil_25:H14 \
  --fallo dificil_25:H19
```

Para ver solo la comparativa compacta sin truncar los mensajes intermedios de un caso puntual:

```bash
python3 video/mostrar_demo_d4.py --qid dificil_25:H07 --completo
```

---

## Guion minuto a minuto (2:45)

### `[0:00 – 0:25]` Arquitectura y aislamiento del adaptador
- **En pantalla:** [`documento/main.pdf`](../documento/main.pdf) (zoom en el grafo de Sección 2 y curva QLoRA de Sección 4).
- **Qué decir:**
  - *"En Deliverable 4 partimos de los 4 agentes de D3 sobre `Qwen/Qwen3-4B`. Al auditar D3 vimos que en 8 de los 9 errores finales la evidencia correcta ya llegaba al top-6 del Redactor, y en el entregable anterior el sistema falló al seguir tocando prompts."*
  - *"Por eso ajustamos con QLoRA exclusivamente al agente `Redactor` con 210 pares sintéticos verificados sin fuga (`180/30`), mientras `Enrutador`, `Recuperador` y `Verificador` siguen ejecutando exactamente el modelo base con `model.disable_adapter()`."*

### `[0:25 – 1:35]` Demo central Base vs Fine-tuned con mensajes intermedios (`dificil_25:H07`)
- **En pantalla:** Terminal con `mostrar_demo_d4.py --qid dificil_25:H07` o tarjeta HTML en `D4_colab_video_demo.ipynb` desplegando los `<details>` de **Mensajes intermedios**.
- **Qué mostrar y decir:**
  - Leer la pregunta real: *"Un estudiante aprobó 42 créditos al término de su cuarto semestre. ¿Está en baja académica por el criterio de promedio de créditos del Artículo 14?"*
  - Mostrar los pasos intermedios (`Enrutador [LoRA OFF]` clasifica `calculo` → `Recuperador ReAct [LoRA OFF]` ejecuta `buscar` y `traer_articulo` trayendo `RI-FI-ART-014` y `RG-ART-028` → `Redactor` → `Verificador [LoRA OFF]`).
  - **Contraste Base vs Fine-tuned sobre la misma entrada:**
    - **Base (`LoRA OFF` en los 4 agentes):** cae en `3 ciclos` (`227,68 s`, `14 pasos`) y se abstiene erróneamente (*"No se puede determinar... falta de información necesaria sobre semestres y créditos"*), ignorando que la consulta ya entrega `42` y `cuarto semestre`.
    - **D4 (`Redactor LoRA ON`):** en **1 solo ciclo (`78,70 s`, `-65%` tiempo)** aplica `42 / 4 = 10,5 créditos semestrales >= 10` con `[RI-FI-ART-014]` y concluye correctamente que **no** está en baja académica.

### `[1:35 – 2:10]` Segundo contraste Base vs Fine-tuned (`dificil_25:H14`) + cifras globales
- **En pantalla:** Caso `dificil_25:H14` y tabla de Sección 5 en [`documento/main.pdf`](../documento/main.pdf).
- **Qué decir:**
  - En `H14` (*"reprobó una asignatura obligatoria por segunda vez, ¿queda automáticamente en baja?"*), **Base** responde *"Sí, queda automáticamente... salvo PLEV o primer año"*, contradiciéndose; **Redactor FT** corrige la polaridad en **1 ciclo**: *"No queda automáticamente en baja académica..."*.
  - Cifras globales sobre las 75 preguntas: D4 FT resuelve `6/9` fallos estrictos de D3 y gana `4/6 vs 1/6` en la comparativa controlada; baja llamadas LLM reales de `711 -> 666 (-6,3%)` y tiempo en T4 de `137,6 -> 114,4 min (-16,9%)`.

### `[2:10 – 2:45]` Transparencia: dónde falla o lo frena la arquitectura (`H19` / `H03`) y cierre
- **En pantalla:** Traza de `dificil_25:H19` en terminal (`--fallo dificil_25:H19`) o Sección 6 de `main.pdf`.
- **Qué decir:**
  - *"¿Por qué la pauta estricta total marca `64/75 (85,3%)` frente a `66/75` en D3, si el núcleo normativo sin cláusulas extra en Condiciones sube a `68/75 (90,7%)`?"*
  - Mostrar `H19`: en los ciclos 1 y 2 el `Redactor FT` acierta la fórmula `[RG-ART-028] a)`, pero el `Verificador base` la rechaza exigiendo créditos de otra causal y fuerza un ciclo 3 erróneo (en total `8/68` aprobaciones del Verificador fueron incorrectas y `4/7` rechazos eran válidos). Y en `H03` sigue fallando el `top-6` del Recuperador en `CAL-2026-S2-02`.
  - Cerrar invitando al repo (`Deliverable 4/`, adaptador público en Hugging Face `Pablox0333/qwen3-4b-redactor-udec-d4`) y recordar subir el video con enlace abierto antes de entregar.
