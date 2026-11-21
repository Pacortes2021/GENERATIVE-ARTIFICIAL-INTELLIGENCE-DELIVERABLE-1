"""Tests unitarios deterministas (sin red ni GPU) para el asistente local UdeC."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from asistente_local.asistente import (
    AsistenteUdeC,
    _compactar_resultado_herramienta,
    _FiltroThinkStream,
    _recopilar_stream_ollama,
    limpiar_think,
    normalizar_citas_respuesta,
    reescribir_consulta_con_historial,
)
from asistente_local.benchmark import cargar_preguntas
from asistente_local.buscador import (
    BM25Index,
    BuscadorNormativa,
    descomponer_subconsultas,
    seleccionar_por_top_p,
)
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

    def test_seleccion_top_p_acumulada(self) -> None:
        self.assertEqual(seleccionar_por_top_p([], k_max=5, top_p=0.8), [])

        candidatos_dominante = [
            (0.95, 0.95, {"id": "A"}),
            (0.40, 0.40, {"id": "B"}),
            (0.35, 0.35, {"id": "C"}),
            (0.30, 0.30, {"id": "D"}),
        ]
        fijo = seleccionar_por_top_p(candidatos_dominante, k_max=3, top_p=None)
        self.assertEqual([u["id"] for _, u in fijo], ["A", "B", "C"])

        corto = seleccionar_por_top_p(candidatos_dominante, k_max=4, top_p=0.80, k_min=1, temperatura=0.12)
        self.assertEqual([u["id"] for _, u in corto], ["A"])

        con_min = seleccionar_por_top_p(candidatos_dominante, k_max=4, top_p=0.80, k_min=2, temperatura=0.12)
        self.assertEqual([u["id"] for _, u in con_min], ["A", "B"])

        empatados = [
            (0.60, 0.60, {"id": "A"}),
            (0.58, 0.58, {"id": "B"}),
            (0.57, 0.57, {"id": "C"}),
            (0.56, 0.56, {"id": "D"}),
            (0.55, 0.55, {"id": "E"}),
        ]
        amplio = seleccionar_por_top_p(empatados, k_max=5, top_p=0.80, k_min=1, temperatura=0.12)
        self.assertEqual(len(amplio), 4)

        hits = self.buscador.buscar("baja academica creditos", k=6, top_p=0.75, expandir_citas=False)
        self.assertTrue(1 <= len(hits) <= 6)


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
        self.assertEqual(asistente.config.top_k_inicial, 6)
        self.assertEqual(asistente.config.top_p_inicial, 0.85)
        self.assertEqual(asistente.config.top_p_temp, 0.13)
        self.assertEqual(asistente.config.top_p_pool, 10)
        self.assertEqual(asistente.config.modo_fusion, "rrf")
        self.assertEqual(asistente.config.k_rrf, 10)
        self.assertTrue(asistente.config.usar_descomposicion)
        self.assertEqual(asistente.config.repeat_penalty, 1.05)
        self.assertEqual(res.turnos_modelo, 2)
        self.assertEqual(len(res.pasos_herramientas), 1)
        self.assertEqual(res.pasos_herramientas[0].resultado["resultado"], 10.5)
        self.assertEqual(res.respuesta, "Promedio 10,5 créditos [RI-FI-ART-014].")
        self.assertEqual(limpiar_think("<think>a</think>hola"), "hola")

    def test_benchmark_cargar_preguntas_sets(self) -> None:
        self.assertEqual(len(cargar_preguntas("dificil_25")), 25)
        self.assertEqual(len(cargar_preguntas("congelado_50")), 50)
        self.assertEqual(len(cargar_preguntas("dificil_25", qids_filtro={"H03", "H07"})), 2)

    def test_expansion_calendario_semestre_y_validador_citas(self) -> None:
        buscador = BuscadorNormativa(usar_embeddings=False)
        hits = buscador.buscar("inicio de clases segundo semestre 03 de agosto", k=5)
        ids = {h["id"] for h in hits}
        self.assertIn("CAL-2026-S2-01", ids)
        self.assertIn("CAL-2026-S2-02", ids)

        txt, validas = normalizar_citas_respuesta(
            "Tope [RI-FI-ART-35] y criterio [RI-FI-ART-014.b].", set(buscador.por_id.keys())
        )
        self.assertEqual(txt, "Tope RI-FI-ART-35 y criterio [RI-FI-ART-014].")
        self.assertEqual(validas, ["RI-FI-ART-014"])

        respuestas = [
            {"message": {"role": "assistant", "content": "Hasta cuatro semanas antes."}},
            {"message": {"role": "assistant", "content": "Hasta cuatro semanas antes. Fuente: [RG-ART-031]"}},
        ]
        asistente = AsistenteUdeC(
            config=ConfigAsistente(modelo="qwen3:4b-instruct", usar_embeddings=False),
            buscador=buscador,
            cliente_chat=lambda _p: respuestas.pop(0),
        )
        res = asistente.responder("¿Hasta cuándo puedo suspender estudios?")
        self.assertEqual(res.turnos_modelo, 2)
        self.assertIn("[RG-ART-031]", res.respuesta)

    def test_compactar_resultado_evita_duplicacion_en_contexto(self) -> None:
        vistas = {"CAL-1": {"id": "CAL-1", "texto": "Texto largo 1"}}
        solo_nuevo = [{"id": "CAL-2", "texto": "Texto largo 2"}]
        self.assertEqual(_compactar_resultado_herramienta(solo_nuevo, vistas), solo_nuevo)

        mixto = [
            {"id": "CAL-1", "texto": "Texto largo 1"},
            {"id": "CAL-2", "texto": "Texto largo 2"},
        ]
        res_mixto = _compactar_resultado_herramienta(mixto, vistas)
        self.assertEqual(res_mixto["ya_en_contexto"], ["CAL-1"])
        self.assertEqual(res_mixto["nuevos"], [{"id": "CAL-2", "texto": "Texto largo 2"}])

        todo_duplicado = [{"id": "CAL-1", "texto": "Texto largo 1"}]
        res_dup = _compactar_resultado_herramienta(todo_duplicado, vistas)
        self.assertNotIn("nuevos", res_dup)
        self.assertEqual(res_dup["ya_en_contexto"], ["CAL-1"])

        buscador = BuscadorNormativa(usar_embeddings=False)
        payloads: list[dict] = []
        respuestas = [
            {
                "message": {
                    "role": "assistant",
                    "tool_calls": [{"function": {"name": "ver_calendario", "arguments": {"semestre": "ambos"}}}],
                }
            },
            {
                "message": {
                    "role": "assistant",
                    "content": "18 y 19 de mayo y 21 y 22 de septiembre (4 días) [CAL-2026-S1-08] [CAL-2026-S2-07].",
                }
            },
        ]

        def fake_chat(payload: dict) -> dict:
            payloads.append(json.loads(json.dumps(payload)))
            return respuestas.pop(0)

        asistente = AsistenteUdeC(
            config=ConfigAsistente(modelo="qwen3:4b-instruct", usar_embeddings=False),
            buscador=buscador,
            cliente_chat=fake_chat,
        )
        res = asistente.responder(
            "Según el Calendario 2026, ¿qué fechas no hay evaluaciones en ambos semestres?"
        )
        self.assertIn("[CAL-2026-S1-08]", res.respuesta)
        self.assertEqual(len(res.pasos_herramientas[0].resultado), 25)
        tool_msg = payloads[1]["messages"][-1]
        tool_json = json.loads(tool_msg["content"])
        self.assertIn("ya_en_contexto", tool_json)
        self.assertEqual(len(tool_json["ya_en_contexto"]), 25)
        self.assertNotIn("No se realizarán evaluaciones", tool_msg["content"])

    def test_filtro_think_stream_y_recopilar_ndjson(self) -> None:
        filtro = _FiltroThinkStream()
        emitidos = [
            filtro.alimentar("<th"),
            filtro.alimentar("ink>oculto</th"),
            filtro.alimentar("ink>\n\nHola "),
            filtro.alimentar("3 <"),
            filtro.alimentar(" 5"),
            filtro.finalizar(),
        ]
        self.assertEqual("".join(emitidos), "Hola 3 < 5")

        filtro_incompleto = _FiltroThinkStream()
        self.assertEqual(filtro_incompleto.alimentar("OK <think>cortado"), "OK ")
        self.assertEqual(filtro_incompleto.finalizar(), "")

        lineas_ndjson = [
            json.dumps({"message": {"role": "assistant", "content": "<think>interno</think>"}}).encode("utf-8"),
            json.dumps({"message": {"role": "assistant", "content": "Aprobación "}}).encode("utf-8"),
            json.dumps({"message": {"role": "assistant", "content": "mínima [RI-FI-ART-014]"}}).encode("utf-8"),
            json.dumps({"message": {"role": "assistant", "content": ""}, "done": True}).encode("utf-8"),
        ]
        tokens: list[str] = []
        merged = _recopilar_stream_ollama(lineas_ndjson, on_token=tokens.append)
        self.assertEqual("".join(tokens), "Aprobación mínima [RI-FI-ART-014]")
        self.assertEqual(merged["message"]["content"], "<think>interno</think>Aprobación mínima [RI-FI-ART-014]")
        self.assertTrue(merged["done"])

        lineas_tool = [
            json.dumps(
                {
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [{"function": {"name": "calcular", "arguments": {"expresion": "1+1"}}}],
                    },
                    "done": True,
                }
            )
        ]
        tokens_tool: list[str] = []
        merged_tool = _recopilar_stream_ollama(lineas_tool, on_token=tokens_tool.append)
        self.assertEqual(tokens_tool, [])
        self.assertEqual(len(merged_tool["message"]["tool_calls"]), 1)

        with self.assertRaises(RuntimeError):
            _recopilar_stream_ollama([json.dumps({"error": "modelo caído"})])

    def test_responder_notifica_stream_y_estado(self) -> None:
        buscador = BuscadorNormativa(usar_embeddings=False)
        payloads: list[dict] = []
        respuestas = [
            {
                "message": {
                    "role": "assistant",
                    "tool_calls": [{"function": {"name": "calcular", "arguments": {"expresion": "42 / 4"}}}],
                }
            },
            {
                "message": {
                    "role": "assistant",
                    "content": "El promedio es 10,5 créditos [RI-FI-ART-014].",
                }
            },
        ]

        def fake_chat(payload: dict) -> dict:
            payloads.append(json.loads(json.dumps(payload)))
            return respuestas.pop(0)

        asistente = AsistenteUdeC(
            config=ConfigAsistente(modelo="qwen3:4b-instruct", usar_embeddings=False),
            buscador=buscador,
            cliente_chat=fake_chat,
        )
        tokens: list[str] = []
        estados: list[str] = []
        res = asistente.responder(
            "¿42 créditos en 4 semestres cae en baja?",
            on_token=tokens.append,
            on_estado=estados.append,
        )
        self.assertTrue(payloads[0]["stream"])
        self.assertTrue(payloads[1]["stream"])
        self.assertIn("Ejecutando herramienta `calcular`...", estados)
        self.assertEqual("".join(tokens), "El promedio es 10,5 créditos [RI-FI-ART-014].")
        self.assertEqual(res.respuesta, "El promedio es 10,5 créditos [RI-FI-ART-014].")

    def test_bm25_descomposicion_rrf_y_reescritura_conversacional(self) -> None:
        idx = BM25Index([["credito", "promedio"], ["embarazo", "matrona", "visado"], ["evaluacion", "plazo"]])
        scores = idx.puntuar(["embarazo", "visado"])
        self.assertGreater(scores[1], scores[0])
        self.assertGreater(scores[1], scores[2])

        subqs, comp = descomponer_subconsultas(
            "¿En qué fechas se inscriben las asignaturas del segundo semestre, y cuál es el mínimo de créditos?"
        )
        self.assertTrue(comp)
        self.assertEqual(len(subqs), 3)

        subqs_simple, comp_simple = descomponer_subconsultas("¿Cuál es la nota mínima?")
        self.assertFalse(comp_simple)
        self.assertEqual(len(subqs_simple), 1)

        buscador = BuscadorNormativa(usar_embeddings=False)
        hits_rrf = buscador.buscar(
            "modificación inscripción eliminar prioridades",
            k=5,
            documento="RI-FI",
            modo_fusion="rrf",
            usar_descomposicion=True,
        )
        self.assertTrue(len(hits_rrf) >= 2)
        self.assertIn("RI-FI-ART-009", {h["id"] for h in hits_rrf})

        hist = [
            {"role": "user", "content": "Si falto a una evaluación por enfermedad justificada"},
            {"role": "assistant", "content": "Tienes 3 días hábiles ante el profesor [RG-ART-026]."},
        ]
        q_seg = reescribir_consulta_con_historial("¿Y si me la rechaza?", hist)
        self.assertIn("evaluacion", q_seg)
        q_indep = "¿Qué condiciones exige el Artículo 57 del Reglamento General sobre Beca Articulación Pregrado-Postgrado?"
        self.assertEqual(reescribir_consulta_con_historial(q_indep, hist), q_indep)

    def test_reparacion_citas_conserva_cuerpo_si_modelo_devuelve_solo_fuente(self) -> None:
        buscador = BuscadorNormativa(usar_embeddings=False)
        respuestas = [
            {"message": {"role": "assistant", "content": "Se pierde la calidad de alumno por resolución disciplinaria del Reglamento de Conducta."}},
            {"message": {"role": "assistant", "content": "[RG-ART-051]"}},
        ]
        asistente = AsistenteUdeC(
            config=ConfigAsistente(modelo="qwen3:4b-instruct", usar_embeddings=False),
            buscador=buscador,
            cliente_chat=lambda _p: respuestas.pop(0),
        )
        res = asistente.responder("¿Cómo se pierde la calidad de alumno disciplinariamente?")
        self.assertIn("resolución disciplinaria", res.respuesta)
        self.assertIn("[RG-ART-051]", res.respuesta)

    def test_normaliza_sufijo_guion_letra_sin_aceptar_inexistentes(self) -> None:
        corpus_ids = {"RI-FI-ART-014", "CAL-2026-S1-01"}
        texto, validas = normalizar_citas_respuesta(
            "Ver [RI-FI-ART-014-b], [RI-FI-ART-014.a], [CAL-2026-S1-01] y falso [RI-FI-ART-35].",
            corpus_ids,
        )
        self.assertIn("[RI-FI-ART-014]", texto)
        self.assertNotIn("[RI-FI-ART-014-b]", texto)
        self.assertNotIn("[RI-FI-ART-35]", texto)
        self.assertEqual(validas, ["RI-FI-ART-014", "CAL-2026-S1-01"])

    def test_solo_citas_dispara_reparacion_y_recupera_prosa(self) -> None:
        buscador = BuscadorNormativa(usar_embeddings=False)
        respuestas = [
            {"message": {"role": "assistant", "content": "[RG-ART-051]"}},
            {
                "message": {
                    "role": "assistant",
                    "content": "La calidad de alumno se pierde disciplinariamente por resolución firme de expulsión.",
                }
            },
        ]
        asistente = AsistenteUdeC(
            config=ConfigAsistente(modelo="qwen3:4b-instruct", usar_embeddings=False),
            buscador=buscador,
            cliente_chat=lambda _p: respuestas.pop(0),
        )
        res = asistente.responder("¿Cómo se pierde la calidad de alumno disciplinariamente?")
        self.assertIn("expulsión", res.respuesta)
        self.assertIn("[RG-ART-051]", res.respuesta)
        self.assertGreaterEqual(res.turnos_modelo, 2)

        respuestas_con_citas = [
            {"message": {"role": "assistant", "content": "[RG-ART-051]"}},
            {
                "message": {
                    "role": "assistant",
                    "content": "La calidad de alumno se pierde disciplinariamente por resolución firme de expulsión [RG-ART-051].",
                }
            },
        ]
        asistente2 = AsistenteUdeC(
            config=ConfigAsistente(modelo="qwen3:4b-instruct", usar_embeddings=False),
            buscador=buscador,
            cliente_chat=lambda _p: respuestas_con_citas.pop(0),
        )
        res2 = asistente2.responder("¿Cómo se pierde la calidad de alumno disciplinariamente?")
        self.assertIn("expulsión", res2.respuesta)
        self.assertIn("[RG-ART-051]", res2.respuesta)
        self.assertNotIn("Fuente: [RG-ART-051]", res2.respuesta)

    def test_verificacion_previa_articulo_inexistente_por_documento(self) -> None:
        buscador = BuscadorNormativa(usar_embeddings=False)
        ch_42 = buscador.verificar_articulos_mencionados(
            "¿Qué requisitos fija el Artículo 36 del Reglamento Interno de Docencia de Pregrado de Ingeniería?"
        )
        self.assertEqual(len(ch_42), 1)
        self.assertEqual(ch_42[0]["doc"], "RI-FI")
        self.assertEqual(ch_42[0]["numero"], 36)
        self.assertFalse(ch_42[0]["existe"])
        self.assertEqual(ch_42[0]["max_articulo"], 35)

        ch_mixto = buscador.verificar_articulos_mencionados(
            "En el Reglamento General (Art. 36) y el Artículo 36 del Reglamento Interno, ¿aplican igual?"
        )
        self.assertEqual({(c["doc"], c["numero"]): c["existe"] for c in ch_mixto}, {
            ("RG", 36): True,
            ("RI-FI", 36): False,
        })

        self.assertEqual(
            buscador.verificar_articulos_mencionados("¿Qué dice el Art. 2° Transitorio y el Art. 36 del PDF que subí?"),
            [],
        )
        solo_pdfs = buscador.con_pdfs_usuario([], incluir_corpus_base=False)
        self.assertEqual(solo_pdfs.verificar_articulos_mencionados("Artículo 36 del Reglamento Interno"), [])

        payloads: list[dict] = []

        def fake_chat(payload: dict) -> dict:
            payloads.append(payload)
            return {
                "message": {
                    "role": "assistant",
                    "content": "El Artículo 36 del Reglamento Interno (RI-FI) no existe; el reglamento llega hasta el Art. 35.",
                }
            }

        asistente = AsistenteUdeC(
            config=ConfigAsistente(modelo="qwen3:4b-instruct", usar_embeddings=False),
            buscador=buscador,
            cliente_chat=fake_chat,
        )
        res = asistente.responder(
            "¿Qué requisitos fija el Artículo 36 del Reglamento Interno de Docencia de Pregrado de Ingeniería?"
        )
        self.assertIn("NO existe en RI-FI", payloads[0]["messages"][1]["content"])
        self.assertEqual(res.pasos_herramientas[0].nombre, "existe_articulo")
        self.assertFalse(res.pasos_herramientas[0].resultado["existe"])


if __name__ == "__main__":
    unittest.main()
