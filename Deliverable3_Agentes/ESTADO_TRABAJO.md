# Estado de trabajo de Deliverable 3

Actualizado el 28-10-2026, tras auditar la última descarga. Autorización vigente: correcciones, inferencia real en Colab T4, descarga y evaluación de todos los intentos, informe LaTeX, guion/video y actualización de GitHub. No usar el prototipo `../Deliverable3/` ni `backup/deliverable3` como implementación. No enviar mensajes a terceros.

## Autorización vigente del 29-10

El usuario respondió «haz lo que sea mejor» a la pregunta explícita de conexión de Drive y acceso/modificación de archivos. Se eligió Drive para persistencia: autorización concedida para conectar este notebook y guardar `GenIA_D3_Agentes/runs`. No volver a pedir el mismo permiso. El primer intento de montaje terminó en `ValueError: mount failed` mientras esperaba la respuesta. Se reejecutó la celda 6 y se aceptó Conectar con Google Drive. Se completaron los pasos Continuar de dos ventanas OAuth de Google Drive for desktop para la cuenta ya seleccionada. Tras cerrarse las ventanas, la herramienta de Safari devolvió repetidamente `noWindowsAvailable` y `timeoutReached`, incluso después de restablecer cua_repl. El inventario confirma Safari abierto, pero todavía no se pudo leer la salida del montaje/modelo. Se pidió al usuario dejar visible la pestaña de Colab; NO pedir de nuevo autorización de Drive. Aún no declarar Drive montado ni inferencia iniciada hasta verificarlo en pantalla. No cerrar/reiniciar Safari ni recargar Colab para intentar resolver el control.

## Última comprobación: 28-10 por la noche (Chile)

El usuario confirmó continuar hasta 300. La sesión de la mañana ya no estaba accesible: Colab mostró «No hay sesiones activas», y Descargas sigue sin ZIP posterior a 39/300. No afirmar que sigue corriendo el bloque de las 10:18. Se reactivó el seguimiento, encontrado nuevamente PAUSED.

Se abrió en Safari el cuaderno por bloques publicado:
https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/4f744885179b764c93dacec9cbf3dc8cb17f857d/Deliverable3_Agentes/Deliverable3_Agentes_Bloques_Colab.ipynb

Dependencias y fuentes restauradas. La celda 6 se preparó para montar Drive y guardar en `MyDrive/GenIA_D3_Agentes/runs`; Google muestra el diálogo de permiso para acceder/modificar archivos de Drive. **Nota histórica: en este punto todavía se esperaba autorización; fue concedida el 29-10 como se indica arriba.** El modelo y el bloque no han arrancado en esta nueva sesión porque el montaje está esperando el diálogo. Las observaciones anteriores de ejecución son históricas.

`operacion/importar_snapshot_lote.py` permite auditar y preservar cada nuevo ZIP sin sobrescribir, verificando configuración congelada y respuestas previas byte a byte. Validado con el avance real 35→39 y el rechazo del retroceso.

Trabajo independiente del 29-10: `entrega/mensajes_reales_v4.md` conserva 14 eventos exactos de P05 y P41 del piloto congelado, con hashes y enlaces. `guion_video.md` ya narra v4: P05 sin loop y P41 con lectura/inventario y parada a 12 llamadas; elimina la narración antigua de v2. Sigue siendo ensayo pendiente del lote completo y de video real. El diálogo de Drive continúa sin autorización; no se ha aceptado ni iniciado inferencia en la nueva sesión.

## Plan por bloques y ejecución anterior

**28-10-2026, nueva decisión del usuario: ejecutar diez bloques de 30 respuestas.** Son cinco preguntas × seis condiciones por bloque, manteniendo el total de 50×6=300. No son diez experimentos distintos: se conserva la identidad `agentes_99b9b55bd79d4572f743` y el sistema v4 congelado.

El usuario informó otra cancelación. Se revisaron Descargas y las sesiones activas de Colab: la sesión visible únicamente contenía `.config` y `sample_data`; no apareció otra sesión recuperable. Último respaldo real auditado: **39/300**, `resultados/lote_99b9b55bd79d4572f743/snapshots/20261028T071051Z_039de300.zip`. No hay evidencia disponible de respuestas posteriores. Primer bloque completo; segundo con 9/30 respuestas, faltan 21 hasta 60/300.

Se preparó `operacion/reanudar_lote_v4_colab.py` para restaurar las 39 respuestas y ejecutar únicamente hasta el siguiente múltiplo de 30. La capa operativa detiene después de exportar una respuesta completa; no modifica código experimental, prompts, semillas, configuración ni orden de variantes. Solicita una descarga inmutable cada seis respuestas nuevas y al cerrar el bloque. Cuatro pruebas de orquestación verificadas; no son inferencia real.

**BLOQUE 2 EN EJECUCIÓN, verificado el 28-10 a las 10:18 Chile (13:18 UTC).** Se ejecutaron solo dependencias, fuentes y carga Qwen/E5. La celda 12 ahora descarga el lanzador operativo del commit `4f744885179b764c93dacec9cbf3dc8cb17f857d` y verifica SHA-256 `be06ae414dd35aeacd7ebc7f7a577f6544007875b00215f206847203def07889`. La salida confirmó «BLOQUE 2/10: 39/300 conservadas; objetivo 60/300», las 39 respuestas omitidas y `P07 sin_descomposicion: ejecutando`. Configuración y fuentes idénticas verificadas antes de inferir. No ejecutar piloto ni lote continuo; no recargar ni detener la celda activa. Al completar cada bloque: recoger ZIP, auditar integridad/configuración/respuestas previas, publicar respaldo y actualizar el estado; después ejecutar el siguiente bloque con el mismo modelo cargado. Si se pierde la sesión, actualizar URL/hash/cantidad del respaldo a la copia más reciente antes de restaurar.

La automatización estaba PAUSADA al revisarla en este turno; se reactivó a ACTIVE y se actualizó su instrucción para recoger/auditar/publicar cada bloque antes del siguiente.

Nuevo cuaderno reproducible: `Deliverable3_Agentes_Bloques_Colab.ipynb`, generado por `operacion/crear_cuaderno_bloques.py`; conserva byte a byte el payload de fuentes del cuaderno v4. Usar el nuevo cuaderno solo en una sesión nueva; la pestaña existente recibirá la misma celda de operación sin recargarla.

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

1. Ejecutar y recoger un bloque de 30 respuestas por vez como se indica arriba. Auditar y preservar las 39 respuestas previas byte a byte. No repetir preparación ni inferencia mientras esté activo.
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

P06 revisada en las seis condiciones y guardada en `evaluacion_progresiva/snapshot_039_p06/`: **36 respuestas revisadas externamente** (P01–P06), sin métricas finales. El lote seguía ejecutándose en la revisión de este turno. Próximo bloque de evaluación: P07 en adelante a partir de nuevos snapshots.
