"""Script reproducible de fine-tuning QLoRA para el agente Redactor (Paso 3).

Entrena un adaptador LoRA sobre `Qwen/Qwen3-4B` (NF4, 4-bit) usando los pares
supervisados de `Deliverable 4/datos/redactor_train.jsonl` (180) y
`redactor_val.jsonl` (30), replicando exactamente el chat template de
inferencia (`enable_thinking=False`) de Deliverable 3 y calculando la pérdida
únicamente sobre los tokens generados por el asistente (`labels = -100` en el
prompt de usuario).

Uso típico en Colab GPU (T4 16GB o superior):
    python "Deliverable 4/scripts/entrenar_redactor.py" \
        --output-dir "Deliverable 4/entrenamiento" \
        --hf-repo "<usuario>/qwen3-4b-redactor-udec-d4"

Para regenerar solo el gráfico desde un `training_metrics.json` existente:
    python3 "Deliverable 4/scripts/entrenar_redactor.py" \
        --plot-only "Deliverable 4/entrenamiento/training_metrics.json"
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import random
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DELIVERABLE4_DIR = REPO_ROOT / "Deliverable 4"
DEFAULT_TRAIN_JSONL = DELIVERABLE4_DIR / "datos" / "redactor_train.jsonl"
DEFAULT_VAL_JSONL = DELIVERABLE4_DIR / "datos" / "redactor_val.jsonl"
DEFAULT_OUTPUT_DIR = DELIVERABLE4_DIR / "entrenamiento"

MODELO_BASE_DEFAULT = "Qwen/Qwen3-4B"
LORA_TARGET_MODULES_DEFAULT: tuple[str, ...] = (
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
)
SMOKE_TEST_VAL_IDS: tuple[str, ...] = ("B1-V01", "B4-V01", "B6-V05")


def sha256_archivo(path: Path) -> str:
    """Calcula el digest SHA-256 hexadecimal de un archivo."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def cargar_jsonl(path: Path) -> list[dict[str, Any]]:
    """Lee un archivo JSONL en UTF-8 ignorando líneas vacías."""
    lineas = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [json.loads(l) for l in lineas]


def formatear_prompt_usuario(tokenizer: Any, user_content: str) -> str:
    """Aplica exactamente la plantilla de chat usada en D3 (`enable_thinking=False`)."""
    msgs = [{"role": "user", "content": user_content}]
    try:
        return tokenizer.apply_chat_template(
            msgs,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            msgs,
            tokenize=False,
            add_generation_prompt=True,
        )


def construir_ejemplo_sft(
    registro: dict[str, Any],
    tokenizer: Any,
    max_seq_length: int = 4096,
) -> dict[str, Any]:
    """Tokeniza un par user/assistant enmascarando el prompt con `labels = -100`."""
    msgs = registro["messages"]
    if len(msgs) != 2 or msgs[0]["role"] != "user" or msgs[1]["role"] != "assistant":
        raise ValueError(f"{registro.get('id')}: se esperaban exactamente 2 mensajes user/assistant")

    prompt_text = formatear_prompt_usuario(tokenizer, msgs[0]["content"])
    eos = tokenizer.eos_token or ""
    target_text = msgs[1]["content"] + eos

    prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    target_ids = tokenizer(target_text, add_special_tokens=False)["input_ids"]

    input_ids = list(prompt_ids) + list(target_ids)
    labels = [-100] * len(prompt_ids) + list(target_ids)
    truncado = len(input_ids) > max_seq_length

    if truncado:
        input_ids = input_ids[:max_seq_length]
        labels = labels[:max_seq_length]
        if not any(tok != -100 for tok in labels):
            raise ValueError(
                f"{registro.get('id')}: el prompt ({len(prompt_ids)} tokens) excede "
                f"max_seq_length={max_seq_length} y no deja tokens supervisados"
            )

    return {
        "id": registro["id"],
        "input_ids": input_ids,
        "attention_mask": [1] * len(input_ids),
        "labels": labels,
        "prompt_tokens": len(prompt_ids),
        "target_tokens": len(target_ids),
        "total_tokens": len(input_ids),
        "truncado": truncado,
    }


def resumen_longitudes_sft(ejemplos: list[dict[str, Any]]) -> dict[str, Any]:
    """Resume longitudes reales en tokens para diagnóstico previo al entrenamiento."""
    totales = [e["total_tokens"] for e in ejemplos]
    prompts = [e["prompt_tokens"] for e in ejemplos]
    targets = [e["target_tokens"] for e in ejemplos]
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
        "prompt_tokens_promedio": round(sum(prompts) / len(prompts), 1),
        "target_tokens_promedio": round(sum(targets) / len(targets), 1),
    }


class DataCollatorParaCompletado:
    """Aplica padding derecho uniforme para `input_ids`, `attention_mask` y `labels`."""

    def __init__(self, pad_token_id: int) -> None:
        self.pad_token_id = int(pad_token_id)

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, Any]:
        import torch

        max_len = max(len(f["input_ids"]) for f in features)
        batch_ids: list[list[int]] = []
        batch_mask: list[list[int]] = []
        batch_labels: list[list[int]] = []
        for f in features:
            pad_n = max_len - len(f["input_ids"])
            batch_ids.append(list(f["input_ids"]) + [self.pad_token_id] * pad_n)
            batch_mask.append(list(f["attention_mask"]) + [0] * pad_n)
            batch_labels.append(list(f["labels"]) + [-100] * pad_n)

        return {
            "input_ids": torch.tensor(batch_ids, dtype=torch.long),
            "attention_mask": torch.tensor(batch_mask, dtype=torch.long),
            "labels": torch.tensor(batch_labels, dtype=torch.long),
        }


def extraer_curvas_de_log_history(
    log_history: list[dict[str, Any]],
    eval_inicial: dict[str, Any] | None = None,
) -> dict[str, list[dict[str, float | int]]]:
    """Extrae series limpias de `train_loss` y `eval_loss` desde Trainer.state.log_history."""
    train_por_step: dict[int, dict[str, float | int]] = {}
    eval_por_step: dict[int, dict[str, float | int]] = {}

    if eval_inicial is not None and "eval_loss" in eval_inicial:
        eval_por_step[0] = {
            "step": 0,
            "epoch": 0.0,
            "eval_loss": round(float(eval_inicial["eval_loss"]), 6),
        }

    for entry in log_history:
        step = int(entry.get("step", 0))
        epoch = round(float(entry.get("epoch", 0.0)), 4)
        if "loss" in entry:
            train_por_step[step] = {
                "step": step,
                "epoch": epoch,
                "loss": round(float(entry["loss"]), 6),
                "learning_rate": float(entry.get("learning_rate", 0.0)),
            }
        if "eval_loss" in entry:
            eval_por_step[step] = {
                "step": step,
                "epoch": epoch,
                "eval_loss": round(float(entry["eval_loss"]), 6),
            }

    return {
        "train": [train_por_step[s] for s in sorted(train_por_step)],
        "eval": [eval_por_step[s] for s in sorted(eval_por_step)],
    }


def graficar_curva_perdida(
    curvas: dict[str, list[dict[str, Any]]],
    salida_png: Path,
    salida_pdf: Path | None = None,
    mejor_step: int | None = None,
    titulo: str = "QLoRA Qwen3-4B (Redactor D4) — Pérdida de entrenamiento y validación",
) -> None:
    """Genera gráfico PNG y PDF listo para el informe técnico."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    train_pts = curvas.get("train", [])
    eval_pts = curvas.get("eval", [])
    if not train_pts and not eval_pts:
        raise ValueError("No hay puntos de pérdida para graficar.")

    fig, ax = plt.subplots(figsize=(6.8, 3.6), dpi=300)

    if train_pts:
        ax.plot(
            [p["step"] for p in train_pts],
            [p["loss"] for p in train_pts],
            marker="o",
            markersize=3.5,
            linewidth=1.8,
            color="#1f4e79",
            label="Entrenamiento (train_loss)",
        )
    if eval_pts:
        ax.plot(
            [p["step"] for p in eval_pts],
            [p["eval_loss"] for p in eval_pts],
            marker="s",
            markersize=4.5,
            linewidth=2.0,
            color="#c0392b",
            label="Validación (eval_loss, n=30)",
        )

    if mejor_step is not None:
        ax.axvline(
            mejor_step,
            linestyle="--",
            linewidth=1.2,
            color="#2c7a4b",
            label=f"Mejor checkpoint (step {mejor_step})",
        )

    ax.set_title(titulo, fontsize=10.5, fontweight="bold", pad=8)
    ax.set_xlabel("Paso de optimización (step)", fontsize=9.5)
    ax.set_ylabel("Cross-Entropy Loss", fontsize=9.5)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(frameon=True, fontsize=8.5, loc="upper right")
    fig.tight_layout()

    salida_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida_png, dpi=300, bbox_inches="tight")
    if salida_pdf is not None:
        salida_pdf.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(salida_pdf, bbox_inches="tight")
    plt.close(fig)


def generar_model_card(
    metricas: dict[str, Any],
    hf_repo: str | None = None,
) -> str:
    """Construye el `README.md` (Model Card) del adaptador LoRA en Hugging Face."""
    modelo_base = metricas["modelo_base"]
    hp = metricas["hiperparametros"]
    hw = metricas["hardware"]
    res = metricas["resultados"]
    repo_mostrar = hf_repo or "<usuario>/qwen3-4b-redactor-udec-d4"

    return f"""---
base_model: {modelo_base}
library_name: peft
license: apache-2.0
language:
  - es
tags:
  - qlora
  - lora
  - peft
  - qwen3
  - rag
  - multi-agent
  - academic-regulations
---

# Adaptador LoRA del Agente Redactor — Deliverable 4 (IA Generativa UdeC)

Adaptador QLoRA entrenado exclusivamente para el agente **Redactor** del sistema multi-agente de 4 agentes de los Deliverables 3 y 4 sobre normativa académica de pregrado de la Universidad de Concepción / Facultad de Ingeniería (`RI-FI`, `RG`, `Calendario 2026`). Los agentes `Enrutador`, `Recuperador` y `Verificador` conservan los pesos base de `{modelo_base}` sin modificar.

## Resumen de entrenamiento

- **Modelo base:** `{modelo_base}` (cuantización 4-bit NF4 con doble cuantización)
- **Dataset:** `{metricas['datos']['train_ejemplos']}` pares de entrenamiento y `{metricas['datos']['val_ejemplos']}` de validación, separados sin fuga de las 75 preguntas de evaluación D3
- **Método:** QLoRA (`r={hp['lora_r']}`, `alpha={hp['lora_alpha']}`, `dropout={hp['lora_dropout']}`, módulos `{', '.join(hp['target_modules'])}`)
- **Pérdida enmascarada:** solo sobre los tokens generados por el asistente (`labels = -100` en el prompt de entrada) con plantilla `enable_thinking=False`
- **Hardware:** `{hw['gpu']}` (`{hw['vram_gb']} GB` VRAM, cómputo `{hw['compute_dtype']}`)
- **Tiempo total:** `{res['tiempo_entrenamiento_min']} min` (`{res['pasos_totales']}` pasos totales, `{hp['epochs']}` épocas)
- **Pérdida inicial vs final (val):** `{res.get('eval_loss_inicial')}` → mejor `eval_loss` = `{res.get('mejor_eval_loss')}` (step `{res.get('mejor_step')}`)

## Carga rápida con PEFT

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
tok = AutoTokenizer.from_pretrained("{modelo_base}")
base = AutoModelForCausalLM.from_pretrained("{modelo_base}", quantization_config=bnb, device_map="auto")
model = PeftModel.from_pretrained(base, "{repo_mostrar}")
model.eval()
```
"""


def es_bf16_nativo(capability: tuple[int, int], bf16_supported: bool) -> bool:
    """Usa bf16 solo en GPUs Ampere+ (sm_80+); Turing (T4) calcula en fp16 nativo."""
    return bool(bf16_supported and capability[0] >= 8)


def _resolver_versiones() -> dict[str, str]:
    paquetes = (
        "torch",
        "transformers",
        "peft",
        "bitsandbytes",
        "accelerate",
        "huggingface_hub",
    )
    out: dict[str, str] = {}
    for p in paquetes:
        try:
            out[p] = importlib.metadata.version(p)
        except importlib.metadata.PackageNotFoundError:
            out[p] = "no_instalado"
    return out


def _ejecutar_smoke_test_val(
    model: Any,
    tokenizer: Any,
    val_registros: list[dict[str, Any]],
    val_ids: tuple[str, ...] = SMOKE_TEST_VAL_IDS,
    max_new_tokens: int = 900,
) -> list[dict[str, Any]]:
    """Compara rápidamente modelo base vs adaptador en ejemplos reservados de validación."""
    import torch

    por_id = {r["id"]: r for r in val_registros}
    seleccion = [por_id[i] for i in val_ids if i in por_id]
    resultados: list[dict[str, Any]] = []

    model.config.use_cache = True
    model.eval()

    def _generar_uno(prompt_text: str) -> str:
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
        prompt_text = formatear_prompt_usuario(tokenizer, reg["messages"][0]["content"])
        with model.disable_adapter():
            salida_base = _generar_uno(prompt_text)
        salida_ft = _generar_uno(prompt_text)
        resultados.append(
            {
                "id": reg["id"],
                "bloque": reg["bloque"],
                "modo": reg["modo"],
                "estado": reg["estado"],
                "esperado": reg["messages"][1]["content"],
                "salida_base": salida_base,
                "salida_finetuned": salida_ft,
            }
        )
    return resultados


def entrenar(args: argparse.Namespace) -> dict[str, Any]:
    """Ejecuta el entrenamiento completo QLoRA en GPU y guarda todos los artefactos."""
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
            "Se requiere GPU CUDA (por ejemplo Google Colab T4/L4/A100) para ejecutar QLoRA. "
            "Usa D4_colab_entrenamiento.ipynb en Colab."
        )

    random.seed(args.seed)
    set_seed(args.seed)

    train_registros = cargar_jsonl(args.train_jsonl)
    val_registros = cargar_jsonl(args.val_jsonl)

    tokenizer = AutoTokenizer.from_pretrained(args.modelo_base)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_sft = [
        construir_ejemplo_sft(r, tokenizer, args.max_seq_length) for r in train_registros
    ]
    val_sft = [
        construir_ejemplo_sft(r, tokenizer, args.max_seq_length) for r in val_registros
    ]

    stats_train = resumen_longitudes_sft(train_sft)
    stats_val = resumen_longitudes_sft(val_sft)

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

    use_bf16 = es_bf16_nativo(
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

    # Garantizar parámetros entrenables en fp32 para evitar fallos de GradScaler con fp16 en T4
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

    collator = DataCollatorParaCompletado(pad_token_id=tokenizer.pad_token_id)
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

    curvas = extraer_curvas_de_log_history(
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
        "modelo_base": args.modelo_base,
        "revision_modelo_base": getattr(model.config, "_commit_hash", None),
        "hf_repo": args.hf_repo,
        "hardware": {
            "gpu": gpu_nombre,
            "vram_gb": vram_gb,
            "compute_dtype": str(compute_dtype),
            "versiones": _resolver_versiones(),
        },
        "datos": {
            "train_jsonl": str(args.train_jsonl),
            "val_jsonl": str(args.val_jsonl),
            "train_sha256": sha256_archivo(args.train_jsonl),
            "val_sha256": sha256_archivo(args.val_jsonl),
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
        generar_model_card(metricas, hf_repo=args.hf_repo),
        encoding="utf-8",
    )

    metrics_path = output_dir / "training_metrics.json"
    metrics_path.write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    png_path = output_dir / "loss_curve.png"
    pdf_path = output_dir / "loss_curve.pdf"
    graficar_curva_perdida(
        curvas,
        salida_png=png_path,
        salida_pdf=pdf_path,
        mejor_step=mejor_step,
    )

    if not args.skip_smoke_test:
        smoke = _ejecutar_smoke_test_val(model, tokenizer, val_registros)
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
                f"Upload QLoRA Redactor D4 adapter (best eval_loss="
                f"{metricas['resultados']['mejor_eval_loss']} @ step {mejor_step})"
            ),
        )
        metricas["hf_url"] = f"https://huggingface.co/{args.hf_repo}"
        metrics_path.write_text(
            json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return metricas


def construir_arg_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos CLI."""
    p = argparse.ArgumentParser(
        description="Entrena adaptador QLoRA para el Redactor (Deliverable 4)."
    )
    p.add_argument("--modelo-base", default=MODELO_BASE_DEFAULT)
    p.add_argument("--train-jsonl", type=Path, default=DEFAULT_TRAIN_JSONL)
    p.add_argument("--val-jsonl", type=Path, default=DEFAULT_VAL_JSONL)
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--max-seq-length", type=int, default=4096)
    p.add_argument("--lora-r", type=int, default=16)
    p.add_argument("--lora-alpha", type=int, default=32)
    p.add_argument("--lora-dropout", type=float, default=0.05)
    p.add_argument(
        "--target-modules", nargs="+", default=list(LORA_TARGET_MODULES_DEFAULT)
    )
    p.add_argument("--epochs", type=float, default=3.0)
    p.add_argument("--batch-size", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=6)
    p.add_argument("--learning-rate", type=float, default=1e-4)
    p.add_argument("--lr-scheduler-type", default="cosine")
    p.add_argument("--warmup-ratio", type=float, default=0.10)
    p.add_argument("--weight-decay", type=float, default=0.01)
    p.add_argument("--logging-steps", type=int, default=5)
    p.add_argument("--eval-steps", type=int, default=15)
    p.add_argument("--save-steps", type=int, default=15)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--skip-smoke-test", action="store_true")
    p.add_argument(
        "--hf-repo",
        default=None,
        help="ID público en Hugging Face (ej. usuario/qwen3-4b-redactor-udec-d4) para subir el adaptador.",
    )
    p.add_argument("--hf-token", default=None)
    p.add_argument(
        "--plot-only",
        type=Path,
        default=None,
        help="Ruta a un training_metrics.json existente para regenerar solo loss_curve.png/pdf.",
    )
    return p


def main() -> None:
    parser = construir_arg_parser()
    args = parser.parse_args()

    if args.plot_only is not None:
        metricas = json.loads(args.plot_only.read_text(encoding="utf-8"))
        out_dir = args.plot_only.parent
        graficar_curva_perdida(
            metricas["curvas"],
            salida_png=out_dir / "loss_curve.png",
            salida_pdf=out_dir / "loss_curve.pdf",
            mejor_step=metricas.get("resultados", {}).get("mejor_step"),
        )
        print(f"Curva regenerada en {out_dir / 'loss_curve.png'} y {out_dir / 'loss_curve.pdf'}")
        return

    metricas = entrenar(args)
    res = metricas["resultados"]
    print(
        f"Entrenamiento completado en {res['tiempo_entrenamiento_min']} min | "
        f"eval_loss inicial={res['eval_loss_inicial']} -> mejor={res['mejor_eval_loss']} (step {res['mejor_step']})"
    )


if __name__ == "__main__":
    main()
