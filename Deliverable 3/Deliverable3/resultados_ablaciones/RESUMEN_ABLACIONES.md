# Ablaciones de v6: resultados guardados y costo corregido

Las planillas originales se conservan sin cambios. La corrección es propuesta y revisable;
v6 conserva nueve filas marcadas REVISAR. Una aprobación interna no equivale a acierto.

| Variante | Originales | Difíciles | Llamadas reales/pregunta (75) |
|---|---:|---:|---:|
| Completo v6 | 46/50 | 20/25 | 9,48 |
| Sin few-shot | 44/50 | 19/25 | 10,68 |
| Sin ReAct | 45/50 | 18/25 | 3,85 |
| Sin CoT del Redactor | 46/50 | 19/25 | 8,27 |
| Sin Verificador (primer borrador) | 44/50 | 19/25 | 6,41 |

Los tres primeros experimentos de ablación incluyen 75 respuestas y trazas cada uno.
Sin Verificador se deriva del primer borrador de v6; no se presenta como otra corrida GPU.
Su calificación está documentada en `../resultados_v6/ablacion_sin_verificador.md`.

El conteo anterior incluía eventos de herramientas automáticas. En completo hay 798 eventos
y 711 llamadas; en sin few-shot 879/801; sin ReAct 375/289; sin CoT 701/620.
El primer borrador acumula 481 llamadas. El costo medio incluye ambos conjuntos.

Las intervenciones sin ReAct y sin Verificador eliminan componentes del flujo, además de sus
instrucciones. Sin CoT afecta al Redactor; el Verificador mantiene su instrucción de razonar.
La semilla depende del prompt: una modificación cambia también el muestreo. Las diferencias
pequeñas de una sola corrida no demuestran una ventaja estable por técnica.
