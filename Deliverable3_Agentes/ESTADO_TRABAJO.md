# Estado de trabajo de Deliverable 3

Actualizado el 27-10-2026, tarde de Chile. Autorización vigente: correcciones, inferencia real en Colab T4, descarga y evaluación de todos los intentos, informe LaTeX, guion/video y actualización de GitHub. No usar el prototipo `../Deliverable3/` ni `backup/deliverable3` como implementación. No enviar mensajes a terceros.

## Operación en curso

**Lote completo v4 en ejecución (50 preguntas × seis condiciones):** comenzó en la misma T4 tras conservar y evaluar el piloto v4. Se activó únicamente `EJECUTAR_LOTE = True` en la sección 6. Se observó `P01 baseline_directo: ejecutando`. Se solicitó ejecutar la sección 8 de exportación mientras el lote está activo; su salida quedó pendiente. No recargar, desconectar, volver a ejecutar todo ni cambiar fuentes/configuración.

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

1. Vigilar el lote completo activo y descargar snapshots desde Archivos, sin interrumpirlo. Recoger la descarga final (posiblemente `resultados_d3_todas_las_corridas.zip`, contenedor con piloto y lote separados). Auditar cada ZIP interno y conservar originales en carpetas nuevas.
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
