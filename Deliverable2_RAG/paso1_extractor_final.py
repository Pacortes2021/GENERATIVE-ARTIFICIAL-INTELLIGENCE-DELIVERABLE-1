import fitz
import os
import json
import re

print("Iniciando ETL Híbrido (Semántica + Recursive Splitter + Retención de Artículos)...")

ruta_pdfs = '../Corpus/'
archivos = [
    'Calendario-Academico-Pregrado-2026.pdf',
    'Reglamento_General_de_Docencia_de_Pregrado.pdf',
    'Reglamento_de_Docencia_de_Pregrado-FI.pdf'
]

def procesar_calendario(texto):
    chunks = []
    lineas = texto.split('\n')
    keywords = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre", "feriado", "vacaciones", "inicio", "término", "suspensión"]
    for linea in lineas:
        linea = linea.strip()
        # Filtro de ruido: Solo guardar líneas con meses o eventos clave, ignorando direcciones
        if len(linea) > 10 and any(k in linea.lower() for k in keywords) and "fono" not in linea.lower() and "calle" not in linea.lower():
            chunks.append(f"[Calendario Académico]: {linea}")
    return chunks

def procesar_reglamento(texto, archivo):
    texto = texto.replace("-\n", "")
    texto_limpio = re.sub(r'(?<![.:;])\n', ' ', texto)
    parrafos = texto_limpio.split('\n')
    
    chunks = []
    articulo_actual = "Sin Artículo"
    abrev = "RG" if "General" in archivo else "RI-FI"
    
    for p in parrafos:
        p = p.strip()
        
        # Atrapar el número de artículo para adjuntarlo como metadato a todos los chunks siguientes
        match_art = re.search(r'(?i)(art[íi]culo\s+\d+°?|art\.\s*\d+°?)', p)
        if match_art:
            # Normalizar a "Art. X"
            num_match = re.search(r'\d+°?', match_art.group(0))
            if num_match:
                articulo_actual = f"Art. {num_match.group(0)}"
                
        if len(p) > 40:
            prefijo = f"[{articulo_actual}, {abrev}]: "
            if len(p) > 1000:
                # BISTURÍ SEMÁNTICO
                oraciones = p.split('. ')
                chunk_actual = ""
                
                for oracion in oraciones:
                    oracion_con_punto = oracion.strip() + ". "
                    
                    if len(chunk_actual) + len(oracion_con_punto) > 800:
                        if chunk_actual:
                            chunks.append(f"{prefijo}{chunk_actual.strip()}")
                        chunk_actual = oracion_con_punto
                    else:
                        chunk_actual += oracion_con_punto
                        
                if chunk_actual:
                    chunks.append(f"{prefijo}{chunk_actual.strip()}")
            else:
                chunks.append(f"{prefijo}{p}")
            
    return chunks

chunks_totales = []
for archivo in archivos:
    ruta_completa = os.path.join(ruta_pdfs, archivo)
    if not os.path.exists(ruta_completa):
        print(f"ADVERTENCIA: No se encontró {ruta_completa}")
        continue
        
    doc = fitz.open(ruta_completa)
    texto_bruto = ""
    for pagina in doc:
        texto_bruto += pagina.get_text() + "\n"
        
    if "Calendario" in archivo:
        chunks_archivo = procesar_calendario(texto_bruto)
    else:
        chunks_archivo = procesar_reglamento(texto_bruto, archivo)
        
    for c in chunks_archivo:
        chunks_totales.append({"fuente": archivo, "texto": c})
            
print(f"-> Base de datos Híbrida creada con {len(chunks_totales)} chunks. (Con retención de contexto)")

with open('base_conocimiento_udec.json', 'w', encoding='utf-8') as f:
    json.dump(chunks_totales, f, ensure_ascii=False, indent=4)
