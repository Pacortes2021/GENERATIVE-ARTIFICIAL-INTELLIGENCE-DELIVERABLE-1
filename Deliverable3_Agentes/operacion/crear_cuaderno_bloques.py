"""Crea un lanzador por bloques conservando el payload experimental v4 intacto."""
import copy
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
base = json.loads((ROOT / 'Deliverable3_Agentes_Colab.ipynb').read_text())
def markdown(text, ident):
    return {'cell_type': 'markdown', 'metadata': {'id': ident}, 'source': text.splitlines(keepends=True)}
nb = copy.deepcopy(base)
nb['cells'] = [markdown('''# Deliverable 3 · lote real en diez bloques

50 preguntas × seis condiciones = 300 respuestas. Cada bloque tiene **30 respuestas** (cinco preguntas en las seis condiciones). No ejecuta el piloto.

1. En una sesión nueva T4, ejecutar preparación, restauración y carga (secciones 1–3).
2. Ejecutar **un bloque** en la última celda. Restaura el respaldo verificado de 39 respuestas cuando haga falta y respeta resultados posteriores ya presentes en la sesión.
3. Descargar y auditar el ZIP al terminar. Cada seis respuestas nuevas se solicita además un respaldo parcial. Comprobar que realmente llegó a Descargas.
4. Para el siguiente bloque en la misma sesión, ejecutar **solo la última celda**; no volver a cargar el modelo. Se detiene en 60, 90, …, 300 según lo ya guardado.

El primer bloque ya está completo. Partiendo del respaldo de 39, se generan 21 respuestas para cerrar el bloque 2 en 60/300. Si se pierde una sesión, el respaldo fijado aquí permite recuperar 39; antes de reanudar desde uno posterior hay que actualizar su URL, SHA-256 y cantidad en la celda de recuperación, tras auditarlo. Los archivos de la sesión temporal no son respaldo persistente.

Código, prompts, preguntas, semillas, controles y orden de condiciones del experimento v4 se mantienen. Solo se agrega una parada operativa después de exportar una respuesta completa.
''','bloques-inicio')] + copy.deepcopy(base['cells'][1:7])
nb['cells'] += [markdown('## 4. Ejecutar un bloque y descargar\n\nVolver a ejecutar esta celda continúa el próximo bloque. No usar Ejecutar todo para continuar en una sesión ya cargada.\n','bloques-ejecucion'), {'cell_type':'code','execution_count':None,'metadata':{'id':'bloques-codigo'},'outputs':[],'source':(ROOT/'operacion/reanudar_lote_v4_colab.py').read_text().splitlines(keepends=True)}]
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        cell['execution_count'] = None
        cell['outputs'] = []
        compile(''.join(cell['source']), cell['metadata'].get('id','cell'), 'exec')
assert nb['cells'][4]['source'] == base['cells'][4]['source'], 'Payload congelado alterado'
target = ROOT / 'Deliverable3_Agentes_Bloques_Colab.ipynb'
target.write_text(json.dumps(nb, ensure_ascii=False, indent=1)+'\n')
print(target.name)
