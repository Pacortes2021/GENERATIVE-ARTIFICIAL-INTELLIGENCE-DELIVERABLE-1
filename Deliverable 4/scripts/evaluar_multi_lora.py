"""Evaluación Multi-LoRA oficial de Deliverable 4 (`Enrutador` + `Recuperador` + `Redactor`).

Carga un único modelo `Qwen/Qwen3-4B` cuantizado 4-bit NF4 y conmuta los adaptadores
QLoRA por rol mediante `model.set_adapter(rol)`, manteniendo al `Verificador` con pesos
base íntegros vía `model.disable_adapter()`.

Configuración oficial D4: `--agentes enrutador,recuperador,redactor`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

D4_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = D4_DIR.parent
D4_SCRIPTS_DIR = D4_DIR / "scripts"
D4_TRAIN_DIR = D4_DIR / "entrenamiento"
D4_EVAL_DIR = D4_DIR / "evaluacion"
D3_AGENTES_DIR = REPO_ROOT / "Deliverable 3" / "Deliverable3" / "agentes"

for _p in (D4_SCRIPTS_DIR, D3_AGENTES_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import evaluar_d4 as ed4  # noqa: E402
from entrenar_redactor import MODELO_BASE_DEFAULT, es_bf16_nativo, formatear_prompt_usuario  # noqa: E402

ROLES_ORDEN: tuple[str, ...] = ("enrutador", "recuperador", "redactor", "verificador")
ROLES_OFICIALES_D4: tuple[str, ...] = ("enrutador", "recuperador", "redactor")
DEFAULT_DRIVE_ENTRENAMIENTO = Path("/content/drive/MyDrive/UdeC_GenIA_Exp_MultiLoRA/entrenamiento")
MANIFEST_HF_PATH = D4_TRAIN_DIR / "manifest_adaptadores_hf.json"

HF_REPOS_D4: dict[str, tuple[str, str | None]] = {
    "enrutador": (
        "Pablox0333/qwen3-4b-enrutador-udec-d4",
        "ab65a4f0b0e969d8e9c0d3975d06d6e1791afec7",
    ),
    "recuperador": (
        "Pablox0333/qwen3-4b-recuperador-udec-d4",
        "6bd665a314663f224ef3eb17823febbd9bc1d10c",
    ),
    "redactor": (ed4.HF_ADAPTER_DEFAULT, ed4.HF_ADAPTER_REVISION_DEFAULT),
    "verificador": (str(D4_TRAIN_DIR / "verificador" / "adapter"), None),
}


def cargar_manifest_hf(manifest_path: Path = MANIFEST_HF_PATH) -> dict[str, dict[str, Any]]:
    """Lee el manifiesto oficial de adaptadores HF (repo, revisión y SHA-256) si existe."""
    if not manifest_path.is_file():
        return {}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return dict(data.get("adaptadores", {}))


def _tiene_pesos_adapter(carpeta: Path) -> bool:
    return (carpeta / "adapter_model.safetensors").is_file() or (
        carpeta / "adapter_model.bin"
    ).is_file()


def _sha256_archivo_adapter(carpeta: Path) -> str | None:
    for nombre in ("adapter_model.safetensors", "adapter_model.bin"):
        p = carpeta / nombre
        if p.is_file():
            h = hashlib.sha256()
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            return h.hexdigest()
    return None


def resolver_fuentes_adaptadores_default(
    drive_dir: Path | None = DEFAULT_DRIVE_ENTRENAMIENTO,
    solo_hf: bool = False,
) -> dict[str, tuple[str, str | None]]:
    """Resuelve cada rol: prioriza HF fijado si `solo_hf` o tiene revisión fijada."""
    manifest = cargar_manifest_hf()
    fuentes: dict[str, tuple[str, str | None]] = {}
    for rol in ROLES_ORDEN:
        info_man = manifest.get(rol, {})
        repo_man = info_man.get("hf_repo")
        rev_man = info_man.get("hf_revision")
        repo_def, rev_def = HF_REPOS_D4[rol]
        hf_pair = (repo_man or repo_def, rev_man or rev_def)

        if solo_hf or (hf_pair[1] and rol in ROLES_OFICIALES_D4):
            fuentes[rol] = hf_pair
            continue

        local_adapter = (
            D4_TRAIN_DIR / "adapter"
            if rol == "redactor"
            else D4_TRAIN_DIR / rol / "adapter"
        )
        if _tiene_pesos_adapter(local_adapter):
            fuentes[rol] = (str(local_adapter), None)
            continue
        if drive_dir is not None:
            drive_adapter = drive_dir / rol / "adapter"
            if _tiene_pesos_adapter(drive_adapter):
                fuentes[rol] = (str(drive_adapter), None)
                continue
        fuentes[rol] = hf_pair
    return fuentes


def parsear_lista_agentes(valor: str) -> tuple[str, ...]:
    """Normaliza `--agentes enrutador,recuperador,redactor` o `oficial`/`todos`/`ninguno`."""
    raw = [x.strip().lower() for x in valor.split(",") if x.strip()]
    if not raw or raw == ["ninguno"] or raw == ["none"]:
        return ()
    if raw == ["oficial"] or raw == ["3lora"]:
        return ROLES_OFICIALES_D4
    if raw == ["todos"] or raw == ["all"]:
        return ROLES_ORDEN
    invalidos = [x for x in raw if x not in ROLES_ORDEN]
    if invalidos:
        raise ValueError(
            f"Agentes desconocidos: {invalidos}. Válidos: {list(ROLES_ORDEN)}, 'oficial', 'todos', 'ninguno'."
        )
    return tuple(r for r in ROLES_ORDEN if r in raw)


def normalizar_filtro_qids(
    raw_qids: str | None,
    nombre_set: str | None = None,
) -> set[str] | None:
    """Normaliza IDs cortos (`H07`, `11`, `N05`) o prefijados (`dificil_25:H07`)."""
    if not raw_qids:
        return None
    salida: set[str] = set()
    for token in raw_qids.split(","):
        q = token.strip()
        if not q:
            continue
        if ":" in q:
            salida.add(q)
        elif nombre_set:
            salida.add(f"{nombre_set}:{q}")
        elif q.upper().startswith("H"):
            salida.add(f"dificil_25:{q.upper()}")
        else:
            salida.add(f"congelado_50:{q}")
    return salida or None


class MultiLoraGenerator:
    """Generador que conmuta el adaptador LoRA por rol y apaga LoRA en roles base."""

    def __init__(
        self,
        model: Any,
        tokenizer: Any,
        adaptadores_activos: dict[str, str | None] | None = None,
        greedy: bool = False,
        semilla_base: int = ed4.SEMILLA_BASE,
        max_tokens_por_agente: dict[str, int] | None = None,
        verbose: bool = False,
        step_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self.model = model
        self.tokenizer = tokenizer
        if adaptadores_activos is None:
            self.adaptadores_activos: dict[str, str | None] = {
                r: (r if r in ROLES_OFICIALES_D4 else None) for r in ROLES_ORDEN
            }
        else:
            self.adaptadores_activos = {
                r: adaptadores_activos.get(r) for r in ROLES_ORDEN
            }
        self.greedy = greedy
        self.semilla_base = semilla_base
        self.max_tokens = dict(max_tokens_por_agente or ed4.MAX_TOKENS_POR_AGENTE)
        self.verbose = verbose
        self.step_callback = step_callback
        self.telemetria: list[dict[str, Any]] = []
        self._ciclo_actual = 1
        self._ultimo_agente: str | None = None

    def reiniciar_estado_sesion(self) -> None:
        """Reinicia el conteo de ciclo al comenzar una pregunta en modo verbose."""
        self._ciclo_actual = 1
        self._ultimo_agente = None

    @staticmethod
    def _formatear_verbose(agente: str, salida: str, despues_de_enrutador: bool = False) -> str:
        """Resume la salida en vivo sin quedar truncado dentro de `<pensar>...</pensar>`."""
        import re

        ag = str(agente).strip().lower()
        txt = str(salida).strip()
        if ag == "redactor":
            limpio = re.sub(r"<pensar>.*?</pensar>", "", txt, flags=re.DOTALL | re.IGNORECASE).strip()
            base_txt = limpio or txt
            compacto = " ".join(base_txt.split())
            return compacto if len(compacto) <= 280 else compacto[:277] + "..."
        try:
            obj = json.loads(txt)
        except Exception:
            compacto = " ".join(txt.split())
            return compacto if len(compacto) <= 260 else compacto[:257] + "..."
        if ag == "enrutador" and isinstance(obj, dict):
            subs = obj.get("sub_consultas", [])
            subs_txt = "; ".join(str(s) for s in subs[:2])
            if len(subs) > 2:
                subs_txt += f" (+{len(subs) - 2})"
            return f"tipo={obj.get('tipo')} | docs={obj.get('documentos')} | subs=[{subs_txt}]"
        if ag == "recuperador" and isinstance(obj, dict):
            acc = obj.get("accion")
            args = obj.get("args", {})
            nota = " (post búsqueda base E5)" if despues_de_enrutador else ""
            if acc == "suficiente":
                return f"accion=suficiente{nota}"
            return f"accion={acc} args={json.dumps(args, ensure_ascii=False)}{nota}"
        if ag == "verificador" and isinstance(obj, dict):
            est = "APROBADO -> fin" if obj.get("aprobado") else f"RECHAZO -> {obj.get('destino')}"
            mot = " ".join(str(obj.get("motivo", "")).split())
            if len(mot) > 180:
                mot = mot[:177] + "..."
            return f"{est} | {mot}"
        return " ".join(txt.split())[:260]

    def __call__(self, agente: str, prompt: str, max_new_tokens: int | None = None) -> str:
        import torch

        text = formatear_prompt_usuario(self.tokenizer, prompt)
        tokens_budget = max_new_tokens or self.max_tokens.get(agente, 512)
        semilla = ed4.semilla_para_llamada(agente, prompt, self.semilla_base)
        nombre_adaptador = self.adaptadores_activos.get(agente)
        usa_adaptador = bool(nombre_adaptador)

        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        torch.manual_seed(semilla)

        gen_kwargs: dict[str, Any] = {
            "max_new_tokens": tokens_budget,
            "pad_token_id": self.tokenizer.eos_token_id,
        }
        if self.greedy:
            gen_kwargs["do_sample"] = False
        else:
            gen_kwargs.update(
                {
                    "do_sample": True,
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 20,
                    "min_p": 0.0,
                }
            )

        t0 = time.time()
        with torch.no_grad():
            if usa_adaptador:
                self.model.set_adapter(nombre_adaptador)
                out = self.model.generate(**inputs, **gen_kwargs)
            else:
                with self.model.disable_adapter():
                    out = self.model.generate(**inputs, **gen_kwargs)
        dt = time.time() - t0

        input_len = int(inputs["input_ids"].shape[1])
        gen_ids = out[0][input_len:]
        salida = self.tokenizer.decode(gen_ids, skip_special_tokens=True).strip()

        registro = {
            "agente": agente,
            "usa_adaptador": usa_adaptador,
            "adaptador_activo": nombre_adaptador or "base",
            "input_tokens": input_len,
            "output_tokens": int(len(gen_ids)),
            "segundos": round(dt, 3),
            "semilla": semilla,
        }
        self.telemetria.append(registro)

        if self.verbose or self.step_callback is not None:
            evento = {**registro, "paso": len(self.telemetria), "salida": salida}
            if self.verbose:
                tag = f"LoRA ON ({nombre_adaptador})" if usa_adaptador else "LoRA OFF (Base)"
                desp_enr = agente == "recuperador" and self._ultimo_agente == "enrutador"
                if agente == "enrutador" and self._ciclo_actual == 1:
                    print("  ── Ciclo 1 ──", flush=True)
                resumen = self._formatear_verbose(agente, salida, despues_de_enrutador=desp_enr)
                print(
                    f"  [Paso {evento['paso']:02d} | {agente.upper():11s} | {tag:22s} | {dt:5.2f}s] {resumen}",
                    flush=True,
                )
                if agente == "verificador":
                    try:
                        ver_obj = json.loads(salida)
                        if isinstance(ver_obj, dict) and not ver_obj.get("aprobado"):
                            self._ciclo_actual += 1
                            dest = ver_obj.get("destino", "redactor")
                            print(
                                f"  ── Ciclo {self._ciclo_actual} (reintento en {dest} tras rechazo del Verificador) ──",
                                flush=True,
                            )
                    except Exception:
                        pass
                self._ultimo_agente = str(agente).strip().lower()
            if self.step_callback is not None:
                self.step_callback(evento)

        return salida


def cargar_modelo_y_multi_lora(
    modelo_base: str,
    fuentes_por_rol: dict[str, tuple[str, str | None]],
    roles_a_cargar: tuple[str, ...] = ROLES_OFICIALES_D4,
) -> tuple[Any, Any, str, str]:
    """Carga una sola instancia 4-bit NF4 de `Qwen3-4B` y enchufa cada adaptador por nombre."""
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    cap = torch.cuda.get_device_capability(0) if torch.cuda.is_available() else (0, 0)
    bf16_nativo = torch.cuda.is_available() and es_bf16_nativo(
        cap, torch.cuda.is_bf16_supported()
    )
    compute_dtype = torch.bfloat16 if bf16_nativo else torch.float16

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(modelo_base)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    base = AutoModelForCausalLM.from_pretrained(
        modelo_base,
        quantization_config=bnb_config,
        device_map="auto",
    )

    roles_efectivos = roles_a_cargar or ("redactor",)
    model: Any = None
    for idx, rol in enumerate(roles_efectivos):
        repo_o_path, revision = fuentes_por_rol[rol]
        p_local = Path(repo_o_path)
        es_ruta_local = (
            repo_o_path.startswith((".", "/"))
            or "\\" in repo_o_path
            or repo_o_path.count("/") > 1
        )
        if es_ruta_local and not p_local.exists():
            raise FileNotFoundError(
                f"No existe el adaptador local para `{rol}` en `{repo_o_path}`. "
                f"Usa Google Drive (`/content/drive/MyDrive/UdeC_GenIA_Exp_MultiLoRA`), "
                f"entrena con `entrenar_agente.py --agente {rol}`, o pasa `--adaptador-{rol} <usuario/repo-hf>`."
            )
        peft_kwargs: dict[str, Any] = {}
        if revision and not p_local.exists():
            peft_kwargs["revision"] = revision
        if idx == 0:
            model = PeftModel.from_pretrained(
                base,
                repo_o_path,
                adapter_name=rol,
                **peft_kwargs,
            )
        else:
            model.load_adapter(
                repo_o_path,
                adapter_name=rol,
                **peft_kwargs,
            )

    model.eval()
    return (
        model,
        tokenizer,
        str(compute_dtype),
        getattr(base.config, "_commit_hash", None) or "",
    )


def verificar_aislamiento_multi_lora(
    model: Any,
    tokenizer: Any,
    roles_activos: tuple[str, ...],
) -> dict[str, Any]:
    """Verifica que cada adaptador difiere del modelo base Y de los demás adaptadores."""
    import torch

    if not roles_activos:
        return {"roles_activos": [], "max_abs_diff_vs_base": {}, "max_abs_diff_cruzada": {}}

    texto = formatear_prompt_usuario(
        tokenizer,
        "Responde brevemente: verificación de conmutación Multi-LoRA entre roles.",
    )
    inputs = tokenizer(texto, return_tensors="pt").to(model.device)
    logits_por_modo: dict[str, Any] = {}

    with torch.no_grad():
        with model.disable_adapter():
            logits_por_modo["base"] = model(**inputs).logits[:, -1, :].float()
        for rol in roles_activos:
            model.set_adapter(rol)
            logits_por_modo[rol] = model(**inputs).logits[:, -1, :].float()

    diff_vs_base: dict[str, float] = {}
    for rol in roles_activos:
        d = float((logits_por_modo[rol] - logits_por_modo["base"]).abs().max().item())
        if d <= 0.0:
            raise RuntimeError(
                f"El adaptador `{rol}` no produjo diferencia frente al modelo base (diff={d})."
            )
        diff_vs_base[rol] = round(d, 6)

    diff_cruzada: dict[str, float] = {}
    for i, r1 in enumerate(roles_activos):
        for r2 in roles_activos[i + 1 :]:
            d = float((logits_por_modo[r1] - logits_por_modo[r2]).abs().max().item())
            if d <= 0.0:
                raise RuntimeError(
                    f"Los adaptadores `{r1}` y `{r2}` dieron logits idénticos (diff={d}); "
                    "revisa si `set_adapter()` o los pesos cargados están duplicados."
                )
            diff_cruzada[f"{r1}_vs_{r2}"] = round(d, 6)

    return {
        "roles_activos": list(roles_activos),
        "max_abs_diff_vs_base": diff_vs_base,
        "max_abs_diff_cruzada": diff_cruzada,
    }


def ejecutar_comparativa_pareada(
    preguntas: list[dict[str, str]],
    corpus: Any,
    generador_a: MultiLoraGenerator,
    generador_b: MultiLoraGenerator,
    etiqueta_a: str,
    etiqueta_b: str,
    output_path: Path,
) -> list[dict[str, Any]]:
    """Compara lado a lado dos configuraciones de agentes (ej. Base vs D4 3-LoRA)."""
    orq_a = ed4.crear_orquestador_d4(corpus, generador_a)
    orq_b = ed4.crear_orquestador_d4(corpus, generador_b)

    resultados: list[dict[str, Any]] = []
    for item in preguntas:
        if getattr(generador_a, "verbose", False):
            if hasattr(generador_a, "reiniciar_estado_sesion"):
                generador_a.reiniciar_estado_sesion()
            print(f"\n{'=' * 78}\n>>> [SISTEMA 1/2: {etiqueta_a.upper()}] {item['qid']} — {item['pregunta']}", flush=True)
        t0 = time.time()
        res_a = orq_a.responder(item["pregunta"])
        dt_a = round(time.time() - t0, 2)
        llamadas_a = sum(1 for p in res_a["traza"] if not p.get("decidido_por"))
        if getattr(generador_a, "verbose", False):
            ver_a = "APROBADO" if res_a["veredicto"].get("aprobado") else f"RECHAZO->{res_a['veredicto'].get('destino', '?')}"
            print(f"[FIN {etiqueta_a.upper()}] ciclos={res_a['ciclos']} | llamadas_llm={llamadas_a} | tiempo={dt_a}s | verificador={ver_a}", flush=True)

        if getattr(generador_b, "verbose", False):
            if hasattr(generador_b, "reiniciar_estado_sesion"):
                generador_b.reiniciar_estado_sesion()
            print(f"\n{'=' * 78}\n>>> [SISTEMA 2/2: {etiqueta_b.upper()}] {item['qid']} — {item['pregunta']}", flush=True)
        t1 = time.time()
        res_b = orq_b.responder(item["pregunta"])
        dt_b = round(time.time() - t1, 2)
        llamadas_b = sum(1 for p in res_b["traza"] if not p.get("decidido_por"))
        if getattr(generador_b, "verbose", False):
            ver_b = "APROBADO" if res_b["veredicto"].get("aprobado") else f"RECHAZO->{res_b['veredicto'].get('destino', '?')}"
            print(f"[FIN {etiqueta_b.upper()}] ciclos={res_b['ciclos']} | llamadas_llm={llamadas_b} | tiempo={dt_b}s | verificador={ver_b}", flush=True)

        resultados.append(
            {
                "qid": item["qid"],
                "set": item["set"],
                "id": item["id"],
                "categoria": item["categoria"],
                "pregunta": item["pregunta"],
                "gold_dato": item["gold_dato"],
                "gold_fuente": item["gold_fuente"],
                etiqueta_a: {
                    "respuesta": res_a["respuesta"],
                    "correcto": None,
                    "veredicto": res_a["veredicto"],
                    "ciclos": res_a["ciclos"],
                    "llamadas_modelo": llamadas_a,
                    "tipo_enrutador": res_a["tipo"],
                    "segundos": dt_a,
                    "fuentes_traidas": ed4.extraer_fuentes_de_traza(res_a["traza"]),
                    "traza": res_a["traza"],
                },
                etiqueta_b: {
                    "respuesta": res_b["respuesta"],
                    "correcto": None,
                    "veredicto": res_b["veredicto"],
                    "ciclos": res_b["ciclos"],
                    "llamadas_modelo": llamadas_b,
                    "tipo_enrutador": res_b["tipo"],
                    "segundos": dt_b,
                    "fuentes_traidas": ed4.extraer_fuentes_de_traza(res_b["traza"]),
                    "traza": res_b["traza"],
                },
            }
        )
        ed4.escribir_json_atomico(output_path, resultados)
    return resultados


def construir_arg_parser() -> argparse.ArgumentParser:
    defaults = resolver_fuentes_adaptadores_default()
    p = argparse.ArgumentParser(
        description="Evaluación Multi-LoRA sobre Qwen3-4B (Deliverable 4: 3 agentes LoRA + Verificador Base)."
    )
    p.add_argument("--modelo-base", default=MODELO_BASE_DEFAULT)
    p.add_argument(
        "--agentes",
        default="enrutador,recuperador,redactor",
        help="Roles con LoRA activo separados por coma (`enrutador,recuperador,redactor`, `ninguno`, `todos`).",
    )
    for rol in ROLES_ORDEN:
        repo_def, rev_def = defaults[rol]
        p.add_argument(f"--adaptador-{rol}", default=repo_def)
        p.add_argument(f"--rev-{rol}", default=rev_def or "")
    p.add_argument("--output-dir", type=Path, default=D4_EVAL_DIR)
    p.add_argument("--output-prefix", default="3lora_75")
    p.add_argument("--preguntas-csv", type=Path, default=None)
    p.add_argument("--nombre-set", default="nuevas_20")
    p.add_argument("--solo-dificiles", action="store_true")
    p.add_argument("--qids", default=None)
    p.add_argument("--greedy", action="store_true")
    p.add_argument("--sin-e5", action="store_true")
    p.add_argument(
        "--comparar-vs-base",
        default=None,
        help="QIDs separados por coma para comparar Base (LoRA OFF) vs --agentes.",
    )
    p.add_argument(
        "--comparar-vs-solo-redactor",
        default=None,
        help="QIDs separados por coma para comparar Solo Redactor FT v2 vs --agentes.",
    )
    p.add_argument("--solo-comparativa", action="store_true")
    p.add_argument(
        "--solo-hf",
        action="store_true",
        help="Fuerza carga de adaptadores desde Hugging Face (ignorando rutas locales o Drive).",
    )
    p.add_argument("--verbose-pasos", action="store_true")
    return p


def _resolver_sha_fuente(fuente: str, revision: str | None, rol: str) -> str | None:
    p = Path(fuente)
    if p.is_dir():
        return _sha256_archivo_adapter(p)
    manifest = cargar_manifest_hf()
    info = manifest.get(rol, {})
    if info.get("hf_repo") == fuente and (
        not revision or info.get("hf_revision") == revision
    ):
        return info.get("adapter_model_sha256")
    try:
        from huggingface_hub import HfApi

        infos = HfApi().get_paths_info(
            repo_id=fuente,
            paths=["adapter_model.safetensors"],
            revision=revision,
            repo_type="model",
        )
        for item in infos:
            lfs = getattr(item, "lfs", None)
            if lfs is not None and getattr(lfs, "sha256", None):
                return str(lfs.sha256)
    except Exception:
        pass
    return None


def main(argv: list[str] | None = None) -> int:
    parser = construir_arg_parser()
    args = parser.parse_args(argv)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    import torch

    prompts_sha = ed4.verificar_prompts_d4()
    roles_activos = parsear_lista_agentes(args.agentes)

    defaults_hf = resolver_fuentes_adaptadores_default(solo_hf=True) if args.solo_hf else None
    fuentes_por_rol: dict[str, tuple[str, str | None]] = {}
    for rol in ROLES_ORDEN:
        if args.solo_hf and defaults_hf is not None and getattr(args, f"adaptador_{rol}") == parser.get_default(f"adaptador_{rol}"):
            fuentes_por_rol[rol] = defaults_hf[rol]
        else:
            fuentes_por_rol[rol] = (
                getattr(args, f"adaptador_{rol}"),
                getattr(args, f"rev_{rol}") or None,
            )
    roles_a_cargar = (
        tuple(dict.fromkeys((*roles_activos, "redactor")))
        if args.comparar_vs_solo_redactor
        else (roles_activos or ("redactor",))
    )

    corpus = ed4.construir_corpus_d3(use_e5=not args.sin_e5)
    model, tokenizer, compute_dtype_str, base_commit = cargar_modelo_y_multi_lora(
        args.modelo_base,
        fuentes_por_rol,
        roles_a_cargar,
    )
    aislamiento = verificar_aislamiento_multi_lora(model, tokenizer, roles_a_cargar)

    adaptadores_map = {rol: (rol if rol in roles_activos else None) for rol in ROLES_ORDEN}
    gen_multi = MultiLoraGenerator(
        model,
        tokenizer,
        adaptadores_activos=adaptadores_map,
        greedy=args.greedy,
        verbose=args.verbose_pasos,
    )

    filtro_qids = normalizar_filtro_qids(
        args.qids,
        nombre_set=args.nombre_set if args.preguntas_csv is not None else None,
    )
    if args.preguntas_csv is not None:
        preguntas = ed4.cargar_preguntas_desde_csv(
            args.preguntas_csv,
            nombre_set=args.nombre_set,
            filtro_qids=filtro_qids,
        )
    else:
        preguntas = ed4.cargar_preguntas_evaluacion(
            solo_dificiles=args.solo_dificiles,
            filtro_qids=filtro_qids,
        )

    if args.comparar_vs_base:
        comp_qids = normalizar_filtro_qids(
            args.comparar_vs_base,
            nombre_set=args.nombre_set if args.preguntas_csv is not None else None,
        )
        preg_comp = (
            ed4.cargar_preguntas_desde_csv(
                args.preguntas_csv, nombre_set=args.nombre_set, filtro_qids=comp_qids
            )
            if args.preguntas_csv is not None
            else ed4.cargar_preguntas_evaluacion(filtro_qids=comp_qids)
        )
        gen_base = MultiLoraGenerator(
            model,
            tokenizer,
            adaptadores_activos={r: None for r in ROLES_ORDEN},
            greedy=args.greedy,
            verbose=args.verbose_pasos,
        )
        ejecutar_comparativa_pareada(
            preg_comp,
            corpus,
            gen_base,
            gen_multi,
            "base",
            "finetuned_3lora",
            args.output_dir / "comparativa_base_vs_3lora.json",
        )

    if args.comparar_vs_solo_redactor:
        comp_qids = normalizar_filtro_qids(
            args.comparar_vs_solo_redactor,
            nombre_set=args.nombre_set if args.preguntas_csv is not None else None,
        )
        preg_comp = (
            ed4.cargar_preguntas_desde_csv(
                args.preguntas_csv, nombre_set=args.nombre_set, filtro_qids=comp_qids
            )
            if args.preguntas_csv is not None
            else ed4.cargar_preguntas_evaluacion(filtro_qids=comp_qids)
        )
        gen_solo_red = MultiLoraGenerator(
            model,
            tokenizer,
            adaptadores_activos={"redactor": "redactor"},
            greedy=args.greedy,
            verbose=args.verbose_pasos,
        )
        ejecutar_comparativa_pareada(
            preg_comp,
            corpus,
            gen_solo_red,
            gen_multi,
            "solo_redactor_d4",
            args.output_prefix or "3lora",
            args.output_dir / f"comparativa_{args.output_prefix or '3lora'}.json",
        )

    if not args.solo_comparativa:
        gpu_nombre = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
        meta = {
            "modelo_base": args.modelo_base,
            "revision_modelo_base": base_commit,
            "roles_con_lora": list(roles_activos),
            "roles_en_base": [r for r in ROLES_ORDEN if r not in roles_activos],
            "fuentes_por_rol": {
                r: {
                    "fuente": fuentes_por_rol[r][0],
                    "revision": fuentes_por_rol[r][1],
                    "sha256_adapter_model": _resolver_sha_fuente(
                        fuentes_por_rol[r][0], fuentes_por_rol[r][1], r
                    ),
                }
                for r in roles_a_cargar
            },
            "hardware": {"gpu": gpu_nombre, "compute_dtype": compute_dtype_str},
            "greedy": args.greedy,
            "aislamiento_multi_lora": aislamiento,
            "prompts_sha256": prompts_sha,
            "versiones": ed4._resolver_versiones_eval(),
        }
        ed4.ejecutar_evaluacion_lote(
            preguntas,
            corpus,
            gen_multi,
            output_dir=args.output_dir,
            condicion=f"multi_lora:{'+'.join(roles_activos) or 'base'}",
            metadata_extra=meta,
            output_prefix=args.output_prefix,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
