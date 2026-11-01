# Corrida 1 — sistema de 4 agentes, Qwen3-4B (2026-10-26)

Configuración: prompts v4, orquestador v3+limpieza, E5, NF4, T4, muestreo igual al E2, semilla 2026 por llamada.
75 preguntas (50 congeladas + 25 difíciles), 148 min, 0 errores, 0 fallbacks de interpretación.

## Comportamiento (no es exactitud; la exactitud sale de la corrección manual)
| Set | 1 ciclo | 2 ciclos | 3 ciclos (tope) | Aprobadas por el Verificador |
|---|---|---|---|---|
| Congelado | 36 | 3 | 11 | 42/50 |
| Difícil | 17 | 1 | 7 | 18/25 |

Promedio 8,7–9,4 llamadas al modelo por pregunta; ~2 min por pregunta.

## Patrones observados en las trazas (a confirmar con la corrección manual)
1. **Recuperación**: el artículo pertinente a veces no entra en la evidencia: P1 (RG-23 en vez de RI-FI-11),
   P6 (no encuentra RI-FI-10 → se abstiene), P7 (cita RI-FI-27 en vez de RI-FI-16), P38 (no trae RG-23; responde "7,0"),
   H03 (falta CAL-2026-S2-02), H08 (cita RG-24 en vez de RI-FI-30). La re-búsqueda pedida por el Verificador no lo corrige.
2. **Verificador como juez (4B)**: detecta errores reales (H06, H07, H18, P30, P34), pero también rechaza respuestas
   aparentemente correctas (P31, P47, H05: pide "justificar el cálculo") y aprueba otras dudosas (P7, H14 "Sí, automáticamente…, salvo…").
3. **El bucle de corrección rara vez repara**: solo 4/75 pasan a "aprobado" en el 2º ciclo; cuando rechaza, suele seguir
   rechazando hasta el tope. Valor posible: marca como "no aprobadas" respuestas dudosas (medible con la tabla Aprobó × Correcto).
4. **Razonamiento del Redactor**: H06 no usa "cuarto semestre" (dice que falta el nº de semestres); H07 compara 42 con 10 sin dividir.
5. **Información añadida sin respaldo**: H18 y P34 ("suspensión hasta tres años"), H17 (excepciones religiosas/discapacidad: revisar si vienen del RG).
6. **Enrutador**: H21 clasificada "numerica" en vez de premisa falsa → respuesta "no_existe"; la misma premisa en P47 sí se resolvió.
7. Premisas falsas con artículo inexistente (P41–P45, H20): abstención correcta en todas.

## Corrección (propuesta por Claude con criterio D2, verificada contra el corpus; PENDIENTE revisión del equipo)
- Congelado: 41/50 (82%) vs D2 RAG 40/50 (80%). Regla (precedentes D2): el relleno de 'Condiciones' no se penaliza (P18);
  omitir una excepción necesaria sí (P11, P36). P1 y P21 = 1; P36 = 0. Diferencia +1 neta: no concluyente.
- Difícil: 17/25 (68%). Por categoría: colisión léxica 5/5, multi-salto 3/4, premisa falsa 3/4, síntesis 3/5,
  negación 2/3, cálculo 1/4.
- Verificador (75): aprobadas 51/60 correctas (85%); no aprobadas 7/15 correctas (47%). Funciona como señal de confianza,
  aunque el bucle casi no repara.
- 10 filas marcadas para revisión: 1, 17, 28, 30, 34, 46, H05, H07, H14, H19.

## Causas de diseño detectadas (2026-10-27) → arreglos v5
1. Recuperador copia ejemplos de su prompt (existe art. 90 ×5, traer art. 8 ×9, buscar 'baja académica' ×2; 7 preguntas, 2 falladas: P7, P34).
2. Acciones repetidas idénticas: 114 de 362 (31%) en 33 preguntas; la re-búsqueda no reformula (P6: misma consulta 7 veces).
3. El Verificador empuja al Redactor a rendirse: de responder a 'no hay información' en P17, P23, H06, H08; rechaza correctas (H05, P31, P47).
4. La búsqueda usa solo las sub-consultas reescritas, no la pregunta original (P4: solo trae anexos; el D2 sí encontraba RG art. 23).
5. Exceso de evidencia: mediana 7 artículos en errores vs 5 en aciertos.
6. 'Condiciones: No aplica' por defecto, negando condiciones que existen (P1, P21, P36).
7. Un borrador vacío por salida cortada (P34): presupuesto de tokens del Redactor.

8. Verificado con el top-5 guardado del E2 (e5_top5_v1): la pregunta original trae el artículo correcto en 34/38 preguntas con fuente de artículo; la evidencia del Recuperador v4, en 29/38.
