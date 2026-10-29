# Lote v4 en diez bloques recuperables

El experimento conserva 50 preguntas × seis condiciones = 300 respuestas. Cada bloque termina en el próximo múltiplo de 30 respuestas (cinco preguntas completas). Consultar siempre `../ESTADO_TRABAJO.md` para saber qué sesión y respaldo están vigentes.

## Ejecutar

En una sesión nueva T4, abrir `../Deliverable3_Agentes_Bloques_Colab.ipynb` y ejecutar preparación, restauración de fuentes y carga una vez. Después ejecutar la última celda para cada bloque. No ejecutar el piloto ni volver a cargar el modelo entre bloques. La copia publicada inicialmente recupera 39 respuestas y completa el bloque 2 en 60; antes de recuperar una sesión perdida desde un respaldo posterior, actualizar URL, SHA-256 y cantidad del respaldo, tras auditarlo.

`reanudar_lote_v4_colab.py` valida el ZIP, entorno de inferencia, preguntas, variantes y configuración completa, incluidas fuentes, prompts e índice. Restaura sin sobrescribir respuestas. La comparación de configuración usa contenido JSON sellado equivalente. El ejecutor original omite resultados existentes y mantiene semillas y orden de variantes. Una capa de exportación en memoria se detiene después de guardar una respuesta completa; no modifica las fuentes experimentales congeladas ni los prompts. La parada prevista no se registra como error técnico. Las excepciones reales se propagan.

Solicita una descarga inmutable cada seis respuestas nuevas y al terminar cada bloque. Comprobar que el archivo llegó realmente a Descargas; una solicitud del navegador no garantiza que haya llegado. Si se autoriza montar Drive, `OUTPUT` puede apuntar a `/content/drive/MyDrive/GenIA_D3_Agentes/runs`: la identidad experimental no depende de esa ruta. No aceptar permisos nuevos de Drive sin autorización del usuario.

## Recoger y auditar antes del bloque siguiente

```bash
python3 operacion/importar_snapshot_lote.py /ruta/al/ZIP_DESCARGADO.zip \
  --previo resultados/lote_99b9b55bd79d4572f743/snapshots/RESPALDO_PREVIO.zip
```

El importador exige la configuración congelada del lote, audita ambos ZIP y comprueba cada respuesta previa byte a byte. Conserva una copia nueva intacta con SHA-256 y procedencia; no sobrescribe ni elimina originales. `--solo-verificar` permite revisar sin copiar. No calcula exactitud: eso requiere evaluación externa. Publicar el respaldo y actualizar el estado antes de continuar.

Validaciones de orquestación (sin inferencia):

```bash
python3 operacion/test_bloques.py
python3 operacion/crear_cuaderno_bloques.py
```

Cuatro pruebas cubren 39→60, 60→90, 299→300 y errores reales. El generador comprueba que el payload experimental del notebook v4 permanece intacto. El importador se verificó con los respaldos reales 35→39 y rechazo del retroceso 39→35.
