"""Publica en Hugging Face los adaptadores entrenados de `enrutador` y `recuperador`.

Pensado para ejecutarse en Google Colab (con Drive montado) o en local donde estén
guardados `adapter_model.safetensors` y `adapter_config.json`, sin reentrenar modelos:
1. Valida que existan los pesos reales del adaptador (`adapter_model.safetensors`)
   y calcula sus hashes SHA-256 locales ANTES de subirlos.
2. Genera la Model Card YAML (`README.md`) con `base_model: Qwen/Qwen3-4B` y `library_name: peft`.
3. Sube la carpeta `adapter/` al repositorio público en Hugging Face Hub y captura `hf_revision`.
4. Verifica que el SHA-256 en Hugging Face (`get_paths_info` / descarga) coincida byte a byte.
5. Actualiza `training_metrics.json`, `adapter/README.md` y `manifest_adaptadores_hf.json`
   con saltos de línea LF garantizados.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

D4_DIR = Path(__file__).resolve().parents[1]
D4_SCRIPTS_DIR = D4_DIR / "scripts"
D4_TRAIN_DIR = D4_DIR / "entrenamiento"
DEFAULT_MANIFEST_PATH = D4_TRAIN_DIR / "manifest_adaptadores_hf.json"

if str(D4_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(D4_SCRIPTS_DIR))

from entrenar_agente import DEFAULTS_POR_AGENTE, generar_model_card_agente  # noqa: E402

DEFAULT_DRIVE_ENTRENAMIENTO = Path("/content/drive/MyDrive/UdeC_GenIA_Exp_MultiLoRA/entrenamiento")


def _escribir_texto_lf(path: Path, contenido: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(contenido)


def _escribir_json_lf(path: Path, payload: Any) -> None:
    _escribir_texto_lf(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def calcular_sha256_archivo(path: Path) -> str:
    """Calcula el SHA-256 hexadecimal en bloques para archivos binarios grandes."""
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def obtener_hashes_adapter(adapter_dir: Path) -> dict[str, Any]:
    """Devuelve SHA-256 y tamaño de los archivos críticos de un adaptador PEFT."""
    pesos_path = Path(adapter_dir) / "adapter_model.safetensors"
    cfg_path = Path(adapter_dir) / "adapter_config.json"
    if not pesos_path.is_file() or not cfg_path.is_file():
        raise FileNotFoundError(
            f"Faltan `adapter_model.safetensors` o `adapter_config.json` en {adapter_dir}"
        )
    return {
        "adapter_model_sha256": calcular_sha256_archivo(pesos_path),
        "adapter_model_bytes": pesos_path.stat().st_size,
        "adapter_config_sha256": calcular_sha256_archivo(cfg_path),
    }


def _verificar_sha256_en_hf(
    api: Any,
    hf_repo: str,
    revision: str | None,
    expected_sha256: str,
    token: str | None = None,
) -> str:
    """Confirma que `adapter_model.safetensors` en HF coincide con `expected_sha256`."""
    remoto_sha: str | None = None
    try:
        infos = api.get_paths_info(
            repo_id=hf_repo,
            paths=["adapter_model.safetensors"],
            revision=revision,
            repo_type="model",
        )
        for info in infos:
            lfs = getattr(info, "lfs", None)
            if lfs is not None and getattr(lfs, "sha256", None):
                remoto_sha = str(lfs.sha256)
                break
    except Exception:
        remoto_sha = None

    if not remoto_sha:
        from huggingface_hub import hf_hub_download

        with tempfile.TemporaryDirectory() as tmp:
            dl = hf_hub_download(
                repo_id=hf_repo,
                filename="adapter_model.safetensors",
                revision=revision,
                repo_type="model",
                cache_dir=tmp,
                force_download=True,
                token=token,
            )
            remoto_sha = calcular_sha256_archivo(Path(dl))

    if remoto_sha.lower() != expected_sha256.lower():
        raise RuntimeError(
            f"SHA-256 en Hugging Face ({remoto_sha}) NO coincide con el adaptador local "
            f"({expected_sha256}) para {hf_repo} @ {revision}"
        )
    return remoto_sha


def actualizar_manifest_hf(
    rol: str,
    info_rol: dict[str, Any],
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
) -> dict[str, Any]:
    """Actualiza el manifiesto versionado con repo, revisión y SHA-256 de cada rol."""
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"version": "d4_3lora_manifest_v1", "modelo_base": "Qwen/Qwen3-4B", "adaptadores": {}}
    adaptadores = manifest.setdefault("adaptadores", {})
    prev = dict(adaptadores.get(rol, {}))
    prev.update(info_rol)
    adaptadores[rol] = prev
    _escribir_json_lf(manifest_path, manifest)
    return manifest


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
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
) -> dict[str, Any]:
    """Calcula SHA-256, sube `adapter_dir` a HF, verifica hash remoto y actualiza D4."""
    from huggingface_hub import HfApi

    metrics_path = D4_TRAIN_DIR / rol / "training_metrics.json"
    if not metrics_path.is_file():
        raise FileNotFoundError(f"Falta {metrics_path}")
    metricas = json.loads(metrics_path.read_text(encoding="utf-8"))

    hashes = obtener_hashes_adapter(adapter_dir)
    readme_txt = generar_model_card_agente(rol, metricas, hf_repo=hf_repo)
    _escribir_texto_lf(adapter_dir / "README.md", readme_txt)
    _escribir_texto_lf(D4_TRAIN_DIR / rol / "adapter" / "README.md", readme_txt)

    tok_efectivo = token or os.environ.get("HF_TOKEN") or None
    api = HfApi(token=tok_efectivo)
    api.create_repo(repo_id=hf_repo, repo_type="model", private=private, exist_ok=True)
    res_meta = metricas.get("resultados", {})
    commit_info = api.upload_folder(
        folder_path=str(adapter_dir),
        repo_id=hf_repo,
        repo_type="model",
        commit_message=(
            f"Upload QLoRA {rol} adapter D4 (best eval_loss="
            f"{res_meta.get('mejor_eval_loss')} @ step {res_meta.get('mejor_step')}; "
            f"sha256={hashes['adapter_model_sha256'][:12]})"
        ),
    )
    revision = getattr(commit_info, "oid", None) or getattr(api.model_info(hf_repo), "sha", None)
    sha_verificado = _verificar_sha256_en_hf(
        api,
        hf_repo=hf_repo,
        revision=revision,
        expected_sha256=hashes["adapter_model_sha256"],
        token=tok_efectivo,
    )

    metricas["hf_repo"] = HF_REPO_NORM = hf_repo
    metricas["hf_url"] = f"https://huggingface.co/{HF_REPO_NORM}"
    if revision:
        metricas["hf_revision"] = revision
    metricas["adapter_model_sha256"] = sha_verificado
    metricas["adapter_model_bytes"] = hashes["adapter_model_bytes"]
    metricas["adapter_config_sha256"] = hashes["adapter_config_sha256"]
    _escribir_json_lf(metrics_path, metricas)

    registro_manifest = {
        "hf_repo": HF_REPO_NORM,
        "hf_revision": revision,
        "adapter_model_sha256": sha_verificado,
        "adapter_model_bytes": hashes["adapter_model_bytes"],
        "adapter_config_sha256": hashes["adapter_config_sha256"],
        "publicado": True,
    }
    actualizar_manifest_hf(rol, registro_manifest, manifest_path=manifest_path)

    return {
        "rol": rol,
        "hf_repo": HF_REPO_NORM,
        "hf_url": metricas["hf_url"],
        "revision": revision,
        "adapter_model_sha256": sha_verificado,
        "adapter_model_bytes": hashes["adapter_model_bytes"],
    }


def verificar_manifest_en_hf(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    token: str | None = None,
) -> dict[str, Any]:
    """Comprueba en HF Hub todos los roles publicados del manifiesto."""
    from huggingface_hub import HfApi

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tok_efectivo = token or os.environ.get("HF_TOKEN") or None
    api = HfApi(token=tok_efectivo)
    reporte: dict[str, Any] = {}
    for rol, info in manifest.get("adaptadores", {}).items():
        if not info.get("publicado") or not info.get("hf_revision") or not info.get("adapter_model_sha256"):
            reporte[rol] = {"verificado": False, "motivo": "pendiente_publicacion"}
            continue
        sha_rem = _verificar_sha256_en_hf(
            api,
            hf_repo=info["hf_repo"],
            revision=info["hf_revision"],
            expected_sha256=info["adapter_model_sha256"],
            token=tok_efectivo,
        )
        reporte[rol] = {
            "verificado": True,
            "hf_repo": info["hf_repo"],
            "hf_revision": info["hf_revision"],
            "adapter_model_sha256": sha_rem,
        }
    return reporte


def construir_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Publica adaptadores Enrutador y Recuperador D4 desde Drive/local a Hugging Face con verificación SHA-256."
    )
    p.add_argument("--hf-username", default="Pablox0333")
    p.add_argument(
        "--roles",
        default="enrutador,recuperador",
        help="Roles a subir separados por coma (ej. `enrutador,recuperador`).",
    )
    p.add_argument("--drive-dir", type=Path, default=DEFAULT_DRIVE_ENTRENAMIENTO)
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    p.add_argument("--hf-token", default=None)
    p.add_argument("--private", action="store_true")
    p.add_argument(
        "--verificar-manifest",
        action="store_true",
        help="Solo verifica en Hugging Face los hashes registrados en manifest_adaptadores_hf.json.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_arg_parser().parse_args(argv)
    if args.verificar_manifest:
        rep = verificar_manifest_en_hf(args.manifest, token=args.hf_token)
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return 0

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
            manifest_path=args.manifest,
        )
        resultados.append(info)
        print(
            f"OK [{rol}] -> {info['hf_url']} @ {info['revision']} "
            f"| sha256={info['adapter_model_sha256']}"
        )
    print(json.dumps(resultados, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
