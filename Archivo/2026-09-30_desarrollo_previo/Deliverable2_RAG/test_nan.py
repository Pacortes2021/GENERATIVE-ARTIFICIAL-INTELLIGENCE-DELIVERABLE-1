import torch
import numpy as np
import json
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("intfloat/multilingual-e5-small", device="cpu")
q = embedder.encode(["prueba"])
print("Pregunta norm:", np.linalg.norm(q))
print("Pregunta nan:", np.isnan(q).any())

v = torch.load('vectores_udec.pt', weights_only=False).cpu().numpy()
print("Vectores nan sum:", np.isnan(v).sum())
print("Vectores norm zero:", (np.linalg.norm(v, axis=1) == 0).sum())
