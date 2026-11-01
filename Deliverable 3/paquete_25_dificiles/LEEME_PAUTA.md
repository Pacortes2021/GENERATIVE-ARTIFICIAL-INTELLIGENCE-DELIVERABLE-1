# 25 preguntas difíciles (H01–H25): archivos y pauta de corrección

Conjunto de 25 preguntas creado en el D3 para separar sistemas que en las 50 preguntas originales ya rinden parecido
(en esas 50, el RAG D2 ya acierta 40). Usa **el mismo corpus del D2**: `corpus.json` y `fragmentos_busqueda.json`
son idénticos byte a byte a `Deliverable2/corpus/generado/`, y todas las fuentes correctas existen en él.
La única excepción es H20, cuya fuente es "(inexistente)" a propósito.

## Archivos

| Archivo | Para qué | ¿Lo ve el modelo? |
|---|---|---|
| `preguntas.json` | Entrada del sistema: solo `id`, `pregunta`, `categoria`. Ids 101–125 (H01 → 101 … H25 → 125), iguales a los usados en la corrida del D2. | Sí |
| `referencias_dificiles_25.csv` | Respuesta correcta, fuente correcta y por qué es difícil. **Solo para corregir.** | No |
| `correcciones_ejemplo_directo_y_D2.xlsx` | Corrección ya hecha de prompting directo y RAG D2 sobre estas 25, con el motivo de cada veredicto. Sirve para corregir con el mismo criterio. | No |

`preguntas.json` ya tiene el formato que acepta `read_assets()` en `d3_agentes/bridge.py`: solo esas tres claves,
sin referencias. Correrlo cambia la configuración y por lo tanto el hash del lote, así que es un **lote nuevo**:
no se mezcla con el lote de 50 en curso.

## Resultados ya medidos en estas 25 (mismo Qwen3-4B, misma inferencia del D2)

| Condición | Correctas |
|---|---|
| Prompting directo | 0/25 |
| RAG D2 (cuaderno original del D2, sin cambios) | 16/25 |
| Agentes de Álvaro (4 agentes, v6) | 20/25 |

Las dos primeras salieron del cuaderno del D2 sin modificar. Si `baseline_directo` y `rag_d2` de su sistema
reproducen exactamente el D2 (mismo prompt, misma semilla por pregunta), deberían dar lo mismo, y se puede verificar
comparando con el xlsx.

## Pauta (la misma del D2)

**Una respuesta es correcta solo si el dato es suficiente para responder lo que se pregunta y la cita lo respalda.**
Se corrige contra el texto del reglamento, no contra la decisión interna del sistema (que el Auditor o Verificador
apruebe una respuesta no la hace correcta).

Reglas que salieron de los precedentes del D2:

1. **Relleno no se penaliza.** Una línea de condiciones con "No aplica" o algo genérico pero no falso no hace
   incorrecta una respuesta correcta (precedente P18).
2. **Omitir una excepción necesaria sí se penaliza.** Ejemplos: P11 y P36 del D2, y H14 de este conjunto
   ("Sí, queda automáticamente" contradice las excepciones del art. 14).
3. **Agregar algo falso o mal citado se penaliza**, aunque el dato principal esté bien (P01, P28, P30).
   Ejemplos en este conjunto:
   - H12: agrega el plazo de 10 días, que corresponde a la baja académica.
   - H01: dice "solo en otra institución", y el art. 21 dice "en esta u otra".
4. **Una cita extra válida no se penaliza.** En H09, citar RG art. 35 además de RI-FI art. 25 se aceptó.
   El problema es solo una cita que no respalda lo afirmado.
5. **Preguntas de varias partes (multi_salto y sintesis):** se exigen todas las partes, cada una con su respaldo.
   Responder solo una es incorrecto.
6. **Cálculos:** el resultado debe ser exacto y el razonamiento debe ser correcto. En H07 la conclusión acertó con
   un razonamiento erróneo (comparó 42 con 10 sin dividir), y se marcó incorrecta.
7. **Premisa falsa (H20–H23):** es correcta si rechaza o corrige la premisa sin inventar. Indicar que el artículo
   no existe, o que no hay respaldo, cuenta como correcta. Confirmar la premisa, o inventar contenido para un
   artículo inexistente, es incorrecto.
8. **Abstenerse cuando la respuesta sí está en el corpus es incorrecto.** Ejemplo: H03, donde las fechas están en
   el calendario.

Las preguntas sin dueño claro conviene marcarlas como "revisar" y decidirlas entre los dos, para que ambos sistemas
se corrijan igual. Si la corrección se hace con ayuda de IA, se declara así en el informe.
