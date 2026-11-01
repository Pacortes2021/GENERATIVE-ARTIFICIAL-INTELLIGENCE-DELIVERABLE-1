"""Audita archivos, respuestas, veredictos exportados y llamadas; no ejecuta modelos."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest = json.loads((ROOT/'auditoria/manifiesto.json').read_text())
    for name, expected in manifest.items():
        assert sha(ROOT/name) == expected, f'Archivo modificado: {name}'
    labels = json.loads((ROOT/'auditoria/veredictos_exportados.json').read_text())
    summary = {}
    questions = None
    for variant, data in labels.items():
        assert sha(ROOT/data['fuente']) == data['sha256_fuente']
        folder = ROOT/'Deliverable3'/('resultados_v6' if variant=='completo' else 'resultados_ablaciones/'+variant)
        with (folder/'resultados_agentes_D3.csv').open(encoding='utf-8-sig',newline='') as f:
            rows = list(csv.DictReader(f))
        traces = json.loads((folder/'trazas_D3.json').read_text())
        judged = {c['pregunta']:c for c in data['casos']}
        assert len(rows)==len(traces)==len(judged)==75
        qs = {r['pregunta'] for r in rows}
        assert questions is None or questions == qs
        questions = qs
        for row in rows:
            assert row['respuesta_sistema']==judged[row['pregunta']]['respuesta']
            key = row['set']+':'+row['id']
            draft = [e['salida'] for e in traces[key] if e['agente']=='redactor'][-1]
            assert draft == row['respuesta_sistema'], f'Traza/CSV diferente: {variant} {key}'
        calls = sum(not event.get('decidido_por') for trace in traces.values() for event in trace)
        groups = {}
        for group in ('congelado_50','dificil_25'):
            selected = [r for r in rows if r['set']==group]
            groups[group] = {'n':len(selected), 'correctas':sum(judged[r['pregunta']]['correcta'] for r in selected)}
        summary[variant] = {'conjuntos':groups, 'llamadas_modelo':calls,
                            'promedio_llamadas':round(calls/75,2),
                            'eventos':sum(map(len,traces.values()))}
    print(json.dumps({'archivos_verificados':len(manifest),'variantes':summary},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
