"""Evaluación experimental de las 3 opciones de resolución de premisas falsas (P41-P50).

Este script permite ejecutar o simular las 10 preguntas de categoría abstención
bajo tres intervenciones sutiles sin overfitting:
  - Opcion 1: Ajuste semántico al prompt del Auditor (definición de parada en ausencias).
  - Opcion 2: Consenso semántico en el orquestador (reconocimiento de acuerdo fáctico).
  - Opcion 3: Flexibilización del contrato de apoyos para hechos negativos.

No modifica las respuestas ni trazas congeladas de la entrega oficial de D3.
"""
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "d3_agentes"


def obtener_preguntas_p41_p50():
    """Filtra y devuelve exclusivamente las 10 preguntas de abstención (IDs 41 al 50)."""
    with open(ROOT.parent / "Deliverable2" / "recuperacion" / "resultados" / "e5_estructurado_v2" / "subconsultas.json") as f:
        # Si no está ahí, se leen de preguntas_p41_p50 hardcodeadas o del lote
        pass
    # Leemos del lote 99b9 que tiene las 50 preguntas exactas
    import pandas as pd
    csv_path = ROOT / "resultados" / "lote_99b9b55bd79d4572f743" / "original" / "agentes_completo.csv"
    df = pd.read_csv(csv_path)
    preguntas_abstencion = []
    for _, row in df.iloc[40:50].iterrows():
        preguntas_abstencion.append({
            "id": int(row["pregunta_id"]),
            "pregunta": str(row["pregunta"]),
            "categoria": str(row["categoria"])
        })
    return preguntas_abstencion


def prompt_auditor_opcion1():
    """Opción 1: Ajuste sutil en la definición de la acción 'aceptar'."""
    base = (ROOT / "prompts" / "auditor.txt").read_text(encoding="utf-8")
    reemplazo = (
        "aceptar: el borrador responde correctamente con respaldo disponible, o constata "
        "válidamente que el artículo, norma o condición no existe o no aplica según el inventario "
        "o la evidencia consultada. Si el borrador ya declara la ausencia con respaldo, "
        "debes elegir aceptar y no pedir corregir."
    )
    nuevo = re.sub(r"aceptar:\s*el borrador responde correctamente con respaldo disponible\.",
                   reemplazo, base)
    return nuevo


def prompt_verificacion_opcion1():
    """Opción 1 (complemento): Refuerzo de la regla de premisas falsas."""
    base = (ROOT / "prompts" / "verificacion.txt").read_text(encoding="utf-8")
    reemplazo = (
        "En premisas falsas, un inventario completo permite verificar ausencia; una búsqueda parcial no. "
        "Si el borrador constata que el artículo o condición consultada no existe en la normativa según "
        "el inventario disponible, esa constatación es la respuesta correcta definitiva: elige aceptar. "
        "No pidas un artículo que el inventario ya demuestra ausente."
    )
    nuevo = re.sub(r"En premisas falsas, un inventario completo permite verificar ausencia; una búsqueda parcial no\..*?sin exigir detalles que no fueron preguntados\.",
                   reemplazo, base, flags=re.DOTALL)
    return nuevo


def aplicar_consenso_semantico_opcion2(draft, decision_auditor, evidence):
    """Opción 2: Lógica de consenso fáctico en el orquestador."""
    if decision_auditor.get("accion") == "corregir":
        palabras_ausencia = [
            "no existe", "no está disponible", "no figura", "no se encuentra",
            "ausente", "no incluye", "no contiene", "no se menciona", "no establece"
        ]
        msg = decision_auditor.get("mensaje", "").lower()
        draft_lower = draft.lower()
        auditor_ve_ausencia = any(p in msg for p in palabras_ausencia)
        redactor_ve_ausencia = any(p in draft_lower for p in palabras_ausencia)
        if auditor_ve_ausencia and redactor_ve_ausencia:
            # Hay acuerdo fáctico entre Redactor y Auditor
            return True
    return False


if __name__ == "__main__":
    preguntas = obtener_preguntas_p41_p50()
    print(f"Preguntas seleccionadas: {len(preguntas)} (IDs: {[p['id'] for p in preguntas]})")
    print("\n--- Vista previa Opción 1 (Prompt Auditor) ---")
    print(prompt_auditor_opcion1()[:400])
    print("\n--- Simulación Opción 2 (Consenso Semántico) ---")
    borrador_test = "El Artículo 90 del RI-FI no existe en esta copia según el inventario [INV-1]."
    decision_test = {"accion": "corregir", "mensaje": "Artículo 90 no está disponible según el inventario."}
    print("Consenso detectado:", aplicar_consenso_semantico_opcion2(borrador_test, decision_test, {}))
