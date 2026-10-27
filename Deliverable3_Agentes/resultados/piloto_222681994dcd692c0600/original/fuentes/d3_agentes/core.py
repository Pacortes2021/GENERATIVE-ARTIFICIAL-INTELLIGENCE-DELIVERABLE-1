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
    return {i.strip() for group in re.findall(r'\[([^\[\]\n]+)\]', text)
            for i in re.split(r'[,;]', group) if i.strip()}


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
    if not isinstance(value, dict) or set(value) != {'accion', 'mensaje', extra}:
        raise ValueError('Claves distintas del contrato de ' + role)
    if not isinstance(value['accion'], str) or value['accion'] not in ACTIONS[role]:
        raise ValueError('Acción no permitida para ' + role)
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
                raise ValueError('Fuente del apoyo inexistente.')
            quote = ' '.join(item['extracto'].split())
            if len(quote) < 8 or quote not in ' '.join(evidence[item['fuente']]['texto'].split()):
                raise ValueError('El extracto no coincide con la fuente.')
    return value


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
            payload = {'pregunta': question, 'evidencia': list(sources.values()),
                       'borrador': draft, 'mensaje_recibido': message,
                       'presupuesto_restante': {'modelo': self.limits.model_calls - sum(visits.values()),
                                                'herramientas': self.limits.tool_calls - tool_count}}
            return [{'role': 'system', 'content': self.prompts.render(target, self.variant)},
                    {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}]

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
                    raise ValueError('Salida cortada o con thinking inesperado.')
                decision = parse_decision(result['respuesta_modelo'], role, evidence)
            except (ValueError, TypeError, KeyError) as exc:
                invalid += 1
                notice = 'Tu salida no cumple el contrato: ' + str(exc) + ' Devuelve el JSON solicitado.'
                emit('salida_invalida', agente=role, detalle=str(exc))
                if invalid >= self.limits.invalid_outputs:
                    return finish('limite_salidas_invalidas', FALLBACK)
                continue
            emit('decision', agente=role, decision=decision)
            action, notice = decision['accion'], decision['mensaje']
            if role == 'investigador' and action == 'herramienta':
                request = decision['herramienta']
                key = digest(request)
                if tool_count >= self.limits.tool_calls or key in used:
                    notice = 'Herramienta bloqueada: presupuesto agotado o solicitud idéntica ya realizada. ' + notice
                    emit('herramienta_bloqueada', solicitud=request, detalle=notice)
                    continue
                tool_count += 1
                used.add(key)
                try:
                    observation = self.tools.execute(request)
                    candidate = combine(evidence, observation['fuentes'], self.limits)
                    # Las fuentes son atómicas: solo se incorporan si todos los agentes pueden recibirlas.
                    for next_role in ROLES:
                        task_for(self.tokenizer, messages(next_role, candidate, observation['observacion']),
                                 self.limits, next_role)
                    evidence = candidate
                    notice = observation['observacion']
                    emit('observacion', agente=role, solicitud=request, resultado=observation)
                except (ToolInputError, ContextLimit) as exc:
                    notice = 'Herramienta no aplicada: ' + str(exc)
                    emit('herramienta_rechazada', solicitud=request, detalle=str(exc))
                continue
            if role == 'investigador':
                target = 'redactor'
            elif role == 'redactor':
                target = 'investigador' if action == 'investigar' else 'auditor'
                if action == 'auditar':
                    draft = decision['respuesta']
                    drafts.append(draft)
            elif action == 'aceptar':
                missing = cited_ids(draft) - evidence.keys()
                if missing:
                    notice = 'El borrador cita fuentes que no se recibieron: ' + ', '.join(sorted(missing))
                    target = 'redactor'
                    emit('aceptacion_bloqueada', detalle=notice)
                else:
                    return finish('aceptada', draft)
            else:
                target = 'redactor' if action == 'corregir' else 'investigador'
            emit('transferencia', emisor=role, receptor=target, mensaje=notice,
                 borrador=draft, fuentes=list(evidence))
            role = target
        return finish('limite_llamadas', FALLBACK)
