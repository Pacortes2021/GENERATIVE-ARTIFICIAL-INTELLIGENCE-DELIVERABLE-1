# Adaptador QLoRA — Agente `verificador` (Exp. Multi-LoRA UdeC)

- **Modelo base:** `Qwen/Qwen3-4B`
- **Agente entrenado:** `verificador`
- **Método:** `QLoRA (4-bit NF4 + doble cuantización)` (`r=16`, `alpha=32`, `dropout=0.05`)
- **Dataset:** `305` train / `68` val (`completion_only_loss=True`, truncados train=`0`, val=`0`)
- **Hardware:** `NVIDIA A100-SXM4-40GB` (`torch.bfloat16`), tiempo `15.19 min`
- **Evaluación:** `eval_loss` `2.833926` → mejor **`0.034402`** (step `150`)
