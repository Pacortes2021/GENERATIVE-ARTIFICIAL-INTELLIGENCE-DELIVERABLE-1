import fitz
import os
import json
import re

print("Iniciando ETL Híbrido (Semántica + Recursive Splitter)...")

ruta_pdfs = '../Deliverables/Reglamento/'
archivos = [
    'Calendario-Academico-Pregrado-2026.pdf',
    'Reglamento_General_de_Docencia_de_Pregrado.pdf',
    'Reglamento_de_Docencia_de_Pregrado-FI.pdf'
]

def procesar_calendario(texto):
    chunks = []
    lineas = texto.split('\n')
    for linea in lineas:
        linea = linea.strip()
        if len(linea) > 10:
            chunks.append(f"[Calendario]: {linea}")
    return chunks

def procesar_reglamento(texto):
    texto = texto.replace("-\n", "")
    texto_limpio = re.sub(r'(?<![.:;])\n', ' ', texto)
    parrafos = texto_limpio.split('\n')
    
    chunks = []
    for p in parrafos:
        p = p.strip()
        if len(p) > 40:
            if len(p) > 1000:
                # EL BISTURÍ SEMÁNTICO: Cortamos por oraciones (punto seguido)
                oraciones = p.split('. ')
                chunk_actual = ""
                
                for oracion in oraciones:
                    oracion_con_punto = oracion.strip() + ". "
                    
                    # Si sumar esta oración excede el límite, guardamos el bloque actual y abrimos uno nuevo
                    if len(chunk_actual) + len(oracion_con_punto) > 800:
                        if chunk_actual:
                            chunks.append(f"[Regla UdeC]: {chunk_actual.strip()}")
                        chunk_actual = oracion_con_punto
                    else:
                        chunk_actual += oracion_con_punto
                        
                # Guardamos el último bloque que quedó en memoria
                if chunk_actual:
                    chunks.append(f"[Regla UdeC]: {chunk_actual.strip()}")
            else:
                chunks.append(f"[Regla UdeC]: {p}")
            
    return chunks

chunks_totales = []
for archivo in archivos:
    ruta_completa = os.path.join(ruta_pdfs, archivo)
    if not os.path.exists(ruta_completa):
        continue
        
    doc = fitz.open(ruta_completa)
    texto_bruto = ""
    for pagina in doc:
        texto_bruto += pagina.get_text() + "\n"
        
    if "Calendario" in archivo:
        chunks_archivo = procesar_calendario(texto_bruto)
    else:
        chunks_archivo = procesar_reglamento(texto_bruto)
        
    for c in chunks_archivo:
        chunks_totales.append({"fuente": archivo, "texto": c})
            
print(f"-> Base de datos Híbrida creada con {len(chunks_totales)} chunks perfectos.")

with open('base_conocimiento_udec.json', 'w', encoding='utf-8') as f:
    json.dump(chunks_totales, f, ensure_ascii=False, indent=4)
