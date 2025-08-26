# backend/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import faiss

MODEL_NAME = os.getenv("SSO_EMBED_MODEL", "all-MiniLM-L6-v2")
_model = None
_index = None
_index_path = os.getenv("SSO_INDEX_PATH", "embeddings.index")
_embeddings_dim = None

def load_model():
    global _model, _embeddings_dim
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
        _embeddings_dim = _model.get_sentence_embedding_dimension()
    return _model

def build_or_load_index():
    global _index
    load_model()
    if os.path.exists(_index_path):
        _index = faiss.read_index(_index_path)
    else:
        _index = faiss.IndexFlatL2(_embeddings_dim)
    return _index

def save_index():
    global _index
    if _index is not None:
        faiss.write_index(_index, _index_path)

def embed_texts(texts):
    m = load_model()
    return m.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

def add_embeddings(embeddings):
    global _index
    if _index is None:
        build_or_load_index()
    _index.add(np.array(embeddings).astype("float32"))
    save_index()

def search(query_embedding, top_k=5):
    global _index
    if _index is None:
        build_or_load_index()
    D, I = _index.search(np.array([query_embedding]).astype("float32"), top_k)
    return D[0], I[0]
