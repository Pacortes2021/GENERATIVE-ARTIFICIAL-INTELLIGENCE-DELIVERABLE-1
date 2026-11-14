"""Pruebas de integridad, formato y antifuga para el dataset de Redactor (Paso 2)."""

from __future__ import annotations

import ast
import json
import re
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

DELIVERABLE4_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = DELIVERABLE4_DIR.parent
DELIVERABLE3_DIR = REPO_ROOT / "Deliverable 3" / "Deliverable3"
SCRIPTS_DIR = DELIVERABLE4_DIR / "scripts"
DATOS_DIR = DELIVERABLE4_DIR / "datos"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import construir_dataset as cd  # noqa: E402
from dataset_blocks.reglas_v2 import (  # noqa: E402
    BLOCKED_UNIT_IDS,
    LEAK_QID_RE,
    UNIT_ID_REF_RE,
)


def _leer_jsonl(path: Path) -> list[dict]:
    lineas = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [json.loads(l) for l in lineas]


def _extraer_modos_orquestador(orquestador_path: Path) -> dict[str, str]:
    arbol = ast.parse(orquestador_path.read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign):
            for target in nodo.targets:
                if isinstance(target, ast.Name) and target.id == "MODOS":
                    valor = ast.literal_eval(nodo.value)
                    assert isinstance(valor, dict)
                    return valor
    raise AssertionError(f"No se encontró MODOS en {orquestador_path}")


class TestDatasetRedactorD4(unittest.TestCase):
    """Valida estructura, trazabilidad con corpus.json y antifuga contra D3."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus_by_id = cd.cargar_unidades_corpus(cd.DEFAULT_CORPUS_PATH)
        cls.eval_rows = cd.cargar_preguntas_eval(cd.DEFAULT_EVAL_CSV_PATH)
        cls.train_rows = _leer_jsonl(DATOS_DIR / "redactor_train.jsonl")
        cls.val_rows = _leer_jsonl(DATOS_DIR / "redactor_val.jsonl")
        cls.resumen = json.loads(
            (DATOS_DIR / "dataset_resumen.json").read_text(encoding="utf-8")
        )
        cls.muestra_md = (DATOS_DIR / "MUESTRA_REVISION_MANUAL.md").read_text(
            encoding="utf-8"
        )

    def test_modos_coinciden_con_orquestador_d3(self) -> None:
        modos_d3 = _extraer_modos_orquestador(
            DELIVERABLE3_DIR / "agentes" / "orquestador.py"
        )
        self.assertEqual(cd.MODOS, modos_d3)

    def test_conteos_splits_y_bloques_exactos(self) -> None:
        self.assertEqual(len(self.train_rows), 180)
        self.assertEqual(len(self.val_rows), 30)
        todos = self.train_rows + self.val_rows
        self.assertEqual(len(todos), 210)

        train_ids = {r["id"] for r in self.train_rows}
        val_ids = {r["id"] for r in self.val_rows}
        self.assertEqual(len(train_ids), 180)
        self.assertEqual(len(val_ids), 30)
        self.assertTrue(train_ids.isdisjoint(val_ids))

        conteo = Counter((r["bloque"], r["split"]) for r in todos)
        for bloque, esperado in cd.EXPECTED_COUNTS.items():
            self.assertEqual(conteo[(bloque, "train")], esperado["train"])
            self.assertEqual(conteo[(bloque, "val")], esperado["val"])

    def test_formato_mensajes_evidencia_y_citas(self) -> None:
        todos = self.train_rows + self.val_rows
        primera_pos_clave = 0
        con_claves = 0

        specs_by_id = {s["id"]: s for s in cd.todas_las_especificaciones()}

        for reg in todos:
            sid = reg["id"]
            msgs = reg["messages"]
            self.assertEqual([m["role"] for m in msgs], ["user", "assistant"])

            user_txt = msgs[0]["content"]
            asst_txt = msgs[1]["content"]

            self.assertFalse(cd.PLACEHOLDER_RE.search(user_txt), f"Placeholder en {sid}")
            self.assertIn("<evidencia>", user_txt)
            self.assertLessEqual(len(reg["evidencia_ids"]), 6)
            for uid in reg["evidencia_ids"]:
                self.assertIn(uid, self.corpus_by_id)
                self.assertIn(f"[{uid}] {self.corpus_by_id[uid]}", user_txt)

            if reg["bloque"] == "resiliencia_feedback":
                self.assertNotIn("(primera versión, sin observaciones)", user_txt)

            m = re.match(
                r"^<pensar>\n(.+?)\n</pensar>\n"
                r"Respuesta: (.+)\n"
                r"Condiciones o límites: (.+)\n"
                r"Fuente: (.+)$",
                asst_txt,
                flags=re.S,
            )
            self.assertIsNotNone(m, f"Formato assistant inválido en {sid}:\n{asst_txt}")
            respuesta, condiciones, fuente = m.group(2), m.group(3), m.group(4)
            self.assertNotIn("\n", respuesta)
            self.assertNotIn("\n", condiciones)
            self.assertNotIn("\n", fuente)

            ev_set = set(reg["evidencia_ids"])
            for cid in cd.CITA_RE.findall(asst_txt):
                self.assertIn(cid, self.corpus_by_id, f"Cita inexistente [{cid}] en {sid}")
                self.assertIn(cid, ev_set, f"Cita fuera de evidencia [{cid}] en {sid}")

            citas_resp_cond = set(cd.CITA_RE.findall(respuesta)) | set(
                cd.CITA_RE.findall(condiciones)
            )
            citas_fuente = set(cd.CITA_RE.findall(fuente))
            self.assertTrue(
                citas_resp_cond.issubset(citas_fuente),
                f"{sid}: citas en Respuesta/Condiciones faltantes en Fuente: {sorted(citas_resp_cond - citas_fuente)}",
            )
            if fuente == "sin respaldo en la normativa consultada":
                self.assertEqual(
                    citas_resp_cond,
                    set(),
                    f"{sid}: contradicción Fuente sin respaldo con citas {sorted(citas_resp_cond)}",
                )

            claves = specs_by_id[sid]["evidencia_clave"]
            if claves:
                con_claves += 1
                if reg["evidencia_ids"][0] in claves:
                    primera_pos_clave += 1

        # Verificar que el barajado evita el sesgo de colocar siempre la clave al inicio
        self.assertGreater(con_claves, 0)
        self.assertLess(primera_pos_clave / con_claves, 0.85)

    def test_antifuga_contra_evaluacion_d3(self) -> None:
        specs = cd.todas_las_especificaciones()
        auditoria = cd.auditar_antifuga(specs, self.eval_rows, etiqueta="evaluacion_d3")
        self.assertEqual(auditoria["duplicados_internos"], 0)
        self.assertEqual(auditoria["coincidencias_exactas_eval"], 0)
        self.assertEqual(auditoria["alertas_sobre_umbral"], 0)
        max_score = auditoria["top_10_pares_mas_cercanos"][0]["score_max"]
        self.assertLess(max_score, 0.75)

        nuevas_rows = cd.cargar_preguntas_nuevas(cd.DEFAULT_NUEVAS_CSV_PATH)
        self.assertEqual(len(nuevas_rows), 20)
        auditoria_nuevas = cd.auditar_antifuga(
            specs, nuevas_rows, etiqueta="evaluacion_nuevas_20"
        )
        self.assertEqual(auditoria_nuevas["coincidencias_exactas_eval"], 0)
        self.assertEqual(auditoria_nuevas["alertas_sobre_umbral"], 0)

    def test_separacion_estricta_unidades_sin_fugas_y_balance_no_aplica(self) -> None:
        todos = self.train_rows + self.val_rows
        no_aplica_count = 0
        for reg in todos:
            sid = reg["id"]
            ev_set = set(reg["evidencia_ids"])
            self.assertTrue(
                ev_set.isdisjoint(BLOCKED_UNIT_IDS),
                f"{sid} contiene unidades reservadas de eval en evidencia_ids: {sorted(ev_set & BLOCKED_UNIT_IDS)}",
            )
            asst_txt = reg["messages"][1]["content"]
            self.assertFalse(
                LEAK_QID_RE.search(asst_txt),
                f"{sid} contiene fuga QID/trampa: {LEAK_QID_RE.findall(asst_txt)}",
            )
            refs = set(UNIT_ID_REF_RE.findall(asst_txt))
            self.assertTrue(
                refs.isdisjoint(BLOCKED_UNIT_IDS),
                f"{sid} refiere unidad reservada en respuesta: {sorted(refs & BLOCKED_UNIT_IDS)}",
            )
            if "\nCondiciones o límites: No aplica\n" in asst_txt:
                no_aplica_count += 1
        self.assertGreaterEqual(no_aplica_count, 40)

    def test_muestra_manual_y_artefactos_sincronizados(self) -> None:
        self.assertEqual(len(self.resumen["muestra_revision_manual_ids"]), 30)
        for sid in self.resumen["muestra_revision_manual_ids"]:
            self.assertIn(f"`{sid}`", self.muestra_md)

        for fname in (
            "redactor_train.jsonl",
            "redactor_val.jsonl",
            "MUESTRA_REVISION_MANUAL.md",
            "preguntas_nuevas_20.csv",
        ):
            raw = (DATOS_DIR / fname).read_bytes()
            self.assertNotIn(b"\r\n", raw, f"CRLF encontrado en {fname}")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            calculado = cd.construir_dataset(datos_dir=tmp_dir)
            esperado = {k: v for k, v in self.resumen.items() if k != "archivos_generados"}
            obtenido = {k: v for k, v in calculado.items() if k != "archivos_generados"}
            self.assertEqual(esperado, obtenido)
            for fname in (
                "redactor_train.jsonl",
                "redactor_val.jsonl",
                "MUESTRA_REVISION_MANUAL.md",
            ):
                self.assertEqual(
                    (DATOS_DIR / fname).read_bytes(),
                    (tmp_dir / fname).read_bytes(),
                )

    def test_firmas_manuales_csv_y_aislamiento_tmp_dir(self) -> None:
        registros = self.train_rows + self.val_rows
        specs_by_id = {s["id"]: s for s in cd.todas_las_especificaciones()}
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            firmas_csv = tmp_dir / "revision_manual_firmas.csv"
            firmas_csv.write_bytes(
                (
                    "sample_id,revisor,fecha,veredicto,observacion\n"
                    "B1-T01,Álvaro Contreras,2026-11-14,Aprobado,\n"
                    "B1-T18,Álvaro Contreras,2026-11-14,Observado,Cita RG-ART-011 junto a RI-FI-ART-033\n"
                ).encode("utf-8")
            )
            out_md = tmp_dir / "MUESTRA_REVISION_MANUAL.md"
            ids = cd.generar_muestra_manual(
                registros,
                specs_by_id,
                self.corpus_by_id,
                out_md,
                firmas_csv_path=firmas_csv,
            )
            self.assertEqual(len(ids), 30)
            txt = out_md.read_text(encoding="utf-8")
            self.assertIn("| 01 | `B1-T01` | `citas_cruce` / `train` | Álvaro Contreras | 2026-11-14 | Aprobado | |", txt)
            self.assertIn(
                "| 02 | `B1-T18` | `citas_cruce` / `train` | Álvaro Contreras | 2026-11-14 | Observado | Cita RG-ART-011 junto a RI-FI-ART-033 |",
                txt,
            )
            self.assertIn("| 03 | `B1-T35` | `citas_cruce` / `train` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |", txt)


if __name__ == "__main__":
    unittest.main()
