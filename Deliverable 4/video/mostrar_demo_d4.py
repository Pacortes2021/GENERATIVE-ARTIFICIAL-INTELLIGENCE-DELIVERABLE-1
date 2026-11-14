"""Demostración y visor de trazas intermedias Base vs Fine-tuned (Deliverable 4).

Permite inspeccionar paso a paso los mensajes intermedios entre los cuatro agentes
(`Enrutador`, `Recuperador`, `Redactor`, `Verificador`) comparando el sistema
completamente Base (`LoRA OFF`) frente al sistema con el adaptador QLoRA acoplado
únicamente en el `Redactor` (`LoRA ON`), usando los registros oficiales guardados o
disparando una corrida en vivo sobre GPU mediante `scripts/evaluar_d4.py`.
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

DELIVERABLE4_DIR = Path(__file__).resolve().parents[1]
DEFAULT_COMPARATIVA_PATH = (
    DELIVERABLE4_DIR / "evaluacion" / "comparativa_base_vs_finetuned.json"
)
DEFAULT_FALLOS_PATH = (
    DELIVERABLE4_DIR / "evaluacion" / "casos_fallo_y_regresion.json"
)
EVAL_SCRIPT_PATH = DELIVERABLE4_DIR / "scripts" / "evaluar_d4.py"
DEFAULT_DEMO_QIDS: tuple[str, ...] = ("dificil_25:H07", "dificil_25:H14")


def _serializar_campo(valor: Any) -> str:
    if isinstance(valor, str):
        return valor.strip()
    return json.dumps(valor, ensure_ascii=False)


def _acortar(valor: Any, limite: int = 340, completo: bool = False) -> str:
    texto = " ".join(_serializar_campo(valor).split())
    if completo or limite <= 0 or len(texto) <= limite:
        return texto
    return texto[: limite - 3].rstrip() + "..."


def etiqueta_adaptador(agente: str, solo_base: bool) -> str:
    """Indica si el paso ejecuta con el adaptador QLoRA activo o con pesos base."""
    if str(agente).lower() == "redactor" and not solo_base:
        return "LoRA ON (Redactor FT)"
    return "LoRA OFF (Base)"


def cargar_comparativas(path: Path = DEFAULT_COMPARATIVA_PATH) -> dict[str, dict[str, Any]]:
    """Carga los casos pareados Base vs Fine-tuned indexados por `qid`."""
    if not path.is_file():
        raise FileNotFoundError(f"No existe el archivo de comparativa: {path}")
    datos = json.loads(path.read_text(encoding="utf-8"))
    return {str(item["qid"]): item for item in datos}


def cargar_fallos(path: Path = DEFAULT_FALLOS_PATH) -> dict[str, dict[str, Any]]:
    """Carga los casos auditados de fallo/degradación indexados por `qid`."""
    if not path.is_file():
        raise FileNotFoundError(f"No existe el archivo de fallos: {path}")
    datos = json.loads(path.read_text(encoding="utf-8"))
    return {str(item["qid"]): item for item in datos.get("casos", [])}


def formatear_traza_pasos(
    traza: list[dict[str, Any]],
    solo_base: bool,
    completo: bool = False,
) -> str:
    """Formatea los intercambios intermedios entre agentes para consola."""
    lineas: list[str] = []
    for paso in traza:
        agente = str(paso.get("agente", "?"))
        num = paso.get("paso", "?")
        auto = " [regla automática]" if paso.get("decidido_por") else ""
        fb = " [FALLBACK]" if paso.get("fallback") else ""
        adapt = "regla Python" if paso.get("decidido_por") else etiqueta_adaptador(agente, solo_base)
        lineas.append(f"  [{num}] {agente.upper()} · {adapt}{auto}{fb}")
        lineas.append(f"      entrada : {_acortar(paso.get('entrada', ''), 260, completo)}")
        lineas.append(f"      salida  : {_acortar(paso.get('salida', ''), 320, completo)}")
        if paso.get("observacion") is not None:
            lineas.append(
                f"      observ. : {_acortar(paso.get('observacion'), 260, completo)}"
            )
    return "\n".join(lineas)


def _formatear_bloque_sistema(
    titulo: str,
    datos: dict[str, Any],
    solo_base: bool,
    mostrar_traza: bool,
    completo: bool,
) -> list[str]:
    veredicto = datos.get("veredicto") or {}
    aprob = veredicto.get("aprobado")
    motivo = veredicto.get("motivo", "")
    lineas = [
        f"--- {titulo} ---",
        (
            f"Ciclos: {datos.get('ciclos')} | Pasos traza: {len(datos.get('traza', []))} | "
            f"Tiempo: {datos.get('segundos')} s | Verificador: aprobado={aprob}"
        ),
        f"Fuentes recuperadas: {datos.get('fuentes_traidas', '')}",
        f"Motivo Verificador : {_acortar(motivo, 260, completo)}",
        "Respuesta final:",
        f"  {datos.get('respuesta', '').strip()}",
    ]
    if mostrar_traza:
        lineas.append("Mensajes intermedios entre agentes:")
        lineas.append(formatear_traza_pasos(datos.get("traza", []), solo_base=solo_base, completo=completo))
    return lineas


def formatear_comparativa_texto(
    caso: dict[str, Any],
    mostrar_traza: bool = True,
    completo: bool = False,
) -> str:
    """Genera una vista legible Base vs Fine-tuned para un mismo `qid`."""
    sep = "=" * 84
    lineas = [
        sep,
        f"CASO {caso['qid']} ({caso.get('categoria', '')})",
        f"Pregunta : {caso['pregunta']}",
        f"Pauta    : {caso['gold_dato']}  |  Fuente: {caso['gold_fuente']}",
        sep,
    ]
    lineas.extend(
        _formatear_bloque_sistema(
            "SISTEMA BASE D3 (4 agentes con Qwen3-4B base · LoRA OFF)",
            caso["base"],
            solo_base=True,
            mostrar_traza=mostrar_traza,
            completo=completo,
        )
    )
    lineas.append("")
    lineas.extend(
        _formatear_bloque_sistema(
            "SISTEMA D4 FINE-TUNED (solo Redactor con QLoRA · otros 3 agentes Base)",
            caso["finetuned_redactor"],
            solo_base=False,
            mostrar_traza=mostrar_traza,
            completo=completo,
        )
    )
    return "\n".join(lineas)


def formatear_fallo_texto(
    caso: dict[str, Any],
    mostrar_traza: bool = True,
    completo: bool = False,
) -> str:
    """Formatea un caso de fallo o degradación desde `casos_fallo_y_regresion.json`."""
    sep = "=" * 84
    lineas = [
        sep,
        f"ANÁLISIS DE FALLO {caso['qid']} ({caso.get('tipo_fallo', '')})",
        f"Causa raíz : {caso.get('causa_raiz', '')} | Transición D3->D4: {caso.get('transicion_d3_a_d4', '')}",
        f"Pregunta   : {caso['pregunta']}",
        f"Pauta      : {caso['gold_dato']} | Fuente: {caso['gold_fuente']}",
        f"Diagnóstico: {caso.get('diagnostico_auditoria', '')}",
        f"Ciclos: {caso.get('ciclos')} | Llamadas modelo: {caso.get('llamadas_modelo')} | Verificador: aprobado={caso.get('aprobado_verificador')}",
        f"Respuesta D4 final:\n  {caso.get('respuesta_final', '').strip()}",
    ]
    if mostrar_traza:
        lineas.append("Traza intermedia completa:")
        lineas.append(formatear_traza_pasos(caso.get("traza_completa", []), solo_base=False, completo=completo))
    return "\n".join(lineas)


def _html_columna(titulo: str, color_borde: str, datos: dict[str, Any], solo_base: bool, max_chars: int) -> str:
    veredicto = datos.get("veredicto") or {}
    pasos_html: list[str] = []
    for paso in datos.get("traza", []):
        agente = str(paso.get("agente", "?"))
        adapt = "regla Python" if paso.get("decidido_por") else etiqueta_adaptador(agente, solo_base)
        badge_color = "#b7791f" if "LoRA ON" in adapt else "#4a5568"
        ent = html.escape(_acortar(paso.get("entrada", ""), max_chars))
        sal = html.escape(_acortar(paso.get("salida", ""), max_chars))
        obs = ""
        if paso.get("observacion") is not None:
            obs = f"<div><b>Observación:</b> <code>{html.escape(_acortar(paso['observacion'], max_chars))}</code></div>"
        pasos_html.append(
            "<details style='border-top:1px solid #e2e8f0;padding:5px 0'>"
            f"<summary><b>Paso {html.escape(str(paso.get('paso')))} · {html.escape(agente.upper())}</b> "
            f"<span style='color:{badge_color};font-size:12px'>[{html.escape(adapt)}]</span></summary>"
            f"<div><b>Entrada:</b> <code>{ent}</code></div>"
            f"<div><b>Salida:</b> <code>{sal}</code></div>"
            f"{obs}</details>"
        )
    return (
        f"<div style='flex:1;min-width:340px;border:2px solid {color_borde};border-radius:10px;padding:12px;background:#ffffff'>"
        f"<h4 style='margin:0 0 6px 0;color:{color_borde}'>{html.escape(titulo)}</h4>"
        f"<div style='font-size:13px;color:#334155;margin-bottom:8px'>"
        f"Ciclos: <b>{html.escape(str(datos.get('ciclos')))}</b> · "
        f"Pasos: <b>{len(datos.get('traza', []))}</b> · "
        f"Tiempo: <b>{html.escape(str(datos.get('segundos')))} s</b> · "
        f"Verificador: <b>aprobado={html.escape(str(veredicto.get('aprobado')))}</b></div>"
        f"<div style='background:#f8fafc;padding:8px;border-radius:6px;white-space:pre-wrap;font-size:13px;margin-bottom:8px'>"
        f"{html.escape(str(datos.get('respuesta', '').strip()))}</div>"
        f"<div style='font-size:12px;color:#475569;margin-bottom:8px'><b>Motivo Verificador:</b> {html.escape(str(veredicto.get('motivo', '')))}</div>"
        f"<details open><summary><b>Mensajes intermedios ({len(pasos_html)} pasos)</b></summary>{''.join(pasos_html)}</details>"
        "</div>"
    )


def renderizar_comparativa_html(caso: dict[str, Any], max_chars: int = 420) -> str:
    """Construye una tarjeta HTML comparativa Base vs Fine-tuned para Colab/Jupyter."""
    col_base = _html_columna(
        "Sistema Base (4 agentes base · LoRA OFF)",
        "#475569",
        caso["base"],
        solo_base=True,
        max_chars=max_chars,
    )
    col_ft = _html_columna(
        "Sistema D4 Fine-tuned (solo Redactor QLoRA · LoRA ON)",
        "#1b4965",
        caso["finetuned_redactor"],
        solo_base=False,
        max_chars=max_chars,
    )
    return (
        "<div style='font-family:system-ui,-apple-system,sans-serif;border:1px solid #cbd5e1;"
        "border-radius:12px;padding:14px;background:#f8fafc;margin:12px 0'>"
        f"<div style='font-size:12px;color:#475569'><b>{html.escape(str(caso['qid']))}</b> · {html.escape(str(caso.get('categoria', '')))}</div>"
        f"<div style='font-size:15px;font-weight:600;margin:4px 0 8px 0'>{html.escape(str(caso['pregunta']))}</div>"
        f"<div style='font-size:13px;color:#0f172a;margin-bottom:10px'><b>Pauta oficial:</b> {html.escape(str(caso['gold_dato']))} "
        f"<span style='color:#64748b'>({html.escape(str(caso['gold_fuente']))})</span></div>"
        f"<div style='display:flex;gap:12px;flex-wrap:wrap'>{col_base}{col_ft}</div>"
        "</div>"
    )


def ejecutar_comparativa_en_vivo(
    qids: list[str],
    output_dir: Path,
    greedy: bool = False,
    sin_e5: bool = False,
) -> Path:
    """Ejecuta `evaluar_d4.py --solo-comparativa` en GPU para generar trazas frescas."""
    if not EVAL_SCRIPT_PATH.is_file():
        raise FileNotFoundError(f"No existe el script de evaluación: {EVAL_SCRIPT_PATH}")
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(EVAL_SCRIPT_PATH),
        "--solo-comparativa",
        "--comparar-ids",
        ",".join(qids),
        "--output-dir",
        str(output_dir),
    ]
    if greedy:
        cmd.append("--greedy")
    if sin_e5:
        cmd.append("--sin-e5")
    subprocess.run(cmd, check=True)
    return output_dir / "comparativa_base_vs_finetuned.json"


def construir_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Muestra trazas intermedias Base vs Redactor Fine-tuned (Deliverable 4).",
    )
    parser.add_argument("--comparativa", type=Path, default=DEFAULT_COMPARATIVA_PATH)
    parser.add_argument("--fallos", type=Path, default=DEFAULT_FALLOS_PATH)
    parser.add_argument(
        "--qid",
        action="append",
        dest="qids",
        help="QID de comparativa Base vs FT a mostrar (repetible). Por defecto H07 y H14.",
    )
    parser.add_argument(
        "--fallo",
        action="append",
        dest="fallos_qids",
        help="QID adicional de `casos_fallo_y_regresion.json` a mostrar (ej. dificil_25:H06).",
    )
    parser.add_argument("--listar", action="store_true", help="Lista QIDs disponibles y termina.")
    parser.add_argument(
        "--solo-resumen",
        action="store_true",
        help="Oculta los pasos intermedios detallados de los agentes.",
    )
    parser.add_argument(
        "--completo",
        action="store_true",
        help="No recorta cadenas largas en las entradas, salidas u observaciones.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Ejecuta en vivo en GPU vía `scripts/evaluar_d4.py --solo-comparativa` antes de imprimir.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DELIVERABLE4_DIR / "video" / "live_runs",
        help="Carpeta destino cuando se usa `--live`.",
    )
    parser.add_argument("--greedy", action="store_true")
    parser.add_argument("--sin-e5", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = construir_arg_parser().parse_args(argv)
    qids_sel = list(args.qids) if args.qids else list(DEFAULT_DEMO_QIDS)

    if args.live:
        comp_path = ejecutar_comparativa_en_vivo(
            qids_sel,
            output_dir=args.output_dir,
            greedy=args.greedy,
            sin_e5=args.sin_e5,
        )
    else:
        comp_path = args.comparativa

    comparativas = cargar_comparativas(comp_path)
    fallos = cargar_fallos(args.fallos) if args.fallos.is_file() else {}

    if args.listar:
        print("QIDs comparativa Base vs FT:", ", ".join(comparativas.keys()))
        print("QIDs fallos/regresiones    :", ", ".join(fallos.keys()))
        return 0

    for qid in qids_sel:
        if qid not in comparativas:
            disponibles = ", ".join(comparativas.keys())
            raise ValueError(f"QID '{qid}' no está en {comp_path}. Disponibles: {disponibles}")
        print(
            formatear_comparativa_texto(
                comparativas[qid],
                mostrar_traza=not args.solo_resumen,
                completo=args.completo,
            )
        )
        print()

    for qid_f in args.fallos_qids or []:
        if qid_f not in fallos:
            disponibles = ", ".join(fallos.keys())
            raise ValueError(f"QID de fallo '{qid_f}' no está en {args.fallos}. Disponibles: {disponibles}")
        print(
            formatear_fallo_texto(
                fallos[qid_f],
                mostrar_traza=not args.solo_resumen,
                completo=args.completo,
            )
        )
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
