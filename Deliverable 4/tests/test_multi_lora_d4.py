"""Pruebas unitarias para el sistema oficial Multi-LoRA 3-LoRA de Deliverable 4."""

from __future__ import annotations

import contextlib
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import torch

DELIVERABLE4_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = DELIVERABLE4_DIR / "scripts"
DATOS_DIR = DELIVERABLE4_DIR / "datos"
TRAIN_DIR = DELIVERABLE4_DIR / "entrenamiento"
EVAL_DIR = DELIVERABLE4_DIR / "evaluacion"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import antifuga_multi as am  # noqa: E402
import construir_datasets_agentes as cda  # noqa: E402
import entrenar_agente as ea  # noqa: E402
import evaluar_multi_lora as eml  # noqa: E402
import generar_reporte_3lora as gr3  # noqa: E402
import publicar_adaptadores_hf as pah  # noqa: E402
import resumir_comparativa as rc  # noqa: E402


class _BatchEncoding(dict):
    def to(self, _device: object) -> "_BatchEncoding":
        return self


class _MockTokenizer:
    eos_token_id = 0

    def __init__(self, modelo: "_MockMultiLoraModel") -> None:
        self._modelo = modelo

    def apply_chat_template(
        self,
        msgs: list[dict[str, str]],
        tokenize: bool = False,
        add_generation_prompt: bool = True,
        enable_thinking: bool = False,
    ) -> str:
        return msgs[0]["content"]

    def __call__(self, text: str, return_tensors: str = "pt") -> _BatchEncoding:
        return _BatchEncoding({"input_ids": torch.tensor([[1, 2, 3]])})

    def decode(self, ids: torch.Tensor, skip_special_tokens: bool = True) -> str:
        tag = self._modelo.ultimo_estado_usado or "desconocido"
        return f"respuesta_simulada[{tag}]"


class _MockMultiLoraModel:
    device = torch.device("cpu")

    def __init__(self) -> None:
        self.active_adapter: str | None = "enrutador"
        self.disabled = False
        self.ultimo_estado_usado: str | None = None
        self.secuencia_estados: list[str] = []

    def set_adapter(self, nombre: str) -> None:
        self.active_adapter = nombre

    @contextlib.contextmanager
    def disable_adapter(self):
        prev = self.disabled
        self.disabled = True
        try:
            yield
        finally:
            self.disabled = prev

    def generate(self, **kwargs: object) -> torch.Tensor:
        estado = "base" if self.disabled else (self.active_adapter or "base")
        self.ultimo_estado_usado = estado
        self.secuencia_estados.append(estado)
        return torch.tensor([[1, 2, 3, 4]])

    def __call__(self, **kwargs: object) -> SimpleNamespace:
        offset = 0.0 if self.disabled else {"enrutador": 1.0, "recuperador": 2.0, "redactor": 3.0}.get(self.active_adapter or "", 0.0)
        return SimpleNamespace(logits=torch.full((1, 3, 8), offset))


class TestDatasetsYAntifugaMultiLora(unittest.TestCase):
    def test_reconstruccion_determinista_y_sha256_enrutador_recuperador(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_datos = Path(tmp)
            res_red = DATOS_DIR / "dataset_resumen.json"
            if res_red.is_file():
                (tmp_datos / "dataset_resumen.json").write_bytes(res_red.read_bytes())

            resumen = cda.construir_datasets_agentes_d4(datos_dir=tmp_datos, seed=202604)
            self.assertEqual(resumen["agentes"]["enrutador"]["train"], 210)
            self.assertEqual(resumen["agentes"]["enrutador"]["val"], 36)
            self.assertEqual(resumen["agentes"]["recuperador"]["train"], 230)
            self.assertEqual(resumen["agentes"]["recuperador"]["val"], 39)
            self.assertEqual(resumen["totales_3_agentes"], {"train": 620, "val": 105, "total": 725})
            for rol in ("enrutador", "recuperador"):
                self.assertEqual(resumen["agentes"][rol]["antifuga"]["unidades_bloqueadas_solapadas"], 0)
                self.assertEqual(resumen["agentes"][rol]["antifuga"]["menciones_qid_eval"], 0)
                self.assertEqual(resumen["agentes"][rol]["antifuga"]["solapamiento_train_val"], 0)
                for split in ("train", "val"):
                    real = DATOS_DIR / f"{rol}_{split}.jsonl"
                    regen = tmp_datos / f"{rol}_{split}.jsonl"
                    self.assertEqual(
                        hashlib.sha256(real.read_bytes()).hexdigest(),
                        hashlib.sha256(regen.read_bytes()).hexdigest(),
                        f"SHA-256 difiere en {rol}_{split}.jsonl",
                    )

    def test_numero_permitido_orquestador(self) -> None:
        self.assertTrue(am.numero_permitido_orquestador(14, "requisitos Art 14", "", []))
        self.assertTrue(am.numero_permitido_orquestador(28, "revisar", "", ["RG-ART-028"]))
        self.assertFalse(am.numero_permitido_orquestador(99, "consulta simple", "", ["RG-ART-028"]))


class TestEntrenamientoYPublicacionMultiLora(unittest.TestCase):
    def test_artefactos_enrutador_recuperador_y_curvas_3agentes(self) -> None:
        self.assertTrue((TRAIN_DIR / "loss_curves_3agentes.png").is_file())
        self.assertTrue((TRAIN_DIR / "loss_curves_3agentes.pdf").is_file())

        for rol, exp_tr, exp_va in (("enrutador", 210, 36), ("recuperador", 230, 39)):
            d = TRAIN_DIR / rol
            metrics = json.loads((d / "training_metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics["agente"], rol)
            self.assertEqual(metrics["modelo_base"], "Qwen/Qwen3-4B")
            self.assertEqual(metrics["datos"]["train_ejemplos"], exp_tr)
            self.assertEqual(metrics["datos"]["val_ejemplos"], exp_va)
            self.assertEqual(metrics["datos"]["tokens_train"]["truncados"], 0)
            self.assertEqual(metrics["datos"]["tokens_val"]["truncados"], 0)
            for fname in ("loss_curve.png", "loss_curve.pdf", "smoke_test_val.json", "adapter/README.md"):
                self.assertTrue((d / fname).is_file(), f"Falta {d / fname}")

            self.assertEqual(
                metrics["datos"]["train_sha256"],
                hashlib.sha256((DATOS_DIR / f"{rol}_train.jsonl").read_bytes()).hexdigest(),
            )
            self.assertEqual(
                metrics["datos"]["val_sha256"],
                hashlib.sha256((DATOS_DIR / f"{rol}_val.jsonl").read_bytes()).hexdigest(),
            )

            card = ea.generar_model_card_agente(rol, metrics)
            self.assertIn("base_model: Qwen/Qwen3-4B", card)
            self.assertIn("library_name: peft", card)

    def test_publicar_adaptadores_hf_localizar_y_mock_upload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_drive = Path(tmp) / "drive_entrenamiento"
            ad = tmp_drive / "enrutador" / "adapter"
            ad.mkdir(parents=True, exist_ok=True)
            (ad / "adapter_model.safetensors").write_bytes(b"fake-weights")
            (ad / "adapter_config.json").write_text("{}", encoding="utf-8")

            encontrado = pah.localizar_carpeta_adapter("enrutador", drive_dir=tmp_drive)
            self.assertEqual(encontrado, ad)

            with self.assertRaises(FileNotFoundError):
                pah.localizar_carpeta_adapter("recuperador", drive_dir=tmp_drive)

            with patch("huggingface_hub.HfApi") as mock_api_cls:
                fake_api = mock_api_cls.return_value
                fake_api.upload_folder.return_value = SimpleNamespace(oid="deadbeef1234")
                with patch.object(pah, "D4_TRAIN_DIR", tmp_drive):
                    (tmp_drive / "enrutador" / "training_metrics.json").write_text(
                        (TRAIN_DIR / "enrutador" / "training_metrics.json").read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )
                    res = pah.publicar_rol("enrutador", "Pablox0333/qwen3-4b-enrutador-udec-d4", ad, token="tok")
                    self.assertEqual(res["revision"], "deadbeef1234")
                    fake_api.create_repo.assert_called_once()
                    fake_api.upload_folder.assert_called_once()


class TestAislamientoYResultadosMultiLora(unittest.TestCase):
    def test_multi_lora_generator_conmutacion_y_verificacion_aislamiento(self) -> None:
        modelo = _MockMultiLoraModel()
        tok = _MockTokenizer(modelo)

        aisl = eml.verificar_aislamiento_multi_lora(modelo, tok, eml.ROLES_OFICIALES_D4)
        self.assertGreater(aisl["max_abs_diff_vs_base"]["enrutador"], 0.0)
        self.assertGreater(aisl["max_abs_diff_vs_base"]["recuperador"], 0.0)
        self.assertGreater(aisl["max_abs_diff_vs_base"]["redactor"], 0.0)
        self.assertGreater(aisl["max_abs_diff_cruzada"]["enrutador_vs_recuperador"], 0.0)

        gen_3lora = eml.MultiLoraGenerator(modelo, tok, greedy=True)
        self.assertIn("enrutador", gen_3lora("enrutador", "p"))
        self.assertIn("recuperador", gen_3lora("recuperador", "p"))
        self.assertIn("redactor", gen_3lora("redactor", "p"))
        self.assertIn("base", gen_3lora("verificador", "p"))
        self.assertEqual(modelo.secuencia_estados, ["enrutador", "recuperador", "redactor", "base"])
        self.assertTrue(gen_3lora.telemetria[0]["usa_adaptador"])
        self.assertTrue(gen_3lora.telemetria[1]["usa_adaptador"])
        self.assertTrue(gen_3lora.telemetria[2]["usa_adaptador"])
        self.assertFalse(gen_3lora.telemetria[3]["usa_adaptador"])

        gen_base = eml.MultiLoraGenerator(modelo, tok, adaptadores_activos={r: None for r in eml.ROLES_ORDEN}, greedy=True)
        for rol in eml.ROLES_ORDEN:
            self.assertIn("base", gen_base(rol, "p"))
        self.assertTrue(all(not c["usa_adaptador"] for c in gen_base.telemetria))

    def test_telemetria_cero_violaciones_y_resumen_3lora_consistente(self) -> None:
        resumen = json.loads((EVAL_DIR / "resumen_comparativo_d4.json").read_text(encoding="utf-8"))
        oficial = resumen["sistemas_a100_bf16"]["multi_lora_3_agentes_oficial"]
        self.assertEqual(oficial["d3_congelado_50"], 46)
        self.assertEqual(oficial["d3_dificil_25"], 18)
        self.assertEqual(oficial["d3_75"], 64)
        self.assertEqual(oficial["nuevas_20"], 10)
        self.assertEqual(oficial["global_95"], 74)
        self.assertEqual(oficial["llamadas_75"], 388)
        self.assertEqual(oficial["llamadas_nuevas20"], 118)

        for fname, exp_ver_calls in (("telemetria_3lora_75.json", 98), ("telemetria_3lora_nuevas20.json", 32)):
            tel = json.loads((EVAL_DIR / fname).read_text(encoding="utf-8"))
            ver_calls = [c for calls in tel.values() for c in calls if c["agente"] == "verificador"]
            self.assertEqual(len(ver_calls), exp_ver_calls)
            self.assertTrue(all(c["usa_adaptador"] is False for c in ver_calls))
            lora_calls = [c for calls in tel.values() for c in calls if c["agente"] in ("enrutador", "recuperador", "redactor")]
            self.assertTrue(all(c["usa_adaptador"] is True and c.get("adaptador_activo") == c["agente"] for c in lora_calls))

        fallos = json.loads((EVAL_DIR / "casos_fallo_y_regresion_3lora.json").read_text(encoding="utf-8"))
        self.assertEqual(fallos["total_casos_documentados"], 11)
        self.assertEqual(len(fallos["casos"]), 11)
        comp = json.loads((EVAL_DIR / "comparativa_base_vs_3lora.json").read_text(encoding="utf-8"))
        self.assertEqual(len(comp), 7)

        r75 = rc.resumir_corrida(
            "3-LoRA",
            EVAL_DIR / "resultados_3lora_75_auditados.csv",
            EVAL_DIR / "telemetria_3lora_75.json",
        )
        self.assertEqual(r75["total"], 75)
        self.assertEqual(r75["correctos"], 64)
        self.assertEqual(r75["llamadas_modelo_total"], 388)
        self.assertEqual(gr3.COMPARATIVA_BASE_VS_3LORA_QIDS[0], "dificil_25:H07")


if __name__ == "__main__":
    unittest.main()
