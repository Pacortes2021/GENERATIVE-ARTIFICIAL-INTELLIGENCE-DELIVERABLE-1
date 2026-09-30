# Configuración de trabajo elegida

Se fija **Qwen3-4B con RAG estructurado**, sin few-shot. El modelo, corpus, fragmentación, política de búsqueda y prompt estructurado son los evaluados previamente. La configuración legible por máquina está en [seleccion_sistema.json](seleccion_sistema.json).

La selección se hizo después de revisar las 50 preguntas de desarrollo: simple 39/50, estructurado 40/50 y few-shot 36/50. Se elige el estructurado por su formato explícito de respuesta, condiciones y fuentes. Una diferencia de una pregunta no prueba superioridad general. Few-shot se conserva como alternativa evaluada y descartada, con sus errores documentados.

## Qué incorpora el sistema consultable

- Construye el índice E5 en CPU desde los 201 fragmentos validados y recupera evidencia para cada pregunta escrita por el usuario.
- Expande a unidades completas, conserva citas, sigue remisiones de un salto y calcula inventarios según la política existente. No hay reglas por ID de pregunta ni acceso a respuestas ideales.
- Genera baseline directo y RAG estructurado con los mismos pesos Qwen, revisión, cuantización, modo sin thinking, parámetros y semilla por pregunta.
- Conserva el prompt directo de E1. Cambian sus parámetros de inferencia para emparejarlo con RAG; por ello este baseline es una corrida adicional, no una reproducción literal del 4% histórico.
- Guarda nuevas respuestas y métricas técnicas. La pauta de evaluación queda fuera del generador y se aplica por igual a ambos CSV.

El cuaderno principal es [Deliverable2_Sistema_RAG_Colab.ipynb](notebooks/Deliverable2_Sistema_RAG_Colab.ipynb). Los cuadernos anteriores de comparación de prompts se conservan para reproducir sus experimentos.

## Límites conservados

No se ajustó la recuperación para forzar que P38 encuentre el artículo 2 ni se reescribió el prompt a partir de P25. En la primera corrida, P25 recibió los artículos 7 y 9 completos y el estructurado omitió desarrollar la remisión; es un fallo de respuesta documentado en [el diagnóstico](resultados/qwen3_4b_4adccec813c53d7f/DIAGNOSTICO_P25.md).

Las preguntas conocidas son de desarrollo. Para medir generalización habrá que fijar este sistema antes de probar un conjunto nuevo. El baseline y RAG difieren en instrucciones y evidencia, por lo que la comparación mide la intervención completa, no únicamente el efecto aislado de recuperación.

## Estado de validación

El código y cuaderno están preparados. Se probó recuperación real E5 en CPU, equivalencia de los 50 contextos y una consulta nueva. El presupuesto se valida con el tokenizador real de Qwen. La generación, los checkpoints y la exportación se comprobaron localmente con simulación. El [piloto en Colab](resultados/piloto_consulta_882da178b0514f0d/REPORTE.md) añade una pregunta nueva generada de verdad en ambas condiciones. La ejecución y evaluación semántica del lote emparejado de 50 siguen pendientes. Ver también la [validación local](notebooks/validacion_sistema.json).
