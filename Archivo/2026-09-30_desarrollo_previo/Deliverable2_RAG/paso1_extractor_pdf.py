import fitz  # PyMuPDF
import os
import json
import re

print("Iniciando extractor de PDFs para RAG...")

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
        print(f"Error: No se encontró el archivo {archivo}")
        continue
        
    print(f"Procesando: {archivo}...")
    doc = fitz.open(ruta_completa)
    texto_documento = ""
    
    # Extraer texto de todas las páginas
    for pagina in doc:
        texto_documento += pagina.get_text() + "\n"
        
    # Limpieza básica de saltos de línea inútiles
    texto_limpio = re.sub(r'\n+', '\n', texto_documento)
    
    # Chunking: Separar por párrafos
    parrafos = texto_limpio.split('\n')
    
    # Filtrar párrafos útiles (> 40 caracteres)
    chunks_archivo = 0
    for p in parrafos:
        p = p.strip()
        if len(p) > 40:
            chunks_totales.append({
                "fuente": archivo,
                "texto": p
            })
            chunks_archivo += 1
            
    print(f" -> {chunks_archivo} fragmentos útiles extraídos.")

# Exportar a JSON
output_file = 'base_conocimiento_udec.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(chunks_totales, f, ensure_ascii=False, indent=4)

print(f"\n¡Proceso finalizado! Se guardaron {len(chunks_totales)} chunks en total.")
print(f"Archivo generado: {output_file}")
