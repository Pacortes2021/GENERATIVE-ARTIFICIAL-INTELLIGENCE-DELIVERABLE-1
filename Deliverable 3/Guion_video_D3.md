# Guion del video · Entregable 3

Duración objetivo: **2:55**, con cinco segundos de margen. La narración está pensada para una locución rápida, con pausas breves al señalar el grafo, las citas y la tabla. Las indicaciones de pantalla y las ramas finales no se narran completas.

[Abrir el notebook actualizado en Colab](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%203/Deliverable3/Demo_D3.ipynb).

El video sigue **B0 → B1 → B2 → B3**. La preparación A1–A5 y la exportación C1–C2 quedan fuera de la grabación. El notebook contiene la presentación; este documento concentra las instrucciones.

## Preparación fuera de la grabación — A1–A5

1. Abrir **una copia nueva y actualizada del notebook**. No continuar con una copia antigua que conserve celdas, variables o salidas de una versión previa.
2. En Colab, seleccionar GPU T4 y ejecutar **A1–A5 en orden**. Este bloque prepara dependencias, fuentes y modelo; no forma parte del video. Comprobar que las fuentes corresponden a la versión fijada en el notebook y conservar el registro de esa versión para la evidencia.
3. La descarga desde el repositorio es la ruta normal. **Solo si falla**, extraer `Deliverable3_ejecucion.zip` de `Materiales_video_D3.zip`, establecer `DESCARGAR_DEL_REPO = False` y subir ese ZIP cuando la celda lo solicite. No usar el ZIP original de Álvaro: no contiene las mismas mejoras de demostración. Esta contingencia se explica aquí, no en las celdas de la presentación.
4. **Reiniciar la sesión solo si Colab lo solicita** tras instalar dependencias. Si ocurre, ejecutar otra vez los pasos de preparación necesarios en orden; no iniciar B1 con variables o modelo sin cargar.
5. Confirmar que el modelo esté cargado antes de grabar. Hacer un ensayo con B1 para comprobar pantalla, audio y duración. **No repetir A5 solo para volver a ensayar** si el modelo ya está preparado; ejecutar nuevamente B1. Cada ejecución debe quedar identificada para poder seleccionar su evidencia después.
6. Preparar la navegación: **B0** arquitectura; **B1** consulta real H17; **B2** fallo histórico H03; **B3** comparación de resultados. El recorrido principal no usa P41. Evitar que las celdas de preparación o mensajes operativos ocupen la pantalla durante el video.
7. Tras grabar, usar **C1** para seleccionar y guardar la ejecución que realmente aparece en el video. Comprobar el identificador, la pregunta y la salida; no elegir un ensayo distinto solo porque dio un mejor resultado. **C2** permite inspeccionar los mensajes y datos de esa ejecución cuando sea necesario; no es un bloque obligatorio de la narración.
8. Si una ejecución excede el tiempo previsto, conservarla completa y recortar únicamente las esperas al editar. Rotular de forma visible **«Espera recortada; tiempo real: …»**. No presentar una traza histórica como salida nueva ni sustituir la salida de B1. Mantener la duración final inferior a tres minutos.

Mostrar claramente el paso de la ejecución nueva de B1 a la traza histórica de B2. No afirmar que la nueva salida reproducirá la anterior.

## 0:00–0:25 · Grafo y roles

**Pantalla B0:** grafo completo; señalar roles y flechas de retorno.

> Nuestro sistema responde consultas sobre normativa de pregrado de Ingeniería UdeC. Conservamos el modelo Qwen3 de cuatro mil millones de parámetros y organizamos el trabajo en cuatro roles. El Enrutador planifica explícitamente, el Recuperador elige herramientas, el Redactor construye la respuesta y el Verificador decide si terminar o pedir correcciones. Hay decisiones del modelo que cambian el recorrido: no es solamente una secuencia fija de instrucciones.

## 0:25–2:10 · Consulta H17 y ejecución real

**Pantalla B1:** ejecutar H17; mantener visibles los mensajes mientras se narra. Avanzar por los puntos según aparezcan. La pregunta exacta debe verse completa:

> Explica los requisitos de asistencia que puede exigir un profesor en la Facultad de Ingeniería y en qué casos ese tope puede ser distinto.

**Narración:**

> Ejecutamos ahora una consulta que combina una regla con sus excepciones: qué asistencia puede exigir un profesor y cuándo cambia ese límite. Esta es una ejecución nueva; el resultado puede diferir del registrado durante la evaluación.
>
> El Enrutador recibe ejemplos que le ayudan a clasificar y descomponer preguntas, especialmente cuando necesita cruzar normas. Esa es la técnica few-shot. Aquí observamos qué subconsultas propone, sin imponerle manualmente la respuesta.
>
> El Recuperador puede buscar, comprobar si existe un artículo, traer su texto o declarar que tiene evidencia suficiente. Con ReAct, decide después de observar cada resultado. Si encuentra un artículo que no corresponde, puede reformular la búsqueda; si repite exactamente una acción, el controlador le advierte que no aporta evidencia nueva. Observemos las acciones efectivamente elegidas en esta ejecución.
>
> El Redactor recibe la evidencia seleccionada. Su prompt usa Chain-of-Thought: solicita razonamiento para manejar cálculos y excepciones, aunque ese bloque no aparece en la respuesta final. Debe distinguir la regla general de sus condiciones y citar las fuentes utilizadas.
>
> Finalmente, el Verificador comprueba citas y suficiencia. Puede devolver el texto al Redactor o solicitar más evidencia al Recuperador. Esta revisión iterativa, Self-refine, permite hasta dos ciclos de corrección.
>
> Para evaluar esta consulta comprobamos el máximo de ochenta por ciento en clases teóricas y prácticas, y el cien por ciento en actividades específicas. Si menciona regímenes especiales, también contrastamos ese contenido con sus fuentes. La aprobación interna, por sí sola, no demuestra que la respuesta sea correcta: hay que contrastarla con los artículos citados.

## 2:10–2:40 · Fallo H03 histórico

**Pantalla B2:** rótulo «Traza histórica H03»; mostrar primer borrador, retorno al Recuperador y salida final.

> Pasamos ahora a una traza histórica, no a otra ejecución en vivo. H03 requiere cuatro fechas para comparar los plazos de modificación de asignaturas. La evidencia seleccionada no conserva todas las necesarias. El primer borrador inventa treinta y uno y doscientos sesenta y dos días. El Verificador objeta y pide correcciones y nuevas búsquedas, pero el sistema finalmente termina absteniéndose tras diecinueve llamadas. La respuesta correcta era veinticuatro y veinticinco días. Detectar el problema no bastó para resolverlo.

## 2:40–2:55 · Comparación y cierre

**Pantalla B3:** tabla; señalar RAG D2 y Sistema completo, columnas originales y difíciles.

> Con el mismo criterio de evaluación, revisado por el equipo, pasamos de cuarenta a cuarenta y seis aciertos en cincuenta consultas originales, y de dieciséis a veinte en veinticinco difíciles. Las ablaciones muestran aportes y costos, pero una sola ejecución no prueba ventajas estables ni generalización.

## Ramas breves según la ejecución nueva

Sustituir parte del último párrafo de H17; no añadir todas estas frases al guion. Mantener el contraste con las fuentes.

- **Respuesta completa y respaldada:** «La respuesta distingue la regla y sus excepciones y cita los artículos correspondientes. Verificamos su contenido, además del estado interno.»
- **Aprueba, pero omite o añade algo incorrecto:** «El Verificador la aprobó, pero aquí observamos [omisión o añadido concreto]. Por eso evaluamos el texto y sus fuentes, no solo la aprobación.»
- **Rechaza una respuesta correcta:** «Aquí rechaza el borrador. Contrastemos el motivo con las normas: una respuesta puede ser correcta aunque la revisión interna no la apruebe.»
- **Devuelve al Redactor:** «La evidencia parece disponible, pero el Verificador solicita corregir cómo se usa en el borrador.»
- **Devuelve al Recuperador:** «El Verificador considera insuficiente la evidencia y solicita una nueva búsqueda; esta decisión cambia el recorrido del sistema.»
- **No hay retorno de revisión:** «En esta ejecución decidió terminar. Las flechas de retorno son opciones, no pasos obligatorios; veremos una de ellas en el fallo histórico.»
- **Tiempo superior al disponible:** conservar la ejecución completa y recortar solo la espera al editar, con un rótulo visible «Espera recortada; tiempo real: …». No sustituir la salida por otra histórica. Si se exige video continuo sin cortes, reducir el resto tras conocer el tiempo real; no prometer que H17 siempre cabe en 106 segundos.
- **Error de ejecución o falta de salida:** no narrar una respuesta inexistente. Resolver el error y volver a grabar la ejecución real antes de presentar la demo definitiva.

## Precisión técnica para quien graba

- «Cuatro roles» no significa cuatro decisores de ruta: el controlador envía siempre el borrador del Redactor al Verificador.
- En la corrida histórica H17 tardó 106,3 segundos y usó nueve llamadas al modelo. Son antecedentes de planificación, no predicciones de esta ejecución.
- H03 necesitaba cuatro fechas; **no faltaban necesariamente las cuatro**. La fecha de inicio del primer semestre apareció en resultados de búsqueda, pero no quedó entre las seis evidencias seleccionadas posteriormente. No decir que el corpus carece de esas fechas.
- Las diecinueve llamadas de H03 excluyen la búsqueda automática: la traza contiene veinte eventos.

## Después de grabar

1. Ejecutar C1 y conservar el ZIP descargado. Por defecto selecciona el último intento H17; si grabaste otro, reemplazar `RUN_IDS_EN_VIDEO` por su identificador antes de exportar. El paquete conserva todos los intentos de la sesión y señala el que aparece en el video.
2. Subir ese ZIP a `Deliverable 3/evidencia_video/` en el repositorio. Incluye prompts y respuestas completos de la ejecución nueva, herramientas, entorno, fuentes y el fallo histórico H03 identificado.
3. Publicar el video con acceso público y comprobar que abre sin iniciar sesión. Debe durar como máximo tres minutos y mostrar mensajes intermedios y respuesta final reales.
4. Publicación oficial: [Google Drive — Video Entregable 3](https://drive.google.com/drive/folders/1tkhRhI4_G7ArWNHW7zNoeZi8lL9RyPf2?usp=sharing), incorporado en el informe técnico y guías de video del repositorio.

## Si ocurre un error

| Situación | Acción fuera de la grabación |
|---|---|
| GPU CUDA no disponible | En Colab: Entorno de ejecución → Cambiar tipo de entorno → GPU T4. Volver a preparar A1–A5. |
| HTTP 404 o rutas antiguas | Abrir una copia nueva desde el enlace de este guion. La nueva descarga fija las fuentes por commit. Si el servicio falla, usar el paquete manual indicado arriba. |
| Falta el soporte del video o el grafo | Usar `Deliverable3_ejecucion.zip` del paquete actualizado, no el ZIP original. |
| Transformers importado difiere del instalado | Reiniciar la sesión y ejecutar A1–A5 nuevamente, en orden. |
| No hay una ejecución exportable | Ejecutar B1; después, comprobar sus identificadores en C1. No repetir A5 entre los intentos que quieras conservar juntos. |

## Notas para explicar con precisión

- El razonamiento solicitado al Redactor es una técnica de prompting; no prueba que cada paso interno sea correcto. En la vista final se muestra la respuesta depurada, mientras el registro conserva la salida cruda.
- La revisión devuelve el motivo de corrección. El controlador conserva el borrador anterior, pero el prompt evaluado del Redactor no lo inserta; no afirmar que relee su texto anterior.
- H17 reúne normas generales y particulares; no es una consulta de un dato aislado. H03 es deliberadamente distinto: exige recuperación, aritmética y comparación.
- La evaluación con apoyo de Claude fue revisada por el equipo, según su confirmación. Las cifras de B3 son históricas; no se recalculan durante el video.
