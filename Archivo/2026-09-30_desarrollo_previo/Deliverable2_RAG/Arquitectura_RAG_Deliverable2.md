# Arquitectura reproducible de Deliverable 2

El punto de entrada es `rag_normativa_ingenieria_4b.ipynb`, respaldado por `pipeline_colab.py`.

```text
Corpus versionado -> passage: E5-small -> embeddings
Pregunta -> query: E5-small -> similitud coseno -> top-5
Pregunta + fragmentos -> prompt DATO/CITA -> Qwen3-4B -> respuesta
Pregunta sin fragmentos -> prompt E1 -> el mismo Qwen3-4B -> baseline
Ambas ramas -> predicciones.csv + trazas.jsonl + metadata.json
Revisión explícita de ambas ramas -> auditoria.py -> métricas
```

El modelo generador nunca recibe los gold. La demo ejecuta ambas ramas; no reproduce una respuesta fija. Las trazas incluyen el contenido exacto del contexto y sus similitudes.

Se mantienen dos corpus:

- Histórico: 198 fragmentos, asociado exclusivamente a las respuestas históricas.
- v2: 169 fragmentos, extractor de encabezados consecutivos, artículos transitorios diferenciados y ventanas con solapamiento. Requiere medición nueva.

Se mantiene k=5 para la reproducción histórica. No se dispone de ablation controlada de k ni de medición de Recall@k. El prompt estructurado no es una restricción formal de la decodificación. La inferencia no garantiza que una respuesta esté completa ni que la abstención indique ausencia en el corpus completo: solo se recupera una parte del corpus.
