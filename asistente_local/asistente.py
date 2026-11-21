"""Orquestador conversacional del asistente local UdeC vía Ollama /api/chat."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable

import requests

from .buscador import BuscadorNormativa
from .config import ConfigAsistente
from .herramientas import ESQUEMAS_HERRAMIENTAS, ejecutar_herramienta

SYSTEM_PROMPT = (
    "Eres el asistente de normativa de pregrado de la Facultad de Ingeniería de la "
    "Universidad de Concepción (Reglamento General RG, Reglamento Interno RI-FI y "
    "Calendario Académico 2026).\n"
    "Reglas obligatorias:\n"
    "1. Responde de forma directa, clara y concisa usando SOLO lo devuelto por las herramientas "
    "o el contexto recuperado. Si falta un artículo o fechas del calendario, llama a "
    "`buscar_reglamento`, `leer_articulo`, `existe_articulo` o `ver_calendario`.\n"
    "2. Si la pregunta pide calcular un promedio, ponderación, diferencia de días o comparación "
    "numérica, llama PRIMERO a `calcular` o `dias_entre` ANTES de afirmar Sí o No "
    "(usa `inclusivo=false` para días transcurridos entre fechas, e `inclusivo=true` solo para "
    "duración inclusive de un rango).\n"
    "3. Responde explícitamente a la pregunta (indica si la norma confirma, corrige, condiciona "
    "o no fija lo pedido; no te limites a copiar literalmente un artículo sin interpretarlo). "
    "Distingue con precisión a qué caso o sujeto aplica cada párrafo o excepción del mismo artículo.\n"
    "4. Cita SIEMPRE al final o en línea usando ÚNICAMENTE los identificadores exactos entre "
    "corchetes presentes en la evidencia (ej. [RI-FI-ART-014], [CAL-2026-S2-02], sin inventar "
    "sufijos como .b o -b). Si `existe_articulo` devuelve `existe: false`, indica en texto el "
    "tope numérico (`max_articulo`, ej. 'llega hasta el Art. 35') SIN encerrarlo entre corchetes."
)

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
_BRACKET_ID_RE = re.compile(r"\[([A-Z]+(?:-[A-Z0-9]+)+(?:\.[a-z0-9]+)?)\]")


def limpiar_think(texto: str) -> str:
    """Elimina bloques <think>...</think> visibles si un modelo los emite."""
    limpio = _THINK_RE.sub("", str(texto or ""))
    limpio = re.sub(r"<think>.*", "", limpio, flags=re.DOTALL)
    return limpio.strip()


def normalizar_citas_respuesta(texto: str, corpus_ids: set[str]) -> tuple[str, list[str]]:
    """Valida corchetes [ID] contra corpus_ids: normaliza sufijos y quita corchetes inexistentes."""
    validas: list[str] = []

    def _reemplazar(match: re.Match[str]) -> str:
        cid = match.group(1)
        if cid in corpus_ids:
            if cid not in validas:
                validas.append(cid)
            return f"[{cid}]"
        base = cid.split(".", 1)[0]
        if base in corpus_ids:
            if base not in validas:
                validas.append(base)
            return f"[{base}]"
        return cid

    limpio = _BRACKET_ID_RE.sub(_reemplazar, texto)
    return limpio, validas


def listar_modelos_ollama(ollama_url: str = "http://localhost:11434", timeout_s: int = 5) -> list[str]:
    """Consulta los modelos disponibles en la instancia local de Ollama."""
    try:
        resp = requests.get(f"{ollama_url.rstrip('/')}/api/tags", timeout=timeout_s)
        resp.raise_for_status()
        modelos = [m["name"] for m in resp.json().get("models", []) if "name" in m]
        return modelos
    except Exception:
        return []


def _parsear_argumentos(raw_args: Any) -> dict[str, Any]:
    if isinstance(raw_args, dict):
        return raw_args
    if isinstance(raw_args, str):
        try:
            parsed = json.loads(raw_args)
            return parsed if isinstance(parsed, dict) else {}
        except ValueError:
            return {}
    return {}


@dataclass
class PasoHerramienta:
    nombre: str
    argumentos: dict[str, Any]
    resultado: Any


@dataclass
class RespuestaAsistente:
    pregunta: str
    respuesta: str
    modelo: str
    segundos: float
    pasos_herramientas: list[PasoHerramienta] = field(default_factory=list)
    fuentes: list[dict[str, Any]] = field(default_factory=list)
    turnos_modelo: int = 0


class AsistenteUdeC:
    """Ejecuta preguntas contra un modelo Ollama local conectado a herramientas Python."""

    def __init__(
        self,
        config: ConfigAsistente | None = None,
        buscador: BuscadorNormativa | None = None,
        cliente_chat: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        self.config = config or ConfigAsistente()
        self.buscador = buscador or BuscadorNormativa(
            corpus_path=self.config.corpus_path,
            fragmentos_path=self.config.fragmentos_path,
            modelo_embeddings=self.config.modelo_embeddings,
            cache_dir=self.config.cache_dir,
            usar_embeddings=self.config.usar_embeddings,
        )
        self._cliente_chat = cliente_chat
        self._session = requests.Session() if cliente_chat is None else None

    def _llamar_ollama(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._cliente_chat is not None:
            return self._cliente_chat(payload)

        assert self._session is not None
        url = f"{self.config.ollama_url.rstrip('/')}/api/chat"
        resp = self._session.post(url, json=payload, timeout=self.config.timeout_s)
        if resp.status_code == 400 and "think" in payload:
            sin_think = {k: v for k, v in payload.items() if k != "think"}
            resp = self._session.post(url, json=sin_think, timeout=self.config.timeout_s)
        resp.raise_for_status()
        return resp.json()

    def _construir_payload(
        self,
        mensajes: list[dict[str, Any]],
        incluir_tools: bool = True,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.config.modelo,
            "messages": mensajes,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_ctx": self.config.num_ctx,
            },
        }
        if incluir_tools:
            payload["tools"] = ESQUEMAS_HERRAMIENTAS
        if self.config.desactivar_thinking and "qwen3" in self.config.modelo.lower():
            payload["think"] = False
        return payload

    def responder(
        self,
        pregunta: str,
        historial: list[dict[str, str]] | None = None,
        prebuscar: bool = True,
    ) -> RespuestaAsistente:
        """Responde una pregunta combinando búsqueda inicial, tool-calling y cálculo exacto."""
        t0 = time.perf_counter()
        fuentes_vistas: dict[str, dict[str, Any]] = {}

        bloque_inicial = ""
        if prebuscar:
            hits_init = self.buscador.buscar(
                pregunta, k=self.config.top_k_inicial, expandir_citas=True
            )
            for h in hits_init:
                fuentes_vistas[h["id"]] = h
            contexto_txt = "\n\n".join(f"[{h['id']}] {h['texto']}" for h in hits_init)
            bloque_inicial = (
                "\n\nContexto normativo inicial recuperado automáticamente "
                "(si necesitas más artículos, calendario completo o cálculos, usa tus herramientas):\n"
                f"{contexto_txt}"
            )

        mensajes: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        for turno in historial or []:
            if turno.get("role") in {"user", "assistant"} and turno.get("content"):
                mensajes.append({"role": turno["role"], "content": str(turno["content"])})
        mensajes.append({"role": "user", "content": f"{pregunta}{bloque_inicial}"})

        pasos_herramientas: list[PasoHerramienta] = []
        turnos = 0
        texto_final = ""

        for _ in range(self.config.max_pasos):
            turnos += 1
            data = self._llamar_ollama(self._construir_payload(mensajes, incluir_tools=True))
            msg = data.get("message", {})
            tool_calls = msg.get("tool_calls") or []
            mensajes.append(msg)

            if not tool_calls:
                texto_final = limpiar_think(msg.get("content", ""))
                break

            for tc in tool_calls:
                fn = tc.get("function", {})
                nombre = str(fn.get("name", ""))
                args = _parsear_argumentos(fn.get("arguments"))
                res = ejecutar_herramienta(nombre, args, self.buscador)
                pasos_herramientas.append(PasoHerramienta(nombre=nombre, argumentos=args, resultado=res))

                # Registrar unidades consultadas para mostrarlas en la UI
                if isinstance(res, list):
                    for item in res:
                        if isinstance(item, dict) and "id" in item and "texto" in item:
                            fuentes_vistas[item["id"]] = item
                elif isinstance(res, dict) and res.get("id") and res.get("texto"):
                    fuentes_vistas[res["id"]] = res

                tool_msg: dict[str, Any] = {
                    "role": "tool",
                    "tool_name": nombre,
                    "content": json.dumps(res, ensure_ascii=False),
                }
                if tc.get("id"):
                    tool_msg["tool_call_id"] = tc["id"]
                mensajes.append(tool_msg)
        else:
            # Si agotó max_pasos pidiendo herramientas, forzar síntesis sin tools
            turnos += 1
            mensajes.append(
                {
                    "role": "user",
                    "content": "Con la información ya obtenida, entrega ahora la respuesta final citada.",
                }
            )
            data = self._llamar_ollama(self._construir_payload(mensajes, incluir_tools=False))
            msg_fin = data.get("message", {})
            mensajes.append(msg_fin)
            texto_final = limpiar_think(msg_fin.get("content", ""))

        corpus_ids = set(self.buscador.por_id.keys())
        texto_final, citas_validas = normalizar_citas_respuesta(texto_final, corpus_ids)
        es_inexistencia = any(
            pat in texto_final.lower()
            for pat in ("no existe", "no se encuentra el artículo", "no figura en")
        )
        if not citas_validas and fuentes_vistas and not es_inexistencia:
            turnos += 1
            mensajes.append(
                {
                    "role": "user",
                    "content": (
                        "Tu respuesta anterior no citó identificadores entre corchetes. "
                        "Mantén exactamente tu respuesta y agrega al final `Fuente: [...]` usando "
                        "únicamente los identificadores exactos del contexto que la respaldan."
                    ),
                }
            )
            data = self._llamar_ollama(self._construir_payload(mensajes, incluir_tools=False))
            texto_rep = limpiar_think(data.get("message", {}).get("content", ""))
            texto_rep, citas_rep = normalizar_citas_respuesta(texto_rep, corpus_ids)
            if citas_rep:
                texto_final = texto_rep

        return RespuestaAsistente(
            pregunta=pregunta,
            respuesta=texto_final,
            modelo=self.config.modelo,
            segundos=round(time.perf_counter() - t0, 2),
            pasos_herramientas=pasos_herramientas,
            fuentes=list(fuentes_vistas.values()),
            turnos_modelo=turnos,
        )
