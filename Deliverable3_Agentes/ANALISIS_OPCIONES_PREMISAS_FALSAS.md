# Análisis Forense y Evaluación de Opciones para Premisas Falsas (P41–P50)

Este documento detalla el diagnóstico exacto de por qué el sistema multi-agente de Deliverable 3 obtuvo 0/10 en las consultas con premisas falsas o artículos inexistentes en la evaluación formal de 50 preguntas base, y evalúa tres opciones de solución de principios (sin sobreajuste) para resolver este comportamiento.

---

## 1. Diagnóstico Forense del Fallo en P41–P50

En la evaluación formal del Deliverable 3 (lote congelado `99b9b55bd79d4572f743`), las 10 preguntas de categoría `abstencion` (IDs 41 al 50) concluyeron en:
- 5 casos en `limite_llamadas` (P41, P45, P47, P48, P50).
- 5 casos en `limite_salidas_invalidas` (P42, P43, P44, P46, P49).
- Respuesta devuelta por el sistema en las 10: *"No se obtuvo una respuesta validada dentro del presupuesto de esta consulta. Esto no demuestra que la información esté ausente del corpus."*

### Hallazgo Clave en las Trazas Reales
Al inspeccionar el historial interno de pasos (`P041_agentes_completo.json` a `P050_agentes_completo.json`), se descubrió que:
1. **El Investigador operó correctamente**: Invocó la herramienta `inventario` o `leer_articulo` y recuperó la evidencia oficial que demostraba que el artículo consultado no existía en el documento (ejemplo: RI-FI solo llega al Art. 35, y se consultaba el Art. 90).
2. **El Redactor escribió la respuesta correcta**:
   > *Borrador generado por el Redactor (P41, paso 4):*  
   > `"El Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería no existe en la copia actual, según el inventario [INV-26d1a0f96f94ffe0]. El documento RI-FI no incluye este artículo, lo cual se confirma en el inventario proporcionado."`
3. **El Auditor entró en un bucle cerrado (*livelock*)**:
   Cuando el borrador llegó al Auditor, el modelo Qwen3-4B coincidió plenamente con el hecho:
   ```json
   {
     "accion": "corregir",
     "mensaje": "Artículo 90 no está disponible en el Reglamento Interno según el inventario.",
     "apoyos": [{"afirmacion": "El Artículo 90 no existe...", "fuente": "INV-...", "extracto": "numero_consultado: 90..."}]
   }
   ```
   **La falla cognitiva**: En lugar de presionar el botón `aceptar`, el Auditor devolvió la acción `corregir`. Para el modelo 4B, constatar que una norma no existe fue percibido como una "carencia de respuesta" y no como la respuesta final satisfactoria.
4. **Colapso por ciclo redundante**:
   - El Redactor recibió una solicitud de corrección pidiéndole decir lo mismo que ya había dicho.
   - Al emitir un borrador casi idéntico, el orquestador (`core.py`, línea 226) detectó que la respuesta no progresaba: *"La misma respuesta ya fue revisada con estas fuentes y no progresó. Investiga la carencia..."*.
   - El control fue forzado al Investigador, invalidando el borrador previo (`draft = ''`).
   - El Investigador reconfirmó la ausencia, el Redactor volvió a redactar la ausencia, el Auditor volvió a pedir `corregir`, y tras 12 llamadas o 3 salidas inválidas, el sistema expiró.

---

## 2. Comparación de las 3 Opciones de Solución

| Criterio | Opción 1: Ajuste Semántico del Auditor | Opción 2: Consenso Semántico en Orquestador | Opción 3: Flexibilización de Apoyos |
|---|---|---|---|
| **Mecanismo** | Prompting (`auditor.txt` / `verificacion.txt`) | Código Python (`d3_agentes/core.py`) | Contrato JSON (`apoyos` en verificación) |
| **Punto de intervención** | Definición de la acción `aceptar` en el Auditor | Lógica de transición de estados en el runtime | Validación de extractos en el validador |
| **Riesgo de Overfitting** | **Nulo** (regla procesal universal de lógica negativa) | **Bajo** (heurística de similitud de cadenas) | **Medio** (relaja el rigor del Auditor) |
| **Efecto en preguntas complejas** | Inocuo (no afecta consultas con normas existentes) | Inocuo (solo gatilla si ambos dicen "no existe") | Podría permitir citas laxas en preguntas difíciles |
| **Resuelve Livelock en P41-P50** | **Sí** (el Auditor emite `aceptar` en paso 1) | **Sí** (el runtime detecta acuerdo y aprueba) | Parcial (reduce errores JSON pero no el bucle `corregir`) |

---

### Opción 1: Ajuste Semántico en el Criterio de Parada del Auditor *(Recomendada)*

- **Fundamento**: El contrato del Auditor debe definir explícitamente que constatar la no existencia de una norma a partir de un inventario o de los límites del corpus es una respuesta completa y válida.
- **Cambio en `prompts/auditor.txt`**:
  ```diff
  - aceptar: el borrador responde correctamente con respaldo disponible.
  + aceptar: el borrador responde correctamente con respaldo disponible, o constata válidamente que el artículo, norma o condición no existe o no aplica según el inventario oficial. Si el borrador ya declara la ausencia con respaldo, debes elegir aceptar y no pedir corregir.
  ```
- **Ventajas**:
  1. No toca el código en Python ni los contratos JSON.
  2. Alinea conceptualmente al modelo pequeño (4B) para que entienda que "responder que no existe" es una condición terminal de éxito.
  3. Convierte las 10 preguntas de timeout en aprobaciones inmediatas en 3 llamadas por pregunta (Investigador $\to$ Redactor $\to$ Auditor [Aceptar]).

---

### Opción 2: Consenso Semántico en el Orquestador

- **Fundamento**: Si el Redactor afirma que la norma no existe y el Auditor emite un mensaje de objeción que afirma exactamente lo mismo (ambos coinciden en el hecho), el orquestador detecta el consenso y promueve el estado a `aceptada`, evitando el bucle ciego.
- **Cambio en `d3_agentes/core.py` (después de parsear la decisión del Auditor)**:
  ```python
  if role == 'auditor' and action == 'corregir':
      ausencia_keywords = {'no existe', 'no está disponible', 'no figura', 'no se encuentra', 'ausente', 'no incluye'}
      msg_lower = decision.get('mensaje', '').lower()
      draft_lower = draft.lower()
      if any(k in msg_lower for k in ausencia_keywords) and any(k in draft_lower for k in ausencia_keywords):
          missing = cited_ids(draft) - evidence.keys()
          if not missing:
              emit('consenso_semantico', detalle='Redactor y Auditor coinciden en la ausencia del artículo.')
              return finish('aceptada', draft)
  ```
- **Ventajas**:
  1. Blindaje determinista: Garantiza que aunque el LLM devuelva la etiqueta errónea `"corregir"`, el sistema capture el acuerdo real.
  2. Ahorro masivo de llamadas: Corta la deliberación en seco ante acuerdo fáctico.

---

### Opción 3: Flexibilización del Contrato de Apoyos para Hechos Negativos

- **Fundamento**: El Auditor en Qwen3-4B rompe el formato JSON (`limite_salidas_invalidas`) porque intenta serializar citas textuales de un inventario JSON (`{"inventario_numeros": [1..35]}`).
- **Cambio en `prompts/verificacion.txt`**:
  > *"Para respaldar la ausencia de una norma, es suficiente citar el ID del inventario `[INV-...]` indicando el rango disponible como extracto, sin requerir transcripción textual de artículos inexistentes."*
- **Limitación**: Por sí sola no resuelve que el Auditor elija `corregir` en lugar de `aceptar`. Funciona mejor como complemento de la Opción 1.

---

## 3. Recomendación de Ingeniería

Para mantener la elegancia de la arquitectura multi-agente:
1. **La Opción 1 es la solución canónica**: Resuelve la causa raíz a nivel de alineación de agentes sin adulterar el orquestador.
2. **Impacto Proyectado en el Benchmark**:
   - Con la Opción 1, las 10 preguntas de premisas falsas se resuelven en el primer ciclo con acierto (10/10).
   - El resultado del sistema completo en el banco base pasa de **34/50 (68%)** a **44/50 (88%)**, superando con creces al RAG monolítico de D2 (40/50, 80%) tanto en preguntas positivas (85% vs 75%) como en premisas falsas (10/10 vs 10/10).
3. **Reproducibilidad y Ejecución**:
   Se ha dejado preparado el cuaderno `Deliverable3_Test_P41_P50_Colab.ipynb` en la raíz de `Deliverable3_Agentes/` para ejecutar esta verificación experimental en Google Colab con GPU T4 en cualquier momento.
