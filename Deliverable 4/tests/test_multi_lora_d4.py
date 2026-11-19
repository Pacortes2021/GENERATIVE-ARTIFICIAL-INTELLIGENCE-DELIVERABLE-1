"""Pruebas unitarias para el sistema oficial Multi-LoRA 3-LoRA de Deliverable 4."""

from __future__ import annotations

import contextlib
import csv
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
        offset = (
            0.0
            if self.disabled
            else {"enrutador": 1.0, "recuperador": 2.0, "redactor": 3.0}.get(
                self.active_adapter or "", 0.0
            )
        )
        return SimpleNamespace(logits=torch.full((1, 3, 8), offset))


class TestDatasetsYAntifugaMultiLora(unittest.TestCase):
    def test_reconstruccion_determinista_y_muestra_manual_enrutador_recuperador(self) -> None:
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

            md_real = DATOS_DIR / "MUESTRA_REVISION_MANUAL_ENRUTADOR_RECUPERADOR.md"
            md_regen = tmp_datos / "MUESTRA_REVISION_MANUAL_ENRUTADOR_RECUPERADOR.md"
            self.assertEqual(md_real.read_bytes(), md_regen.read_bytes())

            ids_esperados = resumen["muestra_manual_enrutador_recuperador_ids"]
            self.assertEqual(len(ids_esperados), 20)
            firmas_csv = tmp_datos / "revision_manual_firmas_agentes.csv"
            self.assertFalse(cda.validar_firmas_agentes_completas(firmas_csv, ids_esperados)["completo"])

            with firmas_csv.open("w", encoding="utf-8", newline="\n") as f:
                writer = csv.writer(f)
                writer.writerow(["sample_id", "revisor", "fecha", "veredicto", "observacion"])
                for sid in ids_esperados:
                    writer.writerow([sid, "Álvaro Contreras", "2026-11-19", "Aprobado", "OK"])

            estado_ok = cda.validar_firmas_agentes_completas(firmas_csv, ids_esperados)
            self.assertTrue(estado_ok["completo"])
            self.assertEqual(estado_ok["firmados"], 20)

    def test_numero_permitido_orquestador(self) -> None:
        self.assertTrue(am.numero_permitido_orquestador(14, "requisitos Art 14", "", []))
        self.assertTrue(am.numero_permitido_orquestador(28, "revisar", "", ["RG-ART-028"]))
        self.assertFalse(am.numero_permitido_orquestador(99, "consulta simple", "", ["RG-ART-028"]))


class TestEntrenamientoYPublicacionMultiLora(unittest.TestCase):
    def test_artefactos_enrutador_recuperador_y_curvas_3agentes(self) -> None:
        self.assertTrue((TRAIN_DIR / "loss_curves_3agentes.png").is_file())
        self.assertTrue((TRAIN_DIR / "loss_curves_3agentes.pdf").is_file())

        manifest_path = TRAIN_DIR / "manifest_adaptadores_hf.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertIn("redactor", manifest["adaptadores"])
        red_info = manifest["adaptadores"]["redactor"]
        self.assertTrue(red_info["publicado"])
        self.assertEqual(len(red_info["hf_revision"]), 40)
        self.assertEqual(len(red_info["adapter_model_sha256"]), 64)

        for rol, info in manifest["adaptadores"].items():
            if info.get("publicado"):
                self.assertTrue(bool(info.get("hf_revision")), f"Falta hf_revision en {rol}")
                self.assertEqual(len(str(info.get("adapter_model_sha256") or "")), 64)

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

    def test_publicar_adaptadores_hf_sha256_manifest_y_verificacion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            tmp_drive = tmp_root / "drive_entrenamiento"
            ad = tmp_drive / "enrutador" / "adapter"
            ad.mkdir(parents=True, exist_ok=True)
            pesos_bytes = b"fake-safetensors-payload"
            (ad / "adapter_model.safetensors").write_bytes(pesos_bytes)
            (ad / "adapter_config.json").write_text("{}", encoding="utf-8")
            sha_esperado = hashlib.sha256(pesos_bytes).hexdigest()

            encontrado = pah.localizar_carpeta_adapter("enrutador", drive_dir=tmp_drive)
            self.assertEqual(encontrado, ad)

            with self.assertRaises(FileNotFoundError):
                pah.localizar_carpeta_adapter("recuperador", drive_dir=tmp_drive)

            manifest_tmp = tmp_root / "manifest_adaptadores_hf.json"
            with patch("huggingface_hub.HfApi") as mock_api_cls:
                fake_api = mock_api_cls.return_value
                fake_api.upload_folder.return_value = SimpleNamespace(oid="deadbeef1234567890")
                fake_api.get_paths_info.return_value = [
                    SimpleNamespace(
                        path="adapter_model.safetensors",
                        lfs=SimpleNamespace(sha256=sha_esperado),
                    )
                ]
                with patch.object(pah, "D4_TRAIN_DIR", tmp_drive):
                    (tmp_drive / "enrutador" / "training_metrics.json").write_text(
                        (TRAIN_DIR / "enrutador" / "training_metrics.json").read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )
                    res = pah.publicar_rol(
                        "enrutador",
                        "Pablox0333/qwen3-4b-enrutador-udec-d4",
                        ad,
                        token="tok",
                        manifest_path=manifest_tmp,
                    )
                    self.assertEqual(res["revision"], "deadbeef1234567890")
                    self.assertEqual(res["adapter_model_sha256"], sha_esperado)
                    manifest_gen = json.loads(manifest_tmp.read_text(encoding="utf-8"))
                    self.assertEqual(
                        manifest_gen["adaptadores"]["enrutador"]["adapter_model_sha256"],
                        sha_esperado,
                    )
                    self.assertTrue(manifest_gen["adaptadores"]["enrutador"]["publicado"])

                # Verifica detección de mismatch de hash remoto
                fake_api.get_paths_info.return_value = [
                    SimpleNamespace(
                        path="adapter_model.safetensors",
                        lfs=SimpleNamespace(sha256="0" * 64),
                    )
                ]
                with self.assertRaises(RuntimeError):
                    pah._verificar_sha256_en_hf(
                        fake_api,
                        hf_repo="Pablox0333/qwen3-4b-enrutador-udec-d4",
                        revision="deadbeef1234567890",
                        expected_sha256=sha_esperado,
                    )


class TestAislamientoYResultadosMultiLora(unittest.TestCase):
    def test_multi_lora_generator_conmutacion_y_verificacion_aislamiento(self) -> None:
        modelo = _MockMultiLoraModel()
        tok = _MockTokenizer(modelo)

        aisl = eml.verificar_aislamiento_multi_lora(modelo, tok, eml.ROLES_OFICIALES_D4)
        self.assertGreater(aisl["max_abs_diff_vs_base"]["enrutador"], 0.0)
        self.assertGreater(aisl["max_abs_diff_vs_base"]["recuperador"], 0.0)
        self.assertGreater(aisl["max_abs_diff_vs_base"]["redactor"], 0.0)
        self.assertGreater(aisl["max_abs_diff_cruzada"]["enrutador_vs_recuperador"], 0.0)

        fuentes_hf = eml.resolver_fuentes_adaptadores_default(solo_hf=True)
        self.assertEqual(fuentes_hf["redactor"][0], "Pablox0333/qwen3-4b-redactor-udec-d4")
        self.assertEqual(fuentes_hf["redactor"][1], "739b031acbd5feef2c49f946b94722712209bce0")

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

        gen_base = eml.MultiLoraGenerator(
            modelo, tok, adaptadores_activos={r: None for r in eml.ROLES_ORDEN}, greedy=True
        )
        for rol in eml.ROLES_ORDEN:
            self.assertIn("base", gen_base(rol, "p"))
        self.assertTrue(all(not c["usa_adaptador"] for c in gen_base.telemetria))

    def test_recalculo_integral_csv_trazas_y_auditorias_3lora(self) -> None:
        # Recalcula directamente desde fuentes primarias (CSV auditados, telemetrias y trazas)
        res_75 = rc.resumir_corrida(
            "3-LoRA 75",
            EVAL_DIR / "resultados_3lora_75_auditados.csv",
            EVAL_DIR / "telemetria_3lora_75.json",
        )
        res_n20 = rc.resumir_corrida(
            "3-LoRA N20",
            EVAL_DIR / "resultados_3lora_nuevas20_auditados.csv",
            EVAL_DIR / "telemetria_3lora_nuevas20.json",
        )
        res_cb75 = rc.resumir_corrida(
            "Control Base 75",
            EVAL_DIR / "resultados_control_base_D4_auditados.csv",
            EVAL_DIR / "telemetria_control_base_D4.json",
        )
        res_cbn20 = rc.resumir_corrida(
            "Control Base N20",
            EVAL_DIR / "resultados_nuevas20_base_D4_auditados.csv",
            EVAL_DIR / "telemetria_nuevas20_base_D4.json",
        )

        with (EVAL_DIR / "resultados_3lora_75_auditados.csv").open(encoding="utf-8", newline="") as f:
            rows_75 = list(csv.DictReader(f))
        cong_ok = sum(int(r["correcto"]) for r in rows_75 if r["set"] == "congelado_50")
        dif_ok = sum(int(r["correcto"]) for r in rows_75 if r["set"] == "dificil_25")

        resumen = json.loads((EVAL_DIR / "resumen_comparativo_d4.json").read_text(encoding="utf-8"))
        oficial = resumen["sistemas_a100_bf16"]["multi_lora_3_agentes_oficial"]
        self.assertEqual(oficial["d3_congelado_50"], cong_ok)
        self.assertEqual(oficial["d3_dificil_25"], dif_ok)
        self.assertEqual(oficial["d3_75"], res_75["correctos"])
        self.assertEqual(oficial["llamadas_75"], res_75["llamadas_modelo_total"])
        self.assertEqual(oficial["nuevas_20"], res_n20["correctos"])
        self.assertEqual(oficial["llamadas_nuevas20"], res_n20["llamadas_modelo_total"])
        self.assertEqual(oficial["global_95"], res_75["correctos"] + res_n20["correctos"])

        ctrl = resumen["sistemas_a100_bf16"]["control_base"]
        self.assertEqual(ctrl["d3_75"], res_cb75["correctos"])
        self.assertEqual(ctrl["llamadas_75"], res_cb75["llamadas_modelo_total"])
        self.assertEqual(ctrl["nuevas_20"], res_cbn20["correctos"])
        self.assertEqual(ctrl["llamadas_nuevas20"], res_cbn20["llamadas_modelo_total"])

        comp_est = resumen["comparacion_estadistica_y_comportamiento"]
        self.assertEqual(comp_est["diferencias_vs_control_75"]["balance_neto"], res_75["correctos"] - res_cb75["correctos"])
        self.assertEqual(comp_est["diferencias_vs_control_n20"]["balance_neto"], res_n20["correctos"] - res_cbn20["correctos"])

        # Verifica 0 violaciones de aislamiento en Verificador sobre las telemetrias reales
        for fname in ("telemetria_3lora_75.json", "telemetria_3lora_nuevas20.json"):
            tel = json.loads((EVAL_DIR / fname).read_text(encoding="utf-8"))
            ver_calls = [c for calls in tel.values() for c in calls if c["agente"] == "verificador"]
            self.assertGreater(len(ver_calls), 0)
            self.assertTrue(all(c["usa_adaptador"] is False for c in ver_calls))
            lora_calls = [
                c
                for calls in tel.values()
                for c in calls
                if c["agente"] in ("enrutador", "recuperador", "redactor")
            ]
            self.assertTrue(
                all(c["usa_adaptador"] is True and c.get("adaptador_activo") == c["agente"] for c in lora_calls)
            )

        # Verifica coherencia de auditoria_3lora_*.json contra sus CSV crudos reales
        for aud_name, csv_crudo_esperado in (
            ("auditoria_3lora_75.json", "resultados_3lora_75.csv"),
            ("auditoria_3lora_nuevas20.json", "resultados_3lora_nuevas20.csv"),
        ):
            aud = json.loads((EVAL_DIR / aud_name).read_text(encoding="utf-8"))
            self.assertEqual(aud["fuente_csv_crudo"], csv_crudo_esperado)
            sha_real = hashlib.sha256((EVAL_DIR / csv_crudo_esperado).read_bytes()).hexdigest()
            self.assertEqual(aud["sha256_csv_crudo"], sha_real)

        fallos = json.loads((EVAL_DIR / "casos_fallo_y_regresion_3lora.json").read_text(encoding="utf-8"))
        self.assertEqual(fallos["total_casos_documentados"], len(fallos["casos"]))
        self.assertEqual(
            fallos["total_casos_documentados"],
            len(rows_75) - res_75["correctos"],
        )
        comp = json.loads((EVAL_DIR / "comparativa_base_vs_3lora.json").read_text(encoding="utf-8"))
        self.assertEqual(len(comp), len(gr3.COMPARATIVA_BASE_VS_3LORA_QIDS))


if __name__ == "__main__":
    unittest.main()
