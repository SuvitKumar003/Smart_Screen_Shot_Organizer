# SSO_Project/backend/db.py
"""
JSON-backed storage for the prototype.
- File: SSO_Project/backend/storage.json
- One entry per image with optional OCR text, tags, and metadata.

Schema:
{
  "id": int,
  "file_path": "SSO_Project/uploads/xxx.png",
  "file_name": "xxx.png",
  "text": "optional OCR text",
  "tags": ["linkedin"],
  "metadata": {
      "assigned_keyword": "linkedin",
      "score": 0.73,
      "bucket_path": "SSO_Project/results/linkedin/xxx.png",
      "uploaded_at": "..."
  },
  "created_at": "...",
  "updated_at": "..."
}
"""

import os
import json
from threading import Lock
from datetime import datetime

STORAGE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../SSO_Project/backend
STORAGE_FILE = os.path.join(STORAGE_DIR, "storage.json")
UPLOADS_DIR = os.path.join(os.path.dirname(STORAGE_DIR), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

_lock = Lock()

def _read_all():
    with _lock:
        if not os.path.exists(STORAGE_FILE):
            return []
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

def _write_all(data):
    with _lock:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def add_or_update_screenshot(file_path: str, file_name: str, text: str, tags: list, metadata: dict):
    data = _read_all()
    tags = [t.strip().lower() for t in (tags or []) if (t and str(t).strip())]

    # update if exists
    for entry in data:
        if entry.get("file_path") == file_path:
            entry["text"] = text or entry.get("text", "")
            entry["tags"] = tags
            entry["metadata"] = metadata or entry.get("metadata", {})
            entry["updated_at"] = datetime.utcnow().isoformat()
            _write_all(data)
            return entry

    # new entry
    new_id = max([e.get("id", 0) for e in data], default=0) + 1
    entry = {
        "id": new_id,
        "file_path": file_path,
        "file_name": file_name,
        "text": text or "",
        "tags": tags,
        "metadata": metadata or {},
        "created_at": datetime.utcnow().isoformat()
    }
    data.append(entry)
    _write_all(data)
    return entry

def get_all_screenshots():
    return _read_all()

def find_by_tag(tag: str):
    tag = tag.strip().lower()
    return [e for e in _read_all() if tag in e.get("tags", [])]

def find_by_text_search(q: str):
    q = q.strip().lower()
    if not q:
        return []
    res = []
    for e in _read_all():
        text = (e.get("text") or "").lower()
        tags = " ".join(e.get("tags", [])).lower()
        if q in text or q in tags or q in (e.get("file_name","").lower()):
            res.append(e)
    return res
