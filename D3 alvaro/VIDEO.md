# Video D3

- [Abrir el notebook en Colab](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/D3%20alvaro/Deliverable3/Demo_D3.ipynb).
- [Notebook en el repositorio](Deliverable3/Demo_D3.ipynb).
- [Guion con tiempos y narración](Guion_video_D3.md).

## Uso

1. En Colab con T4, ejecutar A1–A5 antes de grabar. El paquete se descarga del repositorio y se comprueba contra el manifiesto del mismo commit.
2. Grabar B0–B4: arquitectura, dos consultas nuevas, fallo histórico H03 y resultados provisionales.
3. Ejecutar C1 al terminar. Confirmar los identificadores de las ejecuciones del video y descargar el ZIP de evidencia.
4. Incorporar el ZIP en `evidencia_video/`, publicar una grabación de hasta tres minutos con acceso abierto y añadir su enlace al informe.

Las consultas nuevas usan Qwen3-4B, corpus, prompts y controlador v6 sin cambios. El módulo
`Deliverable3/video/soporte_video.py` añade visualización y registro de prompts completos, salidas crudas,
resultados de herramientas y entorno. Las trazas históricas siguen siendo resumidas y se identifican como históricas.

Las pruebas locales verifican la instrumentación con un modelo simulado y equivalencia de salida/traza con
el controlador original. No sustituyen comprobar la carga de modelos ni la inferencia en Colab con GPU.

**Estado:** notebook y guion preparados; grabación, evidencia de la ejecución GPU y enlace público pendientes.
