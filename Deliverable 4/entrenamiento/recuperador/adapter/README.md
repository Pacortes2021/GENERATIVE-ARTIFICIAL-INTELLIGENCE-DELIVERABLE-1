---
base_model: Qwen/Qwen3-4B
library_name: peft
license: apache-2.0
language:
  - es
tags:
  - qlora
  - lora
  - peft
  - qwen3
  - multi-agent
  - academic-regulations
---

# Adaptador QLoRA — Agente `recuperador` (Deliverable 4 · UdeC)

Adaptador QLoRA del agente **recuperador** dentro del sistema multi-agente de 4 roles (`Enrutador`, `Recuperador`, `Redactor`, `Verificador`) sobre normativa académica de pregrado de la Universidad de Concepción / Facultad de Ingeniería (`RI-FI`, `RG`, `Calendario 2026`). En el entregable final se fine-tunean `Enrutador`, `Recuperador` y `Redactor`, manteniendo `Verificador` con pesos base mediante `model.disable_adapter()`.

## Resumen de entrenamiento

- **Modelo base:** `Qwen/Qwen3-4B`
- **Agente entrenado:** `recuperador`
- **Método:** `QLoRA (4-bit NF4 + doble cuantización)` (`r=16`, `alpha=32`, `dropout=0.05`)
- **Dataset:** `230` train / `39` val (`completion_only_loss=True`, truncados train=`0`, val=`0`)
- **Hardware:** `NVIDIA A100-SXM4-40GB` (`torch.bfloat16`), tiempo `10.43 min` (`117` pasos, `3.0` épocas)
- **Evaluación:** `eval_loss` `1.729132` → mejor **`0.18581`** (step `117`)
- **Hugging Face:** `https://huggingface.co/Pablox0333/qwen3-4b-recuperador-udec-d4`

## Carga rápida con PEFT

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import torch

bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
base = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", quantization_config=bnb, device_map="auto")
model = PeftModel.from_pretrained(base, "Pablox0333/qwen3-4b-recuperador-udec-d4", adapter_name="recuperador")
model.eval()
```
