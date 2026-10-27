"""Máquina de estados nueva: las transferencias válidas las eligen los tres agentes."""
import copy
import json
import re
from .common import Limits, PromptBook, ContextLimit, task_for, digest
from .tools import combine, ToolInputError

ROLES = ('investigador', 'redactor', 'auditor')
ACTIONS = {'investigador': {'herramienta', 'redactar'},
           'redactor': {'investigar', 'auditar'},
           'auditor': {'aceptar', 'corregir', 'investigar'}}
FALLBACK = ('No se obtuvo una respuesta validada dentro del presupuesto de esta consulta. '
            'Esto no demuestra que la información esté ausente del corpus.')


def cited_ids(text):
    bracketed = {i.strip() for group in re.findall(r'\[([^\[\]\n]+)\]', text)
                 for i in re.split(r'[,;]', group) if i.strip()}
    # Los IDs normativos también pueden aparecer entre paréntesis o en prosa.
    explicit = set(re.findall(r'\b(?:RI-FI|RG|CAL|INV)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*', text))
    return bracketed | explicit


def parse_decision(raw, role, evidence):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Clave JSON repetida.')
            result[key] = value
        return result
    # No se extraen subcadenas ni se ejecuta salida del modelo.
    value = json.loads(raw, object_pairs_hook=unique,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Constante JSON inválida.')))
    extra = {'investigador': 'herramienta', 'redactor': 'respuesta', 'auditor': 'apoyos'}[role]
    if not isinstance(value, dict):
        raise ValueError('Devuelve un objeto JSON con accion y mensaje.')
    # Dos formas explícitas del mismo contrato de transporte. Nunca inferir argumentos.
    action = value.get('accion')
    # El modelo puede emitir la misma solicitud explícita sin el contenedor.
    # Solo normalizamos esta forma exacta: no completamos ni inferimos argumentos.
    if (role == 'investigador' and set(value) == {'accion', 'mensaje', 'nombre', 'argumentos'}
            and value.get('nombre') in ('buscar_normativa', 'leer_articulo', 'inventario')
            and action in ('herramienta', value['nombre'])):
        value = {'accion': 'herramienta', 'mensaje': value['mensaje'],
                 'herramienta': {'nombre': value['nombre'], 'argumentos': value['argumentos']}}
        action = value['accion']
    if role == 'investigador' and isinstance(action, str) and action in (
            'buscar_normativa', 'leer_articulo', 'inventario'):
        request = value.get('herramienta')
        if not isinstance(request, dict) or request.get('nombre') != action:
            raise ValueError('La accion y herramienta.nombre deben coincidir.')
        value['accion'] = 'herramienta'
    idle = {'investigador': ('redactar', None), 'redactor': ('investigar', ''),
            'auditor': (None, [])}[role]
    if extra not in value and value.get('accion') == idle[0]:
        value[extra] = idle[1]
    if set(value) != {'accion', 'mensaje', extra}:
        expected = {'accion', 'mensaje', extra}
        raise ValueError('Usa solo accion, mensaje y ' + extra +
                         '; faltan: ' + (', '.join(sorted(expected - set(value))) or 'ninguna') +
                         '; sobran: ' + (', '.join(sorted(set(value) - expected)) or 'ninguna') +
                         '. Elimina las claves sobrantes. No copies las fuentes; el programa ya las conserva.')
    if not isinstance(value['accion'], str) or value['accion'] not in ACTIONS[role]:
        raise ValueError('Acciones permitidas: ' + ', '.join(sorted(ACTIONS[role])))
    if not isinstance(value['mensaje'], str) or not 1 <= len(value['mensaje'].strip()) <= 1500:
        raise ValueError('Se requiere un mensaje breve no vacío.')
    if role == 'investigador':
        tool = value['herramienta']
        if value['accion'] == 'redactar' and tool is not None:
            raise ValueError('Transferir al redactor no ejecuta una herramienta.')
        if value['accion'] == 'herramienta' and not isinstance(tool, dict):
            raise ValueError('Falta la solicitud de herramienta.')
    elif role == 'redactor':
        if not isinstance(value['respuesta'], str):
            raise ValueError('La respuesta debe ser texto.')
        if value['accion'] == 'auditar' and not value['respuesta'].strip():
            raise ValueError('No se puede auditar un borrador vacío.')
        if value['accion'] == 'investigar' and value['respuesta']:
            raise ValueError('Una solicitud de investigación debe dejar respuesta vacía.')
    else:
        supports = value['apoyos']
        if not isinstance(supports, list) or len(supports) > 20:
            raise ValueError('Apoyos debe ser una lista de hasta veinte elementos.')
        for item in supports:
            if (not isinstance(item, dict) or set(item) != {'afirmacion', 'fuente', 'extracto'}
                    or any(not isinstance(v, str) or not v.strip() for v in item.values())):
                raise ValueError('Formato de apoyo inválido.')
            if item['fuente'] not in evidence:
                raise ValueError('Fuente del apoyo inexistente: ' + item['fuente'] +
                                 '. Usa fuentes recibidas; para pedir investigación usa apoyos: [].')
            quote = ' '.join(item['extracto'].split())
            if len(quote) < 8 or quote not in ' '.join(evidence[item['fuente']]['texto'].split()):
                raise ValueError('El extracto no coincide con la fuente.')
    return value


def agent_payload(question, evidence, draft, notice, observations, format_error, model_left, tools_left):
    return {'pregunta': question, 'evidencia': list(evidence.values()),
            'observaciones_herramientas': observations,
            'borrador': draft, 'mensaje_recibido': notice, 'error_formato': format_error,
            'presupuesto_restante': {'modelo': model_left, 'herramientas': tools_left}}


class AgentSystem:
    def __init__(self, tokenizer, generate, tools, variant='agentes_completo',
                 limits=None, prompts=None, observe=None):
        self.tokenizer, self.generate, self.tools = tokenizer, generate, tools
        self.variant = variant
        self.limits, self.prompts = limits or Limits(), prompts or PromptBook()
        self.observe = observe or (lambda event: None)
        self.prompts.render('investigador', variant)  # valida la variante antes de generar

    def run(self, question, seed):
        evidence, trace, drafts, visits = {}, [], [], dict.fromkeys(ROLES, 0)
        role, draft, notice = 'investigador', '', 'Investiga la pregunta con las herramientas del corpus.'
        tool_count, invalid, used = 0, 0, set()
        observations, drafted_states = [], set()
        format_error, repairs = '', 0

        def emit(kind, **payload):
            event = {'orden': len(trace) + 1, 'tipo': kind, **copy.deepcopy(payload)}
            trace.append(event)
            self.observe(event)

        def finish(status, response):
            emit('fin', estado=status, respuesta=response)
            return {'estado': status, 'respuesta_modelo': response, 'borradores': drafts,
                    'evidencia': evidence, 'traza': trace, 'llamadas_por_agente': visits,
                    'herramientas': tool_count, 'salidas_invalidas': invalid,
                    'aceptacion_interna_no_es_exactitud': True}

        def messages(target, sources, message):
            payload = agent_payload(question, sources, draft, message, observations, format_error,
                                    self.limits.model_calls - sum(visits.values()),
                                    self.limits.tool_calls - tool_count)
            return [{'role': 'system', 'content': self.prompts.render(target, self.variant)},
                    {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}]

        def apply_tool(request, origin):
            nonlocal tool_count, evidence, notice, draft, repairs
            key = digest(request)
            if tool_count >= self.limits.tool_calls or key in used:
                notice = ('Herramienta bloqueada: presupuesto agotado o solicitud idéntica ya realizada. '
                          'Revisa las observaciones disponibles o elige otra consulta.')
                emit('herramienta_bloqueada', solicitud=request, detalle=notice, origen=origin)
                return
            tool_count += 1
            used.add(key)
            try:
                observation = self.tools.execute(request)
                candidate = combine(evidence, observation['fuentes'], self.limits)
                record = {'solicitud': request, 'observacion': observation['observacion'],
                          'fuentes': [source['id'] for source in observation['fuentes']]}
                # Validar el estado completo candidato antes de incorporarlo, sin truncar.
                for next_role in ROLES:
                    payload = agent_payload(question, candidate, '', observation['observacion'],
                                            observations + [record], '',
                                            self.limits.model_calls - sum(visits.values()),
                                            self.limits.tool_calls - tool_count)
                    task_for(self.tokenizer, [
                        {'role': 'system', 'content': self.prompts.render(next_role, self.variant)},
                        {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}],
                        self.limits, next_role)
                if candidate != evidence:
                    if draft:
                        emit('borrador_invalidado', motivo='Nueva evidencia: volver a redactar desde las fuentes.',
                             borrador=draft)
                    draft, repairs = '', 0
                evidence = candidate
                observations.append(record)
                notice = observation['observacion']
                emit('observacion', agente='investigador', solicitud=request, resultado=observation, origen=origin)
            except (ToolInputError, ContextLimit) as exc:
                notice = 'Herramienta no aplicada: ' + str(exc)
                emit('herramienta_rechazada', solicitud=request, detalle=str(exc), origen=origin)

        # Recuperación original de D2 como punto de partida, registrada y dentro de las seis consultas.
        # No depende del ID de la pregunta ni de respuestas ideales.
        apply_tool({'nombre': 'buscar_normativa', 'argumentos': {'consulta': question}}, 'inicio_automatico')

        for _ in range(self.limits.model_calls):
            try:
                task = task_for(self.tokenizer, messages(role, evidence, notice), self.limits, role)
            except ContextLimit as exc:
                emit('limite_contexto', agente=role, detalle=str(exc))
                return finish('limite_contexto', FALLBACK)
            # Mismos slots de semilla por agente/visita entre completo y ablaciones.
            call_seed = seed + (ROLES.index(role) + 1) * 10000 + visits[role]
            visits[role] += 1
            result = self.generate(task, call_seed)
            emit('modelo', agente=role, semilla=call_seed, tarea=task, salida=result)
            try:
                if result.get('posible_corte') or result.get('thinking_inesperado'):
                    raise ValueError('Salida cortada o con thinking inesperado. Devuelve solo la decisión breve; '
                                     'no copies fuentes ni artículos completos y cierra el JSON.')
                decision = parse_decision(result['respuesta_modelo'], role, evidence)
            except (ValueError, TypeError, KeyError) as exc:
                invalid += 1
                format_error = 'Tu salida no cumple el contrato: ' + str(exc) + ' Devuelve el JSON solicitado.'
                emit('salida_invalida', agente=role, detalle=str(exc))
                if invalid >= self.limits.invalid_outputs:
                    return finish('limite_salidas_invalidas', FALLBACK)
                continue
            format_error = ''
            emit('decision', agente=role, decision=decision)
            action, notice = decision['accion'], decision['mensaje']
            if role == 'investigador' and action == 'herramienta':
                apply_tool(decision['herramienta'], 'decision_agente')
                continue
            if role == 'investigador':
                if not evidence:
                    notice = 'No hay fuentes recibidas. Consulta una herramienta antes de pedir una respuesta.'
                    emit('transferencia_bloqueada', detalle=notice)
                    continue
                target = 'redactor'
            elif role == 'redactor':
                target = 'investigador' if action == 'investigar' else 'auditor'
                if action == 'auditar':
                    draft = decision['respuesta']
                    drafts.append(draft)
                    state = digest({'texto': ' '.join(draft.split()), 'evidencia': evidence})
                    missing = cited_ids(draft) - evidence.keys()
                    if missing or state in drafted_states:
                        notice = ('El borrador cita fuentes no recibidas: ' + ', '.join(sorted(missing))
                                  if missing else 'La misma respuesta ya fue revisada con estas fuentes y no progresó.')
                        notice += ' Investiga la carencia antes de redactar de nuevo.'
                        emit('borrador_bloqueado', detalle=notice, borrador=draft)
                        draft, target = '', 'investigador'
                    drafted_states.add(state)
            elif action == 'aceptar':
                missing = cited_ids(draft) - evidence.keys()
                if missing:
                    notice = 'El borrador cita fuentes que no se recibieron: ' + ', '.join(sorted(missing))
                    target = 'investigador'
                    emit('aceptacion_bloqueada', detalle=notice)
                else:
                    return finish('aceptada', draft)
            else:
                target = 'redactor' if action == 'corregir' else 'investigador'
                if action == 'corregir':
                    repairs += 1
                    if repairs >= 2:
                        target = 'investigador'
                        notice = 'Dos correcciones sin nueva evidencia. Investiga esta carencia: ' + notice
                        emit('ciclo_interrumpido', detalle=notice)
            if target == 'investigador' and draft:
                emit('borrador_invalidado', motivo='Se solicitó investigar antes de redactar de nuevo.',
                     borrador=draft)
                draft = ''
            emit('transferencia', emisor=role, receptor=target, mensaje=notice,
                 borrador=draft, fuentes=list(evidence))
            role = target
        return finish('limite_llamadas', FALLBACK)
