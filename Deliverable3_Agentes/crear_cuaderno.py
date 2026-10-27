"""Crea el notebook nuevo desde estos fuentes y los componentes expresos de D2."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import textwrap
from d3_agentes.bridge import read_assets, locations
from d3_agentes.common import ROOT, file_sha


def bundle_sources():
    corpus, fragments, questions, config = read_assets()
    d2, data = locations()
    validation = json.loads((data / 'validacion.json').read_text())
    for source in validation['fuentes'].values():
        if file_sha(ROOT.parent / 'Corpus' / source['archivo']) != source['sha256']:
            raise ValueError('Los PDF ya no corresponden al corpus de D2.')
    sources = {}
    for p in sorted((ROOT / 'd3_agentes').glob('*.py')) + sorted((ROOT / 'prompts').glob('*.txt')):
        sources[str(p.relative_to(ROOT))] = p.read_text(encoding='utf-8')
    for name in ('experimento.py', 'sistema.py', 'recuperador_portable.py'):
        sources['d2_runtime/' + name] = (d2 / name).read_text(encoding='utf-8')
    for name in ('corpus.json', 'fragmentos_busqueda.json'):
        if file_sha(data / name) != validation['artefactos_sha256'][name]:
            raise ValueError('Corpus distinto del validado en D2.')
        sources['data/' + name] = (data / name).read_text(encoding='utf-8')
    sources['data/preguntas.json'] = json.dumps(questions, ensure_ascii=False)
    sources['data/configuracion.json'] = json.dumps(config, ensure_ascii=False)
    return sources


def build(destination=None):
    sources = bundle_sources()
    hashes = {n: hashlib.sha256(v.encode()).hexdigest() for n, v in sources.items()}
    raw = json.dumps(sources, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    packed = gzip.compress(raw, mtime=0)
    encoded = base64.b64encode(packed).decode()
    literal = '\n'.join('    ' + repr(s) for s in textwrap.wrap(encoded, 96))
    cells = []
    def md(text):
        cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': textwrap.dedent(text).strip()})
    def code(text, hidden=False):
        source = textwrap.dedent(text).strip()
        compile(source, 'notebook-cell', 'exec')
        cells.append({'cell_type': 'code', 'metadata': {'cellView': 'form'} if hidden else {},
                      'source': source, 'execution_count': None, 'outputs': []})
    md('''
    # Deliverable 3 · Tres agentes sobre normativa UdeC · v4

    Implementación nueva: investigador, redactor y auditor, todos con Qwen3-4B.
    No utiliza los prototipos previos de D3. Integra el corpus, recuperador y controles de D2.

    **Piloto v4 pendiente de evaluación en T4.** La versión anterior obtuvo 1/4 con agentes y 2/4 con D2
    en los cuatro casos de diagnóstico. Este cuaderno incorpora las correcciones; la corrida anterior se conserva en el repositorio.
    La aceptación del auditor no es una calificación. Reinicia la sesión si usaste el cuaderno anterior.
    Este cuaderno genera respuestas reales: requiere GPU CUDA, descarga modelos públicos y conserva trazas.
    1. Selecciona GPU en Colab y ejecuta preparación y carga.
    2. «Ejecutar todo» corre por defecto el piloto de cuatro preguntas (12 respuestas finales).
       La consulta individual es opcional. Los mensajes entre agentes se muestran en pantalla.
    3. La sección 8 crea el ZIP y solicita su descarga. Si el navegador no la permite, descarga
       el archivo desde el panel Archivos de Colab. No cierres la sesión antes de conservarlo.
    4. El lote completo y las ablaciones se activan expresamente después de comprobar el piloto.
    ''')
    md('## 1. Dependencias (reinicia la sesión si ya había otras versiones cargadas)')
    code('''
    import sys, subprocess, importlib.metadata
    PINNED = {'transformers':'4.57.6', 'accelerate':'1.11.0', 'bitsandbytes':'0.48.1',
              'sentence-transformers':'5.1.2', 'tokenizers':'0.22.2'}
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q',
                          *[p+'=='+v for p,v in PINNED.items()]])
    for module, package in [(p.replace('-', '_'), p) for p in PINNED] + [
        ('numpy','numpy'), ('scipy','scipy'), ('torch','torch'), ('sklearn','scikit-learn'),
        ('huggingface_hub','huggingface-hub')]:
        loaded = sys.modules.get(module)
        if loaded is not None and hasattr(loaded, '__version__'):
            if loaded.__version__ != importlib.metadata.version(package):
                raise RuntimeError('Reinicia la sesión: versión anterior en memoria de ' + package)
    print('Dependencias instaladas. No se cargó ningún modelo todavía.')
    ''')
    md('## 2. Restaurar código, prompts externos y corpus incluidos')
    code('BUNDLE_B64 = (\n' + literal + '\n)\n' +
         'EXPECTED = ' + repr(hashlib.sha256(packed).hexdigest()) + '\n' +
         'FILE_HASHES = ' + repr(hashes) + '\n' + '''
import base64, gzip, hashlib, json, sys
from pathlib import Path
packed = base64.b64decode(BUNDLE_B64, validate=True)
if hashlib.sha256(packed).hexdigest() != EXPECTED:
    raise ValueError('Paquete alterado.')
sources = json.loads(gzip.decompress(packed))
if set(sources) != set(FILE_HASHES):
    raise ValueError('Inventario del paquete incorrecto.')
WORKDIR = Path.cwd() / ('d3_nuevo_runtime_' + EXPECTED[:16])
for name, text in sources.items():
    path = Path(name)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Ruta no permitida.')
    if hashlib.sha256(text.encode()).hexdigest() != FILE_HASHES[name]:
        raise ValueError('Fuente alterada: ' + name)
    target = WORKDIR / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')
previous = sys.modules.get('d3_agentes')
if previous is not None and Path(previous.__file__).resolve().parent != (WORKDIR / 'd3_agentes').resolve():
    raise RuntimeError('Reinicia la sesión para cargar esta versión de D3.')
if str(WORKDIR.resolve()) not in sys.path:
    sys.path.insert(0, str(WORKDIR.resolve()))
del BUNDLE_B64, sources, packed
print('Código y prompts restaurados en', WORKDIR)
''', True)
    md('## 3. Cargar una sola instancia Qwen y el índice E5')
    code('''
    from d3_agentes.runtime import load, execute
    from d3_agentes.common import VARIANTS
    from d3_agentes.experiment import export, audit_zip, sealed_load
    USAR_DRIVE = False
    if USAR_DRIVE:
        from google.colab import drive
        drive.mount('/content/drive')
        OUTPUT = Path('/content/drive/MyDrive/GenIA_D3_Agentes/runs')
    else:
        OUTPUT = Path.cwd() / 'd3_agentes_runs'
    ENV = load(OUTPUT)
    print('Preguntas de desarrollo:', len(ENV['questions']))
    ''')
    md('''
    ## 4. Consulta individual con mensajes visibles

    Compara baseline, D2 y tres agentes. Repetir exactamente entradas/configuración reutiliza checkpoints
    y lo indica. Para una repetición nueva cambia ETIQUETA y conserva todos los intentos.
    ''')
    code('''
    PREGUNTA = ''
    ETIQUETA = 'consulta-v4'
    if PREGUNTA.strip():
        RUN_DIR = None  # Evita conservar la ruta de otra corrida si esta ejecución se interrumpe.
        RUN_DIR = execute(ENV, [{'id':1, 'pregunta':PREGUNTA, 'categoria':'nueva'}], OUTPUT,
                          variants=VARIANTS[:3], tag=ETIQUETA, verbose=True)
    else:
        print('Consulta individual omitida. La sección 5 ejecutará el piloto por defecto.')
    ''')
    md('''
    ## 5. Piloto v4 de cuatro casos conocidos

    **Versión corregida tras tres pilotos.** Reinicia la sesión de Colab antes de cargarla.
    Se acepta una forma equivalente de solicitud explícita de herramienta y se reforzaron los bloques de remisiones, alcance y verificación. Se mantienen argumentos, controles y presupuestos.
    Su calidad todavía debe verificarse con esta nueva ejecución en T4.

    P05: caso correcto en D2; P25: omisión; P38: recuperación/cita; P41: premisa falsa.
    Se eligieron para comprobar comportamientos distintos, no para estimar exactitud.
    Conserva rechazos, JSON inválido y regresiones. La aceptación interna no sustituye a la pauta externa.
    **Activado por defecto:** al ejecutar todas las celdas se generan 12 respuestas finales
    (4 preguntas × baseline/D2/agentes). La sección 8 exporta y descarga el ZIP.
    ''')
    code('''
    EJECUTAR_PILOTO = True
    if EJECUTAR_PILOTO:
        RUN_DIR = None
        RUN_DIR = execute(ENV, [q for q in ENV['questions'] if q['id'] in [5,25,38,41]], OUTPUT,
                          variants=VARIANTS[:3], tag='piloto-v4', verbose=True)
        print('Piloto terminado. ZIP guardado:', RUN_DIR.with_suffix('.zip'))
        print('Continúa hasta la sección 8 para descargarlo.')
    else:
        print('Piloto desactivado.')
    ''')
    md('''
    ## 6. Lote completo con tres ablaciones

    Activa solo después de comprobar el piloto y congelar esta versión. Produce 300 respuestas finales
    (50 × 6 condiciones), con múltiples llamadas por sistema de agentes. Puede exceder una sesión gratuita;
    Drive y checkpoints permiten continuar. Estas 50 preguntas son desarrollo, no generalización.
    Ablaciones: sin descomposición explícita del investigador, sin lista de completitud del redactor,
    sin verificación explícita por afirmación del auditor. Se conservan agentes, herramientas e interfaces.
    ''')
    code('''
    EJECUTAR_LOTE = False
    if EJECUTAR_LOTE:
        RUN_DIR = None
        RUN_DIR = execute(ENV, ENV['questions'], OUTPUT, variants=VARIANTS,
                          tag='lote-v4', verbose=False)
    else:
        print('Lote desactivado; no se han generado resultados de ablaciones.')
    ''')
    md('## 7. Inspeccionar una traza completa')
    code('''
    ID = 25
    VARIANTE = 'agentes_completo'
    if globals().get('RUN_DIR') is not None:
        path = RUN_DIR / 'resultados' / f'P{ID:03}_{VARIANTE}.json'
        if path.exists():
            saved = sealed_load(path)
            for event in saved['resultado']['traza']:
                print(json.dumps(event, ensure_ascii=False, indent=2))
            print('Respuesta final:', saved['resultado']['respuesta_modelo'])
        else:
            print('Ese caso aún no está completo en la corrida seleccionada.')
    else:
        print('Selecciona una corrida después de generar.')
    ''')
    md('''
    ## 8. Descargar o recuperar una corrida parcial

    Esta celda encuentra las corridas guardadas aunque RUN_DIR no haya quedado asignado. Por defecto
    conserva todas: si hay varias, las reúne como ZIP individuales dentro de una descarga.
    CARPETA_A_EXPORTAR permite elegir solo una. Un ZIP parcial conserva las llamadas ya realizadas.
    Si el navegador no inicia la descarga, usa el panel Archivos de Colab y la ruta que se imprime.
    ''')
    code('''
    from d3_agentes.downloads import prepare_download
    CARPETA_A_EXPORTAR = ''  # Vacío: recuperar todas las corridas de OUTPUT.
    ZIP = prepare_download(OUTPUT, CARPETA_A_EXPORTAR or None)
    if ZIP is not None:
        print('ZIP listo:', ZIP.resolve(), '| bytes:', ZIP.stat().st_size, flush=True)
        print('Si no se descarga automáticamente: panel Archivos > este ZIP > Descargar.', flush=True)
        try:
            from google.colab import files
            files.download(str(ZIP))
        except Exception as exc:
            print('No se pudo solicitar la descarga automática:', str(exc))
            print('El ZIP sigue guardado en:', ZIP.resolve())
    ''')
    md('''
    ## Evaluación y entrega

    Aplicar la pauta D2 fuera de la generación, con motivos y hashes por respuesta. Los CSV de preguntas
    conocidas son compatibles con su evaluador. Para preguntas nuevas hay que elaborar referencias.
    No reutilizar etiquetas antiguas para nuevas salidas. Reportar aciertos, regresiones, límites,
    errores de formato, tokens y tiempo, junto con las ablaciones; consultar EVALUACION.md del repositorio.
    El informe y el video finales se preparan después de obtener resultados reales.
    ''')
    for i, cell in enumerate(cells):
        cell['id'] = f'd3-nuevo-{i:02}'
    nb = {'nbformat': 4, 'nbformat_minor': 5, 'metadata': {
        'kernelspec': {'display_name':'Python 3', 'language':'python', 'name':'python3'},
        'language_info': {'name':'python'}, 'colab': {'name':'Deliverable3_Agentes_Colab.ipynb'},
        'accelerator':'GPU'}, 'cells': cells}
    target = Path(destination or ROOT / 'Deliverable3_Agentes_Colab.ipynb')
    target.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return target


if __name__ == '__main__':
    print(build())
