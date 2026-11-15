# Adaptador QLoRA — Agente `enrutador` (Exp. Multi-LoRA UdeC)

- **Modelo base:** `Qwen/Qwen3-4B`
- **Agente entrenado:** `enrutador`
- **Método:** `QLoRA (4-bit NF4 + doble cuantización)` (`r=16`, `alpha=32`, `dropout=0.05`)
- **Dataset:** `210` train / `36` val (`completion_only_loss=True`, truncados train=`0`, val=`0`)
- **Hardware:** `NVIDIA A100-SXM4-40GB` (`torch.bfloat16`), tiempo `9.88 min`
- **Evaluación:** `eval_loss` `1.066113` → mejor **`0.122786`** (step `80`)
