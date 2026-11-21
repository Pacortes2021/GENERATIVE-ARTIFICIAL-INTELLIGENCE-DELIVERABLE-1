"""Generador de pares de preferencia DPO (`chosen` vs `rejected`) libre de fugas para Qwen3-4B."""

from __future__ import annotations

import json
import tempfile
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from ..herramientas import ejecutar_herramienta
from .antifuga import (
    BLOCKED_UNIT_IDS,
    _UNIT_ID_RE,
    cargar_preguntas_evaluacion_95,
    validar_registro_sft,
)
from .construir_dataset import (
    DEFAULT_FT_DATA_DIR,
    _construir_alerta_inexistente,
    _construir_bloque_inicial,
    _crear_buscador_limpio,
    _crear_pack_pdf_sintetico,
    _ejecutar_secuencia_tools,
    _system_prompt_para,
    _tc,
)


def _msg_asistente(texto: str = "", tool_calls: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    msg: dict[str, Any] = {"role": "assistant", "content": texto}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return msg


def _armar_par_dpo(
    pid: str,
    split: str,
    categoria: str,
    buscador: Any,
    pregunta: str,
    chosen: dict[str, Any],
    rejected: dict[str, Any],
    tools_previas: list[tuple[str, dict[str, Any]]] | None = None,
    asegurar_ids: list[str] | None = None,
    omitir_ids: set[str] | None = None,
    historial: list[dict[str, str]] | None = None,
    solo_pdfs: bool = False,
    tiene_pdfs: bool = False,
    usar_alerta_inv: bool = False,
) -> dict[str, Any]:
    alerta = _construir_alerta_inexistente(buscador, pregunta) if usar_alerta_inv else ""
    bloque = _construir_bloque_inicial(
        buscador,
        pregunta,
        asegurar_ids=asegurar_ids,
        omitir_ids=omitir_ids,
        historial=historial,
    )
    prompt_msgs: list[dict[str, Any]] = [
        {"role": "system", "content": _system_prompt_para(solo_pdfs=solo_pdfs, tiene_pdfs=tiene_pdfs)}
    ]
    for h in historial or []:
        prompt_msgs.append({"role": h["role"], "content": h["content"]})
    prompt_msgs.append({"role": "user", "content": f"{pregunta}{alerta}{bloque}"})
    if tools_previas:
        prompt_msgs.extend(_ejecutar_secuencia_tools(buscador, tools_previas))

    return {
        "id": pid,
        "split": split,
        "categoria": categoria,
        "prompt": prompt_msgs,
        "chosen": chosen,
        "rejected": rejected,
    }


def _pares_eleccion_herramienta(buscador: Any) -> list[dict[str, Any]]:
    """Pares que enseñan cuándo usar `dias_entre` (e inclusivo), `calcular` y `existe_articulo`."""
    pares: list[dict[str, Any]] = []

    # 1. Fechas -> `dias_entre` vs error clásico `calcular` o cálculo mental
    casos_fechas = [
        ("train", "2026-04-03", "2026-05-01", False, "CAL-2026-S1-09",
         "¿Cuántos días corridos hay desde el feriado nacional del 03 de abril hasta el 01 de mayo de 2026?",
         _msg_asistente(tool_calls=[_tc("calcular", {"expresion": "42 / 4"})])),
        ("train", "2026-06-30", "2026-07-05", True, "CAL-2026-S1-14",
         "¿Cuántos días totales abarcan las vacaciones de invierno del 30 de junio al 05 de julio de 2026 inclusive?",
         _msg_asistente(tool_calls=[_tc("dias_entre", {"fecha_inicio": "2026-06-30", "fecha_fin": "2026-07-05", "inclusivo": False})])),
        ("train", "2026-03-02", "2026-03-06", True, "CAL-2026-S1-01",
         "¿Cuántos días dura inclusive la inducción de Vinculación a la Vida Universitaria del 02 al 06 de marzo de 2026?",
         _msg_asistente(tool_calls=[_tc("dias_entre", {"fecha_inicio": "2026-03-02", "fecha_fin": "2026-03-06", "inclusivo": False})])),
        ("train", "2026-07-10", "2026-07-24", False, "CAL-2026-S1-04",
         "¿Cuántos días pasan entre el cierre de asignaturas semestrales (10 de julio) y el de anuales (24 de julio) en 2026?",
         _msg_asistente(tool_calls=[_tc("calcular", {"expresion": "24 - 10 + 1"})])),
        ("train", "2026-05-01", "2026-05-21", False, "CAL-2026-S1-10",
         "¿Cuántos días transcurren entre el feriado del 01 de mayo y el del 21 de mayo de 2026?",
         _msg_asistente("Entre el 01 de mayo y el 21 de mayo transcurren 21 días corridos [CAL-2026-S1-10].")),
        ("train", "2026-08-20", "2026-12-08", False, "CAL-2026-S2-08",
         "¿Cuántos días separan el feriado nacional del 20 de agosto del feriado del 08 de diciembre de 2026?",
         _msg_asistente(tool_calls=[_tc("calcular", {"expresion": "12 - 8"})])),
        ("val", "2026-07-13", "2026-07-24", True, "CAL-2026-S1-06",
         "¿Cuántos días inclusive duran las Evaluaciones de Recuperación del primer semestre 2026 (del 13 al 24 de julio)?",
         _msg_asistente(tool_calls=[_tc("dias_entre", {"fecha_inicio": "2026-07-13", "fecha_fin": "2026-07-24", "inclusivo": False})])),
        ("val", "2026-10-12", "2026-12-08", False, "CAL-2026-S2-10",
         "¿Cuántos días transcurren entre el feriado del 12 de octubre y el feriado del 08 de diciembre de 2026?",
         _msg_asistente(tool_calls=[_tc("calcular", {"expresion": "42 / 4"})])),
    ]
    for idx, (sp, fi, ff, inc, cid, preg, rej) in enumerate(casos_fechas, 1):
        ch = _msg_asistente(tool_calls=[_tc("dias_entre", {"fecha_inicio": fi, "fecha_fin": ff, "inclusivo": inc})])
        pares.append(
            _armar_par_dpo(f"DPO-TOOL-CAL-{idx:02d}", sp, "dpo_tool_calendario", buscador, preg, ch, rej, asegurar_ids=[cid])
        )

    # 2. Cálculos numéricos -> `calcular` vs operar mentalmente o elegir mal la expresión
    casos_calc = [
        ("train", "RG-ART-038", "(5.5 + 5.9) / 2",
         "Un alumno nuevo promediará sus dos evaluaciones diagnósticas de 5,5 y 5,9 (mitad cada una). ¿Supera el puntaje de Inicio Adelantado?",
         _msg_asistente(tool_calls=[_tc("calcular", {"expresion": "(5.5 + 5.9) / 2"})]),
         _msg_asistente("El promedio es 5,65, por lo que no supera el umbral de 5,7 del Inicio Adelantado [RG-ART-038].")),
        ("train", "RG-ART-013", "(28 / 50) * 100",
         "En una evaluación rindieron 50 alumnos y 28 sacaron nota bajo 4,0. ¿Supera el 50% para convocar a la Comisión de Evaluación?",
         _msg_asistente(tool_calls=[_tc("calcular", {"expresion": "(28 / 50) * 100"})]),
         _msg_asistente("No supera el 50%, porque 28 de 50 es menos de la mitad según [RG-ART-013].")),
        ("train", "RI-FI-ART-015", "46 - 18",
         "Un estudiante convalidó 18 créditos al ingresar a nivel superior y suma 46 créditos registrados. ¿Cuántos créditos reales cursados computan para el Art. 15 RI-FI?",
         _msg_asistente(tool_calls=[_tc("calcular", {"expresion": "46 - 18"})]),
         _msg_asistente(tool_calls=[_tc("calcular", {"expresion": "46 + 18"})])),
        ("val", "RG-ART-048", "0.6 * 5.2 + 0.4 * 5.8",
         "Si un egresado pondera 60% su promedio 5,2 y 40% su examen de 5,8, ¿qué calificación y concepto lleva en su diploma?",
         _msg_asistente(tool_calls=[_tc("calcular", {"expresion": "0.6 * 5.2 + 0.4 * 5.8"})]),
         _msg_asistente("Con promedio 5,5 y 5,8 obtiene Distinción Máxima [RG-ART-048].")),
    ]
    for idx, (sp, uid, _expr, preg, ch, rej) in enumerate(casos_calc, 1):
        pares.append(
            _armar_par_dpo(f"DPO-TOOL-CALC-{idx:02d}", sp, "dpo_tool_calculo", buscador, preg, ch, rej, asegurar_ids=[uid])
        )

    # 3. Artículos inexistentes en RI-FI / RG -> `existe_articulo` vs citar otro reglamento
    casos_ex = [
        ("train", "RI-FI", 51, "Necesito revisar qué disposiciones fija el Artículo 51 del Reglamento Interno de Ingeniería sobre ayudantías.",
         _msg_asistente(tool_calls=[_tc("existe_articulo", {"doc": "RI-FI", "numero": 51})]),
         _msg_asistente(tool_calls=[_tc("leer_articulo", {"doc": "RG", "numero": 51})])),
        ("train", "RG", 64, "¿Qué multa administrativa señala el Artículo 64 del Reglamento General?",
         _msg_asistente(tool_calls=[_tc("existe_articulo", {"doc": "RG", "numero": 64})]),
         _msg_asistente("El Artículo 64 del Reglamento General fija sanciones disciplinarias [RG-ART-052].")),
        ("val", "RI-FI", 48, "¿Qué tabla de distinciones contiene el Art. 48 del Reglamento Interno de Ingeniería?",
         _msg_asistente(tool_calls=[_tc("existe_articulo", {"doc": "RI-FI", "numero": 48})]),
         _msg_asistente(tool_calls=[_tc("leer_articulo", {"doc": "RG", "numero": 48})])),
    ]
    for idx, (sp, doc, num, preg, ch, rej) in enumerate(casos_ex, 1):
        pares.append(
            _armar_par_dpo(f"DPO-TOOL-EX-{idx:02d}", sp, "dpo_tool_existe", buscador, preg, ch, rej)
        )

    # 4. Evidencia faltante en top-p -> `leer_articulo`/`buscar_reglamento` vs inventar; y NO llamar `calcular` innecesariamente
    casos_extra_tools = [
        ("train", "dpo_tool_recuperacion", "RG-ART-014", {"RG-ART-014"},
         "Según el Art. 14 del Reglamento General, ¿qué debe priorizar un alumno si le programan dos actividades obligatorias simultáneas?",
         _msg_asistente(tool_calls=[_tc("leer_articulo", {"doc": "RG", "numero": 14})]),
         _msg_asistente("No tengo información sobre tope de horarios en el Reglamento General [RG-ART-042].")),
        ("train", "dpo_tool_recuperacion", "RI-FI-ART-032", {"RI-FI-ART-032"},
         "En el Reglamento Interno de Ingeniería, ¿cuántos docentes y representantes estudiantiles integran el Consejo de Carrera del Art. 32?",
         _msg_asistente(tool_calls=[_tc("leer_articulo", {"doc": "RI-FI", "numero": 32})]),
         _msg_asistente("El Consejo de Carrera de Ingeniería se compone únicamente por el Jefe de Carrera y dos docentes [RI-FI-ART-033].")),
        ("train", "dpo_tool_recuperacion", "RG-ART-040", {"RG-ART-040"},
         "¿Qué autoridad establece la tabla de asignaturas homologables entre distintas versiones del Plan de Estudio?",
         _msg_asistente(tool_calls=[_tc("buscar_reglamento", {"consulta": "tabla asignaturas homologables Vicedecano plan estudio"})]),
         _msg_asistente("La tabla de homologaciones la aprueba directamente el Centro de Alumnos [RG-ART-037].")),
        ("val", "dpo_tool_recuperacion", "RG-ART-027", {"RG-ART-027"},
         "¿Con qué programa informático oficial se registran las Notas Finales para generar el Acta de Notas en el SAC?",
         _msg_asistente(tool_calls=[_tc("buscar_reglamento", {"consulta": "programa informático Acta de Notas SAC INFODA"})]),
         _msg_asistente("Las Notas Finales se ingresan manualmente en papel sin plataforma informática específica [RG-ART-021].")),
        ("train", "dpo_tool_no_espuria", "RG-ART-019", None,
         "Al comenzar una asignatura, ¿qué documentos e información mínima debe entregar por escrito u otro canal oficial el Profesor Encargado?",
         _msg_asistente(
             "Al inicio de la dictación debe entregar el **Programa y el Syllabus aprobados por la Facultad**, el régimen de asistencia, metodología, actividades, formas de evaluación y modalidad de cálculo de la Nota Final (en medio que permita almacenar o imprimir) [RG-ART-019]."
         ),
         _msg_asistente(tool_calls=[_tc("calcular", {"expresion": "1 + 1"})])),
        ("train", "dpo_tool_no_espuria", "RG-ART-050", None,
         "¿Hasta qué momento conserva un estudiante su calidad de alumno regular entre períodos lectivos?",
         _msg_asistente(
             "La calidad de alumno regular se mantiene **hasta el inicio del periodo de inscripción de asignaturas del Período Lectivo Ordinario siguiente** [RG-ART-050]."
         ),
         _msg_asistente(tool_calls=[_tc("dias_entre", {"fecha_inicio": "2026-03-02", "fecha_fin": "2026-07-10", "inclusivo": False})])),
    ]
    for idx, (sp, cat, uid, omit, preg, ch, rej) in enumerate(casos_extra_tools, 1):
        pares.append(
            _armar_par_dpo(
                f"DPO-TOOL-RET-{idx:02d}",
                sp,
                cat,
                buscador,
                preg,
                ch,
                rej,
                omitir_ids=omit,
                asegurar_ids=[uid] if not omit else None,
            )
        )

    return pares


def _pares_desigualdades_post_tool(buscador: Any) -> list[dict[str, Any]]:
    """Enseña a interpretar estrictamente `<`, `<=`, `>` y rangos tras recibir el resultado de Python."""
    casos = [
        # (split, uid, expr, preg, chosen_txt, rejected_txt)
        ("train", "RG-ART-038", "5.7 > 5.7",
         "Un novato sacó exactamente 5,7 en la Evaluación Diagnóstica. ¿Cumple el requisito para Inicio Adelantado?",
         "No cumple el requisito: la comparación `5.7 > 5.7` da falso, ya que [RG-ART-038] exige obtener un resultado **estrictamente superior a 5,7** en la Evaluación Diagnóstica.",
         "Sí cumple el requisito, porque 5,7 alcanza exactamente el umbral de 5,7 exigido por [RG-ART-038] para optar al Inicio Adelantado."),
        ("train", "RG-ART-038", "(5.6 + 5.9) / 2",
         "Promediando 5,6 y 5,9 en componentes iguales de la Evaluación Diagnóstica, ¿puede optar al Inicio Adelantado?",
         "Sí: el promedio calculado es **5,75**, valor estrictamente superior a 5,7, por lo que cumple la condición del Inicio Adelantado [RG-ART-038].",
         "No cumple, porque 5,75 es inferior al requisito mínimo exigido en [RG-ART-038]."),
        ("train", "RG-ART-038", "(5.4 + 5.8) / 2",
         "Si un estudiante nuevo promedia 5,4 y 5,8 en su Evaluación Diagnóstica, ¿accede al Inicio Adelantado?",
         "No: su promedio es **5,6**, que es inferior a 5,7, mientras que [RG-ART-038] exige un resultado superior a 5,7.",
         "Sí accede al Inicio Adelantado porque su promedio 5,6 supera el puntaje mínimo de [RG-ART-038]."),
        ("train", "RG-ART-013", "(25 / 50) * 100",
         "En un curso de 50 alumnos, 25 obtuvieron nota bajo 4,0. ¿Se cumple la causal automática de más del 50% del Art. 13 RG?",
         "No se cumple automáticamente: el porcentaje es **50%** (`25 / 50 * 100 = 50`), y [RG-ART-013] exige que **más del 50%** de los alumnos que rinden obtenga nota inferior a 4,0.",
         "Sí se cumple la causal del Art. 13, porque 50% alcanza el umbral exigido por [RG-ART-013] para convocar a la Comisión de Evaluación."),
        ("train", "RG-ART-013", "(26 / 50) * 100",
         "De 50 estudiantes que rindieron un certamen, 26 tuvieron nota menor a 4,0. ¿Corresponde convocar a la Comisión de Evaluación por el umbral del 50%?",
         "Sí corresponde: el porcentaje es **52%**, valor superior al 50%, activando la convocatoria a la Comisión de Evaluación por el Director de Departamento [RG-ART-013].",
         "No corresponde convocar a la Comisión porque 52% es inferior al umbral mínimo señalado en [RG-ART-013]."),
        ("train", "RG-ART-043", "18 - 5",
         "Tengo 18 créditos inscritos y quiero abandonar una asignatura de 5 créditos en la semana 3. Si el mínimo reglamentario fuera 14 créditos, ¿me alcanza?",
         "No te alcanza: al restar los 5 créditos quedas con **13 créditos** (`18 - 5 = 13`), que es inferior al mínimo de 14 créditos, y [RG-ART-043] prohíbe quedar bajo el mínimo establecido.",
         "Sí puedes abandonarla porque 13 créditos es superior al mínimo de 14 créditos exigido en [RG-ART-043]."),
        ("train", "RG-ART-043", "21 - 5",
         "Con 21 créditos inscritos en la semana 2, si abandono un ramo de 5 créditos y mi mínimo es 15 créditos, ¿puedo hacerlo?",
         "Sí puedes: quedarías con **16 créditos** (`21 - 5 = 16 >= 15`) y estás dentro de las primeras 4 semanas desde el inicio de clases (si no es PLEV ni repetiste el abandono en el ramo) [RG-ART-043].",
         "No puedes abandonarlo porque quedar con 16 créditos incumple el mínimo de 15 establecido en [RG-ART-043]."),
        ("train", "RG-ART-010", "40 * 0.6",
         "Un Consejo hipotético tiene 40 miembros y asisten 22. Si el quórum es 60%, ¿pueden sesionar?",
         "No pueden sesionar: el 60% de 40 es **24 integrantes**, y como 22 es inferior a 24, no se cumple el quórum mínimo de sesión fijado en [RG-ART-010].",
         "Sí pueden sesionar porque 22 asistentes supera el mínimo de 24 miembros calculado para [RG-ART-010]."),
        # Held-out en VAL (RG-ART-048)
        ("val", "RG-ART-048", "0.6 * 4.7 + 0.4 * 5.2",
         "Un egresado pondera 60% su nota 4,7 y 40% su examen 5,2. ¿Qué concepto obtiene en su Diploma de Título según el Art. 48 RG?",
         "La nota ponderada es **4,9**, ubicada en el tramo `4,0 - 4,9`, por lo que obtiene el concepto **\"Aprobado por Unanimidad\"** según [RG-ART-048].",
         "Con nota 4,9 obtiene el concepto \"Aprobado con Distinción\" de acuerdo con [RG-ART-048]."),
        ("val", "RG-ART-048", "0.5 * 5.4 + 0.5 * 6.0",
         "Si el promedio final ponderado de un titulado es mitad 5,4 y mitad 6,0, ¿obtiene Distinción o Distinción Máxima?",
         "Obtiene **Aprobado con Distinción Máxima**: la nota final es **5,7** (`0.5 * 5.4 + 0.5 * 6.0 = 5.7`), que entra justo en el tramo `5,7 - 7,0` fijado en [RG-ART-048].",
         "Obtiene Aprobado con Distinción, porque 5,7 no supera el tramo superior de 5,7 en [RG-ART-048]."),
        ("val", "RG-ART-048", "0.6 * 5.0 + 0.4 * 5.5",
         "Con 60% nota 5,0 y 40% nota 5,5, ¿qué distinción marca el Diploma de Título según el Art. 48 RG?",
         "Obtiene **Aprobado con Distinción**: la nota calculada es **5,2**, comprendida en el rango `5,0 - 5,6` de [RG-ART-048].",
         "Obtiene Aprobado por Unanimidad porque 5,2 es inferior a 5,6 en la escala de [RG-ART-048]."),
    ]
    pares: list[dict[str, Any]] = []
    for idx, (sp, uid, expr, preg, ch_txt, rej_txt) in enumerate(casos, 1):
        pares.append(
            _armar_par_dpo(
                f"DPO-INEQ-{idx:02d}", sp, "dpo_desigualdades", buscador, preg,
                _msg_asistente(ch_txt), _msg_asistente(rej_txt),
                tools_previas=[("calcular", {"expresion": expr})],
                asegurar_ids=[uid],
            )
        )

    # Pares post-tool `dias_entre`: interpretar días corridos vs topes reglamentarios
    casos_dias_post = [
        ("train", "RG-ART-043", "2026-03-09", "2026-04-10", False,
         "Si las clases comenzaron el 09 de marzo de 2026 y hoy es 10 de abril de 2026, ¿aún estoy dentro del plazo general de 4 semanas (28 días) para abandonar una asignatura?",
         "No: entre el 09 de marzo y el 10 de abril transcurrieron **32 días** corridos, superando el plazo de **4 semanas (28 días)** fijado en [RG-ART-043] para abandonar sin especificación de motivos.",
         "Sí estás dentro del plazo, porque 32 días equivalen exactamente a 4 semanas desde el inicio de clases [RG-ART-043]."),
        ("train", "RG-ART-037", "2026-05-04", "2026-05-18", False,
         "Presenté una solicitud de convalidación el 04 de mayo de 2026 y me respondieron el 18 de mayo. ¿El Vicedecano resolvió dentro del plazo de 15 días del Art. 37 RG?",
         "Sí: transcurrieron **14 días** corridos (`14 <= 15`), por lo que el Vicedecano resolvió dentro del plazo máximo de **15 días** establecido en [RG-ART-037].",
         "No resolvió dentro del plazo, porque entre el 04 y el 18 de mayo pasaron más de 15 días [RG-ART-037]."),
        ("train", "CAL-2026-S1-05", "2026-07-10", "2026-07-24", False,
         "En el primer semestre 2026, ¿cuántos días exactos hay de diferencia entre el cierre de asignaturas semestrales y el de anuales?",
         "Hay **14 días** de diferencia: las semestrales terminan el **10 de julio** [CAL-2026-S1-04] y las anuales el **24 de julio** [CAL-2026-S1-05].",
         "Hay exactamente 15 días de diferencia entre el 10 y el 24 de julio [CAL-2026-S1-04] [CAL-2026-S1-05]."),
        ("val", "RG-ART-044", "2026-03-09", "2026-04-12", False,
         "Me reingresé a mi misma carrera el 09 de marzo de 2026 sin haber perdido la carrera y presenté solicitud el 12 de abril de 2026. ¿Cumplí los 30 primeros días?",
         "No: del 09 de marzo al 12 de abril transcurrieron **34 días**, excediendo el límite de **30 primeros días** desde el ingreso para pedir mantener tu situación académica anterior [RG-ART-044].",
         "Sí cumpliste el plazo, porque 34 días queda dentro del período inicial contemplado en [RG-ART-044]."),
    ]
    for offset, (sp, uid, fi, ff, inc, preg, ch_txt, rej_txt) in enumerate(casos_dias_post, len(casos) + 1):
        aseg = [uid] if uid != "CAL-2026-S1-05" else ["CAL-2026-S1-04", "CAL-2026-S1-05"]
        pares.append(
            _armar_par_dpo(
                f"DPO-INEQ-{offset:02d}", sp, "dpo_desigualdades", buscador, preg,
                _msg_asistente(ch_txt), _msg_asistente(rej_txt),
                tools_previas=[("dias_entre", {"fecha_inicio": fi, "fecha_fin": ff, "inclusivo": inc})],
                asegurar_ids=aseg,
            )
        )
    return pares


def _pares_completitud_y_apelacion(buscador: Any) -> list[dict[str, Any]]:
    """Entrena enumeración completa de requisitos, plazos, excepciones y apelaciones sin truncar."""
    fichas = [
        ("train", "RI-FI-ART-007",
         "¿Cuál es el orden completo de prioridades para inscribir asignaturas en Ingeniería según el RI-FI?",
         "Según [RI-FI-ART-007], siempre cumpliendo prerrequisitos y fechas del calendario, las cuatro prioridades en orden son:\n"
         "a) Asignaturas atrasadas respecto del avance en el Plan de Estudio.\n"
         "b) Asignaturas obligatorias reprobadas anteriormente y no aprobadas a la fecha.\n"
         "c) Asignaturas correspondientes a su nivel de avance.\n"
         "d) Asignaturas que desee adelantar respecto del Plan de Estudio.",
         "Según [RI-FI-ART-007], se priorizan las asignaturas atrasadas, las obligatorias reprobadas y las correspondientes al nivel de avance del estudiante."),
        ("train", "RG-ART-025",
         "Si un alumno revisa su evaluación escrita con el profesor y sigue en desacuerdo con la nota, ¿ante quién puede reclamar, en qué plazo y quién decide finalmente?",
         "Puede solicitar por escrito y fundamentadamente una nueva revisión ante el **Vicedecano** de la Facultad responsable en un plazo máximo de **5 días hábiles** desde la revisión con el profesor [RG-ART-025]. Si la estima fundada, el Vicedecano nombra una **Comisión ad hoc**, la que resuelve en **10 días corridos** desde la reclamación mediante decisión **inapelable** comunicada personalmente con firma del alumno [RG-ART-025].",
         "Si sigue en desacuerdo tras revisar con el profesor, el estudiante tiene 5 días hábiles para revisar su prueba y aclarar dudas [RG-ART-025]."),
        ("train", "RG-ART-033",
         "¿Cuál es la duración máxima de una suspensión de estudios y qué plan de estudios aplica al reincorporarse?",
         "La suspensión de estudios puede extenderse por un máximo de **3 años calendario** (perdiéndose la calidad de alumno si no se solicita reincorporación dentro de ese plazo) [RG-ART-033]. Al reincorporarse debe adscribirse al Plan de Estudio vigente en esa fecha, **con la excepción** de los alumnos en intercambio, quienes se mantienen en su mismo plan [RG-ART-033].",
         "La suspensión dura hasta tres años calendario y al reincorporarse todos los alumnos deben pasar siempre al Plan de Estudio vigente [RG-ART-033]."),
        ("train", "RG-ART-052",
         "¿Qué facilidades académicas reciben los representantes estudiantiles y qué exigencia mantienen sin cambios?",
         "El Vicedecano otorgará facilidades flexibilizando requisitos académicos en clases teóricas y prácticas (cuando sea posible) a Presidentes de Centros de Alumnos, Presidentes/Secretarios/Tesoreros de Federaciones de Estudiantes (Concepción, Chillán y Los Ángeles) y participantes en representación oficial UdeC en actividades extraprogramáticas; **sin embargo, deberán cumplir igualmente con los requisitos para aprobar las asignaturas** [RG-ART-052].",
         "Los presidentes de Centros de Alumnos y federaciones reciben flexibilización de requisitos académicos otorgada por el Vicedecano [RG-ART-052]."),
        ("train", "RG-ART-054",
         "En el cambio de carrera del Art. 54 RG, ¿qué dos requisitos iniciales se piden, dónde se presenta la solicitud y qué autoridades deciden y sancionan?",
         "Exige: a) ser alumno regular manteniendo derecho a continuar estudios en la carrera de origen; b) tener el promedio mínimo del Reglamento Interno de la Facultad de destino (salvo regla distinta dentro de la misma Facultad) [RG-ART-054]. La solicitud se presenta en **UDARAE**, resuelve una Comisión integrada por **Director de Docencia, Decano y Jefe de Carrera**, sanciona el **Rector** y registra **UDARAE en el SAC** [RG-ART-054].",
         "Para cambiar de carrera se requiere ser alumno regular y tener el promedio exigido por la facultad de destino, presentándose en UDARAE [RG-ART-054]."),
        ("train", "RG-ART-037",
         "¿En qué se distingue la revalidación de la convalidación según el Art. 37 RG, qué documentos pide esta última y cuánto tarda el Vicedecano en resolver?",
         "La **revalidación** aplica a una misma asignatura aprobada en otro plan dentro de la UdeC, mientras la **convalidación** reemplaza una asignatura del plan por otra equivalente aprobada en esta u otra institución superior (adjuntando certificado completo de calificaciones y programas acreditados, salvo asignaturas cursadas en la UdeC) [RG-ART-037]. El **Vicedecano**, previo informe del Departamento, resuelve en **15 días** e informa al alumno y su Facultad [RG-ART-037].",
         "La convalidación y revalidación permiten reconocer ramos aprobados previamente presentando certificados de notas ante el Vicedecano [RG-ART-037]."),
        ("train", "RI-FI-ART-024",
         "¿Qué requisitos y trámites exige Ingeniería para validar asignaturas cursadas en intercambio y cómo quedan registradas?",
         "El estudiante en movilidad bajo convenio debe presentar al **Vicedecano** el **programa de la asignatura** y la **calificación obtenida**, ambos debidamente certificados [RI-FI-ART-024]. La nota se incorpora al **SAC** en la Escala Oficial de la UdeC y la asignatura se reconoce como carga académica en el semestre en que fue cursada [RI-FI-ART-024].",
         "El estudiante en intercambio debe presentar sus notas certificadas para que se incorporen al SAC [RI-FI-ART-024]."),
        ("train", "RG-ART-042",
         "¿Qué condiciones debe cumplir un alumno regular al inscribir asignaturas y cuándo puede autorizarse una carga menor al mínimo?",
         "Debe inscribir en fechas del calendario (sin choque de horarios en actividades obligatorias), cumplir prerrequisitos y exigencias, haber respondido la **Encuesta de Evaluación de la Docencia** del período anterior y tomar al menos el mínimo de créditos [RG-ART-042]. Excepcionalmente, el **Vicedecano** puede autorizar menos créditos si la oferta curricular resulta inferior por su situación personal y prerrequisitos, o si solo le restan las asignaturas finales de su carrera [RG-ART-042].",
         "Debe inscribir en las fechas del calendario cumpliendo prerrequisitos y al menos el mínimo de créditos de su carrera [RG-ART-042]."),
        # Held-out VAL
        ("val", "RG-ART-045",
         "¿Qué exige cursar una asignatura en el PLEV y qué efectos produce reprobarla sobre la situación curricular, becas y hoja de vida?",
         "Requiere ser alumno regular y aprobación del **Jefe de Carrera**, pudiendo cursarse **solo una asignatura** por PLEV [RG-ART-045]. Si se reprueba, **no afecta** la situación curricular ni los antecedentes para becas o préstamos, aunque **sí queda registrada** en la hoja curricular [RG-ART-045].",
         "En el PLEV se puede cursar una asignatura con autorización del Jefe de Carrera, y reprobarla no afecta la situación curricular del estudiante [RG-ART-045]."),
        ("val", "RG-ART-044",
         "¿Cómo reingresa alguien a la misma carrera y cuál es la excepción para conservar su historial académico previo?",
         "Quien reingresa a la misma carrera entra a Primer Año como alumno nuevo sin derecho a validar, revalidar, convalidar ni reconocer ramos; **no obstante**, si no incurrió en pérdida de carrera, puede solicitar dentro de los **30 primeros días** del primer semestre mantener su situación académica anterior [RG-ART-044].",
         "Quien decide reingresar a la misma carrera debe hacerlo a Primer Año como alumno nuevo sin poder reconocer asignaturas aprobadas [RG-ART-044]."),
        ("val", "RI-FI-ART-028",
         "Cuando un alumno de Ingeniería se reincorpora teniendo ya cumplida la Licenciatura en Ciencias de la Ingeniería, ¿qué pasa con esa Licenciatura y con las asignaturas posteriores?",
         "Al reincorporarse tras suspender estudios, **se le reconocerá la Licenciatura** ya cumplida al momento de suspender, y las asignaturas cursadas después de la Licenciatura se reconocerán por equivalencia con el Plan de Estudio vigente al reincorporarse [RI-FI-ART-028].",
         "Al reincorporarse en Ingeniería, se le reconocerá automáticamente la Licenciatura en Ciencias de la Ingeniería [RI-FI-ART-028]."),
        ("val", "RI-FI-ART-033",
         "¿Cómo se compone el Comité de Docencia y Asuntos Estudiantiles en Ingeniería, quién designa a sus miembros y cuánto tiempo duran?",
         "Lo preside la **Jefatura de Carrera** y lo integran **dos docentes** elegidos por el Consejo de Carrera de entre sus miembros y **un representante estudiantil** del Consejo de Carrera (con voz y voto, designado por el Centro de Alumnos) [RI-FI-ART-033]. Coincide con el inicio del Director de Departamento y sus integrantes duran **2 años** en sus funciones [RI-FI-ART-033].",
         "Está integrado por la Jefatura de Carrera, dos docentes y representantes estudiantiles del Consejo de Carrera por un periodo fijo [RI-FI-ART-033]."),
    ]
    pares: list[dict[str, Any]] = []
    for idx, (sp, uid, preg, ch_txt, rej_txt) in enumerate(fichas, 1):
        pares.append(
            _armar_par_dpo(
                f"DPO-COMP-{idx:02d}", sp, "dpo_completitud_reglas", buscador, preg,
                _msg_asistente(ch_txt), _msg_asistente(rej_txt), asegurar_ids=[uid],
            )
        )
    return pares


def _pares_fidelidad_pdfs_y_limites(buscador_base: Any) -> list[dict[str, Any]]:
    """Pares de fidelidad estricta: PDFs en caliente, no confundir reglamentos, ni respuestas incompletas/corchetes."""
    pack_tr = _crear_pack_pdf_sintetico(
        "syllabus_algoritmos.pdf",
        [
            "Syllabus Algoritmos Avanzados. Nota mínima de proyecto semestral: 4,8. Asistencia mínima a ayudantías: 75%.",
            "No hay eximición en el examen final para promedios inferiores a 5,2.",
        ],
    )
    pack_va = _crear_pack_pdf_sintetico(
        "protocolo_practica_biomateriales.pdf",
        [
            "Protocolo Práctica Biomateriales. Duración mínima: 320 horas cronológicas. Seguro escolar obligatorio antes del inicio.",
            "El informe final escrito requiere nota mínima 4,5 para aprobar.",
        ],
    )
    b_comb_tr = buscador_base.con_pdfs_usuario([pack_tr], incluir_corpus_base=True)
    b_solo_tr = buscador_base.con_pdfs_usuario([pack_tr], incluir_corpus_base=False)
    b_comb_va = buscador_base.con_pdfs_usuario([pack_va], incluir_corpus_base=True)

    id_tr1, id_tr2 = pack_tr["unidades"][0]["id"], pack_tr["unidades"][1]["id"]
    id_va1, id_va2 = pack_va["unidades"][0]["id"], pack_va["unidades"][1]["id"]

    pares: list[dict[str, Any]] = [
        _armar_par_dpo(
            "DPO-FID-01", "train", "dpo_fidelidad_y_formato", b_solo_tr,
            "Según el syllabus de Algoritmos que subí, ¿qué nota exige el proyecto y desde qué promedio hay eximición de examen?",
            _msg_asistente(f"El proyecto exige nota mínima **4,8** (con 75% de asistencia a ayudantías) [{id_tr1}] [syllabus_algoritmos.pdf p. 1], y no hay eximición del examen final para promedios inferiores a **5,2** [{id_tr2}] [syllabus_algoritmos.pdf p. 2]."),
            _msg_asistente(f"Según el Reglamento General, se aprueba con 4,0 y debes buscar el artículo correspondiente [{id_tr1}]."),
            asegurar_ids=[id_tr1, id_tr2], solo_pdfs=True, tiene_pdfs=True,
        ),
        _armar_par_dpo(
            "DPO-FID-02", "train", "dpo_fidelidad_y_formato", b_solo_tr,
            "¿El syllabus de Algoritmos cargado establece algún porcentaje de beca o matrícula?",
            _msg_asistente(f"No: los fragmentos cargados de `syllabus_algoritmos.pdf` no mencionan becas ni montos de matrícula; solo regulan nota mínima de proyecto, asistencia a ayudantías y eximición de examen [{id_tr1}] [{id_tr2}]."),
            _msg_asistente(f"Sí, exige mantener un promedio ponderado superior a 5,0 para becas de acuerdo con el syllabus [{id_tr1}]."),
            asegurar_ids=[id_tr1, id_tr2], solo_pdfs=True, tiene_pdfs=True,
        ),
        _armar_par_dpo(
            "DPO-FID-03", "train", "dpo_fidelidad_y_formato", b_comb_tr,
            "En el syllabus subido, ¿cuál es la nota mínima del proyecto semestral?",
            _msg_asistente(f"En tu syllabus cargado la nota mínima del proyecto semestral es **4,8** [{id_tr1}] [syllabus_algoritmos.pdf p. 1]."),
            _msg_asistente(f"[{id_tr1}]"),
            asegurar_ids=[id_tr1], tiene_pdfs=True,
        ),
        _armar_par_dpo(
            "DPO-FID-04", "train", "dpo_fidelidad_y_formato", buscador_base,
            "Estoy revisando una minuta que invoca el Artículo 52 del RI-FI de Ingeniería sobre representaciones; ¿existe realmente esa norma?",
            _msg_asistente("El Artículo 52 **no existe** en el Reglamento Interno de la Facultad de Ingeniería (`RI-FI`), pues su articulado oficial llega hasta el Artículo 35. No corresponde aplicarle el Artículo 52 del Reglamento General [RG-ART-052] como si perteneciera al `RI-FI`."),
            _msg_asistente("El Artículo 52 del RI-FI otorga facilidades académicas a los representantes estudiantiles [RG-ART-052]."),
            asegurar_ids=["RG-ART-052"],
            usar_alerta_inv=True,
        ),
        _armar_par_dpo(
            "DPO-FID-05", "train", "dpo_fidelidad_y_formato", buscador_base,
            "¿En qué documento oficial de UdeC se registran las siglas CON, REV, HOM y REC y qué efecto tienen en la carga académica?",
            _msg_asistente("En el Sistema de Administración Curricular (**SAC**) se registran con nota final y esas siglas (junto con VAL), y las convalidadas, revalidadas, homologadas o reconocidas **no cuentan como carga académica del semestre** [RG-ART-041]."),
            _msg_asistente("Se registran en el SAC según [RG-ART-041-b] y sí suman como carga académica regular del semestre."),
            asegurar_ids=["RG-ART-041"],
        ),
        _armar_par_dpo(
            "DPO-FID-06", "train", "dpo_fidelidad_y_formato", buscador_base,
            "¿A quién debe el Director de Departamento comunicar primero la carga docente asignada en una asignatura?",
            _msg_asistente("El Director de Departamento comunica la asignación de carga docente **a su Vicedecano**, quien a su vez informa al Vicedecano y al Jefe de Carrera de la Facultad solicitante [RG-ART-006]."),
            _msg_asistente("[RG-ART-006]"),
            asegurar_ids=["RG-ART-006"],
        ),
        _armar_par_dpo(
            "DPO-FID-07", "train", "dpo_fidelidad_y_formato", buscador_base,
            "Si un caso pendiente existía antes de entrar en vigencia el Reglamento General actual, ¿qué normativa se aplica para resolverlo?",
            _msg_asistente("Se aplican las normas vigentes al momento de su formulación u ocurrencia; **sin embargo**, se resuelve con el reglamento vigente **cuando su aplicación mejore la condición del alumno** [RG-TRANS-001]."),
            _msg_asistente("Se aplican obligatoriamente las normas antiguas en todos los casos, aunque el nuevo reglamento beneficie al estudiante [RG-TRANS-001]."),
            asegurar_ids=["RG-TRANS-001"],
        ),
        _armar_par_dpo(
            "DPO-FID-08", "train", "dpo_fidelidad_y_formato", buscador_base,
            "¿Cuándo se consideran legalmente conocidos por el estudiante los reglamentos internos y el Reglamento General de Docencia?",
            _msg_asistente("Al ser de dominio público en un sistema actualizado de información, **se consideran conocidos por el alumno al formalizar su matrícula** [RG-ART-058]."),
            _msg_asistente("Solo se consideran conocidos después de aprobar el primer semestre de la carrera [RG-ART-058]."),
            asegurar_ids=["RG-ART-058"],
        ),
        _armar_par_dpo(
            "DPO-FID-V01", "val", "dpo_fidelidad_y_formato", b_comb_va,
            "Según el protocolo de práctica de biomateriales subido, ¿cuántas horas dura la práctica y qué nota exige el informe final?",
            _msg_asistente(f"El protocolo exige una duración mínima de **320 horas cronológicas** con seguro escolar previo [{id_va1}] [protocolo_practica_biomateriales.pdf p. 1] y una nota mínima de **4,5** en el informe final escrito [{id_va2}] [protocolo_practica_biomateriales.pdf p. 2]."),
            _msg_asistente(f"Dura 320 horas cronológicas y el informe exige nota mínima 4,0 según la escala general [RG-ART-048] [{id_va1}]."),
            asegurar_ids=[id_va1, id_va2], tiene_pdfs=True,
        ),
        _armar_par_dpo(
            "DPO-FID-V02", "val", "dpo_fidelidad_y_formato", buscador_base,
            "¿Qué pasa si entra en conflicto el Reglamento General de Docencia de Pregrado con una norma de menor jerarquía?",
            _msg_asistente("Prevalecen siempre las normas del **Reglamento General de Docencia de Pregrado** sobre cualesquiera otras que no se concilien con ellas, sin importar de dónde provengan [RG-ART-060]."),
            _msg_asistente("Prevalece la norma específica del Reglamento Interno [RG-ART-060-a]."),
            asegurar_ids=["RG-ART-060"],
        ),
    ]
    return pares


def _pares_multiturno_contexto(buscador: Any) -> list[dict[str, Any]]:
    """Entrena conservación de restricciones e hilo conversacional en repreguntas cortas."""
    escenarios = [
        (
            "train",
            "RG-ART-043",
            [
                {"role": "user", "content": "¿Hasta cuándo puedo abandonar una asignatura semestral sin justificar motivo?"},
                {"role": "assistant", "content": "Tienes hasta **4 semanas** desde el inicio de clases (una sola vez por ramo y sin quedar bajo el mínimo de créditos) [RG-ART-043]."},
            ],
            "¿Y aplica igual si esa asignatura la inscribí en el PLEV?",
            "No: el Reglamento prohíbe expresamente abandonar asignaturas inscritas en el **PLEV** [RG-ART-043].",
            "Sí aplica igual: en el PLEV también tienes 4 semanas desde el inicio para abandonarla sin expresar motivos [RG-ART-043].",
        ),
        (
            "train",
            "RG-ART-033",
            [
                {"role": "user", "content": "Si suspendo mis estudios y luego me reincorporo, ¿a qué plan de estudios debo adscribirme?"},
                {"role": "assistant", "content": "Debes adscribirte al Plan de Estudio que se esté impartiendo al momento de reincorporarte [RG-ART-033]."},
            ],
            "¿Y si mi salida fue para hacer un intercambio académico estudiantil?",
            "En ese caso aplicas a la excepción expresa del artículo: los alumnos en **intercambio** se mantienen en su **mismo plan de estudio** [RG-ART-033].",
            "No hay excepciones por intercambio; igualmente debes pasar al Plan de Estudio vigente al regresar [RG-ART-033].",
        ),
        (
            "train",
            "RG-ART-042",
            [
                {"role": "user", "content": "¿Puedo inscribir asignaturas si olvidé contestar la Encuesta de Evaluación Docente del semestre anterior?"},
                {"role": "assistant", "content": "No directamente como regla general: para inscribir asignaturas se exige haber respondido la **Encuesta de Evaluación de la Docencia** del período lectivo anterior [RG-ART-042]."},
            ],
            "¿Y si solo me quedan por aprobar las últimas asignaturas para terminar mi carrera, debo igualmente tomar el mínimo de créditos?",
            "No estás obligado al mínimo general de créditos en ese caso: quien esté terminando sus estudios puede inscribir **sólo las asignaturas que le falte cursar** [RG-ART-042].",
            "Sí, debes inscribir siempre el mínimo completo de créditos aunque solo te falte una asignatura para egresar [RG-ART-042].",
        ),
        (
            "val",
            "RG-ART-020",
            [
                {"role": "user", "content": "¿Cómo solicito un régimen especial de asistencia si tengo una discapacidad debidamente acreditada?"},
                {"role": "assistant", "content": "Debes solicitarlo al momento de inscribir asignaturas ante el Vicedecano de tu Facultad, quien resuelve previa consulta a INCLUDEC [RG-ART-020]."},
            ],
            "¿Y si el impedimento de horario se debe a razones religiosas?",
            "Si decides darlo a conocer libremente por **razones religiosas**, debes acreditarlo al momento de inscribir la asignatura para que el Profesor Encargado lo considere al programar actividades [RG-ART-020].",
            "Para motivos religiosos el trámite no existe al inscribir; solo aplica a estudiantes con discapacidad vía INCLUDEC [RG-ART-020].",
        ),
    ]
    pares: list[dict[str, Any]] = []
    for idx, (sp, uid, hist, preg, ch_txt, rej_txt) in enumerate(escenarios, 1):
        pares.append(
            _armar_par_dpo(
                f"DPO-TURN-{idx:02d}",
                sp,
                "dpo_multiturno",
                buscador,
                preg,
                _msg_asistente(ch_txt),
                _msg_asistente(rej_txt),
                historial=hist,
                asegurar_ids=[uid],
            )
        )
    return pares


def validar_dataset_dpo(registros: list[dict[str, Any]]) -> dict[str, Any]:
    """Audita pares DPO verificando cero fugas en `chosen`, `rejected` y similitud contra las 95 preguntas."""
    p95 = cargar_preguntas_evaluacion_95()
    errores: list[str] = []
    por_split: dict[str, int] = {}
    por_cat: dict[str, int] = {}
    prompts_split: dict[str, set[str]] = {"train": set(), "val": set()}

    for r in registros:
        pid = str(r.get("id", "<sin-id>"))
        sp = str(r.get("split", "train"))
        cat = str(r.get("categoria", "desconocida"))
        por_split[sp] = por_split.get(sp, 0) + 1
        por_cat[cat] = por_cat.get(cat, 0) + 1

        prompt = r.get("prompt") or []
        chosen = r.get("chosen") or {}
        rejected = r.get("rejected") or {}

        # Validar formato, tool_calls, citas y no-fuga en la rama `chosen` reutilizando el auditor SFT
        errs_ch = validar_registro_sft(
            {"id": f"{pid}(chosen)", "messages": list(prompt) + [chosen]},
            preguntas_95=p95,
        )
        errores.extend(errs_ch)

        # Verificar también que `rejected` no filtre unidades bloqueadas
        blob_rej = json.dumps(rejected, ensure_ascii=False)
        fugas_rej = sorted(set(_UNIT_ID_RE.findall(blob_rej)) & BLOCKED_UNIT_IDS)
        if fugas_rej:
            errores.append(f"{pid}(rejected): fuga de unidades bloqueadas {fugas_rej}")
        if chosen == rejected:
            errores.append(f"{pid}: chosen y rejected son idénticos")

        for m in prompt:
            if m.get("role") == "user":
                q_limpia = str(m.get("content", "")).split("\n\n", 1)[0].strip().lower()
                if sp in prompts_split and q_limpia:
                    prompts_split[sp].add(q_limpia)
                    for p in p95:
                        sim = SequenceMatcher(None, q_limpia, p["pregunta"].strip().lower()).ratio()
                        if sim >= 0.72:
                            errores.append(f"{pid}: similitud {sim:.2f} con {p['dataset']}:{p['id']}")
                            break

    solape = sorted(prompts_split["train"] & prompts_split["val"])
    if solape:
        errores.append(f"Solape de preguntas entre train y val DPO: {len(solape)}")

    return {
        "total": len(registros),
        "ok": len(errores) == 0,
        "errores": errores,
        "por_split": por_split,
        "por_categoria": por_cat,
    }


def construir_pares_dpo() -> list[dict[str, Any]]:
    """Genera todos los pares DPO de entrenamiento y validación sobre corpus limpio."""
    with tempfile.TemporaryDirectory() as tmp:
        buscador_limpio = _crear_buscador_limpio(Path(tmp))
        pares: list[dict[str, Any]] = []
        pares.extend(_pares_eleccion_herramienta(buscador_limpio))
        pares.extend(_pares_desigualdades_post_tool(buscador_limpio))
        pares.extend(_pares_completitud_y_apelacion(buscador_limpio))
        pares.extend(_pares_fidelidad_pdfs_y_limites(buscador_limpio))
        pares.extend(_pares_multiturno_contexto(buscador_limpio))
    return pares


def guardar_dataset_dpo(salida_dir: Path = DEFAULT_FT_DATA_DIR) -> dict[str, Any]:
    """Construye, audita antifuga y guarda `dpo_train.jsonl`, `dpo_val.jsonl` y resumen."""
    pares = construir_pares_dpo()
    aud = validar_dataset_dpo(pares)
    if not aud["ok"]:
        raise ValueError(f"Auditoría antifuga DPO falló ({len(aud['errores'])} errores):\n" + "\n".join(aud["errores"][:10]))

    salida_dir = Path(salida_dir)
    salida_dir.mkdir(parents=True, exist_ok=True)
    tr = [p for p in pares if p["split"] == "train"]
    va = [p for p in pares if p["split"] == "val"]
    (salida_dir / "dpo_train.jsonl").write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in tr) + "\n", encoding="utf-8")
    (salida_dir / "dpo_val.jsonl").write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in va) + "\n", encoding="utf-8")

    resumen = {
        "total": len(pares),
        "train": len(tr),
        "val": len(va),
        "por_categoria": aud["por_categoria"],
        "antifuga_ok": True,
    }
    (salida_dir / "resumen_dpo.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resumen


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Genera pares DPO sin fugas para Qwen3-4B-Instruct-2507")
    parser.add_argument("--salida-dir", type=Path, default=DEFAULT_FT_DATA_DIR)
    args = parser.parse_args(argv)
    print(json.dumps(guardar_dataset_dpo(args.salida_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
