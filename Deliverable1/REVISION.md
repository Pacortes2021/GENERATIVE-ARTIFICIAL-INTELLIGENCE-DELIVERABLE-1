# Revisión del Deliverable 1

Fecha: 30 de septiembre de 2026. Revisión del material conservado, sin ejecutar nuevamente los modelos ni modificar la entrega histórica.

**E1 ofrece una base útil: define una tarea concreta y demuestra que el prompting directo no responde de manera fiable con datos y citas correctos. Antes de reutilizar su evaluación, hay que aclarar los criterios de corrección y moderar algunas conclusiones del informe.**

## Material y comprobaciones

Se revisaron el [enunciado](enunciado.pdf), el [informe presentado](informe/deliverable1.pdf), los dos [notebooks finales](notebooks/), sus 100 respuestas guardadas, los tres [CSV](datos/), la prueba preliminar de diez preguntas y los tres documentos de [Corpus](../Corpus/). Las referencias normativas de esta revisión corresponden a esas copias; no certifican la vigencia actual de los reglamentos.

- Las 50 preguntas y sus campos de referencia coinciden entre ambos notebooks y `test_set_50.csv`.
- Las 50 respuestas visibles de cada notebook coinciden con su CSV correspondiente, normalizando únicamente espacios y saltos de línea de la presentación HTML.
- Los bloques Python de los notebooks finales se pueden analizar sintácticamente, excluyendo la instrucción de instalación propia de Colab. No hay errores de ejecución guardados.
- Los seis archivos originales de E1 mantienen los SHA-256 de `INVENTARIO.json`.
- El informe tiene una página, metadatos de pdfTeX y una composición legible de dos columnas. No se encontró su fuente `.tex` en el repositorio.
- El repositorio de `alnicozu` citado en el PDF responde a `git ls-remote` (`HEAD` observado: `deb965ec13b8ec47bc0ef7625bc8739480dcb67c`). Es el upstream del fork de `Pacortes2021`, no un enlace roto. La reorganización local todavía no está publicada.

## Qué hizo realmente E1

La tarea consiste en responder preguntas en español sobre el Reglamento General (RG), el Reglamento Interno de Ingeniería (RI-FI) y el Calendario 2026 (CAL). Se exige dato correcto y una fuente que lo respalde; las premisas falsas deben detectarse sin inventar contenido.

Se propusieron tres candidatos y se ejecutaron dos: Qwen3-4B y Qwen3-8B. Salamandra quedó como candidato bibliográfico; no hay una corrida suya en E1. El enunciado pide proponer tres modelos, no necesariamente experimentar con los tres.

Las corridas finales usan las mismas 50 preguntas, sin documentos en el prompt, `enable_thinking=False`, `do_sample=False` y un máximo de 256 tokens nuevos. La calificación es **manual**, mediante listas de veredictos incluidas en los notebooks.

| Evidencia histórica | Qwen3-4B | Qwen3-8B |
| --- | ---: | ---: |
| Factual | 0/10 | 1/10 |
| Numérica | 0/10 | 0/10 |
| Condicional | 0/10 | 0/10 |
| Cruce | 0/10 | 0/10 |
| Abstención | 2/10 | 1/10 |
| Total publicado | **2/50 (4%)** | **2/50 (4%)** |
| Preguntas con respuesta en el corpus | 0/40 | 1/40 |
| Preguntas aceptadas | P49, P50 | P3, P50 |

La prueba preliminar obtuvo 2/10 (20%) en otro conjunto. No contradice el 4% del experimento final ni debe mezclarse con él.

El fallo observado combina datos incorrectos, citas incorrectas, contenido inventado y negativas injustificadas a responder. Por ejemplo, 4B responde 60 créditos en P11 cuando RI-FI art. 8 establece un mínimo general de ocho. También puede acertar un dato aislado y citar mal: eso no satisface la métrica declarada. Por tanto, 0/40 no significa que todas las palabras o todos los datos de esas respuestas sean falsos.

## Hallazgos prioritarios

### 1. Un acierto publicado de 4B contiene información inventada

P49 se calificó como correcta porque niega un feriado el 30 de septiembre. Sin embargo, añade que ese día de 2026 es lunes —es miércoles— y cita un supuesto art. 13 de un “Reglamento de Feriados Nacionales”, ajeno al corpus. El propio informe presenta esa invención como evidencia de fallo.

Esto es inconsistente con aceptar únicamente respuestas respaldadas y sin invenciones. Si se invalida **solo P49** por ese motivo, el resultado de 4B pasa a **1/50 (2%)**, manteniéndose 0/40 en preguntas respondibles. Esa es una sensibilidad de la puntuación bajo el criterio explícito, no una nueva corrida ni un reemplazo de la cifra entregada.

P50 recibió una negativa genérica en ambos modelos. Puede aceptarse con la rúbrica histórica; si se exige explicar exactamente la premisa falsa, habrá que establecerlo de antemano y aplicarlo a todas las respuestas.

### 2. Volver a ejecutar los notebooks no produce una nueva evaluación válida automáticamente

Las listas `veredictos` están escritas a mano y corresponden a las respuestas históricas. Si una nueva ejecución produce otras respuestas, el notebook les asignará las mismas etiquetas y volverá a mostrar 4%, siempre que conserve 50 filas. Esto no invalida las salidas guardadas, pero hace imprescindible recalificar cada nueva corrida.

También falta una justificación individual de cada veredicto. El CSV calificado de 8B que el código exporta (`resultados_baseline_8b.csv`) no está conservado; sus etiquetas sí están en el notebook.

### 3. Qwen3-8B supera el límite literal del enunciado

El nombre comercial redondeado no equivale al número total de parámetros. La ficha oficial declara **8,2B** para [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B), mientras el enunciado permite como máximo 8 mil millones. La cuantización disminuye memoria, no el número de parámetros. Bajo una interpretación literal, ese candidato no cumple; no debe presentarse sin matices como “el máximo permitido”.

El modelo principal [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) declara 4,0B y sí cumple. [Salamandra-7B-instruct](https://huggingface.co/BSC-LT/salamandra-7b-instruct) declara 7.768.117.248 parámetros y también cumple. Las fichas identifican licencia Apache 2.0. La decisión docente sobre admitir un nombre nominal “8B” no está documentada.

### 4. Los benchmarks citados usan otro modo de inferencia

Las cifras de E1 son reales, pero proceden de la tabla 17 del reporte Qwen3, correspondiente a **thinking**. La tabla 18 presenta **non-thinking**, el modo utilizado en los notebooks:

| Benchmark | E1: 4B / 8B, thinking | Non-thinking: 4B / 8B |
| --- | --- | --- |
| IFEval | 81,9 / 85,0 | 81,2 / 83,0 |
| Multi-IF | 66,3 / 71,2 | 61,3 / 69,2 |
| MMMLU, 14 idiomas | 69,8 / 74,4 | 61,7 / 66,9 |

Conviene identificar el modo y no presentar esos benchmarks como resultados del corpus UdeC. El protocolo del paper también usa parámetros de generación distintos del greedy local. Fuente: [Qwen3 Technical Report, tablas 17 y 18](https://arxiv.org/html/2505.09388v1).

[IberBench](https://arxiv.org/html/2504.16921v1) respalda la discusión general sobre modelos pequeños y lenguas ibéricas; encuentra resultados destacados entre 3,1B y 10B. No establece que 4B sea el “tamaño mínimo seguro” para esta tarea, ni evalúa este corpus. Esa frase debe tratarse como una elección de diseño, no como un umbral demostrado. La afinidad lingüística de Salamandra justifica considerarlo, pero no demuestra rendimiento en normativa UdeC; mencionar un derivado jurídico tampoco sustituye esa evidencia.

### 5. El diagnóstico causal es más fuerte que el experimento

El experimento demuestra fallo de respuesta y citación sin acceso documental. No permite inspeccionar qué información está o no en los pesos, ni demostrar que el tamaño sea irrelevante en general. La comparación cambia tanto el tamaño como la precisión: 4B usa carga automática y 8B cuantización a cuatro bits.

Tampoco hay en E1 una comparación con contexto correcto que demuestre que RAG resuelva el problema. Una formulación respaldada sería:

> En las configuraciones evaluadas, aumentar el tamaño nominal de 4B a 8B no mejoró la exactitud global publicada. Los errores son compatibles con falta de acceso fiable a las fuentes. Se propone recuperación documental y se evaluará su efecto posteriormente.

### 6. El prompt confunde desconocimiento con ausencia de información

La instrucción pide decir que algo “no está en la normativa” cuando el modelo no tiene la información. Son situaciones diferentes: el modelo puede desconocer una regla que sí existe. Esto contribuye a que una abstención parezca una afirmación falsa sobre el corpus.

La instrucción de brevedad tampoco define qué excepciones o partes de una respuesta compuesta deben conservarse. Un prompt futuro puede pedir todas las partes solicitadas, las excepciones pertinentes y la fuente de cada afirmación. Su eficacia debe medirse con nuevas respuestas y nuevos veredictos; un mejor prompt por sí solo no aporta los documentos ausentes.

## Revisión de las 50 referencias

Los números P1–P50 corresponden al orden de las filas del CSV, comenzando en uno. “Respaldada” significa que el dato y la referencia están presentes en el corpus; no significa que la respuesta del modelo sea correcta. Las observaciones proponen aclaraciones para una versión futura, sin cambiar el test entregado.

| Preguntas | Referencia y resultado de la revisión |
| --- | --- |
| P1–P3 | Respaldadas: 4,0 y al menos tres evaluaciones, RI-FI 11; una recuperación, RI-FI 12. P1 también admite RG 23 como respaldo de la nota, si se contextualiza correctamente. |
| P4 | Respaldada: escala 1–7 y hasta un decimal, RG 23. |
| P5–P8 | Respaldadas: Memoria (RI-FI 29), anticipación mínima de una semana (10), Comité en primera instancia (16), renuncia irrevocable (26). |
| P9–P10 | Respaldadas: dos períodos ordinarios de 19 semanas (RG 16); Primer Año Común no puede convalidar (RI-FI 22). |
| P11 | Ocho créditos es la regla general (RI-FI 8). La referencia omite las excepciones por término de estudios y falta de requisitos. Para una pregunta personal, conviene aclararlas. |
| P12–P13 | Respaldadas: menos de 15 al término del segundo semestre y promedio inferior a diez desde el cuarto (RI-FI 14 a–b). |
| P14 | 80% está respaldado por RI-FI 13. Reformular “asistencia mínima máxima” como “máximo porcentaje de asistencia exigible”. No es una asistencia obligatoria universal del 80%. |
| P15 | Respaldada: 4,5 para convalidación, RI-FI 21. |
| P16–P17 | Los plazos existen, pero las preguntas deben distinguir trámites: cuatro primeras semanas de ingreso a la nueva carrera para asignaturas cursadas en otras carreras (RI-FI 22); primeros treinta días del período para reconocimiento de contenidos mediante evaluación (23). No tratarlos como dos plazos intercambiables de un trámite genérico. |
| P18–P20 | Respaldadas: hasta 36 créditos adicionales (RI-FI 31), semestre de 19 semanas (RG 16), tres días hábiles para solicitar regularización (RG 26). |
| P21–P22 | Respaldados los umbrales 4,5 / 4,2 / 5,0 (RI-FI 17–19). Cumplir el promedio no equivale por sí solo a obtener admisión; los artículos remiten a otros requisitos. |
| P23 | Respaldada: no revalidar si ya se cursó y reprobó en el plan (RI-FI 20). |
| P24 | La referencia incorpora las dos excepciones y es sustancialmente correcta (RI-FI 14 c). Precisar PLEV **del año académico correspondiente** y primer año **de permanencia**. |
| P25 | Respaldada para lo preguntado: asignaturas atrasadas y obligatorias reprobadas todavía no aprobadas (RI-FI 9, en relación con 7 a–b). La modificación también debe respetar el mínimo del art. 8; no hace falta exigir ese dato adicional para una pregunta limitada a qué asignaturas no se pueden eliminar. |
| P26 | Respaldada: solicitar reincorporación a Vicedecanatura (RI-FI 27). |
| P27 | Referencia incompleta: RI-FI 25 permite certificado DAFE sin deudas **o con pago debidamente garantizado**; Bibliotecas debe certificar que no se adeuda material. |
| P28 | Referencia incompleta: RG 29 exceptúa a quienes inscribieron una o más asignaturas anuales en el período anterior. La respuesta categórica omite una excepción que cambia el resultado. |
| P29–P30 | Respaldadas: regularización en tres días hábiles (RG 26); hasta 100% en actividades indicadas (RI-FI 13). Para describir el procedimiento completo, P29 debe mencionar solicitud al profesor y justificativos. |
| P31 | Respaldada por RI-FI 34; RG 60 es otra fuente pertinente. Un solo documento permite contestarla. |
| P32–P33 | Fechas correctas: 04-sep y 02-abr de 2026. Basta la página del semestre correspondiente de CAL para responder la fecha; RI-FI 9 es respaldo complementario. |
| P34 | Derecho a **solicitar** suspensión y plazo de cuatro semanas respaldados por RG 31. RI-FI 25 agrega trámite y remisión al calendario. No confundir solicitud con aprobación automática. |
| P35 | Respaldada: clases comienzan el 10-ago-2026, CAL segundo semestre. Solo necesita un documento. |
| P36 | Respaldada: inscripción 03–07-ago-2026 y mínimo general de ocho créditos, CAL + RI-FI 8. Sí combina documentos; el mínimo tiene las excepciones de P11. |
| P37 | Respaldada: término de clases el 11-dic-2026, CAL. La precisión “término de clases” evita confundirlo con el fin de recuperaciones. |
| P38 | La escala y el 4,0 están respaldados por RG 23 y RI-FI 11; RI-FI 2 vincula los reglamentos. La pregunta solicita aplicabilidad y nota de aprobación, no pide expresamente repetir el rango 1–7. Definir de antemano si ese detalle será obligatorio. |
| P39 | Respaldada: recuperaciones 14–23-dic-2026, CAL. RI-FI 12 explica el derecho, pero no es necesario para responder las fechas. |
| P40 | Respaldada: Reglamento de Memoria de Título y ponderación del 40%, RI-FI 29–30. Combina dos artículos del mismo documento. |
| P41–P42 | Correcta premisa falsa: RI-FI llega al artículo 35; no existen 90 ni 36 en la copia. |
| P43–P44 | Correcta premisa falsa: no existen RG 100 ni 70. RG tiene 60 artículos permanentes **y dos artículos transitorios**; evitar describirlo como solo 60 artículos sin esa precisión. |
| P45–P46 | Correctas premisas falsas: RI-FI 14 solo tiene a–c; RI-FI 25 solo a–b. |
| P47 | Correcto: RI-FI 8 no fija máximo. No extender esa ausencia a todos los reglamentos o a todo el sistema de inscripción. |
| P48 | Correcto: RI-FI 12 no fija una nota mínima de recuperación. Sí dispone que el profesor comunique requisitos y ponderaciones; ausencia de un número en ese artículo no significa ausencia de requisitos. |
| P49 | CAL no consigna feriado el 30-sep; consigna 18-sep. Limitar la respuesta al calendario suministrado, sin presentar su lista como catálogo exhaustivo de feriados nacionales. Revisar la etiqueta positiva de 4B descrita arriba. |
| P50 | Correcto: RI-FI 19 no especifica un promedio para una tercera carrera. No inferir de ello una prohibición general de cursarla. |

La categoría “cruce” no contiene diez casos que exijan recuperar varios documentos: P35/P37 son fechas de CAL y P40 usa solo RI-FI, entre otros. Hay además solapamiento entre P9/P19 y P20/P29. El conjunto sirve como prueba inicial, pero diez etiquetas por categoría no garantizan diez capacidades independientes ni diez casos de dificultad equivalente.

Una referencia no debe convertirse en una coincidencia textual obligatoria: aceptar una fuente alternativa que respalde realmente la afirmación es compatible con evaluación estricta. Hay que separar dato incorrecto, fuente incorrecta, omisión relevante e información adicional falsa.

## Ejecución y reproducibilidad

Las salidas guardadas registran una Tesla T4 con 15,6 GB. Para 4B se imprime 6,44 GB mediante `torch.cuda.memory_allocated()` después de cargar el modelo; además aparece una advertencia de parámetros desplazados a CPU. El código usa `torch_dtype="auto"`: no registra el dtype efectivo. Por ello no sustenta por sí solo la descripción “íntegramente en GPU, bf16, consumo total de 6,44 GB”. Esa lectura puntual tampoco mide el pico durante generación ni la RAM de CPU.

8B registra 6,41 GB y configura NF4 a cuatro bits con cómputo `float16`. Hay evidencia de ejecución de ambas configuraciones, pero no una comparación controlada de memoria o velocidad.

No quedaron fijadas las versiones exactas de dependencias ni revisiones de los pesos. Los contadores de ejecución son nulos aunque las salidas están conservadas. Esto reduce la trazabilidad del entorno y del orden de ejecución; no demuestra que las salidas sean inválidas. La prueba preliminar tampoco debe usarse para atribuir al experimento final su configuración o consumo.

El código no guarda número de tokens generados, token final ni motivo de parada. Por tanto, una salida aparentemente cortada no permite atribuir la causa con certeza al límite de 256 tokens. En particular, **P25 de E1-4B contiene “No está en la normativa.”**, una respuesta completa aunque incorrecta; no es la salida cortada discutida en desarrollos posteriores.

## Relación con la rúbrica y próximo paso

| Criterio de E1 | Balance de la revisión |
| --- | --- |
| Especificación de tarea | Clara y concreta; falta precisar completitud, fuentes alternativas y abstención. |
| Diagnóstico | Evidencia suficiente de fallo directo; las afirmaciones sobre pesos, tamaño y solución deben moderarse. |
| Tres candidatos | Están propuestos y justificados; revisar el total de parámetros de 8B y el modo de los benchmarks. El supuesto mínimo seguro de 4B no está demostrado. |
| Viabilidad | Las salidas evidencian ejecución; matizar dtype, CPU offload y medición de memoria. |
| Repositorio | Material local trazable y enlace upstream accesible. Falta fuente LaTeX y exportación calificada de 8B; la reorganización sigue local. |
| Formato y redacción | Una página producida por pdfTeX, bien estructurada; corregir precisión científica en una eventual revisión. |

No se asigna una nota docente ni se necesita rehacer todo E1. El siguiente paso útil es fijar una rúbrica por pregunta y una versión revisada de las referencias, preservando las salidas originales. Después se podrá recalificar la misma evidencia con un criterio consistente y separar claramente **resultado publicado** de **resultado auditado**. Cualquier cambio de prompt requiere una corrida identificada y una calificación nueva.
