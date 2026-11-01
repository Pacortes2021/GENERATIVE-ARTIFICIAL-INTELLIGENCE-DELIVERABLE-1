"""Crea una copia del cuaderno del D2 (sin modificar sus celdas) y agrega la sección 7:
el mismo sistema (baseline directo + RAG estructurado) sobre las 25 preguntas difíciles del D3."""
import csv, json, sys, copy
from pathlib import Path
origen, preguntas_csv, salida = map(Path, sys.argv[1:4])
nb = json.loads(origen.read_text(encoding="utf-8"))
filas = list(csv.DictReader(preguntas_csv.open(encoding="utf-8")))
assert len(filas) == 25 and [f["id"] for f in filas] == [f"H{i:02d}" for i in range(1, 26)]
# Solo id, texto y categoría (como el D2: las respuestas de referencia no se entregan al sistema).
preguntas = [{"id": 100 + int(f["id"][1:]), "codigo": f["id"], "pregunta": f["pregunta"], "categoria": f["categoria"]}
             for f in filas]

def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t}
def code(t): return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": t}

aviso = md(
"# Copia del cuaderno del D2 · sistema RAG del D2 sobre las 25 preguntas difíciles del D3\n\n"
"Las celdas de las secciones 1–6 son **idénticas** al cuaderno `Deliverable2_Sistema_RAG_Colab.ipynb` "
"(mismo Qwen3-4B, revisión, cuantización, buscador E5, prompt estructurado, decodificación y semilla base). "
"Solo se agrega la **sección 7** al final.\n\n"
"**Cómo usarlo:** GPU T4 → ejecuta las secciones 1, 2, 3 y 4 en orden → salta la 5 y la 6 → ejecuta la **sección 7**. "
"Corre las dos condiciones del D2 (prompting directo y RAG estructurado) sobre las 25 preguntas: 50 generaciones. "
"Al final descarga un ZIP; súbelo al chat.")
seccion7_md = md(
"## 7. Las 25 preguntas difíciles del D3 (mismo sistema del D2)\n\n"
"Cada pregunta H01–H25 recibe el identificador numérico 101–125 (el D2 usa el número para la semilla "
"`2026 + id` y para nombrar archivos). Solo se entregan id, texto y categoría. Antes de crear la corrida se "
"comprueba pregunta por pregunta que la evidencia y el prompt quepan en el presupuesto del D2; si alguna no cabe, "
"se excluye y queda informado (el D2 nunca recorta evidencia). Con `USAR_DRIVE=True` (valor del D2) los avances "
"quedan en tu Drive y la celda se puede volver a ejecutar para continuar.")
seccion7 = code(
"PREGUNTAS_DIFICILES = " + json.dumps(preguntas, ensure_ascii=False, indent=1) + "\n\n"
"from sistema import comparison_tasks\n"
"from experimento import atomic_json\n"
"CODIGO = {q['id']: q['codigo'] for q in PREGUNTAS_DIFICILES}\n"
"seleccion, excluidas = [], []\n"
"for q in PREGUNTAS_DIFICILES:\n"
"    try:\n"
"        caso, _ = retriever.retrieve(q['pregunta'], q['id'], q['categoria'])\n"
"        comparison_tasks([caso], tokenizer, SETTINGS['max_context_tokens'], SETTINGS['generacion']['max_new_tokens'])\n"
"        seleccion.append({k: q[k] for k in ('id', 'pregunta', 'categoria')})\n"
"    except ValueError as error:\n"
"        excluidas.append((q['codigo'], str(error)))\n"
"print('Preguntas que caben en el presupuesto del D2:', len(seleccion), 'de', len(PREGUNTAS_DIFICILES))\n"
"for codigo, motivo in excluidas:\n"
"    print('  EXCLUIDA', codigo, '->', motivo)\n"
"RUN_DIR, CONFIG, CASES, TASKS = prepare_run(seleccion, retriever, tokenizer, SETTINGS, OUTPUT_ROOT)\n"
"atomic_json(RUN_DIR / 'mapa_ids_D3.json', {'ids': CODIGO, 'excluidas': excluidas})\n"
"if not (RUN_DIR / 'preparacion.json').exists():\n"
"    atomic_json(RUN_DIR / 'preparacion.json', {'segundos_carga_e_indexacion_e5': INDEX_SECONDS,\n"
"                                               'segundos_carga_qwen': MODEL_SECONDS,\n"
"                                               'diagnostico_tokenizador_e5': E5_DIAGNOSTIC})\n"
"rows = run_tasks(RUN_DIR, CONFIG, CASES, TASKS, generate)\n"
"ZIP_PATH = export_run(RUN_DIR, CONFIG, TASKS)\n"
"print('Lote de 25 difíciles terminado:', ZIP_PATH)\n"
"try:\n"
"    from google.colab import files\n"
"    files.download(str(ZIP_PATH))\n"
"except Exception as e:\n"
"    print('Descarga el ZIP desde el panel de archivos o tu Drive:', ZIP_PATH, '|', e)\n")
celdas = nb["cells"]
assert "".join(celdas[13]["source"]).startswith("## 6.") and "".join(celdas[15]["source"]).startswith("## Alcance")
nb["cells"] = [aviso] + celdas[:15] + [seccion7_md, seccion7] + celdas[15:]
salida.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("escrito", salida, "| celdas:", len(nb["cells"]))
