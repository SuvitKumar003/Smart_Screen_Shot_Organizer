# 📸 SnapSort - AI Screenshot Organizer

An intelligent screenshot organizer that uses OCR and semi-supervised clustering to automatically categorize your screenshots.

## 🚀 Features (In Progress)

- ✅ Upload multiple screenshots
- ✅ Define custom tags/categories
- 🔄 OCR text extraction (Coming in Step 2)
- 🔄 AI-powered clustering (Coming in Step 3)
- 🔄 Auto-create new categories (Coming in Step 3)
- 🔄 Download organized files (Coming in Step 4)

## 📦 Installation

1. Clone the repository
2. Create folders:
```bash
mkdir uploads organized
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## ▶️ Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🏗️ Project Structure

```
screenshot-organizer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── uploads/              # Temporary storage for uploads
├── organized/            # Output organized folders
└── utils/                # Utility functions (coming soon)
```

## 📝 Progress

**Step 1: Basic UI** ✅ (15% Complete)
- Streamlit interface
- File upload
- Tag definition
- Image preview

**Step 2: OCR Integration** 🔄 (Next)
**Step 3: Clustering Logic** 🔄
**Step 4: Organization & Export** 🔄
**Step 5: Deployment** 🔄

## 👨‍💻 Tech Stack

- **Frontend**: Streamlit
- **OCR**: EasyOCR (Coming)
- **ML**: sentence-transformers (Coming)
- **Language**: Python 3.8+

---

Built with ❤️ for solving real-world problems