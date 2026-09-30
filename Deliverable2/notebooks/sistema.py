"""RAG consultable y comparación emparejada; nunca carga respuestas de referencia."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import time
from datetime import datetime, timezone

import numpy as np
from experimento import digest, evidence, messages, atomic_json, load_checkpoint, stop_reason
from recuperador_portable import POLICY, subqueries, make_contexts, rank_vectors

CONDICIONES = ('baseline_directo', 'rag_estructurado')
BASELINE_SYSTEM = (
    "Eres un asistente experto en la normativa de pregrado de la Facultad de "
    "Ingeniería de la Universidad de Concepción. Responde de forma breve, con el "
    "dato exacto y citando el artículo correspondiente (por ejemplo: 'Art. 8'). "
    "Si no tienes la información, di explícitamente que no está en la normativa."
)


def configure_e5_tokenizer(encoder, tokenizer_path, fragments, expected_sha256, diagnostic_path):
    """Usa el JSON canónico y verifica IDs completos, no solo longitudes."""
    import importlib.metadata
    from tokenizers import Tokenizer
    from transformers import XLMRobertaTokenizerFast

    tokenizer_path = Path(tokenizer_path)
    actual_sha = hashlib.sha256(tokenizer_path.read_bytes()).hexdigest()
    report = {'archivo_sha256': actual_sha, 'archivo_sha256_esperado': expected_sha256,
              'clase_cargada_inicialmente': type(encoder.tokenizer).__name__,
              'versiones': {n: importlib.metadata.version(n) for n in
                           ('transformers', 'tokenizers', 'sentence-transformers')},
              'fragmentos': len(fragments), 'diferencias': [], 'diferencias_iniciales': []}
    if actual_sha != expected_sha256:
        report['estado'] = 'archivo_distinto'
        atomic_json(diagnostic_path, report)
        raise ValueError(f'El archivo del tokenizador E5 no corresponde al corpus. Diagnóstico: {diagnostic_path}')

    raw = Tokenizer.from_file(str(tokenizer_path))
    raw.no_truncation()
    raw.no_padding()
    canonical = XLMRobertaTokenizerFast(tokenizer_file=str(tokenizer_path), model_max_length=512)
    for fragment in fragments:
        text = fragment['texto_embedding']
        raw_ids = raw.encode(text, add_special_tokens=True).ids
        ids = canonical(text, add_special_tokens=True, truncation=False, padding=False)['input_ids']
        if len(ids) != fragment['tokens_e5'] or ids != raw_ids or len(ids) > 512:
            report['diferencias'].append({'id': fragment['id'], 'esperado': fragment['tokens_e5'],
                                          'real': len(ids), 'json_canonico': len(raw_ids),
                                          'ids_identicos_al_json': ids == raw_ids})
        try:
            initial_ids = encoder.tokenizer(text, add_special_tokens=True, truncation=False,
                                            padding=False)['input_ids']
            if initial_ids != ids:
                report['diferencias_iniciales'].append({'id': fragment['id'],
                                                       'inicial': len(initial_ids), 'canonico': len(ids)})
        except (ValueError, TypeError, AttributeError) as exc:
            report['error_tokenizador_inicial'] = str(exc)
    report['max_tokens'] = max((f['tokens_e5'] for f in fragments), default=0)
    if not fragments or report['diferencias']:
        report['estado'] = 'conteo_o_ids_incompatibles'
        atomic_json(diagnostic_path, report)
        raise ValueError('El tokenizador canónico E5 difiere del corpus; no se truncarán ni reescribirán fragmentos. '
                         f'Diferencias: {report["diferencias"][:5]}. Diagnóstico: {diagnostic_path}')
    # El mismo tokenizer validado debe ser el que utilice SentenceTransformer.encode.
    encoder.tokenizer = canonical
    report['estado'] = 'OK'
    report['clase_utilizada'] = type(encoder.tokenizer).__name__
    atomic_json(diagnostic_path, report)
    return report


def encode_checked(encoder, texts):
    lengths = [len(encoder.tokenizer(t, truncation=False, padding=False)['input_ids']) for t in texts]
    if not texts or max(lengths) > 512:
        raise ValueError('E5 admite hasta 512 tokens por entrada; no se truncará la pregunta ni el corpus.')
    return np.asarray(encoder.encode(texts, normalize_embeddings=True, batch_size=16,
                                    show_progress_bar=False), dtype=np.float32)


class LiveRetriever:
    def __init__(self, corpus, fragments, encoder):
        self.corpus, self.fragments, self.encoder = corpus, fragments, encoder
        # Se reconstruye el índice desde los fragmentos, no desde respuestas guardadas.
        self.vectors = encode_checked(encoder, [f['texto_embedding'] for f in fragments])
        rank_vectors(self.vectors, self.vectors[:1])  # valida normalización/valores finitos
        self.index_sha256 = hashlib.sha256(self.vectors.tobytes()).hexdigest()

    def retrieve(self, question, question_id=1, category='nueva'):
        question = question.strip()
        if not question:
            raise ValueError('Escribe una pregunta.')
        start = time.perf_counter()
        parts = subqueries(question)
        query_vectors = encode_checked(self.encoder, ['query: ' + s for s in [question] + parts])
        scores, orders = rank_vectors(self.vectors, query_vectors)
        rankings = [[{'fragmento_id': self.fragments[int(fi)]['id'],
                      'unidad_id': self.fragments[int(fi)]['unidad_id'],
                      'similitud_coseno': float(scores[i, fi])} for fi in order]
                    for i, order in enumerate(orders)]
        contexts = make_contexts(question, self.corpus,
                                 [r['unidad_id'] for r in rankings[0]],
                                 [[r['unidad_id'] for r in ranking] for ranking in rankings[1:]])
        # Evitar una omisión silenciosa incluso si las unidades restantes caben en Qwen.
        if contexts['omitidos_por_presupuesto']:
            raise ValueError('La recuperación excedió el presupuesto de unidades/caracteres; no se generarán respuestas con evidencia omitida.')
        case = {'id': question_id, 'pregunta': question, 'categoria': category,
                'ranking_original': rankings[0],
                'subconsultas': [{'texto': p, 'ranking': r} for p, r in zip(parts, rankings[1:])], **contexts}
        return case, time.perf_counter() - start


def comparison_tasks(cases, tokenizer, max_context=8192, max_new=1024):
    tasks = []
    for case in cases:
        for variant in CONDICIONES:
            chat = ([{'role': 'system', 'content': BASELINE_SYSTEM},
                     {'role': 'user', 'content': case['pregunta']}]
                    if variant == 'baseline_directo' else messages(case, variant))
            prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True, enable_thinking=False)
            count = len(tokenizer(prompt, add_special_tokens=False, truncation=False)['input_ids'])
            if count + max_new + 64 > max_context:
                raise ValueError(f'P{case["id"]} / {variant}: no cabe sin truncar. No se generó ninguna respuesta del lote.')
            tasks.append({'pregunta_id': case['id'], 'pregunta': case['pregunta'], 'categoria': case['categoria'],
                          'variante': variant, 'mensajes': chat, 'prompt': prompt, 'tokens_entrada': count,
                          'prompt_sha256': digest(prompt),
                          'evidencia_sha256': digest('' if variant == 'baseline_directo' else evidence(case))})
    return tasks


def save_fixed(path, value):
    path = Path(path)
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8')) != value:
            raise ValueError('Archivo de corrida incompatible: ' + str(path))
    else:
        atomic_json(path, value)


def prepare_run(questions, retriever, tokenizer, settings, output_root):
    if not questions or len({q['id'] for q in questions}) != len(questions):
        raise ValueError('Se requieren preguntas con identificadores únicos.')
    cases, elapsed = [], {}
    for q in questions:
        case, seconds = retriever.retrieve(q['pregunta'], q['id'], q.get('categoria', 'nueva'))
        cases.append(case)
        elapsed[str(q['id'])] = round(seconds, 6)
    tasks = comparison_tasks(cases, tokenizer, settings['max_context_tokens'], settings['generacion']['max_new_tokens'])
    payload = {'version': 1, 'corpus_sha256': digest(retriever.corpus),
               'fragmentos_sha256': digest(retriever.fragments), 'casos': cases}
    config = {**settings, 'protocolo': 'rag-consultable-baseline-v1', 'variantes': list(CONDICIONES),
              'politica_recuperacion': POLICY, 'indice_sha256': retriever.index_sha256,
              'payload_sha256': digest(payload), 'prompts_sha256': digest(tasks),
              'casos': [c['id'] for c in cases]}
    folder = Path(output_root) / ('comparacion_' + digest(config)[:16])
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'respuestas').mkdir(exist_ok=True)
    save_fixed(folder / 'configuracion.json', config)
    save_fixed(folder / 'evidencia.json', {'origen': payload, 'casos_seleccionados': config['casos']})
    save_fixed(folder / 'prompts.json', tasks)
    # Los tiempos no forman parte de la identidad; al reanudar se conserva la primera recuperación.
    if not (folder / 'tiempos_recuperacion.json').exists():
        atomic_json(folder / 'tiempos_recuperacion.json', elapsed)
    return folder, config, cases, tasks


class QwenGenerator:
    def __init__(self, model, tokenizer, generation):
        self.model, self.tokenizer, self.generation = model, tokenizer, generation

    def __call__(self, task, seed):
        import torch
        from transformers import set_seed
        set_seed(seed)
        inputs = self.tokenizer(task['prompt'], return_tensors='pt', add_special_tokens=False,
                                truncation=False).to('cuda:0')
        if inputs['input_ids'].shape[1] != task['tokens_entrada']:
            raise ValueError('El prompt cambió después de medir su presupuesto.')
        eos = self.model.generation_config.eos_token_id
        if eos is None:
            eos = self.tokenizer.eos_token_id
        if eos is None:
            raise ValueError('Falta token de fin de respuesta.')
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        start = time.perf_counter()
        with torch.inference_mode():
            result = self.model.generate(**inputs, **self.generation, eos_token_id=eos,
                                         pad_token_id=self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else self.tokenizer.eos_token_id,
                                         use_cache=True)
        torch.cuda.synchronize()
        seconds = time.perf_counter() - start
        token_ids = result[0, inputs['input_ids'].shape[1]:].detach().cpu().tolist()
        answer = self.tokenizer.decode(token_ids, skip_special_tokens=True).strip()
        reason = stop_reason(token_ids, eos, self.generation['max_new_tokens'])
        return {'respuesta_modelo': answer, 'ids_tokens_salida': token_ids,
                'salida_con_tokens_especiales': self.tokenizer.decode(token_ids, skip_special_tokens=False),
                'tokens_salida': len(token_ids), 'motivo_parada': reason, 'posible_corte': reason == 'limite_tokens',
                'thinking_inesperado': '<think>' in answer, 'segundos': round(seconds, 4),
                'pico_memoria_gpu_gb': round(torch.cuda.max_memory_allocated()/2**30, 4)}


def run_tasks(folder, config, cases, tasks, generate):
    folder = Path(folder)
    timing = json.loads((folder / 'tiempos_recuperacion.json').read_text())
    task_map = {(t['pregunta_id'], t['variante']): t for t in tasks}
    rows = []
    for i, case in enumerate(cases):
        offset = i % len(CONDICIONES)
        for variant in CONDICIONES[offset:] + CONDICIONES[:offset]:
            task = task_map[case['id'], variant]
            checkpoint = folder / 'respuestas' / f'P{case["id"]:02}_{variant}.json'
            row = load_checkpoint(checkpoint, digest(config), task)
            cached = row is not None
            if row is None:
                seed = config['semilla_base'] + case['id']
                result = generate(task, seed)
                row = {k: task[k] for k in ('pregunta_id', 'pregunta', 'categoria', 'variante', 'tokens_entrada', 'prompt_sha256', 'evidencia_sha256')}
                retrieval_time = 0.0 if variant == 'baseline_directo' else timing[str(case['id'])]
                row.update(result, run_hash=digest(config), respuesta_sha256=digest(result['respuesta_modelo']),
                           semilla=seed, fecha_utc=datetime.now(timezone.utc).isoformat(),
                           segundos_recuperacion=retrieval_time,
                           segundos_consulta=round(retrieval_time + result['segundos'], 4))
                atomic_json(checkpoint, row)
            rows.append(row)
            print(f'{len(rows)}/{len(tasks)} | P{case["id"]:02} | {variant} | '
                  f'{"checkpoint conservado" if cached else "generada ahora"} | {row["motivo_parada"]}', flush=True)
    return rows


def export_run(folder, config, tasks):
    folder = Path(folder)
    rows = []
    for task in tasks:
        row = load_checkpoint(folder / 'respuestas' / f'P{task["pregunta_id"]:02}_{task["variante"]}.json', digest(config), task)
        if row is not None:
            rows.append(row)
    fields = ['pregunta_id', 'pregunta', 'categoria', 'variante', 'respuesta_modelo', 'tokens_entrada', 'tokens_salida',
              'motivo_parada', 'posible_corte', 'thinking_inesperado', 'segundos', 'segundos_recuperacion',
              'segundos_consulta', 'pico_memoria_gpu_gb', 'semilla', 'prompt_sha256', 'evidencia_sha256', 'respuesta_sha256', 'run_hash']
    for variant in CONDICIONES:
        with (folder / (variant + '.csv')).open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(r for r in rows if r['variante'] == variant)
    atomic_json(folder / 'resumen_tecnico.json', {'respuestas_esperadas': len(tasks), 'respuestas_guardadas': len(rows),
                'corrida_completa': len(rows) == len(tasks), 'no_es_evaluacion_semantica': True,
                'posibles_cortes': sum(r['posible_corte'] for r in rows)})
    return Path(shutil.make_archive(str(folder), 'zip', root_dir=folder))


def show_comparison(rows, cases):
    from IPython.display import HTML, display
    import html
    for case in cases:
        selected = {r['variante']: r for r in rows if r['pregunta_id'] == case['id']}
        cells = []
        for v in CONDICIONES:
            r = selected[v]
            cells.append('<td style="vertical-align:top;width:50%;white-space:pre-wrap">' +
                         html.escape(r['respuesta_modelo']) + '<hr>' +
                         html.escape(f'Parada: {r["motivo_parada"]} | Generación: {r["segundos"]:.2f} s | Recuperación: {r["segundos_recuperacion"]:.2f} s') + '</td>')
        display(HTML('<h3>' + html.escape(case['pregunta']) + '</h3><table><tr><th>Sin documentos</th><th>RAG estructurado</th></tr><tr>' + ''.join(cells) + '</tr></table>'))
        display(HTML('<details><summary>Fragmentos exactos enviados únicamente a RAG</summary><pre style="white-space:pre-wrap">' + html.escape(evidence(case)) + '</pre></details>'))
