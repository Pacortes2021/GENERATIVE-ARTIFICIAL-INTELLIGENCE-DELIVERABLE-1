# Estado de trabajo de Deliverable 3

Actualizado el 27-10-2026, tarde de Chile. Autorización vigente: correcciones, inferencia real en Colab T4, descarga y evaluación de todos los intentos, informe LaTeX, guion/video y actualización de GitHub. No usar el prototipo `../Deliverable3/` ni `backup/deliverable3` como implementación. No enviar mensajes a terceros.

## Operación en curso

**Piloto v4 ejecutándose en Colab:** se observó T4 conectada, dependencias instaladas y carga de E5 iniciada. El notebook ejecuta ocho celdas: piloto 4 × 3 condiciones y exportación; lote 50 × 6 desactivado. No recargar, desconectar ni cambiar sus fuentes mientras esté activo.

Pestaña actual, versión congelada:
https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/de2951b22214f294e9f9eb1f5b0fae9a25c622da/Deliverable3_Agentes/Deliverable3_Agentes_Colab.ipynb

Código v4 publicado en `de2951b22214f294e9f9eb1f5b0fae9a25c622da`, paquete 0.4.0, protocolo `d3-agentes-desde-cero-v4`. 38 pruebas aprobadas; 700 prompts medidos con E5 y tokenizador Qwen reales, máximo 3.926 tokens de entrada. No se ejecuta inferencia Qwen en el Mac.

Automatización `seguimiento-nocturno-del-piloto-d3`, nombre «Completar Deliverable 3»: **ACTIVA**, cada cinco minutos. Se reactivó tras «continúa» del usuario. El bloqueo de pantalla anterior está resuelto. No cambiar sus permisos ni crear un duplicado.

## Corridas conservadas y evaluadas

| Versión | Carpeta bajo `resultados/` | Baseline | D2 | Agentes |
|---|---|---:|---:|---:|
| v1 | `piloto_222681994dcd692c0600` | 0/4 | 2/4 | 0/4 |
| v2 | `piloto_14f5ffa72e8a2734d481` | 0/4 | 2/4 | 1/4 |
| v3 | `piloto_9b826dfab6be77ac0ce1` | 0/4 | 2/4 | 1/4 |

ZIP originales intactos y extracciones byte a byte; juicios externos independientes con la pauta D2. Leer REPORTE.md de cada corrida. V3 redujo generación de agentes de 1.453,74 s a 380,05 s, sin mejorar exactitud. P05 es correcta: revisar RG 3.10 **completo**, que sí contempla Memoria; no juzgar solo el extracto incompleto del auditor. P25 omite desarrollar remisiones; P38 carece de respaldo del alcance específico; P41 termina por formato pese al inventario de ausencia. No copiar etiquetas al evaluar v4.

V4 acepta exclusivamente una forma plana equivalente de solicitud explícita de herramienta, conserva argumentos y validadores, precisa IDs de citas y refuerza los tres bloques experimentales. No contiene respuestas de referencia ni rutas por pregunta. Su calidad está pendiente.

## Siguiente secuencia

1. Recoger ZIP v4 en `/Users/pabloignaciocortesvielma/Downloads`; si sigue activo, dejarlo terminar. Auditar antes de importar a carpeta nueva; conservar intento completo, llamadas y fuentes. Evaluar cada respuesta con `evaluar.py` y pauta D2, contrastando fuentes alternativas completas.
2. Resolver fallos operativos si quedan. No convertir cada fallo semántico en otra selección de resultados: cuando el flujo sea utilizable, congelar y ejecutar las **50 preguntas × seis condiciones** sin elegir intentos favorables. Reportar si no supera D2.
3. El programa guarda checkpoints por llamada y actualiza ZIP después de cada respuesta. Durante el lote largo descargar snapshots del ZIP desde Archivos sin interrumpir la ejecución; conservar cada descarga. El almacenamiento temporal de Colab desaparece al terminar la sesión. Drive solo si se logra autorizar de manera apropiada.
4. Evaluar las 300 respuestas externamente y reportar aciertos, regresiones, coste, errores de formato, paradas y cada ablación. Son preguntas de desarrollo, no generalización.
5. Cerrar informe LaTeX y recompilar `entrega/main.tex` → `main.pdf` (una página A4 vertical). El borrador ya contiene pilotos v1/v2/v3 y grafo de agentes/herramientas, decisiones, loops y stops; sigue marcado como incompleto.
6. Ajustar `entrega/guion_video.md` a la versión final. Grabar un video real de pantalla ≤ 3 min con entradas, mensajes y salida; publicar/verificar enlace abierto autorizado. Guion y transcripciones no sustituyen el video. Conservar sus trazas exactas y explicar reproducción.
7. Actualizar GitHub `origin` Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1, sin tocar `upstream`, sin force push y sin incorporar `../Deliverable3/` ajeno. La entrega sigue incompleta.

## Detalles operativos

- El antiguo notebook de Drive `1Y69nHfh0KW6YoIJyDuFVHvCvblxFvRTQ` tuvo conflicto de guardado. No sobrescribir su versión remota. Sus pilotos ya están conservados.
- Abrir desde GitHub evita el selector de subida de Safari que dejaba Cargar desactivado. El aviso normal de Colab «Google no creó este notebook» corresponde al código propio publicado.
- Para UI usar cua_repl. Si el usuario cambia de pestaña, volver a leer el estado antes de actuar. Si el Mac se bloquea, no intentar eludirlo; completar trabajo independiente y explicar el impedimento.
- gh autentica correctamente con acceso de red. Un aviso de token inválido sin red no justifica pedir nuevas credenciales. Las mutaciones de Git/red pueden requerir la aprobación automática de la herramienta.
- LaTeX local: `tectonic` requiere ejecución con acceso de red del entorno; el editor integrado también compila. Revisar `pdfinfo` y render PNG tras cambios.
