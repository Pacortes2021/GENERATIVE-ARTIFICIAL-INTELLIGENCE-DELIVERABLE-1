"""Aplicación web local en Streamlit para el asistente de normativa UdeC."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st

# Permite ejecutar `streamlit run asistente_local/app.py` desde la raíz o dentro de la carpeta
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from asistente_local.asistente import AsistenteUdeC, listar_modelos_ollama
from asistente_local.buscador import BuscadorNormativa
from asistente_local.config import ConfigAsistente


def _render_trazabilidad(meta: dict) -> None:
    """Muestra herramientas Python ejecutadas y artículos consultados."""
    with st.expander(f"Trazabilidad ({meta['modelo']} · {meta['segundos']}s · {meta['turnos']} llamadas)"):
        if meta["herramientas"]:
            st.markdown("**Herramientas Python usadas:**")
            for h in meta["herramientas"]:
                st.code(f"{h['nombre']}({h['argumentos']}) => {h['resultado']}", language="text")
        if meta["fuentes"]:
            st.markdown("**Artículos / unidades consultadas:**")
            for f in meta["fuentes"]:
                st.markdown(f"**`[{f['id']}]`** {f['texto']}")


@st.cache_resource
def _cargar_buscador(usar_embeddings: bool) -> BuscadorNormativa:
    return BuscadorNormativa(usar_embeddings=usar_embeddings)


def main() -> None:
    st.set_page_config(page_title="Asistente Normativa UdeC (Local)", page_icon="📘", layout="wide")
    st.title("Asistente Local de Normativa Pregrado · Ingeniería UdeC")
    st.caption("RAG híbrido (`multilingual-e5-small` + léxico) + Ollama `/api/chat` + calculadora y calendario Python")

    modelos_disp = listar_modelos_ollama()
    preferidos = ["qwen3:4b-instruct", "qwen3:4b", "qwen2.5:3b"]
    modelos_ord = [m for m in preferidos if m in modelos_disp] + [
        m for m in modelos_disp if m not in preferidos
    ]
    if not modelos_ord:
        modelos_ord = ["qwen3:4b-instruct", "qwen2.5:3b"]

    with st.sidebar:
        st.header("Configuración")
        modelo = st.selectbox("Modelo Ollama", modelos_ord, index=0)
        usar_e5 = st.checkbox("Usar embeddings E5 locales", value=True)
        prebuscar = st.checkbox("Pre-cargar contexto inicial (más rápido)", value=True)
        temp = st.slider("Temperatura", 0.0, 0.7, 0.0, 0.05)
        if st.button("Limpiar conversación"):
            st.session_state["mensajes"] = []
            st.rerun()

        st.markdown("---")
        st.markdown("**Pruebas rápidas sugeridas:**")
        ejemplos = [
            "Un estudiante aprobó 42 créditos al término de su cuarto semestre. ¿Está en baja académica según el Art. 14?",
            "En el calendario 2026, ¿cuántos días hay desde el inicio de clases hasta el límite de modificación de asignaturas en cada semestre?",
            "¿Qué nota mínima exige el Artículo 45 del Reglamento Interno de Ingeniería para aprobar la práctica?",
        ]
        for idx, ej in enumerate(ejemplos):
            if st.button(f"Probar ejemplo {idx + 1}", key=f"ej_{idx}"):
                st.session_state["prompt_pendiente"] = ej

    if "mensajes" not in st.session_state:
        st.session_state["mensajes"] = []

    for msg in st.session_state["mensajes"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("meta"):
                _render_trazabilidad(msg["meta"])

    prompt = st.chat_input("Pregunta sobre reglamentos o calendario UdeC 2026...")
    if not prompt and st.session_state.get("prompt_pendiente"):
        prompt = st.session_state.pop("prompt_pendiente")

    if prompt:
        st.session_state["mensajes"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            estado_slot = st.empty()
            estado_box = estado_slot.status("Cargando buscador y normativa...", expanded=False)
            placeholder = st.empty()
            tokens_stream: list[str] = []
            ultimo_render = 0.0

            def _on_estado(texto_estado: str) -> None:
                estado_box.update(label=texto_estado, state="running")
                if tokens_stream:
                    tokens_stream.clear()
                    placeholder.empty()

            def _on_token(tok: str) -> None:
                nonlocal ultimo_render
                if not tokens_stream:
                    estado_box.update(label="Escribiendo respuesta...", state="running")
                tokens_stream.append(tok)
                ahora = time.monotonic()
                if ahora - ultimo_render >= 0.04 or "\n" in tok:
                    placeholder.markdown("".join(tokens_stream) + " ▌")
                    ultimo_render = ahora

            try:
                buscador = _cargar_buscador(usar_e5)
                cfg = ConfigAsistente(modelo=modelo, temperature=temp, usar_embeddings=usar_e5)
                asistente = AsistenteUdeC(config=cfg, buscador=buscador)
                hist = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state["mensajes"][:-1]
                ]
                res = asistente.responder(
                    prompt,
                    historial=hist[-6:],
                    prebuscar=prebuscar,
                    on_token=_on_token,
                    on_estado=_on_estado,
                )
            except Exception as exc:
                estado_box.update(label="Error al consultar Ollama", state="error", expanded=False)
                st.error(f"No se pudo completar la consulta con Ollama: {exc}")
                return

            estado_slot.empty()
            placeholder.markdown(res.respuesta)
            meta = {
                "modelo": res.modelo,
                "segundos": res.segundos,
                "turnos": res.turnos_modelo,
                "herramientas": [
                    {"nombre": p.nombre, "argumentos": p.argumentos, "resultado": p.resultado}
                    for p in res.pasos_herramientas
                ],
                "fuentes": res.fuentes,
            }
            _render_trazabilidad(meta)

        st.session_state["mensajes"].append(
            {"role": "assistant", "content": res.respuesta, "meta": meta}
        )


if __name__ == "__main__":
    main()
