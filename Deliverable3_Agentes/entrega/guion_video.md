# Guion de demostración — máximo 3 minutos

**Estado:** ensayo actualizado con datos reales del piloto v4 congelado. No constituye el video exigido. El guion final debe incorporar la versión congelada y la comparación de las seis condiciones; no grabar una conclusión experimental antes de evaluarlas. Duración objetivo: 2:50, con 10 segundos de margen.

## Preparación de pantalla

Abrir el notebook de la versión que se demostrará, el grafo del informe y las trazas originales. Mantener visibles el identificador de corrida y la versión. Cargar los modelos antes de grabar; la carga no es la demostración. Mostrar la pregunta, decisiones intermedias y respuesta final a un tamaño legible. Si se reproduce una traza ya obtenida, rotular **«Revisión de una ejecución real conservada»**. Si se muestra generación nueva, conservar también ese intento y su ZIP. No presentar checkpoints como inferencia nueva ni acelerar el video sin indicarlo.

El material `mensajes_reales_v4.md` enlaza P05 (acierto) y P41 (fallo) del piloto v4 y conserva los mensajes sin reescribirlos. El resultado favorable sirve para explicar el flujo; la comparación se calcula sobre el conjunto completo, incluyendo los fallos.

## Narración y pantalla

| Tiempo | Pantalla | Narración de ensayo |
|---|---|---|
| 0:00–0:20 | Título, corpus y pregunta | «Continuamos la tarea de D1 y D2: responder preguntas sobre normativa de pregrado de la UdeC usando un corpus cerrado. D2 ya recuperaba documentos, pero aún podía omitir condiciones o citar evidencia que no respaldaba la respuesta. Aquí probamos tres agentes con el mismo Qwen3-4B.» |
| 0:20–0:45 | Grafo completo | «El investigador reúne evidencia y decide si necesita buscar, leer un artículo o consultar el inventario. El redactor escribe o pide información. El auditor puede aceptar, devolver una corrección o pedir otra investigación. Las flechas de retorno y los límites permiten observar cuándo el sistema revisa y cuándo se detiene.» |
| 0:45–1:35 | Pregunta P05; decisiones y mensajes reales | «Esta es una ejecución real conservada. Preguntamos cuál es la actividad final de titulación en Ingeniería. Podemos abrir los mensajes del investigador, el borrador del redactor y la devolución del auditor. En este intento el investigador entrega evidencia, el redactor envía su borrador y el auditor lo acepta sin devolución. La respuesta final identifica la Memoria de Título y cita el artículo 29. La aceptación del auditor es una decisión del sistema; el acierto se determina después con la pauta de D2.» |
| 1:35–2:00 | P41: inventario, borrador y stop | «También conservamos los fallos. Los borradores reconocen que el artículo 90 no existe en esta copia, pero el auditor sigue pidiendo correcciones. El controlador interrumpe el ciclo, solicita investigar y la herramienta devuelve el inventario. Aun así se agotan las doce llamadas. La abstención técnica final no respondió correctamente la pregunta. Este caso es una regresión frente a D2.» |
| 2:00–2:30 | Tabla de resultados y ablaciones | **Texto verificable de ensayo:** «En el piloto de la versión congelada, sobre cuatro casos de diagnóstico, baseline obtuvo cero aciertos, D2 dos y los agentes uno. No es una mejora sobre D2 ni una estimación de generalización. Los agentes usaron veintiuna llamadas y unos doce minutos de generación en total. El lote compara las 50 preguntas y retira por separado descomposición, completitud y verificación; todavía falta completarlo y evaluarlo.» **Para el video final:** sustituir exclusivamente por los conteos, diferencias y costes verificados del lote completo. |
| 2:30–2:50 | Repositorio, fuentes y límites | «El repositorio contiene código ejecutable, prompts externos, fuentes congeladas, trazas y evaluaciones vinculadas por hashes. Todos los intentos se conservan. Las 50 preguntas son de desarrollo; la evaluación externa de las respuestas no convierte este conjunto en una prueba independiente.» |

## Correspondencia con las trazas v4

- P05: eventos 4 y 7, transferencias; evento 9, aceptación; evento 10, respuesta final. No narrar un loop en este caso: eso ocurrió en una versión anterior.
- P41: eventos 7 y 10, borrador y devolución; 13, bloqueo de repetición; 16–17, lectura e inventario; 32, interrupción del ciclo; 36, formato inválido; 40, salida final por límite de llamadas. Para el segmento de 25 segundos, seleccionar 7, 17, 32 y 40; el resto queda enlazado para inspección.
- La pantalla de resultados del video final requiere las seis condiciones completas. Los conteos 0/4, 2/4 y 1/4 son exclusivamente del piloto v4 y nunca deben rotularse como resultados del lote.

## Cierre del video final

- Duración real del archivo ≤ 180 segundos, imagen legible, mensajes intermedios y salida visibles.
- Comparación de las seis condiciones basada en resultados completos; mencionar regresiones y coste, aunque el sistema no supere D2.
- Versión del notebook y trazas del video incluidas en GitHub. Si la demostración usa otra corrida, añadirla sin reemplazar los pilotos.
- Publicar el video real en un enlace abierto autorizado y comprobarlo sin sesión. Incorporar ese enlace en README y PDF. No sustituirlo por este guion, una animación o un enlace a un archivo inexistente.
