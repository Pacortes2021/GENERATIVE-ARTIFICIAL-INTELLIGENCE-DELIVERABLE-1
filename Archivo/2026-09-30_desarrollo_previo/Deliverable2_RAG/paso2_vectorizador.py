import json
import time
import numpy as np
from sentence_transformers import SentenceTransformer

print("Iniciando Paso 2 (Optimizado para Mac sin PyTorch)...")

archivo_entrada = 'base_conocimiento_udec.json'
try:
    with open(archivo_entrada, 'r', encoding='utf-8') as f:
        chunks_totales = json.load(f)
    print(f"-> Base cargada: {len(chunks_totales)} fragmentos.")
except FileNotFoundError:
    print("Falta el json.")
    exit()

# El modelo E5 exige que le digamos explícitamente que estos textos son "documentos" (passage)
textos_para_vectorizar = ["passage: " + item["texto"] for item in chunks_totales]

print("\nCargando modelo...")
embedder = SentenceTransformer("intfloat/multilingual-e5-small", device="cpu")

print("\nVectorizando... (Esto puede tomar un minuto)")
start_time = time.time()

# Convertimos directo a un arreglo de NumPy (100% seguro en Mac)
vectores = embedder.encode(textos_para_vectorizar, normalize_embeddings=True)

end_time = time.time()
print(f"-> Vectorización en {end_time - start_time:.1f} segundos!")

archivo_salida = 'vectores_udec.npy'
np.save(archivo_salida, vectores)

print(f"\n¡Éxito! Base vectorial súper estable guardada en: {archivo_salida}")
