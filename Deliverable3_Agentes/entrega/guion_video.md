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
  > "Continuamos con el asistente de normativa para Ingeniería UdeC. Frente al RAG monolítico de una sola pasada estática, en este Entregable 3 implementamos un sistema multi-agente con decisiones observables: los modelos eligen herramientas, transfieren el control con contratos JSON tipados, reintentan ante objeciones y se detienen cuando la evidencia es insuficiente."

---

### Bloque 2: Arquitectura del Sistema, Grafo TikZ y Herramientas (0:25 – 0:55)
* **Pantalla:** Zoom directo al diagrama de arquitectura en `main.pdf` (Sección 2).
* **Acción del cursor:** Seguir el flujo horizontal: `Pregunta -> Investigador -> Redactor -> Auditor -> Respuesta validada`. Luego señalar el contenedor inferior de *Herramientas Normativas* y finalmente los bucles superiores.
* **Locución (Voz en off):**
  > "El sistema opera con tres roles sobre una misma instancia de Qwen3-4B:
  > El **Investigador** analiza la consulta y accede a herramientas normativas: búsqueda densa con E5, lectura íntegra de artículos y el inventario oficial.
  > El **Redactor** formula la respuesta respaldándose únicamente en las fuentes recibidas.
  > Y el **Auditor** verifica extracto por extracto las afirmaciones, exigiendo corregir citas o reiniciar la investigación ante normativa insuficiente."

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

### Bloque 4: Transparencia Empírica, Diagnóstico y Resolución (1:40 – 2:15)
* **Pantalla:** Cambiar a `P041_agentes_completo.json` o al código de `d3_agentes/core.py` (función de consenso semántico).
* **Acción del cursor:** Resaltar la detección del livelock inicial y el mecanismo de consenso semántico en el orquestador.
* **Locución (Voz en off):**
  > "Un principio central de nuestro trabajo es la transparencia experimental. En las preguntas con premisas falsas diagnosticamos inicialmente una limitación clave:
  > Mientras que RAG D2 abortaba pasivamente, el bucle deliberativo indujo un sesgo de búsqueda activa. Como vemos en la traza de la pregunta 41, el Redactor constataba la ausencia del artículo mediante el inventario, pero el Auditor caía en livelock pidiendo corregir.
  > Para resolverlo sin sobreajuste, incorporamos alineación de parada en ausencias en el prompt del Auditor y consenso semántico en el orquestador. Esta mejora desbloqueó de inmediato 9 de las 10 consultas falsas, alcanzando un 90% de acierto en abstenciones."

---

### Bloque 5: Resultados Empíricos (450 corridas), Ablaciones y Cierre (2:15 – 2:50)
* **Pantalla:** Volver a `main.pdf` en la Sección 4 (Tabla 1) y luego mostrar brevemente el repositorio en GitHub.
* **Acción del cursor:** Resaltar la fila de *Multi-Agente (E3)* (43/50 o 86% en base y 21/25 u 84% en difícil), las comparaciones con RAG D2 y los enlaces del encabezado.
* **Locución (Voz en off):**
  > "Evaluamos las inferencias en GPU cubriendo las configuraciones experimentales en ambos conjuntos de datos.
  > En el banco base, nuestro sistema multi-agente alcanza un 86% de exactitud con 43 de 50 aciertos, superando el 80% del RAG monolítico de D2, y alcanzando un 90% en la detección rigurosa de premisas falsas.
  > En el conjunto de 25 consultas difíciles de estrés normativo, con la normalización de extractos del validador alcanzamos un 84% con 21 de 25 respuestas aprobadas, resolviendo problemas de cálculo ponderado de notas, suspensión y causales de baja donde D2 fallaba.
  > Todo el código, prompts externos versionados y los respaldos auditables se encuentran disponibles en nuestro repositorio de GitHub."

---

## 4. Checklist de Grabación y Verificación

- [ ] Duración total del audio: entre 2:40 y 2:50 minutos.
- [ ] No se usan muletillas ni términos artificiales ("victorias cualitativas", etc.).
- [ ] La pantalla muestra texto grande, nítido y legible.
- [ ] Se muestran tanto un caso exitoso con contratos JSON como el diagnóstico real del fallo en premisas falsas.
- [ ] Se menciona claramente el repositorio GitHub oficial y el estudio de ablación de 450 corridas.
