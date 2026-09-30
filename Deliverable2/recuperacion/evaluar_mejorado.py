"""Audita la selección mejorada y compara cobertura sin alterar contextos."""
import argparse
from pathlib import Path

from evaluar_recuperacion import coverage
from probar_recuperacion import ROOT, read, require, sha, write
from recuperar_mejorado import make_contexts, POLICY, subqueries


def evaluate(run, rubric, corpus, baseline_report):
    require(run['configuracion']['politica'] == POLICY, 'Política distinta: usar el código correspondiente a la corrida')
    require(run['fuentes_sha256']['corpus'] == rubric['corpus_sha256'], 'Corpus distinto a la pauta')
    require([c['id'] for c in run['casos']] == [c['id'] for c in rubric['casos']], 'Casos distintos')
    before = {c['id']: c for c in baseline_report['casos']}
    cases = []
    for case, expected in zip(run['casos'], rubric['casos']):
        require(case['pregunta'] == expected['pregunta'], 'Pregunta distinta')
        require([s['texto'] for s in case['subconsultas']] == subqueries(case['pregunta']), 'Subconsultas alteradas')
        replay = make_contexts(case['pregunta'], corpus, [r['unidad_id'] for r in case['ranking_original']],
                               [[r['unidad_id'] for r in s['ranking']] for s in case['subconsultas']])
        for key, value in replay.items():
            require(case[key] == value, f'Selección/contexto/inventario alterado en P{case["id"]}: {key}')
        ids = [c['unidad_id'] for c in case['contextos']]
        row = {'id': case['id'], 'pregunta': case['pregunta'], 'tipo': expected['tipo'],
               'unidades': ids, 'caracteres': case['caracteres_contexto'],
               'antes_completa': before[case['id']]['completa']}
        if expected['tipo'] == 'evidencia_local':
            row.update(coverage(expected['grupos'], ids))
        else:
            checks = case['comprobaciones_estructurales']
            negative = [c for c in checks if (c['tipo'] == 'articulo' and not c['existe']) or
                        (c['tipo'] == 'feriado' and not c['coincidencias'])]
            row.update(completa=None, evidencia_ausencia_disponible=bool(negative), comprobaciones=checks)
        cases.append(row)
    local = [c for c in cases if c['tipo'] == 'evidencia_local']
    global_cases = [c for c in cases if c['tipo'] == 'ausencia_global']
    return {'version': 1, 'alcance': 'Cobertura de fuentes e inventarios; no exactitud de respuestas del modelo.',
            'resumen': {'cobertura_local_antes': sum(c['antes_completa'] for c in local),
                        'cobertura_local_ahora': sum(c['completa'] for c in local), 'denominador_local': len(local),
                        'ausencias_con_inventario': sum(c['evidencia_ausencia_disponible'] for c in global_cases),
                        'denominador_ausencia': len(global_cases),
                        'mejoran': [c['id'] for c in local if c['completa'] and not c['antes_completa']],
                        'empeoran': [c['id'] for c in local if not c['completa'] and c['antes_completa']],
                        'faltan_fuentes': [c['id'] for c in local if not c['completa']],
                        'promedio_caracteres': round(sum(c['caracteres'] for c in cases) / len(cases)),
                        'max_caracteres': max(c['caracteres'] for c in cases),
                        'unidades_omitidas_presupuesto': sum(len(c['omitidos_por_presupuesto']) for c in run['casos'])},
            'casos': cases}


def markdown(report):
    s = report['resumen']
    lines = ['# Recuperación mejorada: comparación con la primera corrida', '',
             f"La cobertura completa de fuentes pasa de **{s['cobertura_local_antes']}/45 a {s['cobertura_local_ahora']}/45 (95,56%)**. Las cinco consultas de ausencia tienen ahora evidencia estructural obtenida del inventario completo.", '',
             '**No se ha ejecutado Qwen. Estos números no son exactitud de respuestas.** Las 50 preguntas se están utilizando para desarrollo; este resultado no constituye una evaluación independiente de generalización.', '',
             '## Cambios', '',
             '- Citas explícitas: buscar documento y número de artículo en el inventario, además de E5.',
             '- Preguntas compuestas: buscar las partes por separado y añadir sus dos primeros resultados a los cinco de la consulta original.',
             '- Remisiones: añadir artículos mencionados en las unidades seleccionadas, con un solo salto. No confundir referencias a Estatutos con artículos del reglamento.',
             '- Ausencia: conservar el inventario completo consultado y el hash del PDF como evidencia. La afirmación se limita a las copias del corpus.', '',
             f"Mejoran P{s['mejoran']}; no empeora ninguna pregunta previamente cubierta. Quedan sin alguna fuente de la pauta P{s['faltan_fuentes']}.", '',
             '## Casos pendientes', '',
             '- **P34:** se recupera RG art. 31, que contiene el derecho a solicitar suspensión, la autoridad y el plazo. Falta RI-FI art. 25, incluido en la pauta como contexto adicional. No corresponde concluir automáticamente que una futura respuesta sea incorrecta.',
             '- **P38:** se recupera RG art. 23 para escala y aprobación, pero falta RI-FI art. 2 para fundamentar la aplicación en Ingeniería. La parte «se aplica en Ingeniería» pierde contexto al separarse; hay además resultados redundantes del anexo. Es una limitación real de esta descomposición heurística.', '',
             'Se conserva este resultado sin insertar manualmente artículos desde la pauta. Una próxima variante puede preservar mejor el contexto compartido y diversificar fuentes; deberá registrarse como otra corrida.', '',
             '## Tamaño y controles', '',
             f"Contexto medio: {s['promedio_caracteres']} caracteres; máximo: {s['max_caracteres']}. Se omitieron {s['unidades_omitidas_presupuesto']} unidades por presupuesto. Se limita a 14 unidades y 20.000 caracteres de texto documental; los inventarios se contabilizan adicionalmente. No se recortan unidades.", '',
             'Todavía falta medir el presupuesto con el tokenizador de Qwen. La comparación no mantiene el mismo tamaño de contexto entre recuperadores: v2 agrega evidencia a v1. Para comparar prompts, ambas variantes de prompt deben recibir exactamente los mismos contextos congelados.', '',
             '## Detalle de las 50 preguntas', '',
             '| Nº | Cobertura anterior | Cobertura actual | Fuentes ausentes de la pauta |', '|---:|---|---|---|']
    for c in report['casos']:
        if c['completa'] is None:
            lines.append(f"| {c['id']} | Sin evidencia global | Inventario comprobado | — |")
        else:
            missing = '; '.join(' o '.join(g) for g in c['grupos_faltantes']) or '—'
            lines.append(f"| {c['id']} | {'Completa' if c['antes_completa'] else 'Incompleta'} | {'Completa' if c['completa'] else 'Incompleta'} | {missing} |")
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corrida', type=Path, default=Path(__file__).parent / 'resultados/e5_estructurado_v2')
    args = parser.parse_args()
    folder = Path(__file__).parent
    manifest = read(args.corrida / 'manifiesto.json')
    for name, expected in manifest['artefactos_sha256'].items():
        require(sha(args.corrida / name) == expected, 'Artefacto alterado: ' + name)
    corpus_path = ROOT / 'Deliverable2/corpus/generado/corpus.json'
    rubric_path = folder / 'pauta_evidencia.json'
    rubric = read(rubric_path)
    require(sha(corpus_path) == rubric['corpus_sha256'], 'Corpus alterado')
    require(sha(ROOT / 'Deliverable2/evaluacion/referencias.json') == rubric['referencias_sha256'], 'Referencias alteradas')
    report = evaluate(read(args.corrida / 'recuperacion.json'), rubric, read(corpus_path),
                      read(folder / 'resultados/e5_top5_v1/evaluacion_recuperacion.json'))
    report['procedencia_sha256'] = {'corrida': sha(args.corrida / 'recuperacion.json'), 'pauta': sha(rubric_path), 'evaluador': sha(__file__)}
    write(args.corrida / 'evaluacion_recuperacion.json', report)
    (args.corrida / 'REPORTE.md').write_text(markdown(report), encoding='utf-8')
    print(report['resumen'])


if __name__ == '__main__':
    main()
