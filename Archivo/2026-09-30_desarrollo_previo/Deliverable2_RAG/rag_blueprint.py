import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# 1. CARGA Y FRAGMENTACIÓN DE DOCUMENTOS (CHUNKING)
# ==========================================
# En la realidad, usarán librerías como PyPDF2 o pdfplumber para leer los reglamentos oficiales.
# Aquí simulamos que ya leyeron el PDF de la FI UdeC y lo cortaron en párrafos.

documentos_ude = [
    "Art. 8, RI-FI: El mínimo de créditos que debe inscribirse por período es igual o superior a 8 créditos.",
    "Art. 11, RI-FI: La nota mínima para aprobar una asignatura en la Facultad de Ingeniería es 4,0. Toda asignatura debe tener al menos 3 evaluaciones sumativas.",
    "Art. 14 a), RI-FI: Queda en causal de baja académica el estudiante que al término del segundo semestre apruebe menos de 15 créditos.",
    "Art. 34, RI-FI: En caso de discrepancia, prevalece el Reglamento General de Docencia sobre el Reglamento Interno."
]

# ==========================================
# 2. CREACIÓN DE EMBEDDINGS (VECTORES) - BLOQUE 3 DE LA CLASE
# ==========================================
print("Cargando modelo de Embeddings...")
# Usamos un modelo súper liviano y experto en español/multilingüe para crear los vectores
embedder = SentenceTransformer("intfloat/multilingual-e5-small")

print("Convirtiendo los artículos a vectores matemáticos...")
# Convertimos todos los párrafos a una matriz de vectores densos
vectores_documentos = embedder.encode(documentos_ude)

# ==========================================
# 3. EL BUSCADOR SEMÁNTICO (SIMILITUD COSENO)
# ==========================================
def buscar_contexto(pregunta, top_k=1):
    # 1. Convertimos la pregunta del usuario en un vector
    vector_pregunta = embedder.encode([pregunta])
    
    # 2. Calculamos el ángulo (coseno) entre la pregunta y todos los párrafos
    similitudes = cosine_similarity(vector_pregunta, vectores_documentos)[0]
    
    # 3. Buscamos el índice del párrafo con mayor puntaje (el más parecido)
    indice_ganador = np.argmax(similitudes)
    puntaje = similitudes[indice_ganador]
    
    return documentos_ude[indice_ganador], puntaje

# ==========================================
# 4. PREPARACIÓN DEL LLM (QWEN3-4B) - BLOQUE 6 DE LA CLASE
# ==========================================
print("Cargando Qwen3-4B...")
MODEL_NAME = "Qwen/Qwen3-4B"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype="auto", device_map="auto")

def preguntar_con_rag(pregunta_usuario):
    # Paso A: Búsqueda de información (Retrieval)
    contexto_recuperado, confianza = buscar_contexto(pregunta_usuario)
    print(f"\n[Buscador] Encontré este párrafo con {confianza:.2f} de similitud coseno:\n>> {contexto_recuperado}")
    
    # Paso B: Ingeniería de Prompt (Context Engineering)
    # Aquí está la magia: le inyectamos la verdad absoluta al modelo ANTES de que responda
    prompt_rag = f"""Eres un asistente experto en la normativa de la Facultad de Ingeniería de la UdeC.
REGLA: Responde la pregunta basándote ÚNICAMENTE en el contexto oficial proporcionado. Cita el artículo exacto.
Si el contexto no responde la pregunta, debes decir estrictamente 'No está en la normativa'. No inventes información.

CONTEXTO OFICIAL:
{contexto_recuperado}

PREGUNTA DEL ALUMNO: {pregunta_usuario}
"""
    
    # Paso C: Generación (Generation)
    messages = [{"role": "user", "content": prompt_rag}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=100, do_sample=False)
    
    respuesta_final = tokenizer.decode(out[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True)
    return respuesta_final.strip()

# ==========================================
# 5. PRUEBA DEL SISTEMA RAG
# ==========================================
if __name__ == "__main__":
    pregunta = "¿Cuál es el mínimo de créditos que debo inscribir por período en Ingeniería?"
    print(f"\nPregunta del usuario: {pregunta}")
    
    respuesta_ia = preguntar_con_rag(pregunta)
    print(f"\n[IA Responde] -> {respuesta_ia}")
