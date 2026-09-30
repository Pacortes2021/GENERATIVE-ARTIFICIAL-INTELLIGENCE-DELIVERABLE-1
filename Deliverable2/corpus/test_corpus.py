"""Regresiones de extracción real, conservación y expansión de contexto."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from preparar_corpus import ROOT, REVISION, build, expand_hits, validate


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokenizer = Path.home() / ".cache/huggingface/hub/models--intfloat--multilingual-e5-small/snapshots" / REVISION / "tokenizer.json"
        # Para reproducir en otra máquina: descargar la revisión fijada (ver README).
        import os
        cls.tokenizer = Path(os.environ.get("E5_TOKENIZER", cls.tokenizer))
        cls.corpus, cls.fragments, cls.ledger, cls.report = build(ROOT / "Corpus", cls.tokenizer)
        cls.parents = {p["id"]: p for p in cls.corpus["padres"]}

    def test_regulation_complete_sets_and_transitory_ids(self):
        for doc, count in (("RI-FI", 35), ("RG", 60)):
            self.assertEqual([self.parents[f"{doc}-ART-{n:03}"]["articulo"] for n in range(1, count + 1)], list(range(1, count + 1)))
        self.assertNotEqual(self.parents["RG-ART-001"]["texto"], self.parents["RG-TRANS-001"]["texto"])
        self.assertEqual(self.parents["RG-TRANS-002"]["paginas"], [32])

    def test_reference_at_line_start_does_not_split_article(self):
        text = self.parents["RI-FI-ART-009"]["texto"]
        self.assertIn("prioridades a) y b) del Artículo 7°", text)
        self.assertTrue(text.endswith("Artículo 8°."))
        self.assertNotIn("TÍTULO IV", text)

    def test_article_five_heading_and_hyphenation(self):
        text = self.parents["RG-ART-005"]["texto"]
        self.assertTrue(text.startswith("Artículo 5º En cada Facultad"))
        self.assertIn("dependiente del Vicedecano", text)
        self.assertNotIn("Secretaría Académica", self.parents["RG-ART-004"]["texto"])

    def test_cross_page_rule_and_exception_survive(self):
        article = self.parents["RI-FI-ART-013"]
        self.assertEqual(article["paginas"], [2, 3])
        self.assertIn("un 100% en las actividades", article["texto"])
        self.assertTrue(article["texto"].endswith("similares a las mencionadas.") or article["texto"].endswith("similar a las mencionadas."))
        self.assertIn("salvo que", self.parents["RI-FI-ART-014"]["texto"])
        self.assertIn("primer año de permanencia", self.parents["RI-FI-ART-014"]["texto"])

    def test_calendar_multiline_event_and_cross_month_range(self):
        events = [p for p in self.parents.values() if p["tipo"] == "evento"]
        self.assertEqual(len(events), 25)
        vacation = next(p for p in events if p["evento"].startswith("Vacaciones"))
        self.assertEqual(vacation["evento"], "Vacaciones de invierno (aprobación transitoria)")
        self.assertEqual(vacation["fecha"], "30 junio – 05 de julio")
        self.assertEqual(vacation["semestre"], 1)
        suspension = next(p for p in events if p["evento"].startswith("Suspensión"))
        self.assertTrue(suspension["evento"].endswith("pregrado"))
        self.assertEqual(suspension["fecha"], "14 - 17 de septiembre")
        self.assertIn("inducción a la UdeC", events[0]["evento"])

    def test_annex_merged_cell_boundaries_from_pdf(self):
        expected = {5: "", 6: "Aprobado por Unanimidad", 19: "Aprobado por Unanimidad",
                    20: "Aprobado con Distinción", 36: "Aprobado con Distinción",
                    37: "Aprobado con Distinción Máxima", 50: "Aprobado con Distinción Máxima"}
        for index, concept in expected.items():
            self.assertEqual(self.parents[f"RG-ANEXO-{index:02}"]["concepto"], concept)

    def test_glossary_definition_continues_across_page(self):
        unit = next(u for u in self.corpus["unidades"] if u["id"] == "RG-ART-003-DEF-04")
        self.assertIn("TÍTULO PROFESIONAL", unit["texto"])
        self.assertIn("condición habilitante", unit["texto"])
        self.assertNotIn("3.5.", unit["texto"])

    def test_embedding_has_real_token_budget_including_prefix(self):
        self.assertLessEqual(max(f["tokens_e5"] for f in self.fragments), 480)
        self.assertTrue(all(f["texto_embedding"].startswith("passage: ") for f in self.fragments))
        self.assertTrue(all(f["tokens_e5"] > 0 for f in self.fragments))

    def test_search_hit_recovers_whole_article_and_deduplicates(self):
        hits = [f["id"] for f in self.fragments if f["unidad_id"] == "RG-ART-008"]
        self.assertGreater(len(hits), 1)
        contexts = expand_hits(list(reversed(hits)), self.corpus, self.fragments)
        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts[0]["texto"], self.parents["RG-ART-008"]["texto"])

    def test_missing_tail_is_rejected(self):
        altered = copy.deepcopy(self.fragments)
        altered.pop()
        with self.assertRaisesRegex(ValueError, "Cola perdida"):
            validate(self.corpus["padres"], self.corpus["unidades"], altered, self.ledger)

    def test_changed_fragment_is_rejected(self):
        altered = copy.deepcopy(self.fragments)
        altered[0]["texto"] = "texto diferente"
        with self.assertRaisesRegex(ValueError, "Fragmento alterado"):
            validate(self.corpus["padres"], self.corpus["unidades"], altered, self.ledger)

    def test_missing_pdf_fails_instead_of_partial_corpus(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                build(Path(temp), self.tokenizer)

    def test_generated_data_matches_current_extractor(self):
        saved = Path(__file__).parent / "generado"
        self.assertEqual(json.loads((saved / "corpus.json").read_text()), self.corpus)
        self.assertEqual(json.loads((saved / "fragmentos_busqueda.json").read_text()), self.fragments)


if __name__ == "__main__":
    unittest.main()
