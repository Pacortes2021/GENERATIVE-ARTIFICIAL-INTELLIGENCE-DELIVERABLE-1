"""Crea el cuaderno de Colab específico para el lote de 25 preguntas difíciles en 5 bloques."""
import base64
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import crear_cuaderno

def build_cuaderno_dificiles():
    preguntas_path = ROOT / 'conjunto_dificil_25/paquete_dificiles_Pablo/preguntas.json'
    questions = json.loads(preguntas_path.read_text(encoding='utf-8'))
    print(f'Cargando {len(questions)} preguntas difíciles (H01-H25, IDs 101-125)...')

    sources = crear_cuaderno.bundle_sources()
    sources['data/preguntas.json'] = json.dumps(questions, ensure_ascii=False)
    
    hashes = {n: hashlib.sha256(v.encode()).hexdigest() for n, v in sources.items()}
    raw = json.dumps(sources, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    packed = gzip.compress(raw, mtime=0)
    encoded = base64.b64encode(packed).decode()
    literal = '\n'.join('    ' + repr(s) for s in textwrap.wrap(encoded, 96))
    expected = hashlib.sha256(packed).hexdigest()
    
    cells = []
    def md(text, ident):
        cells.append({'cell_type': 'markdown', 'metadata': {'id': ident}, 'source': textwrap.dedent(text).strip().splitlines(keepends=True)})
    def code(text, ident):
        source = textwrap.dedent(text).strip()
        cells.append({'cell_type': 'code', 'metadata': {'id': ident}, 'source': source.splitlines(keepends=True),
                      'execution_count': None, 'outputs': []})
    
    md('''
    # Deliverable 3 · 25 Preguntas Difíciles en 5 Bloques (150 respuestas)

    Conjunto complementario de 25 preguntas difíciles (IDs 101–125) preparadas por el equipo
    para contrastar razonamiento normativo avanzado, colisión léxica y cálculos ponderados.
    
    - 25 preguntas × 6 condiciones = **150 respuestas**.
    - Ejecutado en **5 bloques de 30 respuestas** (5 preguntas × 6 condiciones por bloque).
    - Cada bloque o cada 6 respuestas genera un snapshot inmutable para no perder avance.
    - No altera el lote de 50 preguntas ya completado y auditado.
    ''', 'dificiles-intro')
    
    md('## 1. Instalar dependencias fijadas', 'dificiles-dep-md')
    code('''
    import sys, subprocess, importlib.metadata
    PINNED = {'transformers':'4.57.6', 'accelerate':'1.11.0', 'bitsandbytes':'0.48.1',
              'sentence-transformers':'5.1.2', 'tokenizers':'0.22.2'}
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q',
                          *[p+'=='+v for p,v in PINNED.items()]])
    for module, package in [(p.replace('-', '_'), p) for p in PINNED] + [
        ('numpy','numpy'), ('scipy','scipy'), ('torch','torch'), ('sklearn','scikit-learn'),
        ('huggingface_hub','huggingface-hub')]:
        loaded = sys.modules.get(module)
        if loaded is not None and hasattr(loaded, '__version__'):
            if loaded.__version__ != importlib.metadata.version(package):
                raise RuntimeError('Reinicia la sesión: versión anterior en memoria de ' + package)
    print('Dependencias instaladas. No se cargó ningún modelo todavía.')
    ''', 'dificiles-dep-code')
    
    md('## 2. Restaurar código, prompts y las 25 preguntas difíciles', 'dificiles-restore-md')
    restore_code = ('BUNDLE_B64 = (\n' + literal + '\n)\n' +
         'EXPECTED = ' + repr(expected) + '\n' +
         'FILE_HASHES = ' + repr(hashes) + '\n' + '''
import base64, gzip, hashlib, json, sys
from pathlib import Path
packed = base64.b64decode(BUNDLE_B64, validate=True)
if hashlib.sha256(packed).hexdigest() != EXPECTED:
    raise ValueError('Paquete alterado.')
sources = json.loads(gzip.decompress(packed))
if set(sources) != set(FILE_HASHES):
    raise ValueError('Inventario del paquete incorrecto.')
WORKDIR = Path.cwd() / ('d3_dificiles_runtime_' + EXPECTED[:16])
for name, text in sources.items():
    path = Path(name)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Ruta no permitida.')
    if hashlib.sha256(text.encode()).hexdigest() != FILE_HASHES[name]:
        raise ValueError('Fuente alterada: ' + name)
    target = WORKDIR / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')
previous = sys.modules.get('d3_agentes')
if previous is not None and Path(previous.__file__).resolve().parent != (WORKDIR / 'd3_agentes').resolve():
    raise RuntimeError('Reinicia la sesión para cargar esta versión de D3.')
sys.path.insert(0, str(WORKDIR.resolve())) if str(WORKDIR.resolve()) not in sys.path else None
print('Fuentes restauradas en:', WORKDIR.name)
''')
    code(restore_code, 'dificiles-restore-code')
    
    md('## 3. Cargar modelos e inicializar runtime', 'dificiles-runtime-md')
    code('''
    import sys
    from pathlib import Path
    import torch
    from d3_agentes.runtime import load_runtime
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print('Dispositivo de cómputo:', device)
    if device != 'cuda':
        print('AVISO: Se requiere acelerador GPU (T4) para ejecutar la inferencia de 25 preguntas.')
    
    WORKDIR = next(Path.cwd().glob('d3_dificiles_runtime_*'))
    ENV = load_runtime(WORKDIR, device=device)
    OUTPUT = Path('/content/d3_dificiles_runs')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    print('Runtime listo. Preguntas difíciles cargadas:', len(ENV['questions']))
    ''', 'dificiles-runtime-code')
    
    md('## 4. Ejecutar por bloques de 30 respuestas (5 bloques de 30 = 150 respuestas)', 'dificiles-run-md')
    runner_code = (ROOT / 'operacion/ejecutar_lote_dificiles_colab.py').read_text()
    code(runner_code, 'dificiles-run-code')
    
    md('## 5. Descargar o recuperar respaldos', 'dificiles-download-md')
    code('''
    from d3_agentes.downloads import prepare_download
    ZIP = prepare_download(OUTPUT, None)
    if ZIP is not None:
        print('ZIP listo para descargar:', ZIP.resolve(), '| bytes:', ZIP.stat().st_size)
        try:
            from google.colab import files
            files.download(str(ZIP))
        except Exception as exc:
            print('Descarga automática no iniciada. Descarga manualmente desde el panel Archivos.')
    ''', 'dificiles-download-code')
    
    nb = {'nbformat': 4, 'nbformat_minor': 5, 'metadata': {
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python'},
        'colab': {'name': 'Deliverable3_Dificiles_Bloques_Colab.ipynb'},
        'accelerator': 'GPU'}, 'cells': cells}
    
    target = ROOT / 'Deliverable3_Dificiles_Bloques_Colab.ipynb'
    target.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('Cuaderno de bloques creado con éxito:', target.name)
    print(f'Total bytes: {target.stat().st_size}')

if __name__ == '__main__':
    build_cuaderno_dificiles()
