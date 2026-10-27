# Comprobación frente al enunciado oficial

Fuente: `Deliverables/Deliverable 3 (1).pdf`, fuera de este repositorio, revisada el 27-10-2026. Fecha de entrega: **31-10-2026, 23:59**. Esta tabla distingue implementación, evidencia parcial y requisitos pendientes.

| Requisito | Evidencia actual | Estado / cierre necesario |
|---|---|---|
| Misma tarea y fallo de D1/D2 | Corpus y controles D2, problemas de omisión/citas; README, EVALUACION.md | Implementado; no confundir diagnóstico con mejora demostrada. |
| Al menos tres agentes con decisiones | Investigador, redactor y auditor; roles, entradas/salidas y acciones documentados; trazas v1/v2 | Implementado y ejecutado en T4. cuatro pilotos evaluados; lote completo en ejecución. |
| Un modelo abierto de hasta 8B | Qwen3-4B fijado por revisión; una instancia compartida, E5 como recuperación | Verificado en pilotos reales. |
| Prompts propios fuera del código y versionados | `prompts/*.txt`, fuentes congeladas y commit GitHub | Publicado; conservar versión exacta de cada corrida. |
| Técnicas identificadas y ablaciones individuales | Descomposición, completitud y verificación; tres variantes sin un bloque | Implementadas; faltan ejecuciones y evaluación. |
| Mismos inputs y criterio para seis condiciones | Lote de 50 × 6 previsto, pauta externa D2 con hashes | **Pendiente:** generar/evaluar 300 respuestas. Los pilotos cubren solo cuatro inputs × tres condiciones por versión. |
| Evidencia de mejora, con fallos | v1: 0/4; v2/v3/v4: 1/4; D2: 2/4 en los cuatro | **No se ha demostrado mejora.** Reportar el resultado final aunque sea inferior, sin seleccionar intentos favorables. |
| Mensajes de cada entrada y trazas de fallos/video | JSON de todos los pilotos; P41 preserva regresión; transcripciones enlazadas | Pilotos completos. Añadir trazas exactas de la grabación final y lote. |
| Grafo: agentes, herramientas, handoffs, loops y stops | Grafo TikZ en `main.tex`, herramientas como nodos, mensajes y retornos rotulados | Borrador compilado y revisado; revalidar tras congelar versión final. |
| PDF LaTeX de una página vertical | `main.pdf`, A4 de una página, fuente `main.tex` | Formato verificado; **contenido final pendiente** de resultados y enlace. |
| Video real ≤ 3 min, mensajes y salida visibles | Guion de ensayo y mensajes reales | **Pendiente:** grabación, archivo, duración comprobada y enlace abierto. |
| Repositorio reproducible y enlace funcional | Commit `553944b491291aa862544925361926450eea982d` publicado en origin; notebook abierto desde GitHub en Colab | Código/pilotos publicados. Actualizar guía para reproducir exactamente el video final. |

## Estado operativo actual

El bloqueo de pantalla nocturno se resolvió tras «continúa». El ZIP v3 se descargó, auditó y evaluó sin sobrescribir los anteriores. Se inició un piloto v4 desde el commit `de2951b22214f294e9f9eb1f5b0fae9a25c622da`; se observó T4 conectada y carga de modelos iniciada. El piloto v4 fue evaluado (1/4 estricto de agentes). El lote 50 × 6 está en ejecución con la misma versión congelada. Consultar `../ESTADO_TRABAJO.md` para la pestaña y el próximo paso.
