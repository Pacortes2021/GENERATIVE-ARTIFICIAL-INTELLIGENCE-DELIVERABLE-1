import copy
from pathlib import Path
import unittest

import numpy as np

from probar_recuperacion import ROOT, read, rank_vectors, sha
from recuperar_mejorado import exact_articles, holiday_inventory, references, subqueries, make_contexts
from evaluar_mejorado import evaluate


class ImprovedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = Path(__file__).parent
        cls.corpus = read(ROOT / 'Deliverable2/corpus/generado/corpus.json')
        cls.experiment = read(cls.folder / 'resultados/e5_estructurado_v2/recuperacion.json')
        cls.parents = {p['id']: p for p in cls.corpus['padres']}
        cls.units = {u['id']: u for u in cls.corpus['unidades']}

    def test_exact_reference_not_in_test_set(self):
        ids, checks = exact_articles('Explícame el artículo 33 del RI-FI.', self.corpus)
        self.assertEqual(ids, ['RI-FI-ART-033'])
        self.assertTrue(checks[0]['existe'])

    def test_ambiguous_document_is_not_guessed(self):
        self.assertEqual(exact_articles('¿Qué dice el artículo 9?', self.corpus), ([], []))

    def test_nonexistent_other_article_uses_full_inventory(self):
        ids, checks = exact_articles('Artículo 999 del Reglamento General', self.corpus)
        self.assertEqual(ids, [])
        self.assertEqual(checks[0]['inventario_numeros'], list(range(1, 61)))
        self.assertFalse(checks[0]['existe'])

    def test_transitory_separate_from_regular(self):
        ids, _ = exact_articles('Artículo 2 transitorio del RG', self.corpus)
        self.assertEqual(ids, ['RG-TRANS-002'])

    def test_actual_holiday_and_out_of_scope_year(self):
        check = holiday_inventory('Calendario 2026, feriado del 18 de septiembre', self.corpus)[0]
        self.assertEqual(check['coincidencias'], ['CAL-2026-S2-09'])
        self.assertEqual(check['eventos_calendario_revisados'], 25)
        self.assertEqual(holiday_inventory('Calendario 2027, feriado del 18 de septiembre', self.corpus), [])

    def test_external_reference_not_assigned_to_regulation(self):
        targets = references(self.units['RG-ART-010'], self.parents, self.units)
        self.assertNotIn('RG-ART-057', targets)

    def test_reference_expansion_and_deduplication(self):
        result = make_contexts('Modificar inscripción', self.corpus, ['RI-FI-ART-009', 'RI-FI-ART-009'], [])
        self.assertEqual([c['unidad_id'] for c in result['contextos']], ['RI-FI-ART-009', 'RI-FI-ART-007', 'RI-FI-ART-008'])
        self.assertEqual(result['contextos'][1]['texto'], self.units['RI-FI-ART-007']['texto'])

    def test_compound_question_unseen_wording(self):
        parts = subqueries('¿Cuándo terminan las clases y cuánto dura la recuperación?')
        self.assertEqual(len(parts), 2)

    def test_saved_rankings_reproducible_from_vectors(self):
        path = self.folder / 'resultados/e5_estructurado_v2'
        docs = np.load(self.folder / 'resultados/e5_top5_v1/vectores_documentos.npy', allow_pickle=False)
        queries = np.load(path / 'vectores_subconsultas.npy', allow_pickle=False)
        texts = read(path / 'subconsultas.json')
        fragments = read(ROOT / 'Deliverable2/corpus/generado/fragmentos_busqueda.json')
        _, order = rank_vectors(docs, queries)
        expected = {t: [fragments[int(i)]['id'] for i in row] for t, row in zip(texts, order)}
        for case in self.experiment['casos']:
            for query in case['subconsultas']:
                self.assertEqual([r['fragmento_id'] for r in query['ranking']], expected[query['texto']])

    def test_artifacts_and_script_match_manifest(self):
        path = self.folder / 'resultados/e5_estructurado_v2'
        manifest = read(path / 'manifiesto.json')
        for name, expected in manifest['artefactos_sha256'].items():
            self.assertEqual(sha(path / name), expected)
        self.assertEqual(sha(self.folder / 'recuperar_mejorado.py'), manifest['script_sha256'])

    def test_tampered_inventory_rejected(self):
        altered = copy.deepcopy(self.experiment)
        altered['casos'][40]['comprobaciones_estructurales'][0]['existe'] = True
        with self.assertRaisesRegex(ValueError, 'alterado'):
            evaluate(altered, read(self.folder / 'pauta_evidencia.json'), self.corpus,
                     read(self.folder / 'resultados/e5_top5_v1/evaluacion_recuperacion.json'))


if __name__ == '__main__':
    unittest.main()
