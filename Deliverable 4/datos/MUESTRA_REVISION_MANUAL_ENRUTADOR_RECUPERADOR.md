# Muestra de Revisión Manual — Enrutador y Recuperador D4 (20 casos)

Complementa la muestra de **30 casos del Redactor** en [`MUESTRA_REVISION_MANUAL.md`](MUESTRA_REVISION_MANUAL.md) para completar **50 casos revisables manualmente** a través de los 3 agentes fine-tuneados de Deliverable 4.

- **Enrutador (`10` casos):** 2 por cada `tipo` (`factual`, `numerica`, `condicional`, `cruce`, `premisa_falsa`; 1 `train` + 1 `val`). Procedencia: `30` train + `6` val escritos a mano en `enrutador_bloques.py` (con asistencia de **Gemini 4 Argon** vía Antigravity), más etiquetas derivadas por reglas (`inferir_tipo_y_subconsultas_spec`, `inferir_documentos_spec`).
- **Recuperador (`10` casos):** cobertura estratificada de las 4 acciones (`suficiente`, `buscar`, `traer`, `existe`) en `train` y `val`. Procedencia: trayectorias sintetizadas determinísticamente por `recuperador_bloques.py` replicando a `Orquestador.recuperar()`.
- **Antifuga:** 0 unidades bloqueadas (`D3` + `nuevas_20`), 0 menciones a QIDs de evaluación y 0 solapamiento train/val.

## Registro de Verificación Humana (20 casos)

| # | ID | Agente / Categoría / Split | Revisor | Fecha | Resultado | Observaciones |
|---|---|---|---|:---:|---|---|
| 01 | `ENR-B1-T04` | `enrutador` / `factual` / `train` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 02 | `ENR-B1-V05` | `enrutador` / `factual` / `val` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 03 | `ENR-B4-T01` | `enrutador` / `numerica` / `train` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 04 | `ENR-B4-V01` | `enrutador` / `numerica` / `val` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 05 | `ENR-B2-T01` | `enrutador` / `condicional` / `train` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 06 | `ENR-B2-V01` | `enrutador` / `condicional` / `val` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 07 | `ENR-B1-T01` | `enrutador` / `cruce` / `train` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 08 | `ENR-B1-V01` | `enrutador` / `cruce` / `val` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 09 | `ENR-B3-T03` | `enrutador` / `premisa_falsa` / `train` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 10 | `ENR-B3-V02` | `enrutador` / `premisa_falsa` / `val` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 11 | `REC-B1-T01-S1` | `recuperador` / `suficiente` / `train` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 12 | `REC-B1-V04-RS` | `recuperador` / `suficiente` / `val` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 13 | `REC-B1-T07-B1` | `recuperador` / `buscar` / `train` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 14 | `REC-B1-T12-B1` | `recuperador` / `buscar` / `train` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 15 | `REC-B3-V02-B1` | `recuperador` / `buscar` / `val` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 16 | `REC-B1-T15-FB` | `recuperador` / `traer` / `train` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 17 | `REC-B1-T22-T2` | `recuperador` / `traer` / `train` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 18 | `REC-B6-V02-T2` | `recuperador` / `traer` / `val` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 19 | `REC-ENR-X-T30-EX` | `recuperador` / `existe` / `train` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |
| 20 | `REC-ENR-X-V04-EX` | `recuperador` / `existe` / `val` | [Pendiente revisor] | [YYYY-MM-DD] | [Pendiente] | |

Criterios de revisión:
1. **Enrutador:** `tipo` coherente con la pregunta, `sub_consultas` mínimas sin redundancia y `documentos` correctos (`RI-FI`, `RG`, `CAL`).
2. **Recuperador:** usa `suficiente` cuando la evidencia ya cubre todas las sub-consultas; solo invoca `traer`/`existe` sobre artículos permitidos; consulta léxica limpia cuando usa `buscar`.

---

## 01. `ENR-B1-T04` — `enrutador` | `factual` | split `train`
**Pregunta base:** En la equivalencia de escalas de notas, ¿a qué calificación de 1,0 a 7,0 equivale un puntaje de aprobación de 68 en escala de 1 a 100 y en qué rango de nota de titulación cae dentro de 'Aprobado por Unanimidad'?
**Unidades referenciadas:** `RG-ANEXO-18`, `RG-ART-048`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Pregunta: En la equivalencia de escalas de notas, ¿a qué calificación de 1,0 a 7,0 equivale un puntaje de aprobación de 68 en escala de 1 a 100 y en qué rango de nota de titulación cae dentro de 'Aprobado por Unanimidad'?
Salida:
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "tipo": "factual",
  "sub_consultas": [
    "En la equivalencia de escalas de notas, a qué calificación de 1,0 a 7,0 equivale un puntaje de aprobación de 68 en escala de 1 a 100",
    "en qué rango de nota de titulación cae dentro de 'Aprobado por Unanimidad'"
  ],
  "documentos": [
    "RG"
  ]
}
```

## 02. `ENR-B1-V05` — `enrutador` | `factual` | split `val`
**Pregunta base:** ¿Qué define reglamentariamente al 'Alumno Autorizado a Matricularse' y hasta qué momento del período lectivo conserva su calidad quien ya es Alumno Regular?
**Unidades referenciadas:** `RG-ART-003-DEF-21`, `RG-ART-050`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Pregunta: ¿Qué define reglamentariamente al 'Alumno Autorizado a Matricularse' y hasta qué momento del período lectivo conserva su calidad quien ya es Alumno Regular?
Salida:
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "tipo": "factual",
  "sub_consultas": [
    "Qué define reglamentariamente al 'Alumno Autorizado a Matricularse' y hasta qué momento del período lectivo conserva su calidad quien ya es Alumno Regular"
  ],
  "documentos": [
    "RG"
  ]
}
```

## 03. `ENR-B4-T01` — `enrutador` | `numerica` | split `train`
**Pregunta base:** Según el Calendario de Docencia de Pregrado 2026, ¿cuántos días corridos inclusive duran las actividades de Vinculación a la Vida Universitaria y cuántos días inclusive suman con las vacaciones de invierno del primer semestre?
**Unidades referenciadas:** `CAL-2026-S1-01`, `CAL-2026-S1-14`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Pregunta: Según el Calendario de Docencia de Pregrado 2026, ¿cuántos días corridos inclusive duran las actividades de Vinculación a la Vida Universitaria y cuántos días inclusive suman con las vacaciones de invierno del primer semestre?
Salida:
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "tipo": "numerica",
  "sub_consultas": [
    "Según el Calendario de Docencia de Pregrado 2026, cuántos días corridos inclusive duran las actividades de Vinculación a la Vida Universitaria",
    "cuántos días inclusive suman con las vacaciones de invierno del primer semestre"
  ],
  "documentos": [
    "CAL"
  ]
}
```

## 04. `ENR-B4-V01` — `enrutador` | `numerica` | split `val`
**Pregunta base:** En las filas de reprobación de la escala 1 a 100 del Anexo, ¿a qué calificaciones en escala 1,0 a 7,0 equivalen 5 y 31 puntos, y cuál es la diferencia entre ambas notas?
**Unidades referenciadas:** `RG-ANEXO-05`, `RG-ANEXO-31`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Pregunta: En las filas de reprobación de la escala 1 a 100 del Anexo, ¿a qué calificaciones en escala 1,0 a 7,0 equivalen 5 y 31 puntos, y cuál es la diferencia entre ambas notas?
Salida:
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "tipo": "numerica",
  "sub_consultas": [
    "En las filas de reprobación de la escala 1 a 100 del Anexo, a qué calificaciones en escala 1,0 a 7,0 equivalen 5 y 31 puntos",
    "cuál es la diferencia entre ambas notas"
  ],
  "documentos": [
    "RG"
  ]
}
```

## 05. `ENR-B2-T01` — `enrutador` | `condicional` | split `train`
**Pregunta base:** ¿Qué condiciones, límites de tiempo y excepciones rigen el abandono de asignaturas sin especificación de motivos?
**Unidades referenciadas:** `RG-ART-043`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Pregunta: ¿Qué condiciones, límites de tiempo y excepciones rigen el abandono de asignaturas sin especificación de motivos?
Salida:
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "tipo": "condicional",
  "sub_consultas": [
    "Qué condiciones, límites de tiempo y excepciones rigen el abandono de asignaturas sin especificación de motivos"
  ],
  "documentos": [
    "RG"
  ]
}
```

## 06. `ENR-B2-V01` — `enrutador` | `condicional` | split `val`
**Pregunta base:** ¿Qué excepciones e información especial contempla el Reglamento General sobre cómo se asignan las asignaturas bajo un Programa de Bachillerato frente a una carrera de Licenciatura o Título?
**Unidades referenciadas:** `RG-ART-003-DEF-01`, `RG-ART-003-DEF-02`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Pregunta: ¿Qué excepciones e información especial contempla el Reglamento General sobre cómo se asignan las asignaturas bajo un Programa de Bachillerato frente a una carrera de Licenciatura o Título?
Salida:
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "tipo": "condicional",
  "sub_consultas": [
    "Qué excepciones e información especial contempla el Reglamento General sobre cómo se asignan las asignaturas bajo un Programa de Bachillerato frente a una carrera de Licenciatura o Título"
  ],
  "documentos": [
    "RG"
  ]
}
```

## 07. `ENR-B1-T01` — `enrutador` | `cruce` | split `train`
**Pregunta base:** ¿Qué requisito previo sobre docencia debe cumplir un alumno para inscribir asignaturas y en qué casos un profesor queda exento de ser evaluado en esa encuesta?
**Unidades referenciadas:** `RG-ART-042`, `RG-ART-007`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Pregunta: ¿Qué requisito previo sobre docencia debe cumplir un alumno para inscribir asignaturas y en qué casos un profesor queda exento de ser evaluado en esa encuesta?
Salida:
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "tipo": "cruce",
  "sub_consultas": [
    "Qué requisito previo sobre docencia debe cumplir un alumno para inscribir asignaturas",
    "en qué casos un profesor queda exento de ser evaluado en esa encuesta"
  ],
  "documentos": [
    "RG"
  ]
}
```

## 08. `ENR-B1-V01` — `enrutador` | `cruce` | split `val`
**Pregunta base:** ¿Qué facilidades académicas corresponden a dirigentes estudiantiles acreditados y qué deben hacer estudiantes con impedimentos religiosos o discapacidad al inscribir asignaturas?
**Unidades referenciadas:** `RG-ART-052`, `RG-ART-020`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Pregunta: ¿Qué facilidades académicas corresponden a dirigentes estudiantiles acreditados y qué deben hacer estudiantes con impedimentos religiosos o discapacidad al inscribir asignaturas?
Salida:
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "tipo": "cruce",
  "sub_consultas": [
    "Qué facilidades académicas corresponden a dirigentes estudiantiles acreditados",
    "qué deben hacer estudiantes con impedimentos religiosos o discapacidad al inscribir asignaturas"
  ],
  "documentos": [
    "RG"
  ]
}
```

## 09. `ENR-B3-T03` — `enrutador` | `premisa_falsa` | split `train`
**Pregunta base:** Un compañero me aseguró que cuando un estudiante es autorizado a suspender estudios por salud, la decisión final de su reincorporación le corresponde únicamente al Vicedecano y que la suspensión puede durar hasta cinco años calendario. ¿Es cierto?
**Unidades referenciadas:** `RG-ART-033`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Pregunta: Un compañero me aseguró que cuando un estudiante es autorizado a suspender estudios por salud, la decisión final de su reincorporación le corresponde únicamente al Vicedecano y que la suspensión puede durar hasta cinco años calendario. ¿Es cierto?
Salida:
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "tipo": "premisa_falsa",
  "sub_consultas": [
    "Un compañero me aseguró que cuando un estudiante es autorizado a suspender estudios por salud, la decisión final de su reincorporación le corresponde únicamente al Vicedecano y que la suspensión puede durar hasta cinco años calendario. Es cierto"
  ],
  "documentos": [
    "RI-FI",
    "RG"
  ]
}
```

## 10. `ENR-B3-V02` — `enrutador` | `premisa_falsa` | split `val`
**Pregunta base:** El calendario 2026 dispone que todas las clases del primer semestre —incluidas las asignaturas anuales— finalizan el 10 de julio. ¿Es correcto?
**Unidades referenciadas:** `CAL-2026-S1-04`, `CAL-2026-S1-05`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Pregunta: El calendario 2026 dispone que todas las clases del primer semestre —incluidas las asignaturas anuales— finalizan el 10 de julio. ¿Es correcto?
Salida:
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "tipo": "premisa_falsa",
  "sub_consultas": [
    "El calendario 2026 dispone que todas las clases del primer semestre —incluidas las asignaturas anuales— finalizan el 10 de julio. Es correcto"
  ],
  "documentos": [
    "CAL"
  ]
}
```

## 11. `REC-B1-T01-S1` — `recuperador` | `suficiente` | split `train`
**Pregunta base:** ¿Qué requisito previo sobre docencia debe cumplir un alumno para inscribir asignaturas y en qué casos un profesor queda exento de ser evaluado en esa encuesta?
**Unidades referenciadas:** `RG-ART-007`, `RG-ART-010`, `RG-ART-014`, `RG-ART-019`, `RG-ART-042`, `RI-FI-ART-007`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Responde SOLO con el JSON de la acción.
Contexto: {"sub": "Qué requisito previo sobre docencia debe cumplir un alumno para inscribir asignaturas", "tipo": "cruce", "documentos": ["RG"], "evidencia_reunida": ["RG-ART-042", "RG-ART-007", "RG-ART-019", "RG-ART-010", "RI-FI-ART-007", "RG-ART-014"], "ultima_observacion": null, "intento": 1, "feedback_verificador": null}
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "accion": "suficiente",
  "args": {}
}
```

## 12. `REC-B1-V04-RS` — `recuperador` | `suficiente` | split `val`
**Pregunta base:** ¿Qué autoridad asume la administración centralizada de aulas en los campus Chillán y Los Ángeles frente a Concepción, y quién declara la salud incompatible de un alumno?
**Unidades referenciadas:** `RG-ART-014`, `RG-ART-032`, `RG-ART-033`, `RG-ART-034`, `RG-ART-035`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Responde SOLO con el JSON de la acción.
Contexto: {"sub": "Qué autoridad asume la administración centralizada de aulas en los campus Chillán y Los Ángeles frente a Concepción", "tipo": "cruce", "documentos": ["RG"], "evidencia_reunida": ["RG-ART-014", "RG-ART-032", "RG-ART-033", "RG-ART-034", "RG-ART-035"], "ultima_observacion": {"aviso": "Ya hiciste exactamente esta acción y no aportó nada nuevo. Busca con OTRAS palabras o responde 'suficiente'."}, "intento": 2, "feedback_verificador": null}
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "accion": "suficiente",
  "args": {}
}
```

## 13. `REC-B1-T07-B1` — `recuperador` | `buscar` | split `train`
**Pregunta base:** Si más de la mitad de los alumnos que rinden una evaluación obtienen nota inferior a 4,0 y un estudiante revisa su prueba pero persiste en desacuerdo con su nota, ¿qué instancias actúan en cada situación?
**Unidades referenciadas:** `RG-ART-008`, `RG-ART-021`, `RG-ART-033`, `RG-ART-034`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Responde SOLO con el JSON de la acción.
Contexto: {"sub": "Si más de la mitad de los alumnos que rinden una evaluación obtienen nota inferior a 4,0 y un estudiante revisa su prueba pero persiste en desacuerdo con su nota, qué instancias actúan en cada situación", "tipo": "cruce", "documentos": ["RG"], "evidencia_reunida": ["RG-ART-021", "RG-ART-033", "RG-ART-034", "RG-ART-008"], "ultima_observacion": null, "intento": 1, "feedback_verificador": null}
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "accion": "buscar",
  "args": {
    "consulta": "mitad alumnos rinden evaluacion obtienen articulo asignatura",
    "k": 5
  }
}
```

## 14. `REC-B1-T12-B1` — `recuperador` | `buscar` | split `train`
**Pregunta base:** Si un estudiante ingresa directamente a segundo o tercer año de Ingeniería por convalidaciones o revalidaciones, ¿qué asignaturas se excluyen al verificar el requisito de créditos aprobados del Art. 14 b) y qué pasa con su carga semestral?
**Unidades referenciadas:** `RG-ART-003-DEF-11`, `RG-ART-022`, `RG-ART-025`, `RG-ART-037`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Responde SOLO con el JSON de la acción.
Contexto: {"sub": "Si un estudiante ingresa directamente a segundo o tercer año de Ingeniería por convalidaciones o revalidaciones, qué asignaturas se excluyen al verificar el requisito de créditos aprobados del Art. 14 b)", "tipo": "cruce", "documentos": ["RI-FI", "RG"], "evidencia_reunida": ["RG-ART-037", "RG-ART-022", "RG-ART-025", "RG-ART-003-DEF-11"], "ultima_observacion": null, "intento": 1, "feedback_verificador": null}
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "accion": "buscar",
  "args": {
    "consulta": "ingresa directamente segundo tercer ingenieria articulo consecuencia",
    "k": 5
  }
}
```

## 15. `REC-B3-V02-B1` — `recuperador` | `buscar` | split `val`
**Pregunta base:** El calendario 2026 dispone que todas las clases del primer semestre —incluidas las asignaturas anuales— finalizan el 10 de julio. ¿Es correcto?
**Unidades referenciadas:** `CAL-2026-S1-06`, `CAL-2026-S1-14`, `RG-ART-003-DEF-07`, `RG-ART-032`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Responde SOLO con el JSON de la acción.
Contexto: {"sub": "El calendario 2026 dispone que todas las clases del primer semestre —incluidas las asignaturas anuales— finalizan el 10 de julio. Es correcto", "tipo": "premisa_falsa", "documentos": ["CAL"], "evidencia_reunida": ["CAL-2026-S1-06", "CAL-2026-S1-14", "RG-ART-032", "RG-ART-003-DEF-07"], "ultima_observacion": null, "intento": 1, "feedback_verificador": null}
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "accion": "buscar",
  "args": {
    "consulta": "calendario 2026 dispone todas clases docencia pregrado",
    "k": 5
  }
}
```

## 16. `REC-B1-T15-FB` — `recuperador` | `traer` | split `train`
**Pregunta base:** ¿Qué siglas se consignan en el Acta de Notas para asignaturas de evaluación cualitativa y qué sigla se usa si el Vicedecano autoriza por razones fundadas no rendir la Evaluación de Recuperación?
**Unidades referenciadas:** `RG-ART-021`, `RG-ART-027`, `RG-ART-041`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Responde SOLO con el JSON de la acción.
Contexto: {"sub": "qué sigla se usa si el Vicedecano autoriza por razones fundadas no rendir la Evaluación de Recuperación", "tipo": "cruce", "documentos": ["RI-FI", "RG"], "evidencia_reunida": ["RG-ART-021", "RG-ART-027", "RG-ART-041"], "ultima_observacion": null, "intento": 1, "feedback_verificador": "Falta recuperar el Artículo 22 de RG (RG-ART-022) para responder de forma completa."}
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "accion": "traer",
  "args": {
    "doc": "RG",
    "n": 22
  }
}
```

## 17. `REC-B1-T22-T2` — `recuperador` | `traer` | split `train`
**Pregunta base:** ¿Qué consigna el Diploma de Grado Académico frente al Diploma de Título Profesional respecto de nota versus concepto, y hasta qué momento conserva el estudiante la calidad de alumno regular entre períodos?
**Unidades referenciadas:** `RG-ART-003-DEF-03`, `RG-ART-003-DEF-04`, `RG-ART-048`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Responde SOLO con el JSON de la acción.
Contexto: {"sub": "Qué consigna el Diploma de Grado Académico frente al Diploma de Título Profesional respecto de nota versus concepto, y hasta qué momento conserva el estudiante la calidad de alumno regular entre períodos", "tipo": "cruce", "documentos": ["RG"], "evidencia_reunida": ["RG-ART-003-DEF-03", "RG-ART-003-DEF-04", "RG-ART-048"], "ultima_observacion": [{"id": "RG-ART-048", "extracto": "Artículo 48° El Diploma de Grado Académico que otorgue la Universidad de Concepción, indicará la Nota obtenida por el egresado. Cuando se trate del Diploma de T"}, {"id": "RG-ART-003-DEF-03", "extracto": "3.3. GRADO DE LICENCIADO: Los estudios conducentes al grado de Licenciado comprenden todos los aspectos esenciales de un área del conocimiento o de una discipli"}, {"id": "RG-ART-003-DEF-04", "extracto": "3.4. TÍTULO PROFESIONAL: Los estudios conducentes a un Título Profesional comprenden una formación general y científica necesaria para un adecuado desempeño pro"}, {"id": "RG-ART-003-DEF-15", "extracto": "3.15. ALUMNO REGULAR: Para ser alumno regular de la Universidad de Concepción se requiere:\n\na) Haber sido aceptado mediante cualquiera de los procesos de admisi"}], "intento": 2, "feedback_verificador": null}
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "accion": "traer",
  "args": {
    "doc": "RG",
    "n": 48
  }
}
```

## 18. `REC-B6-V02-T2` — `recuperador` | `traer` | split `val`
**Pregunta base:** ¿Qué dispone el Artículo 15° del Reglamento General respecto a la remuneración económica de los Tutores Académicos y Monitores Estudiantiles?
**Unidades referenciadas:** `RG-ART-002`, `RG-ART-015`, `RG-ART-052`

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Responde SOLO con el JSON de la acción.
Contexto: {"sub": "Qué dispone el Artículo 15° del Reglamento General respecto a la remuneración económica de los Tutores Académicos y Monitores Estudiantiles", "tipo": "factual", "documentos": ["RG"], "evidencia_reunida": ["RG-ART-002", "RG-ART-052", "RG-ART-015"], "ultima_observacion": [{"id": "RG-ART-015", "extracto": "Artículo 15º La Facultad podrá organizar y mantener un sistema de apoyo al estudiante en coordinación con los organismos institucionales que correspondan, con e"}, {"id": "RG-ART-002", "extracto": "Artículo 2° La docencia es una actividad fundamental y prioritaria en la Universidad de Concepción. La docencia de pregrado constituye el primer nivel de formac"}, {"id": "RG-ART-052", "extracto": "Artículo 52° A los alumnos que deban cumplir funciones de representación estudiantil reconocidas por la Universidad, se les otorgarán por el Vicedecano respecti"}, {"id": "RG-ART-008", "extracto": "Artículo 8º Habrá un Jefe de Carrera en cada campus en que ella se dicte, designado por el Decano respectivo, con conocimiento del Consejo de Carrera, debiendo "}], "intento": 2, "feedback_verificador": null}
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "accion": "traer",
  "args": {
    "doc": "RG",
    "n": 15
  }
}
```

## 19. `REC-ENR-X-T30-EX` — `recuperador` | `existe` | split `train`
**Pregunta base:** Me indicaron que el Artículo 95 del Reglamento General prohíbe reincorporarse más de una vez en la carrera; ¿qué dice ese artículo exactamente?

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Responde SOLO con el JSON de la acción.
Contexto: {"sub": "verificar existencia del artículo 95 en RG", "tipo": "premisa_falsa", "documentos": ["RG"], "evidencia_reunida": [], "ultima_observacion": null, "intento": 1, "feedback_verificador": null}
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "accion": "existe",
  "args": {
    "doc": "RG",
    "n": 95
  }
}
```

## 20. `REC-ENR-X-V04-EX` — `recuperador` | `existe` | split `val`
**Pregunta base:** Entiendo que el Artículo 41 del Reglamento Interno de Ingeniería permite convalidar asignaturas cursadas hace más de 15 años sin revisión de programa. ¿Es así?

<details>
<summary>Entrada al agente (extracto contextual del prompt)</summary>

```text
Responde SOLO con el JSON de la acción.
Contexto: {"sub": "verificar existencia del artículo 41 en RI-FI", "tipo": "premisa_falsa", "documentos": ["RI-FI", "RG"], "evidencia_reunida": [], "ultima_observacion": null, "intento": 1, "feedback_verificador": null}
```

</details>

**Salida esperada (`assistant`):**
```json
{
  "accion": "existe",
  "args": {
    "doc": "RI-FI",
    "n": 41
  }
}
```
