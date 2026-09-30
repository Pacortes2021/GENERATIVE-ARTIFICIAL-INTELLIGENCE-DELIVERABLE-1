# Cómo grabar tu video de Deliverable 2

La demostración principal consiste en **ejecutar una pregunta en Qwen y mostrar sus respuestas y la evidencia recuperada dentro de Colab**. Usaremos P25 para comprobar si se reproduce el fallo conocido. La auditoría del lote anterior queda como resumen histórico al final; no sustituye esta ejecución. Conserva la sesión original con Qwen cargado: no repitas las secciones 1–4 ni el lote de 50.

## 1. Probar P25 de nuevo en la sesión abierta

La pregunta exacta es: **«Al modificar la inscripción, ¿qué asignaturas NO puedo eliminar?»**. Es una pregunta conocida, elegida para volver a probar un fallo; no la presentes como una pregunta nueva o independiente.

Añade una celda con **+ Código** y pega este bloque. Para mostrar la ejecución en el video, inicia la grabación antes de pulsar ▶. Usa el modelo y el índice cargados, recupera de nuevo y genera dos respuestas. Cada intento usa una carpeta nueva; no reutiliza checkpoints ni sobrescribe salidas anteriores.

```python
from pathlib import Path
from tempfile import mkdtemp
from sistema import prepare_run, run_tasks, show_comparison, export_run

ID_PRUEBA = 25
PRUEBA_PREGUNTA = next(q for q in QUESTIONS if q['id'] == ID_PRUEBA)
PRUEBA_RAIZ = Path(OUTPUT_ROOT) / 'pruebas_en_vivo'
PRUEBA_RAIZ.mkdir(parents=True, exist_ok=True)
PRUEBA_INTENTO = Path(mkdtemp(prefix=f'P{ID_PRUEBA:02}_', dir=PRUEBA_RAIZ))
print('Pregunta conocida:', PRUEBA_PREGUNTA['pregunta'], flush=True)
print('Generación nueva; semilla:', SETTINGS['semilla_base'] + ID_PRUEBA, flush=True)
PRUEBA_DIR, PRUEBA_CONFIG, PRUEBA_CASOS, PRUEBA_TAREAS = prepare_run(
    [PRUEBA_PREGUNTA], retriever, tokenizer, SETTINGS, PRUEBA_INTENTO)
PRUEBA_RESPUESTAS = run_tasks(PRUEBA_DIR, PRUEBA_CONFIG, PRUEBA_CASOS, PRUEBA_TAREAS, generate)
ZIP_PRUEBA = export_run(PRUEBA_DIR, PRUEBA_CONFIG, PRUEBA_TAREAS)
show_comparison(PRUEBA_RESPUESTAS, PRUEBA_CASOS)
print('Intento conservado en:', ZIP_PRUEBA)
```

Debe aparecer **`generada ahora`** para baseline y RAG. Se conserva el ID 25 para usar su semilla, 2051 con la configuración original. La celda normal de consulta nueva usa el ID 1 y puede reutilizar checkpoints; por eso este paso tiene su propia celda. El cuaderno actual la incluye como sección 5b, desactivada hasta elegir un ID. No hace falta cambiar de cuaderno si pegas el bloque en la sesión que tienes.

Abre **«Fragmentos exactos enviados únicamente a RAG»** bajo las dos respuestas. Comprueba qué respondió ahora y si recibió completos los artículos 7 y 9. Solo si se dan ambas cosas —evidencia completa y respuesta que omite explicar las prioridades— puedes señalar en esta ejecución el fallo de síntesis. Si los fragmentos o la respuesta cambian, explica lo que realmente aparece. No añadas pistas de la respuesta ni los artículos a la pregunta para conseguir un resultado particular.

**Si esta vez responde bien, conserva y muestra ese resultado.** El fallo anterior sigue documentado como tal, pero no afirmes que se reprodujo ni repitas hasta conseguir un error. Esta repetición tampoco cambia automáticamente el 80% histórico. Después de grabar, descarga el intento con `from google.colab import files; files.download(str(ZIP_PRUEBA))`.

## 2. Mostrar el resumen histórico sin seleccionar P25

Esta celda es opcional para la parte final del video. Sustituye el bloque anterior de auditoría por este; `ID_CASO = None` evita seleccionar una respuesta histórica. Descarga una versión fija del código, comprueba su SHA-256 y muestra los recuentos desde el ZIP original. No exige Drive montado: si el archivo falta, descarga la copia publicada de la corrida previa e indica su origen.

```python
import hashlib, urllib.request
ID_CASO = None
URL_AUDITORIA = ('https://raw.githubusercontent.com/Pacortes2021/'
    'GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/06188c5ca15cb696346ea2d7814d65b18bcb319a/'
    'Deliverable2/notebooks/auditar_lote_en_colab.py')
SHA_CODIGO = '398c7f3b66b3f9ccd24a0a13f3d4f101ab911b7042e87e27ceb52a4a970430d1'
codigo = urllib.request.urlopen(URL_AUDITORIA, timeout=30).read()
assert hashlib.sha256(codigo).hexdigest() == SHA_CODIGO, 'Cambió el código de auditoría.'
print('Código de auditoría verificado:', SHA_CODIGO)
exec(compile(codigo.decode('utf-8'), URL_AUDITORIA, 'exec'))
```

Puedes [leer el código completo de la celda](../notebooks/auditar_lote_en_colab.py) antes de ejecutarla. La [versión nueva del cuaderno](../notebooks/Deliverable2_Sistema_RAG_Colab.ipynb) ya la incluye como sección 7, pero **no cambies de cuaderno solo para grabar**: tu sesión anterior conserva Qwen en memoria.

La celda busca `comparacion_f0bff499766960f7.zip` en `ZIP_LOTE`, en `OUTPUT_ROOT`, en la carpeta de Drive y en el almacenamiento temporal de Colab. Si no lo encuentra, descarga la copia original desde el commit fijo `773a7da` a `/content/auditoria_publicada/`. Siempre muestra el origen y la ruta, y verifica el hash del ZIP, configuración, prompts, evidencia y 100 respuestas. Descarga de ese mismo commit los dos paquetes de evaluación y los dos archivos de veredictos, valida sus hashes y comprueba que cada juicio corresponde al texto exacto de la respuesta. Después **recuenta veredictos registrados**: baseline 1/50 y RAG 40/50. Muestra la lista completa de diez errores RAG. Para inspeccionar voluntariamente una respuesta histórica, cambia `ID_CASO` por su número; el resultado se etiqueta como guardado.

Si encuentra un ZIP local cuyo hash es distinto, se detiene sin reemplazarlo. En ese caso, sube el **ZIP original** `comparacion_f0bff499766960f7.zip` desde Descargas y, en una celda antes de la auditoría, fija `ZIP_LOTE = '/content/comparacion_f0bff499766960f7.zip'`. No alteres las respuestas ni los veredictos para que pase la comprobación. Cuando se usa la copia pública, se está auditando aquella corrida previa; no es una ejecución nueva ni demuestra que ese lote se haya generado en la sesión actual.

La auditoría no convierte el juicio de IA en una verdad matemática: el hash prueba integridad y correspondencia, mientras que la [pauta](../evaluacion/criterios.md), las respuestas y los motivos permiten revisar la decisión semántica. Di «40/50 según la pauta y los veredictos asistidos», no «Colab comprobó por sí solo que 40 son correctas».

## 3. Prepara la pantalla

1. En Brave deja abierto solo el Colab original. Cierra descargas y avisos. Ajusta el zoom del navegador hasta que se lean las salidas; 125 % suele funcionar.
2. Localiza las salidas ya terminadas de las secciones 2–4, la nueva celda de prueba individual, la salida del lote de la sección 6 y la auditoría. No ejecutes aún la prueba que vas a grabar.
3. Para esta demostración elegimos P25 como repetición de un fallo conocido. Conserva el resultado que aparezca; esta prueba no se suma al 80% ni mide generalización a preguntas nuevas.
4. Ejecuta la celda de auditoría una vez antes de grabar para comprobar el acceso al ZIP y los archivos publicados. Puedes ejecutarla otra vez en cámara: no llama al modelo ni modifica las respuestas.

## 4. Graba en macOS, sin voz

Pulsa **Mayúsculas + Comando + 5**. Elige **Grabar parte seleccionada** y encuadra solo la ventana de Brave. En **Opciones**, selecciona **Micrófono: Ninguno**, guarda en Escritorio o Descargas y activa mostrar clics si te ayuda. Pulsa **Grabar**; detén desde el icono de la barra de menú antes de los **3:00**. QuickTime permite recortar el comienzo o final con **Comando + T** si quedan segundos vacíos; conserva íntegra la ejecución y las salidas.

Recorrido sugerido para **2:40–2:55**:

| Tiempo aproximado | Qué mostrar en Colab |
|---|---|
| 0:00–0:20 | Título del cuaderno, GPU y salidas existentes: corpus 197/201, E5 e índice, Qwen listo. |
| 0:20–1:30 | Ejecuta P25 en la celda de prueba individual. Muestra pregunta, semilla y `generada ahora` en ambas condiciones. |
| 1:30–2:25 | Lee las dos respuestas y abre los fragmentos exactos. Explica el resultado observado con respecto a los artículos recuperados. |
| 2:25–2:55 | Enseña brevemente la salida previa del lote y el resumen auditado: origen, 1/50 y 40/50, etiquetados como resultados anteriores. |

Todo queda dentro de Colab. Los títulos y las salidas aportan contexto sin voz sintética. La prioridad es que se vea la ejecución y se puedan leer la respuesta y la evidencia. Si la inferencia hace superar los tres minutos, puedes recortar únicamente tiempo de espera, indicando el corte; conserva completos el inicio de la ejecución y sus resultados. No reemplaces la salida por otra toma favorable.

## 5. Después de grabar

Reproduce el archivo y comprueba que se leen las respuestas y las fuentes, que dura menos de tres minutos y que no capturó otra ventana. Guarda el video y el ZIP de esta prueba en Descargas y avísame: podremos revisar el resultado real, preparar el archivo definitivo y actualizar el enlace del PDF.
