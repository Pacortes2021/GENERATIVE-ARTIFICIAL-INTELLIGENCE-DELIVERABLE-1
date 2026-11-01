"""Visualización y registro adicional para el video; no cambia decisiones de v6."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import base64
import csv
import hashlib
import html
import json
import time
import uuid
import zipfile
from orquestador import Orquestador


def utc():
    return datetime.now(timezone.utc).isoformat()


def guardar_json(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)


def serial(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)


def bloque(value, altura=180):
    return (f'<pre style="white-space:pre-wrap;overflow-wrap:anywhere;max-height:{altura}px;overflow:auto;'
            'font:14px/1.4 ui-monospace,monospace;margin:8px 0;padding:10px;background:#f5f8fa;'
            'border:1px solid #dbe4eb;border-radius:5px">' + html.escape(serial(value)) + '</pre>')


def mostrar_html(content):
    from IPython.display import HTML, display
    display(HTML(content))


def marco(title, body, color='#14334b'):
    return (f'<section style="font:17px/1.4 system-ui;color:#172b3a;background:white;'
            f'border:1px solid #cad5de;border-left:6px solid {color};padding:16px;max-width:1100px">'
            f'<h3 style="margin:0 0 10px;color:{color}">{html.escape(title)}</h3>{body}</section>')


class CorpusObservado:
    def __init__(self, corpus, registrar):
        self._corpus, self._registrar = corpus, registrar

    def __getattr__(self, name):
        return getattr(self._corpus, name)

    def _usar(self, nombre, *args, **kwargs):
        inicio = time.perf_counter()
        resultado = getattr(self._corpus, nombre)(*args, **kwargs)
        self._registrar(nombre, {'args': args, 'kwargs': kwargs}, resultado, time.perf_counter() - inicio)
        return resultado

    def buscar(self, *args, **kwargs):
        return self._usar('buscar', *args, **kwargs)

    def traer_articulo(self, *args, **kwargs):
        return self._usar('traer_articulo', *args, **kwargs)

    def existe_articulo(self, *args, **kwargs):
        return self._usar('existe_articulo', *args, **kwargs)


class SesionDemo:
    """Una ejecución independiente; persiste incluso si falla o se interrumpe."""
    def __init__(self, corpus, generar, carpeta, entorno, caso, pregunta, visible=True):
        self.id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '_' + uuid.uuid4().hex[:8]
        self.carpeta = Path(carpeta) / self.id
        self.carpeta.mkdir(parents=True, exist_ok=False)
        self.visible, self.panel = visible, None
        self.generar_base = generar
        self.inicio = time.perf_counter()
        self.fin = None
        self.datos = {'run_id': self.id, 'origen': 'inferencia_real', 'caso': caso,
                      'pregunta': pregunta, 'inicio_utc': utc(), 'estado': 'preparada',
                      'entorno': copy.deepcopy(entorno), 'llamadas': [], 'herramientas': [],
                      'intercambios': [], 'resultado': None}
        sesion = self

        class Observado(Orquestador):
            def _log(self, agente, entrada, salida, extra=None):
                super()._log(agente, entrada, salida, extra)
                sesion.datos['intercambios'].append(copy.deepcopy(self.traza[-1]))
                sesion._evento('intercambio', self.traza[-1])
                sesion._mostrar()

            def chequear_citas(self, borrador, ev):
                t = time.perf_counter()
                valor = super().chequear_citas(borrador, ev)
                sesion._herramienta('chequear_citas', {'borrador': borrador, 'evidencia': ev},
                                    valor, time.perf_counter() - t)
                return valor

        self.orq = Observado(CorpusObservado(corpus, self._herramienta), self._generar)
        self._guardar()

    def _guardar(self):
        self.datos['segundos'] = round((self.fin if self.fin is not None else time.perf_counter()) - self.inicio, 3)
        guardar_json(self.carpeta/'sesion.json', self.datos)

    def _evento(self, tipo, datos):
        with (self.carpeta/'eventos.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps({'utc': utc(), 'tipo': tipo, 'datos': datos}, ensure_ascii=False) + '\n')
        self._guardar()

    def _herramienta(self, nombre, entrada, salida, segundos):
        item = {'nombre': nombre, 'entrada': copy.deepcopy(entrada),
                'salida': copy.deepcopy(salida), 'segundos': round(segundos, 4)}
        self.datos['herramientas'].append(item)
        self._evento('herramienta', item)

    def _generar(self, agente, prompt):
        call = {'numero': len(self.datos['llamadas'])+1, 'agente': agente,
                'inicio_utc': utc(), 'estado': 'generando',
                'mensajes': [{'role': 'user', 'content': prompt}],
                'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest()}
        self.datos['llamadas'].append(call)
        self.datos['activo'] = agente
        self._evento('llamada_inicio', call)
        self._mostrar()
        t = time.perf_counter()
        try:
            salida = self.generar_base(agente, prompt)
        except BaseException as e:
            call.update(estado='error', error=type(e).__name__ + ': ' + str(e), segundos=round(time.perf_counter()-t, 3))
            self._evento('llamada_error', call)
            raise
        call.update(estado='completa', salida_cruda=salida, fin_utc=utc(), segundos=round(time.perf_counter()-t, 3))
        self.datos['activo'] = None
        self._evento('llamada_fin', call)
        return salida

    def ejecutar(self):
        self.inicio = time.perf_counter()
        self.datos['estado'] = 'ejecutando'
        self._mostrar()
        try:
            resultado = self.orq.responder(self.datos['pregunta'])
            self.fin = time.perf_counter()
            self.datos.update(estado='completa', resultado=resultado, activo=None, fin_utc=utc())
            self._evento('resultado', resultado)
            return resultado
        except BaseException as e:
            self.fin = time.perf_counter()
            self.datos.update(estado='interrumpida' if isinstance(e, KeyboardInterrupt) else 'error',
                              error=type(e).__name__ + ': ' + str(e), activo=None, fin_utc=utc())
            self._evento('error', self.datos['error'])
            raise
        finally:
            self._guardar()
            self._mostrar()

    def _mostrar(self):
        if not self.visible:
            return
        from IPython.display import HTML, display
        d = self.datos
        actual = f"Generando: {d['activo']}" if d.get('activo') else d['estado']
        body = '<p><b>EJECUCIÓN REAL · Qwen3-4B</b> · ' + html.escape(actual) + '</p>'
        body += '<p><b>Consulta:</b> ' + html.escape(d['pregunta']) + '</p>'
        body += f'<p>Llamadas al modelo: <b>{len(d["llamadas"])}</b> · Duración: <b>{(self.fin if self.fin is not None else time.perf_counter())-self.inicio:.1f} s</b></p>'
        if d['resultado']:
            body += '<h3>Respuesta final</h3>' + bloque(d['resultado']['respuesta'],280)
            body += '<b>Veredicto interno</b>' + bloque(d['resultado']['veredicto'],150)
            body += '<p style="font-size:14px">La aprobación interna no mide exactitud.</p>'
        def intercambio(e, abierto=False):
            auto = ' · acción automática' if e.get('decidido_por') else ''
            apertura = ' open' if abierto else ''
            text = f'<details{apertura} style="border-top:1px solid #dbe4eb;padding:7px 0"><summary><b>{e["paso"]}. {html.escape(e["agente"].upper())}{auto}</b></summary>'
            text += '<b>Entrada registrada:</b>' + bloque(e['entrada'])
            text += '<b>Salida / decisión:</b>' + bloque(e['salida'])
            if e.get('observacion') is not None:
                text += '<b>Observación:</b>' + bloque(e['observacion'])
            return text + '</details>'
        if d['intercambios']:
            body += '<h4 style="margin-bottom:6px">Último intercambio</h4>' + intercambio(d['intercambios'][-1],True)
            anteriores = d['intercambios'][:-1]
            if anteriores:
                body += f'<details><summary>Historial anterior ({len(anteriores)} intercambios)</summary>'
                body += ''.join(intercambio(e) for e in anteriores) + '</details>'
        if d.get('error'):
            body += '<p><b>Ejecución detenida:</b> ' + html.escape(d['error']) + '</p>'
        body += '<p style="font-size:12px;color:#52616b">Registro: ' + html.escape(self.id) + '</p>'
        content = HTML(marco('H17 · Reglas de asistencia y excepciones' if d['caso']=='H17' else 'Consulta '+str(d['caso']),body))
        if self.panel is None:
            self.panel = display(content, display_id=True)
        else:
            self.panel.update(content)


def mostrar_portada(base):
    grafico = Path(base)/'documento/grafo_compacto.png'
    imagen = base64.b64encode(grafico.read_bytes()).decode('ascii')
    body = '<p>Un agente combina un rol, un prompt propio y una decisión sobre cómo continuar según lo observado.</p>'
    body += f'<img src="data:image/png;base64,{imagen}" alt="Grafo de cuatro roles, herramientas y retornos de revisión" style="width:100%;height:auto;display:block">'
    roles = [('Enrutador','Clasifica y descompone la consulta.'),
             ('Recuperador','Elige herramientas y reúne evidencia.'),
             ('Redactor','Construye o corrige una respuesta con citas.'),
             ('Verificador','Decide terminar o pedir correcciones.')]
    body += '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:10px">'
    for rol,funcion in roles:
        body += '<div style="background:#eaf3f8;padding:9px;font-size:14px"><b>'+rol+'</b><br>'+funcion+'</div>'
    body += '</div><p style="font-size:14px">Enrutador, Recuperador y Verificador deciden el recorrido; el Redactor entrega su borrador al Verificador.</p>'
    body += '<p style="font-size:14px"><b>Qwen3-4B en todos los roles</b> · E5 para recuperar evidencia · Hasta 2 ciclos de corrección</p>'
    mostrar_html(marco('D3 · Arquitectura de agentes',body))


def cargar_fallo(base):
    base = Path(base)
    path = base/'resultados_v6/trazas_D3.json'
    traza = json.loads(path.read_text())['dificil_25:H03']
    with (base/'resultados_v6/resultados_agentes_D3.csv').open(encoding='utf-8-sig', newline='') as f:
        fila = next(r for r in csv.DictReader(f) if r['id']=='H03' and r['set']=='dificil_25')
    return {'origen': 'traza_historica_v6', 'clave': 'dificil_25:H03', 'pregunta': fila['pregunta'],
            'fuente': 'resultados_v6/trazas_D3.json', 'fuente_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'respuesta_referencia': fila['gold_dato'], 'fuentes_referencia': fila['gold_fuente'], 'traza': traza}


def mostrar_fallo(base):
    fallo = cargar_fallo(base)
    borradores = [e['salida'] for e in fallo['traza'] if e['agente']=='redactor']
    verificaciones = [e for e in fallo['traza'] if e['agente']=='verificador']
    llamadas = sum(not e.get('decidido_por') for e in fallo['traza'])
    body = '<p><b>TRAZA HISTÓRICA · NO ES UNA EJECUCIÓN NUEVA</b></p>'
    body += '<p>' + html.escape(fallo['pregunta']) + '</p>'
    body += '<p><b>Exigencia:</b> recuperar cuatro fechas, calcular dos intervalos y compararlos.</p>'
    body += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div><b>Primer borrador</b>'+bloque(borradores[0],150)+'</div><div><b>Último borrador</b>'+bloque(borradores[-1],150)+'</div></div>'
    body += '<p><b>Recorrido de revisión:</b> Verificador → Redactor → Verificador → Recuperador → Redactor → Verificador.</p>'
    body += f'<p><b>{llamadas} llamadas · Terminó sin aprobación.</b> La selección de evidencia omitió fechas necesarias, aunque están en el corpus.</p>'
    body += '<p><b>Respuesta de referencia:</b> ' + html.escape(fallo['respuesta_referencia']) + '</p>'
    body += '<details><summary>Decisiones del Verificador</summary>' + bloque(verificaciones,200) + '</details>'
    body += '<details><summary>Registro histórico completo disponible</summary>' + bloque(fallo['traza'],240) + '</details>'
    mostrar_html(marco('H03 · Fallo de recuperación y corrección',body,'#94611c'))
    return fallo


def mostrar_resultados():
    filas = [('Directo','1/50 (2%)','0/25 (0%)'), ('RAG D2','40/50 (80%)','16/25 (64%)'),
             ('Sistema completo','46/50 (92%)','20/25 (80%)'), ('Sin few-shot','44/50 (88%)','19/25 (76%)'),
             ('Sin ReAct','45/50 (90%)','18/25 (72%)'), ('Sin CoT del Redactor','46/50 (92%)','19/25 (76%)'),
             ('Sin Verificador: primer borrador','44/50 (88%)','19/25 (76%)')]
    body = '<p><b>RESULTADOS HISTÓRICOS · NO SE CALCULAN EN ESTA DEMO</b></p>'
    body += '<table style="border-collapse:collapse;width:100%;text-align:left"><tr><th>Configuración</th><th>50 originales</th><th>25 difíciles</th></tr>'
    for i, fila in enumerate(filas):
        body += '<tr style="border-top:1px solid #ccd7df;' + ('background:#eaf3f8;font-weight:bold' if i==2 else '') + '">'
        body += ''.join('<td style="padding:6px">'+html.escape(c)+'</td>' for c in fila) + '</tr>'
    body += '</table><p>Calificación propuesta con apoyo de Claude y <b>revisada por el equipo</b>. Aprobar internamente no garantiza acertar.</p>'
    body += '<p>Las ablaciones sin ReAct y sin Verificador eliminan componentes; una ejecución por condición no demuestra una ventaja estable.</p>'
    mostrar_html(marco('Evaluación y límites', body))


def exportar_evidencia(base, carpeta, sesiones, seleccion, entorno):
    """Exporta todos los intentos, destacando los run_id que el usuario elige para el video."""
    base, carpeta = Path(base), Path(carpeta)
    sesiones = list(sesiones)
    ids = {s.id for s in sesiones}
    if not seleccion or not set(seleccion).issubset(ids):
        raise ValueError('La selección de ejecuciones está vacía o contiene identificadores inexistentes.')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '_' + uuid.uuid4().hex[:6]
    path = carpeta/f'evidencia_video_{stamp}.zip'
    contenido = {}
    for sesion in sesiones:
        sesion._guardar()
        for f in sesion.carpeta.iterdir():
            if f.is_file() and f.suffix in ('.json','.jsonl'):
                contenido[f'ejecuciones/{sesion.id}/{f.name}'] = f.read_bytes()
    for directorio in ('agentes','prompts','video'):
        for f in sorted((base/directorio).rglob('*')):
            if f.is_file() and '__pycache__' not in f.parts and f.suffix in ('.py','.txt','.json','.csv'):
                contenido['fuentes/'+str(f.relative_to(base))] = f.read_bytes()
    grafico = base/'documento/grafo_compacto.png'
    if grafico.is_file():
        contenido['fuentes/documento/grafo_compacto.png'] = grafico.read_bytes()
    contenido['entorno.json'] = json.dumps(entorno, ensure_ascii=False, indent=2).encode()
    contenido['fallo_H03_historico.json'] = json.dumps(cargar_fallo(base), ensure_ascii=False, indent=2).encode()
    contenido['indice_video.json'] = json.dumps({'run_id_en_video': seleccion,
        'todos_los_intentos': [s.id for s in sesiones], 'video_url': None,
        'nota': 'Confirmar que run_id_en_video corresponde a las ejecuciones visibles en el video.'}, ensure_ascii=False, indent=2).encode()
    contenido['LEEME.txt'] = ('Evidencia de la grabación D3.\n'
        'ejecuciones/: inferencias nuevas, con prompts, salidas crudas, herramientas y traza original.\n'
        'fallo_H03_historico.json: caso anterior, identificado como histórico.\n'
        'fuentes/: copia del código, corpus y prompts utilizados.\n'
        'indice_video.json: ejecuciones que deben coincidir con el video; enlace aún pendiente.\n'
        'Subir este ZIP al repositorio en Deliverable 3/evidencia_video/ junto al enlace público.\n').encode()
    contenido['manifiesto.json'] = json.dumps({k:hashlib.sha256(v).hexdigest() for k,v in contenido.items()}, indent=2).encode()
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for nombre, datos in contenido.items():
            z.writestr(nombre, datos)
    return path
