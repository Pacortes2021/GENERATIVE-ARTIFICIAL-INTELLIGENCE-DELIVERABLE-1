"""Pruebas unitarias para el pipeline QLoRA (Paso 3) sin requerir GPU CUDA."""

from __future__ import annotations

import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path

import torch

DELIVERABLE4_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = DELIVERABLE4_DIR / "scripts"
DATOS_DIR = DELIVERABLE4_DIR / "datos"
NOTEBOOK_PATH = DELIVERABLE4_DIR / "D4_colab_entrenamiento.ipynb"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import entrenar_redactor as er  # noqa: E402


class TestPipelineEntrenamientoRedactor(unittest.TestCase):
    """Valida tokenización exacta, collator, graficado de curvas y notebook Colab."""

    def test_tokenizacion_sft_210_ejemplos_con_tokenizer_qwen3(self) -> None:
        from transformers import AutoTokenizer

        try:
            tok = AutoTokenizer.from_pretrained(er.MODELO_BASE_DEFAULT, local_files_only=True)
        except Exception:
            try:
                tok = AutoTokenizer.from_pretrained(er.MODELO_BASE_DEFAULT)
            except Exception as e:
                self.skipTest(f"Tokenizador {er.MODELO_BASE_DEFAULT} no disponible offline: {e}")

        if tok.pad_token_id is None:
            tok.pad_token = tok.eos_token

        train_rows = er.cargar_jsonl(DATOS_DIR / "redactor_train.jsonl")
        val_rows = er.cargar_jsonl(DATOS_DIR / "redactor_val.jsonl")
        todos = train_rows + val_rows
        self.assertEqual(len(todos), 210)

        ejemplos_sft = []
        for reg in todos:
            ex = er.construir_ejemplo_sft(reg, tok, max_seq_length=4096)
            ejemplos_sft.append(ex)

            self.assertFalse(ex["truncado"], f"Ejemplo truncado inesperadamente: {reg['id']}")
            p_len = ex["prompt_tokens"]
            self.assertEqual(ex["labels"][:p_len], [-100] * p_len)
            target_labels = ex["labels"][p_len:]
            self.assertTrue(all(t != -100 for t in target_labels))

            decodificado = tok.decode(target_labels, skip_special_tokens=False)
            self.assertEqual(
                decodificado,
                reg["messages"][1]["content"] + (tok.eos_token or ""),
                f"Desajuste de decodificación en {reg['id']}",
            )

        resumen_train = er.resumen_longitudes_sft(ejemplos_sft[:180])
        resumen_val = er.resumen_longitudes_sft(ejemplos_sft[180:])
        self.assertEqual(resumen_train["truncados"], 0)
        self.assertEqual(resumen_val["truncados"], 0)
        self.assertLessEqual(
            max(resumen_train["total_tokens"]["max"], resumen_val["total_tokens"]["max"]),
            4096,
        )

        # Collator sobre batch heterogéneo real
        collator = er.DataCollatorParaCompletado(pad_token_id=tok.pad_token_id)
        batch = collator([ejemplos_sft[0], ejemplos_sft[10], ejemplos_sft[190]])
        max_len = max(ejemplos_sft[0]["total_tokens"], ejemplos_sft[10]["total_tokens"], ejemplos_sft[190]["total_tokens"])
        self.assertEqual(tuple(batch["input_ids"].shape), (3, max_len))
        self.assertEqual(tuple(batch["attention_mask"].shape), (3, max_len))
        self.assertEqual(tuple(batch["labels"].shape), (3, max_len))
        self.assertEqual(batch["input_ids"].dtype, torch.long)
        self.assertEqual(batch["labels"].dtype, torch.long)

    def test_curvas_perdida_y_model_card(self) -> None:
        log_history = [
            {"loss": 1.42, "learning_rate": 5e-5, "epoch": 0.17, "step": 5},
            {"loss": 0.98, "learning_rate": 1e-4, "epoch": 0.33, "step": 10},
            {"loss": 0.74, "learning_rate": 9e-5, "epoch": 0.50, "step": 15},
            {"eval_loss": 0.81, "epoch": 0.50, "step": 15},
            {"loss": 0.58, "learning_rate": 6e-5, "epoch": 1.00, "step": 30},
            {"eval_loss": 0.69, "epoch": 1.00, "step": 30},
        ]
        curvas = er.extraer_curvas_de_log_history(log_history, eval_inicial={"eval_loss": 1.65})
        self.assertEqual([p["step"] for p in curvas["eval"]], [0, 15, 30])
        self.assertEqual([p["step"] for p in curvas["train"]], [5, 10, 15, 30])

        with tempfile.TemporaryDirectory() as tmp:
            png = Path(tmp) / "loss_curve.png"
            pdf = Path(tmp) / "loss_curve.pdf"
            er.graficar_curva_perdida(curvas, png, pdf, mejor_step=30)
            self.assertTrue(png.read_bytes().startswith(b"\x89PNG"))
            self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))

        card = er.generar_model_card(
            {
                "modelo_base": "Qwen/Qwen3-4B",
                "datos": {"train_ejemplos": 180, "val_ejemplos": 30},
                "hiperparametros": {
                    "lora_r": 16,
                    "lora_alpha": 32,
                    "lora_dropout": 0.05,
                    "target_modules": list(er.LORA_TARGET_MODULES_DEFAULT),
                    "epochs": 3.0,
                },
                "hardware": {"gpu": "Tesla T4", "vram_gb": 15.8, "compute_dtype": "torch.float16"},
                "resultados": {
                    "tiempo_entrenamiento_min": 14.5,
                    "pasos_totales": 90,
                    "eval_loss_inicial": 1.65,
                    "mejor_eval_loss": 0.69,
                    "mejor_step": 60,
                },
            },
            hf_repo="Pacortes2021/qwen3-4b-redactor-udec-d4",
        )
        self.assertIn("base_model: Qwen/Qwen3-4B", card)
        self.assertIn("library_name: peft", card)
        self.assertIn("Pacortes2021/qwen3-4b-redactor-udec-d4", card)

    def test_notebook_colab_valido_y_coherente_con_cli(self) -> None:
        self.assertTrue(NOTEBOOK_PATH.is_file())
        nb = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
        self.assertEqual(nb["nbformat"], 4)
        self.assertGreaterEqual(len(nb["cells"]), 8)

        parser = er.construir_arg_parser()
        flags_validos = {
            opt for action in parser._actions for opt in action.option_strings
        }

        fuente_completa = []
        for idx, celda in enumerate(nb["cells"]):
            if celda["cell_type"] != "code":
                continue
            src = "".join(celda["source"])
            fuente_completa.append(src)
            lineas_python = [
                l for l in src.splitlines() if not l.lstrip().startswith("%")
            ]
            ast.parse("\n".join(lineas_python), filename=f"cell_{idx}")

        codigo_total = "\n".join(fuente_completa)
        self.assertIn("Deliverable 4/scripts/entrenar_redactor.py", codigo_total)
        self.assertIn('"huggingface-hub>=0.30,<2.0"', codigo_total)
        for flag_usado in (
            "--train-jsonl",
            "--val-jsonl",
            "--output-dir",
            "--max-seq-length",
            "--epochs",
            "--grad-accum",
            "--eval-steps",
            "--save-steps",
        ):
            self.assertIn(flag_usado, flags_validos)
            self.assertIn(flag_usado, codigo_total)

        self.assertFalse(er.es_bf16_nativo((7, 5), True))
        self.assertTrue(er.es_bf16_nativo((8, 9), True))
        self.assertFalse(er.es_bf16_nativo((8, 0), False))


if __name__ == "__main__":
    unittest.main()
