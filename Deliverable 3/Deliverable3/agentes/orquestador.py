"""Orquestador del sistema de 4 agentes (D3) — v6 (código v5; prompts de Redactor y Verificador de la v4) + ablaciones.

Enrutador -> Recuperador (ReAct) -> Redactor -> Verificador, con bucles y registro de trazas.
El acceso al modelo se INYECTA como `generar(agente, prompt) -> str`: en Colab es Qwen3-4B,
en pruebas un modelo simulado.

Decisiones que toma cada agente y cómo cambian el flujo:
  * Enrutador: el `tipo` ramifica. `premisa_falsa` con artículo explícito -> se verifica su
    existencia directamente (sin gastar búsquedas); el `tipo` también fija el MODO del Redactor
    (cálculo, contraste de premisa, varias partes, condiciones). Cada sub-consulta abre su
    propio ciclo ReAct.
  * Recuperador: en cada turno elige buscar / traer / existe / suficiente, viendo la
    observación anterior.
  * Verificador: aprueba (fin), devuelve al Redactor o al Recuperador. Su `motivo` viaja
    como retroalimentación, de modo que el reintento recibe un prompt distinto (con
    decodificación determinista, reintentar con el mismo prompt no cambiaría nada).
Topes: ReAct <= 3 acciones por sub-consulta; <= 2 ciclos de corrección.

v5 (tras la corrida real del 2026-10-26; mecanismos generales, no parches por pregunta):
  * Búsqueda base con la pregunta ORIGINAL antes del ReAct (como el RAG del E2).
  * Una acción idéntica a otra ya hecha en la misma pregunta no se repite: se avisa al
    Recuperador que reformule (en la corrida v4, 31% de sus acciones eran repeticiones).
  * `traer`/`existe` con un número de artículo que no aparece en la pregunta, la sub-consulta,
    la corrección del Verificador ni en lo ya observado se trata como copia de un ejemplo y se
    reemplaza por una búsqueda.
  * Al Redactor y al Verificador llegan solo los MAX_EVIDENCIA artículos más relevantes.
  * En un reintento, el Redactor recibe su borrador anterior además del motivo.
"""
import json, re
from pathlib import Path

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"
TIPOS = {"factual", "numerica", "condicional", "cruce", "premisa_falsa"}
ACCIONES = {"buscar", "traer", "existe", "suficiente"}
DESTINOS = {"fin", "redactor", "recuperador"}
MAX_EVIDENCIA = 6

# ---------------------------------------------------------------- ablaciones (D3)
# Cada ablación quita UNA técnica clave de UN agente; el resto del sistema queda idéntico a la v6.
# Se aplican en el código (los archivos de prompts no cambian) y fallan si el bloque no se encuentra.
ABLACIONES = {
    "sin_fewshot": "Enrutador sin los ejemplos few-shot (bloque <ejemplos>)",
    "sin_react": "Recuperador sin ciclo ReAct: solo la búsqueda base con la pregunta original",
    "sin_cot": "Redactor sin la instrucción de razonar paso a paso en <pensar>",
    "sin_verificador": "Sin Verificador: se entrega el primer borrador del Redactor",
}
_FEWSHOT = re.compile(r"\n<ejemplos>.*?</ejemplos>\n", re.S)
_COT = ("Primero razona paso a paso dentro de <pensar>...</pensar> (qué dice cada evidencia y qué parte\n"
        "de la pregunta cubre; si hay observaciones del verificador, corrígelas). Después escribe solo\n"
        "estas tres líneas:")
_COT_SIN = "Escribe solo estas tres líneas:"

# Modo del Redactor según el tipo decidido por el Enrutador (rama real del flujo).
MODOS = {
    "factual": "Responde el dato pedido de forma directa.",
    "numerica": ("La pregunta exige un cálculo o una comparación numérica: hazlo con las cifras "
                 "de la evidencia y las que entrega la pregunta, mostrando la operación."),
    "condicional": "Enumera todas las condiciones, plazos y excepciones que correspondan.",
    "cruce": "La pregunta tiene varias partes: responde cada una por separado, con su fuente.",
    "premisa_falsa": ("La pregunta puede afirmar algo falso: contrástalo con la evidencia y, si no "
                      "se sostiene, dilo y corrígelo. Nunca confirmes un dato que la evidencia no respalda."),
}

# ---------------------------------------------------------------- utilidades
def _cargar_prompt(archivo):
    """Lee el prompt SIN su cabecera de documentación (líneas iniciales con '#').
    La cabecera es para el repositorio; enviada al modelo, éste tiende a copiarla."""
    lineas = (PROMPTS / archivo).read_text(encoding="utf-8").splitlines()
    while lineas and (lineas[0].startswith("#") or not lineas[0].strip()):
        lineas.pop(0)
    return "\n".join(lineas)

def _sin_pensar(texto):
    """Quita el razonamiento interno (<pensar>/<think>) de la salida del modelo."""
    t = re.sub(r"<(pensar|think)>.*?</\1>", "", texto or "", flags=re.S)
    t = re.sub(r"<(pensar|think)>.*", "", t, flags=re.S)   # bloque sin cerrar (salida cortada)
    return t.strip()

def _limpiar_borrador(texto):
    """Rescata la respuesta del Redactor aunque el modelo haya copiado parte del prompt:
    quita el razonamiento, toma desde el ÚLTIMO 'Respuesta:' y elimina etiquetas sueltas."""
    t = _sin_pensar(texto)
    i = t.rfind("Respuesta:")
    if i >= 0:
        t = t[i:]
    t = re.sub(r"</?[a-z_]+>", "", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()

def _json_de(texto):
    """Último objeto JSON de nivel superior en la salida (ignora el razonamiento previo)."""
    t, dec, i, ultimo = _sin_pensar(texto), json.JSONDecoder(), 0, None
    while i < len(t):
        if t[i] == "{":
            try:
                obj, fin = dec.raw_decode(t[i:])
                if isinstance(obj, dict):
                    ultimo = obj
                i += fin
                continue
            except ValueError:
                pass
        i += 1
    return ultimo

def _doc_n(args):
    """Normaliza los argumentos doc/n que propone el modelo ('RI FI', 'Art. 11', ...)."""
    d = re.sub(r"[^A-Z]", "", str(args.get("doc", "")).upper())
    doc = {"RIFI": "RI-FI", "RI": "RI-FI", "RG": "RG"}.get(d)
    m = re.search(r"\d+", str(args.get("n", "")))
    return doc, (int(m.group(0)) if m else None)

def _articulo_en(pregunta):
    """Artículo citado explícitamente en la pregunta -> (doc, n) o None."""
    m = re.search(r"art(?:[íi]culo|\.)\s*(\d+)", pregunta, re.I)
    if not m:
        return None
    doc = "RG" if re.search(r"reglamento general|\bRG\b", pregunta, re.I) else "RI-FI"
    return doc, int(m.group(1))

def _extracto(e, n=160):
    return {"id": e["id"], "extracto": (e.get("texto") or "")[:n]}


class Orquestador:
    def __init__(self, corpus, generar, max_react=3, max_ciclos=2, ablacion=None):
        if ablacion is not None and ablacion not in ABLACIONES:
            raise ValueError(f"Ablación desconocida: {ablacion}. Opciones: {sorted(ABLACIONES)}")
        self.ablacion = ablacion
        self.c = corpus
        self.generar = generar            # f(agente:str, prompt:str) -> str
        self.max_react = max_react
        self.max_ciclos = max_ciclos
        self.traza = []

    def _prompt(self, archivo):
        """Prompt del agente; si hay ablación, quita exactamente su bloque (o falla si no está)."""
        p = _cargar_prompt(archivo)
        if self.ablacion == "sin_fewshot" and archivo == "01_enrutador.txt":
            p, n = _FEWSHOT.subn("\n", p)
            if n != 1:
                raise RuntimeError("sin_fewshot: no se encontró el bloque <ejemplos> del Enrutador")
        if self.ablacion == "sin_cot" and archivo == "03_redactor.txt":
            if p.count(_COT) != 1:
                raise RuntimeError("sin_cot: no se encontró la instrucción de razonamiento del Redactor")
            p = p.replace(_COT, _COT_SIN)
        return p

    def _log(self, agente, entrada, salida, extra=None):
        self.traza.append({"paso": len(self.traza) + 1, "agente": agente,
                           "entrada": entrada, "salida": salida, **(extra or {})})

    # ------------------------------------------------ Agente 1: Enrutador
    def enrutar(self, pregunta):
        p = self._prompt("01_enrutador.txt").replace("{{PREGUNTA}}", pregunta)
        crudo = self.generar("enrutador", p)
        plan = _json_de(crudo) or {}
        fallback = not plan
        tipo = plan.get("tipo") if plan.get("tipo") in TIPOS else "factual"
        subs = [s for s in plan.get("sub_consultas", []) if isinstance(s, str) and s.strip()][:4]
        plan = {"tipo": tipo, "sub_consultas": subs or [pregunta],
                "documentos": plan.get("documentos", [])}
        self._log("enrutador", pregunta, plan, {"fallback": fallback})
        return plan

    # ------------------------------------------------ Agente 2: Recuperador (ReAct)
    def _sumar(self, e, puntos):
        """Agrega un artículo al conjunto de evidencia de la pregunta y acumula su relevancia."""
        if not e.get("texto"):
            return
        if e["id"] not in self._pool:
            self._pool[e["id"]] = e
        self._puntaje[e["id"]] = self._puntaje.get(e["id"], 0.0) + puntos

    def _seleccion(self):
        """Los MAX_EVIDENCIA artículos más relevantes (traídos explícitamente o repetidos en varias búsquedas)."""
        orden = sorted(self._pool, key=lambda i: -self._puntaje[i])
        return [self._pool[i] for i in orden[:MAX_EVIDENCIA]]

    def _numero_permitido(self, n, sub, pregunta, feedback):
        """¿El número de artículo viene de la pregunta, la sub-consulta, la corrección o lo observado?"""
        texto = " ".join([pregunta, sub, feedback or ""])
        if re.search(rf"(?<!\d){n}(?!\d)", texto):
            return True
        return any(re.search(rf"-ART-0*{n}$", i) for i in self._pool)

    def _buscar(self, consulta, k, origen):
        """La búsqueda base (pregunta original, la del E2) pesa el doble al elegir la evidencia:
        con la pregunta original el artículo correcto quedó en el top-5 en 34/38 preguntas del set
        congelado, frente a 29/38 con las búsquedas del Recuperador v4."""
        peso = 2.0 if origen == "base" else 1.0
        hits = self.c.buscar(consulta, k)
        for r, h in enumerate(hits):
            self._sumar(h, peso / (r + 1))
        return hits

    def recuperar(self, plan, pregunta, feedback=None):
        inexistentes = []

        # Rama decidida por el Enrutador: premisa falsa con artículo explícito.
        if plan["tipo"] == "premisa_falsa":
            ref = _articulo_en(pregunta)
            if ref:
                ok = self.c.existe_articulo(*ref)
                obs = {"existe": ok}
                if ok:
                    art = self.c.traer_articulo(*ref)
                    self._sumar(art, 3.0)
                    obs["traido"] = art["id"]
                else:
                    inexistentes.append(f"{ref[0]} art. {ref[1]}")
                self._log("recuperador", {"rama": "premisa_falsa", "pregunta": pregunta},
                          {"accion": "existe", "args": {"doc": ref[0], "n": ref[1]}},
                          {"observacion": obs, "decidido_por": "enrutador"})
                if not ok:
                    return {"evidencia": [], "estado": "no_existe", "inexistentes": inexistentes}

        # Búsqueda base con la pregunta original (una vez por pregunta), como el RAG del E2.
        if not self._base_hecha:
            self._base_hecha = True
            hits = self._buscar(pregunta, 5, "base")
            self._hechas.add(("buscar", pregunta.strip().lower()))
            self._log("recuperador", {"rama": "busqueda_base", "pregunta": pregunta},
                      {"accion": "buscar", "args": {"consulta": pregunta, "k": 5}},
                      {"observacion": {"hits": [h["id"] for h in hits]}, "decidido_por": "sistema"})

        for sub in ([] if self.ablacion == "sin_react" else plan["sub_consultas"]):
            ultima_obs = None
            for intento in range(self.max_react):
                ctx = {"sub": sub, "tipo": plan["tipo"], "documentos": plan["documentos"],
                       "evidencia_reunida": [e["id"] for e in self._seleccion()],
                       "ultima_observacion": ultima_obs,
                       "intento": intento + 1, "feedback_verificador": feedback}
                p = self._prompt("02_recuperador.txt").replace(
                    "{{PLAN}}", json.dumps(ctx, ensure_ascii=False))
                dec = _json_de(self.generar("recuperador", p))
                fallback = not dec or dec.get("accion") not in ACCIONES
                if fallback:
                    dec = {"accion": "buscar", "args": {"consulta": sub}}
                accion, args = dec["accion"], dec.get("args") or {}
                obs, extra = None, {"fallback": fallback}

                # Número de artículo que no viene de ningún lado: copia de un ejemplo -> buscar.
                if accion in ("traer", "existe"):
                    doc, n = _doc_n(args)
                    if n is not None and not self._numero_permitido(n, sub, pregunta, feedback):
                        extra["corregido"] = f"{accion} art. {n} no mencionado: se busca la sub-consulta"
                        accion, args = "buscar", {"consulta": sub, "k": 5}
                        extra["accion_ejecutada"] = {"accion": accion, "args": args}

                if accion in ("buscar", "traer", "existe"):
                    clave = (accion, (args.get("consulta") or "").strip().lower()) if accion == "buscar" \
                        else (accion,) + _doc_n(args)
                    if clave in self._hechas:
                        obs = {"repetida": True}
                        ultima_obs = {"aviso": "Ya hiciste exactamente esta acción y no aportó nada nuevo. "
                                               "Busca con OTRAS palabras o responde 'suficiente'."}
                        self._log("recuperador", ctx, dec, {"observacion": obs, **extra})
                        continue
                    self._hechas.add(clave)

                if accion == "existe":
                    doc, n = _doc_n(args)
                    ok = bool(doc and n is not None and self.c.existe_articulo(doc, n))
                    obs = {"existe": ok}
                    if ok:
                        art = self.c.traer_articulo(doc, n)
                        self._sumar(art, 3.0)
                        obs["traido"] = art["id"]
                        ultima_obs = [_extracto(art)]
                    else:
                        inexistentes.append(f"{doc or args.get('doc')} art. {n if n is not None else args.get('n')}")
                elif accion == "traer":
                    doc, n = _doc_n(args)
                    art = self.c.traer_articulo(doc, n) if (doc and n is not None) else {"id": None, "texto": None}
                    if art["texto"]:
                        self._sumar(art, 3.0)
                        obs = {"traido": art["id"]}
                        ultima_obs = [_extracto(art)]
                    else:
                        obs = {"error": f"no existe {args}"}
                        ultima_obs = obs
                elif accion == "buscar":
                    hits = self._buscar(args.get("consulta") or sub, int(args.get("k", 5) or 5), "react")
                    obs = {"hits": [h["id"] for h in hits]}
                    ultima_obs = [_extracto(h) for h in hits]

                self._log("recuperador", ctx, dec, {"observacion": obs, **extra})
                if accion == "suficiente" or (accion == "existe" and not obs["existe"]):
                    break

        evidencia = self._seleccion()
        if inexistentes and not evidencia:
            estado = "no_existe"
        elif not evidencia:
            estado = "insuficiente"
        else:
            estado = "suficiente"
        return {"evidencia": evidencia, "estado": estado, "inexistentes": inexistentes}

    # ------------------------------------------------ Agente 3: Redactor
    def redactar(self, pregunta, ev, tipo, feedback=None, anterior=None):
        cab = f"estado: {ev['estado']}"
        if ev.get("inexistentes"):
            cab += f" | no existen en la normativa: {', '.join(ev['inexistentes'])}"
        bloque = "\n".join(f"[{e['id']}] {e['texto']}" for e in ev["evidencia"]) or "(sin evidencia)"
        p = (self._prompt("03_redactor.txt")
             .replace("{{PREGUNTA}}", pregunta)
             .replace("{{MODO}}", MODOS.get(tipo, MODOS["factual"]))
             .replace("{{FEEDBACK}}", feedback or "(primera versión, sin observaciones)")
             .replace("{{BORRADOR_ANTERIOR}}", anterior or "(no hay: es la primera versión)")
             .replace("{{EVIDENCIA}}", f"{cab}\n{bloque}"))
        crudo = self.generar("redactor", p)
        borrador = _limpiar_borrador(crudo)
        self._log("redactor", {"pregunta": pregunta, "modo": tipo, "estado": ev["estado"],
                               "feedback": feedback}, borrador,
                  {"salida_cruda": crudo} if crudo.strip() != borrador else None)
        return borrador

    # ------------------------------------------------ Agente 4: Verificador
    def chequear_citas(self, borrador, ev):
        """Herramienta del Verificador: ¿cada cita existe en la normativa y está en la evidencia?"""
        citados = sorted(set(re.findall(r"(?:RI-FI|RG)-ART-\d{3}|CAL-2026-S[12]-\d{2}", borrador)))
        en_ev = {e["id"] for e in ev["evidencia"]}
        out = []
        for cid in citados:
            m = re.match(r"(RI-FI|RG)-ART-(\d+)", cid)
            existe = self.c.existe_articulo(m.group(1), int(m.group(2))) if m else cid in self.c.por_id
            out.append({"id": cid, "existe": existe, "en_evidencia": cid in en_ev})
        return {"citas": out, "sin_citas": not citados}

    def verificar(self, pregunta, ev, borrador):
        chequeo = self.chequear_citas(borrador, ev)
        bloque = "\n".join(f"[{e['id']}] {(e['texto'] or '')[:700]}" for e in ev["evidencia"]) \
                 or "(sin evidencia)"
        p = (self._prompt("04_verificador.txt")
             .replace("{{PREGUNTA}}", pregunta)
             .replace("{{EVIDENCIA}}", f"estado: {ev['estado']}\n{bloque}")
             .replace("{{CHEQUEO}}", json.dumps(chequeo, ensure_ascii=False))
             .replace("{{BORRADOR}}", borrador))
        ver = _json_de(self.generar("verificador", p))
        fallback = not ver or ver.get("destino") not in DESTINOS
        if fallback:   # sin veredicto legible: se cierra SIN aprobar (y queda registrado)
            ver = {"aprobado": False, "destino": "fin", "motivo": "veredicto no interpretable"}
        ver["aprobado"] = bool(ver.get("aprobado")) and ver["destino"] == "fin"
        self._log("verificador", {"borrador": borrador[:200], "chequeo_citas": chequeo}, ver,
                  {"fallback": fallback})
        return ver

    # ------------------------------------------------ Bucle completo
    def responder(self, pregunta):
        self.traza, self._pool, self._puntaje, self._hechas, self._base_hecha = [], {}, {}, set(), False
        plan = self.enrutar(pregunta)
        ev = self.recuperar(plan, pregunta)
        feedback, borrador = None, None
        for ciclo in range(self.max_ciclos + 1):
            borrador = self.redactar(pregunta, ev, plan["tipo"], feedback, anterior=borrador)
            if self.ablacion == "sin_verificador":
                ver = {"aprobado": None, "destino": "fin", "motivo": "ablación sin Verificador"}
                break
            ver = self.verificar(pregunta, ev, borrador)
            if ver["destino"] == "fin" or ciclo == self.max_ciclos:
                break
            feedback = ver.get("motivo") or "corrige según los criterios"
            if ver["destino"] == "recuperador":
                nueva = self.recuperar(plan, pregunta, feedback=feedback)
                ev = {"evidencia": nueva["evidencia"],
                      "inexistentes": sorted(set(ev.get("inexistentes", []) + nueva.get("inexistentes", [])))}
                ev["estado"] = "suficiente" if ev["evidencia"] else nueva["estado"]
        return {"respuesta": borrador, "veredicto": ver, "ciclos": ciclo + 1,
                "tipo": plan["tipo"], "ablacion": self.ablacion, "traza": self.traza}
