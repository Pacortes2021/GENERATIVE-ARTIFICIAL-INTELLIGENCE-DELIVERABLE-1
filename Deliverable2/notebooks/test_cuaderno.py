import copy
import json
from pathlib import Path
import tempfile
import types
import unittest

import nbformat

from experimento import (VARIANTES, messages, evidence, digest, make_tasks,
                         stop_reason, atomic_json, load_checkpoint)

HERE = Path(__file__).parent


class NotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb = nbformat.read(HERE / 'Deliverable2_RAG_2_variantes_Colab.ipynb', as_version=4)
        data_cell = next(c.source for c in cls.nb.cells if c.cell_type == 'code' and 'PAYLOAD_JSON =' in c.source)
        scope = {}
        exec(data_cell, scope)
        cls.cases = scope['PAYLOAD']['casos']

    def test_notebook_schema_and_all_cells_compile(self):
        nbformat.validate(self.nb)
        for i, cell in enumerate(self.nb.cells):
            if cell.cell_type == 'code':
                compile(cell.source, f'cell{i}', 'exec')
                self.assertEqual(cell.outputs, [])
                self.assertIsNone(cell.execution_count)

    def test_all_variants_share_target_evidence(self):
        for case in self.cases:
            last = [messages(case, variant)[-1] for variant in VARIANTES]
            self.assertEqual(last[0], last[1])

    def test_only_two_variants_without_demonstrations(self):
        self.assertEqual(VARIANTES, ('rag_simple', 'rag_estructurado'))
        for case in self.cases:
            for variant in VARIANTES:
                self.assertEqual([m['role'] for m in messages(case, variant)], ['system', 'user'])
        with self.assertRaises(ValueError):
            messages(self.cases[0], 'rag_estructurado_fewshot')

    def test_payload_excludes_reference_answers_and_verdicts(self):
        forbidden = {'respuesta_referencia', 'correcta', 'grupos_esperados', 'nota_evaluacion', 'respuesta_esperada'}
        def inspect(obj):
            if isinstance(obj, dict):
                self.assertFalse(forbidden.intersection(obj))
                for value in obj.values(): inspect(value)
            elif isinstance(obj, list):
                for value in obj: inspect(value)
        inspect(self.cases)

    def test_stop_reason_eos_at_limit_is_not_cut(self):
        self.assertEqual(stop_reason([1, 2, 9], [9], 3), 'eos')
        self.assertEqual(stop_reason([1, 2, 3], [9], 3), 'limite_tokens')
        self.assertEqual(stop_reason([1], [9], 3), 'otro')

    def test_budget_failure_does_not_truncate(self):
        class FakeTokenizer:
            def apply_chat_template(self, chat, **kwargs):
                assert kwargs['enable_thinking'] is False
                return str(chat)
            def __call__(self, text, **kwargs):
                assert kwargs['truncation'] is False
                return {'input_ids': list(range(500))}
        with self.assertRaisesRegex(ValueError, 'no caben sin truncar'):
            make_tasks(self.cases[:1], FakeTokenizer(), 600, 200)

    def test_checkpoint_resume_and_mutations(self):
        task = {'prompt_sha256': 'p', 'evidencia_sha256': 'e'}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'answer.json'
            self.assertIsNone(load_checkpoint(path, 'r', task))
            row = dict(task, run_hash='r', respuesta_modelo='bien', respuesta_sha256=digest('bien'))
            atomic_json(path, row)
            self.assertEqual(load_checkpoint(path, 'r', task), row)
            with self.assertRaisesRegex(ValueError, 'incompatible'):
                load_checkpoint(path, 'otra corrida', task)
            row['respuesta_modelo'] = 'cambiada'
            atomic_json(path, row)
            with self.assertRaisesRegex(ValueError, 'alterado'):
                load_checkpoint(path, 'r', task)

    def test_generation_resume_export_with_simulated_model(self):
        # Simula solo inferencia/GPU: ejecuta las celdas reales de bucle y exportación.
        import torch
        import experimento
        import csv, shutil, time
        from datetime import datetime, timezone
        class Inputs(dict):
            def to(self, device): return self
        class Tokenizer:
            eos_token_id = 9
            pad_token_id = 0
            def __call__(self, text, **kwargs):
                return Inputs(input_ids=torch.tensor([[1, 2, 3]]), attention_mask=torch.ones((1, 3), dtype=torch.long))
            def decode(self, ids, **kwargs): return 'Respuesta simulada [RI-FI-ART-011].'
        class Model:
            calls = 0
            def generate(self, **kwargs):
                self.calls += 1
                return torch.tensor([[1, 2, 3, 7, 9]])
        gpu = types.SimpleNamespace(synchronize=lambda: None, reset_peak_memory_stats=lambda: None,
                                     max_memory_allocated=lambda: 1)
        fake_torch = types.SimpleNamespace(cuda=gpu, inference_mode=torch.inference_mode)
        case = self.cases[0]
        tasks = [dict(pregunta_id=case['id'], pregunta=case['pregunta'], categoria=case['categoria'],
                      variante=v, prompt='prompt-'+v, tokens_entrada=3,
                      prompt_sha256=digest(v), evidencia_sha256=digest(evidence(case))) for v in VARIANTES]
        with tempfile.TemporaryDirectory() as tmp:
            scope = dict(vars(experimento))
            model = Model()
            scope.update(TASKS=tasks, CASES=[case], SEMILLA=2026, RUN_HASH='test', RUN_DIR=Path(tmp)/'run',
                         torch=fake_torch, tokenizer=Tokenizer(), model=model, set_seed=lambda n: None,
                         EOS_IDS=[9], MAX_NEW_TOKENS=5, GENERACION={'max_new_tokens': 5}, time=time,
                         datetime=datetime, timezone=timezone, csv=csv, shutil=shutil)
            scope['RUN_DIR'].mkdir()
            generation = next(c.source for c in self.nb.cells if c.cell_type == 'code' and c.source.startswith('TASK_MAP ='))
            export = next(c.source for c in self.nb.cells if c.cell_type == 'code' and c.source.startswith('rows = []'))
            exec(generation, scope)
            self.assertEqual(model.calls, 2)
            exec(generation, scope)
            self.assertEqual(model.calls, 2, 'No regenerar respuestas al reanudar')
            exec(export, scope)
            summary = json.loads((scope['RUN_DIR'] / 'resumen_tecnico.json').read_text())
            self.assertTrue(summary['corrida_completa'])
            self.assertTrue(Path(scope['ZIP_PATH']).exists())
            for variant in VARIANTES:
                with (scope['RUN_DIR'] / (variant + '.csv')).open(encoding='utf-8-sig') as f:
                    rows = list(csv.DictReader(f))
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['motivo_parada'], 'eos')


if __name__ == '__main__':
    unittest.main()
