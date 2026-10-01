# Cuadernos de Colab

- [Deliverable2_Sistema_RAG_Colab.ipynb](Deliverable2_Sistema_RAG_Colab.ipynb): Cuaderno principal con el sistema completo. Permite consultar preguntas individuales y contiene la opción de ejecutar el lote emparejado de 50 preguntas (`EJECUTAR_LOTE_50 = True`).
- [Deliverable2_Demo_Video.ipynb](Deliverable2_Demo_Video.ipynb): Cuaderno ágil utilizado para la grabación del video demostrativo (≤ 3 minutos). Presenta de forma secuencial la ejecución en vivo de P25, la consulta manual interactiva y la auditoría rápida del lote sin esperas prolongadas.

## Uso

1. Sube el `.ipynb` a Colab, selecciona GPU y ejecuta las secciones 1–4 en orden. Si acabas de instalar librerías o abriste una versión anterior, reinicia la sesión y vuelve a empezar.
2. En la sección 5 cambia `PREGUNTA = ""` por tu pregunta. La celda busca la evidencia, genera ambas respuestas y muestra los fragmentos enviados solo a RAG.
3. Descarga el ZIP generado. Si ejecutas de nuevo exactamente la misma consulta con igual configuración, se reutilizan los checkpoints y se indica que son respuestas guardadas.
4. Para una comparación nueva sobre las 50 preguntas conocidas, en la sección 6 cambia `EJECUTAR_LOTE_50 = False` a `True` y deja `IDS_LOTE = None`. `IDS_LOTE = [1, 2]` serviría para un lote corto. Al terminar, vuelve a ejecutar la celda de descarga situada antes de la sección 6 para obtener el ZIP con `baseline_directo.csv` y `rag_estructurado.csv`.
5. Evalúa ambos CSV con la [misma pauta](../evaluacion/README.md). El cuaderno registra datos técnicos, pero no asigna corrección semántica por sí solo.
6. La sección 5b permite volver a ejecutar una pregunta conocida, por ejemplo P25, sin reutilizar checkpoints. Elige `ID_PRUEBA`; cada intento recupera y genera de nuevo, conserva el ID y su semilla, y guarda su propio ZIP sin modificar el lote original. No envía respuestas ideales ni veredictos al generador. La [guía de grabación](../entrega/Como_grabar_video_D2.md) incluye el bloque para pegarlo en una sesión ya abierta.
7. La sección 7 audita el ZIP y los veredictos **ya publicados** de la corrida emparejada. Busca el ZIP en `ZIP_LOTE`, `OUTPUT_ROOT`, Drive y el almacenamiento temporal de Colab; si falta, descarga la copia original publicada desde un commit fijo y señala su origen. Comprueba 100 respuestas y sus hashes antes de recalcular 1/50 y 40/50. Por defecto muestra solo recuentos y la lista de fallos: `ID_CASO = None`. Un ID selecciona expresamente una respuesta histórica y su evidencia; no la genera. No requiere GPU, Drive montado ni repetir el lote. Su [código autónomo](auditar_lote_en_colab.py) se puede pegar como una celda nueva en una sesión anterior que tenga Qwen cargado.

`USAR_DRIVE=True` guarda los checkpoints en Drive; Colab pedirá autorización. Con `False`, descarga el ZIP antes de cerrar la sesión. Las respuestas guardan texto, prompt, evidencia, tokens, tiempo, motivo de parada, configuración y hashes. El baseline recibe solo pregunta e instrucción directa; RAG recibe evidencia recuperada. La nueva comparación conserva el prompt de E1 pero utiliza los parámetros de inferencia de RAG para emparejar las condiciones. Su [resultado medido](../resultados/qwen3_4b_f0bff499766960f7/REPORTE.md) está documentado por separado del 4% histórico.

## Si Colab se desconecta

Comprueba que el título del cuaderno indique **`carga-ligera-v1`**. El archivo actual mide unos 250 KB. Reinicia la sesión y ejecuta el cuaderno recién subido: una pestaña abierta no incorpora las correcciones locales. Si tu sesión anterior sigue activa, basta con añadirle la [celda autónoma de auditoría](auditar_lote_en_colab.py); no la reinicies solo para ver esa sección. La sección «Corpus y código incluidos» debe imprimir tres pasos y terminar con `Corpus listo: 197 unidades completas; 201 fragmentos para búsqueda; 50 preguntas.` Esa celda restaura el paquete comprimido con biblioteca estándar, sin importar los modelos.

La sección siguiente anuncia por separado la importación de librerías, la carga de E5 y la construcción del índice. Si la sesión vuelve a reiniciarse, anota el último mensaje visible. El reinicio informado anteriormente no se reprodujo localmente y su causa concreta no está confirmada. La [medición local de la celda de corpus](validacion_carga_colab.json) solo describe este entorno, no la memoria de Colab.

El tokenizador E5 se verifica contra el JSON exacto con el que se fragmentó el corpus. El cuaderno fija `tokenizers==0.22.2`; si detecta otra versión cargada pide reiniciar. Cualquier diferencia real se registra en `diagnostico_e5_*.json` y detiene la generación sin recortar fragmentos.

## Qué está verificado

La [validación del sistema](validacion_sistema.json) documenta la recuperación real con E5 en CPU: al indexar de nuevo y consultar las 50 preguntas se obtuvieron los mismos contextos guardados. Se comprobó una pregunta fuera del test y se midieron los 100 prompts de baseline/RAG con el tokenizador real de Qwen. Las pruebas locales comprueban generación simulada, reanudación y exportación. Un [piloto real en GPU Colab](../resultados/piloto_consulta_882da178b0514f0d/REPORTE.md) produjo una respuesta baseline y una RAG para una pregunta nueva. El [lote emparejado de 50](../resultados/qwen3_4b_f0bff499766960f7/REPORTE.md) ya produjo 100 respuestas, verificadas y evaluadas con la pauta E2.

Para regenerar el cuaderno desde la raíz del repositorio se necesita `nbformat`:

```bash
python3 Deliverable2/notebooks/crear_sistema.py
```

[crear_sistema.py](crear_sistema.py) verifica las fuentes e incluye [sistema.py](sistema.py), [experimento.py](experimento.py) y las funciones originales del recuperador. Las preguntas incluidas contienen solo ID, texto y categoría: las respuestas de referencia y veredictos no se entregan a Qwen. La [configuración elegida](../CONFIGURACION_ELEGIDA.md) explica qué versión se usa y sus límites.

## Experimentos anteriores

El [cuaderno de tres variantes](Deliverable2_RAG_3_variantes_Colab.ipynb) produjo la [primera corrida evaluada](../resultados/qwen3_4b_4adccec813c53d7f/REPORTE.md). El [cuaderno de dos variantes](Deliverable2_RAG_2_variantes_Colab.ipynb) conserva simple y estructurado con evidencia previamente calculada. Estos cuadernos no ejecutan recuperación para preguntas nuevas. [Revisar_resultados_RAG.ipynb](Revisar_resultados_RAG.ipynb) inspecciona el ZIP histórico sin GPU. La [revisión del cuaderno inicial](REVISION_CUADERNO_ANTERIOR.md) documenta qué se aprovechó y qué se corrigió.
