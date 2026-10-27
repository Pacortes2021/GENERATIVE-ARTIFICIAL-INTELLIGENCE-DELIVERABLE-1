# Estado de cierre de Deliverable 3

Actualizado: 27 de octubre de 2026. Pablo autorizó seguimiento nocturno, descarga y análisis, correcciones, ejecución necesaria, informe LaTeX, guion de video y actualización de GitHub. La automatización de este chat se llama `Completar Deliverable 3`, ID `seguimiento-nocturno-del-piloto-d3`, y tiene frecuencia de cinco minutos. Está PAUSADA por bloqueo de pantalla; no se detuvo la ejecución de Colab.

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
5. Borrador compilado y revisado en `entrega/main.pdf` (A4, una página), fuente `entrega/main.tex`. Cerrar el contenido tras el lote: todos los agentes y herramientas en el grafo, aristas/decisiones/loops/stops; técnicas, ablaciones, datos, pauta, resultados y enlaces. Compilar y revisar visualmente. Autores del repositorio: Álvaro Contreras y Pablo Cortés; curso 580694.
6. Guion de ensayo de 2:50 y mensajes reales P05/P41 preparados en `entrega/`. Falta ajustar a la versión final y grabar. Verificar por separado video efectivo y enlace abierto; un guion no satisface ese requisito.
7. Código v3 y pilotos publicados en commit `553944b491291aa862544925361926450eea982d`. Continuar publicando cambios pertinentes en `origin` (Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1), sin incluir otros cambios previos ni secretos, y comprobar que notebook, fuentes, resultados, informe, README y enlaces coinciden con la versión evaluada.
8. Contrastar cada requisito con el enunciado en `../Deliverables/Deliverable 3 (1).pdf` respecto de la raíz del repositorio. La entrega final no está completa todavía.

La autorización permite avanzar sin confirmaciones rutinarias. Si hay una barrera real de permisos, autenticación o disponibilidad, completar primero el trabajo independiente, documentarla y comunicar exactamente qué falta.

## Operación actual

El notebook v3 se abrió desde GitHub, evitando el selector de subida de Safari que mantenía Cargar desactivado:

https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/553944b491291aa862544925361926450eea982d/Deliverable3_Agentes/Deliverable3_Agentes_Colab.ipynb

La sesión anterior del enlace Drive estaba desconectada y su ZIP v2 ya estaba a salvo. Se finalizó únicamente esa sesión para liberar el cupo GPU y se conectó una T4 nueva. Colab mostró «Ejecutando 8 celdas» al ejecutar v3. No modificar esta versión mientras el intento esté pendiente de recoger.

**Bloqueo de interfaz (27-10, aproximadamente 02:20 Chile):** cua_repl informó «The Mac is locked and automatic unlock could not unlock it». Hace falta desbloqueo manual. No se interrumpió ni recargó la nueva corrida; no puede confirmarse su avance. A las 02:21 no existía un ZIP v3 en Descargas. Primero comprobar la nueva pestaña al recuperar acceso y conservar todos los resultados antes de cambiar código o sesión.

El informe preliminar, guion, transcripciones y matriz de requisitos están en `entrega/`; no equivalen a la entrega final. La autenticación de gh funciona con acceso de red; no solicitar nuevas credenciales por el aviso de token inválido de una llamada sin red. Los resultados v1/v2 conservan espacios y terminadores originales para mantener sus hashes.

La automatización se pausó conforme a la autorización de detener el seguimiento ante un bloqueo que requiera al usuario. Para reanudar: desbloquear el Mac y solicitar continuar; activar de nuevo la misma automatización, sin crear un duplicado.
