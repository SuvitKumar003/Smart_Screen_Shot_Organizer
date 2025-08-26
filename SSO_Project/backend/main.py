# SSO_Project/backend/main.py
"""
Keyword-based image clustering API using CLIP (Sentence-Transformers).
Looks "deployed" for demos:
- GET  /                      : health message
- POST /cluster/by_keywords/  : keywords + multiple images -> assign each image to closest keyword
- GET  /list/                 : list stored assignments
- GET  /search/?q=...         : simple search over filename/tags/text

Uploads are saved to:     SSO_Project/uploads/
Clustered copies go to:   SSO_Project/results/<keyword>/
Assignments persisted in: SSO_Project/backend/storage.json
"""

import os
from typing import List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from io import BytesIO
import numpy as np

from sentence_transformers import SentenceTransformer

from SSO_Project.backend import db as storage  # <- package-absolute import

# ---------- Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))                # .../SSO_Project/backend
PROJECT_ROOT = os.path.dirname(BASE_DIR)                              # .../SSO_Project
UPLOADS_DIR = os.path.join(PROJECT_ROOT, "uploads")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------- App
app = FastAPI(title="SSO Keyword Clustering API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow Streamlit/local demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve clustered results as static files (so links/images work)
app.mount("/results", StaticFiles(directory=RESULTS_DIR), name="results")

# ---------- Model (lazy-load)
_model: SentenceTransformer | None = None
def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("clip-ViT-B-32")  # CPU ok; later: _model.to("cuda")
    return _model

# ---------- Utils
def _normalize_keywords(raw: str) -> list[str]:
    return [k.strip().lower() for k in raw.split(",") if k.strip()]

def _save_upload(file: UploadFile) -> str:
    save_path = os.path.join(UPLOADS_DIR, file.filename)
    if os.path.exists(save_path):
        name, ext = os.path.splitext(file.filename)
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        save_path = os.path.join(UPLOADS_DIR, f"{name}_{ts}{ext}")
    with open(save_path, "wb") as f:
        f.write(file.file.read())
    return save_path

def _open_pil(path: str) -> Image.Image:
    with open(path, "rb") as f:
        return Image.open(BytesIO(f.read())).convert("RGB")

def _assign_to_best_keyword(
    img_emb: np.ndarray, kw_embs: np.ndarray, keywords: list[str]
) -> tuple[str, float, int]:
    # cosine sims since vectors are normalized -> dot product
    sims = kw_embs @ img_emb  # (K,)
    best_idx = int(np.argmax(sims))
    return keywords[best_idx], float(sims[best_idx]), best_idx

def _ensure_bucket_dir(keyword: str) -> str:
    bucket_dir = os.path.join(RESULTS_DIR, keyword)
    os.makedirs(bucket_dir, exist_ok=True)
    return bucket_dir

# ---------- Routes
@app.get("/")
def root():
    return {"message": "SSO (SSO_Project) Keyword Clustering backend is running 🚀"}

@app.post("/cluster/by_keywords/")
async def cluster_by_keywords(
    keywords: str = Form(..., description="Comma-separated keywords, e.g. 'linkedin, recruiter, receipt'"),
    files: List[UploadFile] = File(..., description="One or more images"),
):
    """
    - Parse keywords
    - Save uploaded files
    - Encode keywords (text) and images with CLIP
    - Assign each image to the closest keyword by cosine similarity
    - Save a copy under results/<keyword>/, persist assignment in storage.json
    - Return grouped mapping + scores
    """
    try:
        kw_list = _normalize_keywords(keywords)
        if not kw_list:
            return JSONResponse({"status": "error", "detail": "No valid keywords provided"}, status_code=400)

        saved_paths: list[str] = []
        original_names: list[str] = []
        for uf in files:
            saved = _save_upload(uf)
            saved_paths.append(saved)
            original_names.append(os.path.basename(saved))

        model = get_model()
        kw_embs = model.encode(kw_list, convert_to_numpy=True, normalize_embeddings=True)
        pil_images = [_open_pil(p) for p in saved_paths]
        img_embs = model.encode(pil_images, convert_to_numpy=True, normalize_embeddings=True)

        grouped: Dict[str, list[Dict[str, Any]]] = {k: [] for k in kw_list}
        assignments: list[Dict[str, Any]] = []

        for path, fname, emb in zip(saved_paths, original_names, img_embs):
            best_kw, score, _ = _assign_to_best_keyword(emb, kw_embs, kw_list)

            bucket_dir = _ensure_bucket_dir(best_kw)
            bucket_path = os.path.join(bucket_dir, fname)
            if not os.path.exists(bucket_path):
                _open_pil(path).save(bucket_path)

            entry = storage.add_or_update_screenshot(
                file_path=path,
                file_name=fname,
                text="",                          # OCR integration later
                tags=[best_kw],                   # auto tag
                metadata={
                    "assigned_keyword": best_kw,
                    "score": score,
                    "bucket_path": bucket_path,
                    "uploaded_at": datetime.utcnow().isoformat(),
                },
            )
            assignments.append(entry)
            grouped[best_kw].append({
                "file_name": fname,
                "file_path": path,
                "bucket_path": bucket_path,
                "keyword": best_kw,
                "score": score,
            })

        return {
            "status": "ok",
            "keywords": kw_list,
            "grouped": grouped,
            "assignments_count": len(assignments),
        }

    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)

@app.get("/list/")
def list_all():
    items = storage.get_all_screenshots()
    return {"count": len(items), "items": items}

@app.get("/search/")
def search(q: str):
    items = storage.find_by_text_search(q) if q and q.strip() else []
    return {"count": len(items), "items": items}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("SSO_Project.backend.main:app", host="127.0.0.1", port=8000, reload=True)
