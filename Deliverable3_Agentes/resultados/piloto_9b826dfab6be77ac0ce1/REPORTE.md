# Piloto v3: menor coste, calidad todavía inferior a D2

Corrida `9b826dfab6be77ac0ce196b52e2cda518c013a80356ef6f2e0cf859739709149`, Qwen3-4B real en Tesla T4. ZIP original intacto, inventario, hashes, llamadas y correspondencia CSV/JSON auditados; 12/12 respuestas. Importación y revisión: 27-10-2026. Evaluación asistida por Codex con la misma pauta D2, fuera del sistema, sin copiar etiquetas históricas.

| Condición | Aciertos | Llamadas | Tokens de salida | Generación |
|---|---:|---:|---:|---:|
| Baseline | 0/4 | 4 | 327 | 36,00 s |
| RAG D2 | 2/4 | 4 | 414 | 71,83 s |
| Agentes v3 | 1/4 | 15 | 1.963 | 380,05 s |

Sin salidas cortadas. V2 empleó 24 llamadas, 10.353 tokens y 1.453,74 s en agentes. V3 reduce esos costes, pero mantiene 1/4 y la regresión P41 frente a D2. No demuestra mejora en calidad. Las preguntas son cuatro casos de diagnóstico conocidos, no un conjunto independiente.

## Revisión por caso

- **P05, correcta:** Memoria de Título, un semestre, RI-FI art. 29. Se revisó RG 3.10 completo porque la respuesta añade una referencia a Memoria: el texto sí la contempla dentro de habilitación profesional. El extracto seleccionado por el auditor era incompleto, pero no invalida una respuesta respaldada por la fuente completa. No se califica automáticamente a partir del extracto del auditor.
- **P25, incorrecta:** repite prioridades a/b sin desarrollar qué asignaturas son. La pauta exige atrasadas respecto al plan y obligatorias reprobadas aún no aprobadas, no el mínimo de créditos no preguntado. Los tres agentes dieron por suficiente la remisión.
- **P38, incorrecta bajo la pauta de respaldo aplicada:** datos de aplicabilidad y nota correctos, pero RG art. 23 solo respalda escala/nota. Falta documentar el vínculo específico de Ingeniería al RG (RI-FI art. 2). D2 también falla, pues cita equivocadamente RI-FI art. 6. No se exige repetir tres citas ni detalles no preguntados.
- **P41, incorrecta:** termina por tres errores de estructura JSON. El investigador emitió `nombre` y `argumentos` en la raíz en vez de dentro de `herramienta`. El redactor alcanzó un borrador que negaba correctamente la existencia, pero añadió `[RI-FI]`, que no es un ID de evidencia, y el control lo devolvió a investigación. El resultado final fue una abstención técnica, no la negativa normativa válida que D2 sí entrega.

## Cambios generales propuestos para v4

Normalizar únicamente la forma plana exacta de una solicitud explícita de herramienta: no inferir nombre, argumentos, respuesta ni evidencia. Conservar validadores, límites y salidas crudas. Precisar el uso de IDs en citas. Reforzar los bloques externos de descomposición, completitud y verificación para comprobar remisiones y ámbito; esas mismas versiones se retirarán una por una en las ablaciones. No codificar IDs de preguntas ni respuestas esperadas.

No reinterpretar v3 como si hubiera usado estos cambios. El siguiente intento lleva identidad y etiqueta nuevas.
