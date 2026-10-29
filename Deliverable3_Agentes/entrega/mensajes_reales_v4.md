# Mensajes reales de la versión congelada v4

Material para grabar la demostración: **revisión de una ejecución real conservada**, no inferencia nueva ni video entregado. Corresponde al piloto de cuatro preguntas, no al lote de 300 respuestas. Las selecciones muestran un acierto y un fallo; no representan una estimación de rendimiento. Los mensajes JSON se transcriben sin corregirlos.

## P05: ¿Cuál es la actividad final de titulación en las carreras de Ingeniería?

[JSON original](../resultados/piloto_6a4e8925ada1fa3d1dee/original/resultados/P005_agentes_completo.json) · [Evaluación del piloto](../resultados/piloto_6a4e8925ada1fa3d1dee/REPORTE.md)

SHA-256: `ded70427a323ff696a2368b551f0b3d06721eb019ad63449aff16b6a6daf3b61`

Corrida: `6a4e8925ada1fa3d1dee9c585ce825d7f093f809a18523407376638b2f5e12b4`

Estado interno: `aceptada`. Evaluación externa: **correcta**. Llamadas al modelo: 3.

En esta ejecución no hubo devolución para corregir: investigador → redactor → auditor → aceptación. El extracto elegido por el auditor para RG 3.10 es incompleto; la evaluación externa revisó la unidad completa, que sí contempla Memoria. La aceptación interna no equivale a exactitud.

### Evento 4 · transferencia

```json
{
  "orden": 4,
  "tipo": "transferencia",
  "emisor": "investigador",
  "receptor": "redactor",
  "mensaje": "La actividad final de titulación en las carreras de Ingeniería es la Memoria de Título, según el artículo 29 del Reglamento Interno de Docencia de Pregrado de Ingeniería (RI-FI).",
  "borrador": "",
  "fuentes": [
    "RI-FI-ART-029",
    "RI-FI-ART-006",
    "RG-ART-003-DEF-10",
    "RI-FI-ART-005",
    "RI-FI-ART-030"
  ]
}
```

### Evento 7 · transferencia

```json
{
  "orden": 7,
  "tipo": "transferencia",
  "emisor": "redactor",
  "receptor": "auditor",
  "mensaje": "Auditoría de la actividad final de titulación en carreras de Ingeniería",
  "borrador": "La actividad final de titulación en las carreras de Ingeniería es la Memoria de Título, de un semestre de duración, según el artículo 29 del Reglamento Interno de Docencia de Pregrado de Ingeniería (RI-FI). Este requisito se menciona en el artículo 29, y se complementa en el artículo 3 de la norma general (RG-ART-003-DEF-10), donde se establece que las actividades finales de graduación o titulación podrán incluir la Memoria de Título, entre otras opciones. La Memoria de Título se regirá por el Reglamento de Memoria de Título de la Facultad de Ingeniería, según el artículo 29.",
  "fuentes": [
    "RI-FI-ART-029",
    "RI-FI-ART-006",
    "RG-ART-003-DEF-10",
    "RI-FI-ART-005",
    "RI-FI-ART-030"
  ]
}
```

### Evento 9 · decision

```json
{
  "orden": 9,
  "tipo": "decision",
  "agente": "auditor",
  "decision": {
    "accion": "aceptar",
    "mensaje": "La respuesta identifica correctamente la actividad final de titulación en las carreras de Ingeniería como la Memoria de Título, con respaldo en las fuentes proporcionadas.",
    "apoyos": [
      {
        "afirmacion": "La actividad final de titulación es la Memoria de Título",
        "fuente": "RI-FI-ART-029",
        "extracto": "Artículo 29°. La actividad final de titulación para todas las carreras será una asignatura denominada Memoria de Título, de un semestre de duración, la que se regirá por el Reglamento de Memoria de Título de la Facultad de Ingeniería."
      },
      {
        "afirmacion": "La Memoria de Título se regirá por el Reglamento de Memoria de Título de la Facultad de Ingeniería",
        "fuente": "RI-FI-ART-029",
        "extracto": "la que se regirá por el Reglamento de Memoria de Título de la Facultad de Ingeniería."
      },
      {
        "afirmacion": "Las actividades finales de graduación o titulación podrán incluir la Memoria de Título",
        "fuente": "RG-ART-003-DEF-10",
        "extracto": "Las actividades finales de graduación o titulación podrán consistir en Habilitación Profesional, Examen de Grado o Título, Defensa de Título, Proyecto de Grado o Título o Proposición Plástica."
      }
    ]
  }
}
```

### Evento 10 · fin

```json
{
  "orden": 10,
  "tipo": "fin",
  "estado": "aceptada",
  "respuesta": "La actividad final de titulación en las carreras de Ingeniería es la Memoria de Título, de un semestre de duración, según el artículo 29 del Reglamento Interno de Docencia de Pregrado de Ingeniería (RI-FI). Este requisito se menciona en el artículo 29, y se complementa en el artículo 3 de la norma general (RG-ART-003-DEF-10), donde se establece que las actividades finales de graduación o titulación podrán incluir la Memoria de Título, entre otras opciones. La Memoria de Título se regirá por el Reglamento de Memoria de Título de la Facultad de Ingeniería, según el artículo 29."
}
```

### Respuesta final literal

La actividad final de titulación en las carreras de Ingeniería es la Memoria de Título, de un semestre de duración, según el artículo 29 del Reglamento Interno de Docencia de Pregrado de Ingeniería (RI-FI). Este requisito se menciona en el artículo 29, y se complementa en el artículo 3 de la norma general (RG-ART-003-DEF-10), donde se establece que las actividades finales de graduación o titulación podrán incluir la Memoria de Título, entre otras opciones. La Memoria de Título se regirá por el Reglamento de Memoria de Título de la Facultad de Ingeniería, según el artículo 29.

## P41: ¿Qué establece el Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería?

[JSON original](../resultados/piloto_6a4e8925ada1fa3d1dee/original/resultados/P041_agentes_completo.json) · [Evaluación del piloto](../resultados/piloto_6a4e8925ada1fa3d1dee/REPORTE.md)

SHA-256: `2f558d5f1bc117c4e83d85d3effeacbadd0cd43c7ba0d72a934cdcbb1c384da3`

Corrida: `6a4e8925ada1fa3d1dee9c585ce825d7f093f809a18523407376638b2f5e12b4`

Estado interno: `limite_llamadas`. Evaluación externa: **incorrecta**. Llamadas al modelo: 12.

Los borradores reconocen la ausencia del artículo en esta copia, pero el auditor sigue devolviendo correcciones; el controlador interrumpe la repetición y pide investigar. La lectura y su inventario sí se ejecutan. Finalmente se agota el límite de 12 llamadas. Mostrar la respuesta final técnica, no un borrador favorable como si fuera el resultado entregado.

### Evento 7 · transferencia

```json
{
  "orden": 7,
  "tipo": "transferencia",
  "emisor": "redactor",
  "receptor": "auditor",
  "mensaje": "Artículo 90 no encontrado en el Reglamento Interno de Docencia de Pregrado de Ingeniería según el inventario.",
  "borrador": "El Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería no existe en la copia actual, según el inventario [INV-26d1a0f96f94ffe0]. El documento RI-FI no incluye este artículo, lo cual se confirma en el inventario proporcionado.",
  "fuentes": [
    "RI-FI-ART-002",
    "RG-TRANS-002",
    "RG-ART-049",
    "RG-ART-001",
    "RG-ART-038",
    "INV-26d1a0f96f94ffe0"
  ]
}
```

### Evento 10 · transferencia

```json
{
  "orden": 10,
  "tipo": "transferencia",
  "emisor": "auditor",
  "receptor": "redactor",
  "mensaje": "Artículo 90 no está disponible en el Reglamento Interno de Docencia de Pregrado de Ingeniería según el inventario.",
  "borrador": "El Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería no existe en la copia actual, según el inventario [INV-26d1a0f96f94ffe0]. El documento RI-FI no incluye este artículo, lo cual se confirma en el inventario proporcionado.",
  "fuentes": [
    "RI-FI-ART-002",
    "RG-TRANS-002",
    "RG-ART-049",
    "RG-ART-001",
    "RG-ART-038",
    "INV-26d1a0f96f94ffe0"
  ]
}
```

### Evento 13 · borrador_bloqueado

```json
{
  "orden": 13,
  "tipo": "borrador_bloqueado",
  "detalle": "La misma respuesta ya fue revisada con estas fuentes y no progresó. Investiga la carencia antes de redactar de nuevo.",
  "borrador": "El Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería no existe en la copia actual, según el inventario [INV-26d1a0f96f94ffe0]. El documento RI-FI no incluye este artículo, lo cual se confirma en el inventario proporcionado."
}
```

### Evento 16 · decision

```json
{
  "orden": 16,
  "tipo": "decision",
  "agente": "investigador",
  "decision": {
    "accion": "herramienta",
    "mensaje": "Se necesita leer el artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería para conocer su contenido.",
    "herramienta": {
      "nombre": "leer_articulo",
      "argumentos": {
        "documento": "RI-FI",
        "numero": 90
      }
    }
  }
}
```

### Evento 17 · observacion

```json
{
  "orden": 17,
  "tipo": "observacion",
  "agente": "investigador",
  "solicitud": {
    "nombre": "leer_articulo",
    "argumentos": {
      "documento": "RI-FI",
      "numero": 90
    }
  },
  "resultado": {
    "fuentes": [
      {
        "id": "INV-RI-FI",
        "cita": "Inventario completo: Reglamento_de_Docencia_de_Pregrado-FI.pdf",
        "texto": "Inventario completo de esta copia. Artículos ordinarios disponibles: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35\n{\"alcance\":\"copia del corpus, no normativa externa\",\"documento\":\"RI-FI\",\"entradas\":[{\"ambito\":\"ordinario\",\"articulo\":1,\"id\":\"RI-FI-ART-001\",\"paginas\":[1]},{\"ambito\":\"ordinario\",\"articulo\":2,\"id\":\"RI-FI-ART-002\",\"paginas\":[1]},{\"ambito\":\"ordinario\",\"articulo\":3,\"id\":\"RI-FI-ART-003\",\"paginas\":[1]},{\"ambito\":\"ordinario\",\"articulo\":4,\"id\":\"RI-FI-ART-004\",\"paginas\":[1]},{\"ambito\":\"ordinario\",\"articulo\":5,\"id\":\"RI-FI-ART-005\",\"paginas\":[1]},{\"ambito\":\"ordinario\",\"articulo\":6,\"id\":\"RI-FI-ART-006\",\"paginas\":[1]},{\"ambito\":\"ordinario\",\"articulo\":7,\"id\":\"RI-FI-ART-007\",\"paginas\":[2]},{\"ambito\":\"ordinario\",\"articulo\":8,\"id\":\"RI-FI-ART-008\",\"paginas\":[2]},{\"ambito\":\"ordinario\",\"articulo\":9,\"id\":\"RI-FI-ART-009\",\"paginas\":[2]},{\"ambito\":\"ordinario\",\"articulo\":10,\"id\":\"RI-FI-ART-010\",\"paginas\":[2]},{\"ambito\":\"ordinario\",\"articulo\":11,\"id\":\"RI-FI-ART-011\",\"paginas\":[2]},{\"ambito\":\"ordinario\",\"articulo\":12,\"id\":\"RI-FI-ART-012\",\"paginas\":[2]},{\"ambito\":\"ordinario\",\"articulo\":13,\"id\":\"RI-FI-ART-013\",\"paginas\":[2,3]},{\"ambito\":\"ordinario\",\"articulo\":14,\"id\":\"RI-FI-ART-014\",\"paginas\":[3]},{\"ambito\":\"ordinario\",\"articulo\":15,\"id\":\"RI-FI-ART-015\",\"paginas\":[3]},{\"ambito\":\"ordinario\",\"articulo\":16,\"id\":\"RI-FI-ART-016\",\"paginas\":[3]},{\"ambito\":\"ordinario\",\"articulo\":17,\"id\":\"RI-FI-ART-017\",\"paginas\":[3]},{\"ambito\":\"ordinario\",\"articulo\":18,\"id\":\"RI-FI-ART-018\",\"paginas\":[3]},{\"ambito\":\"ordinario\",\"articulo\":19,\"id\":\"RI-FI-ART-019\",\"paginas\":[3]},{\"ambito\":\"ordinario\",\"articulo\":20,\"id\":\"RI-FI-ART-020\",\"paginas\":[4]},{\"ambito\":\"ordinario\",\"articulo\":21,\"id\":\"RI-FI-ART-021\",\"paginas\":[4]},{\"ambito\":\"ordinario\",\"articulo\":22,\"id\":\"RI-FI-ART-022\",\"paginas\":[4]},{\"ambito\":\"ordinario\",\"articulo\":23,\"id\":\"RI-FI-ART-023\",\"paginas\":[4]},{\"ambito\":\"ordinario\",\"articulo\":24,\"id\":\"RI-FI-ART-024\",\"paginas\":[4]},{\"ambito\":\"ordinario\",\"articulo\":25,\"id\":\"RI-FI-ART-025\",\"paginas\":[4]},{\"ambito\":\"ordinario\",\"articulo\":26,\"id\":\"RI-FI-ART-026\",\"paginas\":[4]},{\"ambito\":\"ordinario\",\"articulo\":27,\"id\":\"RI-FI-ART-027\",\"paginas\":[5]},{\"ambito\":\"ordinario\",\"articulo\":28,\"id\":\"RI-FI-ART-028\",\"paginas\":[5]},{\"ambito\":\"ordinario\",\"articulo\":29,\"id\":\"RI-FI-ART-029\",\"paginas\":[5]},{\"ambito\":\"ordinario\",\"articulo\":30,\"id\":\"RI-FI-ART-030\",\"paginas\":[5]},{\"ambito\":\"ordinario\",\"articulo\":31,\"id\":\"RI-FI-ART-031\",\"paginas\":[5]},{\"ambito\":\"ordinario\",\"articulo\":32,\"id\":\"RI-FI-ART-032\",\"paginas\":[5]},{\"ambito\":\"ordinario\",\"articulo\":33,\"id\":\"RI-FI-ART-033\",\"paginas\":[6]},{\"ambito\":\"ordinario\",\"articulo\":34,\"id\":\"RI-FI-ART-034\",\"paginas\":[6]},{\"ambito\":\"ordinario\",\"articulo\":35,\"id\":\"RI-FI-ART-035\",\"paginas\":[6]}]}"
      }
    ],
    "observacion": "Artículo ordinario 90 ausente de esta copia; consultar el inventario.",
    "segundos": 0.00040852400002222566,
    "checkpoint_reutilizado": false
  },
  "origen": "decision_agente"
}
```

### Evento 23 · transferencia

```json
{
  "orden": 23,
  "tipo": "transferencia",
  "emisor": "redactor",
  "receptor": "auditor",
  "mensaje": "Artículo 90 del RI-FI no encontrado en esta copia.",
  "borrador": "El Artículo 90 del Reglamento Interno de Docencia de Pregrado de Ingeniería no existe en esta copia. Según el inventario, el artículo no está disponible. El Reglamento Interno de Docencia de Pregrado de Ingeniería en esta copia solo incluye artículos del 1 al 35. Para obtener información sobre el Artículo 90, se recomienda consultar la versión original o buscar la norma correspondiente.",
  "fuentes": [
    "RI-FI-ART-002",
    "RG-TRANS-002",
    "RG-ART-049",
    "RG-ART-001",
    "RG-ART-038",
    "INV-26d1a0f96f94ffe0",
    "INV-RI-FI"
  ]
}
```

### Evento 25 · decision

```json
{
  "orden": 25,
  "tipo": "decision",
  "agente": "auditor",
  "decision": {
    "accion": "corregir",
    "mensaje": "El Artículo 90 no existe en esta copia del Reglamento Interno de Docencia de Pregrado de Ingeniería.",
    "apoyos": [
      {
        "afirmacion": "El Artículo 90 no existe en esta copia del Reglamento Interno de Docencia de Pregrado de Ingeniería.",
        "fuente": "INV-RI-FI",
        "extracto": "Inventario completo de esta copia. Artículos ordinarios disponibles: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35"
      }
    ]
  }
}
```

### Evento 32 · ciclo_interrumpido

```json
{
  "orden": 32,
  "tipo": "ciclo_interrumpido",
  "detalle": "Dos correcciones sin nueva evidencia. Investiga esta carencia: Artículo 90 no encontrado en la copia actual. Se recomienda consultar la versión original."
}
```

### Evento 36 · salida_invalida

```json
{
  "orden": 36,
  "tipo": "salida_invalida",
  "agente": "investigador",
  "detalle": "Usa solo accion, mensaje y herramienta; faltan: ninguna; sobran: argumentos. Elimina las claves sobrantes. No copies las fuentes; el programa ya las conserva."
}
```

### Evento 40 · fin

```json
{
  "orden": 40,
  "tipo": "fin",
  "estado": "limite_llamadas",
  "respuesta": "No se obtuvo una respuesta validada dentro del presupuesto de esta consulta. Esto no demuestra que la información esté ausente del corpus."
}
```

### Respuesta final literal

No se obtuvo una respuesta validada dentro del presupuesto de esta consulta. Esto no demuestra que la información esté ausente del corpus.
