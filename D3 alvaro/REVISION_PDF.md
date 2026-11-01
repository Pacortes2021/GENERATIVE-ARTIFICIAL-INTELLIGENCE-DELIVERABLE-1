# Revisión del informe D3 por tres subagentes

Fecha: 31 de octubre de 2026.

Se revisó el informe de v6 desde tres perspectivas independientes: cumplimiento de la pauta, claridad de redacción y diseño académico. La integración incluyó una comprobación adicional de coherencia con el controlador y los resultados guardados. No se ejecutó nuevamente el modelo ni se recalificaron las respuestas.

## Cambios incorporados

| Revisión | Hallazgo | Cambio aplicado |
|---|---|---|
| Pauta | Las nueve etiquetas pendientes impiden presentar la evaluación como cerrada. | Sección «Resultados provisionales», con advertencia explícita. |
| Pauta y código | La salida sin aprobación también puede ocurrir por `destino=fin`, además del límite y JSON inválido. | Se agregó esa condición al grafo. |
| Pauta y código | Faltaban detalles del contexto y de la parada del Recuperador. | Se explicitan suficiencia, artículo inexistente o tres acciones; el controlador conserva el borrador anterior. La prueba posterior del notebook confirmó que el prompt restaurado de v6 no lo incorpora; el contrato del PDF se corrigió. |
| Redacción | Algunas frases eran telegráficas o mezclaban magnitudes. | Se explican acciones de cada rol con oraciones completas y se separan llamadas y segundos por consulta. |
| Redacción | La frecuencia de etiqueta «premisa falsa» no mide exactitud. | Se reemplaza ese indicador por la diferencia observada de aciertos sin few-shot. |
| Redacción | El caso H03 no indicaba qué se modifica. | Se precisa que trata del plazo para modificar asignaturas en cada semestre. |
| Diseño | Las etiquetas del grafo eran demasiado pequeñas. | Se aumentan de 6,5 a 7,5 puntos nominales; la etiqueta de parada pasa de 6 a 7,5. Se conserva el cuerpo de 9 puntos. |
| Diseño | Los encabezados de la tabla eran abreviados. | Se usan «Originales», «Difíciles» y «Llamadas»; los tamaños de los conjuntos están explícitos en la introducción. |
| Diseño | Faltaban metadatos del documento. | Se incorporan título, autores e idioma español. Esto no equivale a accesibilidad completa ni a un PDF etiquetado. |
| Trazabilidad | Las trazas históricas no contienen todos los mensajes íntegros. | Se las describe como trazas resumidas; no se reconstruye información ausente. |

Las recomendaciones de diseño aplican principios de jerarquía, contraste, legibilidad y composición. No se atribuyen a una norma académica obligatoria que no aparece en la pauta.

## Reservas que siguen abiertas

- **Video:** falta la grabación real de D3, el enlace público de hasta tres minutos y su correspondencia con las trazas de esas consultas.
- **Evaluación:** nueve casos de v6 siguen marcados para revisión en la planilla. No se cambian etiquetas para presentar resultados como definitivos.
- **Ablaciones:** sin ReAct y sin Verificador eliminan componentes completos. Sin CoT retira la instrucción del Redactor, pero el Verificador conserva la suya. No son pruebas que aíslen perfectamente el efecto de cada técnica.
- **Evidencia experimental:** una ejecución por condición, consultas usadas en desarrollo y semilla dependiente del prompt. No se demuestra generalización ni significación estadística.
- **Trazas históricas:** el registro del Redactor omite evidencia y borrador anterior; el del Verificador conserva un extracto del borrador y no la evidencia. No se puede afirmar que sean transcripciones completas.
- **Reproducción:** no se conservaron todas las revisiones originales de pesos y dependencias. El notebook registra el entorno de nuevas ejecuciones, pero no garantiza identidad de resultados.

## Validación de la versión integrada

- PDF LaTeX de una página A4 vertical.
- Revisión visual del texto, tabla y grafo tras recompilar.
- Cifras originales preservadas; controlador, prompts, CSV, planillas y trazas sin modificaciones.
- Comprobación de integridad y correspondencia entre archivos mediante `auditar.py`.
- PDF y fuentes actualizados en el paquete de ejecución.

No se asigna una nota estimada: el video y la revisión de etiquetas pueden cambiar la evaluación.
