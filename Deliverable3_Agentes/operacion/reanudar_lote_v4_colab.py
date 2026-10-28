# Ejecutar en Colab después de las secciones 1, 2 y 3. No ejecuta el piloto.
from pathlib import Path, PurePosixPath
import hashlib, json, zipfile, urllib.request
from d3_agentes.experiment import audit_zip, prepare, export
from d3_agentes.common import Limits, PromptBook, sealed_load, VARIANTS

SNAPSHOT_URL = 'https://raw.githubusercontent.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/22963a0f4e364e1fbc807883091fe6aebc7d38ca/Deliverable3_Agentes/resultados/lote_99b9b55bd79d4572f743/snapshots/20261028T071051Z_039de300.zip'
SNAPSHOT_SHA256 = 'a9a3b86a82bf2ef1a530ad630ea6c5d8366a3c70d1a19ad6f30bf37d56a4d10d'

def restaurar_respaldo(ENV, OUTPUT):
    backup = Path('/content/respaldo_original_039de300.zip')
    if not backup.exists():
        urllib.request.urlretrieve(SNAPSHOT_URL, backup)
    assert hashlib.sha256(backup.read_bytes()).hexdigest() == SNAPSHOT_SHA256, 'Respaldo distinto.'
    summary = audit_zip(backup)
    assert summary['completadas'] == 39 and summary['esperadas'] == 300
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
    return RUN_DIR

class BloqueTerminado(BaseException):
    """Parada operativa normal después de exportar una respuesta completa."""


def ejecutar_bloque(ENV, OUTPUT, RUN_DIR, descargar, tamaño=30):
    """Conserva identidad y semillas del lote; ejecuta hasta el siguiente límite."""
    import shutil
    import d3_agentes.experiment as experiment_module
    from d3_agentes.runtime import execute
    original_export = experiment_module.export
    original_export(RUN_DIR)
    inicial = audit_zip(RUN_DIR.with_suffix('.zip'))['completadas']
    if inicial == 300:
        print('Las 300 respuestas ya están conservadas. No se ejecuta inferencia.')
        return RUN_DIR
    assert 0 <= inicial < 300 and tamaño == 30
    objetivo = min((inicial // tamaño + 1) * tamaño, 300)
    numero = objetivo // tamaño
    print(f'BLOQUE {numero}/10: {inicial}/300 conservadas; objetivo {objetivo}/300.', flush=True)
    print(f'Se generarán {objetivo - inicial} respuestas pendientes, sin repetir las guardadas.', flush=True)
    backup_progress = {'n': inicial}

    def export_bloque(folder):
        archive_path = original_export(folder)
        n = json.loads((Path(folder) / 'resumen_tecnico.json').read_text())['completadas']
        # Copias inmutables para que la siguiente exportación no altere una descarga activa.
        if n >= backup_progress['n'] + 6 or n >= objetivo:
            snapshot = Path(folder).parent / (Path(folder).name + f'_respaldo_{n:03}de300.zip')
            shutil.copy2(archive_path, snapshot)
            try:
                descargar(str(snapshot))
                print('DESCARGA SOLICITADA:', n, '/300', snapshot.name, flush=True)
            except Exception as exc:
                print('Descargar desde Archivos:', snapshot, type(exc).__name__, flush=True)
            backup_progress['n'] = n
        if n >= objetivo:
            raise BloqueTerminado()
        return archive_path

    # Solo capa de exportación en memoria. Fuentes, prompts, config y semillas intactos.
    # BaseException evita registrar esta parada prevista como error técnico del modelo.
    experiment_module.export = export_bloque
    try:
        execute(ENV, ENV['questions'], OUTPUT, variants=VARIANTS, tag='lote-v4', verbose=False)
    except BloqueTerminado:
        print(f'BLOQUE {numero}/10 TERMINADO. Verifica y conserva el ZIP antes del siguiente.', flush=True)
    finally:
        experiment_module.export = original_export
        original_export(RUN_DIR)
        progress = audit_zip(RUN_DIR.with_suffix('.zip'))
        print('RESPALDO VERIFICADO:', progress['completadas'], '/', progress['esperadas'], flush=True)
        if progress['completadas'] < objetivo:
            try:
                descargar(str(RUN_DIR.with_suffix('.zip')))
            except Exception as exc:
                print('Descargar respaldo parcial desde Archivos:', type(exc).__name__, flush=True)
    return RUN_DIR


if __name__ == '__main__':
    from google.colab import files
    RUN_DIR = restaurar_respaldo(ENV, OUTPUT)
    RUN_DIR = ejecutar_bloque(ENV, OUTPUT, RUN_DIR, files.download)
