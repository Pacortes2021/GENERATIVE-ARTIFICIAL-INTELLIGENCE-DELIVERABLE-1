"""Generador de trayectorias ReAct supervisadas para el Agente 2 (Recuperador).

Replica exactamente `ctx` y el esquema de acciones de `Orquestador.recuperar()`
(`Deliverable 3/Deliverable3/agentes/orquestador.py` L226-290):
- Entrada (`user`): `02_recuperador.txt` con `{{PLAN}}` JSON
- Salida (`assistant`): una sola acción JSON válida (`buscar`, `traer`, `existe`, `suficiente`)
"""

from __future__ import annotations

import json
import re
from typing import Any

from antifuga_multi import (
    BLOCKED_UNIT_IDS,
    cd,
    doc_de_unidad,
    numero_permitido_orquestador,
)
from enrutador_bloques import (
    EJEMPLOS_ENRUTADOR_EXTRA,
    inferir_documentos_spec,
    inferir_tipo_y_subconsultas_spec,
)

ART_STD_RE = re.compile(r"^(RI-FI|RG)-ART-(\d{3})$")
STOP_BUSQ = {
    "como", "cual", "cuales", "cuando", "cuanto", "cuantos", "cuantas",
    "debe", "deben", "donde", "esta", "este", "estos", "hace", "para",
    "pero", "porque", "puede", "pueden", "quien", "quienes", "reglamento",
    "segun", "sobre", "tiene", "tienen", "alumno", "estudiante", "udec",
    "universidad", "concepcion", "pregunta", "indica", "establece",
}


def _buscar_corpus_seguro(
    corpus_obj: Any,
    consulta: str,
    k: int = 5,
    excluir_ids: set[str] | None = None,
) -> list[dict[str, str]]:
    """Usa el buscador léxico real de `Corpus` excluyendo `BLOCKED_UNIT_IDS`."""
    raw = corpus_obj.buscar(consulta, k=max(k * 4, 20))
    excluir = set(BLOCKED_UNIT_IDS) | set(excluir_ids or set())
    filtrados = [h for h in raw if h.get("id") and h["id"] not in excluir]
    return filtrados[:k]


def _extracto_orq(corpus_by_id: dict[str, str], uid: str) -> dict[str, str]:
    txt = corpus_by_id.get(uid, "")
    return {"id": uid, "extracto": txt[:160]}


def _keywords_step_back(
    texto: str,
    docs: list[str],
    claves: list[str],
    corpus_by_id: dict[str, str],
) -> str:
    """Genera una consulta reglamentaria concisa (sin copia textual de pregunta)."""
    toks = [t for t in cd.normalizar_texto(texto).split() if len(t) > 3 and t not in STOP_BUSQ]
    clave_toks: list[str] = []
    for uid in claves[:2]:
        t_art = corpus_by_id.get(uid, "")
        for w in cd.normalizar_texto(t_art[:280]).split():
            if len(w) > 4 and w not in STOP_BUSQ and w not in toks and w not in clave_toks:
                clave_toks.append(w)
                if len(clave_toks) >= 3:
                    break

    base = toks[:5] + clave_toks[:3]
    if "CAL" in docs and "calendario" not in base:
        base.append("calendario")
    if not base:
        base = ["normativa", "docencia", "pregrado"]
    return " ".join(base[:7])


def _sinonimo_reformulado(consulta_previa: str, sub: str, docs: list[str]) -> str:
    """Construye una reformulación distinta garantizada ante aviso de repetición."""
    prev_set = set(cd.normalizar_texto(consulta_previa).split())
    candidatos = [t for t in cd.normalizar_texto(sub).split() if len(t) > 3 and t not in STOP_BUSQ and t not in prev_set]
    extras = []
    if "RI-FI" in docs:
        extras.extend(["facultad", "ingenieria"])
    if "RG" in docs:
        extras.extend(["disposicion", "requisitos"])
    if "CAL" in docs:
        extras.extend(["fecha", "semestre", "2026"])
    for e in extras:
        if e not in prev_set and e not in candidatos:
            candidatos.append(e)
    if not candidatos:
        candidatos = ["articulo", "condiciones", "plazo", "excepcion"]
    return " ".join(candidatos[:6])


def _doc_n_de_unidad(uid: str) -> tuple[str, int] | None:
    m = ART_STD_RE.match(uid)
    if not m:
        return None
    return m.group(1), int(m.group(2))


def _crear_registro(
    prompt_template: str,
    rid: str,
    origen_id: str,
    split: str,
    pregunta_base: str,
    ctx: dict[str, Any],
    accion_obj: dict[str, Any],
    unidades_ref: list[str],
) -> dict[str, Any]:
    plan_json = json.dumps(ctx, ensure_ascii=False)
    prompt = prompt_template.replace("{{PLAN}}", plan_json)
    target = json.dumps(accion_obj, ensure_ascii=False)
    return {
        "id": rid,
        "origen_id": origen_id,
        "agente": "recuperador",
        "split": split,
        "accion": accion_obj["accion"],
        "intento": ctx["intento"],
        "pregunta_base": pregunta_base,
        "unidades_referenciadas": sorted(set(unidades_ref)),
        "ctx": ctx,
        "target_obj": accion_obj,
        "messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": target},
        ],
    }


def construir_registros_recuperador(
    prompt_template: str,
    corpus_obj: Any,
    corpus_by_id: dict[str, str],
) -> list[dict[str, Any]]:
    """Genera trayectorias multi-turno ReAct para entrenar al Recuperador."""
    registros: list[dict[str, Any]] = []
    specs = cd.todas_las_especificaciones()

    # Pool ordenado de unidades base limpias para relleno cuando faltan hits
    clean_fallback_pool = [
        uid
        for uid in sorted(corpus_by_id)
        if uid not in BLOCKED_UNIT_IDS and not uid.startswith("RG-ANEXO")
    ]

    for idx, spec in enumerate(specs):
        sid = spec["id"]
        split = spec["split"]
        pregunta = spec["pregunta"]
        tipo, subs = inferir_tipo_y_subconsultas_spec(spec)
        docs = inferir_documentos_spec(spec)
        sub = subs[0]
        claves = list(spec.get("evidencia_clave") or [])
        distractores = [d for d in (spec.get("distractores") or []) if d not in BLOCKED_UNIT_IDS]

        # 1) Casos de artículo inexistente explícito -> `existe`
        if spec.get("inexistentes"):
            inex = spec["inexistentes"][0]
            dn = _doc_n_de_unidad(inex)
            m_art = re.search(r"art[íi]culo\s*(\d+)", pregunta, re.IGNORECASE)
            if dn and m_art and numero_permitido_orquestador(dn[1], sub, "", []):
                ctx = {
                    "sub": sub,
                    "tipo": tipo,
                    "documentos": docs,
                    "evidencia_reunida": distractores[:3],
                    "ultima_observacion": None,
                    "intento": 1,
                    "feedback_verificador": None,
                }
                registros.append(
                    _crear_registro(
                        prompt_template,
                        f"REC-{sid}-EX",
                        sid,
                        split,
                        pregunta,
                        ctx,
                        {"accion": "existe", "args": {"doc": dn[0], "n": dn[1]}},
                        distractores[:3],
                    )
                )
            continue

        # 2) Casos sin evidencia clave (`insuficiente`) -> `buscar` reformulado o `suficiente` tras buscar
        if not claves:
            hits_init = [h["id"] for h in _buscar_corpus_seguro(corpus_obj, pregunta, k=4)]
            if not hits_init:
                hits_init = distractores[:3] or clean_fallback_pool[:3]
            consulta_sb = _keywords_step_back(sub, docs, [], corpus_by_id)
            if idx % 2 == 0:
                ctx = {
                    "sub": sub,
                    "tipo": tipo,
                    "documentos": docs,
                    "evidencia_reunida": hits_init[:4],
                    "ultima_observacion": None,
                    "intento": 1,
                    "feedback_verificador": None,
                }
                registros.append(
                    _crear_registro(
                        prompt_template,
                        f"REC-{sid}-B",
                        sid,
                        split,
                        pregunta,
                        ctx,
                        {"accion": "buscar", "args": {"consulta": consulta_sb, "k": 5}},
                        hits_init[:4],
                    )
                )
            else:
                # Intento 3 después de buscar y confirmar que no hay datos en el corpus
                obs = [_extracto_orq(corpus_by_id, u) for u in hits_init[:3]]
                ctx = {
                    "sub": sub,
                    "tipo": tipo,
                    "documentos": docs,
                    "evidencia_reunida": hits_init[:4],
                    "ultima_observacion": obs,
                    "intento": 3,
                    "feedback_verificador": None,
                }
                registros.append(
                    _crear_registro(
                        prompt_template,
                        f"REC-{sid}-S3",
                        sid,
                        split,
                        pregunta,
                        ctx,
                        {"accion": "suficiente", "args": {}},
                        hits_init[:4],
                    )
                )
            continue

        # 3) Casos con evidencia clave conocida (limpia fuera de BLOCKED_UNIT_IDS)
        patron = idx % 5
        hits_lex = [
            h["id"]
            for h in _buscar_corpus_seguro(corpus_obj, pregunta, k=5, excluir_ids=set(claves))
        ]
        ruido = (distractores + hits_lex)[:4]

        if patron == 0:
            # Búsqueda base ya cubrió todas las claves -> parar temprano (`suficiente`)
            ev_mix = list(dict.fromkeys(claves + ruido))[:6]
            ctx = {
                "sub": sub,
                "tipo": tipo,
                "documentos": docs,
                "evidencia_reunida": ev_mix,
                "ultima_observacion": None,
                "intento": 1,
                "feedback_verificador": None,
            }
            registros.append(
                _crear_registro(
                    prompt_template,
                    f"REC-{sid}-S1",
                    sid,
                    split,
                    pregunta,
                    ctx,
                    {"accion": "suficiente", "args": {}},
                    ev_mix,
                )
            )
        elif patron == 1:
            # Falta la evidencia clave en búsqueda base -> `buscar` con step-back
            consulta_sb = _keywords_step_back(sub, docs, claves, corpus_by_id)
            ctx = {
                "sub": sub,
                "tipo": tipo,
                "documentos": docs,
                "evidencia_reunida": ruido[:4],
                "ultima_observacion": None,
                "intento": 1,
                "feedback_verificador": None,
            }
            registros.append(
                _crear_registro(
                    prompt_template,
                    f"REC-{sid}-B1",
                    sid,
                    split,
                    pregunta,
                    ctx,
                    {"accion": "buscar", "args": {"consulta": consulta_sb, "k": 5}},
                    ruido[:4],
                )
            )
            # Y si clave[0] es artículo estándar, añadimos turno 2: vio el hit cortado -> `traer`
            dn = _doc_n_de_unidad(claves[0])
            if dn and numero_permitido_orquestador(dn[1], sub, "", [claves[0]]):
                obs2 = [_extracto_orq(corpus_by_id, u) for u in ([claves[0]] + ruido[:3])]
                ev2 = list(dict.fromkeys(ruido[:2] + [claves[0]]))[:5]
                ctx2 = {
                    "sub": subs[-1] if len(subs) > 1 else sub,
                    "tipo": tipo,
                    "documentos": docs,
                    "evidencia_reunida": ev2,
                    "ultima_observacion": obs2,
                    "intento": 2,
                    "feedback_verificador": None,
                }
                registros.append(
                    _crear_registro(
                        prompt_template,
                        f"REC-{sid}-T2",
                        sid,
                        split,
                        pregunta,
                        ctx2,
                        {"accion": "traer", "args": {"doc": dn[0], "n": dn[1]}},
                        ev2,
                    )
                )
        elif patron == 2:
            # Ya observó el artículo en turno anterior -> `traer` o `suficiente`
            dn = _doc_n_de_unidad(claves[0])
            if dn and numero_permitido_orquestador(dn[1], sub, "", ruido[:3] + [claves[0]]):
                obs = [_extracto_orq(corpus_by_id, u) for u in ([ruido[0]] if ruido else []) + [claves[0]]]
                ev_cur = list(dict.fromkeys((ruido[:3] + [claves[0]])))[:5]
                ctx = {
                    "sub": sub,
                    "tipo": tipo,
                    "documentos": docs,
                    "evidencia_reunida": ev_cur,
                    "ultima_observacion": obs,
                    "intento": 2,
                    "feedback_verificador": None,
                }
                registros.append(
                    _crear_registro(
                        prompt_template,
                        f"REC-{sid}-T",
                        sid,
                        split,
                        pregunta,
                        ctx,
                        {"accion": "traer", "args": {"doc": dn[0], "n": dn[1]}},
                        ev_cur,
                    )
                )
            else:
                obs = [_extracto_orq(corpus_by_id, u) for u in claves[:2] + ruido[:2]]
                ev_cur = list(dict.fromkeys(claves + ruido))[:6]
                ctx = {
                    "sub": sub,
                    "tipo": tipo,
                    "documentos": docs,
                    "evidencia_reunida": ev_cur,
                    "ultima_observacion": obs,
                    "intento": 2,
                    "feedback_verificador": None,
                }
                registros.append(
                    _crear_registro(
                        prompt_template,
                        f"REC-{sid}-S2",
                        sid,
                        split,
                        pregunta,
                        ctx,
                        {"accion": "suficiente", "args": {}},
                        ev_cur,
                    )
                )
        elif patron == 3:
            # Resiliencia ante aviso de acción repetida
            aviso = {
                "aviso": "Ya hiciste exactamente esta acción y no aportó nada nuevo. "
                "Busca con OTRAS palabras o responde 'suficiente'."
            }
            if len(claves) >= 2 and idx % 2 == 1:
                ev_parcial = [claves[0]] + ruido[:3]
                faltante = claves[1]
                consulta_alt = _keywords_step_back(
                    sub, [doc_de_unidad(faltante)], [faltante], corpus_by_id
                )
                consulta_alt = _sinonimo_reformulado(sub, consulta_alt, [doc_de_unidad(faltante)])
                ctx = {
                    "sub": subs[-1] if len(subs) > 1 else sub,
                    "tipo": tipo,
                    "documentos": docs,
                    "evidencia_reunida": ev_parcial,
                    "ultima_observacion": aviso,
                    "intento": 2,
                    "feedback_verificador": None,
                }
                registros.append(
                    _crear_registro(
                        prompt_template,
                        f"REC-{sid}-R2",
                        sid,
                        split,
                        pregunta,
                        ctx,
                        {"accion": "buscar", "args": {"consulta": consulta_alt, "k": 5}},
                        ev_parcial,
                    )
                )
            else:
                ev_ok = list(dict.fromkeys(claves + ruido))[:6]
                ctx = {
                    "sub": sub,
                    "tipo": tipo,
                    "documentos": docs,
                    "evidencia_reunida": ev_ok,
                    "ultima_observacion": aviso,
                    "intento": 2,
                    "feedback_verificador": None,
                }
                registros.append(
                    _crear_registro(
                        prompt_template,
                        f"REC-{sid}-RS",
                        sid,
                        split,
                        pregunta,
                        ctx,
                        {"accion": "suficiente", "args": {}},
                        ev_ok,
                    )
                )
        else:
            # Ciclo 2 tras `feedback_verificador` pidiendo la evidencia faltante
            faltante = claves[-1]
            doc_f = doc_de_unidad(faltante)
            ya = [c for c in claves[:-1]] + ruido[:2]
            dn = _doc_n_de_unidad(faltante)
            if dn and idx % 2 == 0:
                fb = f"Falta recuperar el Artículo {dn[1]} de {dn[0]} ({faltante}) para responder de forma completa."
                accion_fb = {"accion": "traer", "args": {"doc": dn[0], "n": dn[1]}}
            else:
                fb = (
                    f"Falta evidencia del documento {doc_f} que respalde todos los requisitos o "
                    "condiciones de la pregunta."
                )
                q_fb = _keywords_step_back(
                    sub, [doc_f], [faltante], corpus_by_id
                )
                accion_fb = {"accion": "buscar", "args": {"consulta": q_fb, "k": 5}}

            ctx = {
                "sub": subs[-1] if len(subs) > 1 else sub,
                "tipo": tipo,
                "documentos": docs,
                "evidencia_reunida": ya[:5],
                "ultima_observacion": None,
                "intento": 1,
                "feedback_verificador": fb,
            }
            registros.append(
                _crear_registro(
                    prompt_template,
                    f"REC-{sid}-FB",
                    sid,
                    split,
                    pregunta,
                    ctx,
                    accion_fb,
                    ya[:5],
                )
            )

    # Sumar ejemplos adicionales curados desde ENR-X:
    # (a) verificación de artículos presuntamente inexistentes (`existe` y paso siguiente)
    # (b) cruces multi-reglamento (`RI-FI` / `CAL` -> `RG`)
    for extra in EJEMPLOS_ENRUTADOR_EXTRA:
        sub0 = extra["sub_consultas"][0] if extra["sub_consultas"] else ""
        m_ex = re.search(
            r"verificar existencia del art[íi]culo\s+(\d+)\s+en\s+(RI-FI|RG)",
            sub0,
            re.IGNORECASE,
        )
        if m_ex:
            art_n = int(m_ex.group(1))
            doc_ex = m_ex.group(2).upper()
            if numero_permitido_orquestador(art_n, sub0, "", []):
                ctx_ex = {
                    "sub": sub0,
                    "tipo": extra["tipo"],
                    "documentos": extra["documentos"],
                    "evidencia_reunida": [],
                    "ultima_observacion": None,
                    "intento": 1,
                    "feedback_verificador": None,
                }
                registros.append(
                    _crear_registro(
                        prompt_template,
                        f"REC-{extra['id']}-EX",
                        extra["id"],
                        extra["split"],
                        extra["pregunta"],
                        ctx_ex,
                        {"accion": "existe", "args": {"doc": doc_ex, "n": art_n}},
                        [],
                    )
                )
                # Turno 2 tras confirmar existe=False: buscar norma real si aplica, o parar (`suficiente`)
                refs_ex = [u for u in extra["unidades_referenciadas"] if u not in BLOCKED_UNIT_IDS]
                obs_false = {"doc": doc_ex, "n": art_n, "existe": False}
                if refs_ex:
                    doc_f2 = doc_de_unidad(refs_ex[0])
                    sub_t2 = extra["sub_consultas"][-1]
                    q_t2 = _keywords_step_back(sub_t2, [doc_f2], refs_ex, corpus_by_id)
                    acc_t2 = {"accion": "buscar", "args": {"consulta": q_t2, "k": 5}}
                else:
                    sub_t2 = sub0
                    acc_t2 = {"accion": "suficiente", "args": {}}
                ctx_t2 = {
                    "sub": sub_t2,
                    "tipo": extra["tipo"],
                    "documentos": extra["documentos"],
                    "evidencia_reunida": [],
                    "ultima_observacion": obs_false,
                    "intento": 2,
                    "feedback_verificador": None,
                }
                registros.append(
                    _crear_registro(
                        prompt_template,
                        f"REC-{extra['id']}-EX2",
                        extra["id"],
                        extra["split"],
                        extra["pregunta"],
                        ctx_t2,
                        acc_t2,
                        [],
                    )
                )
            continue

        refs = [u for u in extra["unidades_referenciadas"] if u not in BLOCKED_UNIT_IDS]
        if len(refs) < 2:
            continue
        # Simular caso típico N12/N19: ya tiene la parte RI-FI (o CAL) y debe buscar la de RG
        ya = [refs[0]]
        falta = refs[1]
        doc_f = doc_de_unidad(falta)
        sub_target = extra["sub_consultas"][-1]
        q_target = _keywords_step_back(sub_target, [doc_f], [falta], corpus_by_id)
        ctx = {
            "sub": sub_target,
            "tipo": extra["tipo"],
            "documentos": extra["documentos"],
            "evidencia_reunida": ya,
            "ultima_observacion": None,
            "intento": 1,
            "feedback_verificador": None,
        }
        registros.append(
            _crear_registro(
                prompt_template,
                f"REC-{extra['id']}",
                extra["id"],
                extra["split"],
                extra["pregunta"],
                ctx,
                {"accion": "buscar", "args": {"consulta": q_target, "k": 5}},
                ya,
            )
        )

    return registros
