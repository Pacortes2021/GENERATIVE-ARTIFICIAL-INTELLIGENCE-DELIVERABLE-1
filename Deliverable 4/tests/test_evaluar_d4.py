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
NOTEBOOK_EVAL_PATH = DELIVERABLE4_DIR / "D4_colab_evaluacion.ipynb"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import evaluar_d4 as ed  # noqa: E402


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
        for flag in ("--hf-repo", "--output-dir", "--qids", "--solo-comparativa", "--comparar-ids"):
            self.assertIn(flag, flags_validos)
            self.assertIn(flag, codigo)


if __name__ == "__main__":
    unittest.main()
