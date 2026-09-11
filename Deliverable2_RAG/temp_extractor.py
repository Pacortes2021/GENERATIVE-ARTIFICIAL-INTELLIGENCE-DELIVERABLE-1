import fitz
import os
import json
import re

ruta_pdfs = '../Deliverables/Reglamento/'
archivos = [
    'Calendario-Academico-Pregrado-2026.pdf',
    'Reglamento_General_de_Docencia_de_Pregrado.pdf',
    'Reglamento_de_Docencia_de_Pregrado-FI.pdf'
]
chunks_totales = []
for archivo in archivos:
    ruta_completa = os.path.join(ruta_pdfs, archivo)
    if not os.path.exists(ruta_completa):
        print(f"Falta {archivo}")
        continue
    doc = fitz.open(ruta_completa)
    texto = ""
    for pag in doc:
        texto += pag.get_text() + "\n"
    texto = re.sub(r'\n+', '\n', texto)
    parrafos = texto.split('\n')
    for p in parrafos:
        p = p.strip()
        if len(p) > 40:
            chunks_totales.append({"fuente": archivo, "texto": p})

with open('base_conocimiento_udec.json', 'w', encoding='utf-8') as f:
    json.dump(chunks_totales, f, ensure_ascii=False, indent=4)
print(f"¡Éxito! Generados {len(chunks_totales)} chunks de texto limpio.")
for i in range(3):
    print(chunks_totales[i])
