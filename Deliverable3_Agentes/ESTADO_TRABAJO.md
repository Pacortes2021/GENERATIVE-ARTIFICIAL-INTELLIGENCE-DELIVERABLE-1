# Estado de trabajo de Deliverable 3

Actualizado el 28-10-2026, tras auditar la última descarga. Autorización vigente: correcciones, inferencia real en Colab T4, descarga y evaluación de todos los intentos, informe LaTeX, guion/video y actualización de GitHub. No usar el prototipo `../Deliverable3/` ni `backup/deliverable3` como implementación. No enviar mensajes a terceros.

## Operación en curso


**LOTE REAL REANUDADO el 28-10-2026 aproximadamente a las 04:00 Chile (07:00 UTC).** Esta es la observación vigente; el diagnóstico de interrupción más abajo es histórico. Se ejecutaron únicamente preparación, restauración de fuentes y carga de Qwen en T4, sin piloto. La sección 6/celda 12 fue reemplazada por la celda de `operacion/reanudar_lote_v4_colab.py`: descarga el snapshot publicado de 35/300 por URL de commit y SHA-256, audita, exige configuración idéntica y restaura resultados/checkpoints. La primera comprobación encontró una diferencia de serialización JSON de la configuración; se corrigió la comparación a contenido sellado equivalente, sin cambiar el sistema experimental ni sus parámetros.

Se verificó visualmente «LOTE REAL: 50 preguntas x 6 condiciones», las 35 respuestas conservadas y **`P06 sin_completitud: ejecutando`**. Misma corrida `agentes_99b9b55bd79d4572f743`, mismo código, prompts, corpus, índice, inferencia y límites. No interrumpir, recargar ni pulsar Ejecutar todo. El programa exporta el ZIP tras cada respuesta y la celda solicita descarga al finalizar o ante excepción. Sigue en almacenamiento temporal `/content/d3_agentes_runs`; Drive no está montado. La copia `agentes_99b9b55bd79d4572f743-3.zip` descargada al comienzo todavía conserva 35/300 (se exporta al completar cada respuesta); no representa nuevas respuestas completas.

La automatización se encontró PAUSADA y se reactivó mediante herramienta tras la orden «corramos el código real». Ahora está ACTIVA cada cinco minutos. Próximo paso: vigilar esta ejecución, descargar y auditar el ZIP cuando avance, conservando originales y sin reinferir resultados previos. La salida AX se trunca a 500 caracteres; para ver la última línea, hacer clic en el encabezado de la sección 7 y mirar screenshot: desplaza al final de la salida de la sección 6 sin ejecutarla.

Última copia auditada tras reanudar: **39/300**, `resultados/lote_99b9b55bd79d4572f743/snapshots/20261028T071051Z_039de300.zip`. Captura UTC 20261028T071051Z; misma configuración completa y las 35 respuestas previas intactas byte a byte. Se observó P07 sin_descomposicion ejecutando; sin fallo técnico visible.

### Diagnóstico anterior a la reanudación

**El lote ya no está activo en la sesión visible. Último respaldo verificable: 35/300.** El 28 de octubre se auditó `agentes_6a4e8925ada1fa3d1dee-2.zip`, descargado el día 27 a las 19:24 Chile: es otra ejecución del piloto, 12/12 (P05/P25/P38/P41 × tres condiciones), no el lote 50×6. Conservado aparte en `resultados/piloto_6a4e8925ada1fa3d1dee_repeticion_20261027T2210/`. Sus 12 respuestas finales coinciden textualmente con las del piloto previo, pero las trazas y tiempos son nuevos. No sobrescribir ni sumar intentos.

La interfaz actual muestra `EJECUTAR_LOTE = False` y «Lote desactivado; no se han generado resultados de ablaciones». Estaba desconectada; se pulsó Reconectar para buscar archivos. El entorno conectado muestra únicamente `sample_data`, sin `d3_agentes_runs`: no se encontró allí el lote anterior. No se ejecutaron nuevas inferencias en esta revisión. La fecha y causa exactas de la pérdida/interrupción no están demostradas. El lote anterior sí existió y su snapshot de 35 respuestas está auditado y publicado.

**Próximo paso:** restaurar el snapshot de 35/300 en una T4 y verificar configuración/fuentes/checkpoints idénticos antes de reanudar el lote, sin repetir el piloto. Preparar respaldo persistente para no depender solo del almacenamiento temporal. No usar «Ejecutar todo» con los valores por defecto, pues solo ejecuta el piloto. No se contrató otra GPU; el usuario no ha aprobado ningún gasto.

El piloto v4 `agentes_6a4e8925ada1fa3d1dee.zip` está conservado y auditado en `resultados/piloto_6a4e8925ada1fa3d1dee`, con evaluación completa: agentes 1/4, D2 2/4, baseline 0/4. Ver `CONGELACION_V4.md`: se congela el sistema para medirlo completo, incluidos los fallos residuales del modelo.

Pestaña actual, versión congelada:
https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/de2951b22214f294e9f9eb1f5b0fae9a25c622da/Deliverable3_Agentes/Deliverable3_Agentes_Colab.ipynb

Código v4 publicado en `de2951b22214f294e9f9eb1f5b0fae9a25c622da`, paquete 0.4.0, protocolo `d3-agentes-desde-cero-v4`. 38 pruebas aprobadas; 700 prompts medidos con E5 y tokenizador Qwen reales, máximo 3.926 tokens de entrada. No se ejecuta inferencia Qwen en el Mac.

Automatización `seguimiento-nocturno-del-piloto-d3`, nombre «Completar Deliverable 3»: **ACTIVA**, cada cinco minutos. Se reactivó tras «continúa» del usuario. El bloqueo de pantalla anterior está resuelto. No cambiar sus permisos ni crear un duplicado.

## Corridas conservadas y evaluadas

| Versión | Carpeta bajo `resultados/` | Baseline | D2 | Agentes |
|---|---|---:|---:|---:|
| v1 | `piloto_222681994dcd692c0600` | 0/4 | 2/4 | 0/4 |
| v2 | `piloto_14f5ffa72e8a2734d481` | 0/4 | 2/4 | 1/4 |
| v3 | `piloto_9b826dfab6be77ac0ce1` | 0/4 | 2/4 | 1/4 |
| v4 | `piloto_6a4e8925ada1fa3d1dee` | 0/4 | 2/4 | 1/4 |

ZIP originales intactos y extracciones byte a byte; juicios externos independientes con la pauta D2. Leer REPORTE.md de cada corrida. V3 redujo generación de agentes de 1.453,74 s a 380,05 s, sin mejorar exactitud. P05 es correcta: revisar RG 3.10 **completo**, que sí contempla Memoria; no juzgar solo el extracto incompleto del auditor. P25 omite desarrollar remisiones; P38 carece de respaldo del alcance específico; P41 termina por formato pese al inventario de ausencia. No copiar etiquetas al evaluar v4.

V4 acepta exclusivamente una forma plana equivalente de solicitud explícita de herramienta, conserva argumentos y validadores, precisa IDs de citas y refuerza los tres bloques experimentales. No contiene respuestas de referencia ni rutas por pregunta. El piloto v4 está evaluado; la comparación completa sigue pendiente.

## Siguiente secuencia

1. Vigilar el lote reanudado descrito arriba. Descargar snapshots del ZIP actualizado, auditar y preservar los 35 resultados previos byte a byte. No repetir preparación ni inferencia mientras esté activo.
2. Mantener la versión congelada. No hacer más ajustes antes de terminar las 300 respuestas y su evaluación. Reportar si no supera D2; no reemplazar fallos por otros intentos.
3. El programa guarda checkpoints por llamada y actualiza ZIP después de cada respuesta. Durante el lote largo descargar snapshots del ZIP desde Archivos sin interrumpir la ejecución; conservar cada descarga. El almacenamiento temporal de Colab desaparece al terminar la sesión. Drive solo si se logra autorizar de manera apropiada.
4. Evaluar las 300 respuestas externamente y reportar aciertos, regresiones, coste, errores de formato, paradas y cada ablación. Son preguntas de desarrollo, no generalización.
5. Cerrar informe LaTeX y recompilar `entrega/main.tex` → `main.pdf` (una página A4 vertical). El borrador ya contiene pilotos v1/v2/v3 y grafo de agentes/herramientas, decisiones, loops y stops; sigue marcado como incompleto.
6. Ajustar `entrega/guion_video.md` a la versión final. Grabar un video real de pantalla ≤ 3 min con entradas, mensajes y salida; publicar/verificar enlace abierto autorizado. Guion y transcripciones no sustituyen el video. Conservar sus trazas exactas y explicar reproducción.
7. Actualizar GitHub `origin` Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1, sin tocar `upstream`, sin force push y sin incorporar `../Deliverable3/` ajeno. La entrega sigue incompleta.

## Detalles operativos

- El antiguo notebook de Drive `1Y69nHfh0KW6YoIJyDuFVHvCvblxFvRTQ` tuvo conflicto de guardado. No sobrescribir su versión remota. Sus pilotos ya están conservados.
- Abrir desde GitHub evita el selector de subida de Safari que dejaba Cargar desactivado. El aviso normal de Colab «Google no creó este notebook» corresponde al código propio publicado.
- Para UI usar cua_repl. Si el usuario cambia de pestaña, volver a leer el estado antes de actuar. Si el Mac se bloquea, no intentar eludirlo; completar trabajo independiente y explicar el impedimento.
- gh autentica correctamente con acceso de red. Un aviso de token inválido sin red no justifica pedir nuevas credenciales. Las mutaciones de Git/red pueden requerir la aprobación automática de la herramienta.
- LaTeX local: `tectonic` requiere ejecución con acceso de red del entorno; el editor integrado también compila. Revisar `pdfinfo` y render PNG tras cambios.

## Snapshot y operación del lote

Identidad activa: `agentes_99b9b55bd79d4572f743`. Ruta Colab `/content/d3_agentes_runs/agentes_99b9b55bd79d4572f743.zip`. Primera copia descargada y auditada a las 14:48 de Chile: **12/300 respuestas**, 2 por condición. Coinciden fuentes, prompts, inferencia y límites con el piloto v4. Guardada en `resultados/lote_99b9b55bd79d4572f743/snapshots/20261027T174824Z_012de300.zip` y metadata JSON. No preparar métricas de exactitud final aún.

Para próximos snapshots (aproximadamente cada 30 minutos o ante riesgo real de desconexión): en la pestaña v4, panel Archivos → seleccionar `d3_agentes_runs` → tecla Right para expandir (doble clic no abrió de forma estable) → clic derecho en `agentes_99b9b55bd79d4572f743.zip` → Descargar. Guardar el nuevo ZIP en una ruta de snapshot distinta, auditar y registrar cuántas respuestas conserva. Safari puede agregar sufijos `(1)`, `(2)`; no asumir que el nombre sin sufijo es la copia más reciente. No interrumpir la celda activa.

La salida de Colab puede verse vieja en AX hasta pulsar «Enfocar la última celda ejecutada»; el botón solo muestra la celda y no la reinicia. Si el usuario cambia de pestaña, volver a leer el estado y seleccionar la pestaña v4 por su URL, no actuar sobre índices viejos. La última salida observada antes del snapshot llegó a P03.

Evaluación progresiva independiente iniciada con el snapshot de 12 respuestas: `resultados/lote_99b9b55bd79d4572f743/evaluacion_progresiva/snapshot_012/` contiene P01 y P02 revisadas en las seis condiciones, con paquetes y veredictos validados por el evaluador D2. No se calcularon métricas finales. Al integrar en las 300 respuestas, comprobar correspondencia exacta de hashes de respuesta, pregunta, corpus, pauta y referencias; no tomar etiquetas de pilotos o D1/D2. Ver el README de evaluación progresiva. Esto permite avanzar sin modificar ni interrumpir la corrida activa.

Nueva copia auditada 20261027T182649Z: **35/300 respuestas**, archivo `resultados/lote_99b9b55bd79d4572f743/snapshots/20261027T182649Z_035de300.zip`. La ejecución sigue activa en P06; inferencia y fuentes coinciden con v4 congelada. El ritmo observado a los 50 minutos proyectaba unas 7–8 horas totales, estimación no garantizada. Evaluar progresivamente las respuestas nuevas sin duplicar P01/P02 ya juzgadas.

Evaluación progresiva ampliada: `evaluacion_progresiva/snapshot_039_p03_p05/` añade 18 juicios validados de P03–P05 en seis condiciones. Con P01/P02, hay 30 respuestas de este lote revisadas externamente; no son métricas finales. Fuentes adicionales completas y hashes de procedencia conservados.
