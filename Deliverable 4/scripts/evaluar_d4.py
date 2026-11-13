"""Evaluación del sistema multi-agente D4 con adaptador QLoRA solo en el Redactor.

Integra el adaptador entrenado (`Pablox0333/qwen3-4b-redactor-udec-d4`) únicamente
para el agente `Redactor`, manteniendo los pesos base sin modificar de
`Qwen/Qwen3-4B` para `Enrutador`, `Recuperador` y `Verificador` mediante
`model.disable_adapter()`.

Reutiliza exactamente el orquestador, herramientas (`Corpus` + recuperador denso
E5), prompts v6 (`Deliverable 4/prompts/`) y parámetros de decodificación de
Deliverable 3 para garantizar una comparación controlada sobre las 75 preguntas
(`congelado_50` + `dificil_25`).
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import importlib.metadata
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
DELIVERABLE4_DIR = REPO_ROOT / "Deliverable 4"
DELIVERABLE3_DIR = REPO_ROOT / "Deliverable 3" / "Deliverable3"
D3_AGENTES_DIR = DELIVERABLE3_DIR / "agentes"
D3_PROMPTS_DIR = DELIVERABLE3_DIR / "prompts"
D4_PROMPTS_DIR = DELIVERABLE4_DIR / "prompts"
D4_SCRIPTS_DIR = DELIVERABLE4_DIR / "scripts"
DEFAULT_EVAL_OUTPUT_DIR = DELIVERABLE4_DIR / "evaluacion"

MODELO_BASE_DEFAULT = "Qwen/Qwen3-4B"
HF_ADAPTER_DEFAULT = "Pablox0333/qwen3-4b-redactor-udec-d4"
E5_MODELO_DEFAULT = "intfloat/multilingual-e5-small"

PROMPT_FILES: tuple[str, ...] = (
    "01_enrutador.txt",
    "02_recuperador.txt",
    "03_redactor.txt",
    "04_verificador.txt",
)

MAX_TOKENS_POR_AGENTE: dict[str, int] = {
    "enrutador": 256,
    "recuperador": 160,
    "redactor": 1200,
    "verificador": 700,
}
SEMILLA_BASE = 2026
COMPARATIVA_IDS_DEFAULT: tuple[str, ...] = (
    "congelado_50:13",
    "congelado_50:24",
    "congelado_50:36",
    "dificil_25:H03",
    "dificil_25:H07",
    "dificil_25:H14",
)

CSV_FIELDNAMES: tuple[str, ...] = (
    "set",
    "condicion",
    "id",
    "categoria",
    "pregunta",
    "gold_dato",
    "gold_fuente",
    "respuesta_sistema",
    "tipo_enrutador",
    "aprobado_verificador",
    "motivo_verificador",
    "ciclos",
    "llamadas_modelo",
    "llamadas_redactor",
    "llamadas_base",
    "eventos_traza",
    "fallbacks",
    "fuentes_traidas",
    "segundos",
    "error",
    "correcto",
)

for _p in (D4_SCRIPTS_DIR, D3_AGENTES_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from entrenar_redactor import (  # noqa: E402
    es_bf16_nativo,
    formatear_prompt_usuario,
    sha256_archivo,
)


def escribir_texto_atomico(path: Path, contenido: str) -> None:
    """Escribe un archivo de texto de forma atómica usando temporal + reemplazo."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        f.write(contenido)
    tmp.replace(path)


def escribir_json_atomico(path: Path, datos: Any) -> None:
    """Serializa JSON en UTF-8 con escritura atómica."""
    escribir_texto_atomico(
        path,
        json.dumps(datos, ensure_ascii=False, indent=2) + "\n",
    )


def escribir_csv_atomico(path: Path, filas: list[dict[str, Any]], fieldnames: tuple[str, ...]) -> None:
    """Guarda filas en CSV UTF-8 de forma atómica."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(fieldnames),
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for fila in filas:
            writer.writerow({k: fila.get(k, "") for k in fieldnames})
    tmp.replace(path)


def verificar_prompts_d4(
    prompts_d4: Path = D4_PROMPTS_DIR,
    prompts_d3: Path = D3_PROMPTS_DIR,
) -> dict[str, str]:
    """Comprueba que los prompts de D4 existan, coincidan bit a bit con D3 v6 y retorna sus SHA-256."""
    hashes: dict[str, str] = {}
    for nombre in PROMPT_FILES:
        p4 = prompts_d4 / nombre
        p3 = prompts_d3 / nombre
        if not p4.is_file():
            raise FileNotFoundError(f"Falta prompt D4 requerido: {p4}")
        if p3.is_file() and p4.read_bytes() != p3.read_bytes():
            raise ValueError(
                f"El prompt D4 {p4} difiere del de D3 v6 {p3}; "
                "D4 debe mantener exactamente los mismos prompts base."
            )
        hashes[nombre] = sha256_archivo(p4)
    return hashes


def semilla_para_llamada(agente: str, prompt: str, semilla_base: int = SEMILLA_BASE) -> int:
    """Reproduce exactamente el esquema determinista por agente+prompt de D3."""
    digest = hashlib.sha256((agente + prompt).encode("utf-8")).hexdigest()[:8]
    return semilla_base + int(digest, 16) % 1_000_000


def extraer_fuentes_de_traza(traza: list[dict[str, Any]]) -> str:
    """Lista ordenada de IDs normativos recuperados/traídos en la traza."""
    out: set[str] = set()
    for paso in traza:
        obs = paso.get("observacion") or {}
        if paso.get("agente") == "recuperador":
            if obs.get("traido"):
                out.add(str(obs["traido"]))
            for hid in obs.get("hits", []):
                out.add(str(hid))
    return "; ".join(sorted(out))


def cargar_preguntas_desde_csv(
    csv_path: Path,
    nombre_set: str = "nuevas_20",
    filtro_qids: set[str] | None = None,
) -> list[dict[str, str]]:
    """Carga preguntas externas con esquema gold (`id,categoria,pregunta,gold_dato,gold_fuente`)."""
    if not csv_path.is_file():
        raise FileNotFoundError(f"No existe el archivo de preguntas CSV: {csv_path}")
    preguntas: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            pid = str(row["id"]).strip()
            qid = f"{nombre_set}:{pid}"
            preguntas.append(
                {
                    "set": nombre_set,
                    "id": pid,
                    "qid": qid,
                    "categoria": str(row.get("categoria", "")).strip(),
                    "pregunta": str(row["pregunta"]).strip(),
                    "gold_dato": str(row.get("gold_dato", "")).strip(),
                    "gold_fuente": str(row.get("gold_fuente", "")).strip(),
                }
            )
    if filtro_qids is not None:
        existentes = {p["qid"] for p in preguntas}
        faltantes = sorted(filtro_qids - existentes)
        if faltantes:
            raise ValueError(f"QIDs solicitados inexistentes en {csv_path}: {faltantes}")
        preguntas = [p for p in preguntas if p["qid"] in filtro_qids]
    return preguntas


def cargar_preguntas_evaluacion(
    agentes_dir: Path = D3_AGENTES_DIR,
    solo_dificiles: bool = False,
    filtro_qids: set[str] | None = None,
) -> list[dict[str, str]]:
    """Carga los test sets oficiales de D3 (`congelado_50` y `dificil_25`) preservando IDs str."""
    conjuntos: list[tuple[str, Path]] = []
    if not solo_dificiles:
        conjuntos.append(("congelado_50", agentes_dir / "test_set_50.csv"))
    conjuntos.append(("dificil_25", agentes_dir / "test_set_dificil_25.csv"))

    preguntas: list[dict[str, str]] = []
    for nombre_set, csv_path in conjuntos:
        if not csv_path.is_file():
            raise FileNotFoundError(f"No se encontró test set: {csv_path}")
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = f"{nombre_set}:{row['id']}"
                if filtro_qids is not None and qid not in filtro_qids:
                    continue
                preguntas.append(
                    {
                        "qid": qid,
                        "set": nombre_set,
                        "id": str(row["id"]),
                        "categoria": str(row.get("categoria", "")),
                        "pregunta": str(row["pregunta"]),
                        "gold_dato": str(row.get("gold_dato", "")),
                        "gold_fuente": str(row.get("gold_fuente", "")),
                    }
                )
    if filtro_qids is not None:
        encontrados = {p["qid"] for p in preguntas}
        faltantes = sorted(filtro_qids - encontrados)
        if faltantes:
            raise ValueError(f"QIDs no encontrados en los test sets: {faltantes}")
    return preguntas


def construir_corpus_d3(
    agentes_dir: Path = D3_AGENTES_DIR,
    use_e5: bool = True,
    e5_model_name: str = E5_MODELO_DEFAULT,
    device: str | None = None,
) -> Any:
    """Carga `Corpus` de D3 y opcionalmente inyecta el recuperador denso E5."""
    from tools import Corpus

    corpus = Corpus(agentes_dir)
    if not use_e5:
        return corpus

    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer

    dev = device or ("cuda" if torch.cuda.is_available() else "cpu")
    e5 = SentenceTransformer(e5_model_name, device=dev)
    frag = corpus.frag
    matriz_p = e5.encode(
        [f["texto_embedding"] for f in frag],
        normalize_embeddings=True,
        batch_size=64,
        show_progress_bar=False,
    )

    def buscar_e5(consulta: str, k: int = 5) -> list[dict[str, Any]]:
        q_vec = e5.encode(["query: " + str(consulta)], normalize_embeddings=True)[0]
        sims = matriz_p @ q_vec
        orden = np.argsort(-sims)
        vistos: set[str] = set()
        salida: list[dict[str, Any]] = []
        for idx in orden:
            f = frag[int(idx)]
            uid = f.get("unidad_id") or f.get("parent_id")
            if not uid or uid in vistos:
                continue
            vistos.add(uid)
            u = corpus.por_id.get(uid, {})
            salida.append({"id": uid, "texto": u.get("texto", f["texto"])})
            if len(salida) >= k:
                break
        return salida

    corpus.buscar = buscar_e5
    return corpus


class AdaptadorRedactorGenerator:
    """Generador multi-agente: activa el adaptador LoRA solo para `redactor`.

    Cuando `agente != 'redactor'` (o cuando `solo_base=True`), ejecuta dentro de
    `model.disable_adapter()` para usar exactamente los pesos base de `Qwen/Qwen3-4B`.
    """

    def __init__(
        self,
        model: Any,
        tokenizer: Any,
        greedy: bool = False,
        semilla_base: int = SEMILLA_BASE,
        max_tokens_por_agente: dict[str, int] | None = None,
        solo_base: bool = False,
    ) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.greedy = greedy
        self.semilla_base = semilla_base
        self.max_tokens = dict(max_tokens_por_agente or MAX_TOKENS_POR_AGENTE)
        self.solo_base = solo_base
        self.telemetria: list[dict[str, Any]] = []

    def __call__(self, agente: str, prompt: str, max_new_tokens: int | None = None) -> str:
        import torch

        text = formatear_prompt_usuario(self.tokenizer, prompt)
        tokens_budget = max_new_tokens or self.max_tokens.get(agente, 512)
        semilla = semilla_para_llamada(agente, prompt, self.semilla_base)
        usa_adaptador = (agente == "redactor") and (not self.solo_base)

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
                out = self.model.generate(**inputs, **gen_kwargs)
            else:
                with self.model.disable_adapter():
                    out = self.model.generate(**inputs, **gen_kwargs)
        dt = time.time() - t0

        input_len = int(inputs["input_ids"].shape[1])
        gen_ids = out[0][input_len:]
        salida = self.tokenizer.decode(gen_ids, skip_special_tokens=True).strip()

        self.telemetria.append(
            {
                "agente": agente,
                "usa_adaptador": usa_adaptador,
                "input_tokens": input_len,
                "output_tokens": int(len(gen_ids)),
                "segundos": round(dt, 3),
                "semilla": semilla,
            }
        )
        return salida


def verificar_aislamiento_adaptador(model: Any, tokenizer: Any) -> dict[str, Any]:
    """Comprueba empíricamente que `disable_adapter()` produce logits distintos al adaptador."""
    import torch

    texto = formatear_prompt_usuario(tokenizer, "Responde brevemente: prueba de aislamiento.")
    inputs = tokenizer(texto, return_tensors="pt").to(model.device)
    with torch.no_grad():
        logits_ft = model(**inputs).logits[:, -1, :].float()
        with model.disable_adapter():
            logits_base = model(**inputs).logits[:, -1, :].float()

    max_diff = float((logits_ft - logits_base).abs().max().item())
    if max_diff <= 0.0:
        raise RuntimeError(
            "El adaptador LoRA no produjo diferencia respecto al modelo base "
            f"(max_abs_logit_diff={max_diff}). Revisa la carga de PeftModel."
        )
    return {
        "max_abs_logit_diff": round(max_diff, 6),
        "active_adapters": list(getattr(model, "active_adapters", [])),
    }


def _cargar_csv_previo(csv_path: Path) -> list[dict[str, Any]]:
    if not csv_path.is_file():
        return []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _cargar_json_previo(json_path: Path, default: Any) -> Any:
    if not json_path.is_file():
        return default
    return json.loads(json_path.read_text(encoding="utf-8"))


def _resolver_versiones_eval() -> dict[str, str]:
    paquetes = (
        "torch",
        "transformers",
        "peft",
        "bitsandbytes",
        "accelerate",
        "huggingface_hub",
        "sentence-transformers",
    )
    out: dict[str, str] = {}
    for p in paquetes:
        try:
            out[p] = importlib.metadata.version(p)
        except importlib.metadata.PackageNotFoundError:
            out[p] = "no_instalado"
    return out


def crear_orquestador_d4(
    corpus: Any,
    generador: Callable[[str, str], str],
    prompts_dir: Path = D4_PROMPTS_DIR,
    agentes_dir: Path = D3_AGENTES_DIR,
) -> Any:
    """Instancia `Orquestador` de D3 apuntando explícitamente a `Deliverable 4/prompts`."""
    if str(agentes_dir) not in sys.path:
        sys.path.insert(0, str(agentes_dir))
    import orquestador

    orquestador.PROMPTS = Path(prompts_dir)
    return orquestador.Orquestador(corpus, generador, max_react=3, max_ciclos=2, ablacion=None)


def ejecutar_evaluacion_lote(
    preguntas: list[dict[str, str]],
    corpus: Any,
    generador: AdaptadorRedactorGenerator,
    output_dir: Path,
    condicion: str = "finetuned_redactor",
    prompts_dir: Path = D4_PROMPTS_DIR,
    agentes_dir: Path = D3_AGENTES_DIR,
    metadata_extra: dict[str, Any] | None = None,
    progreso_callback: Callable[[str, dict[str, Any]], None] | None = None,
    limpiar_cache_cuda_cada: int = 10,
    output_prefix: str = "",
) -> dict[str, Any]:
    """Ejecuta el lote con guardado incremental tras cada pregunta y soporte de reanudación."""
    output_dir.mkdir(parents=True, exist_ok=True)
    prefijo = output_prefix.strip().rstrip("_")
    if prefijo:
        csv_path = output_dir / f"resultados_{prefijo}.csv"
        trazas_path = output_dir / f"trazas_{prefijo}.json"
        telemetria_path = output_dir / f"telemetria_{prefijo}.json"
        config_path = output_dir / f"configuracion_{prefijo}.json"
    else:
        csv_path = output_dir / "resultados_agentes_D4.csv"
        trazas_path = output_dir / "trazas_D4.json"
        telemetria_path = output_dir / "telemetria_llamadas.json"
        config_path = output_dir / "configuracion_evaluacion.json"

    filas = _cargar_csv_previo(csv_path)
    trazas: dict[str, Any] = _cargar_json_previo(trazas_path, {})
    telemetria_por_qid: dict[str, Any] = _cargar_json_previo(telemetria_path, {})
    hechas = {f"{f['set']}:{f['id']}" for f in filas}

    orq = crear_orquestador_d4(corpus, generador, prompts_dir=prompts_dir, agentes_dir=agentes_dir)

    if metadata_extra is not None and not config_path.is_file():
        escribir_json_atomico(config_path, metadata_extra)

    t_inicio = time.time()
    nuevas = 0
    for item in preguntas:
        qid = item["qid"]
        if qid in hechas:
            continue

        idx_tel_inicio = len(generador.telemetria)
        t0 = time.time()
        try:
            res = orq.responder(item["pregunta"])
            error = ""
        except Exception as e:
            res = {
                "respuesta": "",
                "veredicto": {},
                "ciclos": 0,
                "tipo": "",
                "traza": list(orq.traza),
            }
            error = repr(e)
        dt = round(time.time() - t0, 2)

        traza = res["traza"]
        llamadas_q = generador.telemetria[idx_tel_inicio:]
        llamadas_redactor = sum(1 for c in llamadas_q if c["usa_adaptador"])
        llamadas_base = sum(1 for c in llamadas_q if not c["usa_adaptador"])

        fila = {
            "set": item["set"],
            "condicion": condicion,
            "id": item["id"],
            "categoria": item["categoria"],
            "pregunta": item["pregunta"],
            "gold_dato": item["gold_dato"],
            "gold_fuente": item["gold_fuente"],
            "respuesta_sistema": res["respuesta"],
            "tipo_enrutador": res["tipo"],
            "aprobado_verificador": res["veredicto"].get("aprobado", ""),
            "motivo_verificador": res["veredicto"].get("motivo", ""),
            "ciclos": res["ciclos"],
            "llamadas_modelo": sum(1 for p in traza if not p.get("decidido_por")),
            "llamadas_redactor": llamadas_redactor,
            "llamadas_base": llamadas_base,
            "eventos_traza": len(traza),
            "fallbacks": sum(1 for p in traza if p.get("fallback")),
            "fuentes_traidas": extraer_fuentes_de_traza(traza),
            "segundos": dt,
            "error": error,
            "correcto": "",
        }
        filas.append(fila)
        trazas[qid] = traza
        telemetria_por_qid[qid] = llamadas_q

        escribir_csv_atomico(csv_path, filas, CSV_FIELDNAMES)
        escribir_json_atomico(trazas_path, trazas)
        escribir_json_atomico(telemetria_path, telemetria_por_qid)

        hechas.add(qid)
        nuevas += 1
        if progreso_callback is not None:
            progreso_callback(qid, fila)

        if limpiar_cache_cuda_cada > 0 and nuevas % limpiar_cache_cuda_cada == 0:
            try:
                import torch

                if torch.cuda.is_available():
                    gc.collect()
                    torch.cuda.empty_cache()
            except Exception:
                pass

    return {
        "total_filas": len(filas),
        "nuevas_procesadas": nuevas,
        "duracion_sesion_seg": round(time.time() - t_inicio, 2),
        "csv_path": str(csv_path),
        "trazas_path": str(trazas_path),
        "telemetria_path": str(telemetria_path),
        "config_path": str(config_path),
    }


def ejecutar_comparativa_base_vs_finetuned(
    preguntas: list[dict[str, str]],
    corpus: Any,
    generador_base: AdaptadorRedactorGenerator,
    generador_ft: AdaptadorRedactorGenerator,
    output_path: Path,
    prompts_dir: Path = D4_PROMPTS_DIR,
    agentes_dir: Path = D3_AGENTES_DIR,
) -> list[dict[str, Any]]:
    """Corre extremo a extremo el pipeline base vs Redactor QLoRA sobre los mismos casos."""
    orq_base = crear_orquestador_d4(corpus, generador_base, prompts_dir=prompts_dir, agentes_dir=agentes_dir)
    orq_ft = crear_orquestador_d4(corpus, generador_ft, prompts_dir=prompts_dir, agentes_dir=agentes_dir)

    resultados: list[dict[str, Any]] = []
    for item in preguntas:
        t0 = time.time()
        res_base = orq_base.responder(item["pregunta"])
        dt_base = round(time.time() - t0, 2)

        t1 = time.time()
        res_ft = orq_ft.responder(item["pregunta"])
        dt_ft = round(time.time() - t1, 2)

        resultados.append(
            {
                "qid": item["qid"],
                "set": item["set"],
                "id": item["id"],
                "categoria": item["categoria"],
                "pregunta": item["pregunta"],
                "gold_dato": item["gold_dato"],
                "gold_fuente": item["gold_fuente"],
                "base": {
                    "respuesta": res_base["respuesta"],
                    "veredicto": res_base["veredicto"],
                    "ciclos": res_base["ciclos"],
                    "tipo_enrutador": res_base["tipo"],
                    "segundos": dt_base,
                    "fuentes_traidas": extraer_fuentes_de_traza(res_base["traza"]),
                    "traza": res_base["traza"],
                },
                "finetuned_redactor": {
                    "respuesta": res_ft["respuesta"],
                    "veredicto": res_ft["veredicto"],
                    "ciclos": res_ft["ciclos"],
                    "tipo_enrutador": res_ft["tipo"],
                    "segundos": dt_ft,
                    "fuentes_traidas": extraer_fuentes_de_traza(res_ft["traza"]),
                    "traza": res_ft["traza"],
                },
            }
        )
        escribir_json_atomico(output_path, resultados)
    return resultados


def _cargar_modelo_y_adaptador(modelo_base: str, hf_repo: str) -> tuple[Any, Any, str, str]:
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    cap = torch.cuda.get_device_capability(0) if torch.cuda.is_available() else (0, 0)
    bf16_nativo = torch.cuda.is_available() and es_bf16_nativo(cap, torch.cuda.is_bf16_supported())
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
    model = PeftModel.from_pretrained(base, hf_repo)
    model.eval()
    return model, tokenizer, str(compute_dtype), getattr(base.config, "_commit_hash", None) or ""


def construir_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluación multi-agente D4 (Qwen3-4B base + adaptador LoRA solo en Redactor).",
    )
    parser.add_argument("--modelo-base", default=MODELO_BASE_DEFAULT)
    parser.add_argument("--hf-repo", default=HF_ADAPTER_DEFAULT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_EVAL_OUTPUT_DIR)
    parser.add_argument(
        "--output-prefix",
        type=str,
        default="",
        help="Prefijo opcional para archivos de salida (ej. `control_base_D4` o `nuevas20_ft_D4`).",
    )
    parser.add_argument(
        "--solo-base",
        action="store_true",
        help="Ejecuta los 4 agentes con LoRA desactivado (`disable_adapter()`) como control en el mismo entorno.",
    )
    parser.add_argument(
        "--preguntas-csv",
        type=Path,
        default=None,
        help="CSV alternativo de preguntas con esquema gold (ej. `preguntas_nuevas_20.csv`).",
    )
    parser.add_argument(
        "--nombre-set",
        type=str,
        default="nuevas_20",
        help="Etiqueta de `set` cuando se usa `--preguntas-csv`.",
    )
    parser.add_argument("--solo-dificiles", action="store_true")
    parser.add_argument(
        "--qids",
        default=None,
        help="Subconjunto opcional de QIDs separados por coma (ej. congelado_50:13,dificil_25:H03).",
    )
    parser.add_argument(
        "--greedy",
        action="store_true",
        help="Decodificación greedy; por defecto usa temperature=0.7/top_p=0.8/top_k=20 igual a D3.",
    )
    parser.add_argument("--sin-e5", action="store_true")
    parser.add_argument(
        "--comparar-ids",
        default=None,
        help="QIDs separados por coma para generar comparativa lado a lado Base vs Fine-tuned.",
    )
    parser.add_argument(
        "--solo-comparativa",
        action="store_true",
        help="Omite el lote principal y ejecuta únicamente --comparar-ids.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = construir_arg_parser().parse_args(argv)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    import torch

    prompts_sha = verificar_prompts_d4()
    filtro_qids = (
        {q.strip() for q in args.qids.split(",") if q.strip()} if args.qids else None
    )

    corpus = construir_corpus_d3(use_e5=not args.sin_e5)
    model, tokenizer, compute_dtype_str, base_commit = _cargar_modelo_y_adaptador(
        args.modelo_base,
        args.hf_repo,
    )
    aislamiento = verificar_aislamiento_adaptador(model, tokenizer)
    print("Aislamiento LoRA verificado:", aislamiento)

    gpu_nombre = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    vram_gb = (
        round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2)
        if torch.cuda.is_available()
        else 0.0
    )

    metadata = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "modelo_base": args.modelo_base,
        "revision_modelo_base": base_commit,
        "hf_adaptador_redactor": args.hf_repo,
        "agentes_base": ["enrutador", "recuperador", "verificador"],
        "agentes_finetuned": ["redactor"],
        "decoding": (
            {"do_sample": False}
            if args.greedy
            else {"do_sample": True, "temperature": 0.7, "top_p": 0.8, "top_k": 20, "min_p": 0.0}
        ),
        "semilla_base": SEMILLA_BASE,
        "max_tokens": MAX_TOKENS_POR_AGENTE,
        "enable_thinking": False,
        "recuperador_e5": None if args.sin_e5 else E5_MODELO_DEFAULT,
        "aislamiento_verificado": aislamiento,
        "hardware": {"gpu": gpu_nombre, "vram_gb": vram_gb, "compute_dtype": compute_dtype_str},
        "versiones": _resolver_versiones_eval(),
        "prompts_sha256": prompts_sha,
    }

    if not args.solo_comparativa:
        if args.preguntas_csv is not None:
            preguntas = cargar_preguntas_desde_csv(
                args.preguntas_csv,
                nombre_set=args.nombre_set,
                filtro_qids=filtro_qids,
            )
        else:
            preguntas = cargar_preguntas_evaluacion(
                solo_dificiles=args.solo_dificiles,
                filtro_qids=filtro_qids,
            )
        generador = AdaptadorRedactorGenerator(
            model, tokenizer, greedy=args.greedy, solo_base=args.solo_base
        )

        def _log_prog(qid: str, fila: dict[str, Any]) -> None:
            print(
                f"  [{qid}] tipo={fila['tipo_enrutador']:13s} ciclos={fila['ciclos']} "
                f"calls={fila['llamadas_modelo']} (red={fila['llamadas_redactor']}/"
                f"base={fila['llamadas_base']}) aprob={fila['aprobado_verificador']} "
                f"{fila['segundos']}s"
                + (f" ERROR={fila['error']}" if fila["error"] else ""),
                flush=True,
            )

        condicion_eval = (
            "control_base_lora_apagado" if args.solo_base else "finetuned_redactor"
        )
        prefijo_out = args.output_prefix.strip()
        if not prefijo_out:
            if args.preguntas_csv is not None:
                prefijo_out = f"{args.nombre_set}_{'base' if args.solo_base else 'ft'}_D4"
            elif args.solo_base:
                prefijo_out = "control_base_D4"
        resumen = ejecutar_evaluacion_lote(
            preguntas,
            corpus,
            generador,
            args.output_dir,
            condicion=condicion_eval,
            metadata_extra=metadata,
            progreso_callback=_log_prog,
            output_prefix=prefijo_out,
        )
        print("Lote completado:", json.dumps(resumen, ensure_ascii=False))

    if args.comparar_ids or args.solo_comparativa:
        raw_ids = args.comparar_ids or ",".join(COMPARATIVA_IDS_DEFAULT)
        ids_comp = {q.strip() for q in raw_ids.split(",") if q.strip()}
        if args.preguntas_csv is not None:
            preguntas_comp = cargar_preguntas_desde_csv(
                args.preguntas_csv,
                nombre_set=args.nombre_set,
                filtro_qids=ids_comp,
            )
        else:
            preguntas_comp = cargar_preguntas_evaluacion(filtro_qids=ids_comp)
        gen_base = AdaptadorRedactorGenerator(model, tokenizer, greedy=args.greedy, solo_base=True)
        gen_ft = AdaptadorRedactorGenerator(model, tokenizer, greedy=args.greedy, solo_base=False)
        comp_name = (
            f"comparativa_{args.output_prefix.strip().rstrip('_')}.json"
            if args.output_prefix.strip()
            else "comparativa_base_vs_finetuned.json"
        )
        comp_path = args.output_dir / comp_name
        ejecutar_comparativa_base_vs_finetuned(
            preguntas_comp,
            corpus,
            gen_base,
            gen_ft,
            comp_path,
        )
        print("Comparativa guardada en:", comp_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
