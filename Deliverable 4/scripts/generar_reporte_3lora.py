"""Genera gráficos consolidados, comparativas Base vs 3-LoRA y trazas de fallo para D4.

Produce de forma determinista y sin inventar cifras:
1. `Deliverable 4/entrenamiento/loss_curves_3agentes.{pdf,png}` con las curvas reales
   de `Enrutador`, `Recuperador` y `Redactor`.
2. `Deliverable 4/evaluacion/comparativa_base_vs_3lora.json` emparejando las corridas
   en A100 bf16 (`Control Base` vs `D4 3-LoRA`) sobre casos diagnósticos y victorias clave.
3. `Deliverable 4/evaluacion/casos_fallo_y_regresion_3lora.json` con trazas completas,
   telemetría y causa raíz de los 11 fallos estrictos de `3-LoRA` en las 75 preguntas.
4. `Deliverable 4/evaluacion/resumen_comparativo_d4.json` consolidando 75 D3, 20 nuevas
   y total 95 (incluyendo referencia `Solo Redactor` y ablaciones del Verificador).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

D4_DIR = Path(__file__).resolve().parents[1]
D4_TRAIN_DIR = D4_DIR / "entrenamiento"
D4_EVAL_DIR = D4_DIR / "evaluacion"


def _escribir_json_lf(path: Path, payload: Any) -> None:
    """Escribe un archivo JSON con saltos LF garantizados en cualquier OS."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _mcnemar_exacto(gana: int, pierde: int) -> float:
    """Calcula valor-p exacto bilateral (prueba binomial sobre pares discordantes)."""
    n = gana + pierde
    if n == 0:
        return 1.0
    k = min(gana, pierde)
    p = 2.0 * sum(math.comb(n, i) * (0.5**n) for i in range(k + 1))
    return round(min(1.0, p), 4)

COMPARATIVA_BASE_VS_3LORA_QIDS: tuple[str, ...] = (
    "dificil_25:H07",
    "dificil_25:H14",
    "congelado_50:11",
    "congelado_50:43",
    "dificil_25:H18",
    "dificil_25:H24",
    "dificil_25:H03",
)

# Resumen verificado de las ablaciones del Verificador en ramas exp/multi-lora-*
ABLACIONES_VERIFICADOR: dict[str, Any] = {
    "nota": (
        "Corridas experimentales sobre idéntico A100 bf16 que justifican mantener "
        "Verificador en Qwen/Qwen3-4B Base (ramas exp/multi-lora-todos y "
        "exp/multi-lora-verificador-v2)."
    ),
    "ablacion_red_ver_nuevas20": {
        "agentes_finetuned": ["redactor", "verificador"],
        "nuevas_20_aciertos": 9,
        "nuevas_20_total": 20,
        "nuevas_20_pct": 45.0,
        "llamadas_nuevas20": 190,
        "segundos_nuevas20": 1691.21,
    },
    "multi_lora_4_agentes_v1": {
        "agentes_finetuned": ["enrutador", "recuperador", "redactor", "verificador"],
        "d3_75_aciertos": 58,
        "d3_75_congelado_50": 40,
        "d3_75_dificil_25": 18,
        "d3_75_pct": 77.3,
        "llamadas_75": 493,
        "segundos_75": 6350.0,
        "nuevas_20_aciertos": 14,
        "nuevas_20_pct": 70.0,
        "llamadas_nuevas20": 138,
        "global_95_aciertos": 72,
        "global_95_pct": 75.8,
        "hallazgo": "Colapsó en abstenciones de D3 por sesgo del dataset Verificador v1 hacia rechazo de 'No aplica' (P10, P16, P28, P46, P47, P48).",
    },
    "multi_lora_4_agentes_v2": {
        "agentes_finetuned": ["enrutador", "recuperador", "redactor", "verificador_v2"],
        "d3_75_aciertos": 56,
        "d3_75_congelado_50": 40,
        "d3_75_dificil_25": 16,
        "d3_75_pct": 74.7,
        "llamadas_75": 486,
        "segundos_75": 6491.74,
        "nuevas_20_aciertos": 12,
        "nuevas_20_pct": 60.0,
        "llamadas_nuevas20": 147,
        "segundos_nuevas20": 2492.21,
        "global_95_aciertos": 68,
        "global_95_pct": 71.6,
        "hallazgo": "Corrigió el sesgo 'No aplica', pero mantuvo sobre-rechazo en síntesis/condiciones dejando peor resultado global que 3-LoRA (Verificador base).",
    },
}


def _cargar_csv_por_qid(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return {f"{r['set']}:{r['id']}": r for r in csv.DictReader(f)}


def _construir_bloque_sistema(
    row: dict[str, str],
    traza: list[dict[str, Any]],
) -> dict[str, Any]:
    aprob_raw = str(row.get("aprobado_verificador", "")).strip().lower()
    aprob = aprob_raw in {"true", "1", "si", "sí"}
    return {
        "respuesta": row.get("respuesta_sistema", ""),
        "correcto": int(row["correcto"]) if row.get("correcto") in {"0", "1"} else None,
        "veredicto": {
            "aprobado": aprob,
            "destino": "fin" if aprob else "redactor",
            "motivo": row.get("motivo_verificador", ""),
        },
        "ciclos": int(float(row.get("ciclos") or 0)),
        "llamadas_modelo": int(float(row.get("llamadas_modelo") or 0)),
        "tipo_enrutador": row.get("tipo_enrutador", ""),
        "segundos": round(float(row.get("segundos") or 0.0), 2),
        "fuentes_traidas": row.get("fuentes_traidas", ""),
        "traza": traza,
    }


def generar_curva_3_agentes(
    train_dir: Path = D4_TRAIN_DIR,
) -> dict[str, str]:
    """Dibuja 3 mini-paneles lado a lado con `train_loss` y `eval_loss` reales."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    specs = [
        ("Enrutador", train_dir / "enrutador" / "training_metrics.json", "#1d4ed8"),
        ("Recuperador", train_dir / "recuperador" / "training_metrics.json", "#0f766e"),
        ("Redactor", train_dir / "training_metrics.json", "#b45309"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(11.5, 1.98), dpi=300)
    for ax, (titulo, mpath, color) in zip(axes, specs):
        m = json.loads(mpath.read_text(encoding="utf-8"))
        curvas = m["curvas"]
        train_pts = curvas.get("train", [])
        eval_pts = curvas.get("eval", [])
        res = m["resultados"]
        mejor_step = res.get("mejor_step")

        if train_pts:
            ax.plot(
                [p["step"] for p in train_pts],
                [p["loss"] for p in train_pts],
                color=color,
                alpha=0.55,
                linewidth=1.45,
                label="Train",
            )
        if eval_pts:
            ax.plot(
                [p["step"] for p in eval_pts],
                [p["eval_loss"] for p in eval_pts],
                color="#14334b",
                marker="o",
                markersize=3.6,
                linewidth=1.95,
                label="Val",
            )
        if mejor_step is not None:
            ax.axvline(mejor_step, color="#059669", linestyle="--", linewidth=1.1, alpha=0.85)

        ax.set_title(
            f"{titulo} — val: {res['eval_loss_inicial']:.3f} → {res['mejor_eval_loss']:.3f} (step {mejor_step})",
            fontsize=9.2,
            fontweight="bold",
            color="#14334b",
        )
        ax.set_xlabel("Paso", fontsize=8.5)
        ax.tick_params(labelsize=8.0)
        ax.grid(True, linestyle=":", alpha=0.35)
        ax.legend(fontsize=8.0, loc="upper right", frameon=True)

    axes[0].set_ylabel("Loss (completion-only)", fontsize=8.5)
    fig.tight_layout(pad=0.6)

    out_pdf = train_dir / "loss_curves_3agentes.pdf"
    out_png = train_dir / "loss_curves_3agentes.png"
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)
    return {"pdf": str(out_pdf), "png": str(out_png)}


def generar_comparativa_base_vs_3lora(
    eval_dir: Path = D4_EVAL_DIR,
    qids: tuple[str, ...] = COMPARATIVA_BASE_VS_3LORA_QIDS,
) -> list[dict[str, Any]]:
    """Construye `comparativa_base_vs_3lora.json` con trazas reales en A100 bf16."""
    cb_rows = _cargar_csv_por_qid(eval_dir / "resultados_control_base_D4_auditados.csv")
    ml_rows = _cargar_csv_por_qid(eval_dir / "resultados_3lora_75_auditados.csv")
    cb_trazas = json.loads((eval_dir / "trazas_control_base_D4.json").read_text(encoding="utf-8"))
    ml_trazas = json.loads((eval_dir / "trazas_3lora_75.json").read_text(encoding="utf-8"))

    salida: list[dict[str, Any]] = []
    for qid in qids:
        rb = cb_rows[qid]
        rm = ml_rows[qid]
        salida.append(
            {
                "qid": qid,
                "set": rm["set"],
                "id": rm["id"],
                "categoria": rm["categoria"],
                "pregunta": rm["pregunta"],
                "gold_dato": rm["gold_dato"],
                "gold_fuente": rm["gold_fuente"],
                "base": _construir_bloque_sistema(rb, cb_trazas[qid]),
                "finetuned_3lora": _construir_bloque_sistema(rm, ml_trazas[qid]),
            }
        )

    out_path = eval_dir / "comparativa_base_vs_3lora.json"
    _escribir_json_lf(out_path, salida)
    return salida


def generar_casos_fallo_3lora(eval_dir: Path = D4_EVAL_DIR) -> dict[str, Any]:
    """Empaqueta los 11 fallos estrictos de `3-LoRA` en las 75 preguntas."""
    aud = json.loads((eval_dir / "auditoria_3lora_75.json").read_text(encoding="utf-8"))
    ml_rows = _cargar_csv_por_qid(eval_dir / "resultados_3lora_75_auditados.csv")
    ml_trazas = json.loads((eval_dir / "trazas_3lora_75.json").read_text(encoding="utf-8"))
    ml_tel = json.loads((eval_dir / "telemetria_3lora_75.json").read_text(encoding="utf-8"))

    casos: list[dict[str, Any]] = []
    for v in aud["veredictos"]:
        if int(v.get("correcto_estricto", 1)) != 0:
            continue
        qid = v["qid"]
        row = ml_rows[qid]
        aprob = str(row.get("aprobado_verificador", "")).strip().lower() in {"true", "1"}
        casos.append(
            {
                "qid": qid,
                "set": v["set"],
                "id": v["id"],
                "categoria": v["categoria"],
                "pregunta": v["pregunta"],
                "gold_dato": row.get("gold_dato", ""),
                "gold_fuente": row.get("gold_fuente", ""),
                "respuesta_final": row.get("respuesta_sistema", ""),
                "aprobado_verificador": aprob,
                "motivo_verificador": row.get("motivo_verificador", ""),
                "ciclos": v["ciclos"],
                "llamadas_modelo": v["llamadas_modelo"],
                "segundos": v["segundos"],
                "fuentes_traidas": [
                    s.strip() for s in (row.get("fuentes_traidas") or "").split(";") if s.strip()
                ],
                "tipo_fallo": v.get("tipo_fallo"),
                "causa_raiz": v.get("causa_raiz"),
                "solo_condicion_p01": bool(v.get("solo_condicion_p01")),
                "diagnostico_auditoria": v.get("motivo_auditoria"),
                "telemetria": ml_tel.get(qid, []),
                "traza_completa": ml_trazas.get(qid, []),
            }
        )

    paquete = {
        "descripcion": (
            "Trazas completas de los 11 fallos estrictos de Deliverable 4 (sistema oficial "
            "3-LoRA: Enrutador + Recuperador + Redactor QLoRA, Verificador Base) en A100 bf16 "
            "(64/75, 85,3%), destacando cortes prematuros del Recuperador (H03, P36, P25), "
            "bucles del Verificador Base (H17, H19) y desvíos residuales del Redactor (H06, H12, H22, H25)."
        ),
        "total_casos_documentados": len(casos),
        "casos": casos,
    }
    out_path = eval_dir / "casos_fallo_y_regresion_3lora.json"
    _escribir_json_lf(out_path, paquete)
    return paquete


def _resumir_estadistica_y_comportamiento(eval_dir: Path) -> dict[str, Any]:
    """Recalcula McNemar pareado, balance por set y trazas de Enrutador/Recuperador."""
    cb_75 = _cargar_csv_por_qid(eval_dir / "resultados_control_base_D4_auditados.csv")
    ml_75 = _cargar_csv_por_qid(eval_dir / "resultados_3lora_75_auditados.csv")
    cb_n20 = _cargar_csv_por_qid(eval_dir / "resultados_nuevas20_base_D4_auditados.csv")
    ml_n20 = _cargar_csv_por_qid(eval_dir / "resultados_3lora_nuevas20_auditados.csv")

    gana_75 = sorted(q for q in ml_75 if int(ml_75[q]["correcto"]) == 1 and int(cb_75[q]["correcto"]) == 0)
    pierde_75 = sorted(q for q in ml_75 if int(ml_75[q]["correcto"]) == 0 and int(cb_75[q]["correcto"]) == 1)
    gana_n20 = sorted(q for q in ml_n20 if int(ml_n20[q]["correcto"]) == 1 and int(cb_n20[q]["correcto"]) == 0)
    pierde_n20 = sorted(q for q in ml_n20 if int(ml_n20[q]["correcto"]) == 0 and int(cb_n20[q]["correcto"]) == 1)

    tr_75 = json.loads((eval_dir / "trazas_3lora_75.json").read_text(encoding="utf-8"))
    tr_cb_75 = json.loads((eval_dir / "trazas_control_base_D4.json").read_text(encoding="utf-8"))

    enr_solo_rg_75 = sum(
        1
        for t in tr_75.values()
        if t and t[0].get("agente") == "enrutador" and t[0].get("salida", {}).get("documentos") == ["RG"]
    )
    rec_suf_p1_75 = sum(
        1
        for t in tr_75.values()
        if len(t) > 2
        and t[2].get("agente") == "recuperador"
        and t[2].get("salida", {}).get("accion") == "suficiente"
    )
    rec_buscar_3l = sum(
        1
        for t in tr_75.values()
        for p in t
        if p.get("agente") == "recuperador"
        and p.get("decidido_por") != "sistema"
        and p.get("salida", {}).get("accion") == "buscar"
    )
    rec_buscar_cb = sum(
        1
        for t in tr_cb_75.values()
        for p in t
        if p.get("agente") == "recuperador"
        and p.get("decidido_por") != "sistema"
        and p.get("salida", {}).get("accion") == "buscar"
    )

    return {
        "diferencias_vs_control_75": {
            "gana_3lora": gana_75,
            "pierde_3lora": pierde_75,
            "balance_neto": len(gana_75) - len(pierde_75),
            "mcnemar_p_exacto": _mcnemar_exacto(len(gana_75), len(pierde_75)),
        },
        "diferencias_vs_control_n20": {
            "gana_3lora": gana_n20,
            "pierde_3lora": pierde_n20,
            "balance_neto": len(gana_n20) - len(pierde_n20),
        },
        "diferencias_vs_control_95": {
            "gana_3lora_count": len(gana_75) + len(gana_n20),
            "pierde_3lora_count": len(pierde_75) + len(pierde_n20),
            "balance_neto": (len(gana_75) + len(gana_n20)) - (len(pierde_75) + len(pierde_n20)),
            "mcnemar_p_exacto": _mcnemar_exacto(
                len(gana_75) + len(gana_n20), len(pierde_75) + len(pierde_n20)
            ),
        },
        "comportamiento_enrutador_y_recuperador_75": {
            "enrutador_solo_rg_75": enr_solo_rg_75,
            "recuperador_suficiente_paso1_75": rec_suf_p1_75,
            "recuperador_buscar_modelo_3lora_75": rec_buscar_3l,
            "recuperador_buscar_modelo_control_base_75": rec_buscar_cb,
        },
    }


def generar_resumen_comparativo_d4(
    eval_dir: Path = D4_EVAL_DIR,
    train_dir: Path = D4_TRAIN_DIR,
) -> dict[str, Any]:
    """Consolida métricas de Base, Solo Redactor, 3-LoRA oficial y ablaciones."""
    aud_cb_75 = json.loads((eval_dir / "auditoria_control_base_D4.json").read_text(encoding="utf-8"))
    aud_cb_n20 = json.loads((eval_dir / "auditoria_nuevas20_base_D4.json").read_text(encoding="utf-8"))
    aud_red_75 = json.loads((eval_dir / "auditoria_D4.json").read_text(encoding="utf-8"))
    aud_red_n20 = json.loads((eval_dir / "auditoria_nuevas20_ft_D4.json").read_text(encoding="utf-8"))
    aud_3l_75 = json.loads((eval_dir / "auditoria_3lora_75.json").read_text(encoding="utf-8"))
    aud_3l_n20 = json.loads((eval_dir / "auditoria_3lora_nuevas20.json").read_text(encoding="utf-8"))

    m_enr = json.loads((train_dir / "enrutador" / "training_metrics.json").read_text(encoding="utf-8"))
    m_rec = json.loads((train_dir / "recuperador" / "training_metrics.json").read_text(encoding="utf-8"))
    m_red = json.loads((train_dir / "training_metrics.json").read_text(encoding="utf-8"))

    resumen = {
        "sistema_oficial": "3-LoRA (Enrutador + Recuperador + Redactor QLoRA; Verificador Qwen3-4B Base)",
        "entrenamientos": {
            ag: {
                "modelo_base": m["modelo_base"],
                "hf_repo": m.get("hf_repo"),
                "hf_revision": m.get("hf_revision")
                or (
                    "739b031acbd5feef2c49f946b94722712209bce0"
                    if ag == "redactor"
                    else None
                ),
                "adapter_model_sha256": m.get("adapter_model_sha256")
                or (
                    "438a23664aab0457b060a42fb0eea77d6db82949459aa33280c36dcdb755b3c1"
                    if ag == "redactor"
                    else None
                ),
                "hardware": m["hardware"]["gpu"],
                "dtype": m["hardware"]["compute_dtype"],
                "train_ejemplos": m["datos"]["train_ejemplos"],
                "val_ejemplos": m["datos"]["val_ejemplos"],
                "truncados": m["datos"]["tokens_train"]["truncados"] + m["datos"]["tokens_val"]["truncados"],
                "tiempo_min": m["resultados"]["tiempo_entrenamiento_min"],
                "pasos_totales": m["resultados"]["pasos_totales"],
                "eval_loss_inicial": m["resultados"]["eval_loss_inicial"],
                "mejor_eval_loss": m["resultados"]["mejor_eval_loss"],
                "mejor_step": m["resultados"]["mejor_step"],
            }
            for ag, m in (("enrutador", m_enr), ("recuperador", m_rec), ("redactor", m_red))
        },
        "sistemas_a100_bf16": {
            "control_base": {
                "d3_congelado_50": aud_cb_75["resumen_por_set"]["congelado_50"]["aciertos"],
                "d3_dificil_25": aud_cb_75["resumen_por_set"]["dificil_25"]["aciertos"],
                "d3_75": aud_cb_75["aciertos_humanos"],
                "d3_75_pct": aud_cb_75["porcentaje_humano"],
                "llamadas_75": aud_cb_75["telemetria_y_aislamiento"]["llamadas_modelo_totales"],
                "llamadas_por_agente_75": aud_cb_75["telemetria_y_aislamiento"]["llamadas_por_agente"],
                "segundos_75": aud_cb_75["telemetria_y_aislamiento"]["segundos_totales"],
                "nuevas_20": aud_cb_n20["aciertos_humanos"],
                "nuevas_20_pct": aud_cb_n20["porcentaje_humano"],
                "llamadas_nuevas20": aud_cb_n20["telemetria_y_aislamiento"]["llamadas_modelo_totales"],
                "segundos_nuevas20": aud_cb_n20["telemetria_y_aislamiento"]["segundos_totales"],
                "global_95": aud_cb_75["aciertos_humanos"] + aud_cb_n20["aciertos_humanos"],
                "global_95_pct": round(100.0 * (aud_cb_75["aciertos_humanos"] + aud_cb_n20["aciertos_humanos"]) / 95.0, 1),
            },
            "solo_redactor_v2": {
                "d3_congelado_50": aud_red_75["resumen_global"]["congelado_50"]["aciertos_estrictos"],
                "d3_dificil_25": aud_red_75["resumen_global"]["dificil_25"]["aciertos_estrictos"],
                "d3_75": aud_red_75["resumen_global"]["global_75"]["aciertos_estrictos"],
                "d3_75_pct": aud_red_75["resumen_global"]["global_75"]["porcentaje_estricto"],
                "llamadas_75": aud_red_75["telemetria_y_aislamiento"]["llamadas_modelo_totales"],
                "llamadas_por_agente_75": aud_red_75["telemetria_y_aislamiento"]["llamadas_por_agente"],
                "segundos_75": aud_red_75["telemetria_y_aislamiento"]["segundos_totales"],
                "nuevas_20": aud_red_n20["aciertos_humanos"],
                "nuevas_20_pct": aud_red_n20["porcentaje_humano"],
                "llamadas_nuevas20": aud_red_n20["telemetria_y_aislamiento"]["llamadas_modelo_totales"],
                "segundos_nuevas20": aud_red_n20["telemetria_y_aislamiento"]["segundos_totales"],
                "global_95": aud_red_75["resumen_global"]["global_75"]["aciertos_estrictos"] + aud_red_n20["aciertos_humanos"],
                "global_95_pct": round(100.0 * (aud_red_75["resumen_global"]["global_75"]["aciertos_estrictos"] + aud_red_n20["aciertos_humanos"]) / 95.0, 1),
            },
            "multi_lora_3_agentes_oficial": {
                "d3_congelado_50": aud_3l_75["resumen_por_set"]["congelado_50"]["aciertos_estrictos"],
                "d3_dificil_25": aud_3l_75["resumen_por_set"]["dificil_25"]["aciertos_estrictos"],
                "d3_75": aud_3l_75["resumen_global"]["aciertos_estrictos"],
                "d3_75_nucleo": aud_3l_75["resumen_global"]["aciertos_nucleo_sin_condicion_p01"],
                "d3_75_pct": aud_3l_75["resumen_global"]["porcentaje_estricto"],
                "ciclos_promedio_75": aud_3l_75["resumen_global"]["ciclos_promedio"],
                "llamadas_75": aud_3l_75["telemetria"]["llamadas_modelo_totales"],
                "llamadas_por_agente_75": aud_3l_75["telemetria"]["llamadas_por_agente"],
                "segundos_75": aud_3l_75["resumen_global"]["segundos_totales"],
                "nuevas_20": aud_3l_n20["resumen_global"]["aciertos_estrictos"],
                "nuevas_20_nucleo": aud_3l_n20["resumen_global"]["aciertos_nucleo_sin_condicion_p01"],
                "nuevas_20_pct": aud_3l_n20["resumen_global"]["porcentaje_estricto"],
                "ciclos_promedio_n20": aud_3l_n20["resumen_global"]["ciclos_promedio"],
                "llamadas_nuevas20": aud_3l_n20["telemetria"]["llamadas_modelo_totales"],
                "segundos_nuevas20": aud_3l_n20["resumen_global"]["segundos_totales"],
                "global_95": aud_3l_75["resumen_global"]["aciertos_estrictos"] + aud_3l_n20["resumen_global"]["aciertos_estrictos"],
                "global_95_pct": round(100.0 * (aud_3l_75["resumen_global"]["aciertos_estrictos"] + aud_3l_n20["resumen_global"]["aciertos_estrictos"]) / 95.0, 1),
                "fallos_75_por_causa": aud_3l_75["fallos_por_causa_raiz"],
                "fallos_n20_por_causa": aud_3l_n20["fallos_por_causa_raiz"],
                "nota_especial": aud_3l_75.get("nota_especial"),
            },
        },
        "comparacion_estadistica_y_comportamiento": _resumir_estadistica_y_comportamiento(eval_dir),
        "ablaciones_verificador": ABLACIONES_VERIFICADOR,
    }
    out_path = eval_dir / "resumen_comparativo_d4.json"
    _escribir_json_lf(out_path, resumen)
    return resumen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Genera curvas, comparativas y trazas de fallo del sistema oficial 3-LoRA."
    )
    parser.add_argument("--train-dir", type=Path, default=D4_TRAIN_DIR)
    parser.add_argument("--eval-dir", type=Path, default=D4_EVAL_DIR)
    args = parser.parse_args(argv)

    curvas = generar_curva_3_agentes(args.train_dir)
    comp = generar_comparativa_base_vs_3lora(args.eval_dir)
    fallos = generar_casos_fallo_3lora(args.eval_dir)
    resumen = generar_resumen_comparativo_d4(args.eval_dir, args.train_dir)
    print(
        json.dumps(
            {
                "curvas_3_agentes": curvas,
                "comparativa_casos": len(comp),
                "fallos_3lora": fallos["total_casos_documentados"],
                "global_95_oficial": resumen["sistemas_a100_bf16"]["multi_lora_3_agentes_oficial"]["global_95"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
