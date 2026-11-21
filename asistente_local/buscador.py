"""Buscador híbrido (embeddings E5 + léxico + referencias cruzadas) sobre corpus.json."""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from .config import DEFAULT_CACHE_DIR, DEFAULT_CORPUS_PATH, DEFAULT_FRAGMENTOS_PATH

_STOPWORDS_ES = {
    "a", "al", "algo", "ante", "bajo", "cada", "como", "con", "cual", "cuando",
    "cuanto", "cuantos", "cuanta", "cuantas", "de", "del", "desde", "donde", "el",
    "ella", "en", "entre", "es", "esa", "ese", "eso", "esta", "este", "esto",
    "fue", "ha", "hasta", "hay", "la", "las", "le", "les", "lo", "los", "mas",
    "me", "mi", "no", "o", "para", "pero", "por", "que", "quien", "se", "si",
    "sin", "sobre", "su", "sus", "te", "tengo", "un", "una", "uno", "unos", "y",
}
_ART_REF_RE = re.compile(r"\bart(?:[íi]culo|\.?)\s*(\d+)\s*(?:°|º)?", re.IGNORECASE)
_CAL_ORDER_RE = re.compile(r"^CAL-(\d+)-S([12])-(\d+)$")


def normalizar_texto(texto: str) -> str:
    """Normaliza a minúsculas sin tildes preservando alfanuméricos y ñ."""
    descomp = unicodedata.normalize("NFD", str(texto or "").lower())
    sin_tildes = "".join(c for c in descomp if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]+", " ", sin_tildes).strip()


def _tokens_clave_lista(texto: str) -> list[str]:
    return [t for t in normalizar_texto(texto).split() if t not in _STOPWORDS_ES and len(t) > 1]


def _tokens_clave(texto: str) -> set[str]:
    return set(_tokens_clave_lista(texto))


def descomponer_subconsultas(consulta: str) -> tuple[list[str], bool]:
    """Divide preguntas compuestas en subcláusulas atómicas para RAG-Fusion sin usar LLM."""
    partes = re.split(
        r"(?:,?\s+y\s+(?:que|cual|cuál|como|cómo|cuando|cuándo|cuanto|cuánto|quien|quién|si)\b"
        r"|\?\s+¿|;\s*|\s+frente\s+al?\b)",
        consulta,
        flags=re.IGNORECASE,
    )
    clausulas = [p.strip(" ¿?.,;") for p in partes if len(_tokens_clave(p)) >= 2]
    if len(clausulas) <= 1:
        return [consulta], False
    return [consulta] + clausulas[:3], True


class BM25Index:
    """Índice BM25 (Robertson–Sparck Jones) en Python puro ponderado por IDF y longitud."""

    def __init__(self, documentos_tokens: list[list[str]], k1: float = 1.5, b: float = 0.75) -> None:
        self.docs = [Counter(dt) for dt in documentos_tokens]
        self.lens = [len(dt) for dt in documentos_tokens]
        self.avgdl = sum(self.lens) / max(1, len(self.lens))
        self.n_docs = len(self.docs)
        df: Counter[str] = Counter()
        for dt in self.docs:
            for w in dt:
                df[w] += 1
        self.idf = {
            w: math.log((self.n_docs - freq + 0.5) / (freq + 0.5) + 1.0)
            for w, freq in df.items()
        }
        self.k1 = k1
        self.b = b

    def puntuar(self, consulta_tokens: list[str]) -> np.ndarray:
        """Devuelve un vector con los puntajes BM25 de la consulta por fragmento."""
        scores = np.zeros(self.n_docs, dtype=np.float32)
        if not self.n_docs or not consulta_tokens:
            return scores
        unicos = set(consulta_tokens)
        for i, doc_c in enumerate(self.docs):
            dl = self.lens[i]
            if dl == 0:
                continue
            norm_len = 1.0 - self.b + self.b * (dl / self.avgdl)
            s = 0.0
            for w in unicos:
                tf = doc_c.get(w, 0)
                if tf:
                    s += self.idf.get(w, 0.0) * (tf * (self.k1 + 1.0)) / (tf + self.k1 * norm_len)
            scores[i] = s
        return scores


def _normalizar_doc(doc: str | None) -> str | None:
    if not doc:
        return None
    limpio = re.sub(r"[^A-Z]", "", str(doc).upper())
    return {
        "RIFI": "RI-FI",
        "RI": "RI-FI",
        "INGENIERIA": "RI-FI",
        "RG": "RG",
        "GENERAL": "RG",
        "CAL": "CAL",
        "CALENDARIO": "CAL",
    }.get(limpio)


def seleccionar_por_top_p(
    candidatos: list[tuple[float, float, dict[str, Any]]],
    k_max: int,
    top_p: float | None = None,
    k_min: int = 1,
    temperatura: float = 0.10,
    pool_max: int = 10,
    peso_boost_top_p: float = 0.0,
) -> list[tuple[float, dict[str, Any]]]:
    """Selecciona entre k_min y k_max candidatos hasta acumular `top_p` de masa softmax."""
    if not candidatos:
        return []
    k_lim = max(1, min(int(k_max), len(candidatos)))
    if top_p is None:
        return [(total, u) for total, _, u in candidatos[:k_lim]]

    p_obj = max(0.05, min(float(top_p), 1.0))
    k_inf = max(1, min(int(k_min), k_lim))
    pool = candidatos[: max(k_lim, min(int(pool_max), len(candidatos)))]

    temp = max(float(temperatura), 1e-4)
    w_boost = max(0.0, min(float(peso_boost_top_p), 1.0))
    logits = [base + w_boost * (total - base) for total, base, _ in pool]
    max_logit = max(logits)
    exps = [math.exp((v - max_logit) / temp) for v in logits]
    norm = sum(exps) or 1.0

    elegidos: list[tuple[float, dict[str, Any]]] = []
    acum = 0.0
    for (total, _, u), exp_v in zip(pool[:k_lim], exps[:k_lim]):
        elegidos.append((total, u))
        acum += exp_v / norm
        if len(elegidos) >= k_inf and acum >= p_obj:
            break
    return elegidos


class BuscadorNormativa:
    """Índice híbrido en memoria con caché de vectores E5 en disco."""

    def __init__(
        self,
        corpus_path: Path = DEFAULT_CORPUS_PATH,
        fragmentos_path: Path = DEFAULT_FRAGMENTOS_PATH,
        modelo_embeddings: str = "intfloat/multilingual-e5-small",
        cache_dir: Path = DEFAULT_CACHE_DIR,
        usar_embeddings: bool = True,
    ) -> None:
        self.corpus_path = Path(corpus_path)
        self.fragmentos_path = Path(fragmentos_path)
        self.modelo_embeddings = modelo_embeddings
        self.cache_dir = Path(cache_dir)
        self.usar_embeddings = usar_embeddings

        corpus = json.loads(self.corpus_path.read_text(encoding="utf-8"))
        unidades = corpus.get("unidades", [])
        self.unidades: list[dict[str, Any]] = (
            unidades if isinstance(unidades, list) else list(unidades.values())
        )
        self.fragmentos: list[dict[str, Any]] = json.loads(
            self.fragmentos_path.read_text(encoding="utf-8")
        )
        self._es_derivado = False
        self.solo_pdfs = False
        self._e5: Any = None
        self._matriz_e5: np.ndarray | None = None
        self._reconstruir_indices()

    def _reconstruir_indices(self) -> None:
        """Precomputa tabla por ID, tokens léxicos, índice BM25 e inventario de artículos."""
        self.por_id: dict[str, dict[str, Any]] = {u["id"]: u for u in self.unidades}
        self._frag_tokens_lista: list[list[str]] = [
            _tokens_clave_lista(f"{f.get('unidad_id', '')} {f.get('texto', '')}")
            for f in self.fragmentos
        ]
        self._frag_tokens: list[set[str]] = [set(t) for t in self._frag_tokens_lista]
        self._bm25 = BM25Index(self._frag_tokens_lista)
        self.inventario: dict[str, set[int]] = {}
        for u in self.unidades:
            m = re.match(r"^(RI-FI|RG)-ART-(\d+)$", u["id"])
            if m:
                self.inventario.setdefault(m.group(1), set()).add(int(m.group(2)))
        self.tiene_pdfs_usuario = any(bool(u.get("es_pdf_usuario")) for u in self.unidades)

    def _asegurar_embeddings(self) -> None:
        if (
            not self.usar_embeddings
            or self._es_derivado
            or (self._e5 is not None and self._matriz_e5 is not None)
        ):
            return
        from sentence_transformers import SentenceTransformer

        try:
            self._e5 = SentenceTransformer(
                self.modelo_embeddings, device="cpu", local_files_only=True
            )
        except Exception:
            self._e5 = SentenceTransformer(self.modelo_embeddings, device="cpu")

        sha = hashlib.sha256(self.fragmentos_path.read_bytes()).hexdigest()[:12]
        slug = re.sub(r"[^a-z0-9]+", "_", self.modelo_embeddings.lower()).strip("_")
        cache_file = self.cache_dir / f"e5_{slug}_{sha}.npz"

        if cache_file.is_file():
            datos = np.load(cache_file)
            mat = datos["vectores"]
            if mat.shape[0] == len(self.fragmentos):
                self._matriz_e5 = mat
                return

        textos = [f.get("texto_embedding") or f"passage: {f['texto']}" for f in self.fragmentos]
        mat = self._e5.encode(textos, normalize_embeddings=True, batch_size=64, show_progress_bar=False)
        mat = np.asarray(mat, dtype=np.float32)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cache_file, vectores=mat)
        self._matriz_e5 = mat

    def existe_articulo(self, doc: str, numero: int) -> dict[str, Any]:
        """Verifica si el artículo N existe en RG o RI-FI."""
        doc_norm = _normalizar_doc(doc)
        if doc_norm not in {"RG", "RI-FI"}:
            return {"doc": doc, "numero": int(numero), "existe": False, "error": "Documento inválido (use RG o RI-FI)."}
        n = int(numero)
        existe = n in self.inventario.get(doc_norm, set())
        uid = f"{doc_norm}-ART-{n:03d}" if existe else None
        return {
            "doc": doc_norm,
            "numero": n,
            "existe": existe,
            "unidad_id": uid,
            "max_articulo": max(self.inventario.get(doc_norm, {0})),
        }

    def leer_articulo(self, doc: str, numero: int) -> dict[str, Any]:
        """Devuelve el texto íntegro del artículo N en RG o RI-FI."""
        doc_norm = _normalizar_doc(doc)
        if doc_norm not in {"RG", "RI-FI"}:
            return {"id": None, "texto": None, "error": f"Documento desconocido: {doc}"}
        uid = f"{doc_norm}-ART-{int(numero):03d}"
        return self.leer_unidad(uid)

    def leer_unidad(self, unidad_id: str) -> dict[str, Any]:
        """Devuelve una unidad exacta por su ID (ej. RG-ART-028, CAL-2026-S2-02, RG-TRANS-002)."""
        u = self.por_id.get(str(unidad_id).strip().upper())
        if not u:
            return {"id": unidad_id, "texto": None, "encontrado": False}
        return {
            "id": u["id"],
            "documento": u.get("documento"),
            "paginas": u.get("paginas"),
            "texto": u["texto"],
            "encontrado": True,
        }

    def ver_calendario(self, semestre: str = "ambos") -> list[dict[str, Any]]:
        """Lista ordenadamente las entradas del Calendario 2026 (S1, S2 o ambos)."""
        sem_norm = normalizar_texto(semestre)
        filtro = None
        if any(k in sem_norm for k in ("1", "primer", "s1")):
            filtro = "1"
        elif any(k in sem_norm for k in ("2", "segund", "s2")):
            filtro = "2"

        items: list[tuple[tuple[int, int, int], dict[str, Any]]] = []
        for u in self.unidades:
            m = _CAL_ORDER_RE.match(u["id"])
            if not m:
                continue
            if filtro and m.group(2) != filtro:
                continue
            clave = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            items.append((clave, {"id": u["id"], "texto": u["texto"]}))
        items.sort(key=lambda x: x[0])
        return [it for _, it in items]

    def _referencias_cruzadas(self, unidad: dict[str, Any], max_refs: int = 2) -> list[dict[str, Any]]:
        """Detecta citas a otros artículos en el texto de una unidad para enriquecer contexto."""
        texto = unidad.get("texto", "")
        doc_origen = unidad.get("documento")
        extras: list[dict[str, Any]] = []
        for match in _ART_REF_RE.finditer(texto):
            num = int(match.group(1))
            ventana = normalizar_texto(texto[max(0, match.start() - 40) : match.end() + 50])
            doc_obj = "RG" if "reglamento general" in ventana else ("RI-FI" if "interno" in ventana else doc_origen)
            if doc_obj not in {"RG", "RI-FI"}:
                continue
            uid_ref = f"{doc_obj}-ART-{num:03d}"
            if uid_ref != unidad["id"] and uid_ref in self.por_id:
                u_ref = self.por_id[uid_ref]
                if all(e["id"] != uid_ref for e in extras):
                    extras.append({"id": uid_ref, "documento": u_ref.get("documento"), "texto": u_ref["texto"], "por_referencia_desde": unidad["id"]})
            if len(extras) >= max_refs:
                break
        return extras

    def _resolver_filtro_doc(self, documento: str | None) -> str | None:
        if not documento:
            return None
        conocido = _normalizar_doc(documento)
        if conocido:
            return conocido
        cand = str(documento).strip().upper()
        for u in self.unidades:
            doc_u = str(u.get("documento", "")).strip()
            if doc_u.upper() == cand:
                return doc_u
        return None

    def _puntuar_subconsultas_rrf(
        self,
        subconsultas: list[str],
        indices_validos: list[int],
        k_rrf: int = 10,
    ) -> dict[str, float]:
        """Fusiona rankings E5 + BM25 y subcláusulas mediante Reciprocal Rank Fusion (RRF)."""
        sims_matriz: np.ndarray | None = None
        if self.usar_embeddings:
            self._asegurar_embeddings()
            if self._e5 is not None and self._matriz_e5 is not None:
                q_vecs = self._e5.encode(
                    [f"query: {sq}" for sq in subconsultas], normalize_embeddings=True
                )
                q_arr = np.asarray(q_vecs, dtype=np.float32)
                # Producto fila a fila sin BLAS matmul para evitar warnings numéricos en ARM64
                sims_matriz = np.stack(
                    [np.sum(self._matriz_e5 * q_row, axis=1, dtype=np.float32) for q_row in q_arr],
                    axis=0,
                )

        rrf_por_uid: dict[str, float] = {}
        for sq_idx, sq in enumerate(subconsultas):
            s_bm = self._bm25.puntuar(_tokens_clave_lista(sq))
            s_e5 = sims_matriz[sq_idx] if sims_matriz is not None else None

            uid_e5: dict[str, float] = {}
            uid_bm: dict[str, float] = {}
            for idx in indices_validos:
                frag = self.fragmentos[idx]
                uid = frag.get("unidad_id") or frag.get("parent_id")
                if not uid:
                    continue
                vb = float(s_bm[idx])
                if uid not in uid_bm or vb > uid_bm[uid]:
                    uid_bm[uid] = vb
                if s_e5 is not None:
                    ve = float(s_e5[idx])
                    if uid not in uid_e5 or ve > uid_e5[uid]:
                        uid_e5[uid] = ve

            rk_bm = {u: rk for rk, (u, _) in enumerate(sorted(uid_bm.items(), key=lambda x: -x[1]), 1)}
            rk_e5 = (
                {u: rk for rk, (u, _) in enumerate(sorted(uid_e5.items(), key=lambda x: -x[1]), 1)}
                if uid_e5
                else None
            )
            for uid in uid_bm:
                rrf = 1.0 / (k_rrf + rk_bm[uid])
                if rk_e5 is not None:
                    rrf += 1.0 / (k_rrf + rk_e5[uid])
                rrf_por_uid[uid] = rrf_por_uid.get(uid, 0.0) + rrf

        rmax = max(rrf_por_uid.values(), default=1.0) or 1.0
        return {uid: val / rmax for uid, val in rrf_por_uid.items()}

    def buscar(
        self,
        consulta: str,
        k: int = 6,
        documento: str | None = None,
        expandir_citas: bool = True,
        top_p: float | None = None,
        top_k_min: int = 1,
        top_p_temp: float = 0.10,
        top_p_pool: int = 10,
        peso_boost_top_p: float = 0.0,
        modo_fusion: str = "lineal",
        k_rrf: int = 10,
        usar_descomposicion: bool = False,
    ) -> list[dict[str, Any]]:
        """Búsqueda híbrida (lineal o BM25+E5 RRF + subcláusulas) con corte Top-k o Top-p."""
        k = max(1, min(int(k), 12))
        doc_filtro = self._resolver_filtro_doc(documento)
        q_tokens = _tokens_clave(consulta)
        q_norm = normalizar_texto(consulta)

        art_menciones = [int(m.group(1)) for m in _ART_REF_RE.finditer(consulta)]
        ids_boost: set[str] = set()
        for num in art_menciones:
            for d in ([doc_filtro] if doc_filtro in {"RG", "RI-FI"} else ["RG", "RI-FI"]):
                ids_boost.add(f"{d}-ART-{num:03d}")
        if "transitorio" in q_norm:
            for num in art_menciones or [1, 2]:
                ids_boost.add(f"RG-TRANS-{num:03d}")

        indices_validos: list[int] = []
        for idx, frag in enumerate(self.fragmentos):
            uid = frag.get("unidad_id") or frag.get("parent_id")
            u = self.por_id.get(uid)
            if not u:
                continue
            if doc_filtro and u.get("documento") != doc_filtro:
                continue
            indices_validos.append(idx)

        if not indices_validos:
            return []

        mejores_por_uid: dict[str, tuple[float, float, dict[str, Any]]] = {}
        es_compuesta = False
        if modo_fusion == "rrf":
            subconsultas, es_compuesta = (
                descomponer_subconsultas(consulta) if usar_descomposicion else ([consulta], False)
            )
            bases = self._puntuar_subconsultas_rrf(subconsultas, indices_validos, k_rrf=k_rrf)
            for uid, base in bases.items():
                u = self.por_id[uid]
                boost = 0.45 if uid in ids_boost else 0.0
                if doc_filtro is None and "calendario" in q_norm and u.get("documento") == "CAL":
                    boost += 0.15
                mejores_por_uid[uid] = (base + boost, base, u)
        else:
            sims_e5: np.ndarray | None = None
            if self.usar_embeddings:
                self._asegurar_embeddings()
                if self._e5 is not None and self._matriz_e5 is not None:
                    q_vec = self._e5.encode([f"query: {consulta}"], normalize_embeddings=True)[0]
                    q_arr = np.asarray(q_vec, dtype=np.float32)
                    raw = np.sum(self._matriz_e5 * q_arr, axis=1, dtype=np.float32)
                    rmin, rmax = float(raw.min()), float(raw.max())
                    sims_e5 = (raw - rmin) / (rmax - rmin + 1e-8)

            denom = max(1, len(q_tokens))
            for idx in indices_validos:
                frag = self.fragmentos[idx]
                uid = frag.get("unidad_id") or frag.get("parent_id")
                u = self.por_id[uid]
                lex = len(q_tokens & self._frag_tokens[idx]) / denom if q_tokens else 0.0
                boost = 0.45 if uid in ids_boost else 0.0
                if doc_filtro is None and "calendario" in q_norm and u.get("documento") == "CAL":
                    boost += 0.15

                base = 0.65 * float(sims_e5[idx]) + 0.35 * lex if sims_e5 is not None else lex
                score = base + boost
                prev = mejores_por_uid.get(uid)
                if prev is None or score > prev[0]:
                    mejores_por_uid[uid] = (score, base, u)

        k_min_ef = max(int(top_k_min), 2) if es_compuesta else int(top_k_min)
        ordenados = sorted(mejores_por_uid.values(), key=lambda par: -par[0])
        seleccionados = seleccionar_por_top_p(
            ordenados,
            k_max=k,
            top_p=top_p,
            k_min=k_min_ef,
            temperatura=top_p_temp,
            pool_max=top_p_pool,
            peso_boost_top_p=peso_boost_top_p,
        )
        salida: list[dict[str, Any]] = []
        vistos: set[str] = set()
        for score, u in seleccionados:
            vistos.add(u["id"])
            salida.append(
                {
                    "id": u["id"],
                    "documento": u.get("documento"),
                    "paginas": u.get("paginas"),
                    "relevancia": round(float(score), 4),
                    "texto": u["texto"],
                }
            )

        if expandir_citas and salida:
            extras: list[dict[str, Any]] = []
            for item in salida[:2]:
                u_orig = self.por_id[item["id"]]
                for ref in self._referencias_cruzadas(u_orig, max_refs=1):
                    if ref["id"] not in vistos:
                        vistos.add(ref["id"])
                        extras.append(ref)
            salida.extend(extras[:2])

            semestres_cal: list[str] = []
            for item in salida[:3]:
                m_cal = _CAL_ORDER_RE.match(item["id"])
                if m_cal and m_cal.group(2) not in semestres_cal:
                    semestres_cal.append(m_cal.group(2))
            for sem in semestres_cal:
                for cal_item in self.ver_calendario(sem):
                    if cal_item["id"] not in vistos:
                        vistos.add(cal_item["id"])
                        salida.append(
                            {
                                "id": cal_item["id"],
                                "documento": "CAL",
                                "texto": cal_item["texto"],
                                "por_referencia_desde": f"calendario_s{sem}",
                            }
                        )

        return salida

    def con_pdfs_usuario(
        self,
        packs_pdf: list[dict[str, Any]],
        incluir_corpus_base: bool = True,
    ) -> "BuscadorNormativa":
        """Crea un buscador en memoria combinando (o aislando) PDFs cargados por el usuario."""
        if not packs_pdf and incluir_corpus_base:
            return self

        if self.usar_embeddings:
            self._asegurar_embeddings()

        unidades: list[dict[str, Any]] = list(self.unidades) if incluir_corpus_base else []
        fragmentos: list[dict[str, Any]] = list(self.fragmentos) if incluir_corpus_base else []
        matrices: list[np.ndarray] = []
        if (
            incluir_corpus_base
            and self.usar_embeddings
            and self._matriz_e5 is not None
            and len(self.fragmentos)
        ):
            matrices.append(np.asarray(self._matriz_e5, dtype=np.float32))

        shas_vistos: set[str] = set()
        if packs_pdf:
            from .pdfs import cargar_o_calcular_vectores_pdf

            for pack in packs_pdf:
                sha = str(pack.get("sha256", ""))
                if sha and sha in shas_vistos:
                    continue
                if sha:
                    shas_vistos.add(sha)

                u_pack = list(pack.get("unidades") or [])
                f_pack = list(pack.get("fragmentos") or [])
                if not f_pack:
                    continue

                if self.usar_embeddings and self._e5 is not None:
                    mat_pdf = cargar_o_calcular_vectores_pdf(pack, self._e5, self.cache_dir)
                    if mat_pdf.ndim == 2 and mat_pdf.shape[0] == len(f_pack):
                        matrices.append(np.asarray(mat_pdf, dtype=np.float32))
                unidades.extend(u_pack)
                fragmentos.extend(f_pack)

        nuevo = BuscadorNormativa.__new__(BuscadorNormativa)
        nuevo.corpus_path = self.corpus_path
        nuevo.fragmentos_path = self.fragmentos_path
        nuevo.modelo_embeddings = self.modelo_embeddings
        nuevo.cache_dir = self.cache_dir
        nuevo.usar_embeddings = self.usar_embeddings
        nuevo._es_derivado = True
        nuevo.solo_pdfs = not incluir_corpus_base
        nuevo._e5 = self._e5
        nuevo.unidades = unidades
        nuevo.fragmentos = fragmentos
        if matrices:
            nuevo._matriz_e5 = np.vstack(matrices) if len(matrices) > 1 else matrices[0]
        else:
            nuevo._matriz_e5 = None
        nuevo._reconstruir_indices()
        return nuevo
