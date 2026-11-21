"""Persistencia local de conversaciones y exportación a Markdown."""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

from .config import DEFAULT_CACHE_DIR

DEFAULT_CHATS_DIR = DEFAULT_CACHE_DIR / "chats"


def _sanitizar_chat_id(chat_id: str) -> str:
    limpio = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(chat_id or "").strip()).strip("_")
    return limpio or "chat_default"


def generar_titulo_chat(mensajes: list[dict[str, Any]]) -> str:
    """Construye un título corto a partir de la primera pregunta del usuario."""
    for m in mensajes:
        if m.get("role") == "user" and str(m.get("content", "")).strip():
            txt = re.sub(r"\s+", " ", str(m["content"]).strip())
            return txt if len(txt) <= 58 else txt[:55].rstrip() + "..."
    return "Nueva conversación"


def guardar_chat(
    chat_id: str,
    mensajes: list[dict[str, Any]],
    titulo: str | None = None,
    base_dir: Path | None = None,
) -> Path:
    """Guarda en disco una conversación completa incluyendo metadatos de trazabilidad."""
    carpeta = Path(base_dir) if base_dir is not None else DEFAULT_CHATS_DIR
    carpeta.mkdir(parents=True, exist_ok=True)
    cid = _sanitizar_chat_id(chat_id)
    ruta = carpeta / f"{cid}.json"
    ahora = dt.datetime.now().isoformat(timespec="seconds")
    payload = {
        "id": cid,
        "titulo": titulo or generar_titulo_chat(mensajes),
        "actualizado_en": ahora,
        "mensajes": mensajes,
    }
    ruta.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ruta


def listar_chats(base_dir: Path | None = None) -> list[dict[str, Any]]:
    """Lista las conversaciones guardadas ordenadas de la más reciente a la más antigua."""
    carpeta = Path(base_dir) if base_dir is not None else DEFAULT_CHATS_DIR
    if not carpeta.is_dir():
        return []
    chats: list[dict[str, Any]] = []
    for p in carpeta.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("id"):
                chats.append(data)
        except Exception:
            continue
    chats.sort(key=lambda c: str(c.get("actualizado_en", "")), reverse=True)
    return chats


def cargar_chat(chat_id: str, base_dir: Path | None = None) -> dict[str, Any] | None:
    """Carga una conversación guardada por ID o devuelve None si no existe."""
    carpeta = Path(base_dir) if base_dir is not None else DEFAULT_CHATS_DIR
    ruta = carpeta / f"{_sanitizar_chat_id(chat_id)}.json"
    if not ruta.is_file():
        return None
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except Exception:
        return None


def eliminar_chat(chat_id: str, base_dir: Path | None = None) -> bool:
    """Elimina un archivo de conversación guardado si existe."""
    carpeta = Path(base_dir) if base_dir is not None else DEFAULT_CHATS_DIR
    ruta = carpeta / f"{_sanitizar_chat_id(chat_id)}.json"
    if ruta.is_file():
        ruta.unlink()
        return True
    return False


def exportar_chat_markdown(
    mensajes: list[dict[str, Any]],
    titulo: str = "Consulta Asistente Normativa UdeC",
) -> str:
    """Genera un documento Markdown limpio con preguntas, respuestas, herramientas y fuentes."""
    lineas = [f"# {titulo}", ""]
    for msg in mensajes:
        rol = msg.get("role")
        contenido = str(msg.get("content", "")).strip()
        if rol == "user":
            lineas.extend([f"## Pregunta", "", contenido, ""])
        elif rol == "assistant":
            lineas.extend([f"### Respuesta", "", contenido, ""])
            meta = msg.get("meta") or {}
            if meta.get("modelo"):
                lineas.append(
                    f"*Modelo: `{meta['modelo']}` · Tiempo: {meta.get('segundos', '-')}s · Llamadas: {meta.get('turnos', '-')}*"
                )
                lineas.append("")
            tools = meta.get("herramientas") or []
            if tools:
                lineas.append("**Herramientas ejecutadas:**")
                for t in tools:
                    lineas.append(f"- `{t.get('nombre')}({t.get('argumentos')})`")
                lineas.append("")
            fuentes = meta.get("fuentes") or []
            if fuentes:
                lineas.append("**Fuentes consultadas:**")
                for f in fuentes:
                    resumen = re.sub(r"\s+", " ", str(f.get("texto", ""))).strip()
                    if len(resumen) > 260:
                        resumen = resumen[:257] + "..."
                    lineas.append(f"- **`[{f.get('id')}]`**: {resumen}")
                lineas.append("")
            lineas.extend(["---", ""])
    return "\n".join(lineas).rstrip() + "\n"
