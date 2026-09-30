"""Primera prueba de E5: solo corpus y preguntas, sin respuestas de referencia."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Deliverable2/corpus"))
from preparar_corpus import MODEL, REVISION, TOKENIZER_SHA256, expand_hits


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_inputs(corpus_dir, questions_path):
    report = read(corpus_dir / "validacion.json")
    for name, expected in report["artefactos_sha256"].items():
        require(sha(corpus_dir / name) == expected, f"Artefacto modificado: {name}; regenerar el corpus")
    corpus = read(corpus_dir / "corpus.json")
    fragments = read(corpus_dir / "fragmentos_busqueda.json")
    for source in corpus["fuentes"].values():
        require(sha(ROOT / "Corpus" / source["archivo"]) == source["sha256"], "PDF modificado: regenerar el corpus")
    # El CSV de E1 también contiene respuestas. Solo estos campos salen del lector.
    with questions_path.open(encoding="utf-8-sig", newline="") as stream:
        questions = [{"id": i, "pregunta": row["pregunta"], "categoria": row["categoria"]}
                     for i, row in enumerate(csv.DictReader(stream), 1)]
    require(len(questions) == 50 and len({q['pregunta'] for q in questions}) == 50, "Se esperaban las 50 preguntas originales")
    return corpus, fragments, questions


def rank_vectors(document_vectors, query_vectors):
    require(document_vectors.ndim == query_vectors.ndim == 2, "Vectores deben ser matrices")
    require(document_vectors.shape[1] == query_vectors.shape[1], "Dimensiones incompatibles")
    for vectors in (document_vectors, query_vectors):
        require(bool(np.isfinite(vectors).all()), "Vectores no finitos")
        require(bool(np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5)), "Se requieren vectores normalizados")
    # Para este índice pequeño basta la contracción directa; evita avisos numéricos
    # espurios observados con BLAS/Accelerate en el equipo de reproducción.
    scores = np.einsum("ij,kj->ik", query_vectors, document_vectors, optimize=False)
    require(bool(np.isfinite(scores).all()), "Similitudes no finitas")
    require(bool((np.abs(scores) <= 1.00001).all()), "Similitudes fuera del rango del coseno")
    return scores, np.argsort(-scores, axis=1, kind="stable")


def retrieve(corpus, fragments, questions, document_vectors, query_vectors, k):
    require(len(document_vectors) == len(fragments), "Índice incompatible con el corpus")
    require(len(query_vectors) == len(questions), "Faltan vectores de consulta")
    require(1 <= k <= len(fragments), "k fuera de rango")
    scores, orders = rank_vectors(document_vectors, query_vectors)
    cases = []
    for qi, question in enumerate(questions):
        ranking = [{"posicion": ri, "fragmento_id": fragments[int(fi)]["id"],
                    "unidad_id": fragments[int(fi)]["unidad_id"], "similitud_coseno": float(scores[qi, fi])}
                   for ri, fi in enumerate(orders[qi], 1)]
        contexts = expand_hits([r["fragmento_id"] for r in ranking[:k]], corpus, fragments)
        cases.append({**question, "ranking": ranking, "contextos": contexts,
                      "caracteres_contexto": sum(len(c["texto"]) for c in contexts)})
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo-local", type=Path, default=Path.home() / ".cache/huggingface/hub/models--intfloat--multilingual-e5-small/snapshots" / REVISION)
    parser.add_argument("--salida", type=Path, default=Path(__file__).parent / "resultados/e5_top5_v1")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    require(not args.salida.exists(), "La salida ya existe; usar un nombre nuevo para conservar la corrida anterior")
    corpus_dir = ROOT / "Deliverable2/corpus/generado"
    questions_path = ROOT / "Deliverable1/datos/test_set_50.csv"
    corpus, fragments, questions = load_inputs(corpus_dir, questions_path)
    require(sha(args.modelo_local / "tokenizer.json") == TOKENIZER_SHA256, "Tokenizador distinto al usado para fragmentar")
    from sentence_transformers import SentenceTransformer
    import torch
    torch.set_num_threads(4)
    torch.manual_seed(0)
    model = SentenceTransformer(str(args.modelo_local), device="cpu", local_files_only=True)
    require(model.max_seq_length == 512, "Configuración inesperada de longitud E5")
    passages = [f["texto_embedding"] for f in fragments]
    queries = ["query: " + q["pregunta"] for q in questions]
    for kind, texts in (("fragmento", passages), ("consulta", queries)):
        lengths = [len(model.tokenizer(text, truncation=False, padding=False)["input_ids"]) for text in texts]
        require(max(lengths) <= 512, f"Hay un {kind} que E5 truncaría")
        if kind == "fragmento":
            require(lengths == [f["tokens_e5"] for f in fragments], "El conteo real difiere del usado para fragmentar")
    print("Codificando 201 fragmentos y 50 preguntas en CPU...", flush=True)
    documents = model.encode(passages, normalize_embeddings=True, batch_size=16, show_progress_bar=False)
    queries = model.encode(queries, normalize_embeddings=True, batch_size=16, show_progress_bar=False)
    cases = retrieve(corpus, fragments, questions, documents, queries, args.k)
    args.salida.mkdir(parents=True)
    np.save(args.salida / "vectores_documentos.npy", documents, allow_pickle=False)
    np.save(args.salida / "vectores_consultas.npy", queries, allow_pickle=False)
    payload = {"version": 1, "configuracion": {"modelo": MODEL, "revision": REVISION, "k_fragmentos": args.k,
               "busqueda": "similitud coseno exacta", "expansion": "unidad completa; sin seguir remisiones", "dispositivo": "cpu",
               "prefijo_documentos": "passage: ", "prefijo_consultas": "query: ", "normalizacion_l2": True,
               "desempate": "orden estable del corpus", "sin_reescritura_consultas": True},
               "fragmentos_orden_indice": [f["id"] for f in fragments],
               "fuentes_sha256": {"corpus": sha(corpus_dir / "corpus.json"), "fragmentos": sha(corpus_dir / "fragmentos_busqueda.json"), "preguntas_e1": sha(questions_path)},
               "casos": cases}
    write(args.salida / "recuperacion.json", payload)
    manifest = {"script_sha256": sha(__file__), "versiones": {n: importlib.metadata.version(n) for n in ("sentence-transformers", "transformers", "torch", "numpy")},
                "archivos_modelo_sha256": {str(p.relative_to(args.modelo_local)): sha(p) for p in sorted(args.modelo_local.rglob("*")) if p.is_file()},
                "artefactos_sha256": {name: sha(args.salida / name) for name in ("recuperacion.json", "vectores_documentos.npy", "vectores_consultas.npy")}}
    write(args.salida / "manifiesto.json", manifest)
    print(f"Recuperación guardada: {args.salida}", flush=True)


if __name__ == "__main__":
    main()
