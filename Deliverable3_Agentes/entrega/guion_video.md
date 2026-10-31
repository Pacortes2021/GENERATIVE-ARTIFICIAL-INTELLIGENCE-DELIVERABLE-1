# Guion de Demostración y Video Técnico (Máximo 3 Minutos)

**Entregable:** Deliverable 3 — Arquitectura multi-agente con decisiones observables, herramientas normativas y estudio de ablación.  
**Equipo:** Álvaro Contreras y Pablo Cortés | Generative Artificial Intelligence (580694) — Facultad de Ingeniería, Universidad de Concepción.  
**Duración objetivo:** 2 minutos y 50 segundos (170 segundos), dejando 10 segundos de holgura bajo el límite estricto de 180 segundos.

---

## 1. Ficha Técnica y Preparación de Pantalla

Antes de iniciar la grabación con OBS Studio, QuickTime o la herramienta de captura de pantalla:
1. **Configuración de pantalla:** Resolución 1080p (1920×1080), escala de fuentes legible (125% o zoom en navegador/VS Code).
2. **Pestañas y ventanas preparadas en orden de aparición:**
   - **Ventana 1:** `Deliverable3_Agentes/entrega/main.pdf` abierto en visor de PDF con zoom al encabezado y al diagrama TikZ.
   - **Ventana 2:** VS Code con `d3_agentes/core.py` y la carpeta `prompts/` abierta en el explorador.
   - **Ventana 3:** Traza real de ejecución exitosa (`P005_agentes_completo.json`) abierta en formato JSON legible.
   - **Ventana 4:** Traza real de diagnóstico de fallo (`P041_agentes_completo.json`) para ilustrar el comportamiento en premisas falsas.
   - **Ventana 5:** Tabla 1 del informe PDF y repositorio GitHub abierto en el navegador.
3. **Consistencia técnica:** Recordar que la inferencia no se simula en vivo durante la locución para no perder tiempo de video; se exhiben **trazas reales completas conservadas en el repositorio** (`modelo_real`, Qwen3-4B, GPU T4).

---

## 2. Minutaje y Estructura Segundo a Segundo

```
[0:00 - 0:25] | Bloque 1: Motivación, Corpus y Salto Conceptual a Multi-Agente
[0:25 - 0:55] | Bloque 2: Arquitectura del Sistema, Grafo TikZ y Contratos JSON
[0:55 - 1:40] | Bloque 3: Demostración de Traza Real Observable (Caso Exitoso)
[1:40 - 2:15] | Bloque 4: Transparencia Empírica y Diagnóstico de Fallos (Premisas Falsas)
[2:15 - 2:50] | Bloque 5: Resultados Empíricos (450 corridas), Ablaciones y Repositorio
```

---

## 3. Guion de Locución y Acciones en Pantalla

### Bloque 1: Motivación, Corpus y Salto a Multi-Agente (0:00 – 0:25)
* **Pantalla:** Mostrar la cabecera de `main.pdf` y la Sección 1.
* **Acción del cursor:** Resaltar el título institucional, el modelo (`Qwen/Qwen3-4B`) y el corpus cerrado.
* **Locución (Voz en off):**
  > "Continuamos con el asistente normativo para la Facultad de Ingeniería de la Universidad de Concepción. Mientras que en los entregables anteriores utilizábamos un pipeline RAG monolítico donde el modelo respondía en una sola pasada estática, en este Entregable 3 implementamos un sistema multi-agente donde los modelos toman decisiones observables en tiempo de ejecución: eligen herramientas, transfieren el control mediante contratos JSON tipados, reintentan ante objeciones y se detienen cuando la evidencia es insuficiente."

---

### Bloque 2: Arquitectura del Sistema, Grafo TikZ y Herramientas (0:25 – 0:55)
* **Pantalla:** Zoom directo al diagrama de arquitectura en `main.pdf` (Sección 2).
* **Acción del cursor:** Seguir el flujo horizontal: `Pregunta -> Investigador -> Redactor -> Auditor -> Respuesta validada`. Luego señalar el contenedor inferior de *Herramientas Normativas* y finalmente los bucles superiores.
* **Locución (Voz en off):**
  > "El sistema opera mediante tres roles especializados que comparten una misma instancia de Qwen3-4B de 4 mil millones de parámetros:
  > Primero, el **Investigador**, que analiza la consulta y accede de forma exclusiva a herramientas normativas: búsqueda densa con embeddings E5, lectura íntegra de artículos y el inventario del articulado oficial.
  > Segundo, el **Redactor**, que sintetiza la respuesta respaldada únicamente en las fuentes recuperadas.
  > Y tercero, el **Auditor**, que verifica extracto por extracto el respaldo literal de cada afirmación. Si detecta discrepancias de citas, devuelve una orden de corregir al Redactor; si constata que la normativa es insuficiente, dispara un bucle de re-investigación hacia el Investigador."

---

### Bloque 3: Demostración de Traza Real Observable (0:55 – 1:40)
* **Pantalla:** Cambiar a VS Code. Mostrar el archivo de traza real `P005_agentes_completo.json` (consulta sobre titulación en Ingeniería).
* **Acción del cursor:** Desplazarse por los eventos clave de la traza:
  1. Solicitud y respuesta de la herramienta `leer_articulo` (Art. 29 RI-FI).
  2. JSON de transferencia del Investigador hacia el Redactor con `accion: "redactar"`.
  3. Borrador JSON del Redactor con citas explícitas `[RI-FI-ART-029]`.
  4. Evaluación del Auditor con `accion: "aceptar"` y lista de `apoyos` con extractos literales.
* **Locución (Voz en off):**
  > "Veamos una traza real ejecutada en GPU Tesla T4. Ante la consulta sobre la actividad final de titulación, observamos cómo el Investigador recupera el Artículo 29 del Reglamento Interno y transfiere el control con un contrato JSON limpio.
  > El Redactor formula la respuesta identificando la Memoria de Título con su cita oficial.
  > A continuación, el Auditor audita el borrador, valida que el extracto literal respalda exactamente la condición de titulación y emite la acción 'aceptar'.
  > Todo el proceso es determinista, reproducible y auditable mediante hashes SHA-256 en cada llamada."

---

### Bloque 4: Transparencia Empírica y Diagnóstico de Fallos (1:40 – 2:15)
* **Pantalla:** Cambiar a `P041_agentes_completo.json` o al diagrama TikZ en la flecha de parada *Abstención técnica* (`límite de revisiones o formato inválido`).
* **Acción del cursor:** Resaltar el evento de ciclo interrumpido y la respuesta terminal segura por límite de llamadas.
* **Locución (Voz en off):**
  > "Un principio central de nuestro trabajo es la transparencia experimental. En las 10 preguntas con premisas falsas —como consultar por artículos inexistentes— diagnosticamos una limitación clave de los agentes deliberativos frente al RAG estático:
  > Mientras que RAG D2 abortaba pasivamente, el bucle deliberativo de los agentes indujo un sesgo de búsqueda activa. Como vemos en la traza de la pregunta 41, el Redactor redactó correctamente que el artículo no existía citando el inventario, pero el Auditor pequeño interpretó la ausencia como una carencia y solicitó reiteradamente corregir. El orquestador interrumpió el ciclo seguro al agotar límites, devolviendo una abstención técnica justificada."

---

### Bloque 5: Resultados Empíricos (450 corridas), Ablaciones y Cierre (2:15 – 2:50)
* **Pantalla:** Volver a `main.pdf` en la Sección 4 (Tabla 1) y luego mostrar brevemente el repositorio en GitHub.
* **Acción del cursor:** Resaltar la fila de *Multi-Agente (E3)* (34/50 y 11/25), las ablaciones (*sin descomp.* y *sin verific.* con 14/25) y los enlaces del encabezado.
* **Locución (Voz en off):**
  > "Evaluamos 450 inferencias en GPU cubriendo seis configuraciones experimentales.
  > En preguntas sobre normativa vigente, los agentes superaron a RAG D2 con un 85% frente a 75%, resolviendo problemas complejos de cálculo ponderado de notas y prelación de asignaturas.
  > El estudio de ablación demostró que al retirar la verificación léxica estricta, el acierto en casos difíciles sube de 44% a 56%, evidenciando que una auditoría demasiado rígida sobre un modelo 4B puede provocar abstenciones indebidas.
  > Esta deliberación demanda 5,1 llamadas por consulta frente a 1 llamada de RAG, marcando el compromiso entre rigor analítico y latencia.
  > Todo el código, prompts externos versionados y los 25 snapshots inmutables se encuentran disponibles en nuestro repositorio de GitHub."

---

## 4. Checklist de Grabación y Verificación

- [ ] Duración total del audio: entre 2:40 y 2:50 minutos.
- [ ] No se usan muletillas ni términos artificiales ("victorias cualitativas", etc.).
- [ ] La pantalla muestra texto grande, nítido y legible.
- [ ] Se muestran tanto un caso exitoso con contratos JSON como el diagnóstico real del fallo en premisas falsas.
- [ ] Se menciona claramente el repositorio GitHub oficial y el estudio de ablación de 450 corridas.
