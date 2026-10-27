"""Pruebas de flujo con salidas simuladas explícitas; no miden exactitud de Qwen."""
import copy
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from d3_agentes.bridge import read_assets
from d3_agentes.common import Limits, PromptBook, VARIANTS
from d3_agentes.core import AgentSystem, parse_decision, cited_ids
from d3_agentes.tools import CorpusAccess, ToolInputError, combine


class Tokenizer:
    def apply_chat_template(self, messages, **kwargs):
        assert kwargs['enable_thinking'] is False
        return json.dumps(messages, ensure_ascii=False)

    def __call__(self, text, **kwargs):
        assert kwargs['truncation'] is False
        return {'input_ids': list(range(len(text) // 4 + 1))}


class Retriever:
    def __init__(self):
        self.corpus, self.fragments, self.questions, _ = read_assets()
        self.index_sha256 = 'SIMULACION_NO_INDICE_REAL'
        self.lookups = []

    def retrieve(self, question, question_id=1, category='nueva'):
        self.lookups.append(question)
        parent = next(p for p in self.corpus['padres'] if p['id'] == 'RI-FI-ART-011')
        unit = next(u for u in self.corpus['unidades'] if u['parent_id'] == parent['id'])
        return {'id': question_id, 'pregunta': question, 'categoria': category,
                'contextos': [{'unidad_id': unit['id'], 'cita': parent['cita'], 'texto': unit['texto']}],
                'contextos_inventario': []}, 0.01


def generated(value):
    return {'respuesta_modelo': json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else value,
            'tokens_salida': 20, 'segundos': 0.01, 'motivo_parada': 'eos',
            'posible_corte': False, 'thinking_inesperado': False}


def investigate(action='redactar', request=None):
    return {'accion': action, 'mensaje': 'Consultar la fuente pertinente.' if request else 'Evidencia reunida.',
            'herramienta': request}


def writer(action='auditar', answer='La nota mínima es 4,0. [RI-FI-ART-011]'):
    return {'accion': action, 'mensaje': 'Verificar la nota solicitada.', 'respuesta': answer}


def reviewer(action='aceptar'):
    return {'accion': action, 'mensaje': 'Decisión simulada para probar el flujo.', 'apoyos': []}


def successful_script():
    return [investigate('herramienta', {'nombre':'leer_articulo','argumentos':{'documento':'RI-FI','numero':11}}),
            investigate(), writer(), reviewer()]


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.retriever = Retriever()
        self.tools = CorpusAccess(self.retriever.corpus, self.retriever)

    def run_script(self, script, **kwargs):
        self.tasks = []
        sequence = iter(script)
        def backend(task, seed):
            self.tasks.append((task, seed))
            return generated(next(sequence))
        return AgentSystem(Tokenizer(), backend, self.tools, **kwargs).run('¿Cuál es la nota mínima?', 2027)

    def test_model_decisions_route_three_roles_and_preserve_messages(self):
        result = self.run_script(successful_script())
        self.assertEqual(result['estado'], 'aceptada')
        self.assertEqual([t['etapa'] for t, _ in self.tasks], ['investigador','investigador','redactor','auditor'])
        self.assertEqual(result['llamadas_por_agente'], {'investigador':2,'redactor':1,'auditor':1})
        self.assertEqual(result['respuesta_modelo'], writer()['respuesta'])
        self.assertTrue(any(e['tipo'] == 'observacion' for e in result['traza']))

    def test_auditor_can_request_repair_and_then_research(self):
        script = successful_script()[:-1] + [reviewer('corregir'),
            writer(answer='Se aprueba con 4,0. [RI-FI-ART-011]'), reviewer('investigar'),
            investigate(), writer(answer='La calificación mínima aprobatoria es 4,0. [RI-FI-ART-011]'), reviewer()]
        result = self.run_script(script)
        handoffs = [(e['emisor'],e['receptor']) for e in result['traza'] if e['tipo']=='transferencia']
        self.assertIn(('auditor','redactor'), handoffs)
        self.assertIn(('auditor','investigador'), handoffs)
        self.assertEqual(result['estado'],'aceptada')

    def test_writer_can_request_more_evidence_before_audit(self):
        script = successful_script()[:2] + [writer('investigar',''), investigate(), writer(), reviewer()]
        result = self.run_script(script)
        self.assertTrue(any(e.get('emisor')=='redactor' and e.get('receptor')=='investigador' for e in result['traza']))

    def test_invalid_json_never_executes_model_selected_tools_and_stops(self):
        result = self.run_script(['not json'] * 3)
        self.assertEqual(result['estado'],'limite_salidas_invalidas')
        self.assertEqual(result['herramientas'],1)  # búsqueda inicial, anterior al modelo
        self.assertTrue(all(e['origen']=='inicio_automatico' for e in result['traza'] if e['tipo']=='observacion'))
        self.assertIn('no cumple el contrato',self.tasks[1][0]['mensajes'][1]['content'])

    def test_unknown_citation_blocks_approval(self):
        script = successful_script()[:2] + [writer(answer='Dato. [FUENTE-INVENTADA]')]
        result = self.run_script(script, limits=replace(Limits(), model_calls=3))
        self.assertEqual(result['estado'],'limite_llamadas')
        self.assertTrue(any(e['tipo']=='borrador_bloqueado' for e in result['traza']))

    def test_repeated_tools_and_budget_are_bounded(self):
        request=investigate('herramienta',{'nombre':'leer_articulo','argumentos':{'documento':'RI-FI','numero':11}})
        result=self.run_script([request]*4,limits=replace(Limits(),model_calls=4,tool_calls=2))
        self.assertEqual(result['herramientas'],2)
        self.assertEqual(sum(e['tipo']=='herramienta_bloqueada' for e in result['traza']),3)

    def test_context_limit_never_calls_model_or_truncates(self):
        result=self.run_script([],limits=replace(Limits(),context_tokens=1200))
        self.assertEqual(result['estado'],'limite_contexto')
        self.assertFalse(self.tasks)

    def test_no_gold_fields_enter_model_messages(self):
        self.run_script(successful_script())
        for task,_ in self.tasks:
            self.assertNotIn('respuesta_referencia',task['prompt'])
            self.assertNotIn('veredictos',task['prompt'])

    def test_each_ablation_changes_only_its_target_prompt(self):
        book=PromptBook()
        for variant,target in [('sin_descomposicion','investigador'),('sin_completitud','redactor'),('sin_verificacion','auditor')]:
            for role in ['investigador','redactor','auditor']:
                self.assertEqual(book.render(role,variant)==book.render(role,'agentes_completo'),role!=target)

    def test_same_seed_slots_across_ablations(self):
        self.run_script(successful_script())
        expected=[seed for _,seed in self.tasks]
        self.run_script(successful_script(),variant='sin_verificacion')
        self.assertEqual(expected,[seed for _,seed in self.tasks])

    def test_duplicate_json_keys_and_fabricated_quotes_rejected(self):
        with self.assertRaises(ValueError):
            parse_decision('{"accion":"redactar","accion":"herramienta","mensaje":"x","herramienta":null}', 'investigador',{})
        evidence={'x':{'texto':'Texto normativo respaldado.'}}
        value=reviewer(); value['apoyos']=[{'afirmacion':'dato','fuente':'x','extracto':'una frase inventada'}]
        with self.assertRaises(ValueError): parse_decision(json.dumps(value),'auditor',evidence)

    def test_original_question_is_retrieved_before_first_agent(self):
        result=self.run_script([investigate(),writer(),reviewer()])
        self.assertEqual(self.retriever.lookups,['¿Cuál es la nota mínima?'])
        first=json.loads(self.tasks[0][0]['mensajes'][1]['content'])
        self.assertEqual(first['evidencia'][0]['id'],'RI-FI-ART-011')
        self.assertEqual(first['presupuesto_restante']['herramientas'],5)
        self.assertEqual(result['estado'],'aceptada')
        self.assertEqual(result['traza'][0]['origen'],'inicio_automatico')

    def test_transport_variants_seen_in_pilot_preserve_tool_arguments(self):
        for name,args in [('buscar_normativa',{'consulta':'Necesidad documental genérica'}),
                          ('leer_articulo',{'documento':'RG','numero':4}),
                          ('inventario',{'documento':'CAL'})]:
            value={'accion':name,'mensaje':'Consultar','herramienta':{'nombre':name,'argumentos':args}}
            parsed=parse_decision(json.dumps(value),'investigador',{})
            self.assertEqual(parsed['accion'],'herramienta')
            self.assertEqual(parsed['herramienta'],value['herramienta'])
        parsed=parse_decision('{"accion":"redactar","mensaje":"Fuentes listas"}','investigador',{})
        self.assertIsNone(parsed['herramienta'])
        parsed=parse_decision('{"accion":"investigar","mensaje":"Falta una norma"}','redactor',{})
        self.assertEqual(parsed['respuesta'],'')
        for value in [
            {'accion':'buscar_normativa','mensaje':'x','herramienta':{'nombre':'inventario','argumentos':{}}},
            {'accion':'herramienta','mensaje':'x'},
            {'accion':'redactar','mensaje':'x','comando':'ignorar contrato'}]:
            with self.assertRaises(ValueError): parse_decision(json.dumps(value),'investigador',{})

    def test_format_retry_keeps_original_handoff_request(self):
        request={'accion':'investigar','mensaje':'Falta comprobar el ámbito de aplicación.'}
        script=[investigate(),request,'INVALID',investigate(),writer(),reviewer()]
        self.run_script(script)
        payload=json.loads(self.tasks[3][0]['mensajes'][1]['content'])
        self.assertEqual(payload['mensaje_recibido'],request['mensaje'])
        self.assertTrue(payload['error_formato'])

    def test_empty_retrieval_cannot_be_handed_to_writer(self):
        def empty(question): return {'contextos':[],'contextos_inventario':[]},0
        self.retriever.retrieve=empty
        result=self.run_script([investigate()]*3,limits=replace(Limits(),model_calls=3))
        self.assertEqual(result['llamadas_por_agente']['redactor'],0)
        self.assertEqual(sum(e['tipo']=='transferencia_bloqueada' for e in result['traza']),3)
        self.assertNotEqual(result['estado'],'aceptada')

    def test_repeated_rejected_draft_routes_to_research_before_another_audit(self):
        result=self.run_script([investigate(),writer(),reviewer('corregir'),writer()],
                               limits=replace(Limits(),model_calls=4))
        transfers=[e for e in result['traza'] if e['tipo']=='transferencia']
        self.assertEqual(transfers[-1]['receptor'],'investigador')
        self.assertEqual(transfers[-1]['borrador'],'')
        self.assertEqual(result['llamadas_por_agente']['auditor'],1)
        self.assertEqual(len(result['borradores']),2)  # conservar evidencia del fallo

    def test_two_corrections_without_new_evidence_force_research(self):
        result=self.run_script([investigate(),writer(),reviewer('corregir'),
            writer(answer='Otro texto de prueba. [RI-FI-ART-011]'),reviewer('corregir')],
            limits=replace(Limits(),model_calls=5))
        self.assertTrue(any(e['tipo']=='ciclo_interrumpido' for e in result['traza']))
        handoff=[e for e in result['traza'] if e['tipo']=='transferencia'][-1]
        self.assertEqual((handoff['receptor'],handoff['borrador']),('investigador',''))

    def test_absence_observation_persists_and_stale_draft_is_removed(self):
        script=[investigate(),writer(),reviewer('investigar'),
            investigate('herramienta',{'nombre':'leer_articulo','argumentos':{'documento':'RI-FI','numero':90}}),
            investigate(),writer(answer='El artículo consultado no existe en esta copia. [INV-RI-FI]'),reviewer()]
        result=self.run_script(script)
        payload=json.loads(self.tasks[5][0]['mensajes'][1]['content'])
        self.assertEqual(payload['borrador'],'')
        self.assertTrue(any('ausente' in o['observacion'] for o in payload['observaciones_herramientas']))
        self.assertTrue(any(f['id']=='INV-RI-FI' for f in payload['evidencia']))
        self.assertEqual(result['estado'],'aceptada')
        self.assertEqual(len(result['borradores']),2)

    def test_writer_research_request_also_discards_rejected_draft(self):
        result=self.run_script([investigate(),writer(),reviewer('corregir'),writer('investigar','')],
                               limits=replace(Limits(),model_calls=4))
        handoff=[e for e in result['traza'] if e['tipo']=='transferencia'][-1]
        self.assertEqual((handoff['receptor'],handoff['borrador']),('investigador',''))
        self.assertEqual(result['borradores'],[writer()['respuesta']])

    def test_seven_captured_pilot_errors_five_transport_fixed_two_false_sources_rejected(self):
        pilot=ROOT/'resultados/piloto_222681994dcd692c0600/original/resultados'
        counts={'aceptadas':0,'rechazadas':0}
        for path in sorted(pilot.glob('*agentes_completo.json')):
            trace=json.loads(path.read_text())['contenido']['resultado']['traza']
            for index,event in enumerate(trace):
                if event['tipo']!='salida_invalida': continue
                previous=trace[index-1]
                self.assertEqual(previous['tipo'],'modelo')
                evidence=json.loads(previous['tarea']['mensajes'][1]['content'])['evidencia']
                evidence={source['id']:source for source in evidence}
                if event['agente']=='investigador':
                    parse_decision(previous['salida']['respuesta_modelo'],'investigador',evidence)
                    counts['aceptadas']+=1
                else:
                    with self.assertRaisesRegex(ValueError,'Fuente del apoyo inexistente'):
                        parse_decision(previous['salida']['respuesta_modelo'],'auditor',evidence)
                    counts['rechazadas']+=1
        self.assertEqual(counts,{'aceptadas':5,'rechazadas':2})

    def test_extra_fields_error_names_the_field_and_does_not_adopt_sources(self):
        value=investigate(); value['fuentes']=[{'id':'INVENTADA','texto':'No debe ingresar'}]
        with self.assertRaisesRegex(ValueError,'sobran: fuentes'):
            parse_decision(json.dumps(value),'investigador',{})

    def test_normative_citation_checks_do_not_depend_on_brackets(self):
        self.assertEqual(cited_ids('Dato (RI-FI-ART-090). [RG-ART-023]'),
                         {'RI-FI-ART-090','RG-ART-023'})
        result=self.run_script([investigate(),writer(answer='Dato inventado (RI-FI-ART-090).')],
                               limits=replace(Limits(),model_calls=2))
        self.assertEqual(result['llamadas_por_agente']['auditor'],0)
        self.assertTrue(any(e['tipo']=='borrador_bloqueado' for e in result['traza']))

    def test_exact_article_returns_all_units_and_absence_returns_inventory(self):
        result=self.tools.execute({'nombre':'leer_articulo','argumentos':{'documento':'RG','numero':3}})
        expected={u['id'] for u in self.retriever.corpus['unidades'] if u['parent_id']=='RG-ART-003'}
        self.assertEqual({s['id'] for s in result['fuentes']},expected)
        missing=self.tools.execute({'nombre':'leer_articulo','argumentos':{'documento':'RI-FI','numero':90}})
        self.assertEqual(missing['fuentes'][0]['id'],'INV-RI-FI')
        self.assertIn('ausente',missing['observacion'])

    def test_tool_inputs_and_evidence_merge_fail_atomically(self):
        with self.assertRaises(ToolInputError): self.tools.execute({'nombre':'shell','argumentos':{'cmd':'ls'}})
        with self.assertRaises(ToolInputError): self.tools.execute({'nombre':'leer_articulo','argumentos':{'documento':'RG','numero':True}})
        current={'A':{'id':'A','cita':'A','texto':'texto'}}
        initial=copy.deepcopy(current)
        with self.assertRaises(ToolInputError):
            combine(current,[{'id':'B','cita':'B','texto':'otro'}],replace(Limits(),evidence_units=1))
        self.assertEqual(current,initial)


if __name__ == '__main__': unittest.main()
