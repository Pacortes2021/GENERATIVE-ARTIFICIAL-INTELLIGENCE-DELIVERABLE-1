# Ejecutar en Colab después de las secciones 1, 2 y 3. No ejecuta el piloto.
from pathlib import Path, PurePosixPath
import hashlib, json, zipfile, urllib.request
from d3_agentes.experiment import audit_zip, prepare, export
from d3_agentes.common import Limits, PromptBook, sealed_load

SNAPSHOT_URL = 'https://raw.githubusercontent.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/79a20243b715fdf6fb4f25ff15bc0ab447eb4298/Deliverable3_Agentes/resultados/lote_99b9b55bd79d4572f743/snapshots/20261027T182649Z_035de300.zip'
SNAPSHOT_SHA256 = 'b8a05014c9340bec2154262063ab600090db59f6a97201add07f08b352447568'
backup = Path('/content/respaldo_original_035de300.zip')
if not backup.exists():
    urllib.request.urlretrieve(SNAPSHOT_URL, backup)
assert hashlib.sha256(backup.read_bytes()).hexdigest() == SNAPSHOT_SHA256, 'Respaldo distinto.'
summary = audit_zip(backup)
assert summary['completadas'] == 35 and summary['esperadas'] == 300
with zipfile.ZipFile(backup) as archive:
    config = json.loads(archive.read('configuracion.json'))['contenido']
    assert config['inferencia'] == ENV['settings'], 'Entorno distinto: revisar versiones antes de reanudar.'
    assert config['preguntas'] == ENV['questions'] and config['variantes'] == list(VARIANTS)
    RUN_DIR, actual = prepare(ENV['questions'], ENV['retriever'], ENV['settings'], OUTPUT,
                              tuple(config['variantes']), Limits(**config['limites']),
                              config['etiqueta'], PromptBook())
    assert actual == config and RUN_DIR.name == 'agentes_99b9b55bd79d4572f743'
    for name in archive.namelist():
        relative = PurePosixPath(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        target = RUN_DIR / name
        if target.exists():
            if name == 'configuracion.json':
                assert sealed_load(target) == config, 'Configuracion incompatible.'
            elif name.startswith(('resultados/', 'llamadas/', 'fuentes/', 'prompts/')):
                assert target.read_bytes() == archive.read(name), 'Conflicto con respaldo: ' + name
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(name))
export(RUN_DIR)
print('LOTE REAL: 50 preguntas x 6 condiciones. Respaldo de 35 respuestas restaurado y verificado.', flush=True)
print('Las respuestas conservadas se omiten; se generan solo las pendientes.', flush=True)
try:
    RUN_DIR = execute(ENV, ENV['questions'], OUTPUT, variants=VARIANTS, tag='lote-v4', verbose=False)
finally:
    export(RUN_DIR)
    progress = audit_zip(RUN_DIR.with_suffix('.zip'))
    print('RESPALDO:', progress['completadas'], '/', progress['esperadas'], RUN_DIR.with_suffix('.zip'), flush=True)
    from google.colab import files
    files.download(str(RUN_DIR.with_suffix('.zip')))
