"""Recuperación con citas exactas, subconsultas e inventarios; no lee la pauta."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import unicodedata

import numpy as np

from probar_recuperacion import ROOT, REVISION, TOKENIZER_SHA256, load_inputs, rank_vectors, read, require, sha, write

POLICY = {"top_original": 5, "top_por_subconsulta": 2, "max_subconsultas": 4,
          "max_unidades": 14, "max_caracteres": 20000, "saltos_remisiones": 1}


def normal(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")


def subqueries(question):
    pieces = re.split(r"[¿?;]|,?\s+y\s+(?=(?:cu[aá]l|cu[aá]nt|cu[aá]ndo|qu[eé]|hasta|c[oó]mo)\b)", question, flags=re.I)
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path(__file__).parent / "resultados/e5_top5_v1")
    parser.add_argument("--salida", type=Path, default=Path(__file__).parent / "resultados/e5_estructurado_v2")
    parser.add_argument("--modelo-local", type=Path, default=Path.home() / ".cache/huggingface/hub/models--intfloat--multilingual-e5-small/snapshots" / REVISION)
    args = parser.parse_args()
    require(not args.salida.exists(), "Usar una salida nueva; las corridas se conservan")
    manifest = read(args.base / "manifiesto.json")
    for filename, expected in manifest["artefactos_sha256"].items():
        require(sha(args.base / filename) == expected, "Corrida base alterada")
    corpus_dir = ROOT / "Deliverable2/corpus/generado"
    corpus, fragments, questions = load_inputs(corpus_dir, ROOT / "Deliverable1/datos/test_set_50.csv")
    baseline = read(args.base / "recuperacion.json")
    require(baseline["fuentes_sha256"]["corpus"] == sha(corpus_dir / "corpus.json"), "Corpus distinto a la base")
    require(baseline["fuentes_sha256"]["fragmentos"] == sha(corpus_dir / "fragmentos_busqueda.json"), "Fragmentos distintos a la base")
    require(baseline["fragmentos_orden_indice"] == [f["id"] for f in fragments], "Orden de índice distinto")
    require(sha(args.modelo_local / "tokenizer.json") == TOKENIZER_SHA256, "Tokenizador incorrecto")
    for filename, expected in manifest["archivos_modelo_sha256"].items():
        require(sha(args.modelo_local / filename) == expected, "Modelo distinto al de los vectores base")
    from sentence_transformers import SentenceTransformer
    import torch
    torch.set_num_threads(4)
    torch.manual_seed(0)
    model = SentenceTransformer(str(args.modelo_local), device="cpu", local_files_only=True)
    decomposed = [subqueries(q["pregunta"]) for q in questions]
    texts = list(dict.fromkeys(t for parts in decomposed for t in parts))
    encoded_texts = ["query: " + text for text in texts]
    require(all(len(model.tokenizer(t, truncation=False)["input_ids"]) <= 512 for t in encoded_texts), "Subconsulta demasiado larga")
    vectors = model.encode(encoded_texts, normalize_embeddings=True, batch_size=16, show_progress_bar=False)
    docs = np.load(args.base / "vectores_documentos.npy", allow_pickle=False)
    scores, orders = rank_vectors(docs, vectors)
    rankings = {}
    for i, text in enumerate(texts):
        rankings[text] = [{"fragmento_id": fragments[int(fi)]["id"], "unidad_id": fragments[int(fi)]["unidad_id"], "similitud": float(scores[i, fi])} for fi in orders[i]]
    cases = []
    for q, original, parts in zip(questions, baseline["casos"], decomposed):
        require(q["pregunta"] == original["pregunta"], "Pregunta distinta a la base")
        original_ids = [r["unidad_id"] for r in original["ranking"]]
        subrankings = [[r["unidad_id"] for r in rankings[t]] for t in parts]
        result = make_contexts(q["pregunta"], corpus, original_ids, subrankings)
        cases.append({**q, "subconsultas": [{"texto": t, "ranking": rankings[t]} for t in parts],
                      "ranking_original": original["ranking"], **result})
    args.salida.mkdir(parents=True)
    output = {"version": 2, "configuracion": {**baseline["configuracion"], "politica": POLICY,
              "expansion": "citas exactas, partes de pregunta, remisiones de un salto e inventarios", "sin_reescritura_consultas": False},
              "fuentes_sha256": baseline["fuentes_sha256"], "corrida_base_sha256": sha(args.base / "recuperacion.json"), "casos": cases}
    write(args.salida / "recuperacion.json", output)
    np.save(args.salida / "vectores_subconsultas.npy", vectors, allow_pickle=False)
    write(args.salida / "subconsultas.json", texts)
    write(args.salida / "manifiesto.json", {"script_sha256": sha(__file__), "dependencias_sha256": {n: sha(Path(__file__).parent / n) for n in ("probar_recuperacion.py",)},
          "modelo_y_versiones": manifest, "artefactos_sha256": {n: sha(args.salida / n) for n in ("recuperacion.json", "vectores_subconsultas.npy", "subconsultas.json")}})
    print(f"Guardadas {len(cases)} consultas con {len(texts)} subconsultas diferentes en {args.salida}")


if __name__ == "__main__":
    main()
