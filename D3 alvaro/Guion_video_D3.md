# Guion de grabación · Entregable 3

**Duración objetivo: 2:45–2:55. Límite: 3:00.**

Notebook: `Deliverable3/Demo_D3.ipynb`. Ejecutar en Colab con T4.

## Antes de grabar

1. Abrir el notebook y ejecutar **A1–A5**. La instalación, descarga de pesos y preparación de E5 quedan fuera del video.
2. Confirmar «LISTO PARA GRABAR». Mantener el modelo cargado y la sesión conectada.
3. Cerrar el panel de archivos y ajustar el zoom para leer pregunta, mensajes y respuesta. Grabar pantalla y micrófono; no es necesaria una cámara.
4. Abrir B0. Ejecutar las celdas de la sección B una por una, no «Ejecutar todo».
5. Si se hace un ensayo, conservarlo. Cada intento se registra en otra carpeta. No volver a ejecutar A5, que reinicia la lista de intentos disponibles para exportar.

Los casos P01 y P41 tardaron **69,2 y 32,8 segundos** en la evaluación histórica. Son una referencia para planificar, no una promesa de duración. No se han reducido los tokens ni los ciclos de v6 para acelerar la demo.

## Secuencia y texto para narrar

Los tiempos son orientativos. Mientras el modelo calcula, explicar el recorrido y mostrar los mensajes que vayan apareciendo. No leer todo el JSON.

| Tiempo objetivo | Pantalla y acción | Narración sugerida |
|---|---|---|
| **0:00–0:15** | Ejecutar **B0**. Mostrar los cuatro roles. | «Nuestro sistema responde consultas sobre la normativa de pregrado de Ingeniería UdeC. Partimos del RAG de D2 y añadimos planificación y revisión. Todos los roles usan Qwen3 de cuatro mil millones de parámetros.» |
| **0:15–1:25** | Ejecutar **B1**. Mostrar la pregunta y seguir los mensajes. Abrir la fila del Enrutador o Recuperador cuando aparezca. | «Primero preguntamos la nota mínima para aprobar. El Enrutador clasifica y prepara el plan. El Recuperador decide qué buscar y observa los resultados. El Redactor construye una respuesta con fuentes. Finalmente, el Verificador decide terminar o pedir una corrección. Aquí vemos decisiones y mensajes de una ejecución real.» |
| **Al finalizar B1** | Mostrar **Respuesta final** y **Veredicto interno**. Leer el dato y la cita que efectivamente aparezcan. | «La respuesta obtenida es [leer el dato visible], con estas referencias. Este veredicto es una revisión interna: no sustituye la evaluación externa de exactitud.» |
| **1:25–2:05** | Ejecutar **B2**. Mostrar la pregunta sobre el artículo 90 y el resultado de existencia. | «Ahora preguntamos por un artículo inexistente. Esta consulta comprueba si el sistema contrasta la premisa antes de responder. Observamos la decisión del Enrutador y la comprobación de existencia. La salida que aparece es [describir brevemente la salida real].» |
| **2:05–2:30** | Ejecutar **B3**. Señalar el aviso de traza histórica, primer borrador y último borrador. | «Este es un fallo histórico, no una ejecución nueva. En H03 faltaron fechas en la evidencia seleccionada. El primer borrador inventó dos plazos y las correcciones no resolvieron la falta de información. El sistema terminó sin aprobación tras diecinueve llamadas. Detectar un problema no garantiza corregirlo.» |
| **2:30–2:50** | Ejecutar **B4**. Señalar las filas D2, completo y ablaciones. | «En la evaluación histórica, v6 pasa de cuarenta a cuarenta y seis aciertos sobre cincuenta; en las difíciles, de dieciséis a veinte sobre veinticinco. Las ablaciones comparan qué ocurre al retirar técnicas o componentes. Son resultados provisionales: nueve casos requieren revisión. Código, prompts y evidencia se conservan en el repositorio.» |

### Si la salida real no coincide con la esperada

No decir que acertó solo porque el Verificador aprobó. Usar una frase fiel a lo mostrado:

- **Respuesta respaldada:** «La respuesta incluye el dato y las referencias que podemos comprobar.»
- **Se abstiene:** «El sistema declara que no tiene respaldo suficiente; podemos revisar si la abstención está justificada.»
- **Falla o entra en corrección:** «En esta ejecución aparece una limitación: [describirla]. El Verificador [decisión visible]. La traza permite revisar cómo ocurrió.»
- **El Enrutador no toma la rama esperada en P41:** describir las búsquedas que aparecen; no afirmar que ejecutó una comprobación directa que no se observa.

No hace falta forzar un bucle de corrección en las consultas en vivo: H03 permite mostrar uno real, identificado como histórico.

## Mantener el video bajo tres minutos

- Grabar con los modelos ya cargados. No grabar instalaciones, descargas ni indexación.
- Si la ejecución dura más que el presupuesto, editar **solo las esperas** y añadir «Espera de inferencia recortada». Mantener visibles pregunta, acciones, mensajes, respuesta y tiempo real registrado.
- No acelerar la lectura de los resultados ni sustituir una ejecución por una animación o salidas preparadas.
- Revisar el archivo exportado: máximo 3:00, audio entendible y letra legible.

## Después de grabar: evidencia y publicación

1. Ejecutar **C1**. Revisar los `run_id` seleccionados y confirmar que coincidan con las ejecuciones visibles en el video. Si grabaste un intento anterior, ajustar `RUN_IDS_EN_VIDEO` antes de exportar.
2. Descargar `evidencia_video_…zip`. Incluye los intentos, prompts completos, salidas crudas, resultados de herramientas, entorno, fuentes y el fallo H03 histórico separado.
3. Guardar ese ZIP en `D3 alvaro/evidencia_video/`. Los archivos locales de Colab se pierden al cerrar o reiniciar el entorno.
4. Publicar la grabación con acceso abierto y comprobar el enlace desde una ventana sin sesión iniciada.
5. Incorporar el enlace público en el encabezado de `Deliverable3/documento/main.tex`, donde ahora dice «Pendiente de enlace público». Recompilar y verificar que siga siendo una página.
6. Actualizar el README y el manifiesto de auditoría al incorporar la evidencia. No marcar el video como completo antes de tener grabación y enlace comprobado.

## Qué demuestra cada pantalla

- **B1 y B2:** comportamiento real, mensajes y respuesta de nuevas consultas.
- **B3:** limitación observada en una ejecución histórica; no se presenta como inferencia nueva.
- **B4:** resultados del conjunto evaluado, separados de los ejemplos del video.
- **C1:** trazabilidad de lo grabado; el notebook no publica archivos ni completa el enlace por sí solo.

## Referencias de configuración

Se conserva la configuración sin thinking nativo de [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) y la carga NF4 mediante [bitsandbytes en Transformers](https://huggingface.co/docs/transformers/quantization/bitsandbytes). La configuración completa y las revisiones de los pesos se guardan con la ejecución.
