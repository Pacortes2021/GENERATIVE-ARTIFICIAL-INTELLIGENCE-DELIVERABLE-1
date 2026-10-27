# Corrección tras el primer piloto en T4

27 de octubre de 2026. Versión de código 0.2.0, protocolo `d3-agentes-desde-cero-v2`, piloto `piloto-v2`.

La versión v2 corrige los fallos de coordinación observados en el [piloto v1](resultados/piloto_222681994dcd692c0600/REPORTE.md). Su exactitud con Qwen está pendiente: las pruebas locales comprueban comportamiento del código, no calidad de respuestas.

| Fallo observado | Cambio general, sin reglas por ID de pregunta |
|---|---|
| Acciones de búsqueda válidas rechazadas por usar el nombre de herramienta; transferencias rechazadas por omitir un campo vacío | Contrato condicional explícito. Se admiten nombres de herramienta solo si coinciden con la solicitud; no se infieren argumentos. Se permite omitir `herramienta` al redactar y `respuesta` al investigar. Las salidas originales y decisiones normalizadas permanecen en la traza. |
| Redacción sin evidencia y reformulación inicial que pierde información | Búsqueda inicial automática con la pregunta original mediante el recuperador D2. Consume una de las seis consultas. No se permite transferir al redactor sin fuentes. |
| Correcciones reiteradas sin conseguir respaldo | Los prompts distinguen corregir con evidencia disponible de investigar lo que falta. Un borrador idéntico con las mismas fuentes, una cita desconocida o dos correcciones sin nueva evidencia provocan una transferencia registrada al investigador. |
| Repetición de un artículo inventado después de comprobar su ausencia | Historial de observaciones disponible para los tres agentes, inventario legible y eliminación del borrador al pedir investigación o incorporar nuevas fuentes. Se conservan todos los borradores anteriores en la traza, fuera de la entrada activa. |
| Error de formato que reemplaza la solicitud del otro agente | Campo separado de error de formato, con instrucciones concretas y preservación de la necesidad documental original. |

Los mensajes entre agentes se identifican expresamente como datos no verificados. Los prompts no incluyen respuestas de referencia ni una solución específica para P05/P25/P38/P41. No aumentaron los límites: siguen siendo doce llamadas, seis consultas y tres salidas inválidas. Los controles baseline/D2, modelo, semillas y muestreo se conservan. Las tres ablaciones mantienen estos mismos cambios operativos.

## Comprobaciones

- 35 pruebas aprobadas: transferencias, límites, eliminación de borradores obsoletos, ausencia documental, controles D2, ablaciones, reanudación, exportación e integridad.
- Relectura de las siete salidas inválidas reales del piloto: las cinco rechazadas por formato pasan el contrato v2; las dos con fuentes inventadas siguen rechazadas. Esto no reejecuta Qwen ni demuestra que las nuevas respuestas sean correctas.
- Ejecución de las celdas de piloto y descarga con un generador simulado: doce resultados, etiqueta v2 y solicitud de descarga. Las simulaciones no se guardan como resultados reales.
- E5 y tokenizador Qwen reales, sin pesos generativos: [validación CPU de la versión final](validacion/cpu_v2_final/reporte.json). Se midieron 700 prompts sobre las 50 preguntas; los borradores de longitud son sintéticos. Cada llamada futura vuelve a comprobar su contexto.
- El ZIP original, sus fuentes congeladas y su evaluación se conservan intactos.

## Repetir en T4

1. Subir [el notebook actualizado](Deliverable3_Agentes_Colab.ipynb) a Colab. El título debe terminar en **v2**.
2. Reiniciar la sesión para descargar de memoria el código anterior; mantener la GPU T4.
3. Ejecutar todas las celdas. El piloto está activado y el lote de 50 preguntas desactivado.
4. Conservar el ZIP de la sección 8. Si la descarga automática falla, usar la ruta impresa en el panel Archivos.
5. Auditar y evaluar las doce respuestas nuevas con la pauta D2 antes de decidir si la versión sirve para el lote completo.

El ZIP contiene una configuración y fuentes distintas, por lo que no reutiliza las respuestas del piloto v1. Si la carpeta de salida también conserva corridas antiguas, la descarga puede agrupar varios ZIP; sus configuraciones permiten distinguirlos.
