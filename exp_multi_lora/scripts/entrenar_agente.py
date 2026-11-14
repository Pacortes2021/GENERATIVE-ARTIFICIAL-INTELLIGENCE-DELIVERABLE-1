"""Entrenamiento QLoRA parametrizable por agente (`enrutador`, `recuperador`, `verificador`, `redactor`).

Reutiliza las primitivas verificadas de `Deliverable 4/scripts/entrenar_redactor.py`:
- Cuantización 4 bits NF4 + doble cuantización (`bf16` en A100+, `fp16` en T4)
- `completion_only_loss` (`labels = -100` en todo el prompt del sistema/contexto)
- `LoraConfig` `r=16, alpha=32` sobre las 7 proyecciones lineales
- Guardado completo de `adapter/`, curvas de pérdida, `training_metrics.json` y `smoke_test_val.json`
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
D4_SCRIPTS_DIR = REPO_ROOT / "Deliverable 4" / "scripts"
D4_DATOS_DIR = REPO_ROOT / "Deliverable 4" / "datos"
EXP_DIR = REPO_ROOT / "exp_multi_lora"
EXP_DATOS_DIR = EXP_DIR / "datos"
EXP_TRAIN_DIR = EXP_DIR / "entrenamiento"

if str(D4_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(D4_SCRIPTS_DIR))

import entrenar_redactor as er  # noqa: E402

DEFAULTS_POR_AGENTE: dict[str, dict[str, Any]] = {
    "enrutador": {
        "train_jsonl": EXP_DATOS_DIR / "enrutador_train.jsonl",
        "val_jsonl": EXP_DATOS_DIR / "enrutador_val.jsonl",
        "output_dir": EXP_TRAIN_DIR / "enrutador",
        "max_seq_length": 2048,
        "epochs": 3.0,
        "batch_size": 1,
        "grad_accum": 6,
        "learning_rate": 1e-4,
        "eval_steps": 10,
        "save_steps": 10,
        "smoke_max_new_tokens": 256,
    },
    "recuperador": {
        "train_jsonl": EXP_DATOS_DIR / "recuperador_train.jsonl",
        "val_jsonl": EXP_DATOS_DIR / "recuperador_val.jsonl",
        "output_dir": EXP_TRAIN_DIR / "recuperador",
        "max_seq_length": 2048,
        "epochs": 3.0,
        "batch_size": 1,
        "grad_accum": 6,
        "learning_rate": 1e-4,
        "eval_steps": 15,
        "save_steps": 15,
        "smoke_max_new_tokens": 160,
    },
    "verificador": {
        "train_jsonl": EXP_DATOS_DIR / "verificador_train.jsonl",
        "val_jsonl": EXP_DATOS_DIR / "verificador_val.jsonl",
        "output_dir": EXP_TRAIN_DIR / "verificador",
        "max_seq_length": 4096,
        "epochs": 3.0,
        "batch_size": 1,
        "grad_accum": 6,
        "learning_rate": 1e-4,
        "eval_steps": 15,
        "save_steps": 15,
        "smoke_max_new_tokens": 700,
    },
    "redactor": {
        "train_jsonl": D4_DATOS_DIR / "redactor_train.jsonl",
        "val_jsonl": D4_DATOS_DIR / "redactor_val.jsonl",
        "output_dir": EXP_TRAIN_DIR / "redactor",
        "max_seq_length": 4096,
        "epochs": 3.0,
        "batch_size": 1,
        "grad_accum": 6,
        "learning_rate": 1e-4,
        "eval_steps": 15,
        "save_steps": 15,
        "smoke_max_new_tokens": 900,
    },
}


def generar_model_card_agente(
    agente: str,
    metricas: dict[str, Any],
    hf_repo: str | None = None,
) -> str:
    """Genera un README.md claro para el adaptador LoRA de `agente`."""
    res = metricas["resultados"]
    datos = metricas["datos"]
    hip = metricas["hiperparametros"]
    hw = metricas["hardware"]
    lineas = [
        f"# Adaptador QLoRA — Agente `{agente}` (Exp. Multi-LoRA UdeC)",
        "",
        f"- **Modelo base:** `{metricas['modelo_base']}`",
        f"- **Agente entrenado:** `{agente}`",
        f"- **Método:** `{hip['metodo']}` (`r={hip['lora_r']}`, `alpha={hip['lora_alpha']}`, `dropout={hip['lora_dropout']}`)",
        f"- **Dataset:** `{datos['train_ejemplos']}` train / `{datos['val_ejemplos']}` val (`completion_only_loss=True`, truncados train=`{datos['tokens_train']['truncados']}`, val=`{datos['tokens_val']['truncados']}`)",
        f"- **Hardware:** `{hw['gpu']}` (`{hw['compute_dtype']}`), tiempo `{res['tiempo_entrenamiento_min']} min`",
        f"- **Evaluación:** `eval_loss` `{res['eval_loss_inicial']}` → mejor **`{res['mejor_eval_loss']}`** (step `{res['mejor_step']}`)",
    ]
    if hf_repo:
        lineas.append(f"- **Hugging Face:** `https://huggingface.co/{hf_repo}`")
    lineas.append("")
    return "\n".join(lineas)


def _smoke_test_val_agente(
    model: Any,
    tokenizer: Any,
    val_registros: list[dict[str, Any]],
    max_new_tokens: int = 512,
    n_muestras: int = 3,
) -> list[dict[str, Any]]:
    """Compara rápidamente salida base vs adaptador en `n_muestras` estratificadas de val."""
    import torch

    if not val_registros:
        return []
    if len(val_registros) <= n_muestras:
        seleccion = list(val_registros)
    else:
        idxs = sorted({0, len(val_registros) // 2, len(val_registros) - 1})
        seleccion = [val_registros[i] for i in idxs[:n_muestras]]

    model.config.use_cache = True
    model.eval()
    resultados: list[dict[str, Any]] = []

    def _gen(prompt_text: str) -> str:
        inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)
        torch.manual_seed(2026)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        gen = out[0][inputs["input_ids"].shape[1] :]
        return tokenizer.decode(gen, skip_special_tokens=True).strip()

    for reg in seleccion:
        prompt_text = er.formatear_prompt_usuario(tokenizer, reg["messages"][0]["content"])
        with model.disable_adapter():
            salida_base = _gen(prompt_text)
        salida_ft = _gen(prompt_text)
        resultados.append(
            {
                "id": reg["id"],
                "esperado": reg["messages"][1]["content"],
                "salida_base": salida_base,
                "salida_finetuned": salida_ft,
            }
        )
    return resultados


def entrenar_agente(args: argparse.Namespace) -> dict[str, Any]:
    """Ejecuta el entrenamiento QLoRA completo para `args.agente`."""
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        Trainer,
        TrainingArguments,
        set_seed,
    )

    if not torch.cuda.is_available():
        raise RuntimeError(
            "Se requiere GPU CUDA (Colab T4/L4/A100) para entrenar el adaptador QLoRA."
        )

    random.seed(args.seed)
    set_seed(args.seed)

    train_registros = er.cargar_jsonl(args.train_jsonl)
    val_registros = er.cargar_jsonl(args.val_jsonl)

    tokenizer = AutoTokenizer.from_pretrained(args.modelo_base)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_sft = [
        er.construir_ejemplo_sft(r, tokenizer, args.max_seq_length)
        for r in train_registros
    ]
    val_sft = [
        er.construir_ejemplo_sft(r, tokenizer, args.max_seq_length)
        for r in val_registros
    ]
    stats_train = er.resumen_longitudes_sft(train_sft)
    stats_val = er.resumen_longitudes_sft(val_sft)

    class _DatasetSFT(torch.utils.data.Dataset):
        def __init__(self, items: list[dict[str, Any]]) -> None:
            self.items = [
                {
                    "input_ids": x["input_ids"],
                    "attention_mask": x["attention_mask"],
                    "labels": x["labels"],
                }
                for x in items
            ]

        def __len__(self) -> int:
            return len(self.items)

        def __getitem__(self, idx: int) -> dict[str, Any]:
            return self.items[idx]

    use_bf16 = er.es_bf16_nativo(
        torch.cuda.get_device_capability(0), torch.cuda.is_bf16_supported()
    )
    compute_dtype = torch.bfloat16 if use_bf16 else torch.float16
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=True,
    )

    try:
        model = AutoModelForCausalLM.from_pretrained(
            args.modelo_base,
            quantization_config=bnb_config,
            device_map="auto",
            attn_implementation="sdpa",
        )
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(
            args.modelo_base,
            quantization_config=bnb_config,
            device_map="auto",
        )

    model.config.use_cache = False
    model = prepare_model_for_kbit_training(
        model,
        use_gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
    )

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=list(args.target_modules),
    )
    model = get_peft_model(model, lora_config)
    for p in model.parameters():
        if p.requires_grad and p.dtype != torch.float32:
            p.data = p.data.float()

    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())

    steps_per_epoch = max(
        1, math.ceil(len(train_sft) / (args.batch_size * args.grad_accum))
    )
    total_steps = max(1, int(round(steps_per_epoch * args.epochs)))
    warmup_steps = max(1, int(round(total_steps * args.warmup_ratio)))

    output_dir = Path(args.output_dir)
    checkpoints_dir = output_dir / "checkpoints"
    adapter_dir = output_dir / "adapter"
    output_dir.mkdir(parents=True, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=str(checkpoints_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=args.grad_accum,
        eval_accumulation_steps=4,
        learning_rate=args.learning_rate,
        lr_scheduler_type=args.lr_scheduler_type,
        warmup_steps=warmup_steps,
        weight_decay=args.weight_decay,
        max_grad_norm=1.0,
        optim="paged_adamw_8bit",
        fp16=not use_bf16,
        bf16=use_bf16,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        logging_strategy="steps",
        logging_steps=args.logging_steps,
        eval_strategy="steps",
        eval_steps=args.eval_steps,
        save_strategy="steps",
        save_steps=args.save_steps,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        remove_unused_columns=False,
        dataloader_num_workers=0,
        report_to="none",
        seed=args.seed,
    )

    collator = er.DataCollatorParaCompletado(pad_token_id=tokenizer.pad_token_id)
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=collator,
        train_dataset=_DatasetSFT(train_sft),
        eval_dataset=_DatasetSFT(val_sft),
    )

    eval_inicial = trainer.evaluate()
    t0 = time.perf_counter()
    train_out = trainer.train()
    wall_time_sec = round(time.perf_counter() - t0, 2)

    curvas = er.extraer_curvas_de_log_history(
        trainer.state.log_history, eval_inicial=eval_inicial
    )
    mejor_step = None
    if trainer.state.best_model_checkpoint:
        try:
            mejor_step = int(Path(trainer.state.best_model_checkpoint).name.split("-")[-1])
        except ValueError:
            mejor_step = None

    gpu_nombre = torch.cuda.get_device_name(0)
    vram_gb = round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2)

    metricas: dict[str, Any] = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "agente": args.agente,
        "modelo_base": args.modelo_base,
        "revision_modelo_base": getattr(model.config, "_commit_hash", None),
        "hf_repo": args.hf_repo,
        "hardware": {
            "gpu": gpu_nombre,
            "vram_gb": vram_gb,
            "compute_dtype": str(compute_dtype),
            "versiones": er._resolver_versiones(),
        },
        "datos": {
            "train_jsonl": str(args.train_jsonl),
            "val_jsonl": str(args.val_jsonl),
            "train_sha256": er.sha256_archivo(args.train_jsonl),
            "val_sha256": er.sha256_archivo(args.val_jsonl),
            "train_ejemplos": len(train_sft),
            "val_ejemplos": len(val_sft),
            "max_seq_length": args.max_seq_length,
            "tokens_train": stats_train,
            "tokens_val": stats_val,
        },
        "hiperparametros": {
            "metodo": "QLoRA (4-bit NF4 + doble cuantización)",
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
            "target_modules": list(args.target_modules),
            "epochs": args.epochs,
            "per_device_train_batch_size": args.batch_size,
            "gradient_accumulation_steps": args.grad_accum,
            "effective_batch_size": args.batch_size * args.grad_accum,
            "learning_rate": args.learning_rate,
            "lr_scheduler_type": args.lr_scheduler_type,
            "warmup_ratio": args.warmup_ratio,
            "warmup_steps": warmup_steps,
            "weight_decay": args.weight_decay,
            "optim": "paged_adamw_8bit",
            "seed": args.seed,
            "completion_only_loss": True,
            "enable_thinking": False,
        },
        "parametros": {
            "total": total_params,
            "entrenables_lora": trainable_params,
            "porcentaje_entrenable": round(100.0 * trainable_params / total_params, 4),
        },
        "resultados": {
            "pasos_totales": int(trainer.state.global_step),
            "tiempo_entrenamiento_seg": wall_time_sec,
            "tiempo_entrenamiento_min": round(wall_time_sec / 60.0, 2),
            "train_loss_final_agregada": round(float(train_out.training_loss), 6),
            "eval_loss_inicial": round(float(eval_inicial["eval_loss"]), 6),
            "mejor_eval_loss": (
                round(float(trainer.state.best_metric), 6)
                if trainer.state.best_metric is not None
                else None
            ),
            "mejor_step": mejor_step,
            "best_model_checkpoint": trainer.state.best_model_checkpoint,
        },
        "curvas": curvas,
    }

    adapter_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))
    (adapter_dir / "README.md").write_text(
        generar_model_card_agente(args.agente, metricas, hf_repo=args.hf_repo),
        encoding="utf-8",
    )

    metrics_path = output_dir / "training_metrics.json"
    metrics_path.write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    er.graficar_curva_perdida(
        curvas,
        salida_png=output_dir / "loss_curve.png",
        salida_pdf=output_dir / "loss_curve.pdf",
        mejor_step=mejor_step,
        titulo=f"QLoRA Qwen3-4B ({args.agente.capitalize()}) — Pérdida train y val",
    )

    if not args.skip_smoke_test:
        smoke_tokens = DEFAULTS_POR_AGENTE[args.agente]["smoke_max_new_tokens"]
        smoke = _smoke_test_val_agente(
            model, tokenizer, val_registros, max_new_tokens=smoke_tokens
        )
        (output_dir / "smoke_test_val.json").write_text(
            json.dumps(smoke, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    if args.hf_repo:
        from huggingface_hub import HfApi

        api = HfApi(token=args.hf_token or os.environ.get("HF_TOKEN") or None)
        api.create_repo(repo_id=args.hf_repo, repo_type="model", private=False, exist_ok=True)
        api.upload_folder(
            folder_path=str(adapter_dir),
            repo_id=args.hf_repo,
            repo_type="model",
            commit_message=(
                f"Upload QLoRA {args.agente} adapter (best eval_loss="
                f"{metricas['resultados']['mejor_eval_loss']} @ step {mejor_step})"
            ),
        )
        metricas["hf_url"] = f"https://huggingface.co/{args.hf_repo}"
        metrics_path.write_text(
            json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return metricas


def construir_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Entrena un adaptador QLoRA independiente para un agente específico."
    )
    p.add_argument(
        "--agente",
        required=True,
        choices=sorted(DEFAULTS_POR_AGENTE.keys()),
        help="Agente a entrenar (`enrutador`, `recuperador`, `verificador`, `redactor`).",
    )
    p.add_argument("--modelo-base", default=er.MODELO_BASE_DEFAULT)
    p.add_argument("--train-jsonl", type=Path, default=None)
    p.add_argument("--val-jsonl", type=Path, default=None)
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--max-seq-length", type=int, default=None)
    p.add_argument("--lora-r", type=int, default=16)
    p.add_argument("--lora-alpha", type=int, default=32)
    p.add_argument("--lora-dropout", type=float, default=0.05)
    p.add_argument(
        "--target-modules", nargs="+", default=list(er.LORA_TARGET_MODULES_DEFAULT)
    )
    p.add_argument("--epochs", type=float, default=None)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--grad-accum", type=int, default=None)
    p.add_argument("--learning-rate", type=float, default=None)
    p.add_argument("--lr-scheduler-type", default="cosine")
    p.add_argument("--warmup-ratio", type=float, default=0.10)
    p.add_argument("--weight-decay", type=float, default=0.01)
    p.add_argument("--logging-steps", type=int, default=5)
    p.add_argument("--eval-steps", type=int, default=None)
    p.add_argument("--save-steps", type=int, default=None)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--skip-smoke-test", action="store_true")
    p.add_argument("--hf-repo", default=None)
    p.add_argument("--hf-token", default=None)
    return p


def resolver_args_con_defaults(args: argparse.Namespace) -> argparse.Namespace:
    """Completa argumentos opcionales usando los defaults calibrados para `args.agente`."""
    d = DEFAULTS_POR_AGENTE[args.agente]
    for campo in (
        "train_jsonl",
        "val_jsonl",
        "output_dir",
        "max_seq_length",
        "epochs",
        "batch_size",
        "grad_accum",
        "learning_rate",
        "eval_steps",
        "save_steps",
    ):
        if getattr(args, campo) is None:
            setattr(args, campo, d[campo])
    return args


def main(argv: list[str] | None = None) -> int:
    parser = construir_arg_parser()
    args = resolver_args_con_defaults(parser.parse_args(argv))
    metricas = entrenar_agente(args)
    res = metricas["resultados"]
    print(
        f"[{args.agente}] Completado en {res['tiempo_entrenamiento_min']} min | "
        f"eval_loss inicial={res['eval_loss_inicial']} -> mejor={res['mejor_eval_loss']} (step {res['mejor_step']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
