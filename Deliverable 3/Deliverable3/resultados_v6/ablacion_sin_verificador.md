# Ablación "sin Verificador" (desde las trazas de la v6)

El primer borrador del Redactor es la salida del sistema sin el bucle de verificación: todo lo anterior al primer
borrador es idéntico (mismo prompt y misma semilla por llamada). Solo difiere en las 21 preguntas con más de un borrador.

| | Congelado (50) | Difícil (25) | Llamadas al modelo | Tiempo |
|---|---|---|---|---|
| v6 con Verificador | 46 | 20 | 711 | 138 min (medido) |
| v6 sin Verificador | 44 | 19 | 481 (−32,3 %) | No medido separadamente |

El Verificador corrige 4 preguntas y empeora 1 (+3 netos sobre 75).

| Pregunta | Primer borrador (sin Verificador) | Final (con Verificador) | Motivo del veredicto del primer borrador |
|---|---|---|---|
| P25 | 0 | 1 | Responde "no_existe"; la versión final identifica las prioridades a) y b) |
| P40 | 0 | 1 | Afirma el 40 % citando solo RI-FI art. 29 (el 40 % está en el art. 30) |
| H08 | 0 | 1 | 4,0 pero cita RI-FI art. 31 (la final cita el art. 30) |
| H12 | 0 | 1 | Mezcla reglas de la baja académica con la baja por no inscripción |
| H07 | 1 | 0 | Primer borrador correcto (10,5 no es inferior a 10); tras dos rechazos, la final dice que no se puede determinar |

Las otras 16 preguntas con más de un borrador tienen el mismo veredicto en el primer borrador y en el final
(P20, P34, P45–P50, H03, H04, H05, H06, H14, H18, H21, H22).
