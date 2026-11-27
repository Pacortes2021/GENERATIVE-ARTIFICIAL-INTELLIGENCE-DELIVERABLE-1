"""Reglas de separación estricta (Dataset v2) entre entrenamiento y conjuntos de evaluación."""

from __future__ import annotations

import re

# 40 unidades de corpus.json referenciadas en las 75 preguntas de evaluación D3
# (`test_set_50.csv` + `test_set_dificil_25.csv`). Prohibidas en Dataset v2
# tanto en `evidencia_clave` como en `distractores` y referencias textuales.
EVAL_40_UNIT_IDS: frozenset[str] = frozenset(
    {
        "CAL-2026-S1-02",
        "CAL-2026-S1-03",
        "CAL-2026-S2-01",
        "CAL-2026-S2-02",
        "CAL-2026-S2-03",
        "CAL-2026-S2-04",
        "CAL-2026-S2-05",
        "CAL-2026-S2-09",
        "RG-ART-016",
        "RG-ART-023",
        "RG-ART-024",
        "RG-ART-026",
        "RG-ART-028",
        "RG-ART-029",
        "RG-ART-030",
        "RG-ART-031",
        "RG-ART-049",
        "RI-FI-ART-005",
        "RI-FI-ART-008",
        "RI-FI-ART-009",
        "RI-FI-ART-010",
        "RI-FI-ART-011",
        "RI-FI-ART-012",
        "RI-FI-ART-013",
        "RI-FI-ART-014",
        "RI-FI-ART-016",
        "RI-FI-ART-017",
        "RI-FI-ART-018",
        "RI-FI-ART-019",
        "RI-FI-ART-020",
        "RI-FI-ART-021",
        "RI-FI-ART-022",
        "RI-FI-ART-023",
        "RI-FI-ART-025",
        "RI-FI-ART-026",
        "RI-FI-ART-027",
        "RI-FI-ART-029",
        "RI-FI-ART-030",
        "RI-FI-ART-031",
        "RI-FI-ART-034",
    }
)

# 21 unidades reservadas exclusivamente para el conjunto ciego `preguntas_nuevas_20.csv`.
HELDOUT_21_UNIT_IDS: frozenset[str] = frozenset(
    {
        "CAL-2026-S1-07",
        "CAL-2026-S1-08",
        "CAL-2026-S2-06",
        "CAL-2026-S2-07",
        "RG-ART-004",
        "RG-ART-005",
        "RG-ART-012",
        "RG-ART-017",
        "RG-ART-018",
        "RG-ART-036",
        "RG-ART-046",
        "RG-ART-047",
        "RG-ART-051",
        "RG-ART-053",
        "RG-ART-056",
        "RG-ART-057",
        "RG-ART-059",
        "RG-TRANS-002",
        "RI-FI-ART-003",
        "RI-FI-ART-006",
        "RI-FI-ART-035",
    }
)

BLOCKED_UNIT_IDS: frozenset[str] = EVAL_40_UNIT_IDS | HELDOUT_21_UNIT_IDS

# Pool ordenado de unidades limpias aptas como distractores temáticos (ninguna en BLOCKED_UNIT_IDS).
DISTRACTORES_LIMPIOS: tuple[str, ...] = (
    "RI-FI-ART-001",
    "RI-FI-ART-002",
    "RI-FI-ART-004",
    "RI-FI-ART-007",
    "RI-FI-ART-015",
    "RI-FI-ART-024",
    "RI-FI-ART-028",
    "RI-FI-ART-032",
    "RI-FI-ART-033",
    "RG-ART-001",
    "RG-ART-002",
    "RG-ART-003-DEF-01",
    "RG-ART-003-DEF-05",
    "RG-ART-003-DEF-07",
    "RG-ART-003-DEF-08",
    "RG-ART-003-DEF-09",
    "RG-ART-003-DEF-10",
    "RG-ART-003-DEF-11",
    "RG-ART-003-DEF-12",
    "RG-ART-003-DEF-15",
    "RG-ART-003-DEF-18",
    "RG-ART-006",
    "RG-ART-007",
    "RG-ART-008",
    "RG-ART-009",
    "RG-ART-010",
    "RG-ART-011",
    "RG-ART-013",
    "RG-ART-014",
    "RG-ART-015",
    "RG-ART-019",
    "RG-ART-020",
    "RG-ART-021",
    "RG-ART-022",
    "RG-ART-025",
    "RG-ART-027",
    "RG-ART-032",
    "RG-ART-033",
    "RG-ART-034",
    "RG-ART-035",
    "RG-ART-037",
    "RG-ART-038",
    "RG-ART-039",
    "RG-ART-040",
    "RG-ART-041",
    "RG-ART-042",
    "RG-ART-043",
    "RG-ART-044",
    "RG-ART-045",
    "RG-ART-048",
    "RG-ART-050",
    "RG-ART-052",
    "RG-ART-054",
    "RG-ART-055",
    "RG-ART-058",
    "RG-ART-060",
    "RG-TRANS-001",
    "CAL-2026-S1-01",
    "CAL-2026-S1-04",
    "CAL-2026-S1-05",
    "CAL-2026-S1-06",
    "CAL-2026-S1-14",
)

# Expresión regular para detectar fugas de IDs de evaluación (H01..H25, P1..P50, N01..N20)
# o jerga meta-referencial de diseño de trampas en textos del dataset.
LEAK_QID_RE = re.compile(r"\b(?:H(?:0[1-9]|[12][0-9])|P(?:[1-9]|[1-4][0-9]|50)|N(?:0[1-9]|1[0-9]|20)|trampa|estilo)\b", re.IGNORECASE)

# Cualquier referencia textual a IDs de unidades normativas.
UNIT_ID_REF_RE = re.compile(r"(?:RG|RI-FI)-ART-\d+(?:-DEF-\d+)?|RG-(?:TRANS|ANEXO)-\d+|RG-PREAMBULO|CAL-\d{4}-S[12]-\d{2}")


def filtrar_y_completar_distractores(
    evidencia_clave: list[str],
    distractores: list[str],
    seed_key: str,
    objetivo: int = 3,
) -> list[str]:
    """Devuelve distractores libres de unidades bloqueadas, duplicados o colisión con claves."""
    usados = set(evidencia_clave) | set(BLOCKED_UNIT_IDS)
    limpios: list[str] = []
    for uid in distractores:
        if uid not in usados:
            limpios.append(uid)
            usados.add(uid)
    if len(limpios) < objetivo:
        offset = sum(ord(ch) for ch in seed_key) % len(DISTRACTORES_LIMPIOS)
        rotada = DISTRACTORES_LIMPIOS[offset:] + DISTRACTORES_LIMPIOS[:offset]
        for cand in rotada:
            if cand not in usados:
                limpios.append(cand)
                usados.add(cand)
                if len(limpios) >= objetivo:
                    break
    return limpios
