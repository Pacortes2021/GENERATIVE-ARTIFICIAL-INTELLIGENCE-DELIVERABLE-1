# Entregable 3 — Arquitectura de agentes (v6, versión final)

Sistema de **4 agentes** que reconstruye la solución RAG del Entregable 2 como un grafo de
agentes con **decisiones y bucles reales** (no un pipeline fijo). Todos los agentes usan el
**mismo modelo** `Qwen/Qwen3-4B` (≤8B, Apache 2.0), con prompts y roles distintos.

> Enunciado: *"una secuencia fija de prompts sin una decisión adentro es un pipeline y NO
> califica como sistema de agentes"*. Por eso cada agente **decide** qué pasa después (usar una
> herramienta, pasar a otro agente, reintentar o detenerse), y esa decisión cambia el flujo.

---

## 1. Los cuatro agentes

| # | Agente | Rol (que los demás no cubren) | Entrada | Salida | Herramientas | Decisión que cambia el flujo |
|---|--------|-------------------------------|---------|--------|--------------|------------------------------|
| 1 | **Enrutador** | Clasifica la pregunta y la **descompone** en sub-consultas | pregunta | JSON `{tipo, sub_consultas, documentos}` | — | El `tipo` ramifica: `premisa_falsa` con artículo explícito → verificación directa de existencia (sin búsquedas); el `tipo` fija el **modo** del Redactor; cada sub-consulta abre su propio ciclo ReAct |
| 2 | **Recuperador** (ReAct) | **Reúne la evidencia** | sub-consulta + evidencia reunida + observación anterior + corrección del Verificador | evidencia + estado (`suficiente` / `insuficiente` / `no_existe`) | `buscar`, `traer_articulo`, `existe_articulo` | En cada turno elige buscar / traer / verificar existencia / parar (≤3 acciones por sub-consulta) |
| 3 | **Redactor** | **Redacta** la respuesta (Respuesta / Condiciones / Fuente) usando solo la evidencia | pregunta + modo + evidencia + corrección del Verificador | borrador con citas | — | Se abstiene si el estado es `no_existe` o `insuficiente` |
| 4 | **Verificador** (Self-Refine) | **Audita** el borrador y decide el siguiente paso | pregunta + evidencia (texto) + chequeo de citas + borrador | JSON `{aprobado, destino, motivo}` | `chequear_citas` (usa `existe_articulo`) | Aprueba (**STOP**) / devuelve al Redactor / devuelve al Recuperador; su `motivo` viaja como corrección |

Cada prompt vive en un archivo versionado aparte en `prompts/` (historial en `prompts/CHANGELOG.md`):
`01_enrutador.txt`, `02_recuperador.txt`, `03_redactor.txt`, `04_verificador.txt`.

## 2. Las herramientas

Funciones que el modelo pide y la aplicación ejecuta. Se apoyan en el corpus del E2 (197 unidades:
RI-FI art. 1–35, RG art. 1–60, CAL 25 entradas; 201 fragmentos de búsqueda, IDs tipo `RI-FI-ART-011`).

- `buscar(consulta, k=5)` → recuperación densa con `multilingual-e5-small` (igual que el E2).
- `traer_articulo(doc, n)` → texto completo del artículo n.
- `existe_articulo(doc, n)` → `True/False` según el **inventario** real. Resuelve premisas falsas.
- `chequear_citas(borrador)` → por cada cita del borrador: ¿existe en la normativa? ¿está en la
  evidencia reunida? El resultado se entrega al Verificador.

## 3. Grafo de agentes

`grafo_agentes.pdf` / `.png`. Nodos: 4 agentes, 4 herramientas, entrada y salida.
- Negro: flujo principal, con lo que se pasa en cada arista.
- Violeta punteado: **ramas decididas por el Enrutador** (premisa falsa → `existe_articulo`;
  modo del Redactor según el tipo).
- Rojo discontinuo: **bucles de decisión**: ReAct del Recuperador (≤3), Verificador → Redactor
  y Verificador → Recuperador, ambos llevando el `motivo` (≤2 ciclos de corrección).
- Parada: Verificador → Respuesta final (aprobado). Si se agota el tope, se entrega el último
  borrador **marcado como no aprobado**.

## 4. Técnicas de prompting por agente

| Agente | Técnicas | Falla que ataca (diagnóstico E1/E2) |
|--------|----------|--------------------------------------|
| Enrutador | few-shot, XML tags, instrucciones positivas | preguntas de **cruce** respondidas a medias (P36) |
| Recuperador | **ReAct**, step-back, XML tags | **colisión léxica** (P3/P38): re-busca si trae el artículo equivocado |
| Redactor | **cadena de pensamiento** (`<pensar>`, se elimina antes de mostrar), salida estructurada, XML tags, rol | invención y formato; hereda el prompt estructurado del E2 |
| Verificador | **auto-refinamiento**, criterios explícitos, CoT, herramienta de citas | **condición omitida** (P25) y **cita equivocada** (P38) |

## 5. Experimento

Mismo criterio de corrección para todas las filas (pauta y precedentes del E2), sobre el set congelado
de 50 y el set difícil de 25 (`test_set_dificil_25.csv`, respuesta al comentario del profesor).
Corrección propuesta con apoyo de Claude (uso de IA permitido en el curso), con motivo por fila, verificada
contra el texto del corpus y revisada por el equipo.

Decodificación idéntica al E2 y a la recomendación de Qwen para el modo sin razonamiento:
temperatura 0,7, top-p 0,8, top-k 20, min-p 0, semilla base 2026. En el E3 la semilla se fija por
llamada (derivada del prompt): la misma entrada en el mismo entorno produce la misma salida. Como no se
fijaron todas las versiones de las bibliotecas, otra sesión de Colab puede dar respuestas distintas.

## 6. Mapa a la rúbrica del D3

- **Continuidad:** misma tarea, falla, modelo, corpus, recuperador y decodificación del E2.
- **Grafo de agentes:** nodos, aristas etiquetadas, bucles, ramas y parada (§3).
- **Diseño de agentes:** tabla §1; cada rol es necesario y no lo cubre otro agente.
- **Técnicas:** §4 + ablación y comparación de versiones (§14).
- **Evidencia de mejora:** tabla de §14, mismo criterio para baseline / E2 / agentes.
- **Repo y reproducibilidad:** prompts versionados, trazas por entrada (`trazas_D3.json`),
  notebook `D3_colab_qwen3_4b.ipynb` con guardado progresivo.

## 7. Estado

| Pieza | Estado |
|-------|--------|
| Orquestador v6 + 4 herramientas | Hecho; lógica probada con simulador determinista (`agentes/demo_mock.py`, 29 comprobaciones) |
| Prompts v6 | Hecho (historial en `prompts/CHANGELOG.md` y `prompts/historial/`) |
| Set difícil (25) | Hecho; fuentes verificadas contra el corpus |
| Corridas reales con Qwen3-4B | v4, v5 y v6 (75 preguntas cada una) + RAG del E2 sobre el set difícil |
| Ablaciones | Las cuatro técnicas, una a la vez, sobre las 75 preguntas (§15); "sin Verificador" desde las trazas de la v6 |
| Documento LaTeX de una página y video | Hecho: `documento/main.pdf`; el video está enlazado en el informe y en el README |

---

## 8. Cambios v2 (2026-10-24)

1. ReAct con **acciones estructuradas** (una acción JSON por turno) en vez de texto libre: más
   robusto para un modelo de 4B.
2. El Verificador decide destino (`fin` / `redactor` / `recuperador`).
3. Se describió un Enrutador que ramifica y un Verificador anclado en `existe_articulo`.
   **Nota v3:** esa descripción iba por delante del código; ambas cosas recién quedaron
   implementadas en la v3 (ver §9).

## 9. Cambios v3 (2026-10-26) — revisión crítica del código

| Problema encontrado | Consecuencia | Corrección |
|---------------------|--------------|------------|
| Los reintentos usaban el mismo prompt | Con semilla/decodificación fija, el reintento repite la misma salida: el bucle no corregía nada | El `motivo` del Verificador entra al prompt del Redactor y del Recuperador |
| El Verificador solo veía los IDs de la evidencia | No podía comprobar si el dato coincidía con el texto | Recibe el texto (≤700 caracteres por evidencia) y el resultado de `chequear_citas` |
| El Verificador no tenía herramienta en el código | La afirmación "anclado en `existe_articulo`" no era cierta | Nueva herramienta `chequear_citas` |
| Veredicto ilegible → aprobado | Fallos del Verificador quedaban ocultos como aciertos | Ahora se cierra **sin aprobar** y se registra como `fallback` |
| El `tipo` del Enrutador no cambiaba nada en el código | Riesgo de "pipeline disfrazado" | Rama `premisa_falsa` y modo del Redactor por tipo |
| El Recuperador no veía lo que devolvía su acción | ReAct sin "observar" | Recibe `ultima_observacion` con extractos |
| `existe` = verdadero detenía la sub-consulta sin traer el texto | Evidencia vacía | Si existe, se trae el artículo |
| El Redactor prohibía en la práctica los cálculos | Preguntas numéricas imposibles | Permite calcular con cifras de la evidencia y de la pregunta |
| El bloque `<pensar>` quedaba en la respuesta y podía romper la lectura del JSON | Respuestas sucias, veredictos perdidos | Se elimina y se lee el último JSON |
| Generación determinista en el notebook | Rompía la continuidad con el E2 y contradice la recomendación de Qwen | Mismo muestreo que el E2, semilla por llamada |

## 10. Cambios v4 (2026-10-26) — primera prueba con Qwen3-4B real

Con 2 preguntas de prueba, el Enrutador, el Recuperador (ReAct) y la rama de premisa falsa funcionaron
como se diseñó, y ambas respuestas fueron correctas. Pero el Redactor **copiaba su propio prompt**
antes de responder, y un identificador de ejemplo de sus reglas se colaba como cita falsa en
`chequear_citas`. Causas y correcciones: ver `prompts/CHANGELOG.md` (v4). La salida real quedó como
prueba de regresión en `agentes/demo_mock.py` (escenario E).

## 11. Resultados v4 y cambios v5 (2026-10-27)

**Corrida v4** (75 preguntas, 148 min, 0 errores): set congelado **41/50 (82 %)** frente a
**40/50 (80 %)** del RAG del E2 (diferencia no concluyente: 7 preguntas mejoran y 6 empeoran); set
difícil **17/25 (68 %)**. El Verificador funciona como señal de confianza: 85 % de acierto en lo que
aprueba frente a 47 % en lo que no aprueba.

**Diagnóstico de los 16 errores** (comprobando si el artículo correcto llegó al Redactor): 4 del
Recuperador (no lo encontró), 11 del Redactor (lo tenía y respondió mal), 1 del Enrutador. Las trazas
revelaron causas de **diseño**, no del tamaño del modelo:

| Causa observada | Evidencia en la corrida v4 | Cambio v5 |
|---|---|---|
| El Recuperador copia los ejemplos de su prompt | "existe art. 90" ×5, "traer art. 8" ×9, "baja académica" ×2 en 7 preguntas | Ejemplos genéricos; número de artículo no mencionado → se busca en su lugar |
| Acciones repetidas idénticas | 114 de 362 acciones (31 %) | La acción repetida no se ejecuta; se avisa que reformule |
| No se busca con la pregunta original | Con la pregunta original (top-5 guardado del E2) el artículo correcto aparece en 34/38 preguntas; con las búsquedas del Recuperador v4, en 29/38 (P1, P4, P7, P17, P38 lo pierden) | Búsqueda base con la pregunta, con doble peso al elegir la evidencia |
| Exceso de evidencia | Mediana 7 artículos en errores vs 5 en aciertos | Máximo 6 artículos, los más relevantes |
| El rechazo hace que el Redactor se rinda | 4 casos: de responder a "no hay información" | El Redactor recibe su borrador anterior y corrige solo lo señalado |
| El Verificador rechaza respuestas correctas | H05 (5,72), P31, P47 | Rechaza solo errores concretos; reconoce premisas corregidas |
| "Condiciones: No aplica" de relleno; excepciones omitidas | P36 omite las excepciones del art. 8 | Incluir requisitos y excepciones de la evidencia; omitir la línea si no hay |
| Borrador vacío por tokens | P34 | Razonamiento breve; 1200 tokens para el Redactor |

Son mecanismos generales, pero se diseñaron **después de ver** estas 75 preguntas: la mejora sobre ellas
debe leerse como evidencia de que los mecanismos funcionan, no como estimación de generalización.

## 12. Resultados v5 (2026-10-27)

| | E2 | v4 | v5 |
|---|---|---|---|
| Congelado (50) | 40 | 41 | 39 |
| Difícil (25) | — | 17 | 16 |

La v5 no mejora en total, pero separa efectos: los cambios de **código** de recuperación funcionan (recupera 4, 6, 7,
38, justo las predichas), mientras que los cambios de **prompt** del Redactor (incluir condiciones) y del Verificador
(más permisivo) introducen reglas mal aplicadas y rompen las premisas falsas (47–50). Detalle en
`resultados_v5/observaciones_corrida_v5.md`.

## 13. Variante v6 (2026-10-27) — versión final

Código v5 (búsqueda base, bloqueo de repeticiones y de números copiados, tope de 6 artículos) + prompt del
Recuperador v5 + prompts del Redactor y del Verificador **restaurados tal como se usaron en la corrida v4**.
Por eso, en v6 el Redactor recibe el motivo del Verificador pero no su borrador anterior (el cambio de v5 de la tabla de
§11 no quedó en la versión final).

| | E2 (RAG) | v4 | v5 | **v6** |
|---|---|---|---|---|
| Congelado (50) | 40 (80 %) | 41 (82 %) | 39 (78 %) | **46 (92 %)** |
| Difícil (25) | 16 (64 %) | 17 (68 %) | 16 (64 %) | **20 (80 %)** |

Frente al E2, pregunta a pregunta: en el congelado 7 mejoran y 1 empeora; en el difícil 6 mejoran y 2 empeoran.
Las versiones se ajustaron mirando estas 75 preguntas, por lo que la cifra no estima la generalización. Detalle por
pregunta en `resultados_v6/correccion_D3_v6.xlsx`.

## 14. Ablación y tabla de resultados (2026-10-29)

| Configuración | Congelado (50) | Difícil (25) |
|---|---|---|
| Prompting directo, misma inferencia (E2) | 1 (2 %) | 0 (0 %) |
| RAG estructurado (E2) | 40 (80 %) | 16 (64 %) |
| Agentes v4 (primer diseño) | 41 (82 %) | 17 (68 %) |
| Agentes v5 (recuperación v5 + prompts v5) | 39 (78 %) | 16 (64 %) |
| **Agentes v6 (final)** | **46 (92 %)** | **20 (80 %)** |
| v6 sin Verificador (ablación desde trazas) | 44 (88 %) | 19 (76 %) |

Las filas del E2 en el set difícil se obtuvieron el 2026-10-29 corriendo el **mismo cuaderno del E2 sin cambios**
(sección 7 agregada: `../D2_sobre_25_dificiles/D2_RAG_sobre_25_dificiles_Colab.ipynb`) sobre las 25 preguntas nuevas.

Lectura: sin recuperación el modelo inventa en todas las preguntas difíciles (0/25), incluida la confirmación de la
premisa falsa del 4,5. El RAG del E2 llega a 64 %. Los agentes v6 llegan a 80 %: ganan sobre todo en cálculos con
datos de la pregunta (H05, H06, H08), en la trampa de las dos bajas (H12) y en una síntesis (H19); pierden H18 y H25.
La recuperación con la pregunta original y el bloqueo de repeticiones y copias aportan la mayor parte de la mejora; el
Verificador aporta +3 netos con ~48 % más llamadas al modelo (711 frente a 481 del primer borrador). Todas las correcciones: pauta y precedentes del E2.

## 15. Ablaciones completas (2026-10-30)

Se quita **una** técnica a la vez (`Orquestador(..., ablacion=...)`); todo lo demás igual a la v6 (mismos prompts,
semillas por llamada, decodificación y entradas). Las corridas `sin_fewshot`, `sin_react` y `sin_cot` se hicieron con
Qwen3-4B en Colab (T4) sobre las 75 preguntas; `sin_verificador` sale del primer borrador guardado en las trazas de la v6
(mismo prompt y misma semilla). Corrección con el mismo criterio (`resultados_ablaciones/`); las marcas REVISAR de
cada xlsx son históricas: el equipo revisó esos casos.

| Configuración | Congelado (50) | Difícil (25) | Llamadas al modelo/pregunta (75) | Seg/pregunta (cong. / dif.) |
|---|---|---|---|---|
| Prompting directo | 1 (2 %) | 0 (0 %) | 1 | — |
| RAG E2 | 40 (80 %) | 16 (64 %) | 1 | — |
| **Agentes v6 (completo)** | **46 (92 %)** | **20 (80 %)** | 9,48 | ~110 |
| sin few-shot (Enrutador) | 44 (88 %) | 19 (76 %) | 10,68 | 99 / 145 |
| sin ReAct (Recuperador) | 45 (90 %) | 18 (72 %) | 3,85 | 69 / 99 |
| sin CoT (Redactor) | 46 (92 %) | 19 (76 %) | 8,27 | 51 / 64 |
| sin Verificador | 44 (88 %) | 19 (76 %) | 6,41 | — |

Las llamadas excluyen los pasos automáticos que no invocan al modelo (búsqueda base y comprobación decidida por el
Enrutador); es el mismo conteo del informe. El detalle está en `../AUDITORIA.md`.

Lectura honesta: el completo es el mejor o empata en ambos sets, pero ninguna ablación baja más de 2 preguntas en un
set; con n = 25/50 eso no es estadísticamente significativo. Las técnicas son en parte redundantes (el Verificador
corrige al Redactor; `existe` cubre premisas falsas que el Enrutador sin few-shot ya no detecta: clasifica 6 como
premisa_falsa frente a 14, y nunca usa `cruce`). Sin ReAct cae más en las difíciles (H05 no calcula por falta de
evidencia, H08 cita el artículo equivocado) con menos de la mitad de llamadas. Sin CoT el tiempo baja a la mitad y
empata en el congelado; en el difícil pierde un cálculo y una premisa falsa (H06, H21) y gana H07 y H14.
