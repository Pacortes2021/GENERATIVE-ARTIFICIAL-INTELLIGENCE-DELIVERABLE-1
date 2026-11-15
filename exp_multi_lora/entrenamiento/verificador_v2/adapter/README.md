# Adaptador QLoRA — Agente `verificador_v2` (Exp. Multi-LoRA UdeC)

- **Modelo base:** `Qwen/Qwen3-4B`
- **Agente entrenado:** `verificador_v2`
- **Método:** `QLoRA (4-bit NF4 + doble cuantización)` (`r=16`, `alpha=32`, `dropout=0.1`)
- **Dataset:** `389` train / `74` val (`completion_only_loss=True`, truncados train=`0`, val=`0`)
- **Hardware:** `NVIDIA A100-SXM4-40GB` (`torch.bfloat16`), tiempo `14.34 min`
- **Evaluación:** `eval_loss` `2.739193` → mejor **`0.264956`** (step `130`)
