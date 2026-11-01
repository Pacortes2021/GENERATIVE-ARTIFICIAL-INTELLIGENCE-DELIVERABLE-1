"""Prueba de la lógica del orquestador v3 con un modelo SIMULADO determinista.

El simulador responde solo en función del prompt que recibe (como Qwen3-4B en el notebook, con semilla fija derivada del prompt):
mismo prompt -> misma salida. Por eso un bucle de corrección solo puede cambiar el resultado si
el prompt del reintento es distinto (lleva el `motivo` del Verificador). La prueba lo comprueba.
"""
import sys, json, re
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from tools import Corpus
from orquestador import Orquestador, MODOS

C = Corpus(AQUI)

def ctx_de(prompt):
    return json.loads(prompt.split("Contexto:", 1)[1].strip())

def evidencia_ids(prompt):
    bloque = prompt.split("<evidencia>")[-1]
    return re.findall(r"\[((?:RI-FI|RG)-ART-\d{3}|CAL-2026-S[12]-\d{2})\]", bloque)

class Simulador:
    """Política fija por escenario: f(agente, prompt) -> str. Cuenta las llamadas."""
    def __init__(self, politica):
        self.politica, self.llamadas, self.prompts = politica, {}, {}
    def __call__(self, agente, prompt):
        self.llamadas[agente] = self.llamadas.get(agente, 0) + 1
        self.prompts.setdefault(agente, []).append(prompt)
        return self.politica[agente](prompt)

def correr(nombre, politica, pregunta):
    sim = Simulador(politica)
    r = Orquestador(C, sim).responder(pregunta)
    print(f"\n===== {nombre} =====\nPregunta: {pregunta}")
    print(f"tipo={r['tipo']} | ciclos={r['ciclos']} | veredicto={r['veredicto']}")
    for t in r["traza"]:
        sal = t["salida"] if isinstance(t["salida"], str) else json.dumps(t["salida"], ensure_ascii=False)
        obs = f"  obs={t['observacion']}" if t.get("observacion") else ""
        print(f"  [{t['paso']}] {t['agente']:11s} -> {sal[:75]}{obs}")
    print("Respuesta:", r["respuesta"][:110].replace("\n", " | "))
    return r, sim

aprobar = lambda p: '<pensar>todo {ok}</pensar>{"aprobado":true,"destino":"fin","motivo":"correcto"}'

# ---- A: CRUCE (2 sub-consultas; el Recuperador decide según la observación) ----
A = {
 "enrutador": lambda p: '{"tipo":"cruce","sub_consultas":["fechas inscripcion asignaturas segundo semestre 2026","minimo de creditos a inscribir por periodo"],"documentos":["CAL","RI-FI"]}',
 "recuperador": lambda p: ('{"accion":"suficiente","args":{}}' if ctx_de(p)["ultima_observacion"]
                           else json.dumps({"accion":"buscar","args":{"consulta":ctx_de(p)["sub"]}})),
 "redactor": lambda p: "<pensar>dos partes</pensar>Respuesta: inscripción 03-07 agosto [CAL-2026-S2-01]; mínimo 8 créditos [RI-FI-ART-008].\nFuente: [CAL-2026-S2-01] [RI-FI-ART-008]",
 "verificador": aprobar,
}
rA, sA = correr("A — CRUCE", A, "¿En qué fechas se inscriben las asignaturas del segundo semestre 2026 y cuál es el mínimo de créditos?")

# ---- B: PREMISA FALSA con artículo inexistente (rama decidida por el Enrutador) ----
B = {
 "enrutador": lambda p: '{"tipo":"premisa_falsa","sub_consultas":["articulo 45 RI-FI practica profesional"],"documentos":["RI-FI"]}',
 "recuperador": lambda p: '{"accion":"buscar","args":{"consulta":"practica"}}',
 "redactor": lambda p: ("Respuesta: El artículo 45 no figura en la normativa consultada; no hay respaldo para esa nota."
                        if "no_existe" in p else "Respuesta: 4,0 [RI-FI-ART-045]"),
 "verificador": aprobar,
}
rB, sB = correr("B — PREMISA FALSA (Art. 45)", B, "El Artículo 45 del Reglamento Interno de la Facultad de Ingeniería fija la nota mínima de la práctica profesional. ¿Cuál es?")

# ---- C: el Verificador rechaza una cita; el motivo viaja y el reintento cambia ----
def ver_C(p):
    chequeo = json.loads(p.split("<chequeo_citas>")[-1].split("</chequeo_citas>")[0])
    malas = [c["id"] for c in chequeo["citas"] if not c["en_evidencia"]]
    if malas:
        return json.dumps({"aprobado": False, "destino": "recuperador",
                           "motivo": f"la cita {malas[0]} no está en la evidencia; traer RI-FI art. 11"})
    return '{"aprobado":true,"destino":"fin","motivo":"cita respaldada"}'
C_ = {
 "enrutador": lambda p: '{"tipo":"factual","sub_consultas":["nota minima de aprobacion de asignatura"],"documentos":["RI-FI"]}',
 "recuperador": lambda p: ('{"accion":"traer","args":{"doc":"RI FI","n":"Art. 11"}}' if ctx_de(p)["feedback_verificador"] and not ctx_de(p)["ultima_observacion"]
                           else '{"accion":"suficiente","args":{}}' if ctx_de(p)["ultima_observacion"]
                           else '{"accion":"buscar","args":{"consulta":"asistencia"}}'),
 "redactor": lambda p: ("Respuesta: 4,0.\nFuente: [RI-FI-ART-011]" if "RI-FI-ART-011" in evidencia_ids(p)
                        else "Respuesta: 4,0.\nFuente: [RG-ART-050]"),
 "verificador": ver_C,
}
rC, sC = correr("C — VERIFICADOR RECHAZA y re-busca", C_, "¿Cuál es la nota mínima para aprobar una asignatura en Ingeniería?")

# ---- D: NUMÉRICA (el tipo cambia el modo del Redactor) + salidas desordenadas del modelo ----
D = {
 "enrutador": lambda p: 'Claro, aquí va: {"tipo":"numerica","sub_consultas":["ponderacion nota de titulacion memoria"],"documentos":["RI-FI"]} espero sirva',
 "recuperador": lambda p: ('{"accion":"suficiente","args":{}}' if ctx_de(p)["ultima_observacion"]
                           else '<pensar>es la nota de titulación {art 30}</pensar>{"accion":"existe","args":{"doc":"RI-FI","n":30}}'),
 "redactor": lambda p: ("Respuesta: 0,6×5,2 + 0,4×6,5 = 5,72.\nFuente: [RI-FI-ART-030]" if MODOS["numerica"] in p
                        else "Respuesta: no puedo calcular."),
 "verificador": lambda p: "no sé qué responder",          # salida ilegible -> no se aprueba
}
rD, sD = correr("D — NUMÉRICA + salidas desordenadas", D, "La Memoria obtuvo 6,5 y el promedio del plan (sin Memoria) fue 5,2. ¿Cuál es la nota de titulación?")

# ---------------------------------------------------------------- chequeos
print("\n===== CHEQUEOS =====")
def ok(cond, msg):
    assert cond, msg
    print("OK ", msg)

ok(rA["ciclos"] == 1 and sA.llamadas["recuperador"] == 4, "A: 2 sub-consultas x (buscar -> observar -> suficiente)")
ok({"CAL-2026-S2-01", "RI-FI-ART-008"} <= {t2 for t in rA["traza"] for t2 in (t.get("observacion") or {}).get("hits", [])},
   "A: el buscador trajo las dos fuentes necesarias")
ok("recuperador" not in sB.llamadas, "B: la rama premisa_falsa verificó existencia sin gastar búsquedas")
ok("no figura" in rB["respuesta"], "B: el Redactor se abstiene (estado no_existe)")
ok(rC["ciclos"] == 2 and "RI-FI-ART-011" in rC["respuesta"], "C: rechazo -> re-búsqueda -> respuesta corregida")
ok(sC.prompts["redactor"][0] != sC.prompts["redactor"][1], "C: el reintento recibe un prompt distinto (lleva el motivo)")
ok("traer RI-FI art. 11" in sC.prompts["recuperador"][-2], "C: el Recuperador recibe el motivo del Verificador")
ok(rC["veredicto"]["aprobado"] is True, "C: aprobado al final")
ok(rD["tipo"] == "numerica" and "5,72" in rD["respuesta"], "D: tipo numerica -> modo cálculo en el Redactor")
ok(any((t.get("observacion") or {}).get("traido") == "RI-FI-ART-030" for t in rD["traza"]),
   "D: 'existe' con razonamiento previo con llaves se interpreta bien y trae el artículo")
ok(rD["veredicto"]["aprobado"] is False, "D: veredicto ilegible -> NO se aprueba (antes se aprobaba en silencio)")
print("\nTodo con modelo SIMULADO determinista; en Colab se inyecta Qwen3-4B real.")

# ---- E: regresión con la salida REAL de Qwen3-4B (primera prueba en Colab, 2026-10-26) ----
# El Redactor copió su prompt antes de responder; el ejemplo [RI-FI-ART-011] de las reglas se
# coló como cita. La limpieza debe dejar solo la respuesta.
from orquestador import _limpiar_borrador, _cargar_prompt
ECO_REAL_45 = """<rol>
Eres el agente REDACTOR, experto en normativa de pregrado de Ingeniería UdeC. Redactas la
respuesta final a partir de la evidencia entregada.
</rol>

<reglas>
- Cita cada afirmación con el identificador exacto de la evidencia (ej.: [RI-FI-ART-011]).
</reglas>

<modo>La pregunta puede afirmar algo falso: contrástalo con la evidencia.</modo>

<razonamiento_interno>
El artículo 45 del Reglamento Interno de la Facultad de Ingeniería no existe en la normativa consultada.
</razonamiento_interno>

<formato_salida>
Respuesta: El Artículo 45 del Reglamento Interno de la Facultad de Ingeniería no figura en la normativa consultada. Por lo tanto, no se puede determinar la nota mínima de la práctica profesional según ese artículo.
Condiciones o límites: El estado de "no_existe" indica que el artículo no está disponible en la normativa consultada.
Fuente: [estado: no_existe | no existen en la normativa: RI-FI art. 45]
"""
limpio = _limpiar_borrador(ECO_REAL_45)
print("\n===== E — regresión con salida real =====\n" + limpio)
ok(limpio.startswith("Respuesta: El Artículo 45") and "<rol>" not in limpio and "Eres el agente" not in limpio,
   "E: la limpieza deja solo la respuesta (sin el prompt copiado)")
ok("RI-FI-ART-011" not in limpio, "E: desaparece la cita falsa [RI-FI-ART-011] que venía del ejemplo copiado")
ok(all(_cargar_prompt(f).lstrip().startswith("<rol>") for f in
       ["01_enrutador.txt", "02_recuperador.txt", "03_redactor.txt", "04_verificador.txt"]),
   "E: ningún prompt envía al modelo su cabecera de documentación '#'")
ok("RI-FI-ART-011" not in _cargar_prompt("03_redactor.txt"), "E: el prompt del Redactor ya no trae un ID de ejemplo que se pueda colar")
ok(_cargar_prompt("03_redactor.txt").rstrip().endswith("Fuente: (identificadores entre corchetes)"),
   "E: el prompt del Redactor termina con la orden de la tarea, no con datos")

# ---- F: regresión v5 con los patrones reales de la corrida v4 (2026-10-26) ----
import orquestador as O
# F1-F4: el Recuperador repite SIEMPRE la misma búsqueda (P6) y copia "existe art. 90" (P7).
llamadas_rec = {"n": 0}
def rec_F(p):
    llamadas_rec["n"] += 1
    return '{"accion":"existe","args":{"doc":"RI-FI","n":90}}' if llamadas_rec["n"] == 1 \
        else '{"accion":"buscar","args":{"consulta":"minima anticipacion para comunicar evaluaciones","k":5}}'
F = {
 "enrutador": lambda p: '{"tipo":"factual","sub_consultas":["minima anticipacion para comunicar evaluaciones","plazo para informar certamenes"],"documentos":["RI-FI"]}',
 "recuperador": rec_F,
 "redactor": lambda p: "Respuesta: no menos de una semana [RI-FI-ART-010]\nFuente: [RI-FI-ART-010]",
 "verificador": lambda p: ('{"aprobado":false,"destino":"redactor","motivo":"falta la condición del syllabus"}'
                           if len(sF_prompts_red) == 1 else
                           '{"aprobado":true,"destino":"fin","motivo":"ok"}'),
}
sF_prompts_red = []
_red = F["redactor"]
F["redactor"] = lambda p: (sF_prompts_red.append(p), _red(p))[1]
rF, sF = correr("F — patrones reales v4: repetición + ejemplo copiado", F,
                "¿Con cuánta anticipación mínima deben comunicarse las evaluaciones a los estudiantes?")
recs = [t for t in rF["traza"] if t["agente"] == "recuperador"]
base = [t for t in recs if t.get("decidido_por") == "sistema"]
ok(len(base) == 1 and base[0]["salida"]["args"]["consulta"].startswith("¿Con cuánta"),
   "F: búsqueda base con la pregunta original, una sola vez")
ok(any("existe art. 90 no mencionado" in (t.get("corregido") or "") for t in recs),
   "F: 'existe art. 90' copiado del ejemplo se reemplaza por una búsqueda")
ejecutada = lambda t: t.get("accion_ejecutada") or t["salida"]
ejec = [t for t in recs if (t.get("observacion") or {}).get("hits") is not None
        and ejecutada(t).get("args", {}).get("consulta", "").startswith("minima anticipacion")]
rep = [t for t in recs if (t.get("observacion") or {}).get("repetida")]
ok(len(ejec) == 1 and len(rep) >= 3, f"F: la búsqueda repetida se ejecuta 1 vez y se bloquea {len(rep)} veces")
ok(all(len(re.findall(r"^\[(?:RI-FI|RG|CAL)", p, re.M)) <= O.MAX_EVIDENCIA for p in sF_prompts_red),
   f"F: al Redactor llegan como máximo {O.MAX_EVIDENCIA} artículos")
ok(len(sF_prompts_red) == 2 and "falta la condición del syllabus" in sF_prompts_red[1]
   and "falta la condición del syllabus" not in sF_prompts_red[0],
   "F: en el reintento el Redactor recibe el motivo del Verificador (prompts v6 = v4)")

# F6: no bloquear de más: traer un número que aparece en lo observado SÍ se permite.
o = Orquestador(C, lambda a, p: "")
o._pool, o._puntaje = {"RI-FI-ART-030": {"id": "RI-FI-ART-030", "texto": "x"}}, {"RI-FI-ART-030": 1}
ok(o._numero_permitido(30, "nota de titulacion", "¿Cuál es la nota?", None) and
   not o._numero_permitido(90, "nota de titulacion", "¿Cuál es la nota?", None),
   "F: se permite un número visto en la evidencia y se bloquea uno inventado")
ok(not re.search(r'"n":\s*\d', _cargar_prompt("02_recuperador.txt")) and "baja académica" not in _cargar_prompt("02_recuperador.txt"),
   "F: el prompt del Recuperador ya no trae números ni frases de ejemplo que copiar")

# ---- G: ablaciones (cada una quita UNA técnica de UN agente; el resto queda idéntico) ----
import orquestador as O2
def grabar(ablacion, pregunta="¿Cuál es la nota mínima para aprobar una asignatura en Ingeniería?"):
    prompts = {}
    def gen(agente, p):
        prompts.setdefault(agente, []).append(p)
        return {"enrutador": '{"tipo":"factual","sub_consultas":["nota minima aprobacion"],"documentos":["RI-FI"]}',
                "recuperador": '{"accion":"suficiente","args":{}}',
                "redactor": "Respuesta: 4,0\nFuente: [RI-FI-ART-011]",
                "verificador": '{"aprobado":true,"destino":"fin","motivo":"ok"}'}[agente]
    r = O2.Orquestador(C, gen, ablacion=ablacion).responder(pregunta)
    return r, prompts
completo, P0 = grabar(None)
print("\n===== G — ablaciones =====")
for nombre in O2.ABLACIONES: print(" ", nombre, "→", O2.ABLACIONES[nombre])
_, Pf = grabar("sin_fewshot")
ok("<ejemplos>" in P0["enrutador"][0] and "<ejemplos>" not in Pf["enrutador"][0]
   and Pf["redactor"] == P0["redactor"] and Pf["verificador"] == P0["verificador"],
   "G: sin_fewshot quita solo los ejemplos del Enrutador")
_, Pc = grabar("sin_cot")
ok("Primero razona paso a paso" in P0["redactor"][0] and "Primero razona" not in Pc["redactor"][0]
   and "Escribe solo estas tres líneas:" in Pc["redactor"][0]
   and Pc["enrutador"] == P0["enrutador"] and Pc["verificador"] == P0["verificador"],
   "G: sin_cot quita solo la instrucción de razonar del Redactor")
rr, Pr = grabar("sin_react")
ok("recuperador" in P0 and "recuperador" not in Pr
   and any(t.get("decidido_por") == "sistema" for t in rr["traza"]),
   "G: sin_react no llama al Recuperador (queda la búsqueda base)")
rv, Pv = grabar("sin_verificador")
ok("verificador" not in Pv and rv["ciclos"] == 1 and rv["respuesta"] == completo["respuesta"],
   "G: sin_verificador entrega el primer borrador sin llamar al Verificador")
try:
    O2.Orquestador(C, lambda a, p: "", ablacion="sin_algo"); malo = False
except ValueError:
    malo = True
ok(malo, "G: una ablación con nombre inválido se rechaza")
ok(completo.get("ablacion") is None and rv.get("ablacion") == "sin_verificador",
   "G: cada resultado registra qué ablación se usó")
