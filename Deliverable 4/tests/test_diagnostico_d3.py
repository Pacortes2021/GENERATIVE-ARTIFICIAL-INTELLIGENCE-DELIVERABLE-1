"""Pruebas de integridad para el diagnostico D3 y prompts base de Deliverable 4."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

DELIVERABLE4_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = DELIVERABLE4_DIR.parent
DELIVERABLE3_DIR = REPO_ROOT / "Deliverable 3" / "Deliverable3"
SCRIPTS_DIR = DELIVERABLE4_DIR / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import diagnostico_d3  # noqa: E402


class TestDiagnosticoD3(unittest.TestCase):
    """Verifica trazabilidad entre D3 v6, prompts versionados y diagnostico_d3."""

    def test_prompts_d4_coinciden_byte_a_byte_con_d3_v6(self) -> None:
        archivos = [
            "01_enrutador.txt",
            "02_recuperador.txt",
            "03_redactor.txt",
            "04_verificador.txt",
        ]
        for nombre in archivos:
            src = DELIVERABLE3_DIR / "prompts" / nombre
            dst = DELIVERABLE4_DIR / "prompts" / nombre
            self.assertTrue(dst.is_file(), f"Falta prompt {dst}")
            self.assertEqual(src.read_bytes(), dst.read_bytes(), f"Difiere {nombre}")

    def test_totales_y_origen_errores_diagnostico(self) -> None:
        diag = diagnostico_d3.generar_diagnostico()
        rg = diag["resumen_global"]
        de = diag["desglose_errores"]

        self.assertEqual(rg["total"]["total"], 75)
        self.assertEqual(rg["congelado_50"]["correctos"], 46)
        self.assertEqual(rg["dificil_25"]["correctos"], 20)
        self.assertEqual(rg["total"]["correctos"], 66)
        self.assertEqual(rg["total"]["incorrectos"], 9)
        self.assertEqual(rg["llamadas_modelo_llm_total"], 711)
        self.assertEqual(rg["eventos_traza_total"], 798)
        self.assertEqual(rg["fallbacks_total"], 0)
        self.assertEqual(rg["rechazos_verificador_a_redactor"], 25)
        self.assertEqual(rg["rechazos_verificador_a_recuperador"], 21)

        self.assertEqual(de["total_errores"], 9)
        self.assertEqual(de["origen_redactor_con_evidencia_top6"], 8)
        self.assertEqual(de["origen_recuperador_evidencia_faltante"], 1)
        self.assertEqual(de["ids_origen_recuperador"], ["dificil_25:H03"])
        self.assertEqual(
            de["ids_origen_redactor"],
            [
                "congelado_50:13",
                "congelado_50:24",
                "congelado_50:26",
                "congelado_50:36",
                "dificil_25:H07",
                "dificil_25:H14",
                "dificil_25:H18",
                "dificil_25:H25",
            ],
        )

    def test_evidencia_top6_y_caso_h03(self) -> None:
        diag = diagnostico_d3.generar_diagnostico()
        for caso in diag["casos"]:
            self.assertLessEqual(len(caso["top6"]), diagnostico_d3.MAX_EVIDENCIA)

        errores_por_id = {c["case_key"]: c for c in diag["desglose_errores"]["casos"]}
        h03 = errores_por_id["dificil_25:H03"]
        self.assertFalse(h03["todas_requeridas_en_top6"])
        self.assertEqual(
            h03["requeridas_faltantes_top6"],
            ["CAL-2026-S1-02", "CAL-2026-S2-02"],
        )
        self.assertEqual(h03["requeridas_faltantes_pool"], ["CAL-2026-S2-02"])

        for key, err in errores_por_id.items():
            if key != "dificil_25:H03":
                self.assertTrue(err["todas_con_extra_en_top6"], f"Falta evidencia top-6 en {key}")

    def test_artefacto_json_sincronizado(self) -> None:
        json_path = DELIVERABLE4_DIR / "diagnostico" / "diagnostico_d3.json"
        self.assertTrue(json_path.is_file(), f"Falta {json_path}")
        en_disco = json.loads(json_path.read_text(encoding="utf-8"))
        calculado = diagnostico_d3.generar_diagnostico()
        self.assertEqual(en_disco, calculado)


if __name__ == "__main__":
    unittest.main()
