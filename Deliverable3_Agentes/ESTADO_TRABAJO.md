# Estado de cierre de Deliverable 3

Actualizado: 27 de octubre de 2026. Pablo autorizó seguimiento nocturno, descarga y análisis, correcciones, ejecución necesaria, informe LaTeX, guion de video y actualización de GitHub. La automatización de este chat se llama `Completar Deliverable 3`, ID `seguimiento-nocturno-del-piloto-d3`, y revisa cada cinco minutos.

## Evidencia disponible

- Código nuevo desde D1/D2 en esta carpeta; no utilizar el otro directorio `Deliverable3/` ni la rama `backup/deliverable3` como fuentes.
- Piloto v1 intacto: `resultados/piloto_222681994dcd692c0600`, agentes 0/4 frente a D2 2/4.
- Piloto v2 ya descargado, importado, auditado y evaluado: `resultados/piloto_14f5ffa72e8a2734d481`, agentes 1/4 frente a D2 2/4. Ver su REPORTE.md antes de volver a diagnosticar.
- Código actual v3: 37 pruebas locales aprobadas; validación CPU final con E5 y tokenizador reales, 700 prompts. No equivale a calidad generativa.
- Colab en Safari: https://colab.research.google.com/drive/1Y69nHfh0KW6YoIJyDuFVHvCvblxFvRTQ . v2 terminó y se descargó como `agentes_14f5ffa72e8a2734d481.zip`. Hay un conflicto de guardado remoto; no sobrescribir cambios desconocidos. Antes de cualquier operación, comprobar el estado actual.

## Orden de trabajo pendiente

1. Implementado en v3 (pendiente de medir): corregir el protocolo del investigador: transfiere decisiones, no copia el corpus. Mejorar retroalimentación de propiedades extra y salidas cortadas. Reducir mensajes y extractos excesivos sin codificar respuestas del test. Diagnóstico detallado en el reporte v2.
2. v3 está implementada, probada y el notebook regenerado. Ejecutar el piloto real en la misma T4, conservando v1/v2. No alterar checkpoints ni seleccionar solo intentos favorables.
3. Cuando el flujo sea utilizable, congelar código/prompts/configuración y ejecutar 50 preguntas por seis condiciones. Resolver interrupciones desde checkpoints. Si la calidad es inferior a D2, reportarlo; no es lícito inventar una mejora.
4. Evaluar externamente las 300 respuestas con la misma pauta y registrar errores, regresiones, coste, ablaciones y limitaciones de desarrollo. No confundir aceptación del auditor con acierto.
5. Elaborar informe LaTeX vertical de una página: todos los agentes y herramientas en el grafo, aristas/decisiones/loops/stops; técnicas, ablaciones, datos, pauta, resultados y enlaces. Compilar y revisar visualmente. Autores del repositorio: Álvaro Contreras y Pablo Cortés; curso 580694.
6. Crear guion cronometrado de hasta tres minutos y preparar una demostración con mensajes y trazas reales. Verificar por separado video efectivo y enlace abierto; un guion no satisface ese requisito.
7. Publicar cambios pertinentes en `origin` (Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1), sin incluir otros cambios previos ni secretos, y comprobar que notebook, fuentes, resultados, informe, README y enlaces coinciden con la versión evaluada.
8. Contrastar cada requisito con el enunciado en `../Deliverables/Deliverable 3 (1).pdf` respecto de la raíz del repositorio. La entrega final no está completa todavía.

La autorización permite avanzar sin confirmaciones rutinarias. Si hay una barrera real de permisos, autenticación o disponibilidad, completar primero el trabajo independiente, documentarla y comunicar exactamente qué falta.

## Operación actual

La subida de notebook desde Safari deja el botón Cargar desactivado, incluso con una copia idéntica en `/private/tmp/D3_v3.ipynb`. Se intentará abrir el notebook publicado desde GitHub. La autenticación de gh funciona al disponer de red; el aviso inicial de token inválido fue causado por la conexión restringida. Los resultados v1/v2 conservan espacios y terminadores originales para mantener sus hashes.
