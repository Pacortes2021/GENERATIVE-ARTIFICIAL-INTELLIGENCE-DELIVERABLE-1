# Asistente de normativa de pregrado · Ingeniería UdeC

Álvaro Contreras y Pablo Cortés · Generative Artificial Intelligence (580694), segundo semestre 2026.

El sistema responde preguntas en español sobre un corpus cerrado de tres PDF: Reglamento General (RG), Reglamento Interno de Ingeniería (RI-FI) y Calendario de Docencia 2026. Debe entregar todos los datos pedidos y las fuentes correctas, o abstenerse sin inventar ante premisas falsas. El conjunto propio del equipo tiene 50 preguntas, diez por categoría.

## Estado de Deliverable 2

La versión de trabajo corrige la demostración y la evaluación. **Todavía requiere una nueva ejecución en Colab T4, revisión del equipo y grabación del video.** Los resultados históricos se conservan sin modificar. No hay nuevas inferencias de Qwen3-4B realizadas durante esta revisión.

- Modelo principal de E1: `Qwen/Qwen3-4B`; encoder: `intfloat/multilingual-e5-small`.
- Intervención medida: RAG denso con top-5 y prompt que solicita `DATO:` / `CITA:`. No se usa decodificación restringida por gramática.
- Hardware observado en salidas históricas: Colab Tesla T4, 15,64 GB totales, 8,53 GB asignados al cargar encoder y generador. Se empleó dtype `auto`; la nueva ejecución registra su valor efectivo y cualquier descarga a CPU.
- Los ensayos de Qwen2.5-3B/Ollama son exploratorios. Sus resultados no se mezclan con los del modelo principal ni demuestran ejecución en el hardware declarado en E1.

## Resultados históricos revisados

**Revisión semántica asistida por IA, pendiente de validación del equipo.** La tabla aplica un criterio conservador uniforme a ambos sistemas: dato completo, fuentes suficientes para respaldar todo lo pedido y ausencia de contenido inventado. El script únicamente recuenta los veredictos explícitos; no califica semánticamente respuestas nuevas.

| Categoría (10 preguntas) | Baseline Qwen3-4B | RAG Qwen3-4B |
| --- | ---: | ---: |
| Factual | 0/10 | 9/10 |
| Numérica | 0/10 | 10/10 |
| Condicional | 0/10 | 8/10 |
| Cruce | 0/10 | 7/10 |
| Abstención | 1/10 | 10/10 |
| **Global** | **1/50 (2%)** | **44/50 (88%)** |

E1 publicó **2/50 (4%)**. La revisión invalida P49 porque, aunque rechaza el feriado supuesto, inventa una autoridad ajena al corpus y un día de semana. Se declara este cambio; no se altera el CSV original. La mejora bajo la misma revisión es **86 puntos porcentuales**.

El **98% anterior no es exactitud estricta**: el evaluador aceptaba coincidencias de un solo término, cifra o artículo. Por ejemplo, P36 omite los ocho créditos y su fuente y aun así se daba por correcta. Las cifras anteriores de 76%, 96% y 98% no deben combinarse ni presentarse como corroboración independiente.

La fuente citada debe respaldar todos los datos pedidos. P32, P33 y P39 citan el calendario, que basta para la fecha; P34 cita el Art. 31 RG, que basta para el derecho y el plazo. Mi primera revisión les exigió además referencias redundantes y produjo **40/50 (80%)**. Corregida esa exigencia, la revisión provisional es **44/50 (88%)**. El equipo debe fijar esta convención antes de la entrega final. Ver [protocolo](Deliverable2_RAG/PROTOCOLO_EVALUACION.md) y [revisión de 100 respuestas](Deliverable2_RAG/revision_historica.csv).

Latencia histórica RAG: media **5,386 s**, mediana **4,825 s**, mínimo 2,32 y máximo 11,40. Incluye recuperación y generación, no descarga/carga/indexación. No hay evidencia para la afirmación previa de 0,5 s.

## Reproducir la auditoría local (sin GPU ni dependencias externas)

Desde la raíz del repositorio, con Python 3.10 o posterior:

```bash
python -m Deliverable2_RAG.auditoria
python -m unittest Deliverable2_RAG.test_entrega2 -v
```

La auditoría valida que preguntas, gold y predicciones coincidan. Cada revisión está vinculada por SHA-256; modificar una respuesta exige volver a revisarla. Los resultados consolidados están en `Deliverable2_RAG/metricas_auditadas.json`.

## Ejecutar el sistema y reproducir el video en Colab

1. Abrir `rag_normativa_ingenieria_4b.ipynb` y seleccionar GPU **T4**.
2. Si esta versión aún no está publicada, subir el notebook a Colab y dejar `FUENTE="zip"`: la primera celda solicita el paquete `genia_deliverable2.zip`. Si ya se publicó, usar `FUENTE="github"` y fijar `REF_REPO` al commit de la entrega.
3. Ejecutar las celdas de preparación, instalación, auditoría y carga. Requiere Internet para dependencias y pesos. Registrar la GPU y los metadatos impresos.
4. Dejar `CORPUS_VERSION="historico"` para usar la base de 198 fragmentos. `PROMPT_VERSION="completo_v1"` prueba las nuevas instrucciones de completitud; elegir `historico` para repetir las anteriores. Se mantiene k=5 y generación greedy sin thinking. Las revisiones de pesos/dependencias históricas no se registraron, por lo que no se garantiza identidad de salidas. La celda 3b compara ambos prompts con idénticos fragmentos en los cinco casos revisados. El efecto del prompt nuevo está pendiente de medir; ver [experimento](Deliverable2_RAG/EXPERIMENTO_PROMPT.md).
5. En la demo, escribir una entrada o dejarla vacía para sortearla en ese momento. La celda **genera baseline y RAG**, muestra el contexto exacto enviado y guarda ambas respuestas. No imprime un baseline fijo.
6. Ejecutar las 50 comparaciones y la inspección del caso P25. Descargar el ZIP de resultados y guardar el notebook con sus salidas reales.
7. Completar `revision_pendiente.csv` aplicando el protocolo a ambos sistemas. Una revisión vacía impide calcular exactitud. Conservar los responsables y las decisiones.

Para recontar una corrida nueva ya revisada:

```bash
python -m Deliverable2_RAG.auditoria --run Deliverable2_RAG/runs/FECHA --review RUTA/revision_completada.csv --output RUTA/metricas.json
```

Cada carpeta de corrida incluye `metadata.json`, `predicciones.csv`, `trazas.jsonl` y `revision_pendiente.csv`. Los metadatos registran revisiones de pesos, versiones instaladas, dtype, dispositivos, hashes y límite del encoder. Para repetir, usar las revisiones impresas en `MODEL_REVISION` y `EMBEDDING_REVISION` y las mismas versiones de paquetes.

## Fallos y segunda versión del corpus

P25 responde «Las asignaturas correspondientes a las prioridades a) y b) del». La base histórica cortó el Art. 9 ante una referencia al Art. 7 al inicio de una línea. La referencia dejó de formar parte del artículo que explica la prohibición. El [reporte por pregunta](Deliverable2_RAG/reporte_comparativo_50_preguntas.md) también documenta excepciones omitidas (P24), respuesta parcial (P36) y citas incompletas.

La abstención de P3 es observable, pero sin el contexto histórico no se puede afirmar que se deba a que el Art. 12 quedó fuera del top-5. La nueva versión guarda esa evidencia.

El extractor corregido conserva encabezados consecutivos, trata aparte los dos artículos transitorios del RG y divide artículos largos en ventanas de 160 palabras con 30 de solapamiento. `base_conocimiento_v2.json` contiene **169 fragmentos**; sus resultados de generación están **pendientes de medir**.

```bash
# Requiere Poppler/pdftotext instalado en PATH.
python -m Deliverable2_RAG.preparar_corpus_v2
```

En el notebook, cambiar a `CORPUS_VERSION="v2"` crea un experimento nuevo. No atribuirle el 88% histórico. El parser tabular del calendario se conserva; esta revisión no certifica cobertura perfecta de todos los detalles de los PDF.

## Archivos de la entrega

| Archivo | Función |
| --- | --- |
| `rag_normativa_ingenieria_4b.ipynb` | Ejecución, demo real y evaluación en T4 |
| `Deliverable2_RAG/pipeline_colab.py` | Recuperación y generación, sin acceso al gold |
| `Deliverable2_RAG/deliverable2.tex` | Documento técnico vertical; borrador pendiente de cierre |
| `Deliverable2_RAG/GUION_VIDEO.md` | Guion de máximo tres minutos y preparación |
| `Deliverable2_RAG/PROTOCOLO_EVALUACION.md` | Criterios y límites de la revisión |
| `Deliverable2_RAG/evidencia_historica/` | Notebook y documentos previos, con inconsistencias conservadas como historial |
| `Corpus/` | Los tres PDF utilizados |

Los scripts `paso0_*` a `paso4_*`, `auto_evaluador.py` y los otros extractores se conservan como desarrollo histórico. La ruta recomendada para la entrega es el notebook actualizado y `pipeline_colab.py`.

## Cierre de la entrega

- Medir el prompt `completo_v1` frente al histórico con el mismo contexto; luego evaluar las 50 preguntas con el prompt elegido.
- Validar las decisiones de revisión con el equipo y declarar la convención sobre citas complementarias.
- Ejecutar en T4, conservar salidas y revisar ambos sistemas con el mismo criterio.
- Actualizar la tabla y el estado del `.tex` si se reporta una corrida nueva; no trasladar cifras entre versiones.
- Grabar un video de máximo 3:00 con entrada no escogida para favorecer el sistema, baseline visible, ejecución real y fallo explicado; subir con acceso abierto.
- Incorporar el enlace real al documento, compilar a una página vertical y comprobarla visualmente.
- Publicar el código/evidencia que corresponde al video y probar los enlaces antes del 30 de septiembre de 2026, 23:59.
