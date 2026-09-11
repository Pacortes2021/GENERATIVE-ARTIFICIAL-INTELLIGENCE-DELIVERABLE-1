import fitz
import os
import json
import re

print("Iniciando ETL Semántico (Data Engineering Avanzado)...")

ruta_pdfs = '../Deliverables/Reglamento/'
archivos = [
    'Calendario-Academico-Pregrado-2026.pdf',
    'Reglamento_General_de_Docencia_de_Pregrado.pdf',
    'Reglamento_de_Docencia_de_Pregrado-FI.pdf'
]

def procesar_calendario(texto):
    """El calendario es una lista/tabla. Cada salto de línea es un evento distinto."""
    chunks = []
    lineas = texto.split('\n')
    for linea in lineas:
        linea = linea.strip()
        if len(linea) > 10:
            # Agregamos contexto explícito para que el LLM no se confunda
            chunks.append(f"[Evento del Calendario UdeC]: {linea}")
    return chunks

def procesar_reglamento(texto):
    """Los reglamentos son prosa. Debemos unir los cortes de página y cortar por párrafos reales."""
    # 1. Unir guiones
    texto = texto.replace("-\n", "")
    
    # 2. MAGIA REGEX: Si un salto de línea NO tiene un punto (.) o dos puntos (:) antes, 
    # significa que es un corte físico de la página. Lo cambiamos por espacio.
    # Si sí tiene un punto, lo dejamos como \n porque es un verdadero cambio de párrafo.
    texto_limpio = re.sub(r'(?<![.:;])\n', ' ', texto)
    
    # 3. Cortamos por los verdaderos saltos de línea
    parrafos = texto_limpio.split('\n')
    
    chunks = []
    for p in parrafos:
        p = p.strip()
        if len(p) > 40:
            chunks.append(f"[Regla UdeC]: {p}")
            
    return chunks

chunks_totales = []

for archivo in archivos:
    ruta_completa = os.path.join(ruta_pdfs, archivo)
    if not os.path.exists(ruta_completa):
        continue
        
    print(f"Enrutando y limpiando: {archivo}...")
    doc = fitz.open(ruta_completa)
    texto_bruto = ""
    for pagina in doc:
        texto_bruto += pagina.get_text() + "\n"
        
    # Enrutador Semántico (ETL Routing)
    if "Calendario" in archivo:
        chunks_archivo = procesar_calendario(texto_bruto)
    else:
        chunks_archivo = procesar_reglamento(texto_bruto)
        
    for c in chunks_archivo:
        chunks_totales.append({
            "fuente": archivo,
            "texto": c
        })
            
    print(f" -> {len(chunks_archivo)} fragmentos perfectos generados.")

output_file = 'base_conocimiento_udec.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(chunks_totales, f, ensure_ascii=False, indent=4)

print(f"\n¡Éxito! Base de datos semántica creada con {len(chunks_totales)} chunks independientes.")
