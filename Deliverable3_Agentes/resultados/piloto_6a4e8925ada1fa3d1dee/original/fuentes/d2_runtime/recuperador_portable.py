# Generado por crear_sistema.py a partir del recuperador evaluado. No editar a mano.

import json
import re
import unicodedata
import numpy as np

def require(condition, message):
    if not condition:
        raise ValueError(message)

def rank_vectors(document_vectors, query_vectors):
    require(document_vectors.ndim == query_vectors.ndim == 2, "Vectores deben ser matrices")
    require(document_vectors.shape[1] == query_vectors.shape[1], "Dimensiones incompatibles")
    for vectors in (document_vectors, query_vectors):
        require(bool(np.isfinite(vectors).all()), "Vectores no finitos")
        require(bool(np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5)), "Se requieren vectores normalizados")
    # Para este índice pequeño basta la contracción directa; evita avisos numéricos
    # espurios observados con BLAS/Accelerate en el equipo de reproducción.
    scores = np.einsum("ij,kj->ik", query_vectors, document_vectors, optimize=False)
    require(bool(np.isfinite(scores).all()), "Similitudes no finitas")
    require(bool((np.abs(scores) <= 1.00001).all()), "Similitudes fuera del rango del coseno")
    return scores, np.argsort(-scores, axis=1, kind="stable")

POLICY = {"top_original": 5, "top_por_subconsulta": 2, "max_subconsultas": 4,
          "max_unidades": 14, "max_caracteres": 20000, "saltos_remisiones": 1}

def normal(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")

def subqueries(question):
    pieces = re.split(r"[¿?;]|,?\s+y\s+(?=(?:cu[aá]l(?:es)?|cu[aá]nt(?:o|a|os|as)|cu[aá]ndo|qu[eé]|hasta|c[oó]mo)\b)", question, flags=re.I)
    pieces = [p.strip(" ,.") for p in pieces if len(p.strip(" ,.")) >= 15]
    if len(pieces) < 2:
        return []
    return list(dict.fromkeys(pieces))[:POLICY["max_subconsultas"]]

def named_documents(text):
    t = normal(text)
    docs = []
    if "ri-fi" in t or "reglamento interno" in t or "ingenieria" in t:
        docs.append("RI-FI")
    if "reglamento general" in t or re.search(r"\brg\b", t):
        docs.append("RG")
    return docs

def exact_articles(question, corpus):
    docs = named_documents(question)
    numbers = [int(m[1]) for m in re.finditer(r"art[ií]culo\s+(\d+)\b", question, re.I)]
    if len(docs) != 1 or not numbers:
        return [], []  # No adivinar qué documento nombra una cita ambigua.
    doc = docs[0]
    requested_scope = "transitorio" if "transitori" in normal(question) else "ordinario"
    articles = [p for p in corpus["padres"] if p["documento"] == doc and p["tipo"] == "articulo" and p["ambito"] == requested_scope]
    inventory = sorted(p["articulo"] for p in articles)
    by_number = {p["articulo"]: p for p in articles}
    found, checks = [], []
    for number in dict.fromkeys(numbers):
        exists = number in by_number
        if exists:
            # Un artículo puede tener varias unidades (glosario); no seleccionar solo su introducción.
            found.extend(u["id"] for u in corpus["unidades"] if u["parent_id"] == by_number[number]["id"])
        checks.append({"tipo": "articulo", "documento": doc, "ambito": requested_scope,
                       "numero_consultado": number, "existe": exists, "inventario_numeros": inventory,
                       "fuente": corpus["fuentes"][doc]})
    return found, checks

def holiday_inventory(question, corpus):
    t = normal(question)
    if "feriado" not in t or "calendario" not in t:
        return []
    dates = re.findall(r"\b(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b", t)
    years = re.findall(r"\b20\d{2}\b", t)
    events = [p for p in corpus["padres"] if p["tipo"] == "evento"]
    require(bool(events), "Calendario vacío")
    available_years = sorted({p["anio"] for p in events})
    if len(dates) != 1 or not years or any(int(y) not in available_years for y in years):
        return []
    holidays = [p for p in events if "feriado nacional" in normal(p["evento"])]
    day, month = dates[0]
    candidates = []
    for event in holidays:
        m = re.search(r"\b(\d{1,2})\s+de\s+(\w+)", normal(event["fecha"]))
        require(m is not None, "Feriado con formato no reconocido; no certificar ausencia")
        if int(m[1]) == int(day) and m[2] == month:
            candidates.append(event["id"])
    return [{"tipo": "feriado", "anio": int(years[0]), "dia": int(day), "mes": month,
             "coincidencias": candidates, "eventos_calendario_revisados": len(events),
             "inventario_feriados": [{"unidad_id": p["id"], "fecha": p["fecha"], "pagina": p["paginas"][0]} for p in holidays],
             "fuente": corpus["fuentes"]["CAL"]}]

def references(unit, parents, available):
    parent = parents[unit["parent_id"]]
    if parent["tipo"] != "articulo":
        return []
    targets = []
    for match in re.finditer(r"art[ií]culo\s+(\d+)\b", unit["texto"], re.I):
        if match.start() == 0:  # Encabezado, no remisión.
            continue
        following = normal(unit["texto"][match.end():match.end() + 100]).split(".")[0]
        if "estatutos" in following or "otro reglamento" in following:
            continue
        doc = "RG" if "reglamento general" in following else parent["documento"]
        identifier = f"{doc}-ART-{int(match[1]):03}"
        if identifier in available and identifier != parent["id"]:
            targets.append(identifier)
    return list(dict.fromkeys(targets))

def make_contexts(question, corpus, original_ids, subrankings):
    units = {u["id"]: u for u in corpus["unidades"]}
    parents = {p["id"]: p for p in corpus["padres"]}
    exact, checks = exact_articles(question, corpus)
    checks += holiday_inventory(question, corpus)
    candidates = []
    def add(identifier, reason):
        candidates.append({"unidad_id": identifier, "motivo": reason})
    for uid in exact:
        add(uid, "cita_explicita_en_pregunta")
    # Priorizar primer resultado de cada parte evita que una sola domine el contexto.
    for i, ranking in enumerate(subrankings):
        for uid in ranking[:POLICY["top_por_subconsulta"]]:
            add(uid, f"subconsulta_{i + 1}")
    for uid in original_ids[:POLICY["top_original"]]:
        add(uid, "consulta_original")
    for uid in list(dict.fromkeys(c["unidad_id"] for c in candidates)):
        for target in references(units[uid], parents, units):
            add(target, "remision_desde:" + uid)
    contexts, omitted, seen = [], [], set()
    used = 0
    for candidate in candidates:
        uid = candidate["unidad_id"]
        if uid in seen:
            continue
        seen.add(uid)
        u, p = units[uid], parents[units[uid]["parent_id"]]
        if len(contexts) >= POLICY["max_unidades"] or used + len(u["texto"]) > POLICY["max_caracteres"]:
            omitted.append({**candidate, "motivo_omision": "presupuesto; no se corta texto"})
            continue
        contexts.append({**candidate, "parent_id": p["id"], "texto": u["texto"], "cita": p["cita"],
                         "archivo": p["archivo"], "sha256_pdf": p["sha256_pdf"]})
        used += len(u["texto"])
    # Evidencia estructural calculada desde TODO el corpus validado, no desde top-k.
    inventories = []
    for check in checks:
        source = check["fuente"]
        inventories.append({"tipo": check["tipo"], "archivo": source["archivo"], "sha256_pdf": source["sha256"],
                            "texto": json.dumps(check, ensure_ascii=False, sort_keys=True)})
    return {"contextos": contexts, "comprobaciones_estructurales": checks, "contextos_inventario": inventories,
            "candidatos": candidates, "omitidos_por_presupuesto": omitted,
            "caracteres_contexto": used + sum(len(c["texto"]) for c in inventories)}
