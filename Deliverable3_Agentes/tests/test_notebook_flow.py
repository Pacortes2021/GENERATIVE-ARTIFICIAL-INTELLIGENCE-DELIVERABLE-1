"""Regresión de Ejecutar todo y descarga, usando inferencia explícitamente simulada."""
import contextlib
import io
import json
import sys
import tempfile
import types
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch
import test_experiment as fixtures
from crear_cuaderno import build
from d3_agentes.common import VARIANTS
from d3_agentes.downloads import prepare_download
from d3_agentes.experiment import audit_zip, sealed_load
from d3_agentes.runtime import execute


class NotebookFlowTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ExperimentTests()
        self.fixture.setUp()

    def run_notebook_after_load(self, directory, download):
        notebook = json.loads(build(Path(directory) / 'flujo.ipynb').read_text())
        environment = {'retriever': self.fixture.retriever, 'tokenizer': fixtures.Tokenizer(),
                       'generate': self.fixture.model, 'settings': fixtures.SETTINGS,
                       'questions': self.fixture.retriever.questions,
                       'preparation': {'ejecucion': 'simulacion_pruebas'}}
        namespace = {'ENV': environment, 'OUTPUT': Path(directory) / 'runs',
                     'execute': execute, 'VARIANTS': VARIANTS, 'Path': Path,
                     'json': json, 'sealed_load': sealed_load}
        colab = types.ModuleType('google.colab')
        colab.files = types.SimpleNamespace(download=download)
        google = types.ModuleType('google')
        google.colab = colab
        active = False
        output = io.StringIO()
        with patch.dict(sys.modules, {'google': google, 'google.colab': colab}), contextlib.redirect_stdout(output):
            for cell in notebook['cells']:
                if cell['cell_type'] == 'markdown' and cell['source'].startswith('## 4.'):
                    active = True
                if active and cell['cell_type'] == 'code':
                    exec(compile(cell['source'], cell['id'], 'exec'), namespace)
        return namespace, output.getvalue()

    def test_run_all_defaults_generate_twelve_answers_and_request_download(self):
        with tempfile.TemporaryDirectory() as directory:
            download = Mock()
            namespace, output = self.run_notebook_after_load(directory, download)
            archive = namespace['ZIP']
            summary = audit_zip(archive)
            self.assertEqual(summary['esperadas'], 12)
            self.assertEqual(summary['completadas'], 12)
            self.assertTrue(summary['completa'])
            config=sealed_load(namespace['RUN_DIR']/'configuracion.json')
            self.assertEqual(config['etiqueta'],'piloto-v4')
            self.assertEqual(config['protocolo'],'d3-agentes-desde-cero-v4')
            self.assertEqual(summary['ejecucion'], 'simulacion_pruebas')
            self.assertFalse(namespace['EJECUTAR_LOTE'])
            download.assert_called_once_with(str(archive))
            self.assertIn('ZIP listo:', output)

    def test_browser_download_failure_preserves_zip_and_prints_manual_path(self):
        with tempfile.TemporaryDirectory() as directory:
            namespace, output = self.run_notebook_after_load(directory, Mock(side_effect=RuntimeError('navegador bloqueado')))
            self.assertTrue(namespace['ZIP'].is_file())
            self.assertIn('El ZIP sigue guardado en:', output)

    def test_no_run_explains_that_loading_models_is_not_generation(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertIsNone(prepare_download(directory))
            self.assertIn('cargar los modelos no genera respuestas', output.getvalue())
            self.assertFalse(list(Path(directory).glob('*.zip')))

    def test_recovers_interrupted_run_without_run_dir_variable(self):
        def crash(task, seed):
            if task['etapa'] == 'redactor':
                raise RuntimeError('interrupción simulada')
            return self.fixture.model(task, seed)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                self.fixture.execute(directory, generate=crash, variants=('agentes_completo',))
            with contextlib.redirect_stdout(io.StringIO()):
                archive = prepare_download(directory)
            summary = audit_zip(archive)
            self.assertFalse(summary['completa'])
            with zipfile.ZipFile(archive) as zipped:
                self.assertTrue(any(n.startswith('llamadas/') for n in zipped.namelist()))

    def test_multiple_runs_are_all_preserved_in_one_download(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.fixture.execute(directory, variants=VARIANTS[:2])
            self.fixture.question = [self.fixture.retriever.questions[1]]
            second = self.fixture.execute(directory, variants=VARIANTS[:2])
            with contextlib.redirect_stdout(io.StringIO()):
                archive = prepare_download(directory)
            with zipfile.ZipFile(archive) as zipped:
                self.assertEqual(set(zipped.namelist()), {'corridas.json', first.with_suffix('.zip').name,
                                                        second.with_suffix('.zip').name})
                self.assertEqual(len(json.loads(zipped.read('corridas.json'))), 2)


if __name__ == '__main__':
    unittest.main()
