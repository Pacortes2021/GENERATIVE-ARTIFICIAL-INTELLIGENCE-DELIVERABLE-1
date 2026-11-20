"""Benchmark local reproducible para evaluar el asistente sobre conjuntos D3/D4."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from .asistente import AsistenteUdeC
from .config import ConfigAsistente, REPO_ROOT

DATOS_D3_DIR = REPO_ROOT / "Deliverable 3" / "Deliverable3" / "agentes"
DEFAULT_OUT_DIR = Path(__file__).resolve().parent / "resultados"
_CITE_RE = re.compile(r"\[([A-Z]+(?:-[A-Z0-9]+)+)\]")


def cargar_preguntas(dataset: str, qids_filtro: set[str] | None = None) -> list[dict[str, str]]:
    """Carga dificil_25, congelado_50 o nuevas_20 (desde rama deliverable-4 si no está local)."""
    if dataset in {"dificil_25", "congelado_50"}:
        archivo = "test_set_dificil_25.csv" if dataset == "dificil_25" else "test_set_50.csv"
        with (DATOS_D3_DIR / archivo).open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    elif dataset == "nuevas_20":
        ruta_local = REPO_ROOT / "Deliverable 4" / "datos" / "preguntas_nuevas_20.csv"
        if ruta_local.is_file():
            with ruta_local.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
        else:
            raw = subprocess.check_output(
                ["git", "-C", str(REPO_ROOT), "show", "deliverable-4:Deliverable 4/datos/preguntas_nuevas_20.csv"],
                text=True,
            )
            rows = list(csv.DictReader(io.StringIO(raw)))
    else:
        raise ValueError(f"Dataset desconocido: {dataset}")

    if qids_filtro:
        rows = [r for r in rows if str(r.get("id", "")).strip() in qids_filtro]
    return rows


def ejecutar_benchmark(
    dataset: str = "dificil_25",
    modelo: str = "qwen3:4b-instruct",
    usar_embeddings: bool = True,
    prebuscar: bool = True,
    qids_filtro: set[str] | None = None,
    salida_path: Path | None = None,
    reanudar: bool = True,
) -> Path:
    """Corre el asistente pregunta por pregunta guardando progreso incremental en JSON."""
    rows = cargar_preguntas(dataset, qids_filtro=qids_filtro)
    slug_modelo = re.sub(r"[^a-zA-Z0-9._-]+", "_", modelo)
    out = salida_path or (DEFAULT_OUT_DIR / f"benchmark_{dataset}_{slug_modelo}.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    existentes: dict[str, dict[str, Any]] = {}
    if reanudar and out.is_file():
        prev = json.loads(out.read_text(encoding="utf-8"))
        for item in prev.get("casos", []):
            existentes[str(item["id"])] = item

    cfg = ConfigAsistente(modelo=modelo, usar_embeddings=usar_embeddings)
    asistente = AsistenteUdeC(config=cfg)
    corpus_ids = set(asistente.buscador.por_id.keys())

    por_id: dict[str, dict[str, Any]] = dict(existentes)
    for idx, row in enumerate(rows, start=1):
        qid = str(row["id"]).strip()
        if qid in por_id:
            continue

        t0 = time.perf_counter()
        res = asistente.responder(row["pregunta"], prebuscar=prebuscar)
        citas = sorted(set(_CITE_RE.findall(res.respuesta)))
        citas_validas = [c for c in citas if c in corpus_ids]
        citas_inexistentes = [c for c in citas if c not in corpus_ids]

        caso = {
            "id": qid,
            "categoria": row.get("categoria", ""),
            "pregunta": row["pregunta"],
            "gold_dato": row.get("gold_dato", ""),
            "gold_fuente": row.get("gold_fuente", ""),
            "respuesta": res.respuesta,
            "modelo": res.modelo,
            "segundos": res.segundos,
            "turnos_modelo": res.turnos_modelo,
            "herramientas": [
                {"nombre": p.nombre, "argumentos": p.argumentos, "resultado": p.resultado}
                for p in res.pasos_herramientas
            ],
            "fuentes_ids": [f["id"] for f in res.fuentes],
            "citas_en_respuesta": citas,
            "citas_validas": citas_validas,
            "citas_inexistentes": citas_inexistentes,
            "correcto_manual": None,
            "nota_revision": "",
        }
        por_id[qid] = caso
        casos = list(por_id.values())
        payload = {
            "dataset": dataset,
            "modelo": modelo,
            "usar_embeddings": usar_embeddings,
            "prebuscar": prebuscar,
            "completados": len(casos),
            "total": max(len(rows), len(casos)),
            "segundos_totales": round(sum(c["segundos"] for c in casos), 2),
            "casos": casos,
        }
        with out.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")

        tools_str = ", ".join(h["nombre"] for h in caso["herramientas"]) or "ninguna"
        print(
            f"[{idx}/{len(rows)}] {qid} ({caso['categoria']}) | {caso['segundos']:.1f}s | "
            f"turnos={caso['turnos_modelo']} | tools=[{tools_str}] | elapsed={time.perf_counter()-t0:.1f}s",
            flush=True,
        )

    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark del asistente local UdeC")
    parser.add_argument("--dataset", default="dificil_25", choices=["dificil_25", "congelado_50", "nuevas_20"])
    parser.add_argument("--modelo", default="qwen3:4b-instruct")
    parser.add_argument("--solo-lexico", action="store_true")
    parser.add_argument("--sin-prebusqueda", action="store_true")
    parser.add_argument("--qids", default="", help="Lista separada por comas, ej. H01,H02")
    parser.add_argument("--salida", default=None)
    parser.add_argument("--no-reanudar", action="store_true")
    args = parser.parse_args(argv)

    qids = {q.strip() for q in args.qids.split(",") if q.strip()} if args.qids else None
    out = Path(args.salida) if args.salida else None
    ruta = ejecutar_benchmark(
        dataset=args.dataset,
        modelo=args.modelo,
        usar_embeddings=not args.solo_lexico,
        prebuscar=not args.sin_prebusqueda,
        qids_filtro=qids,
        salida_path=out,
        reanudar=not args.no_reanudar,
    )
    print("Benchmark guardado en:", ruta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
