# Cómo grabar tu video de Deliverable 2

La nueva versión debe ser **una grabación de tu Colab**, sin voz sintética ni pantallas de resultados añadidas en edición. La sesión original de Brave con Qwen cargado sirve: **no vuelvas a ejecutar las secciones 1–4 ni el lote de 50 de la sección 6**. Solo ejecuta una pregunta nueva y la auditoría ligera descrita abajo.

## 1. Añade la auditoría a tu sesión actual

Al final del cuaderno abierto en Brave, pulsa **+ Código** y pega esta celda. Descarga código visible en el repositorio, comprueba su SHA-256 antes de ejecutarlo y luego muestra en Colab los resultados obtenidos desde el ZIP guardado en Drive.

```python
import hashlib, urllib.request
URL_AUDITORIA = ('https://raw.githubusercontent.com/Pacortes2021/'
    'GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/main/'
    'Deliverable2/notebooks/auditar_lote_en_colab.py')
SHA_CODIGO = 'fc9699ab5f578cc066a5b6d8c61dc8d59ddd8fd49b19e9c2184935b615cc2cf8'
codigo = urllib.request.urlopen(URL_AUDITORIA, timeout=30).read()
assert hashlib.sha256(codigo).hexdigest() == SHA_CODIGO, 'Cambió el código de auditoría.'
print('Código de auditoría verificado:', SHA_CODIGO)
exec(compile(codigo.decode('utf-8'), URL_AUDITORIA, 'exec'))
```

Puedes [leer el código completo de la celda](../notebooks/auditar_lote_en_colab.py) antes de ejecutarla. La [versión nueva del cuaderno](../notebooks/Deliverable2_Sistema_RAG_Colab.ipynb) ya la incluye como sección 7, pero **no cambies de cuaderno solo para grabar**: tu sesión anterior conserva Qwen en memoria.

La celda abre `/content/drive/MyDrive/GenIA_Deliverable2/sistema_runs/comparacion_f0bff499766960f7.zip`. Verifica el hash del ZIP original, configuración, prompts, evidencia y 100 respuestas. Descarga del commit fijo `773a7da` los dos paquetes de evaluación y los dos archivos de veredictos, valida sus hashes y comprueba que cada juicio corresponde al texto exacto de la respuesta. Después **recuenta veredictos registrados**: baseline 1/50 y RAG 40/50. Muestra la lista completa de diez errores RAG y, por defecto, P25 con la respuesta, la referencia, el motivo y los artículos 7 y 9 completos que estaban en el prompt de Qwen.

Si aparece «No encuentro el ZIP», comprueba en el panel Archivos de Colab que Drive sigue montado. Si el ZIP de Drive fue reexportado y cambió su hash, sube el **ZIP original** `comparacion_f0bff499766960f7.zip` desde Descargas y, en una celda antes de la auditoría, fija `ZIP_LOTE = '/content/comparacion_f0bff499766960f7.zip'`. No alteres las respuestas ni los veredictos para que pase la comprobación.

La auditoría no convierte el juicio de IA en una verdad matemática: el hash prueba integridad y correspondencia, mientras que la [pauta](../evaluacion/criterios.md), las respuestas y los motivos permiten revisar la decisión semántica. Di «40/50 según la pauta y los veredictos asistidos», no «Colab comprobó por sí solo que 40 son correctas».

## 2. Prepara la pantalla

1. En Brave deja abierto solo el Colab original. Cierra descargas y avisos. Ajusta el zoom del navegador hasta que se lean las salidas; 125 % suele funcionar.
2. Localiza las salidas ya terminadas de las secciones 2–4, la celda de la sección 5, la salida del lote de la sección 6 y la nueva celda de auditoría. No ejecutes aún una pregunta nueva.
3. Elige tú una pregunta sobre el corpus que **no hayas probado**. Escribirla y ejecutar la sección 5 durante la grabación, sin descartar el resultado si falla, evita escoger una respuesta favorable. La consulta ilustrativa no se suma al 80 %.
4. Ejecuta la celda de auditoría una vez antes de grabar solo si necesitas comprobar la ruta de Drive. Puedes ejecutarla otra vez en cámara: no llama al modelo ni modifica el ZIP.

## 3. Graba en macOS, sin voz

Pulsa **Mayúsculas + Comando + 5**. Elige **Grabar parte seleccionada** y encuadra solo la ventana de Brave. En **Opciones**, selecciona **Micrófono: Ninguno**, guarda en Escritorio o Descargas y activa mostrar clics si te ayuda. Pulsa **Grabar**; detén desde el icono de la barra de menú antes de los **3:00**. QuickTime permite recortar el comienzo o final con **Comando + T** si quedan segundos vacíos; conserva íntegra la ejecución y las salidas.

Recorrido sugerido para **2:40–2:55**:

| Tiempo aproximado | Qué mostrar en Colab |
|---|---|
| 0:00–0:20 | Título del cuaderno, GPU y salidas existentes: corpus 197/201, E5 e índice, Qwen listo. |
| 0:20–1:25 | Escribe la pregunta elegida en sección 5, ejecútala una vez y espera las dos respuestas. Muestra `generada ahora` y los fragmentos recuperados. |
| 1:25–1:40 | Enseña la salida previa `100/100` de sección 6. **No la ejecutes otra vez.** |
| 1:40–2:50 | Ejecuta la nueva celda de auditoría. Detente en las comprobaciones `OK`, 1/50 y 40/50; baja hasta la lista de diez fallos, P25, su veredicto y los dos artículos íntegros. |

Todo queda dentro de Colab. Los títulos de secciones y la salida de la auditoría aportan el contexto que antes intentaba dar la voz. Si tu pregunta en vivo resulta incorrecta, muéstrala igualmente y señala la limitación: eso hace la demostración más creíble.

## 4. Después de grabar

Reproduce el archivo y comprueba que se leen las respuestas, la tabla de recuentos y P25. Asegúrate de que dure menos de tres minutos y no se haya capturado otra ventana. Guarda el archivo en Descargas y avísame; puedo verificar duración, resolución y contenido, reemplazar el borrador anterior y actualizar el enlace del PDF sin alterar lo que se ve en tu ejecución.
