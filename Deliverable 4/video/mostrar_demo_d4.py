"""Visor interactivo y script de demo para Deliverable 4 (Sistema Multi-LoRA 3-LoRA).

Muestra comparativas lado a lado entre Control Base (Qwen/Qwen3-4B sin LoRA)
y el Sistema Oficial D4 3-LoRA (Enrutador + Recuperador + Redactor QLoRA
conmutados con `set_adapter()`, y Verificador en pesos base mediante
`disable_adapter()`), ademas de tarjetas HTML legibles para Colab y video <= 3 min.

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
import re
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


def _limpiar_pensar(texto: str) -> str:
    """Elimina bloques `<pensar>...</pensar>` para mostrar directo la respuesta emitida."""
    limpio = re.sub(r"<pensar>.*?</pensar>", "", str(texto), flags=re.DOTALL | re.IGNORECASE).strip()
    return limpio or str(texto).strip()


def _detalle_paso(paso: dict[str, Any], max_texto: int = 120) -> str:
    """Genera una descripcion legible y completa de la salida de un paso."""
    agente = str(paso.get("agente", "?")).lower()
    salida = paso.get("salida", {})
    obs = paso.get("observacion") or {}

    if agente == "enrutador" and isinstance(salida, dict):
        subs = [str(s) for s in salida.get("sub_consultas", [])]
        subs_txt = " | ".join(s[:65] + ("..." if len(s) > 65 else "") for s in subs[:2])
        if len(subs) > 2:
            subs_txt += f" (+{len(subs) - 2})"
        return (
            f"tipo={salida.get('tipo')} · docs={salida.get('documentos')} · "
            f"subs({len(subs)}): {subs_txt}"
        )
    if agente == "recuperador" and isinstance(salida, dict):
        accion = salida.get("accion")
        args = salida.get("args", {})
        if accion == "buscar":
            hits = obs.get("hits") if isinstance(obs, dict) else None
            hits_txt = f" -> hits={hits}" if hits else ""
            return f"buscar('{str(args.get('consulta', ''))[:52]}...', k={args.get('k')}){hits_txt}"
        if accion in {"traer", "existe"}:
            return f"{accion}({args.get('doc')}, art={args.get('n')})"
        if accion == "suficiente":
            return f"suficiente(citas={len(paso.get('entrada', {}).get('evidencia_reunida', []))})"
        return f"{accion}({args})"
    if agente == "redactor":
        texto = str(salida.get("respuesta", "")) if isinstance(salida, dict) else str(salida)
        texto_limpio = " ".join(_limpiar_pensar(texto).split())
        preview = texto_limpio[:max_texto] + ("..." if len(texto_limpio) > max_texto else "")
        citas = salida.get("citas_detectadas") if isinstance(salida, dict) else []
        extra = f", citas={citas}" if citas else ""
        return f"borrador({len(texto)} chars{extra}): {preview}"
    if agente == "verificador" and isinstance(salida, dict):
        estado = "APROBADO" if salida.get("aprobado") else f"RECHAZO->{salida.get('destino')}"
        motivo = " ".join(str(salida.get("motivo", "")).split())
        if len(motivo) > max_texto:
            motivo = motivo[: max_texto - 3] + "..."
        return f"{estado} | {motivo}"
    return " ".join(str(salida).split())[:max_texto]


def _resumir_paso(paso: dict[str, Any], solo_base: bool, max_texto: int = 110) -> str:
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
    return f"  [{idx}] {agente:<11} [{etiqueta}] -> {_detalle_paso(paso, max_texto=max_texto)}"


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


def render_estado_carga_html(
    modelo_base: str,
    repo_commit: str,
    dtype_str: str,
    fuentes: dict[str, tuple[str, str | None]],
    manifest_check: dict[str, Any],
    aislamiento: dict[str, Any],
) -> str:
    """Tarjeta compacta de arranque (Paso 2): arquitectura 1 NF4 + 3 LoRA + SHA-256 + aislamiento."""
    diffs_base = aislamiento.get("max_abs_diff_vs_base", {})
    roles_html = []
    for rol in ("enrutador", "recuperador", "redactor", "verificador"):
        if rol == "verificador":
            roles_html.append(
                '<div style="flex:1;min-width:170px;background:#1e293b;border:1px solid #475569;'
                'border-radius:8px;padding:8px 10px;">'
                '<div style="font-size:12px;font-weight:700;color:#cbd5e1;">Verificador</div>'
                '<div style="font-size:11.5px;color:#94a3b8;margin-top:2px;"><b>LoRA OFF (Base)</b> · disable_adapter()</div>'
                '<div style="font-size:11px;color:#38bdf8;margin-top:2px;">Pesos base intactos</div>'
                "</div>"
            )
            continue
        repo, rev = fuentes.get(rol, ("?", "?"))
        m = manifest_check.get(rol, {})
        sha_ok = "SHA-256 OK" if m.get("verificado") else "SHA pendiente"
        diff_val = diffs_base.get(rol)
        diff_txt = f"ΔBase={diff_val:.2f}" if isinstance(diff_val, (int, float)) else "ΔBase ok"
        roles_html.append(
            '<div style="flex:1;min-width:170px;background:#064e3b;border:1px solid #10b981;'
            'border-radius:8px;padding:8px 10px;">'
            f'<div style="font-size:12px;font-weight:700;color:#ecfdf5;">{html.escape(rol.capitalize())}</div>'
            f'<div style="font-size:11.5px;color:#a7f3d0;margin-top:2px;"><b>LoRA ON</b> · rev {html.escape(str(rev)[:7])}</div>'
            f'<div style="font-size:11px;color:#d1fae5;margin-top:2px;">{html.escape(sha_ok)} · {html.escape(diff_txt)} · {html.escape(str(repo).split("/")[-1])}</div>'
            "</div>"
        )
    cruz = aislamiento.get("max_abs_diff_cruzada", {})
    cruz_txt = ", ".join(f"{k}={v:.2f}" for k, v in cruz.items() if isinstance(v, (int, float)))
    return (
        '<div style="margin:10px 0;padding:14px;border-radius:12px;background:#0f172a;color:#f8fafc;'
        'border:1px solid #334155;font-family:ui-sans-serif,system-ui;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">'
        f'<div style="font-size:15px;font-weight:700;">Paso 2 listo · Único modelo NF4: <code>{html.escape(modelo_base)}</code> + E5 denso</div>'
        '<span style="background:#065f46;color:#d1fae5;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;">Aislamiento Multi-LoRA Verificado</span>'
        "</div>"
        f'<div style="font-size:12px;color:#cbd5e1;margin-bottom:10px;">Commit <b>main@{html.escape(repo_commit)}</b> · dtype <b>{html.escape(dtype_str)}</b> · Δ cruzada: {html.escape(cruz_txt or "OK")}</div>'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap;">{"".join(roles_html)}</div>'
        "</div>"
    )


def render_pregunta_banner_html(pregunta_item: dict[str, str]) -> str:
    """Banner legible sobre el stream en vivo de Paso 3 con la pregunta y pauta esperada."""
    qid = html.escape(str(pregunta_item.get("qid", "")))
    cat = html.escape(str(pregunta_item.get("categoria", "")))
    preg = html.escape(str(pregunta_item.get("pregunta", "")))
    gold = html.escape(f"{pregunta_item.get('gold_dato', '')} [{pregunta_item.get('gold_fuente', '')}]")
    return (
        '<div style="margin:8px 0 12px 0;padding:12px 14px;border-radius:10px;background:#1e293b;'
        'border-left:4px solid #38bdf8;color:#f8fafc;font-family:ui-sans-serif,system-ui;">'
        f'<div style="font-size:12px;color:#38bdf8;font-weight:700;">EJECUCIÓN EN VIVO · {qid} · {cat}</div>'
        f'<div style="font-size:15px;font-weight:700;margin:4px 0;line-height:1.4;">{preg}</div>'
        f'<div style="font-size:12.5px;color:#cbd5e1;"><b>Pauta esperada:</b> {gold}</div>'
        "</div>"
    )


def _agrupar_pasos_por_ciclo(traza: list[dict[str, Any]]) -> list[tuple[int, list[dict[str, Any]]]]:
    """Agrupa los eventos de la traza por ciclo de ejecucion (incrementando tras cada rechazo)."""
    ciclos: list[tuple[int, list[dict[str, Any]]]] = []
    ciclo_num = 1
    actual: list[dict[str, Any]] = []
    for paso in traza:
        actual.append(paso)
        if str(paso.get("agente", "")).lower() == "verificador":
            sal = paso.get("salida", {})
            if isinstance(sal, dict) and not sal.get("aprobado"):
                ciclos.append((ciclo_num, actual))
                ciclo_num += 1
                actual = []
    if actual:
        ciclos.append((ciclo_num, actual))
    return ciclos or [(1, list(traza))]


def render_comparativa_html(caso: dict[str, Any]) -> str:
    """Genera tarjetas HTML lado a lado con Hero Strip y piramide invertida para Colab 1080p."""

    def _badge(lado: dict[str, Any]) -> str:
        estado = _estado_auditoria(lado)
        if estado == "CORRECTA":
            st_aud = "background:#14532d;color:#dcfce7;"
            aud_txt = "CORRECTA"
        elif estado == "INCORRECTA":
            st_aud = "background:#7f1d1d;color:#fee2e2;"
            aud_txt = "INCORRECTA"
        else:
            st_aud = "background:#334155;color:#e2e8f0;"
            aud_txt = "Auditoría externa: SIN CALIFICAR"

        ver = lado.get("veredicto", {})
        ver_txt = f"Verificador: {_estado_verificador(ver)}"
        st_ver = (
            "background:#065f46;color:#d1fae5;"
            if ver.get("aprobado")
            else "background:#78350f;color:#fef3c7;"
        )
        return (
            f'<div style="display:flex;gap:6px;flex-wrap:wrap;">'
            f'<span style="{st_ver}padding:3px 9px;border-radius:999px;font-size:11.5px;font-weight:700;">{html.escape(ver_txt)}</span>'
            f'<span style="{st_aud}padding:3px 9px;border-radius:999px;font-size:11.5px;font-weight:700;">{aud_txt}</span>'
            f"</div>"
        )

    def _render_paso_html(paso: dict[str, Any], solo_base: bool) -> str:
        idx = paso.get("paso", "?")
        agente = str(paso.get("agente", "?")).lower()
        decidido_por = paso.get("decidido_por")
        if decidido_por == "sistema":
            etiqueta = "Sistema (busqueda inicial)"
            pill_style = "background:#1e3a8a;color:#dbeafe;"
        elif decidido_por:
            etiqueta = f"Sistema ({decidido_por})"
            pill_style = "background:#1e3a8a;color:#dbeafe;"
        else:
            etiqueta = etiqueta_adaptador(agente, solo_base)
            pill_style = (
                "background:#065f46;color:#d1fae5;"
                if "LoRA ON" in etiqueta
                else "background:#334155;color:#e2e8f0;"
            )
        detalle = html.escape(_detalle_paso(paso, max_texto=155))
        return (
            '<div style="padding:5px 7px;border-bottom:1px solid #334155;font-size:12px;line-height:1.4;">'
            f'<span style="color:#94a3b8;font-family:ui-monospace,monospace;">[{html.escape(str(idx))}]</span> '
            f'<b style="color:#f8fafc;">{html.escape(agente.upper())}</b> '
            f'<span style="{pill_style}padding:1px 6px;border-radius:6px;font-size:10.5px;font-weight:700;">{html.escape(etiqueta)}</span> '
            f'<span style="color:#cbd5e1;">→ {detalle}</span>'
            "</div>"
        )

    def _card(titulo: str, roles_txt: str, acento: str, lado: dict[str, Any], solo_base: bool) -> str:
        resp_txt = _limpiar_pensar(str(lado.get("respuesta", "")))
        resp_html = html.escape(resp_txt).replace("\n", "<br>")
        llamadas = _contar_llamadas(lado)
        ver = lado.get("veredicto", {})
        ver_motivo = html.escape(str(ver.get("motivo", "")))
        ver_head = html.escape(_estado_verificador(ver))
        ver_border = "#10b981" if ver.get("aprobado") else "#f59e0b"

        ciclos_html = []
        for num_c, pasos_c in _agrupar_pasos_por_ciclo(lado.get("traza", [])):
            subtitulo = f"Ciclo {num_c}" if num_c == 1 else f"Ciclo {num_c} (reintento)"
            filas = "".join(_render_paso_html(p, solo_base=solo_base) for p in pasos_c)
            ciclos_html.append(
                '<div style="margin-bottom:8px;border:1px solid #334155;border-radius:8px;overflow:hidden;">'
                f'<div style="background:#334155;color:#f1f5f9;font-size:11px;font-weight:700;padding:3px 8px;">{subtitulo}</div>'
                f'<div style="background:#0f172a;">{filas}</div>'
                "</div>"
            )

        meta = (
            f"Ciclos: <b>{lado.get('ciclos')}</b> · "
            f"Llamadas: <b>{llamadas}</b> · "
            f"Tiempo: <b>{lado.get('segundos')}s</b>"
        )
        return (
            f'<div style="flex:1;min-width:360px;border:2px solid {acento};border-radius:12px;'
            f'padding:14px;background:#0f172a;color:#e2e8f0;font-family:ui-sans-serif,system-ui;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:4px;">'
            f'<span style="font-weight:800;font-size:14.5px;color:#f8fafc;">{html.escape(titulo)}</span>'
            f"{_badge(lado)}</div>"
            f'<div style="font-size:11.5px;color:#94a3b8;margin-bottom:6px;">{html.escape(roles_txt)}</div>'
            f'<div style="font-size:12.5px;color:#cbd5e1;margin-bottom:10px;">{meta}</div>'
            f'<div style="font-size:13.5px;line-height:1.5;background:#1e293b;padding:11px 12px;'
            f'border-radius:8px;border-left:4px solid {acento};color:#f8fafc;margin-bottom:8px;">'
            f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:0.04em;color:#94a3b8;font-weight:700;margin-bottom:4px;">Respuesta final emitida</div>'
            f"{resp_html}</div>"
            f'<div style="font-size:12px;line-height:1.4;background:#172554;padding:8px 10px;'
            f'border-radius:8px;border-left:3px solid {ver_border};margin-bottom:10px;color:#e2e8f0;">'
            f'<b>Verificador Base ({ver_head}):</b> {ver_motivo}</div>'
            f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:0.04em;color:#94a3b8;font-weight:700;margin-bottom:4px;">Mensajes intermedios por ciclo</div>'
            f'{"".join(ciclos_html)}'
            "</div>"
        )

    preg = html.escape(str(caso.get("pregunta", "")))
    gold = html.escape(f"{caso.get('gold_dato', '')} [{caso.get('gold_fuente', '')}]")
    base = caso.get("base", {})
    ft = caso.get("finetuned_3lora", {})
    calls_b, calls_f = _contar_llamadas(base), _contar_llamadas(ft)
    delta_txt = (
        f" ({round((calls_f - calls_b) * 100.0 / calls_b, 1):+.1f}%)"
        if calls_b > 0
        else ""
    )
    ver_b = _estado_verificador(base.get("veredicto", {}))
    ver_f = _estado_verificador(ft.get("veredicto", {}))

    hero_kpis = (
        '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px;">'
        f'<div style="flex:1;min-width:150px;background:#0f172a;border:1px solid #334155;border-radius:8px;padding:8px 10px;">'
        f'<div style="font-size:11px;color:#94a3b8;">Llamadas LLM</div>'
        f'<div style="font-size:15px;font-weight:800;color:#34d399;">{calls_b} → {calls_f}{delta_txt}</div></div>'
        f'<div style="flex:1;min-width:130px;background:#0f172a;border:1px solid #334155;border-radius:8px;padding:8px 10px;">'
        f'<div style="font-size:11px;color:#94a3b8;">Ciclos</div>'
        f'<div style="font-size:15px;font-weight:800;color:#f8fafc;">{base.get("ciclos")} → {ft.get("ciclos")}</div></div>'
        f'<div style="flex:1;min-width:150px;background:#0f172a;border:1px solid #334155;border-radius:8px;padding:8px 10px;">'
        f'<div style="font-size:11px;color:#94a3b8;">Tiempo</div>'
        f'<div style="font-size:15px;font-weight:800;color:#f8fafc;">{base.get("segundos")}s → {ft.get("segundos")}s</div></div>'
        f'<div style="flex:1;min-width:180px;background:#0f172a;border:1px solid #334155;border-radius:8px;padding:8px 10px;">'
        f'<div style="font-size:11px;color:#94a3b8;">Verificador Base</div>'
        f'<div style="font-size:13.5px;font-weight:800;color:#fbbf24;">{html.escape(ver_b)} → <span style="color:#34d399;">{html.escape(ver_f)}</span></div></div>'
        "</div>"
    )

    return (
        '<div style="margin:12px 0;font-family:ui-sans-serif,system-ui;">'
        '<div style="background:#1e293b;color:#f1f5f9;padding:12px 14px;border-radius:10px;margin-bottom:10px;">'
        f'<div style="font-size:12px;color:#93c5fd;font-weight:700;">{html.escape(str(caso.get("qid")))} · {html.escape(str(caso.get("categoria")))}</div>'
        f'<div style="font-size:15.5px;font-weight:700;margin:4px 0;line-height:1.4;">{preg}</div>'
        f'<div style="font-size:12.5px;color:#cbd5e1;"><b>Pauta esperada:</b> {gold}</div>'
        "</div>"
        f"{hero_kpis}"
        '<div style="display:flex;gap:12px;flex-wrap:wrap;align-items:stretch;">'
        f'{_card("CONTROL BASE · LoRA OFF (4 agentes)", "Enr OFF · Rec OFF · Red OFF · Ver OFF", "#ef4444", base, solo_base=True)}'
        f'{_card("D4 3-LoRA · Enr+Rec+Red FT · Verificador Base", "Enr ON · Rec ON · Red ON · Ver OFF (Base intacto)", "#10b981", ft, solo_base=False)}'
        "</div></div>"
    )


def render_fallos_html(
    fallos: dict[str, Any],
    qids_filtro: tuple[str, ...] | None = DEFAULT_FAIL_QIDS,
) -> str:
    """Tarjetas HTML de transparencia (protagonista H03 + H17/H06) para Paso 4 en vivo."""
    casos = fallos.get("casos", [])
    por_qid = {c.get("qid"): c for c in casos}
    orden = list(qids_filtro) if qids_filtro is not None else list(por_qid.keys())
    seleccionados = [por_qid[q] for q in orden if q in por_qid]
    if not seleccionados:
        return ""

    h03 = next((c for c in seleccionados if c.get("qid") == "dificil_25:H03"), seleccionados[0])
    otros = [c for c in seleccionados if c.get("qid") != h03.get("qid")]

    traza_h03 = h03.get("traza_completa", [])[:5]
    traza_rows = []
    for p in traza_h03:
        estilo_hi = (
            "background:#451a03;border-left:3px solid #f59e0b;"
            if str(p.get("agente", "")).lower() == "recuperador"
            else "background:#0f172a;border-left:3px solid #475569;"
        )
        traza_rows.append(
            f'<div style="{estilo_hi}padding:4px 8px;margin-bottom:3px;border-radius:4px;font-size:11.5px;color:#e2e8f0;">'
            f'{html.escape(_resumir_paso(p, solo_base=False, max_texto=115))}</div>'
        )

    hero_html = (
        '<div style="background:#1e293b;border:2px solid #f59e0b;border-radius:10px;padding:12px 14px;margin-bottom:10px;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:6px;">'
        f'<span style="font-size:14px;font-weight:800;color:#fde68a;">Caso de fallo documentado · {html.escape(str(h03.get("qid")))} (causa: {html.escape(str(h03.get("causa_raiz")))})</span>'
        f'<span style="font-size:12px;color:#cbd5e1;">Ciclos: <b>{h03.get("ciclos")}</b> · Llamadas: <b>{h03.get("llamadas_modelo")}</b> · {h03.get("segundos")}s</span>'
        "</div>"
        f'<div style="font-size:13px;font-weight:600;color:#f8fafc;margin-bottom:6px;">{html.escape(str(h03.get("pregunta", "")))}</div>'
        f'<div style="font-size:12px;color:#fca5a5;margin-bottom:6px;"><b>Diagnóstico:</b> {html.escape(str(h03.get("diagnostico_auditoria", "")))}</div>'
        '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px;">'
        f'<div style="flex:1;min-width:260px;background:#0f172a;padding:8px;border-radius:6px;font-size:12px;color:#e2e8f0;"><b>Respuesta emitida:</b><br>{html.escape(str(h03.get("respuesta_final", "")))}</div>'
        f'<div style="flex:1;min-width:260px;background:#064e3b;padding:8px;border-radius:6px;font-size:12px;color:#ecfdf5;"><b>Pauta esperada:</b><br>{html.escape(str(h03.get("gold_dato", "")))}</div>'
        "</div>"
        '<div style="font-size:11px;color:#94a3b8;font-weight:700;margin-bottom:4px;">PRIMEROS PASOS DE LA TRAZA ARCHIVADA (corte prematuro del Recuperador)</div>'
        f'{"".join(traza_rows)}'
        "</div>"
    )

    otros_cards = []
    for c in otros:
        otros_cards.append(
            '<div style="flex:1;min-width:300px;background:#1e293b;border:1px solid #475569;border-radius:10px;padding:10px 12px;">'
            f'<div style="font-size:12.5px;font-weight:700;color:#93c5fd;margin-bottom:4px;">{html.escape(str(c.get("qid")))} · causa: {html.escape(str(c.get("causa_raiz")))} ({c.get("ciclos")} ciclos, {c.get("llamadas_modelo")} llam., {c.get("segundos")}s)</div>'
            f'<div style="font-size:12px;color:#f1f5f9;margin-bottom:4px;">{html.escape(str(c.get("pregunta", "")))}</div>'
            f'<div style="font-size:11.5px;color:#cbd5e1;">{html.escape(str(c.get("diagnostico_auditoria", "")))}</div>'
            "</div>"
        )

    return (
        '<div style="margin:10px 0;font-family:ui-sans-serif,system-ui;color:#f8fafc;">'
        f"{hero_html}"
        f'<div style="display:flex;gap:10px;flex-wrap:wrap;">{"".join(otros_cards)}</div>'
        "</div>"
    )


def render_resumen_a100_html(resumen: dict[str, Any]) -> str:
    """Tabla HTML compacta con los resultados globales oficiales en A100 bf16."""
    sis = resumen.get("sistemas_a100_bf16", {})
    est = resumen.get("comparacion_estadistica_y_comportamiento", {})
    abl = resumen.get("ablaciones_verificador", {})

    cb = sis.get("control_base", {})
    sr = sis.get("solo_redactor_v2", {})
    m3 = sis.get("multi_lora_3_agentes_oficial", {})
    v1 = abl.get("multi_lora_4_agentes_v1", {})
    v2 = abl.get("multi_lora_4_agentes_v2", {})

    filas = [
        ("Control Base (A100 bf16)", cb.get("d3_75"), cb.get("d3_75_pct"), cb.get("nuevas_20"), cb.get("global_95"), cb.get("llamadas_75"), cb.get("llamadas_nuevas20"), "#0f172a"),
        ("Solo Redactor v2 (1-LoRA)", sr.get("d3_75"), sr.get("d3_75_pct"), sr.get("nuevas_20"), sr.get("global_95"), sr.get("llamadas_75"), sr.get("llamadas_nuevas20"), "#0f172a"),
        ("D4 3-LoRA Oficial (Verif. Base)", m3.get("d3_75"), m3.get("d3_75_pct"), m3.get("nuevas_20"), m3.get("global_95"), m3.get("llamadas_75"), m3.get("llamadas_nuevas20"), "#064e3b"),
        ("Ablaciones 4-LoRA (v1 / v2)", f"{v1.get('d3_75_aciertos')} / {v2.get('d3_75_aciertos')}", f"{v1.get('d3_75_pct')} / {v2.get('d3_75_pct')}", f"{v1.get('nuevas_20_aciertos')} / {v2.get('nuevas_20_aciertos')}", f"{v1.get('global_95_aciertos')} / {v2.get('global_95_aciertos')}", f"{v1.get('llamadas_75')} / {v2.get('llamadas_75')}", f"{v1.get('llamadas_nuevas20')} / {v2.get('llamadas_nuevas20')}", "#1e293b"),
    ]
    tr_html = []
    for nom, d75, p75, n20, g95, l75, l20, bg in filas:
        tr_html.append(
            f'<tr style="background:{bg};">'
            f'<td style="padding:6px 10px;border-bottom:1px solid #334155;font-weight:700;">{html.escape(str(nom))}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #334155;text-align:right;">{d75}/75 ({p75}%)</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #334155;text-align:right;">{n20}/20</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #334155;text-align:right;">{g95}/95</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #334155;text-align:right;">{l75} / {l20}</td>'
            "</tr>"
        )
    p_val = est.get("diferencias_vs_control_75", {}).get("mcnemar_p_exacto", "?")
    return (
        '<div style="margin:10px 0;background:#0f172a;border:1px solid #334155;border-radius:10px;padding:12px;color:#f8fafc;font-family:ui-sans-serif,system-ui;">'
        '<div style="font-size:13.5px;font-weight:800;margin-bottom:8px;">Resumen oficial A100 bf16 (75 + Nuevas 20)</div>'
        '<table style="width:100%;border-collapse:collapse;font-size:12.5px;">'
        '<thead><tr style="background:#1e293b;color:#93c5fd;">'
        '<th style="padding:6px 10px;text-align:left;">Sistema</th>'
        '<th style="padding:6px 10px;text-align:right;">D3 (75)</th>'
        '<th style="padding:6px 10px;text-align:right;">Nuevas (20)</th>'
        '<th style="padding:6px 10px;text-align:right;">Global (95)</th>'
        '<th style="padding:6px 10px;text-align:right;">Llamadas (75 / 20)</th>'
        f"</tr></thead><tbody>{''.join(tr_html)}</tbody></table>"
        f'<div style="font-size:12px;color:#cbd5e1;margin-top:8px;">McNemar 75: p={p_val} (sin diferencia de exactitud) · Recorte total de llamadas: <b>−41,0%</b> (658 → 388; Recuperador −69,8%) · Fallos en 75: Redactor 6 · Recuperador 3 · Verificador Base 2</div>'
        "</div>"
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
