"""Extracción y fragmentación dinámica de PDFs locales para consulta RAG en caliente."""

from __future__ import annotations

import hashlib
import io
import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np


def _limpiar_texto_pdf(texto: str) -> str:
    """Limpia cortes de palabra por guion y saltos redundantes preservando párrafos."""
    t = str(texto or "").replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"([a-záéíóúüñA-ZÁÉÍÓÚÜÑ])-\n([a-záéíóúüñ])", r"\1\2", t)
    parrafos = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n{2,}", t)]
    return "\n\n".join(p for p in parrafos if p)


def _slug_archivo(nombre: str, sha_hex: str) -> str:
    base = nombre.rsplit(".", 1)[0]
    norm = unicodedata.normalize("NFD", base)
    solo_ascii = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    alfanum = re.sub(r"[^A-Za-z0-9]+", "", solo_ascii).upper()[:12] or "DOC"
    suf = re.sub(r"[^A-Z0-9]", "", sha_hex.upper())[:4] or "0000"
    return f"{alfanum}{suf}"


def extraer_paginas_pdf(contenido_bytes: bytes, nombre_archivo: str = "documento.pdf") -> list[dict[str, Any]]:
    """Extrae texto página por página usando pdfplumber con respaldo automático de PyMuPDF."""
    if not contenido_bytes:
        raise ValueError(f"El archivo '{nombre_archivo}' está vacío.")

    paginas_txt: list[str] = []
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(contenido_bytes)) as pdf:
            for page in pdf.pages:
                paginas_txt.append(page.extract_text() or "")
    except Exception:
        paginas_txt = []

    # Respaldar páginas vacías o fallo completo usando PyMuPDF (fitz)
    if not paginas_txt or any(not p.strip() for p in paginas_txt):
        try:
            import fitz

            with fitz.open(stream=contenido_bytes, filetype="pdf") as doc:
                if not paginas_txt:
                    paginas_txt = [page.get_text("text") or "" for page in doc]
                else:
                    for idx, page in enumerate(doc):
                        if idx < len(paginas_txt) and not paginas_txt[idx].strip():
                            paginas_txt[idx] = page.get_text("text") or ""
        except Exception as exc:
            if not paginas_txt:
                raise ValueError(f"No se pudo leer '{nombre_archivo}': {exc}") from exc

    paginas: list[dict[str, Any]] = []
    for num, raw in enumerate(paginas_txt, start=1):
        limpio = _limpiar_texto_pdf(raw)
        if limpio:
            paginas.append({"pagina": num, "texto": limpio})

    if not paginas:
        raise ValueError(
            f"'{nombre_archivo}' no contiene texto extraíble (podría estar escaneado como imagen)."
        )
    return paginas


def _dividir_en_trozos(texto: str, max_chars: int = 950, solapamiento: int = 140) -> list[str]:
    """Divide texto por límites de párrafo/oración cuidando el presupuesto del tokenizador E5."""
    if len(texto) <= max_chars:
        return [texto]

    trozos: list[str] = []
    inicio = 0
    n = len(texto)
    while inicio < n:
        limite = min(inicio + max_chars, n)
        corte = limite
        if limite < n:
            ventana = texto[inicio:limite]
            for sep in ("\n\n", ". ", "; ", "\n", " "):
                pos = ventana.rfind(sep)
                if pos >= int(max_chars * 0.45):
                    corte = inicio + pos + len(sep)
                    break
        trozo = texto[inicio:corte].strip()
        if trozo:
            trozos.append(trozo)
        if corte >= n:
            break
        inicio = max(corte - solapamiento, inicio + 1)
    return trozos


def construir_unidades_pdf(
    contenido_bytes: bytes,
    nombre_archivo: str,
    max_chars: int = 950,
    solapamiento: int = 140,
) -> dict[str, Any]:
    """Convierte un PDF en unidades y fragmentos compatibles con BuscadorNormativa."""
    sha_hex = hashlib.sha256(contenido_bytes).hexdigest()
    slug = _slug_archivo(nombre_archivo, sha_hex)
    doc_id = f"PDF:{nombre_archivo}"
    paginas = extraer_paginas_pdf(contenido_bytes, nombre_archivo=nombre_archivo)

    unidades: list[dict[str, Any]] = []
    fragmentos: list[dict[str, Any]] = []
    for pg in paginas:
        num_pag = int(pg["pagina"])
        trozos = _dividir_en_trozos(pg["texto"], max_chars=max_chars, solapamiento=solapamiento)
        for j, trozo in enumerate(trozos, start=1):
            uid = f"PDF-{slug}-P{num_pag:02d}-{j:02d}"
            texto_unidad = f"[{nombre_archivo}, pág. {num_pag}]\n{trozo}"
            unidades.append(
                {
                    "id": uid,
                    "parent_id": uid,
                    "documento": doc_id,
                    "archivo": nombre_archivo,
                    "paginas": [num_pag],
                    "texto": texto_unidad,
                    "es_pdf_usuario": True,
                }
            )
            fragmentos.append(
                {
                    "id": f"{uid}-F01",
                    "unidad_id": uid,
                    "parent_id": uid,
                    "texto": texto_unidad,
                    "texto_embedding": f"passage: [{uid} | {nombre_archivo}, PDF p. {num_pag}]\n{trozo}",
                }
            )

    return {
        "nombre_archivo": nombre_archivo,
        "documento": doc_id,
        "sha256": sha_hex,
        "paginas_con_texto": len(paginas),
        "unidades": unidades,
        "fragmentos": fragmentos,
    }


def cargar_o_calcular_vectores_pdf(
    pack: dict[str, Any],
    codificador: Any,
    cache_dir: Path,
) -> np.ndarray:
    """Devuelve la matriz E5 de fragmentos de un PDF usando caché en disco por SHA-256."""
    frags = pack.get("fragmentos") or []
    if not frags or codificador is None:
        return np.zeros((0, 0), dtype=np.float32)

    pdfs_dir = Path(cache_dir) / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)
    sha_corto = str(pack.get("sha256", ""))[:16]
    archivo_cache = pdfs_dir / f"e5_pdf_{sha_corto}.npz"
    if archivo_cache.is_file():
        datos = np.load(archivo_cache)
        mat = np.asarray(datos["vectores"], dtype=np.float32)
        if mat.shape[0] == len(frags):
            return mat

    textos = [f.get("texto_embedding") or f"passage: {f['texto']}" for f in frags]
    mat = codificador.encode(
        textos, normalize_embeddings=True, batch_size=32, show_progress_bar=False
    )
    mat = np.asarray(mat, dtype=np.float32)
    np.savez_compressed(archivo_cache, vectores=mat)
    return mat
