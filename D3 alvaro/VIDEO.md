# Video de D3 — máximo tres minutos

Usar `Deliverable3/Demo_D3.ipynb` en Colab con una T4. Cargar paquetes, corpus y modelos antes
de empezar a grabar. La grabación debe mostrar ejecución real; no cambiar las salidas ni presentar
el fallo histórico como una ejecución nueva.

## Guion sugerido

- **0:00–0:20:** explicar la tarea y mostrar el grafo del informe. Cuatro roles, un Qwen3-4B.
- **0:20–1:40:** ejecutar la celda de consulta real. Mostrar pregunta, mensajes de agentes y resultado.
  La pregunta corta por defecto pide la nota mínima de aprobación. El tiempo puede variar.
- **1:40–2:15:** mostrar el fallo H03 desde su traza guardada, rotulado como histórico.
  Explicar que no recuperó todas las fechas y agotó el ciclo de corrección.
- **2:15–2:50:** mostrar la tabla del informe. Aclarar que son correcciones externas propuestas,
  que la aprobación del Verificador no es exactitud y que las diferencias entre ablaciones son pequeñas.

Si la consulta tarda demasiado, elegir una grabación nueva con el modelo ya cargado. No inventar tiempos
ni ocultar un fallo. Se puede editar preparación y esperas, señalando los cortes si los hay.

## Conservación y publicación

La celda real guarda `demo_consulta_real.json` con pregunta, respuesta y traza del caso ejecutado.
Descargarlo y conservarlo en esta carpeta junto a una nota del entorno utilizado. La traza H03 ya está
en `Deliverable3/resultados_v6/trazas_D3.json`, clave `dificil_25:H03`.

Subir el video real a un servicio con acceso abierto, comprobar que dure como máximo tres minutos
y reemplazar `\\VIDEO` en `Deliverable3/documento/main.tex`. Recompilar, revisar que siga siendo una página
y actualizar el estado del README. El video y su enlace no se han generado en esta preparación.
