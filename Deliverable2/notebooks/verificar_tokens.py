"""Comprueba los 100 prompts con el tokenizador real, sin descargar pesos."""
import argparse
import hashlib
import json
from pathlib import Path

import nbformat
from transformers import AutoTokenizer, AutoConfig
from experimento import VARIANTES, make_tasks
from crear_cuaderno import REVISION

HERE = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tokenizador-local', type=Path)
    args = parser.parse_args()
    path = HERE / 'Deliverable2_RAG_2_variantes_Colab.ipynb'
    notebook = nbformat.read(path, as_version=4)
    namespace = {}
    for cell in notebook.cells:
        if cell.cell_type == 'code' and 'PAYLOAD_JSON =' in cell.source:
            exec(cell.source, namespace)
    if args.tokenizador_local:
        tokenizer = AutoTokenizer.from_pretrained(args.tokenizador_local, local_files_only=True)
        config = AutoConfig.from_pretrained(args.tokenizador_local, local_files_only=True)
        revision_file = args.tokenizador_local / 'revision.txt'
        if not revision_file.exists() or revision_file.read_text().strip() != REVISION:
            raise ValueError('La carpeta local debe incluir revision.txt con la revisión fijada.')
    else:
        tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-4B', revision=REVISION)
        config = AutoConfig.from_pretrained('Qwen/Qwen3-4B', revision=REVISION)
    tasks = make_tasks(namespace['PAYLOAD']['casos'], tokenizer, 8192, 1024)
    report = {'tokenizador_revision': REVISION, 'limite_operativo': 8192, 'reserva_salida': 1024, 'margen': 64,
              'max_position_embeddings': config.max_position_embeddings, 'total_prompts': len(tasks),
              'notebook_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'alcance': 'Plantilla y conteo real comprobados; no se ejecutó inferencia de Qwen ni GPU Colab localmente.',
              'variantes': {}}
    for variant in VARIANTES:
        counts = [t['tokens_entrada'] for t in tasks if t['variante'] == variant]
        report['variantes'][variant] = {'media_tokens_entrada': round(sum(counts)/len(counts), 2),
                                       'max_tokens_entrada': max(counts), 'max_entrada_salida_margen': max(counts)+1088}
    (HERE / 'validacion_tokens.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
