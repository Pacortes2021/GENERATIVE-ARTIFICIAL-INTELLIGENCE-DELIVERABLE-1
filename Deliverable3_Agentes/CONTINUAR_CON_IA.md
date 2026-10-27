# Continuar el trabajo con otro modelo de IA

Este documento permite retomar el proyecto sin el historial del chat. Leer primero [ESTADO_TRABAJO.md](ESTADO_TRABAJO.md), que registra la última observación disponible; no confundir esa observación con el estado en vivo de Colab.

## Contexto y archivos de entrada

El equipo es Álvaro Contreras y Pablo Cortés. El objetivo es completar Deliverable 3 desde cero sobre D1/D2, trabajando exclusivamente en `Deliverable3_Agentes/`. No reutilizar los prototipos de `Deliverable3/` ni de ramas de respaldo. El usuario autorizó implementar, ejecutar experimentos reales en T4, evaluar, finalizar informe y materiales de video y actualizar este repositorio. No enviar mensajes a terceros.

Leer en este orden:

1. [Enunciado oficial](enunciado.pdf) y [requisitos pendientes](entrega/REQUISITOS.md).
2. [Estado actual](ESTADO_TRABAJO.md), [README de D3](README.md) y [congelación v4](CONGELACION_V4.md).
3. [D1](../Deliverable1/README.md) y [D2](../Deliverable2/README.md), incluida la pauta externa de evaluación que se conserva para D3.
4. [Evaluación](EVALUACION.md), [validación](VALIDACION.md) y reportes de los cuatro pilotos bajo `resultados/`.
5. [Entrega provisional](entrega/README.md): fuente LaTeX, PDF compilado de una página, guion y mensajes reales. Son borradores; no existe todavía el video final ni su enlace abierto.

## Estado respaldado en GitHub

- Código experimental congelado en `de2951b22214f294e9f9eb1f5b0fae9a25c622da`, paquete 0.4.0. Qwen3-4B en T4; seis condiciones sobre las mismas 50 preguntas. No modificar código, prompts, semilla ni parámetros mientras se termina y evalúa el lote.
- Cuatro pilotos reales preservados con ZIP, fuentes, trazas y evaluación independiente. V4 obtuvo agentes 1/4, D2 2/4 y baseline 0/4: no afirmar una mejora de exactitud.
- Corrida completa iniciada: `99b9b55bd79d4572f743`. Último respaldo auditado de este traspaso: **35/300 respuestas**, capturado el 27-10-2026 a las 18:26:49 UTC (15:26:49 Chile), en [snapshots](resultados/lote_99b9b55bd79d4572f743/snapshots/). Conservar todos los ZIP intactos y sus metadatos SHA-256.
- Las primeras 12 respuestas de ese mismo lote tienen [evaluación progresiva](resultados/lote_99b9b55bd79d4572f743/evaluacion_progresiva/README.md). Solo integrar esos juicios en el paquete final si coinciden exactamente los hashes de respuestas, preguntas, corpus, pauta y referencias. No copiar etiquetas de pilotos ni de D1/D2.

## Próxima acción

Comprobar primero si la corrida ya está siendo supervisada por otra sesión. En el Mac original hay una automatización de seguimiento; su configuración y los permisos de Safari no se transfieren al clonar GitHub. Coordinar un único responsable de la interfaz y de los cambios para evitar descargas, reinicios o commits concurrentes.

Usar la pestaña de Colab indicada en el estado de trabajo. No abrir otra sesión para ejecutar el mismo lote, ni pulsar «Ejecutar todo», recargar o desconectar una corrida activa. Descargar el ZIP actualizado desde el panel Archivos sin interrumpir la inferencia y conservarlo como snapshot nuevo. GitHub contiene lo descargado; **no contiene automáticamente el progreso posterior que solo está en la máquina temporal de Colab**.

Si se perdió la sesión de Colab, auditar el último ZIP y revisar el procedimiento de restauración de sus fuentes y checkpoints antes de iniciar otra T4. Conservar identidad/configuración exactas para reanudar; no presentar llamadas recuperadas como inferencias nuevas. No sobrescribir ni reemplazar respuestas fallidas por intentos favorables.

Al completar 300/300: auditar, extraer en una carpeta nueva, evaluar todas las respuestas con la misma pauta D2 y registrar motivos y hashes. Comparar las seis condiciones, incluyendo errores, regresiones, costes y paradas. La aceptación del auditor interno no es un acierto externo y las preguntas son de desarrollo, no una prueba de generalización.

Actualizar el informe de una página A4 vertical con resultados verificados, grafo de todos los agentes y herramientas, decisiones, ciclos y paradas, técnicas, ablaciones y limitaciones. Compilar y revisar visualmente. Ajustar el guion y grabar una demostración real de pantalla de hasta tres minutos con entradas, mensajes intermedios y salida; verificar el enlace abierto. Un guion o una transcripción no sustituyen ese video.

Publicar cambios pertinentes en `origin` (`Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1`), preservando cambios ajenos, sin secretos ni push forzado. Mantener actualizado el estado y no declarar terminada la entrega mientras falten resultados, evaluación, PDF final o video real con enlace.

## Límites del traspaso

Un modelo con acceso de lectura al repositorio puede analizar código, trazas y borradores. Para continuar la ejecución o publicar cambios necesita acceso efectivo a Colab o a una GPU y permisos de escritura correspondientes; el enlace del repositorio por sí solo no proporciona esos accesos. No compartir contraseñas ni tokens en el chat o el repositorio.
