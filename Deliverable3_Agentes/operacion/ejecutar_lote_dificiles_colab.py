# Ejecutar en Colab después de las secciones 1, 2 y 3.
# Lote de 25 preguntas difíciles (150 respuestas = 5 bloques de 30 respuestas).
from pathlib import Path, PurePosixPath
import hashlib, json, zipfile, urllib.request, shutil
from d3_agentes.experiment import audit_zip, prepare, export
from d3_agentes.common import Limits, PromptBook, sealed_load, VARIANTS
import d3_agentes.experiment as experiment_module
from d3_agentes.runtime import execute

class BloqueTerminado(BaseException):
    """Parada operativa normal después de exportar una respuesta completa."""

def preparar_corrida_dificiles(ENV, OUTPUT):
    """Prepara o recupera el directorio de ejecución para las 25 preguntas difíciles."""
    config_esperada = {
        'preguntas': ENV['questions'],
        'variantes': list(VARIANTS),
        'limites': Limits(),
        'etiqueta': 'dificiles-25'
    }
    RUN_DIR, actual = prepare(ENV['questions'], ENV['retriever'], ENV['settings'], OUTPUT,
                              VARIANTS, Limits(), 'dificiles-25', PromptBook())
    export(RUN_DIR)
    print(f'Directorio de corrida: {RUN_DIR.name}', flush=True)
    return RUN_DIR

def ejecutar_bloque_dificil(ENV, OUTPUT, RUN_DIR, descargar, tamaño=30, total=150):
    """Ejecuta un bloque de 30 respuestas (5 preguntas x 6 variantes) y exporta snapshot."""
    original_export = experiment_module.export
    original_export(RUN_DIR)
    zip_path = RUN_DIR.with_suffix('.zip')
    inicial = audit_zip(zip_path)['completadas'] if zip_path.exists() else 0
    
    if inicial >= total:
        print(f'Las {total} respuestas ya están conservadas. No se ejecuta inferencia.')
        return RUN_DIR
        
    objetivo = min((inicial // tamaño + 1) * tamaño, total)
    numero = objetivo // tamaño
    print(f'======================================================================')
    print(f'BLOQUE {numero}/5: {inicial}/{total} conservadas; objetivo {objetivo}/{total}.', flush=True)
    print(f'Se generarán {objetivo - inicial} respuestas pendientes sin repetir las guardadas.', flush=True)
    print(f'======================================================================', flush=True)
    
    backup_progress = {'n': inicial}

    def export_bloque(folder):
        archive_path = original_export(folder)
        resumen_path = Path(folder) / 'resumen_tecnico.json'
        if not resumen_path.exists():
            return archive_path
        n = json.loads(resumen_path.read_text())['completadas']
        if n >= backup_progress['n'] + 6 or n >= objetivo:
            snapshot = Path(folder).parent / (Path(folder).name + f'_respaldo_{n:03}de{total}.zip')
            shutil.copy2(archive_path, snapshot)
            try:
                descargar(str(snapshot))
                print(f'--> DESCARGA SOLICITADA: {n}/{total} ({snapshot.name})', flush=True)
            except Exception as exc:
                print(f'Descargar desde Archivos de Colab: {snapshot.name} ({type(exc).__name__})', flush=True)
            backup_progress['n'] = n
        if n >= objetivo:
            raise BloqueTerminado()
        return archive_path

    experiment_module.export = export_bloque
    try:
        execute(ENV, ENV['questions'], OUTPUT, variants=VARIANTS, tag='dificiles-25', verbose=False)
    except BloqueTerminado:
        print(f'BLOQUE {numero}/5 TERMINADO ({objetivo}/{total}).', flush=True)
    finally:
        experiment_module.export = original_export
        original_export(RUN_DIR)
        progress = audit_zip(RUN_DIR.with_suffix('.zip'))
        print(f'RESPALDO VERIFICADO: {progress["completadas"]}/{progress["esperadas"]}', flush=True)
        if progress['completadas'] < objetivo:
            try:
                descargar(str(RUN_DIR.with_suffix('.zip')))
            except Exception as exc:
                print('Descargar respaldo parcial desde Archivos:', type(exc).__name__, flush=True)
    return RUN_DIR

CONTINUAR_HASTA_FINAL = True  # True: ejecuta automáticamente los 5 bloques hasta 150

if __name__ == '__main__':
    from google.colab import files
    RUN_DIR = preparar_corrida_dificiles(ENV, OUTPUT)
    if globals().get('CONTINUAR_HASTA_FINAL', False):
        while True:
            RUN_DIR = ejecutar_bloque_dificil(ENV, OUTPUT, RUN_DIR, files.download, tamaño=30, total=150)
            progress = audit_zip(RUN_DIR.with_suffix('.zip'))
            if progress['completadas'] >= 150:
                print('¡ÉXITO TOTAL! 150/150 respuestas de preguntas difíciles completadas y respaldadas.', flush=True)
                break
    else:
        RUN_DIR = ejecutar_bloque_dificil(ENV, OUTPUT, RUN_DIR, files.download, tamaño=30, total=150)
