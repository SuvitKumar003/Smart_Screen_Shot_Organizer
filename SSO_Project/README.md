# Smart Screenshot Organizer (SSO) - Quick Start

1. Install system dependencies:
   - Tesseract OCR (Ubuntu): sudo apt install tesseract-ocr
   - (Optional) ffmpeg for Whisper transcription

2. Create and activate a virtual env, then:
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm

3. Start backend API:
   uvicorn backend.main:app --reload --port 8000

4. Start Streamlit dashboard:
   streamlit run dashboard/streamlit_app.py

5. Upload screenshots via the Streamlit UI or call the /ingest/upload/ API.

6. For Google Drive ingestion:
   - Put `credentials.json` (OAuth client) in project root.
   - Use backend.cloud_sync.get_drive_service() and list/download helper to fetch files, then call the ingestion endpoint for each downloaded file.

Notes:
- FAISS index file is `embeddings.index`.
- Database is SQLite `sso.db` by default. Override with SSO_DB env var.
