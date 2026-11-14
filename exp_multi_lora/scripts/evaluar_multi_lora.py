"""Evaluación Multi-LoRA: conmuta hasta 4 adaptadores sobre un único `Qwen/Qwen3-4B`.

Permite evaluar con el mismo entorno, prompts v6 y semillas que D4:
- Control Base (`--agentes ninguno`)
- Solo agente crítico (`--agentes redactor`, equivalente a D4 v2)
- Ablaciones parciales (`--agentes redactor,verificador`, etc.)
- Multi-LoRA completo (`--agentes enrutador,recuperador,redactor,verificador`)
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
D4_SCRIPTS_DIR = REPO_ROOT / "Deliverable 4" / "scripts"
D3_AGENTES_DIR = REPO_ROOT / "Deliverable 3" / "Deliverable3" / "agentes"
EXP_DIR = REPO_ROOT / "exp_multi_lora"
EXP_TRAIN_DIR = EXP_DIR / "entrenamiento"
EXP_EVAL_DIR = EXP_DIR / "evaluacion"

for _p in (D4_SCRIPTS_DIR, D3_AGENTES_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import evaluar_d4 as ed4  # noqa: E402
from entrenar_redactor import MODELO_BASE_DEFAULT, es_bf16_nativo, formatear_prompt_usuario  # noqa: E402

ROLES_ORDEN: tuple[str, ...] = ("enrutador", "recuperador", "redactor", "verificador")


def resolver_fuentes_adaptadores_default() -> dict[str, tuple[str, str | None]]:
    """Mapa default de adaptadores: D4 v2 para `redactor` y locales para los otros 3."""
    return {
        "enrutador": (str(EXP_TRAIN_DIR / "enrutador" / "adapter"), None),
        "recuperador": (str(EXP_TRAIN_DIR / "recuperador" / "adapter"), None),
        "redactor": (ed4.HF_ADAPTER_DEFAULT, ed4.HF_ADAPTER_REVISION_DEFAULT),
        "verificador": (str(EXP_TRAIN_DIR / "verificador" / "adapter"), None),
    }


def parsear_lista_agentes(valor: str) -> tuple[str, ...]:
    """Normaliza `--agentes enrutador,recuperador,redactor,verificador` o `ninguno`/`todos`."""
    raw = [x.strip().lower() for x in valor.split(",") if x.strip()]
    if not raw or raw == ["ninguno"] or raw == ["none"]:
        return ()
    if raw == ["todos"] or raw == ["all"]:
        return ROLES_ORDEN
    invalidos = [x for x in raw if x not in ROLES_ORDEN]
    if invalidos:
        raise ValueError(
            f"Agentes desconocidos: {invalidos}. Válidos: {list(ROLES_ORDEN)}, 'todos', 'ninguno'."
        )
    return tuple(r for r in ROLES_ORDEN if r in raw)


class MultiLoraGenerator:
    """Generador que activa el adaptador específico de cada rol con `model.set_adapter()`.

    Si un agente no figura en `adaptadores_activos` (o su valor es `None`), corre dentro de
    `model.disable_adapter()` usando exactamente los pesos base de `Qwen/Qwen3-4B`.
    """

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
            self.adaptadores_activos: dict[str, str | None] = {r: r for r in ROLES_ORDEN}
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
                tag = f"LoRA:{nombre_adaptador}" if usa_adaptador else "BASE(OFF)"
                resumen = " ".join(salida.split())
                if len(resumen) > 320:
                    resumen = resumen[:317] + "..."
                print(
                    f"  [Paso {evento['paso']:02d} | {agente.upper():11s} | {tag:16s} | {dt:5.2f}s] {resumen}",
                    flush=True,
                )
            if self.step_callback is not None:
                self.step_callback(evento)

        return salida


def cargar_modelo_y_multi_lora(
    modelo_base: str,
    fuentes_por_rol: dict[str, tuple[str, str | None]],
    roles_a_cargar: tuple[str, ...],
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
                f"Entrena primero con `entrenar_agente.py --agente {rol}` o pasa "
                f"`--adaptador-{rol} <usuario/repo-hf>`."
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
    """Compara lado a lado dos configuraciones de agentes (ej. Solo Redactor vs Multi-LoRA)."""
    orq_a = ed4.crear_orquestador_d4(corpus, generador_a)
    orq_b = ed4.crear_orquestador_d4(corpus, generador_b)

    resultados: list[dict[str, Any]] = []
    for item in preguntas:
        if getattr(generador_a, "verbose", False):
            print(f"\n>>> [{etiqueta_a}] {item['qid']}: {item['pregunta']}", flush=True)
        t0 = time.time()
        res_a = orq_a.responder(item["pregunta"])
        dt_a = round(time.time() - t0, 2)

        if getattr(generador_b, "verbose", False):
            print(f"\n>>> [{etiqueta_b}] {item['qid']}: {item['pregunta']}", flush=True)
        t1 = time.time()
        res_b = orq_b.responder(item["pregunta"])
        dt_b = round(time.time() - t1, 2)

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
                    "veredicto": res_a["veredicto"],
                    "ciclos": res_a["ciclos"],
                    "tipo_enrutador": res_a["tipo"],
                    "segundos": dt_a,
                    "fuentes_traidas": ed4.extraer_fuentes_de_traza(res_a["traza"]),
                    "traza": res_a["traza"],
                },
                etiqueta_b: {
                    "respuesta": res_b["respuesta"],
                    "veredicto": res_b["veredicto"],
                    "ciclos": res_b["ciclos"],
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
        description="Evaluación Multi-LoRA sobre Qwen3-4B con conmutación dinámica por rol."
    )
    p.add_argument("--modelo-base", default=MODELO_BASE_DEFAULT)
    p.add_argument(
        "--agentes",
        default="todos",
        help="Roles con LoRA activo separados por coma, 'todos' o 'ninguno'.",
    )
    for rol in ROLES_ORDEN:
        repo_def, rev_def = defaults[rol]
        p.add_argument(f"--adaptador-{rol}", default=repo_def)
        p.add_argument(f"--rev-{rol}", default=rev_def or "")
    p.add_argument("--output-dir", type=Path, default=EXP_EVAL_DIR)
    p.add_argument("--output-prefix", default="multi_lora_full")
    p.add_argument("--preguntas-csv", type=Path, default=None)
    p.add_argument("--nombre-set", default="nuevas_20")
    p.add_argument("--solo-dificiles", action="store_true")
    p.add_argument("--qids", default=None)
    p.add_argument("--greedy", action="store_true")
    p.add_argument("--sin-e5", action="store_true")
    p.add_argument(
        "--comparar-vs-solo-redactor",
        default=None,
        help="QIDs separados por coma para comparar Solo Redactor FT v2 vs --agentes.",
    )
    p.add_argument("--solo-comparativa", action="store_true")
    p.add_argument("--verbose-pasos", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_arg_parser().parse_args(argv)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    import torch

    prompts_sha = ed4.verificar_prompts_d4()
    roles_activos = parsear_lista_agentes(args.agentes)

    fuentes_por_rol = {
        rol: (
            getattr(args, f"adaptador_{rol}"),
            getattr(args, f"rev_{rol}") or None,
        )
        for rol in ROLES_ORDEN
    }
    roles_a_cargar = tuple(dict.fromkeys((*roles_activos, "redactor"))) if args.comparar_vs_solo_redactor else roles_activos

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

    filtro_qids = (
        {q.strip() for q in args.qids.split(",") if q.strip()} if args.qids else None
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

    if args.comparar_vs_solo_redactor:
        comp_qids = {
            q.strip() for q in args.comparar_vs_solo_redactor.split(",") if q.strip()
        }
        if args.preguntas_csv is not None:
            preg_comp = ed4.cargar_preguntas_desde_csv(
                args.preguntas_csv,
                nombre_set=args.nombre_set,
                filtro_qids=comp_qids,
            )
        else:
            preg_comp = ed4.cargar_preguntas_evaluacion(filtro_qids=comp_qids)
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
            args.output_prefix or "multi_lora",
            args.output_dir / f"comparativa_{args.output_prefix or 'multi_lora'}.json",
        )

    if not args.solo_comparativa:
        gpu_nombre = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
        meta = {
            "modelo_base": args.modelo_base,
            "revision_modelo_base": base_commit,
            "roles_con_lora": list(roles_activos),
            "fuentes_por_rol": {
                r: {"fuente": fuentes_por_rol[r][0], "revision": fuentes_por_rol[r][1]}
                for r in roles_a_cargar
            },
            "hardware": {"gpu": gpu_nombre, "compute_dtype": compute_dtype_str},
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
