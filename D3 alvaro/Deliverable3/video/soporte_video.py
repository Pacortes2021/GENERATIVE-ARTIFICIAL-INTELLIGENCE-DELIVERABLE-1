"""Visualización y registro adicional para el video; no cambia decisiones de v6."""
from pathlib import Path
from datetime import datetime, timezone
import copy
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


def bloque(value):
    return '<pre style="white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.4 monospace;margin:8px 0">' + html.escape(serial(value)) + '</pre>'


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
        body += '<p><b>Pregunta:</b> ' + html.escape(d['pregunta']) + '</p>'
        body += '<p>Enrutador → Recuperador ⇄ herramientas → Redactor → Verificador ↺</p>'
        body += f'<p>Llamadas al modelo: <b>{len(d["llamadas"])}</b> · Tiempo transcurrido: <b>{(self.fin if self.fin is not None else time.perf_counter())-self.inicio:.1f} s</b></p>'
        body += '<p style="font-size:14px">Los mensajes aparecen al terminar cada llamada. Abre una fila para revisar su entrada y salida.</p>'
        for i, e in enumerate(d['intercambios']):
            auto = ' · acción automática' if e.get('decidido_por') else ''
            abierto = ' open' if i >= len(d['intercambios'])-2 else ''
            body += f'<details{abierto} style="border-top:1px solid #dbe4eb;padding:7px 0"><summary><b>{e["paso"]}. {html.escape(e["agente"].upper())}{auto}</b></summary>'
            body += '<b>Entrada registrada:</b>' + bloque(e['entrada'])
            body += '<b>Salida / decisión:</b>' + bloque(e['salida'])
            if e.get('observacion') is not None:
                body += '<b>Observación de herramienta:</b>' + bloque(e['observacion'])
            body += '</details>'
        if d['resultado']:
            body += '<hr><h3>Respuesta final</h3>' + bloque(d['resultado']['respuesta'])
            body += '<b>Veredicto interno (no es una calificación externa):</b>' + bloque(d['resultado']['veredicto'])
        if d.get('error'):
            body += '<p><b>Ejecución detenida:</b> ' + html.escape(d['error']) + '</p>'
        body += '<p style="font-size:13px">Run: ' + html.escape(self.id) + ' · El archivo descargable incluye prompts y salidas completos.</p>'
        content = HTML(marco('Consulta ' + str(d['caso']), body))
        if self.panel is None:
            self.panel = display(content, display_id=True)
        else:
            self.panel.update(content)


def mostrar_portada():
    mostrar_html(marco('D3 · Agentes para normativa de pregrado', '''
<p><b>Pregunta:</b> cómo responder con respaldo y corregir fallos de recuperación o redacción.</p>
<p><b>Enrutador</b> planifica → <b>Recuperador</b> elige herramientas → <b>Redactor</b> responde → <b>Verificador</b> termina o pide corregir.</p>
<p>Todos los roles: <b>Qwen3-4B</b> · recuperación E5 · máximo 3 acciones por subconsulta y 2 ciclos de corrección.</p>
<p>Mostraremos <b>dos consultas reales</b>. Después, un fallo histórico identificado y resultados provisionales.</p>'''))


def cargar_fallo(base):
    base = Path(base)
    path = base/'resultados_v6/trazas_D3.json'
    traza = json.loads(path.read_text())['dificil_25:H03']
    with (base/'resultados_v6/resultados_agentes_D3.csv').open(encoding='utf-8-sig', newline='') as f:
        fila = next(r for r in csv.DictReader(f) if r['id']=='H03' and r['set']=='dificil_25')
    return {'origen': 'traza_historica_v6', 'clave': 'dificil_25:H03', 'pregunta': fila['pregunta'],
            'fuente': 'resultados_v6/trazas_D3.json', 'fuente_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'traza': traza}


def mostrar_fallo(base):
    fallo = cargar_fallo(base)
    borradores = [e['salida'] for e in fallo['traza'] if e['agente']=='redactor']
    verificaciones = [e['salida'] for e in fallo['traza'] if e['agente']=='verificador']
    llamadas = sum(not e.get('decidido_por') for e in fallo['traza'])
    body = '<p><b>TRAZA HISTÓRICA · NO ES UNA EJECUCIÓN NUEVA</b></p>'
    body += '<p>' + html.escape(fallo['pregunta']) + '</p>'
    body += '<b>Primer borrador:</b>' + bloque(borradores[0])
    body += '<b>Último borrador:</b>' + bloque(borradores[-1])
    body += f'<p><b>{llamadas} llamadas</b> · La selección de evidencia omitió fechas. La revisión no recuperó todo lo necesario.</p>'
    body += '<b>Veredicto final:</b>' + bloque(verificaciones[-1])
    body += '<details><summary>Ver todos los mensajes históricos disponibles</summary>' + bloque(fallo['traza']) + '</details>'
    mostrar_html(marco('Fallo observado · H03', body, '#94611c'))
    return fallo


def mostrar_resultados():
    filas = [('Directo','1/50 (2%)','0/25 (0%)'), ('RAG D2','40/50 (80%)','16/25 (64%)'),
             ('Completo v6','46/50 (92%)','20/25 (80%)'), ('Sin few-shot','44/50 (88%)','19/25 (76%)'),
             ('Sin ReAct','45/50 (90%)','18/25 (72%)'), ('Sin CoT del Redactor','46/50 (92%)','19/25 (76%)'),
             ('Sin Verificador: primer borrador','44/50 (88%)','19/25 (76%)')]
    body = '<p><b>RESULTADOS HISTÓRICOS PROVISIONALES · NO SE CALCULAN EN ESTA DEMO</b></p>'
    body += '<table style="border-collapse:collapse;width:100%;text-align:left"><tr><th>Configuración</th><th>50 originales</th><th>25 difíciles</th></tr>'
    for i, fila in enumerate(filas):
        body += '<tr style="border-top:1px solid #ccd7df;' + ('background:#eaf3f8;font-weight:bold' if i==2 else '') + '">'
        body += ''.join('<td style="padding:6px">'+html.escape(c)+'</td>' for c in fila) + '</tr>'
    body += '</table><p>Calificación propuesta con apoyo de Claude; <b>9 casos de v6 pendientes de revisión</b>. Aprobar internamente no garantiza acertar.</p>'
    body += '<p>Las ablaciones sin ReAct y sin Verificador eliminan componentes; una ejecución por condición no demuestra una ventaja estable.</p>'
    mostrar_html(marco('Evaluación y límites', body))


def exportar_evidencia(base, carpeta, sesiones, seleccion, entorno):
    """Exporta todos los intentos, destacando los run_id que el usuario elige para el video."""
    base, carpeta = Path(base), Path(carpeta)
    sesiones = list(sesiones)
    ids = {s.id for s in sesiones}
    if not seleccion or not set(seleccion).issubset(ids):
        raise ValueError('Selecciona run_id existentes que coincidan con la grabación.')
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
        'Subir este ZIP al repositorio en D3 alvaro/evidencia_video/ junto al enlace público.\n').encode()
    contenido['manifiesto.json'] = json.dumps({k:hashlib.sha256(v).hexdigest() for k,v in contenido.items()}, indent=2).encode()
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for nombre, datos in contenido.items():
            z.writestr(nombre, datos)
    return path
