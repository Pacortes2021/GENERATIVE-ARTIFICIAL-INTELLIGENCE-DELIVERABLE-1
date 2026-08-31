# Asistente de normativa de pregrado (Ingeniería UdeC)

Proyecto semestral de Generative Articial Intelligence (580694), segundo semestre 2026, Universidad de Concepción.
Entregable 1: tarea, modelo y baseline.

## Equipo
- Álvaro Contreras
- Pablo Cortés

## La tarea
Responder preguntas en español sobre la normativa de pregrado de la Facultad de Ingeniería UdeC, dando (i) el dato exacto y (ii) la cita del artículo que lo respalda. Si la respuesta no está en el corpus, la respuesta correcta es abstenerse.

**Corpus cerrado** (documentos oficiales públicos):
1. Reglamento General de Docencia de Pregrado (RG)
2. Reglamento Interno de Docencia de Pregrado, Facultad de Ingeniería (RI-FI)
3. Calendario de Docencia de Pregrado 2026 (CAL)

**Métrica:** exactitud estricta (correcto solo si el dato y el artículo son correctos), reportada por categoría (factual, numérica, condicional, cruce entre documentos, abstención).

## Modelo
- **Principal:** `Qwen/Qwen3-4B` (Apache 2.0). Elegido por la tarea (corpus pequeño + RAG) para optar al bono de modelo notablemente < 8B.

  Justificación (benchmarking): según el Reporte Técnico de Qwen3, Qwen3-4B casi iguala al 8B en IFEval (81,9 vs 85,0), Multi-IF (66,3 vs 71,2) y MMMLU-14 idiomas (69,8 vs 74,4). IberBench (lenguas ibéricas) muestra que los mejores modelos están en el rango de 3 a 10B y que bajo ~3B el rendimiento cae, por lo que 4B es el tamaño mínimo seguro. Fuentes: arXiv:2505.09388, arXiv:2504.16921, La Leaderboard (BSC/HF).
- **Candidatos alternativos:** `BSC-LT/salamandra-7b-instruct` (español), `Qwen/Qwen3-8B` (cota superior).

## Resultado del baseline (prompting directo, sin documentos)
Qwen3-4B, zero-shot, sin RAG: 2/50 (4%) global; 0/40 en preguntas cuya respuesta está en el corpus. Ante preguntas de premisa falsa (artículos inexistentes), fabricó su contenido en 8 de 10 casos. La abstención está descalibrada: inventa cuando debería abstenerse y niega datos que sí existen. Qwen3-8B (el doble de tamaño) obtiene el mismo 2/50 (4%), lo que confirma que la falla es estructural y no depende del tamaño del modelo.

## Contenido del repositorio
- `baseline_normativa_ingenieria.ipynb`: cuaderno principal (Qwen3-4B) que genera la tabla de fallas.
- `baseline_normativa_ingenieria_8b.ipynb`: réplica con Qwen3-8B (cota superior).
- `test_set_50.csv`: conjunto de evaluación (50 preguntas con su respuesta de referencia y fuente).
- `deliverable1.pdf` 
- `resultados_baseline.csv`: csv con los resultados del baseline con Qwen3-4B.
- `resultados_baseline_8b.csv`: csv con los resultados del baseline con Qwen3-8B.

Los cuadernos se versionan ya ejecutados: sus salidas (GPU, modelo cargado, respuestas y resumen) son la evidencia de ejecución.

## Estado del trabajo
Tarea, modelo y baseline definidos y medidos. 

**Próximo paso:** implementar RAG sobre el corpus y medir la mejora contra este baseline (4%).
