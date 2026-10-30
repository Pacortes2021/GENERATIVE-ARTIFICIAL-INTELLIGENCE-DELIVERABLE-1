"""Crea el cuaderno de Colab específico para el lote de 25 preguntas difíciles."""
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

    # Bundle sources with the difficult questions
    sources = crear_cuaderno.bundle_sources()
    # Reemplazar data/preguntas.json con el conjunto difícil
    sources['data/preguntas.json'] = json.dumps(questions, ensure_ascii=False)
    
    # Empaquetar
    hashes = {n: hashlib.sha256(v.encode()).hexdigest() for n, v in sources.items()}
    raw = json.dumps(sources, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    packed = gzip.compress(raw, mtime=0)
    encoded = base64.b64encode(packed).decode()
    literal = '\n'.join('    ' + repr(s) for s in textwrap.wrap(encoded, 96))
    
    # Base notebook cells
    base_nb = json.loads((ROOT / 'Deliverable3_Agentes_Colab.ipynb').read_text())
    
    # Crear nuevo notebook
    target = ROOT / 'Deliverable3_Dificiles_25_Colab.ipynb'
    crear_cuaderno.build(target)
    
    # Reemplazar la celda 2 con el nuevo literal y EXPECTED
    nb = json.loads(target.read_text())
    expected = hashlib.sha256(packed).hexdigest()
    
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
    
    # Header cell
    nb['cells'][0]['source'] = textwrap.dedent('''
    # Deliverable 3 · 25 Preguntas Difíciles (H01–H25) · v4

    Conjunto complementario de 25 preguntas difíciles (IDs 101–125) preparadas por el equipo
    para contrastar razonamiento normativo avanzado, colisión léxica y cálculos ponderados.
    
    - 25 preguntas × 6 condiciones = 150 respuestas (o seleccionar variantes).
    - Inferencia emparejada con Qwen3-4B NF4 en T4 GPU.
    - No altera el lote de 50 preguntas ya completado y auditado.
    ''').strip().splitlines(keepends=True)
    
    # Cell 2 (restauración)
    for c in nb['cells']:
        if c.get('id') == 'd3-nuevo-02':
            c['source'] = textwrap.dedent(restore_code).strip().splitlines(keepends=True)
            
    # Cell 6 (ejecución del lote de 25)
    for c in nb['cells']:
        if c.get('id') == 'd3-nuevo-06':
            c['source'] = textwrap.dedent('''
            EJECUTAR_LOTE = True
            if EJECUTAR_LOTE:
                RUN_DIR = None
                print(f"Iniciando corrida de {len(ENV['questions'])} preguntas difíciles...")
                RUN_DIR = execute(ENV, ENV['questions'], OUTPUT, variants=VARIANTS,
                                  tag='lote-dificiles-25', verbose=False)
            else:
                print('Lote desactivado.')
            ''').strip().splitlines(keepends=True)

    target.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('Cuaderno de 25 preguntas difíciles creado con éxito:', target.name)
    print(f'Total bytes: {target.stat().st_size}')

if __name__ == '__main__':
    build_cuaderno_dificiles()
