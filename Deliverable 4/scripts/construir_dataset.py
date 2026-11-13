"""Construye, valida y audita el dataset híbrido de fine-tuning para el Redactor (Paso 2).

Ensambla los 210 pares supervisados definidos en `dataset_blocks/` usando
exclusivamente textos literales de `corpus.json` y la plantilla real de
`prompts/03_redactor.txt`, replicando byte a byte el formato de entrada y
salida de `Orquestador.redactar`.

Genera en `Deliverable 4/datos/`:
- `redactor_train.jsonl` (180 ejemplos)
- `redactor_val.jsonl` (30 ejemplos)
- `dataset_resumen.json` (estadísticas, longitudes y auditoría antifuga)
- `MUESTRA_REVISION_MANUAL.md` (30 ejemplos estratificados para revisión humana)
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import statistics
import sys
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from dataset_blocks import (  # noqa: E402
    BLOQUE_1_CITAS_CRUCE,
    BLOQUE_2_CONDICIONES_EXCEPCIONES,
    BLOQUE_3_POLARES_Y_LECTURA,
    BLOQUE_4_CALCULOS_Y_ORDEN,
    BLOQUE_5_RESILIENCIA_FEEDBACK,
    BLOQUE_6_ABSTENCION_HONESTA,
)
from dataset_blocks.reglas_v2 import (  # noqa: E402
    BLOCKED_UNIT_IDS,
    EVAL_40_UNIT_IDS,
    HELDOUT_21_UNIT_IDS,
    LEAK_QID_RE,
    UNIT_ID_REF_RE,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CORPUS_PATH = (
    REPO_ROOT / "Deliverable 3" / "Deliverable3" / "agentes" / "corpus.json"
)
DEFAULT_PROMPT_PATH = REPO_ROOT / "Deliverable 4" / "prompts" / "03_redactor.txt"
DEFAULT_EVAL_CSV_PATH = (
    REPO_ROOT
    / "Deliverable 3"
    / "Deliverable3"
    / "resultados_v6"
    / "resultados_agentes_D3.csv"
)
DEFAULT_NUEVAS_CSV_PATH = (
    REPO_ROOT / "Deliverable 4" / "datos" / "preguntas_nuevas_20.csv"
)
DEFAULT_DATOS_DIR = REPO_ROOT / "Deliverable 4" / "datos"

# Copia exacta del diccionario MODOS en Deliverable 3/Deliverable3/agentes/orquestador.py
MODOS: dict[str, str] = {
    "factual": "Responde el dato pedido de forma directa.",
    "numerica": (
        "La pregunta exige un cálculo o una comparación numérica: hazlo con las cifras "
        "de la evidencia y las que entrega la pregunta, mostrando la operación."
    ),
    "condicional": "Enumera todas las condiciones, plazos y excepciones que correspondan.",
    "cruce": "La pregunta tiene varias partes: responde cada una por separado, con su fuente.",
    "premisa_falsa": (
        "La pregunta puede afirmar algo falso: contrástalo con la evidencia y, si no "
        "se sostiene, dilo y corrígelo. Nunca confirmes un dato que la evidencia no respalda."
    ),
}

EXPECTED_COUNTS: dict[str, dict[str, int]] = {
    "citas_cruce": {"train": 35, "val": 5},
    "condiciones_excepciones": {"train": 35, "val": 5},
    "polares_y_lectura": {"train": 30, "val": 5},
    "calculos_y_orden": {"train": 30, "val": 5},
    "resiliencia_feedback": {"train": 25, "val": 5},
    "abstencion_honesta": {"train": 25, "val": 5},
}

ESTADOS_VALIDOS = {"suficiente", "insuficiente", "no_existe"}
STOPWORDS_ES = {
    "a", "al", "ante", "bajo", "con", "contra", "cual", "cuales", "cuando",
    "de", "del", "desde", "donde", "el", "ella", "ellas", "ellos", "en",
    "entre", "era", "es", "esa", "ese", "eso", "esta", "este", "esto",
    "fue", "ha", "han", "hasta", "hay", "la", "las", "le", "les", "lo",
    "los", "mas", "me", "mi", "no", "o", "para", "pero", "por", "que",
    "quien", "quienes", "se", "si", "sin", "sobre", "su", "sus", "un",
    "una", "uno", "unos", "y", "ya",
}
CITA_RE = re.compile(r"\[([A-Z0-9-]+)\]")
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def normalizar_texto(texto: str) -> str:
    """Normaliza un texto para comparación léxica sin tildes ni puntuación."""
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    sin_tildes = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    limpio = re.sub(r"[^a-z0-9]+", " ", sin_tildes)
    return re.sub(r"\s+", " ", limpio).strip()


def tokens_contenido(texto: str) -> set[str]:
    """Devuelve tokens normalizados descartando stopwords cortas en español."""
    toks = normalizar_texto(texto).split()
    filtrados = {t for t in toks if t not in STOPWORDS_ES and len(t) > 1}
    return filtrados or set(toks)


def cargar_unidades_corpus(corpus_path: Path) -> dict[str, str]:
    """Carga el mapa {id_unidad: texto_literal} desde corpus.json."""
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    unidades = data["unidades"]
    lista = unidades if isinstance(unidades, list) else list(unidades.values())
    por_id: dict[str, str] = {}
    for u in lista:
        uid = u["id"]
        if uid in por_id:
            raise ValueError(f"ID de unidad duplicado en corpus.json: {uid}")
        por_id[uid] = u["texto"]
    return por_id


def cargar_prompt_redactor(prompt_path: Path) -> str:
    """Lee 03_redactor.txt eliminando líneas de comentario `#`, igual que Orquestador."""
    lineas = prompt_path.read_text(encoding="utf-8").splitlines()
    return "\n".join(l for l in lineas if not l.lstrip().startswith("#")).strip()


def cargar_preguntas_eval(eval_csv_path: Path) -> list[dict[str, str]]:
    """Carga las 75 preguntas de evaluación de D3 v6."""
    with eval_csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 75:
        raise ValueError(
            f"Se esperaban 75 filas en {eval_csv_path}, encontradas: {len(rows)}"
        )
    return rows


def cargar_preguntas_nuevas(nuevas_csv_path: Path) -> list[dict[str, str]]:
    """Carga el conjunto ciego de 20 preguntas nuevas (`preguntas_nuevas_20.csv`)."""
    with nuevas_csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r.setdefault("set", "nuevas_20")
    return rows


def todas_las_especificaciones() -> list[dict[str, Any]]:
    """Reúne en orden los 6 bloques curados."""
    return (
        list(BLOQUE_1_CITAS_CRUCE)
        + list(BLOQUE_2_CONDICIONES_EXCEPCIONES)
        + list(BLOQUE_3_POLARES_Y_LECTURA)
        + list(BLOQUE_4_CALCULOS_Y_ORDEN)
        + list(BLOQUE_5_RESILIENCIA_FEEDBACK)
        + list(BLOQUE_6_ABSTENCION_HONESTA)
    )


def ensamblar_evidencia_ids(
    spec: dict[str, Any],
    corpus_by_id: dict[str, str],
    seed: int = 202604,
    max_unidades: int = 6,
) -> list[str]:
    """Valida, combina hasta 6 unidades y baraja determinísticamente la evidencia."""
    sid = spec["id"]
    claves = list(spec["evidencia_clave"])
    distractores = list(spec["distractores"])

    # Verificar que no haya duplicados dentro de claves ni dentro de distractores, ni solapamiento.
    if len(set(claves)) != len(claves):
        raise ValueError(f"{sid}: evidencia_clave contiene duplicados: {claves}")
    if len(set(distractores)) != len(distractores):
        raise ValueError(f"{sid}: distractores contiene duplicados: {distractores}")
    cruce = set(claves) & set(distractores)
    if cruce:
        raise ValueError(
            f"{sid}: IDs repetidos entre evidencia_clave y distractores: {sorted(cruce)}"
        )

    for uid in claves + distractores:
        if uid not in corpus_by_id:
            raise KeyError(f"{sid}: unidad '{uid}' no existe en corpus.json")

    if len(claves) > max_unidades:
        raise ValueError(
            f"{sid}: evidencia_clave tiene {len(claves)} unidades (máximo {max_unidades})"
        )

    espacio_distractores = max_unidades - len(claves)
    combinada = claves + distractores[:espacio_distractores]
    rng = random.Random(f"{seed}:{sid}")
    rng.shuffle(combinada)
    return combinada


def construir_user_prompt(
    template: str,
    spec: dict[str, Any],
    evidencia_ids: list[str],
    corpus_by_id: dict[str, str],
) -> str:
    """Construye el mensaje `user` exactamente como Orquestador.redactar."""
    cab = f"estado: {spec['estado']}"
    inexistentes = spec.get("inexistentes") or []
    if inexistentes:
        cab += f" | no existen en la normativa: {', '.join(inexistentes)}"

    bloque = (
        "\n".join(f"[{uid}] {corpus_by_id[uid]}" for uid in evidencia_ids)
        or "(sin evidencia)"
    )
    feedback = spec.get("feedback") or "(primera versión, sin observaciones)"

    prompt = (
        template.replace("{{PREGUNTA}}", spec["pregunta"].strip())
        .replace("{{MODO}}", MODOS[spec["modo"]])
        .replace("{{FEEDBACK}}", feedback.strip())
        .replace("{{BORRADOR_ANTERIOR}}", "(no hay: es la primera versión)")
        .replace("{{EVIDENCIA}}", f"{cab}\n{bloque}")
    )
    restantes = PLACEHOLDER_RE.findall(prompt)
    if restantes:
        raise ValueError(
            f"{spec['id']}: quedaron placeholders sin reemplazar: {restantes}"
        )
    return prompt


def construir_assistant_target(spec: dict[str, Any]) -> str:
    """Ensambla el objetivo `<pensar>...</pensar>` + 3 líneas estándar."""
    pensar = spec["pensar"].strip()
    respuesta = spec["respuesta"].strip()
    condiciones = spec["condiciones"].strip()
    fuente = spec["fuente"].strip()
    return (
        f"<pensar>\n{pensar}\n</pensar>\n"
        f"Respuesta: {respuesta}\n"
        f"Condiciones o límites: {condiciones}\n"
        f"Fuente: {fuente}"
    )


def validar_especificacion(
    spec: dict[str, Any],
    evidencia_ids: list[str],
    corpus_by_id: dict[str, str],
) -> None:
    """Ejecuta validaciones estructurales y de fidelidad de citas sobre un ejemplo."""
    sid = spec["id"]
    if spec["bloque"] not in EXPECTED_COUNTS:
        raise ValueError(f"{sid}: bloque desconocido '{spec['bloque']}'")
    if spec["split"] not in {"train", "val"}:
        raise ValueError(f"{sid}: split inválido '{spec['split']}'")
    if spec["modo"] not in MODOS:
        raise ValueError(f"{sid}: modo inválido '{spec['modo']}'")
    if spec["estado"] not in ESTADOS_VALIDOS:
        raise ValueError(f"{sid}: estado inválido '{spec['estado']}'")

    for campo in ("pregunta", "pensar", "respuesta", "condiciones", "fuente"):
        val = spec.get(campo)
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"{sid}: campo '{campo}' vacío o no es string")

    for campo in ("respuesta", "condiciones", "fuente"):
        if "\n" in spec[campo].strip():
            raise ValueError(
                f"{sid}: el campo '{campo}' contiene salto de línea interno"
            )

    if spec["bloque"] == "resiliencia_feedback":
        fb = spec.get("feedback")
        if not isinstance(fb, str) or not fb.strip():
            raise ValueError(f"{sid}: Bloque 5 requiere feedback no vacío")

    # Validar citas [ID] en pensar, respuesta, condiciones y fuente.
    ev_set = set(evidencia_ids)
    claves_set = set(spec["evidencia_clave"])
    fuente_texto = spec["fuente"].strip()

    for campo in ("pensar", "respuesta", "condiciones", "fuente"):
        citas = CITA_RE.findall(spec[campo])
        for cid in citas:
            if cid not in corpus_by_id:
                raise ValueError(
                    f"{sid}: cita inventada [{cid}] en '{campo}' (no existe en corpus.json)"
                )
            if cid not in ev_set:
                raise ValueError(
                    f"{sid}: cita fuera de contexto [{cid}] en '{campo}' (evidencia={sorted(ev_set)})"
                )

    citas_fuente = set(CITA_RE.findall(fuente_texto))
    sin_respaldo = fuente_texto == "sin respaldo en la normativa consultada"
    permite_abstencion = (
        spec["bloque"] == "abstencion_honesta"
        or (
            spec["bloque"] == "resiliencia_feedback"
            and spec["estado"] in {"insuficiente", "no_existe"}
            and not claves_set
        )
    )

    if not permite_abstencion:
        if sin_respaldo or not citas_fuente:
            raise ValueError(
                f"{sid}: bloque '{spec['bloque']}' requiere citas en Fuente, obtuvo: {fuente_texto!r}"
            )
        faltantes_en_fuente = claves_set - citas_fuente
        if faltantes_en_fuente:
            raise ValueError(
                f"{sid}: evidencia_clave no reflejada en Fuente: {sorted(faltantes_en_fuente)}"
            )
    else:
        if not sin_respaldo and not citas_fuente:
            raise ValueError(
                f"{sid}: debe usar 'sin respaldo en la normativa consultada' o citas válidas"
            )
        # Si hay citas de evidencia_clave en abstención parcial con norma relacionada,
        # deben coincidir con Fuente:.
        if claves_set and not sin_respaldo:
            faltantes = claves_set - citas_fuente
            if faltantes:
                raise ValueError(
                    f"{sid}: evidencia_clave de abstención parcial faltante en Fuente: {sorted(faltantes)}"
                )

    # Verificar coherencia mínima con D3: cada afirmación en respuesta/condiciones de bloques 1-5
    # o en respuestas con fuente explícita cita en corchetes o remite al bloque Fuente:.
    if not sin_respaldo and not CITA_RE.search(spec["respuesta"]) and spec["bloque"] in {
        "citas_cruce",
        "condiciones_excepciones",
        "resiliencia_feedback",
    }:
        raise ValueError(
            f"{sid}: se esperaba al menos una cita inline [ID] en 'respuesta'"
        )

    # Verificar separación estricta v2: cero unidades bloqueadas en evidencia o textos,
    # y cero menciones meta-referenciales a IDs de evaluación (Hxx/Pxx/Nxx).
    fuga_ev = sorted(set(evidencia_ids) & BLOCKED_UNIT_IDS)
    if fuga_ev:
        raise ValueError(
            f"{sid}: unidades reservadas de evaluación en evidencia_ids: {fuga_ev}"
        )
    for campo in ("pregunta", "pensar", "respuesta", "condiciones", "fuente"):
        texto_campo = spec[campo]
        leaks_qid = LEAK_QID_RE.findall(texto_campo)
        if leaks_qid:
            raise ValueError(
                f"{sid}: mención meta/QID prohibida en '{campo}': {leaks_qid}"
            )
        refs_bloqueadas = sorted(set(UNIT_ID_REF_RE.findall(texto_campo)) & BLOCKED_UNIT_IDS)
        if refs_bloqueadas:
            raise ValueError(
                f"{sid}: referencia textual a unidad reservada en '{campo}': {refs_bloqueadas}"
            )


def auditar_antifuga(
    specs: list[dict[str, Any]],
    eval_rows: list[dict[str, str]],
    seq_threshold: float = 0.85,
    jaccard_threshold: float = 0.80,
    etiqueta: str = "evaluación",
) -> dict[str, Any]:
    """Verifica cero duplicados internos y evalúa similitud contra un conjunto de test."""
    norm_vistas: dict[str, str] = {}
    for spec in specs:
        norm = normalizar_texto(spec["pregunta"])
        if norm in norm_vistas:
            raise ValueError(
                f"Pregunta duplicada dentro del dataset: {spec['id']} == {norm_vistas[norm]}"
            )
        norm_vistas[norm] = spec["id"]

    parejas: list[dict[str, Any]] = []
    coincidencias_exactas: list[dict[str, str]] = []
    alertas_similitud: list[dict[str, Any]] = []

    for spec in specs:
        q_ds = spec["pregunta"]
        n_ds = normalizar_texto(q_ds)
        t_ds = tokens_contenido(q_ds)
        for row in eval_rows:
            q_ev = row["pregunta"]
            n_ev = normalizar_texto(q_ev)
            if n_ds == n_ev:
                coincidencias_exactas.append(
                    {
                        "dataset_id": spec["id"],
                        "eval_set": row["set"],
                        "eval_id": row["id"],
                        "pregunta": q_ds,
                    }
                )
            seq_ratio = SequenceMatcher(None, n_ds, n_ev).ratio()
            t_ev = tokens_contenido(q_ev)
            union = t_ds | t_ev
            jacc = len(t_ds & t_ev) / len(union) if union else 0.0
            score = max(seq_ratio, jacc)
            registro = {
                "dataset_id": spec["id"],
                "bloque": spec["bloque"],
                "split": spec["split"],
                "eval_set": row["set"],
                "eval_id": row["id"],
                "seq_ratio": round(seq_ratio, 4),
                "jaccard_contenido": round(jacc, 4),
                "score_max": round(score, 4),
                "pregunta_dataset": q_ds,
                "pregunta_eval": q_ev,
            }
            parejas.append(registro)
            if seq_ratio >= seq_threshold or jacc >= jaccard_threshold:
                alertas_similitud.append(registro)

    if coincidencias_exactas:
        raise ValueError(
            f"¡Fuga exacta detectada contra evaluación D3!: {coincidencias_exactas}"
        )
    if alertas_similitud:
        raise ValueError(
            f"Similitud excesiva contra evaluación D3 (>={seq_threshold}/{jaccard_threshold}): "
            f"{json.dumps(alertas_similitud[:5], ensure_ascii=False)}"
        )

    parejas.sort(key=lambda x: x["score_max"], reverse=True)
    return {
        "total_preguntas_dataset": len(specs),
        "total_preguntas_eval": len(eval_rows),
        "duplicados_internos": 0,
        "coincidencias_exactas_eval": 0,
        "alertas_sobre_umbral": 0,
        "umbrales": {
            "seq_ratio_max": seq_threshold,
            "jaccard_contenido_max": jaccard_threshold,
        },
        "top_10_pares_mas_cercanos": parejas[:10],
    }


def _stats_enteros(valores: list[int]) -> dict[str, float | int]:
    ordenados = sorted(valores)
    n = len(ordenados)
    p95_idx = min(n - 1, max(0, int(round(0.95 * (n - 1)))))
    return {
        "min": ordenados[0],
        "mediana": statistics.median(ordenados),
        "promedio": round(sum(ordenados) / n, 1),
        "p95": ordenados[p95_idx],
        "max": ordenados[-1],
    }


def generar_muestra_manual(
    registros: list[dict[str, Any]],
    specs_by_id: dict[str, dict[str, Any]],
    corpus_by_id: dict[str, str],
    output_path: Path,
) -> list[str]:
    """Crea `MUESTRA_REVISION_MANUAL.md` con 30 casos (3 train + 2 val por bloque)."""
    seleccionados: list[dict[str, Any]] = []
    por_bloque_split: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for reg in registros:
        clave = (reg["bloque"], reg["split"])
        por_bloque_split.setdefault(clave, []).append(reg)

    for bloque in EXPECTED_COUNTS:
        train_list = por_bloque_split[(bloque, "train")]
        val_list = por_bloque_split[(bloque, "val")]
        t_idxs = [0, len(train_list) // 2, len(train_list) - 1]
        v_idxs = [0, len(val_list) - 1]
        for idx in t_idxs:
            seleccionados.append(train_list[idx])
        for idx in v_idxs:
            seleccionados.append(val_list[idx])

    lineas: list[str] = [
        "# Muestra de Revisión Manual — Dataset Redactor D4 v2 (30 casos)",
        "",
        "Muestra estratificada de **30 ejemplos** (`3 train + 2 val` por cada uno de los 6 bloques) "
        "extraída desde `redactor_train.jsonl` y `redactor_val.jsonl` para verificación humana previa "
        "al entrenamiento QLoRA (Paso 3).",
        "",
        "## Autoría y Separación de Datos (v2)",
        "- **Fuente normativa:** Fragmentos literales de `corpus.json` (reglamentos y calendario UdeC).",
        "- **Autoría de los pares supervisados:** Especificaciones redactadas y curadas por el equipo con asistencia de **Antigravity (modelo asistente IA)** y verificadas programáticamente contra `corpus.json` (citas, cálculos aritméticos y fechas).",
        "- **Separación estricta:** 0 de las 40 unidades de corpus evaluadas en las 75 preguntas de D3 y 0 de las 21 unidades reservadas para `preguntas_nuevas_20.csv` aparecen en `evidencia_clave`, `distractores` ni referencias textuales del dataset.",
        "",
        "## Registro de Verificación Humana (30 casos)",
        "",
        "> **Nota:** Complete esta tabla al revisar los casos antes de validar la entrega final (revisor, fecha y estado).",
        "",
        "| # | ID | Bloque / Split | Revisor | Fecha | Resultado | Observaciones |",
        "|---|---|---|---|:---:|---|---|",
    ]

    for i, reg in enumerate(seleccionados, start=1):
        sid = reg["id"]
        lineas.append(
            f"| {i:02d} | `{sid}` | `{reg['bloque']}` / `{reg['split']}` | `[Pendiente revisor]` | `[YYYY-MM-DD]` | `[Pendiente]` | |"
        )

    lineas.extend(
        [
            "",
            "Criterios a revisar en cada ejemplo:",
            "1. La respuesta esperada se deduce íntegramente de los fragmentos literales mostrados en `<evidencia>`.",
            "2. Todas las citas `[ID]` existen en la evidencia entregada y cubren cada afirmación relevante.",
            "3. El bloque `<pensar>` razona sin saltos lógicos ni contradecir la salida final.",
            "4. Cuando la evidencia falta o es parcial, el modelo no inventa datos y se abstiene honestamente; si no hay salvedades extra aplicables, usa `Condiciones o límites: No aplica`.",
            "",
            "---",
            "",
        ]
    )

    for i, reg in enumerate(seleccionados, start=1):
        sid = reg["id"]
        spec = specs_by_id[sid]
        target = reg["messages"][1]["content"]
        lineas.extend(
            [
                f"## {i:02d}. `{sid}` — bloque `{reg['bloque']}` | split `{reg['split']}` | modo `{reg['modo']}` | estado `{reg['estado']}`",
                "",
                f"**Pregunta:** {spec['pregunta']}",
                "",
            ]
        )
        if spec.get("feedback"):
            lineas.append(f"**Observaciones del Verificador (entrada):** {spec['feedback']}")
            lineas.append("")
        if spec.get("inexistentes"):
            lineas.append(f"**Artículos marcados como inexistentes:** {', '.join(spec['inexistentes'])}")
            lineas.append("")

        claves = spec["evidencia_clave"]
        distractores = [uid for uid in reg["evidencia_ids"] if uid not in set(claves)]
        lineas.append(f"**Evidencia ensamblada ({len(reg['evidencia_ids'])} unidades, orden barajado):** `{'`, `'.join(reg['evidencia_ids'])}`")
        lineas.append(f"- Clave esperada: `{', '.join(claves) if claves else '(ninguna)'}` | Distractores incluidos: `{', '.join(distractores) if distractores else '(ninguno)'}`")
        lineas.append("")
        if claves:
            lineas.append("<details>")
            lineas.append("<summary>Textos literales de las unidades clave en corpus.json</summary>")
            lineas.append("")
            for uid in claves:
                texto_plano = " ".join(corpus_by_id[uid].split())
                lineas.append(f"- **[{uid}]** {texto_plano}")
            lineas.append("")
            lineas.append("</details>")
            lineas.append("")

        lineas.append("**Salida esperada del Redactor (`assistant`):**")
        lineas.append("```text")
        lineas.append(target)
        lineas.append("```")
        lineas.append("")

    with output_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lineas) + "\n")
    return [reg["id"] for reg in seleccionados]


def construir_dataset(
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    prompt_path: Path = DEFAULT_PROMPT_PATH,
    eval_csv_path: Path = DEFAULT_EVAL_CSV_PATH,
    nuevas_csv_path: Path = DEFAULT_NUEVAS_CSV_PATH,
    datos_dir: Path = DEFAULT_DATOS_DIR,
    seed: int = 202604,
) -> dict[str, Any]:
    """Construye, valida y escribe todos los archivos del dataset v2 del Redactor."""
    corpus_by_id = cargar_unidades_corpus(corpus_path)
    prompt_template = cargar_prompt_redactor(prompt_path)
    eval_rows = cargar_preguntas_eval(eval_csv_path)
    nuevas_rows = (
        cargar_preguntas_nuevas(nuevas_csv_path) if nuevas_csv_path.is_file() else []
    )
    specs = todas_las_especificaciones()

    # Verificar IDs únicos y conteos exactos por bloque y split.
    vistos: set[str] = set()
    conteo: Counter[tuple[str, str]] = Counter()
    for spec in specs:
        sid = spec["id"]
        if sid in vistos:
            raise ValueError(f"ID de especificación duplicado: {sid}")
        vistos.add(sid)
        conteo[(spec["bloque"], spec["split"])] += 1

    for bloque, esperado in EXPECTED_COUNTS.items():
        for split in ("train", "val"):
            actual = conteo[(bloque, split)]
            if actual != esperado[split]:
                raise ValueError(
                    f"Conteo inválido para {bloque}/{split}: esperado {esperado[split]}, actual {actual}"
                )

    auditoria = auditar_antifuga(specs, eval_rows, etiqueta="evaluacion_d3")
    auditoria_nuevas = (
        auditar_antifuga(specs, nuevas_rows, etiqueta="evaluacion_nuevas_20")
        if nuevas_rows
        else None
    )

    registros: list[dict[str, Any]] = []
    train_rows: list[dict[str, Any]] = []
    val_rows: list[dict[str, Any]] = []
    specs_by_id: dict[str, dict[str, Any]] = {}

    user_chars: list[int] = []
    assistant_chars: list[int] = []
    total_chars: list[int] = []
    total_est_tokens: list[int] = []
    unidades_usadas: set[str] = set()
    ev_lens: list[int] = []

    for spec in specs:
        specs_by_id[spec["id"]] = spec
        evidencia_ids = ensamblar_evidencia_ids(spec, corpus_by_id, seed=seed)
        validar_especificacion(spec, evidencia_ids, corpus_by_id)

        user_prompt = construir_user_prompt(
            prompt_template, spec, evidencia_ids, corpus_by_id
        )
        assistant_target = construir_assistant_target(spec)

        registro = {
            "id": spec["id"],
            "bloque": spec["bloque"],
            "split": spec["split"],
            "modo": spec["modo"],
            "estado": spec["estado"],
            "evidencia_ids": evidencia_ids,
            "messages": [
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": assistant_target},
            ],
        }
        registros.append(registro)
        if spec["split"] == "train":
            train_rows.append(registro)
        else:
            val_rows.append(registro)

        uc = len(user_prompt)
        ac = len(assistant_target)
        tc = uc + ac
        user_chars.append(uc)
        assistant_chars.append(ac)
        total_chars.append(tc)
        # Estimación conservadora (~3.4 chars/token para texto legal en español + tags XML)
        total_est_tokens.append(int(round(tc / 3.4)))
        unidades_usadas.update(evidencia_ids)
        ev_lens.append(len(evidencia_ids))

    datos_dir.mkdir(parents=True, exist_ok=True)
    train_path = datos_dir / "redactor_train.jsonl"
    val_path = datos_dir / "redactor_val.jsonl"
    resumen_path = datos_dir / "dataset_resumen.json"
    muestra_path = datos_dir / "MUESTRA_REVISION_MANUAL.md"

    with train_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in train_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with val_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in val_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    muestra_ids = generar_muestra_manual(registros, specs_by_id, corpus_by_id, muestra_path)

    distribucion_bloques = {
        bloque: {
            "train": conteo[(bloque, "train")],
            "val": conteo[(bloque, "val")],
            "total": conteo[(bloque, "train")] + conteo[(bloque, "val")],
        }
        for bloque in EXPECTED_COUNTS
    }
    distribucion_modos = dict(Counter(r["modo"] for r in registros))
    distribucion_estados = dict(Counter(r["estado"] for r in registros))
    ejemplos_no_aplica = sum(
        1 for s in specs if s["condiciones"].strip().lower() == "no aplica"
    )

    def _ruta_legible(path: Path) -> str:
        try:
            return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        except ValueError:
            return path.as_posix()

    resumen = {
        "version_dataset": "v2",
        "total_ejemplos": len(registros),
        "train_ejemplos": len(train_rows),
        "val_ejemplos": len(val_rows),
        "seed_barajado_evidencia": seed,
        "unidades_corpus_total": len(corpus_by_id),
        "unidades_corpus_cubiertas_en_evidencia": len(unidades_usadas),
        "ejemplos_condiciones_no_aplica": ejemplos_no_aplica,
        "distribucion_bloques": distribucion_bloques,
        "distribucion_modos": distribucion_modos,
        "distribucion_estados": distribucion_estados,
        "evidencia_unidades_por_ejemplo": _stats_enteros(ev_lens),
        "longitudes_caracteres": {
            "user": _stats_enteros(user_chars),
            "assistant": _stats_enteros(assistant_chars),
            "total": _stats_enteros(total_chars),
        },
        "tokens_estimados_conservadores_3_4_chars_por_token": _stats_enteros(
            total_est_tokens
        ),
        "separacion_unidades_corpus": {
            "unidades_eval_d3_bloqueadas": len(EVAL_40_UNIT_IDS),
            "unidades_heldout_20_bloqueadas": len(HELDOUT_21_UNIT_IDS),
            "solapamiento_evidencia_vs_eval_d3": len(unidades_usadas & EVAL_40_UNIT_IDS),
            "solapamiento_evidencia_vs_heldout_20": len(unidades_usadas & HELDOUT_21_UNIT_IDS),
        },
        "declaracion_autoria": (
            "Pares supervisados curados a partir de fragmentos literales de corpus.json "
            "con asistencia de Antigravity (modelo asistente IA) y validación automática "
            "frente a corpus.json y normas de separación de evaluación."
        ),
        "antifuga_evaluacion_d3": auditoria,
        "antifuga_evaluacion_nuevas_20": auditoria_nuevas,
        "muestra_revision_manual_ids": muestra_ids,
        "archivos_generados": {
            "train_jsonl": _ruta_legible(train_path),
            "val_jsonl": _ruta_legible(val_path),
            "resumen_json": _ruta_legible(resumen_path),
            "muestra_md": _ruta_legible(muestra_path),
        },
    }
    with resumen_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n")
    return resumen


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Construye y valida el dataset de fine-tuning para el agente Redactor (D4 v2)."
    )
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT_PATH)
    parser.add_argument("--eval-csv", type=Path, default=DEFAULT_EVAL_CSV_PATH)
    parser.add_argument("--nuevas-csv", type=Path, default=DEFAULT_NUEVAS_CSV_PATH)
    parser.add_argument("--datos-dir", type=Path, default=DEFAULT_DATOS_DIR)
    parser.add_argument("--seed", type=int, default=202604)
    args = parser.parse_args()

    resumen = construir_dataset(
        corpus_path=args.corpus,
        prompt_path=args.prompt,
        eval_csv_path=args.eval_csv,
        nuevas_csv_path=args.nuevas_csv,
        datos_dir=args.datos_dir,
        seed=args.seed,
    )
    print(
        f"Dataset D4 construido: {resumen['train_ejemplos']} train + "
        f"{resumen['val_ejemplos']} val = {resumen['total_ejemplos']} ejemplos."
    )
    print(
        "Longitud total (chars):",
        resumen["longitudes_caracteres"]["total"],
        "| Tokens estimados:",
        resumen["tokens_estimados_conservadores_3_4_chars_por_token"],
    )
    top3 = resumen["antifuga_evaluacion_d3"]["top_10_pares_mas_cercanos"][:3]
    print("Top-3 similitud vs eval D3:", [(p["dataset_id"], p["eval_id"], p["score_max"]) for p in top3])


if __name__ == "__main__":
    main()
