# Congelación para el experimento de 50 × 6

Fecha: 27-10-2026. Código y prompts: commit `de2951b22214f294e9f9eb1f5b0fae9a25c622da`. Cambios posteriores de documentación no modifican el sistema experimental. Paquete 0.4.0; protocolo `d3-agentes-desde-cero-v4`.

Se terminó, auditó y evaluó el piloto v4 `6a4e8925ada1fa3d1dee`. Sus fallos siguen presentes y se conservan. El lote completo se inicia una vez sin seleccionar por calidad respuestas o semillas. Una interrupción técnica puede reanudarse desde checkpoints de la misma configuración; no se reemplazan errores semánticos por nuevos intentos.

- Entradas: las 50 preguntas de desarrollo D1/D2, sin incorporar referencias ni veredictos a la generación.
- Condiciones: `baseline_directo`, `rag_d2`, `agentes_completo`, `sin_descomposicion`, `sin_completitud`, `sin_verificacion`.
- Misma instancia Qwen3-4B, revisión y muestreo originales de D2; E5 y corpus fijados. Semilla base 2026 y slots por pregunta/rol/visita. Orden de condiciones rotatorio.
- Prompts externos v4; cada ablación retira únicamente un bloque experimental. Controles y límites compartidos: 12 llamadas, 6 herramientas, 3 salidas inválidas; entrada+salida+margen dentro de 8.192 tokens.
- Etiqueta: `lote-v4`; 300 resultados esperados, cada uno con llamadas y trazas propias. Los hashes exactos de configuración, fuentes, corpus y prompts quedan en el ZIP de la corrida.
- Pauta externa D2, versión de referencias `e2-referencias-v1`, sin cambios. Cada respuesta se revisa por significado, suficiencia, condiciones materiales y respaldo; aceptación interna no se usa como etiqueta. Conservar juicios con motivos y hashes, incluidas regresiones y abstenciones técnicas.
- Los cuatro pilotos no se suman al lote para calcular exactitud. Comparaciones entre pilotos son diagnóstico y no evidencia independiente de mejora.

## Operación

En el notebook del commit indicado, tras carga y piloto, se cambia únicamente `EJECUTAR_LOTE = True` en la sección 6 y se ejecuta esa celda. La exportación de la sección 8 se solicita después; si queda en cola, se ejecutará al terminar el kernel. Con dos corridas presentes, `prepare_download` genera un ZIP contenedor con piloto y lote separados.

El almacenamiento temporal actual es `/content/d3_agentes_runs`. El sistema actualiza el ZIP después de cada respuesta. Descargar copias parciales desde Archivos sin interrumpir el kernel; conservarlas con identidad y momento de descarga. Antes de reanudar en otra sesión, auditar y restaurar las fuentes/checkpoints exactos. No confundir una copia parcial con 300 respuestas completas.
