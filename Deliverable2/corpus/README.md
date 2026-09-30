# Preparación del corpus para RAG

Estado: extracción y segmentación implementadas y comprobadas contra los PDF locales. Las [pruebas de recuperación](../recuperacion/README.md) alcanzan 40/45 con E5 simple y 43/45 con búsqueda exacta, subconsultas y remisiones; quedan limitaciones documentadas. La segunda corrida también incluye inventarios para verificar ausencia. Todavía no se han ejecutado las nuevas pruebas de Qwen.

La [revisión de los fallos anteriores](REVISION_FRAGMENTACION.md) explica qué estaba mal y qué cambió. Para inspeccionar el resultado sin leer JSON, abrir [el corpus legible](generado/corpus.md).

## Diseño

1. Extraer los reglamentos respetando los encabezados reales de artículo y sus continuaciones de página. Una mención de «Artículo 7°» dentro de otro artículo no crea una nueva unidad.
2. Extraer el calendario por celdas: evento, fecha completa, semestre y año permanecen juntos. Conservar el anexo como filas, incluyendo la geometría de las celdas combinadas.
3. Guardar los artículos completos. El artículo 3 del Reglamento General es un glosario de siete páginas: sus 24 definiciones numeradas y su introducción constituyen unidades independientes de recuperación, sin eliminar el artículo completo del archivo fuente.
4. Crear fragmentos de búsqueda con un presupuesto de **480 tokens reales de E5**, incluidos prefijo `passage:`, identificación, cita y tokens especiales. El máximo del modelo es 512. No hay truncamiento habilitado.
5. Cuando la búsqueda encuentre un fragmento, usar `expand_hits()` para recuperar su unidad íntegra, eliminando duplicados. Un fragmento de búsqueda es una pista para localizar evidencia; **no debe pasarse aislado a Qwen**.

No se aplica solapamiento fijo: los intervalos de texto cubren cada unidad sin huecos y la expansión recupera su totalidad. Esto evita duplicar texto innecesariamente. No se afirma que esta elección maximice la recuperación: se comprobará en la siguiente etapa y podrá ajustarse si falla una consulta situada cerca de un límite.

La extracción depende de la estructura de estos tres PDF; no es un extractor universal. Un cambio de edición, tipografía o tablas necesita revisión y regeneración.

## Archivos

| Archivo | Contenido |
|---|---|
| `preparar_corpus.py` | Extractor, segmentación, validaciones y expansión de resultados |
| `generado/corpus.json` | 173 unidades fuente y 197 unidades recuperables, con texto completo y procedencia |
| `generado/fragmentos_busqueda.json` | 201 fragmentos; campo `texto_embedding` listo para E5 |
| `generado/trazabilidad.json` | Las 1.208 líneas detectadas, página, coordenadas y destino; también registra encabezados y metadatos excluidos del texto de artículos |
| `generado/validacion.json` | Conteos, versiones, hashes de fuentes/artefactos y presupuesto de tokens |
| `generado/corpus.md` | Versión legible para inspección |
| `test_corpus.py` | Regresiones de extracción, pérdida de texto y expansión de contexto |

Los 173 registros fuente contienen 95 artículos ordinarios, 2 transitorios, 1 preámbulo, 25 eventos y 50 filas del anexo. Hay 24 unidades recuperables adicionales por la separación del glosario. Solo cuatro unidades requieren dos fragmentos de búsqueda: las definiciones 3.9 y 3.10 y los artículos 8 y 10 del Reglamento General. El resto cabe en uno.

Las páginas citadas son las páginas físicas del PDF, contadas desde 1. Los apartados del glosario heredan el intervalo de páginas del artículo 3; no se ha calculado una cita de página más estrecha para cada definición.

## Reproducción

Desde la raíz del repositorio, con Python 3.10 o superior:

```bash
python3 -m pip install -r Deliverable2/corpus/requirements.txt
python3 Deliverable2/corpus/preparar_corpus.py
python3 -m unittest discover -s Deliverable2/corpus -v
```

En el equipo actual el tokenizador ya está en la caché de Hugging Face. En otro equipo basta descargar **el tokenizador**, sin pesos del modelo ni GPU:

```bash
curl --fail --location 'https://huggingface.co/intfloat/multilingual-e5-small/resolve/614241f622f53c4eeff9890bdc4f31cfecc418b3/tokenizer.json' --output /tmp/e5-tokenizer.json
python3 Deliverable2/corpus/preparar_corpus.py --tokenizer /tmp/e5-tokenizer.json
E5_TOKENIZER=/tmp/e5-tokenizer.json python3 -m unittest discover -s Deliverable2/corpus -v
```

La revisión y el SHA-256 del tokenizador están fijados en el extractor; usar otro falla explícitamente. La generación es determinista para los mismos PDF, versiones y parámetros. Todos los documentos se validan antes de escribir resultados; si falta uno, no se publica un corpus parcial. No se leen preguntas, respuestas de referencia ni resultados de E1 para construir el corpus.

## Integración siguiente

- Indexar `texto_embedding` con `intfloat/multilingual-e5-small`, revisión fijada. Ese campo ya incluye `passage:`: **no añadirlo otra vez**. Las consultas usarán `query:`. Guardar junto al índice la lista ordenada de IDs, revisión, parámetros y hash del JSON; invalidarlo si cambia el corpus. No reutilizar los `.npy` archivados.
- Probar la recuperación antes de generar respuestas: comprobar si devuelve la evidencia necesaria, registrar fallos y distinguirlos de errores del modelo.
- Resolver las remisiones necesarias. Por ejemplo, el artículo 9 de Ingeniería conserva completas sus referencias a los artículos 7 y 8, pero una pregunta sobre las prioridades requerirá además el texto del artículo 7. `expand_hits()` expande la unidad hallada; todavía no sigue esas referencias.
- Comprobar el presupuesto con el **tokenizador de Qwen**, reservando espacio para pregunta, prompt y respuesta. Los tokens de E5 sirven para el índice, no para medir el contexto del generador. Si no cabe una unidad completa, registrarlo y ajustar la selección; evitar recortar silenciosamente el texto.
- Guardar una selección de evidencia por pregunta y reutilizarla exactamente en **RAG simple** y **RAG con prompt estructurado**. Un ejemplo one-shot, si se incorpora, debe quedar fuera de las 50 preguntas evaluadas.

La conservación de caracteres entre texto extraído y fragmentos se verifica al 100%. Eso no demuestra por sí solo fidelidad semántica completa al PDF, buena recuperación ni respuestas correctas. Se complementó con revisión visual de casos problemáticos y 13 pruebas de regresión.

Documentación del modelo: [E5: prefijos y límite de 512 tokens](https://huggingface.co/intfloat/multilingual-e5-small/raw/main/README.md).
