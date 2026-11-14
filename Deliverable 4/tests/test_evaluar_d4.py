"""Pruebas unitarias del evaluador multi-agente D4 sin requerir GPU CUDA."""

from __future__ import annotations

import ast
import contextlib
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import torch

DELIVERABLE4_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = DELIVERABLE4_DIR / "scripts"
VIDEO_DIR = DELIVERABLE4_DIR / "video"
NOTEBOOK_EVAL_PATH = DELIVERABLE4_DIR / "D4_colab_evaluacion.ipynb"
NOTEBOOK_VIDEO_PATH = DELIVERABLE4_DIR / "D4_colab_video_demo.ipynb"

for _p in (SCRIPTS_DIR, VIDEO_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import evaluar_d4 as ed  # noqa: E402
import generar_auditoria_d4 as ga  # noqa: E402
import mostrar_demo_d4 as demo  # noqa: E402


class _BatchEncoding(dict):
    def to(self, _device: object) -> "_BatchEncoding":
        return self


class _DummyTokenizer:
    eos_token_id = 0

    def __init__(self) -> None:
        self._respuestas: list[str] = []

    def apply_chat_template(
        self,
        msgs: list[dict[str, str]],
        tokenize: bool = False,
        add_generation_prompt: bool = True,
        enable_thinking: bool = False,
    ) -> str:
        assert not tokenize and add_generation_prompt and not enable_thinking
        return msgs[0]["content"]

    def __call__(self, text: str, return_tensors: str = "pt") -> _BatchEncoding:
        assert return_tensors == "pt"
        if "Eres el agente ENRUTADOR" in text:
            prompt_id = 1
        elif "Eres el agente RECUPERADOR" in text:
            prompt_id = 2
        elif "Eres el agente VERIFICADOR" in text:
            prompt_id = 4
        else:
            prompt_id = 3
        input_ids = torch.tensor([[100, prompt_id]], dtype=torch.long)
        return _BatchEncoding(input_ids=input_ids, attention_mask=torch.ones_like(input_ids))

    def registrar_salida(self, texto: str) -> list[int]:
        idx = len(self._respuestas) + 1000
        self._respuestas.append(texto)
        return [idx]

    def decode(self, gen_ids: torch.Tensor, skip_special_tokens: bool = True) -> str:
        assert skip_special_tokens
        idx = int(gen_ids[0].item()) - 1000
        return self._respuestas[idx]


class _DummyPeftModel:
    device = torch.device("cpu")
    active_adapters = ["default"]

    def __init__(self, tok: _DummyTokenizer, fuerza_rechazo_primera_vez: bool = False) -> None:
        self.tok = tok
        self.adapter_disabled = False
        self.calls: list[dict[str, object]] = []
        self._redactor_calls = 0
        self._verificador_calls = 0
        self._fuerza_rechazo_primera_vez = fuerza_rechazo_primera_vez
        self.logits_identicos = False

    @contextlib.contextmanager
    def disable_adapter(self):
        prev = self.adapter_disabled
        self.adapter_disabled = True
        try:
            yield
        finally:
            self.adapter_disabled = prev

    def __call__(self, input_ids: torch.Tensor, **_kwargs: object) -> SimpleNamespace:
        val = 1.0 if (self.adapter_disabled or self.logits_identicos) else 2.5
        logits = torch.full((1, input_ids.shape[1], 8), val)
        return SimpleNamespace(logits=logits)

    def generate(self, input_ids: torch.Tensor, **_kwargs: object) -> torch.Tensor:
        prompt_tipo = int(input_ids[0, 1].item())
        self.calls.append({"prompt_tipo": prompt_tipo, "adapter_disabled": self.adapter_disabled})

        if prompt_tipo == 1:
            texto = '{"tipo":"factual","sub_consultas":["nota minima aprobar"],"documentos":["RI-FI"]}'
        elif prompt_tipo == 2:
            texto = '{"accion":"suficiente","args":{}}'
        elif prompt_tipo == 4:
            self._verificador_calls += 1
            if self._fuerza_rechazo_primera_vez and self._verificador_calls == 1:
                texto = '{"aprobado":false,"destino":"redactor","motivo":"precisar escala"}'
            else:
                texto = '{"aprobado":true,"destino":"fin","motivo":"respaldado"}'
        else:
            self._redactor_calls += 1
            marca = "BASE" if self.adapter_disabled else "LORA"
            texto = (
                "<pensar>Verificado.</pensar>\n"
                f"Respuesta: [{marca}] La nota mínima es 4,0 [RI-FI-ART-011].\n"
                "Condiciones o límites: Escala de 1 a 7.\n"
                "Fuente: [RI-FI-ART-011]"
            )

        out_toks = self.tok.registrar_salida(texto)
        gen = torch.tensor([out_toks], dtype=torch.long)
        return torch.cat([input_ids, gen], dim=1)


class TestEvaluarD4(unittest.TestCase):
    def test_carga_75_preguntas_y_filtro_qids(self) -> None:
        todas = ed.cargar_preguntas_evaluacion()
        self.assertEqual(len(todas), 75)
        self.assertEqual(sum(1 for p in todas if p["set"] == "congelado_50"), 50)
        self.assertEqual(sum(1 for p in todas if p["set"] == "dificil_25"), 25)
        self.assertEqual(todas[0]["id"], "1")
        self.assertEqual(todas[-1]["id"], "H25")

        sub = ed.cargar_preguntas_evaluacion(filtro_qids={"congelado_50:1", "dificil_25:H03"})
        self.assertEqual([p["qid"] for p in sub], ["congelado_50:1", "dificil_25:H03"])

        with self.assertRaises(ValueError):
            ed.cargar_preguntas_evaluacion(filtro_qids={"congelado_50:999"})

    def test_aislamiento_adaptador_solo_redactor_en_orquestador_real(self) -> None:
        ed.verificar_prompts_d4()
        corpus = ed.construir_corpus_d3(use_e5=False)
        tok = _DummyTokenizer()
        model = _DummyPeftModel(tok, fuerza_rechazo_primera_vez=True)

        aislamiento = ed.verificar_aislamiento_adaptador(model, tok)
        self.assertGreater(aislamiento["max_abs_logit_diff"], 0.0)

        model.logits_identicos = True
        with self.assertRaises(RuntimeError):
            ed.verificar_aislamiento_adaptador(model, tok)
        model.logits_identicos = False

        generador = ed.AdaptadorRedactorGenerator(model, tok, greedy=True, solo_base=False)
        orq = ed.crear_orquestador_d4(corpus, generador)
        res = orq.responder("¿Cuál es la nota mínima para aprobar una asignatura?")

        self.assertEqual(res["ciclos"], 2)
        self.assertIn("[LORA]", res["respuesta"])
        self.assertFalse(model.adapter_disabled)

        red_calls = [c for c in generador.telemetria if c["agente"] == "redactor"]
        otros_calls = [c for c in generador.telemetria if c["agente"] != "redactor"]
        self.assertEqual(len(red_calls), 2)
        self.assertTrue(all(c["usa_adaptador"] for c in red_calls))
        self.assertGreaterEqual(len(otros_calls), 3)
        self.assertTrue(all(not c["usa_adaptador"] for c in otros_calls))

        # Verificar a nivel de llamadas en _DummyPeftModel también
        self.assertTrue(all(not c["adapter_disabled"] for c in model.calls if c["prompt_tipo"] == 3))
        self.assertTrue(all(c["adapter_disabled"] for c in model.calls if c["prompt_tipo"] != 3))

    def test_guardado_incremental_reanudacion_y_comparativa(self) -> None:
        corpus = ed.construir_corpus_d3(use_e5=False)
        tok = _DummyTokenizer()
        model = _DummyPeftModel(tok)
        generador = ed.AdaptadorRedactorGenerator(model, tok, greedy=False, solo_base=False)

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "eval"
            lote1 = ed.cargar_preguntas_evaluacion(filtro_qids={"congelado_50:1", "dificil_25:H01"})
            r1 = ed.ejecutar_evaluacion_lote(
                lote1,
                corpus,
                generador,
                out_dir,
                metadata_extra={"hf_adaptador_redactor": ed.HF_ADAPTER_DEFAULT},
                limpiar_cache_cuda_cada=0,
            )
            self.assertEqual(r1["nuevas_procesadas"], 2)
            self.assertEqual(r1["total_filas"], 2)

            calls_tras_lote1 = len(generador.telemetria)
            lote2 = ed.cargar_preguntas_evaluacion(
                filtro_qids={"congelado_50:1", "dificil_25:H01", "dificil_25:H03"}
            )
            r2 = ed.ejecutar_evaluacion_lote(
                lote2,
                corpus,
                generador,
                out_dir,
                limpiar_cache_cuda_cada=0,
            )
            self.assertEqual(r2["nuevas_procesadas"], 1)
            self.assertEqual(r2["total_filas"], 3)
            self.assertGreater(len(generador.telemetria), calls_tras_lote1)

            with (out_dir / "resultados_agentes_D4.csv").open("r", encoding="utf-8", newline="") as f:
                filas = list(csv.DictReader(f))
            self.assertEqual(len(filas), 3)
            self.assertEqual([f["id"] for f in filas], ["1", "H01", "H03"])
            self.assertTrue(all(f["correcto"] == "" for f in filas))
            self.assertTrue(all(int(f["llamadas_redactor"]) >= 1 for f in filas))
            self.assertTrue(all(int(f["llamadas_base"]) >= 2 for f in filas))

            # Comparativa lado a lado Base vs Fine-tuned
            gen_base = ed.AdaptadorRedactorGenerator(model, tok, greedy=True, solo_base=True)
            gen_ft = ed.AdaptadorRedactorGenerator(model, tok, greedy=True, solo_base=False)
            comp_path = out_dir / "comparativa_base_vs_finetuned.json"
            comp = ed.ejecutar_comparativa_base_vs_finetuned(
                lote1[:1], corpus, gen_base, gen_ft, comp_path
            )
            self.assertEqual(len(comp), 1)
            self.assertIn("[BASE]", comp[0]["base"]["respuesta"])
            self.assertIn("[LORA]", comp[0]["finetuned_redactor"]["respuesta"])
            self.assertTrue(all(not c["usa_adaptador"] for c in gen_base.telemetria))
            self.assertTrue(any(c["usa_adaptador"] for c in gen_ft.telemetria))

    def test_notebook_evaluacion_valido_y_coherente_con_cli(self) -> None:
        self.assertTrue(NOTEBOOK_EVAL_PATH.is_file())
        nb = json.loads(NOTEBOOK_EVAL_PATH.read_text(encoding="utf-8"))
        self.assertEqual(nb["nbformat"], 4)

        parser = ed.construir_arg_parser()
        flags_validos = {opt for act in parser._actions for opt in act.option_strings}

        fuentes = []
        for idx, celda in enumerate(nb["cells"]):
            if celda["cell_type"] != "code":
                continue
            src = "".join(celda["source"])
            fuentes.append(src)
            py_lines = [l for l in src.splitlines() if not l.lstrip().startswith("%")]
            ast.parse("\n".join(py_lines), filename=f"eval_cell_{idx}")

        codigo = "\n".join(fuentes)
        self.assertIn('"evaluar_d4.py"', codigo)
        self.assertIn("Pablox0333/qwen3-4b-redactor-udec-d4", codigo)
        self.assertIn('"huggingface-hub>=0.30,<2.0"', codigo)
        for flag in (
            "--hf-repo",
            "--output-dir",
            "--qids",
            "--solo-comparativa",
            "--comparar-ids",
            "--solo-base",
            "--preguntas-csv",
            "--nombre-set",
            "--output-prefix",
        ):
            self.assertIn(flag, flags_validos)
            self.assertIn(flag, codigo)


class TestAuditoriaArtefactosD4(unittest.TestCase):
    def test_artefactos_evaluacion_y_auditoria_consistentes(self) -> None:
        eval_dir = DELIVERABLE4_DIR / "evaluacion"
        aud = json.loads((eval_dir / "auditoria_D4.json").read_text(encoding="utf-8"))
        fallos = json.loads(
            (eval_dir / "casos_fallo_y_regresion.json").read_text(encoding="utf-8")
        )
        with (eval_dir / "resultados_agentes_D4_auditados.csv").open(
            encoding="utf-8", newline=""
        ) as f:
            rows = list(csv.DictReader(f))

        self.assertEqual(len(rows), 75)
        self.assertTrue(all(r["correcto"] in {"0", "1"} for r in rows))

        cong_ok = sum(int(r["correcto"]) for r in rows if r["set"] == "congelado_50")
        dif_ok = sum(int(r["correcto"]) for r in rows if r["set"] == "dificil_25")
        rg = aud["resumen_global"]
        self.assertEqual(cong_ok, rg["congelado_50"]["aciertos_estrictos"])
        self.assertEqual(dif_ok, rg["dificil_25"]["aciertos_estrictos"])
        self.assertEqual(cong_ok + dif_ok, rg["global_75"]["aciertos_estrictos"])
        self.assertEqual(aud["telemetria_y_aislamiento"]["violaciones_aislamiento_lora"], 0)
        self.assertEqual(
            sum(aud["comparacion_d3_a_d4"]["transiciones_vs_d3"].values()), 75
        )
        qids_fallos = {c["qid"] for c in fallos["casos"]}
        self.assertTrue(
            {"dificil_25:H03", "dificil_25:H04", "dificil_25:H06", "congelado_50:36"}.issubset(
                qids_fallos
            )
        )
        for caso in fallos["casos"]:
            self.assertGreater(len(caso["traza_completa"]), 0)
            self.assertGreater(len(caso["telemetria"]), 0)

        for fname, exp_total, exp_ok in (
            ("auditoria_control_base_D4.json", 75, 62),
            ("auditoria_nuevas20_ft_D4.json", 20, 10),
            ("auditoria_nuevas20_base_D4.json", 20, 11),
        ):
            p_aud = eval_dir / fname
            self.assertTrue(p_aud.is_file(), f"Falta auditoría v2: {fname}")
            d_aud = json.loads(p_aud.read_text(encoding="utf-8"))
            self.assertEqual(d_aud["total_preguntas"], exp_total)
            self.assertEqual(d_aud["aciertos_humanos"], exp_ok)
            self.assertEqual(d_aud["telemetria_y_aislamiento"]["violaciones_aislamiento_lora"], 0)

    def test_generar_auditoria_determinista_en_directorio_temporal(self) -> None:
        eval_dir = DELIVERABLE4_DIR / "evaluacion"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_eval = Path(tmp)
            for fname in (
                "resultados_agentes_D4.csv",
                "trazas_D4.json",
                "telemetria_llamadas.json",
                "comparativa_base_vs_finetuned.json",
                "configuracion_evaluacion.json",
            ):
                (tmp_eval / fname).write_bytes((eval_dir / fname).read_bytes())
            res = ga.generar_auditoria(eval_dir=tmp_eval)
            self.assertEqual(res["resumen_global"]["global_75"]["aciertos_estrictos"], 60)
            self.assertTrue((tmp_eval / "resultados_agentes_D4_auditados.csv").exists())
            self.assertTrue((tmp_eval / "casos_fallo_y_regresion.json").exists())


class TestDemoVideoD4(unittest.TestCase):
    def test_etiqueta_adaptador_y_formato_comparativa_y_fallo(self) -> None:
        self.assertEqual(demo.etiqueta_adaptador("redactor", solo_base=False), "LoRA ON (Redactor FT)")
        self.assertEqual(demo.etiqueta_adaptador("redactor", solo_base=True), "LoRA OFF (Base)")
        self.assertEqual(demo.etiqueta_adaptador("verificador", solo_base=False), "LoRA OFF (Base)")

        comparativas = demo.cargar_comparativas()
        self.assertIn("dificil_25:H07", comparativas)
        txt = demo.formatear_comparativa_texto(comparativas["dificil_25:H07"])
        self.assertIn("SISTEMA BASE D3", txt)
        self.assertIn("SISTEMA D4 FINE-TUNED", txt)
        self.assertIn("REDACTOR · LoRA ON (Redactor FT)", txt)
        self.assertIn("42 / 4 = 10,5", txt)

        html_card = demo.renderizar_comparativa_html(comparativas["dificil_25:H07"])
        self.assertIn("Mensajes intermedios", html_card)
        self.assertIn("LoRA ON (Redactor FT)", html_card)

        fallos = demo.cargar_fallos()
        self.assertIn("dificil_25:H06", fallos)
        txt_fallo = demo.formatear_fallo_texto(fallos["dificil_25:H06"])
        self.assertIn("ANÁLISIS DE FALLO dificil_25:H06", txt_fallo)
        self.assertIn("VERIFICADOR · LoRA OFF (Base)", txt_fallo)

    def test_cli_demo_y_notebook_video_valido(self) -> None:
        self.assertEqual(demo.main(["--listar"]), 0)
        with self.assertRaises(ValueError):
            demo.main(["--qid", "qid_inexistente:999"])

        nb = json.loads(NOTEBOOK_VIDEO_PATH.read_text(encoding="utf-8"))
        self.assertEqual(nb.get("nbformat"), 4)
        src_total = "\n".join("".join(c.get("source", [])) for c in nb.get("cells", []))
        self.assertIn("mostrar_demo_d4", src_total)
        self.assertIn("dificil_25:H07", src_total)

    def test_preguntas_nuevas_20_control_solo_base_y_auditoria_general(self) -> None:
        nuevas_csv = DELIVERABLE4_DIR / "datos" / "preguntas_nuevas_20.csv"
        self.assertTrue(nuevas_csv.is_file())
        preguntas_n20 = ed.cargar_preguntas_desde_csv(nuevas_csv, nombre_set="nuevas_20")
        self.assertEqual(len(preguntas_n20), 20)
        self.assertEqual(preguntas_n20[0]["qid"], "nuevas_20:N01")
        self.assertEqual(preguntas_n20[-1]["qid"], "nuevas_20:N20")

        sub_n20 = ed.cargar_preguntas_desde_csv(
            nuevas_csv,
            nombre_set="nuevas_20",
            filtro_qids={"nuevas_20:N01", "nuevas_20:N19"},
        )
        self.assertEqual([p["qid"] for p in sub_n20], ["nuevas_20:N01", "nuevas_20:N19"])
        with self.assertRaises(ValueError):
            ed.cargar_preguntas_desde_csv(nuevas_csv, filtro_qids={"nuevas_20:N999"})

        parser = ed.construir_arg_parser()
        flags_validos = {opt for act in parser._actions for opt in act.option_strings}
        for flag in ("--solo-base", "--preguntas-csv", "--nombre-set", "--output-prefix"):
            self.assertIn(flag, flags_validos)

        corpus = ed.construir_corpus_d3(use_e5=False)
        tok = _DummyTokenizer()
        model = _DummyPeftModel(tok)
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "eval_general"
            gen_ft = ed.AdaptadorRedactorGenerator(model, tok, greedy=True, solo_base=False)
            gen_base = ed.AdaptadorRedactorGenerator(model, tok, greedy=True, solo_base=True)

            ed.ejecutar_evaluacion_lote(
                sub_n20,
                corpus,
                gen_ft,
                out_dir,
                condicion="finetuned_redactor",
                metadata_extra={"condicion": "finetuned_redactor"},
                limpiar_cache_cuda_cada=0,
                output_prefix="nuevas20_ft_D4",
            )
            ed.ejecutar_evaluacion_lote(
                sub_n20,
                corpus,
                gen_base,
                out_dir,
                condicion="control_base_lora_apagado",
                metadata_extra={"condicion": "control_base_lora_apagado"},
                limpiar_cache_cuda_cada=0,
                output_prefix="nuevas20_base_D4",
            )
            self.assertTrue(all(not c["usa_adaptador"] for c in gen_base.telemetria))
            for fname in (
                "resultados_nuevas20_ft_D4.csv",
                "trazas_nuevas20_ft_D4.json",
                "telemetria_nuevas20_ft_D4.json",
                "configuracion_nuevas20_ft_D4.json",
                "resultados_nuevas20_base_D4.csv",
                "trazas_nuevas20_base_D4.json",
                "telemetria_nuevas20_base_D4.json",
                "configuracion_nuevas20_base_D4.json",
            ):
                p = out_dir / fname
                self.assertTrue(p.is_file(), f"Falta salida esperada: {fname}")
                self.assertNotIn(b"\r\n", p.read_bytes(), f"CRLF inesperado en {fname}")

            aud_ft = ga.generar_auditoria_general(
                eval_dir=out_dir,
                resultados_csv=out_dir / "resultados_nuevas20_ft_D4.csv",
                control_csv=out_dir / "resultados_nuevas20_base_D4.csv",
                prefijo_salida="nuevas20_ft_D4",
            )
            self.assertEqual(aud_ft["total_preguntas"], 2)
            self.assertEqual(aud_ft["pendientes_revision_humana"], 2)
            self.assertIsNone(aud_ft["aciertos_humanos"])
            self.assertEqual(aud_ft["telemetria_y_aislamiento"]["violaciones_aislamiento_lora"], 0)
            self.assertEqual(aud_ft["chequeos_deterministas"]["total_formato_3_lineas_ok"], 2)
            self.assertEqual(aud_ft["chequeos_deterministas"]["total_con_citas_inexistentes"], 0)
            comp = aud_ft["comparativa_control_base_vs_ft"]
            self.assertEqual(comp["preguntas_emparejadas"], 2)
            self.assertEqual(comp["respuestas_distintas_ft_vs_control"], 2)

            aud_base = ga.generar_auditoria_general(
                eval_dir=out_dir,
                resultados_csv=out_dir / "resultados_nuevas20_base_D4.csv",
                prefijo_salida="nuevas20_base_D4",
            )
            self.assertEqual(
                aud_base["telemetria_y_aislamiento"]["violaciones_aislamiento_lora"],
                0,
                "El modo control_base_lora_apagado no debe marcar falso aislamiento LoRA.",
            )
            corpus_ids = ga._cargar_corpus_ids(ga.DEFAULT_CORPUS_PATH)
            det_aluc = ga.auditar_fila_determinista(
                {
                    "respuesta_sistema": "Respuesta: Regla [RG-ART-999].\nCondiciones o límites: No aplica.\nFuente: [RG-ART-999]",
                    "fuentes_traidas": "RI-FI-ART-011",
                    "aprobado_verificador": "True",
                    "error": "",
                },
                corpus_ids,
            )
            self.assertEqual(det_aluc["citas_inexistentes_en_corpus"], ["RG-ART-999"])
            self.assertTrue(det_aluc["tiene_condicion_no_aplica"])


if __name__ == "__main__":
    unittest.main()
