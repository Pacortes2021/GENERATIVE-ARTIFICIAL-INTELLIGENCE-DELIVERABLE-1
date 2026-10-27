"""Pruebas de persistencia, controles D2, evaluación y notebook nuevo."""
import contextlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from test_agents import ROOT, Retriever, Tokenizer, generated, investigate, writer, reviewer
from d3_agentes.bridge import d2_modules
from d3_agentes.common import Limits, VARIANTS, digest, sealed_load, sealed_save
from d3_agentes.experiment import run, audit_zip, export
from crear_cuaderno import build, bundle_sources
from evaluar import prepare_all, compare


SETTINGS={'ejecucion':'simulacion_pruebas','semilla_base':2026,
          'generacion':{'max_new_tokens':1024},'modelo':'SIMULACION_EXPLICITA'}


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.retriever=Retriever()
        self.question=[self.retriever.questions[0]]
        self.calls=[]

    def model(self,task,seed):
        self.calls.append((task,seed))
        if task['etapa']=='investigador':
            payload=json.loads(task['mensajes'][1]['content'])
            return generated(investigate() if payload['evidencia'] else investigate('herramienta',
                {'nombre':'leer_articulo','argumentos':{'documento':'RI-FI','numero':11}}))
        if task['etapa']=='redactor': return generated(writer())
        if task['etapa']=='auditor': return generated(reviewer())
        return generated('4,0. [RI-FI-ART-011]')

    def execute(self,path,generate=None,variants=VARIANTS):
        with contextlib.redirect_stdout(io.StringIO()):
            return run(self.question,self.retriever,Tokenizer(),generate or self.model,SETTINGS,path,
                       variants=variants,verbose=False)

    def test_all_six_conditions_have_same_inputs_and_no_quality_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=self.execute(tmp)
            summary=audit_zip(folder.with_suffix('.zip'))
            self.assertEqual(summary['completadas'],6)
            self.assertTrue(summary['completa'])
            self.assertIsNone(summary['exactitud'])
            self.assertEqual(summary['ejecucion'],'simulacion_pruebas')
            result=sealed_load(folder/'resultados/P001_agentes_completo.json')
            self.assertEqual(result['uso']['llamadas_modelo'],3)

    def test_baseline_and_d2_prompts_are_original_and_share_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.execute(tmp,variants=VARIANTS[:2])
        experiment,d2=d2_modules()
        baseline=next((task,seed) for task,seed in self.calls if task['etapa']=='baseline_directo')
        rag=next((task,seed) for task,seed in self.calls if task['etapa']=='rag_d2')
        self.assertEqual(baseline[0]['mensajes'][0]['content'],d2.BASELINE_SYSTEM)
        case,_=self.retriever.retrieve(self.question[0]['pregunta'])
        self.assertEqual(rag[0]['mensajes'],experiment.messages(case,'rag_estructurado'))
        self.assertEqual(baseline[1],rag[1])

    def test_resume_completed_run_does_not_generate(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=self.execute(tmp)
            count=len(self.calls)
            snapshot=(folder/'resultados/P001_agentes_completo.json').read_bytes()
            self.execute(tmp)
            self.assertEqual(len(self.calls),count)
            self.assertEqual(snapshot,(folder/'resultados/P001_agentes_completo.json').read_bytes())

    def test_interruption_preserves_prior_model_calls_and_exports_partial(self):
        def crash(task,seed):
            if task['etapa']=='redactor': raise RuntimeError('GPU interrumpida: prueba simulada')
            return self.model(task,seed)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError): self.execute(tmp,generate=crash,variants=('agentes_completo',))
            archive=next(Path(tmp).glob('*.zip'))
            self.assertFalse(audit_zip(archive)['completa'])
            count=len(self.calls)
            folder=self.execute(tmp,variants=('agentes_completo',))
            self.assertEqual(len(self.calls)-count,2)  # solo redactor y auditor faltantes
            result=sealed_load(folder/'resultados/P001_agentes_completo.json')
            self.assertEqual(result['uso']['llamadas_nuevas_este_intento'],2)
            self.assertTrue(any(o.get('resultado',{}).get('checkpoint_reutilizado')
                                for o in result['resultado']['traza'] if o['tipo']=='observacion'))
            self.assertEqual(result['uso']['llamadas_modelo'],3)

    def test_tampered_result_and_zip_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=self.execute(tmp,variants=VARIANTS[:2])
            bad=Path(tmp)/'bad.zip'
            with zipfile.ZipFile(folder.with_suffix('.zip')) as src,zipfile.ZipFile(bad,'w') as dst:
                for name in src.namelist(): dst.writestr(name,b'bad' if name=='baseline_directo.csv' else src.read(name))
            with self.assertRaises(ValueError): audit_zip(bad)
            p=folder/'resultados/P001_baseline_directo.json'
            v=json.loads(p.read_text()); v['contenido']['resultado']['respuesta_modelo']='Alterado'
            p.write_text(json.dumps(v))
            with self.assertRaises(ValueError): self.execute(tmp,variants=VARIANTS[:2])

    def test_gold_fields_and_duplicate_conditions_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): self.execute(tmp,variants=('rag_d2','rag_d2'))
            self.question[0]={**self.question[0],'respuesta_referencia':'prohibida'}
            with self.assertRaises(ValueError): self.execute(tmp)

    def test_evaluation_stays_pending_then_checks_all_conditions_and_csv_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=self.execute(tmp)
            judgments=Path(tmp)/'evaluacion'
            prepare_all(folder,judgments)
            with self.assertRaises(ValueError): compare(folder,judgments)
            for variant in VARIANTS:
                p=judgments/variant/'veredictos.json'; value=json.loads(p.read_text())
                value['evaluador']='PRUEBA SIMULADA'; value['modalidad']='humana'
                for row in value['evaluaciones']:
                    row.update(correcta=True,motivo='Etiqueta sintética exclusiva de la prueba de integración.')
                p.write_text(json.dumps(value))
            report=compare(folder,judgments)
            self.assertEqual(report['ejecucion'],'simulacion_pruebas')
            self.assertEqual(len(report['metricas']),6)
            with (folder/'rag_d2.csv').open('a') as stream: stream.write('\n')
            with self.assertRaises(ValueError): compare(folder,judgments)

    def test_notebook_is_reproducible_restores_sources_and_excludes_old_prototypes(self):
        sources=bundle_sources()
        self.assertFalse(any('harness' in name or 'veredictos' in name or 'referencias.json' in name for name in sources))
        self.assertEqual(set(json.loads(sources['data/preguntas.json'])[0]),{'id','pregunta','categoria'})
        self.assertEqual(len(json.loads(sources['data/preguntas.json'])),50)
        with tempfile.TemporaryDirectory() as tmp:
            p=build(Path(tmp)/'nuevo.ipynb'); before=p.read_bytes(); build(p)
            self.assertEqual(before,p.read_bytes())
            nb=json.loads(p.read_text())
            import nbformat
            nbformat.validate(nbformat.from_dict(nb))
            for cell in nb['cells']:
                if cell['cell_type']=='code':
                    compile(cell['source'],'cell','exec')
                    self.assertFalse(cell['outputs'])
            cell=next(c['source'] for c in nb['cells'] if 'BUNDLE_B64 = (' in c['source'])
            # Ejecutar restauración en un subproceso para no contaminar módulos del test.
            import subprocess,sys
            proc=subprocess.run([sys.executable,'-c',cell],cwd=tmp,text=True,capture_output=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            restored=next(Path(tmp).glob('d3_nuevo_runtime_*'))
            self.assertEqual((restored/'d3_agentes/core.py').read_text(),sources['d3_agentes/core.py'])
            self.assertEqual((restored/'prompts/investigador.txt').read_text(),sources['prompts/investigador.txt'])


if __name__=='__main__': unittest.main()
