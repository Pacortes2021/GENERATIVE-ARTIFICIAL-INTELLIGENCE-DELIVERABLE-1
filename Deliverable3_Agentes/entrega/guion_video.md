# Guion de Demostración Oficial en Google Colab (≤ 3 Minutos)

**Entregable:** Deliverable 3 — Arquitectura multi-agente con decisiones observables, herramientas normativas y estudio de ablación.  
**Cuaderno de soporte:** `Deliverable3_Agentes/Deliverable3_Demo_Video.ipynb` (Google Colab en modo oscuro).  
**Equipo:** Álvaro Contreras y Pablo Cortés | Generative Artificial Intelligence (580694) — Facultad de Ingeniería, Universidad de Concepción.  
**Extensión total de locución:** **342 palabras** (calibrado a 2 minutos y 50 segundos).  
**Duración objetivo:** **2 minutos y 50 segundos** (170 segundos), dejando 10 segundos de holgura bajo el límite reglamentario de 180 segundos.  
**Ritmo de locución:** Pausado, seguro y natural (~120 palabras por minuto).

---

## 1. Preparación de Pantalla en Google Colab

Antes de grabar:
1. **Configuración de pantalla:** Resolución 1080p (1920×1080), escala de fuentes en navegador al 110% o 120% para legibilidad óptima.
2. **Tema de Colab:** Modo oscuro activado (Herramientas → Configuración → Tema del sitio → Dark).
3. **Cuaderno abierto:** [`Deliverable3_Demo_Video.ipynb`](../Deliverable3_Demo_Video.ipynb) con las salidas de las celdas ya ejecutadas dinámicamente desde las trazas y datos reales del repositorio.

---

## 2. Minutaje y Estructura por Secciones

```text
[0:00 - 0:30] | Bloque 1: Introducción, Autores y Corpus Normativo
[0:30 - 1:00] | Bloque 2: Arquitectura del Sistema, Grafo y Herramientas
[1:00 - 1:45] | Bloque 3: Inspección de Traza Real: Caso de Titulación P105 (H05)
[1:45 - 2:20] | Bloque 4: Diagnóstico Técnico: Premisas Falsas, Inventario y Consenso (P041)
[2:20 - 2:50] | Bloque 5: Auditoría Criptográfica, Tabla 1 Oficial y Estudio de Ablación
```

---

## 3. Guion de Locución y Acciones en Pantalla

### Bloque 1: Introducción y Fundamentos (0:00 – 0:30) | 60 palabras
* **Sección en Colab:** Encabezado y Sección 1 («Verificación Criptográfica Dinámica de Prompts Versionados»).
* **Acción en pantalla:** El cursor señala el título institucional y los nombres de los autores (Álvaro Contreras y Pablo Cortés). Luego baja suavemente por el encabezado mostrando la configuración con el modelo `Qwen3-4B` en GPU Tesla T4 (cuantizado en 4-bit NF4) y el corpus de 197 unidades normativas.
* **Locución (Voz en off):**
> *"Hola, somos Álvaro Contreras y Pablo Cortés. Presentamos nuestro sistema multi-agente para normativas de la Facultad de Ingeniería de la Universidad de Concepción. Mientras en el entregable dos usamos un RAG de una sola pasada, aquí implementamos tres agentes deliberativos con Qwen3-4B cuantizado en NF4 sobre GPU Tesla T4, operando sobre un corpus de 197 unidades normativas."*

---

### Bloque 2: Arquitectura del Sistema y Herramientas (0:30 – 1:00) | 64 palabras
* **Sección en Colab:** Sección 2 («Arquitectura del Sistema: Grafo de Tres Agentes y Herramientas Normativas»).
* **Acción en pantalla:** Mostrar el diagrama de arquitectura y flujo del cuaderno. El cursor sigue el recorrido: `Investigador -> Redactor -> Auditor`, señalando las 3 herramientas normativas (`buscar_normativa`, `leer_articulo`, `inventario`) y los bucles superiores de corrección y parada.
* **Locución (Voz en off):**
> *"Dividimos el trabajo en tres agentes coordinados por contratos JSON. El Investigador descompone consultas y consulta herramientas normativas: embeddings E5, lectura de artículos e inventario reglamentario. El Redactor sintetiza la respuesta con citas oficiales. Y el Auditor verifica extracto por extracto el respaldo documental y los cálculos; si detecta inconsistencias o alucinaciones, rechaza el borrador y abre un bucle de corrección supervisado."*

---

### Bloque 3: Inspección de Traza Real: Caso de Titulación P105 (1:00 – 1:45) | 76 palabras
* **Sección en Colab:** Sección 2 del cuaderno («Inspección de Traza Real: Caso H05 / P105 - Cálculo Numérico de Titulación»).
* **Acción en pantalla:** El cursor enfoca la celda que lee el archivo de traza real `P105_agentes_completo_...jsonl`. Se despliega la salida estructurada: la llamada a `buscar_normativa`, el mensaje del Investigador citando el Artículo 30 del RI-FI, el cálculo intermedio del Redactor aplicando $(5{,}2 \times 0{,}6) + (6{,}5 \times 0{,}4) = 5{,}72 \rightarrow 5{,}7$, y la validación final del Auditor.
* **Locución (Voz en off):**
> *"Revisamos la traza real registrada en GPU T4 para la consulta P105: un estudiante con promedio 5,2 y nota 6,5 en su memoria de título. En los eventos observamos el flujo observable en JSON. El Investigador recupera el artículo 30 del RI-FI. Con esa evidencia, el Redactor aplica la ponderación de sesenta por ciento de asignaturas y cuarenta de memoria, calculando 5,72 que aproxima a 5,7. El Auditor valida el cálculo aritmético y emite la aprobación final."*

---

### Bloque 4: Diagnóstico Técnico: Premisas Falsas y Mitigación (1:45 – 2:20) | 72 palabras
* **Sección en Colab:** Sección 3 del cuaderno («Inspección de Premisas Falsas Resueltas: Caso P041 - Artículo 90 Inexistente»).
* **Acción en pantalla:** El cursor enfoca la celda que lee la traza real de P041. Muestra cómo el Investigador consulta el inventario reglamentario constatando que el RI-FI solo posee 35 artículos, y cómo el Auditor valida formalmente `{"existe": false}` aceptando la abstención justificada.
* **Locución (Voz en off):**
> *"En premisas falsas y normas inexistentes, evaluamos la capacidad de abstención del sistema. En la pregunta P41 sobre un supuesto artículo 90, el Investigador constata con el inventario que el reglamento solo posee 35 artículos. El Auditor valida formalmente esa ausencia, evitando el bloqueo o livelock observado en pruebas preliminares. Con esta alineación y el consenso semántico en el orquestador, el sistema resolvió exitosamente nueve de las diez premisas falsas."*

---

### Bloque 5: Auditoría Criptográfica, Tabla 1 Oficial y Cierre (2:20 – 2:50) | 70 palabras
* **Sección en Colab:** Sección 1 (celda de hashes) y Sección 4 («Auditoría de Métricas Experimentales y Estudio de Ablación»).
* **Acción en pantalla:** Mostrar la salida de los hashes SHA-256 calculados en vivo sobre los archivos `.txt` de prompts. Luego enfoca la salida de la **Tabla 1 Oficial**: **86%** en Base (50 consultas), **84%** en Difícil (25 consultas), el promedio de **4,48 inferencias LLM por consulta** y el impacto comparativo de las variantes de ablación.
* **Locución (Voz en off):**
> *"Para reproducibilidad, la celda calcula dinámicamente los hashes SHA-256 de los seis prompts en disco. La tabla final registra un desempeño de ochenta y seis por ciento en el conjunto Base y ochenta y cuatro por ciento en las veinticinco consultas Difíciles, con cuatro coma cinco llamadas de inferencia de modelo por consulta. El estudio de ablación confirma la contribución del bucle de auditoría y la descomposición ante razonamientos complejos."*

---

## 4. Resumen de Métricas de Calibración

| Bloque | Sección en Colab | Tiempo | Palabras | WPM |
| :--- | :--- | :---: | :---: | :---: |
| **B1: Introducción y Setup** | Sec. 1 (Entorno y Corpus) | 0:00 – 0:30 (30 s) | **60** | 120 |
| **B2: Arquitectura y Grafo** | Sec. 2 (Agentes y Herramientas) | 0:30 – 1:00 (30 s) | **64** | 128 |
| **B3: Traza Real P105 (Titulación)**| Sec. 3 (Inspección P105 / H05) | 1:00 – 1:45 (45 s) | **76** | 101 |
| **B4: Premisa Falsa P041** | Sec. 4 (Inventario y Consenso) | 1:45 – 2:20 (35 s) | **72** | 123 |
| **B5: Auditoría y Cierre** | Sec. 5 (Hashes y Tabla 1) | 2:20 – 2:50 (30 s) | **70** | 140 |
| **TOTAL** | **Cuaderno completo** | **2:50 min** | **342** | **121** |

### Checklist de Cumplimiento
- [x] **0% Falsas Afirmaciones:** Eliminado "ejecutamos en vivo". Se transparenta que se inspeccionan las trazas reales registradas en GPU T4.
- [x] **Hashes Dinámicos Reales:** La celda calcula SHA-256 con `hashlib` sobre los 6 prompts versionados en disco.
- [x] **Métrica Exacta:** Corregido "llamadas a herramientas" por "llamadas de inferencia de modelo por consulta" (4,48 llamadas/q).
- [x] **Identidad Natural:** Iniciado con "Somos Álvaro Contreras y Pablo Cortés...".
- [x] **Tono Humano y Riguroso:** Sin términos dogmáticos ni soberbia técnica.
- [x] **Duración Segura:** 342 palabras a ritmo natural equivalen a 2:48 – 2:50 min, con 10 s de margen bajo el límite de 3 min.
