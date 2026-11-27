"""Visor interactivo y script de demo para Deliverable 4 (Sistema Multi-LoRA 3-LoRA).

Muestra comparativas lado a lado entre Control Base (Qwen/Qwen3-4B sin LoRA)
y el Sistema Oficial D4 3-LoRA (Enrutador + Recuperador + Redactor QLoRA
conmutados con `set_adapter()`, y Verificador en pesos base mediante
`disable_adapter()`), ademas de un resumen transparente de fallos reales.

Modos de uso:
  1) Offline (recomendado, usa trazas reales ejecutadas en A100 bf16):
       python3 "Deliverable 4/video/mostrar_demo_d4.py"
       python3 "Deliverable 4/video/mostrar_demo_d4.py" --qids dificil_25:H07 dificil_25:H18
       python3 "Deliverable 4/video/mostrar_demo_d4.py" --todos --mostrar-fallos

  2) En vivo (GPU Colab, invoca scripts/evaluar_multi_lora.py):
       python3 "Deliverable 4/video/mostrar_demo_d4.py" --live --qids dificil_25:H07
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


DELIVERABLE4_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = DELIVERABLE4_DIR / "scripts"
EVALUACION_DIR = DELIVERABLE4_DIR / "evaluacion"

DEFAULT_COMPARATIVA_PATH = EVALUACION_DIR / "comparativa_base_vs_3lora.json"
DEFAULT_FALLOS_PATH = EVALUACION_DIR / "casos_fallo_y_regresion_3lora.json"
DEFAULT_QIDS = ("dificil_25:H07", "dificil_25:H18", "congelado_50:43")
DEFAULT_FAIL_QIDS = ("dificil_25:H03", "dificil_25:H17", "dificil_25:H06")

AGENTES_CON_LORA = ("enrutador", "recuperador", "redactor")


def etiqueta_adaptador(agente: str, solo_base: bool) -> str:
    """Devuelve la etiqueta legible de estado LoRA para un agente del grafo."""
    agente_norm = str(agente).strip().lower()
    if solo_base or agente_norm == "verificador":
        return "LoRA OFF (Base)"
    if agente_norm in AGENTES_CON_LORA:
        return f"LoRA ON ({agente_norm.capitalize()} FT)"
    return "LoRA OFF (Base)"


def cargar_comparativas(path: Path = DEFAULT_COMPARATIVA_PATH) -> dict[str, dict[str, Any]]:
    """Carga comparativa Pareada Base vs 3-LoRA indexada por `qid`."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        pares: dict[str, dict[str, Any]] = {}
        for item in data:
            qid = str(item.get("qid") or f"{item.get('set', '')}:{item.get('id', '')}")
            normalizado = dict(item)
            if "finetuned_3lora" not in normalizado and "finetuned_redactor" in normalizado:
                normalizado["finetuned_3lora"] = normalizado["finetuned_redactor"]
            pares[qid] = normalizado
        return pares
    if isinstance(data, dict):
        pares = {}
        for qid, item in data.items():
            normalizado = dict(item)
            normalizado.setdefault("qid", str(qid))
            if "finetuned_3lora" not in normalizado and "finetuned_redactor" in normalizado:
                normalizado["finetuned_3lora"] = normalizado["finetuned_redactor"]
            pares[str(qid)] = normalizado
        return pares
    raise ValueError(f"Formato no reconocido en comparativa: {path}")


def cargar_fallos_y_regresiones(path: Path = DEFAULT_FALLOS_PATH) -> dict[str, Any]:
    """Carga la auditoria de fallos reales del sistema oficial 3-LoRA."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def construir_comando_live(
    qids: list[str],
    output_dir: Path,
    adaptador_enrutador: str | None = None,
    adaptador_recuperador: str | None = None,
    adaptador_redactor: str | None = None,
) -> list[str]:
    """Construye la llamada CLI a `scripts/evaluar_multi_lora.py` para modo live."""
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "evaluar_multi_lora.py"),
        "--agentes",
        "enrutador,recuperador,redactor",
        "--comparar-vs-base",
        ",".join(qids),
        "--solo-comparativa",
        "--verbose-pasos",
        "--output-dir",
        str(output_dir),
    ]
    if adaptador_enrutador:
        cmd.extend(["--adaptador-enrutador", adaptador_enrutador])
    if adaptador_recuperador:
        cmd.extend(["--adaptador-recuperador", adaptador_recuperador])
    if adaptador_redactor:
        cmd.extend(["--adaptador-redactor", adaptador_redactor])
    return cmd


def ejecutar_comparativa_live(
    qids: list[str],
    output_dir: Path,
    adaptador_enrutador: str | None = None,
    adaptador_recuperador: str | None = None,
    adaptador_redactor: str | None = None,
) -> Path:
    """Ejecuta `evaluar_multi_lora.py --comparar-vs-base` y retorna el JSON generado."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = construir_comando_live(
        qids=qids,
        output_dir=out_dir,
        adaptador_enrutador=adaptador_enrutador,
        adaptador_recuperador=adaptador_recuperador,
        adaptador_redactor=adaptador_redactor,
    )
    subprocess.run(cmd, check=True)
    return out_dir / "comparativa_base_vs_3lora.json"


def _contar_llamadas(lado: dict[str, Any]) -> int:
    """Devuelve `llamadas_modelo` o lo reconstruye desde los pasos LLM de la traza."""
    valor = lado.get("llamadas_modelo")
    if valor is not None:
        return int(valor)
    return sum(1 for p in lado.get("traza", []) if not p.get("decidido_por"))


def _resumir_paso(paso: dict[str, Any], solo_base: bool) -> str:
    """Resume una entrada de `traza` mostrando agente, estado LoRA y accion."""
    idx = paso.get("paso", "?")
    agente = str(paso.get("agente", "?")).lower()
    decidido_por = paso.get("decidido_por")
    if decidido_por == "sistema":
        etiqueta = "Sistema (busqueda inicial)"
    elif decidido_por:
        etiqueta = f"Sistema ({decidido_por})"
    else:
        etiqueta = etiqueta_adaptador(agente, solo_base)

    salida = paso.get("salida", {})
    if agente == "enrutador" and isinstance(salida, dict):
        detalle = (
            f"tipo={salida.get('tipo')} docs={salida.get('documentos')} "
            f"subs={len(salida.get('sub_consultas', []))}"
        )
    elif agente == "recuperador" and isinstance(salida, dict):
        accion = salida.get("accion")
        args = salida.get("args", {})
        if accion == "buscar":
            detalle = f"buscar('{str(args.get('consulta', ''))[:48]}...', k={args.get('k')})"
        elif accion in {"traer", "existe"}:
            detalle = f"{accion}({args.get('doc')}, art={args.get('n')})"
        elif accion == "suficiente":
            detalle = f"suficiente(citas={len(paso.get('entrada', {}).get('evidencia_reunida', []))})"
        else:
            detalle = f"{accion}({args})"
    elif agente == "redactor":
        texto = str(salida.get("respuesta", "")) if isinstance(salida, dict) else str(salida)
        preview = " ".join(texto.split())[:86]
        citas = salida.get("citas_detectadas") if isinstance(salida, dict) else []
        extra = f", citas={citas}" if citas else ""
        detalle = f"borrador({len(texto)} chars{extra}): {preview}..."
    elif agente == "verificador" and isinstance(salida, dict):
        estado = "APROBADO" if salida.get("aprobado") else f"RECHAZO->{salida.get('destino')}"
        motivo = str(salida.get("motivo", ""))[:80]
        detalle = f"{estado} | {motivo}"
    else:
        detalle = str(salida)[:80]
    return f"  [{idx}] {agente:<11} [{etiqueta}] -> {detalle}"


def _estado_auditoria(lado: dict[str, Any]) -> str:
    """Distingue entre veredicto auditado (`CORRECTA`/`INCORRECTA`) y corrida sin calificar."""
    val = lado.get("correcto")
    if val is None or val == "":
        return "SIN CALIFICAR"
    if isinstance(val, str):
        if val.strip() in {"1", "true", "True"}:
            return "CORRECTA"
        if val.strip() in {"0", "false", "False"}:
            return "INCORRECTA"
        return "SIN CALIFICAR"
    return "CORRECTA" if bool(val) else "INCORRECTA"


def _estado_verificador(ver: dict[str, Any]) -> str:
    aprob = bool(ver.get("aprobado"))
    return "APROBADO" if aprob else f"RECHAZO->{ver.get('destino', '?')}"


def _formatear_lado(titulo: str, lado: dict[str, Any], solo_base: bool) -> str:
    """Formatea un sistema (Control Base o D4 3-LoRA) en texto plano."""
    ok = _estado_auditoria(lado)
    ver = lado.get("veredicto", {})
    llamadas = _contar_llamadas(lado)
    cab = (
        f"--- {titulo} ---\n"
        f"Resultado: {ok} | Ciclos: {lado.get('ciclos')} | "
        f"Llamadas LLM: {llamadas} | Tiempo: {lado.get('segundos')}s\n"
        f"Verificador final: {_estado_verificador(ver)} ({ver.get('motivo', '')})\n"
        f"Fuentes reunidas: {lado.get('fuentes_traidas')}\n"
        f"Traza paso a paso:"
    )
    pasos = [_resumir_paso(p, solo_base=solo_base) for p in lado.get("traza", [])]
    resp = f"Respuesta emitida:\n{lado.get('respuesta', '')}"
    return "\n".join([cab, *pasos, resp])


def formatear_comparativa_texto(caso: dict[str, Any]) -> str:
    """Genera una ficha comparativa completa de un QID para terminal."""
    base = caso.get("base", {})
    ft = caso.get("finetuned_3lora", {})
    sep = "=" * 86
    header = (
        f"{sep}\n"
        f"CASO {caso.get('qid')} | Categoria: {caso.get('categoria')}\n"
        f"Pregunta: {caso.get('pregunta')}\n"
        f"Referencia esperada: {caso.get('gold_dato')} [{caso.get('gold_fuente')}]\n"
        f"{sep}"
    )
    lado_base = _formatear_lado("CONTROL BASE (Qwen/Qwen3-4B · LoRA OFF en los 4 agentes)", base, solo_base=True)
    lado_ft = _formatear_lado(
        "D4 3-LoRA OFICIAL (Enrutador + Recuperador + Redactor LoRA ON · Verificador Base)",
        ft,
        solo_base=False,
    )
    return f"{header}\n{lado_base}\n\n{lado_ft}\n"


def render_comparativa_html(caso: dict[str, Any]) -> str:
    """Genera tarjetas HTML lado a lado listas para `IPython.display.HTML` en Colab."""

    def _badge(lado: dict[str, Any]) -> str:
        estado = _estado_auditoria(lado)
        if estado == "CORRECTA":
            st_aud = "background:#14532d;color:#dcfce7;"
        elif estado == "INCORRECTA":
            st_aud = "background:#7f1d1d;color:#fee2e2;"
        else:
            st_aud = "background:#334155;color:#e2e8f0;"

        ver = lado.get("veredicto", {})
        ver_txt = f"Verificador: {_estado_verificador(ver)}"
        st_ver = (
            "background:#065f46;color:#d1fae5;"
            if ver.get("aprobado")
            else "background:#78350f;color:#fef3c7;"
        )
        return (
            f'<div style="display:flex;gap:6px;flex-wrap:wrap;">'
            f'<span style="{st_ver}padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;">{html.escape(ver_txt)}</span>'
            f'<span style="{st_aud}padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;">{estado}</span>'
            f"</div>"
        )

    def _card(titulo: str, acento: str, lado: dict[str, Any], solo_base: bool) -> str:
        traza_html = "<br>".join(
            html.escape(_resumir_paso(p, solo_base=solo_base)) for p in lado.get("traza", [])
        )
        resp_html = html.escape(str(lado.get("respuesta", ""))).replace("\n", "<br>")
        llamadas = _contar_llamadas(lado)
        meta = (
            f"Ciclos: <b>{lado.get('ciclos')}</b> · "
            f"Llamadas: <b>{llamadas}</b> · "
            f"Tiempo: <b>{lado.get('segundos')}s</b>"
        )
        return (
            f'<div style="flex:1;min-width:340px;border:2px solid {acento};border-radius:10px;'
            f'padding:14px;background:#0f172a;color:#e2e8f0;font-family:ui-sans-serif,system-ui;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px;">'
            f'<span style="font-weight:700;color:#f8fafc;">{html.escape(titulo)}</span>'
            f"{_badge(lado)}</div>"
            f'<div style="font-size:12px;color:#cbd5e1;margin-bottom:8px;">{meta}</div>'
            f'<div style="font-size:11.5px;background:#1e293b;padding:8px;border-radius:6px;'
            f'font-family:ui-monospace,monospace;white-space:pre-wrap;margin-bottom:10px;">{traza_html}</div>'
            f'<div style="font-size:12.5px;line-height:1.45;background:#111827;padding:10px;'
            f'border-radius:6px;border-left:3px solid {acento};">{resp_html}</div>'
            f"</div>"
        )

    preg = html.escape(str(caso.get("pregunta", "")))
    gold = html.escape(f"{caso.get('gold_dato', '')} [{caso.get('gold_fuente', '')}]")
    base = caso.get("base", {})
    ft = caso.get("finetuned_3lora", {})
    return (
        f'<div style="margin:14px 0;font-family:ui-sans-serif,system-ui;">'
        f'<div style="background:#1e293b;color:#f1f5f9;padding:12px 14px;border-radius:10px;margin-bottom:10px;">'
        f'<div style="font-size:12px;color:#93c5fd;font-weight:700;">{html.escape(str(caso.get("qid")))} · {html.escape(str(caso.get("categoria")))}</div>'
        f'<div style="font-size:14px;font-weight:600;margin:4px 0;">{preg}</div>'
        f'<div style="font-size:12px;color:#cbd5e1;"><b>Pauta esperada:</b> {gold}</div>'
        f"</div>"
        f'<div style="display:flex;gap:12px;flex-wrap:wrap;">'
        f'{_card("CONTROL BASE · LoRA OFF (4 agentes)", "#dc2626", base, solo_base=True)}'
        f'{_card("D4 3-LoRA · Enr+Rec+Red FT · Verificador Base", "#059669", ft, solo_base=False)}'
        f"</div></div>"
    )


def formatear_fallos_texto(
    fallos: dict[str, Any],
    qids_filtro: tuple[str, ...] | None = DEFAULT_FAIL_QIDS,
) -> str:
    """Formatea la seccion de transparencia con fallos reales del sistema 3-LoRA."""
    casos = fallos.get("casos", [])
    seleccionados = (
        [c for c in casos if c.get("qid") in qids_filtro]
        if qids_filtro is not None
        else casos
    )
    lineas = [
        "=" * 86,
        f"AUDITORIA DE FALLOS REALES D4 3-LoRA ({len(seleccionados)} mostrados de {fallos.get('total_casos_documentados', len(casos))})",
        str(fallos.get("descripcion", "")),
        "=" * 86,
    ]
    for caso in seleccionados:
        lineas.extend(
            [
                f"\n[{caso.get('qid')}] Causa raiz: {caso.get('causa_raiz')} | Tipo: {caso.get('tipo_fallo')} | "
                f"Ciclos: {caso.get('ciclos')} | Llamadas: {caso.get('llamadas_modelo')} | {caso.get('segundos')}s",
                f"Pregunta: {caso.get('pregunta')}",
                f"Diagnostico: {caso.get('diagnostico_auditoria')}",
                f"Respuesta emitida: {caso.get('respuesta_final')}",
            ]
        )
    return "\n".join(lineas) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demo comparativa Control Base vs D4 3-LoRA.")
    parser.add_argument("--listar", action="store_true", help="Lista QIDs disponibles en comparativa y fallos.")
    parser.add_argument("--qid", default=None, help="QID unico a mostrar (opcional, sobreescribe --qids).")
    parser.add_argument("--qids", nargs="+", default=list(DEFAULT_QIDS), help="QIDs a mostrar.")
    parser.add_argument("--todos", action="store_true", help="Muestra todos los casos de la comparativa.")
    parser.add_argument("--mostrar-fallos", action="store_true", help="Muestra trazas de fallos reales.")
    parser.add_argument("--live", action="store_true", help="Ejecuta los QIDs en GPU mediante evaluar_multi_lora.py.")
    parser.add_argument("--output-dir", type=Path, default=EVALUACION_DIR / "demo_live_3lora")
    parser.add_argument("--json-comparativa", type=Path, default=DEFAULT_COMPARATIVA_PATH)
    parser.add_argument("--json-fallos", type=Path, default=DEFAULT_FALLOS_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.listar:
        comp = cargar_comparativas(args.json_comparativa)
        print("Comparativas disponibles:", ", ".join(comp.keys()))
        if args.json_fallos.exists():
            fallos = cargar_fallos_y_regresiones(args.json_fallos)
            print("Fallos documentados:", ", ".join(c.get("qid", "") for c in fallos.get("casos", [])))
        return 0

    qids_objetivo = [args.qid] if args.qid else args.qids
    ruta_comp = (
        ejecutar_comparativa_live(qids_objetivo, args.output_dir)
        if args.live
        else args.json_comparativa
    )
    comparativas = cargar_comparativas(ruta_comp)
    qids_mostrar = list(comparativas.keys()) if args.todos else qids_objetivo
    faltantes = [q for q in qids_mostrar if q not in comparativas]
    if faltantes:
        raise ValueError(f"QID(s) no encontrados en {ruta_comp}: {faltantes}")
    for qid in qids_mostrar:
        print(formatear_comparativa_texto(comparativas[qid]))

    if args.mostrar_fallos and args.json_fallos.exists():
        fallos = cargar_fallos_y_regresiones(args.json_fallos)
        print(formatear_fallos_texto(fallos))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
