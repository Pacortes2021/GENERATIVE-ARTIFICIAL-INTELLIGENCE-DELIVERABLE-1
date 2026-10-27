"""Verifica E5 real y tokenización Qwen sin cargar pesos generativos ni calcular exactitud."""
import argparse
import json
from pathlib import Path
from d3_agentes.bridge import read_assets, d2_modules, source_identity
from d3_agentes.common import Limits, PromptBook, VARIANTS, task_for, file_sha, save
from d3_agentes.tools import CorpusAccess, combine
from d3_agentes.core import agent_payload


def validate(tokenizer_directory, output):
    import torch
    from sentence_transformers import SentenceTransformer
    from transformers import AutoTokenizer
    from huggingface_hub import snapshot_download
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    corpus,fragments,questions,config=read_assets()
    if (Path(tokenizer_directory)/'revision.txt').read_text().strip()!=config['revision']:
        raise ValueError('Revisión del tokenizador distinta de D2.')
    tokenizer=AutoTokenizer.from_pretrained(str(tokenizer_directory),local_files_only=True)
    experiment,d2=d2_modules()
    torch.set_num_threads(4)
    snapshot=Path(snapshot_download(config['embedding_modelo'],revision=config['embedding_revision'],local_files_only=True))
    encoder=SentenceTransformer(str(snapshot),device='cpu',local_files_only=True)
    diagnostic=d2.configure_e5_tokenizer(encoder,snapshot/'tokenizer.json',fragments,
                    config['embedding_tokenizer_sha256'],output/'tokenizador_e5.json')
    retriever=d2.LiveRetriever(corpus,fragments,encoder)
    tools,book,limits=CorpusAccess(corpus,retriever),PromptBook(),Limits()
    records=[]
    for q in questions:
        case,_=retriever.retrieve(q['pregunta'],q['id'],q['categoria'])
        chats={'baseline_directo':[{'role':'system','content':d2.BASELINE_SYSTEM},{'role':'user','content':q['pregunta']}],
               'rag_d2':experiment.messages(case,'rag_estructurado')}
        found=tools.execute({'nombre':'buscar_normativa','argumentos':{'consulta':q['pregunta']}})
        sources=combine({},found['fuentes'],limits)
        # El borrador es sintético y solo sirve para medir longitud, no para simular un acierto.
        for variant in VARIANTS[2:]:
            for role in ('investigador','redactor','auditor'):
                payload=agent_payload(q['pregunta'],sources,
                    'Borrador sintético exclusivo de la prueba de presupuesto. '*20,
                    'Verifica la suficiencia de la evidencia.',
                    [{'solicitud':{'nombre':'buscar_normativa','argumentos':{'consulta':q['pregunta']}},
                      'observacion':found['observacion'],'fuentes':list(sources)}], '', 8, 5)
                chats[variant+'/'+role]=[{'role':'system','content':book.render(role,variant)},
                                        {'role':'user','content':json.dumps(payload,ensure_ascii=False)}]
        for name,chat in chats.items():
            task=task_for(tokenizer,chat,limits,name)
            records.append({'id':q['id'],'condicion_agente':name,'tokens_entrada':task['tokens_entrada']})
    inventories={doc:len(tools.execute({'nombre':'inventario','argumentos':{'documento':doc}})['fuentes'])
                 for doc in ('RG','RI-FI','CAL')}
    absent=tools.execute({'nombre':'leer_articulo','argumentos':{'documento':'RI-FI','numero':90}})
    assert absent['fuentes'][0]['id']=='INV-RI-FI'
    for doc in ('RG','RI-FI'):
        for parent in corpus['padres']:
            if parent['documento']==doc and parent.get('ambito')=='ordinario' and parent['tipo']=='articulo':
                result=tools.execute({'nombre':'leer_articulo','argumentos':{'documento':doc,'numero':parent['articulo']}})
                expected={u['id'] for u in corpus['unidades'] if u['parent_id']==parent['id']}
                assert {f['id'] for f in result['fuentes']}==expected
    report={'tipo':'recuperacion_y_tokenizacion_reales_sin_inferencia_Qwen','exactitud_d3':None,
            'preguntas':len(questions),'prompts_medidos':len(records),'max_tokens_entrada':max(r['tokens_entrada'] for r in records),
            'presupuesto_total':limits.context_tokens,'reserva_salida':limits.output_tokens,'margen':limits.token_margin,
            'indice_sha256':retriever.index_sha256,'archivos_sha256':source_identity(),
            'tokenizador_qwen_sha256':{p.name:file_sha(p) for p in Path(tokenizer_directory).glob('*.json')},
            'max_por_tipo':{name:max(r['tokens_entrada'] for r in records if r['condicion_agente']==name)
                            for name in sorted({r['condicion_agente'] for r in records})},
            'inventarios':inventories,'detalle':records,
            'limite':'Estos contextos no cubren todas las trayectorias posibles; cada llamada vuelve a medir su entrada.'}
    save(output/'reporte.json',report)
    return {k:v for k,v in report.items() if k not in ('detalle','archivos_sha256','tokenizador_qwen_sha256')}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tokenizador',required=True,type=Path)
    p.add_argument('--salida',required=True,type=Path)
    args=p.parse_args()
    print(json.dumps(validate(args.tokenizador,args.salida),ensure_ascii=False,indent=2))
