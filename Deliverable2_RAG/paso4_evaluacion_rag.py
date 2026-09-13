import csv
import json
import numpy as np
import requests
import time
import warnings
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Silenciar las advertencias matemáticas de Apple Silicon
warnings.filterwarnings("ignore", category=RuntimeWarning)

print("Iniciando Evaluación RAG Automatizada (Ollama local - qwen2.5:3b)...")

# Cargar base de conocimiento
with open('base_conocimiento_udec.json', 'r', encoding='utf-8') as f:
    textos_udec = json.load(f)
vectores_udec = np.load('vectores_udec.npy')
embedder = SentenceTransformer("intfloat/multilingual-e5-small", device="cpu")

def buscar_mejores_parrafos(pregunta, top_k=5):
    pregunta_formateada = "query: " + pregunta
    vector_pregunta = embedder.encode([pregunta_formateada], normalize_embeddings=True)
    similitudes = cosine_similarity(vector_pregunta, vectores_udec)[0]
    indices_ganadores = similitudes.argsort()[-top_k:][::-1]
    
    textos_combinados = ""
    for idx in indices_ganadores:
        textos_combinados += f"\n- {textos_udec[idx]['texto']}"
    return textos_combinados

def preguntar_a_ollama_rag(pregunta, contexto):
    system_prompt = (
        "Eres un asistente experto en la normativa de pregrado de la Facultad de "
        "Ingeniería de la Universidad de Concepción. Responde de forma breve, con el "
        "dato exacto y citando el artículo correspondiente (por ejemplo: 'Art. 8') "
        "basándote ÚNICAMENTE en el contexto provisto. Si no tienes la información "
        "en el contexto, di explícitamente que no está en la normativa."
        f"\n\nContexto normativo:\n{contexto}"
    )
    
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "qwen2.5:3b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": pregunta}
        ],
        "stream": False,
        "options": {"temperature": 0.0}
    }
    
    try:
        respuesta = requests.post(url, json=payload)
        return respuesta.json()['message']['content'].strip()
    except Exception as e:
        return f"ERROR_OLLAMA: {str(e)}"

# Cargar dataset original
input_file = '../test_set_50.csv'
output_file = 'resultados_rag_qwen2.5.csv'

resultados = []
with open(input_file, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    filas = list(reader)
    total = len(filas)
    
    print(f"Evaluando {total} preguntas con sistema RAG...")
    for i, fila in enumerate(filas):
        print(f"[{i+1}/{total}] Pregunta: {fila['pregunta']}")
        contexto = buscar_mejores_parrafos(fila['pregunta'], top_k=5)
        respuesta = preguntar_a_ollama_rag(fila['pregunta'], contexto)
        
        fila_resultado = fila.copy()
        fila_resultado['prediccion_rag'] = respuesta
        resultados.append(fila_resultado)
        
        time.sleep(0.1)

# Guardar resultados
if resultados:
    fieldnames = list(resultados[0].keys())
    with open(output_file, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados)
        
print(f"✅ Evaluación RAG completada. Guardado en {output_file}")
