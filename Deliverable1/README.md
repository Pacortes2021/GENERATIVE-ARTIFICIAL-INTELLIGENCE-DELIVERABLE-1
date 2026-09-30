# Deliverable 1 · Base del proyecto

Esta carpeta reúne el desarrollo de la entrega 1. El informe, los dos notebooks finales y los tres CSV se reubicaron sin modificar su contenido. `INVENTARIO.json` registra sus rutas anteriores y hashes SHA-256.

La [revisión completa de E1](REVISION.md) contrasta el informe, las 50 referencias, las respuestas y el código. Documenta las limitaciones del resultado publicado sin modificar los archivos históricos.

## Material principal

| Archivo | Contenido |
| --- | --- |
| [enunciado.pdf](enunciado.pdf) | Requisitos y rúbrica de la entrega 1 |
| [informe/deliverable1.pdf](informe/deliverable1.pdf) | Informe presentado: tarea, diagnóstico, candidatos y viabilidad |
| [notebooks/baseline_normativa_ingenieria.ipynb](notebooks/baseline_normativa_ingenieria.ipynb) | Qwen3-4B: prompting directo, 50 preguntas, salidas y calificación |
| [notebooks/baseline_normativa_ingenieria_8b.ipynb](notebooks/baseline_normativa_ingenieria_8b.ipynb) | Comparación con Qwen3-8B cuantizado a 4 bits |
| [datos/test_set_50.csv](datos/test_set_50.csv) | Preguntas, categorías, respuestas de referencia y fuentes |
| [datos/resultados_baseline.csv](datos/resultados_baseline.csv) | Respuestas y veredictos guardados del experimento de 4B |
| [datos/respuestas_baseline_8b.csv](datos/respuestas_baseline_8b.csv) | Respuestas guardadas de 8B; la calificación está en su notebook |

El corpus compartido está en [../Corpus](../Corpus): Reglamento General, Reglamento Interno de Ingeniería y Calendario de Docencia 2026.

## Qué quedó establecido en E1

El modelo recibe una pregunta en español sin los documentos normativos. Se le solicita el dato, una cita y abstención cuando no tenga la información. La inferencia usa generación greedy y desactiva el modo thinking.

El informe propone Qwen3-4B, Salamandra-7B y Qwen3-8B; el experimento principal utiliza Qwen3-4B. Los notebooks registran ejecución en Google Colab con Tesla T4. El 4B usa carga automática y el 8B cuantización a 4 bits.

La cifra publicada del baseline principal es **2/50 (4%)**: dos aciertos de abstención y cero aciertos en las 40 consultas con respuesta. El notebook de 8B también registra 2/50, pero corresponde a un acierto factual y uno de abstención. Estos son los resultados declarados en E1, conservados como punto de partida.

## Abrir o repetir los experimentos

1. Abrir el notebook de `notebooks/` en Google Colab; puede subirse el archivo desde el diálogo de apertura.
2. Seleccionar un entorno con GPU T4 y ejecutar las celdas en orden. Requiere conexión para instalar dependencias y descargar los pesos.
3. Las 50 preguntas están incluidas en el propio notebook, por lo que mover el archivo a esta carpeta no rompe su ejecución.
4. Los CSV generados se escriben en el directorio de ejecución de Colab. Descargarlos desde su panel de archivos y conservar cada corrida nueva por separado.

Los notebooks se preservan tal como se entregaron: las versiones exactas de dependencias y pesos no quedaron fijadas. Una nueva ejecución puede producir respuestas distintas. No reemplazar las salidas históricas con una nueva corrida sin documentarlo.

**La calificación está escrita a mano.** Las listas `veredictos` corresponden a las salidas originales: deben revisarse para cada corrida nueva. Ejecutar todas las celdas sin recalificar reutiliza las mismas etiquetas y no constituye una nueva evaluación válida.

## Antecedente preliminar

[antecedentes/prueba_inicial_10_preguntas.ipynb](antecedentes/prueba_inicial_10_preguntas.ipynb) es la prueba temprana de diez preguntas, incorporada desde los archivos locales del curso. No es el experimento final de 50 preguntas que sustenta el informe.
