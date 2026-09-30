"""Celda final para Colab: audita el ZIP de la corrida y los juicios publicados.

Pégala al final de la sesión ya ejecutada. Solo usa biblioteca estándar;
no carga E5 ni Qwen y no genera ni califica respuestas nuevas.
"""
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile

# Puedes definir ZIP_LOTE e ID_CASO en Colab antes de ejecutar esta celda.
# Si no hay una copia local, se descarga la corrida previa publicada; no se genera otra.
ID_CASO = globals().get('ID_CASO', 25)  # Cualquier número de 1 a 50.

ZIP_NOMBRE = 'comparacion_f0bff499766960f7.zip'
ZIP_SHA256 = 'e6d6628c8ae27f85f8f6bfd11f859a5d95d32731c51a88ab3e1a4e5b4c42a797'
RUN_SHA256 = 'f0bff499766960f7bf41e9c8a29bcb9d74fac7d2431dc2663a5ccfe8304cc598'
CORRIDA_PUBLICADA = ('https://raw.githubusercontent.com/Pacortes2021/'
                    'GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/773a7da/'
                    'Deliverable2/resultados/qwen3_4b_f0bff499766960f7')
BASE = CORRIDA_PUBLICADA + '/evaluacion'
PUBLICADOS = {
    'baseline_directo': {
        'paquete.json': '4bdd4ac6739677a9c33e3017c204aecf2d587f6d580cf55b75e2d13a354a24f5',
        'veredictos.json': '52dccafdaa6ecdfd29327b3b163b93d0f434f5e402568e0166ca588a76848d3d',
    },
    'rag_estructurado': {
        'paquete.json': '93c7b4bc9a52cf757a26ebaaf9f561387d21413e3a76c43cc6e44515ee41287b',
        'veredictos.json': 'e993dcd96e8c13334c99b97b14fd8baad70a9b8321076a95cc15f36894fdd276',
    },
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def localizar_zip(preferido=None, output_root=None, content_root=Path('/content')):
    content_root = Path(content_root)
    copia_publicada = content_root / 'auditoria_publicada' / ZIP_NOMBRE
    candidatos = [Path(preferido)] if preferido is not None else []
    if output_root is not None:
        candidatos.append(Path(output_root) / ZIP_NOMBRE)
    candidatos.extend([
        content_root / 'drive/MyDrive/GenIA_Deliverable2/sistema_runs' / ZIP_NOMBRE,
        content_root / 'sistema_runs' / ZIP_NOMBRE,
        content_root / ZIP_NOMBRE,
        copia_publicada,
    ])
    for ruta in dict.fromkeys(candidatos):
        if ruta.is_file():
            assert sha(ruta.read_bytes()) == ZIP_SHA256, (
                f'El ZIP local no coincide con el original evaluado: {ruta}. '
                'No se reemplazó. Usa el ZIP original de la corrida f0bff499766960f7.')
            origen = ('Copia publicada en GitHub, conservada en Colab'
                      if ruta == copia_publicada else 'Archivo local verificado')
            return ruta, origen
    url = CORRIDA_PUBLICADA + '/' + ZIP_NOMBRE
    print('El ZIP no está en las rutas locales. Descargando la copia de la corrida previa:')
    print(url)
    with urllib.request.urlopen(url, timeout=30) as response:
        data = response.read()
    assert sha(data) == ZIP_SHA256, 'La descarga no coincide con el ZIP original; no se guardó.'
    copia_publicada.parent.mkdir(parents=True, exist_ok=True)
    copia_publicada.write_bytes(data)
    return copia_publicada, 'Copia de la corrida previa descargada de GitHub (commit 773a7da)'

def canon(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())

def digest_evaluacion(value):
    # evaluar.py usa los separadores predeterminados de json.dumps.
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True).encode())

def publicado(variante, nombre):
    url = f'{BASE}/{variante}/{nombre}'
    with urllib.request.urlopen(url, timeout=30) as response:
        data = response.read()
    assert sha(data) == PUBLICADOS[variante][nombre], f'Cambió el archivo publicado: {url}'
    return json.loads(data)

ZIP_LOTE, origen_zip = localizar_zip(globals().get('ZIP_LOTE'), globals().get('OUTPUT_ROOT'))
zip_bytes = ZIP_LOTE.read_bytes()
assert sha(zip_bytes) == ZIP_SHA256, ('El ZIP no coincide byte a byte con el descargado y evaluado. '
                                     'Usa el comparacion_f0bff499766960f7.zip original; no otro exportado después.')
with zipfile.ZipFile(ZIP_LOTE) as z:
    assert z.testzip() is None, 'El ZIP tiene un miembro corrupto.'
    config = json.loads(z.read('configuracion.json'))
    tasks = json.loads(z.read('prompts.json'))
    evidence = json.loads(z.read('evidencia.json'))
    assert canon(config) == RUN_SHA256, 'La configuración no corresponde a la corrida evaluada.'
    assert canon(tasks) == config['prompts_sha256'], 'Cambiaron los prompts del lote.'
    assert canon(evidence['origen']) == config['payload_sha256'], 'Cambió la evidencia del lote.'
    assert config['casos'] == list(range(1, 51)), 'El ZIP no contiene las 50 preguntas esperadas.'
    task_by_key = {(t['pregunta_id'], t['variante']): t for t in tasks}
    assert len(task_by_key) == len(tasks) == 100, 'Faltan o se duplican prompts.'
    answers = {}
    for member in z.namelist():
        if not member.startswith('respuestas/') or not member.endswith('.json'):
            continue
        row = json.loads(z.read(member))
        key = (row['pregunta_id'], row['variante'])
        assert key not in answers and key in task_by_key, f'Respuesta inesperada: {member}'
        task = task_by_key[key]
        assert row['run_hash'] == RUN_SHA256 and row['pregunta'] == task['pregunta'], member
        assert row['prompt_sha256'] == task['prompt_sha256'] == canon(task['prompt']), member
        assert row['evidencia_sha256'] == task['evidencia_sha256'], member
        assert row['respuesta_sha256'] == canon(row['respuesta_modelo']), member
        answers[key] = row
    assert len(answers) == 100, 'No están las 100 respuestas individuales.'

packets, judgments, marks = {}, {}, {}
for variant in PUBLICADOS:
    packet = publicado(variant, 'paquete.json')
    verdicts = publicado(variant, 'veredictos.json')
    assert verdicts['paquete_sha256'] == digest_evaluacion(packet), f'Paquete y veredictos no coinciden: {variant}'
    cases = {c['caso_id']: c for c in packet['casos']}
    decisions = {e['caso_id']: e for e in verdicts['evaluaciones']}
    assert len(cases) == len(decisions) == 50, f'No hay 50 juicios para {variant}.'
    marks[variant] = {}
    for number in range(1, 51):
        case_id = f'P{number:02}'
        case, decision, answer = cases[case_id], decisions[case_id], answers[(number, variant)]
        raw_answer_hash = sha(answer['respuesta_modelo'].encode())
        assert case['pregunta'] == answer['pregunta'], case_id
        assert case['respuesta_modelo'] == answer['respuesta_modelo'], case_id
        assert case['respuesta_sha256'] == decision['respuesta_sha256'] == raw_answer_hash, case_id
        assert isinstance(decision['correcta'], bool) and decision['motivo'].strip(), case_id
        marks[variant][number] = decision['correcta']
    packets[variant], judgments[variant] = cases, decisions

print('AUDITORÍA DEL LOTE EMPAREJADO')
print('Origen:', origen_zip, '| Ruta:', ZIP_LOTE)
print('Se audita la corrida previa f0bff499766960f7; esta celda no ejecuta una corrida nueva.')
print('ZIP original:', ZIP_LOTE.name, '| SHA-256, CRC y 100 respuestas: OK')
print('Configuración, prompts, evidencia y hashes de 100 respuestas: OK')
print('100 juicios publicados en un commit fijo; hashes y vínculos con respuestas: OK')
print('Estos son recuentos de veredictos asistidos previamente, no una evaluación semántica automática en Colab.\n')
for variant, label in [('baseline_directo', 'Baseline sin documentos'),
                       ('rag_estructurado', 'RAG estructurado')]:
    correct = sum(marks[variant].values())
    print(f'{label}: {correct}/50 ({correct*2} %)')
wrong_rag = [f'P{i:02}' for i, correct in marks['rag_estructurado'].items() if not correct]
print('Todos los fallos RAG:', ', '.join(wrong_rag))

assert 1 <= ID_CASO <= 50
case_id = f'P{ID_CASO:02}'
row = answers[(ID_CASO, 'rag_estructurado')]
case = next(c for c in evidence['origen']['casos'] if c['id'] == ID_CASO)
task = task_by_key[(ID_CASO, 'rag_estructurado')]
print(f'\nCASO {case_id}: {row["pregunta"]}')
print('Respuesta RAG:', row['respuesta_modelo'])
print('Referencia del evaluador:', packets['rag_estructurado'][case_id]['respuesta_referencia'])
print('Veredicto registrado:', judgments['rag_estructurado'][case_id]['correcta'])
print('Motivo registrado:', judgments['rag_estructurado'][case_id]['motivo'])
print('Parada:', row['motivo_parada'], '| posible corte:', row['posible_corte'])
print('Unidades enviadas en el prompt:', ', '.join(c['unidad_id'] for c in case['contextos']))

if ID_CASO == 25:
    prompt_usuario = task['mensajes'][-1]['content']
    for unit_id in ('RI-FI-ART-007', 'RI-FI-ART-009'):
        unit = next(c for c in case['contextos'] if c['unidad_id'] == unit_id)
        assert unit['texto'] in prompt_usuario, f'{unit_id} no aparece íntegro en el prompt.'
        print(f'\n{unit_id} — texto íntegro que recibió Qwen:\n{unit["texto"]}')
