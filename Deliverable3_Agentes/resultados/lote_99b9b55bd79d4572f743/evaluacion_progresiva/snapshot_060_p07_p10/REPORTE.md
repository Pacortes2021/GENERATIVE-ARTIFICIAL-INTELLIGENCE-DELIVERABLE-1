# Evaluación progresiva P07–P10 (Snapshot 60)

- **Lote:** `agentes_99b9b55bd79d4572f743`
- **Snapshot base:** `snapshots/20261029T040805589463Z_060de300.zip`
- **SHA-256:** `1b955f91fa88f950c5c00e4aea06c7b33897e5727da2670a035a526cfafb9bf7`
- **Fecha de auditoría:** 29 de octubre de 2026
- **Alcance:** 24 respuestas (P07 a P10 en las seis condiciones)

## Resultados por condición (P07 a P10)

| Condición | P07 | P08 | P09 | P10 | Total P07–P10 | Acierto (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `rag_d2` | ✅ | ✅ | ✅ | ✅ | 4/4 | 100.0% |
| `agentes_completo` | ✅ | ✅ | ✅ | ✅ | 4/4 | 100.0% |
| `sin_completitud` | ✅ | ✅ | ✅ | ✅ | 4/4 | 100.0% |
| `sin_descomposicion` | ❌ (límite salidas) | ✅ | ✅ | ✅ | 3/4 | 75.0% |
| `sin_verificacion` | ❌ (límite salidas) | ✅ | ✅ | ✅ | 3/4 | 75.0% |
| `baseline_directo` | ❌ | ❌ | ❌ | ❌ | 0/4 | 0.0% |

## Acumulado global P01 a P10 (60 respuestas)

| Condición | P01–P06 | P07–P10 | Acumulado P01–P10 | Tasa global (%) |
|---|:---:|:---:|:---:|:---:|
| `rag_d2` | 5/6 | 4/4 | **9/10** | **90.0%** |
| `agentes_completo` | 4/6 | 4/4 | **8/10** | **80.0%** |
| `sin_completitud` | 4/6 | 4/4 | **8/10** | **80.0%** |
| `sin_descomposicion` | 3/6 | 3/4 | **6/10** | **60.0%** |
| `sin_verificacion` | 3/6 | 3/4 | **6/10** | **60.0%** |
| `baseline_directo` | 0/6 | 0/4 | **0/10** | **0.0%** |

## Hallazgos de ablación
1. **P07 (Continuación de estudios)**: `agentes_completo` acierta en una pasada limpia de 3 llamadas (Investigador, Redactor, Auditor). Las ablaciones `sin_descomposicion` y `sin_verificacion` sufrieron desajuste en los extractos de citas del auditor, agotando el presupuesto de salidas inválidas (`limite_salidas_invalidas`).
2. **P10 (Convalidación Primer Año Común)**: Se evidenció el beneficio del control del auditor para desambiguar entre la norma general de reingreso (RG art. 44) y la excepción expresa de Primer Año Común (RI-FI art. 22).
3. **Consumo de recursos en P07–P10**:
   - `rag_d2`: 4 llamadas, 4.297 tokens entrada, 376 tokens salida (56,99 s).
   - `agentes_completo`: 15 llamadas, 28.337 tokens entrada, 2.385 tokens salida (380,96 s).
