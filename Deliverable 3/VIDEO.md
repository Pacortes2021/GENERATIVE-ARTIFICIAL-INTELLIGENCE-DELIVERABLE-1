# Video D3

- [Video de la demostración](https://drive.google.com/drive/folders/1tkhRhI4_G7ArWNHW7zNoeZi8lL9RyPf2?usp=sharing) (≤ 3 minutos, acceso abierto).
- [Abrir el notebook en Colab](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%203/Deliverable3/Demo_D3.ipynb).
- [Notebook en el repositorio](Deliverable3/Demo_D3.ipynb).
- [Guion con tiempos y narración](Guion_video_D3.md).

La consulta H17 combina la regla de asistencia, sus excepciones y regímenes especiales. El fallo H03 exige cuatro fechas, dos intervalos y una comparación. El grafo del informe y las funciones de los cuatro roles se muestran en B0. Las instrucciones de preparación, grabación y solución de errores están en el guion.

## Uso

1. En Colab con T4, ejecutar A1–A5 (preparación). El paquete se descarga de una versión fija del repositorio y se comprueba contra el manifiesto del mismo commit.
2. Ejecutar B0–B3, que es lo que muestra el video: grafo y roles, consulta compleja H17 en ejecución real, fallo histórico H03 y resultados revisados por el equipo.
3. Ejecutar C1 para descargar el ZIP de evidencia con los identificadores de cada ejecución; se guarda en [`evidencia_video/`](evidencia_video/README.md).

La consulta nueva usa Qwen3-4B, corpus, prompts y controlador v6 sin cambios. El módulo
`Deliverable3/video/soporte_video.py` añade visualización y registro de prompts completos, salidas crudas,
resultados de herramientas y entorno. Las trazas históricas siguen siendo resumidas y se identifican como históricas.

Las pruebas locales verifican la instrumentación con un modelo simulado y equivalencia de salida/traza con
el controlador original. No sustituyen comprobar la carga de modelos ni la inferencia en Colab con GPU.

**Estado:** video grabado y publicado; su enlace está arriba y en el informe.
