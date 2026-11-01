# Historial de versiones de los prompts (D3)

## Ablaciones — 2026-10-29
Sin cambios en los archivos. Las ablaciones (`sin_fewshot`, `sin_cot`) quitan un bloque exacto desde el código
(`orquestador.ABLACIONES`); `sin_react` y `sin_verificador` omiten la llamada al agente correspondiente.

## v6 — 2026-10-27 (tras la corrida v5)
- La corrida v5 separó efectos: los cambios de CÓDIGO de recuperación mejoraron (P4, P6, P7, P38), pero los cambios
  de PROMPT del Redactor (incluir condiciones) y del Verificador (más permisivo) introdujeron reglas mal aplicadas
  (P14, P27, H04, H12, H18) y rompieron premisas falsas (P47–P50).
- v6 = código v5 + 02_recuperador v5 (sin ejemplos copiables) + 03_redactor y 04_verificador restaurados tal como
  se usaron en la corrida v4. Las versiones v5 quedan en prompts/historial/.

## v5 — 2026-10-27 (tras la corrida completa v4: 75 preguntas)
Cambios por patrones generales observados en las trazas, no por preguntas concretas:
- 02_recuperador: sin valores de ejemplo concretos (el modelo copiaba "existe art. 90", "traer art. 8"
  y "baja académica" en 7 preguntas ajenas); "existe"/"traer" solo con números presentes en el contexto;
  instrucción de reformular ante el aviso de acción repetida (31% de acciones repetidas en v4).
- 03_redactor: recibe su borrador anterior y corrige solo lo señalado (en v4, 4 rechazos llevaron al
  Redactor de responder a "no hay información"); prohibido negar condiciones con "No aplica"
  (afirmación falsa en P1, P21, P36); usa las cifras de la pregunta en cálculos; razonamiento breve
  (un borrador quedó vacío por agotar tokens).
- 04_verificador: rechaza solo por errores concretos nombrables; no rechaza un dato correcto por
  "falta de justificación" (H05); reconoce como correcta la corrección de una premisa falsa (P47);
  rehace los cálculos; detecta condiciones omitidas o negadas.

## v4 — 2026-10-26 (primera prueba con Qwen3-4B real)
- Observado: el Redactor copiaba su propio prompt (rol, reglas, etiquetas) antes de responder, y el
  ejemplo "[RI-FI-ART-011]" de las reglas se colaba como cita falsa en el chequeo de citas.
- Causas: (1) la cabecera de documentación (líneas '#') se enviaba al modelo; (2) el prompt terminaba
  con el bloque de evidencia, sin orden final, y el modelo "continuaba el documento".
- Cambios: el orquestador ya no envía las líneas '#'; 03_redactor termina con una TAREA explícita, sin
  ejemplos de identificadores en las reglas; el orquestador rescata la respuesta desde el último
  "Respuesta:" (la salida cruda queda en la traza como `salida_cruda`).

## v3 — 2026-10-26 (revisión crítica)
- 02_recuperador: recibe `ultima_observacion` (extractos de lo que devolvió su acción anterior),
  `documentos` y `feedback_verificador`. Antes solo veía IDs, lo que dejaba el ciclo ReAct sin "observar".
- 03_redactor: nuevo `<modo>` según el tipo del Enrutador; nuevo bloque de observaciones del
  Verificador; permite calcular con cifras de la evidencia y de la pregunta (antes lo prohibía
  de hecho, lo que bloqueaba las preguntas numéricas). El bloque <pensar> se elimina antes de
  mostrar y verificar.
- 04_verificador: recibe el TEXTO de la evidencia (antes solo IDs: no podía comprobar datos) y el
  resultado de la herramienta `chequear_citas`. El motivo se usa como corrección en el reintento.
- 01_enrutador: definición breve de cada tipo.

## v2 — 2026-10-24
- Acciones estructuradas en el Recuperador; Verificador con decisión de destino.

## v1 — 2026-10-24
- Primera versión de los 4 prompts.
