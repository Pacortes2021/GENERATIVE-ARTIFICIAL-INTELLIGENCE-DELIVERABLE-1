"""Regresión: un tokenizador automático diferente no debe alterar el corpus."""
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest

from tokenizers import Tokenizer, models, pre_tokenizers, processors
from sistema import configure_e5_tokenizer


class CanonicalTokenizerTests(unittest.TestCase):
    def fixture(self, directory):
        raw = Tokenizer(models.WordLevel({'<s>':0, '<pad>':1, '</s>':2, '<unk>':3, '<mask>':4, 'dato':5}, unk_token='<unk>'))
        raw.pre_tokenizer = pre_tokenizers.Whitespace()
        raw.post_processor = processors.TemplateProcessing(single='<s> $A </s>',
            pair='<s> $A </s> </s> $B </s>', special_tokens=[('<s>',0),('</s>',2)])
        path=Path(directory)/'tokenizer.json'
        raw.save(str(path))
        fragments=[{'id':'unidad-prueba','texto_embedding':'dato dato','tokens_e5':4}]
        # Reproduce la condición del error: el cargador automático entrega un conteo distinto.
        encoder=types.SimpleNamespace(tokenizer=lambda text,**kwargs:{'input_ids':[5]})
        return encoder,path,fragments,hashlib.sha256(path.read_bytes()).hexdigest()

    def test_replaces_divergent_auto_tokenizer_and_preserves_fragments(self):
        with tempfile.TemporaryDirectory() as tmp:
            encoder,path,fragments,sha=self.fixture(tmp)
            before=json.dumps(fragments)
            report=configure_e5_tokenizer(encoder,path,fragments,sha,Path(tmp)/'diagnostico.json')
            self.assertEqual(report['estado'],'OK')
            self.assertEqual(report['diferencias_iniciales'],[{'id':'unidad-prueba','inicial':1,'canonico':4}])
            self.assertEqual(encoder.tokenizer('dato dato',truncation=False,padding=False)['input_ids'],[0,5,5,2])
            self.assertEqual(before,json.dumps(fragments))

    def test_wrong_file_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            encoder,path,fragments,sha=self.fixture(tmp)
            with self.assertRaisesRegex(ValueError,'no corresponde al corpus'):
                configure_e5_tokenizer(encoder,path,fragments,'wrong',Path(tmp)/'diagnostico.json')
            self.assertEqual(json.loads((Path(tmp)/'diagnostico.json').read_text())['estado'],'archivo_distinto')

    def test_real_corpus_mismatch_is_not_hidden_or_recounted(self):
        with tempfile.TemporaryDirectory() as tmp:
            encoder,path,fragments,sha=self.fixture(tmp)
            fragments[0]['tokens_e5']=8
            with self.assertRaisesRegex(ValueError,'unidad-prueba'):
                configure_e5_tokenizer(encoder,path,fragments,sha,Path(tmp)/'diagnostico.json')
            self.assertEqual(fragments[0]['tokens_e5'],8)
            report=json.loads((Path(tmp)/'diagnostico.json').read_text())
            self.assertEqual(report['diferencias'][0]['real'],4)
            self.assertEqual(report['diferencias'][0]['esperado'],8)

    def test_same_count_but_different_ids_are_detected_and_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            encoder,path,fragments,sha=self.fixture(tmp)
            encoder.tokenizer=lambda text,**kwargs:{'input_ids':[0,3,3,2]}
            report=configure_e5_tokenizer(encoder,path,fragments,sha,Path(tmp)/'diagnostico.json')
            self.assertEqual(len(report['diferencias_iniciales']),1)
            self.assertEqual(encoder.tokenizer('dato dato')['input_ids'],[0,5,5,2])


if __name__=='__main__': unittest.main()
