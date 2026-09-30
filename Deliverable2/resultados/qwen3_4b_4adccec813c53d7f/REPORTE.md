# Primera corrida Colab: tres variantes RAG

Corrida `4adccec813c53d7f`, importada desde el ZIP descargado por el usuario. Se preservan el ZIP y los archivos originales. Se verificaron hashes, correspondencia de CSV/checkpoints, 150 preguntas-variante, prompts y evidencia idéntica de la consulta entre variantes. No se regeneraron respuestas.

## Resultado de la revisión asistida

La IA de este chat leyó las 150 respuestas y aplicó la pauta v2 de dato suficiente, respaldo de fuentes y ausencia de falsedades. Los veredictos no son coincidencias automáticas de palabras: quedan registrados por respuesta y hash para que el equipo pueda revisarlos. No se considera una medición independiente ni una evaluación infalible.

| Variante | Correctas | Porcentaje | Tiempo medio de generación | Tokens de entrada medios | Tokens de salida medios |
|---|---:|---:|---:|---:|---:|
| RAG simple | 39/50 | 78.0% | 15.95 s | 1118.44 | 108.78 |
| RAG estructurado | 40/50 | 80.0% | 14.98 s | 1320.44 | 94.78 |
| RAG estructurado + few-shot | 36/50 | 72.0% | 19.29 s | 1890.44 | 114.22 |

**Todas las respuestas terminaron con EOS: cero cortes por límite y cero respuestas vacías.** La corrida se ejecutó en Tesla T4, Qwen3-4B NF4, modo sin thinking y muestreo con semilla fijada. Las latencias miden generación; la recuperación ya estaba calculada.

El estructurado supera al simple por **una sola respuesta**. Una semilla sobre 50 preguntas conocidas no permite afirmar superioridad general. El few-shot utilizado empeora esta corrida; esto no demuestra que todo few-shot sea perjudicial.

## Por categoría

| Categoría | Simple | Estructurado | Few-shot |
|---|---:|---:|---:|
| factual | 7/10 | 9/10 | 8/10 |
| numerica | 8/10 | 7/10 | 6/10 |
| condicional | 7/10 | 6/10 | 6/10 |
| cruce | 7/10 | 8/10 | 7/10 |
| abstencion | 10/10 | 10/10 | 9/10 |

## Hallazgos verificables

- **P24:** few-shot conserva las excepciones PLEV/primer año. El estructurado dice solo «salvo excepciones» y el simple cambia PLEV por Plan de Estudio. Aquí few-shot sí ayuda.
- **P25:** simple identifica asignaturas atrasadas y obligatorias reprobadas; los otros dos repiten prioridades a) y b) sin explicarlas, pese a recibir el artículo 7 completo. Es un fallo de uso de la evidencia, no de extracción ni de corte.
- **P36:** las tres respuestas ya dan fechas y ocho créditos, pero omiten la excepción por falta de requisitos. El simple tampoco cita sus fuentes. Recuperar la evidencia completa no garantiza conservar todas las condiciones.
- **P38:** persiste el problema de respaldo de la aplicación del RG en Ingeniería. El estructurado inventa apoyo en RI-FI art. 6 (cupos); el artículo pertinente, RI-FI art. 2, no fue recuperado.
- **P34:** se aceptan las tres respuestas: RG art. 31 basta para el derecho/plazo preguntados. La ausencia de RI-FI art. 25 en la pauta de recuperación no obliga a declarar incorrecta una respuesta suficiente.
- **P40:** las tres respuestas identifican el reglamento y el 40%, con las fuentes pertinentes.
- **P41–44 y P49:** las tres variantes reconocen las ausencias a partir del inventario; no se atribuyen contenidos a artículos inexistentes.

## Efecto no deseado de mis ejemplos few-shot

El asistente diseñó cuatro demostraciones ficticias para evitar filtrar las respuestas del examen. Qwen copió el rótulo «norma ficticia» a fuentes reales en **P02, P11, P16, P18 y P25**. También inventó **[EJ-F] en P47**, ID que no está en los ejemplos ni en la evidencia. Es un defecto del diseño de demostraciones y de su uso por el modelo; no un problema que hubiera introducido el usuario en el corpus.

P02, P11 y P16 se rechazan únicamente por esa descripción falsa de la fuente, aun cuando el dato es correcto. En P18 y P25 hay además errores sustantivos. Como sensibilidad —sin reemplazar la métrica principal— si se ignorara solo el rótulo «norma ficticia» de esos tres casos, few-shot tendría 39/50 (78%). La cita inventada [EJ-F] sigue siendo un error. Este desglose permite discutir la severidad del criterio sin ocultar las respuestas.

No se cambió el prompt ni se corrigieron salidas después de ver el resultado. Una versión con demostraciones sin esos rótulos deberá ser otra corrida, con su propia identidad, y no una sustitución de esta.

## Cómo se aplicó la pauta

- Se exige respaldo de fuentes para las preguntas respondibles. Por eso una fecha correcta sin cita puede fallar (simple P39), mientras que «según el calendario proporcionado» se acepta en P37 porque el documento/semestre son inequívocos en la consulta.
- Se penalizan condiciones que cambian la aplicación de una regla y citas que no respaldan afirmaciones adicionales. No se exige copiar todos los detalles complementarios de la referencia.
- P03: se acepta el derecho a una recuperación; el comentario sobre un máximo no se interpreta como un derecho a recuperaciones ilimitadas. P20 few-shot: el comentario sobre RG art. 25 se interpreta referido al plazo de regularización consultado.
- P18 estructurado contiene texto de la instrucción «omite esta línea»; se registra como defecto de formato, pero el dato y fuente son correctos. «Interino» junto a RI-FI y el artículo correcto se acepta como denominación imprecisa; «Reglamento de Inglés…» (P15 simple) sí identifica una fuente inventada.
- Las negativas sobre premisas falsas no requieren citar un artículo inexistente. Se rechazan añadidos falsos o citas inventadas incluso si el dato principal coincide.

Estos límites de juicio y los errores exclusivamente de cita merecen revisión del equipo. Los archivos de veredictos se pueden corregir con trazabilidad si se discrepa; no deben ajustarse para conseguir un porcentaje deseado.

## Archivos para revisar y reproducir los porcentajes

- [Registro de las 150 decisiones](revision_asistida.json): motivo y etiquetas diagnósticas por caso, identificados como revisión asistida en chat.
- [Simple: tabla de evaluación](evaluacion/rag_simple/reporte/evaluacion.csv).
- [Estructurado: tabla de evaluación](evaluacion/rag_estructurado/reporte/evaluacion.csv).
- [Few-shot: tabla de evaluación](evaluacion/rag_estructurado_fewshot/reporte/evaluacion.csv).
- Cada carpeta de evaluación incluye el paquete de pregunta/referencia/respuesta, veredictos firmados con hashes y resumen por categoría. `evaluar.py resumir` reproduce los porcentajes a partir de esos veredictos; no vuelve a juzgar la semántica.
- [ZIP original](qwen3_4b_4adccec813c53d7f.zip), [configuración](original/configuracion.json) y [comparación técnica](comparacion.json).

## Límite de la conclusión y continuación

El 4% de E1 se conserva como resultado histórico y no se recalcula. Estos prompts usan cuantización/muestreo diferentes del baseline antiguo; para una comparación causal de RAG frente a ausencia de documentos haría falta un baseline emparejado. Tampoco se ha medido generalización: las 50 preguntas ya se utilizaron para desarrollo del recuperador.

Antes de ajustar otra vez los prompts, el equipo debería revisar una muestra de los juicios —en especial rechazos por citas/etiquetas—. Después se puede fijar una variante nueva de ejemplos y reservar preguntas nuevas no utilizadas en los ajustes. No se afirma que unos ejemplos corregidos vayan a mejorar hasta medirlo.

## Comparación por pregunta

| Pregunta | Simple | Estructurado | Few-shot |
|---:|---|---|---|
| P01 | Correcta | Incorrecta | Correcta |
| P02 | Correcta | Correcta | Incorrecta |
| P03 | Correcta | Correcta | Correcta |
| P04 | Correcta | Correcta | Correcta |
| P05 | Correcta | Correcta | Incorrecta |
| P06 | Incorrecta | Correcta | Correcta |
| P07 | Correcta | Correcta | Correcta |
| P08 | Correcta | Correcta | Correcta |
| P09 | Incorrecta | Correcta | Correcta |
| P10 | Incorrecta | Correcta | Correcta |
| P11 | Incorrecta | Incorrecta | Incorrecta |
| P12 | Correcta | Correcta | Correcta |
| P13 | Correcta | Incorrecta | Incorrecta |
| P14 | Correcta | Correcta | Correcta |
| P15 | Incorrecta | Incorrecta | Correcta |
| P16 | Correcta | Correcta | Incorrecta |
| P17 | Correcta | Correcta | Correcta |
| P18 | Correcta | Correcta | Incorrecta |
| P19 | Correcta | Correcta | Correcta |
| P20 | Correcta | Correcta | Correcta |
| P21 | Correcta | Correcta | Correcta |
| P22 | Correcta | Correcta | Correcta |
| P23 | Correcta | Correcta | Correcta |
| P24 | Incorrecta | Incorrecta | Correcta |
| P25 | Correcta | Incorrecta | Incorrecta |
| P26 | Incorrecta | Correcta | Incorrecta |
| P27 | Correcta | Correcta | Correcta |
| P28 | Correcta | Incorrecta | Incorrecta |
| P29 | Incorrecta | Correcta | Correcta |
| P30 | Correcta | Incorrecta | Incorrecta |
| P31 | Correcta | Correcta | Correcta |
| P32 | Correcta | Correcta | Correcta |
| P33 | Correcta | Correcta | Correcta |
| P34 | Correcta | Correcta | Correcta |
| P35 | Correcta | Correcta | Correcta |
| P36 | Incorrecta | Incorrecta | Incorrecta |
| P37 | Correcta | Correcta | Correcta |
| P38 | Incorrecta | Incorrecta | Incorrecta |
| P39 | Incorrecta | Correcta | Incorrecta |
| P40 | Correcta | Correcta | Correcta |
| P41 | Correcta | Correcta | Correcta |
| P42 | Correcta | Correcta | Correcta |
| P43 | Correcta | Correcta | Correcta |
| P44 | Correcta | Correcta | Correcta |
| P45 | Correcta | Correcta | Correcta |
| P46 | Correcta | Correcta | Correcta |
| P47 | Correcta | Correcta | Incorrecta |
| P48 | Correcta | Correcta | Correcta |
| P49 | Correcta | Correcta | Correcta |
| P50 | Correcta | Correcta | Correcta |

## Decisión posterior a la revisión

El usuario decidió retirar few-shot de la comparación principal y continuar con simple y estructurado. Se conservan aquí las tres condiciones originales, sin cambiar respuestas ni porcentajes. Las dos variantes restantes ya tienen 100 respuestas evaluadas; no requieren repetirse solo por retirar few-shot. Esta selección utiliza resultados del conjunto de desarrollo y no constituye validación independiente.
