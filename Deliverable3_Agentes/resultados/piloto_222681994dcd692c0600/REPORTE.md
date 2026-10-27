# Primer piloto real de D3: ejecución completa, agentes sin aciertos

Revisión: 27 de octubre de 2026. Archivo recibido desde Descargas: `agentes_222681994dcd692c0600.zip`.

**La ejecución y la descarga funcionaron. El sistema de agentes no mejoró D2 en este piloto: produjo cuatro respuestas finales de falta de validación y ninguna respuesta correcta. D2 resolvió dos de los cuatro casos.** No corresponde ejecutar todavía el lote completo para presentar una mejora; primero hay que corregir el comportamiento observado y repetir el piloto conservando esta evidencia.

## Integridad y configuración

- ZIP original conservado, SHA-256 `b77f56a84e823bf641541c34fa353858de670ff4b207bb9b56230207e32f5937`.
- Auditoría de manifiesto, archivos congelados, prompts, checkpoints y correspondencia CSV/JSON aprobada.
- 12 respuestas finales guardadas de 12 esperadas; cuatro preguntas en tres condiciones. No hay ablaciones en esta corrida.
- La configuración registra Tesla T4, Qwen3-4B, revisión `1cfa9a7208912126459214e8b04321603b3df60c`, NF4, cómputo configurado en `torch.bfloat16`, muestreo a temperatura 0,7 y modo sin thinking.
- Los hashes de los fuentes de inferencia y prompts coinciden con la implementación local inspeccionada. No se ejecutó el código contenido en el ZIP para hacer esta revisión.
- 45 llamadas al modelo: 4 baseline, 4 D2 y 37 agentes. Ninguna salida aparece cortada por el límite de tokens. No hay eventos `error_tecnico` en los diarios conservados.

La completitud técnica significa que todas las condiciones terminaron y guardaron sus respuestas, incluidas las respuestas de fallo. No significa que los agentes resolvieran las consultas.

## Evaluación externa al controlador

Se revisaron las doce respuestas finales con la pauta D2, sus referencias y las fuentes adicionales pertinentes. Modalidad: revisión asistida por Codex en este chat, identificada en cada archivo de veredictos. Se calificaron las respuestas finales, no las afirmaciones favorables de un borrador intermedio.

| Caso | Baseline | RAG D2 | Agentes completos |
|---|---|---|---|
| P05 · Actividad final de titulación | Incorrecta: dato/cita no respaldados | Correcta: Memoria de Título, RI-FI art. 29 | Incorrecta: termina sin validar respuesta |
| P25 · Asignaturas que no se pueden eliminar | Incorrecta: inventa una autorización | Incorrecta: no desarrolla prioridades a) y b) | Incorrecta: termina por salidas inválidas |
| P38 · Aplicabilidad y nota de aprobación | Incorrecta: niega aplicación y responde 3,0 | Incorrecta: cita art. 6 para aplicabilidad | Incorrecta: agota llamadas sin responder |
| P41 · Artículo 90 inexistente | Incorrecta: inventa contenido | Correcta: comprueba ausencia con inventario | Incorrecta: termina por límite, sin negar inequívocamente la premisa |
| **Total del piloto** | **0/4** | **2/4** | **0/4** |

Las regresiones respecto de D2 son P05 y P41; no hubo casos corregidos. La salida final de P41 dice que no obtuvo validación y que eso no demuestra ausencia. Esa frase no equivale a responder que el art. 90 no existe en la copia, por lo que no se cuenta como abstención correcta.

Las preguntas se eligieron para diagnóstico, no por muestreo representativo. El 2/4 de D2 no sustituye su 40/50 histórico; el 0/4 de agentes describe únicamente este piloto. No permite estimar exactitud general ni efectos de técnicas sin ejecutar las ablaciones.

## Qué muestran las trazas

### 1. Contrato JSON difícil de seguir y errores poco orientadores

En la primera llamada de P05, P25 y P41, el investigador devuelve `accion: "buscar_normativa"` y una solicitud de herramienta bien identificada. El contrato exige `accion: "herramienta"`, así que el controlador rechaza esas tres salidas. No es un error del navegador ni de la T4.

En P25 aparecen otros dos rechazos porque el investigador omite la clave `herramienta` al elegir `redactar`, aunque el contrato exige incluirla con valor `null`. La segunda de esas salidas ya identifica las asignaturas atrasadas y las obligatorias reprobadas: es un mensaje intermedio, no una respuesta final válida del sistema. El modelo nunca llega al redactor en ese caso.

De las 37 llamadas de agentes, siete salidas se rechazan: tres por acción no permitida, dos por claves del contrato y dos por apoyar afirmaciones en una fuente que no se recibió. Estas dos últimas son fallos de fundamentación, no simples errores de formato.

### 2. Transferencia al redactor sin evidencia

P05 no ejecuta ninguna herramienta. Después del primer rechazo, el investigador transfiere un texto no respaldado al redactor con el inventario de evidencia vacío. El redactor inventa contenido y cita `RG-ART-015`. El auditor detecta la falta de fuente algunas veces, pero también intenta aceptar usando como extracto el mismo contenido inventado. Los controles impiden la aceptación; la respuesta final sigue siendo una omisión de la información solicitada.

En P41 también se redacta inicialmente sin haber consultado el corpus. El sistema conserva ese borrador inventado durante las revisiones posteriores.

### 3. Recuperación insuficiente y ciclo que no vuelve a investigar

P38 realiza una sola búsqueda, con una reformulación distinta de la pregunta original. Obtiene cinco filas del anexo de equivalencia de notas y ningún artículo sobre aplicabilidad o aprobación. El investigador interpreta una equivalencia 58/4,4 como nota de aprobación y el redactor la repite.

El auditor pide correcciones cinco veces, pero no solicita investigación adicional. Además introduce una exigencia que no estaba en la pregunta: comprobar si la escala se aplica **exclusivamente** a Ingeniería. Se consumen las doce llamadas entre reformulaciones del borrador, sin recuperar la evidencia pertinente.

### 4. La evidencia nueva no corrige el borrador previo

En P41 sí se llega a consultar `leer_articulo(RI-FI, 90)`. La herramienta devuelve el inventario completo y declara que ese artículo ordinario no figura. El investigador comunica correctamente su ausencia en una transferencia; el redactor, sin embargo, repite el borrador que inventaba contenidos del artículo 90.

Después se consulta también `inventario(RI-FI)`. Aun con esa evidencia, los mensajes vuelven a atribuir contenido al artículo inexistente y se agota el presupuesto. Este comportamiento es compatible con una dependencia excesiva del borrador previo, pero la traza no demuestra el mecanismo interno del modelo.

## Costos observados

| Condición | Llamadas en cuatro casos | Tiempo total de generación | Media por pregunta |
|---|---:|---:|---:|
| Baseline | 4 | 36,53 s | 9,13 s |
| RAG D2 | 4 | 69,21 s | 17,30 s |
| Agentes | 37 | 774,32 s | 193,58 s |

Los agentes consumen aproximadamente 11,2 veces el tiempo de generación de D2 en este piloto, sin aciertos adicionales. Los tiempos excluyen carga inicial y recuperación; son las duraciones de generación registradas. Las 45 llamadas aparecen como nuevas en este intento, no como checkpoints reutilizados.

| Caso de agentes | Llamadas | Herramientas | Salidas inválidas | Estado final |
|---|---:|---:|---:|---|
| P05 | 9 | 0 | 3 | `limite_salidas_invalidas` |
| P25 | 4 | 1 | 3 | `limite_salidas_invalidas` |
| P38 | 12 | 1 | 0 | `limite_llamadas` |
| P41 | 12 | 2 | 1 | `limite_llamadas` |

## Correcciones prioritarias para una siguiente versión

1. Simplificar y precisar el contrato de acciones del investigador y la retroalimentación de errores. Probar acciones y campos por rama sin transformar decisiones ambiguas del modelo en órdenes ejecutables ni relajar los controles de fuentes.
2. Impedir la entrega de una respuesta factual a partir de evidencia vacía. Evaluar entregar al investigador la recuperación inicial original de D2 como punto de partida, dejando que decida si necesita nuevas herramientas. Esto preservaría los recursos de D2; es una hipótesis de desarrollo, no una mejora ya medida.
3. Distinguir en la auditoría «hay evidencia, falta redactar» de «falta evidencia, hay que investigar». Evitar ciclos de corrección sobre la misma evidencia insuficiente y mantener la pregunta original, sin añadir exigencias de exclusividad.
4. Exigir que el redactor vuelva a contrastar el borrador con las nuevas fuentes y pueda descartar afirmaciones contradichas por el inventario. No tratar mensajes de otros agentes o borradores anteriores como fuentes normativas.
5. Repetir estos cuatro casos antes de lanzar las 50 preguntas y las ablaciones. Aumentar el presupuesto de llamadas, por sí solo, prolongaría los ciclos observados y no está justificado por esta evidencia.

Estas correcciones están propuestas; esta revisión no modificó agentes, prompts ni los resultados originales. Los tests anteriores verificaron flujos con modelos simulados y tokenización real; no podían garantizar que Qwen siguiera los contratos ni que sus decisiones fueran acertadas. Este piloto identifica precisamente esas limitaciones.

## Artefactos conservados

- [ZIP original](agentes_222681994dcd692c0600.zip) y [registro de importación](importacion.json).
- [Configuración original](original/configuracion.json) y [resultados/trazas por pregunta](original/resultados/).
- [Comparación evaluada](comparacion_evaluada.json).
- [Veredictos baseline](evaluacion/baseline_directo/veredictos.json), [D2](evaluacion/rag_d2/veredictos.json) y [agentes](evaluacion/agentes_completo/veredictos.json), con hashes y motivos de las doce decisiones.
