"""Orquestador conversacional del asistente local UdeC vía Ollama /api/chat."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

import requests

from .buscador import BuscadorNormativa, _tokens_clave
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
_BRACKET_ID_RE = re.compile(r"\[([A-Z]+(?:-[A-Z0-9]+)+(?:\.[a-z0-9]+|-[a-z])?)\]")


def limpiar_think(texto: str) -> str:
    """Elimina bloques <think>...</think> visibles si un modelo los emite."""
    limpio = _THINK_RE.sub("", str(texto or ""))
    limpio = re.sub(r"<think>.*", "", limpio, flags=re.DOTALL)
    return limpio.strip()


def _longitud_prefijo_cola(texto: str, objetivo: str) -> int:
    """Longitud del mayor sufijo de `texto` que es prefijo estricto de `objetivo`."""
    max_len = min(len(texto), len(objetivo) - 1)
    for k in range(max_len, 0, -1):
        if texto.endswith(objetivo[:k]):
            return k
    return 0


class _FiltroThinkStream:
    """Filtra en vivo bloques <think>...</think> aunque lleguen fragmentados."""

    def __init__(self) -> None:
        self._en_think = False
        self._buffer = ""
        self._recortar_inicio = True

    def _emitir_limpio(self, trozo: str, salida: list[str]) -> None:
        if not trozo:
            return
        if self._recortar_inicio:
            trozo = trozo.lstrip()
            if not trozo:
                return
            self._recortar_inicio = False
        salida.append(trozo)

    def alimentar(self, delta: str) -> str:
        """Procesa un fragmento entrante y devuelve solo texto visible fuera de <think>."""
        if not delta:
            return ""
        self._buffer += delta
        salida: list[str] = []
        while self._buffer:
            if self._en_think:
                idx = self._buffer.find("</think>")
                if idx == -1:
                    corte = len("</think>") - 1
                    if len(self._buffer) > corte:
                        self._buffer = self._buffer[-corte:]
                    break
                self._buffer = self._buffer[idx + len("</think>") :]
                self._en_think = False
                self._recortar_inicio = True
                continue

            idx = self._buffer.find("<think>")
            if idx != -1:
                self._emitir_limpio(self._buffer[:idx], salida)
                self._buffer = self._buffer[idx + len("<think>") :]
                self._en_think = True
                continue

            retener = _longitud_prefijo_cola(self._buffer, "<think>")
            limite = len(self._buffer) - retener
            self._emitir_limpio(self._buffer[:limite], salida)
            self._buffer = self._buffer[limite:]
            break
        return "".join(salida)

    def finalizar(self) -> str:
        """Entrega el remanente seguro al cerrarse el stream."""
        if self._en_think or not self._buffer:
            self._buffer = ""
            return ""
        salida: list[str] = []
        self._emitir_limpio(self._buffer, salida)
        self._buffer = ""
        return "".join(salida)


def _recopilar_stream_ollama(
    lineas: Iterable[str | bytes],
    on_token: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Reconstruye el mensaje completo desde NDJSON de Ollama emitiendo tokens en vivo."""
    rol = "assistant"
    partes_texto: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    ultimo_chunk: dict[str, Any] = {}
    filtro = _FiltroThinkStream()

    for cruda in lineas:
        if not cruda:
            continue
        linea = cruda.decode("utf-8") if isinstance(cruda, bytes) else cruda
        linea = linea.strip()
        if not linea:
            continue
        chunk = json.loads(linea)
        if chunk.get("error"):
            raise RuntimeError(f"Error de Ollama: {chunk['error']}")
        ultimo_chunk = chunk
        msg = chunk.get("message") or {}
        if msg.get("role"):
            rol = str(msg["role"])
        tc_chunk = msg.get("tool_calls") or []
        if tc_chunk:
            tool_calls.extend(tc_chunk)
        delta = str(msg.get("content") or "")
        if delta:
            partes_texto.append(delta)
            if on_token is not None and not tc_chunk:
                visible = filtro.alimentar(delta)
                if visible:
                    on_token(visible)

    if on_token is not None:
        restante = filtro.finalizar()
        if restante and not tool_calls:
            on_token(restante)

    mensaje: dict[str, Any] = {"role": rol, "content": "".join(partes_texto)}
    if tool_calls:
        mensaje["tool_calls"] = tool_calls
    return {**ultimo_chunk, "message": mensaje, "done": True}


def reescribir_consulta_con_historial(
    pregunta: str,
    historial: list[dict[str, str]] | None,
) -> str:
    """Enriquece preguntas cortas o de seguimiento con palabras clave del turno previo."""
    if not historial:
        return pregunta
    q_tokens = _tokens_clave(pregunta)
    q_low = str(pregunta or "").strip().lower()
    marcadores = (
        "y si", "y en", "y que", "y qué", "y cual", "y cuál", "y cuanto", "y cuánto",
        "ese ", "esa ", "eso", "este ", "esta ", "estos", "dicho", "mismo", "anterior",
        "apelo", "apelar", "entonces", "tambien", "también", "tampoco", "pero ",
    )
    es_seguimiento = len(q_tokens) <= 7 and (
        len(q_tokens) <= 4 or any(m in q_low for m in marcadores) or q_low.startswith(("¿y ", "y "))
    )
    if not es_seguimiento:
        return pregunta

    contexto_prev: list[str] = []
    for turno in reversed(historial):
        if turno.get("role") == "user" and turno.get("content"):
            for tok in _tokens_clave(str(turno["content"])):
                if tok not in q_tokens and tok not in contexto_prev:
                    contexto_prev.append(tok)
                if len(contexto_prev) >= 8:
                    break
        if len(contexto_prev) >= 8:
            break
    if not contexto_prev:
        return pregunta
    return f"{pregunta} ({' '.join(contexto_prev)})"


def normalizar_citas_respuesta(texto: str, corpus_ids: set[str]) -> tuple[str, list[str]]:
    """Valida corchetes [ID] contra corpus_ids: normaliza sufijos y quita corchetes inexistentes."""
    validas: list[str] = []

    def _reemplazar(match: re.Match[str]) -> str:
        cid = match.group(1)
        if cid in corpus_ids:
            if cid not in validas:
                validas.append(cid)
            return f"[{cid}]"
        base = re.split(r"\.(?=[a-z0-9]+$)|-(?=[a-z]$)", cid, maxsplit=1)[0]
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


def _compactar_resultado_herramienta(
    resultado: Any,
    fuentes_vistas: dict[str, dict[str, Any]],
) -> Any:
    """Evita reenviar listas de unidades ya presentes en contexto para cuidar num_ctx."""
    if not isinstance(resultado, list):
        return resultado

    nuevos: list[Any] = []
    ya_en_contexto: list[str] = []
    for item in resultado:
        if (
            isinstance(item, dict)
            and "id" in item
            and "texto" in item
            and item["id"] in fuentes_vistas
        ):
            ya_en_contexto.append(str(item["id"]))
        else:
            nuevos.append(item)

    if not ya_en_contexto:
        return resultado

    if nuevos:
        return {
            "nuevos": nuevos,
            "ya_en_contexto": ya_en_contexto,
            "nota": (
                "Los IDs en ya_en_contexto ya están completos arriba en tu contexto; "
                "úsalos sin volver a repetirlos."
            ),
        }

    return {
        "ya_en_contexto": ya_en_contexto,
        "nota": (
            "Todas estas unidades ya figuran completas arriba en tu contexto; "
            "úsalas y continúa si necesitas llamar a `calcular` o `dias_entre`."
        ),
    }


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

    def _ejecutar_post_ollama(self, payload: dict[str, Any], stream: bool) -> requests.Response:
        assert self._session is not None
        url = f"{self.config.ollama_url.rstrip('/')}/api/chat"
        resp = self._session.post(url, json=payload, timeout=self.config.timeout_s, stream=stream)
        if resp.status_code == 400 and "think" in payload:
            resp.close()
            sin_think = {k: v for k, v in payload.items() if k != "think"}
            resp = self._session.post(url, json=sin_think, timeout=self.config.timeout_s, stream=stream)
        resp.raise_for_status()
        return resp

    def _llamar_ollama(
        self,
        payload: dict[str, Any],
        on_token: Callable[[str], None] | None = None,
    ) -> dict[str, Any]:
        if self._cliente_chat is not None:
            data = self._cliente_chat(payload)
            if on_token is not None:
                msg = data.get("message", {})
                if msg.get("content") and not msg.get("tool_calls"):
                    visible = limpiar_think(msg["content"])
                    if visible:
                        on_token(visible)
            return data

        stream = bool(payload.get("stream"))
        with self._ejecutar_post_ollama(payload, stream=stream) as resp:
            if stream:
                return _recopilar_stream_ollama(
                    resp.iter_lines(decode_unicode=False),
                    on_token=on_token,
                )
            return resp.json()

    def _construir_payload(
        self,
        mensajes: list[dict[str, Any]],
        incluir_tools: bool = True,
        stream: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.config.modelo,
            "messages": mensajes,
            "stream": stream,
            "options": {
                "temperature": self.config.temperature,
                "num_ctx": self.config.num_ctx,
                "num_predict": self.config.num_predict,
                "repeat_penalty": self.config.repeat_penalty,
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
        on_token: Callable[[str], None] | None = None,
        on_estado: Callable[[str], None] | None = None,
    ) -> RespuestaAsistente:
        """Responde una pregunta combinando búsqueda inicial, tool-calling y cálculo exacto."""
        t0 = time.perf_counter()
        fuentes_vistas: dict[str, dict[str, Any]] = {}
        pasos_herramientas: list[PasoHerramienta] = []

        bloque_inventario = ""
        checks_art = (
            self.buscador.verificar_articulos_mencionados(pregunta)
            if hasattr(self.buscador, "verificar_articulos_mencionados")
            else []
        )
        inexistentes = [c for c in checks_art if not c.get("existe")]
        if inexistentes:
            lineas_inv = [
                f"- El Artículo {c['numero']} NO existe en {c['doc']} "
                f"(el rango oficial de {c['doc']} llega hasta el Art. {c.get('max_articulo', 0)}). "
                f"No lo confundas con un artículo homónimo de otro reglamento."
                for c in inexistentes
            ]
            bloque_inventario = (
                "\n\nVerificación determinista previa del inventario oficial (`existe_articulo`):\n"
                + "\n".join(lineas_inv)
            )
            for c in inexistentes:
                pasos_herramientas.append(
                    PasoHerramienta(
                        nombre="existe_articulo",
                        argumentos={"doc": c["doc"], "numero": c["numero"]},
                        resultado=c,
                    )
                )

        bloque_inicial = ""
        if prebuscar:
            if on_estado is not None:
                on_estado("Buscando normativa relevante...")
            consulta_busqueda = reescribir_consulta_con_historial(pregunta, historial)
            hits_init = self.buscador.buscar(
                consulta_busqueda,
                k=self.config.top_k_inicial,
                expandir_citas=True,
                top_p=self.config.top_p_inicial,
                top_k_min=self.config.top_k_min,
                top_p_temp=self.config.top_p_temp,
                top_p_pool=self.config.top_p_pool,
                peso_boost_top_p=self.config.peso_boost_top_p,
                modo_fusion=self.config.modo_fusion,
                k_rrf=self.config.k_rrf,
                usar_descomposicion=self.config.usar_descomposicion,
            )
            for h in hits_init:
                fuentes_vistas[h["id"]] = h
            if hits_init:
                contexto_txt = "\n\n".join(f"[{h['id']}] {h['texto']}" for h in hits_init)
                encabezado = (
                    "\n\nContexto inicial recuperado de tus PDFs subidos "
                    "(si necesitas buscar otros pasajes, usa `buscar_reglamento` sin filtrar `documento`):\n"
                    if getattr(self.buscador, "solo_pdfs", False)
                    else "\n\nContexto normativo inicial recuperado automáticamente "
                    "(si necesitas más artículos, calendario completo o cálculos, usa tus herramientas):\n"
                )
                bloque_inicial = f"{encabezado}{contexto_txt}"

        system_prompt = SYSTEM_PROMPT
        if getattr(self.buscador, "solo_pdfs", False):
            system_prompt += (
                "\n5. MODO SOLO PDFs DEL USUARIO: La búsqueda opera únicamente sobre los PDFs cargados "
                "por el usuario (identificadores `[PDF-...]`). Responde basándote SOLO en esos documentos, "
                "cita `[PDF-...]` junto al nombre de archivo y página (`[archivo.pdf p. X]`), y si no hay "
                "PDFs cargados o el dato no figura en ellos, indícalo claramente sin afirmar reglas de UdeC que no estén en el contexto."
            )
        elif getattr(self.buscador, "tiene_pdfs_usuario", False):
            system_prompt += (
                "\n5. PDFs DEL USUARIO TAMBIÉN INDEXADOS: Además de los reglamentos UdeC, hay PDFs subidos "
                "por el usuario indexados en el buscador (`[PDF-...]`). Si la evidencia contiene pasajes `[PDF-...]`, "
                "cítalos junto con su archivo y página (`[archivo.pdf p. X]`) y no los descartes."
            )

        mensajes: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        for turno in historial or []:
            if turno.get("role") in {"user", "assistant"} and turno.get("content"):
                mensajes.append({"role": turno["role"], "content": str(turno["content"])})
        mensajes.append({"role": "user", "content": f"{pregunta}{bloque_inventario}{bloque_inicial}"})

        turnos = 0
        texto_final = ""
        usar_stream = on_token is not None

        for _ in range(self.config.max_pasos):
            turnos += 1
            if on_estado is not None:
                on_estado(
                    "Analizando pregunta..."
                    if turnos == 1
                    else "Redactando respuesta con la evidencia..."
                )
            data = self._llamar_ollama(
                self._construir_payload(mensajes, incluir_tools=True, stream=usar_stream),
                on_token=on_token,
            )
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
                if on_estado is not None:
                    on_estado(f"Ejecutando herramienta `{nombre}`...")
                res = ejecutar_herramienta(nombre, args, self.buscador)
                pasos_herramientas.append(PasoHerramienta(nombre=nombre, argumentos=args, resultado=res))
                res_para_modelo = _compactar_resultado_herramienta(res, fuentes_vistas)

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
                    "content": json.dumps(res_para_modelo, ensure_ascii=False),
                }
                if tc.get("id"):
                    tool_msg["tool_call_id"] = tc["id"]
                mensajes.append(tool_msg)
        else:
            # Si agotó max_pasos pidiendo herramientas, forzar síntesis sin tools
            turnos += 1
            if on_estado is not None:
                on_estado("Sintetizando respuesta final...")
            mensajes.append(
                {
                    "role": "user",
                    "content": "Con la información ya obtenida, entrega ahora la respuesta final citada.",
                }
            )
            data = self._llamar_ollama(
                self._construir_payload(mensajes, incluir_tools=False, stream=usar_stream),
                on_token=on_token,
            )
            msg_fin = data.get("message", {})
            mensajes.append(msg_fin)
            texto_final = limpiar_think(msg_fin.get("content", ""))

        corpus_ids = set(self.buscador.por_id.keys())
        texto_final, citas_validas = normalizar_citas_respuesta(texto_final, corpus_ids)
        es_inexistencia = any(
            pat in texto_final.lower()
            for pat in ("no existe", "no se encuentra el artículo", "no figura en")
        )
        texto_sin_citas = _BRACKET_ID_RE.sub("", texto_final).replace("Fuente:", "").strip(" .:-\n\t")
        solo_citas = bool(citas_validas) and len(texto_sin_citas) < 20 and not es_inexistencia
        if (not citas_validas or solo_citas) and fuentes_vistas and not es_inexistencia:
            turnos += 1
            prompt_reparacion = (
                (
                    "Tu respuesta anterior solo incluyó identificadores entre corchetes sin explicar la respuesta. "
                    "Responde de forma clara, completa y fiel a la pregunta usando el contexto consultado, "
                    "e incluye las citas exactas entre corchetes [ID]."
                )
                if solo_citas
                else (
                    "Tu respuesta anterior no citó identificadores entre corchetes. "
                    "Mantén exactamente tu respuesta y agrega al final `Fuente: [...]` usando "
                    "únicamente los identificadores exactos del contexto que la respaldan."
                )
            )
            mensajes.append({"role": "user", "content": prompt_reparacion})
            data = self._llamar_ollama(self._construir_payload(mensajes, incluir_tools=False))
            texto_rep = limpiar_think(data.get("message", {}).get("content", ""))
            texto_rep, citas_rep = normalizar_citas_respuesta(texto_rep, corpus_ids)
            if solo_citas:
                rep_sin_citas = _BRACKET_ID_RE.sub("", texto_rep).replace("Fuente:", "").strip(" .:-\n\t")
                if len(rep_sin_citas) >= 20:
                    if citas_rep:
                        texto_final = texto_rep
                    else:
                        citas_str = " ".join(f"[{cid}]" for cid in citas_validas)
                        texto_final = f"{texto_rep.strip()}\n\nFuente: {citas_str}".strip()
                    texto_final, citas_validas = normalizar_citas_respuesta(texto_final, corpus_ids)
            elif citas_rep:
                if len(texto_rep.strip()) >= max(40, int(len(texto_final.strip()) * 0.5)):
                    texto_final = texto_rep
                else:
                    citas_str = " ".join(f"[{cid}]" for cid in citas_rep)
                    texto_final = f"{texto_final}\n\nFuente: {citas_str}".strip()
                texto_final, citas_validas = normalizar_citas_respuesta(texto_final, corpus_ids)

        return RespuestaAsistente(
            pregunta=pregunta,
            respuesta=texto_final,
            modelo=self.config.modelo,
            segundos=round(time.perf_counter() - t0, 2),
            pasos_herramientas=pasos_herramientas,
            fuentes=list(fuentes_vistas.values()),
            turnos_modelo=turnos,
        )
