"""Prepara evidencia para un juez y calcula reportes; no juzga semántica por sí solo."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CRITERIOS = Path(__file__).with_name('criterios.md')
REFERENCIAS = Path(__file__).with_name('referencias.json')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(obj):
    return sha(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode())


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def check_destination(path):
    path = Path(path).resolve()
    for name in ('Deliverable1', 'Corpus', 'Archivo', '.git'):
        protected = ROOT / name
        if path == protected or protected in path.parents:
            raise ValueError('No se escribe dentro de ' + name)
    return path


def preparar(csv_path, output):
    csv_path = Path(csv_path)
    with (ROOT / 'Deliverable1/datos/test_set_50.csv').open(encoding='utf-8-sig', newline='') as f:
        referencias = list(csv.DictReader(f))
    pauta = read_json(REFERENCIAS)
    respuestas = pauta['respuestas']
    if len(respuestas) != len(referencias) or any(
        r['id'] != i + 1 or r['pregunta'] != original['pregunta']
        or r['categoria'] != original['categoria']
        or not r['respuesta_referencia'].strip() or not r['fuentes']
        for i, (r, original) in enumerate(zip(respuestas, referencias))
    ):
        raise ValueError('La pauta no corresponde a las 50 preguntas originales.')
    for fuente in pauta['corpus']:
        if sha((ROOT / fuente['archivo']).read_bytes()) != fuente['sha256']:
            raise ValueError('Cambió el corpus; verificar la pauta antes de evaluar.')
    por_pregunta = {r['pregunta']: r for r in respuestas}
    with csv_path.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError('El CSV está vacío.')
    casos, seen = [], set()
    for row in rows:
        if not {'pregunta', 'respuesta_modelo'} <= row.keys():
            raise ValueError('Se requieren las columnas pregunta y respuesta_modelo.')
        if row['pregunta'] not in por_pregunta:
            raise ValueError('Pregunta no reconocida; use el texto exacto del test E1.')
        ref = por_pregunta[row['pregunta']]
        numero = ref['id']
        if numero in seen:
            raise ValueError('Pregunta duplicada: ' + str(numero))
        seen.add(numero)
        answer = row['respuesta_modelo']
        if not isinstance(answer, str):
            raise ValueError('Respuesta ausente; una salida vacía debe guardarse como cadena vacía.')
        casos.append({'caso_id': f'P{numero:02}', 'pregunta_id': numero,
                      **ref, 'respuesta_modelo': answer,
                      'respuesta_sha256': sha(answer.encode())})
    corpus = []
    for path in sorted((ROOT / 'Corpus').glob('*.pdf')):
        corpus.append({'archivo': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())})
    if len(corpus) != 3:
        raise ValueError('Se esperaban los tres PDF del corpus.')
    packet = {'version': 2, 'creado_utc': datetime.now(timezone.utc).isoformat(),
              'entrada_sha256': sha(csv_path.read_bytes()),
              'referencias_version': pauta['version'],
              'referencias_sha256': sha(REFERENCIAS.read_bytes()),
              'test_sha256': sha((ROOT / 'Deliverable1/datos/test_set_50.csv').read_bytes()),
              'criterios': CRITERIOS.read_text(encoding='utf-8'),
              'corpus': corpus, 'casos': casos}
    judgments = {'paquete_sha256': digest(packet), 'evaluador': '', 'modalidad': '',
                 'evaluaciones': [{'caso_id': c['caso_id'],
                                   'respuesta_sha256': c['respuesta_sha256'],
                                   'correcta': None, 'motivo': ''}
                                  for c in casos]}
    output = check_destination(output)
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / 'paquete.json', packet)
    write_json(output / 'veredictos.json', judgments)
    return len(casos)


def resultados(packet, judgments):
    if packet.get('version') != 2:
        raise ValueError('Versión anterior: preparar un paquete nuevo con la pauta de E2.')
    if judgments['paquete_sha256'] != digest(packet):
        raise ValueError('Los veredictos pertenecen a otro paquete o el paquete cambió.')
    cases = packet['casos']
    if not cases or len({c['caso_id'] for c in cases}) != len(cases):
        raise ValueError('Paquete vacío o con identificadores duplicados.')
    decisions = judgments['evaluaciones']
    by_id = {r['caso_id']: r for r in decisions}
    if len(by_id) != len(decisions) or set(by_id) != {c['caso_id'] for c in cases}:
        raise ValueError('Deben existir exactamente los mismos casos, sin duplicados.')
    rows = []
    for case in cases:
        r = by_id[case['caso_id']]
        if r['respuesta_sha256'] != sha(case['respuesta_modelo'].encode()):
            raise ValueError('La respuesta cambió: ' + case['caso_id'])
        correcta = r['correcta']
        if correcta is not None and type(correcta) is not bool:
            raise ValueError('correcta acepta solo true, false o null.')
        if not isinstance(r['motivo'], str):
            raise ValueError('El motivo debe ser texto.')
        touched = correcta is not None or bool(r['motivo'].strip())
        if touched:
            if not r['motivo'].strip():
                raise ValueError('Falta motivo en ' + case['caso_id'])
            if not isinstance(judgments.get('evaluador'), str) or not judgments['evaluador'].strip():
                raise ValueError('Debe identificarse al evaluador.')
            if judgments.get('modalidad') not in ('revision_asistida_chat', 'api', 'humana'):
                raise ValueError('Modalidad de evaluación inválida.')
        verdict = 'pendiente' if correcta is None else ('correcta' if correcta else 'incorrecta')
        # Solo incorporar campos de juicio; el juez no puede sobrescribir la evidencia.
        rows.append({**case, 'correcta': correcta, 'motivo': r['motivo'], 'veredicto': verdict})
    return rows


def resumen(rows):
    if not rows:
        raise ValueError('No se puede calcular una evaluación sin casos.')
    counts = Counter(r['veredicto'] for r in rows)
    n = len(rows)
    return {'total': n, 'correctas': counts['correcta'], 'incorrectas': counts['incorrecta'],
            'pendientes': counts['pendiente'],
            'exactitud_porcentaje': None if counts['pendiente'] else round(100 * counts['correcta'] / n, 2)}


def resumir(packet_path, judgments_path, output):
    packet, judgments = read_json(packet_path), read_json(judgments_path)
    rows = resultados(packet, judgments)
    report = {'paquete_sha256': digest(packet), 'veredictos_sha256': digest(judgments),
              'referencias_version': packet['referencias_version'],
              'referencias_sha256': packet['referencias_sha256'],
              'evaluador': judgments['evaluador'], 'modalidad': judgments['modalidad'],
              'global': resumen(rows),
              'por_categoria': {cat: resumen([r for r in rows if r['categoria'] == cat])
                                for cat in sorted({r['categoria'] for r in rows})}}
    output = check_destination(output)
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / 'resumen.json', report)
    fields = ['caso_id', 'categoria', 'pregunta', 'respuesta_referencia', 'respuesta_modelo',
              'correcta', 'veredicto', 'motivo', 'respuesta_sha256']
    with (output / 'evaluacion.csv').open('x', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    return report['global']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('preparar')
    p.add_argument('--respuestas', required=True)
    p.add_argument('--salida', required=True)
    p = commands.add_parser('resumir')
    p.add_argument('--paquete', required=True)
    p.add_argument('--veredictos', required=True)
    p.add_argument('--salida', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'preparar':
            print(f'{preparar(args.respuestas, args.salida)} casos preparados; sin calificar.')
        else:
            print(json.dumps(resumir(args.paquete, args.veredictos, args.salida), ensure_ascii=False))
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
