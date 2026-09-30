import copy
import csv
import tempfile
import unittest
from pathlib import Path

import evaluar as ev


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.source = ev.ROOT / 'Deliverable1/datos/resultados_baseline.csv'
        self.output = self.path / 'paquete'
        ev.preparar(self.source, self.output)
        self.packet = ev.read_json(self.output / 'paquete.json')
        self.labels = ev.read_json(self.output / 'veredictos.json')

    def complete(self):
        self.labels.update(evaluador='test_double', modalidad='humana')
        for row in self.labels['evaluaciones']:
            row['correcta'] = True
            row.update(motivo='Fixture para probar el cálculo, no un juicio real.')

    def test_historical_labels_not_reused(self):
        rows = ev.resultados(self.packet, self.labels)
        self.assertEqual(ev.resumen(rows)['pendientes'], 50)
        self.assertIsNone(ev.resumen(rows)['exactitud_porcentaje'])
        self.assertNotIn('correcto', self.packet['casos'][0])

    def test_one_missing_judgment_prevents_final_score(self):
        self.complete()
        self.labels['evaluaciones'][0]['correcta'] = None
        result = ev.resumen(ev.resultados(self.packet, self.labels))
        self.assertEqual(result['correctas'], 49)
        self.assertEqual(result['total'], 50)
        self.assertIsNone(result['exactitud_porcentaje'])

    def test_binary_verdicts_determine_score(self):
        self.complete()
        self.labels['evaluaciones'][0]['correcta'] = False
        self.labels['evaluaciones'][1]['correcta'] = False
        self.assertEqual(ev.resumen(ev.resultados(self.packet, self.labels))['exactitud_porcentaje'], 96.0)

    def test_changed_answer_invalidates_old_labels(self):
        self.packet['casos'][0]['respuesta_modelo'] = 'Nueva respuesta'
        with self.assertRaises(ValueError):
            ev.resultados(self.packet, self.labels)

    def test_changed_reference_invalidates_old_labels(self):
        self.packet['casos'][0]['respuesta_referencia'] = 'Otra respuesta'
        with self.assertRaises(ValueError):
            ev.resultados(self.packet, self.labels)

    def test_reference_evidence_is_embedded(self):
        self.assertEqual(self.packet['version'], 2)
        self.assertEqual(len(self.packet['casos']), 50)
        case = self.packet['casos'][35]
        self.assertIn('ocho', case['respuesta_referencia'])
        self.assertEqual({f['documento'] for f in case['fuentes']}, {'CAL', 'RI-FI'})

    def test_judge_cannot_overwrite_answer(self):
        self.labels['evaluaciones'][0]['respuesta_modelo'] = 'Una respuesta inventada'
        rows = ev.resultados(self.packet, self.labels)
        self.assertEqual(rows[0]['respuesta_modelo'], self.packet['casos'][0]['respuesta_modelo'])

    def test_changed_rubric_invalidates_old_labels(self):
        self.packet['criterios'] += ' nueva regla'
        with self.assertRaises(ValueError):
            ev.resultados(self.packet, self.labels)

    def test_duplicate_or_missing_judgments_rejected(self):
        for labels in (self.labels['evaluaciones'][:-1], self.labels['evaluaciones'] + [self.labels['evaluaciones'][0]]):
            other = copy.deepcopy(self.labels)
            other['evaluaciones'] = labels
            with self.assertRaises(ValueError):
                ev.resultados(self.packet, other)

    def test_string_boolean_rejected(self):
        self.labels['evaluaciones'][0]['correcta'] = 'false'
        with self.assertRaises(ValueError):
            ev.resultados(self.packet, self.labels)

    def test_unsupported_decision_rejected(self):
        self.complete()
        self.labels['evaluaciones'][0]['motivo'] = ''
        with self.assertRaises(ValueError):
            ev.resultados(self.packet, self.labels)

    def test_report_exports_pending_without_score(self):
        report = self.path / 'report'
        summary = ev.resumir(self.output / 'paquete.json', self.output / 'veredictos.json', report)
        self.assertIsNone(summary['exactitud_porcentaje'])
        with (report / 'evaluacion.csv').open(newline='') as f:
            self.assertEqual(len(list(csv.DictReader(f))), 50)

    def test_existing_output_and_historical_destination_protected(self):
        with self.assertRaises(FileExistsError):
            ev.preparar(self.source, self.output)
        with self.assertRaises(ValueError):
            ev.check_destination(ev.ROOT / 'Deliverable1/nueva_corrida')

    def test_duplicate_questions_rejected(self):
        source = self.path / 'duplicated.csv'
        case = self.packet['casos'][0]
        with source.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['pregunta', 'respuesta_modelo'])
            w.writeheader()
            for _ in range(2):
                w.writerow({k: case[k] for k in w.fieldnames})
        with self.assertRaises(ValueError):
            ev.preparar(source, self.path / 'dup')


if __name__ == '__main__':
    unittest.main()
