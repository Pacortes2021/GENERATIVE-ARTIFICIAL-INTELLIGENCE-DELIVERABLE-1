"""Tests unitarios deterministas para PDFs dinámicos, historial local y evaluador RAGAS."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from asistente_local.asistente import AsistenteUdeC
from asistente_local.buscador import BuscadorNormativa
from asistente_local.config import REPO_ROOT, ConfigAsistente
from asistente_local.evaluador import (
    evaluar_caso_determinista,
    juzgar_fidelidad_llm,
    resumir_evaluacion_benchmark,
)
from asistente_local.historial import (
    cargar_chat,
    eliminar_chat,
    exportar_chat_markdown,
    guardar_chat,
    listar_chats,
)
from asistente_local.pdfs import (
    cargar_o_calcular_vectores_pdf,
    construir_unidades_pdf,
    extraer_paginas_pdf,
)
from asistente_local.verificador import (
    necesita_revision_selectiva,
    verificar_y_corregir_respuesta,
)


class TestPDFsDinamicos(unittest.TestCase):
    def test_extraer_y_fragmentar_pdf_real(self) -> None:
        pdf_path = REPO_ROOT / "Corpus" / "Reglamento_de_Docencia_de_Pregrado-FI.pdf"
        raw = pdf_path.read_bytes()
        paginas = extraer_paginas_pdf(raw, nombre_archivo=pdf_path.name)
        self.assertGreaterEqual(len(paginas), 5)
        self.assertTrue(any("Artículo" in p["texto"] for p in paginas))

        pack = construir_unidades_pdf(raw, nombre_archivo=pdf_path.name, max_chars=700, solapamiento=100)
        self.assertEqual(pack["documento"], f"PDF:{pdf_path.name}")
        self.assertGreaterEqual(len(pack["unidades"]), len(paginas))
        self.assertEqual(len(pack["unidades"]), len(pack["fragmentos"]))
        uid0 = pack["unidades"][0]["id"]
        self.assertRegex(uid0, r"^PDF-[A-Z0-9]+-P\d{2}-\d{2}$")

    def test_rechaza_pdf_vacio_o_corrupto(self) -> None:
        with self.assertRaises(ValueError):
            extraer_paginas_pdf(b"", "vacio.pdf")
        with self.assertRaises(ValueError):
            extraer_paginas_pdf(b"esto-no-es-un-pdf", "malo.pdf")

    def test_cache_vectores_pdf_en_disco(self) -> None:
        import numpy as np

        pdf_path = REPO_ROOT / "Corpus" / "Calendario-Academico-Pregrado-2026.pdf"
        pack = construir_unidades_pdf(pdf_path.read_bytes(), nombre_archivo=pdf_path.name)
        llamadas = {"n": 0}

        class _FakeEncoder:
            def encode(self, textos, **_kwargs):
                llamadas["n"] += 1
                return np.ones((len(textos), 8), dtype=np.float32)

        with tempfile.TemporaryDirectory() as tmp:
            m1 = cargar_o_calcular_vectores_pdf(pack, _FakeEncoder(), Path(tmp))
            m2 = cargar_o_calcular_vectores_pdf(pack, _FakeEncoder(), Path(tmp))
            self.assertEqual(llamadas["n"], 1)
            self.assertEqual(m1.shape[0], len(pack["fragmentos"]))
            self.assertTrue(np.allclose(m1, m2))


class TestHistorialChats(unittest.TestCase):
    def test_ciclo_completo_y_export_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            msgs = [
                {"role": "user", "content": "¿Cuántos créditos exige el Art. 14?"},
                {
                    "role": "assistant",
                    "content": "Exige al menos 15 créditos al segundo semestre [RI-FI-ART-014].",
                    "meta": {
                        "modelo": "qwen3:4b-instruct",
                        "segundos": 12.4,
                        "turnos": 1,
                        "herramientas": [],
                        "fuentes": [{"id": "RI-FI-ART-014", "texto": "Artículo 14°..."}],
                    },
                },
            ]
            guardar_chat("sesion_1", msgs, base_dir=base)
            lista = listar_chats(base_dir=base)
            self.assertEqual(len(lista), 1)
            self.assertEqual(lista[0]["id"], "sesion_1")
            cargado = cargar_chat("sesion_1", base_dir=base)
            self.assertIsNotNone(cargado)
            self.assertEqual(len(cargado["mensajes"]), 2)

            md = exportar_chat_markdown(msgs, titulo="Prueba UdeC")
            self.assertIn("# Prueba UdeC", md)
            self.assertIn("[RI-FI-ART-014]", md)
            self.assertTrue(eliminar_chat("sesion_1", base_dir=base))
            self.assertIsNone(cargar_chat("sesion_1", base_dir=base))


class TestEvaluadorRAGAS(unittest.TestCase):
    def test_metricas_deterministas_y_juez_mock(self) -> None:
        unidades = {
            "RI-FI-ART-014": {
                "id": "RI-FI-ART-014",
                "texto": "Artículo 14. Aprobar menos de 15 créditos o promedio inferior a 10 créditos.",
            }
        }
        caso = {
            "id": "H06",
            "pregunta": "¿Cae en baja con promedio inferior a 10 créditos?",
            "gold_dato": "Promedio inferior a 10 créditos.",
            "gold_fuente": "RI-FI-ART-014",
            "respuesta": "Sí, si el promedio es inferior a 10 créditos cae en baja [RI-FI-ART-014].",
            "fuentes_ids": ["RI-FI-ART-014"],
            "citas_validas": ["RI-FI-ART-014"],
            "citas_inexistentes": [],
            "segundos": 15.0,
        }
        det = evaluar_caso_determinista(caso, unidades)
        self.assertEqual(det["recall_contexto"], 1.0)
        self.assertEqual(det["recall_citas"], 1.0)
        self.assertEqual(det["cobertura_numerica"], 1.0)
        self.assertGreater(det["respaldo_lexico"], 0.6)

        resumen = resumir_evaluacion_benchmark([caso], unidades)
        self.assertEqual(resumen["total"], 1)
        self.assertEqual(resumen["citas_inexistentes_totales"], 0)

        def fake_judge(_payload):
            return {
                "message": {
                    "content": json.dumps(
                        {
                            "afirmaciones": [
                                {"texto": "Promedio inferior a 10 cae en baja", "respaldada": True},
                                {"texto": "Dato extra inventado", "respaldada": False},
                            ],
                            "no_respaldadas": ["Dato extra inventado"],
                        }
                    )
                }
            }

        juez = juzgar_fidelidad_llm(
            caso["pregunta"],
            unidades["RI-FI-ART-014"]["texto"],
            caso["respuesta"],
            cliente_chat=fake_judge,
        )
        self.assertEqual(juez["afirmaciones_totales"], 2)
        self.assertEqual(juez["afirmaciones_respaldadas"], 1)
        self.assertAlmostEqual(juez["faithfulness_score"], 0.5)
        self.assertFalse(juez["parse_incompleto"])

        juez_trunc = juzgar_fidelidad_llm(
            caso["pregunta"],
            unidades["RI-FI-ART-014"]["texto"],
            caso["respuesta"],
            cliente_chat=lambda _p: {
                "message": {
                    "content": '{"afirmaciones": [{"texto": "A", "respaldada": true}, {"texto": "B", "respaldada": false}, {"texto": "C truncada'
                }
            },
        )
        self.assertTrue(juez_trunc["parse_incompleto"])
        self.assertEqual(juez_trunc["afirmaciones_totales"], 2)
        self.assertAlmostEqual(juez_trunc["faithfulness_score"], 0.5)


class TestVerificadorSelectivo(unittest.TestCase):
    def test_compuerta_y_correccion_segura(self) -> None:
        fuentes = [{"id": "RG-ART-057", "texto": "Requisitos: 1) alumno regular, 2) licenciado, 3) aceptado, 4) proposición."}]
        debe_no, _ = necesita_revision_selectiva(
            "¿Cuál es la nota mínima?",
            "La nota es 4,0 [RI-FI-ART-011].",
            ["RI-FI-ART-011"],
            fuentes,
        )
        self.assertFalse(debe_no)

        debe_si, motivo = necesita_revision_selectiva(
            "¿Qué condiciones exige el Art. 57?",
            "Ser regular y licenciado [RG-ART-057].",
            ["RG-ART-057"],
            fuentes,
        )
        self.assertTrue(debe_si)
        self.assertEqual(motivo, "pregunta_multiclausula_o_requisitos")

        cfg = ConfigAsistente()
        ok_res = verificar_y_corregir_respuesta(
            "¿Qué condiciones exige?",
            "Borrador completo [RG-ART-057].",
            ["RG-ART-057"],
            fuentes,
            cfg,
            cliente_chat=lambda _p: {"message": {"content": '{"completo": true, "fiel": true, "hallazgo": "ok", "respuesta_corregida": ""}'}},
        )
        self.assertFalse(ok_res["modificada"])
        self.assertEqual(ok_res["respuesta"], "Borrador completo [RG-ART-057].")

        fix_res = verificar_y_corregir_respuesta(
            "¿Qué condiciones exige?",
            "Faltan puntos [RG-ART-057].",
            ["RG-ART-057"],
            fuentes,
            cfg,
            cliente_chat=lambda _p: {
                "message": {
                    "content": json.dumps(
                        {
                            "completo": False,
                            "fiel": True,
                            "hallazgo": "faltaban 2 requisitos",
                            "respuesta_corregida": "Exige ser alumno regular, licenciado, aceptado en postgrado y proposición [RG-ART-057].",
                        }
                    )
                }
            },
        )
        self.assertTrue(fix_res["modificada"])
        self.assertIn("proposición", fix_res["respuesta"])

        bad_json = verificar_y_corregir_respuesta(
            "¿Qué condiciones exige?",
            "Borrador original intacto [RG-ART-057].",
            ["RG-ART-057"],
            fuentes,
            cfg,
            cliente_chat=lambda _p: {"message": {"content": "no es json"}},
        )
        self.assertFalse(bad_json["modificada"])
        self.assertEqual(bad_json["respuesta"], "Borrador original intacto [RG-ART-057].")


class TestIntegracionPDFsYMultiturno(unittest.TestCase):
    def _pack_pdf_sintetico(self) -> dict:
        uid = "PDF-SILABOABCD-P01-01"
        texto = "[silabo_robotica.pdf, pág. 1]\nEl taller de robótica exige asistencia de 85% y nota mínima 5,0."
        return {
            "nombre_archivo": "silabo_robotica.pdf",
            "documento": "PDF:silabo_robotica.pdf",
            "sha256": "abcd1234abcd1234abcd1234abcd1234",
            "paginas_con_texto": 1,
            "unidades": [
                {
                    "id": uid,
                    "parent_id": uid,
                    "documento": "PDF:silabo_robotica.pdf",
                    "archivo": "silabo_robotica.pdf",
                    "paginas": [1],
                    "texto": texto,
                    "es_pdf_usuario": True,
                }
            ],
            "fragmentos": [
                {
                    "id": f"{uid}-F01",
                    "unidad_id": uid,
                    "parent_id": uid,
                    "texto": texto,
                    "texto_embedding": f"passage: [{uid}] {texto}",
                }
            ],
        }

    def test_con_pdfs_usuario_combinado_y_solo_pdfs_con_mock_e5(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = BuscadorNormativa(cache_dir=Path(tmp), usar_embeddings=False)
            vacio_pdf = base.con_pdfs_usuario([], incluir_corpus_base=False)
            self.assertTrue(vacio_pdf.solo_pdfs)
            self.assertEqual(vacio_pdf.buscar("robótica"), [])

            pack = self._pack_pdf_sintetico()
            comb = base.con_pdfs_usuario([pack], incluir_corpus_base=True)
            self.assertTrue(comb.tiene_pdfs_usuario)
            self.assertFalse(comb.solo_pdfs)
            hits_comb = comb.buscar("taller de robótica asistencia", k=4, modo_fusion="rrf")
            self.assertTrue(any(h["id"] == "PDF-SILABOABCD-P01-01" for h in hits_comb))

            solo = base.con_pdfs_usuario([pack], incluir_corpus_base=False)
            self.assertTrue(solo.solo_pdfs)
            self.assertEqual(len(solo.unidades), 1)
            self.assertEqual(solo.buscar("baja académica", documento="RG"), [])
            hits_solo = solo.buscar("asistencia mínima robótica", k=3, modo_fusion="rrf")
            self.assertEqual(hits_solo[0]["id"], "PDF-SILABOABCD-P01-01")

            # Verifica apilado de vectores E5 en caché con encoder mock sin red
            class _FakeE5:
                def encode(self, textos, normalize_embeddings=True, batch_size=32, show_progress_bar=False):
                    return np.tile(np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float32), (len(textos), 1))

            base.usar_embeddings = True
            base._e5 = _FakeE5()
            base._matriz_e5 = np.tile(
                np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float32),
                (len(base.fragmentos), 1),
            )
            comb_e5 = base.con_pdfs_usuario([pack], incluir_corpus_base=True)
            self.assertEqual(comb_e5._matriz_e5.shape[0], len(comb_e5.fragmentos))
            hits_e5 = comb_e5.buscar("nota mínima taller robótica", k=4, modo_fusion="rrf")
            self.assertTrue(len(hits_e5) >= 1)

    def test_asistente_multiturno_y_prompt_pdfs(self) -> None:
        base = BuscadorNormativa(usar_embeddings=False)
        solo = base.con_pdfs_usuario([self._pack_pdf_sintetico()], incluir_corpus_base=False)
        payloads: list[dict] = []

        def fake_chat(payload: dict) -> dict:
            payloads.append(payload)
            return {
                "message": {
                    "role": "assistant",
                    "content": "Exige 85% de asistencia en el taller [silabo_robotica.pdf p. 1] [PDF-SILABOABCD-P01-01].",
                }
            }

        asistente = AsistenteUdeC(
            config=ConfigAsistente(modelo="qwen3:4b-instruct", usar_embeddings=False),
            buscador=solo,
            cliente_chat=fake_chat,
        )
        res = asistente.responder(
            "¿Y cuánta asistencia pide?",
            historial=[
                {"role": "user", "content": "¿Qué exige el taller de robótica?"},
                {"role": "assistant", "content": "Exige nota mínima 5,0 [PDF-SILABOABCD-P01-01]."},
            ],
        )
        self.assertIn("MODO SOLO PDFs DEL USUARIO", payloads[0]["messages"][0]["content"])
        self.assertIn("[PDF-SILABOABCD-P01-01]", res.respuesta)
        self.assertIn("[silabo_robotica.pdf p. 1]", res.respuesta)


if __name__ == "__main__":
    unittest.main()
