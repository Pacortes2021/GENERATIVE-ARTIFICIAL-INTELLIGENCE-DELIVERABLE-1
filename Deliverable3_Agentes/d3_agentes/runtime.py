"""Carga real de E5 y una única instancia Qwen3-4B para todas las condiciones."""
import importlib.metadata
import platform
import time
from pathlib import Path
from .bridge import read_assets, d2_modules
from .common import save, file_sha

PINNED = {'transformers': '4.57.6', 'accelerate': '1.11.0', 'bitsandbytes': '0.48.1',
          'sentence-transformers': '5.1.2', 'tokenizers': '0.22.2'}


def load(output):
    for package, version in PINNED.items():
        if importlib.metadata.version(package) != version:
            raise RuntimeError(f'Instala {package}=={version} y reinicia la sesión.')
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, AutoConfig
    from sentence_transformers import SentenceTransformer
    from huggingface_hub import hf_hub_download
    if not torch.cuda.is_available():
        raise RuntimeError('Esta ejecución requiere GPU CUDA. En Colab: Entorno de ejecución > Cambiar tipo > GPU.')
    corpus, fragments, questions, config = read_assets()
    if config['modelo'] != 'Qwen/Qwen3-4B' or config['revision'] != '1cfa9a7208912126459214e8b04321603b3df60c':
        raise ValueError('Modelo distinto del control D2 fijado.')
    _, d2 = d2_modules()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(4)
    torch.manual_seed(0)
    started = time.perf_counter()
    print('Cargando E5 e indexando el corpus de D2 en CPU...', flush=True)
    encoder = SentenceTransformer(config['embedding_modelo'], revision=config['embedding_revision'], device='cpu')
    tokenizer_path = hf_hub_download(config['embedding_modelo'], 'tokenizer.json', revision=config['embedding_revision'])
    diagnostic_path = output / ('tokenizador_e5_' + file_sha(tokenizer_path)[:16] + '.json')
    diagnostic = d2.configure_e5_tokenizer(encoder, tokenizer_path, fragments,
                                          config['embedding_tokenizer_sha256'], diagnostic_path)
    retriever = d2.LiveRetriever(corpus, fragments, encoder)
    index_seconds = time.perf_counter() - started
    print('Cargando una instancia Qwen3-4B en GPU...', flush=True)
    started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(config['modelo'], revision=config['revision'])
    model_config = AutoConfig.from_pretrained(config['modelo'], revision=config['revision'])
    if config['max_context_tokens'] > model_config.max_position_embeddings:
        raise ValueError('Contexto superior al soportado por el modelo.')
    compute = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                                     bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=compute)
    model = AutoModelForCausalLM.from_pretrained(config['modelo'], revision=config['revision'],
             quantization_config=quantization, torch_dtype=compute, device_map={'': 0}, attn_implementation='sdpa')
    model.eval()
    model_seconds = time.perf_counter() - started
    generation = d2.QwenGenerator(model, tokenizer, config['generacion'])
    settings = {**config, 'ejecucion': 'modelo_real', 'thinking': False,
                'cuantizacion': {'bits': 4, 'tipo': 'nf4', 'double_quant': True, 'compute_dtype': str(compute)},
                'gpu': torch.cuda.get_device_name(0), 'cuda': torch.version.cuda,
                'python': platform.python_version(),
                'versiones': {p: importlib.metadata.version(p) for p in [*PINNED, 'torch', 'numpy']}}
    preparation = {'segundos_e5': index_seconds, 'segundos_qwen': model_seconds, 'diagnostico_e5': diagnostic}
    print('Listo: todas las llamadas usan los mismos pesos y muestreo de D2 (temperatura 0,7).', flush=True)
    return {'retriever': retriever, 'tokenizer': tokenizer, 'generate': generation,
            'settings': settings, 'questions': questions, 'preparation': preparation}


def execute(environment, questions, output, **kwargs):
    from .experiment import run, export
    folder = run(questions, environment['retriever'], environment['tokenizer'], environment['generate'],
                 environment['settings'], output, **kwargs)
    path = folder / 'preparacion.json'
    if not path.exists():
        save(path, environment['preparation'])
    export(folder)
    return folder
