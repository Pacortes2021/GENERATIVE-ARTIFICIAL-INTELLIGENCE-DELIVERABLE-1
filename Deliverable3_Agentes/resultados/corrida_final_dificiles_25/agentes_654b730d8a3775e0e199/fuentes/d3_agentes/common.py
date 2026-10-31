"""Identidad de artefactos, presupuestos y prompts externos."""
import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TECHNIQUES = {
    'descomposicion': ('investigador', 'descomposicion.txt'),
    'completitud': ('redactor', 'completitud.txt'),
    'verificacion': ('auditor', 'verificacion.txt'),
}
VARIANTS = ('baseline_directo', 'rag_d2', 'agentes_completo',
            'sin_descomposicion', 'sin_completitud', 'sin_verificacion')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temp.replace(path)


def sealed_save(path, value):
    save(path, {'contenido': value, 'sha256': digest(value)})


def sealed_load(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    if set(value) != {'contenido', 'sha256'} or digest(value['contenido']) != value['sha256']:
        raise ValueError('Artefacto alterado: ' + str(path))
    return value['contenido']


@dataclass(frozen=True)
class Limits:
    model_calls: int = 12
    tool_calls: int = 6
    invalid_outputs: int = 3
    context_tokens: int = 8192
    output_tokens: int = 1024
    token_margin: int = 64
    evidence_units: int = 28
    evidence_characters: int = 30000

    def __post_init__(self):
        if any(type(v) is not int or v <= 0 for v in asdict(self).values()):
            raise ValueError('Los límites deben ser enteros positivos.')
        if self.context_tokens <= self.output_tokens + self.token_margin:
            raise ValueError('No queda espacio para la entrada.')


class PromptBook:
    def __init__(self, directory=None):
        self.directory = Path(directory or ROOT / 'prompts')
        names = [r + '.txt' for r in ('investigador', 'redactor', 'auditor')]
        names += [v[1] for v in TECHNIQUES.values()]
        self.texts = {name: (self.directory / name).read_text(encoding='utf-8') for name in names}
        if any(not text.strip() for text in self.texts.values()):
            raise ValueError('Prompt vacío.')

    def render(self, role, variant):
        if variant not in VARIANTS[2:] or role not in ('investigador', 'redactor', 'auditor'):
            raise ValueError('Agente o variante inválida.')
        blocks = [self.texts[role + '.txt']]
        for technique, (target, filename) in TECHNIQUES.items():
            if target == role and variant != 'sin_' + technique:
                blocks.append(self.texts[filename])
        return '\n\n'.join(blocks)

    def identity(self):
        return {name: hashlib.sha256(self.texts[name].encode()).hexdigest() for name in sorted(self.texts)}


class ContextLimit(ValueError):
    pass


def task_for(tokenizer, messages, limits, stage):
    prompt = tokenizer.apply_chat_template(messages, tokenize=False,
                                          add_generation_prompt=True, enable_thinking=False)
    count = len(tokenizer(prompt, add_special_tokens=False, truncation=False)['input_ids'])
    if count + limits.output_tokens + limits.token_margin > limits.context_tokens:
        raise ContextLimit(f'{stage}: {count} tokens de entrada; no cabe sin truncar.')
    return {'etapa': stage, 'mensajes': messages, 'prompt': prompt,
            'tokens_entrada': count, 'prompt_sha256': digest(prompt)}
