# Validación actual v4

38 pruebas locales aprobadas. Contextos reales: 700 prompts, máximo de entrada 3.926 tokens, total con salida y margen 5.014 < 8.192. Ver `validacion/cpu_v4/`. No se midió aún calidad generativa v4. El piloto v3 real se conserva y evalúa en `resultados/piloto_9b826dfab6be77ac0ce1/`.

# Validación de la implementación nueva

Actualizado el 27 de octubre de 2026. Se distingue la validación del código de la calidad del modelo. Todo corresponde a `Deliverable3_Agentes/`, desarrollado desde cero a partir de D1/D2.

## Versión v3: estado actual

37 pruebas locales aprobadas. Se añadieron regresiones para identificar claves sobrantes sin adoptar fuentes generadas por el modelo y para verificar citas normativas incluso cuando aparecen en prosa o entre paréntesis. Se mantienen las pruebas de contratos, límites, controles D2, ablaciones, reanudación y descarga de doce resultados.

[Validación CPU v3](validacion/cpu_v3/reporte.json): E5 y tokenizador reales, 50 preguntas, 700 prompts, máxima entrada 3.797 tokens (4.885 con salida y margen), menor que 8.192. No se ejecutó Qwen v3 todavía. La versión v2 sí se ejecutó en T4 y se evaluó en [su reporte](resultados/piloto_14f5ffa72e8a2734d481/REPORTE.md); las secciones siguientes documentan comprobaciones históricas de v2.

## Versión v2: código y notebook

**35 pruebas aprobadas**, ejecutadas con:

```bash
python3 -m unittest discover -s Deliverable3_Agentes/tests -v
```

Cubren los contratos condicionales, la búsqueda inicial, decisiones de los tres agentes, fuentes inventadas, recuperación de información faltante, descarte de borradores obsoletos, interrupción de ciclos, límites y contextos sin truncamiento. También verifican que los controles baseline/D2 conservan sus prompts, que cada ablación cambia solo su bloque de prompting, semillas por rol, checkpoints, reanudación, integridad de ZIP/CSV y evaluación externa pendiente.

Una prueba vuelve a leer las siete salidas inválidas reales del piloto v1: las cinco con errores de transporte ahora pasan; las dos con fuentes inventadas siguen rechazadas. Es una comprobación del analizador, no una nueva respuesta de Qwen.

Los demás flujos de inferencia se prueban con backends **simulados y etiquetados `simulacion_pruebas`**, en carpetas temporales. No se presentan como exactitud del sistema. Las celdas reales de consulta/piloto/lote/inspección/descarga se ejecutan después de una carga simulada: generan doce respuestas, llevan la etiqueta `piloto-v2` y solicitan la descarga. Se prueban interrupciones, múltiples corridas, ausencia de resultados y bloqueo de descarga del navegador.

La construcción del notebook es reproducible; se validan esquema, sintaxis, fuentes y prompts restaurados, y ausencia de salidas precargadas. La versión nueva exige reiniciar la sesión si siguen cargados módulos de otro paquete.

## Versión v2: recuperación y tokenización reales

[Reporte de la versión final](validacion/cpu_v2_final/reporte.json) y [diagnóstico E5](validacion/cpu_v2_final/tokenizador_e5.json).

- E5 se cargó desde caché y reconstruyó el índice de 201 fragmentos.
- Se recuperó evidencia para las 50 preguntas de desarrollo.
- Se midieron 700 prompts con el tokenizador real de la revisión fijada de Qwen3-4B: baseline, D2 y tres roles en cuatro condiciones de agentes.
- Máxima entrada: 3.770 tokens. Con 1.024 reservados para salida y 64 de margen: 4.858, dentro del límite de 8.192.
- Se comprobaron los tres inventarios y la lectura íntegra de los 95 artículos ordinarios RG/RI-FI, incluidas todas sus unidades. Consultar un artículo ausente devuelve el inventario.

Los borradores de esta medición son sintéticos. Estos contextos no abarcan todas las trayectorias posibles: el controlador mide cada llamada y rechaza incorporar evidencia si no cabe; no trunca artículos. Los hashes fijan las fuentes verificadas. El reporte intermedio `cpu_v2` se conserva y precede al último ajuste de descarte del borrador; `cpu_v2_final` corresponde al código entregado.

Para repetir, con E5 en caché y el tokenizador Qwen acompañado por `revision.txt`:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python3 Deliverable3_Agentes/validar_cpu.py --tokenizador /ruta/tokenizador_qwen --salida /ruta/nueva/validacion
```

## Inferencia real y calidad

El [piloto v1 en T4](resultados/piloto_222681994dcd692c0600/REPORTE.md) guardó las doce respuestas: baseline 0/4, D2 2/4 y agentes 0/4 según revisión asistida con la pauta D2. Los agentes agotaron límites de formato o llamadas. Esta corrida se conserva intacta y motivó las [correcciones v2](CORRECCION_V2.md).

**Esta sección era previa a la inferencia v2, ahora registrada en su reporte.** Este equipo local no tiene CUDA; las pruebas locales no determinan su exactitud, tasa real de JSON válido, utilidad de decisiones ni latencia. El paso pendiente es repetir P05/P25/P38/P41 con el notebook actualizado en T4 y evaluar sus doce respuestas. La aceptación interna del auditor nunca sustituye esa evaluación.

## Validaciones históricas

El [reporte CPU v1](validacion/cpu_v1/reporte.json) corresponde a la implementación inicial: 700 prompts, máxima entrada de 3.523 tokens. No describe los prompts v2.

El 26 de octubre se corrigió el flujo que solo cargaba modelos al ejecutar todas las celdas: consulta vacía, piloto desactivado y lote desactivado. El piloto ahora está activado y la exportación recupera corridas aun sin `RUN_DIR`. La corrección sigue comprobada por las pruebas del notebook v2.
