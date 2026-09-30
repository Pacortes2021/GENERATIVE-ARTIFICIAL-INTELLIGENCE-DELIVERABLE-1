import copy
from pathlib import Path
import unittest

import numpy as np

from evaluar_recuperacion import coverage, evaluate
from probar_recuperacion import ROOT, load_inputs, rank_vectors, read, retrieve, sha


class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = Path(__file__).parent / "resultados/e5_top5_v1"
        cls.experiment = read(cls.folder / "recuperacion.json")
        cls.rubric = read(Path(__file__).parent / "pauta_evidencia.json")

    def test_cosine_order_and_stable_ties(self):
        docs = np.array([[1., 0.], [0., 1.], [1., 0.], [-1., 0.]])
        scores, order = rank_vectors(docs, np.array([[1., 0.]]))
        self.assertEqual(order.tolist(), [[0, 2, 1, 3]])
        np.testing.assert_allclose(scores, [[1., 0., 1., -1.]])

    def test_invalid_vectors_rejected(self):
        for docs in (np.array([[2., 0.]]), np.array([[np.nan, 0.]])):
            with self.assertRaises(ValueError):
                rank_vectors(docs, np.array([[1., 0.]]))

    def test_multisource_question_requires_every_component(self):
        result = coverage([["fecha"], ["creditos"]], ["fecha", "irrelevante"])
        self.assertFalse(result["completa"])
        self.assertEqual(result["grupos_faltantes"], [["creditos"]])

    def test_valid_alternative_counts_once(self):
        result = coverage([["interno", "general"]], ["general"])
        self.assertTrue(result["completa"])
        self.assertEqual(result["grupos_cubiertos"], 1)

    def test_empty_evidence_does_not_count_as_success(self):
        with self.assertRaises(ValueError):
            coverage([], ["similar"])

    def test_absence_cases_stay_pending_and_outside_denominator(self):
        report = evaluate(self.experiment, self.rubric)
        self.assertEqual(report["resumen"]["evaluables_cobertura_local"], 45)
        self.assertEqual(report["resumen"]["pendientes_verificacion_global"], 5)
        pending = [c for c in report["casos"] if c["completa"] is None]
        self.assertEqual([c["id"] for c in pending], [41, 42, 43, 44, 49])

    def test_context_must_match_actual_search_results(self):
        altered = copy.deepcopy(self.experiment)
        altered["casos"][0]["contextos"].append({"unidad_id": "fuente_insertada_desde_la_pauta"})
        with self.assertRaisesRegex(ValueError, "Contexto no coincide"):
            evaluate(altered, self.rubric)

    def test_stale_corpus_rubric_rejected(self):
        altered = copy.deepcopy(self.rubric)
        altered["corpus_sha256"] = "otro corpus"
        with self.assertRaisesRegex(ValueError, "corpus distintos"):
            evaluate(self.experiment, altered)

    def test_questions_loader_excludes_baseline_answers(self):
        _, _, questions = load_inputs(ROOT / "Deliverable2/corpus/generado", ROOT / "Deliverable1/datos/test_set_50.csv")
        self.assertTrue(all(set(q) == {"id", "pregunta", "categoria"} for q in questions))

    def test_saved_vectors_reproduce_ranking_and_full_contexts(self):
        corpus, fragments, questions = load_inputs(ROOT / "Deliverable2/corpus/generado", ROOT / "Deliverable1/datos/test_set_50.csv")
        docs = np.load(self.folder / "vectores_documentos.npy", allow_pickle=False)
        queries = np.load(self.folder / "vectores_consultas.npy", allow_pickle=False)
        cases = retrieve(corpus, fragments, questions, docs, queries, 5)
        self.assertEqual(cases, self.experiment["casos"])

    def test_artifact_integrity(self):
        manifest = read(self.folder / "manifiesto.json")
        for name, expected in manifest["artefactos_sha256"].items():
            self.assertEqual(sha(self.folder / name), expected)
        self.assertEqual(sha(Path(__file__).parent / "probar_recuperacion.py"), manifest["script_sha256"])


if __name__ == "__main__":
    unittest.main()
