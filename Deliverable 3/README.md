# Deliverable 3 — agentes para consultas de normativa de pregrado

Esta carpeta integra el trabajo de cuatro agentes sin modificar su controlador ni los prompts evaluados.
El sistema anterior de Pablo permanece en `../Deliverable3_Agentes/`, con sus resultados independientes.
No se mezclaron respuestas ni porcentajes de ambos sistemas.

## Archivos principales

- [Informe técnico](Deliverable3/documento/main.pdf): una página vertical en LaTeX; [fuente](Deliverable3/documento/main.tex).
- [Notebook completo](Deliverable3/D3_colab_qwen3_4b.ipynb): completo v6, 75 preguntas por defecto.
- [Notebook de demostración](Deliverable3/Demo_D3.ipynb): grafo, roles y consulta compleja H17 con mensajes visibles, registro íntegro nuevo y fallo histórico H03 identificado.
- [Paquete para Colab](Deliverable3_ejecucion.zip): subir este ZIP cuando lo solicite el notebook.
- [Guía del video](VIDEO.md) y [guion con narración](Guion_video_D3.md): grabación de hasta tres minutos.
- [Auditoría y limitaciones](AUDITORIA.md).
- [Archivo original sin modificar](D3_nuestro_completo_original.zip).

## Reproducir

1. Abrir el notebook completo en Google Colab y seleccionar una GPU T4.
2. Ejecutar las celdas de preparación y subir `Deliverable3_ejecucion.zip` en el Paso 2.
3. Las consultas individuales sirven para comprobar el sistema. No son los resultados del lote.
4. Para el lote, conservar `ABLACION = None` y `SOLO_DIFICILES = False`.
5. Conectar Drive en su celda. Cada intento crea una carpeta nueva. Para reanudar, pegar su ruta en
   `REANUDAR_CARPETA`; se verifican fuentes, configuración, versiones y revisión del modelo.
6. Ejecutar el lote y conservar CSV, trazas y `configuracion_reproduccion.json`.
7. Calificar las respuestas nuevas con la pauta; no reutilizar las etiquetas históricas.

Para las ablaciones, cambiar `ABLACION` por `sin_fewshot`, `sin_react`, `sin_cot` o `sin_verificador`.
Cada variante tiene una carpeta independiente. Los pesos y las dependencias de la corrida original no
quedaron fijados completamente: la nueva reproducción registra el entorno, pero no promete resultados idénticos.

## Grabar el video

Abrir [Demo_D3 en Colab](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%203/Deliverable3/Demo_D3.ipynb).
Ejecutar A1–A5 con T4 antes de grabar; grabar B0–B3; usar C1 para descargar la evidencia.
El notebook descarga el paquete y verifica su hash. La opción de carga manual queda disponible.
El [guion](Guion_video_D3.md) explica qué mostrar y narrar. No se ha ejecutado esta nueva demo en GPU durante la preparación.

## Resultados históricos, sin nueva inferencia

| Condición | 50 originales | 25 difíciles |
|---|---:|---:|
| Directo | 1/50 | 0/25 |
| RAG D2 | 40/50 | 16/25 |
| Sistema completo | 46/50 | 20/25 |
| Sin few-shot | 44/50 | 19/25 |
| Sin ReAct | 45/50 | 18/25 |
| Sin CoT del Redactor | 46/50 | 19/25 |
| Sin Verificador, primer borrador de v6 | 44/50 | 19/25 |

Calificación propuesta con apoyo de Claude y revisada por el equipo, según su confirmación del 31 de octubre de 2026. Las planillas originales se conservan sin cambios; sus antiguas marcas `REVISAR` no describen el estado actual de esa revisión.
El criterio externo evalúa el texto final aunque el Verificador no lo apruebe. La aceptación interna no mide exactitud.
El costo corregido del completo es 711 llamadas / 75 = 9,48 llamadas por pregunta.
El archivo original conserva todos los documentos y cifras anteriores para poder contrastar los cambios.

## Verificación sin GPU

Desde la raíz del repositorio:

```bash
python3 'Deliverable 3/auditar.py'
python3 'Deliverable 3/Deliverable3/agentes/demo_mock.py'
python3 'Deliverable 3/Deliverable3/video/test_soporte_video.py'
```

La auditoría usa solo la biblioteca estándar de Python. Comprueba hashes, las 75 preguntas comunes,
correspondencia planilla exportada/CSV/traza y conteos; no recalifica las respuestas contra el corpus.
El demo contiene 29 comprobaciones con un modelo simulado; no mide exactitud de Qwen.

## Estado de entrega

La carpeta integra el sistema v6 y sus materiales. **El video real de D3 y su enlace público siguen pendientes.**
El PDF lo indica expresamente. No se reutiliza el video de D2 ni se presenta una reproducción de trazas como inferencia nueva.
Esta es la carpeta que debe consultarse para reproducir el sistema de cuatro agentes; el otro sistema conserva su carpeta independiente.

Para recompilar el informe (Tectonic):

```bash
cd 'Deliverable 3/Deliverable3/documento'
tectonic grafo_compacto.tex
tectonic main.tex
pdfinfo main.pdf
```
