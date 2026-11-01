# Video demostrativo · Entregable 3

- **[Ver video en Google Drive (acceso abierto)](https://drive.google.com/drive/folders/1tkhRhI4_G7ArWNHW7zNoeZi8lL9RyPf2?usp=sharing)**
- [Abrir el notebook en Colab](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/Deliverable%203/Deliverable3/Demo_D3.ipynb).
- [Notebook en el repositorio](Deliverable3/Demo_D3.ipynb).
- [Guion con tiempos y narración](Guion_video_D3.md).

La consulta H17 combina la regla de asistencia, sus excepciones y regímenes especiales. El fallo H03 exige cuatro fechas, dos intervalos y una comparación. El grafo del informe y las funciones de los cuatro roles se muestran en B0. Las instrucciones de preparación, grabación y solución de errores están en el guion.

## Uso

1. En Colab con T4, ejecutar A1–A5 antes de grabar. El paquete se descarga de una versión fija del repositorio y se comprueba contra el manifiesto del mismo commit. Las copias antiguas que aún usan `D3 alvaro` deben reemplazarse por este notebook.
2. Grabar B0–B3: grafo y roles, consulta compleja H17 en ejecución real, fallo histórico H03 y resultados revisados por el equipo.
3. Ejecutar C1 al terminar. Confirmar los identificadores de las ejecuciones del video y descargar el ZIP de evidencia.
4. Incorporar el ZIP en `evidencia_video/`, publicar una grabación de hasta tres minutos con acceso abierto y añadir su enlace al informe.

La consulta nueva usa Qwen3-4B, corpus, prompts y controlador v6 sin cambios. El módulo
`Deliverable3/video/soporte_video.py` añade visualización y registro de prompts completos, salidas crudas,
resultados de herramientas y entorno. Las trazas históricas siguen siendo resumidas y se identifican como históricas.

Las pruebas locales verifican la instrumentación con un modelo simulado y equivalencia de salida/traza con
el controlador original. No sustituyen comprobar la carga de modelos ni la inferencia en Colab con GPU.

**Estado:** Video grabado, auditado y publicado con acceso abierto en Google Drive. El enlace oficial está incorporado en los informes técnicos de entrega.
