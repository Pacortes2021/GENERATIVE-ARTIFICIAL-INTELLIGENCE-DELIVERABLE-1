"""Aplicación web local en Streamlit para el asistente de normativa UdeC."""

from __future__ import annotations

import datetime as dt
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import streamlit as st

# Permite ejecutar `streamlit run asistente_local/app.py` desde la raíz o dentro de la carpeta
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from asistente_local.asistente import AsistenteUdeC, listar_modelos_ollama, normalizar_citas_respuesta
from asistente_local.buscador import BuscadorNormativa
from asistente_local.config import ConfigAsistente
from asistente_local.historial import (
    cargar_chat,
    eliminar_chat,
    exportar_chat_markdown,
    generar_titulo_chat,
    guardar_chat,
    listar_chats,
)
from asistente_local.pdfs import construir_unidades_pdf
from asistente_local.verificador import verificar_y_corregir_respuesta


def _nuevo_chat_id() -> str:
    return dt.datetime.now().strftime("chat_%Y%m%d_%H%M%S_") + uuid.uuid4().hex[:6]


def _render_trazabilidad(meta: dict[str, Any]) -> None:
    """Muestra herramientas Python ejecutadas y artículos o PDFs consultados."""
    with st.expander(f"Trazabilidad ({meta['modelo']} · {meta['segundos']}s · {meta['turnos']} llamadas)"):
        if meta.get("herramientas"):
            st.markdown("**Herramientas Python usadas:**")
            for h in meta["herramientas"]:
                st.code(f"{h['nombre']}({h['argumentos']}) => {h['resultado']}", language="text")
        if meta.get("fuentes"):
            st.markdown("**Artículos / fragmentos consultados:**")
            for f in meta["fuentes"]:
                st.markdown(f"**`[{f['id']}]`** {f['texto']}")


@st.cache_resource
def _cargar_buscador(usar_embeddings: bool) -> BuscadorNormativa:
    return BuscadorNormativa(usar_embeddings=usar_embeddings)


@st.cache_data(show_spinner=False)
def _procesar_pdf_cacheado(nombre: str, contenido: bytes) -> dict[str, Any]:
    return construir_unidades_pdf(contenido, nombre_archivo=nombre)


def _obtener_buscador_activo(
    usar_e5: bool,
    packs_pdf: list[dict[str, Any]],
    alcance: str,
) -> BuscadorNormativa:
    """Devuelve el buscador base o combinado con PDFs reutilizando caché en sesión."""
    clave = (usar_e5, alcance, tuple(str(p.get("sha256", "")) for p in packs_pdf))
    if st.session_state.get("_buscador_clave") == clave and st.session_state.get("_buscador_obj") is not None:
        return st.session_state["_buscador_obj"]

    base = _cargar_buscador(usar_e5)
    if alcance == "Reglamentos UdeC":
        activo = base
    elif alcance == "Combinado (UdeC + mis PDFs)":
        activo = base.con_pdfs_usuario(packs_pdf, incluir_corpus_base=True)
    else:
        activo = base.con_pdfs_usuario(packs_pdf, incluir_corpus_base=False)

    st.session_state["_buscador_clave"] = clave
    st.session_state["_buscador_obj"] = activo
    return activo


def _render_sidebar_pdfs() -> tuple[list[dict[str, Any]], str]:
    """Renderiza carga de PDFs propios y selector de alcance en la barra lateral."""
    st.subheader("PDFs propios en caliente")
    archivos = st.file_uploader(
        "Subir PDFs para consultar",
        type=["pdf"],
        accept_multiple_files=True,
        help="Extrae texto por página, calcula embeddings E5 con caché local y habilita citas [PDF-...].",
    )
    packs_pdf: list[dict[str, Any]] = []
    for f in archivos or []:
        try:
            pack = _procesar_pdf_cacheado(f.name, f.getvalue())
            packs_pdf.append(pack)
        except Exception as exc:
            st.warning(f"No se pudo cargar '{f.name}': {exc}")

    if packs_pdf:
        total_pags = sum(int(p.get("paginas_con_texto", 0)) for p in packs_pdf)
        total_frags = sum(len(p.get("fragmentos") or []) for p in packs_pdf)
        st.success(f"{len(packs_pdf)} PDF(s) · {total_pags} págs · {total_frags} fragmentos")
        for p in packs_pdf:
            st.caption(f"• {p['nombre_archivo']} ({p['paginas_con_texto']} págs)")

    st.session_state.setdefault("alcance_fuentes", "Reglamentos UdeC")
    st.session_state.setdefault("_tuvo_pdfs", False)
    if packs_pdf and not st.session_state["_tuvo_pdfs"]:
        st.session_state["alcance_fuentes"] = "Combinado (UdeC + mis PDFs)"
        st.session_state["_tuvo_pdfs"] = True
    elif not packs_pdf and st.session_state["_tuvo_pdfs"]:
        st.session_state["_tuvo_pdfs"] = False
        if st.session_state["alcance_fuentes"] != "Reglamentos UdeC":
            st.session_state["alcance_fuentes"] = "Reglamentos UdeC"

    alcance = st.radio(
        "Alcance de búsqueda",
        ["Reglamentos UdeC", "Combinado (UdeC + mis PDFs)", "Solo mis PDFs subidos"],
        key="alcance_fuentes",
    )
    if alcance == "Solo mis PDFs subidos" and not packs_pdf:
        st.info("Sube al menos un PDF arriba para consultar en modo solo-PDF.")
    return packs_pdf, alcance


def _render_sidebar_chats() -> None:
    """Renderiza persistencia local de conversaciones y exportación a Markdown."""
    st.subheader("Conversaciones")
    col_nuevo, col_limpiar = st.columns(2)
    with col_nuevo:
        if st.button("➕ Nuevo chat", use_container_width=True):
            st.session_state["chat_id"] = _nuevo_chat_id()
            st.session_state["mensajes"] = []
            st.rerun()
    with col_limpiar:
        if st.button("🧹 Limpiar", use_container_width=True):
            st.session_state["mensajes"] = []
            st.rerun()

    chats_guardados = listar_chats()
    if chats_guardados:
        etiquetas = {
            c["id"]: f"{c.get('titulo', c['id'])} ({str(c.get('actualizado_en', ''))[:16].replace('T', ' ')})"
            for c in chats_guardados
        }
        ids_chats = list(etiquetas.keys())
        idx_def = ids_chats.index(st.session_state["chat_id"]) if st.session_state["chat_id"] in ids_chats else 0
        sel_id = st.selectbox(
            "Historial guardado en disco",
            ids_chats,
            index=idx_def,
            format_func=lambda cid: etiquetas[cid],
        )
        col_cargar, col_borrar = st.columns(2)
        with col_cargar:
            if st.button("Cargar chat", use_container_width=True):
                cargado = cargar_chat(sel_id)
                if cargado:
                    st.session_state["chat_id"] = cargado["id"]
                    st.session_state["mensajes"] = list(cargado.get("mensajes") or [])
                    st.rerun()
        with col_borrar:
            if st.button("Borrar chat", use_container_width=True):
                eliminar_chat(sel_id)
                if sel_id == st.session_state["chat_id"]:
                    st.session_state["chat_id"] = _nuevo_chat_id()
                    st.session_state["mensajes"] = []
                st.rerun()

    mensajes = st.session_state.get("mensajes") or []
    if mensajes:
        titulo_md = generar_titulo_chat(mensajes)
        md_doc = exportar_chat_markdown(mensajes, titulo=titulo_md)
        st.download_button(
            "⬇️ Descargar chat (.md)",
            data=md_doc,
            file_name=f"{st.session_state['chat_id']}.md",
            mime="text/markdown",
            use_container_width=True,
        )


def main() -> None:
    st.set_page_config(page_title="Asistente Normativa UdeC (Local)", page_icon="📘", layout="wide")
    st.title("Asistente Local de Normativa y PDFs · Ingeniería UdeC")
    st.caption(
        "RAG híbrido (`BM25` + `multilingual-e5-small` con `RRF` y `Top-p 85%`) · "
        "PDFs propios en caliente · Ollama + Python"
    )

    st.session_state.setdefault("mensajes", [])
    st.session_state.setdefault("chat_id", _nuevo_chat_id())

    modelos_disp = listar_modelos_ollama()
    preferidos = ["qwen3:4b-instruct", "qwen3:4b", "qwen2.5:3b"]
    modelos_ord = [m for m in preferidos if m in modelos_disp] + [
        m for m in modelos_disp if m not in preferidos
    ]
    if not modelos_ord:
        modelos_ord = ["qwen3:4b-instruct", "qwen2.5:3b"]

    with st.sidebar:
        packs_pdf, alcance = _render_sidebar_pdfs()
        st.markdown("---")
        st.subheader("Motor IA y Recuperación")
        modelo = st.selectbox("Modelo Ollama", modelos_ord, index=0)
        usar_e5 = st.checkbox("Usar embeddings E5 locales", value=True)
        usar_rrf = st.checkbox(
            "Fusión RRF (BM25 + E5) + subcláusulas",
            value=True,
            help="Combina BM25 y E5 por Reciprocal Rank Fusion y divide preguntas compuestas.",
        )
        usar_top_p = st.checkbox(
            "Selección adaptativa Top-p (85%)",
            value=True,
            help=(
                "Trae entre 1 y 6 artículos hasta sumar 85% de relevancia acumulada "
                "(si se desactiva, usa k=6 fijo)."
            ),
        )
        prebuscar = st.checkbox("Pre-cargar contexto inicial (más rápido)", value=True)
        temp = st.slider("Temperatura", 0.0, 0.7, 0.0, 0.05)

        st.markdown("---")
        _render_sidebar_chats()

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

    cfg = ConfigAsistente(
        modelo=modelo,
        temperature=temp,
        usar_embeddings=usar_e5,
        top_p_inicial=0.85 if usar_top_p else None,
        modo_fusion="rrf" if usar_rrf else "lineal",
        usar_descomposicion=usar_rrf,
    )

    mensajes = st.session_state["mensajes"]
    for idx, msg in enumerate(mensajes):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            meta = msg.get("meta")
            if msg["role"] == "assistant" and meta:
                _render_trazabilidad(meta)
                verif = meta.get("verificacion")
                if verif:
                    if verif.get("modificada"):
                        st.info(f"🛠️ Verificador Self-RAG actualizó la respuesta: {verif.get('diagnostico', '')}")
                    else:
                        st.caption(f"🔎 Self-RAG verificó la evidencia: {verif.get('diagnostico', 'aprobada')}")
                if idx == len(mensajes) - 1 and meta.get("fuentes"):
                    if st.button(
                        "🔎 Verificar fidelidad (Self-RAG)",
                        key=f"selfrag_{st.session_state['chat_id']}_{idx}",
                    ):
                        pregunta_orig = str(mensajes[idx - 1]["content"]) if idx > 0 else ""
                        with st.spinner("Auditando completitud y citas contra la evidencia..."):
                            buscador_act = _obtener_buscador_activo(usar_e5, packs_pdf, alcance)
                            _, citas_val = normalizar_citas_respuesta(
                                msg["content"], set(buscador_act.por_id.keys())
                            )
                            res_verif = verificar_y_corregir_respuesta(
                                pregunta=pregunta_orig,
                                borrador=msg["content"],
                                citas_validas=citas_val,
                                fuentes=meta["fuentes"],
                                config=cfg,
                            )
                        if res_verif.get("modificada"):
                            corr, _ = normalizar_citas_respuesta(
                                str(res_verif["respuesta"]), set(buscador_act.por_id.keys())
                            )
                            meta["borrador_original"] = msg["content"]
                            msg["content"] = corr
                        meta["verificacion"] = {
                            "modificada": bool(res_verif.get("modificada")),
                            "diagnostico": str(res_verif.get("diagnostico", "")),
                        }
                        guardar_chat(st.session_state["chat_id"], st.session_state["mensajes"])
                        st.rerun()

    placeholder_chat = (
        "Pregunta sobre tus PDFs subidos..."
        if alcance == "Solo mis PDFs subidos"
        else "Pregunta sobre reglamentos UdeC 2026 o tus PDFs subidos..."
    )
    prompt = st.chat_input(placeholder_chat)
    if not prompt and st.session_state.get("prompt_pendiente"):
        prompt = st.session_state.pop("prompt_pendiente")

    if prompt:
        st.session_state["mensajes"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            estado_slot = st.empty()
            estado_box = estado_slot.status("Cargando buscador e índices...", expanded=False)
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
                buscador_activo = _obtener_buscador_activo(usar_e5, packs_pdf, alcance)
                asistente = AsistenteUdeC(config=cfg, buscador=buscador_activo)
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
        guardar_chat(st.session_state["chat_id"], st.session_state["mensajes"])
        st.rerun()


if __name__ == "__main__":
    main()
