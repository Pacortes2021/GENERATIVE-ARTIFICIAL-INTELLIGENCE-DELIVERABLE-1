"""Pruebas unitarias offline para el experimento Multi-LoRA (`exp_multi_lora/`)."""

from __future__ import annotations

import ast
import contextlib
import csv
import json
import re
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = REPO_ROOT / "exp_multi_lora"
EXP_SCRIPTS_DIR = EXP_DIR / "scripts"
EXP_DATOS_DIR = EXP_DIR / "datos"
D4_DIR = REPO_ROOT / "Deliverable 4"
D4_SCRIPTS_DIR = D4_DIR / "scripts"
D4_PROMPTS_DIR = D4_DIR / "prompts"
D3_AGENTES_DIR = REPO_ROOT / "Deliverable 3" / "Deliverable3" / "agentes"

for _p in (EXP_SCRIPTS_DIR, D4_SCRIPTS_DIR, D3_AGENTES_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import antifuga_multi as af  # noqa: E402
import construir_datasets_agentes as cda  # noqa: E402
import entrenar_agente as ea  # noqa: E402
import entrenar_redactor as er  # noqa: E402
import evaluar_d4 as ed4  # noqa: E402
import evaluar_multi_lora as eml  # noqa: E402
import generar_auditoria_multi as gam  # noqa: E402
import resumir_comparativa as rc  # noqa: E402
from orquestador import Orquestador  # noqa: E402


def _cargar_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class _FakeTensor:
    """Tensor mínimo sin CUDA para probar `MultiLoraGenerator` y aislamiento."""

    def __init__(self, data: list[list[float]], shape: tuple[int, ...]) -> None:
        self.data = data
        self.shape = shape

    def float(self) -> "_FakeTensor":
        return self

    def __sub__(self, other: "_FakeTensor") -> "_FakeTensor":
        diff = [
            [a - b for a, b in zip(ra, rb)]
            for ra, rb in zip(self.data, other.data)
        ]
        return _FakeTensor(diff, self.shape)

    def abs(self) -> "_FakeTensor":
        return _FakeTensor([[abs(x) for x in r] for r in self.data], self.shape)

    def max(self) -> "_FakeTensor":
        m = max(x for r in self.data for x in r)
        return _FakeTensor([[m]], (1,))

    def item(self) -> float:
        return float(self.data[0][0])

    def __getitem__(self, idx):
        # Soporta logits[:, -1, :] o slice sencillo en tests de aislamiento
        return self


class _FakeInputs(dict):
    def to(self, _device):
        return self


class _FakeTokenizer:
    eos_token_id = 2
    pad_token_id = 0

    def apply_chat_template(
        self,
        messages,
        tokenize: bool = False,
        add_generation_prompt: bool = False,
        enable_thinking: bool = False,
    ) -> str:
        prompt = messages[-1]["content"]
        return f"<|user|>\n{prompt}\n<|assistant|>\n"

    def __call__(self, text: str, return_tensors: str = "pt") -> _FakeInputs:
        # Tokens ficticios de longitud fija pequeña
        return _FakeInputs(
            {
                "input_ids": _FakeTensor([[1, 2, 3, 4]], (1, 4)),
                "attention_mask": _FakeTensor([[1, 1, 1, 1]], (1, 4)),
            }
        )

    def decode(self, ids, skip_special_tokens: bool = True) -> str:
        if isinstance(ids, list) and ids and isinstance(ids[0], str):
            return ids[0]
        return ""


class _FakePeftModel:
    device = "cpu"

    def __init__(self, respuestas_por_estado: dict[str, list[str]] | None = None) -> None:
        self.active_adapter: str | None = "redactor"
        self.disabled = False
        self.eventos: list[tuple[str, str | None]] = []
        self.gen_kwargs_vistos: list[dict] = []
        self.respuestas_por_estado = respuestas_por_estado or {}
        self.logits_por_modo = {
            "base": [[0.1, 0.2, 0.3]],
            "enrutador": [[1.5, 0.2, 0.3]],
            "recuperador": [[0.1, 2.5, 0.3]],
            "redactor": [[0.1, 0.2, 3.5]],
            "verificador": [[-1.0, 2.0, 0.3]],
        }

    def set_adapter(self, name: str) -> None:
        self.active_adapter = name
        self.disabled = False
        self.eventos.append(("set_adapter", name))

    @contextlib.contextmanager
    def disable_adapter(self):
        prev = self.disabled
        self.disabled = True
        self.eventos.append(("disable_adapter", None))
        try:
            yield
        finally:
            self.disabled = prev

    def generate(self, **kwargs):
        self.gen_kwargs_vistos.append(kwargs)
        modo = "base" if self.disabled else (self.active_adapter or "base")
        self.eventos.append(("generate", modo))
        cola = self.respuestas_por_estado.get(modo, ["{}"])
        texto = cola.pop(0) if len(cola) > 1 else cola[0]
        # El slice `out[0][4:]` devuelve `[texto]` para que `_FakeTokenizer.decode` lo recupere
        return [[1, 2, 3, 4, texto]]

    def __call__(self, **_kwargs):
        modo = "base" if self.disabled else (self.active_adapter or "base")
        vec = self.logits_por_modo[modo]
        return types.SimpleNamespace(logits=_FakeTensor(vec, (1, len(vec[0]))))


class TestDatasetsMultiLora(unittest.TestCase):
    def test_construccion_determinista_y_lf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            cda.construir_todos_datasets(datos_dir=tmp_dir, seed=202604)
            archivos = sorted(p.name for p in EXP_DATOS_DIR.iterdir() if p.is_file())
            expected = {
                "enrutador_train.jsonl",
                "enrutador_val.jsonl",
                "recuperador_train.jsonl",
                "recuperador_val.jsonl",
                "verificador_train.jsonl",
                "verificador_val.jsonl",
                "resumen_datasets_multi_lora.json",
            }
            self.assertEqual(set(archivos), expected)
            for name in expected:
                committed = (EXP_DATOS_DIR / name).read_bytes()
                rebuilt = (tmp_dir / name).read_bytes()
                self.assertEqual(
                    committed,
                    rebuilt,
                    f"Diferencia no determinista en {name}",
                )
                self.assertNotIn(b"\r", committed, f"CRLF detectado en {name}")

    def test_sin_crlf_en_todo_exp_multi_lora(self) -> None:
        for path in EXP_DIR.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".jsonl", ".json", ".md", ".ipynb", ".csv"}:
                self.assertNotIn(b"\r", path.read_bytes(), f"CRLF en {path}")

    def test_antifuga_estricto_en_todos_los_agentes(self) -> None:
        preguntas_eval = af.cargar_preguntas_prohibidas()
        for agente in ("enrutador", "recuperador", "verificador"):
            train = _cargar_jsonl(EXP_DATOS_DIR / f"{agente}_train.jsonl")
            val = _cargar_jsonl(EXP_DATOS_DIR / f"{agente}_val.jsonl")
            audit = af.auditar_antifuga_agente(agente, train + val, preguntas_eval)
            self.assertEqual(audit["unidades_bloqueadas_solapadas"], 0, agente)
            self.assertEqual(audit["menciones_qid_eval"], 0, agente)
            self.assertEqual(audit["solapamiento_train_val"], 0, agente)
            for reg in train + val:
                txt = "\n".join(m["content"] for m in reg["messages"])
                for blocked in af.BLOCKED_UNIT_IDS:
                    self.assertNotIn(blocked, txt, f"{reg['id']} filtra {blocked}")

    def test_esquemas_enrutador(self) -> None:
        for split in ("train", "val"):
            rows = _cargar_jsonl(EXP_DATOS_DIR / f"enrutador_{split}.jsonl")
            self.assertGreater(len(rows), 20)
            for r in rows:
                out = json.loads(r["messages"][1]["content"])
                self.assertEqual(set(out.keys()), {"tipo", "sub_consultas", "documentos"})
                self.assertIn(out["tipo"], af.TIPOS_VALIDOS)
                self.assertTrue(1 <= len(out["sub_consultas"]) <= 3)
                self.assertTrue(set(out["documentos"]).issubset(af.DOCS_VALIDOS))

    def test_esquemas_recuperador_y_guardia_numero_permitido(self) -> None:
        acciones_por_split: dict[str, set[str]] = {"train": set(), "val": set()}
        for split in ("train", "val"):
            rows = _cargar_jsonl(EXP_DATOS_DIR / f"recuperador_{split}.jsonl")
            for r in rows:
                user_msg = r["messages"][0]["content"]
                ctx_raw = user_msg.rsplit("Contexto:", 1)[1].strip()
                ctx = json.loads(ctx_raw)
                out = json.loads(r["messages"][1]["content"])
                self.assertEqual(set(out.keys()), {"accion", "args"})
                acc = out["accion"]
                self.assertIn(acc, af.ACCIONES_VALIDAS)
                acciones_por_split[split].add(acc)
                if acc == "buscar":
                    self.assertTrue(out["args"].get("consulta"))
                    self.assertEqual(out["args"].get("k"), 5)
                elif acc in ("traer", "existe"):
                    doc = out["args"]["doc"]
                    n = int(out["args"]["n"])
                    self.assertIn(doc, ("RI-FI", "RG"))
                    self.assertTrue(
                        af.numero_permitido_orquestador(
                            n,
                            ctx["sub"],
                            ctx.get("feedback_verificador") or "",
                            ctx.get("evidencia_reunida") or [],
                        ),
                        f"{r['id']} fallaría guardia `_numero_permitido`: {out}",
                    )
                else:
                    self.assertEqual(out["args"], {})
        self.assertEqual(acciones_por_split["train"], set(af.ACCIONES_VALIDAS))
        self.assertEqual(acciones_por_split["val"], set(af.ACCIONES_VALIDAS))

    def test_esquemas_verificador_y_cero_alucinaciones_manuales(self) -> None:
        frases_prohibidas = (
            "15 días hábiles",
            "Director de Docencia [RG-ART-025]",
            "entre 27 y 30 horas",
            "30 horas por crédito",
        )
        for split in ("train", "val"):
            rows = _cargar_jsonl(EXP_DATOS_DIR / f"verificador_{split}.jsonl")
            for r in rows:
                out = r["messages"][1]["content"]
                m = re.match(r"^<pensar>.+?</pensar>\n(\{.+\})$", out, flags=re.S)
                self.assertIsNotNone(m, f"Formato inválido en {r['id']}: {out}")
                obj = json.loads(m.group(1))
                self.assertEqual(set(obj.keys()), {"aprobado", "destino", "motivo"})
                self.assertIsInstance(obj["aprobado"], bool)
                self.assertIn(obj["destino"], af.DESTINOS_VALIDOS)
                if obj["aprobado"]:
                    self.assertEqual(obj["destino"], "fin")
                else:
                    self.assertIn(obj["destino"], ("redactor", "recuperador"))
                todo = r["messages"][0]["content"] + "\n" + out
                for mala in frases_prohibidas:
                    self.assertNotIn(mala, todo, f"Dato alucinado `{mala}` en {r['id']}")

    def test_paridad_helpers_con_orquestador(self) -> None:
        corpus_obj, _ = af.cargar_corpus_limpio()
        ev = ["RG-ART-041", "RI-FI-ART-024", "RG-ART-003-DEF-08"]
        borr = "Texto [RG-ART-041] y [RI-FI-ART-099] y [RG-ART-003-DEF-08]."
        self.assertEqual(
            af.chequear_citas_orquestador(corpus_obj, borr, ev),
            Orquestador.chequear_citas(
                types.SimpleNamespace(c=corpus_obj),
                borr,
                {"evidencia": [{"id": uid} for uid in ev]},
            ),
        )
        self.assertFalse(
            af.numero_permitido_orquestador(
                43,
                "Falta citar RG-ART-043 en la respuesta",
                "",
                ["RG-ART-041"],
            )
        )
        self.assertTrue(
            af.numero_permitido_orquestador(
                43,
                "Falta recuperar el Artículo 43 de RG",
                "",
                ["RG-ART-041"],
            )
        )


class TestTokenizacionYEntrenamientoAgent(unittest.TestCase):
    def test_defaults_y_model_card(self) -> None:
        parser = ea.construir_arg_parser()
        for agente in ("enrutador", "recuperador", "verificador", "redactor"):
            args = ea.resolver_args_con_defaults(parser.parse_args(["--agente", agente]))
            self.assertEqual(args.max_seq_length, ea.DEFAULTS_POR_AGENTE[agente]["max_seq_length"])
            self.assertTrue(Path(args.train_jsonl).is_file(), f"Falta train_jsonl de {agente}")
            self.assertTrue(Path(args.val_jsonl).is_file(), f"Falta val_jsonl de {agente}")
        card = ea.generar_model_card_agente(
            "verificador",
            {
                "modelo_base": "Qwen/Qwen3-4B",
                "resultados": {
                    "tiempo_entrenamiento_min": 12.5,
                    "eval_loss_inicial": 1.2,
                    "mejor_eval_loss": 0.35,
                    "mejor_step": 60,
                },
                "datos": {
                    "train_ejemplos": 305,
                    "val_ejemplos": 68,
                    "tokens_train": {"truncados": 0},
                    "tokens_val": {"truncados": 0},
                },
                "hiperparametros": {
                    "metodo": "QLoRA (4-bit NF4 + doble cuantización)",
                    "lora_r": 16,
                    "lora_alpha": 32,
                    "lora_dropout": 0.05,
                },
                "hardware": {"gpu": "NVIDIA A100", "compute_dtype": "torch.bfloat16"},
            },
            hf_repo="Pablox0333/qwen3-4b-verificador-udec-exp",
        )
        self.assertIn("verificador", card)
        self.assertIn("0.35", card)
        self.assertIn("https://huggingface.co/Pablox0333/qwen3-4b-verificador-udec-exp", card)

    def test_tokenizacion_qwen3_real_sin_truncados(self) -> None:
        from transformers import AutoTokenizer

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                er.MODELO_BASE_DEFAULT, local_files_only=True
            )
        except Exception:
            self.skipTest("Tokenizer Qwen3-4B no está en caché local offline.")

        for agente in ("enrutador", "recuperador", "verificador"):
            max_seq = ea.DEFAULTS_POR_AGENTE[agente]["max_seq_length"]
            for split in ("train", "val"):
                regs = er.cargar_jsonl(EXP_DATOS_DIR / f"{agente}_{split}.jsonl")
                ejemplos = [er.construir_ejemplo_sft(r, tokenizer, max_seq) for r in regs]
                stats = er.resumen_longitudes_sft(ejemplos)
                self.assertEqual(
                    stats["truncados"],
                    0,
                    f"Se truncaron ejemplos en {agente}_{split} con max_seq={max_seq}",
                )
                self.assertEqual(
                    len(ejemplos[0]["input_ids"]),
                    len(ejemplos[0]["labels"]),
                )
                self.assertEqual(ejemplos[0]["labels"][0], -100)
                self.assertTrue(any(tok != -100 for tok in ejemplos[0]["labels"]))


class TestEvaluacionMultiLoraYComparativa(unittest.TestCase):
    def test_parsear_lista_agentes(self) -> None:
        self.assertEqual(eml.parsear_lista_agentes("todos"), eml.ROLES_ORDEN)
        self.assertEqual(eml.parsear_lista_agentes("ninguno"), ())
        self.assertEqual(
            eml.parsear_lista_agentes("verificador, redactor"),
            ("redactor", "verificador"),
        )
        with self.assertRaises(ValueError):
            eml.parsear_lista_agentes("enrutador,inventado")
        self.assertEqual(
            eml.normalizar_filtro_qids("H06, 13, dificil_25:H22"),
            {"dificil_25:H06", "congelado_50:13", "dificil_25:H22"},
        )
        self.assertEqual(
            eml.normalizar_filtro_qids("N05,nuevas_20:N12", nombre_set="nuevas_20"),
            {"nuevas_20:N05", "nuevas_20:N12"},
        )

    def test_fuente_default_redactor_fija_d4_v2(self) -> None:
        fuentes = eml.resolver_fuentes_adaptadores_default()
        self.assertEqual(
            fuentes["redactor"],
            (ed4.HF_ADAPTER_DEFAULT, ed4.HF_ADAPTER_REVISION_DEFAULT),
        )

    def test_conmutacion_4_adaptadores_con_orquestador_y_ablacion(self) -> None:
        corpus_obj, _ = af.cargar_corpus_limpio()
        tok = _FakeTokenizer()
        torch_mock = mock.MagicMock()

        enrutador_out = json.dumps(
            {
                "tipo": "factual",
                "sub_consultas": ["requisito de encuesta docente para inscribir asignaturas"],
                "documentos": ["RG"],
            }
        )
        recuperador_out_1 = json.dumps({"accion": "traer", "args": {"doc": "RG", "n": 42}})
        recuperador_out_2 = json.dumps({"accion": "suficiente", "args": {}})
        redactor_malo = (
            "Respuesta: Debe responder la encuesta docente [RG-ART-042].\n"
            "Condiciones o límites: No aplica.\nFuente: [RG-ART-042]"
        )
        redactor_bueno = (
            "Respuesta: Todo alumno deberá contestar la Encuesta de Evaluación Docente al término de cada periodo para inscribir asignaturas [RG-ART-042].\n"
            "Condiciones o límites: Excepciones por retiro de curso o licencia médica [RG-ART-042].\n"
            "Fuente: [RG-ART-042]"
        )
        ver_rechazo = '<pensar>Falta excepción.</pensar>\n{"aprobado": false, "destino": "redactor", "motivo": "faltan excepciones"}'
        ver_ok = '<pensar>Todo verificado.</pensar>\n{"aprobado": true, "destino": "fin", "motivo": "completo"}'

        fake_model = _FakePeftModel(
            {
                "enrutador": [enrutador_out],
                "recuperador": [recuperador_out_1, recuperador_out_2],
                "redactor": [redactor_malo, redactor_bueno],
                "verificador": [ver_rechazo, ver_ok],
            }
        )
        gen = eml.MultiLoraGenerator(
            fake_model,
            tok,
            adaptadores_activos={r: r for r in eml.ROLES_ORDEN},
            greedy=False,
        )
        orq = ed4.crear_orquestador_d4(corpus_obj, gen)
        with mock.patch.dict(sys.modules, {"torch": torch_mock}):
            res = orq.responder("¿Qué exige el Artículo 42 para inscribir asignaturas?")

        self.assertTrue(res["veredicto"]["aprobado"])
        self.assertEqual(res["ciclos"], 2)
        roles_llamados = [x["adaptador_activo"] for x in gen.telemetria]
        self.assertIn("enrutador", roles_llamados)
        self.assertIn("recuperador", roles_llamados)
        self.assertEqual(roles_llamados.count("redactor"), 2)
        self.assertEqual(roles_llamados.count("verificador"), 2)
        self.assertNotIn("base", roles_llamados)
        self.assertNotIn(("disable_adapter", None), fake_model.eventos)

        # Verificar sampling kwargs de D4
        self.assertTrue(fake_model.gen_kwargs_vistos[0]["do_sample"])
        self.assertEqual(fake_model.gen_kwargs_vistos[0]["temperature"], 0.7)
        self.assertEqual(fake_model.gen_kwargs_vistos[0]["top_p"], 0.8)
        self.assertEqual(fake_model.gen_kwargs_vistos[0]["top_k"], 20)

        # Ahora ablación: solo Redactor activo, otros 3 en disable_adapter()
        fake_model_ab = _FakePeftModel(
            {
                "base": [enrutador_out, recuperador_out_2, ver_ok],
                "redactor": [redactor_bueno],
            }
        )
        gen_ab = eml.MultiLoraGenerator(
            fake_model_ab,
            tok,
            adaptadores_activos={"redactor": "redactor"},
            greedy=True,
        )
        orq_ab = ed4.crear_orquestador_d4(corpus_obj, gen_ab)
        with mock.patch.dict(sys.modules, {"torch": torch_mock}):
            orq_ab.responder("¿Qué exige el Artículo 42?")
        modos_ab = [x["adaptador_activo"] for x in gen_ab.telemetria]
        self.assertEqual(modos_ab.count("redactor"), 1)
        self.assertGreaterEqual(modos_ab.count("base"), 2)
        self.assertFalse(fake_model_ab.gen_kwargs_vistos[0]["do_sample"])

    def test_verificar_aislamiento_multi_lora_y_errores(self) -> None:
        tok = _FakeTokenizer()
        torch_mock = mock.MagicMock()
        model = _FakePeftModel()
        with mock.patch.dict(sys.modules, {"torch": torch_mock}):
            res = eml.verificar_aislamiento_multi_lora(model, tok, eml.ROLES_ORDEN)
        self.assertEqual(len(res["max_abs_diff_vs_base"]), 4)
        self.assertEqual(len(res["max_abs_diff_cruzada"]), 6)

        # Caso falla: un adaptador produce logits idénticos a otro
        model.logits_por_modo["verificador"] = list(model.logits_por_modo["redactor"])
        with mock.patch.dict(sys.modules, {"torch": torch_mock}):
            with self.assertRaises(RuntimeError):
                eml.verificar_aislamiento_multi_lora(model, tok, eml.ROLES_ORDEN)

    def test_resumir_comparativa_lee_d4_y_calcula_diffs(self) -> None:
        csv_base = D4_DIR / "evaluacion" / "resultados_control_base_D4_auditados.csv"
        csv_ft = D4_DIR / "evaluacion" / "resultados_agentes_D4_auditados.csv"
        r_base = rc.resumir_corrida("Control Base D4", csv_base)
        r_ft = rc.resumir_corrida("Solo Redactor D4", csv_ft)
        self.assertEqual(r_base["correctos"], 62)
        self.assertEqual(r_ft["correctos"], 60)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            tel_path = tmp_dir / "tel.json"
            tel_path.write_text(
                json.dumps(
                    {
                        "N01": [
                            {"agente": "enrutador", "adaptador_activo": "enrutador", "segundos": 0.4, "output_tokens": 30},
                            {"agente": "redactor", "adaptador_activo": "redactor", "segundos": 1.2, "output_tokens": 110},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            r_tel = rc.resumir_corrida(
                "Multi-LoRA",
                D4_DIR / "evaluacion" / "resultados_nuevas20_ft_D4_auditados.csv",
                tel_path,
            )
            self.assertEqual(r_tel["correctos"], 10)
            self.assertEqual(r_tel["telemetria"]["llamadas_por_adaptador"]["enrutador:enrutador"], 1)
            tabla = rc.formatear_tabla_markdown([r_base, r_ft, r_tel])
            self.assertIn("62/75", tabla)
            self.assertIn("60/75", tabla)


class TestNotebookYCoherencia(unittest.TestCase):
    def test_colab_notebook_ast_y_versiones(self) -> None:
        nb_path = EXP_DIR / "Exp_MultiLoRA_Colab.ipynb"
        self.assertTrue(nb_path.is_file())
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        self.assertEqual(nb["nbformat"], 4)
        todo_src = []
        for idx, cell in enumerate(nb["cells"]):
            src = "".join(cell["source"])
            todo_src.append(src)
            if cell["cell_type"] == "code":
                ast.parse(src, filename=f"notebook_cell_{idx}")
        unido = "\n".join(todo_src)
        self.assertIn("exp/multi-lora-todos", unido)
        self.assertIn("739b031", unido)
        for rel in re.findall(r'Path\("(Deliverable [^"]+)"\)', unido):
            self.assertTrue((REPO_ROOT / rel).exists(), f"Ruta inexistente en notebook: {rel}")
        self.assertEqual(
            len(ed4.cargar_preguntas_evaluacion(filtro_qids={"dificil_25:H06", "dificil_25:H07", "dificil_25:H22"})),
            3,
        )
        self.assertEqual(
            len(
                ed4.cargar_preguntas_desde_csv(
                    REPO_ROOT / "Deliverable 4" / "datos" / "preguntas_nuevas_20.csv",
                    nombre_set="nuevas_20",
                    filtro_qids={"nuevas_20:N05", "nuevas_20:N12"},
                )
            ),
            2,
        )
        cfg = json.loads((D4_DIR / "evaluacion" / "configuracion_evaluacion.json").read_text(encoding="utf-8"))
        for pkg in ("transformers", "peft", "bitsandbytes", "accelerate", "huggingface_hub", "sentence-transformers"):
            pkg_pip = "huggingface-hub" if pkg == "huggingface_hub" else pkg
            self.assertIn(f"{pkg_pip}=={cfg['versiones'][pkg]}", unido)


class TestAuditoriaYArtefactosColab(unittest.TestCase):
    def test_artefactos_entrenamiento_completos_y_sin_truncados(self) -> None:
        ent_dir = EXP_DIR / "entrenamiento"
        for role in ("enrutador", "recuperador", "verificador"):
            role_dir = ent_dir / role
            for rel in (
                "training_metrics.json",
                "smoke_test_val.json",
                "loss_curve.png",
                "loss_curve.pdf",
                "adapter/README.md",
            ):
                self.assertTrue((role_dir / rel).is_file(), f"Falta {role}/{rel}")

            metrics = json.loads((role_dir / "training_metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics["datos"]["tokens_train"]["truncados"], 0)
            self.assertEqual(metrics["datos"]["tokens_val"]["truncados"], 0)
            self.assertEqual(metrics["parametros"]["entrenables_lora"], 33030144)
            res = metrics["resultados"]
            self.assertLess(res["mejor_eval_loss"], res["eval_loss_inicial"])

            smoke = json.loads((role_dir / "smoke_test_val.json").read_text(encoding="utf-8"))
            self.assertEqual(len(smoke), 3)

    def test_auditorias_en_disco_coherentes_con_csvs_y_reporte(self) -> None:
        self.assertTrue((EXP_DIR / "README.md").is_file())
        self.assertTrue((EXP_DIR / "REPORTE_RESULTADOS.md").is_file())

        eval_dir = EXP_DIR / "evaluacion"
        resumen_global = json.loads(
            (eval_dir / "resumen_comparativo_global.json").read_text(encoding="utf-8")
        )
        self.assertEqual(resumen_global["nuevas_20"]["multi_lora_4_agentes"]["aciertos"], 14)
        self.assertEqual(resumen_global["nuevas_20"]["ablacion_red_ver"]["aciertos"], 9)
        self.assertEqual(resumen_global["benchmark_75_d3"]["multi_lora_4_agentes"]["aciertos"], 58)
        self.assertEqual(
            resumen_global["benchmark_75_d3"]["multi_lora_4_agentes"]["por_set"]["congelado_50"]["aciertos_estrictos"],
            40,
        )
        self.assertEqual(
            resumen_global["benchmark_75_d3"]["multi_lora_4_agentes"]["por_set"]["dificil_25"]["aciertos_estrictos"],
            18,
        )
        self.assertEqual(resumen_global["consolidado_95_preguntas"]["multi_lora_4_agentes"]["aciertos"], 72)

        esperados = [
            (
                "multi_lora_nuevas20",
                "resultados_multi_lora_nuevas20.csv",
                "resultados_multi_lora_nuevas20_auditados.csv",
                "auditoria_multi_lora_nuevas20.json",
                "telemetria_multi_lora_nuevas20.json",
                "configuracion_multi_lora_nuevas20.json",
                14,
            ),
            (
                "ablacion_red_ver_nuevas20",
                "resultados_ablacion_red_ver_nuevas20.csv",
                "resultados_ablacion_red_ver_nuevas20_auditados.csv",
                "auditoria_ablacion_red_ver_nuevas20.json",
                "telemetria_ablacion_red_ver_nuevas20.json",
                "configuracion_ablacion_red_ver_nuevas20.json",
                9,
            ),
            (
                "multi_lora_75",
                "resultados_multi_lora_75.csv",
                "resultados_multi_lora_75_auditados.csv",
                "auditoria_multi_lora_75.json",
                "telemetria_multi_lora_75.json",
                "configuracion_multi_lora_75.json",
                58,
            ),
        ]
        cfg_d4 = json.loads((D4_DIR / "evaluacion" / "configuracion_evaluacion.json").read_text(encoding="utf-8"))

        for nombre, raw_csv, aud_csv, aud_json, tel_json, cfg_json, ok_esperados in esperados:
            self.assertEqual(gam.sha256_archivo(eval_dir / raw_csv), gam.SHA256_CRUDOS[raw_csv])
            with (eval_dir / aud_csv).open("r", encoding="utf-8", newline="") as f:
                filas = list(csv.DictReader(f))
            self.assertEqual(sum(int(r["correcto"]) for r in filas), ok_esperados)

            aud = json.loads((eval_dir / aud_json).read_text(encoding="utf-8"))
            self.assertEqual(aud["resumen_global"]["aciertos_estrictos"], ok_esperados)
            self.assertEqual(aud["chequeos_deterministas"]["total_con_citas_inexistentes"], 0)
            self.assertEqual(aud["chequeos_deterministas"]["total_con_citas_fuera_de_evidencia"], 0)
            self.assertEqual(aud["chequeos_deterministas"]["total_fallbacks_enrutador"], 0)

            cfg = json.loads((eval_dir / cfg_json).read_text(encoding="utf-8"))
            self.assertEqual(cfg["prompts_sha256"], cfg_d4["prompts_sha256"])
            self.assertEqual(len(cfg["aislamiento_multi_lora"]["max_abs_diff_vs_base"]), 4)
            self.assertTrue(all(v > 0 for v in cfg["aislamiento_multi_lora"]["max_abs_diff_vs_base"].values()))

            res_rc = rc.resumir_corrida(nombre, eval_dir / aud_csv, eval_dir / tel_json)
            self.assertEqual(res_rc["correctos"], ok_esperados)

    def test_ejecutar_auditoria_en_directorio_temporal_y_sha_invalido(self) -> None:
        eval_dir = EXP_DIR / "evaluacion"
        prefijos = (
            "multi_lora_nuevas20",
            "ablacion_red_ver_nuevas20",
            "multi_lora_75",
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_eval = Path(tmp) / "evaluacion"
            tmp_eval.mkdir(parents=True, exist_ok=True)
            for pref in prefijos:
                for kind in ("resultados", "configuracion", "telemetria", "trazas"):
                    ext = "csv" if kind == "resultados" else "json"
                    shutil.copy2(eval_dir / f"{kind}_{pref}.{ext}", tmp_eval / f"{kind}_{pref}.{ext}")

            resumen_tmp = gam.ejecutar_auditoria(
                eval_dir=tmp_eval,
                corpus_path=D3_AGENTES_DIR / "corpus.json",
                d4_eval_dir=D4_DIR / "evaluacion",
                entrenamiento_dir=EXP_DIR / "entrenamiento",
            )
            resumen_disco = json.loads(
                (eval_dir / "resumen_comparativo_global.json").read_text(encoding="utf-8")
            )
            self.assertEqual(resumen_tmp, resumen_disco)
            for fname in (
                "auditoria_multi_lora_nuevas20.json",
                "auditoria_ablacion_red_ver_nuevas20.json",
                "auditoria_multi_lora_75.json",
                "resultados_multi_lora_nuevas20_auditados.csv",
                "resultados_ablacion_red_ver_nuevas20_auditados.csv",
                "resultados_multi_lora_75_auditados.csv",
                "resumen_comparativo_global.json",
            ):
                self.assertEqual(
                    (tmp_eval / fname).read_bytes(),
                    (eval_dir / fname).read_bytes(),
                    f"Salida no determinista en {fname}",
                )

            # Corrupción en CSV crudo debe ser rechazada por verificación SHA-256
            raw_n20 = tmp_eval / "resultados_multi_lora_nuevas20.csv"
            raw_n20.write_text(raw_n20.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                gam.ejecutar_auditoria(
                    eval_dir=tmp_eval,
                    corpus_path=D3_AGENTES_DIR / "corpus.json",
                    d4_eval_dir=D4_DIR / "evaluacion",
                    entrenamiento_dir=EXP_DIR / "entrenamiento",
                )


if __name__ == "__main__":
    unittest.main()
