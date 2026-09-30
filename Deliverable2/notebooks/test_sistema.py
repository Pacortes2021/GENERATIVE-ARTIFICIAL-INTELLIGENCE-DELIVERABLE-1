import ast
import base64
import gzip
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import types
import unittest
from unittest.mock import patch

import nbformat
import numpy as np

from crear_sistema import portable_source
from diagnostico import read_run_zip
from experimento import digest, evidence, messages
from sistema import (BASELINE_SYSTEM, LiveRetriever, QwenGenerator, comparison_tasks, encode_checked,
                     prepare_run, run_tasks, export_run)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class ChatTokenizer:
    def apply_chat_template(self, chat, **kwargs):
        assert kwargs['enable_thinking'] is False
        return json.dumps(chat, ensure_ascii=False)

    def __call__(self, text, **kwargs):
        assert kwargs['truncation'] is False
        return {'input_ids': list(range(max(1, len(text) // 8)))}


class ReplayEncoder:
    """Vectores reales ya guardados, para verificar equivalencia sin descargar modelos."""
    def __init__(self, fragments, corpus, base, improved):
        self.tokenizer = lambda text, **kwargs: {'input_ids': [1] * 20}
        self.docs = np.load(base / 'vectores_documentos.npy', allow_pickle=False)
        self.map = {f['texto_embedding']: v for f, v in zip(fragments, self.docs)}
        old = json.loads((base / 'recuperacion.json').read_text())
        vectors = np.load(base / 'vectores_consultas.npy', allow_pickle=False)
        self.map.update({'query: ' + c['pregunta']: v for c, v in zip(old['casos'], vectors)})
        parts = json.loads((improved / 'subconsultas.json').read_text())
        vectors = np.load(improved / 'vectores_subconsultas.npy', allow_pickle=False)
        self.map.update({'query: ' + s: v for s, v in zip(parts, vectors)})
        self.calls = []

    def encode(self, texts, **kwargs):
        self.calls.append(list(texts))
        return np.array([self.map[t] for t in texts])


class SystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = ROOT / 'Deliverable2/corpus/generado'
        cls.corpus = json.loads((data / 'corpus.json').read_text())
        cls.fragments = json.loads((data / 'fragmentos_busqueda.json').read_text())
        cls.base = ROOT / 'Deliverable2/recuperacion/resultados/e5_top5_v1'
        cls.improved = ROOT / 'Deliverable2/recuperacion/resultados/e5_estructurado_v2'
        cls.previous = json.loads((cls.improved / 'recuperacion.json').read_text())['casos']
        cls.nb = nbformat.read(HERE / 'Deliverable2_Sistema_RAG_Colab.ipynb', as_version=4)

    def retriever(self):
        return LiveRetriever(self.corpus, self.fragments,
                             ReplayEncoder(self.fragments, self.corpus, self.base, self.improved))

    def test_packaged_retriever_is_literal_current_source(self):
        self.assertEqual((HERE / 'recuperador_portable.py').read_text(), portable_source())

    def test_dynamic_retrieval_reproduces_all_50_saved_contexts(self):
        retriever = self.retriever()
        for original in self.previous:
            case, seconds = retriever.retrieve(original['pregunta'], original['id'], original['categoria'])
            self.assertEqual(case['contextos'], original['contextos'])
            self.assertEqual(case['contextos_inventario'], original['contextos_inventario'])
            self.assertGreaterEqual(seconds, 0)
        self.assertEqual(len(retriever.encoder.calls), 51, 'El índice se crea una vez y cada consulta se codifica de nuevo.')

    def test_unseen_question_is_encoded_not_looked_up_in_exam(self):
        r = self.retriever()
        unseen = 'Necesito conocer el artículo 33 del RI-FI.'
        # Vector sintético solo para comprobar el flujo de una pregunta fuera del test.
        r.encoder.map['query: ' + unseen] = r.vectors[0]
        case, _ = r.retrieve(unseen)
        self.assertEqual(r.encoder.calls[-1], ['query: ' + unseen])
        self.assertEqual(case['contextos'][0]['unidad_id'], 'RI-FI-ART-033')

    def test_baseline_uses_exact_e1_system_and_no_evidence(self):
        nb = json.loads((ROOT / 'Deliverable1/notebooks/baseline_normativa_ingenieria.ipynb').read_text())
        systems = []
        for c in nb['cells']:
            if c['cell_type'] != 'code' or 'SYSTEM = (' not in ''.join(c['source']): continue
            for node in ast.parse(''.join(c['source'])).body:
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SYSTEM' for t in node.targets):
                    systems.append(ast.literal_eval(node.value))
        self.assertEqual(systems, [BASELINE_SYSTEM])
        case = self.previous[24]
        baseline, rag = comparison_tasks([case], ChatTokenizer())
        self.assertEqual(baseline['mensajes'], [{'role':'system','content':BASELINE_SYSTEM}, {'role':'user','content':case['pregunta']}])
        self.assertEqual(baseline['evidencia_sha256'], digest(''))
        self.assertEqual(rag['mensajes'], messages(case, 'rag_estructurado'))
        self.assertNotIn('EVIDENCIA DE ESTA CONSULTA', baseline['prompt'])

    def test_e5_and_qwen_budgets_refuse_truncation(self):
        r = self.retriever()
        r.encoder.tokenizer = lambda text, **kwargs: {'input_ids': [1]*513}
        with self.assertRaisesRegex(ValueError, '512'):
            r.retrieve('Una consulta demasiado extensa')
        with self.assertRaisesRegex(ValueError, 'no cabe sin truncar'):
            comparison_tasks([self.previous[24]], ChatTokenizer(), max_context=64, max_new=32)

    def test_p25_articles_complete_in_both_historical_prompts(self):
        tasks = json.loads((ROOT/'Deliverable2/resultados/qwen3_4b_4adccec813c53d7f/original/prompts.json').read_text())
        units = {u['id']:u for u in self.corpus['unidades']}
        for t in tasks:
            if t['pregunta_id'] == 25 and t['variante'] in ['rag_simple','rag_estructurado']:
                for uid in ['RI-FI-ART-007','RI-FI-ART-009']:
                    self.assertIn(units[uid]['texto'], t['mensajes'][-1]['content'])

    def test_generation_resume_export_and_new_question_isolation(self):
        r = self.retriever()
        questions = [{k:c[k] for k in ['id','pregunta','categoria']} for c in self.previous[:2]]
        settings = {'max_context_tokens':8192, 'generacion':{'max_new_tokens':1024}, 'semilla_base':2026}
        calls = []
        def generate(task, seed):
            calls.append((task['pregunta_id'], task['variante'], seed))
            return {'respuesta_modelo':'Salida simulada', 'tokens_salida':2, 'motivo_parada':'eos',
                    'posible_corte':False,'thinking_inesperado':False,'segundos':0.1,'pico_memoria_gpu_gb':0.0}
        with tempfile.TemporaryDirectory() as tmp:
            folder, config, cases, tasks = prepare_run(questions, r, ChatTokenizer(), settings, tmp)
            rows = run_tasks(folder, config, cases, tasks, generate)
            self.assertEqual(calls, [(1,'baseline_directo',2027),(1,'rag_estructurado',2027),
                                    (2,'rag_estructurado',2028),(2,'baseline_directo',2028)])
            folder2, config2, cases2, tasks2 = prepare_run(questions, r, ChatTokenizer(), settings, tmp)
            self.assertEqual(folder, folder2)
            run_tasks(folder2, config2, cases2, tasks2, generate)
            self.assertEqual(len(calls),4)
            archive = export_run(folder,config,tasks)
            loaded, evidence_cases, loaded_config = read_run_zip(archive)
            self.assertEqual(len(loaded),4)
            self.assertEqual(loaded_config,config)
            self.assertEqual(evidence_cases,cases)
            other, _, _, _ = prepare_run(questions[1:],r,ChatTokenizer(),settings,tmp)
            self.assertNotEqual(other,folder)
            self.assertTrue((folder/'baseline_directo.csv').exists())
            self.assertTrue(all(row['segundos_recuperacion']==0 for row in rows if row['variante']=='baseline_directo'))
            # Un checkpoint editado no se acepta como salida genuina.
            file = next((folder/'respuestas').glob('*.json'))
            bad=json.loads(file.read_text());bad['respuesta_modelo']='alterada';file.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'alterado'):
                run_tasks(folder,config,cases,tasks,generate)

    def test_notebook_bundle_is_self_contained_and_has_no_gold(self):
        nbformat.validate(self.nb)
        for c in self.nb.cells:
            if c.cell_type=='code':
                compile(c.source,'cell','exec')
                self.assertFalse(c.outputs)
        cell=next(c for c in self.nb.cells if c.cell_type=='code' and 'BUNDLE_B64 = (' in c.source)
        tree=ast.parse(cell.source)
        packed=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='BUNDLE_B64')
        sources=json.loads(gzip.decompress(base64.b64decode(packed)))
        for n in ['sistema.py','experimento.py','recuperador_portable.py']:
            self.assertEqual(sources[n],(HERE/n).read_text())
            compile(sources[n],n,'exec')
        qs=json.loads(sources['preguntas.json'])
        self.assertEqual(len(qs),50)
        self.assertTrue(all(set(q)=={'id','pregunta','categoria'} for q in qs))
        self.assertNotIn('referencias.json',sources)
        self.assertNotIn('veredictos.json',sources)
        self.assertTrue(any('EJECUTAR_LOTE_50 = False' in c.source for c in self.nb.cells))
        self.assertTrue(any('PREGUNTA = ""' in c.source for c in self.nb.cells))

    def test_corpus_cell_runs_in_fresh_process_without_native_ml_imports(self):
        cell=next(c for c in self.nb.cells if c.cell_type=='code' and 'BUNDLE_B64 = (' in c.source)
        with tempfile.TemporaryDirectory() as tmp:
            script=Path(tmp)/'check_bootstrap.py'
            script.write_text(cell.source + '''
assert not {'numpy', 'torch', 'transformers', 'sentence_transformers'} & set(sys.modules)
assert len(CORPUS['unidades']) == 197 and len(FRAGMENTS) == 201 and len(QUESTIONS) == 50
for name, expected in SOURCE_HASHES.items():
    assert hashlib.sha256((WORKDIR / name).read_bytes()).hexdigest() == expected
print('CARGA_VERIFICADA_SIN_MODELOS')
''')
            result=subprocess.run([sys.executable,str(script)],cwd=tmp,text=True,capture_output=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('Corpus listo:',result.stdout)
            self.assertIn('CARGA_VERIFICADA_SIN_MODELOS',result.stdout)
        self.assertLess(max(map(len,cell.source.splitlines())),1000,'Evitar líneas gigantes en Colab')
        self.assertLess(len(cell.source.encode()),300000)

    def test_corrupted_compressed_bundle_is_rejected_before_writing_modules(self):
        cell=next(c for c in self.nb.cells if c.cell_type=='code' and 'BUNDLE_B64 = (' in c.source)
        # Una alteración del archivo debe fallar, no producir módulos incompletos.
        source=cell.source.replace("packed = base64.b64decode(BUNDLE_B64, validate=True)",
                                   "packed = base64.b64decode(BUNDLE_B64, validate=True) + b'alterado'")
        with tempfile.TemporaryDirectory() as tmp:
            script=Path(tmp)/'check_corruption.py';script.write_text(source)
            result=subprocess.run([sys.executable,str(script)],cwd=tmp,text=True,capture_output=True,timeout=30)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('paquete comprimido está alterado',result.stderr)
            self.assertFalse(list(Path(tmp).glob('genia_runtime_*')))

    def test_qwen_adapter_uses_only_new_tokens_and_records_stop(self):
        import torch
        class Inputs(dict):
            def to(self, device): return self
        class Tokenizer:
            pad_token_id = 0
            eos_token_id = 9
            def __call__(self, prompt, **kwargs):
                assert kwargs['truncation'] is False
                return Inputs(input_ids=torch.tensor([[1, 2, 3]]))
            def decode(self, tokens, **kwargs):
                assert tokens == [7, 9], 'No decodificar el prompt como respuesta'
                return 'Respuesta de prueba'
        model = types.SimpleNamespace(generation_config=types.SimpleNamespace(eos_token_id=[9]),
                                      generate=lambda **kwargs: torch.tensor([[1, 2, 3, 7, 9]]))
        fake_torch = types.SimpleNamespace(inference_mode=torch.inference_mode,
            cuda=types.SimpleNamespace(synchronize=lambda:None, reset_peak_memory_stats=lambda:None,
                                       max_memory_allocated=lambda:0))
        seeds=[]
        with patch.dict(sys.modules, {'torch':fake_torch, 'transformers':types.SimpleNamespace(set_seed=seeds.append)}):
            result=QwenGenerator(model,Tokenizer(),{'max_new_tokens':2})({'prompt':'x','tokens_entrada':3},2027)
        self.assertEqual(seeds,[2027])
        self.assertEqual(result['tokens_salida'],2)
        self.assertEqual(result['motivo_parada'],'eos')
        self.assertFalse(result['posible_corte'])

    def test_partial_export_after_generation_failure(self):
        r=self.retriever()
        settings={'max_context_tokens':8192,'generacion':{'max_new_tokens':1024},'semilla_base':2026}
        with tempfile.TemporaryDirectory() as tmp:
            folder,config,cases,tasks=prepare_run([self.previous[0]],r,ChatTokenizer(),settings,tmp)
            def fail_second(task,seed):
                if task['variante']=='rag_estructurado': raise RuntimeError('Interrupción simulada')
                return {'respuesta_modelo':'primera','motivo_parada':'eos','posible_corte':False,
                        'segundos':0.1,'tokens_salida':1,'thinking_inesperado':False}
            with self.assertRaisesRegex(RuntimeError,'Interrupción'):
                run_tasks(folder,config,cases,tasks,fail_second)
            loaded,_,_=read_run_zip(export_run(folder,config,tasks))
            self.assertEqual(len(loaded),1)
            summary=json.loads((folder/'resumen_tecnico.json').read_text())
            self.assertFalse(summary['corrida_completa'])


if __name__=='__main__': unittest.main()
