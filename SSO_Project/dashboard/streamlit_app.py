# SSO_Project/dashboard/streamlit_app.py
"""
Streamlit dashboard:
- Enter keywords (comma-separated)
- Upload multiple images
- Calls /cluster/by_keywords/ on backend
- Shows grouped results with scores & previews
"""

import streamlit as st
import requests
import os
from PIL import Image

API_BASE = os.getenv("SSO_API", "http://localhost:8000")

st.set_page_config(page_title="SSO: Keyword Clustering", layout="wide")
st.title("🔎 Smart Screenshot Organizer — Keyword-based Clustering")

with st.sidebar:
    st.header("1) Provide Keywords")
    kw = st.text_input("Keywords (comma-separated)", "linkedin, recruiter, receipt")

    st.header("2) Upload Images")
    files = st.file_uploader("Select one or more images", type=["png","jpg","jpeg"], accept_multiple_files=True)

    if st.button("Cluster Images"):
        if not kw.strip():
            st.warning("Please enter at least one keyword.")
        elif not files:
            st.warning("Please upload at least one image.")
        else:
            data = {"keywords": kw}
            multipart = []
            for f in files:
                multipart.append(("files", (f.name, f.getvalue(), f.type)))
            try:
                r = requests.post(f"{API_BASE}/cluster/by_keywords/", data=data, files=multipart, timeout=180)
                if r.status_code == 200:
                    st.session_state["cluster_result"] = r.json()
                    st.success("Clustering complete!")
                else:
                    st.error(f"Backend error {r.status_code}")
                    try:
                        st.json(r.json())
                    except Exception:
                        st.write(r.text)
            except Exception as e:
                st.error(f"Request failed: {e}")

res = st.session_state.get("cluster_result")
if res and res.get("status") == "ok":
    st.subheader("Results")
    keywords = res.get("keywords", [])
    grouped = res.get("grouped", {})

    for kw in keywords:
        items = grouped.get(kw, [])
        with st.expander(f"📁 {kw}  —  {len(items)} image(s)", expanded=True):
            if not items:
                st.write("No images assigned.")
                continue
            cols = st.columns(3)
            col_idx = 0
            for it in items:
                with cols[col_idx]:
                    try:
                        img = Image.open(it["file_path"])
                        st.image(img, use_column_width=True)
                    except Exception:
                        st.text("(Image not available)")
                    st.caption(os.path.basename(it["file_path"]))
                    st.write(f"**Score:** {it['score']:.3f}")
                col_idx = (col_idx + 1) % 3
else:
    st.info("Use the sidebar: set keywords, upload images, then click **Cluster Images**.")

st.markdown("---")
st.subheader("Stored Assignments (from backend)")
if st.button("Refresh from backend"):
    try:
        r = requests.get(f"{API_BASE}/list/")
        if r.status_code == 200:
            data = r.json().get("items", [])
            st.write(f"Total stored: {len(data)}")
            for it in data[:100]:
                st.write(
                    f"**File:** {it['file_name']} | **Tags:** {', '.join(it.get('tags', []))} "
                    f"| **Assigned:** {it.get('metadata', {}).get('assigned_keyword')} "
                    f"| **Score:** {it.get('metadata', {}).get('score')}"
                )
        else:
            st.error("Failed to fetch.")
    except Exception as e:
        st.error(f"Error: {e}")
