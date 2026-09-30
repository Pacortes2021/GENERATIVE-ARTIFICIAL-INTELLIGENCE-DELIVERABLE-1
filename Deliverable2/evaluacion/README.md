# Evaluar con respuestas de referencia

El flujo acordado es sencillo: **pregunta + respuesta de referencia + respuesta del modelo → IA juez → correcta sí/no y motivo**. Empezamos aquí en el chat, sin API. Python prepara los archivos, valida las decisiones y calcula los resultados; la comparación de significado la realiza la IA.

## La pauta

[Las 50 respuestas de referencia](respuestas_referencia.md) están redactadas con datos y citas comprobados contra los tres PDF del corpus. [referencias.json](referencias.json) contiene las mismas respuestas, los fragmentos de respaldo y las páginas para que el evaluador pueda trabajar sin volver a buscar cada artículo. Las preguntas y categorías siguen siendo las de E1; sus respuestas resumidas se amplían en una pauta separada de E2.

Los [criterios del juez](criterios.md) aceptan paráfrasis y citas alternativas válidas, y evitan exigir todos los detalles complementarios. El juez consulta el PDF si aparece una duda o fuente alternativa que no pueda comprobar con los fragmentos. La pauta nunca se entrega a Qwen como parte de su prueba: se reserva para evaluar. En RAG se usan únicamente los documentos originales.

El 4% histórico permanece sin cambios. La [primera corrida RAG evaluada](../resultados/qwen3_4b_4adccec813c53d7f/REPORTE.md) contiene 150 decisiones asistidas y sus motivos. El baseline emparejado con esa solución sigue pendiente; cuando se ejecute, se aplicará esta misma pauta a baseline y RAG por separado. La [muestra didáctica anterior](calibracion.md) sigue disponible como material opcional; no es un paso obligatorio ni un resultado experimental.

## Preparar una corrida

El CSV de entrada necesita `pregunta` y `respuesta_modelo`. Las preguntas deben coincidir exactamente con E1. Las etiquetas antiguas y referencias que pueda contener ese CSV se ignoran: se usa la pauta de E2. Se permiten subconjuntos, cuyo tamaño se informa explícitamente. Las preguntas duplicadas o desconocidas se rechazan.

Desde la raíz `Proyecto_Git`:

```bash
python3 Deliverable2/evaluacion/evaluar.py preparar \
  --respuestas /ruta/a/respuestas_nuevas.csv \
  --salida Deliverable2/resultados/prueba_001
```

El directorio debe ser nuevo. Se crean:

- `paquete.json`: preguntas, respuestas de referencia con evidencia, respuestas del modelo, criterios y hashes de la pauta y del corpus.
- `veredictos.json`: plantilla; cada caso tiene `correcta: null` y `motivo` vacío.

Después puedes decir aquí: **“Compara las respuestas del paquete prueba_001 con la pauta y guarda los veredictos.”** La IA completa `correcta` con `true` o `false` y explica cada decisión. Si una duda impide decidir, conserva `null` y explica la limitación. No se necesita una clave API para trabajar así en este chat.

## Obtener el reporte

```bash
python3 Deliverable2/evaluacion/evaluar.py resumir \
  --paquete Deliverable2/resultados/prueba_001/paquete.json \
  --veredictos Deliverable2/resultados/prueba_001/veredictos.json \
  --salida Deliverable2/resultados/prueba_001/reporte
```

`evaluacion.csv` muestra pregunta, referencia, respuesta generada, sí/no y motivo. `resumen.json` informa aciertos globales y por categoría. Si hay pendientes no se publica una exactitud final: se mantiene el total de casos y se informa cuántos faltan. Los resultados no se sobrescriben; guardar revisiones con nombres nuevos.

Los hashes permiten detectar cambios en respuestas, pauta y criterios. No prueban que una decisión semántica sea correcta. Conviene revisar una muestra de decisiones y los casos dudosos antes de presentar resultados. Los archivos de `Deliverable2/resultados/` se pueden versionar en Git para reproducir la evaluación; ninguna evidencia se envía a servicios externos desde este programa.

## Comprobaciones

```bash
python3 -m unittest discover -s Deliverable2/evaluacion -p 'test_*.py' -v
```

Se usa únicamente Python estándar. Las pruebas validan la preparación, la integridad de los archivos y el cálculo; no certifican la precisión de la IA juez. Los paquetes v1 del diseño anterior deben prepararse de nuevo: v2 utiliza la pauta ampliada y decisiones binarias.
