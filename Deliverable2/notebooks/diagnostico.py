"""Inspección de resultados: no asigna corrección semántica ni hace inferencia."""
import hashlib
import json
import re
import statistics
import zipfile
from pathlib import Path


def diagnostic_digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def read_run_zip(path):
    # Leer JSON sin ejecutar código ni extraer rutas del ZIP.
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('El ZIP contiene nombres duplicados.')
        required = {'configuracion.json', 'evidencia.json', 'prompts.json'}
        if not required <= set(names):
            raise ValueError('Se requiere un ZIP exportado por los cuadernos RAG del proyecto.')
        if sum(i.file_size for i in archive.infolist()) > 200 * 1024 * 1024:
            raise ValueError('El ZIP supera el tamaño esperado para un reporte de texto.')
        read = lambda name: json.loads(archive.read(name))
        config = read('configuracion.json')
        evidence_packet = read('evidencia.json')
        tasks = read('prompts.json')
        if diagnostic_digest(evidence_packet['origen']) != config['payload_sha256']:
            raise ValueError('La evidencia no coincide con la configuración.')
        if diagnostic_digest(tasks) != config['prompts_sha256']:
            raise ValueError('Los prompts no coinciden con la configuración.')
        expected = {(t['pregunta_id'], t['variante']): t for t in tasks}
        rows, seen = [], set()
        for name in sorted(names):
            if not (name.startswith('respuestas/') and name.endswith('.json')):
                continue
            row = read(name)
            key = (row['pregunta_id'], row['variante'])
            if key not in expected or key in seen:
                raise ValueError('Respuesta desconocida o duplicada: ' + str(key))
            seen.add(key)
            task = expected[key]
            if (row['run_hash'] != diagnostic_digest(config) or row['prompt_sha256'] != task['prompt_sha256']
                    or row['evidencia_sha256'] != task['evidencia_sha256']
                    or diagnostic_digest(row['respuesta_modelo']) != row['respuesta_sha256']):
                raise ValueError('Respuesta incompatible o alterada: ' + name)
            rows.append(row)
    return rows, evidence_packet['origen']['casos'], config


def diagnostic_summary(rows):
    groups = {}
    for row in rows:
        groups.setdefault((row['variante'], row['categoria']), []).append(row)
    result = []
    for (variant, category), items in sorted(groups.items()):
        result.append({'variante': variant, 'categoria': category, 'respuestas': len(items),
                       'posibles_cortes': sum(bool(r['posible_corte']) for r in items),
                       'vacias': sum(not r['respuesta_modelo'].strip() for r in items),
                       'thinking_inesperado': sum(bool(r['thinking_inesperado']) for r in items),
                       'media_segundos': round(statistics.mean(r['segundos'] for r in items), 2),
                       'mediana_segundos': round(statistics.median(r['segundos'] for r in items), 2),
                       'media_tokens_entrada': round(statistics.mean(r['tokens_entrada'] for r in items), 1),
                       'media_tokens_salida': round(statistics.mean(r['tokens_salida'] for r in items), 1)})
    return result


def cite_alerts(row, case):
    valid = {c['unidad_id'] for c in case['contextos']}
    valid |= {f'INV-{i}' for i, _ in enumerate(case.get('contextos_inventario', []), 1)}
    mentions = re.findall(r'\[([^\]\n]+)\]', row['respuesta_modelo'])
    # Solo reconocer el esquema de ID enseñado. Una cita libre no se juzga aquí.
    ids = {m.strip() for m in mentions if re.fullmatch(r'(?:RI-FI|RG|CAL|INV|EJ)-[\w-]+', m.strip())}
    return {'ids_reconocidos': sorted(ids), 'ids_ajenos_a_evidencia': sorted(ids - valid),
            'sin_id_reconocido': not bool(ids)}


def show_case(question_id, rows, cases):
    case = next((c for c in cases if c['id'] == question_id), None)
    if case is None:
        raise ValueError('Pregunta no incluida en el paquete.')
    print(f"P{question_id:02}: {case['pregunta']}\nCategoría: {case['categoria']}")
    selected = [r for r in rows if r['pregunta_id'] == question_id]
    if not selected:
        print('Todavía no hay respuestas guardadas para esta pregunta.')
    for row in selected:
        print('\n' + '=' * 65)
        print(row['variante'], '| parada:', row['motivo_parada'], '| salida:', row['tokens_salida'], 'tokens')
        print(row['respuesta_modelo'])
        print('Alertas mecánicas de citas:', cite_alerts(row, case))
    print('\n' + '=' * 65 + '\nEVIDENCIA EXACTA DE ESTA CONSULTA:')
    for context in case['contextos']:
        print(f"\n[{context['unidad_id']}] {context['cita']}\n{context['texto']}")
    for i, inventory in enumerate(case.get('contextos_inventario', []), 1):
        print(f"\n[INV-{i}] Inventario de {inventory['archivo']}\n{inventory['texto']}")
    print('\nLas alertas no son veredictos: una cita existente puede no respaldar la respuesta y una cita libre puede ser válida.')
