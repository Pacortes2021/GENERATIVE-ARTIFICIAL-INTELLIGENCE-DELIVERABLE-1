"""Regresión: auditar la corrida publicada sin depender de Drive ni de la GPU."""
import contextlib
import io
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / 'Deliverable2/resultados/qwen3_4b_f0bff499766960f7'
NAME = 'comparacion_f0bff499766960f7.zip'


def respuesta_publicada(url, timeout):
    relative = url.split('/qwen3_4b_f0bff499766960f7/', 1)[1]
    return io.BytesIO((RUN / relative).read_bytes())


class AuditoriaColabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        salida = io.StringIO()
        with patch('urllib.request.urlopen', side_effect=respuesta_publicada), contextlib.redirect_stdout(salida):
            cls.audit = runpy.run_path(str(HERE / 'auditar_lote_en_colab.py'),
                                      init_globals={'ZIP_LOTE': RUN / NAME})
        cls.salida = salida.getvalue()

    def test_audita_las_100_respuestas_y_juicios_del_zip_original(self):
        self.assertEqual(len(self.audit['answers']), 100)
        self.assertEqual(sum(self.audit['marks']['baseline_directo'].values()), 1)
        self.assertEqual(sum(self.audit['marks']['rag_estructurado'].values()), 40)
        self.assertIn('Archivo local verificado', self.salida)
        self.assertIn('esta celda no ejecuta una corrida nueva', self.salida)
        self.assertNotIn('CASO HISTÓRICO', self.salida)
        self.assertNotIn('Referencia del evaluador:', self.salida)

    def test_caso_historico_solo_si_se_solicita(self):
        salida = io.StringIO()
        with patch('urllib.request.urlopen', side_effect=respuesta_publicada), contextlib.redirect_stdout(salida):
            runpy.run_path(str(HERE / 'auditar_lote_en_colab.py'),
                          init_globals={'ZIP_LOTE': RUN / NAME, 'ID_CASO': 25})
        self.assertIn('CASO HISTÓRICO P25 (respuesta guardada)', salida.getvalue())
        self.assertIn('RI-FI-ART-007 — texto íntegro del prompt histórico', salida.getvalue())

    def test_sin_drive_descarga_copia_original_y_la_reutiliza(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch('urllib.request.urlopen', side_effect=respuesta_publicada) as fetch, contextlib.redirect_stdout(io.StringIO()):
                ruta, origen = self.audit['localizar_zip'](
                    preferido=root / 'drive_ausente' / NAME, content_root=root)
                self.assertEqual(ruta.read_bytes(), (RUN / NAME).read_bytes())
                self.assertIn('GitHub', origen)
                fetch.assert_called_once_with(self.audit['CORRIDA_PUBLICADA'] + '/' + NAME, timeout=30)
            with patch('urllib.request.urlopen') as fetch:
                reutilizada, origen = self.audit['localizar_zip'](preferido=ruta, content_root=root)
                self.assertEqual(reutilizada, ruta)
                self.assertIn('Copia publicada', origen)
                fetch.assert_not_called()

    def test_encuentra_lote_en_output_root_sin_descargar(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output = root / 'salidas'
            output.mkdir()
            local = output / NAME
            local.write_bytes((RUN / NAME).read_bytes())
            with patch('urllib.request.urlopen') as fetch:
                ruta, origen = self.audit['localizar_zip'](
                    preferido=root / 'drive_ausente' / NAME, output_root=output, content_root=root)
                self.assertEqual(ruta, local)
                self.assertEqual(origen, 'Archivo local verificado')
                fetch.assert_not_called()

    def test_descarga_alterada_no_se_guarda(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch('urllib.request.urlopen', return_value=io.BytesIO(b'ZIP alterado')), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(AssertionError, 'descarga no coincide'):
                    self.audit['localizar_zip'](content_root=root)
            self.assertFalse((root / 'auditoria_publicada' / NAME).exists())

    def test_zip_local_distinto_no_se_reemplaza_con_la_copia_publica(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            local = root / NAME
            local.write_bytes(b'otra corrida')
            with patch('urllib.request.urlopen') as fetch:
                with self.assertRaisesRegex(AssertionError, 'ZIP local no coincide'):
                    self.audit['localizar_zip'](preferido=local, content_root=root)
                fetch.assert_not_called()
            self.assertEqual(local.read_bytes(), b'otra corrida')


if __name__ == '__main__':
    unittest.main()
