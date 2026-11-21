"""Tests deterministas de antifuga, tokenización multi-turno y exportación Ollama del fine-tuning."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from asistente_local.finetune.antifuga import (
    BLOCKED_UNIT_IDS,
    validar_dataset_completo,
    validar_registro_sft,
)
from asistente_local.finetune.construir_dataset import construir_registros_sft
from asistente_local.finetune.entrenar_agente_sft import (
    construir_ejemplo_sft_multiturno,
    resumir_tokens_dataset,
)
from asistente_local.finetune.exportar_ollama import generar_modelfile


class _FakeTokenizer:
    """Simula `apply_chat_template` de Qwen3 en forma determinista para tests sin red."""

    eos_token = "<|im_end|>"
    pad_token_id = 0

    def apply_chat_template(
        self,
        msgs: list[dict],
        tools=None,
        add_generation_prompt: bool = False,
        tokenize: bool = False,
    ):
        partes: list[str] = []
        if tools:
            partes.append(f"<tools>{len(tools)}</tools>")
        for m in msgs:
            role = m["role"]
            if role == "tool":
                partes.append(f"<|im_start|>user\n<tool_response>{m['content']}</tool_response><|im_end|>")
            elif role == "assistant" and m.get("tool_calls"):
                tc = json.dumps(m["tool_calls"], ensure_ascii=False)
                partes.append(f"<|im_start|>assistant\n<tool_call>{tc}</tool_call><|im_end|>")
            else:
                partes.append(f"<|im_start|>{role}\n{m.get('content', '')}<|im_end|>")
        if add_generation_prompt:
            partes.append("<|im_start|>assistant\n")
        txt = "\n".join(partes)
        if not tokenize:
            return txt
        return [ord(ch) for ch in txt]


class TestFinetuneAgente(unittest.TestCase):
    def test_antifuga_rechaza_unidades_bloqueadas_citas_sin_respaldo_y_clones(self) -> None:
        ejemplo_fuga = {
            "id": "BAD-01",
            "split": "train",
            "categoria": "tool_calcular",
            "messages": [
                {"role": "system", "content": "Sistema."},
                {"role": "user", "content": "Contexto [RI-FI-ART-014]"},
                {"role": "assistant", "content": "Cita [RI-FI-ART-014] y falsa [RG-ART-999]."},
            ],
        }
        errs = validar_registro_sft(ejemplo_fuga, preguntas_95=[])
        self.assertTrue(any("fuga de unidades bloqueadas" in e for e in errs))
        self.assertTrue(any("no respaldada" in e for e in errs))

        ejemplo_clon = {
            "id": "BAD-02",
            "split": "train",
            "categoria": "factual",
            "messages": [
                {"role": "system", "content": "Sistema."},
                {"role": "user", "content": "¿Cuál es la nota mínima para aprobar una asignatura en la Facultad de Ingeniería?"},
                {"role": "assistant", "content": "Es 4,0."},
            ],
        }
        errs_clon = validar_registro_sft(
            ejemplo_clon,
            preguntas_95=[
                {
                    "dataset": "congelado_50",
                    "id": "1",
                    "pregunta": "¿Cuál es la nota mínima para aprobar una asignatura en la Facultad de Ingeniería?",
                }
            ],
        )
        self.assertTrue(any("demasiado similar" in e for e in errs_clon))

    def test_dataset_generado_cumple_antifuga_y_splits_disjuntos(self) -> None:
        registros = construir_registros_sft()
        self.assertGreaterEqual(len(registros), 80)
        aud = validar_dataset_completo(registros)
        self.assertTrue(aud["ok"], f"Errores antifuga: {aud['errores'][:5]}")
        self.assertGreater(aud["por_split"].get("train", 0), 50)
        self.assertGreater(aud["por_split"].get("val", 0), 15)
        self.assertGreaterEqual(len(aud["por_categoria"]), 7)
        # Ninguna unidad bloqueada debe existir en registros
        for r in registros:
            blob_sin_sys = json.dumps(r["messages"][1:], ensure_ascii=False)
            for bid in ("RI-FI-ART-014", "CAL-2026-S1-03", "RG-ART-036", "RG-ART-057"):
                self.assertIn(bid, BLOCKED_UNIT_IDS)
                self.assertNotIn(bid, blob_sin_sys)

    def test_enmascaramiento_multiturno_y_modelfile_ollama(self) -> None:
        tok = _FakeTokenizer()
        reg = {
            "id": "MASK-01",
            "messages": [
                {"role": "system", "content": "Eres asistente."},
                {"role": "user", "content": "Turno historial 1"},
                {"role": "assistant", "content": "Respuesta historial 1 [RG-ART-038]."},
                {"role": "user", "content": "Pregunta actual con [RG-ART-038]"},
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{"type": "function", "function": {"name": "calcular", "arguments": {"expresion": "5.8 > 5.7"}}}],
                },
                {"role": "tool", "name": "calcular", "content": '{"ok": true, "resultado": true}'},
                {"role": "assistant", "content": "Sí cumple [RG-ART-038]."},
            ],
        }
        ej = construir_ejemplo_sft_multiturno(reg, tok, max_seq_length=4096)
        self.assertFalse(ej["truncado"])
        texto_supervisado = "".join(
            chr(tid) for tid, lab in zip(ej["input_ids"], ej["labels"]) if lab != -100
        )
        # Historial previo, system, prompt actual y tool_response deben estar enmascarados (-100)
        self.assertNotIn("Respuesta historial 1", texto_supervisado)
        self.assertNotIn("Pregunta actual", texto_supervisado)
        self.assertNotIn("<tool_response>", texto_supervisado)
        # Solo tool_call y respuesta final deben supervisarse
        self.assertIn("<tool_call>", texto_supervisado)
        self.assertIn("Sí cumple [RG-ART-038].", texto_supervisado)

        stats = resumir_tokens_dataset([ej])
        self.assertEqual(stats["ejemplos"], 1)

        mf = generar_modelfile("./udec-agente-qwen3-4b-ft-Q4_K_M.gguf")
        self.assertIn("FROM ./udec-agente-qwen3-4b-ft-Q4_K_M.gguf", mf)
        self.assertIn("<tools>", mf)
        self.assertIn("<tool_call>", mf)
        self.assertIn("<tool_response>", mf)
        self.assertIn("PARAMETER num_ctx 4096", mf)
        self.assertIn("PARAMETER repeat_penalty 1.05", mf)


if __name__ == "__main__":
    unittest.main()
