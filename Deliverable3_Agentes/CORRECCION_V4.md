# Versión v4: solicitudes de herramientas y cobertura de evidencia

Motivación: [piloto v3](resultados/piloto_9b826dfab6be77ac0ce1/REPORTE.md), 1/4 con agentes y 2/4 con D2. El coste se redujo, pero persisten omisiones y un fallo operativo.

- Se acepta la forma plana exacta `{accion, mensaje, nombre, argumentos}` solo para una herramienta conocida y una acción compatible. Se convierte al mismo contrato anidado conservando argumentos. Campos adicionales, incoherencias y fuentes inventadas siguen rechazados. Las salidas originales se conservan.
- El redactor distingue nombres de documentos e IDs de evidencia para evitar citas como un nombre abreviado entre corchetes.
- Los tres bloques experimentales precisan cobertura, remisiones y contraste entre afirmación y alcance de fuente. No hay respuestas, números de pregunta ni rutas por caso. Las ablaciones siguen retirando exactamente un bloque, con igual protocolo y límites.
- Modelos, muestreo, controles baseline/D2, corpus y presupuestos no cambian. Versión `0.4.0`, protocolo `d3-agentes-desde-cero-v4`; etiquetas nuevas para conservar intentos.

Validación: 38 pruebas locales aprobadas y 700 prompts medidos con E5/tokenizador Qwen reales. Entrada máxima 3.926 tokens; con salida 1.024 y margen 64, total 5.014 < 8.192. No es inferencia generativa ni prueba de calidad. El piloto real v4 sigue pendiente.
