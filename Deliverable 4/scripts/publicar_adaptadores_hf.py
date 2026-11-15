"""Publica en Hugging Face los adaptadores entrenados de `enrutador` y `recuperador`.

Pensado para ejecutarse en Google Colab (con Drive montado) o en local donde estén
guardados `adapter_model.safetensors` y `adapter_config.json`, sin reentrenar modelos:
1. Valida que existan los pesos reales del adaptador (`adapter_model.safetensors`).
2. Genera la Model Card YAML (`README.md`) con `base_model: Qwen/Qwen3-4B` y `library_name: peft`.
3. Sube la carpeta `adapter/` al repositorio público en Hugging Face Hub.
4. Actualiza `training_metrics.json` y `adapter/README.md` locales de `Deliverable 4/entrenamiento/`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

D4_DIR = Path(__file__).resolve().parents[1]
D4_SCRIPTS_DIR = D4_DIR / "scripts"
D4_TRAIN_DIR = D4_DIR / "entrenamiento"

if str(D4_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(D4_SCRIPTS_DIR))

from entrenar_agente import DEFAULTS_POR_AGENTE, generar_model_card_agente  # noqa: E402

DEFAULT_DRIVE_ENTRENAMIENTO = Path("/content/drive/MyDrive/UdeC_GenIA_Exp_MultiLoRA/entrenamiento")


def localizar_carpeta_adapter(
    rol: str,
    drive_dir: Path | None = DEFAULT_DRIVE_ENTRENAMIENTO,
) -> Path:
    """Encuentra la carpeta con `adapter_model.safetensors` en local o en Drive."""
    candidatos = [D4_TRAIN_DIR / rol / "adapter"]
    if drive_dir is not None:
        candidatos.append(drive_dir / rol / "adapter")
    for cand in candidatos:
        if (cand / "adapter_model.safetensors").is_file() and (cand / "adapter_config.json").is_file():
            return cand
    buscados = ", ".join(str(c) for c in candidatos)
    raise FileNotFoundError(
        f"No se encontraron pesos `adapter_model.safetensors` para `{rol}` en: {buscados}"
    )


def publicar_rol(
    rol: str,
    hf_repo: str,
    adapter_dir: Path,
    token: str | None = None,
    private: bool = False,
) -> dict[str, Any]:
    """Genera Model Card, sube `adapter_dir` a HF Hub y actualiza métricas en D4."""
    from huggingface_hub import HfApi

    metrics_path = D4_TRAIN_DIR / rol / "training_metrics.json"
    if not metrics_path.is_file():
        raise FileNotFoundError(f"Falta {metrics_path}")
    metricas = json.loads(metrics_path.read_text(encoding="utf-8"))

    readme_txt = generar_model_card_agente(rol, metricas, hf_repo=hf_repo)
    (adapter_dir / "README.md").write_text(readme_txt, encoding="utf-8")

    local_readme = D4_TRAIN_DIR / rol / "adapter" / "README.md"
    local_readme.parent.mkdir(parents=True, exist_ok=True)
    local_readme.write_text(readme_txt, encoding="utf-8")

    api = HfApi(token=token or os.environ.get("HF_TOKEN") or None)
    api.create_repo(repo_id=hf_repo, repo_type="model", private=private, exist_ok=True)
    res_meta = metricas.get("resultados", {})
    commit_info = api.upload_folder(
        folder_path=str(adapter_dir),
        repo_id=hf_repo,
        repo_type="model",
        commit_message=(
            f"Upload QLoRA {rol} adapter D4 (best eval_loss="
            f"{res_meta.get('mejor_eval_loss')} @ step {res_meta.get('mejor_step')})"
        ),
    )
    revision = getattr(commit_info, "oid", None)

    metricas["hf_repo"] = hf_repo
    metricas["hf_url"] = f"https://huggingface.co/{hf_repo}"
    if revision:
        metricas["hf_revision"] = revision
    metrics_path.write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"rol": rol, "hf_repo": hf_repo, "hf_url": metricas["hf_url"], "revision": revision}


def construir_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Publica adaptadores Enrutador y Recuperador D4 desde Drive/local a Hugging Face."
    )
    p.add_argument("--hf-username", default="Pablox0333")
    p.add_argument(
        "--roles",
        default="enrutador,recuperador",
        help="Roles a subir separados por coma (ej. `enrutador,recuperador`).",
    )
    p.add_argument("--drive-dir", type=Path, default=DEFAULT_DRIVE_ENTRENAMIENTO)
    p.add_argument("--hf-token", default=None)
    p.add_argument("--private", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_arg_parser().parse_args(argv)
    roles = [r.strip().lower() for r in args.roles.split(",") if r.strip()]
    resultados = []
    for rol in roles:
        if rol not in DEFAULTS_POR_AGENTE or rol == "redactor":
            raise ValueError(
                f"Rol inválido para subida incremental: `{rol}`. Válidos: enrutador, recuperador."
            )
        hf_repo = f"{args.hf_username}/qwen3-4b-{rol}-udec-d4"
        adapter_dir = localizar_carpeta_adapter(rol, drive_dir=args.drive_dir)
        info = publicar_rol(
            rol,
            hf_repo=hf_repo,
            adapter_dir=adapter_dir,
            token=args.hf_token,
            private=args.private,
        )
        resultados.append(info)
        print(f"OK [{rol}] -> {info['hf_url']} (commit {info['revision']})")
    print(json.dumps(resultados, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
