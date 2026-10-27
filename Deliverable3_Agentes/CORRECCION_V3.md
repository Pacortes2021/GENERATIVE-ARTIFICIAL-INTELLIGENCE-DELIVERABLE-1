# Corrección v3: salidas breves y reparación del contrato

Código 0.3.0, protocolo `d3-agentes-desde-cero-v3`, etiqueta `piloto-v3`. Inferencia real pendiente.

El piloto v2 mostró cinco salidas cortadas, copia del corpus por el investigador y mensajes de formato poco útiles. Los agentes acertaron 1/4 frente a 2/4 de D2; se conserva toda esa evidencia.

Cambios generales:

- El investigador recibe una instrucción explícita: el programa ya transfiere las fuentes, por lo que debe devolver solo una decisión breve. Se eliminó el ejemplo de mensaje que el modelo repetía literalmente y se aclararon los campos permitidos.
- Redactor y auditor reciben instrucciones más concisas; deben responder a lo solicitado, evitar especulación sobre artículos ausentes y usar extractos breves. No se incorporan respuestas de los cuatro casos ni reglas por pregunta.
- El error de contrato enumera claves faltantes y sobrantes. Ante una salida cortada, la reparación pide una decisión breve sin copiar artículos. No se aceptan ni adoptan fuentes escritas por el modelo.
- La comprobación de IDs reconoce también identificadores en prosa o paréntesis, evitando que una cita inventada eluda la validación por no usar corchetes.

No se aumentaron los presupuestos ni se cambiaron pesos, muestreo, controles baseline/D2, semillas o bloques experimentales. Las cuatro condiciones de agentes comparten el protocolo operativo. Cada ablación sigue retirando solo su bloque específico.

Verificación: 37 pruebas locales aprobadas; [700 prompts medidos con E5 y tokenizador reales](validacion/cpu_v3/reporte.json), sin inferencia Qwen. El [notebook actual](Deliverable3_Agentes_Colab.ipynb) lleva v3 en el título, ejecuta el piloto y descarga el ZIP. La utilidad de estas instrucciones requiere el nuevo piloto T4; no se declara mejora de exactitud.
