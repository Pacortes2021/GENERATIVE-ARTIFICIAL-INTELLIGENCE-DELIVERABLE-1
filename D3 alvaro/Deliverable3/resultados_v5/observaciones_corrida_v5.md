# Corrida v5 — 2026-10-27 (cuenta de Pablo)

75/75, 0 errores, 0 fallbacks, 84 min (v4: 148 min). 75 acciones repetidas bloqueadas, 7 números copiados corregidos.

## Exactitud (corrección con Claude, pauta y precedentes del E2)
| | E2 | v4 | v5 |
|---|---|---|---|
| Congelado (50) | 40 | 41 | 39 |
| Difícil (25) | — | 17 | 16 |

v4→v5: mejoran 4, 6, 7, 38, H19, H21 · empeoran 14, 27, 47, 48, 49, 50, H04, H12, H18.
Verificador v5: aprueba 72/75 (75 % correctas) frente a v4 60/75 (85 %): perdió poder de discriminación.

## Lectura por mecanismo
1. **La recuperación v5 funcionó**: las 4 mejoras del set congelado (4, 6, 7, 38) son exactamente las que la
   búsqueda con la pregunta original predecía (artículo correcto presente en el top-5 del E2).
2. **El prompt v5 del Redactor dañó**: la instrucción de incluir requisitos y excepciones en "Condiciones" produjo
   reglas mal aplicadas (14, 27, H04, H12, H18): el modelo agrega normas de artículos vecinos.
3. **Premisas falsas colapsaron**: 47 y 48 inventan una respuesta usando cifras de artículos traídos por la búsqueda
   base (art. 31 "36 créditos", art. 11 "4,0"); 49 y 50 responden solo "no_existe" (copia la etiqueta de estado).
4. **El prompt v5 del Verificador lo volvió permisivo** (aprueba casi todo, incluidas 47 y 48).

Conclusión: los cambios de código (búsqueda base, bloqueo de repeticiones y copias, tope de evidencia) ayudan; los
cambios de prompt del Redactor y del Verificador perjudican. Siguiente variante natural (v6): código v5 + prompts v4 de
Redactor y Verificador. Advertencia: cada iteración se ajusta mirando las mismas 75 preguntas (riesgo de sobreajuste).
