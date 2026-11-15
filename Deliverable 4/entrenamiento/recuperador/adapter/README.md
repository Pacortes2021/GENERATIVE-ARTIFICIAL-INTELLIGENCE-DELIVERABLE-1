# Adaptador QLoRA — Agente `recuperador` (Exp. Multi-LoRA UdeC)

- **Modelo base:** `Qwen/Qwen3-4B`
- **Agente entrenado:** `recuperador`
- **Método:** `QLoRA (4-bit NF4 + doble cuantización)` (`r=16`, `alpha=32`, `dropout=0.05`)
- **Dataset:** `230` train / `39` val (`completion_only_loss=True`, truncados train=`0`, val=`0`)
- **Hardware:** `NVIDIA A100-SXM4-40GB` (`torch.bfloat16`), tiempo `10.43 min`
- **Evaluación:** `eval_loss` `1.729132` → mejor **`0.18581`** (step `117`)
