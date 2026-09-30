"""Parser tabular del experimento original, aislado sin efectos al importar."""
import re


def calendar_chunks(text):
    result = []
    semester = "Año Académico 2026"
    for line in text.splitlines():
        line = line.strip()
        if "PRIMER SEMESTRE" in line.upper():
            semester = "Primer Semestre 2026"
            continue
        if "SEGUNDO SEMESTRE" in line.upper():
            semester = "Segundo Semestre 2026"
            continue
        date = re.search(r"(\d{1,2}.*?(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?:\s+de\s+\d{4})?)", line, re.I)
        if date:
            event = re.sub(r"\s{2,}", " ", line[:date.start()].strip()).rstrip(":–- ")
            if len(event) >= 3 and not any(x in event.lower() for x in ("fono", "calle")):
                result.append(f"[Calendario 2026, {semester}]: {event} — {date[1].strip()}")
    return result
