"""Entrenamiento DPO (Direct Preference Optimization) Split-Backward con QLoRA para Qwen3-4B.

Diseñado para ejecutarse de forma estable dentro de 15 GB de VRAM (Colab T4) sin duplicar
el modelo de referencia ni usar dependencias frágiles: precomputa `ref_logps` en una sola
pasada `no_grad` inicial y desacopla los backward de `chosen` y `rejected` conservando la
equivalencia exacta del gradiente DPO + regularización NLL sobre `chosen` (`lambda_nll`).
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gc
import json
import math
import os
from pathlib import Path
import random
import shutil
import time
from typing import Any

from ..herramientas import ESQUEMAS_HERRAMIENTAS
from . import MODELO_BASE_HF
from .construir_dataset import DEFAULT_FT_DATA_DIR
from .construir_dataset_dpo import validar_dataset_dpo
from .entrenar_agente_sft import (
    LORA_TARGET_MODULES,
    _fijar_semillas,
    _tokenizar_chat,
    cargar_jsonl,
    resumir_tokens_dataset,
)

DEFAULT_DPO_OUTPUT_DIR = Path(__file__).resolve().parent / "salidas_dpo_qwen3_4b"


def construir_par_dpo(
    registro: dict[str, Any],
    tokenizer: Any,
    tools: list[dict[str, Any]] = ESQUEMAS_HERRAMIENTAS,
    max_seq_length: int = 3584,
) -> dict[str, Any]:
    """Tokeniza `(prompt, chosen, rejected)` con plantilla Qwen3+Tools enmascarando el prompt (`-100`)."""
    prompt = registro.get("prompt") or []
    chosen = registro.get("chosen") or {}
    rejected = registro.get("rejected") or {}
    if not prompt or not chosen or not rejected:
        raise ValueError(f"{registro.get('id')}: par DPO incompleto (falta prompt/chosen/rejected)")

    p_ids = _tokenizar_chat(tokenizer, list(prompt), tools=tools, add_generation_prompt=True)
    c_ids = _tokenizar_chat(tokenizer, list(prompt) + [chosen], tools=tools, add_generation_prompt=False)
    r_ids = _tokenizar_chat(tokenizer, list(prompt) + [rejected], tools=tools, add_generation_prompt=False)

    if c_ids[: len(p_ids)] != p_ids or r_ids[: len(p_ids)] != p_ids:
        raise ValueError(f"{registro.get('id')}: desalineación de prefijo entre prompt y respuestas DPO")

    c_labels = [-100] * len(p_ids) + c_ids[len(p_ids) :]
    r_labels = [-100] * len(p_ids) + r_ids[len(p_ids) :]

    truncado = len(c_ids) > max_seq_length or len(r_ids) > max_seq_length
    c_ids, c_labels = c_ids[:max_seq_length], c_labels[:max_seq_length]
    r_ids, r_labels = r_ids[:max_seq_length], r_labels[:max_seq_length]

    c_sup = sum(1 for x in c_labels if x != -100)
    r_sup = sum(1 for x in r_labels if x != -100)
    if c_sup == 0 or r_sup == 0:
        raise ValueError(
            f"{registro.get('id')}: 0 tokens supervisados tras truncar a max_seq_length={max_seq_length} "
            f"(chosen={c_sup}, rejected={r_sup})"
        )

    return {
        "id": str(registro["id"]),
        "categoria": str(registro.get("categoria", "")),
        "chosen_input_ids": c_ids,
        "chosen_labels": c_labels,
        "rejected_input_ids": r_ids,
        "rejected_labels": r_labels,
        "prompt_tokens": len(p_ids),
        "chosen_sup_tokens": c_sup,
        "rejected_sup_tokens": r_sup,
        "total_tokens": max(len(c_ids), len(r_ids)),
        "supervised_tokens": c_sup,
        "truncado": truncado,
    }


def secuencia_logps_y_nll(logits: Any, labels: Any) -> tuple[Any, Any]:
    """Calcula `(sum_logps, nll_mean)` en float32 solo sobre tokens supervisados (`labels != -100`)."""
    import torch
    import torch.nn.functional as F

    shift_logits = logits[:, :-1, :].float()
    shift_labels = labels[:, 1:]
    mask = shift_labels.ne(-100)
    safe_labels = shift_labels.masked_fill(~mask, 0)

    log_probs = F.log_softmax(shift_logits, dim=-1)
    tok_logps = torch.gather(log_probs, dim=-1, index=safe_labels.unsqueeze(-1)).squeeze(-1)
    sum_logps = (tok_logps * mask.float()).sum(dim=-1)
    denom = mask.sum(dim=-1).clamp(min=1).float()
    nll_mean = -sum_logps / denom
    return sum_logps, nll_mean


def calcular_pesos_dpo_split(
    logp_w: Any,
    logp_l: Any,
    ref_w: Any,
    ref_l: Any,
    beta: float = 0.1,
) -> tuple[Any, dict[str, float]]:
    """Calcula el peso escalar exacto `w_dpo = beta * sigmoid(-beta * margin)` y métricas DPO.

    Se cumple que:
    `d(L_DPO)/d(theta) = -w_dpo * grad(logp_w) + w_dpo * grad(logp_l)` con `w_dpo` detached,
    permitiendo retropropagar `chosen` y `rejected` en grafos separados sin cambiar el gradiente.
    """
    import torch
    import torch.nn.functional as F

    rw = torch.as_tensor(logp_w - ref_w, dtype=torch.float32)
    rl = torch.as_tensor(logp_l - ref_l, dtype=torch.float32)
    margin = rw - rl
    beta_f = float(beta)
    z = beta_f * margin
    w_dpo = (beta_f * torch.sigmoid(-z)).detach()
    dpo_loss = (-F.logsigmoid(z)).detach()

    return w_dpo, {
        "dpo_loss": float(dpo_loss.item()),
        "reward_margin": float((beta_f * margin).item()),
        "reward_w": float((beta_f * rw).item()),
        "reward_l": float((beta_f * rl).item()),
        "pref_acc": 1.0 if float(margin.item()) > 0.0 else 0.0,
    }


def _capture_rng_state(device: Any) -> tuple[Any, Any]:
    import torch

    cpu_st = torch.get_rng_state()
    cuda_st = torch.cuda.get_rng_state(device) if device.type == "cuda" else None
    return cpu_st, cuda_st


def _restore_rng_state(estado: tuple[Any, Any], device: Any) -> None:
    import torch

    cpu_st, cuda_st = estado
    torch.set_rng_state(cpu_st)
    if device.type == "cuda" and cuda_st is not None:
        torch.cuda.set_rng_state(cuda_st, device)


def _forward_logp_par(
    model: Any,
    input_ids_list: list[int],
    labels_list: list[int],
    device: Any,
    compute_dtype: Any,
) -> tuple[Any, Any]:
    import torch

    ids = torch.tensor([input_ids_list], dtype=torch.long, device=device)
    labs = torch.tensor([labels_list], dtype=torch.long, device=device)
    mask = torch.ones_like(ids)
    ctx = (
        torch.amp.autocast("cuda", dtype=compute_dtype)
        if device.type == "cuda"
        else torch.autocast("cpu", enabled=False)
    )
    with ctx:
        out = model(input_ids=ids, attention_mask=mask, use_cache=False)
        sum_logps, nll_mean = secuencia_logps_y_nll(out.logits, labs)
    return sum_logps.squeeze(0), nll_mean.squeeze(0)


def _precomputar_ref_logps(
    model: Any,
    pares: list[dict[str, Any]],
    device: Any,
    compute_dtype: Any,
) -> list[dict[str, Any]]:
    import torch

    model.eval()
    con_ref: list[dict[str, Any]] = []
    with torch.no_grad():
        for par in pares:
            ref_w, _ = _forward_logp_par(model, par["chosen_input_ids"], par["chosen_labels"], device, compute_dtype)
            ref_l, _ = _forward_logp_par(model, par["rejected_input_ids"], par["rejected_labels"], device, compute_dtype)
            copia = dict(par)
            copia["ref_w"] = float(ref_w.item())
            copia["ref_l"] = float(ref_l.item())
            con_ref.append(copia)
    return con_ref


def _evaluar_dpo(
    model: Any,
    pares_val: list[dict[str, Any]],
    device: Any,
    compute_dtype: Any,
    beta: float,
    lambda_nll: float,
) -> dict[str, float]:
    import torch

    was_training = model.training
    model.eval()
    totales = {"dpo_loss": 0.0, "total_loss": 0.0, "reward_margin": 0.0, "reward_w": 0.0, "reward_l": 0.0, "pref_acc": 0.0}
    with torch.no_grad():
        for par in pares_val:
            lp_w, nll_w = _forward_logp_par(model, par["chosen_input_ids"], par["chosen_labels"], device, compute_dtype)
            lp_l, _ = _forward_logp_par(model, par["rejected_input_ids"], par["rejected_labels"], device, compute_dtype)
            _, m = calcular_pesos_dpo_split(lp_w, lp_l, par["ref_w"], par["ref_l"], beta=beta)
            totales["dpo_loss"] += m["dpo_loss"]
            totales["total_loss"] += m["dpo_loss"] + float(lambda_nll) * float(nll_w.item())
            totales["reward_margin"] += m["reward_margin"]
            totales["reward_w"] += m["reward_w"]
            totales["reward_l"] += m["reward_l"]
            totales["pref_acc"] += m["pref_acc"]
    if was_training:
        model.train()

    n = max(1, len(pares_val))
    return {
        "eval_dpo_loss": round(totales["dpo_loss"] / n, 6),
        "eval_total_loss": round(totales["total_loss"] / n, 6),
        "eval_reward_margin": round(totales["reward_margin"] / n, 6),
        "eval_reward_w": round(totales["reward_w"] / n, 6),
        "eval_reward_l": round(totales["reward_l"] / n, 6),
        "eval_pref_acc": round(totales["pref_acc"] / n, 4),
    }


def _smoke_test_dpo(model: Any, tokenizer: Any, val_raw: list[dict[str, Any]], max_ejemplos: int = 4) -> list[dict[str, Any]]:
    import torch

    elegidos: list[dict[str, Any]] = []
    vistas: set[str] = set()
    for r in val_raw:
        if r.get("categoria") not in vistas:
            elegidos.append(r)
            vistas.add(str(r.get("categoria")))
        if len(elegidos) >= max_ejemplos:
            break

    model.config.use_cache = True
    model.eval()
    device = next(model.parameters()).device
    muestras: list[dict[str, Any]] = []
    for r in elegidos:
        prompt_text = tokenizer.apply_chat_template(
            r["prompt"], tools=ESQUEMAS_HERRAMIENTAS, add_generation_prompt=True, tokenize=False
        )
        enc = tokenizer(prompt_text, return_tensors="pt", add_special_tokens=False).to(device)
        with torch.no_grad():
            gen = model.generate(
                **enc, max_new_tokens=220, do_sample=False, pad_token_id=tokenizer.pad_token_id
            )
        nuevo = gen[0][enc["input_ids"].shape[1] :]
        salida = tokenizer.decode(nuevo, skip_special_tokens=False).strip()
        muestras.append({"id": r["id"], "categoria": r.get("categoria", ""), "generado": salida[:420]})
    return muestras


def graficar_curvas_dpo(
    train_log: list[dict[str, Any]],
    eval_log: list[dict[str, Any]],
    salida_png: Path | None = None,
    mejor_step: int | None = None,
) -> dict[str, Any]:
    """Genera PNG con curvas de `dpo_loss`, `eval_pref_acc` y `eval_reward_margin`."""
    if salida_png is not None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 7.2), sharex=True)
        if train_log:
            ax1.plot([p["step"] for p in train_log], [p["dpo_loss"] for p in train_log], marker=".", alpha=0.8, label="train_dpo_loss")
        if eval_log:
            ax1.plot([p["step"] for p in eval_log], [p["eval_dpo_loss"] for p in eval_log], marker="s", linewidth=2, label="eval_dpo_loss")
            l1 = ax2.plot([p["step"] for p in eval_log], [p["eval_pref_acc"] for p in eval_log], marker="o", color="tab:blue", label="eval_pref_acc")
            ax2_r = ax2.twinx()
            l2 = ax2_r.plot([p["step"] for p in eval_log], [p["eval_reward_margin"] for p in eval_log], marker="^", color="tab:orange", label="eval_reward_margin")
            ax2_r.set_ylabel("Reward Margin", color="tab:orange")
            lines = l1 + l2
            ax2.legend(lines, [ln.get_label() for ln in lines], loc="upper left")
        if mejor_step is not None:
            ax1.axvline(mejor_step, linestyle="--", color="green", label=f"best step {mejor_step}")
            ax2.axvline(mejor_step, linestyle="--", color="green")

        ax1.set_title("DPO Split-Backward QLoRA sobre Qwen3-4B-Instruct-2507")
        ax1.set_ylabel("DPO Loss")
        ax1.grid(True, linestyle=":", alpha=0.5)
        ax1.legend()

        ax2.set_xlabel("Optimizer Step")
        ax2.set_ylabel("Preference Accuracy", color="tab:blue")
        ax2.set_ylim(-0.05, 1.08)
        ax2.grid(True, linestyle=":", alpha=0.5)

        fig.tight_layout()
        salida_png.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(salida_png, dpi=220, bbox_inches="tight")
        plt.close(fig)

    return {"train": train_log, "eval": eval_log}


def _crear_optimizador(model: Any, learning_rate: float) -> Any:
    params = [p for p in model.parameters() if p.requires_grad]
    try:
        import bitsandbytes as bnb

        return bnb.optim.PagedAdamW8bit(params, lr=learning_rate, weight_decay=0.01)
    except Exception:
        import torch

        return torch.optim.AdamW(params, lr=learning_rate, weight_decay=0.01)


def _paso_split_backward_par(
    model: Any,
    par: dict[str, Any],
    device: Any,
    compute_dtype: Any,
    scaler: Any,
    beta: float,
    lambda_nll: float,
    chunk_len: int,
) -> dict[str, float]:
    import torch

    # Capturar máscara dropout y evaluar logps actuales en no_grad para fijar w_dpo exacto
    rng_w = _capture_rng_state(device)
    with torch.no_grad():
        lp_w0, nll_w0 = _forward_logp_par(model, par["chosen_input_ids"], par["chosen_labels"], device, compute_dtype)

    rng_l = _capture_rng_state(device)
    with torch.no_grad():
        lp_l0, _ = _forward_logp_par(model, par["rejected_input_ids"], par["rejected_labels"], device, compute_dtype)

    w_dpo, metricas = calcular_pesos_dpo_split(lp_w0, lp_l0, par["ref_w"], par["ref_l"], beta=beta)
    inv_m = 1.0 / float(max(1, chunk_len))

    # Rama 1: backward solo sobre `chosen` (1 único grafo en VRAM)
    _restore_rng_state(rng_w, device)
    lp_w, nll_w = _forward_logp_par(model, par["chosen_input_ids"], par["chosen_labels"], device, compute_dtype)
    loss_w = (-w_dpo * lp_w + float(lambda_nll) * nll_w) * inv_m
    scaler.scale(loss_w).backward()

    # Rama 2: backward solo sobre `rejected`
    _restore_rng_state(rng_l, device)
    lp_l, _ = _forward_logp_par(model, par["rejected_input_ids"], par["rejected_labels"], device, compute_dtype)
    loss_l = (w_dpo * lp_l) * inv_m
    scaler.scale(loss_l).backward()

    metricas["total_loss"] = metricas["dpo_loss"] + float(lambda_nll) * float(nll_w0.item())
    return metricas


def entrenar_dpo_qlora(
    data_dir: Path = DEFAULT_FT_DATA_DIR,
    output_dir: Path = DEFAULT_DPO_OUTPUT_DIR,
    modelo_base: str = MODELO_BASE_HF,
    max_seq_length: int = 3584,
    beta: float = 0.1,
    lambda_nll: float = 0.05,
    epochs: float = 3.0,
    grad_accum: int = 4,
    learning_rate: float = 1e-5,
    lora_r: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.08,
    eval_every_steps: int = 6,
    seed: int = 2026,
    validate_only: bool = False,
    merge_dir: Path | None = None,
) -> dict[str, Any]:
    """Audita pares DPO, precomputa `ref_logps` y entrena QLoRA Split-Backward + fusiona FP16."""
    from transformers import AutoTokenizer

    train_raw = cargar_jsonl(data_dir / "dpo_train.jsonl")
    val_raw = cargar_jsonl(data_dir / "dpo_val.jsonl")
    aud = validar_dataset_dpo(train_raw + val_raw)
    if not aud["ok"]:
        raise ValueError(f"Falla auditoría antifuga DPO: {aud['errores'][:5]}")

    tokenizer = AutoTokenizer.from_pretrained(modelo_base)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_tok = [construir_par_dpo(r, tokenizer, max_seq_length=max_seq_length) for r in train_raw]
    val_tok = [construir_par_dpo(r, tokenizer, max_seq_length=max_seq_length) for r in val_raw]

    resumen = {
        "modelo_base": modelo_base,
        "antifuga_ok": True,
        "train_count": len(train_tok),
        "val_count": len(val_tok),
        "tokens_train": resumir_tokens_dataset(train_tok),
        "tokens_val": resumir_tokens_dataset(val_tok),
    }
    if validate_only:
        return resumen

    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    import torch
    from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig

    if not torch.cuda.is_available():
        raise RuntimeError("El entrenamiento DPO QLoRA requiere GPU CUDA (Colab T4/L4/A100).")

    _fijar_semillas(seed)
    t0 = time.perf_counter()
    cap = torch.cuda.get_device_capability(0)
    usar_bf16 = bool(torch.cuda.is_bf16_supported() and cap[0] >= 8)
    compute_dtype = torch.bfloat16 if usar_bf16 else torch.float16
    device = torch.device("cuda:0")

    bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        modelo_base,
        quantization_config=bnb_cfg,
        device_map="auto",
        torch_dtype=compute_dtype,
        attn_implementation="sdpa",
    )
    base_model.config.use_cache = False
    base_model = prepare_model_for_kbit_training(
        base_model,
        use_gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
    )

    # Precomputar `ref_logps` sobre el modelo base congelado (ya normalizado) antes de acoplar LoRA
    train_pares = _precomputar_ref_logps(base_model, train_tok, device, compute_dtype)
    val_pares = _precomputar_ref_logps(base_model, val_tok, device, compute_dtype)
    lora_cfg = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=list(LORA_TARGET_MODULES),
    )
    model = get_peft_model(base_model, lora_cfg)
    for param in model.parameters():
        if param.requires_grad and param.dtype != torch.float32:
            param.data = param.data.float()

    # Planificación de chunks de grad_accum para calcular total_steps del scheduler
    rng_ep = random.Random(seed)
    total_chunks: list[list[int]] = []
    full_epochs = int(math.ceil(epochs))
    for ep_idx in range(full_epochs):
        idxs = list(range(len(train_pares)))
        rng_ep.shuffle(idxs)
        if ep_idx == full_epochs - 1 and epochs < full_epochs:
            frac = epochs - (full_epochs - 1)
            idxs = idxs[: max(1, int(round(len(idxs) * frac)))]
        for start in range(0, len(idxs), grad_accum):
            total_chunks.append(idxs[start : start + grad_accum])

    total_steps = max(1, len(total_chunks))
    warmup_steps = max(1, int(round(0.1 * total_steps)))
    optimizer = _crear_optimizador(model, learning_rate=learning_rate)

    def _lr_lambda(step_idx: int) -> float:
        if step_idx < warmup_steps:
            return float(step_idx + 1) / float(warmup_steps)
        progreso = min(1.0, float(step_idx - warmup_steps) / float(max(1, total_steps - warmup_steps)))
        return 0.1 + 0.9 * 0.5 * (1.0 + math.cos(math.pi * progreso))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, _lr_lambda)
    scaler = torch.amp.GradScaler("cuda", enabled=(compute_dtype == torch.float16))

    output_dir = Path(output_dir)
    adapter_dir = output_dir / "adapter"
    best_adapter_dir = output_dir / "best_adapter"
    output_dir.mkdir(parents=True, exist_ok=True)

    eval_inicial = _evaluar_dpo(model, val_pares, device, compute_dtype, beta=beta, lambda_nll=lambda_nll)
    mejor_eval_loss = float(eval_inicial["eval_dpo_loss"])
    mejor_step = 0
    model.save_pretrained(str(best_adapter_dir))
    tokenizer.save_pretrained(str(best_adapter_dir))

    train_log: list[dict[str, Any]] = []
    eval_log: list[dict[str, Any]] = [{"step": 0, **eval_inicial}]

    model.train()
    for step, chunk in enumerate(total_chunks, 1):
        optimizer.zero_grad(set_to_none=True)
        acum = {"dpo_loss": 0.0, "total_loss": 0.0, "reward_margin": 0.0, "pref_acc": 0.0}
        for idx in chunk:
            m = _paso_split_backward_par(
                model,
                train_pares[idx],
                device,
                compute_dtype,
                scaler,
                beta=beta,
                lambda_nll=lambda_nll,
                chunk_len=len(chunk),
            )
            for k in acum:
                acum[k] += m[k]

        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()
        scheduler.step()

        denom = float(len(chunk))
        tr_entry = {
            "step": step,
            "dpo_loss": round(acum["dpo_loss"] / denom, 6),
            "total_loss": round(acum["total_loss"] / denom, 6),
            "reward_margin": round(acum["reward_margin"] / denom, 6),
            "pref_acc": round(acum["pref_acc"] / denom, 4),
            "lr": float(scheduler.get_last_lr()[0]),
        }
        train_log.append(tr_entry)
        print(f"[DPO step {step}/{total_steps}] loss={tr_entry['dpo_loss']:.4f} margin={tr_entry['reward_margin']:.4f} acc={tr_entry['pref_acc']:.2f}", flush=True)

        if step % eval_every_steps == 0 or step == total_steps:
            ev = _evaluar_dpo(model, val_pares, device, compute_dtype, beta=beta, lambda_nll=lambda_nll)
            eval_log.append({"step": step, **ev})
            print(
                f"  -> [EVAL step {step}] eval_dpo_loss={ev['eval_dpo_loss']:.4f} "
                f"eval_pref_acc={ev['eval_pref_acc']:.3f} margin={ev['eval_reward_margin']:.4f}",
                flush=True,
            )
            if ev["eval_dpo_loss"] < mejor_eval_loss:
                mejor_eval_loss = float(ev["eval_dpo_loss"])
                mejor_step = step
                model.save_pretrained(str(best_adapter_dir))
                tokenizer.save_pretrained(str(best_adapter_dir))

    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))

    curvas = graficar_curvas_dpo(
        train_log,
        eval_log,
        salida_png=output_dir / "dpo_loss_curve.png",
        mejor_step=mejor_step,
    )

    # Smoke test sobre el mejor checkpoint observado en validación
    smoke_model = model
    if best_adapter_dir.exists():
        try:
            smoke_model.load_adapter(str(best_adapter_dir), adapter_name="best_dpo")
            smoke_model.set_adapter("best_dpo")
        except Exception:
            smoke_model = model
    smoke = _smoke_test_dpo(smoke_model, tokenizer, val_raw, max_ejemplos=4)

    eval_final = eval_log[-1]
    metricas = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "modelo_base": modelo_base,
        "gpu": torch.cuda.get_device_name(0),
        "compute_dtype": str(compute_dtype).replace("torch.", ""),
        "hiperparametros": {
            "beta": beta,
            "lambda_nll": lambda_nll,
            "lora_r": lora_r,
            "lora_alpha": lora_alpha,
            "lora_dropout": lora_dropout,
            "learning_rate": learning_rate,
            "epochs": epochs,
            "grad_accum": grad_accum,
            "max_seq_length": max_seq_length,
        },
        "datos": resumen,
        "resultados": {
            "eval_dpo_loss_inicial": eval_inicial["eval_dpo_loss"],
            "eval_dpo_loss_final": eval_final["eval_dpo_loss"],
            "mejor_eval_dpo_loss": round(mejor_eval_loss, 6),
            "eval_pref_acc_inicial": eval_inicial["eval_pref_acc"],
            "eval_pref_acc_final": eval_final["eval_pref_acc"],
            "eval_reward_margin_final": eval_final["eval_reward_margin"],
            "pasos_totales": total_steps,
            "mejor_step": mejor_step,
            "tiempo_min": round((time.perf_counter() - t0) / 60.0, 2),
        },
        "curvas": curvas,
        "smoke_test_val": smoke,
    }
    (output_dir / "training_metrics.json").write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if merge_dir is not None:
        del smoke_model, model, base_model, optimizer, scaler, scheduler
        gc.collect()
        torch.cuda.empty_cache()

        origen_merge = best_adapter_dir if best_adapter_dir.exists() else adapter_dir
        fp_base = AutoModelForCausalLM.from_pretrained(
            modelo_base, torch_dtype=compute_dtype, device_map="auto", low_cpu_mem_usage=True
        )
        merged = PeftModel.from_pretrained(fp_base, str(origen_merge)).merge_and_unload()
        Path(merge_dir).mkdir(parents=True, exist_ok=True)
        merged.save_pretrained(str(merge_dir), safe_serialization=True)
        tokenizer.save_pretrained(str(merge_dir))
        if best_adapter_dir != adapter_dir and best_adapter_dir.exists():
            shutil.copy2(best_adapter_dir / "adapter_model.safetensors", adapter_dir / "best_adapter_model.safetensors")
        metricas["merged_dir"] = str(merge_dir)
        metricas["merged_from"] = origen_merge.name
        (output_dir / "training_metrics.json").write_text(
            json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return metricas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Entrena DPO Split-Backward QLoRA sobre Qwen3-4B-Instruct-2507")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_FT_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_DPO_OUTPUT_DIR)
    parser.add_argument("--merge-dir", type=Path, default=None)
    parser.add_argument("--modelo-base", type=str, default=MODELO_BASE_HF)
    parser.add_argument("--max-seq-length", type=int, default=3584)
    parser.add_argument("--beta", type=float, default=0.1)
    parser.add_argument("--lambda-nll", type=float, default=0.05)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--lr", type=float, default=1e-5)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.08)
    parser.add_argument("--eval-every", type=int, default=6)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)

    res = entrenar_dpo_qlora(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        modelo_base=args.modelo_base,
        max_seq_length=args.max_seq_length,
        beta=args.beta,
        lambda_nll=args.lambda_nll,
        epochs=args.epochs,
        grad_accum=args.grad_accum,
        learning_rate=args.lr,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        eval_every_steps=args.eval_every,
        validate_only=args.validate_only,
        merge_dir=args.merge_dir,
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
