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
  - rag
  - multi-agent
  - academic-regulations
---

# Adaptador LoRA del Agente Redactor — Deliverable 4 (IA Generativa UdeC)

Adaptador QLoRA entrenado exclusivamente para el agente **Redactor** del sistema multi-agente de 4 agentes de los Deliverables 3 y 4 sobre normativa académica de pregrado de la Universidad de Concepción / Facultad de Ingeniería (`RI-FI`, `RG`, `Calendario 2026`). Los agentes `Enrutador`, `Recuperador` y `Verificador` conservan los pesos base de `Qwen/Qwen3-4B` sin modificar.

## Resumen de entrenamiento

- **Modelo base:** `Qwen/Qwen3-4B` (cuantización 4-bit NF4 con doble cuantización)
- **Dataset:** `180` pares de entrenamiento y `30` de validación, separados sin fuga de las 75 preguntas de evaluación D3
- **Método:** QLoRA (`r=16`, `alpha=32`, `dropout=0.05`, módulos `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj`)
- **Pérdida enmascarada:** solo sobre los tokens generados por el asistente (`labels = -100` en el prompt de entrada) con plantilla `enable_thinking=False`
- **Hardware:** `Tesla T4` (`15.64 GB` VRAM, cómputo `torch.float16`)
- **Tiempo total:** `52.38 min` (`90` pasos totales, `3.0` épocas)
- **Pérdida inicial vs final (val):** `1.600629` → mejor `eval_loss` = `0.516354` (step `90`)

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
tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
base = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", quantization_config=bnb, device_map="auto")
model = PeftModel.from_pretrained(base, "Pablox0333/qwen3-4b-redactor-udec-d4")
model.eval()
```
