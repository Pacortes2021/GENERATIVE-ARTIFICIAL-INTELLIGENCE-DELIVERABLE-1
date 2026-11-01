# Evidencia de la grabación

[Video de la demostración](https://drive.google.com/drive/folders/1tkhRhI4_G7ArWNHW7zNoeZi8lL9RyPf2?usp=sharing) (≤ 3 minutos, acceso abierto).

Trazas de las entradas que aparecen en el video:

- **H17 (ejecución nueva):** [`evidencia_video_20261101T021610_5134d8.zip`](evidencia_video_20261101T021610_5134d8.zip),
  exportado por la celda C1 de `Demo_D3.ipynb` en la sesión grabada. Ejecución `20261101T021307_19529ebd`:
  Qwen3-4B en una Tesla T4, 31 de octubre de 2026 entre 23:13 y 23:15 (hora de Chile), 9 llamadas al modelo,
  respuesta aprobada por el Verificador en un ciclo. El paquete usado es el del commit `d35e432` (SHA-256
  `dee3db3e…a3cb`), el mismo que verifica el cuaderno.
- **H03 (caso de falla, histórico):** clave `dificil_25:H03` en
  [`../Deliverable3/resultados_v6/trazas_D3.json`](../Deliverable3/resultados_v6/trazas_D3.json); también va incluido
  en el ZIP como `fallo_H03_historico.json`.

Contenido del ZIP:

| Ruta | Contenido |
|---|---|
| `ejecuciones/20261101T021307_19529ebd/` | `sesion.json` (prompts completos, salidas crudas, herramientas, intercambios y resultado) y `eventos.jsonl` |
| `fallo_H03_historico.json` | Traza del caso de falla, rotulada como histórica |
| `entorno.json` | GPU, versiones, modelo, parámetros de generación, commit y hash del paquete |
| `fuentes/` | Copia del código, prompts y corpus usados |
| `indice_video.json` | `run_id` de la ejecución que aparece en el video |
| `manifiesto.json` | Hashes de los archivos del ZIP |

El ZIP se conserva tal como lo exportó el cuaderno; su campo `video_url` quedó vacío porque el enlace se publicó
después de la grabación. El enlace está arriba y en el informe.
