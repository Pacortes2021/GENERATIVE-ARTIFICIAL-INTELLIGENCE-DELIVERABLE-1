"""Pruebas de integridad y regresiones que afectaban la evaluación. Sin GPU."""
import ast
import copy
import csv
import json
import tempfile
import types
import unittest
from unittest.mock import patch
from pathlib import Path
from .auditoria import ROOT, HERE, read_csv, run, score, aligned_predictions
from .preparar_corpus_v2 import articles


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.q = read_csv(ROOT / 'test_set_50.csv')
        self.r = read_csv(HERE / 'revision_historica.csv')
        self.p = aligned_predictions(self.q, read_csv(HERE / 'resultados_rag_qwen3_4b.csv'), 'prediccion_rag')

    def test_incomplete_answers_do_not_pass(self):
        result = run()
        self.assertEqual(result['rag']['aciertos'], 44)
        self.assertEqual(result['baseline']['aciertos'], 1)
        for question in [24, 25, 36, 38, 40]:
            self.assertIn(question, result['rag']['fallos'])
        self.assertIn(49, result['baseline']['fallos'])

    def test_changed_answer_invalidates_review(self):
        self.p['1'] = 'DATO: 60\nCITA: Art. 11 RI-FI'
        with self.assertRaisesRegex(ValueError, 'cambió'):
            score(self.q, self.p, self.r, 'rag')

    def test_partial_or_duplicate_reviews_rejected(self):
        with self.assertRaises(ValueError):
            score(self.q, self.p, self.r[:-1], 'rag')
        rows = copy.deepcopy(self.r)
        rows[-1] = rows[-2]
        with self.assertRaises(ValueError):
            score(self.q, self.p, rows, 'rag')

    def test_pending_review_rejected(self):
        rows = copy.deepcopy(self.r)
        rows[-1]['abstencion_valida'] = ''
        with self.assertRaises(ValueError):
            score(self.q, self.p, rows, 'rag')

    def test_reordered_predictions_rejected(self):
        raw = read_csv(HERE / 'resultados_rag_qwen3_4b.csv')
        raw[0], raw[1] = raw[1], raw[0]
        with self.assertRaises(ValueError):
            aligned_predictions(self.q, raw, 'prediccion_rag')

    def test_new_run_counts_only_its_reviewed_predictions(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            rows = []
            for r in self.r:
                rows.append({k: r[k] for k in ('sistema', 'id', 'categoria', 'pregunta', 'gold_dato', 'gold_fuente', 'respuesta')})
            with (directory / 'predicciones.csv').open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0])
                writer.writeheader(); writer.writerows(rows)
            with (directory / 'revision_pendiente.csv').open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.r[0])
                writer.writeheader(); writer.writerows(self.r)
            self.assertEqual(run(directory)['rag']['aciertos'], 44)
            rows[0]['respuesta'] = 'Una predicción nueva requiere revisión nueva'
            with (directory / 'predicciones.csv').open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0])
                writer.writeheader(); writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, 'cambió'):
                run(directory)


class CorpusTests(unittest.TestCase):
    def test_cross_reference_is_not_a_new_heading(self):
        text = 'Artículo 1°. Primera regla.\nArtículo 2°. Se aplican las prioridades del\nArtículo 1°, sin excepciones.\nArtículo 3°. Fin.'
        parsed = articles(text, 3)
        self.assertEqual(len(parsed), 3)
        self.assertIn('Artículo 1°, sin excepciones.', parsed[1][1])

    def test_missing_article_fails_loudly(self):
        with self.assertRaises(ValueError):
            articles('Artículo 1°. Texto\nArtículo 3°. Texto', 3)

    def test_actual_corpus_preserves_article_9(self):
        corpus = json.loads((HERE / 'base_conocimiento_v2.json').read_text())
        article9 = [x for x in corpus if x['id'].startswith('RI-FI-9-')]
        self.assertEqual(len(article9), 1)
        self.assertIn('Artículo 7°, ni contravenir', article9[0]['texto'])
        self.assertEqual(len({x['articulo'] for x in corpus if x['id'].startswith('RI-FI-')}), 35)
        self.assertEqual(len({x['articulo'] for x in corpus if x['id'].startswith('RG-')}), 62)

    def test_calendar_unchanged(self):
        old = json.loads((HERE / 'base_conocimiento_udec.json').read_text())
        new = json.loads((HERE / 'base_conocimiento_v2.json').read_text())
        events = lambda cs: [c['texto'] for c in cs if c['fuente'].startswith('Calendario')]
        self.assertEqual(events(old), events(new))


class NotebookTests(unittest.TestCase):
    def test_all_current_cells_parse_and_are_unexecuted(self):
        notebook = json.loads((ROOT / 'rag_normativa_ingenieria_4b.ipynb').read_text())
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                ast.parse(''.join(cell['source']))
                self.assertEqual(cell['outputs'], [])
                self.assertIsNone(cell['execution_count'])


class PromptComparisonTests(unittest.TestCase):
    def test_comparison_uses_same_context_and_never_passes_gold(self):
        from . import pipeline_colab as pipeline
        question = {'id': '24', 'pregunta': 'Pregunta de prueba', 'gold_dato': 'RESPUESTA_RESERVADA'}
        fragments = [{'indice': 0, 'texto': 'Fragmento de prueba', 'similitud': 0.9}]
        fake_torch = types.SimpleNamespace(cuda=types.SimpleNamespace(synchronize=lambda: None))
        with tempfile.TemporaryDirectory() as directory, \
             patch.dict('sys.modules', {'torch': fake_torch}), \
             patch.object(pipeline, 'new_run_dir', return_value=Path(directory)), \
             patch.object(pipeline, 'retrieve', return_value=fragments) as retrieve, \
             patch.object(pipeline, 'generate', return_value={'respuesta': 'Salida de prueba', 'alcanzo_limite_tokens': False}) as generate, \
             patch('builtins.print'):
            pipeline.compare_prompts({'metadata': {}}, [question])
            self.assertEqual(retrieve.call_count, 1)
            self.assertEqual(generate.call_count, 2)
            for call in generate.call_args_list:
                self.assertIs(call.args[3], fragments)
                self.assertEqual(call.args[1], question['pregunta'])
                self.assertNotIn(question['gold_dato'], call.args[2])
            saved = [json.loads(line) for line in (Path(directory) / 'comparacion_prompts.jsonl').read_text().splitlines()]
            self.assertEqual(saved[0]['contextos'], saved[1]['contextos'])
            self.assertEqual({r['prompt_version'] for r in saved}, {'historico', 'completo_v1'})

    def test_invalid_prompt_fails_before_loading_weights(self):
        from .pipeline_colab import load_pipeline
        with self.assertRaisesRegex(ValueError, 'Prompt desconocido'):
            load_pipeline('irrelevante.json', prompt_version='error_de_escritura')


if __name__ == '__main__':
    unittest.main()
