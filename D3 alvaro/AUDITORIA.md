# Alcance de la preparación

Se conserva `D3_nuestro_completo_original.zip` exactamente como fue recibido.
El controlador `agentes/orquestador.py`, herramientas y prompts son idénticos al original.
Los CSV, trazas y planillas históricas no se modificaron. Las etiquetas exportadas a JSON
permiten revisar las sumas con Python estándar y registran el hash de la planilla fuente.

## Cambios de integración

- Carga de Colab compatible con el paquete de ejecución, ZIP original o ZIP del repositorio.
- Completo v6 sobre 75 preguntas como configuración por defecto.
- Directorios separados por corrida; reanudación protegida por hashes y configuración.
- Conteo de llamadas separado del número de eventos de traza.
- Notebook de demostración y guía de grabación.
- Informe y resúmenes con costos corregidos y evaluación propuesta declarada.
- Marcador de video pendiente explícito, sin enlace ficticio o de D2.

## Costos corregidos

| Variante | Eventos | Llamadas de modelo | Media sobre 75 |
|---|---:|---:|---:|
| Completo | 798 | 711 | 9,48 |
| Sin few-shot | 879 | 801 | 10,68 |
| Sin ReAct | 375 | 289 | 3,85 |
| Sin CoT | 701 | 620 | 8,27 |
| Primer borrador sin Verificador | — | 481 | 6,41 |

Se excluyen eventos `decidido_por = sistema/enrutador`: el código los ejecuta sin una nueva llamada generativa.
El CSV histórico guarda el conteo anterior para preservar la evidencia. El nuevo notebook exporta ambos conteos.

## Limitaciones de la versión evaluada

Se documentan sin modificar la lógica, porque cambiarla generaría otra versión que requeriría evaluación:

1. `bool(ver.get('aprobado'))` interpreta la cadena `"false"` como verdadera. Debe usarse un booleano JSON estricto en una versión futura.
2. `chequear_citas` informa al Verificador pero no impone un veto en código a las citas inexistentes.
3. El patrón de citas no reconoce completa la unidad `RG-ART-003-DEF-22`.
4. El Verificador recibe solo los primeros 700 caracteres por unidad, mientras el Redactor recibe el texto completo.
5. La semilla depende del prompt: las ablaciones también cambian el muestreo. Son una corrida por condición sobre preguntas usadas durante desarrollo.
6. Sin ReAct y sin Verificador eliminan componentes, no solo un bloque de instrucciones; sin CoT afecta únicamente al Redactor.
7. Nueve etiquetas v6 siguen marcadas para revisión. Hay 64 aprobaciones internas: 57 correctas y siete incorrectas según la planilla; otros nueve aciertos son borradores rechazados internamente.
8. Los 44/50 y 19/25 de sin Verificador proceden de evaluar el primer borrador de v6; no son una corrida GPU independiente.
9. Las revisiones exactas originales de pesos/dependencias no están completamente conservadas. Registrar el entorno nuevo no reconstruye el histórico.

10. Los registros históricos son resumidos: el Redactor no registra evidencia ni borrador anterior en su entrada, y el Verificador registra solo 200 caracteres del borrador, sin evidencia. No constituyen transcripciones completas de todos los mensajes.

Las 29 comprobaciones simuladas y la auditoría de archivos no sustituyen una nueva corrida GPU ni una recalificación independiente.
