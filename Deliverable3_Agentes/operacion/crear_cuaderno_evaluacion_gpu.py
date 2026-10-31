"""Genera el cuaderno de Colab definitivo para evaluar con Qwen3-4B en GPU T4."""
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

def build_cuaderno_evaluacion_gpu():
    # 1. Cargar las 10 preguntas de premisas falsas
    csv_base = ROOT / "resultados" / "lote_99b9b55bd79d4572f743" / "original" / "agentes_completo.csv"
    df_base = pd.read_csv(csv_base)
    preguntas_p41_p50 = []
    for _, row in df_base.iloc[40:50].iterrows():
        preguntas_p41_p50.append({
            "id": int(row["pregunta_id"]),
            "pregunta": str(row["pregunta"]),
            "categoria": str(row["categoria"])
        })
        
    # 2. Cargar las 25 preguntas difíciles
    preguntas_dificiles_path = ROOT / 'conjunto_dificil_25/paquete_dificiles_Pablo/preguntas.json'
    preguntas_dificiles = json.loads(preguntas_dificiles_path.read_text(encoding='utf-8'))
    
    print(f"Cargadas: {len(preguntas_p41_p50)} premisas falsas y {len(preguntas_dificiles)} difíciles.")

    # 3. Empaquetar fuentes con código y prompts actualizados
    sources = crear_cuaderno.bundle_sources()
    sources["data/preguntas_p41_p50.json"] = json.dumps(preguntas_p41_p50, ensure_ascii=False)
    sources["data/preguntas_dificiles.json"] = json.dumps(preguntas_dificiles, ensure_ascii=False)
    
    raw = json.dumps(sources, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    packed = gzip.compress(raw, mtime=0)
    encoded = base64.b64encode(packed).decode()
    literal = '\n'.join('    ' + repr(s) for s in textwrap.wrap(encoded, 96))
    expected = hashlib.sha256(packed).hexdigest()
    file_hashes = {n: hashlib.sha256(v.encode()).hexdigest() for n, v in sources.items()}
    
    cells = []
    def md(text, ident):
        cells.append({'cell_type': 'markdown', 'metadata': {'id': ident}, 'source': textwrap.dedent(text).strip().splitlines(keepends=True)})
    def code(text, ident):
        source = textwrap.dedent(text).strip()
        cells.append({'cell_type': 'code', 'metadata': {'id': ident}, 'source': source.splitlines(keepends=True),
                      'execution_count': None, 'outputs': []})
                      
    md('''
    # 🚀 Deliverable 3 · Evaluación Oficial en GPU T4 (Qwen3-4B)
    
    Este cuaderno reproduce las evaluaciones oficiales del sistema Multi-Agente en **Google Colab** utilizando la GPU Tesla T4 y el modelo oficial fijado por la asignatura (**Qwen/Qwen3-4B** cuantizado en 4 bits NF4).
    
    ### Objetivos de esta corrida:
    1. **Parte 1 (P41 a P50):** Verificar empíricamente en GPU la resolución del *livelock* en las 10 preguntas con premisas falsas (salto de 0/10 a 9/10).
    2. **Parte 2 (H01 a H25):** Evaluar las 25 consultas difíciles con el validador normalizado y las reglas de parada en modo `agentes_completo`.
    
    Ambas pruebas corren exclusivamente en modo Multi-Agente (`agentes_completo`), completándose en ~15 minutos.
    ''', 'header')
    
    code('''
    # 1. Verificación de Acelerador GPU CUDA
    import torch
    print("PyTorch versión:", torch.__version__)
    print("CUDA disponible:", torch.cuda.is_available())
    if not torch.cuda.is_available():
        raise RuntimeError("⚠️ Debes activar GPU T4 en: Entorno de ejecución > Cambiar tipo de entorno > T4 GPU.")
    print("GPU detectada:", torch.cuda.get_device_name(0))
    ''', 'check-gpu')
    
    code('''
    # 2. Instalación de dependencias fijadas por contrato
    !pip install --quiet \\
        transformers==4.57.6 \\
        accelerate==1.11.0 \\
        bitsandbytes==0.48.1 \\
        sentence-transformers==5.1.2 \\
        tokenizers==0.22.2
    print("✅ Dependencias fijadas instaladas correctamente.")
    ''', 'install-deps')
    
    restore_code = f'''
    # 3. Desempaquetado del entorno, prompts y conjuntos de preguntas
    BUNDLE_B64 = (
{literal}
    )
    EXPECTED = {repr(expected)}
    FILE_HASHES = {repr(file_hashes)}
    
    import base64, gzip, hashlib, json, sys
    from pathlib import Path

    packed = base64.b64decode(BUNDLE_B64, validate=True)
    if hashlib.sha256(packed).hexdigest() != EXPECTED:
        raise ValueError("Paquete alterado o corrupto.")
    sources = json.loads(gzip.decompress(packed))
    if set(sources) != set(FILE_HASHES):
        raise ValueError("Inventario del paquete alterado.")

    WORKDIR = Path.cwd() / f"d3_gpu_runtime_{{EXPECTED[:16]}}"
    for name, text in sources.items():
        path = WORKDIR / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    sys.path.insert(0, str(WORKDIR.resolve()))
    print("✅ Fuentes restauradas en:", WORKDIR.name)
    '''
    code(restore_code, 'restore-bundle')
    
    code('''
    # 4. Carga de E5 y del modelo oficial Qwen3-4B en GPU T4
    from pathlib import Path
    from d3_agentes.runtime import load, execute
    
    OUTPUT = Path("/content/d3_evaluacion_runs")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    ENV = load(OUTPUT)
    print("✅ Modelo oficial Qwen3-4B cargado exitosamente en GPU.")
    ''', 'load-model')
    
    code('''
    # 5. PARTE 1: Ejecutar las 10 preguntas con premisas falsas (P41 a P50)
    import json, pandas as pd
    from d3_agentes.common import VARIANTS
    
    preguntas_p41_p50 = json.loads((WORKDIR / "data/preguntas_p41_p50.json").read_text(encoding="utf-8"))
    print(f"🚀 Iniciando evaluación de {len(preguntas_p41_p50)} preguntas con premisas falsas (P41-P50)...")
    
    out_dir_p41_p50 = execute(ENV, preguntas_p41_p50, OUTPUT, variants=("agentes_completo",), tag="eval_p41_p50_gpu", verbose=True)
    print("✅ Parte 1 completada en:", out_dir_p41_p50.name)
    
    # Mostrar resumen inmediato
    csv_p41 = out_dir_p41_p50 / "agentes_completo.csv"
    if csv_p41.exists():
        df_res = pd.read_csv(csv_p41)
        print("\\n=== RESULTADOS PREMISAS FALSAS (P41-P50) ===")
        for _, r in df_res.iterrows():
            print(f"P{int(r['pregunta_id'])}: estado={r['estado']} | llamadas={r['llamadas_modelo']} | resp={str(r['respuesta_modelo'])[:60]}...")
    ''', 'run-p41-p50')
    
    code('''
    # 6. PARTE 2: Ejecutar las 25 consultas difíciles (H01 a H25)
    preguntas_dificiles = json.loads((WORKDIR / "data/preguntas_dificiles.json").read_text(encoding="utf-8"))
    print(f"🚀 Iniciando evaluación de {len(preguntas_dificiles)} preguntas difíciles (H01-H25)...")
    
    out_dir_dificiles = execute(ENV, preguntas_dificiles, OUTPUT, variants=("agentes_completo",), tag="eval_dificiles_gpu", verbose=True)
    print("✅ Parte 2 completada en:", out_dir_dificiles.name)
    
    # Mostrar resumen inmediato
    csv_dif = out_dir_dificiles / "agentes_completo.csv"
    if csv_dif.exists():
        df_dif = pd.read_csv(csv_dif)
        print("\\n=== RESULTADOS PREGUNTAS DIFÍCILES (H01-H25) ===")
        for idx, r in df_dif.iterrows():
            print(f"H{idx+1:02d} (id {int(r['pregunta_id'])}): estado={r['estado']} | llamadas={r['llamadas_modelo']} | resp={str(r['respuesta_modelo'])[:60]}...")
    ''', 'run-dificiles')
    
    code('''
    # 7. Descargar respaldos ZIP auditables
    from google.colab import files
    from d3_agentes.downloads import prepare_download
    
    zip_p41 = prepare_download(out_dir_p41_p50, None)
    zip_dif = prepare_download(out_dir_dificiles, None)
    
    print("ZIP Premisas Falsas:", zip_p41)
    print("ZIP Difíciles:", zip_dif)
    
    try:
        if zip_p41 and zip_p41.exists(): files.download(str(zip_p41))
        if zip_dif and zip_dif.exists(): files.download(str(zip_dif))
    except Exception as e:
        print("Descarga manual desde Archivos:", e)
    ''', 'download-zips')

    nb = {
        'nbformat': 4,
        'nbformat_minor': 5,
        'metadata': {
            'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python'},
            'colab': {'name': 'Deliverable3_Evaluacion_GPU_Colab.ipynb'},
            'accelerator': 'GPU'
        },
        'cells': cells
    }
    
    target = ROOT / 'Deliverable3_Evaluacion_GPU_Colab.ipynb'
    target.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('Cuaderno creado con éxito:', target.name)
    print(f'Total bytes: {target.stat().st_size}')

if __name__ == '__main__':
    build_cuaderno_evaluacion_gpu()
