# Revisión de los cuadernos anteriores frente al actual

Se inspeccionaron todas las celdas de dos archivos diferentes y el módulo del que depende el segundo:

- [Original histórico con salidas guardadas](../../Archivo/2026-09-30_desarrollo_previo/Deliverable2_RAG/evidencia_historica/rag_qwen3_4b_original.ipynb): 21 celdas. Es el que contiene el resultado impreso de 98%.
- [Revisión posterior del cuaderno RAG](../../Archivo/2026-09-30_desarrollo_previo/rag_normativa_ingenieria_4b.ipynb): 18 celdas; delega la inferencia al módulo `pipeline_colab.py`. Ya había corregido varios problemas del original.
- [Pipeline de la revisión posterior](../../Archivo/2026-09-30_desarrollo_previo/Deliverable2_RAG/pipeline_colab.py).

Los números de celda indicados a continuación empiezan en **0**, como en el archivo ipynb. Se inspeccionaron código, textos y salidas; no se volvió a ejecutar la inferencia histórica. Sí se ejecutó aisladamente el evaluador guardado sobre ejemplos controlados para demostrar sus fallos.

## Qué estaba bien

1. La arquitectura básica de RAG era válida: separar recuperación y generación, usar E5 multilingüe, prefijos `passage:`/`query:`, similitud coseno y Qwen3-4B. No hacía falta añadir una base vectorial compleja para un corpus tan pequeño. Que `encode()` no normalizara explícitamente los vectores no era un fallo en ese código: después utilizaba `util.cos_sim`.
2. El formato dato/cita y la instrucción de abstenerse eran buenas intenciones. El problema era cómo se definía la abstención y cómo se verificaba la respuesta.
3. El original ya aplicaba `enable_thinking=False`. No faltaba implementar thinking; la comparación actual conserva ese modo.
4. Separar la carga de modelos de la demostración, medir tiempos y exportar respuestas eran decisiones útiles.
5. La revisión posterior tenía una mejora especialmente importante: baseline y RAG se ejecutaban realmente, mostraban el contexto exacto, guardaban trazas y dejaban una plantilla de evaluación sin asignar aciertos automáticamente.
6. La revisión posterior ya comparaba prompts con idéntico contexto en los cinco casos de desarrollo, preservaba excepciones en sus instrucciones y reconocía que no debía extrapolarse la mejora de esos casos a todo el conjunto.

## Problemas concretos del original histórico

| Ubicación | Hallazgo | Consecuencia |
|---|---|---|
| Celdas 5 y 11 | Usa la base histórica de 198 fragmentos y entrega los cinco mejores sin expandir artículos ni remisiones. | Una regla puede llegar incompleta o sin el artículo que explica sus prioridades. Los problemas de extracción se documentaron por separado. |
| Celda 11 | Ordena responder «No está en la normativa» cuando la información no aparece en el contexto recuperado. | Confunde ausencia en unos fragmentos con ausencia en toda la normativa. |
| Celda 11 | El formato se solicita por prompt, sin esquema/gramática ni restricción de tokens de salida. | No era técnicamente decodificación restringida ni una garantía de formato, pese a llamarse «Structural Forcing». |
| Celda 11 | Límite de 256 tokens sin guardar tokens de salida ni motivo de parada. | No se podía distinguir un corte por presupuesto de una respuesta que terminó normalmente. No prueba que P25 se cortara por generación: su fragmento fuente ya estaba cortado. |
| Celda 13 | Muestra los tres mejores fragmentos, pero genera con cinco. | Lo mostrado como contexto no es exactamente todo lo que recibió el modelo. |
| Celda 13 | El baseline se imprime como una cadena fija; solo RAG se ejecuta en esa celda. | Sirve como ilustración histórica si se etiqueta así, no como dos inferencias en vivo. La revisión posterior sí lo corrigió. |
| Celda 17 | Evalúa por coincidencias parciales de números/palabras y basta una fuente reconocida. | Puede aprobar respuestas incompletas, cifras erróneas o una cita del documento equivocado. |
| Celda 19 | La respuesta mostrada a P3 es «No está en la normativa», pero el diagnóstico afirma que confundió tres evaluaciones sumativas con recuperación. | La explicación no está respaldada por esa salida; además no se guarda el contexto de esa ejecución para confirmar la atribución al retriever. RAG no garantiza recall. |
| Celdas 3, 5 y 9 | Dependencias abiertas, rama del repo sin fijar y modelos sin revisión fijada. | Reejecutar en otra fecha podía cambiar el experimento. |
| Celdas 8–9 | El texto afirma bfloat16 y GPU; el código usa dtype y distribución de dispositivos automáticos. | La afirmación no quedaba demostrada sin registrar dtype y mapa efectivo. La revisión posterior ya los registraba. |
| Celda 15 | Acumula los resultados en memoria y escribe el CSV al final. | Una desconexión antes del final podía perder el avance. La revisión posterior ya guardaba por pregunta. |

### Contraejemplos reproducidos del evaluador

Se aislaron `NUM_WORDS`, `normalizar()` y `calificar_robusto()` de la celda 17, sin ejecutar sus lecturas de CSV ni la inferencia.

- Gold: **80%, Art. 13, RI-FI**. Predicción: **«DATO: 8%. CITA: Art. 13, Reglamento General.»**. Devuelve `True`: `80` comienza por `8`, y el número de artículo basta aunque sea otro reglamento.
- Categoría abstención. Predicción: **«CITA: Ninguna. DATO: El artículo 90 exige pagar 50000 pesos.»**. Devuelve `True`: la palabra «ninguna» basta aunque el dato sea inventado.
- La respuesta guardada de **P36** solo da las fechas, sin el mínimo de créditos, y el evaluador devuelve `True`.
- La respuesta guardada de **P40** da 40% pero cita únicamente el artículo 29; el evaluador devuelve `True` aunque ese dato requiere el artículo 30.

Esto explica por qué el 98% impreso no certifica completitud y respaldo de las respuestas. No se recalcula aquí una nueva exactitud semántica ni se modifica el 4% histórico de E1.

### Estado reproducible del archivo guardado

El original histórico conserva salidas, pero sus celdas 13 y 17 contienen cadenas con saltos de línea literales que hoy no compilan tal como están guardadas. La celda 17 también contiene cinco caracteres de retroceso `U+0008` donde parecen haberse pretendido límites de palabra `\b`. Una salida guardada no demuestra que ese mismo código actual se ejecutó para producirla.

Al ejecutar solo las funciones actuales del evaluador sobre el CSV histórico se obtiene **30/50**, no el 49/50 impreso. Esto es una **inconsistencia entre código y salida almacenada**, no una evaluación alternativa válida del modelo: ese evaluador sigue siendo defectuoso. No se puede determinar desde el archivo cuándo se introdujeron esas diferencias ni atribuirlas a la ejecución original.

## Qué aporta la revisión posterior y qué quedaba pendiente

El segundo cuaderno ya sustituye el contraste escrito a mano por inferencias reales; unifica el k mostrado y enviado; guarda metadata, hashes, contextos y progreso; y evita puntuar nuevas respuestas usando el evaluador permisivo. Esas correcciones no deben describirse como errores que seguían presentes en ambas versiones.

Todavía conserva 256 tokens de salida, recuperación top-k sin expansión de artículos y una comprobación de longitud de E5 posterior a codificar. Las revisiones del modelo son parámetros opcionales que por defecto quedan en `None`. Además, las bases v1/v2 seguían teniendo los problemas de calendario revisados anteriormente. La revisión nueva del corpus y el cuaderno actual abordan esos puntos.

## Diferencias que también debo reconocer en el cuaderno nuevo

- El anterior permitía **una pregunta nueva con recuperación en vivo**; el nuevo contiene 50 contextos congelados. Esta elección facilita comparar prompts, pero no reemplaza aún una demostración RAG completa ante preguntas nuevas.
- La revisión posterior también podía repetir un **baseline sin documentos bajo la misma configuración**. El nuevo ejecuta las tres condiciones RAG solicitadas; no ofrece todavía ese control adicional. El 4% publicado sigue siendo histórico.
- El nuevo usa NF4 de 4 bits y muestreo con semilla; el original utilizaba carga automática sin esa cuantización y `do_sample=False`. No corresponde atribuir toda diferencia respecto de resultados antiguos únicamente al prompt o al corpus. Dentro de la nueva corrida, las tres condiciones sí comparten modelo, precisión y parámetros.
- La latencia del original incluía recuperación e inferencia; la del nuevo mide generación con evidencia precalculada. Es necesario indicar esta diferencia al comparar tiempos.

## Mejoras incorporadas sin alterar la corrida en curso

Se añadieron al final del cuaderno principal tres celdas opcionales de diagnóstico. Se verificó que **sus primeras 20 celdas son idénticas** a la versión entregada antes de esta revisión: no cambian prompts, few-shot, datos, semillas ni parámetros.

Las celdas permiten ver las tres respuestas para una pregunta junto a su evidencia exacta y resumir por categoría tiempos, tokens, respuestas vacías y posibles cortes. También alertan si un ID de cita reconocido no está entre las fuentes recibidas, incluyendo citas accidentales de los ejemplos ficticios. No convierten esas alertas en veredictos de corrección.

Para quien ya está ejecutando la versión anterior, se creó [Revisar_resultados_RAG.ipynb](Revisar_resultados_RAG.ipynb). Abre el ZIP exportado, verifica sus hashes y permite el mismo diagnóstico **sin GPU y sin volver a generar respuestas**. No hace falta detener la ejecución en Colab.

La demo de recuperación para preguntas nuevas y el baseline emparejado son componentes rescatables para la fase siguiente; no se introdujeron a mitad de este experimento.
