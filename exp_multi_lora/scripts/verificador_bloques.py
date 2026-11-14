"""Generador de pares supervisados para el Agente 4 (Verificador / Self-Refine).

Replica exactamente `04_verificador.txt` y `Orquestador.verificar()`
(`orquestador.py` L320-347):
- Trunca cada texto en `<evidencia>` a 700 caracteres, igual que `Orquestador`.
- Calcula `<chequeo_citas>` con la función exacta `chequear_citas_orquestador`.
- Genera ejemplos balanceados en 3 clases:
  1) `aprobado: true, destino: "fin"` (incluyendo cálculos/divisiones válidas y `No aplica` reales)
  2) `aprobado: false, destino: "redactor"` (omisión condiciones, error cálculo/polaridad, mínimo/máximo, cruce incompleto, sin citas, premisa falsa confirmada)
  3) `aprobado: false, destino: "recuperador"` (cita fuera de evidencia o inexistente, falta documento/evidencia en cruce)
"""

from __future__ import annotations

import json
import re
from typing import Any

from antifuga_multi import (
    BLOCKED_UNIT_IDS,
    cd,
    chequear_citas_orquestador,
    doc_de_unidad,
)

# Casos adicionales enfocados en aritmética / divisiones correctas vs erróneas sobre
# unidades limpias para vacunar contra falsos rechazos matemáticos (tipo H06/H22).
CASOS_ARITMETICOS_EXTRA: list[dict[str, Any]] = [
    {
        "id": "VER-ARIT-T01",
        "split": "train",
        "pregunta": "Si un estudiante inscrito en 5 asignaturas acumuló 135 horas totales semestrales entre trabajo presencial y autónomo, ¿cuántos créditos SCT representa en promedio por asignatura según las horas por crédito del glosario?",
        "evidencia_ids": ["RG-ART-003-DEF-08"],
        "borrador": (
            "Respuesta: Con 27 horas de trabajo presencial y no presencial por crédito transferible (SCT) [RG-ART-003-DEF-08], "
            "135 / 27 = 5 créditos SCT totales, lo que equivale a 5 / 5 = 1 crédito SCT promedio por asignatura.\n"
            "Condiciones o límites: Cada crédito transferible equivale a 27 horas de trabajo presencial y no presencial [RG-ART-003-DEF-08].\n"
            "Fuente: [RG-ART-003-DEF-08]"
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "cálculo correcto y condiciones fieles al artículo",
        "pensar": "Las divisiones 135 / 27 = 5 y 5 / 5 = 1 son aritméticamente exactas según las 27 horas por SCT de [RG-ART-003-DEF-08]; aunque chequear_citas abrevia RG-ART-003, la cita [RG-ART-003-DEF-08] consta literalmente en <evidencia>.",
    },
    {
        "id": "VER-ARIT-T02",
        "split": "train",
        "pregunta": "Si un estudiante acumula 270 horas totales de trabajo presencial y no presencial en 5 asignaturas, ¿cuántos créditos SCT suma y cuál es el promedio por asignatura?",
        "evidencia_ids": ["RG-ART-003-DEF-08"],
        "borrador": (
            "Respuesta: Considerando 27 horas de trabajo por crédito transferible [RG-ART-003-DEF-08], suma 270 / 27 = 10 créditos SCT totales, "
            "con un promedio de 10 / 5 = 2 créditos SCT por asignatura.\n"
            "Condiciones o límites: Se asigna 1 crédito transferible (SCT) a 27 horas de trabajo presencial y no presencial [RG-ART-003-DEF-08].\n"
            "Fuente: [RG-ART-003-DEF-08]"
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "operación correcta y equivalencia horaria fiel",
        "pensar": "El cálculo 270 / 27 = 10 y 10 / 5 = 2 está bien resuelto y cita [RG-ART-003-DEF-08], presente literalmente en <evidencia>.",
    },
    {
        "id": "VER-ARIT-T03",
        "split": "train",
        "pregunta": "Si un programa de formación complementaria exige al menos 24 créditos transferibles y un estudiante cursó 3 semestres aprobando 18 créditos, ¿cumple con el mínimo reglamentario?",
        "evidencia_ids": ["RG-ART-003-DEF-12"],
        "borrador": (
            "Respuesta: No cumple todavía con el mínimo: lleva 18 créditos (promedio 18 / 3 = 6 créditos por semestre), "
            "cifra inferior al piso de 24 créditos transferibles exigido para un Programa de Formación Complementaria [RG-ART-003-DEF-12], "
            "por lo que le faltan 24 - 18 = 6 créditos.\n"
            "Condiciones o límites: Estos programas están dirigidos a alumnos de distintas carreras que hayan aprobado los dos primeros años y deben tener carga no inferior a 24 créditos transferibles [RG-ART-003-DEF-12].\n"
            "Fuente: [RG-ART-003-DEF-12]"
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "cálculo, conclusión y condiciones consistentes",
        "pensar": "Tanto 18 / 3 = 6 como 18 < 24 y 24 - 18 = 6 son correctas y coherentes con 'No cumple', incluye la condición de haber aprobado los dos primeros años y la cita [RG-ART-003-DEF-12] consta en <evidencia>.",
    },
    {
        "id": "VER-ARIT-T04",
        "split": "train",
        "pregunta": "Si un estudiante aprobó 26 créditos en un Programa de Formación Complementaria tras 2 semestres, ¿cumple con la carga mínima exigida y puede exceder los 24 créditos?",
        "evidencia_ids": ["RG-ART-003-DEF-12"],
        "borrador": (
            "Respuesta: No, 26 créditos (promedio 26 / 2 = 13 créditos por semestre) sí supera el piso de 24 créditos exigido [RG-ART-003-DEF-12], por lo que cumple.\n"
            "Condiciones o límites: Dirigido a alumnos de distintas carreras que hayan aprobado los dos primeros años; carga académica no inferior a 24 créditos transferibles [RG-ART-003-DEF-12].\n"
            "Fuente: [RG-ART-003-DEF-12]"
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "el borrador abre negando ('No') pero luego concluye que 26 > 24 sí cumple",
        "pensar": "Aunque 26 / 2 = 13 y 26 > 24 son correctos, el borrador se contradice al abrir con 'No,' antes de afirmar que sí cumple.",
    },
    {
        "id": "VER-ARIT-T05",
        "split": "train",
        "pregunta": "Si en la Universidad un certificado de notas valida 2 asignaturas de intercambio de 5 créditos cada una en un semestre donde además el alumno aprobó 20 créditos en su carrera y 6 créditos de una asignatura revalidada (REV), ¿cuántos créditos suman como carga académica del semestre?",
        "evidencia_ids": ["RG-ART-041", "RI-FI-ART-024"],
        "borrador": (
            "Respuesta: Suman 20 + (2 * 5) = 30 créditos en la carga académica del semestre, ya que las asignaturas validadas (VAL) por intercambio sí se reconocen como carga académica del semestre en que se cursaron [RI-FI-ART-024], mientras que los 6 créditos de la asignatura revalidada (REV) no se consideran carga académica del semestre [RG-ART-041].\n"
            "Condiciones o límites: Para validar intercambio debe presentarse programa y calificación debidamente certificados al Vicedecano en el marco de convenios de movilidad [RI-FI-ART-024]; tampoco cuentan como carga las asignaturas CON, HOM o REC [RG-ART-041].\n"
            "Fuente: [RG-ART-041] [RI-FI-ART-024]"
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "cálculo y distinción VAL vs REV exactos",
        "pensar": "La operación 20 + (2 * 5) = 30 excluye correctamente los 6 créditos REV según [RG-ART-041] y reconoce VAL como carga semestral según [RI-FI-ART-024]; ambas citas existen en <chequeo_citas> y <evidencia>.",
    },
    {
        "id": "VER-ARIT-T06",
        "split": "train",
        "pregunta": "Si un profesor entregó los resultados de una evaluación escrita el día 12 tras rendirla el día 1 y afirma tener 20 días hábiles de plazo reglamentario, ¿cumplió el plazo de entrega?",
        "evidencia_ids": ["RG-ART-025"],
        "borrador": (
            "Respuesta: Según el Reglamento General, el profesor tiene un plazo máximo de 10 días hábiles para dar a conocer las calificaciones y pautas de corrección (no existe un plazo ordinario de 20 días hábiles), por lo que de haber transcurrido más de 10 días hábiles entre el día 1 y el día 12 no habría cumplido el plazo base [RG-ART-025].\n"
            "Condiciones o límites: En días calendario entre el día 1 y el día 12 corresponde verificar días inhábiles/feriados; además, el Vicedecano puede ampliar dicho plazo por razones justificadas, y los alumnos disponen de 5 días hábiles (también ampliables por el Vicedecano) para ejercer el derecho a revisión y aclarar dudas [RG-ART-025].\n"
            "Fuente: [RG-ART-025]"
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "refuta plazo de 20 días hábiles con condiciones fieles al artículo",
        "pensar": "El borrador cita correctamente [RG-ART-025] (presente en <chequeo_citas> y <evidencia>), aplica el plazo máximo de diez días hábiles, menciona la salvedad de ampliación por el Vicedecano y distingue días hábiles de corridos sin inventar cifras.",
    },
    {
        "id": "VER-ARIT-V01",
        "split": "val",
        "pregunta": "Si un estudiante aprobó 4 asignaturas sumando 324 horas totales de trabajo presencial y no presencial a razón de 27 horas por crédito transferible (SCT), ¿cuántos créditos SCT acumuló y cuál fue el promedio por asignatura?",
        "evidencia_ids": ["RG-ART-003-DEF-08"],
        "borrador": (
            "Respuesta: A razón de 27 horas por crédito transferible [RG-ART-003-DEF-08], 324 / 27 = 12 créditos SCT totales, "
            "equivalentes a un promedio de 12 / 4 = 3 créditos SCT por asignatura.\n"
            "Condiciones o límites: Cada crédito transferible representa 27 horas de trabajo presencial y no presencial [RG-ART-003-DEF-08].\n"
            "Fuente: [RG-ART-003-DEF-08]"
        ),
        "aprobado": True,
        "destino": "fin",
        "motivo": "cálculo correcto y equivalencia fiel",
        "pensar": "Las divisiones 324 / 27 = 12 y 12 / 4 = 3 son exactas y el borrador cita [RG-ART-003-DEF-08] presente literalmente en <evidencia>.",
    },
    {
        "id": "VER-ARIT-V02",
        "split": "val",
        "pregunta": "Si un estudiante obtuvo 22 créditos en su Programa de Formación Complementaria en 2 semestres, ¿cumple con el mínimo reglamentario de créditos transferibles?",
        "evidencia_ids": ["RG-ART-003-DEF-12"],
        "borrador": (
            "Respuesta: Sí cumple, ya que 22 / 2 = 11 créditos por semestre y 22 supera el mínimo de 24 créditos transferibles [RG-ART-003-DEF-12].\n"
            "Condiciones o límites: Dirigido a alumnos que hayan aprobado los dos primeros años; carga mínima no inferior a 24 créditos transferibles [RG-ART-003-DEF-12].\n"
            "Fuente: [RG-ART-003-DEF-12]"
        ),
        "aprobado": False,
        "destino": "redactor",
        "motivo": "afirma erróneamente que 22 supera el mínimo de 24 créditos transferibles",
        "pensar": "Aunque la división 22 / 2 = 11 es correcta, 22 es menor que 24, por lo que no cumple el mínimo exigido en [RG-ART-003-DEF-12].",
    },
]


def _formatear_borrador(respuesta: str, condiciones: str, fuente: str) -> str:
    return (
        f"Respuesta: {respuesta}\n"
        f"Condiciones o límites: {condiciones}\n"
        f"Fuente: {fuente}"
    )


def _construir_prompt_verificador(
    prompt_template: str,
    corpus_obj: Any,
    corpus_by_id: dict[str, str],
    pregunta: str,
    estado: str,
    evidencia_ids: list[str],
    borrador: str,
) -> str:
    bloque = (
        "\n".join(
            f"[{uid}] {corpus_by_id.get(uid, '')[:700]}" for uid in evidencia_ids
        )
        or "(sin evidencia)"
    )
    chequeo = chequear_citas_orquestador(corpus_obj, borrador, evidencia_ids)
    return (
        prompt_template.replace("{{PREGUNTA}}", pregunta)
        .replace("{{EVIDENCIA}}", f"estado: {estado}\n{bloque}")
        .replace("{{CHEQUEO}}", json.dumps(chequeo, ensure_ascii=False))
        .replace("{{BORRADOR}}", borrador)
    )


def _crear_registro_ver(
    prompt_template: str,
    corpus_obj: Any,
    corpus_by_id: dict[str, str],
    rid: str,
    origen_id: str,
    split: str,
    pregunta: str,
    estado: str,
    evidencia_ids: list[str],
    borrador: str,
    pensar: str,
    aprobado: bool,
    destino: str,
    motivo: str,
    unidades_ref: list[str],
) -> dict[str, Any]:
    prompt = _construir_prompt_verificador(
        prompt_template,
        corpus_obj,
        corpus_by_id,
        pregunta,
        estado,
        evidencia_ids,
        borrador,
    )
    veredicto_obj = {
        "aprobado": bool(aprobado),
        "destino": destino,
        "motivo": motivo,
    }
    target = f"<pensar>{pensar.strip()}</pensar>\n{json.dumps(veredicto_obj, ensure_ascii=False)}"
    return {
        "id": rid,
        "origen_id": origen_id,
        "agente": "verificador",
        "split": split,
        "aprobado": bool(aprobado),
        "destino": destino,
        "pregunta_base": pregunta,
        "unidades_referenciadas": sorted(set(unidades_ref)),
        "veredicto_obj": veredicto_obj,
        "messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": target},
        ],
    }


def _tiene_datos_en_700(
    spec: dict[str, Any],
    corpus_by_id: dict[str, str],
) -> bool:
    """Comprueba que las unidades clave no queden totalmente cortadas antes de cubrir el núcleo."""
    for uid in spec.get("evidencia_clave") or []:
        if not corpus_by_id.get(uid):
            return False
    return True


def _mutar_a_redactor(
    spec: dict[str, Any],
    evidencia_ids: list[str],
    idx: int,
) -> tuple[str, str, str] | None:
    """Genera `(borrador_malo, pensar, motivo)` verificable con destino `redactor`."""
    resp = spec["respuesta"]
    cond = spec["condiciones"]
    fuente = spec["fuente"]
    claves = list(spec.get("evidencia_clave") or [])

    # 1) Omisión de condiciones/excepciones relevantes
    if spec["estado"] == "suficiente" and cond.strip().lower() != "no aplica" and len(cond) >= 30 and idx % 3 == 0:
        borrador = _formatear_borrador(resp, "No aplica", fuente)
        pensar = (
            "Las citas existen en la evidencia, pero el borrador responde 'No aplica' en Condiciones o límites "
            "omitiendo salvedades, plazos o excepciones relevantes que sí figuran en los artículos entregados."
        )
        motivo = "omite condiciones y excepciones presentes en la evidencia bajo 'Condiciones o límites: No aplica'"
        return borrador, pensar, motivo

    # 2) Confirmación indebida de premisa falsa
    if spec["modo"] == "premisa_falsa" and spec["estado"] == "suficiente":
        borrador = _formatear_borrador(
            f"Sí, es correcto tal como indica la pregunta {fuente}.",
            cond,
            fuente,
        )
        pensar = (
            "La pregunta plantea un supuesto erróneo y la evidencia entregada lo desmiente, "
            "pero el borrador confirma indebidamente la premisa falsa en lugar de corregirla."
        )
        motivo = "confirma una premisa falsa que la evidencia entregada desmiente"
        return borrador, pensar, motivo

    # 3) Invertir mínimo / máximo si aparece explícitamente en la respuesta
    if re.search(r"\bm[íi]nim[oa]|no inferior a|al menos\b", resp, re.IGNORECASE):
        resp_inv = re.sub(r"\bm[íi]nimo\b", "máximo", resp, count=1, flags=re.IGNORECASE)
        if resp_inv == resp:
            resp_inv = re.sub(r"\bm[íi]nima\b", "máxima", resp, count=1, flags=re.IGNORECASE)
        if resp_inv == resp:
            resp_inv = re.sub(r"\bno inferior a\b", "como máximo de", resp, count=1, flags=re.IGNORECASE)
        if resp_inv == resp:
            resp_inv = re.sub(r"\bal menos\b", "como máximo", resp, count=1, flags=re.IGNORECASE)
        if resp_inv != resp:
            borrador = _formatear_borrador(resp_inv, cond, fuente)
            pensar = (
                "El texto del artículo fija un mínimo o piso reglamentario, pero el borrador lo transforma "
                "en un máximo, alterando el sentido normativo de la regla."
            )
            motivo = "convierte un mínimo de la evidencia en un máximo en la respuesta"
            return borrador, pensar, motivo

    # 4) Pregunta de cruce respondida a medias (estando todas las evidencias presentes)
    if len(claves) >= 2 and ";" in resp:
        primera_parte = resp.split(";", 1)[0].strip() + "."
        borrador = _formatear_borrador(primera_parte, "No aplica", f"[{claves[0]}]")
        pensar = (
            f"La pregunta consulta sobre dos partes distintas y la evidencia contiene [{claves[0]}] y [{claves[1]}], "
            "pero el borrador solo responde la primera parte e ignora la segunda."
        )
        motivo = f"responde solo una parte de la pregunta de cruce pese a contar con [{claves[1]}] en la evidencia"
        return borrador, pensar, motivo

    # 5) Respuesta polar contradictoria ("No, ..." antes de afirmar la regla)
    if resp.startswith(("Sí", "Si ", "Para ", "El ", "La ", "Un ", "Una ")) and idx % 2 == 1 and spec["estado"] == "suficiente":
        resp_contra = f"No, {resp[0].lower()}{resp[1:]}"
        borrador = _formatear_borrador(resp_contra, cond, fuente)
        pensar = (
            "El borrador abre con 'No,' contradiciendo la explicación afirmativa que entrega inmediatamente después "
            "con respaldo de la normativa."
        )
        motivo = "contradicción lógica entre el 'No' inicial y el desarrollo posterior de la respuesta"
        return borrador, pensar, motivo

    # 6) Falta total de citas en evidencia suficiente (`sin_citas: true`)
    if spec["estado"] == "suficiente" and claves:
        resp_sin = re.sub(r"\s*\[[A-Z0-9-]+\]", "", resp).strip()
        cond_sin = re.sub(r"\s*\[[A-Z0-9-]+\]", "", cond).strip()
        borrador = _formatear_borrador(resp_sin, cond_sin, "Reglamentación universitaria")
        pensar = (
            "El parámetro <chequeo_citas> indica sin_citas=true y no existen identificadores entre corchetes "
            "que respalden cada afirmación ni la fuente a partir de la evidencia entregada."
        )
        motivo = "omite los identificadores de cita [ID] exigidos tanto en el texto como en Fuente"
        return borrador, pensar, motivo

    return None


def _mutar_a_recuperador(
    spec: dict[str, Any],
    evidencia_ids: list[str],
    idx: int,
) -> tuple[list[str], str, str, str] | None:
    """Genera `(evidencia_truncada, borrador, pensar, motivo)` con destino `recuperador`."""
    claves = list(spec.get("evidencia_clave") or [])
    resp = spec["respuesta"]
    cond = spec["condiciones"]
    fuente = spec["fuente"]

    # Solo mutar casos con citas estándar visibles en `chequear_citas` para señal limpia
    citas_std = [u for u in claves if re.match(r"^(?:RI-FI|RG)-ART-\d{3}$|^CAL-2026-S[12]-\d{2}$", u)]
    if citas_std and idx % 2 == 0:
        quitada = citas_std[-1]
        ev_sin = [u for u in evidencia_ids if u != quitada]
        borrador = _formatear_borrador(resp, cond, fuente)
        m_art = re.match(r"^(RI-FI|RG)-ART-(\d{3})$", quitada)
        desc_cita = f"el Artículo {int(m_art.group(2))} de {m_art.group(1)} ({quitada})" if m_art else quitada
        pensar = (
            f"Según <chequeo_citas>, la cita [{quitada}] usada en el borrador figura con en_evidencia=false "
            f"y tampoco aparece en <evidencia>. Falta recuperar [{quitada}] antes de aprobar."
        )
        motivo = f"falta recuperar {desc_cita} en la evidencia (figura en_evidencia=false en chequeo de citas)"
        return ev_sin, borrador, pensar, motivo

    # Caso alternativo: cita inexistente alucinada o evidencia de cruce incompleta
    if len(claves) >= 2:
        faltante = claves[-1]
        ev_parcial = [u for u in evidencia_ids if u != faltante]
        doc_f = doc_de_unidad(faltante)
        borrador = _formatear_borrador(
            f"Con la evidencia disponible solo consta lo indicado en [{claves[0]}], pero falta información del documento {doc_f}.",
            "No aplica",
            f"[{claves[0]}]",
        )
        pensar = (
            f"La pregunta exige información de {doc_f} ({faltante}) que no figura en <evidencia>; "
            "corresponde devolver al Recuperador para buscar esa parte faltante."
        )
        motivo = f"falta recuperar evidencia de {doc_f} para responder de forma completa"
        return ev_parcial, borrador, pensar, motivo

    if spec["estado"] == "suficiente" and evidencia_ids:
        doc_fake = "RI-FI" if idx % 2 == 0 else "RG"
        fake_id = f"{doc_fake}-ART-098"
        borrador = _formatear_borrador(
            f"Según el artículo correspondiente, se aplica la regla solicitada [{fake_id}].",
            "No aplica",
            f"[{fake_id}]",
        )
        pensar = (
            f"<chequeo_citas> indica que [{fake_id}] tiene existe=false y en_evidencia=false; "
            "se debe devolver al Recuperador para localizar el artículo real."
        )
        motivo = f"la cita [{fake_id}] no existe en la normativa; el Recuperador debe buscar la fuente real"
        return evidencia_ids, borrador, pensar, motivo

    return None


def construir_registros_verificador(
    prompt_template: str,
    corpus_obj: Any,
    corpus_by_id: dict[str, str],
    seed: int = 202604,
) -> list[dict[str, Any]]:
    """Genera el dataset train/val completo para el Agente 4 (Verificador)."""
    registros: list[dict[str, Any]] = []
    specs = cd.todas_las_especificaciones()

    for idx, spec in enumerate(specs):
        sid = spec["id"]
        split = spec["split"]
        if not _tiene_datos_en_700(spec, corpus_by_id):
            continue

        evidencia_ids = cd.ensamblar_evidencia_ids(spec, corpus_by_id, seed=seed)
        evidencia_ids = [u for u in evidencia_ids if u not in BLOCKED_UNIT_IDS]

        # 1) Ejemplo positivo verdadero para TODOS los specs de validación y mayoría de train
        if split == "val" or (idx % 2 == 0) or spec["bloque"] in ("calculos_y_orden", "abstencion_honesta"):
            borrador_ok = _formatear_borrador(spec["respuesta"], spec["condiciones"], spec["fuente"])
            claves_std = [u for u in (spec.get("evidencia_clave") or []) if not re.match(r"^(?:RI-FI|RG)-ART-\d{3}$|^CAL-2026-S[12]-\d{2}$", u)]
            if spec["estado"] in ("insuficiente", "no_existe"):
                pensar_ok = (
                    f"La evidencia tiene estado '{spec['estado']}', el borrador declara explícitamente la ausencia "
                    "de respaldo sin inventar cifras ni artículos y cierra con Fuente sin respaldo."
                )
                motivo_ok = "abstención honesta fiel a la ausencia de evidencia"
            elif claves_std:
                pensar_ok = (
                    f"La respuesta responde todas las partes sin contradicciones; aunque chequear_citas abrevia o "
                    f"omite identificadores especiales ({', '.join(claves_std[:2])}), los textos citados constan literalmente en <evidencia>."
                )
                motivo_ok = "respuesta completa, citas verificables en <evidencia> y condiciones fieles"
            else:
                pensar_ok = (
                    "Cumple los cinco criterios: responde todas las partes, los datos y cálculos coinciden con los artículos, "
                    "todas las citas aparecen válidas y en evidencia en <chequeo_citas> y respeta condiciones."
                )
                motivo_ok = "respuesta completa, verificada en evidencia y citas válidas"

            registros.append(
                _crear_registro_ver(
                    prompt_template,
                    corpus_obj,
                    corpus_by_id,
                    f"VER-{sid}-OK",
                    sid,
                    split,
                    spec["pregunta"],
                    spec["estado"],
                    evidencia_ids,
                    borrador_ok,
                    pensar_ok,
                    True,
                    "fin",
                    motivo_ok,
                    evidencia_ids,
                )
            )

        # 2) Ejemplo negativo -> `redactor`
        mut_red = _mutar_a_redactor(spec, evidencia_ids, idx)
        if mut_red is not None and (split == "val" or idx % 2 == 1 or spec["bloque"] in ("condiciones_excepciones", "polares_y_lectura", "resiliencia_feedback")):
            b_malo, p_red, m_red = mut_red
            registros.append(
                _crear_registro_ver(
                    prompt_template,
                    corpus_obj,
                    corpus_by_id,
                    f"VER-{sid}-RED",
                    sid,
                    split,
                    spec["pregunta"],
                    spec["estado"],
                    evidencia_ids,
                    b_malo,
                    p_red,
                    False,
                    "redactor",
                    m_red,
                    evidencia_ids,
                )
            )

        # 3) Ejemplo negativo -> `recuperador`
        if idx % 3 == 1:
            mut_rec = _mutar_a_recuperador(spec, evidencia_ids, idx)
            if mut_rec is not None:
                ev_sub, b_rec, p_rec, m_rec = mut_rec
                estado_sub = "suficiente" if ev_sub else "insuficiente"
                registros.append(
                    _crear_registro_ver(
                        prompt_template,
                        corpus_obj,
                        corpus_by_id,
                        f"VER-{sid}-REC",
                        sid,
                        split,
                        spec["pregunta"],
                        estado_sub,
                        ev_sub,
                        b_rec,
                        p_rec,
                        False,
                        "recuperador",
                        m_rec,
                        ev_sub,
                    )
                )

    # 4) Sumar los casos aritméticos curados anti-falso-rechazo
    for caso in CASOS_ARITMETICOS_EXTRA:
        ev_ids = [u for u in caso["evidencia_ids"] if u not in BLOCKED_UNIT_IDS]
        registros.append(
            _crear_registro_ver(
                prompt_template,
                corpus_obj,
                corpus_by_id,
                caso["id"],
                caso["id"],
                caso["split"],
                caso["pregunta"],
                "suficiente",
                ev_ids,
                caso["borrador"],
                caso["pensar"],
                caso["aprobado"],
                caso["destino"],
                caso["motivo"],
                ev_ids,
            )
        )

    return registros
