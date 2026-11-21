"""Buscador híbrido (embeddings E5 + léxico + referencias cruzadas) sobre corpus.json."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
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


def _tokens_clave(texto: str) -> set[str]:
    return {t for t in normalizar_texto(texto).split() if t not in _STOPWORDS_ES and len(t) > 1}


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
        self.por_id: dict[str, dict[str, Any]] = {u["id"]: u for u in self.unidades}
        self.fragmentos: list[dict[str, Any]] = json.loads(
            self.fragmentos_path.read_text(encoding="utf-8")
        )

        # Precomputar tokens léxicos por fragmento y unidad
        self._frag_tokens: list[set[str]] = [
            _tokens_clave(f"{f.get('unidad_id', '')} {f.get('texto', '')}")
            for f in self.fragmentos
        ]
        self.inventario: dict[str, set[int]] = {}
        for u in self.unidades:
            m = re.match(r"^(RI-FI|RG)-ART-(\d+)$", u["id"])
            if m:
                self.inventario.setdefault(m.group(1), set()).add(int(m.group(2)))

        self._e5: Any = None
        self._matriz_e5: np.ndarray | None = None

    def _asegurar_embeddings(self) -> None:
        if not self.usar_embeddings or (self._e5 is not None and self._matriz_e5 is not None):
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

    def buscar(
        self,
        consulta: str,
        k: int = 6,
        documento: str | None = None,
        expandir_citas: bool = True,
    ) -> list[dict[str, Any]]:
        """Búsqueda híbrida (E5 + léxica + boost por artículo) filtrable por documento."""
        k = max(1, min(int(k), 12))
        doc_filtro = _normalizar_doc(documento)
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

        sims_e5: np.ndarray | None = None
        if self.usar_embeddings:
            self._asegurar_embeddings()
            if self._e5 is not None and self._matriz_e5 is not None:
                q_vec = self._e5.encode([f"query: {consulta}"], normalize_embeddings=True)[0]
                q_arr = np.asarray(q_vec, dtype=np.float32)
                raw = np.sum(self._matriz_e5 * q_arr, axis=1, dtype=np.float32)
                rmin, rmax = float(raw.min()), float(raw.max())
                sims_e5 = (raw - rmin) / (rmax - rmin + 1e-8)

        mejores_por_uid: dict[str, tuple[float, dict[str, Any]]] = {}
        denom = max(1, len(q_tokens))
        for idx, frag in enumerate(self.fragmentos):
            uid = frag.get("unidad_id") or frag.get("parent_id")
            u = self.por_id.get(uid)
            if not u:
                continue
            if doc_filtro and u.get("documento") != doc_filtro:
                continue

            lex = len(q_tokens & self._frag_tokens[idx]) / denom if q_tokens else 0.0
            boost = 0.45 if uid in ids_boost else 0.0
            if doc_filtro is None and "calendario" in q_norm and u.get("documento") == "CAL":
                boost += 0.15

            if sims_e5 is not None:
                score = 0.65 * float(sims_e5[idx]) + 0.35 * lex + boost
            else:
                score = lex + boost

            prev = mejores_por_uid.get(uid)
            if prev is None or score > prev[0]:
                mejores_por_uid[uid] = (score, u)

        ordenados = sorted(mejores_por_uid.values(), key=lambda par: -par[0])
        salida: list[dict[str, Any]] = []
        vistos: set[str] = set()
        for score, u in ordenados[:k]:
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
