"""Generador determinista y libre de fugas del dataset SFT multi-turno para Qwen3-4B-Instruct."""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any

from ..asistente import SYSTEM_PROMPT, reescribir_consulta_con_historial
from ..buscador import BuscadorNormativa
from ..config import DEFAULT_CACHE_DIR, DEFAULT_CORPUS_PATH, DEFAULT_FRAGMENTOS_PATH
from ..herramientas import ejecutar_herramienta
from .antifuga import BLOCKED_UNIT_IDS, validar_dataset_completo

DEFAULT_FT_DATA_DIR = Path(__file__).resolve().parent / "datos"


def _system_prompt_para(solo_pdfs: bool = False, tiene_pdfs: bool = False) -> str:
    prompt = SYSTEM_PROMPT
    if solo_pdfs:
        prompt += (
            "\n5. MODO SOLO PDFs DEL USUARIO: La búsqueda opera únicamente sobre los PDFs cargados "
            "por el usuario (identificadores `[PDF-...]`). Responde basándote SOLO en esos documentos, "
            "cita `[PDF-...]` junto al nombre de archivo y página (`[archivo.pdf p. X]`), y si no hay "
            "PDFs cargados o el dato no figura en ellos, indícalo claramente sin afirmar reglas de UdeC que no estén en el contexto."
        )
    elif tiene_pdfs:
        prompt += (
            "\n5. PDFs DEL USUARIO TAMBIÉN INDEXADOS: Además de los reglamentos UdeC, hay PDFs subidos "
            "por el usuario indexados en el buscador (`[PDF-...]`). Si la evidencia contiene pasajes `[PDF-...]`, "
            "cítalos junto con su archivo y página (`[archivo.pdf p. X]`) y no los descartes."
        )
    return prompt


def _crear_pack_pdf_sintetico(nombre_archivo: str, paginas: list[str]) -> dict[str, Any]:
    """Construye un paquete PDF compatible con `BuscadorNormativa.con_pdfs_usuario` sin I/O PDF binario."""
    sha_hex = hashlib.sha256(f"{nombre_archivo}|{'|'.join(paginas)}".encode("utf-8")).hexdigest()
    base = re.sub(r"[^A-Za-z0-9]+", "", nombre_archivo.rsplit(".", 1)[0]).upper()[:10] or "DOC"
    slug = f"{base}{sha_hex[:4].upper()}"
    doc_id = f"PDF:{nombre_archivo}"
    unidades: list[dict[str, Any]] = []
    fragmentos: list[dict[str, Any]] = []
    for num_pag, cuerpo in enumerate(paginas, start=1):
        uid = f"PDF-{slug}-P{num_pag:02d}-01"
        texto_u = f"[{nombre_archivo}, pág. {num_pag}]\n{cuerpo.strip()}"
        unidades.append(
            {
                "id": uid,
                "parent_id": uid,
                "documento": doc_id,
                "archivo": nombre_archivo,
                "paginas": [num_pag],
                "texto": texto_u,
                "es_pdf_usuario": True,
            }
        )
        fragmentos.append(
            {
                "id": f"{uid}-F01",
                "unidad_id": uid,
                "parent_id": uid,
                "texto": texto_u,
                "texto_embedding": f"passage: [{uid} | {nombre_archivo}, PDF p. {num_pag}]\n{cuerpo.strip()}",
            }
        )
    return {
        "nombre_archivo": nombre_archivo,
        "documento": doc_id,
        "sha256": sha_hex,
        "paginas_con_texto": len(paginas),
        "unidades": unidades,
        "fragmentos": fragmentos,
    }


def _crear_buscador_limpio(tmp_dir: Path) -> BuscadorNormativa:
    """Crea un BuscadorNormativa filtrado estrictamente sin ninguna unidad bloqueada."""
    corpus = json.loads(DEFAULT_CORPUS_PATH.read_text(encoding="utf-8"))
    frags = json.loads(DEFAULT_FRAGMENTOS_PATH.read_text(encoding="utf-8"))

    unidades_limpias = [u for u in corpus.get("unidades", []) if u["id"] not in BLOCKED_UNIT_IDS]
    ids_limpios = {u["id"] for u in unidades_limpias}
    frags_limpios = [
        f
        for f in frags
        if (f.get("unidad_id") or f.get("parent_id")) in ids_limpios
    ]

    c_path = tmp_dir / "corpus_limpio.json"
    f_path = tmp_dir / "frags_limpios.json"
    c_path.write_text(json.dumps({"unidades": unidades_limpias}, ensure_ascii=False), encoding="utf-8")
    f_path.write_text(json.dumps(frags_limpios, ensure_ascii=False), encoding="utf-8")
    return BuscadorNormativa(corpus_path=c_path, fragmentos_path=f_path, cache_dir=tmp_dir, usar_embeddings=False)


def _construir_bloque_inicial(
    buscador: BuscadorNormativa,
    pregunta: str,
    asegurar_ids: list[str] | None = None,
    omitir_ids: set[str] | None = None,
    historial: list[dict[str, str]] | None = None,
) -> str:
    """Simula el bloque `Contexto inicial` real del orquestador manteniendo realismo y distractores."""
    consulta_busq = reescribir_consulta_con_historial(pregunta, historial)
    hits = buscador.buscar(
        consulta_busq,
        k=5,
        expandir_citas=False,
        top_p=0.85,
        top_k_min=1,
        top_p_temp=0.13,
        top_p_pool=10,
        modo_fusion="rrf",
        k_rrf=10,
        usar_descomposicion=True,
    )
    omitir = omitir_ids or set()
    elegidos: list[dict[str, Any]] = [h for h in hits if h["id"] not in omitir][:4]
    vistos = {h["id"] for h in elegidos}

    for uid in asegurar_ids or []:
        if uid not in vistos and uid not in omitir and uid in buscador.por_id:
            u = buscador.por_id[uid]
            elegidos.insert(0, {"id": u["id"], "texto": u["texto"]})
            vistos.add(uid)
    elegidos = elegidos[:5]
    if not elegidos:
        return ""

    ctx = "\n\n".join(f"[{h['id']}] {h['texto']}" for h in elegidos)
    enc = (
        "\n\nContexto inicial recuperado de tus PDFs subidos "
        "(si necesitas buscar otros pasajes, usa `buscar_reglamento` sin filtrar `documento`):\n"
        if getattr(buscador, "solo_pdfs", False)
        else "\n\nContexto normativo inicial recuperado automáticamente "
        "(si necesitas más artículos, calendario completo o cálculos, usa tus herramientas):\n"
    )
    return f"{enc}{ctx}"


def _construir_alerta_inexistente(buscador: BuscadorNormativa, pregunta: str) -> str:
    checks = buscador.verificar_articulos_mencionados(pregunta)
    inex = [c for c in checks if not c.get("existe")]
    if not inex:
        return ""
    lineas = [
        f"- El Artículo {c['numero']} NO existe en {c['doc']} "
        f"(el rango oficial de {c['doc']} llega hasta el Art. {c.get('max_articulo', 0)}). "
        f"No lo confundas con un artículo homónimo de otro reglamento."
        for c in inex
    ]
    return "\n\nVerificación determinista previa del inventario oficial (`existe_articulo`):\n" + "\n".join(lineas)


def _tc(nombre: str, args: dict[str, Any]) -> dict[str, Any]:
    return {"type": "function", "function": {"name": nombre, "arguments": args}}


def _ejecutar_secuencia_tools(
    buscador: BuscadorNormativa,
    llamadas: list[tuple[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Convierte llamadas `(nombre, args)` en turnos `(assistant tool_calls -> tool response)` reales."""
    turnos: list[dict[str, Any]] = []
    for nombre, args in llamadas:
        res = ejecutar_herramienta(nombre, args, buscador)
        turnos.append({"role": "assistant", "content": "", "tool_calls": [_tc(nombre, args)]})
        turnos.append({"role": "tool", "name": nombre, "content": json.dumps(res, ensure_ascii=False)})
    return turnos


def _armar_registro(
    rid: str,
    split: str,
    categoria: str,
    buscador: BuscadorNormativa,
    pregunta: str,
    respuesta_final: str,
    tools: list[tuple[str, dict[str, Any]]] | None = None,
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
    msgs: list[dict[str, Any]] = [
        {"role": "system", "content": _system_prompt_para(solo_pdfs=solo_pdfs, tiene_pdfs=tiene_pdfs)}
    ]
    for h in historial or []:
        msgs.append({"role": h["role"], "content": h["content"]})
    msgs.append({"role": "user", "content": f"{pregunta}{alerta}{bloque}"})
    if tools:
        msgs.extend(_ejecutar_secuencia_tools(buscador, tools))
    msgs.append({"role": "assistant", "content": respuesta_final})

    return {
        "id": rid,
        "split": split,
        "categoria": categoria,
        "solo_pdfs": solo_pdfs,
        "tiene_pdfs": tiene_pdfs,
        "messages": msgs,
    }


def _generar_bloque_calculo(buscador: BuscadorNormativa) -> list[dict[str, Any]]:
    """Escenarios numéricos con tool-calling obligatorio a `calcular`."""
    ejemplos: list[dict[str, Any]] = []

    # 1. Inicio Adelantado (RG-ART-038: > 5.7)
    casos_adelantado = [
        ("train", 5.8, True, "¿Cuál es la situación de un novato que sacó 5,8 en la Evaluación Diagnóstica de una asignatura fundamental y pregunta si puede optar al Inicio Adelantado?"),
        ("train", 5.7, False, "Si un alumno de nuevo ingreso obtiene exactamente 5,7 en la Evaluación Diagnóstica, ¿puede acceder al Inicio Adelantado?"),
        ("train", 5.4, False, "Un estudiante nuevo rindió la Evaluación Diagnóstica de cálculo y sacó 5,4. ¿Cumple el puntaje para Inicio Adelantado?"),
        ("train", 6.3, True, "En el Reglamento General, ¿habilita un 6,3 en la Evaluación Diagnóstica para rendir la evaluación de Inicio Adelantado?"),
        ("train", 5.65, False, "Si en dos pruebas diagnósticas promediables un novato obtuvo 5,5 y 5,8 (mitad cada una), ¿supera el umbral de Inicio Adelantado?"),
        ("train", 6.05, True, "Una estudiante promedió 5,9 y 6,2 en sus componentes diagnósticas ponderados por igual. ¿Alcanza el requisito de Inicio Adelantado?"),
    ]
    for idx, (sp, nota_val, cumple, preg) in enumerate(casos_adelantado, 1):
        if "5,5 y 5,8" in preg:
            expr = "(5.5 + 5.8) / 2"
            txt_calc = "El promedio es **(5.5 + 5.8) / 2 = 5,65**"
        elif "5,9 y 6,2" in preg:
            expr = "(5.9 + 6.2) / 2"
            txt_calc = "El promedio es **(5.9 + 6.2) / 2 = 6,05**"
        else:
            expr = f"{nota_val} > 5.7"
            txt_calc = f"La comparación `{nota_val} > 5,7` da **{'verdadero' if cumple else 'falso'}**"
        resp = (
            f"{'Sí' if cumple else 'No'}, {'cumple' if cumple else 'no cumple'} el umbral para el Inicio Adelantado según [RG-ART-038]. "
            f"{txt_calc}, y la norma exige un resultado **estrictamente superior a 5,7** en la Evaluación Diagnóstica asociada para rendir la evaluación específica sin cursar la asignatura [RG-ART-038]."
        )
        ejemplos.append(
            _armar_registro(
                f"FT-CALC-AD-{idx:02d}", sp, "tool_calcular", buscador, preg, resp,
                tools=[("calcular", {"expresion": expr})], asegurar_ids=["RG-ART-038"],
            )
        )

    # 2. Comisión de Evaluación (RG-ART-013: > 50% con nota inferior a 4.0)
    casos_comision = [
        ("train", 28, 50, True, "En una evaluación rindieron 50 alumnos y 28 obtuvieron nota inferior a 4,0. ¿Debe el Director de Departamento convocar a la Comisión de Evaluación?"),
        ("train", 25, 50, False, "De 50 estudiantes que rindieron un certamen, exactamente 25 sacaron nota bajo 4,0. ¿Se cumple la causal automática de convocatoria a la Comisión de Evaluación por porcentaje?"),
        ("train", 19, 34, True, "En una sección de 34 alumnos, 19 obtuvieron calificación menor a 4,0. ¿Corresponde convocar a la Comisión de Evaluación?"),
        ("train", 12, 30, False, "Si 12 de 30 alumnos reprobaron la prueba con nota inferior a 4,0, ¿se activa la regla del 50% en el Art. 13 del RG?"),
    ]
    for idx, (sp, reprob, total, supera, preg) in enumerate(casos_comision, 1):
        pct = round((reprob / total) * 100, 2)
        resp = (
            f"{'Sí' if supera else 'No'} se cumple la causal porcentual del Art. 13 del Reglamento General [RG-ART-013]. "
            f"El porcentaje con nota inferior a 4,0 es `{reprob} / {total} * 100 = {pct}%`, y la norma exige que **más del 50%** de quienes rinden obtenga nota inferior a 4,0 "
            f"{'para convocar a la Comisión de Evaluación y resolver informando al Vicedecano' if supera else '(50% exacto o menor no supera el 50%)'} [RG-ART-013]."
        )
        ejemplos.append(
            _armar_registro(
                f"FT-CALC-COM-{idx:02d}", sp, "tool_calcular", buscador, preg, resp,
                tools=[("calcular", {"expresion": f"({reprob} / {total}) * 100"})],
                asegurar_ids=["RG-ART-013"],
            )
        )

    # 3. Conceptos de Diploma de Título (RG-ART-048) -> reservado estrictamente para VAL!
    casos_diploma = [
        ("val", "0.6 * 4.8 + 0.4 * 5.6", 5.12, "Aprobado con Distinción", "Si un egresado tiene promedio ponderado 4,8 (60%) y nota 5,6 en su examen final (40%), ¿qué concepto le corresponde en su Diploma de Título según el Reglamento General?"),
        ("val", "(5.8 + 5.7 + 6.1) / 3", 5.8667, "Aprobado con Distinción Máxima", "Con tres calificaciones igualmente ponderadas de 5,8, 5,7 y 6,1 en su evaluación de grado terminal, ¿qué mención lleva su diploma?"),
        ("val", "0.7 * 4.5 + 0.3 * 5.2", 4.71, "Aprobado por Unanimidad", "Si el promedio de asignaturas vale 70% con nota 4,5 y la actividad final vale 30% con nota 5,2, ¿cuál es el concepto del Diploma de Título?"),
        ("val", "0.5 * 5.0 + 0.5 * 6.4", 5.7, "Aprobado con Distinción Máxima", "Un estudiante promedia 5,0 en la primera mitad y 6,4 en la segunda (50% y 50%). ¿Qué concepto obtiene en el Diploma según el RG?"),
    ]
    for idx, (sp, expr, val_num, concepto, preg) in enumerate(casos_diploma, 1):
        resp = (
            f"La nota obtenida es **{val_num}** (aproximada a un decimal), por lo que corresponde el concepto **\"{concepto}\"** según la escala del Artículo 48° del Reglamento General [RG-ART-048] "
            f"(4,0–4,9: Aprobado por Unanimidad; 5,0–5,6: Aprobado con Distinción; 5,7–7,0: Aprobado con Distinción Máxima)."
        )
        ejemplos.append(
            _armar_registro(
                f"FT-CALC-DIP-{idx:02d}", sp, "tool_calcular", buscador, preg, resp,
                tools=[("calcular", {"expresion": expr})],
                asegurar_ids=["RG-ART-048"],
            )
        )

    # 4. Ponderaciones y créditos con RI-FI-ART-015 / RG-ART-043
    casos_creditos = [
        ("train", "48 - 18", "RI-FI-ART-015", "Un estudiante convalidó 18 créditos al ingresar directamente a segundo año y en su nuevo avance completó 48 créditos acumulados totales. ¿Cuántos créditos reales cursados se le contabilizan para el Art. 15 del RI-FI?"),
        ("train", "20 - 6", "RG-ART-043", "Tengo inscritos 20 créditos y quiero abandonar una asignatura de 6 créditos dentro del plazo de 4 semanas. Si el mínimo de mi carrera fuera 15 créditos, ¿quedarían suficientes créditos?"),
        ("train", "60 * 0.6", "RG-ART-010", "Si un Consejo de Carrera tiene 60 miembros en un experimento hipotético y se exige 60% de asistencia para sesionar, ¿cuántos miembros como mínimo se requieren?"),
        ("train", "25 * 0.6", "RG-ART-010", "En un Consejo de Carrera integrado por 25 personas, ¿cuántos integrantes representan exactamente el quórum del 60% exigido para sesionar?"),
    ]
    for idx, (sp, expr, uid, preg) in enumerate(casos_creditos, 1):
        res_c = ejecutar_herramienta("calcular", {"expresion": expr}, buscador)["resultado"]
        if uid == "RI-FI-ART-015":
            resp = (
                f"Se le contabilizan **{res_c} créditos** (`48 - 18 = {res_c}`), porque el Artículo 15° del RI-FI establece que los créditos revalidados, convalidados o reconocidos **no se contabilizan** para verificar la exigencia del nivel al que ingresa [RI-FI-ART-015]."
            )
        elif uid == "RG-ART-043":
            resp = (
                f"Al abandonar la asignatura de 6 créditos quedarías con **{res_c} créditos** (`20 - 6 = {res_c}`), lo cual es inferior a un mínimo de 15 créditos. "
                f"Según [RG-ART-043], el abandono dentro de las cuatro semanas desde el inicio de clases solo procede si no quedas con un número de créditos inferior al mínimo establecido."
            )
        else:
            resp = (
                f"El 60% exigido equivale a **{res_c} integrantes** (`{expr} = {res_c}`), necesario tanto para el quórum de sesión como para solicitar reuniones extraordinarias del Consejo de Carrera [RG-ART-010]."
            )
        ejemplos.append(
            _armar_registro(
                f"FT-CALC-VAR-{idx:02d}", sp, "tool_calcular", buscador, preg, resp,
                tools=[("calcular", {"expresion": expr})],
                asegurar_ids=[uid],
            )
        )

    return ejemplos


def _generar_bloque_calendario(buscador: BuscadorNormativa) -> list[dict[str, Any]]:
    """Escenarios de fechas limpias del Calendario 2026 con `dias_entre` y `ver_calendario`."""
    ejemplos: list[dict[str, Any]] = []

    casos_dias = [
        # (split, omitir_cal, usar_ver_cal, fi, ff, inclusivo, cite_id, pregunta, explicacion)
        ("train", False, False, "2026-06-30", "2026-07-05", True, "CAL-2026-S1-14",
         "¿Cuántos días corridos duran las vacaciones de invierno 2026 considerando del 30 de junio al 05 de julio inclusive?",
         "Las vacaciones de invierno 2026 duran **6 días corridos** (del 30 de junio al 05 de julio inclusive) [CAL-2026-S1-14]."),
        ("train", True, True, "2026-06-30", "2026-07-05", True, "CAL-2026-S1-14",
         "Según el Calendario Académico 2026, ¿cuántos días totales abarcan las vacaciones de invierno en el primer semestre?",
         "Según el Calendario 2026, las vacaciones de invierno van del 30 de junio al 05 de julio, lo que suma **6 días corridos inclusive** [CAL-2026-S1-14]."),
        ("train", False, False, "2026-03-02", "2026-03-06", True, "CAL-2026-S1-01",
         "¿Cuántos días dura inclusive la semana de Vinculación a la Vida Universitaria del 02 al 06 de marzo de 2026?",
         "La semana de Vinculación a la Vida Universitaria del 02 al 06 de marzo dura **5 días corridos inclusive** [CAL-2026-S1-01]."),
        ("train", False, False, "2026-07-10", "2026-07-24", False, "CAL-2026-S1-04",
         "¿Cuántos días transcurren entre el término de clases semestrales (10 de julio) y el término de clases anuales (24 de julio) en el primer semestre 2026?",
         "Entre el 10 de julio [CAL-2026-S1-04] y el 24 de julio [CAL-2026-S1-05] transcurren **14 días corridos**."),
        ("train", False, False, "2026-05-01", "2026-05-21", False, "CAL-2026-S1-10",
         "En el primer semestre 2026, ¿cuántos días hay entre el feriado del 01 de mayo y el feriado del 21 de mayo?",
         "Entre el 01 de mayo [CAL-2026-S1-10] y el 21 de mayo [CAL-2026-S1-11] transcurren **20 días corridos**."),
        ("train", False, False, "2026-04-03", "2026-05-01", False, "CAL-2026-S1-09",
         "¿Cuántos días separan el feriado nacional del viernes 03 de abril del feriado del viernes 01 de mayo en 2026?",
         "Entre el 03 de abril [CAL-2026-S1-09] y el 01 de mayo [CAL-2026-S1-10] transcurren **28 días corridos**."),
        ("train", True, True, "2026-06-29", "2026-07-16", False, "CAL-2026-S1-12",
         "¿Cuántos días pasan entre el feriado de junio y el feriado de julio en el primer semestre 2026?",
         "El feriado de junio es el 29 de junio [CAL-2026-S1-12] y el de julio es el 16 de julio [CAL-2026-S1-13], por lo que transcurren **17 días corridos** entre ambos."),
        ("train", False, False, "2026-08-20", "2026-12-08", False, "CAL-2026-S2-08",
         "¿Cuántos días transcurren desde el feriado nacional del 20 de agosto hasta el feriado nacional del 08 de diciembre en el segundo semestre 2026?",
         "Entre el 20 de agosto [CAL-2026-S2-08] y el 08 de diciembre [CAL-2026-S2-11] transcurren **110 días corridos**."),
        # Held-out en VAL (S1-06 y S2-10 solo aparecen aquí)
        ("val", False, False, "2026-07-13", "2026-07-24", True, "CAL-2026-S1-06",
         "¿Cuántos días corridos inclusive duran las Evaluaciones de Recuperación del primer semestre 2026 (del 13 al 24 de julio)?",
         "Las Evaluaciones de Recuperación del primer semestre 2026 (del 13 al 24 de julio) duran **12 días corridos inclusive** [CAL-2026-S1-06]."),
        ("val", True, True, "2026-08-20", "2026-10-12", False, "CAL-2026-S2-10",
         "¿Cuántos días hay entre el feriado de agosto y el feriado de octubre en el calendario del segundo semestre 2026?",
         "Entre el feriado del 20 de agosto [CAL-2026-S2-08] y el del lunes 12 de octubre [CAL-2026-S2-10] transcurren **53 días corridos**."),
        ("val", False, False, "2026-10-12", "2026-12-08", False, "CAL-2026-S2-10",
         "En el segundo semestre 2026, ¿cuántos días separan el feriado del 12 de octubre del feriado del 08 de diciembre?",
         "Entre el 12 de octubre [CAL-2026-S2-10] y el 08 de diciembre [CAL-2026-S2-11] transcurren **57 días corridos**."),
    ]
    for idx, (sp, omitir_cal, usa_ver, fi, ff, inc, cid, preg, resp) in enumerate(casos_dias, 1):
        llamadas: list[tuple[str, dict[str, Any]]] = []
        if usa_ver:
            sem = "1" if "S1" in cid else "2"
            llamadas.append(("ver_calendario", {"semestre": sem}))
        llamadas.append(("dias_entre", {"fecha_inicio": fi, "fecha_fin": ff, "inclusivo": inc}))
        omitir = {c for c in buscador.por_id if c.startswith("CAL-")} if omitir_cal else None
        ejemplos.append(
            _armar_registro(
                f"FT-CAL-{idx:02d}", sp, "tool_calendario_dias", buscador, preg, resp,
                tools=llamadas, asegurar_ids=None if omitir_cal else [cid], omitir_ids=omitir,
            )
        )
    return ejemplos


def _generar_bloque_multirequisito(buscador: BuscadorNormativa) -> list[dict[str, Any]]:
    """Artículos densos en requisitos, plazos, órganos, apelaciones y excepciones."""
    fichas = [
        # (id_tag, split, unit_id, necesita_leer_art, pregunta, respuesta)
        ("MR-01", "train", "RI-FI-ART-007", False,
         "¿Cuáles son las cuatro prioridades exactas de inscripción de asignaturas en Ingeniería según el Artículo 7 del RI-FI?",
         "Según [RI-FI-ART-007], siempre que cumplan los requisitos de cada asignatura y en las fechas del calendario anual, las prioridades en orden son:\n"
         "a) Las asignaturas atrasadas respecto de su nivel de avance en el Plan de Estudio.\n"
         "b) Las asignaturas obligatorias reprobadas anteriormente y aún no aprobadas.\n"
         "c) Las asignaturas correspondientes a su nivel de avance en el Plan de Estudio.\n"
         "d) Las asignaturas que desee adelantar respecto de su nivel de avance."),
        ("MR-02", "train", "RI-FI-ART-024", False,
         "¿Qué condiciones y documentos debe presentar un estudiante de intercambio para validar asignaturas aprobadas en otra universidad, ante quién lo hace y cómo se registran?",
         "De acuerdo con [RI-FI-ART-024], el estudiante en intercambio que aprobó asignaturas bajo convenios de movilidad suscritos por la UdeC debe:\n"
         "- Presentar ante el **Vicedecano** el **programa de la asignatura** y la **calificación obtenida**, ambos debidamente certificados.\n"
         "- La nota validada se incorpora al **SAC** en la Escala Oficial de la Universidad de Concepción y la asignatura se reconoce como carga académica en el semestre en que fue cursada."),
        ("MR-03", "train", "RG-ART-025", False,
         "¿Cuáles son todos los plazos del Artículo 25 RG para conocer calificaciones, revisar evaluaciones, conservar pruebas y apelar si persiste el desacuerdo, y quién decide la apelación?",
         "Según [RG-ART-025], los plazos y el procedimiento de apelación son:\n"
         "1. El profesor debe entregar calificaciones y pautas en un máximo de **10 días hábiles** (ampliable por el Vicedecano por razones justificadas) y conservar las evaluaciones escritas al menos **30 días hábiles** tras el periodo académico.\n"
         "2. El alumno tiene **5 días hábiles** para revisar la evaluación y aclarar dudas ante el profesor.\n"
         "3. Si persiste desacuerdo, puede pedir una nueva revisión por escrito y fundamentada ante el **Vicedecano** dentro de **5 días hábiles** desde la revisión con el profesor.\n"
         "4. Si el Vicedecano estima fundada la solicitud, nombra una **Comisión ad hoc**, la que debe resolver en **10 días corridos** desde la reclamación; su decisión es **inapelable** y se comunica personalmente dejando constancia con la firma del alumno."),
        ("MR-04", "train", "RG-ART-054", True,
         "¿Qué requisitos exige el Artículo 54 RG para cambiar de carrera, qué excepción rige dentro de la misma Facultad, dónde se presenta la solicitud y quién integra la Comisión que resuelve?",
         "Según [RG-ART-054]:\n"
         "- **Requisitos:** a) ser alumno regular conservando el derecho a continuar estudios en la carrera de origen; b) tener al menos el promedio mínimo exigido por el Reglamento Interno de la Facultad de destino (excepción: si el cambio es dentro de una misma Facultad, su Reglamento Interno puede fijar promedios o puntajes distintos).\n"
         "- **Recepción y cupos:** las Facultades fijan cupos anuales (mínimo uno en primer semestre) y la solicitud documentada se presenta en **UDARAE** dentro del periodo fijado por la Dirección de Docencia.\n"
         "- **Resolución:** decide una Comisión integrada por el **Director de Docencia**, el **Decano de la Facultad** y el **Jefe de Carrera**, debe ser sancionada por el **Rector** y registrada en el **SAC** por UDARAE."),
        ("MR-05", "train", "RG-ART-052", False,
         "¿A quiénes otorga facilidades académicas el Artículo 52 del RG y qué límite mantiene igual para aprobar?",
         "De acuerdo con [RG-ART-052], el **Vicedecano** respectivo otorgará facilidades flexibilizando cuando sea posible los requisitos académicos de clases teóricas y actividades prácticas a:\n"
         "- Presidentes de Centros de Alumnos.\n"
         "- Presidentes, Secretarios y Tesoreros de las Federaciones de Estudiantes de Concepción, Chillán y Los Ángeles.\n"
         "- Alumnos que participen en actividades extraprogramáticas en representación oficial de la UdeC.\n"
         "**Límite obligatorio:** no obstante estas facilidades, deberán cumplir íntegramente con los requisitos para aprobar las asignaturas."),
        ("MR-06", "train", "RG-ART-037", False,
         "¿Qué diferencia hay entre revalidación y convalidación en el Artículo 37 RG, qué documentos exige la convalidación y en qué plazo resuelve el Vicedecano?",
         "Según [RG-ART-037]:\n"
         "- **Revalidación:** aplica a una misma asignatura aprobada en otro plan de estudio de otra carrera dentro de la UdeC.\n"
         "- **Convalidación:** aplica a una asignatura del plan por otra equivalente aprobada en esta u otra institución de educación superior; exige adjuntar certificado completo de calificaciones y programas debidamente acreditados (salvo asignaturas aprobadas en la UdeC).\n"
         "- **Plazo y autoridad:** el **Vicedecano**, previo informe del Departamento a cargo de la asignatura, resuelve dentro de **15 días** e informa al alumno y a su Facultad."),
        ("MR-07", "train", "RG-ART-042", False,
         "¿Cuáles son las condiciones obligatorias y posibles excepciones para inscribir asignaturas según el Artículo 42 del Reglamento General?",
         "De acuerdo con [RG-ART-042], para inscribir asignaturas:\n"
         "1. Se realiza en las fechas del Calendario (en alumnos nuevos forma parte de la matrícula); el **Vicedecano** puede autorizar modificaciones o inscripciones fuera de plazo solo en casos justificados y excepcionales.\n"
         "2. Debe inscribirse al menos el mínimo de créditos fijado por la Facultad, salvo autorización del Vicedecano por oferta menor de créditos o si al alumno solo le faltan las asignaturas finales de su carrera.\n"
         "3. Debe cumplir prerrequisitos y exigencias (si no, la inscripción queda sin efecto), haber respondido la **Encuesta de Evaluación de la Docencia** del periodo anterior y no tener choque de horarios en actividades obligatorias."),
        ("MR-08", "train", "RG-ART-043", False,
         "¿Cuál es el plazo para hacer abandono de asignaturas sin expresar motivo y qué dos restricciones prohíben o limitan ese derecho?",
         "Según [RG-ART-043], el estudiante tiene **4 semanas** desde el inicio de clases del calendario para abandonar asignaturas semestrales o anuales sin especificar motivos (en cursos más cortos el plazo lo fija la Facultad). Restricciones:\n"
         "- Solo puede usarse **una vez** en cada asignatura y sin quedar por debajo del mínimo de créditos establecido.\n"
         "- **No procede** el abandono respecto de asignaturas inscritas en el **PLEV**."),
        ("MR-09", "train", "RG-ART-032", True,
         "Si un estudiante tiene una condición de salud incompatible con la carrera, ¿quién toma la decisión de suspenderle estudios y a quiénes debe informar?",
         "De acuerdo con [RG-ART-032], previo informe de la Dirección de Servicios Estudiantiles (o su unidad equivalente en Chillán o Los Ángeles), la suspensión corresponde al **Decano** mediante resolución fundada, quien deberá informar al **Vicerrector** y a **UDARAE** para su registro en el SAC."),
        ("MR-10", "train", "RG-ART-027", False,
         "¿Cómo se genera el Acta de Notas y qué se necesita para modificarla después de emitida?",
         "Según [RG-ART-027], el Profesor Encargado graba las Notas Finales (incluyendo Recuperación si aplica) mediante INFODA y el ejemplar impreso lo firman la Comisión de Evaluación y el Director de Departamento (o el Vicedecano si no depende de un Departamento), archivándose en Secretaría Académica.\n"
         "Para modificar un Acta de Notas se requiere **visto bueno del Vicedecano**, firma de un Acta de Modificación por la Comisión y el Director de Departamento, e ingreso al SAC por Secretaría Académica a más tardar **antes del término del semestre siguiente** al evaluado."),
        # Held-out en VAL (artículos nunca vistos en TRAIN)
        ("MR-V01", "val", "RG-ART-045", False,
         "¿Qué condiciones, límite de asignaturas y efecto sobre becas tiene reprobar un curso en el PLEV según el Artículo 45 RG?",
         "Según [RG-ART-045], el **PLEV** es opcional, permite cursar **solo una asignatura por periodo**, requiere ser alumno regular y contar con aprobación del **Jefe de Carrera**.\n"
         "Si reprueba la asignatura en el PLEV, **no afecta** la situación curricular del alumno ni sus antecedentes para becas o préstamos, aunque **sí queda registrada** en su hoja curricular."),
        ("MR-V02", "val", "RG-ART-044", True,
         "¿En qué condiciones reingresa un estudiante a su misma carrera y cuándo puede solicitar conservar su situación académica previa?",
         "Según [RG-ART-044], quien reingresa a la misma carrera entra a Primer Año como alumno nuevo, sujeto a las exigencias vigentes y sin derecho a validar, revalidar, convalidar ni reconocer asignaturas previas.\n"
         "**Excepción:** si el estudiante no incurrió en pérdida de carrera, puede solicitar dentro de los **30 primeros días** del primer semestre mantener su situación académica anterior."),
        ("MR-V03", "val", "RI-FI-ART-028", False,
         "Si un estudiante de Ingeniería se reincorpora tras suspender estudios habiendo cumplido ya los requisitos de la Licenciatura en Ciencias de la Ingeniería, ¿cómo se le reconocen esa Licenciatura y los ramos posteriores?",
         "Según [RI-FI-ART-028], al estudiante que se reincorpora y ya había cumplido los requisitos de la Licenciatura en Ciencias de la Ingeniería al suspender, **se le reconocerá dicha Licenciatura**. Además, las asignaturas aprobadas con posterioridad a la Licenciatura se reconocerán según su equivalencia con el Plan de Estudio vigente al momento de reincorporarse."),
        ("MR-V04", "val", "RI-FI-ART-033", False,
         "¿Quiénes integran el Comité de Docencia y Asuntos Estudiantiles en Ingeniería, cuánto duran en el cargo y cuáles son sus atribuciones?",
         "Según [RI-FI-ART-033], el Comité de Docencia y Asuntos Estudiantiles se integra por la **Jefatura de Carrera** (quien lo preside), **dos docentes** elegidos por el Consejo de Carrera entre sus miembros y **un representante estudiantil** del Consejo de Carrera con derecho a voz y voto (designado por el Centro de Alumnos).\n"
         "Sus integrantes duran **2 años** (coincidiendo con el periodo del Director de Departamento) y el Comité resuelve todos los asuntos que afectan al alumno en su vida académica y sus solicitudes de desempeño o situación académica."),
        ("MR-V05", "val", "RG-ART-055", True,
         "¿Qué requisitos y órganos intervienen cuando un estudiante UdeC postula a ingresar a otra carrera según el Art. 55 RG?",
         "De acuerdo con [RG-ART-055], debe: a) ser alumno regular y conservar derecho a continuar estudios en su carrera de origen; b) cumplir el promedio mínimo fijado en el Reglamento Interno de la Facultad de destino dentro de los cupos anuales.\n"
         "UDARAE recepciona solo solicitudes completas en el plazo fijado por Dirección de Docencia; resuelve una Comisión integrada por el **Director de Docencia**, el **Decano** y el **Jefe de Carrera**, con sanción del **Rector** y registro en el SAC por UDARAE."),
    ]

    ejemplos: list[dict[str, Any]] = []
    for fid, sp, uid, usar_leer, preg, resp in fichas:
        doc_short = "RI-FI" if uid.startswith("RI-FI") else "RG"
        num_art = int(uid.split("-ART-")[-1])
        tools = [("leer_articulo", {"doc": doc_short, "numero": num_art})] if usar_leer else None
        omitir = {uid} if usar_leer else None
        aseg = None if usar_leer else [uid]
        ejemplos.append(
            _armar_registro(
                f"FT-{fid}", sp, "multi_requisito", buscador, preg, resp,
                tools=tools, asegurar_ids=aseg, omitir_ids=omitir,
            )
        )
    return ejemplos


def _generar_bloque_pdfs(buscador_base: BuscadorNormativa) -> list[dict[str, Any]]:
    """Consultas sobre PDFs propios en caliente (modo solo-PDF, combinado y abstención en PDF)."""
    packs_train = [
        _crear_pack_pdf_sintetico(
            "manual_laboratorio_redes.pdf",
            [
                "Laboratorio de Redes de Computadores (FI-UdeC). Asistencia mínima obligatoria: 90% a sesiones prácticas. Dos inasistencias justificadas requieren recuperación en semana 16.",
                "Ponderación de notas: informes de laboratorio 55%, proyecto final 30%, controles de entrada 15%. Nota mínima de aprobación de informes: 4,2.",
            ],
        ),
        _crear_pack_pdf_sintetico(
            "instructivo_tesis_magister.pdf",
            [
                "Instructivo Interno de Tesis. Plazo máximo de entrega del borrador al comité revisor: 15 días hábiles antes del examen de grado. Se permiten hasta 2 co-guías externos.",
                "Formato exigido: documento en PDF con normas IEEE, extensión entre 45 y 90 páginas sin contar anexos.",
            ],
        ),
        _crear_pack_pdf_sintetico(
            "syllabus_estructuras_datos.pdf",
            [
                "Syllabus Estructuras de Datos 2026. Evaluaciones: 3 certámenes (25% cada uno) y 2 tareas de programación en C++ (12,5% cada una).",
                "No existe eximición de evaluaciones recuperativas para quienes promedien menos de 4,0 en los certámenes. Uso de herramientas de IA permitido solo si se declara en el README.",
            ],
        ),
    ]
    packs_val = [
        _crear_pack_pdf_sintetico(
            "protocolo_practica_biomateriales.pdf",
            [
                "Protocolo de Práctica Industrial Biomateriales. Duración mínima: 320 horas cronológicas en empresa supervisada. Seguro escolar obligatorio antes del primer día.",
                "El informe final del estudiante se evalúa con nota 1 a 7 y debe obtener al menos 4,5 para aprobar la etapa escrita, además de evaluación favorable del supervisor externo.",
            ],
        ),
        _crear_pack_pdf_sintetico(
            "normas_residencia_estudiantil.pdf",
            [
                "Reglamento Residencia Universitaria. Horario de silencio nocturno de domingo a jueves: 23:00 a 07:00 hrs. Visitas registradas hasta las 22:00.",
            ],
        ),
    ]

    busc_solo_tr = buscador_base.con_pdfs_usuario(packs_train, incluir_corpus_base=False)
    busc_comb_tr = buscador_base.con_pdfs_usuario(packs_train, incluir_corpus_base=True)
    busc_solo_va = buscador_base.con_pdfs_usuario(packs_val, incluir_corpus_base=False)
    busc_comb_va = buscador_base.con_pdfs_usuario(packs_val, incluir_corpus_base=True)

    id_redes_1 = packs_train[0]["unidades"][0]["id"]
    id_redes_2 = packs_train[0]["unidades"][1]["id"]
    id_tesis_1 = packs_train[1]["unidades"][0]["id"]
    id_syl_1 = packs_train[2]["unidades"][0]["id"]
    id_syl_2 = packs_train[2]["unidades"][1]["id"]
    id_bio_1 = packs_val[0]["unidades"][0]["id"]
    id_bio_2 = packs_val[0]["unidades"][1]["id"]
    id_res_1 = packs_val[1]["unidades"][0]["id"]

    specs = [
        ("FT-PDF-01", "train", True, False, busc_solo_tr, [id_redes_1], None,
         "Según el manual de laboratorio de redes que subí, ¿cuál es la asistencia mínima exigida?",
         f"El manual exige una asistencia mínima obligatoria del **90%** a sesiones prácticas; además, dos inasistencias justificadas requieren recuperación en semana 16 [{id_redes_1}] [manual_laboratorio_redes.pdf p. 1].",
         None),
        ("FT-PDF-02", "train", True, False, busc_solo_tr, [id_redes_2], None,
         "¿Cómo se ponderan las notas en el manual de redes y cuál es la nota mínima de informes?",
         f"La ponderación del laboratorio de redes es: informes **55%**, proyecto final **30%** y controles de entrada **15%**, con nota mínima de **4,2** para aprobar los informes [{id_redes_2}] [manual_laboratorio_redes.pdf p. 2].",
         [("calcular", {"expresion": "55 + 30 + 15"})]),
        ("FT-PDF-03", "train", True, False, busc_solo_tr, None, {id_tesis_1},
         "En el instructivo de tesis que cargué, ¿con cuántos días de anticipación se entrega el borrador al comité y cuántos co-guías permite?",
         f"Debe entregarse con al menos **15 días hábiles** de anticipación antes del examen de grado, y se permiten hasta **2 co-guías externos** [{id_tesis_1}] [instructivo_tesis_magister.pdf p. 1].",
         [("buscar_reglamento", {"consulta": "plazo borrador comite co-guias tesis"})]),
        ("FT-PDF-04", "train", False, True, busc_comb_tr, [id_syl_2], None,
         "Comparando mi syllabus de Estructuras de Datos con el Reglamento General, ¿quién define las formas de evaluación de la asignatura y qué regla fija el syllabus para recuperativas?",
         f"Según el Reglamento General, el Profesor Encargado comunica al inicio el programa, syllabus y formas de evaluación oficiales [RG-ART-019]. En tu syllabus específico se fija que **no hay eximición de evaluaciones recuperativas** si el promedio en certámenes es menor a 4,0, y el uso de IA debe declararse en el README [{id_syl_2}] [syllabus_estructuras_datos.pdf p. 2].",
         None),
        ("FT-PDF-05", "train", True, False, busc_solo_tr, [id_syl_1], None,
         "Si saqué 5,0, 4,6 y 5,4 en los 3 certámenes y 6,0 y 6,2 en las 2 tareas de Estructuras de Datos, ¿cuál es mi nota final según el syllabus?",
         f"Con 25% por cada certamen y 12,5% por cada tarea [{id_syl_1}] [syllabus_estructuras_datos.pdf p. 1], tu nota final ponderada es **5,275**.",
         [("calcular", {"expresion": "0.25 * (5.0 + 4.6 + 5.4) + 0.125 * (6.0 + 6.2)"})]),
        ("FT-PDF-06", "train", True, False, busc_solo_tr, [id_redes_1, id_redes_2], None,
         "¿Qué dice el manual de laboratorio de redes sobre el puntaje mínimo PSU o de ingreso PAES?",
         f"El manual de laboratorio de redes cargado no menciona ningún puntaje PSU ni PAES de ingreso; únicamente regula asistencia (90%), recuperaciones y ponderación de notas [{id_redes_1}] [manual_laboratorio_redes.pdf p. 1] [{id_redes_2}] [manual_laboratorio_redes.pdf p. 2].",
         None),
        # Held-out en VAL
        ("FT-PDF-V01", "val", True, False, busc_solo_va, [id_bio_1, id_bio_2], None,
         "Según el protocolo de práctica de biomateriales subido, ¿cuántas horas dura la práctica y qué nota mínima exige el informe final?",
         f"El protocolo exige una duración mínima de **320 horas cronológicas** en empresa supervisada con seguro escolar previo [{id_bio_1}] [protocolo_practica_biomateriales.pdf p. 1], y una nota mínima de **4,5** en el informe final escrito además de evaluación favorable del supervisor [{id_bio_2}] [protocolo_practica_biomateriales.pdf p. 2].",
         None),
        ("FT-PDF-V02", "val", False, True, busc_comb_va, [id_res_1], None,
         "En el reglamento de residencia subido, ¿desde qué hora rige el silencio nocturno de domingo a jueves?",
         f"En tu documento cargado se establece horario de silencio nocturno de **23:00 a 07:00 hrs** de domingo a jueves y visitas registradas hasta las 22:00 [{id_res_1}] [normas_residencia_estudiantil.pdf p. 1].",
         None),
    ]

    ejemplos: list[dict[str, Any]] = []
    for rid, sp, solo_p, comb_p, b_obj, aseg, omit, preg, resp, tools in specs:
        ejemplos.append(
            _armar_registro(
                rid, sp, "pdfs_en_caliente", b_obj, preg, resp,
                tools=tools, asegurar_ids=aseg, omitir_ids=omit,
                solo_pdfs=solo_p, tiene_pdfs=(solo_p or comb_p),
            )
        )
    return ejemplos


def _generar_bloque_multiturno(buscador: BuscadorNormativa) -> list[dict[str, Any]]:
    """Seguimientos conversacionales cortos (`historial`) manteniendo contexto y citas completas."""
    casos = [
        ("train", "RG-ART-033",
         [{"role": "user", "content": "¿Cuánto dura como máximo una suspensión de estudios en la UdeC?"},
          {"role": "assistant", "content": "La suspensión de estudios puede extenderse por un máximo de tres años calendario [RG-ART-033]."}],
         "¿Y si no solicito mi reincorporación dentro de ese plazo? ¿Qué plan de estudios rige cuando vuelvo?",
         "Si no solicitas tu reincorporación dentro del plazo máximo de tres años calendario, **pierdes la calidad de alumno de pregrado de la UdeC** [RG-ART-033]. Al reincorporarte deberás adscribirte al Plan de Estudio vigente en esa fecha, salvo si eres alumno en intercambio (en cuyo caso mantienes tu mismo plan) [RG-ART-033].",
         None),
        ("train", "RG-ART-025",
         [{"role": "user", "content": "¿Cuántos días tiene el profesor para entregar calificaciones y pautas?"},
          {"role": "assistant", "content": "Tiene un plazo máximo de diez días hábiles, ampliable por el Vicedecano por razones justificadas [RG-ART-025]."}],
         "¿Y si después de revisar con el profesor sigo en desacuerdo?",
         "Puedes solicitar por escrito y de manera fundamentada una nueva revisión ante el **Vicedecano** dentro de un plazo máximo de **5 días hábiles** contados desde la revisión con el profesor [RG-ART-025]. Si la estima fundada, nombrará una Comisión ad hoc que resolverá de forma inapelable en 10 días corridos [RG-ART-025].",
         None),
        ("train", "RG-ART-042",
         [{"role": "user", "content": "¿Es obligatorio contestar la Encuesta Docente antes de inscribir ramos?"},
          {"role": "assistant", "content": "Sí, para inscribir asignaturas el alumno debe haber respondido la Encuesta de Evaluación de la Docencia del período lectivo anterior [RG-ART-042]."}],
         "¿Y qué pasa si me faltan pocos ramos para terminar y la oferta no llega al mínimo de créditos?",
         "El **Vicedecano** puede autorizar una inscripción menor al mínimo de créditos cuando la oferta es inferior a ese mínimo por tu situación curricular personal y prerrequisitos; además, si estás terminando tus estudios puedes inscribir solo las asignaturas que te falten cursar [RG-ART-042].",
         None),
        ("train", "RG-ART-019",
         [{"role": "user", "content": "¿Cuándo debe entregarnos el profesor el syllabus y reglas de evaluación?"},
          {"role": "assistant", "content": "Al inicio de la dictación de la asignatura, por escrito o canal oficial que permita almacenarlo o imprimirlo [RG-ART-019]."}],
         "¿Qué porcentaje de alumnos con nota bajo 4,0 obliga después a convocar a la Comisión de Evaluación?",
         "Cuando **más del 50%** de los alumnos que rinden una evaluación obtiene nota inferior a 4,0 (o ante filtraciones u otras anomalías), el Director del Departamento convoca a la **Comisión de Evaluación**, que estudia el caso, resuelve e informa al Vicedecano [RG-ART-013].",
         [("leer_articulo", {"doc": "RG", "numero": 13})]),
        ("val", "RI-FI-ART-032",
         [{"role": "user", "content": "¿Cuántos docentes del Departamento integran el Consejo de Carrera en Ingeniería?"},
          {"role": "assistant", "content": "Un mínimo de seis docentes del Departamento adscritos a la carrera con contrato indefinido y al menos media jornada [RI-FI-ART-032]."}],
         "¿Y cuántos estudiantes participan, quién los elige y cuánto duran?",
         "Participan **tres representantes estudiantiles** de la carrera con derecho a voz y voto; son elegidos por el **Centro de Alumnos** respectivo y duran **1 año** en sus funciones [RI-FI-ART-032].",
         None),
        ("val", "RG-ART-045",
         [{"role": "user", "content": "¿Cuántas asignaturas puedo cursar en un PLEV?"},
          {"role": "assistant", "content": "Solo una asignatura por cada PLEV, siendo alumno regular y con aprobación del Jefe de Carrera [RG-ART-045]."}],
         "¿Y si repruebo ese ramo pierdo mi beca o se afecta mi avance curricular?",
         "No: según [RG-ART-045], reprobar una asignatura en el PLEV **no afecta** tu situación curricular ni tus antecedentes para becas o préstamos, aunque sí queda registrada en tu hoja curricular.",
         None),
    ]
    ejemplos: list[dict[str, Any]] = []
    for idx, (sp, uid, hist, preg, resp, tools) in enumerate(casos, 1):
        aseg = None if tools else [uid]
        ejemplos.append(
            _armar_registro(
                f"FT-MT-{idx:02d}", sp, "conversacion_multiturno", buscador, preg, resp,
                tools=tools, asegurar_ids=aseg, historial=hist,
            )
        )
    return ejemplos


def _generar_bloque_abstenciones(buscador: BuscadorNormativa) -> list[dict[str, Any]]:
    """Artículos fuera de rango (con `existe_articulo`), incisos falsos y datos no regulados."""
    casos = [
        ("train", True, ("RI-FI", 39),
         "Necesito revisar si existe algún protocolo de tutorías pares en el Art. 39 del RI-FI de Ingeniería.",
         "El Artículo 39 **no existe** en el Reglamento Interno de Docencia de Pregrado de la Facultad de Ingeniería (`RI-FI`), ya que ese reglamento llega hasta el Artículo 35. No debe confundirse con el Artículo 39 del Reglamento General.",
         True),
        ("train", True, ("RI-FI", 41),
         "Me piden revisar el Art. 41 de la normativa interna de Ingeniería sobre siglas SAC, ¿qué establece exactamente?",
         "El Artículo 41 **no existe** en el Reglamento Interno de Ingeniería (`RI-FI`), cuyo alcance máximo llega al Artículo 35 (las siglas SAC corresponden al Art. 41 del Reglamento General, no al RI-FI).",
         True),
        ("train", True, ("RG", 64),
         "En una apelación me citaron el Art. 64 del RG por sanciones administrativas, ¿me puedes decir qué dispone?",
         "El Artículo 64 **no existe** en el Reglamento General de Docencia de Pregrado (`RG`); su articulado ordinario llega hasta el Artículo 60 (más disposiciones transitorias).",
         True),
        ("train", True, ("RG", 78),
         "Quisiera consultar qué dice el Art. 78 del RG sobre becas de residencia estudiantil.",
         "El Artículo 78 **no existe** en el Reglamento General de Docencia de Pregrado (`RG`), porque el texto oficial llega solo hasta el Artículo 60.",
         True),
        ("train", False, None,
         "¿Qué prioridad de inscripción contempla el inciso e) dentro del Art. 7 del RI-FI?",
         "No existe un inciso e) en el Artículo 7° del RI-FI: dicho artículo únicamente contempla las prioridades **a), b), c) y d)** [RI-FI-ART-007].",
         False),
        ("train", False, None,
         "Para entrar por Ingreso Directo en Ingeniería, ¿qué puntaje PAES específico fija el Art. 4 del RI-FI?",
         "El Artículo 4° del RI-FI no fija ningún puntaje PAES específico; únicamente indica que la Facultad de Ingeniería define cada año los cupos de Ingreso Directo e Ingreso Común [RI-FI-ART-004].",
         False),
        ("train", False, None,
         "¿Cuál es el monto mensual en pesos de la ayuda económica fijada en el Art. 15 del RG?",
         "El Artículo 15° del Reglamento General no establece ningún monto en dinero ni becas monetarias; regula únicamente los sistemas de apoyo al estudiante mediante Tutorías Académicas y Monitores Estudiantiles [RG-ART-015].",
         False),
        ("train", False, None,
         "Si abandono un curso en el PLEV dentro de las primeras dos semanas, ¿bajo qué causal de Art. 43 RG queda registrado?",
         "No procede el abandono en el PLEV: según [RG-ART-043], los alumnos **no podrán hacer abandono** de asignaturas inscritas en el PLEV.",
         False),
        ("val", True, ("RI-FI", 48),
         "¿Dónde aparece la escala de distinciones de titulación en el Art. 48 de las normas internas de Ingeniería?",
         "El Artículo 48 **no existe** en el Reglamento Interno de Docencia de Pregrado de la Facultad de Ingeniería (`RI-FI`), porque llega hasta el Artículo 35 (esa escala figura en el Art. 48 del RG, no del RI-FI).",
         True),
        ("val", True, ("RG", 82),
         "Estoy buscando el plazo para apelar suspensiones en el Art. 82 del RG, ¿me ayudas a leerlo?",
         "El Artículo 82 **no existe** en el Reglamento General de Docencia de Pregrado (`RG`), ya que su articulado llega hasta el Artículo 60.",
         True),
        ("val", False, None,
         "¿Qué documento extra solicita la letra c) del Art. 55 RG al postular a otra carrera?",
         "El Artículo 55° del Reglamento General no posee letra c); sus requisitos formales son únicamente los incisos **a)** y **b)** [RG-ART-055].",
         False),
    ]

    ejemplos: list[dict[str, Any]] = []
    for idx, (sp, es_inex, doc_num, preg, resp, usar_alerta) in enumerate(casos, 1):
        tools = [("existe_articulo", {"doc": doc_num[0], "numero": doc_num[1]})] if (es_inex and doc_num and idx % 2 == 1) else None
        aseg = None
        if "Art. 7" in preg or "Artículo 7" in preg:
            aseg = ["RI-FI-ART-007"]
        elif "Art. 4" in preg or "Artículo 4" in preg:
            aseg = ["RI-FI-ART-004"]
        elif "Art. 15" in preg or "Artículo 15" in preg:
            aseg = ["RG-ART-015"]
        elif "Art. 43" in preg:
            aseg = ["RG-ART-043"]
        elif "Art. 55" in preg or "Artículo 55" in preg:
            aseg = ["RG-ART-055"]
        ejemplos.append(
            _armar_registro(
                f"FT-ABST-{idx:02d}", sp, "abstencion_y_limites", buscador, preg, resp,
                tools=tools, asegurar_ids=aseg, usar_alerta_inv=usar_alerta,
            )
        )
    return ejemplos


def _generar_bloque_ampliado_y_encadenado(buscador: BuscadorNormativa) -> list[dict[str, Any]]:
    """Agrega diversidad de artículos limpios, cadenas de 2 herramientas y PDFs extras."""
    ejemplos: list[dict[str, Any]] = []

    # 1. Cadenas de 2 herramientas (`buscar_reglamento`/`leer_articulo` + `calcular` o `ver_calendario` + `dias_entre`)
    cadenas = [
        ("FT-CHAIN-01", "train", "tool_encadenada",
         "¿Cuál es la diferencia en días entre el feriado nacional de abril y el feriado nacional de mayo de 2026?",
         "En el primer semestre 2026 hay feriados nacionales el viernes **03 de abril** [CAL-2026-S1-09] y el viernes **01 de mayo** [CAL-2026-S1-10], lo que equivale a **28 días corridos** entre ambos (y también del 01 de mayo al 21 de mayo hay 20 días [CAL-2026-S1-11]).",
         [("ver_calendario", {"semestre": "1"}), ("dias_entre", {"fecha_inicio": "2026-04-03", "fecha_fin": "2026-05-01", "inclusivo": False})],
         {c for c in buscador.por_id if c.startswith("CAL-")}),
        ("FT-CHAIN-02", "train", "tool_encadenada",
         "Si un estudiante con nota 5,9 en la Evaluación Diagnóstica rindió además dos controles evaluados con 5,5 y 6,0 (ponderados 40% y 60%), ¿cumple primero la condición del Art. 38 RG para Inicio Adelantado y cuál es el promedio ponderado de sus controles?",
         "Sí: **5,9 supera el umbral estricto de 5,7** fijado para optar al Inicio Adelantado en [RG-ART-038], y el promedio ponderado de ambos controles es `0.4 * 5.5 + 0.6 * 6.0 = 5,8`.",
         [("leer_articulo", {"doc": "RG", "numero": 38}), ("calcular", {"expresion": "0.4 * 5.5 + 0.6 * 6.0"})],
         {"RG-ART-038"}),
        ("FT-CHAIN-03", "train", "tool_encadenada",
         "¿Cuántos días de clases o periodo hay desde el 30 de junio hasta el 24 de julio (término anual del primer semestre)? Usa el calendario si falta alguna fecha.",
         "Las vacaciones de invierno inician el **30 de junio** [CAL-2026-S1-14] y las asignaturas anuales terminan el **24 de julio** [CAL-2026-S1-05], mediando **24 días corridos** entre ambas fechas.",
         [("ver_calendario", {"semestre": "1"}), ("dias_entre", {"fecha_inicio": "2026-06-30", "fecha_fin": "2026-07-24", "inclusivo": False})],
         {c for c in buscador.por_id if c.startswith("CAL-")}),
        ("FT-CHAIN-04", "val", "tool_encadenada",
         "Si un egresado de carrera terminal obtuvo 5,1 (70%) y 6,2 (30%) según la regla de conceptos del Art. 48 RG, ¿qué calificación final y qué concepto le corresponden en su Diploma?",
         "Su calificación ponderada es **5,43** (`0.7 * 5.1 + 0.3 * 6.2 = 5,43`), ubicándose en el tramo `5,0 - 5,6` que corresponde al concepto **\"Aprobado con Distinción\"** en el Diploma de Licenciado en carrera terminal según [RG-ART-048].",
         [("leer_articulo", {"doc": "RG", "numero": 48}), ("calcular", {"expresion": "0.7 * 5.1 + 0.3 * 6.2"})],
         {"RG-ART-048"}),
    ]
    for rid, sp, cat, preg, resp, tools, omit in cadenas:
        ejemplos.append(_armar_registro(rid, sp, cat, buscador, preg, resp, tools=tools, omitir_ids=omit))

    # 2. Reglas adicionales limpias en RG y RI-FI (1 y 2 turnos con citas estrictas)
    articulos_extra = [
        ("FT-EXT-01", "train", "RG-ART-006", False,
         "¿Quién asigna la carga docente en cada asignatura y qué pasa si participan varios Departamentos o Facultades?",
         "El **Director de Departamento** asigna la carga docente y designa a un Profesor Encargado (y eventualmente alterno), comunicándolo a su Vicedecano, quien informa al Vicedecano y al Jefe de Carrera solicitantes y se registra en el SAC [RG-ART-006]. Si participan varios Departamentos o Facultades, la administración recae en el **Vicedecano** de la Facultad a la que está adscrita la asignatura [RG-ART-006]."),
        ("FT-EXT-02", "train", "RG-ART-007", False,
         "¿Quién aplica la Encuesta de Evaluación Docente y qué profesores quedan exceptuados de ella?",
         "La encuesta se aplica en cada periodo lectivo en línea vía **Plataforma Encuesta Docente** bajo responsabilidad de la **Dirección de Docencia**; se exceptúa únicamente a los profesores que hayan impartido docencia en la asignatura por reemplazos u otras circunstancias [RG-ART-007]."),
        ("FT-EXT-03", "train", "RG-ART-009", False,
         "¿Tienen derecho a voto los invitados especiales en el Consejo de Carrera? ¿Cuántos estudiantes integran ese Consejo según el RG?",
         "No: los invitados especiales (académicos, expertos, egresados o empleadores) tienen derecho a **voz, pero no a voto** [RG-ART-009]. Según el RG, integran el Consejo entre **tres y hasta cuatro representantes estudiantiles** con derecho a voz y voto [RG-ART-009]."),
        ("FT-EXT-04", "train", "RG-ART-010", True,
         "¿Cada cuánto debe sesionar el Consejo de Carrera y qué sanción aplica a un representante estudiantil o a un académico tras dos ausencias seguidas injustificadas?",
         "Debe sesionar al menos **tres veces por semestre** (con quórum mínimo de 60% de sus miembros y convocatoria con al menos una semana de antelación) [RG-ART-010]. Ante **dos ausencias consecutivas sin justificación**, si es representante estudiantil será **reemplazado**, y si es académico recibirá un **llamado de atención por escrito** [RG-ART-010]."),
        ("FT-EXT-05", "train", "RG-ART-014", False,
         "Si a un estudiante le coinciden en el mismo día y horario dos actividades académicas que son requisito, ¿cuál debe priorizar?",
         "Debe priorizar la actividad académica **que no tiene posibilidad de ser recuperada**, teniendo derecho a recuperar la que no efectuó; el **Jefe de Carrera** velará por ello e informará a los profesores encargados [RG-ART-014]."),
        ("FT-EXT-06", "train", "RG-ART-021", False,
         "¿Cómo se consignan en el Acta de Notas las asignaturas con evaluación cualitativa?",
         "En asignaturas con evaluación cualitativa se utilizan los conceptos Aprobado o Reprobado, consignándose en el Acta de Notas como **APR** o **REP**, respectivamente [RG-ART-021]."),
        ("FT-EXT-07", "train", "RG-ART-040", True,
         "¿En qué casos procede la homologación de asignaturas y quién aprueba la tabla de homologaciones?",
         "La homologación procede para asignaturas del plan de estudio de una **misma carrera** registradas con otro código en el SAC por dictarse en otra sede o pertenecer a una versión anterior del plan [RG-ART-040]. La tabla la establece el **Vicedecano** de la Facultad a la que está adscrita la carrera, con **visto bueno del Vicedecano** de la Facultad que dicta la asignatura, y se registra en el SAC por UDARAE [RG-ART-040]."),
        ("FT-EXT-08", "train", "RG-ART-041", False,
         "¿Qué siglas se usan en el SAC para validar, convalidar, revalidar, homologar o reconocer, y cuentan como carga académica del semestre?",
         "En el SAC se registran como **VAL** (validadas), **CON** (convalidadas), **REV** (revalidadas), **HOM** (homologadas) y **REC** (reconocidas) [RG-ART-041]. Las asignaturas convalidadas, revalidadas, homologadas o reconocidas **no se consideran carga académica del semestre** [RG-ART-041]."),
        ("FT-EXT-09", "train", "RG-ART-050", False,
         "¿Hasta cuándo se mantiene vigente la calidad de alumno regular entre un semestre y el siguiente?",
         "La calidad de alumno regular se mantendrá hasta el inicio del período de inscripción de asignaturas del Período Lectivo Ordinario siguiente [RG-ART-050]."),
        ("FT-EXT-10", "train", "RG-ART-058", False,
         "¿Puede un estudiante matriculado alegar desconocimiento del Reglamento General o de los Reglamentos Internos?",
         "No: según [RG-ART-058], tanto el Reglamento General como los Reglamentos Internos de cada Facultad son de dominio público y **se consideran conocidos por el alumno al formalizar su matrícula**."),
        ("FT-EXT-11", "train", "RI-FI-ART-002", False,
         "¿Qué cuerpos normativos rigen la docencia de pregrado en la Facultad de Ingeniería según el Art. 2 del RI-FI?",
         "Según [RI-FI-ART-002], la docencia de pregrado en Ingeniería se rige por el Reglamento General de Docencia de Pregrado UdeC vigente, las Normas de Ingreso a las Carreras de Pregrado vigentes, el Reglamento Interno de la Facultad de Ingeniería vigente y el propio Reglamento Interno de Docencia de Pregrado que complementa a los anteriores."),
        ("FT-EXT-12", "val", "RG-ART-060", False,
         "Si existe contradicción entre el Reglamento General de Docencia de Pregrado y una norma interna distinta, ¿cuál prevalece?",
         "Prevalecen siempre las normas del **Reglamento General de Docencia de Pregrado** sobre cualesquiera otras que no se concilien con ellas, sin importar de dónde provengan [RG-ART-060]."),
        ("FT-EXT-13", "val", "RG-TRANS-001", False,
         "¿Qué regla se aplica a las situaciones académicas que estaban pendientes al entrar en vigencia el Reglamento General?",
         "Se resuelven aplicando las normas vigentes al momento de su formulación u ocurrencia, **salvo** cuando la aplicación del nuevo Reglamento General mejore la condición del alumno [RG-TRANS-001]."),
        ("FT-EXT-14", "val", "RI-FI-ART-001", False,
         "¿Quiénes tienen la calidad de estudiantes de pregrado de la Facultad de Ingeniería según el Art. 1 RI-FI?",
         "Son estudiantes de pregrado de la Facultad de Ingeniería quienes ingresan a una de sus carreras cumpliendo con los requisitos generales establecidos por la Universidad de Concepción [RI-FI-ART-001]."),
    ]
    for rid, sp, uid, usar_leer, preg, resp in articulos_extra:
        doc_short = "RI-FI" if uid.startswith("RI-FI") else ("RG-TRANS" if "TRANS" in uid else "RG")
        if usar_leer and doc_short in {"RG", "RI-FI"}:
            num = int(uid.split("-ART-")[-1])
            ejemplos.append(
                _armar_registro(
                    rid, sp, "lectura_y_citas", buscador, preg, resp,
                    tools=[("leer_articulo", {"doc": doc_short, "numero": num})],
                    omitir_ids={uid},
                )
            )
        else:
            ejemplos.append(
                _armar_registro(
                    rid, sp, "lectura_y_citas", buscador, preg, resp,
                    asegurar_ids=[uid],
                )
            )

    # 3. Dos PDFs extra en TRAIN + seguimientos adicionales multi-turno PDF y UdeC
    pack_beca = _crear_pack_pdf_sintetico(
        "guia_beca_movilidad.pdf",
        [
            "Programa Beca de Movilidad Estudiantil 2026. Cobertura máxima: USD 3.500 para pasajes y manutención semestral.",
            "Requisito académico: haber aprobado al menos el 50% de los créditos del plan de estudio y mantener promedio ponderado igual o superior a 5,2.",
        ],
    )
    pack_taller = _crear_pack_pdf_sintetico(
        "reglamento_taller_prototipos.pdf",
        [
            "Reglamento Interno Taller de Prototipos. Uso de cortadora láser restringido a estudiantes con inducción aprobada (100% de asistencia en módulo de seguridad).",
            "Reserva de equipos: máximo 4 horas semanales por equipo de proyecto a través del portal intranet del taller.",
        ],
    )
    b_comb_ex = buscador.con_pdfs_usuario([pack_beca, pack_taller], incluir_corpus_base=True)
    b_solo_ex = buscador.con_pdfs_usuario([pack_beca, pack_taller], incluir_corpus_base=False)

    id_b1, id_b2 = pack_beca["unidades"][0]["id"], pack_beca["unidades"][1]["id"]
    id_t1, id_t2 = pack_taller["unidades"][0]["id"], pack_taller["unidades"][1]["id"]

    extras_pdf_y_mt = [
        ("FT-PDF-07", "train", "pdfs_en_caliente", b_comb_ex, [id_b1, id_b2], None, True, False, None,
         "En la guía de beca de movilidad que subí, ¿cuál es el monto máximo cubierto y qué promedio ponderado pide?",
         f"La beca cubre hasta **USD 3.500** para pasajes y manutención semestral [{id_b1}] [guia_beca_movilidad.pdf p. 1] y exige haber aprobado al menos el 50% de los créditos del plan junto con un promedio ponderado **igual o superior a 5,2** [{id_b2}] [guia_beca_movilidad.pdf p. 2].",
         None),
        ("FT-PDF-08", "train", "pdfs_en_caliente", b_comb_ex, [id_b2, "RI-FI-ART-024"], None, True, False, None,
         "Si gano esa beca de movilidad y apruebo ramos en el extranjero bajo convenio, ¿ante quién los valido en Ingeniería según el reglamento y cómo se registran?",
         f"Además de cumplir los requisitos de postulación de tu guía (promedio >= 5,2 y >= 50% de créditos) [{id_b2}] [guia_beca_movilidad.pdf p. 2], al volver de intercambio bajo convenio UdeC debes presentar al **Vicedecano** el programa y calificación certificados para validarlos en el SAC en la Escala Oficial y en el semestre cursado [RI-FI-ART-024].",
         None),
        ("FT-PDF-09", "train", "pdfs_en_caliente", b_solo_ex, [id_t1, id_t2], None, True, True, None,
         "¿Puedo usar la cortadora láser del taller de prototipos si falté a parte de la inducción, y cuántas horas a la semana permite reservar el reglamento?",
         f"No: el uso de la cortadora láser exige aprobar la inducción con **100% de asistencia** en el módulo de seguridad [{id_t1}] [reglamento_taller_prototipos.pdf p. 1]. Además, el máximo de reserva es de **4 horas semanales** por equipo de proyecto en la intranet del taller [{id_t2}] [reglamento_taller_prototipos.pdf p. 2].",
         None),
        ("FT-MT-07", "train", "conversacion_multiturno", b_solo_ex, [id_b2], None, True, True,
         [{"role": "user", "content": "¿Cuál es la cobertura económica máxima de la beca de movilidad en el PDF?"},
          {"role": "assistant", "content": f"Cubre hasta USD 3.500 para pasajes y manutención semestral [{id_b1}] [guia_beca_movilidad.pdf p. 1]."}],
         "¿Y si tengo promedio 5,1 y 45% de créditos aprobados puedo postular?",
         f"No cumples ninguno de los dos requisitos mínimos del PDF: se exige haber aprobado al menos **50%** de los créditos del plan (tienes 45%) y mantener un promedio ponderado igual o superior a **5,2** (tienes 5,1) [{id_b2}] [guia_beca_movilidad.pdf p. 2].",
         None),
        ("FT-MT-08", "train", "conversacion_multiturno", buscador, ["RG-ART-054"], None, False, False,
         [{"role": "user", "content": "¿Dónde entrego los papeles para pedir un cambio de carrera en la UdeC?"},
          {"role": "assistant", "content": "Debes presentar la solicitud documentada en UDARAE dentro del periodo fijado por Dirección de Docencia [RG-ART-054]."}],
         "¿Y quiénes resuelven finalmente esa solicitud?",
         "La resuelve una Comisión integrada por el **Director de Docencia**, el **Decano de la Facultad** y el **Jefe de Carrera**, requiriendo sanción del **Rector** y registro en el SAC por UDARAE [RG-ART-054].",
         None),
    ]
    for rid, sp, cat, b_obj, aseg, omit, tiene_p, solo_p, hist, preg, resp, tools in extras_pdf_y_mt:
        ejemplos.append(
            _armar_registro(
                rid, sp, cat, b_obj, preg, resp,
                tools=tools, asegurar_ids=aseg, omitir_ids=omit,
                historial=hist, solo_pdfs=solo_p, tiene_pdfs=tiene_p,
            )
        )

    return ejemplos


def construir_registros_sft() -> list[dict[str, Any]]:
    """Genera todos los registros SFT balanceados verificados contra corpus limpio."""
    with tempfile.TemporaryDirectory() as tmp:
        buscador_limpio = _crear_buscador_limpio(Path(tmp))
        registros: list[dict[str, Any]] = []
        registros.extend(_generar_bloque_calculo(buscador_limpio))
        registros.extend(_generar_bloque_calendario(buscador_limpio))
        registros.extend(_generar_bloque_multirequisito(buscador_limpio))
        registros.extend(_generar_bloque_pdfs(buscador_limpio))
        registros.extend(_generar_bloque_multiturno(buscador_limpio))
        registros.extend(_generar_bloque_abstenciones(buscador_limpio))
        registros.extend(_generar_bloque_ampliado_y_encadenado(buscador_limpio))
    return registros


def guardar_dataset_sft(
    salida_dir: Path = DEFAULT_FT_DATA_DIR,
) -> dict[str, Any]:
    """Construye, audita antifuga y escribe `train.jsonl`, `val.jsonl` y resumen en disco."""
    registros = construir_registros_sft()
    auditoria = validar_dataset_completo(registros)
    if not auditoria["ok"]:
        muestra = "\n".join(auditoria["errores"][:10])
        raise ValueError(f"Auditoría antifuga falló con {len(auditoria['errores'])} error(es):\n{muestra}")

    salida_dir = Path(salida_dir)
    salida_dir.mkdir(parents=True, exist_ok=True)
    train = [r for r in registros if r["split"] == "train"]
    val = [r for r in registros if r["split"] == "val"]

    (salida_dir / "train.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in train) + "\n", encoding="utf-8"
    )
    (salida_dir / "val.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in val) + "\n", encoding="utf-8"
    )
    resumen = {
        "total": len(registros),
        "train": len(train),
        "val": len(val),
        "por_categoria": auditoria["por_categoria"],
        "antifuga_ok": True,
    }
    (salida_dir / "resumen_dataset.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return resumen


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Genera train.jsonl / val.jsonl sin fugas para fine-tuning Qwen3-4B")
    parser.add_argument("--salida-dir", type=Path, default=DEFAULT_FT_DATA_DIR)
    args = parser.parse_args(argv)
    resumen = guardar_dataset_sft(args.salida_dir)
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
