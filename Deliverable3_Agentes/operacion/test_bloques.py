"""Pruebas de orquestación; no son inferencia ni resultados experimentales."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import d3_agentes.experiment as experiment
from d3_agentes.common import VARIANTS
spec = importlib.util.spec_from_file_location('operacion_bloques', Path(__file__).with_name('reanudar_lote_v4_colab.py'))
bloques = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bloques)


class BloquesTest(unittest.TestCase):
    def probar(self, inicial, fallo=None):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / 'corrida'
            folder.mkdir()
            estado = {'n': inicial}
            generadas, descargas, errores = [], [], []
            questions = [{'id': i} for i in range(1, 51)]
            def exportar(path):
                (path / 'resumen_tecnico.json').write_text(json.dumps({'completadas': estado['n']}))
                target = path.with_suffix('.zip')
                target.write_text(str(estado['n']))
                return target
            def auditar(path):
                return {'completadas': int(path.read_text()), 'esperadas': 300}
            def ejecutar(env, qs, output, **kwargs):
                self.assertIs(qs, questions)
                self.assertEqual(kwargs['variants'], VARIANTS)
                self.assertEqual(kwargs['tag'], 'lote-v4')
                for n in range(inicial + 1, 301):
                    if fallo == n:
                        raise RuntimeError('fallo real')
                    generadas.append(n)
                    estado['n'] = n
                    try:
                        experiment.export(folder)
                    except Exception:
                        errores.append(n)
                        raise
            def descargar(path):
                descargas.append((Path(path).name, Path(path).read_text()))
            with patch.object(experiment, 'export', exportar), patch.object(bloques, 'audit_zip', auditar), patch('d3_agentes.runtime.execute', ejecutar), contextlib.redirect_stdout(io.StringIO()):
                try:
                    bloques.ejecutar_bloque({'questions': questions}, Path(tmp), folder, descargar)
                finally:
                    self.assertIs(experiment.export, exportar)
            return generadas, descargas, errores

    def test_restaurado_39_detiene_exactamente_en_60(self):
        generadas, descargas, errores = self.probar(39)
        self.assertEqual(generadas, list(range(40, 61)))
        self.assertEqual([int(x[1]) for x in descargas], [45, 51, 57, 60])
        self.assertFalse(errores)

    def test_siguiente_bloque_60_a_90(self):
        generadas, descargas, _ = self.probar(60)
        self.assertEqual(generadas, list(range(61, 91)))
        self.assertEqual(int(descargas[-1][1]), 90)

    def test_final_299_a_300_sin_otra_inferencia(self):
        self.assertEqual(self.probar(299)[0], [300])
        self.assertEqual(self.probar(300)[0], [])

    def test_error_real_no_se_oculta_y_restaura_exportador(self):
        with self.assertRaisesRegex(RuntimeError, 'fallo real'):
            self.probar(39, fallo=42)


if __name__ == '__main__':
    unittest.main()
