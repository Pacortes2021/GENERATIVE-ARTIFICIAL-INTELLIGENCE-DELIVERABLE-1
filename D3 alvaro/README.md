# D3 Álvaro — sistema de cuatro agentes, versión v6

Esta carpeta integra el trabajo de cuatro agentes sin modificar su controlador ni los prompts evaluados.
El sistema anterior de Pablo permanece en `../Deliverable3_Agentes/`, con sus resultados independientes.
No se mezclaron respuestas ni porcentajes de ambos sistemas.

## Archivos principales

- [Informe técnico](Deliverable3/documento/main.pdf): una página vertical en LaTeX; [fuente](Deliverable3/documento/main.tex).
- [Notebook completo](Deliverable3/D3_colab_qwen3_4b.ipynb): completo v6, 75 preguntas por defecto.
- [Notebook de demostración](Deliverable3/Demo_D3.ipynb): consulta real con mensajes visibles y fallo histórico identificado.
- [Paquete para Colab](D3_alvaro_ejecucion.zip): subir este ZIP cuando lo solicite el notebook.
- [Guía del video](VIDEO.md): grabación de menos de tres minutos.
- [Auditoría y limitaciones](AUDITORIA.md).
- [Archivo original sin modificar](D3_nuestro_completo_original.zip).

## Reproducir

1. Abrir el notebook completo en Google Colab y seleccionar una GPU T4.
2. Ejecutar las celdas de preparación y subir `D3_alvaro_ejecucion.zip` en el Paso 2.
3. Las consultas individuales sirven para comprobar el sistema. No son los resultados del lote.
4. Para el lote, conservar `ABLACION = None` y `SOLO_DIFICILES = False`.
5. Conectar Drive en su celda. Cada intento crea una carpeta nueva. Para reanudar, pegar su ruta en
   `REANUDAR_CARPETA`; se verifican fuentes, configuración, versiones y revisión del modelo.
6. Ejecutar el lote y conservar CSV, trazas y `configuracion_reproduccion.json`.
7. Calificar las respuestas nuevas con la pauta; no reutilizar las etiquetas históricas.

Para las ablaciones, cambiar `ABLACION` por `sin_fewshot`, `sin_react`, `sin_cot` o `sin_verificador`.
Cada variante tiene una carpeta independiente. Los pesos y las dependencias de la corrida original no
quedaron fijados completamente: la nueva reproducción registra el entorno, pero no promete resultados idénticos.

## Resultados históricos, sin nueva inferencia

| Condición | 50 originales | 25 difíciles |
|---|---:|---:|
| Directo | 1/50 | 0/25 |
| RAG D2 | 40/50 | 16/25 |
| Cuatro agentes v6 | 46/50 | 20/25 |
| Sin few-shot | 44/50 | 19/25 |
| Sin ReAct | 45/50 | 18/25 |
| Sin CoT del Redactor | 46/50 | 19/25 |
| Sin Verificador, primer borrador de v6 | 44/50 | 19/25 |

Correcciones asistidas por Claude; nueve filas de v6 siguen marcadas `REVISAR` en la planilla original.
El criterio externo evalúa el texto final aunque el Verificador no lo apruebe. La aceptación interna no mide exactitud.
El costo corregido del completo es 711 llamadas / 75 = 9,48 llamadas por pregunta.
El archivo original conserva todos los documentos y cifras anteriores para poder contrastar los cambios.

## Verificación sin GPU

Desde la raíz del repositorio:

```bash
python3 'D3 alvaro/auditar.py'
python3 'D3 alvaro/Deliverable3/agentes/demo_mock.py'
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
cd 'D3 alvaro/Deliverable3/documento'
tectonic grafo_compacto.tex
tectonic main.tex
pdfinfo main.pdf
```
