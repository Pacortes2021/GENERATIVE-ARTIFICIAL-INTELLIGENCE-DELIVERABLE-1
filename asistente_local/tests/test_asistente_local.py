"""Tests unitarios deterministas (sin red ni GPU) para el asistente local UdeC."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from asistente_local.asistente import AsistenteUdeC, limpiar_think
from asistente_local.benchmark import cargar_preguntas
from asistente_local.buscador import BuscadorNormativa
from asistente_local.config import ConfigAsistente
from asistente_local.herramientas import calcular, dias_entre, ejecutar_herramienta


class TestCalculadoraYCalendario(unittest.TestCase):
    def test_calculadora_basica_y_coma_decimal(self) -> None:
        r1 = calcular("42 / 4")
        self.assertTrue(r1["ok"])
        self.assertEqual(r1["resultado"], 10.5)

        r2 = calcular("0,6 * 5,2 + 0,4 * 6,5")
        self.assertTrue(r2["ok"])
        self.assertAlmostEqual(r2["resultado"], 5.72, places=6)

        r3 = calcular("round(5,72, 1)")
        self.assertTrue(r3["ok"])
        self.assertEqual(r3["resultado"], 5.7)

    def test_calculadora_rechaza_codigo_inseguro_y_div_cero(self) -> None:
        self.assertFalse(calcular("10 / 0")["ok"])
        self.assertFalse(calcular("__import__('os').system('ls')")["ok"])
        self.assertFalse(calcular("2 ** 5000")["ok"])

    def test_dias_entre_casos_reales_h03_y_n07(self) -> None:
        s1 = dias_entre("09 de marzo", "02 de abril")
        self.assertTrue(s1["ok"])
        self.assertEqual(s1["dias_corridos"], 24)

        s2 = dias_entre("10 de agosto", "04 de septiembre")
        self.assertTrue(s2["ok"])
        self.assertEqual(s2["dias_corridos"], 25)

        n07 = dias_entre("2026-05-11", "2026-09-14")
        self.assertTrue(n07["ok"])
        self.assertEqual(n07["dias_corridos"], 126)

        pausa = dias_entre("11 de mayo", "15 de mayo", inclusivo=True)
        self.assertTrue(pausa["ok"])
        self.assertEqual(pausa["resultado_solicitado"], 5)


class TestBuscadorNormativa(unittest.TestCase):
    def setUp(self) -> None:
        self.buscador = BuscadorNormativa(usar_embeddings=False)

    def test_existe_y_leer_articulo(self) -> None:
        self.assertTrue(self.buscador.existe_articulo("RI-FI", 14)["existe"])
        self.assertFalse(self.buscador.existe_articulo("RI-FI", 45)["existe"])
        art = self.buscador.leer_articulo("RG", 28)
        self.assertTrue(art["encontrado"])
        self.assertIn("promedio de créditos", art["texto"].lower())

    def test_buscar_con_filtro_documento_y_expansion(self) -> None:
        hits_ri = self.buscador.buscar("modificación inscripción eliminar prioridades", k=3, documento="RI-FI")
        ids_ri = {h["id"] for h in hits_ri}
        self.assertIn("RI-FI-ART-009", ids_ri)
        self.assertIn("RI-FI-ART-007", ids_ri)
        for h in hits_ri:
            self.assertEqual(h["documento"], "RI-FI")

    def test_ver_calendario_ordenado(self) -> None:
        s2 = self.buscador.ver_calendario("2")
        self.assertGreater(len(s2), 5)
        self.assertEqual(s2[0]["id"], "CAL-2026-S2-01")
        self.assertEqual(
            ejecutar_herramienta("calcular", {"expresion": "38 / 4"}, self.buscador)["resultado"],
            9.5,
        )


class TestAsistenteOrquestadorOffline(unittest.TestCase):
    def test_flujo_tool_calling_y_argumentos_json_string(self) -> None:
        buscador = BuscadorNormativa(usar_embeddings=False)
        llamadas = []

        def mock_ollama(payload):
            llamadas.append(payload)
            if len(llamadas) == 1:
                return {
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "c1",
                                "function": {
                                    "name": "calcular",
                                    "arguments": '{"expresion": "42 / 4"}',
                                },
                            }
                        ],
                    }
                }
            return {
                "message": {
                    "role": "assistant",
                    "content": "<think>razonamiento interno</think>Promedio 10,5 créditos [RI-FI-ART-014].",
                }
            }

        asistente = AsistenteUdeC(
            config=ConfigAsistente(modelo="qwen3:4b-instruct", usar_embeddings=False),
            buscador=buscador,
            cliente_chat=mock_ollama,
        )
        res = asistente.responder("¿42 créditos en 4 semestres cae en baja?")
        self.assertEqual(asistente.config.top_k_inicial, 5)
        self.assertEqual(res.turnos_modelo, 2)
        self.assertEqual(len(res.pasos_herramientas), 1)
        self.assertEqual(res.pasos_herramientas[0].resultado["resultado"], 10.5)
        self.assertEqual(res.respuesta, "Promedio 10,5 créditos [RI-FI-ART-014].")
        self.assertEqual(limpiar_think("<think>a</think>hola"), "hola")

    def test_benchmark_cargar_preguntas_sets(self) -> None:
        self.assertEqual(len(cargar_preguntas("dificil_25")), 25)
        self.assertEqual(len(cargar_preguntas("congelado_50")), 50)
        self.assertEqual(len(cargar_preguntas("dificil_25", qids_filtro={"H03", "H07"})), 2)


if __name__ == "__main__":
    unittest.main()
