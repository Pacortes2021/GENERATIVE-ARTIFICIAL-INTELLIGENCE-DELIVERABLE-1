# Guion de Demostración Oficial en Google Colab (≤ 3 Minutos)

**Entregable:** Deliverable 3 — Arquitectura multi-agente con decisiones observables, herramientas normativas y estudio de ablación.  
**Cuaderno de soporte:** `Deliverable3_Agentes/Deliverable3_Demo_Video.ipynb` (Google Colab en modo oscuro).  
**Equipo:** Álvaro Contreras y Pablo Cortés | Generative Artificial Intelligence (580694) — Facultad de Ingeniería, Universidad de Concepción.  
**Extensión total de locución:** **335 palabras** (dentro del rango estricto de 330 a 340 palabras).  
**Duración objetivo:** **2 minutos y 50 segundos** (170 segundos), dejando 10 segundos de holgura bajo el límite reglamentario de 180 segundos.  
**Ritmo de locución:** Pausado, seguro y natural (~118 a 122 palabras por minuto).

---

## 1. Preparación de Pantalla en Google Colab

Antes de iniciar la grabación con OBS Studio o QuickTime Player (`Cmd + Shift + 5`):
1. **Configuración de pantalla:** Resolución 1080p (1920×1080), escala de fuentes en navegador al 110% o 120% para legibilidad óptima de código y tablas.
2. **Tema de Colab:** Modo oscuro activado (Herramientas → Configuración → Tema del sitio → Dark).
3. **Cuaderno abierto:** [`Deliverable3_Demo_Video.ipynb`](../Deliverable3_Demo_Video.ipynb) con las salidas de las celdas ya ejecutadas previamente para una navegación fluida sin tiempos muertos de cómputo.

---

## 2. Minutaje y Estructura por Secciones

```
[0:00 - 0:30] | Bloque 1: Introducción, Autores y Corpus Normativo (Secciones 1 y 2)
[0:30 - 1:00] | Bloque 2: Arquitectura del Sistema, Grafo y Herramientas (Sección 3)
[1:00 - 1:45] | Bloque 3: Demostración en Vivo: Caso de Titulación P105 (Sección 4)
[1:45 - 2:20] | Bloque 4: Diagnóstico Técnico: Premisas Falsas y Mitigación (Sección 5)
[2:20 - 2:50] | Bloque 5: Auditoría Reproducible y Resultados Finales (Secciones 6 y 7)
```

---

## 3. Guion de Locución y Acciones en Pantalla

### Bloque 1: Introducción y Fundamentos (0:00 – 0:30) | 63 palabras
* **Sección en Colab:** Encabezado y Sección 1 («Preparación del Entorno y Verificación Criptográfica»).
* **Acción en pantalla:** El cursor señala el título institucional y los nombres de los autores (Álvaro Contreras y Pablo Cortés). Luego baja suavemente por la celda de configuración mostrando el modelo `Qwen3-4B` en GPU Tesla T4 (cuantizado en 4-bit NF4) y el corpus cerrado de 197 unidades normativas.
* **Locución (Voz en off):**
> *"Hola. Junto a Álvaro Contreras y Pablo Cortés, presentamos el sistema multiagente para normativas de la Facultad de Ingeniería de la Universidad de Concepción. En el entregable dos usamos un RAG simple de una sola pasada. Para este trabajo implementamos agentes deliberativos con el modelo Qwen3-4B cuantizado en NF4 sobre una GPU Tesla T4, operando sobre un corpus de 197 unidades normativas estructuradas."*

---

### Bloque 2: Arquitectura del Sistema y Herramientas (0:30 – 1:00) | 60 palabras
* **Sección en Colab:** Sección 2 («Grafo de Agentes y Herramientas Normativas»).
* **Acción en pantalla:** Mostrar el diagrama de arquitectura insertado en el cuaderno. El cursor sigue el flujo: `Investigador -> Redactor -> Auditor`, señalando las 3 herramientas normativas (`buscar_normativa`, `leer_articulo`, `inventario`) y los bucles superiores de corrección y parada.
* **Locución (Voz en off):**
> *"En la arquitectura dividimos el trabajo en tres agentes que intercambian contratos JSON. El Investigador busca mediante embeddings E5, lee artículos íntegros e inspecciona inventarios reglamentarios. El Redactor sintetiza la evidencia citando fuentes oficiales. Finalmente, el Auditor verifica el respaldo normativo y los cálculos numéricos; si detecta inconsistencias o alucinaciones, rechaza la respuesta y abre un bucle de corrección supervisado."*

---

### Bloque 3: Demostración en Vivo: Caso de Titulación P105 (1:00 – 1:45) | 77 palabras
* **Sección en Colab:** Sección 3 («Demostración en Vivo: Consulta Compleja de Cálculo (Caso H05 / P105)»).
* **Acción en pantalla:** Se pulsa *Run* o se enfoca la celda del caso P105 (alumno con promedio 5,2 y memoria 6,5). Se despliega el flujo interactivo de logs: la llamada del Investigador recuperando el Artículo 30 del RI-FI, el mensaje JSON intermedio del Redactor aplicando la fórmula $(5{,}2 \times 0{,}6) + (6{,}5 \times 0{,}4) = 5{,}72 \rightarrow 5{,}7$, y la tarjeta de aprobación sin reparos del Auditor.
* **Locución (Voz en off):**
> *"Ejecutamos en vivo la consulta de titulación P105: un estudiante con promedio 5,2 en asignaturas y nota 6,5 en su memoria. En los registros observamos el flujo de mensajes intermedios en JSON. El Investigador recupera el artículo 30. Con esa evidencia, el Redactor aplica la ponderación reglamentaria de sesenta por ciento de asignaturas y cuarenta por ciento de memoria, calculando 5,72, que redondea formalmente a 5,7. El Auditor valida el cálculo aritmético y emite la aprobación final."*

---

### Bloque 4: Diagnóstico Técnico: Premisas Falsas y Mitigación (1:45 – 2:20) | 69 palabras
* **Sección en Colab:** Sección 4 («Diagnóstico Transparente y Resolución de Premisas Falsas»).
* **Acción en pantalla:** Mostrar la caja de la consulta P41, donde el agente ejecuta la herramienta de inventario (`INV-`) y refuta la premisa con evidencia de ausencia. Luego se enfoca el caso P44, explicando visualmente el bloqueo de reintentos (*livelock*) cuando el modelo base 4B insistía en alucinar la norma, y cómo el orquestador resolvió 9 de las 10 consultas mediante consenso semántico.
* **Locución (Voz en off):**
> *"En la evaluación de premisas falsas analizamos el comportamiento ante consultas engañosas. En la pregunta P41, el sistema demuestra formalmente la inexistencia de la norma mediante la herramienta de inventario. En cambio, en P44 el modelo 4B cayó en livelock al alucinar presencia del artículo inexistente. Para resolver esta compensación de diseño, incorporamos consenso semántico en el orquestador, logrando resolver exitosamente nueve de las diez consultas con premisas falsas."*

---

### Bloque 5: Auditoría Reproducible y Resultados Finales (2:20 – 2:50) | 66 palabras
* **Sección en Colab:** Sección 5 («Auditoría Criptográfica Global y Tabla 1 de Resultados»).
* **Acción en pantalla:** Se ejecuta o visualiza la celda de verificación de integridad mostrando los hashes SHA-256 coincidentes para los archivos de prompts. Se enfoca la **Tabla 1** con el **86%** en el conjunto Base (50 consultas), **84%** en el conjunto Difícil (25 consultas), la tasa de **4,5 llamadas** por consulta y el estudio comparativo de ablaciones.
* **Locución (Voz en off):**
> *"Para asegurar reproducibilidad, verificamos los hashes SHA-256 inmutables de los prompts externos. La tabla final registra un desempeño de ochenta y seis por ciento en el conjunto Base de cincuenta preguntas y ochenta y cuatro por ciento en las veinticinco Difíciles, con cuatro coma cinco llamadas promedio a herramientas. El análisis de ablaciones confirma el impacto decisivo del bucle de auditoría en la precisión del sistema."*

---

## 4. Resumen de Métricas de Calibración

| Bloque | Sección en Colab | Tiempo | Palabras | WPM |
| :--- | :--- | :---: | :---: | :---: |
| **B1: Introducción y Setup** | Sec. 1 (Entorno y Corpus) | 0:00 – 0:30 (30 s) | **63** | 126 |
| **B2: Arquitectura y Grafo** | Sec. 2 (Agentes y Herramientas) | 0:30 – 1:00 (30 s) | **60** | 120 |
| **B3: Caso en Vivo (Titulación)** | Sec. 3 (Ejecución P105 / H05) | 1:00 – 1:45 (45 s) | **77** | 103 |
| **B4: Premisas Falsas** | Sec. 4 (Casos P41, P44 y Consenso) | 1:45 – 2:20 (35 s) | **69** | 118 |
| **B5: Auditoría y Cierre** | Sec. 5 (Hashes y Tabla 1) | 2:20 – 2:50 (30 s) | **66** | 132 |
| **TOTAL** | **Cuaderno completo** | **2:50 min** | **335** | **118** |

### Checklist de Cumplimiento
- [x] **0% Clichés de IA:** Eliminadas palabras como "monolítico", "paradigmático", "sinérgico", "holístico", "crucial", "vital", "salto cualitativo", "victorias cualitativas".
- [x] **Tono Humano de Ingeniería:** Redacción fluida, técnica, rigurosa y directa de un estudiante de la UdeC.
- [x] **Sincronización Total con Colab:** El guion sigue exactamente el scroll y las celdas de `Deliverable3_Demo_Video.ipynb`.
- [x] **Duración Segura:** 335 palabras habladas a ritmo relajado equivalen a 2:45 – 2:50 min, con 10 s de margen bajo el límite de 3 min.
