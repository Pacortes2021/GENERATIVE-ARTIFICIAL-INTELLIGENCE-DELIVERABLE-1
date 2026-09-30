"""Extractor corregido. Crea una base nueva; conserva intacta la base histórica.

Requiere Poppler (pdftotext) en PATH. Desde la raíz:
python -m Deliverable2_RAG.preparar_corpus_v2
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = re.compile(r"^[ \t]*Artículo\s+(\d+)[°º]?\.?\s+", re.M | re.I)


def extract(path, layout=False):
    executable = shutil.which("pdftotext")
    if not executable:
        raise RuntimeError("Instala Poppler: apt-get install poppler-utils (Colab) o brew install poppler (macOS)")
    return subprocess.check_output([executable, *(["-layout"] if layout else []), str(path), "-"], text=True)


def articles(text, expected):
    """Acepta encabezados consecutivos: una referencia al Art. 7 dentro del 9 no inicia bloque."""
    text = text.replace("\f", "\n")
    text = re.sub(r"(?m)^REGLAMENTO GENERAL DE DOCENCIA DE PREGRADO /.*\n?", "", text)
    text = re.sub(r"(?m)^\d+\s*$", "", text)
    text = re.sub(r"(\w)-\n[ \t]*(\w)", r"\1\2", text)
    sections = re.split(r"DISPOSICIONES TRANSITORIAS", text, maxsplit=1)
    starts = []
    for m in ARTICLE.finditer(sections[0]):
        if int(m[1]) == len(starts) + 1:
            starts.append(m)
    if len(starts) != expected:
        raise ValueError(f"Se esperaban {expected} artículos consecutivos y se encontraron {len(starts)}")
    result = []
    for i, m in enumerate(starts):
        end = starts[i+1].start() if i+1 < len(starts) else len(sections[0])
        result.append((str(i+1), re.sub(r"\s+", " ", sections[0][m.start():end]).strip()))
    # No confundir los dos artículos transitorios del RG con los artículos permanentes 1 y 2.
    if len(sections) == 2:
        for number, content in articles(sections[1], 2):
            result.append(("transitorio-" + number, content))
    return result


def split_words(text, size=160, overlap=30):
    words = text.split()
    if size <= overlap or overlap < 0:
        raise ValueError("Ventana y solapamiento inválidos")
    for start in range(0, len(words), size-overlap):
        yield " ".join(words[start:start+size])
        if start+size >= len(words):
            break


def build():
    # Se reutiliza la extracción tabular histórica para mantener los eventos/fechas;
    # la modificación de v2 se concentra en encabezados y referencias de artículos.
    from .legacy_calendar import calendar_chunks
    chunks = []
    calendar = ROOT / "Corpus/Calendario-Academico-Pregrado-2026.pdf"
    for i, text in enumerate(calendar_chunks(extract(calendar, layout=True)), 1):
        chunks.append({"id": f"CAL-{i}", "fuente": calendar.name, "texto": text})
    for filename, abbreviation, count in [
        ("Reglamento_General_de_Docencia_de_Pregrado.pdf", "RG", 60),
        ("Reglamento_de_Docencia_de_Pregrado-FI.pdf", "RI-FI", 35),
    ]:
        for number, content in articles(extract(ROOT / "Corpus" / filename, layout=True), count):
            for part, text in enumerate(split_words(content), 1):
                chunks.append({"id": f"{abbreviation}-{number}-{part}", "fuente": filename,
                               "articulo": number, "texto": f"[Art. {number}, {abbreviation}]: {text}"})
    return chunks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "base_conocimiento_v2.json")
    args = parser.parse_args()
    chunks = build()
    args.output.write_text(json.dumps(chunks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(chunks)} fragmentos → {args.output}")
    print("SHA256:", hashlib.sha256(args.output.read_bytes()).hexdigest())
    print("Esta nueva base requiere una corrida nueva; no hereda resultados históricos.")
