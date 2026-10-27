"""Entrada CLI para GPU; los tests no pasan por este cargador."""
import argparse
from pathlib import Path
from d3_agentes.common import VARIANTS
from d3_agentes.runtime import load, execute


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    select = parser.add_mutually_exclusive_group(required=True)
    select.add_argument('--pregunta')
    select.add_argument('--ids', type=int, nargs='+')
    select.add_argument('--todas', action='store_true')
    parser.add_argument('--variantes', nargs='+', choices=VARIANTS, default=list(VARIANTS))
    parser.add_argument('--salida', type=Path, default=Path(__file__).parent / 'runs')
    parser.add_argument('--etiqueta', default='desarrollo-v4')
    parser.add_argument('--silencioso', action='store_true')
    args = parser.parse_args()
    if args.pregunta is not None and not args.pregunta.strip():
        parser.error('La pregunta no puede estar vacía.')
    if args.ids is not None and (len(set(args.ids)) != len(args.ids) or any(n < 1 or n > 50 for n in args.ids)):
        parser.error('Usa IDs distintos entre 1 y 50.')
    env = load(args.salida)
    questions = ([{'id': 1, 'pregunta': args.pregunta, 'categoria': 'nueva'}] if args.pregunta else
                 [q for q in env['questions'] if args.todas or q['id'] in args.ids])
    folder = execute(env, questions, args.salida, variants=tuple(args.variantes),
                     tag=args.etiqueta, verbose=not args.silencioso)
    print('Resultados y trazas:', folder)
    print('ZIP:', folder.with_suffix('.zip'))


if __name__ == '__main__':
    main()
