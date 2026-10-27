# Lote v4 en curso: 50 preguntas × seis condiciones

**Todavía incompleto.** Este directorio conserva snapshots del experimento real, no una evaluación final. No interpretar el número de archivos ni una aceptación interna como acierto.

Primera copia auditada: **12/300 respuestas**, dos preguntas en cada una de las seis condiciones. Las fuentes, prompts, inferencia y límites coinciden exactamente con el piloto v4 congelado. Las copias están en `snapshots/`, cada una con ZIP original, instante UTC, SHA-256 y resumen de auditoría. No se sobrescriben copias previas.

Corrida en Colab: `/content/d3_agentes_runs/agentes_99b9b55bd79d4572f743`. ZIP actual: misma ruta con `.zip`. Se actualiza de forma atómica tras cada respuesta completada. Descargar desde Archivos mientras continúa la ejecución, sin ejecutar otra inferencia ni exportar concurrentemente desde un segundo proceso.

Al terminar, conservar el ZIP final por separado, auditar 300/300 y extraer a una carpeta nueva. Solo entonces preparar las seis evaluaciones completas con `evaluar.py`. Cada respuesta recibe un juicio externo nuevo con motivo y hash. Los resultados de los pilotos no se suman a este lote.
