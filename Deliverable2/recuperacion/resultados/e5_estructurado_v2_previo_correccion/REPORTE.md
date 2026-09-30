# Recuperación mejorada: comparación con la primera corrida

La cobertura completa de fuentes pasa de **40/45 a 43/45 (95,56%)**. Las cinco consultas de ausencia tienen ahora evidencia estructural obtenida del inventario completo.

**No se ha ejecutado Qwen. Estos números no son exactitud de respuestas.** Las 50 preguntas se están utilizando para desarrollo; este resultado no constituye una evaluación independiente de generalización.

## Cambios

- Citas explícitas: buscar documento y número de artículo en el inventario, además de E5.
- Preguntas compuestas: buscar las partes por separado y añadir sus dos primeros resultados a los cinco de la consulta original.
- Remisiones: añadir artículos mencionados en las unidades seleccionadas, con un solo salto. No confundir referencias a Estatutos con artículos del reglamento.
- Ausencia: conservar el inventario completo consultado y el hash del PDF como evidencia. La afirmación se limita a las copias del corpus.

Mejoran P[25, 36, 50]; no empeora ninguna pregunta previamente cubierta. Quedan sin alguna fuente de la pauta P[34, 38].

## Casos pendientes

- **P34:** se recupera RG art. 31, que contiene el derecho a solicitar suspensión, la autoridad y el plazo. Falta RI-FI art. 25, incluido en la pauta como contexto adicional. No corresponde concluir automáticamente que una futura respuesta sea incorrecta.
- **P38:** se recupera RG art. 23 para escala y aprobación, pero falta RI-FI art. 2 para fundamentar la aplicación en Ingeniería. La parte «se aplica en Ingeniería» pierde contexto al separarse; hay además resultados redundantes del anexo. Es una limitación real de esta descomposición heurística.

Se conserva este resultado sin insertar manualmente artículos desde la pauta. Una próxima variante puede preservar mejor el contexto compartido y diversificar fuentes; deberá registrarse como otra corrida.

## Tamaño y controles

Contexto medio: 3326 caracteres; máximo: 9335. Se omitieron 0 unidades por presupuesto. Se limita a 14 unidades y 20.000 caracteres de texto documental; los inventarios se contabilizan adicionalmente. No se recortan unidades.

Todavía falta medir el presupuesto con el tokenizador de Qwen. La comparación no mantiene el mismo tamaño de contexto entre recuperadores: v2 agrega evidencia a v1. Para comparar prompts, ambas variantes de prompt deben recibir exactamente los mismos contextos congelados.

## Detalle de las 50 preguntas

| Nº | Cobertura anterior | Cobertura actual | Fuentes ausentes de la pauta |
|---:|---|---|---|
| 1 | Completa | Completa | — |
| 2 | Completa | Completa | — |
| 3 | Completa | Completa | — |
| 4 | Completa | Completa | — |
| 5 | Completa | Completa | — |
| 6 | Completa | Completa | — |
| 7 | Completa | Completa | — |
| 8 | Completa | Completa | — |
| 9 | Completa | Completa | — |
| 10 | Completa | Completa | — |
| 11 | Completa | Completa | — |
| 12 | Completa | Completa | — |
| 13 | Completa | Completa | — |
| 14 | Completa | Completa | — |
| 15 | Completa | Completa | — |
| 16 | Completa | Completa | — |
| 17 | Completa | Completa | — |
| 18 | Completa | Completa | — |
| 19 | Completa | Completa | — |
| 20 | Completa | Completa | — |
| 21 | Completa | Completa | — |
| 22 | Completa | Completa | — |
| 23 | Completa | Completa | — |
| 24 | Completa | Completa | — |
| 25 | Incompleta | Completa | — |
| 26 | Completa | Completa | — |
| 27 | Completa | Completa | — |
| 28 | Completa | Completa | — |
| 29 | Completa | Completa | — |
| 30 | Completa | Completa | — |
| 31 | Completa | Completa | — |
| 32 | Completa | Completa | — |
| 33 | Completa | Completa | — |
| 34 | Incompleta | Incompleta | RI-FI-ART-025 |
| 35 | Completa | Completa | — |
| 36 | Incompleta | Completa | — |
| 37 | Completa | Completa | — |
| 38 | Incompleta | Incompleta | RI-FI-ART-002 |
| 39 | Completa | Completa | — |
| 40 | Completa | Completa | — |
| 41 | Sin evidencia global | Inventario comprobado | — |
| 42 | Sin evidencia global | Inventario comprobado | — |
| 43 | Sin evidencia global | Inventario comprobado | — |
| 44 | Sin evidencia global | Inventario comprobado | — |
| 45 | Completa | Completa | — |
| 46 | Completa | Completa | — |
| 47 | Completa | Completa | — |
| 48 | Completa | Completa | — |
| 49 | Sin evidencia global | Inventario comprobado | — |
| 50 | Incompleta | Completa | — |
