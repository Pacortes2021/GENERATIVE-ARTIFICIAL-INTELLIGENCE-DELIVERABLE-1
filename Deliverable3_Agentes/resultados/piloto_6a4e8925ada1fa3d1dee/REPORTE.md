# Piloto v4: flujo completo conservado; persisten fallos de coordinación

Corrida real Qwen3-4B en T4, 12/12 respuestas. ZIP original intacto y auditado, CSV/JSON consistentes y fuentes congeladas. Evaluación individual externa con pauta D2 y revisión del corpus; no se copiaron etiquetas de otros pilotos.

| Condición | Aciertos estrictos | Llamadas | Tokens de salida | Generación |
|---|---:|---:|---:|---:|
| Baseline | 0/4 | 4 | 327 | 37,18 s |
| RAG D2 | 2/4 | 4 | 414 | 78,77 s |
| Agentes v4 | 1/4 | 21 | 3.228 | 723,35 s |

No hubo salidas cortadas ni excepción de infraestructura. Se exportaron todas las respuestas. No se demuestra mejora frente a D2. Son cuatro casos de desarrollo, elegidos para diagnóstico.

## Juicios y diagnóstico

- **P05 correcta:** identifica Memoria de Título, un semestre, y cita RI-FI art. 29 inequívocamente en prosa. RG 3.10 completo contempla Memoria entre actividades de habilitación profesional; se acepta la paráfrasis, sin imponer corchetes.
- **P25 incorrecta estricta, con mejora parcial:** ahora desarrolla las dos categorías y cita RI-FI 7/9. Sin embargo, «obligatorias reprobadas anteriormente» omite «no aprobadas a la fecha», condición que delimita cuáles no pueden eliminarse. Haber reprobado alguna vez no equivale a continuar sin aprobar. Los detalles del mínimo de créditos no fueron exigidos por el evaluador.
- **P38 incorrecta por respaldo del alcance:** afirma correctamente sí y 4,0, pero cita solo RG art. 23; falta documentar el vínculo específico de Ingeniería al RG. Mismo criterio aplicado a v3. El sistema no ejecutó la investigación que su bloque de descomposición pedía para esa carencia.
- **P41 incorrecta:** los borradores reconocieron ausencia, pero el auditor siguió devolviéndolos sin identificar una corrección útil. Tras dos correcciones el controlador pidió nueva investigación. El resultado final agotó 12 llamadas (investigador 5, redactor 4, auditor 3), con 2 consultas incluidas la búsqueda inicial. La solicitud plana pudo normalizarse y la herramienta ejecutó la lectura; después apareció otra forma inválida (`herramienta` como cadena y `argumentos` externo), registrada y rechazada. Hubo una salida inválida, no una excepción del programa. Los borradores no se sustituyen por el resultado final.

## Decisión experimental

Congelar v4 y ejecutar las 50 preguntas en las seis condiciones. Los problemas de inferencia restantes forman parte del resultado que debe medirse: no se ocultan ni se transforman en respuestas correctas mediante reglas por pregunta. El flujo genera, limita, conserva y exporta intentos; no se seguirá ajustando indefinidamente a estos cuatro casos. El lote completo tampoco es un test independiente: las 50 preguntas ya se usaron en desarrollo.
