# Índice de `Deliverable 4/entrenamiento/`

Esta carpeta agrupa los artefactos de entrenamiento QLoRA de los tres adaptadores oficiales y su manifiesto de publicación en Hugging Face.

## 1. Artefactos conjuntos (`3-LoRA`)
- **Manifiesto oficial HF (revisiones y hashes SHA-256 verificados):** [`manifest_adaptadores_hf.json`](manifest_adaptadores_hf.json)
- **Curva consolidada de los 3 roles (en el PDF técnico):** [`loss_curves_3agentes.pdf`](loss_curves_3agentes.pdf) / [`loss_curves_3agentes.png`](loss_curves_3agentes.png)

## 2. Artefactos por rol
- **Enrutador (`A100 bf16`, `210` train / `36` val):** [`enrutador/`](enrutador/) (`training_metrics.json`, `loss_curve.{png,pdf}`, `smoke_test_val.json`, `adapter/README.md`)
- **Recuperador (`A100 bf16`, `230` train / `39` val):** [`recuperador/`](recuperador/) (`training_metrics.json`, `loss_curve.{png,pdf}`, `smoke_test_val.json`, `adapter/README.md`)
- **Redactor (`T4 fp16`, `180` train / `30` val — ubicado en la raíz por continuidad histórica de D4 paso 3):** [`training_metrics.json`](training_metrics.json), [`loss_curve.png`](loss_curve.png), [`loss_curve.pdf`](loss_curve.pdf), [`smoke_test_val.json`](smoke_test_val.json), [`adapter/README.md`](adapter/README.md) *(nota: esa Model Card inicial se escribió antes de añadir los LoRAs de Enrutador y Recuperador; en la arquitectura final `3-LoRA` solo el Verificador conserva pesos Base)*.
