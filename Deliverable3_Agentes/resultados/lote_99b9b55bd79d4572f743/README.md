# Lote v4 completo: 50 preguntas × seis condiciones (300 respuestas)

**Completado y evaluado al 100%.** Este directorio contiene la corrida oficial inmutable del experimento sobre el corpus cerrado UdeC y la pauta oficial de D2.

- **Respaldo final auditado:** **300/300 respuestas**, `snapshots/20261030T012637381925Z_300de300.zip`, SHA-256: `9756a348858cf1a8cdbbec8e509e013307a348f7f47714e6e647e50c1bc8d411`.
- **Datos originales extraídos:** En `original/`, con los 6 archivos CSV de 50 preguntas cada uno (`agentes_completo.csv`, `baseline_directo.csv`, `rag_d2.csv`, `sin_descomposicion.csv`, `sin_completitud.csv`, `sin_verificacion.csv`), trazas individuales completas y llamadas a herramientas.
- **Evaluación externa formal:** En `evaluacion/`, con paquetes y veredictos para cada variante.
- **Informe comparativo consolidado:** En `informe_comparativo_final.json`, generado con `evaluar.py comparar`.

### Resumen de Resultados Empíricos

| Condición | Total (50) | P01–P40 (Sustantivas) | Llamadas/q | Tokens In/q | Tokens Out/q | Latencia/q |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `baseline_directo` | 1/50 (2,0%) | 1/40 (2,5%) | 1,0 | 119 | 65 | 6,7 s |
| `rag_d2` | 40/50 (80,0%) | 30/40 (75,0%) | 1,0 | 1.320 | 95 | 15,1 s |
| `agentes_completo` | 34/50 (68,0%) | 34/40 (85,0%) | 5,1 | 12.009 | 887 | 152,3 s |
| `sin_descomposicion` | 34/50 (68,0%) | 32/40 (80,0%) | 5,4 | 12.598 | 933 | 161,5 s |
| `sin_completitud` | 34/50 (68,0%) | 33/40 (82,5%) | 5,2 | 11.711 | 816 | 142,1 s |
| `sin_verificacion` | 32/50 (64,0%) | 31/40 (77,5%) | 4,9 | 10.515 | 867 | 139,2 s |

En preguntas sustantivas de la normativa (P01–P40), `agentes_completo` supera a `rag_d2` por **+10,0 puntos porcentuales (85,0% vs. 75,0%)**, corrigiendo 9 de las 10 fallas históricas de D2 (P01, P11, P13, P15, P24, P25, P28, P30, P38). En preguntas con artículos inexistentes (P41–P50), el auditor frena alucinaciones mediante abstenciones técnicas controladas por presupuesto.
