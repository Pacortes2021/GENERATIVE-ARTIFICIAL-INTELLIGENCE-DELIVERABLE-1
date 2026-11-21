"""Pruebas unitarias para construcción antifuga DPO y paridad matemática Split-Backward."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from asistente_local.finetune.construir_dataset_dpo import (
    construir_pares_dpo,
    guardar_dataset_dpo,
    validar_dataset_dpo,
)
from asistente_local.finetune.entrenar_agente_dpo import (
    calcular_pesos_dpo_split,
    construir_par_dpo,
    secuencia_logps_y_nll,
)


class _FakeDpoTokenizer:
    """Tokenizador determinista mínimo que emula apply_chat_template sin red ni transformers."""

    pad_token_id = 0
    eos_token_id = 1

    def apply_chat_template(
        self,
        msgs: list[dict],
        tools=None,
        add_generation_prompt: bool = False,
        tokenize: bool = False,
    ):
        partes = [f"<SYS:{len(tools or [])}>"]
        for m in msgs:
            role = m.get("role", "")
            content = m.get("content", "")
            tc = json.dumps(m.get("tool_calls", []), sort_keys=True, ensure_ascii=False)
            partes.append(f"|{role}:{content}:{tc}")
        if add_generation_prompt:
            partes.append("|assistant:")
        txt = "".join(partes)
        if not tokenize:
            return txt
        return self(txt, add_special_tokens=False)["input_ids"]

    def __call__(self, texto: str, add_special_tokens: bool = False) -> dict[str, list[int]]:
        return {"input_ids": [max(2, (ord(c) % 250) + 2) for c in texto]}


class TestDpoAgente(unittest.TestCase):
    """Valida pares DPO, bloqueo antifuga y equivalencia exacta de gradientes Split-Backward."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.pares = construir_pares_dpo()

    def test_dataset_dpo_antifuga_y_cobertura(self) -> None:
        aud = validar_dataset_dpo(self.pares)
        self.assertTrue(aud["ok"], f"Errores antifuga inesperados: {aud['errores']}")
        self.assertGreaterEqual(aud["por_split"].get("train", 0), 40)
        self.assertGreaterEqual(aud["por_split"].get("val", 0), 14)

        with tempfile.TemporaryDirectory() as tmp:
            resumen = guardar_dataset_dpo(Path(tmp))
            self.assertTrue(resumen["antifuga_ok"])
            self.assertTrue((Path(tmp) / "dpo_train.jsonl").is_file())
            self.assertTrue((Path(tmp) / "dpo_val.jsonl").is_file())
            self.assertTrue((Path(tmp) / "resumen_dpo.json").is_file())

    def test_validar_dataset_dpo_rechaza_fuga_en_rejected_y_clon(self) -> None:
        muestra_fuga = copy.deepcopy(self.pares[0])
        muestra_fuga["id"] = "DPO-TEST-FUGA"
        muestra_fuga["rejected"] = {"role": "assistant", "content": "Según [RG-ART-028] no corresponde."}

        muestra_igual = copy.deepcopy(self.pares[1])
        muestra_igual["id"] = "DPO-TEST-IDENTICO"
        muestra_igual["rejected"] = copy.deepcopy(muestra_igual["chosen"])

        muestra_eval = copy.deepcopy(self.pares[2])
        muestra_eval["id"] = "DPO-TEST-SIMILAR"
        muestra_eval["prompt"][-1]["content"] = (
            "¿En qué fechas son las matrículas de alumnos nuevos según el calendario 2026?"
        )

        aud = validar_dataset_dpo([muestra_fuga, muestra_igual, muestra_eval])
        self.assertFalse(aud["ok"])
        blob = "\n".join(aud["errores"])
        self.assertIn("RG-ART-028", blob)
        self.assertIn("idénticos", blob)

    def test_construir_par_dpo_enmascara_prompt_identico(self) -> None:
        tok = _FakeDpoTokenizer()
        par_tok = construir_par_dpo(self.pares[0], tok, max_seq_length=8192)
        p_len = par_tok["prompt_tokens"]
        self.assertGreater(p_len, 0)
        self.assertEqual(par_tok["chosen_labels"][:p_len], [-100] * p_len)
        self.assertEqual(par_tok["rejected_labels"][:p_len], [-100] * p_len)
        self.assertEqual(
            par_tok["chosen_labels"][p_len:],
            par_tok["chosen_input_ids"][p_len:],
        )
        self.assertEqual(
            par_tok["rejected_labels"][p_len:],
            par_tok["rejected_input_ids"][p_len:],
        )
        self.assertGreater(par_tok["chosen_sup_tokens"], 0)
        self.assertGreater(par_tok["rejected_sup_tokens"], 0)

    def test_paridad_exacta_gradiente_split_backward_vs_simultaneo(self) -> None:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F

        class _TinyLM(nn.Module):
            def __init__(self, vocab: int = 48, dim: int = 16) -> None:
                super().__init__()
                self.emb = nn.Embedding(vocab, dim)
                self.h1 = nn.Linear(dim, dim)
                self.drop = nn.Dropout(p=0.15)
                self.head = nn.Linear(dim, vocab)

            def forward(self, ids: torch.Tensor) -> torch.Tensor:
                x = torch.tanh(self.h1(self.emb(ids)))
                return self.head(self.drop(x))

        torch.manual_seed(42)
        modelo = _TinyLM()
        modelo.train()

        c_ids = torch.tensor([[3, 7, 11, 15, 19, 23, 27, 5]], dtype=torch.long)
        c_labs = torch.tensor([[-100, -100, -100, -100, 19, 23, 27, 5]], dtype=torch.long)
        r_ids = torch.tensor([[3, 7, 11, 15, 29, 31, 9]], dtype=torch.long)
        r_labs = torch.tensor([[-100, -100, -100, -100, 29, 31, 9]], dtype=torch.long)
        ref_w, ref_l = -14.2, -11.5
        beta, lambda_nll = 0.1, 0.05

        # 1. Referencia simultánea directa con máscaras de dropout fijadas por rama
        rng_w = torch.get_rng_state()
        lp_w_sim, nll_w_sim = secuencia_logps_y_nll(modelo(c_ids), c_labs)
        rng_l = torch.get_rng_state()
        lp_l_sim, _ = secuencia_logps_y_nll(modelo(r_ids), r_labs)

        margin_sim = (lp_w_sim.squeeze(0) - ref_w) - (lp_l_sim.squeeze(0) - ref_l)
        loss_sim = -F.logsigmoid(beta * margin_sim) + lambda_nll * nll_w_sim.squeeze(0)
        modelo.zero_grad(set_to_none=True)
        loss_sim.backward()
        grads_sim = {k: p.grad.detach().clone() for k, p in modelo.named_parameters()}

        # 2. Split-Backward desacoplado idéntico al bucle de Colab
        modelo.zero_grad(set_to_none=True)
        torch.set_rng_state(rng_w)
        with torch.no_grad():
            lp_w0, _ = secuencia_logps_y_nll(modelo(c_ids), c_labs)
        torch.set_rng_state(rng_l)
        with torch.no_grad():
            lp_l0, _ = secuencia_logps_y_nll(modelo(r_ids), r_labs)

        w_dpo, _ = calcular_pesos_dpo_split(lp_w0.squeeze(0), lp_l0.squeeze(0), ref_w, ref_l, beta=beta)

        torch.set_rng_state(rng_w)
        lp_w_sp, nll_w_sp = secuencia_logps_y_nll(modelo(c_ids), c_labs)
        (-w_dpo * lp_w_sp.squeeze(0) + lambda_nll * nll_w_sp.squeeze(0)).backward()

        torch.set_rng_state(rng_l)
        lp_l_sp, _ = secuencia_logps_y_nll(modelo(r_ids), r_labs)
        (w_dpo * lp_l_sp.squeeze(0)).backward()

        for nombre, p in modelo.named_parameters():
            self.assertIsNotNone(p.grad, f"Gradiente nulo en {nombre}")
            self.assertTrue(
                torch.allclose(p.grad, grads_sim[nombre], atol=1e-5, rtol=1e-5),
                f"Desajuste Split-Backward en {nombre}",
            )


if __name__ == "__main__":
    unittest.main()
