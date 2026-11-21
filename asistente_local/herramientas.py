"""Herramientas deterministas (calculadora AST, calendario y corpus) para Ollama."""

from __future__ import annotations

import ast
import datetime as dt
import math
import operator
import re
from typing import Any

from .buscador import BuscadorNormativa, normalizar_texto

_OPS_BINARIOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_OPS_UNARIOS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_FUNCIONES_SEGURAS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "ceil": math.ceil,
    "floor": math.floor,
    "sqrt": math.sqrt,
}

_MESES_ES = {
    "ene": 1, "enero": 1,
    "feb": 2, "febrero": 2,
    "mar": 3, "marzo": 3,
    "abr": 4, "abril": 4,
    "may": 5, "mayo": 5,
    "jun": 6, "junio": 6,
    "jul": 7, "julio": 7,
    "ago": 8, "agosto": 8,
    "sep": 9, "sept": 9, "septiembre": 9, "setiembre": 9,
    "oct": 10, "octubre": 10,
    "nov": 11, "noviembre": 11,
    "dic": 12, "diciembre": 12,
}


def _evaluar_nodo(nodo: ast.AST) -> float | int:
    if isinstance(nodo, ast.Expression):
        return _evaluar_nodo(nodo.body)
    if isinstance(nodo, ast.Constant):
        if isinstance(nodo.value, bool) or not isinstance(nodo.value, (int, float)):
            raise ValueError("Solo se permiten constantes numéricas.")
        return nodo.value
    if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in _OPS_UNARIOS:
        return _OPS_UNARIOS[type(nodo.op)](_evaluar_nodo(nodo.operand))
    if isinstance(nodo, ast.BinOp) and type(nodo.op) in _OPS_BINARIOS:
        izq = _evaluar_nodo(nodo.left)
        der = _evaluar_nodo(nodo.right)
        if isinstance(nodo.op, (ast.Div, ast.FloorDiv, ast.Mod)) and der == 0:
            raise ZeroDivisionError("División por cero.")
        if isinstance(nodo.op, ast.Pow) and abs(der) > 100:
            raise ValueError("Exponente fuera de límite seguro (<= 100).")
        return _OPS_BINARIOS[type(nodo.op)](izq, der)
    if isinstance(nodo, ast.Call):
        if not isinstance(nodo.func, ast.Name) or nodo.func.id not in _FUNCIONES_SEGURAS:
            raise ValueError("Función no permitida en la calculadora.")
        if nodo.keywords:
            raise ValueError("No se admiten argumentos con nombre en la calculadora.")
        args = [_evaluar_nodo(a) for a in nodo.args]
        return _FUNCIONES_SEGURAS[nodo.func.id](*args)
    raise ValueError(f"Expresión matemática no permitida: {type(nodo).__name__}")


def calcular(expresion: str) -> dict[str, Any]:
    """Evalúa expresiones matemáticas de forma segura con AST (admite coma decimal)."""
    cruda = str(expresion or "").strip()
    if not cruda or len(cruda) > 200:
        return {"ok": False, "expresion": cruda, "error": "Expresión vacía o demasiado larga."}

    normalizada = (
        cruda.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("^", "**")
    )
    normalizada = re.sub(r"\b(\d+),(\d+)\b", r"\1.\2", normalizada)
    try:
        arbol = ast.parse(normalizada, mode="eval")
        res = _evaluar_nodo(arbol)
    except ZeroDivisionError as exc:
        return {"ok": False, "expresion": cruda, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "expresion": cruda, "error": f"Expresión inválida: {exc}"}

    if isinstance(res, float) and res.is_integer():
        res_fmt: float | int = int(res)
    elif isinstance(res, float):
        res_fmt = round(res, 6)
    else:
        res_fmt = res
    return {"ok": True, "expresion": cruda, "resultado": res_fmt}


def parsear_fecha(texto: str, anio_por_defecto: int = 2026) -> dt.date:
    """Convierte fechas ISO, DD/MM/YYYY o español ('09 de marzo') a datetime.date."""
    limpia = normalizar_texto(texto)
    tokens = limpia.split()
    if not tokens:
        raise ValueError(f"Fecha vacía: {texto!r}")

    # Formato YYYY MM DD
    m_iso = re.fullmatch(r"(\d{4})\s+(\d{1,2})\s+(\d{1,2})", limpia)
    if m_iso:
        return dt.date(int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3)))

    # Formato DD MM [YYYY]
    m_num = re.fullmatch(r"(\d{1,2})\s+(\d{1,2})(?:\s+(\d{4}))?", limpia)
    if m_num:
        anio = int(m_num.group(3) or anio_por_defecto)
        return dt.date(anio, int(m_num.group(2)), int(m_num.group(1)))

    # Formato español: '09 de marzo [2026]' o 'marzo 09'
    tokens_filtrados = [t for t in tokens if t not in {"de", "del", "el"}]
    dia = None
    mes = None
    anio = anio_por_defecto
    for t in tokens_filtrados:
        if t in _MESES_ES and mes is None:
            mes = _MESES_ES[t]
        elif t.isdigit():
            val = int(t)
            if val >= 1900:
                anio = val
            elif 1 <= val <= 31 and dia is None:
                dia = val
    if dia is not None and mes is not None:
        return dt.date(anio, mes, dia)

    raise ValueError(f"No se pudo interpretar la fecha: {texto!r}")


def dias_entre(
    fecha_inicio: str,
    fecha_fin: str,
    inclusivo: bool = False,
    anio_por_defecto: int = 2026,
) -> dict[str, Any]:
    """Calcula días reales de calendario entre dos fechas (exacto con datetime.date)."""
    try:
        f1 = parsear_fecha(fecha_inicio, anio_por_defecto=anio_por_defecto)
        f2 = parsear_fecha(fecha_fin, anio_por_defecto=anio_por_defecto)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}

    delta = (f2 - f1).days
    abs_dias = abs(delta)
    return {
        "ok": True,
        "fecha_inicio_iso": f1.isoformat(),
        "fecha_fin_iso": f2.isoformat(),
        "dias_diferencia": delta,
        "dias_corridos": abs_dias,
        "dias_inclusivos": abs_dias + 1,
        "resultado_solicitado": abs_dias + 1 if inclusivo else delta,
        "inclusivo": bool(inclusivo),
    }


ESQUEMAS_HERRAMIENTAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "buscar_reglamento",
            "description": (
                "Busca artículos y fragmentos relevantes en el corpus oficial UdeC "
                "(RG, RI-FI y Calendario 2026). Puede filtrar por documento."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "consulta": {
                        "type": "string",
                        "description": "Texto o palabras clave de la pregunta.",
                    },
                    "k": {
                        "type": "integer",
                        "description": "Cantidad de resultados a devolver (entre 1 y 12; default 6).",
                    },
                    "documento": {
                        "type": "string",
                        "enum": ["RG", "RI-FI", "CAL"],
                        "description": "Opcional: restringe a RG, RI-FI o CAL.",
                    },
                },
                "required": ["consulta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "leer_articulo",
            "description": "Trae el texto literal completo de un artículo específico de RG o RI-FI.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc": {"type": "string", "enum": ["RG", "RI-FI"]},
                    "numero": {"type": "integer", "description": "Número del artículo (ej. 14)."},
                },
                "required": ["doc", "numero"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "existe_articulo",
            "description": "Verifica si un artículo N existe realmente en RG (1-60) o RI-FI (1-35).",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc": {"type": "string", "enum": ["RG", "RI-FI"]},
                    "numero": {"type": "integer"},
                },
                "required": ["doc", "numero"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ver_calendario",
            "description": "Muestra todas las fechas oficiales del Calendario Académico 2026.",
            "parameters": {
                "type": "object",
                "properties": {
                    "semestre": {
                        "type": "string",
                        "enum": ["1", "2", "ambos"],
                        "description": "Primer semestre ('1'), segundo ('2') o 'ambos'.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calcular",
            "description": "Calculadora matemática exacta en Python (promedios, ponderaciones, comparaciones).",
            "parameters": {
                "type": "object",
                "properties": {
                    "expresion": {
                        "type": "string",
                        "description": "Expresión aritmética, ej. '42 / 4' o '0.6 * 5.2 + 0.4 * 6.5'.",
                    }
                },
                "required": ["expresion"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "dias_entre",
            "description": "Calcula exactamente los días corridos entre dos fechas del calendario.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_inicio": {
                        "type": "string",
                        "description": "Ej. '2026-03-09' o '09 de marzo'.",
                    },
                    "fecha_fin": {
                        "type": "string",
                        "description": "Ej. '2026-04-02' o '02 de abril'.",
                    },
                    "inclusivo": {
                        "type": "boolean",
                        "description": (
                            "False por defecto para días que transcurren entre una fecha y otra; "
                            "True solo si piden duración inclusive (ej. 'del 11 al 15 inclusive' = 5 días)."
                        ),
                    },
                },
                "required": ["fecha_inicio", "fecha_fin"],
            },
        },
    },
]


def ejecutar_herramienta(
    nombre: str,
    argumentos: dict[str, Any],
    buscador: BuscadorNormativa,
) -> Any:
    """Despacha de forma segura la llamada de herramienta pedida por el modelo."""
    args = argumentos if isinstance(argumentos, dict) else {}
    if nombre == "buscar_reglamento":
        return buscador.buscar(
            consulta=str(args.get("consulta", "")),
            k=int(args.get("k", 6)),
            documento=args.get("documento"),
            modo_fusion="rrf",
            usar_descomposicion=True,
        )
    if nombre == "leer_articulo":
        return buscador.leer_articulo(
            doc=str(args.get("doc", "")),
            numero=int(args.get("numero", 0)),
        )
    if nombre == "existe_articulo":
        return buscador.existe_articulo(
            doc=str(args.get("doc", "")),
            numero=int(args.get("numero", 0)),
        )
    if nombre == "ver_calendario":
        return buscador.ver_calendario(semestre=str(args.get("semestre", "ambos")))
    if nombre == "calcular":
        return calcular(expresion=str(args.get("expresion", "")))
    if nombre == "dias_entre":
        return dias_entre(
            fecha_inicio=str(args.get("fecha_inicio", "")),
            fecha_fin=str(args.get("fecha_fin", "")),
            inclusivo=bool(args.get("inclusivo", False)),
        )
    return {"error": f"Herramienta desconocida: {nombre}"}
