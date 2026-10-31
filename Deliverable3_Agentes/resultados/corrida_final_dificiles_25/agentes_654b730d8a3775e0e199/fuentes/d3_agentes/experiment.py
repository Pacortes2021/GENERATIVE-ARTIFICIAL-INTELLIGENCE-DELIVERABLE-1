"""Ejecución emparejada, checkpoints por llamada y exportación sin juicios automáticos."""
import csv
import json
import time
import zipfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from .bridge import source_identity, source_files, d2_modules
from .common import (Limits, PromptBook, VARIANTS, digest, file_sha, save,
                     sealed_save, sealed_load, task_for)
from .core import AgentSystem
from .tools import CorpusAccess


def validate_questions(questions):
    if not questions or any(not isinstance(q, dict) or set(q) != {'id', 'pregunta', 'categoria'}
            or type(q['id']) is not int or q['id'] <= 0
            or not isinstance(q['pregunta'], str) or not q['pregunta'].strip()
            or not isinstance(q['categoria'], str) for q in questions):
        raise ValueError('Se requieren id positivo, pregunta y categoría; sin respuestas ideales.')
    if len({q['id'] for q in questions}) != len(questions):
        raise ValueError('IDs duplicados.')
    if len({q['pregunta'] for q in questions}) != len(questions):
        raise ValueError('Preguntas duplicadas.')


class Journal:
    def __init__(self, path, verbose=False):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose

    def __call__(self, event):
        with self.path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + '\n')
            stream.flush()
        if self.verbose:
            kind = event['tipo']
            if kind == 'modelo':
                print('\n[' + event.get('agente', 'modelo') + '] ' +
                      ('CHECKPOINT' if event['salida'].get('checkpoint_reutilizado') else 'GENERADO AHORA'), flush=True)
                print(event['salida']['respuesta_modelo'], flush=True)
            elif kind in ('transferencia', 'decision', 'observacion', 'fin', 'salida_invalida',
                          'herramienta_bloqueada', 'herramienta_rechazada', 'aceptacion_bloqueada',
                          'borrador_bloqueado', 'borrador_invalidado', 'ciclo_interrumpido', 'transferencia_bloqueada'):
                print(json.dumps(event, ensure_ascii=False, indent=2), flush=True)


class RecordedModel:
    def __init__(self, folder, identity, generate):
        self.folder, self.identity, self.generate = Path(folder), identity, generate
        self.calls = []

    def __call__(self, task, seed):
        identity = {'contexto': self.identity, 'tarea': task, 'semilla': seed}
        path = self.folder / (digest(identity) + '.json')
        cached = path.exists()
        if cached:
            saved = sealed_load(path)
            if saved['identidad'] != identity:
                raise ValueError('Checkpoint incompatible.')
            output = saved['salida']
        else:
            output = self.generate(task, seed)
            if not isinstance(output.get('respuesta_modelo'), str):
                raise ValueError('El backend no devolvió texto.')
            sealed_save(path, {'identidad': identity, 'salida': output})
        output = {**output, 'checkpoint_reutilizado': cached}
        self.calls.append({'tarea': task, 'semilla': seed, 'salida': output, 'archivo': path.name})
        return output


class RecordedTools:
    def __init__(self, folder, identity, tools):
        self.folder, self.identity, self.tools = Path(folder), identity, tools
        self.observations = []

    def execute(self, request):
        identity = {'contexto': self.identity, 'solicitud': request}
        path = self.folder / (digest(identity) + '.json')
        cached = path.exists()
        if cached:
            saved = sealed_load(path)
            if saved['identidad'] != identity:
                raise ValueError('Observación incompatible.')
        else:
            started = time.perf_counter()
            result = self.tools.execute(request)
            saved = {'identidad': identity, 'resultado': result, 'segundos': time.perf_counter() - started}
            sealed_save(path, saved)
        result = {**saved['resultado'], 'segundos': saved['segundos'], 'checkpoint_reutilizado': cached}
        self.observations.append(result)
        return result


def prepare(questions, retriever, settings, output, variants, limits, tag, prompts):
    validate_questions(questions)
    if not variants or len(set(variants)) != len(variants) or any(v not in VARIANTS for v in variants):
        raise ValueError('Condiciones desconocidas o duplicadas.')
    if settings['generacion']['max_new_tokens'] != limits.output_tokens:
        raise ValueError('Presupuesto de salida y backend distintos.')
    if settings.get('ejecucion') not in ('modelo_real', 'simulacion_pruebas'):
        raise ValueError('Identifica explícitamente si la ejecución usa modelo real o simulación.')
    config = {'protocolo': 'd3-agentes-desde-cero-v4', 'preguntas': questions,
              'variantes': list(variants), 'inferencia': settings, 'limites': asdict(limits),
              'etiqueta': tag, 'archivos_sha256': source_identity(), 'prompts_sha256': prompts.identity(),
              'corpus_sha256': digest(retriever.corpus), 'fragmentos_sha256': digest(retriever.fragments),
              'indice_sha256': retriever.index_sha256}
    folder = Path(output) / ('agentes_' + digest(config)[:20])
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / 'configuracion.json'
    if destination.exists():
        if sealed_load(destination) != config:
            raise ValueError('La carpeta tiene otra configuración.')
    else:
        sealed_save(destination, config)
    # Congelar código y corpus además de hashes: permite reconstruir el experimento exportado.
    for name, source in source_files().items():
        target = folder / 'fuentes' / name
        if file_sha(source) != config['archivos_sha256'][name]:
            raise ValueError('Cambió el código mientras se preparaba la corrida.')
        if target.exists() and file_sha(target) != config['archivos_sha256'][name]:
            raise ValueError('Una fuente exportada está alterada.')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    # Se exportan también los textos exactos; sus hashes no sustituyen los prompts.
    for name, text in prompts.texts.items():
        target = folder / 'prompts' / name
        target.parent.mkdir(exist_ok=True)
        if target.exists() and target.read_text(encoding='utf-8') != text:
            raise ValueError('Prompt exportado alterado.')
        target.write_text(text, encoding='utf-8')
    return folder, config


def run(questions, retriever, tokenizer, generate, settings, output,
        variants=VARIANTS, limits=None, tag='desarrollo-v4', verbose=True):
    limits, prompts = limits or Limits(), PromptBook()
    folder, config = prepare(questions, retriever, settings, output, variants, limits, tag, prompts)
    experiment, d2 = d2_modules()
    run_hash = digest(config)
    for index, question in enumerate(questions):
        # Rota el orden de las condiciones sin cambiar sus semillas ni sus entradas.
        offset = index % len(variants)
        order = list(variants[offset:]) + list(variants[:offset])
        for variant in order:
            dest = folder / 'resultados' / f'P{question["id"]:03}_{variant}.json'
            identity = {'corrida': run_hash, 'pregunta': question, 'variante': variant}
            if dest.exists():
                previous = sealed_load(dest)
                if previous['identidad'] != identity:
                    raise ValueError('Resultado incompatible.')
                print(f'P{question["id"]:02} {variant}: resultado conservado; no es inferencia nueva.', flush=True)
                continue
            print(f'P{question["id"]:02} {variant}: ejecutando', flush=True)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
            journal = Journal(folder / 'intentos' / f'P{question["id"]:03}_{variant}_{stamp}.jsonl', verbose)
            model = RecordedModel(folder / 'llamadas', identity, generate)
            tools = RecordedTools(folder / 'herramientas', identity, CorpusAccess(retriever.corpus, retriever))
            started = time.perf_counter()
            seed = settings['semilla_base'] + question['id']
            try:
                retrieval_seconds = 0.0
                if variant in VARIANTS[:2]:
                    if variant == 'baseline_directo':
                        chat = [{'role': 'system', 'content': d2.BASELINE_SYSTEM},
                                {'role': 'user', 'content': question['pregunta']}]
                        case = None
                    else:
                        # El control D2 conserva literalmente su recuperador y prompt.
                        cache = folder / 'recuperacion_d2' / f'P{question["id"]:03}.json'
                        if cache.exists():
                            item = sealed_load(cache)
                            if item['pregunta'] != question or item['corrida'] != run_hash:
                                raise ValueError('Recuperación D2 incompatible.')
                        else:
                            case, seconds = retriever.retrieve(question['pregunta'], question['id'], question['categoria'])
                            item = {'caso': case, 'segundos': seconds, 'pregunta': question, 'corrida': run_hash}
                            sealed_save(cache, item)
                        case, retrieval_seconds = item['caso'], item['segundos']
                        chat = experiment.messages(case, 'rag_estructurado')
                    task = task_for(tokenizer, chat, limits, variant)
                    generated = model(task, seed)
                    event = {'tipo': 'modelo', 'agente': variant, 'tarea': task, 'semilla': seed, 'salida': generated}
                    journal(event)
                    result = {'respuesta_modelo': generated['respuesta_modelo'], 'estado': 'respuesta_directa',
                              'evidencia': case, 'traza': [event]}
                else:
                    result = AgentSystem(tokenizer, model, tools, variant, limits, prompts, journal).run(question['pregunta'], seed)
                usage = {'llamadas_modelo': len(model.calls),
                         'llamadas_nuevas_este_intento': sum(not c['salida']['checkpoint_reutilizado'] for c in model.calls),
                         'tokens_entrada': sum(c['tarea']['tokens_entrada'] for c in model.calls),
                         'tokens_salida': sum(c['salida'].get('tokens_salida', 0) for c in model.calls),
                         'segundos_modelo_logicos': sum(c['salida'].get('segundos', 0) for c in model.calls),
                         'segundos_herramientas_logicos': retrieval_seconds + sum(o['segundos'] for o in tools.observations),
                         'segundos_pared_este_intento': time.perf_counter() - started,
                         'salidas_cortadas': sum(bool(c['salida'].get('posible_corte')) for c in model.calls)}
                sealed_save(dest, {'identidad': identity, 'resultado': result, 'uso': usage,
                                   'ejecucion': settings['ejecucion'], 'checkpoints': [c['archivo'] for c in model.calls]})
                export(folder)
            except Exception as exc:
                journal({'tipo': 'error_tecnico', 'clase': type(exc).__name__, 'mensaje': str(exc)})
                export(folder)
                raise
    export(folder)
    return folder


def export(folder):
    folder = Path(folder)
    config = sealed_load(folder / 'configuracion.json')
    run_hash, rows = digest(config), []
    expected = {(q['id'], v) for q in config['preguntas'] for v in config['variantes']}
    for p in sorted((folder / 'resultados').glob('*.json')):
        saved = sealed_load(p)
        identity, result = saved['identidad'], saved['resultado']
        if (identity['corrida'] != run_hash or identity['pregunta'] not in config['preguntas']
                or saved['ejecucion'] != config['inferencia']['ejecucion']):
            raise ValueError('Resultado ajeno a esta corrida.')
        q = identity['pregunta']
        rows.append({'pregunta_id': q['id'], 'pregunta': q['pregunta'], 'categoria': q['categoria'],
                     'variante': identity['variante'], 'respuesta_modelo': result['respuesta_modelo'],
                     'estado': result['estado'], 'ejecucion': saved['ejecucion'], **saved['uso']})
    actual = {(r['pregunta_id'], r['variante']) for r in rows}
    if len(actual) != len(rows) or not actual <= expected:
        raise ValueError('Condiciones duplicadas o inesperadas.')
    fields = ['pregunta_id', 'pregunta', 'categoria', 'variante', 'respuesta_modelo', 'estado', 'ejecucion',
              'llamadas_modelo', 'llamadas_nuevas_este_intento', 'tokens_entrada', 'tokens_salida',
              'segundos_modelo_logicos', 'segundos_herramientas_logicos', 'segundos_pared_este_intento', 'salidas_cortadas']
    for variant in config['variantes']:
        with (folder / (variant + '.csv')).open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(r for r in rows if r['variante'] == variant)
    save(folder / 'resumen_tecnico.json', {'esperadas': len(expected), 'completadas': len(actual),
         'completa': actual == expected, 'ejecucion': config['inferencia']['ejecucion'],
         'exactitud': None, 'nota': 'La exactitud requiere evaluación externa; una aceptación interna no es un acierto.',
         'por_variante': {v: {'n': sum(r['variante'] == v for r in rows),
             **{k: sum(r[k] for r in rows if r['variante'] == v) for k in
                ('llamadas_modelo', 'tokens_entrada', 'tokens_salida', 'segundos_modelo_logicos', 'salidas_cortadas')}}
             for v in config['variantes']}})
    files = {str(p.relative_to(folder)): file_sha(p) for p in folder.rglob('*')
             if p.is_file() and p.name != 'manifiesto.json'}
    save(folder / 'manifiesto.json', {'archivos_sha256': files})
    target = folder.with_suffix('.zip')
    temporary = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files) + ['manifiesto.json']:
            archive.write(folder / name, name)
    temporary.replace(target)
    return target


def audit_zip(path):
    import hashlib
    import io
    with zipfile.ZipFile(path) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())) or archive.testzip() is not None:
            raise ValueError('ZIP corrupto o con entradas duplicadas.')
        manifest = json.loads(archive.read('manifiesto.json'))['archivos_sha256']
        if set(archive.namelist()) != set(manifest) | {'manifiesto.json'}:
            raise ValueError('Inventario del ZIP distinto del manifiesto.')
        for name, expected in manifest.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected:
                raise ValueError('Archivo del ZIP alterado: ' + name)
        def unseal(name):
            value = json.loads(archive.read(name))
            if set(value) != {'contenido','sha256'} or digest(value['contenido']) != value['sha256']:
                raise ValueError('Sello inválido en ' + name)
            return value['contenido']
        config = unseal('configuracion.json')
        for name, expected in config['archivos_sha256'].items():
            if hashlib.sha256(archive.read('fuentes/' + name)).hexdigest() != expected:
                raise ValueError('Las fuentes no corresponden a la configuración.')
        for name, expected in config['prompts_sha256'].items():
            if hashlib.sha256(archive.read('prompts/' + name)).hexdigest() != expected:
                raise ValueError('El prompt no corresponde a la configuración.')
        results = {}
        for name in manifest:
            if name.startswith(('llamadas/', 'herramientas/', 'recuperacion_d2/')):
                unseal(name)
            if name.startswith('resultados/'):
                saved = unseal(name)
                identity = saved['identidad']
                if (identity['corrida'] != digest(config) or identity['pregunta'] not in config['preguntas']
                        or identity['variante'] not in config['variantes']
                        or saved['ejecucion'] != config['inferencia']['ejecucion']):
                    raise ValueError('Resultado ajeno a esta corrida.')
                key = (identity['pregunta']['id'], identity['variante'])
                if key in results:
                    raise ValueError('Resultado duplicado.')
                results[key] = saved
                for checkpoint in saved['checkpoints']:
                    record = unseal('llamadas/' + checkpoint)
                    if record['identidad']['contexto'] != identity:
                        raise ValueError('Llamada de otra condición.')
        seen = set()
        for variant in config['variantes']:
            rows = csv.DictReader(io.StringIO(archive.read(variant + '.csv').decode('utf-8')))
            for row in rows:
                key = (int(row['pregunta_id']), variant)
                if key not in results or key in seen:
                    raise ValueError('CSV con resultado faltante o duplicado.')
                saved = results[key]
                if (row['respuesta_modelo'] != saved['resultado']['respuesta_modelo']
                        or row['pregunta'] != saved['identidad']['pregunta']['pregunta']
                        or row['estado'] != saved['resultado']['estado']
                        or row['ejecucion'] != saved['ejecucion'] or row['variante'] != variant):
                    raise ValueError('CSV no coincide con sus respuestas originales.')
                seen.add(key)
        summary = json.loads(archive.read('resumen_tecnico.json'))
        expected_count = len(config['preguntas']) * len(config['variantes'])
        if (seen != set(results) or summary['completadas'] != len(seen)
                or summary['esperadas'] != expected_count or summary['completa'] != (len(seen)==expected_count)
                or summary['exactitud'] is not None):
            raise ValueError('Resumen técnico incompatible.')
        return summary
