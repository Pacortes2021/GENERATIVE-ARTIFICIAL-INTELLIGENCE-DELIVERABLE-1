# Materiales Oficiales de Entrega — Deliverable 3

**Generative Artificial Intelligence (580694) · Semestre Primavera 2026**  
**Equipo:** Álvaro Contreras y Pablo Cortés  
**Repositorio:** [github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1](https://github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1)

---

## 1. Documento Técnico Oficial (1 página A4 en LaTeX)

- **PDF compilado:** [`main.pdf`](main.pdf) (y copia oficial [`Informe_tecnico_D3.pdf`](Informe_tecnico_D3.pdf)).
  - Verificado: exactamente **1 página A4 vertical**, sin desbordes.
- **Fuente LaTeX:** [`main.tex`](main.tex) (y copia [`Informe_tecnico_D3.tex`](Informe_tecnico_D3.tex)).
- **Contenido:** Grafo de agentes con contratos JSON y herramientas normativas, técnicas de prompting, tabla de ablación controlada vs. sistema final, análisis cualitativo y compensación de costes en GPU Tesla T4.

### Compilar y verificar localmente:
```bash
tectonic Deliverable3_Agentes/entrega/main.tex
python3 -c "import fitz; doc = fitz.open('Deliverable3_Agentes/entrega/main.pdf'); print('Páginas:', len(doc))"
```

---

## 2. Demostración en Video (≤ 3 minutos)

El video muestra la ejecución real del sistema multi-agente en Google Colab sobre GPU Tesla T4, evidenciando las decisiones intermedias, las herramientas y las trazas completas:

1. **Caso de cálculo multi-salto (H05):** Ponderación de titulación 60/40 (RI-FI Art. 30), resolviendo $0{,}6 \times 5{,}2 + 0{,}4 \times 6{,}5 = 5{,}72$ donde RAG D2 falló.
2. **Caso de premisa falsa (P41):** Consulta sobre el Art. 90 inexistente; constatación de ausencia mediante catálogo e inventario oficial (`INV-RG-CATALOGO`).
3. **Caso de falla presupuestaria (P44):** Límite de 3 salidas inválidas del Auditor ante un artículo inexistente alucinado por el modelo 4B, culminando en abstención controlada sin inventar contenido.
4. **Tabla de resultados consolidados:** Resumen comparativo en vivo.

- **Duración del video:** 2 minutos y 50 segundos (dentro del límite estricto de 3 minutos).
- **Archivos locales de video:**
  - Con locución/audio guía: [`video_demostracion_colab_con_audio_guia.mp4`](video_demostracion_colab_con_audio_guia.mp4) (27 MB).
  - Pista muda (para locución directa): [`video_demostracion_colab_mudo.mp4`](video_demostracion_colab_mudo.mp4) (25 MB).
- **Enlace de acceso abierto:** Disponible en Google Drive (enlace en el encabezado de [`main.pdf`](main.pdf)).

---

## 3. Cuaderno de Demostración y Reproducibilidad

- **Cuaderno del video:** [`Deliverable3_Demo_Video.ipynb`](../Deliverable3_Demo_Video.ipynb).
  - Ejecutable en Google Colab con GPU Tesla T4 (NF4, sin thinking).
  - Muestra paso a paso la verificación de hashes SHA-256 de los prompts externos, la inicialización del modelo, la ejecución en vivo de los casos y el renderizado visual de trazas.

---

## 4. Resultados Empíricos Consolidados

Evaluación comparativa rigurosa bajo la pauta estricta oficial (`LEEME_PAUTA.md` y criterios D2):

| Configuración Experimental | Lote Base (50) | Set Difícil (25) | Coste (Llam./q) | Latencia Media |
|---|:---:|:---:|:---:|:---:|
| **Baseline Directo (E1)** | 1 / 50 (2,0%) | 0 / 25 (0,0%) | 1,0 llam. | 6,7 s |
| **RAG Monolítico (E2)** | 40 / 50 (80,0%) | 16 / 25 (64,0%) | 1,0 llam. | 15,1 s |
| **Diseño Factorial Controlado (Versión Base):** | | | | |
| \quad Multi-Agente base | 34 / 50 (68,0%) | 11 / 25 (44,0%) | 5,1 llam. | 152,3 s |
| \quad -- `sin_descomposicion` | 34 / 50 (68,0%) | 14 / 25 (56,0%) | 5,4 llam. | 161,5 s |
| \quad -- `sin_completitud` | 34 / 50 (68,0%) | 12 / 25 (48,0%) | 5,2 llam. | 142,1 s |
| \quad -- `sin_verificacion` | 32 / 50 (64,0%) | 14 / 25 (56,0%) | 4,9 llam. | 139,2 s |
| **Multi-Agente Final (E3 Optimizado):** | **43 / 50 (86,0%)** | **18 / 25 (72,0%)\*** | **4,5 llam.** | **133,0 s** |

*\*Nota:* En el set difícil, el Auditor aceptó internamente 21/25 (84,0%), pero bajo la pauta externa estricta se obtienen 18/25 (72,0%) al penalizarse H07 (cálculo sin división por 4 semestres), H12 (plazo de baja académica en vez de no inscripción) y H23 (confusión de fecha de inscripción con inicio de clases).

---

## 5. Pruebas Unitarias de Regresión

El sistema cuenta con una suite completa de **40 pruebas unitarias automatizadas** que verifican el cumplimiento del contrato JSON, la contención del presupuesto, el grafo de decisiones, el bloqueo de citas inventadas y la prevención de falsos consensos:

```bash
python3 -m unittest discover -s Deliverable3_Agentes/tests -v
```
Todas las pruebas pasan en runtime sin requerir descarga de modelos ni GPU.
