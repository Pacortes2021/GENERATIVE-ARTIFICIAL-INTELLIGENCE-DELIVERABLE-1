"""Construye el sistema consultable sin cambiar los experimentos históricos."""
import ast
import base64
import csv
import gzip
import hashlib
import json
from pathlib import Path
import textwrap

import nbformat as nbf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REVISION = '1cfa9a7208912126459214e8b04321603b3df60c'


def portable_source():
    """Empaqueta las funciones originales literalmente; no duplica una implementación manual."""
    selected = [('probar_recuperacion.py', {'require', 'rank_vectors'}),
                ('recuperar_mejorado.py', {'POLICY', 'normal', 'subqueries', 'named_documents', 'exact_articles',
                                          'holiday_inventory', 'references', 'make_contexts'})]
    output = ['# Generado por crear_sistema.py a partir del recuperador evaluado. No editar a mano.',
              'import json\nimport re\nimport unicodedata\nimport numpy as np']
    for filename, names in selected:
        source = (ROOT / 'Deliverable2/recuperacion' / filename).read_text()
        found = set()
        for node in ast.parse(source).body:
            name = node.name if isinstance(node, ast.FunctionDef) else (node.targets[0].id if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) else None)
            if name in names:
                output.append(ast.get_source_segment(source, node))
                found.add(name)
        assert found == names
    return '\n\n'.join(output) + '\n'


def build():
    portable = portable_source()
    audit_cell = (HERE / 'auditar_lote_en_colab.py').read_text(encoding='utf-8')
    (HERE / 'recuperador_portable.py').write_text(portable)
    sources = {n: (HERE / n).read_text() for n in ['experimento.py', 'recuperador_portable.py', 'sistema.py']}
    data_dir = ROOT / 'Deliverable2/corpus/generado'
    for n in ['corpus.json', 'fragmentos_busqueda.json']:
        sources[n] = (data_dir / n).read_text()
    validation = json.loads((data_dir / 'validacion.json').read_text())
    for source in validation['fuentes'].values():
        assert hashlib.sha256((ROOT / 'Corpus' / source['archivo']).read_bytes()).hexdigest() == source['sha256'], 'PDF modificado: regenerar el corpus'
    for n in ['corpus.json', 'fragmentos_busqueda.json']:
        assert hashlib.sha256(sources[n].encode()).hexdigest() == validation['artefactos_sha256'][n]
    with (ROOT / 'Deliverable1/datos/test_set_50.csv').open(encoding='utf-8-sig', newline='') as f:
        questions = [{'id': i, 'pregunta': row['pregunta'], 'categoria': row['categoria']}
                     for i, row in enumerate(csv.DictReader(f), 1)]
    sources['preguntas.json'] = json.dumps(questions, ensure_ascii=False)
    hashes = {n: hashlib.sha256(s.encode()).hexdigest() for n, s in sources.items()}
    # Evitar literales de un megabyte en una sola línea en el editor de Colab.
    raw_bundle = json.dumps(sources, ensure_ascii=False, separators=(',', ':')).encode()
    packed_bundle = gzip.compress(raw_bundle, compresslevel=9, mtime=0)
    bundle_b64 = base64.b64encode(packed_bundle).decode('ascii')
    bundle_literal = '\n'.join('    ' + repr(part) for part in textwrap.wrap(bundle_b64, 96))
    cells = []
    def md(s): cells.append(nbf.v4.new_markdown_cell(textwrap.dedent(s).strip()))
    def code(s, hidden=False):
        c = nbf.v4.new_code_cell(textwrap.dedent(s).strip())
        if hidden: c.metadata = {'cellView': 'form', 'jupyter': {'source_hidden': True}}
        cells.append(c)
    md('''
    # Deliverable 2 · Sistema RAG consultable + baseline

    **Versión del cuaderno: carga-ligera-v1 + auditoría de corrida publicada.**

    **Escribe una pregunta nueva y compara Qwen3-4B sin documentos con RAG estructurado.**
    El sistema crea el índice E5 desde el corpus procesado, recupera para cada consulta y genera ambas respuestas.
    Las secciones de generación no reciben respuestas ideales, veredictos ni salidas precalculadas.
    La sección 7, que se ejecuta **después** de generar, audita el ZIP guardado y los juicios publicados.

    1. Sube este `.ipynb` a Colab y selecciona GPU. Ejecuta las secciones 1–4 para preparar el sistema.
    2. Escribe una pregunta en la sección 5 y ejecuta su celda; puedes repetirla con otra pregunta.
    3. Descarga el ZIP de la consulta. Conserva prompts, fragmentos, respuestas y configuración.
    4. Para medir las mismas 50 preguntas de E1, activa expresamente la sección 6. Genera 100 respuestas nuevas: baseline + RAG.
    5. Para mostrar los resultados de la corrida ya evaluada sin repetir el lote, ejecuta la sección 7. Verifica el ZIP,
       los 100 hashes de respuesta y los veredictos publicados antes de contar aciertos.

    **Si vienes de una versión anterior:** reinicia la sesión de Colab y ejecuta este archivo desde el principio.
    Esta versión fija el archivo del tokenizador E5, su hash y la versión de `tokenizers`; conserva los fragmentos.
    El corpus se incluye comprimido, en líneas cortas, para reducir la carga del editor de Colab.

    **Configuración elegida:** RAG estructurado. Se conserva su prompt evaluado y la política de recuperación;
    no se añaden reglas para preguntas específicas. El resultado previo de 80% no es un resultado de esta nueva ejecución.
    El 4% de E1 sigue siendo histórico. Este baseline conserva el prompt de E1, con los mismos parámetros de inferencia
    de la nueva solución (NF4, muestreo, sin thinking, 1.024 tokens), por lo que es otra corrida.

    El corpus fue extraído y validado previamente. Su texto completo, metadatos y fragmentos de búsqueda están incluidos;
    la indexación y la recuperación sí se ejecutan aquí. No se entregan los tres documentos completos a Qwen.
    ''')
    md('''
    ## 1. Preparar Colab

    La primera carga descarga los modelos y puede tardar varios minutos. Se mantiene el PyTorch/CUDA de Colab.
    E5 trabaja en CPU; Qwen ocupa la GPU. La consulta y el lote comparten el modelo cargado.
    ''')
    code('''
    import subprocess, sys, importlib.metadata
    PINNED = {'transformers': '4.57.6', 'accelerate': '1.11.0', 'bitsandbytes': '0.48.1',
              'sentence-transformers': '5.1.2', 'tokenizers': '0.22.2'}
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q',
        *[name + '==' + version for name, version in PINNED.items()]])
    stale = []
    for name, expected in PINNED.items():
        if importlib.metadata.version(name) != expected:
            raise RuntimeError('No se instaló la versión fijada de ' + name)
        loaded = sys.modules.get(name.replace('-', '_'))
        if loaded is not None and getattr(loaded, '__version__', None) != expected:
            stale.append(name)
    # Pip también puede actualizar dependencias indirectas; no mezclar binarios
    # nuevos en disco con módulos ya importados en la sesión anterior.
    for module, package in [('numpy', 'numpy'), ('scipy', 'scipy'), ('torch', 'torch'),
                            ('sklearn', 'scikit-learn'), ('huggingface_hub', 'huggingface-hub')]:
        loaded = sys.modules.get(module)
        if loaded is not None and hasattr(loaded, '__version__'):
            if loaded.__version__ != importlib.metadata.version(package):
                stale.append(package)
    if stale:
        raise RuntimeError('Colab conserva versiones anteriores en memoria: ' + ', '.join(stale) +
                           '. Reinicia la sesión y vuelve a ejecutar desde la primera celda.')
    print('Dependencias fijadas:', PINNED)
    ''')
    code(f'''
    MODEL_ID = 'Qwen/Qwen3-4B'
    MODEL_REVISION = '{REVISION}'
    E5_ID = '{validation['embedding']['modelo']}'
    E5_REVISION = '{validation['embedding']['revision']}'
    E5_TOKENIZER_SHA256 = '{validation['embedding']['tokenizer_sha256']}'
    USAR_DRIVE = True
    SEMILLA = 2026
    MAX_CONTEXT_TOKENS = 8192
    GENERACION = dict(do_sample=True, temperature=0.7, top_p=0.8, top_k=20, min_p=0.0,
                      repetition_penalty=1.0, max_new_tokens=1024)
    ''')
    md('''
    ## 2. Corpus y código incluidos

    Se comprueba la integridad del paquete antes de cargarlo. Los módulos son copias del código del repositorio.
    Los datos están comprimidos dentro del cuaderno; esta celda los restaura sin descargarlos ni cargar modelos.
    Mostrará tres pasos de avance y al terminar indicará «Corpus listo».
    La política de recuperación se empaqueta automáticamente desde las mismas funciones del experimento anterior:
    E5, subconsultas, artículos completos, remisiones de un salto e inventarios cuando corresponde.
    ''')
    code('import base64, gzip, hashlib, json, sys\nfrom pathlib import Path\n' +
         'BUNDLE_B64 = (\n' + bundle_literal + '\n)\n' +
         'PACKED_SHA256 = ' + repr(hashlib.sha256(packed_bundle).hexdigest()) + '\n' +
         'RAW_BUNDLE_BYTES = ' + str(len(raw_bundle)) + '\n' +
         'SOURCE_HASHES = ' + json.dumps(hashes, ensure_ascii=False, indent=4) + '''
print('[1/3] Restaurando el paquete incluido...', flush=True)
packed = base64.b64decode(BUNDLE_B64, validate=True)
if hashlib.sha256(packed).hexdigest() != PACKED_SHA256:
    raise ValueError('El paquete comprimido está alterado; vuelve a subir el cuaderno actualizado.')
raw_bundle = gzip.decompress(packed)
if len(raw_bundle) != RAW_BUNDLE_BYTES:
    raise ValueError('El paquete no tiene el tamaño original esperado.')
SOURCES = json.loads(raw_bundle)
if set(SOURCES) != set(SOURCE_HASHES):
    raise ValueError('Faltan archivos en el paquete incluido.')
print('[2/3] Verificando y guardando corpus y código...', flush=True)
for name, source in SOURCES.items():
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_HASHES[name]:
        raise ValueError('Paquete alterado: ' + name)
BUNDLE_HASH = hashlib.sha256(json.dumps(SOURCE_HASHES, sort_keys=True).encode()).hexdigest()
WORKDIR = Path.cwd() / ('genia_runtime_' + BUNDLE_HASH[:16])
WORKDIR.mkdir(exist_ok=True)
for name, source in SOURCES.items():
    (WORKDIR / name).write_text(source, encoding='utf-8')
print('[3/3] Leyendo datos; todavía no se cargan librerías de modelos...', flush=True)
CORPUS = json.loads(SOURCES['corpus.json'])
FRAGMENTS = json.loads(SOURCES['fragmentos_busqueda.json'])
QUESTIONS = json.loads(SOURCES['preguntas.json'])
del BUNDLE_B64, packed, raw_bundle, SOURCES
print('Corpus listo:', len(CORPUS['unidades']), 'unidades completas;', len(FRAGMENTS),
      'fragmentos para búsqueda;', len(QUESTIONS), 'preguntas.', flush=True)
''', hidden=True)
    md('''
    ## 3. Crear el índice y preparar el generador

    Los límites de E5 se comprueban sin truncar. Los artículos se expanden completos después de recuperar los fragmentos.
    Para cada consulta se comprueba el presupuesto de Qwen antes de generar ambas respuestas.
    ''')
    code('''
    import importlib.metadata, platform, time
    print('Importando funciones del sistema y NumPy...', flush=True)
    # Evitar mezclar módulos propios de distintas versiones en una sesión ya abierta.
    for module in ['experimento', 'recuperador_portable', 'sistema']:
        previous = sys.modules.get(module)
        if previous is not None and Path(previous.__file__).resolve().parent != WORKDIR.resolve():
            raise RuntimeError('Reinicia la sesión para cargar esta versión del sistema.')
    if str(WORKDIR.resolve()) not in sys.path:
        sys.path.insert(0, str(WORKDIR.resolve()))
    from sistema import LiveRetriever, QwenGenerator, configure_e5_tokenizer, prepare_run, run_tasks, export_run, show_comparison
    from experimento import digest
    print('Importando PyTorch, Transformers y SentenceTransformers...', flush=True)
    import torch
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM, BitsAndBytesConfig
    from huggingface_hub import hf_hub_download
    if not torch.cuda.is_available():
        raise RuntimeError('Selecciona un entorno de Colab con GPU y vuelve a ejecutar.')
    if USAR_DRIVE:
        from google.colab import drive
        drive.mount('/content/drive')
        OUTPUT_ROOT = Path('/content/drive/MyDrive/GenIA_Deliverable2/sistema_runs')
    else:
        OUTPUT_ROOT = Path.cwd() / 'sistema_runs'
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(4)
    torch.manual_seed(0)
    start_index = time.perf_counter()
    print('Cargando E5 en CPU...', flush=True)
    encoder = SentenceTransformer(E5_ID, revision=E5_REVISION, device='cpu')
    if encoder.max_seq_length != 512:
        raise ValueError('Configuración inesperada del modelo E5.')
    e5_tokenizer_path = hf_hub_download(E5_ID, 'tokenizer.json', revision=E5_REVISION)
    E5_DIAGNOSTIC_PATH = OUTPUT_ROOT / ('diagnostico_e5_' + BUNDLE_HASH[:16] + '.json')
    E5_DIAGNOSTIC = configure_e5_tokenizer(encoder, e5_tokenizer_path, FRAGMENTS,
                                          E5_TOKENIZER_SHA256, E5_DIAGNOSTIC_PATH)
    print('E5: archivo verificado; 201 fragmentos sin truncar; máximo', E5_DIAGNOSTIC['max_tokens'], 'tokens.')
    if E5_DIAGNOSTIC['diferencias_iniciales']:
        print('Se sustituyó el tokenizador cargado automáticamente por el archivo canónico del corpus.')
    print('Diagnóstico guardado en:', E5_DIAGNOSTIC_PATH)
    retriever = LiveRetriever(CORPUS, FRAGMENTS, encoder)
    INDEX_SECONDS = time.perf_counter() - start_index
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    model_config = AutoConfig.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    if MAX_CONTEXT_TOKENS > model_config.max_position_embeddings:
        raise ValueError('Presupuesto superior al soportado por Qwen.')
    print('Índice creado en', round(INDEX_SECONDS, 2), 's. GPU:', torch.cuda.get_device_name(0))
    ''')
    md('''
    ## 4. Cargar Qwen3-4B una sola vez

    Ambas condiciones usan los mismos pesos, precisión, parámetros y semilla por pregunta, sin historial compartido.
    La preparación y carga de modelos no se incluyen en el tiempo de consulta; quedan separadas en el archivo de preparación.
    ''')
    code('''
    COMPUTE_DTYPE = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                                      bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=COMPUTE_DTYPE)
    start_model = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REVISION,
        quantization_config=quantization, torch_dtype=COMPUTE_DTYPE,
        device_map={'': 0}, attn_implementation='sdpa')
    model.eval()
    MODEL_SECONDS = time.perf_counter() - start_model
    generate = QwenGenerator(model, tokenizer, GENERACION)
    SETTINGS = {'modelo': MODEL_ID, 'revision': MODEL_REVISION, 'thinking': False,
                'cuantizacion': {'bits': 4, 'tipo': 'nf4', 'double_quant': True, 'compute_dtype': str(COMPUTE_DTYPE)},
                'generacion': GENERACION, 'semilla_base': SEMILLA, 'semilla_por_pregunta': 'semilla_base + pregunta_id',
                'max_context_tokens': MAX_CONTEXT_TOKENS, 'margen_tokens': 64,
                'embedding': {'modelo': E5_ID, 'revision': E5_REVISION, 'device': 'cpu'},
                'tokenizador_e5': {'sha256': E5_DIAGNOSTIC['archivo_sha256'],
                                   'clase': E5_DIAGNOSTIC['clase_utilizada']},
                'versiones': {n: importlib.metadata.version(n) for n in
                             ['transformers', 'torch', 'accelerate', 'bitsandbytes', 'sentence-transformers', 'tokenizers', 'numpy']},
                'gpu': torch.cuda.get_device_name(0), 'cuda': torch.version.cuda,
                'python': platform.python_version(), 'atencion': 'sdpa',
                'archivos_paquete_sha256': SOURCE_HASHES, 'bundle_sha256': BUNDLE_HASH}
    print('Qwen listo. Configuración fijada; modo sin thinking.')
    ''')
    md('''
    ## 5. Consultar una pregunta nueva

    Escribe tu pregunta en `PREGUNTA` y ejecuta la celda. Se recuperan sus propios fragmentos desde el índice;
    no se reutiliza la evidencia de otra pregunta. La tabla muestra ambas respuestas y permite desplegar los fragmentos.
    Puedes cambiar la pregunta y ejecutar de nuevo esta misma celda.

    Se guarda cada respuesta inmediatamente. Si repites exactamente una consulta bajo la misma configuración,
    se recuperan sus checkpoints y se indica **checkpoint conservado**; no se presenta como generación nueva.
    Si una consulta excede los presupuestos, se detiene sin recortar textos ni ocultar la limitación.
    ''')
    code('''
    PREGUNTA = ""  # Escribe aquí una pregunta sobre la normativa del corpus.
    if PREGUNTA.strip():
        RUN_DIR, CONFIG, CASES, TASKS = prepare_run(
            [{'id': 1, 'pregunta': PREGUNTA, 'categoria': 'nueva'}], retriever, tokenizer, SETTINGS, OUTPUT_ROOT)
        from experimento import atomic_json
        if not (RUN_DIR / 'preparacion.json').exists():
            atomic_json(RUN_DIR / 'preparacion.json', {'segundos_carga_e_indexacion_e5': INDEX_SECONDS,
                                                       'segundos_carga_qwen': MODEL_SECONDS,
                                                       'diagnostico_tokenizador_e5': E5_DIAGNOSTIC})
        rows = run_tasks(RUN_DIR, CONFIG, CASES, TASKS, generate)
        show_comparison(rows, CASES)
        ZIP_PATH = export_run(RUN_DIR, CONFIG, TASKS)
        print('Consulta conservada en:', ZIP_PATH)
    else:
        print('Sistema listo. Escribe PREGUNTA y ejecuta esta celda para comparar baseline y RAG.')
    ''')
    code('''
    # Ejecuta esta celda después de la consulta o del lote para descargar sus resultados.
    if 'RUN_DIR' in globals():
        ZIP_PATH = export_run(RUN_DIR, CONFIG, TASKS)  # También rescata una corrida parcial.
        try:
            from google.colab import files
            files.download(str(ZIP_PATH))
        except ImportError:
            print('ZIP:', ZIP_PATH)
    else:
        print('Todavía no se ha creado una corrida.')
    ''')
    md('''
    ## 6. Comparación adicional sobre las 50 preguntas de E1 (opcional)

    Activa `EJECUTAR_LOTE_50 = True` para medir baseline y RAG bajo el mismo entorno: 100 respuestas.
    `IDS_LOTE = [1, 2]` permite un piloto; `None` incluye las 50. Cada pregunta recupera en vivo.
    El orden de las dos condiciones rota por pregunta, con la misma semilla para ambas.

    La evaluación de contenido y citas se realiza después, fuera del modelo, usando la misma pauta para ambos CSV.
    Esta celda **no calcula precisión**. El 4% histórico no se sobrescribe. Las 50 preguntas son de desarrollo,
    no una prueba independiente; la selección del estructurado ya utilizó sus resultados previos.
    ''')
    code('''
    EJECUTAR_LOTE_50 = False
    IDS_LOTE = None
    if EJECUTAR_LOTE_50:
        if IDS_LOTE is not None and (not IDS_LOTE or len(set(IDS_LOTE)) != len(IDS_LOTE) or
                                     not set(IDS_LOTE) <= {q['id'] for q in QUESTIONS}):
            raise ValueError('IDS_LOTE debe contener identificadores distintos entre 1 y 50.')
        selected = [q for q in QUESTIONS if IDS_LOTE is None or q['id'] in IDS_LOTE]
        RUN_DIR, CONFIG, CASES, TASKS = prepare_run(selected, retriever, tokenizer, SETTINGS, OUTPUT_ROOT)
        from experimento import atomic_json
        if not (RUN_DIR / 'preparacion.json').exists():
            atomic_json(RUN_DIR / 'preparacion.json', {'segundos_carga_e_indexacion_e5': INDEX_SECONDS,
                                                       'segundos_carga_qwen': MODEL_SECONDS,
                                                       'diagnostico_tokenizador_e5': E5_DIAGNOSTIC})
        rows = run_tasks(RUN_DIR, CONFIG, CASES, TASKS, generate)
        ZIP_PATH = export_run(RUN_DIR, CONFIG, TASKS)
        print('Lote terminado:', ZIP_PATH)
        print('Vuelve a la celda de descarga para obtener el ZIP. La evaluación semántica está pendiente.')
    else:
        print('Lote desactivado. Las consultas individuales no lanzan las 50 preguntas.')
    ''')
    md('''
    ## 7. Auditar la corrida evaluada sin volver a generar

    Esta celda **no ejecuta E5 ni Qwen**. Busca el ZIP exacto de 100 respuestas de la corrida emparejada
    ya evaluada en `ZIP_LOTE`, `OUTPUT_ROOT`, Drive y el almacenamiento temporal de Colab. Si no está,
    descarga la copia publicada desde un commit fijo y muestra su origen; no requiere montar Drive.
    Obtiene también los paquetes y veredictos publicados desde ese commit. Verifica sus hashes, los
    prompts, la evidencia y la correspondencia entre cada respuesta y su juicio antes de contar 1/50 y 40/50.
    Muestra los diez fallos RAG y permite cambiar `ID_CASO` para inspeccionar cualquiera de las 50 preguntas.
    Para P25 también muestra los artículos 7 y 9 que estaban íntegros en el prompt realmente enviado.

    **Alcance:** los aciertos son recuentos de veredictos asistidos ya registrados, no una evaluación semántica
    automática nueva. El evaluador y sus motivos son visibles en los archivos publicados. Si un ZIP local fue
    reexportado después, usa el ZIP original descargado para esta corrida; la celda se detiene ante un hash distinto
    sin reemplazar ese archivo. La copia pública se guarda por separado en `/content/auditoria_publicada/`.
    ''')
    code(audit_cell)
    md('''
    ## Alcance y reproducción

    - Sistema elegido: RAG estructurado, sin few-shot; no se entrenan pesos ni se corrigen preguntas a mano.
    - El baseline recibe únicamente el prompt directo original de E1 y la pregunta. Las referencias del evaluador no están en este notebook.
    - El baseline conserva la instrucción histórica de decir que la información no está en la normativa si no la conoce; esa instrucción también tiene límites. La comparación mide el sistema completo, no aísla únicamente el efecto del retrieval.
    - P25 falló en el estructurado anterior aunque los artículos 7 y 9 estaban completos en su prompt: no desarrolló la remisión. No fue un corte. P38 mantiene una limitación conocida de recuperación.
    - Corpus procesado: tres PDF del proyecto. Solo los fragmentos seleccionados y los inventarios pertinentes llegan a Qwen.
    - Los tiempos de consulta suman búsqueda y generación en RAG; el índice y la carga de pesos se registran aparte.
    - Reproducción en el repositorio: `python3 Deliverable2/notebooks/crear_sistema.py` genera este cuaderno.
    - La sección 7 audita una corrida emparejada ya evaluada. Ejecutar otra vez la sección 6 produce respuestas y ZIP propios, que requieren juicios nuevos antes de calcular precisión; no se hereda automáticamente el 80%.
    ''')
    nb = nbf.v4.new_notebook(cells=cells, metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python'}, 'colab': {'name': 'Deliverable2_Sistema_RAG_Colab.ipynb'}, 'accelerator': 'GPU'})
    for i, c in enumerate(nb.cells):
        c['id'] = f'sistema-{i:02}'
        if c.cell_type == 'code': compile(c.source, f'cell-{i}', 'exec')
    nbf.validate(nb)
    out = HERE / 'Deliverable2_Sistema_RAG_Colab.ipynb'
    nbf.write(nb, out)
    print(out, '|', len(cells), 'celdas |', out.stat().st_size, 'bytes')
    return nb


if __name__ == '__main__':
    build()
