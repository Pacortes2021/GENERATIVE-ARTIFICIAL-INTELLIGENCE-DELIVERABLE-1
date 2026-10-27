"""Acceso explícito a D2; no importa ni lee ningún prototipo D3."""
import csv
import importlib
import json
import sys
from pathlib import Path
from .common import ROOT, file_sha


def locations():
    packaged = ROOT / 'data'
    project = ROOT.parent
    if packaged.is_dir():
        return ROOT / 'd2_runtime', packaged
    return project / 'Deliverable2/notebooks', project / 'Deliverable2/corpus/generado'


def d2_modules():
    directory, _ = locations()
    for name in ('experimento', 'recuperador_portable', 'sistema'):
        loaded = sys.modules.get(name)
        if loaded is not None and Path(loaded.__file__).resolve().parent != directory.resolve():
            raise RuntimeError('Hay otra versión de D2 cargada; reinicia la sesión.')
    sys.path.insert(0, str(directory.resolve())) if str(directory.resolve()) not in sys.path else None
    return importlib.import_module('experimento'), importlib.import_module('sistema')


def read_assets():
    _, directory = locations()
    corpus = json.loads((directory / 'corpus.json').read_text())
    fragments = json.loads((directory / 'fragmentos_busqueda.json').read_text())
    if (directory / 'preguntas.json').exists():
        questions = json.loads((directory / 'preguntas.json').read_text())
        config = json.loads((directory / 'configuracion.json').read_text())
    else:
        with (ROOT.parent / 'Deliverable1/datos/test_set_50.csv').open(encoding='utf-8-sig') as stream:
            questions = [{'id': n, 'pregunta': r['pregunta'], 'categoria': r['categoria']}
                         for n, r in enumerate(csv.DictReader(stream), 1)]
        original = json.loads((ROOT.parent / 'Deliverable2/seleccion_sistema.json').read_text())
        config = {k: original[k] for k in ('modelo', 'revision', 'embedding_modelo', 'embedding_revision',
                  'embedding_tokenizer_sha256', 'generacion', 'semilla_base', 'max_context_tokens')}
    if any(set(q) != {'id', 'pregunta', 'categoria'} for q in questions):
        raise ValueError('Las preguntas del runtime no pueden incluir referencias ni veredictos.')
    return corpus, fragments, questions, config


def source_files():
    directory, data = locations()
    paths = list((ROOT / 'd3_agentes').glob('*.py')) + list((ROOT / 'prompts').glob('*.txt'))
    files = {str(p.relative_to(ROOT)): p for p in paths}
    for name in ('experimento.py', 'sistema.py', 'recuperador_portable.py'):
        files['d2_runtime/' + name] = directory / name
    for name in ('corpus.json', 'fragmentos_busqueda.json'):
        files['data/' + name] = data / name
    return files


def source_identity():
    return {name: file_sha(path) for name, path in source_files().items()}
