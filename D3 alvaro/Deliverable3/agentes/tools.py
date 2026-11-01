"""Herramientas de los agentes (D3), ancladas en el corpus real del E2.
Las herramientas son funciones que el modelo pide y la aplicación ejecuta.
`buscar` admite inyectar el recuperador E5 real; si no, usa un respaldo léxico."""
import json, re, unicodedata
from pathlib import Path

def _norm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ ]", " ", s)

class Corpus:
    def __init__(self, directorio):
        d = Path(directorio)
        self.corpus = json.loads((d / "corpus.json").read_text(encoding="utf-8"))
        self.frag = json.loads((d / "fragmentos_busqueda.json").read_text(encoding="utf-8"))
        U = self.corpus["unidades"]
        self.unidades = U if isinstance(U, list) else list(U.values())
        self.por_id = {u["id"]: u for u in self.unidades}
        # inventario real de artículos por documento
        self.inventario = {}
        for u in self.unidades:
            m = re.match(r"(RI-FI|RG)-ART-(\d+)", u["id"])
            if m:
                self.inventario.setdefault(m.group(1), set()).add(int(m.group(2)))

    # ---- Herramienta: existe_articulo(doc, n) -> bool ----
    def existe_articulo(self, doc, n):
        return int(n) in self.inventario.get(doc, set())

    # ---- Herramienta: traer_articulo(doc, n) -> texto completo ----
    def traer_articulo(self, doc, n):
        uid = f"{doc}-ART-{int(n):03d}"
        u = self.por_id.get(uid)
        return {"id": uid, "texto": u["texto"]} if u else {"id": uid, "texto": None}

    # ---- Herramienta: buscar(consulta, k) -> top-k fragmentos ----
    # Respaldo léxico (overlap de tokens). En Colab se reemplaza por el recuperador E5.
    def buscar(self, consulta, k=5):
        q = set(_norm(consulta).split())
        res = []
        for f in self.frag:
            t = set(_norm(f["texto"]).split())
            score = len(q & t) / (len(q) + 1)
            if score > 0:
                res.append((score, f))
        res.sort(key=lambda x: -x[0])
        vistos, salida = set(), []
        for _, f in res:
            uid = f.get("unidad_id") or f.get("parent_id")
            if uid in vistos:
                continue
            vistos.add(uid)
            u = self.por_id.get(uid, {})
            salida.append({"id": uid, "texto": u.get("texto", f["texto"])})
            if len(salida) >= k:
                break
        return salida
