"""Exportación para notebook, incluida recuperación sin una variable RUN_DIR."""
import json
import zipfile
from pathlib import Path
from .experiment import export, audit_zip


def prepare_download(output, selected=None):
    """Devuelve un ZIP real; si hay varias corridas recupera todas en un contenedor."""
    output = Path(output)
    if selected is not None and str(selected).strip():
        candidates = [Path(selected)]
        if not (candidates[0] / 'configuracion.json').is_file():
            raise ValueError('La carpeta seleccionada no contiene una corrida: ' + str(selected))
    else:
        candidates = sorted(p for p in output.glob('agentes_*')
                            if p.is_dir() and (p / 'configuracion.json').is_file())
    if not candidates:
        print('No hay corridas guardadas: cargar los modelos no genera respuestas. '
              'Ejecuta la sección 5 con EJECUTAR_PILOTO = True y vuelve a esta celda. '
              'No necesitas volver a cargar Qwen.', flush=True)
        return None
    archives, inventory = [], []
    for folder in candidates:
        archive = export(folder)
        summary = audit_zip(archive)
        print(f"{folder.name}: {summary['completadas']}/{summary['esperadas']} respuestas; "
              f"{'completa' if summary['completa'] else 'parcial; conserva checkpoints'}.", flush=True)
        archives.append(archive)
        inventory.append({'zip': archive.name, 'resumen': summary})
    if len(archives) == 1:
        return archives[0]
    target = output / 'resultados_d3_todas_las_corridas.zip'
    temporary = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('corridas.json', json.dumps(inventory, ensure_ascii=False, indent=2))
        for item in archives:
            archive.write(item, item.name)
    temporary.replace(target)
    print(f'Se reunieron {len(archives)} corridas; cada ZIP interno conserva su propia configuración.', flush=True)
    return target
