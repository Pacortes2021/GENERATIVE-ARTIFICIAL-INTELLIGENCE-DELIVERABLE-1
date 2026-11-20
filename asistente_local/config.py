"""Configuración centralizada del asistente local UdeC."""

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTES_D3_DIR = REPO_ROOT / "Deliverable 3" / "Deliverable3" / "agentes"
DEFAULT_CORPUS_PATH = AGENTES_D3_DIR / "corpus.json"
DEFAULT_FRAGMENTOS_PATH = AGENTES_D3_DIR / "fragmentos_busqueda.json"
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "udec_asistente_local"


@dataclass(frozen=True)
class ConfigAsistente:
    """Parámetros de ejecución del asistente local sobre Ollama."""

    ollama_url: str = "http://localhost:11434"
    modelo: str = "qwen3:4b-instruct"
    modelo_embeddings: str = "intfloat/multilingual-e5-small"
    corpus_path: Path = DEFAULT_CORPUS_PATH
    fragmentos_path: Path = DEFAULT_FRAGMENTOS_PATH
    cache_dir: Path = DEFAULT_CACHE_DIR
    temperature: float = 0.0
    max_pasos: int = 6
    num_ctx: int = 4096
    timeout_s: int = 120
    usar_embeddings: bool = True
    desactivar_thinking: bool = True
