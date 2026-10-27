"""Prepara juicios externos con la pauta D2 y compara todas las condiciones configuradas."""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
from d3_agentes.common import ROOT, digest, file_sha, save, sealed_load


def evaluator():
    path = ROOT.parent / 'Deliverable2/evaluacion/evaluar.py'
    spec = importlib.util.spec_from_file_location('evaluador_d2_externo', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_all(run_folder, destination):
    folder, output = Path(run_folder), Path(destination)
    if output.exists():
        raise ValueError('La carpeta de evaluación ya existe. Conserva los juicios anteriores.')
    config = sealed_load(folder / 'configuracion.json')
    summary = json.loads((folder / 'resumen_tecnico.json').read_text())
    if not summary['completa']:
        raise ValueError('Completa primero todas las condiciones de la corrida seleccionada.')
    module = evaluator()
    for variant in config['variantes']:
        module.preparar(folder / (variant + '.csv'), output / variant)
    save(output / 'origen.json', {'corrida': digest(config), 'variantes': config['variantes']})
    return {'estado': 'pendiente_de_juicios', 'variantes': config['variantes']}


def compare(run_folder, evaluations):
    folder, evaluations = Path(run_folder), Path(evaluations)
    config = sealed_load(folder / 'configuracion.json')
    origin = json.loads((evaluations / 'origen.json').read_text())
    if origin != {'corrida': digest(config), 'variantes': config['variantes']}:
        raise ValueError('Evaluaciones de otra corrida.')
    module, judged, packets = evaluator(), {}, {}
    expected_questions = {q['pregunta'] for q in config['preguntas']}
    for variant in config['variantes']:
        directory = evaluations / variant
        packet = json.loads((directory / 'paquete.json').read_text())
        decisions = json.loads((directory / 'veredictos.json').read_text())
        rows = module.resultados(packet, decisions)
        if any(r['correcta'] is None for r in rows):
            raise ValueError('Quedan juicios pendientes en ' + variant)
        csv_path = folder / (variant + '.csv')
        if packet['entrada_sha256'] != file_sha(csv_path):
            raise ValueError('El CSV cambió después de preparar los juicios.')
        with csv_path.open(encoding='utf-8-sig') as stream:
            exported = list(csv.DictReader(stream))
        if (len(exported) != len(expected_questions) or len(rows) != len(expected_questions)
                or {r['pregunta'] for r in rows} != expected_questions
                or {r['pregunta'] for r in exported} != expected_questions):
            raise ValueError('No se evaluaron las mismas preguntas en todas las condiciones.')
        actual = {r['pregunta']: r for r in exported}
        for row in rows:
            if row['respuesta_modelo'] != actual[row['pregunta']]['respuesta_modelo']:
                raise ValueError('Una respuesta cambió dentro del paquete de evaluación.')
        judged[variant] = {r['pregunta']: r for r in rows}
        packets[variant] = packet
    first = packets[config['variantes'][0]]
    for packet in packets.values():
        for key in ('corpus', 'criterios', 'test_sha256', 'referencias_sha256'):
            if packet[key] != first[key]:
                raise ValueError('No se aplicó la misma pauta y corpus.')
    metrics = {v: module.resumen(list(rows.values())) for v, rows in judged.items()}
    changes = {}
    if 'agentes_completo' in judged:
        full = judged['agentes_completo']
        for variant in judged:
            if variant == 'agentes_completo':
                continue
            before = judged[variant]
            changes[variant] = {
                'correcta_solo_completo': [full[q]['caso_id'] for q in full if full[q]['correcta'] and not before[q]['correcta']],
                'correcta_solo_comparador': [full[q]['caso_id'] for q in full if before[q]['correcta'] and not full[q]['correcta']],
                'delta_puntos_porcentuales': round(metrics['agentes_completo']['exactitud_porcentaje'] -
                                                 metrics[variant]['exactitud_porcentaje'], 2)}
    return {'corrida': digest(config), 'ejecucion': config['inferencia']['ejecucion'],
            'metricas': metrics, 'completo_frente_a': changes,
            'alcance': 'Conjunto de desarrollo de D1/D2; no demuestra generalización.',
            'nota': 'Juicios externos al sistema; la aceptación interna del auditor no se usa como etiqueta.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('accion', choices=('preparar', 'comparar'))
    parser.add_argument('--corrida', type=Path, required=True)
    parser.add_argument('--evaluaciones', type=Path, required=True)
    parser.add_argument('--informe', type=Path)
    args = parser.parse_args()
    if args.accion == 'preparar':
        result = prepare_all(args.corrida, args.evaluaciones)
    else:
        result = compare(args.corrida, args.evaluaciones)
        if args.informe:
            with args.informe.open('x', encoding='utf-8') as stream:
                json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
