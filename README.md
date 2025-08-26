# SSO Project

> ⚠️ Note: This repository was originally named **Credit-Card--Fraud-Detection-AutoEncoder** by mistake.  
> The contents have been replaced with my **SSO Project**.

📸 Smart Screenshot Organizer (SSSO)

A Machine Learning-powered screenshot management system that automatically classifies, organizes, and makes screenshots searchable. Instead of manually scrolling through hundreds of images, SSSO enables smart search, auto-tagging, and context-aware organization of screenshots.

🌟 Features

✅ Automatic Classification – Detects the type of screenshot (e.g., LinkedIn post, job opening, bill, chat, etc.)
✅ Metadata Extraction – Captures key text (company name, job role, numbers, etc.) using OCR
✅ Searchable Screenshots – Quickly find images using keywords (e.g., “Google internship”, “Invoice”)
✅ Organized Storage – Screenshots are automatically grouped into folders by category
✅ Extensible ML Pipeline – Easily add more categories and improve classification over time

🧠 Tech Stack

Frontend: React.js

Backend: Flask / FastAPI

Machine Learning:

CNN / Transfer Learning for screenshot classification

OCR (Tesseract / EasyOCR) for extracting text

NLP for keyword tagging


⚙️ Installation

Clone the repo

git clone https://github.com/SuvitKumar003/Smart_ScreenShot_Organizer.git
cd Smart_ScreenShot_Organizer


Backend Setup

cd backend
pip install -r requirements.txt
python app.py


Frontend Setup

cd frontend
npm install
npm start


Access App
Open: http://localhost:3000

📂 Project Structure
Smart_ScreenShot_Organizer/
│── backend/              # Flask backend + ML models
│   ├── models/           # Trained ML models
│   ├── app.py            # API endpoints
│   └── utils/            # OCR + preprocessing
│
│── frontend/             # React frontend
│   ├── src/              # Components + UI
│   └── public/
│
│── dataset/              # Training dataset (sample screenshots)
│── README.md             # Project documentation

🚀 Future Improvements

🔍 Visual Search → Search by uploading a sample image

🤖 FAANG-level ML → Better models with transformers for text + image

☁️ Cloud Integration → Auto-sync with Google Drive / Dropbox

📊 Analytics Dashboard → See screenshot usage trends

📜 License

This project is licensed under the MIT License.

👨‍💻 Author

Suvit Kumar
LinkedIn
 | GitHub

Database: SQLite / MongoDB (to store metadata & searchable tags)

Deployment: Docker + GitHub Actions (future scope: cloud hosting on AWS/GCP)
