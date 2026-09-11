import fitz  # PyMuPDF
import os
import json
import re

print("Iniciando Extractor de PDFs Inteligente (Chunking con Traslape)...")

ruta_pdfs = '../Deliverables/Reglamento/'
archivos = [
    'Calendario-Academico-Pregrado-2026.pdf',
    'Reglamento_General_de_Docencia_de_Pregrado.pdf',
    'Reglamento_de_Docencia_de_Pregrado-FI.pdf'
]

# Función Inteligente de Chunking
def chunking_inteligente(texto, max_palabras=80, traslape=15):
    """
    Corta el texto en fragmentos de 80 palabras, pero retrocede 15 palabras 
    antes de hacer el siguiente corte. Así nunca cortamos una idea por la mitad.
    """
    # 1. Limpiar la basura del PDF:
    # Unir palabras cortadas por guion a final de línea
    texto = texto.replace("-\n", "")
    # Reemplazar todos los saltos de línea múltiples por un solo espacio (crea un texto continuo)
    texto = re.sub(r'\s+', ' ', texto)
    
    # 2. Cortar por palabras
    palabras = texto.split()
    chunks = []
    
    # 3. Ventana Deslizante (Sliding Window)
    i = 0
    while i < len(palabras):
        fragmento = " ".join(palabras[i:i + max_palabras])
        if len(fragmento) > 50: # Filtro de seguridad
            chunks.append(fragmento)
        i += (max_palabras - traslape) # Avanzamos, pero repetimos las últimas 15 palabras
        
    return chunks

chunks_totales = []

for archivo in archivos:
    ruta_completa = os.path.join(ruta_pdfs, archivo)
    if not os.path.exists(ruta_completa):
        print(f"Error: No se encontró {archivo}")
        continue
        
    print(f"Procesando inteligentemente: {archivo}...")
    doc = fitz.open(ruta_completa)
    texto_documento = ""
    
    # Extraer texto de todo el PDF
    for pagina in doc:
        texto_documento += pagina.get_text() + "\n"
        
    # Aplicar nuestro método avanzado
    chunks_archivo = chunking_inteligente(texto_documento)
    
    for c in chunks_archivo:
        chunks_totales.append({
            "fuente": archivo,
            "texto": c
        })
            
    print(f" -> {len(chunks_archivo)} fragmentos semánticos extraídos.")

# Exportar a JSON
output_file = 'base_conocimiento_udec.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(chunks_totales, f, ensure_ascii=False, indent=4)

print(f"\n¡Proceso finalizado! Se guardaron {len(chunks_totales)} chunks ultra-limpios en total.")
