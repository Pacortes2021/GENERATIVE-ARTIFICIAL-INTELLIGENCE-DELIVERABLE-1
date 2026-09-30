# Prueba de recuperación antes de ejecutar Qwen

## Estado actual: segunda corrida

La [recuperación mejorada](resultados/e5_estructurado_v2/REPORTE.md) alcanza **43/45 preguntas con cobertura completa de la pauta**, frente a 40/45 de la primera corrida. Mejora las preguntas 25, 36 y 50, sin perder cobertura en las anteriores. Las cinco consultas de ausencia incluyen ahora comprobaciones contra el inventario completo del corpus. Las preguntas 34 y 38 conservan limitaciones documentadas; no se añadieron manualmente sus fuentes esperadas.

`recuperar_mejorado.py` añade búsqueda exacta por artículo/documento, subconsultas para preguntas compuestas, remisiones de un salto e inventarios. `evaluar_mejorado.py` vuelve a ejecutar la selección desde los rankings y comprueba que ni los textos ni los inventarios se hayan alterado. Hay **22 pruebas de recuperación aprobadas**, incluidas consultas ajenas a las 50 originales y reconstrucción de rankings desde vectores.

Estos porcentajes miden **cobertura de evidencia recuperada**, no corrección de respuestas. La primera corrida de Qwen se documenta por separado en [resultados de Deliverable 2](../resultados/README.md). Las reglas de recuperación se desarrollaron después de observar fallos de estas 50 preguntas, que por tanto son un conjunto de desarrollo.

Para reproducir la segunda corrida con el modelo local y la primera corrida intacta:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python3 Deliverable2/recuperacion/recuperar_mejorado.py --salida Deliverable2/recuperacion/resultados/e5_estructurado_repeticion
python3 Deliverable2/recuperacion/evaluar_mejorado.py --corrida Deliverable2/recuperacion/resultados/e5_estructurado_repeticion
python3 -m unittest discover -s Deliverable2/recuperacion -v
```

La carpeta `e5_estructurado_v2_previo_correccion` conserva una ejecución intermedia y la copia exacta de su extractor, anterior a corregir la separación de preguntas con «cuánto». La corrida vigente es `e5_estructurado_v2`.

## Primera corrida conservada

Se ejecutó una primera búsqueda sobre las 50 preguntas originales. Con E5 y los cinco fragmentos más cercanos, **40 de 45 preguntas** recuperan todas las fuentes requeridas por la pauta de cobertura. Cinco tienen cobertura incompleta; las otras cinco preguntas del conjunto requieren verificar ausencia en el documento completo y siguen pendientes.

Esto equivale a **88,89% de cobertura completa entre las preguntas evaluables localmente**. No es precisión de respuestas, no se divide por 50 y no debe compararse directamente con el 4% histórico de E1. La generación y sus porcentajes se presentan por separado en [resultados](../resultados/README.md).

Consultar el [reporte por pregunta](resultados/e5_top5_v1/REPORTE.md), los [contextos y rankings completos](resultados/e5_top5_v1/recuperacion.json) y la [pauta de evidencia](pauta_evidencia.json).

## Qué se probó

- `intfloat/multilingual-e5-small`, revisión `614241f622f53c4eeff9890bdc4f31cfecc418b3`, ejecutado en CPU con archivos ya descargados, sin API.
- Los 201 fragmentos del corpus validado, prefijados con `passage: `. Las consultas son las preguntas originales, prefijadas con `query: `. Se verifica la longitud con el tokenizador real antes de codificar, sin truncamiento silencioso.
- Vectores normalizados de 384 dimensiones y similitud coseno exacta. Para este corpus pequeño no hace falta un servidor vectorial ni un índice aproximado.
- **k=5 fragmentos**, fijado antes de inspeccionar resultados; expansión a la unidad completa y deduplicación. Todavía no se siguen remisiones a otros artículos ni se reescriben preguntas.
- Se guardan los vectores, el orden exacto de IDs, hashes de corpus/modelo/artefactos, versiones, todos los rankings y el texto íntegro de los contextos.

Los contextos tienen en promedio 2.881 caracteres, con un máximo de 7.716. Esto aún no es una medición de tokens de Qwen; se realizará antes de generar respuestas.

## Separación entre búsqueda y evaluación

`probar_recuperacion.py` lee únicamente los documentos preparados y los campos pregunta/categoría del test. Aunque el CSV histórico también contiene respuestas, el lector las excluye. No lee las respuestas de referencia ni la pauta de evidencia.

`evaluar_recuperacion.py` recibe una corrida ya finalizada y comprueba si sus unidades cubren los componentes de evidencia definidos en `pauta_evidencia.json`. No añade fuentes al contexto ni cambia el ranking para que coincida con la pauta. Por ejemplo, en la pregunta 36 se necesitan dos componentes: el evento de inscripción y el artículo del mínimo de créditos. Encontrar solo uno no cuenta como cobertura completa.

La pauta procede de las referencias ya revisadas, con fuentes alternativas explícitas cuando basta cualquiera de ellas. Se fijó antes de inspeccionar estos rankings. No es un catálogo exhaustivo de equivalencias semánticas: «cobertura incompleta» significa que falta alguna fuente de esta pauta, no que toda posible respuesta basada en otro pasaje sea necesariamente incorrecta. En particular, la pregunta 34 ya recupera el artículo general del derecho y plazo; falta el artículo interno incluido para contextualizar la solicitud.

Las preguntas 41–44 y 49 requieren evidencia de ausencia global. Encontrar artículos parecidos o un feriado de otra fecha no demuestra que el artículo/evento pedido no exista. Por eso no se incluyen en el denominador local y quedan pendientes.

## Qué falta mejorar

| Pregunta | Diagnóstico observado | Mejora que corresponde probar |
|---|---|---|
| 25 | Encuentra el art. 9 de Ingeniería, pero el art. 7 al que remite queda en posición 8. | Seguir remisiones explícitas con límites y trazabilidad. |
| 34 | Encuentra el art. 31 general; el art. 25 interno queda en posición 8. | Revisar suficiencia de la evidencia y recuperación complementaria entre reglamentos. |
| 36 | Recupera fechas; el mínimo de créditos queda en posición 27. | Descomponer preguntas con varias partes y unir sus resultados. |
| 38 | Recupera la escala general, pero muchas filas del anexo ocupan el resto; falta el art. 2 de Ingeniería, en posición 94. | Separar aplicación de la norma y escala; revisar diversidad de resultados para evitar redundancia del anexo. |
| 50 | El art. 19 citado expresamente queda en posición 8. | Resolver citas de artículo con búsqueda exacta por documento y número. |
| 41–44, 49 | La similitud semántica devuelve texto cercano sin demostrar ausencia. | Consultar el inventario estructural completo y citar el alcance de la búsqueda. |

Estas mejoras deben ser reglas generales, **sin listas de respuestas o rutas por número de pregunta** en el recuperador. El diagnóstico por k=1,3,5,10 está en el reporte; aumentar k a 10 solo alcanza 43/45 y no resuelve por sí solo las preguntas compuestas ni la ausencia global.

Al ajustar el recuperador con estas 50 preguntas, ese conjunto pasa a servir también para desarrollo. Debe declararse este uso; antes de afirmar capacidad de generalización, conviene añadir preguntas de validación nuevas que no se usen para ajustar las reglas.

## Reproducción

Desde la raíz del repositorio, con Python 3.10 o superior:

```bash
python3 -m pip install -r Deliverable2/recuperacion/requirements.txt
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python3 Deliverable2/recuperacion/probar_recuperacion.py --salida Deliverable2/recuperacion/resultados/e5_top5_repeticion
python3 Deliverable2/recuperacion/evaluar_recuperacion.py --corrida Deliverable2/recuperacion/resultados/e5_top5_repeticion
python3 -m unittest discover -s Deliverable2/recuperacion -v
```

La corrida almacenada está en `resultados/e5_top5_v1`; el script exige una salida nueva para no sobrescribir experimentos. Las pruebas verifican la corrida almacenada, incluyendo reconstrucción exacta de rankings y contextos desde sus vectores, sin ejecutar de nuevo E5.

En otra máquina, descargar primero el modelo completo y fijar su revisión (requiere red, sin clave de API para este modelo público):

```python
from huggingface_hub import snapshot_download
snapshot_download("intfloat/multilingual-e5-small", revision="614241f622f53c4eeff9890bdc4f31cfecc418b3")
```

También puede especificarse `--modelo-local /ruta/a/la/instantanea`. Los pesos no se incluyen en el repositorio. Las similitudes pueden variar mínimamente entre plataformas/versiones; se conservan todos los datos para auditar la corrida efectivamente realizada.

Los contextos de esta corrida se congelaron para la primera comparación de prompts. El [sistema consultable](../notebooks/README.md) usa la misma política para preguntas nuevas.

Fuente técnica: [ficha oficial de E5, prefijos, normalización y ejemplo de recuperación](https://huggingface.co/intfloat/multilingual-e5-small/raw/main/README.md).
