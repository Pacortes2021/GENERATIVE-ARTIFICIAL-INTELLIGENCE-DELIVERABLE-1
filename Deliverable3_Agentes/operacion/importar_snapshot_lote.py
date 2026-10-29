"""Audita un ZIP del lote contra un respaldo previo y conserva una copia intacta."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from d3_agentes.experiment import audit_zip


def verificar(nuevo, previo):
    actual, anterior = audit_zip(nuevo), audit_zip(previo)
    if actual['esperadas'] != 300 or actual['ejecucion'] != 'modelo_real':
        raise ValueError('No es el lote real completo de 300 condiciones.')
    ancla = ROOT / 'resultados/lote_99b9b55bd79d4572f743/snapshots/20261028T071051Z_039de300.zip'
    with zipfile.ZipFile(ancla) as trusted:
        config_fijada = json.loads(trusted.read('configuracion.json'))['contenido']
    with zipfile.ZipFile(nuevo) as a, zipfile.ZipFile(previo) as b:
        config = json.loads(a.read('configuracion.json'))['contenido']
        config_previa = json.loads(b.read('configuracion.json'))['contenido']
        if config != config_previa or config != config_fijada:
            raise ValueError('Configuración incompatible con el respaldo previo.')
        resultados = [n for n in b.namelist() if n.startswith('resultados/') and n.endswith('.json')]
        for name in resultados:
            if name not in a.namelist() or a.read(name) != b.read(name):
                raise ValueError('Respuesta previa perdida o alterada: ' + name)
    if actual['completadas'] < anterior['completadas']:
        raise ValueError('El respaldo nuevo retrocede.')
    return actual, len(resultados)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('nuevo', type=Path)
    parser.add_argument('--previo', type=Path, required=True)
    parser.add_argument('--solo-verificar', action='store_true')
    args = parser.parse_args()
    summary, preserved = verificar(args.nuevo, args.previo)
    data = args.nuevo.read_bytes()
    checksum = hashlib.sha256(data).hexdigest()
    print(f"Verificado: {summary['completadas']}/300; {preserved} respuestas previas intactas; SHA-256 {checksum}")
    if args.solo_verificar:
        return
    destination = ROOT / 'resultados/lote_99b9b55bd79d4572f743/snapshots'
    destination.mkdir(parents=True, exist_ok=True)
    for p in destination.glob('*.zip'):
        if hashlib.sha256(p.read_bytes()).hexdigest() == checksum:
            print('Esta copia exacta ya está conservada:', p)
            return
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target = destination / f"{stamp}_{summary['completadas']:03}de300.zip"
    with target.open('xb') as stream:
        stream.write(data)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == checksum
    metadata = {'capturada_utc': stamp, 'zip': target.name, 'zip_sha256': checksum,
                'integridad': 'audit_zip_correcta', 'resumen': summary,
                'respuestas_previas_intactas': preserved,
                'respaldo_previo': args.previo.name,
                'respaldo_previo_sha256': hashlib.sha256(args.previo.read_bytes()).hexdigest(),
                'origen_descarga': args.nuevo.name,
                'nota': 'Mismo lote y configuración; copia original intacta. Exactitud pendiente de evaluación externa.'}
    with target.with_suffix('.json').open('x', encoding='utf-8') as stream:
        json.dump(metadata, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print('Conservado:', target)


if __name__ == '__main__':
    main()
