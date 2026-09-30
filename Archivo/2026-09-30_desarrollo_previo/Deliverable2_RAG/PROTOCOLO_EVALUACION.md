# Criterio de corrección y procedencia

Se conserva la tarea de E1: responder con el dato completo y su fuente, o abstenerse ante premisas falsas. Las 50 preguntas son elaboradas por el equipo; no son un benchmark oficial ni un test independiente de desarrollo.

## Revisión de resultados históricos

`revision_historica.csv` contiene 100 decisiones, una por pregunta y sistema. Es una revisión semántica asistida por IA que el equipo debe validar antes de presentarla como resultado definitivo. `auditoria.py` únicamente verifica identidad y cuenta decisiones; **no es un juez automático de calidad semántica**. Los CSV de respuestas originales no se modifican.

Reglas aplicadas por igual a ambos sistemas:

1. Deben estar todos los datos pedidos, incluidas condiciones y excepciones presentes en la referencia. Se aceptan paráfrasis, números en palabras y unidades inequívocas por la pregunta.
2. Se exige que las fuentes citadas respalden **todos los datos pedidos**. Se acepta el artículo completo aunque no se nombre el inciso. Una referencia complementaria en el gold no es obligatoria si otra fuente citada respalda por sí sola toda la respuesta. Así, el calendario basta para las fechas de P32, P33 y P39; el Art. 31 RG basta para el derecho y plazo de P34. En cambio, P36 y P38 necesitan dos fuentes para sus dos datos, y P40 necesita el Art. 30 para respaldar el 40%. Aplicar la misma regla a ambos sistemas.
3. Para fechas, el año puede constar en la fuente citada. Una fuente adicional válida no invalida la respuesta.
4. Una abstención debe rechazar la premisa sin inventar datos o autoridades. No basta con encontrar la palabra «no» o «ninguna». Se acepta la abstención genérica del protocolo original en las preguntas 41–50.
5. Los números de artículo no cuentan como datos. Acertar un término, uno de varios números o una de varias citas no basta.

Cada decisión incluye una huella de pregunta, referencia y respuesta. Al cambiar cualquiera de ellas, el recuento falla y exige una revisión nueva. No se reutilizan veredictos para una corrida nueva.

## Correcciones a la evidencia publicada

- E1 publicó 2/50 (4%). P49 rechaza correctamente el supuesto feriado, pero añade un día de semana incorrecto y un «Art. 13 del Reglamento de Feriados Nacionales» ajeno al corpus. Aplicando la regla de no inventar, queda 1/50 (2%). Se conserva y declara la cifra original de E1.
- RAG histórico: 44/50 (88%) bajo estas reglas. Fallos: 3, 24, 25, 36, 38 y 40. El 98% anterior aceptaba datos o citas parciales y no debe describirse como exactitud estricta.
- La primera revisión asistida por IA dio 40/50 porque exigió literalmente todas las fuentes del gold. Una lectura directa de los PDF mostró que P32, P33, P34 y P39 sí citan una fuente suficiente para lo preguntado. Se corrigieron sus veredictos; las preguntas y salidas originales siguen intactas. Si el curso exige citar **todas** las referencias escritas en el gold aun cuando sean redundantes, el resultado bajo esa convención sería 40/50. El equipo debe fijar una convención antes de presentar la cifra final.
- Mejora con criterio homogéneo de suficiencia: 2% → 88%, **86 puntos porcentuales**. Frente al 4% publicado: +84 puntos, con la salvedad del cambio de revisión del baseline.
- Latencia media histórica: 5,386 s por pregunta, medida alrededor de recuperación y generación; no incluye descarga, carga del modelo ni construcción inicial del índice.

## Límites de la evidencia

No hay trazas históricas del top-5 para cada pregunta. Por tanto, la abstención de P3 es real, pero no demuestra que el Art. 12 haya quedado fuera del contexto. La nueva ejecución guarda el contexto para distinguir fallos de recuperación y de generación.

P25 tiene una causa comprobable en la base histórica: el extractor cortó el Art. 9 ante una referencia al Art. 7 situada al inicio de una línea. El fragmento termina en «prioridades a) y b) del». La respuesta conserva ese corte. No se puede atribuir todo el error al generador.

El prompt solicita `DATO` y `CITA`; no impone una gramática al decodificador. Se denomina **prompt estructurado**, no decodificación restringida. No se cuenta con experimentos controlados que prueben optimalidad de k=5, Recall@5=98%, mínimo viable de 4B o eliminación total de alucinaciones.

## Corrida final

El notebook guarda ambos sistemas sobre las mismas 50 preguntas, trazas y metadatos en un directorio nuevo. La plantilla de revisión empieza vacía. Dos integrantes pueden revisar independientemente y resolver discrepancias; registrar sus nombres y la fecha solo después de que lo hagan. Para inferir generalización, añadir un conjunto reservado sin usarlo para ajustar el sistema.
