# Piloto v2: inferencia real en T4

27 de octubre de 2026. Corrida `14f5ffa72e8a2734d4814efab97541620fb0d63cbd42ad0307cd801f4acede43`, protocolo `d3-agentes-desde-cero-v2`, etiqueta `piloto-v2`.

El ZIP descargado pasó la auditoría de integridad: doce respuestas completas, cuatro preguntas y tres condiciones. Se conserva el archivo original y su extracción exacta en `original/`. No se ejecutó código contenido en el ZIP para calificarlo.

## Evaluación externa

Revisión asistida en este chat con la pauta D2, fuentes del corpus y juicios nuevos vinculados a los hashes de estas respuestas. La aprobación del agente auditor no es la etiqueta de corrección.

| Caso | Baseline | D2 | Agentes |
|---|---|---|---|
| P05: actividad final de titulación | Incorrecta | Correcta | Correcta |
| P25: asignaturas no eliminables | Incorrecta | Incorrecta | Incorrecta |
| P38: aplicabilidad y nota de aprobación | Incorrecta | Incorrecta | Incorrecta |
| P41: artículo inexistente | Incorrecta | Correcta | Incorrecta |
| Total | 0/4 | 2/4 | 1/4 |

P05 del sistema de agentes identifica Memoria de Título y cita inequívocamente el artículo 29 de RI-FI, aunque use paréntesis en lugar de corchetes. El añadido general sobre alternativas está respaldado por RG art. 3 definición 10 y distingue el caso específico de Ingeniería. No se exige duración porque la pregunta no la solicita.

En los otros tres casos la respuesta final es la abstención por presupuesto, no una respuesta al usuario. Los motivos de las doce decisiones están en `evaluacion/*/veredictos.json`; la comparación calculada está en `comparacion_evaluada.json`.

El sistema recupera P05 respecto de v1, pero continúa por debajo de D2 en este piloto. No corrige ningún error de D2 y mantiene la regresión P41. Los cuatro casos son de desarrollo y diagnóstico, no una estimación de generalización.

## Fallos observados

- El investigador copia fuentes completas en propiedades no permitidas (`fuentes`, `redactar`, entre otras), aun cuando debe devolver solo una decisión breve. Cinco salidas llegaron al límite de tokens; P25 agotó sus tres intentos de esta manera.
- El mensaje de formato ante propiedades extra indica claves faltantes vacías, sin enumerar las propiedades sobrantes. La retroalimentación no guía bien la reparación.
- P38 sigue añadiendo una exigencia de exclusividad no preguntada y no consigue evidencia de aplicabilidad. El control de repetición sí devuelve la tarea al investigador, pero este vuelve a fallar el contrato.
- P41 recibe evidencia de ausencia desde la búsqueda inicial, pero el redactor especula sobre el contenido del artículo inexistente. El auditor pide retirar la especulación; el redactor repite el texto, se activa el control de repetición y el siguiente investigador agota el límite de formato.
- P05 genera una corrección innecesaria y apoyos extensos; un extracto no literal provoca otro intento.

La incorporación de evidencia inicial, conservación del inventario y bloqueo de repeticiones funcionan como código. No bastan para que el modelo cumpla los contratos o emita buenas decisiones.

## Costes medidos

| Condición | Llamadas | Tokens de salida | Tiempo total de generación | Salidas cortadas |
|---|---:|---:|---:|---:|
| Baseline | 4 | 327 | 35,82 s | 0 |
| D2 | 4 | 414 | 71,31 s | 0 |
| Agentes | 24 | 10.353 | 1.453,74 s | 5 |

La generación conjunta tomó 1.560,87 segundos, aproximadamente 26 minutos, sin incluir la preparación. El promedio por pregunta de agentes fue 363,43 segundos frente a 17,83 segundos de D2. Aunque hubo menos llamadas de agentes que en v1, las salidas largas aumentaron el coste. No se debe prometer menor latencia por reducir llamadas sin medir también tokens.

## Siguiente decisión

No activar aún el lote completo. Simplificar y aclarar el protocolo de salida y su reparación, indicar que el controlador transfiere las fuentes automáticamente y que el agente no debe reproducirlas, y acotar la comunicación pública a decisiones breves. Mantener los límites y controles originales para no ocultar fallos aumentando presupuesto. Comprobar con nuevas pruebas de regresión y otro piloto real, conservando esta corrida.
