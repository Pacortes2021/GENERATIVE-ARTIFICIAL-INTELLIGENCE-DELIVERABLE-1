# Protocolo experimental D3 nuevo

## Hipótesis

La investigación dirigida, una redacción que explicita remisiones/condiciones y una auditoría con revisión pueden corregir errores documentados de D2. Pueden también empeorar respuestas correctas o aumentar abstenciones. No se presupone mejora ni se usan las decisiones del auditor como etiquetas de exactitud.

La tarea, corpus y pauta se mantienen respecto de D2. Las 50 preguntas son desarrollo: se utilizaron al diseñar la solución. Un conjunto nuevo, con referencias verificadas y reservado antes de ajustar prompts, sería necesario para estudiar generalización; no se presenta como requisito adicional del enunciado.

## Condiciones

| Condición | Intervención |
|---|---|
| `baseline_directo` | Prompt de D1 sin documentos, con inferencia emparejada D2. |
| `rag_d2` | Recuperación y prompt estructurado de D2, sin agentes. |
| `agentes_completo` | Los tres roles y los tres bloques experimentales de prompting. |
| `sin_descomposicion` | Se retira únicamente `prompts/descomposicion.txt`. |
| `sin_completitud` | Se retira únicamente `prompts/completitud.txt`. |
| `sin_verificacion` | Se retira únicamente `prompts/verificacion.txt`. |

Las versiones, pesos, cuantización, parámetros, corpus y entradas deben coincidir. Baseline y D2 comparten semilla por pregunta. Completo y ablaciones comparten semilla por pregunta/agente/número de visita; al cambiar decisiones pueden cambiar la cantidad y la secuencia de llamadas. El orden de las condiciones rota por pregunta. No seleccionar una semilla por su mejor resultado.

Las ablaciones miden contribuciones locales de instrucciones dentro de un sistema con componentes redundantes. No aíslan todo el costo de coordinación ni eliminan capacidades implícitas del modelo. Las interfaces JSON son un contrato operativo común y no se presentan como una cuarta técnica evaluada.

## Piloto y congelación

La versión v2 se ajustó con los fallos del piloto v1, que permanece intacto. Todas las condiciones de agentes parten ahora de una búsqueda D2 con el texto original, incluida dentro de las seis consultas; mantienen los mismos controles de formato, fuentes y repetición. Las ablaciones retiran únicamente el bloque de prompting indicado. No combinar resultados v1/v2 ni copiar sus veredictos. La comparación de calidad v2 requiere otra corrida y evaluación externa completa.

1. Ejecutar P05, P25, P38 y P41 en baseline/D2/completo. Verificar que realmente se generan decisiones de los tres roles, que las herramientas operan y que las salidas JSON son utilizables.
2. Conservar todas las trazas, errores y regresiones. Ajustar durante desarrollo si hace falta; no sumar intentos selectivamente a un resultado final.
3. Congelar código, prompts, pauta y semilla antes del lote de seis condiciones. El ZIP incluye fuentes y hashes; publicar esa versión en Git antes de entregar.
4. Ejecutar las 50 preguntas en todas las condiciones. Reanudar si es necesario, sin sustituir fallos semánticos por ejecuciones elegidas a posteriori.
5. Auditar el ZIP y confirmar la completitud técnica antes de calcular exactitud.

## Calificar externamente

Descomprimir el ZIP en una carpeta nueva. Los comandos siguientes se ejecutan desde la raíz del repositorio; reemplazar las rutas de ejemplo:

```bash
python3 Deliverable3_Agentes/evaluar.py preparar --corrida /ruta/a/corrida --evaluaciones /ruta/nueva/juicios
```

Se usa el evaluador de D2 para preparar una carpeta por condición. `correcta` comienza en `null`; no hay calificación por palabras clave ni por aprobación interna. Revisar respuesta, evidencia y pauta, registrar un motivo por juicio e identificar al evaluador y modalidad (`humana`, `revision_asistida_chat` o `api`). Las etiquetas de corridas históricas no se copian a respuestas nuevas.

```bash
python3 Deliverable3_Agentes/evaluar.py comparar --corrida /ruta/a/corrida --evaluaciones /ruta/nueva/juicios --informe /ruta/nueva/comparacion.json
```

El comparador rechaza juicios pendientes, CSV alterados, preguntas distintas, referencias diferentes o respuestas sustituidas. Entrega exactitud por condición y casos acertados solo por el sistema completo o por su comparador. Una abstención innecesaria también puede ser una regresión.

La pauta existente reconoce las preguntas originales. Las consultas nuevas requieren referencias y evaluación propias antes de producir porcentajes. Si se corrige la pauta, aplicar la misma versión a todas las condiciones y documentar la razón.

## Reportar y cerrar

- Exactitud estricta, tamaño del conjunto y modalidad de evaluación.
- Diferencia completo–D2 y completo–cada ablación; mostrar también regresiones.
- Cantidad de llamadas, tokens, tiempo, JSON inválido, límites alcanzados y aceptación interna equivocada.
- Un caso de mejora si existe y un fallo real con sus trazas. No afirmar que el sistema mejora si los datos no lo muestran.
- PDF vertical de una página producido en LaTeX, con grafo de agentes/herramientas y aristas etiquetadas, técnicas/ablaciones, resultados y limitaciones.
- Video de hasta tres minutos mostrando ejecución, mensajes entre agentes y respuesta final; enlace abierto y trazas de sus entradas en el repositorio.

Fecha límite según la pauta: 31 de octubre de 2026, 23:59. Ponderación: 30 % del proyecto semestral.
