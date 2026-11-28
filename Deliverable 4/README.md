# Deliverable 4 — Especialización Multi-LoRA por rol (`Qwen/Qwen3-4B`)

Continuación directa de Deliverables 1–3 sobre normativa de pregrado de Ingeniería UdeC ([`corpus.json`](../Deliverable%203/Deliverable3/agentes/corpus.json): `173` artículos/secciones padre, `197` unidades evaluables y `201` fragmentos de búsqueda), manteniendo **un único modelo `Qwen/Qwen3-4B` cuantizado en 4 bits (NF4)** y el grafo multi-agente de D3 sobre `75` preguntas oficiales (`congelado_50` + `dificil_25`) más `20` preguntas nuevas ([`preguntas_nuevas_20.csv`](datos/preguntas_nuevas_20.csv)).

---

## Qué abrir primero (mapeado a la rúbrica de [`enunciado.pdf`](enunciado.pdf))

| Criterio de evaluación | Dónde verificarlo en `Deliverable 4/` |
|---|---|
| **Documento técnico (1 pág. A4 LaTeX)** | [`documento/main.pdf`](documento/main.pdf) · fuentes [`main.tex`](documento/main.tex) y [`grafo_d4.tex`](documento/grafo_d4.tex) |
| **Video demostrativo (≤ 3 min)** | `[Pendiente: enlace público tras ensayo H07 y grabación]` · [`video/GUION_VIDEO_D4.md`](video/GUION_VIDEO_D4.md) · [`video/mostrar_demo_d4.py`](video/mostrar_demo_d4.py) |
| **Colab en vivo (`--solo-hf`, Pasos 1–4)** | [![Demo H07](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%204/D4_colab_video_demo.ipynb) · [![Eval completa](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%204/D4_colab_evaluacion.ipynb) |
| **Adaptadores Hugging Face (`SHA-256`)** | [`Pablox0333/qwen3-4b-enrutador-udec-d4`](https://huggingface.co/Pablox0333/qwen3-4b-enrutador-udec-d4) (`ab65a4f`) · [`recuperador`](https://huggingface.co/Pablox0333/qwen3-4b-recuperador-udec-d4) (`6bd665a`) · [`redactor`](https://huggingface.co/Pablox0333/qwen3-4b-redactor-udec-d4) (`739b031`) · [`manifest_adaptadores_hf.json`](entrenamiento/manifest_adaptadores_hf.json) |
| **Diagnóstico D3 y elección de agentes** | [`diagnostico/DIAGNOSTICO_D3.md`](diagnostico/DIAGNOSTICO_D3.md) y [`diagnostico/diagnostico_d3.json`](diagnostico/diagnostico_d3.json) |
| **Datos antifuga (`725`) y firmas (`50/50`)** | [`datos/`](datos/) · [`firmas Redactor`](datos/revision_manual_firmas.csv) · [`firmas Enr/Rec`](datos/revision_manual_firmas_agentes.csv) |
| **Prompts congelados de D3 v6** | [`01_enrutador.txt`](prompts/01_enrutador.txt) · [`02_recuperador.txt`](prompts/02_recuperador.txt) · [`03_redactor.txt`](prompts/03_redactor.txt) · [`04_verificador.txt`](prompts/04_verificador.txt) |
| **Evaluación, reproducción HF y fallos** | [`evaluacion/README.md`](evaluacion/README.md) · [`casos_fallo_y_regresion_3lora.json`](evaluacion/casos_fallo_y_regresion_3lora.json) · [`comparativa_reproduccion_hf.json`](evaluacion/comparativa_reproduccion_hf.json) |

---

## Arquitectura `3-LoRA` y por qué pasamos de `1` a `3` adaptadores (con Verificador Base)

1. **Punto de partida (D3 v6, `66/75`):** iterar los prompts en D3 ya había tocado techo (en `v5` editar `03_redactor.txt` y `04_verificador.txt` provocó regresiones de `58/75 → 55/75` obligando a revertir a `v4`, y quitar CoT mantuvo `65/75` frente a `66/75` en [`RESUMEN_ABLACIONES.md`](../Deliverable%203/Deliverable3/resultados_ablaciones/RESUMEN_ABLACIONES.md)). En nuestro diagnóstico, **8 de 9 errores finales** ya tenían los 6 fragmentos de evidencia en el Redactor (`top-6`).
2. **Por qué `1-LoRA` (`Solo Redactor v2`) no bastó:** al fine-tunear solo al Redactor y compararlo en A100 `bf16` contra el Control Base (`60/75` vs `62/75`), las trazas mostraron un cuello de botella operativo aguas arriba: **`373` de `648` llamadas en las `75` (`132` en `N20`) ocurrían en el Recuperador** repitiendo búsquedas sobre planes del Enrutador Base. *(Variante respaldada en la rama `backup/d4-solo-redactor`)*.
3. **Arquitectura oficial `3-LoRA` (`set_adapter()` + `disable_adapter()`):** sobre un único `Qwen/Qwen3-4B` en 4 bits (NF4), activamos por turno adaptadores QLoRA (`r=16`, `alpha=32`) para **`Enrutador`**, **`Recuperador`** y **`Redactor`**, mientras **`Verificador` ejecuta siempre con pesos Base intactos** (`98/98` llamadas OFF en `75`, `32/32` OFF en `N20`, **`0` violaciones**). Mantenerlo en Base evita el sesgo de sobre-rechazo medido en las ablaciones `4-LoRA v1` (`58/75`) y `v2` (`56/75`).

---

## Mapa del directorio `Deliverable 4/` (`118` archivos en `main`)

| Ruta | Qué contiene | Notas de navegación |
|---|---|---|
| `D4_colab_video_demo.ipynb` / `evaluacion` / `entrenamiento` | 3 notebooks Colab reproducibles desde rama `main` (`SOLO_HF = True`, sin Drive por defecto) | Demo `H07` corre directo en GPU |
| [`datos/`](datos/) | `620` train + `105` val JSONL (`725` pares), `preguntas_nuevas_20.csv`, `preguntas_demo_alumnos.csv` (2 consultas naturales de alumno para el video), muestras manuales y CSVs firmados | [`MUESTRA_REVISION_MANUAL.md`](datos/MUESTRA_REVISION_MANUAL.md) y [`...ENRUTADOR_RECUPERADOR.md`](datos/MUESTRA_REVISION_MANUAL_ENRUTADOR_RECUPERADOR.md) |
| [`diagnostico/`](diagnostico/) | Auditoría D3 `v6` (`8/9` con evidencia top-6, reversión v5) | Base de elección inicial de agente |
| [`documento/`](documento/) | [`main.pdf`](documento/main.pdf) (1 página A4), [`main.tex`](documento/main.tex), [`grafo_d4.tex`](documento/grafo_d4.tex) | Compilado con `tectonic` |
| [`entrenamiento/`](entrenamiento/README.md) | Pesos/métricas por rol + manifiesto HF SHA-256 + curvas `loss_curves_3agentes.*` | Raíz = `Redactor` + globales; subcarpetas `enrutador/` y `recuperador/` |
| [`evaluacion/`](evaluacion/README.md) | `46` archivos de resultados, auditorías, trazas y telemetría (`resumen_comparativo_d4.json`) | Ver índice para separar oficial `3-LoRA`, `Control Base` e histórico `1-LoRA` |
| [`prompts/`](prompts/) | `01_enrutador.txt` .. `04_verificador.txt` | Idénticos bit a bit a D3 v6 (`test_diagnostico_d3.py`) |
| [`scripts/`](scripts/) | Constructores (`construir_dataset*.py`, `antifuga_multi.py`), entrenadores (`entrenar_*.py`), evaluadores (`evaluar_*.py`), publicador HF y generador de reporte | `dataset_blocks/` guarda especificaciones del Redactor |
| [`tests/`](tests/) | 5 suites (`test_dataset`, `test_diagnostico_d3`, `test_entrenamiento`, `test_evaluar_d4`, `test_multi_lora_d4`) | **`32` tests offline** en verde |
| [`video/`](video/) | [`GUION_VIDEO_D4.md`](video/GUION_VIDEO_D4.md) y visor interactivo [`mostrar_demo_d4.py`](video/mostrar_demo_d4.py) | Tarjetas HTML `SIN CALIFICAR` + Verificador + CLI offline |

---

## Resultados experimentales (`A100 bf16` vs históricos en `T4`)

Evaluación bajo la pauta estricta heredada de D2/D3 ([`LEEME_PAUTA.md`](../Deliverable%203/paquete_25_dificiles/LEEME_PAUTA.md)): dato correcto y cita normativa exacta, penalizando omisión de condiciones o afirmaciones falsas extra. `Control Base (A100)` ejecuta exactamente el sistema D3 v6 con semillas `2026`.

| Sistema / Control | Entorno | Orig. (50) | Dif. (25) | D3 Total (75) | Nuevas (20) | Global (95) | Llamadas (`75 / 20`) | Tiempo (`75 / 20`) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| D1 Directo (`greedy`, solo abst.) | T4 | 2 (4,0%) | --- | --- | --- | --- | --- | --- |
| Baseline Directo D2/D3 (`T=0,7`) | T4 | 1 (2,0%) | 0 (0,0%) | 1 (1,3%) | --- | --- | 75 / --- | --- |
| RAG D2 (`E5`) | T4 (`bf16`) | 40 (80,0%) | 16 (64,0%) | 56 (74,7%) | --- | --- | 75 / --- | --- |
| Multi-agente D3 Base (`v6`) | T4 | **46 (92,0%)** | **20 (80,0%)** | **66 (88,0%)** | --- | --- | 711 / --- | 137,6 min / --- |
| Control Base (`= D3 v6`, `LoRA OFF`) | A100 `bf16` | **46 (92,0%)** | 16 (64,0%) | 62 (82,7%) | **11 (55,0%)** | 73 (76,8%) | 658 / 254 | 75,3 min / 32,8 min |
| Solo Redactor v2 (`1-LoRA`) | A100 `bf16` | 43 (86,0%) | 17 (68,0%) | 60 (80,0%) | 10 (50,0%) | 70 (73,7%) | 648 / 212 | 75,7 min / 25,1 min |
| **D4 Oficial (`3-LoRA` · Verif. Base)** | **A100 `bf16`** | **46 (92,0%)** | **18 (72,0%)** | **64 (85,3%)** | 10 (50,0%) | **74 (77,9%)** | **388 / 118** | **72,6 min / 30,2 min** |
| *Ablación 4-LoRA v1 (Verificador FT)* | A100 `bf16` | 40 (80,0%) | 18 (72,0%) | 58 (77,3%) | **14 (70,0%)** | 72 (75,8%) | 493 / 138 | --- |
| *Ablación 4-LoRA v2 (Verificador FT)* | A100 `bf16` | 40 (80,0%) | 16 (64,0%) | 56 (74,7%) | 12 (60,0%) | 68 (71,6%) | 486 / 147 | --- |

### Qué demuestran realmente estos números (`resumen_comparativo_d4.json`)
- **Exactitud comparable (McNemar no detectó diferencia):** el propio sistema base varía `66 → 62` al cambiar de T4 a A100. Frente a Control Base A100, `3-LoRA` marca `64/75` vs `62/75` (5 ganancias, 3 pérdidas, `p=0,7266`), `10/20` vs `11/20` en nuevas y `74/95` vs `73/95` global (`7/6`, `p=1,0`). Como se eligió la arquitectura entre 5 variantes observando estas `95` preguntas, las `20` nuevas ya no actúan como set ciego estricto entre arquitecturas (sí estuvieron fuera de entrenamiento).
- **Ahorro real de llamadas (`-41,0%` en `75`, `-53,5%` en `N20`):** atribuido al sistema `3-LoRA` y localizado en el **Recuperador LoRA**, que aprendió a detenerse rápido (`suficiente` en su 1.ª acción tras la búsqueda base `traza[2]` en `65/75` casos; o **`66/75`** contando la 1.ª llamada LLM real incluyendo `P50`; `21` búsquedas propias vs `157` Base, `-69,8%`). El Enrutador entrega `documentos` solo como contexto (`49/75` proponen solo `RG`). El tiempo total baja `-3,7%` (`75,3 → 72,6 min`) porque el Redactor domina la generación.
- **Caso contraste `H07` (*baja académica con 42 créditos en 4.º semestre*):** en el **benchmark A100 archivado**, Control Base acierta `10,5 > 10` en ciclo 2 pero el Verificador Base lo rechaza falsamente forzando abstención en ciclo 3 (`177,44 s`, `13` llamadas), Solo Redactor tarda `89,37 s`, y `3-LoRA` resuelve en `1` ciclo / `4` llamadas (`53,84 s`). En el ensayo independiente `--solo-hf` (`comparativa_reproduccion_hf.json`), Base mantuvo `3` ciclos / `13` llamadas (`172,56 s`) y `3-LoRA` aprobó en `1` ciclo / `6` llamadas (`59,91 s`).
- **Auditoría transparente de fallos (`11/75` + `10/20`):** documentados con traza completa en [`casos_fallo_y_regresion_3lora.json`](evaluacion/casos_fallo_y_regresion_3lora.json) y [`trazas_3lora_nuevas20.json`](evaluacion/trazas_3lora_nuevas20.json): *(1)* cortes prematuros del Recuperador (`H03`: omite `CAL-2026-S1-02/S2-02`; `P36`: omite `RI-FI-ART-008`), *(2)* sobre-rechazos del Verificador Base (`H17`, `H19`) e ablaciones `4-LoRA` (`v1` colapsó rechazando `"No aplica"`), *(3)* errores residuales del Redactor (`H06` inicia negando cuando sí hay baja; `H12/P26` mezclan artículos).

<details>
<summary>Ver notas granulares de evaluación (`P7/P8`, QIDs con diferencias y fallos por causa)</summary>

- **Diferencias Control Base vs `3-LoRA`:** en `75`, gana `5` (`congelado_50:11, 43; dificil_25:H07, H18, H24`) y pierde `3` (`congelado_50:24, 26; dificil_25:H17`). En `nuevas_20`, gana `N09, N12` y pierde `N05, N06, N20`.
- **Formato `Fuente:` (`P7` y `P8`):** cumplen correctamente la pauta semántica de `LEEME_PAUTA.md` con citas inline válidas, omitiendo la tercera línea literal `Fuente:` (`64/75`; sin penalizar omisiones menores de formato o de condiciones accesorias en `H22`/`N06` daría `65/75` y `11/20`).
- **Causas de fallo (`11` en `75` / `10` en `N20`):** Redactor (`6 / 4`), Recuperador (`3 / 3`), Verificador Base (`2 / 3`). **`0` fallbacks JSON y `0` citas inexistentes en corpus** en `3-LoRA`.
</details>

---

## Datasets (`725` pares), alcance antifuga y entrenamiento QLoRA

Construidos por rol (`seed=202604`) preservando `prompts/01--03` bit a bit con **`0` coincidencias** contra las `61` unidades normativas excluidas (`D3-75`: `40`, `N20`: `21`), `0` IDs de evaluación y `0` ejemplos truncados *(nota transparente: `01_enrutador.txt`, congelado de D3 v6, incluye literalmente a `P36` como ejemplo few-shot donde `3-LoRA` aún falla)*:

| Agente | Train / Val | Unid. | Procedencia exacta de cada salida correcta | Entrenamiento y `eval_loss` |
|---|---:|---:|---|---|
| **Enrutador** | `210 / 36` (`246`) | `97/197` | `30` train + `6` val escritos a mano (asist. **Gemini 4 Argon** vía Antigravity), más `210` etiquetados por reglas (`enrutador_bloques.py`) | A100 `bf16`: `9,88 min / 105` pasos · `1,066 → 0,123` (`paso 80`) |
| **Recuperador** | `230 / 39` (`269`) | `109/197` | Trayectorias ReAct deterministas (`recuperador_bloques.py`) replicando a `Orquestador.recuperar()` | A100 `bf16`: `10,43 min / 117` pasos · `1,729 → 0,186` (`paso 117`) |
| **Redactor** | `180 / 30` (`210`) | `112/197` | Especificaciones curadas en `dataset_blocks/` (asist. **Gemini 4 Argon**) validadas contra `corpus.json` (`No aplica`: `74`) | T4 `fp16`: `52,38 min / 90` pasos · `1,601 → 0,516` (`paso 90`) |
| **Total D4** | **`620 / 105` (`725`)** | **`0/61 excl.`** | **Muestra manual (`50/50` firmados el `2026-11-19`)**: `30` Redactor ([firmas](datos/revision_manual_firmas.csv)) + `20` Enr./Rec. ([firmas](datos/revision_manual_firmas_agentes.csv)) | Curvas en [`loss_curves_3agentes.png`](entrenamiento/loss_curves_3agentes.png) |

---

## Reproducción offline y estado de cierre

```bash
# 1. Verificar hashes SHA-256 en Hugging Face Hub vs manifest_adaptadores_hf.json
python3 "Deliverable 4/scripts/publicar_adaptadores_hf.py" --verificar-manifest

# 2. Reconstruir datasets (725 pares) y consolidar métricas/curvas/reporte
python3 "Deliverable 4/scripts/construir_dataset.py"
python3 "Deliverable 4/scripts/construir_datasets_agentes.py"
python3 "Deliverable 4/scripts/generar_reporte_3lora.py"

# 3. Suite completa de pruebas unitarias offline (32/32)
python3 -m unittest discover -s "Deliverable 4/tests" -v

# 4. Visor demo offline (H07 + fallos reales H03, H17, H06)
python3 "Deliverable 4/video/mostrar_demo_d4.py" --qid dificil_25:H07 --mostrar-fallos

# 5. Compilar grafo TikZ y PDF de 1 página vertical
cd "Deliverable 4/documento" && tectonic grafo_d4.tex && tectonic main.tex
```

**Estado previo a la entrega final:**
1. **Reproducción limpia desde HF (`--solo-hf` en A100):** completada y archivada en [`comparativa_reproduccion_hf.json`](evaluacion/comparativa_reproduccion_hf.json).
2. **Revisión humana (`50/50` muestras):** aprobada y firmada el `2026-11-19`.
3. **Video demostrativo (`<= 3 min`):** único pendiente — ensayar `H07` en [`D4_colab_video_demo.ipynb`](D4_colab_video_demo.ipynb) (`MONTAR_DRIVE = False`), grabar siguiendo [`GUION_VIDEO_D4.md`](video/GUION_VIDEO_D4.md) y pegar la URL pública en ambos READMEs y [`documento/main.tex`](documento/main.tex) recompilando `main.pdf`.
