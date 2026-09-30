"""Extracción verificable de los tres PDF del proyecto; no utiliza preguntas ni respuestas.

Los fragmentos de búsqueda NO se entregan aislados al generador: se recupera
su unidad completa (artículo, definición numerada, evento o fila del anexo).
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re

import pdfplumber
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "RI-FI": "Reglamento_de_Docencia_de_Pregrado-FI.pdf",
    "RG": "Reglamento_General_de_Docencia_de_Pregrado.pdf",
    "CAL": "Calendario-Academico-Pregrado-2026.pdf",
}
MODEL = "intfloat/multilingual-e5-small"
REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
TOKENIZER_SHA256 = "0b44a9d7b51c3c62626640cda0e2c2f70fdacdc25bbbd68038369d14ebdf4c39"
ARTICLE = re.compile(r"^Artículo\s+(\d+)[°º]", re.I)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compact(text):
    return re.sub(r"\s+", " ", text or "").strip()


def render_lines(lines):
    text = ""
    previous = None
    for line in lines:
        value = line["texto"]
        if text and re.search(r"[a-záéíóúüñ]-$", text, re.I) and re.match(r"[a-záéíóúüñ]", value):
            text = text[:-1] + value
        else:
            paragraph = previous and previous["pagina"] == line["pagina"] and line["bbox"][1] - previous["bbox"][3] > 8
            text += ("\n\n" if paragraph else " ") + value
        previous = line
    return text.strip()


def source_line(doc, page, index, line, purpose):
    return {
        "id": f"{doc}:p{page}:l{index}", "documento": doc,
        "pagina": page, "bbox": [round(line[k], 3) for k in ("x0", "top", "x1", "bottom")],
        "texto": line["text"], "destino": purpose,
    }


def parse_regulation(path, doc):
    parents, ledger, headings = [], [], []
    current = None
    scope = "ordinario"
    preamble = []
    with pdfplumber.open(path) as pdf:
        require(len(pdf.pages) == (34 if doc == "RG" else 6), f"Cambió el número de páginas de {doc}")
        for page_num, page in enumerate(pdf.pages, 1):
            for index, line in enumerate(page.extract_text_lines(x_tolerance=2, y_tolerance=3), 1):
                value = line["text"].strip()
                entry = source_line(doc, page_num, index, line, None)
                ledger.append(entry)
                if doc == "RG" and page_num in (1, 34):
                    entry["destino"] = "metadatos:portada"; continue
                if value.startswith("REGLAMENTO GENERAL DE DOCENCIA DE PREGRADO / DECRETO") and line["top"] < 80:
                    entry["destino"] = "metadatos:encabezado_repetido"; continue
                if value.isdigit() and line["bottom"] > page.height - 35:
                    entry["destino"] = "metadatos:numero_pagina"; continue
                if doc == "RG" and page_num == 33:
                    entry["destino"] = "anexo:tabla_extraida_por_celdas"; continue
                if doc == "RI-FI" and value in ("Facultad de Ingeniería – Universidad de Concepción", "Agosto de 2022"):
                    entry["destino"] = "metadatos:pie_documento"; continue
                chars = [c for c in line["chars"] if c["text"].strip()]
                bold = lambda c: "bold" in c["fontname"].lower()
                match = ARTICLE.match(value)
                # Una referencia al inicio de una línea NO es un encabezado de artículo.
                is_article = match and all(bold(c) for c in sorted(chars, key=lambda c: c["x0"])[:8])
                if value == "DISPOSICIONES TRANSITORIAS":
                    scope = "transitorio"
                if is_article:
                    number = int(match[1])
                    prefix = "TRANS" if scope == "transitorio" else "ART"
                    identifier = f"{doc}-{prefix}-{number:03}"
                    current = {"id": identifier, "documento": doc, "tipo": "articulo", "ambito": scope,
                               "articulo": number, "encabezados": headings[:], "lineas": []}
                    headings.clear()
                    parents.append(current)
                elif chars and value.upper() == value and all(bold(c) for c in chars):
                    entry["destino"] = "estructura:encabezado"
                    headings.append(value)
                    continue
                if current:
                    entry["destino"] = current["id"]
                    current["lineas"].append(entry)
                else:
                    entry["destino"] = f"{doc}-PREAMBULO"
                    preamble.append(entry)
    expected = 60 if doc == "RG" else 35
    for kind, count in (("ordinario", expected), ("transitorio", 2 if doc == "RG" else 0)):
        actual = [p["articulo"] for p in parents if p["ambito"] == kind]
        require(actual == list(range(1, count + 1)), f"Artículos fuera de secuencia en {doc}/{kind}: {actual}")
    if preamble:
        parents.insert(0, {"id": f"{doc}-PREAMBULO", "documento": doc, "tipo": "preambulo", "lineas": preamble})
    for parent in parents:
        parent["texto"] = render_lines(parent["lineas"])
        parent["paginas"] = sorted({l["pagina"] for l in parent["lineas"]})
        require(bool(parent["texto"]), f"Unidad vacía: {parent['id']}")
    return parents, ledger


def parse_calendar(path):
    parents, ledger = [], []
    with pdfplumber.open(path) as pdf:
        require(len(pdf.pages) == 2, "El calendario debe tener dos páginas")
        for page_num, page in enumerate(pdf.pages, 1):
            semester = "Primer" if page_num == 1 else "Segundo"
            require(f"{semester.upper()} SEMESTRE 2026" in page.extract_text(), "Semestre/año de calendario inesperado")
            tables = page.find_tables()
            require(len(tables) == 2, "Cambió la estructura de tablas del calendario")
            records = []
            for table_num, table in enumerate(tables, 1):
                table_records = []
                extracted_cells = table.extract()
                for row_num, (cells, row) in enumerate(zip(extracted_cells, table.rows), 1):
                    event = compact(" ".join(c for c in cells[:-1] if c))
                    date = compact(cells[-1])
                    raw = {"tabla": table_num, "fila": row_num, "celdas": cells, "bbox": list(row.bbox)}
                    if date:
                        require(bool(event), "Fecha sin evento")
                        table_records.append({"evento": event, "fecha": date, "filas_origen": [raw]})
                    else:
                        require(bool(event) and bool(table_records), "Fila de calendario sin asociación inequívoca")
                        table_records[-1]["evento"] += " " + event
                        table_records[-1]["filas_origen"].append(raw)
                source_words = Counter(" ".join(c for row in extracted_cells for c in row if c).split())
                result_words = Counter(" ".join(r["evento"] + " " + r["fecha"] for r in table_records).split())
                require(source_words == result_words, "Se perdió o duplicó texto de las celdas del calendario")
                records.extend(table_records)
            require(len(records) == (14 if page_num == 1 else 11), "Número inesperado de eventos")
            for i, record in enumerate(records, 1):
                identifier = f"CAL-2026-S{page_num}-{i:02}"
                parents.append({"id": identifier, "documento": "CAL", "tipo": "evento", "paginas": [page_num],
                                "semestre": page_num, "anio": 2026, **record,
                                "texto": f"Calendario de docencia de pregrado 2026. {semester} semestre. {record['evento']}: {record['fecha']}."})
            # Conserva además el texto ajeno a las tablas para inspeccionar títulos y notas.
            for i, line in enumerate(page.extract_text_lines(x_tolerance=2, y_tolerance=3), 1):
                inside = any(t.bbox[1] <= (line["top"] + line["bottom"]) / 2 <= t.bbox[3] for t in tables)
                ledger.append(source_line("CAL", page_num, i, line, "calendario:tabla_extraida_por_celdas" if inside else "metadatos:calendario"))
    return parents, ledger


def parse_annex(path):
    parents = []
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[32]
        table = max(page.find_tables(), key=lambda t: len(t.rows))
        rows = table.extract()
        require(len(rows) == 52, "Cambió la tabla de equivalencia de notas")
        concept_x = table.rows[2].cells[-1][0] if table.rows[2].cells[-1] else table.rows[0].cells[-1][0]
        concept_cells = [c for c in table.cells if abs(c[0] - concept_x) < 0.1]
        for i, (row, geometry) in enumerate(zip(rows[2:], table.rows[2:]), 1):
            require(int(row[0]) == i and int(row[2]) == i + 50, "Fila incompleta/desordenada del anexo")
            center = (geometry.bbox[1] + geometry.bbox[3]) / 2
            cells = [c for c in concept_cells if c[1] <= center < c[3]]
            require(len(cells) == 1, "Celda combinada de concepto ambigua")
            concept = compact(page.crop(cells[0]).extract_text())
            text = (f"Anexo: equivalencia de escalas de notas. Reprobación: {row[0]} en escala de 1 a 100 equivale a {row[1]} en escala de 1,0 a 7,0. "
                    f"Aprobación: {row[2]} en escala de 1 a 100 equivale a {row[3]} en escala de 1,0 a 7,0. "
                    + (f"Concepto en el título o grado: {concept}." if concept else "La celda de concepto está vacía en el documento."))
            parents.append({"id": f"RG-ANEXO-{i:02}", "documento": "RG", "tipo": "fila_anexo", "paginas": [33],
                            "texto": text, "celdas_origen": row, "bbox": list(geometry.bbox), "concepto": concept,
                            "bbox_concepto": list(cells[0])})
    return parents


def make_units(parents):
    units = []
    for parent in parents:
        text = parent["texto"]
        # El artículo 3 contiene un glosario de siete páginas. Recuperar una definición
        # completa evita incorporar todas las definiciones ajenas a la pregunta.
        if parent["id"] == "RG-ART-003":
            matches = list(re.finditer(r"(?<!\S)3\.(\d+)\.\s+[A-ZÁÉÍÓÚÑ]", text))
            require([int(m[1]) for m in matches] == list(range(1, 25)), "Glosario incompleto")
            spans = [(0, matches[0].start(), "INTRO")]
            spans += [(m.start(), matches[i + 1].start() if i + 1 < len(matches) else len(text), f"DEF-{int(m[1]):02}") for i, m in enumerate(matches)]
        else:
            spans = [(0, len(text), None)]
        for start, end, suffix in spans:
            identifier = parent["id"] + ("-" + suffix if suffix else "")
            units.append({"id": identifier, "parent_id": parent["id"], "documento": parent["documento"],
                          "paginas": parent["paginas"], "inicio": start, "fin": end, "texto": text[start:end]})
    return units


def citation(parent):
    if parent["tipo"] == "articulo":
        label = f"artículo {parent['articulo']}" + (" transitorio" if parent["ambito"] == "transitorio" else "")
    elif parent["tipo"] == "evento":
        label = f"calendario 2026, semestre {parent['semestre']}"
    elif parent["tipo"] == "fila_anexo":
        label = "anexo de equivalencia de notas"
    else:
        label = "preámbulo"
    return f"{parent['documento']}, {label}, PDF p. {', '.join(map(str, parent['paginas']))}"


def make_fragments(units, parents, tokenizer, limit):
    parent_map = {p["id"]: p for p in parents}
    fragments = []
    for unit in units:
        parent = parent_map[unit["parent_id"]]
        header = f"[{unit['id']} | {parent['cita']}]\n"
        text = unit["texto"]
        start, index = 0, 0
        while start < len(text):
            # Busca el mayor prefijo seguro en límites de palabra; luego prefiere
            # párrafo/frase si ocupa al menos la mitad de ese espacio.
            ends = [m.end() for m in re.finditer(r"\S+\s*", text[start:])]
            ends = [start + end for end in ends]
            low, high, best = 0, len(ends) - 1, None
            while low <= high:
                mid = (low + high) // 2
                size = len(tokenizer.encode("passage: " + header + text[start:ends[mid]]).ids)
                if size <= limit:
                    best = ends[mid]; low = mid + 1
                else:
                    high = mid - 1
            require(best is not None, f"Una palabra/encabezado supera el presupuesto: {unit['id']}")
            end = best
            if end < len(text):
                preferred = [start + m.end() for m in re.finditer(r"\n\n|[.!?;]\s+", text[start:end])]
                preferred = [p for p in preferred if p >= start + (end - start) / 2]
                if preferred:
                    end = preferred[-1]
            fragment = text[start:end]
            payload = "passage: " + header + fragment
            count = len(tokenizer.encode(payload).ids)
            require(count <= limit, "Un fragmento excede el límite real del tokenizador")
            index += 1
            fragments.append({"id": f"{unit['id']}-F{index:02}", "unidad_id": unit["id"], "parent_id": parent["id"],
                              "inicio": start, "fin": end, "texto": fragment, "texto_embedding": payload, "tokens_e5": count})
            start = end
    return fragments


def expand_hits(fragment_ids, corpus, fragments):
    """Unifica resultados de búsqueda en unidades completas, sin cortar ni duplicar.

    El pipeline de generación deberá comprobar su propio presupuesto Qwen y guardar
    los contextos exactos. Esta función no añade artículos citados automáticamente.
    """
    by_fragment = {f["id"]: f for f in fragments}
    by_unit = {u["id"]: u for u in corpus["unidades"]}
    parents = {p["id"]: p for p in corpus["padres"]}
    seen, result = set(), []
    for identifier in fragment_ids:
        uid = by_fragment[identifier]["unidad_id"]
        if uid in seen:
            continue
        seen.add(uid)
        unit = by_unit[uid]
        parent = parents[unit["parent_id"]]
        result.append({"unidad_id": uid, "parent_id": parent["id"], "cita": parent["cita"], "texto": unit["texto"],
                       "archivo": parent["archivo"], "sha256_pdf": parent["sha256_pdf"]})
    return result


def validate(parents, units, fragments, ledger):
    for label, items in (("padres", parents), ("unidades", units), ("fragmentos", fragments), ("líneas", ledger)):
        require(len({x["id"] for x in items}) == len(items), f"IDs duplicados: {label}")
    require(all(l["destino"] for l in ledger), "Hay líneas sin clasificar")
    for parent in parents:
        related = [u for u in units if u["parent_id"] == parent["id"]]
        require("".join(u["texto"] for u in related) == parent["texto"], f"Pérdida de contenido en {parent['id']}")
    for unit in units:
        related = [f for f in fragments if f["unidad_id"] == unit["id"]]
        cursor = 0
        for fragment in related:
            require(fragment["inicio"] == cursor, "Hueco/solapamiento no declarado")
            require(fragment["texto"] == unit["texto"][fragment["inicio"]:fragment["fin"]], "Fragmento alterado")
            cursor = fragment["fin"]
        require(cursor == len(unit["texto"]), f"Cola perdida en {unit['id']}")
    for parent in parents:
        if "lineas" in parent:
            require(parent["texto"] == render_lines(parent["lineas"]), "Texto distinto a sus líneas de origen")
    assigned = Counter(l["id"] for p in parents for l in p.get("lineas", []))
    for line in ledger:
        if line["destino"] in {p["id"] for p in parents}:
            require(assigned[line["id"]] == 1, "Línea de artículo perdida o duplicada")


def build(source, tokenizer_path, limit=480):
    require(64 <= limit <= 512, "El límite debe estar entre 64 y 512")
    paths = {doc: source / filename for doc, filename in FILES.items()}
    sources = {doc: {"archivo": path.name, "sha256": sha(path)} for doc, path in paths.items()}
    require(sha(tokenizer_path) == TOKENIZER_SHA256, "El tokenizador no corresponde a la revisión fijada de E5")
    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    tokenizer.no_truncation()
    tokenizer.no_padding()
    parents, ledger = [], []
    for doc in ("RI-FI", "RG"):
        extracted, lines = parse_regulation(paths[doc], doc)
        parents.extend(extracted); ledger.extend(lines)
    events, lines = parse_calendar(paths["CAL"])
    parents.extend(events); ledger.extend(lines)
    parents.extend(parse_annex(paths["RG"]))
    for parent in parents:
        parent.update(archivo=sources[parent["documento"]]["archivo"], sha256_pdf=sources[parent["documento"]]["sha256"])
        parent["cita"] = citation(parent)
    units = make_units(parents)
    fragments = make_fragments(units, parents, tokenizer, limit)
    validate(parents, units, fragments, ledger)
    report = {
        "validacion_estructural": "OK", "fuentes": sources,
        "extractor_sha256": sha(__file__),
        "versiones": {name: importlib.metadata.version(name) for name in ("pdfplumber", "tokenizers")},
        "embedding": {"modelo": MODEL, "revision": REVISION, "tokenizer_sha256": sha(tokenizer_path),
                      "limite_modelo": 512, "limite_fragmento": limit, "prefijo_incluido_en_conteo": "passage: "},
        "conteos": {"padres": len(parents), "unidades": len(units), "fragmentos": len(fragments),
                    "tipos": dict(Counter(p["tipo"] for p in parents)), "lineas_pdf": len(ledger)},
        "max_tokens_fragmento": max(f["tokens_e5"] for f in fragments),
        "cobertura_caracteres_unidades_y_fragmentos": "100% del texto canónico extraído; no equivale a certificar toda la semántica del PDF",
        "pendiente": ["Medir recuperación de evidencia", "Resolver remisiones entre artículos durante retrieval", "Presupuesto de contexto con tokenizador Qwen", "Evaluar respuestas del modelo"],
    }
    corpus = {"version": 1, "fuentes": sources, "padres": parents, "unidades": units}
    return corpus, fragments, ledger, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", type=Path, default=ROOT / "Corpus")
    parser.add_argument("--salida", type=Path, default=Path(__file__).parent / "generado")
    parser.add_argument("--tokenizer", type=Path, default=Path.home() / ".cache/huggingface/hub" / "models--intfloat--multilingual-e5-small" / "snapshots" / REVISION / "tokenizer.json")
    parser.add_argument("--limite-tokens", type=int, default=480)
    args = parser.parse_args()
    corpus, fragments, ledger, report = build(args.pdf_dir, args.tokenizer, args.limite_tokens)
    args.salida.mkdir(parents=True, exist_ok=True)
    # Solo se escriben artefactos tras validar todos los documentos.
    outputs = {"corpus.json": corpus, "fragmentos_busqueda.json": fragments, "trazabilidad.json": ledger}
    for name, data in outputs.items():
        (args.salida / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["artefactos_sha256"] = {name: sha(args.salida / name) for name in outputs}
    (args.salida / "validacion.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readable = ["# Corpus extraído de los PDF", "\nFuente para RAG; no contiene preguntas ni respuestas de referencia.\n"]
    for parent in corpus["padres"]:
        readable.extend([f"## {parent['id']} · {parent['cita']}", f"\n{parent['texto']}\n"])
    (args.salida / "corpus.md").write_text("\n".join(readable), encoding="utf-8")
    print(json.dumps({"salida": str(args.salida), **report["conteos"], "max_tokens": report["max_tokens_fragmento"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
