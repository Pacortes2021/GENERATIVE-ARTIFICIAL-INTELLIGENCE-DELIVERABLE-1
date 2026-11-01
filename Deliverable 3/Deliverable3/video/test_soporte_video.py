"""Pruebas locales de instrumentación; no son ejecuciones ni evaluación de Qwen."""
from pathlib import Path
import sys, tempfile, json, zipfile, hashlib, ast, types
BASE=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(BASE/'agentes'),str(Path(__file__).parent)]
from orquestador import Orquestador
from tools import Corpus
from soporte_video import SesionDemo, exportar_evidencia, bloque, mostrar_portada, mostrar_fallo, mostrar_resultados

class ModeloSimulado:
    def __init__(self): self.ver=0; self.red=0
    def __call__(self, agente, prompt):
        if agente=='enrutador':
            return '{"tipo":"factual","sub_consultas":["nota mínima"],"documentos":["RI-FI"]}'
        if agente=='recuperador': return '{"accion":"suficiente","args":{}}'
        if agente=='redactor':
            self.red+=1
            return '<pensar>razonamiento de prueba</pensar>Respuesta: 4,0 [RI-FI-ART-011]' + (' corregida' if self.red>1 else '')
        if agente=='verificador':
            self.ver+=1
            return json.dumps({'aprobado':self.ver>1,'destino':'fin' if self.ver>1 else 'redactor','motivo':'completar condiciones'})
        raise ValueError(agente)

q='¿Cuál es la nota mínima para aprobar una asignatura en la Facultad de Ingeniería?'
# Probar también el HTML sin necesitar un kernel de Colab.
capturas=[]
class HTMLSimulado:
    def __init__(self, data): self.data=data
class PanelSimulado:
    def update(self, value): capturas.append(value.data)
def display_simulado(value, **kwargs):
    capturas.append(value.data)
    return PanelSimulado()
display_mod=types.ModuleType('IPython.display')
display_mod.HTML=HTMLSimulado
display_mod.display=display_simulado
sys.modules['IPython.display']=display_mod
plain=Orquestador(Corpus(BASE/'agentes'),ModeloSimulado()).responder(q)
with tempfile.TemporaryDirectory() as tmp:
    ses=SesionDemo(Corpus(BASE/'agentes'),ModeloSimulado(),tmp,{'prueba':'MODELO SIMULADO'},'TEST',q,visible=True)
    observed=ses.ejecutar()
    assert capturas and 'Respuesta final' in capturas[-1]
    final=capturas[-1]
    assert final.index('Respuesta final') < final.index('Último intercambio') < final.index('Historial anterior')
    assert final.count('<details open')==1, 'Solo el último intercambio debe abrirse por defecto.'
    assert ses.datos['activo'] is None
    assert '<details' in capturas[-1] and 'Entrada registrada:' in capturas[-1]
    assert plain==observed, 'La instrumentación cambió el resultado o la traza original.'
    saved=json.loads((ses.carpeta/'sesion.json').read_text())
    assert saved['estado']=='completa' and len(saved['llamadas'])==6
    assert len([e for e in saved['llamadas'] if e['agente']=='redactor'])==2
    assert all(c['mensajes'][0]['content'] and c['salida_cruda'] for c in saved['llamadas'])
    assert any('<pensar>' in c['salida_cruda'] for c in saved['llamadas'])
    second=[c for c in saved['llamadas'] if c['agente']=='redactor'][1]
    assert 'completar condiciones' in second['mensajes'][0]['content']
    # v6 conserva feedback, pero su prompt restaurado no contiene BORRADOR_ANTERIOR.
    assert 'Respuesta: 4,0' not in second['mensajes'][0]['content']
    assert {'buscar','chequear_citas','existe_articulo'} <= {x['nombre'] for x in saved['herramientas']}
    tiempo_final=ses.datos['segundos']
    archive=exportar_evidencia(BASE,tmp,[ses],[ses.id],{'prueba':'SIMULADO'})
    assert ses.datos['segundos']==tiempo_final, 'La descarga alteró el tiempo de inferencia.'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert z.read('fuentes/documento/grafo_compacto.png') == (BASE/'documento/grafo_compacto.png').read_bytes()
        hashes=json.loads(z.read('manifiesto.json'))
        assert all(hashlib.sha256(z.read(k)).hexdigest()==v for k,v in hashes.items())
        assert json.loads(z.read('indice_video.json'))['run_id_en_video']==[ses.id]
        hist=json.loads(z.read('fallo_H03_historico.json'))
        assert hist['origen']=='traza_historica_v6'
        assert sum(not x.get('decidido_por') for x in hist['traza'])==19
    def romper(agente,prompt): raise KeyboardInterrupt('interrupción de prueba')
    interrupted=SesionDemo(Corpus(BASE/'agentes'),romper,tmp,{},'TEST',q,visible=False)
    assert interrupted.id!=ses.id
    try: interrupted.ejecutar()
    except KeyboardInterrupt: pass
    else: raise AssertionError('Interrupción absorbida')
    partial=json.loads((interrupted.carpeta/'sesion.json').read_text())
    assert partial['estado']=='interrumpida' and partial['llamadas'][0]['mensajes']
    assert '&lt;script&gt;' in bloque('<script>')
mostrar_portada(BASE)
assert 'data:image/png;base64,' in capturas[-1] and all(x in capturas[-1] for x in ('Enrutador','Recuperador','Redactor','Verificador'))
assert 'Hasta 2 ciclos' in capturas[-1]
fallo=mostrar_fallo(BASE)
assert 'TRAZA HISTÓRICA' in capturas[-1] and '19 llamadas' in capturas[-1]
assert all(x in fallo['respuesta_referencia'] for x in ('24','25'))
assert 'Primer borrador' in capturas[-1] and 'Último borrador' in capturas[-1]
mostrar_resultados()
assert all(x in capturas[-1] for x in ('46/50','20/25','revisada por el equipo'))
nb=json.loads((BASE/'Demo_D3.ipynb').read_text())
code='\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code')
assert "caso='H17'" in code and 'mostrar_portada(BASE)' in code
assert 'test_set_dificil_25.csv' in code and 'mostrar_fallo(BASE)' in code
for i,c in enumerate(nb['cells']):
    if c['cell_type']=='code': ast.parse(''.join(c['source']),filename=f'celda {i}')
assert all(not c.get('outputs') for c in nb['cells'])
try:
    import nbformat
    nbformat.validate(nb)
except ImportError: print('nbformat no disponible; JSON y sintaxis validados.')
print('OK: misma salida/traza que v6, mensajes íntegros, corrección, herramientas, interrupción, exportación, grafo, casos H17/H03, presentación, hashes y sintaxis del notebook.')
