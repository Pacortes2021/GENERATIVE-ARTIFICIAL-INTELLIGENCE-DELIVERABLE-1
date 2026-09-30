# Revisión de fragmentación · 30 de septiembre de 2026

## Hallazgos observados

Se revisaron los cuatro extractores anteriores (`pdf`, `avanzado`, `definitivo`, `final`), el vectorizador, las verificaciones de JSON y las bases guardadas de 198 y 169 fragmentos en [el desarrollo archivado](../../Archivo/2026-09-30_desarrollo_previo/Deliverable2_RAG/). También se consultó el pipeline posterior archivado, sin reactivar experimentos anteriores.

| Caso | Artefacto anterior | Extracción actual |
|---|---|---|
| Ingeniería, art. 9 | En `base_conocimiento_udec.json`, termina en «prioridades a) y b) del». La continuación se separa como si comenzara otro artículo. | Conserva la oración completa, incluidas las referencias a los artículos 7 y 8. |
| Reglamento General, art. 5 | En la misma base, aparece bajo `[Art. 4, RG]`, con `VicedecaArtículo 5º no`. | Artículo 5 independiente, «Vicedecano» recompuesto y funciones completas. |
| Vacaciones de invierno | En **ambas bases**, «Vacaciones de invierno (aprobación — 30 junio». | «Vacaciones de invierno (aprobación transitoria): 30 junio – 05 de julio». |
| Suspensión de septiembre | En ambas bases, «Suspensión de actividades de docencia de»; falta «pregrado». | Nombre completo y fecha «14 - 17 de septiembre», segundo semestre de 2026. |
| Títulos de sección | Algunos títulos se anexan al artículo precedente, incluso en la base v2. | Encabezados clasificados y conservados como estructura, separados del cuerpo del artículo. |
| Transitorios | Etiquetas poco distintivas respecto de artículos ordinarios del mismo número. | IDs diferentes: `RG-ART-001` y `RG-TRANS-001`. |

La versión v2 **ya había corregido** los dos primeros problemas de los reglamentos. No corresponde atribuirle todos los errores de la versión original. Sí mantenía los problemas señalados del calendario y contaminación por encabezados.

Se cotejaron los casos con el [Reglamento de Ingeniería](../../Corpus/Reglamento_de_Docencia_de_Pregrado-FI.pdf), el [Reglamento General](../../Corpus/Reglamento_General_de_Docencia_de_Pregrado.pdf) y el [Calendario 2026](../../Corpus/Calendario-Academico-Pregrado-2026.pdf). Se inspeccionaron visualmente, entre otras, las páginas 2 de Ingeniería, 10 y 33 del Reglamento General y 1 del calendario.

## Causas

- Cortar por salto de línea confunde una línea visual del PDF con una unidad de significado. Los filtros por longitud también pueden eliminar fechas, incisos y continuaciones breves.
- Una ventana fija de palabras o caracteres puede separar una regla de su excepción. El solapamiento no garantiza que ambas lleguen juntas al generador.
- El orden de extracción de texto sin geometría puede insertar el encabezado de un artículo dentro de una palabra del cuerpo; ocurrió en el artículo 5.
- Separar ante cualquier línea que comience con «Artículo N» confunde una referencia interna con un encabezado nuevo. En Ingeniería, el inicio real está en negrita; la remisión al artículo 7 dentro del artículo 9 está en fuente normal.
- El calendario contiene celdas multilínea y rangos entre meses. Una expresión que toma solo la primera fecha/mes pierde el final del rango.
- Comprobar que un fragmento termine en punto no comprueba integridad. También faltaba registrar fuente, versión y relación entre fragmentos y unidades completas de manera consistente entre extractores.

No está demostrado que todos los errores de respuesta anteriores provengan de estos problemas: establecer esa causalidad exigiría repetir consultas controladas. Sí está demostrado que ciertas evidencias llegaban incompletas o mal identificadas en los archivos guardados.

## Límite del embedding: observado frente a riesgo

Se contaron tokens con el tokenizador real de `intfloat/multilingual-e5-small`, sin truncamiento ni padding, sobre `passage: ` más el campo `texto` guardado:

| Base | Fragmentos | Mayor longitud | Más de 512 tokens |
|---|---:|---:|---:|
| Original | 198 | 473 | 0 |
| v2 | 169 | 288 | 0 |
| Nueva | 201 | 476 | 0 |

Por tanto, **no se encontró truncamiento por el límite de E5 en esas dos bases guardadas**. La falla observada era anterior al embedding. El truncamiento sí sería un riesgo al indexar directamente artículos largos completos; la nueva preparación lo previene con un límite de 480 y comprobación del tokenizador.

## Resultado y comprobaciones

La preparación nueva conserva 97 artículos (95 ordinarios y 2 transitorios), 25 eventos, 50 filas del anexo y un preámbulo. Guarda fuente, SHA-256, páginas, texto y coordenadas de origen. El glosario se recupera por definición numerada, conservando también su artículo íntegro. Los 201 fragmentos mantienen intervalos de caracteres para reconstruir sin pérdida las 197 unidades recuperables.

Las 13 pruebas cubren casos reales de los PDF, continuidad entre páginas, fechas entre meses, celdas combinadas, expansión de un fragmento al artículo completo, deduplicación y rechazo de fragmentos alterados, colas perdidas o documentos faltantes. El informe de [validación](generado/validacion.json) registra versiones y hashes. Las comprobaciones de conservación parten del texto extraído, no certifican automáticamente que toda interpretación del documento sea correcta.

## Límite del documento fuente

La tabla del anexo de la página 33 del Reglamento General presenta conceptos en celdas combinadas cuyos límites no coinciden con los rangos del artículo 48, página 28. Por ejemplo, el anexo asocia 69/100 con 5,1 y «Aprobado por Unanimidad», mientras que el artículo 48 sitúa 5,1 dentro del rango 5,0–5,6 de «Aprobado con Distinción». La extracción conserva fielmente ambos lugares, incluida la celda vacía de concepto en las primeras filas del anexo, sin inventar ni corregir su contenido. Si una consulta depende de esa diferencia, debe citarse la fuente concreta y explicitar la ambigüedad.

Esto se distingue de un error de extracción. Tampoco se resolverán automáticamente las remisiones a otros artículos hasta implementar y comprobar la recuperación. El siguiente paso es probar **solo la recuperación de evidencia**, antes de ejecutar Qwen y comparar prompts.
