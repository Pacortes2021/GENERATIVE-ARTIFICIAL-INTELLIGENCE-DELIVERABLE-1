# Materiales de entrega en preparación

**No entregar todavía.** Faltan los resultados completos de las seis condiciones y el video real con enlace abierto. Los materiales contienen únicamente resultados verificados de los pilotos v1/v2.

- [Informe de desarrollo, PDF](main.pdf): una página A4 vertical, compilada desde [LaTeX](main.tex). Grafo completo, técnicas, resultados disponibles y limitaciones. Se revisó visualmente la página; sustituir la tabla provisional tras evaluar el lote.
- [Guion cronometrado](guion_video.md): ensayo de 2:50, con 10 segundos de margen. La conclusión final está condicionada a resultados que aún no existen.
- [Mensajes reales v2](mensajes_reales_v2.md): transcripciones de P05 y P41, con enlaces a los JSON originales y sus hashes. Incluyen el acierto y la regresión, así como errores de formato y paradas.
- [Matriz de requisitos](REQUISITOS.md): comprobación contra el enunciado oficial.

## Compilar y verificar

Desde la raíz del repositorio, con Tectonic instalado:

```bash
tectonic Deliverable3_Agentes/entrega/main.tex --outdir Deliverable3_Agentes/entrega
pdfinfo Deliverable3_Agentes/entrega/main.pdf
pdftoppm -png -singlefile -scale-to 1600 Deliverable3_Agentes/entrega/main.pdf /tmp/d3-informe
```

Comprobar `Pages: 1`, tamaño A4, orientación vertical y revisar la imagen. El editor LaTeX de Codex también compiló correctamente el proyecto. El PDF es un borrador explícitamente rotulado; la compilación no significa que los requisitos experimentales estén completos.

## Video

No hay archivo de video ni enlace público todavía. El guion y las trazas son materiales de preparación. La grabación final debe mostrar entradas reales, mensajes intermedios y respuesta final; conservar en el repositorio las trazas exactas que aparezcan en pantalla y explicar su reproducción en el README.
