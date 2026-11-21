"""Exportador de modelo HF fusionado a GGUF Q4_K_M + Modelfile exacto para Ollama local."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Plantilla exacta extraída de `ollama show qwen3:4b-instruct --modelfile` para preservar tool-calling
TEMPLATE_OLLAMA_QWEN3_INSTRUCT = """{{- $lastUserIdx := -1 -}}
{{- range $idx, $msg := .Messages -}}
{{- if eq $msg.Role "user" }}{{ $lastUserIdx = $idx }}{{ end -}}
{{- end }}
{{- if or .System .Tools }}<|im_start|>system
{{ if .System }}{{ .System }}

{{ end }}
{{- if .Tools }}# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{{- range .Tools }}
{"type": "function", "function": {{ .Function }}}
{{- end }}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>
{{- end -}}
<|im_end|>
{{ end }}
{{- range $i, $_ := .Messages }}
{{- $last := eq (len (slice $.Messages $i)) 1 -}}
{{- if eq .Role "user" }}<|im_start|>user
{{ .Content }}<|im_end|>
{{ else if eq .Role "assistant" }}<|im_start|>assistant
{{ if .Content }}{{ .Content }}{{ end }}
{{- if .ToolCalls }}
{{- range .ToolCalls }}
<tool_call>
{"name": "{{ .Function.Name }}", "arguments": {{ .Function.Arguments }}}
</tool_call>
{{- end }}
{{- end }}{{ if not $last }}<|im_end|>
{{ end }}
{{- else if eq .Role "tool" }}<|im_start|>user
<tool_response>
{{ .Content }}
</tool_response><|im_end|>
{{ end }}
{{- if and (ne .Role "assistant") $last }}<|im_start|>assistant
{{ end }}
{{- end }}"""


def generar_modelfile(
    ruta_gguf: str | Path,
    temperature: float = 0.0,
    num_ctx: int = 4096,
    repeat_penalty: float = 1.05,
) -> str:
    """Construye un Modelfile compatible con Ollama `/api/chat` + tool-calling para 8 GB RAM."""
    return (
        f"FROM {ruta_gguf}\n"
        f'TEMPLATE """{TEMPLATE_OLLAMA_QWEN3_INSTRUCT}"""\n'
        f"PARAMETER temperature {temperature}\n"
        f"PARAMETER num_ctx {num_ctx}\n"
        f"PARAMETER repeat_penalty {repeat_penalty}\n"
        "PARAMETER top_k 20\n"
        "PARAMETER top_p 0.8\n"
        'PARAMETER stop "<|im_start|>"\n'
        'PARAMETER stop "<|im_end|>"\n'
    )


def convertir_merged_a_gguf(
    merged_dir: Path,
    salida_dir: Path,
    llama_cpp_dir: Path,
    nombre_base: str = "udec-agente-qwen3-4b-ft",
    cuantizacion: str = "Q4_K_M",
    conservar_f16: bool = False,
) -> dict[str, Path]:
    """Convierte un directorio HF fusionado a GGUF cuantizado y genera el `Modelfile`."""
    merged_dir = Path(merged_dir).resolve()
    salida_dir = Path(salida_dir).resolve()
    llama_cpp_dir = Path(llama_cpp_dir).resolve()
    salida_dir.mkdir(parents=True, exist_ok=True)

    convert_py = llama_cpp_dir / "convert_hf_to_gguf.py"
    if not convert_py.is_file():
        raise FileNotFoundError(f"No se encontró {convert_py}")

    quant_bin = llama_cpp_dir / "build" / "bin" / "llama-quantize"
    if not quant_bin.is_file():
        which_q = shutil.which("llama-quantize")
        if which_q:
            quant_bin = Path(which_q)
        else:
            raise FileNotFoundError("No se encontró `llama-quantize`; compila llama.cpp con CMake primero.")

    gguf_f16 = salida_dir / f"{nombre_base}-f16.gguf"
    gguf_quant = salida_dir / f"{nombre_base}-{cuantizacion}.gguf"

    subprocess.run(
        [sys.executable, str(convert_py), str(merged_dir), "--outfile", str(gguf_f16), "--outtype", "f16"],
        check=True,
    )
    subprocess.run(
        [str(quant_bin), str(gguf_f16), str(gguf_quant), cuantizacion],
        check=True,
    )
    if not conservar_f16 and gguf_f16.exists():
        gguf_f16.unlink()

    modelfile_path = salida_dir / "Modelfile"
    modelfile_path.write_text(generar_modelfile(f"./{gguf_quant.name}"), encoding="utf-8")
    return {"gguf": gguf_quant, "modelfile": modelfile_path}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Genera Modelfile y opcionalmente convierte HF -> GGUF Q4_K_M")
    parser.add_argument("--merged-dir", type=Path, default=None)
    parser.add_argument("--salida-dir", type=Path, required=True)
    parser.add_argument("--llama-cpp-dir", type=Path, default=None)
    parser.add_argument("--nombre-base", default="udec-agente-qwen3-4b-ft")
    parser.add_argument("--cuantizacion", default="Q4_K_M")
    parser.add_argument("--solo-modelfile", action="store_true")
    args = parser.parse_args(argv)

    args.salida_dir.mkdir(parents=True, exist_ok=True)
    if args.solo_modelfile:
        gguf_name = f"./{args.nombre_base}-{args.cuantizacion}.gguf"
        mf = args.salida_dir / "Modelfile"
        mf.write_text(generar_modelfile(gguf_name), encoding="utf-8")
        print(f"Modelfile generado: {mf}")
        return 0

    if not args.merged_dir or not args.llama_cpp_dir:
        raise SystemExit("Debes especificar --merged-dir y --llama-cpp-dir (o usar --solo-modelfile).")

    res = convertir_merged_a_gguf(
        merged_dir=args.merged_dir,
        salida_dir=args.salida_dir,
        llama_cpp_dir=args.llama_cpp_dir,
        nombre_base=args.nombre_base,
        cuantizacion=args.cuantizacion,
    )
    print(f"GGUF listo: {res['gguf']}\nModelfile listo: {res['modelfile']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
