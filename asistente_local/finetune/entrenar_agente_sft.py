"""Entrenamiento QLoRA multi-turno para Qwen3-4B-Instruct-2507 con tool-calling nativo."""

from __future__ import annotations

import argparse
import gc
import inspect
import json
import math
import os
import random
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..herramientas import ESQUEMAS_HERRAMIENTAS
from . import MODELO_BASE_HF
from .antifuga import validar_dataset_completo
from .construir_dataset import DEFAULT_FT_DATA_DIR

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "salida"
LORA_TARGET_MODULES: tuple[str, ...] = (
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
)


def cargar_jsonl(path: Path) -> list[dict[str, Any]]:
    """Lee un archivo JSONL UTF-8 devolviendo la lista de registros."""
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def construir_ejemplo_sft_multiturno(
    registro: dict[str, Any],
    tokenizer: Any,
    tools: list[dict[str, Any]] = ESQUEMAS_HERRAMIENTAS,
    max_seq_length: int = 4096,
) -> dict[str, Any]:
    """Tokeniza con plantilla oficial Qwen3+Tools y calcula pérdida solo tras el último turno `user`."""
    msgs = registro["messages"]
    ultimo_user_idx = max((i for i, m in enumerate(msgs) if m.get("role") == "user"), default=-1)
    if ultimo_user_idx < 0:
        raise ValueError(f"{registro.get('id')}: conversación sin mensajes de usuario")

    full_ids: list[int] = list(
        tokenizer.apply_chat_template(
            msgs,
            tools=tools,
            add_generation_prompt=False,
            tokenize=True,
        )
    )
    labels = [-100] * len(full_ids)

    # Enmascarar system, historial previo, último prompt user y `<tool_response>` con -100;
    # entrenar únicamente los turnos `assistant` posteriores al último `user` (tool_calls + respuesta).
    for i in range(ultimo_user_idx + 1, len(msgs)):
        if msgs[i].get("role") != "assistant":
            continue
        s_ids = list(
            tokenizer.apply_chat_template(
                msgs[:i],
                tools=tools,
                add_generation_prompt=True,
                tokenize=True,
            )
        )
        e_ids = list(
            tokenizer.apply_chat_template(
                msgs[: i + 1],
                tools=tools,
                add_generation_prompt=False,
                tokenize=True,
            )
        )
        if full_ids[: len(s_ids)] != s_ids or full_ids[: len(e_ids)] != e_ids:
            raise ValueError(f"{registro.get('id')}: desalineación de prefijo en turno assistant idx={i}")
        for pos in range(len(s_ids), len(e_ids)):
            labels[pos] = full_ids[pos]

    truncado = len(full_ids) > max_seq_length
    if truncado:
        full_ids = full_ids[:max_seq_length]
        labels = labels[:max_seq_length]

    sup_tokens = sum(1 for lab in labels if lab != -100)
    if sup_tokens == 0:
        raise ValueError(
            f"{registro.get('id')}: 0 tokens supervisados tras truncar a max_seq_length={max_seq_length}"
        )

    return {
        "id": registro["id"],
        "input_ids": full_ids,
        "attention_mask": [1] * len(full_ids),
        "labels": labels,
        "total_tokens": len(full_ids),
        "supervised_tokens": sup_tokens,
        "truncado": truncado,
    }


def resumir_tokens_dataset(ejemplos: list[dict[str, Any]]) -> dict[str, Any]:
    """Resume distribución de longitudes totales y supervisadas para diagnóstico previo."""
    totales = [e["total_tokens"] for e in ejemplos]
    sups = [e["supervised_tokens"] for e in ejemplos]
    ordenados = sorted(totales)
    p95_idx = min(len(ordenados) - 1, max(0, int(round(0.95 * (len(ordenados) - 1)))))
    return {
        "ejemplos": len(ejemplos),
        "truncados": sum(1 for e in ejemplos if e["truncado"]),
        "total_tokens": {
            "min": min(totales),
            "mediana": statistics.median(totales),
            "promedio": round(sum(totales) / len(totales), 1),
            "p95": ordenados[p95_idx],
            "max": max(totales),
        },
        "supervised_tokens_promedio": round(sum(sups) / len(sups), 1),
    }


class DataCollatorMultiTurno:
    """Aplica padding derecho alineado a `input_ids`, `attention_mask` y `labels` (`-100`)."""

    def __init__(self, pad_token_id: int) -> None:
        self.pad_token_id = int(pad_token_id)

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, Any]:
        import torch

        max_len = max(len(f["input_ids"]) for f in features)
        b_ids, b_mask, b_labels = [], [], []
        for f in features:
            pad_n = max_len - len(f["input_ids"])
            b_ids.append(list(f["input_ids"]) + [self.pad_token_id] * pad_n)
            b_mask.append(list(f["attention_mask"]) + [0] * pad_n)
            b_labels.append(list(f["labels"]) + [-100] * pad_n)
        return {
            "input_ids": torch.tensor(b_ids, dtype=torch.long),
            "attention_mask": torch.tensor(b_mask, dtype=torch.long),
            "labels": torch.tensor(b_labels, dtype=torch.long),
        }


def graficar_curvas_perdida(
    log_history: list[dict[str, Any]],
    eval_inicial: dict[str, Any] | None,
    salida_png: Path,
    mejor_step: int | None = None,
) -> dict[str, list[dict[str, float | int]]]:
    """Extrae curvas train/eval y guarda gráfico PNG de diagnóstico."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    train_pts: dict[int, dict[str, Any]] = {}
    eval_pts: dict[int, dict[str, Any]] = {}
    if eval_inicial and "eval_loss" in eval_inicial:
        eval_pts[0] = {"step": 0, "epoch": 0.0, "eval_loss": round(float(eval_inicial["eval_loss"]), 6)}
    for entry in log_history:
        step = int(entry.get("step", 0))
        epoch = round(float(entry.get("epoch", 0.0)), 4)
        if "loss" in entry:
            train_pts[step] = {"step": step, "epoch": epoch, "loss": round(float(entry["loss"]), 6)}
        if "eval_loss" in entry:
            eval_pts[step] = {"step": step, "epoch": epoch, "eval_loss": round(float(entry["eval_loss"]), 6)}

    tr = [train_pts[k] for k in sorted(train_pts)]
    ev = [eval_pts[k] for k in sorted(eval_pts)]
    if tr or ev:
        fig, ax = plt.subplots(figsize=(7.0, 3.8), dpi=220)
        if tr:
            ax.plot([p["step"] for p in tr], [p["loss"] for p in tr], marker="o", label="train_loss")
        if ev:
            ax.plot([p["step"] for p in ev], [p["eval_loss"] for p in ev], marker="s", label="eval_loss")
        if mejor_step is not None:
            ax.axvline(mejor_step, linestyle="--", color="green", label=f"best step {mejor_step}")
        ax.set_title("QLoRA Qwen3-4B-Instruct-2507 (Agente Único Tool-Calling + RAG)")
        ax.set_xlabel("Step")
        ax.set_ylabel("Cross-Entropy Loss")
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend()
        fig.tight_layout()
        salida_png.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(salida_png, dpi=220, bbox_inches="tight")
        plt.close(fig)
    return {"train": tr, "eval": ev}


def _fijar_semillas(seed: int) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    import torch

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _smoke_test_validacion(model: Any, tokenizer: Any, val_records: list[dict[str, Any]], max_ejemplos: int = 3) -> list[dict[str, Any]]:
    """Ejecuta generación real greedy sobre ejemplos de validación (tool_call y texto)."""
    import torch

    muestras: list[dict[str, Any]] = []
    categorias_vistas: set[str] = set()
    elegidos: list[dict[str, Any]] = []
    for r in val_records:
        if r.get("categoria") not in categorias_vistas:
            elegidos.append(r)
            categorias_vistas.add(str(r.get("categoria")))
        if len(elegidos) >= max_ejemplos:
            break

    model.config.use_cache = True
    model.eval()
    device = next(model.parameters()).device
    for r in elegidos:
        msgs = r["messages"]
        u_idx = max(i for i, m in enumerate(msgs) if m.get("role") == "user")
        prompt_text = tokenizer.apply_chat_template(
            msgs[: u_idx + 1], tools=ESQUEMAS_HERRAMIENTAS, add_generation_prompt=True, tokenize=False
        )
        inputs = tokenizer(prompt_text, return_tensors="pt").to(device)
        with torch.no_grad():
            out_ids = model.generate(
                **inputs, max_new_tokens=320, do_sample=False, pad_token_id=tokenizer.pad_token_id
            )
        gen = tokenizer.decode(out_ids[0][inputs["input_ids"].shape[1] :], skip_special_tokens=False)
        muestras.append(
            {
                "id": r["id"],
                "categoria": r.get("categoria"),
                "esperado_tool_call": bool(msgs[u_idx + 1].get("tool_calls")),
                "salida_generada": gen.strip(),
            }
        )
    return muestras


def entrenar_qlora(
    data_dir: Path = DEFAULT_FT_DATA_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    modelo_base: str = MODELO_BASE_HF,
    max_seq_length: int = 4096,
    epochs: float = 3.0,
    grad_accum: int = 4,
    learning_rate: float = 5e-5,
    lora_r: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.08,
    seed: int = 2026,
    validate_only: bool = False,
    merge_dir: Path | None = None,
) -> dict[str, Any]:
    """Valida dataset sin fugas, tokeniza multi-turno y opcionalmente entrena + fusiona QLoRA."""
    from transformers import AutoTokenizer

    train_raw = cargar_jsonl(data_dir / "train.jsonl")
    val_raw = cargar_jsonl(data_dir / "val.jsonl")
    auditoria = validar_dataset_completo(train_raw + val_raw)
    if not auditoria["ok"]:
        raise ValueError(f"Falla auditoría antifuga: {auditoria['errores'][:5]}")

    tokenizer = AutoTokenizer.from_pretrained(modelo_base)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_sft = [construir_ejemplo_sft_multiturno(r, tokenizer, max_seq_length=max_seq_length) for r in train_raw]
    val_sft = [construir_ejemplo_sft_multiturno(r, tokenizer, max_seq_length=max_seq_length) for r in val_raw]

    resumen = {
        "modelo_base": modelo_base,
        "antifuga_ok": True,
        "tokens_train": resumir_tokens_dataset(train_sft),
        "tokens_val": resumir_tokens_dataset(val_sft),
    }
    if validate_only:
        return resumen

    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig, Trainer, TrainingArguments

    if not torch.cuda.is_available():
        raise RuntimeError("El entrenamiento QLoRA requiere GPU CUDA (ejecútalo en Colab T4/L4/A100).")

    _fijar_semillas(seed)
    t0 = time.perf_counter()
    cap = torch.cuda.get_device_capability(0)
    usar_bf16 = bool(torch.cuda.is_bf16_supported() and cap[0] >= 8)
    compute_dtype = torch.bfloat16 if usar_bf16 else torch.float16

    bnb_cfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )
    try:
        base_model = AutoModelForCausalLM.from_pretrained(
            modelo_base,
            quantization_config=bnb_cfg,
            device_map="auto",
            torch_dtype=compute_dtype,
            attn_implementation="sdpa",
        )
    except TypeError:
        base_model = AutoModelForCausalLM.from_pretrained(
            modelo_base,
            quantization_config=bnb_cfg,
            device_map="auto",
            torch_dtype=compute_dtype,
        )
    base_model.config.use_cache = False
    base_model = prepare_model_for_kbit_training(
        base_model,
        use_gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
    )

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

    output_dir = Path(output_dir)
    checkpoints_dir = output_dir / "checkpoints"
    adapter_dir = output_dir / "adapter"
    output_dir.mkdir(parents=True, exist_ok=True)

    class _DatasetSFT(torch.utils.data.Dataset):
        def __init__(self, items: list[dict[str, Any]]) -> None:
            self.items = [
                {"input_ids": e["input_ids"], "attention_mask": e["attention_mask"], "labels": e["labels"]}
                for e in items
            ]

        def __len__(self) -> int:
            return len(self.items)

        def __getitem__(self, idx: int) -> dict[str, Any]:
            return self.items[idx]

    ds_train = _DatasetSFT(train_sft)
    ds_val = _DatasetSFT(val_sft)

    steps_per_epoch = max(1, math.ceil(len(train_sft) / max(1, grad_accum)))
    total_steps = max(1, int(round(steps_per_epoch * epochs)))
    warmup_steps = max(1, int(round(total_steps * 0.10)))

    ta_params = inspect.signature(TrainingArguments.__init__).parameters
    eval_key = "eval_strategy" if "eval_strategy" in ta_params else "evaluation_strategy"
    ta_kwargs: dict[str, Any] = {
        "output_dir": str(checkpoints_dir),
        "per_device_train_batch_size": 1,
        "per_device_eval_batch_size": 1,
        "gradient_accumulation_steps": grad_accum,
        "eval_accumulation_steps": 4,
        "learning_rate": learning_rate,
        "num_train_epochs": epochs,
        "lr_scheduler_type": "cosine",
        "warmup_steps": warmup_steps,
        "weight_decay": 0.01,
        "max_grad_norm": 1.0,
        "logging_steps": 5,
        eval_key: "steps",
        "save_strategy": "steps",
        "eval_steps": 9,
        "save_steps": 9,
        "save_total_limit": 2,
        "load_best_model_at_end": True,
        "metric_for_best_model": "eval_loss",
        "greater_is_better": False,
        "bf16": usar_bf16,
        "fp16": not usar_bf16,
        "optim": "paged_adamw_8bit",
        "gradient_checkpointing": True,
        "report_to": "none",
        "seed": seed,
        "remove_unused_columns": False,
    }
    args_train = TrainingArguments(**ta_kwargs)
    trainer = Trainer(
        model=model,
        args=args_train,
        train_dataset=ds_train,
        eval_dataset=ds_val,
        data_collator=DataCollatorMultiTurno(tokenizer.pad_token_id),
    )

    eval_inicial = trainer.evaluate()
    train_res = trainer.train()
    eval_final = trainer.evaluate()

    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))

    mejor_ckpt = str(trainer.state.best_model_checkpoint or "")
    mejor_step = int(mejor_ckpt.split("checkpoint-")[-1]) if "checkpoint-" in mejor_ckpt else None
    curvas = graficar_curvas_perdida(
        trainer.state.log_history,
        eval_inicial=eval_inicial,
        salida_png=output_dir / "loss_curve.png",
        mejor_step=mejor_step,
    )
    smoke = _smoke_test_validacion(model, tokenizer, val_raw, max_ejemplos=4)

    metricas = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "modelo_base": modelo_base,
        "gpu": torch.cuda.get_device_name(0),
        "compute_dtype": str(compute_dtype).replace("torch.", ""),
        "hiperparametros": {
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
            "eval_loss_inicial": round(float(eval_inicial["eval_loss"]), 6),
            "eval_loss_final": round(float(eval_final["eval_loss"]), 6),
            "mejor_eval_loss": round(float(trainer.state.best_metric or eval_final["eval_loss"]), 6),
            "train_loss_final": round(float(train_res.training_loss), 6),
            "pasos_totales": int(trainer.state.global_step),
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
        from peft import PeftModel

        del trainer, model, base_model
        gc.collect()
        torch.cuda.empty_cache()
        fp_base = AutoModelForCausalLM.from_pretrained(
            modelo_base, torch_dtype=compute_dtype, device_map="auto", low_cpu_mem_usage=True
        )
        merged = PeftModel.from_pretrained(fp_base, str(adapter_dir)).merge_and_unload()
        Path(merge_dir).mkdir(parents=True, exist_ok=True)
        merged.save_pretrained(str(merge_dir), safe_serialization=True)
        tokenizer.save_pretrained(str(merge_dir))
        metricas["merged_dir"] = str(merge_dir)

    return metricas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fine-tuning QLoRA multi-turno para asistente local UdeC")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_FT_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--modelo-base", default=MODELO_BASE_HF)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--merge-dir", type=Path, default=None)
    args = parser.parse_args(argv)

    res = entrenar_qlora(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        modelo_base=args.modelo_base,
        epochs=args.epochs,
        learning_rate=args.lr,
        grad_accum=args.grad_accum,
        validate_only=args.validate_only,
        merge_dir=args.merge_dir,
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
