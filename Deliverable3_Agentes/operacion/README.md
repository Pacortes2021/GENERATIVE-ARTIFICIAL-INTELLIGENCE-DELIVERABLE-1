# Reanudar el lote v4

La celda `reanudar_lote_v4_colab.py` reemplaza únicamente la sección 6 en el notebook del commit congelado de2951b. Ejecutar antes las secciones 1, 2 y 3; omitir el piloto. No ejecutar esta preparación de nuevo sobre la sesión activa.

Valida SHA-256 del ZIP de 35/300, auditoría interna, inferencia, preguntas, variantes y configuración completa (incluidas fuentes, prompts e índice). Restaura sin sobrescribir respuestas existentes y llama al ejecutor original, que omite resultados conservados. La configuración JSON se compara por contenido sellado porque su orden de claves puede variar. Al terminar o ante una excepción exporta y solicita la descarga. No monta Drive: el ZIP temporal requiere descargas periódicas durante la ejecución.

Validado en T4 el 28-10-2026: configuración idéntica, respaldo restaurado y comienzo de P06 sin_completitud. Código experimental sin modificaciones.
