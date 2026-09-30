import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import nbformat
from diagnostico import diagnostic_digest, read_run_zip, cite_alerts, diagnostic_summary


class DiagnosticTests(unittest.TestCase):
    def fixture(self):
        payload = {'casos': []}
        tasks = [{'pregunta_id': 1, 'variante': 'rag_simple', 'prompt_sha256': 'p', 'evidencia_sha256': 'e'}]
        config = {'payload_sha256': diagnostic_digest(payload), 'prompts_sha256': diagnostic_digest(tasks)}
        row = dict(tasks[0], run_hash=diagnostic_digest(config), respuesta_modelo='Respuesta',
                   respuesta_sha256=diagnostic_digest('Respuesta'), categoria='factual', posible_corte=False,
                   thinking_inesperado=False, segundos=2.0, tokens_entrada=20, tokens_salida=3)
        return {'configuracion.json': config, 'evidencia.json': {'origen': payload},
                'prompts.json': tasks, 'respuestas/P01_rag_simple.json': row}

    def read_fixture(self, contents):
        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w') as z:
            for name, obj in contents.items(): z.writestr(name, json.dumps(obj))
        data.seek(0)
        return read_run_zip(data)

    def test_valid_zip_and_category_stats(self):
        rows, _, _ = self.read_fixture(self.fixture())
        summary = diagnostic_summary(rows)
        self.assertEqual(summary[0]['respuestas'], 1)
        self.assertEqual(summary[0]['mediana_segundos'], 2.0)
        self.assertNotIn('correcta', summary[0])

    def test_tampered_answer_rejected(self):
        obj = self.fixture()
        obj['respuestas/P01_rag_simple.json']['respuesta_modelo'] = 'Alterada'
        with self.assertRaisesRegex(ValueError, 'alterada'): self.read_fixture(obj)

    def test_tampered_evidence_rejected(self):
        obj = self.fixture()
        obj['evidencia.json']['origen']['casos'] = ['nuevo caso']
        with self.assertRaisesRegex(ValueError, 'evidencia'): self.read_fixture(obj)

    def test_duplicate_case_rejected(self):
        obj = self.fixture()
        obj['respuestas/duplicada.json'] = obj['respuestas/P01_rag_simple.json']
        with self.assertRaisesRegex(ValueError, 'duplicada'): self.read_fixture(obj)

    def test_fewshot_citation_detected_without_semantic_verdict(self):
        case = {'contextos': [{'unidad_id': 'RG-ART-001'}]}
        row = {'respuesta_modelo': 'Dato [RG-ART-001] y dato [EJ-A].'}
        result = cite_alerts(row, case)
        self.assertEqual(result['ids_ajenos_a_evidencia'], ['EJ-A'])
        self.assertNotIn('correcta', result)

    def test_companion_notebook_valid_and_compilable(self):
        nb = nbformat.read(Path(__file__).parent / 'Revisar_resultados_RAG.ipynb', as_version=4)
        nbformat.validate(nb)
        for c in nb.cells:
            if c.cell_type == 'code': compile(c.source, '<cell>', 'exec')


if __name__ == '__main__': unittest.main()
