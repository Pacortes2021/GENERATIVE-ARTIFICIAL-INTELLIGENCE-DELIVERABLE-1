"""Módulo de verificación selectiva estilo CRAG / Self-RAG sobre evidencia citada."""

from __future__ import annotations

import json
import re
from typing import Any, Callable

import requests

from .config import ConfigAsistente

_PATRONES_ABSTENCION = (
    "no se especifica",
    "no menciona",
    "no figura en",
    "no contiene",
    "no se encuentra",
    "no hay mención",
)
_PATRONES_MULTI_REQUISITO = (
    "condiciones",
    "requisitos",
    "excepciones",
    "diferencia",
    "cuáles",
    "cuales",
    "procedimiento",
    "ante quién",
    "ante quien",
    "y qué",
    "y que",
)


def necesita_revision_selectiva(
    pregunta: str,
    borrador: str,
    citas_validas: list[str],
    fuentes: list[dict[str, Any]],
) -> tuple[bool, str]:
    """Compuerta determinista CRAG: decide cuándo justifica hacer una 2da pasada revisora."""
    if not fuentes:
        return False, "sin_fuentes"

    low_resp = str(borrador or "").lower()
    if not citas_validas:
        return True, "sin_citas"
    if any(p in low_resp for p in _PATRONES_ABSTENCION):
        return True, "abstencion_en_presencia_de_fuentes"

    low_q = str(pregunta or "").lower()
    if any(p in low_q for p in _PATRONES_MULTI_REQUISITO):
        return True, "pregunta_multiclausula_o_requisitos"
    return False, "respuesta_directa_simple"


def _seleccionar_evidencia_revisor(
    citas_validas: list[str],
    fuentes: list[dict[str, Any]],
    max_unidades: int = 3,
) -> list[dict[str, Any]]:
    """Prioriza las unidades realmente citadas para evitar que distractores contaminen al revisor."""
    por_id = {f["id"]: f for f in fuentes if "id" in f}
    elegidas: list[dict[str, Any]] = []
    vistas: set[str] = set()
    for cid in citas_validas:
        if cid in por_id and cid not in vistas:
            elegidas.append(por_id[cid])
            vistas.add(cid)
        if len(elegidas) >= max_unidades:
            return elegidas
    for f in fuentes:
        fid = f.get("id")
        if fid and fid not in vistas:
            elegidas.append(f)
            vistas.add(fid)
        if len(elegidas) >= max_unidades:
            break
    return elegidas


def verificar_y_corregir_respuesta(
    pregunta: str,
    borrador: str,
    citas_validas: list[str],
    fuentes: list[dict[str, Any]],
    config: ConfigAsistente,
    cliente_chat: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evalúa completitud y fidelidad del borrador respecto a la evidencia y corrige si falta algo."""
    evidencia = _seleccionar_evidencia_revisor(citas_validas, fuentes, max_unidades=3)
    if not evidencia or not borrador.strip():
        return {"revisado": False, "modificada": False, "diagnostico": "sin_evidencia", "respuesta": borrador}

    bloque_ev = "\n\n".join(f"[{u['id']}] {u.get('texto', '')}" for u in evidencia)
    prompt = (
        "Eres un revisor estricto de fidelidad y completitud normativa.\n"
        "Compara el BORRADOR contra la EVIDENCIA OFICIAL y verifica únicamente dos puntos:\n"
        "1. `completo`: ¿El borrador incluye TODOS los requisitos, plazos, excepciones y posibilidades de apelación que aparecen en el artículo relevante de la evidencia para responder la pregunta?\n"
        "2. `fiel`: ¿Todo lo afirmado proviene directamente de la evidencia sin inventar restricciones ni mezclar reglas de un caso distinto?\n\n"
        "Responde SOLO un JSON válido con estas claves exactas:\n"
        '{"completo": true, "fiel": true, "hallazgo": "ok", "respuesta_corregida": ""}\n'
        "Solo llena `respuesta_corregida` (manteniendo citas exactas entre corchetes `[ID]`) si `completo` es false o `fiel` es false; si ambos son true deja `respuesta_corregida` vacía.\n\n"
        f"PREGUNTA: {pregunta}\n\n"
        f"EVIDENCIA OFICIAL:\n{bloque_ev}\n\n"
        f"BORRADOR:\n{borrador}"
    )

    payload: dict[str, Any] = {
        "model": config.modelo,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.0,
            "num_ctx": config.num_ctx,
            "num_predict": min(config.num_predict, 700),
            "repeat_penalty": config.repeat_penalty,
        },
    }
    if config.desactivar_thinking and "qwen3" in config.modelo.lower():
        payload["think"] = False

    if cliente_chat is not None:
        data = cliente_chat(payload)
    else:
        url = f"{config.ollama_url.rstrip('/')}/api/chat"
        resp = requests.post(url, json=payload, timeout=config.timeout_s)
        if resp.status_code == 400 and "think" in payload:
            sin_think = {k: v for k, v in payload.items() if k != "think"}
            resp = requests.post(url, json=sin_think, timeout=config.timeout_s)
        resp.raise_for_status()
        data = resp.json()

    raw = str(data.get("message", {}).get("content", "")).strip()
    try:
        obj = json.loads(raw)
    except ValueError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return {"revisado": True, "modificada": False, "diagnostico": "json_invalido", "respuesta": borrador}
        try:
            obj = json.loads(m.group(0))
        except ValueError:
            return {"revisado": True, "modificada": False, "diagnostico": "json_invalido", "respuesta": borrador}

    completo = bool(obj.get("completo", True))
    fiel = bool(obj.get("fiel", True))
    corregida = str(obj.get("respuesta_corregida") or "").strip()
    hallazgo = str(obj.get("hallazgo") or "").strip()

    if (not completo or not fiel) and len(corregida) >= 30:
        return {
            "revisado": True,
            "modificada": True,
            "diagnostico": hallazgo or "corregida",
            "respuesta": corregida,
        }
    return {
        "revisado": True,
        "modificada": False,
        "diagnostico": hallazgo or "aprobada",
        "respuesta": borrador,
    }
