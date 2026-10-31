"""Generador del cuaderno autónomo de Colab para probar las 3 opciones en P41-P50."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import sys
import textwrap
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import crear_cuaderno

def build_cuaderno_p41_p50():
    # 1. Obtener las 10 preguntas de premisas falsas (P41 a P50)
    csv_path = ROOT / "resultados" / "lote_99b9b55bd79d4572f743" / "original" / "agentes_completo.csv"
    df = pd.read_csv(csv_path)
    questions = []
    for _, row in df.iloc[40:50].iterrows():
        questions.append({
            "id": int(row["pregunta_id"]),
            "pregunta": str(row["pregunta"]),
            "categoria": str(row["categoria"])
        })
    print(f"Preguntas seleccionadas: {len(questions)} (IDs: {[q['id'] for q in questions]})")

    sources = crear_cuaderno.bundle_sources()
    sources["data/preguntas.json"] = json.dumps(questions, ensure_ascii=False)
    
    raw = json.dumps(sources, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    packed = gzip.compress(raw, mtime=0)
    encoded = base64.b64encode(packed).decode()
    literal = '\n'.join('    ' + repr(s) for s in textwrap.wrap(encoded, 96))
    expected = hashlib.sha256(packed).hexdigest()
    
    cells = []
    def md(text, ident):
        cells.append({'cell_type': 'markdown', 'metadata': {'id': ident}, 'source': textwrap.dedent(text).strip().splitlines(keepends=True)})
    def code(text, ident):
        source = textwrap.dedent(text).strip()
        cells.append({'cell_type': 'code', 'metadata': {'id': ident}, 'source': source.splitlines(keepends=True),
                      'execution_count': None, 'outputs': []})
    
    md('''
    # Deliverable 3 · Evaluación Experimental de Premisas Falsas (P41–P50)
    
    Este cuaderno ejecuta las **10 preguntas con premisas falsas / ausentes** del conjunto base
    bajo las tres intervenciones de solución al bucle (*livelock*) del Auditor:
    
    - **Opción 1**: Ajuste semántico del criterio de parada en `auditor.txt` (reconoce la ausencia normada como `aceptar`).
    - **Opción 2**: Consenso semántico en el orquestador (`core.py`, si Redactor y Auditor coinciden en que no existe, aprueba).
    - **Opción 3**: Flexibilización de apoyos para hechos negativos en `verificacion.txt`.
    
    Total de inferencias: 10 preguntas (toma solo ~5-8 minutos en GPU T4 de Colab).
    ''', 'intro-p41-p50')

    code('''
    # 1. Verificación de GPU CUDA
    import torch
    print("PyTorch:", torch.__version__)
    print("CUDA disponible:", torch.cuda.is_available())
    if not torch.cuda.is_available():
        raise RuntimeError("Activa GPU T4 en: Entorno de ejecución > Cambiar tipo de entorno > GPU T4.")
    print("GPU:", torch.cuda.get_device_name(0))
    ''', 'check-gpu')

    code('''
    # 2. Instalación de dependencias fijadas
    !pip install --quiet \
        transformers==4.57.6 \
        accelerate==1.11.0 \
        bitsandbytes==0.48.1 \
        sentence-transformers==5.1.2 \
        tokenizers==0.22.2
    ''', 'install-deps')

    code(f'''
    # 3. Desempaquetado del entorno y las 10 preguntas
    import base64, gzip, hashlib, json, shutil
    from pathlib import Path

    ARCHIVE = (
{literal}
    )
    EXPECTED_SHA256 = {expected!r}

    data = gzip.decompress(base64.b64decode(ARCHIVE))
    assert hashlib.sha256(gzip.compress(data, mtime=0)).hexdigest() == EXPECTED_SHA256
    files = json.loads(data.decode('utf-8'))

    ROOT = Path('workspace_p41_p50')
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True)

    for relpath, content in files.items():
        dest = ROOT / relpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding='utf-8')

    print(f"Entorno desempaquetado en {{ROOT}}. Total archivos: {{len(files)}}")
    ''', 'unpack')

    code('''
    # 4. Carga del Modelo Qwen3-4B y Retriever E5
    import sys
    sys.path.insert(0, str(Path("workspace_p41_p50").resolve()))

    from d3_agentes.runtime import load
    ENV = load("salida_runtime")
    print("Modelo y retriever cargados exitosamente.")
    ''', 'load-model')

    code('''
    # 5. Ejecución experimental de las 10 preguntas con la Opción 1 (Ajuste sutil del Auditor)
    from pathlib import Path
    from d3_agentes.runtime import execute
    from d3_agentes.experiment import export

    print("Ejecutando las 10 preguntas de premisas falsas con el Auditor actualizado (Opción 1)...")
    RUN_DIR = execute(ENV, ENV['questions'], Path("corrida_opcion1"), variants=['agentes_completo'], tag='p41-p50-opcion1', verbose=True)
    zip_path = RUN_DIR.with_suffix('.zip')
    print("Corrida completada y exportada a:", zip_path)
    ''', 'run-opcion1')

    code('''
    # 6. Descarga del archivo ZIP de resultados
    from google.colab import files
    files.download(str(zip_path))
    ''', 'download-results')

    notebook = {
        'cells': cells,
        'metadata': {
            'accelerator': 'GPU',
            'colab': {'name': 'Deliverable3_Test_P41_P50_Colab.ipynb', 'provenance': []},
            'kernelspec': {'display_name': 'Python 3', 'name': 'python3'},
            'language_info': {'name': 'python'}
        },
        'nbformat': 4,
        'nbformat_minor': 0
    }
    
    out_path = ROOT / "Deliverable3_Test_P41_P50_Colab.ipynb"
    out_path.write_text(json.dumps(notebook, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Cuaderno generado con éxito: {out_path} ({len(cells)} celdas)")

if __name__ == "__main__":
    build_cuaderno_p41_p50()
