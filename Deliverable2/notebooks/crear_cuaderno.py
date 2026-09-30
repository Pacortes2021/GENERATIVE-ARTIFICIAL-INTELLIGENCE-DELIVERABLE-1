"""Construye un ipynb autocontenido; no incluye respuestas de referencia."""
import hashlib
import json
from pathlib import Path
import textwrap

import nbformat as nbf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / 'Deliverable2/recuperacion/resultados/e5_estructurado_v2/recuperacion.json'
REVISION = '1cfa9a7208912126459214e8b04321603b3df60c'


def build():
    raw = json.loads(RUN.read_text())
    payload = {'version': 1, 'recuperacion_sha256': hashlib.sha256(RUN.read_bytes()).hexdigest(),
               'configuracion_recuperacion': raw['configuracion'], 'fuentes_sha256': raw['fuentes_sha256'],
               'casos': [{k: c[k] for k in ('id', 'pregunta', 'categoria', 'contextos', 'contextos_inventario', 'omitidos_por_presupuesto')} for c in raw['casos']]}
    payload_json = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    payload_sha = hashlib.sha256(payload_json.encode()).hexdigest()
    cells = []
    def md(value): cells.append(nbf.v4.new_markdown_cell(textwrap.dedent(value).strip()))
    def code(value, hidden=False):
        cell = nbf.v4.new_code_cell(textwrap.dedent(value).strip())
        if hidden: cell['metadata'] = {'cellView': 'form', 'jupyter': {'source_hidden': True}}
        cells.append(cell)
    md('''
    # Deliverable 2 · Qwen3-4B · Dos variantes de RAG

    **Cuaderno listo para subir a Google Colab.** Incluye las 50 preguntas y los contextos recuperados de la corrida `e5_estructurado_v2`. No requiere clonar el repositorio, subir PDF ni configurar una API.

    1. En Colab selecciona **Entorno de ejecución → Cambiar tipo de entorno de ejecución → GPU** (T4 o superior).
    2. Ejecuta las celdas en orden. Si está activado, autoriza montar tu Drive para guardar el avance.
    3. Se comprueban los tokens antes de descargar los pesos y se generan **100 respuestas: 50 × 2 variantes**.
    4. Descarga el ZIP al final. Contiene CSV por variante, respuestas completas, prompts, evidencia y metadatos para evaluar después.

    | Variante | Qué recibe |
    |---|---|
    | `rag_simple` | Evidencia + pregunta + instrucción breve |
    | `rag_estructurado` | Misma evidencia + instrucciones de completitud, excepciones, citas y abstención |

    **Se comparan prompts, sin entrenamiento de pesos.** No se entregan respuestas de referencia ni veredictos a Qwen. Se retiró few-shot de la comparación principal tras revisar la primera corrida. Las respuestas de simple y estructurado ya obtenidas siguen siendo válidas: no es necesario volver a ejecutarlas solo por retirar esa variante.

    La recuperación ya está calculada y congelada: este cuaderno ejecuta la fase de generación del RAG sobre esa evidencia, sin volver a seleccionar documentos. Todos los datos necesarios están dentro del ipynb, cuya celda de datos puede mantenerse contraída.
    ''')
    md('''
    ## 1. Dependencias

    Se fijan versiones de Transformers, Accelerate y bitsandbytes. Se conserva PyTorch/CUDA del entorno de Colab y se registran sus versiones. No hace falta una clave de Hugging Face para el modelo público. Se descargarán sus pesos (varios GB) la primera vez.

    Si ya habías importado otra versión de Transformers en este entorno, reinicia la sesión después de instalar y vuelve a ejecutar las celdas.
    ''')
    code('''
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q',
                           'transformers==4.57.6', 'accelerate==1.11.0', 'bitsandbytes==0.48.1'])
    ''')
    md('''
    ## 2. Configuración compartida

    Para la corrida completa deja `IDS_PREGUNTAS = None`. Para comprobar primero que tu entorno funciona, puedes usar `[1, 2]`; ese piloto se guardará como una corrida distinta.

    Se usa cuantización NF4 de 4 bits para reducir memoria, modo sin thinking, muestreo con los parámetros recomendados por Qwen para ese modo y una semilla fijada por pregunta. Las dos variantes comparten estos ajustes. Una sola semilla no mide variabilidad: futuras repeticiones deben registrarse como corridas separadas.

    `USAR_DRIVE=True` conserva checkpoints tras una desconexión. Con `False`, los resultados quedan en el almacenamiento temporal de Colab y debes descargar el ZIP antes de cerrar la sesión. No se cambia automáticamente de precisión ni se recortan entradas si falta memoria.
    ''')
    code(f'''
    MODEL_ID = 'Qwen/Qwen3-4B'
    MODEL_REVISION = '{REVISION}'
    IDS_PREGUNTAS = None
    USAR_DRIVE = True
    SEMILLA = 2026
    MAX_CONTEXT_TOKENS = 8192
    MAX_NEW_TOKENS = 1024
    ENABLE_THINKING = False
    GENERACION = dict(do_sample=True, temperature=0.7, top_p=0.8, top_k=20, min_p=0.0,
                      repetition_penalty=1.0, max_new_tokens=MAX_NEW_TOKENS)
    ''')
    code('''
    import os, platform, time, csv, shutil, importlib.metadata
    from datetime import datetime, timezone
    from pathlib import Path
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError('Activa una GPU en Entorno de ejecución → Cambiar tipo de entorno de ejecución y reconecta.')
    from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM, BitsAndBytesConfig, set_seed
    COMPUTE_DTYPE = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    if USAR_DRIVE:
        from google.colab import drive
        drive.mount('/content/drive')
        OUTPUT_ROOT = Path('/content/drive/MyDrive/GenIA_Deliverable2/runs')
    else:
        OUTPUT_ROOT = Path.cwd() / 'runs'
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    print('GPU:', torch.cuda.get_device_name(0))
    print('Memoria total GB:', round(torch.cuda.get_device_properties(0).total_memory / 2**30, 2))
    print('Cómputo:', COMPUTE_DTYPE, '| Resultados:', OUTPUT_ROOT)
    ''')
    md('''
    ## 3. Datos fijados y funciones

    Los textos corresponden a los PDF del proyecto; cada contexto conserva ID, cita y hash de su PDF. Los inventarios son metadatos calculados a partir del corpus completo y se identifican como tales. **No son instrucciones ni respuestas de referencia.**

    Limitaciones conocidas: falta una fuente adicional de la pauta en P34 y falta el artículo de aplicación de la norma en P38. Se mantienen esos casos para observar qué responde el modelo con la evidencia realmente recuperada. No se insertan manualmente fuentes desde el evaluador.
    ''')
    code('#@title Datos de evaluación y evidencia congelada (incluidos en este archivo)\nimport json, hashlib\nPAYLOAD_JSON = ' + repr(payload_json) + '\nassert hashlib.sha256(PAYLOAD_JSON.encode()).hexdigest() == ' + repr(payload_sha) + '\nPAYLOAD = json.loads(PAYLOAD_JSON)\nprint("Preguntas incluidas:", len(PAYLOAD["casos"]))', hidden=True)
    code(HERE.joinpath('experimento.py').read_text(), hidden=True)
    code('''
    ALL_CASES = PAYLOAD['casos']
    assert len(ALL_CASES) == 50 and len({c['id'] for c in ALL_CASES}) == 50
    if IDS_PREGUNTAS is not None:
        assert IDS_PREGUNTAS and len(set(IDS_PREGUNTAS)) == len(IDS_PREGUNTAS)
        assert set(IDS_PREGUNTAS) <= {c['id'] for c in ALL_CASES}
    CASES = [c for c in ALL_CASES if IDS_PREGUNTAS is None or c['id'] in IDS_PREGUNTAS]
    assert not any(c['omitidos_por_presupuesto'] for c in CASES), 'Hay evidencia omitida: revisar antes de generar.'
    for case in CASES:
        assert len({messages(case, v)[-1]['content'] for v in VARIANTES}) == 1
    print(f'{len(CASES)} preguntas, {len(VARIANTES)} variantes, {len(CASES) * len(VARIANTES)} respuestas esperadas.')
    ''')
    md('''
    ## 4. Medir tokens reales y congelar los prompts

    Se aplica la plantilla de conversación de **Qwen3-4B con `enable_thinking=False`**. La longitud cuenta el prompt completo y la evidencia. Se reservan 1.024 tokens de salida y 64 de margen. Si alguna entrada no cabe, la ejecución se detiene: no trunca artículos ni reduce evidencia solo para una variante.
    ''')
    code('''
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    model_config = AutoConfig.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    assert MAX_CONTEXT_TOKENS <= model_config.max_position_embeddings
    assert ENABLE_THINKING is False, 'Esta comparación está fijada en modo sin thinking.'
    TASKS = make_tasks(CASES, tokenizer, MAX_CONTEXT_TOKENS, MAX_NEW_TOKENS)
    for variant in VARIANTES:
        counts = [t['tokens_entrada'] for t in TASKS if t['variante'] == variant]
        print(variant, '| tokens entrada: media', round(sum(counts)/len(counts)), '| máximo', max(counts))
    print('Todas las entradas caben sin recortar. Máximo entrada + salida + margen:',
          max(t['tokens_entrada'] for t in TASKS) + MAX_NEW_TOKENS + 64)
    ''')
    code('''
    VERSIONS = {name: importlib.metadata.version(name) for name in
                ('transformers', 'torch', 'accelerate', 'bitsandbytes', 'tokenizers', 'huggingface-hub')}
    CONFIG = {'modelo': MODEL_ID, 'revision': MODEL_REVISION, 'thinking': ENABLE_THINKING,
              'cuantizacion': {'bits': 4, 'tipo': 'nf4', 'double_quant': True, 'compute_dtype': str(COMPUTE_DTYPE)},
              'generacion': GENERACION, 'semilla_base': SEMILLA, 'semilla_por_pregunta': 'semilla_base + pregunta_id',
              'max_context_tokens': MAX_CONTEXT_TOKENS, 'margen_tokens': 64,
              'casos': [c['id'] for c in CASES], 'payload_sha256': digest(PAYLOAD),
              'prompts_sha256': digest(TASKS), 'versiones': VERSIONS,
              'gpu': torch.cuda.get_device_name(0), 'cuda': torch.version.cuda, 'python': platform.python_version(),
              'atencion': 'sdpa', 'orden': 'variantes rotan por pregunta',
              'protocolo': 'colab-dos-variantes-v1'}
    RUN_HASH = digest(CONFIG)
    RUN_DIR = OUTPUT_ROOT / ('qwen3_4b_' + RUN_HASH[:16])
    RUN_DIR.mkdir(exist_ok=True)
    if (RUN_DIR / 'configuracion.json').exists():
        assert json.loads((RUN_DIR / 'configuracion.json').read_text()) == CONFIG, 'Corrida incompatible.'
    atomic_json(RUN_DIR / 'configuracion.json', CONFIG)
    atomic_json(RUN_DIR / 'evidencia.json', {'origen': PAYLOAD, 'casos_seleccionados': CONFIG['casos']})
    atomic_json(RUN_DIR / 'prompts.json', TASKS)
    print('Carpeta de esta corrida:', RUN_DIR)
    print('Si vuelves a ejecutar con la misma configuración y entorno, se reutilizan únicamente los checkpoints compatibles.')
    ''')
    md('''
    ## 5. Cargar Qwen3-4B una sola vez

    El modelo permanece en GPU para las dos variantes. Si ocurre un error de memoria, el proceso se detiene; no cambia silenciosamente el modelo, el contexto ni la cuantización. No se descarga ningún modelo de 8B.
    ''')
    code('''
    quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                                      bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=COMPUTE_DTYPE)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, quantization_config=quantization,
        torch_dtype=COMPUTE_DTYPE, device_map={'': 0}, attn_implementation='sdpa')
    model.eval()
    EOS_IDS = model.generation_config.eos_token_id
    if EOS_IDS is None:
        EOS_IDS = tokenizer.eos_token_id
    if EOS_IDS is None:
        raise RuntimeError('No se encontró el token de finalización del modelo.')
    print('Modelo cargado; memoria de pesos GB:', round(model.get_memory_footprint() / 2**30, 2))
    ''')
    md('''
    ## 6. Generar y guardar después de cada respuesta

    Cada respuesta conserva su texto completo, tokens generados, motivo de parada, tiempo, memoria y hashes del prompt y evidencia. **Alcanzar el límite de tokens queda marcado como posible corte**, no se considera una respuesta terminada con normalidad.

    El orden de las variantes rota entre preguntas. Se reinicia la misma semilla por pregunta en cada variante, sin historial compartido entre preguntas. Si una celda falla, los checkpoints anteriores permanecen; al reejecutarla se omiten los ya terminados. Una salida cortada se conserva: ampliar el límite crea otra corrida, sin sobrescribirla.
    ''')
    code('''
    TASK_MAP = {(t['pregunta_id'], t['variante']): t for t in TASKS}
    RESULTS_DIR = RUN_DIR / 'respuestas'
    RESULTS_DIR.mkdir(exist_ok=True)
    def generate_one(task):
        seed = SEMILLA + task['pregunta_id']
        set_seed(seed)
        inputs = tokenizer(task['prompt'], return_tensors='pt', add_special_tokens=False, truncation=False).to('cuda:0')
        assert inputs['input_ids'].shape[1] == task['tokens_entrada']
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        start = time.perf_counter()
        with torch.inference_mode():
            output = model.generate(**inputs, **GENERACION, eos_token_id=EOS_IDS,
                                    pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id,
                                    use_cache=True)
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        token_ids = output[0, inputs['input_ids'].shape[1]:].detach().cpu().tolist()
        answer = tokenizer.decode(token_ids, skip_special_tokens=True).strip()
        reason = stop_reason(token_ids, EOS_IDS, MAX_NEW_TOKENS)
        row = {k: task[k] for k in ('pregunta_id', 'pregunta', 'categoria', 'variante', 'tokens_entrada', 'prompt_sha256', 'evidencia_sha256')}
        row.update(run_hash=RUN_HASH, respuesta_modelo=answer, respuesta_sha256=digest(answer),
                   salida_con_tokens_especiales=tokenizer.decode(token_ids, skip_special_tokens=False),
                   ids_tokens_salida=token_ids, tokens_salida=len(token_ids), motivo_parada=reason,
                   posible_corte=reason == 'limite_tokens', thinking_inesperado='<think>' in answer,
                   segundos=round(elapsed, 4), pico_memoria_gpu_gb=round(torch.cuda.max_memory_allocated()/2**30, 4),
                   semilla=seed, fecha_utc=datetime.now(timezone.utc).isoformat())
        return row

    completed = 0
    for index, case in enumerate(CASES):
        offset = index % len(VARIANTES)
        order = VARIANTES[offset:] + VARIANTES[:offset]
        for variant in order:
            task = TASK_MAP[(case['id'], variant)]
            checkpoint = RESULTS_DIR / f"P{case['id']:02}_{variant}.json"
            row = load_checkpoint(checkpoint, RUN_HASH, task)
            if row is None:
                try:
                    row = generate_one(task)
                    atomic_json(checkpoint, row)
                except Exception as exc:
                    atomic_json(RUN_DIR / 'ultimo_error.json', {'pregunta_id': case['id'], 'variante': variant,
                                'tipo': type(exc).__name__, 'detalle': str(exc), 'fecha_utc': datetime.now(timezone.utc).isoformat()})
                    raise
            completed += 1
            print(f"{completed}/{len(TASKS)} | P{case['id']:02} | {variant} | {row['tokens_salida']} tokens | {row['motivo_parada']}", flush=True)
    print('Generación completa. Ejecuta la exportación para descargar los resultados.')
    ''')
    md('''
    ## 7. Exportar resultados (también funciona con una corrida parcial)

    Cada CSV incluye `pregunta` y `respuesta_modelo`, compatibles con nuestro evaluador. El reporte técnico muestra tiempos y posibles cortes; **no asigna corrección semántica**. Para obtener porcentajes de respuestas correctas evaluaremos los CSV después contra la pauta separada.

    El ZIP incluye evidencias, prompts y configuración. Si hubo una interrupción puedes ejecutar esta celda para rescatar lo ya producido. Un ZIP parcial está marcado explícitamente como tal.
    ''')
    code('''
    rows = []
    for task in TASKS:
        path = RESULTS_DIR / f"P{task['pregunta_id']:02}_{task['variante']}.json"
        row = load_checkpoint(path, RUN_HASH, task)
        if row is not None:
            rows.append(row)
    fields = ['pregunta_id', 'pregunta', 'categoria', 'variante', 'respuesta_modelo', 'tokens_entrada',
              'tokens_salida', 'motivo_parada', 'posible_corte', 'thinking_inesperado', 'segundos',
              'pico_memoria_gpu_gb', 'semilla', 'prompt_sha256', 'evidencia_sha256', 'respuesta_sha256', 'run_hash']
    for variant in VARIANTES:
        with (RUN_DIR / f'{variant}.csv').open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(r for r in rows if r['variante'] == variant)
    summary = {'respuestas_esperadas': len(TASKS), 'respuestas_guardadas': len(rows),
               'corrida_completa': len(rows) == len(TASKS), 'no_es_evaluacion_semantica': True, 'variantes': {}}
    for variant in VARIANTES:
        group = [r for r in rows if r['variante'] == variant]
        summary['variantes'][variant] = {'respuestas': len(group), 'posibles_cortes': sum(r['posible_corte'] for r in group),
              'segundos_totales': round(sum(r['segundos'] for r in group), 2),
              'tokens_entrada_totales': sum(r['tokens_entrada'] for r in group),
              'tokens_salida_totales': sum(r['tokens_salida'] for r in group)}
    atomic_json(RUN_DIR / 'resumen_tecnico.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    ZIP_PATH = shutil.make_archive(str(RUN_DIR), 'zip', root_dir=RUN_DIR)
    print('ZIP guardado:', ZIP_PATH)
    try:
        from google.colab import files
        files.download(ZIP_PATH)
    except ImportError:
        print('Fuera de Colab: descarga el ZIP desde la ruta mostrada.')
    ''')
    md('''
    ## Interpretar el experimento y preparar preguntas nuevas

    - Los dos prompts usan la misma evidencia de la consulta, modelo, cuantización y parámetros. Cambian únicamente las instrucciones. El experimento previo con tres variantes se conserva en su cuaderno y ZIP originales.
    - La pauta de respuestas está separada y no participa en generación. El cuaderno no calcula una supuesta precisión mediante coincidencias de palabras.
    - Las 50 preguntas ya se usaron para diagnosticar el recuperador; son un conjunto de desarrollo conocido. No deben presentarse como una prueba independiente de generalización. Guarda nuevas preguntas sin mirar sus resultados mientras ajustas el sistema y evalúalas solo después de fijar la configuración.
    - La inferencia con 4 bits y los ajustes de esta corrida pueden diferir del baseline histórico. Su 4% se conserva como antecedente; una comparación causal estricta exige correr también un baseline sin corpus bajo este mismo protocolo y evaluador.
    - Para preguntas nuevas, primero genera evidencia con el recuperador congelado y un archivo nuevo de consultas; después reutiliza estos mismos dos prompts. Este cuaderno contiene exclusivamente los 50 contextos fijados y no permite inventar preguntas reutilizando evidencia de otra.
    - Semillas iguales no garantizan identidad entre distintas GPU, versiones o formas de cómputo. Se registran esos datos y se conserva cada respuesta.

    Fuentes técnicas: [Qwen3-4B: thinking y parámetros de inferencia](https://huggingface.co/Qwen/Qwen3-4B), [Transformers: cuantización con bitsandbytes](https://huggingface.co/docs/transformers/v4.57.1/quantization/bitsandbytes).
    ''')
    # El cuaderno histórico de tres variantes se conserva como archivo independiente.
    md('''
    ## 8. Inspección opcional recuperada del cuaderno anterior

    Esta sección no genera respuestas ni altera prompts, configuración o checkpoints.
    Recupera dos ideas útiles del trabajo anterior: analizar por categoría y mirar cada
    respuesta junto a la evidencia exacta enviada al modelo. Los tiempos corresponden a
    generación: la recuperación fue calculada antes de esta corrida.

    Las alertas de citas son mecánicas y no asignan aciertos. Una cita con un ID válido
    puede no respaldar lo afirmado; una cita en formato libre puede ser correcta.
    ''')
    code(HERE.joinpath('diagnostico.py').read_text(), hidden=True)
    code('''
    if 'rows' not in globals():
        raise RuntimeError('Ejecuta primero la celda de exportación para leer los checkpoints.')
    print('RESUMEN TÉCNICO POR CATEGORÍA (no es precisión):')
    print(json.dumps(diagnostic_summary(rows), ensure_ascii=False, indent=2))
    ID_INSPECCION = 25  # Cambia el número para revisar otra pregunta.
    show_case(ID_INSPECCION, rows, ALL_CASES)
    ''')
    nb = nbf.v4.new_notebook(cells=cells, metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                            'language_info': {'name': 'python'}, 'colab': {'name': 'Deliverable2_RAG_2_variantes_Colab.ipynb'}, 'accelerator': 'GPU'})
    for i, cell in enumerate(nb.cells):
        cell['id'] = f'cell-{i:02}'
        if cell.cell_type == 'code': compile(cell.source, f'cell-{i}', 'exec')
    nbf.validate(nb)
    out = HERE / 'Deliverable2_RAG_2_variantes_Colab.ipynb'
    nbf.write(nb, out)
    print(out, '|', len(cells), 'celdas |', out.stat().st_size, 'bytes')
    return nb


if __name__ == '__main__':
    build()
