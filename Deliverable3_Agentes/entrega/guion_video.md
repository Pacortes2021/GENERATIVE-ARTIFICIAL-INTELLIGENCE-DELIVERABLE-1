# Guion del Video Oficial — Entregable 3 (≤ 3 minutos)

**Cuaderno:** `Deliverable3_Demo_Video.ipynb` (exploración no entregada; el cuaderno no se subió al repositorio)  
**Entorno:** Google Colab con acelerador GPU Tesla T4 (o ejecución previa para recorrido fluido).  
**Equipo:** Álvaro Contreras y Pablo Cortés | Generative Artificial Intelligence (580694) — UdeC.  
**Extensión total:** **327 palabras** (~2 min 45 s a ritmo pausado y tranquilo, ~119 ppm).  

---

## Estructura por Secciones y Minutaje

```text
[0:00 – 0:25] | Secciones 1 y 2: Presentación institucional y verificación de prompts
[0:25 – 0:45] | Sección 3: Reparto de trabajo entre los tres agentes (Grafo)
[0:45 – 1:25] | Secciones 4 y 5: Demostración Caso de Cálculo (H05 - Titulación 60/40)
[1:25 – 1:50] | Sección 5: Demostración Premisa Falsa (P41 - Artículo 90 inexistente)
[1:50 – 2:20] | Sección 6: Demostración Caso de Falla (P44 - Salidas inválidas y detención)
[2:20 – 2:50] | Sección 7: Resultados experimentales (Tabla 1) y análisis transparente
```

---

## Guion de Locución y Acciones en Pantalla

### [0:00 – 0:25] Secciones 1 y 2: Presentación y Prompts
* **Pantalla:** Título del cuaderno en Colab; luego la salida con los seis prompts y «coincide».
* **Locución (Voz en off):**
> *"Somos Álvaro Contreras y Pablo Cortés. Nuestro asistente responde preguntas sobre los reglamentos de pregrado de Ingeniería UdeC, siempre citando el artículo. En el Entregable 2 era un RAG de una sola llamada; ahora son tres agentes que usan el mismo modelo, Qwen3-4B. Este cuaderno descarga nuestro repositorio y muestra trazas reales que el sistema guardó al correr en Colab. Primero comprobamos que los prompts de cada agente son los mismos con los que se corrió."*

---

### [0:25 – 0:45] Cómo se reparte el trabajo
* **Pantalla:** Sección 3 (diagrama de flujo de agentes) o el grafo del informe.
* **Locución (Voz en off):**
> *"El Investigador busca en los reglamentos con herramientas. El Redactor escribe la respuesta usando solo esa evidencia. El Auditor revisa que cada afirmación esté respaldada por un extracto real; si no lo está, la devuelve o pide buscar más."*

---

### [0:45 – 1:25] Sección 4: Caso de cálculo
* **Pantalla:** Recorrer las cajas de H05 de arriba abajo.
* **Locución (Voz en off):**
> *"Primera pregunta: memoria con 6,5 y promedio 5,2, ¿cuál es la nota de titulación? El Investigador busca y encuentra el artículo 30. Se lo pasa al Redactor, que calcula sesenta por ciento de 5,2 más cuarenta por ciento de 6,5: 5,72. El Auditor compara con el texto del artículo y acepta. El RAG del Entregable 2 había respondido 5,6."*

---

### [1:25 – 1:50] Sección 5: Premisa falsa
* **Pantalla:** Cajas de P41.
* **Locución (Voz en off):**
> *"Ahora una trampa: el artículo 90 del reglamento interno, que no existe. Con el inventario del documento, los tres agentes concluyen que no existe, y el Auditor lo acepta sin inventar contenido."*

---

### [1:50 – 2:20] Sección 6: Caso de falla
* **Pantalla:** Cajas de P44; detenerse en las tres salidas inválidas en rojo.
* **Locución (Voz en off):**
> *"Y un caso que falla: el artículo 70 del Reglamento General, que tampoco existe. Aquí el modelo afirma que sí está en el inventario. El Auditor responde tres veces con un formato inválido y el sistema se detiene sin respuesta validada. No inventa, pero tampoco responde."*

---

### [2:20 – 2:50] Sección 7: Resultados
* **Pantalla:** La tabla impresa.
* **Locución (Voz en off):**
> *"Con el mismo código para todas las condiciones, los agentes aciertan 34 de 50 y 11 de 25 difíciles, por debajo del RAG del Entregable 2, y quitar una técnica no cambia mucho. Después corregimos el validador y corrimos de nuevo solo el sistema completo: 21 de 25 difíciles y 9 de 10 premisas falsas, pero esas mejoras no tienen ablación propia."*

---

### Resumen de Calibración
* **Palabras totales:** 327 palabras.
* **Velocidad de locución:** ~119 palabras por minuto (ritmo tranquilo, natural y claro).
* **Duración objetivo:** 2 minutos y 45 segundos (con 15 segundos de margen seguro bajo los 3 minutos).
