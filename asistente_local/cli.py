"""Interfaz de línea de comandos para probar el asistente local UdeC."""

from __future__ import annotations

import argparse

from .asistente import AsistenteUdeC, ConfigAsistente


def _imprimir_resultado(res) -> None:
    print(f"\n[{res.modelo} | {res.segundos:.2f}s | {res.turnos_modelo} llamadas]")
    if res.pasos_herramientas:
        print("Herramientas ejecutadas:")
        for p in res.pasos_herramientas:
            resumen = str(p.resultado)
            if len(resumen) > 140:
                resumen = resumen[:140] + "..."
            print(f"  - {p.nombre}({p.argumentos}) -> {resumen}")
    print("\nRespuesta:\n" + res.respuesta)
    if res.fuentes:
        print("\nFuentes consultadas:", ", ".join(f["id"] for f in res.fuentes))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Asistente local de normativa UdeC")
    parser.add_argument("--modelo", default="qwen3:4b-instruct", help="Nombre del modelo en Ollama")
    parser.add_argument("--pregunta", default=None, help="Ejecuta una sola consulta y termina")
    parser.add_argument("--sin-prebusqueda", action="store_true", help="Obliga al modelo a buscar todo con tools")
    parser.add_argument("--solo-lexico", action="store_true", help="Desactiva embeddings E5 (modo ultra rápido)")
    args = parser.parse_args(argv)

    cfg = ConfigAsistente(modelo=args.modelo, usar_embeddings=not args.solo_lexico)
    asistente = AsistenteUdeC(config=cfg)

    if args.pregunta:
        res = asistente.responder(args.pregunta, prebuscar=not args.sin_prebusqueda)
        _imprimir_resultado(res)
        return 0

    print(f"Asistente local UdeC listo con `{args.modelo}`. Escribe 'salir' para terminar.")
    historial: list[dict[str, str]] = []
    while True:
        try:
            q = input("\nTú> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q or q.lower() in {"salir", "exit", "quit"}:
            break
        res = asistente.responder(q, historial=historial, prebuscar=not args.sin_prebusqueda)
        _imprimir_resultado(res)
        historial.append({"role": "user", "content": q})
        historial.append({"role": "assistant", "content": res.respuesta})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
