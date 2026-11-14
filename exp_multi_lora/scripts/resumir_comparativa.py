"""Resumen comparativo de telemetría y aciertos (Control Base vs Solo Redactor D4 vs Multi-LoRA).

Lee directamente los CSV/JSON producidos por `evaluar_d4.py` y `evaluar_multi_lora.py`
sin modificar los archivos oficiales de `Deliverable 4/`.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
D4_EVAL_DIR = REPO_ROOT / "Deliverable 4" / "evaluacion"


def _es_verdadero(valor: Any) -> bool:
    return str(valor or "").strip().lower() in {"1", "true", "si", "sí", "correcto"}


def _es_falso(valor: Any) -> bool:
    return str(valor or "").strip().lower() in {"0", "false", "no", "incorrecto"}


def _to_int(valor: Any, default: int = 0) -> int:
    try:
        return int(float(valor))
    except (TypeError, ValueError):
        return default


def _to_float(valor: Any, default: float = 0.0) -> float:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return default


def cargar_filas_csv(csv_path: Path) -> list[dict[str, str]]:
    """Carga un CSV de evaluación y devuelve sus filas como diccionarios."""
    with Path(csv_path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def resumir_telemetria(telemetria_path: Path | None) -> dict[str, Any] | None:
    """Agrega llamadas, tokens y tiempo promedio por rol y adaptador activo."""
    if telemetria_path is None or not Path(telemetria_path).is_file():
        return None
    raw = json.loads(Path(telemetria_path).read_text(encoding="utf-8"))
    llamadas_por_rol: Counter[str] = Counter()
    llamadas_por_adaptador: Counter[str] = Counter()
    seg_por_rol: Counter[str] = Counter()
    tok_out_por_rol: Counter[str] = Counter()
    total_llamadas = 0

    for lista in raw.values():
        if not isinstance(lista, list):
            continue
        for c in lista:
            rol = str(c.get("agente", "desconocido"))
            adapt = str(
                c.get("adaptador_activo")
                or ("redactor" if c.get("usa_adaptador") else "base")
            )
            llamadas_por_rol[rol] += 1
            llamadas_por_adaptador[f"{rol}:{adapt}"] += 1
            seg_por_rol[rol] += _to_float(c.get("segundos"))
            tok_out_por_rol[rol] += _to_int(c.get("output_tokens"))
            total_llamadas += 1

    return {
        "total_llamadas": total_llamadas,
        "llamadas_por_rol": dict(sorted(llamadas_por_rol.items())),
        "llamadas_por_adaptador": dict(sorted(llamadas_por_adaptador.items())),
        "segundos_por_rol": {k: round(v, 2) for k, v in sorted(seg_por_rol.items())},
        "output_tokens_por_rol": dict(sorted(tok_out_por_rol.items())),
    }


def resumir_corrida(
    etiqueta: str,
    csv_path: Path,
    telemetria_path: Path | None = None,
) -> dict[str, Any]:
    """Calcula métricas operacionales y de exactitud para una corrida de evaluación."""
    filas = cargar_filas_csv(csv_path)
    total = len(filas)
    ciclos_sum = sum(_to_int(r.get("ciclos")) for r in filas)
    llamadas_sum = sum(_to_int(r.get("llamadas_modelo")) for r in filas)
    seg_sum = sum(_to_float(r.get("segundos")) for r in filas)
    fallbacks_sum = sum(_to_int(r.get("fallbacks")) for r in filas)
    errores = sum(1 for r in filas if str(r.get("error", "")).strip())
    aprobados = sum(1 for r in filas if _es_verdadero(r.get("aprobado_verificador")))

    anotados = [
        r for r in filas if _es_verdadero(r.get("correcto")) or _es_falso(r.get("correcto"))
    ]
    correctos = sum(1 for r in anotados if _es_verdadero(r.get("correcto")))

    res = {
        "etiqueta": etiqueta,
        "csv_path": str(csv_path),
        "total": total,
        "ciclos_total": ciclos_sum,
        "ciclos_promedio": round(ciclos_sum / total, 2) if total else 0.0,
        "llamadas_modelo_total": llamadas_sum,
        "segundos_total": round(seg_sum, 2),
        "segundos_promedio": round(seg_sum / total, 2) if total else 0.0,
        "fallbacks_total": fallbacks_sum,
        "errores": errores,
        "aprobado_verificador_true": aprobados,
        "correcto_anotados": len(anotados),
        "correctos": correctos if anotados else None,
        "accuracy_pct": round(100.0 * correctos / len(anotados), 1) if anotados else None,
        "telemetria": resumir_telemetria(telemetria_path),
    }
    return res


def diferencias_por_pregunta(
    csv_base: Path,
    csv_exp: Path,
    etiqueta_base: str = "solo_redactor",
    etiqueta_exp: str = "multi_lora",
) -> list[dict[str, Any]]:
    """Lista las preguntas donde difieren ciclos, llamadas, veredicto o respuesta."""
    filas_a = {f"{r['set']}:{r['id']}": r for r in cargar_filas_csv(csv_base)}
    filas_b = {f"{r['set']}:{r['id']}": r for r in cargar_filas_csv(csv_exp)}
    cambios: list[dict[str, Any]] = []
    for qid in filas_b:
        if qid not in filas_a:
            continue
        ra, rb = filas_a[qid], filas_b[qid]
        diff_campos: list[str] = []
        if _to_int(ra.get("ciclos")) != _to_int(rb.get("ciclos")):
            diff_campos.append("ciclos")
        if _es_verdadero(ra.get("aprobado_verificador")) != _es_verdadero(
            rb.get("aprobado_verificador")
        ):
            diff_campos.append("aprobado_verificador")
        if ra.get("correcto") and rb.get("correcto") and ra.get("correcto") != rb.get("correcto"):
            diff_campos.append("correcto")
        if ra.get("respuesta_sistema", "").strip() != rb.get("respuesta_sistema", "").strip():
            diff_campos.append("respuesta")
        if diff_campos:
            cambios.append(
                {
                    "qid": qid,
                    "categoria": rb.get("categoria", ""),
                    "campos_cambiados": diff_campos,
                    etiqueta_base: {
                        "ciclos": _to_int(ra.get("ciclos")),
                        "llamadas": _to_int(ra.get("llamadas_modelo")),
                        "aprobado": ra.get("aprobado_verificador"),
                        "correcto": ra.get("correcto"),
                    },
                    etiqueta_exp: {
                        "ciclos": _to_int(rb.get("ciclos")),
                        "llamadas": _to_int(rb.get("llamadas_modelo")),
                        "aprobado": rb.get("aprobado_verificador"),
                        "correcto": rb.get("correcto"),
                    },
                }
            )
    return cambios


def formatear_tabla_markdown(resumenes: list[dict[str, Any]]) -> str:
    """Construye una tabla Markdown comparando múltiples corridas."""
    lineas = [
        "| Condición | N | Aciertos | Ciclos prom. | Llamadas modelo | Aprob. Verificador | Fallbacks | Errores | Tiempo total (s) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in resumenes:
        if r["correctos"] is not None:
            aciertos_txt = f"{r['correctos']}/{r['correcto_anotados']} ({r['accuracy_pct']}%)"
        else:
            aciertos_txt = "Pendiente auditoría"
        lineas.append(
            f"| {r['etiqueta']} | {r['total']} | {aciertos_txt} | "
            f"{r['ciclos_promedio']:.2f} | {r['llamadas_modelo_total']} | "
            f"{r['aprobado_verificador_true']}/{r['total']} | {r['fallbacks_total']} | "
            f"{r['errores']} | {r['segundos_total']:.1f} |"
        )
    return "\n".join(lineas)


def construir_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Compara telemetría y resultados entre D4 Base/Redactor y Multi-LoRA."
    )
    p.add_argument("--multi-csv", type=Path, required=True)
    p.add_argument("--multi-telemetria", type=Path, default=None)
    p.add_argument(
        "--benchmark",
        choices=("75", "nuevas_20"),
        default="nuevas_20",
        help="Conjunto de referencia D4 con el cual comparar.",
    )
    p.add_argument("--etiqueta-multi", default="Multi-LoRA (4 agentes)")
    p.add_argument("--salida-json", type=Path, default=None)
    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_arg_parser().parse_args(argv)
    if args.benchmark == "75":
        csv_base = D4_EVAL_DIR / "resultados_control_base_D4_auditados.csv"
        tel_base = D4_EVAL_DIR / "telemetria_control_base_D4.json"
        csv_red = D4_EVAL_DIR / "resultados_agentes_D4_auditados.csv"
        tel_red = D4_EVAL_DIR / "telemetria_llamadas.json"
    else:
        csv_base = D4_EVAL_DIR / "resultados_nuevas20_base_D4_auditados.csv"
        tel_base = D4_EVAL_DIR / "telemetria_nuevas20_base_D4.json"
        csv_red = D4_EVAL_DIR / "resultados_nuevas20_ft_D4_auditados.csv"
        tel_red = D4_EVAL_DIR / "telemetria_nuevas20_ft_D4.json"

    resumenes = [
        resumir_corrida("Control Base D4", csv_base, tel_base),
        resumir_corrida("Solo Redactor D4", csv_red, tel_red),
        resumir_corrida(args.etiqueta_multi, args.multi_csv, args.multi_telemetria),
    ]
    tabla = formatear_tabla_markdown(resumenes)
    print(tabla)

    diffs = diferencias_por_pregunta(csv_red, args.multi_csv)
    print(f"\nPreguntas con diferencias vs Solo Redactor D4: {len(diffs)}")
    if args.salida_json is not None:
        args.salida_json.parent.mkdir(parents=True, exist_ok=True)
        args.salida_json.write_text(
            json.dumps(
                {"resumenes": resumenes, "diferencias_vs_solo_redactor": diffs},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
