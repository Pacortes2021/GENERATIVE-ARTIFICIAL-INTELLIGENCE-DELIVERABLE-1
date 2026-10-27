"""Herramientas nuevas de lectura; el buscador se integra desde D2."""
import copy
from .common import canonical, digest


class ToolInputError(ValueError):
    pass


class CorpusAccess:
    def __init__(self, corpus, retriever):
        self.corpus = corpus
        self.retriever = retriever
        self.parents = {p['id']: p for p in corpus['padres']}

    def inventory(self, doc):
        entries = []
        for parent in self.corpus['padres']:
            if parent['documento'] == doc and parent['tipo'] in ('articulo', 'evento'):
                entries.append({k: parent[k] for k in
                                ('id', 'articulo', 'ambito', 'evento', 'fecha', 'anio', 'paginas') if k in parent})
        return {'id': 'INV-' + doc, 'cita': 'Inventario completo: ' + self.corpus['fuentes'][doc]['archivo'],
                'texto': canonical({'documento': doc, 'alcance': 'copia del corpus, no normativa externa',
                                    'entradas': entries})}

    def execute(self, request):
        if not isinstance(request, dict) or set(request) != {'nombre', 'argumentos'}:
            raise ToolInputError('Se requieren nombre y argumentos.')
        name, args = request['nombre'], request['argumentos']
        if not isinstance(name, str) or not isinstance(args, dict):
            raise ToolInputError('Tipos de herramienta inválidos.')
        if name == 'buscar_normativa':
            if (set(args) != {'consulta'} or not isinstance(args['consulta'], str)
                    or not 1 <= len(args['consulta'].strip()) <= 500):
                raise ToolInputError('Consulta inválida: usa entre 1 y 500 caracteres.')
            case, _ = self.retriever.retrieve(args['consulta'].strip())
            evidence = [{'id': c['unidad_id'], 'cita': c['cita'], 'texto': c['texto']}
                        for c in case['contextos']]
            for item in case.get('contextos_inventario', []):
                evidence.append({'id': 'INV-' + digest(item)[:16],
                                 'cita': 'Inventario de ' + item['archivo'], 'texto': item['texto']})
            return {'fuentes': evidence, 'observacion': 'Resultados de D2; una búsqueda parcial no prueba ausencia.'}
        if name not in ('leer_articulo', 'inventario'):
            raise ToolInputError('Herramienta no permitida.')
        doc = args.get('documento')
        if not isinstance(doc, str) or doc not in ('RG', 'RI-FI', 'CAL'):
            raise ToolInputError('Documento no reconocido.')
        if name == 'inventario':
            if set(args) != {'documento'}:
                raise ToolInputError('Inventario solo recibe documento.')
            return {'fuentes': [self.inventory(doc)], 'observacion': 'Inventario completo de esta copia.'}
        number = args.get('numero')
        if (set(args) != {'documento', 'numero'} or doc == 'CAL'
                or type(number) is not int or not 1 <= number <= 999):
            raise ToolInputError('Lectura requiere RG/RI-FI y un número de artículo ordinario entre 1 y 999.')
        key = f'{doc}-ART-{number:03}'
        units = [u for u in self.corpus['unidades'] if u['parent_id'] == key]
        if not units:
            return {'fuentes': [self.inventory(doc)],
                    'observacion': f'Artículo ordinario {number} ausente de esta copia; consultar el inventario.'}
        return {'fuentes': [{'id': u['id'], 'cita': self.parents[key]['cita'], 'texto': u['texto']} for u in units],
                'observacion': 'Artículo completo: se incluyen todas sus unidades.'}


def combine(current, incoming, limits):
    merged = copy.deepcopy(current)
    for source in incoming:
        if source['id'] in merged and merged[source['id']] != source:
            raise ToolInputError('Una fuente conocida cambió de contenido.')
        merged[source['id']] = copy.deepcopy(source)
    if len(merged) > limits.evidence_units or sum(len(v['texto']) for v in merged.values()) > limits.evidence_characters:
        raise ToolInputError('La evidencia excede el presupuesto: no se incorporó ni truncó.')
    return merged
