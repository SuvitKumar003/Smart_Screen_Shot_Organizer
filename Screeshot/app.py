import streamlit as st
from PIL import Image
from utils.ocr_helper import OCRProcessor
from utils.smart_clustering import EnhancedClusteringEngine
import json
import time

# Must be first
st.set_page_config(
    page_title="SnapSort AI - Smart Screenshot Organizer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize dark mode state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Dark/Light mode CSS
if st.session_state.dark_mode:
    # DARK MODE - Cyberpunk style
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600;700&display=swap');
        
        /* Main background */
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* Animated gradient header */
        .mega-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 200% 200%;
            animation: gradientShift 3s ease infinite;
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
            border: 2px solid rgba(255,255,255,0.1);
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .mega-header h1 {
            color: white !important;
            font-family: 'Orbitron', sans-serif !important;
            font-size: 3.5rem !important;
            font-weight: 900 !important;
            margin: 0 !important;
            text-shadow: 0 0 20px rgba(255,255,255,0.5);
            letter-spacing: 2px;
        }
        
        .mega-header p {
            color: #e0e7ff !important;
            font-size: 1.3rem !important;
            margin-top: 1rem !important;
            font-weight: 300;
        }
        
        /* Glowing cards */
        .glow-card {
            background: rgba(15, 12, 41, 0.7);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 20px;
            border: 2px solid rgba(102, 126, 234, 0.3);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        
        .glow-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
            animation: rotate 6s linear infinite;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .glow-card:hover {
            transform: translateY(-10px) scale(1.02);
            border-color: rgba(102, 126, 234, 0.8);
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        }
        
        /* Neon buttons */
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: 2px solid #667eea;
            border-radius: 15px;
            padding: 1rem 2.5rem;
            font-weight: 700;
            font-size: 1.1rem;
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 1px;
            transition: all 0.3s;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
            text-transform: uppercase;
        }
        
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 40px rgba(102, 126, 234, 0.8);
            border-color: #f093fb;
        }
        
        /* Animated tags */
        .neon-tag {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.7rem 1.5rem;
            border-radius: 25px;
            margin: 0.5rem;
            font-weight: 700;
            font-size: 1rem;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.6);
            animation: pulse 2s ease-in-out infinite;
            border: 2px solid rgba(255,255,255,0.3);
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        /* Metrics with glow */
        [data-testid="stMetricValue"] {
            font-size: 3rem !important;
            font-weight: 900 !important;
            background: linear-gradient(135deg, #667eea 0%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Orbitron', sans-serif !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #a5b4fc !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
        }
        
        /* Progress bar animation */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 200% 100%;
            animation: shimmer 2s linear infinite;
        }
        
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        /* Sidebar dark */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f0c29 0%, #302b63 100%);
            border-right: 2px solid rgba(102, 126, 234, 0.3);
        }
        
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background: rgba(102, 126, 234, 0.2) !important;
            border-radius: 15px !important;
            border: 2px solid rgba(102, 126, 234, 0.3) !important;
            color: white !important;
            font-weight: 700 !important;
        }
        
        /* Image hover effect */
        .stImage {
            border-radius: 15px;
            overflow: hidden;
            transition: all 0.3s;
            border: 2px solid rgba(102, 126, 234, 0.3);
        }
        
        .stImage:hover {
            transform: scale(1.05);
            box-shadow: 0 0 30px rgba(102, 126, 234, 0.6);
            border-color: #667eea;
        }
        
        /* Loading animation container */
        .loading-container {
            text-align: center;
            padding: 3rem;
        }
        
        .loader {
            width: 80px;
            height: 80px;
            border: 5px solid rgba(102, 126, 234, 0.3);
            border-top: 5px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 2rem auto;
            box-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Success animation */
        .success-boom {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            font-weight: 700;
            font-size: 1.5rem;
            animation: boom 0.5s ease-out;
            box-shadow: 0 0 40px rgba(16, 185, 129, 0.6);
            border: 2px solid rgba(255,255,255,0.3);
        }
        
        @keyframes boom {
            0% { transform: scale(0); opacity: 0; }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); opacity: 1; }
        }
        
        /* Text color */
        p, span, div {
            color: #e0e7ff !important;
        }
        
        h1, h2, h3, h4 {
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # LIGHT MODE - Clean & Professional
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Poppins', sans-serif;
        }
        
        .mega-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        }
        
        .mega-header h1 {
            color: white !important;
            font-family: 'Poppins', sans-serif !important;
            font-size: 3.5rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
        }
        
        .mega-header p {
            color: #e0e7ff !important;
            font-size: 1.3rem !important;
            margin-top: 1rem !important;
        }
        
        .glow-card {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
        }
        
        .glow-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 1rem 2.5rem;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.3s;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }
        
        .neon-tag {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.7rem 1.5rem;
            border-radius: 25px;
            margin: 0.5rem;
            font-weight: 700;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
        }
        
        [data-testid="stMetricValue"] {
            font-size: 3rem !important;
            font-weight: 800 !important;
            color: #667eea !important;
        }
        
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        
        .success-boom {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            font-weight: 700;
            font-size: 1.5rem;
            animation: boom 0.5s ease-out;
            box-shadow: 0 10px 40px rgba(16, 185, 129, 0.3);
        }
        
        @keyframes boom {
            0% { transform: scale(0); opacity: 0; }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .loader {
            width: 80px;
            height: 80px;
            border: 5px solid rgba(102, 126, 234, 0.2);
            border-top: 5px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 2rem auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize processors
if 'ocr_processor' not in st.session_state:
    st.session_state.ocr_processor = OCRProcessor()

if 'clustering_engine' not in st.session_state:
    st.session_state.clustering_engine = EnhancedClusteringEngine()

if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}

if 'organized_results' not in st.session_state:
    st.session_state.organized_results = None

if 'processing_step' not in st.session_state:
    st.session_state.processing_step = 0

# Animated header
mode_icon = "🌙" if st.session_state.dark_mode else "☀️"
st.markdown(f"""
<div class="mega-header">
    <h1>🎯 SNAPSORT AI</h1>
    <p>⚡ Next-Gen Screenshot Organization Powered by Artificial Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Dark mode toggle at top
    st.markdown("### 🎨 Appearance")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"☀️ Light", use_container_width=True, type="secondary" if st.session_state.dark_mode else "primary"):
            st.session_state.dark_mode = False
            st.rerun()
    
    with col2:
        if st.button(f"🌙 Dark", use_container_width=True, type="primary" if st.session_state.dark_mode else "secondary"):
            st.session_state.dark_mode = True
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 🎯 Quick Presets")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👔 Recruiter", use_container_width=True):
            st.session_state.preset_tags = [
                "LinkedIn profiles",
                "Job postings", 
                "Candidate resumes",
                "Interview schedules"
            ]
            st.rerun()
    
    with col2:
        if st.button("💼 Business", use_container_width=True):
            st.session_state.preset_tags = [
                "Invoices",
                "Contracts",
                "Reports",
                "Presentations"
            ]
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🏷️ Your Categories")
    
    num_tags = st.slider("Number of categories", 1, 8, 3)
    
    user_tags = []
    preset_tags = st.session_state.get('preset_tags', [])
    
    for i in range(num_tags):
        default_value = preset_tags[i] if i < len(preset_tags) else ""
        tag = st.text_input(
            f"Category {i+1}", 
            value=default_value,
            key=f"tag_{i}", 
            placeholder=f"e.g., LinkedIn profiles"
        )
        if tag:
            user_tags.append(tag)
    
    st.markdown("---")
    
    with st.expander("🔧 Advanced Settings"):
        threshold = st.slider(
            "Match Sensitivity",
            min_value=0.1,
            max_value=0.9,
            value=0.35,
            step=0.05
        )
        st.session_state.clustering_engine.similarity_threshold = threshold
        
        sensitivity_text = "🔥 Strict" if threshold > 0.5 else "⚖️ Balanced" if threshold > 0.3 else "🎯 Lenient"
        st.markdown(f"**Current:** {sensitivity_text}")

# Main content
if user_tags:
    st.markdown("### ✨ Active Categories")
    tags_html = "".join([f'<span class="neon-tag">🏷️ {tag}</span>' for tag in user_tags])
    st.markdown(tags_html, unsafe_allow_html=True)
    st.markdown("")

# Upload section
st.markdown("### 📤 Upload Screenshots")

uploaded_files = st.file_uploader(
    "Drag & drop your screenshots here or click to browse",
    type=['png', 'jpg', 'jpeg'],
    accept_multiple_files=True,
    help="Supports PNG, JPG, JPEG formats"
)

if uploaded_files:
    st.markdown(f"""
    <div class="success-boom">
        ✅ {len(uploaded_files)} FILES LOADED & READY!
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📸 Preview All Screenshots", expanded=False):
        cols = st.columns(5)
        for idx, f in enumerate(uploaded_files):
            with cols[idx % 5]:
                image = Image.open(f)
                st.image(image, use_container_width=True)
                st.caption(f[:20])

# Processing section
if uploaded_files and user_tags:
    st.markdown("---")
    st.markdown("### 🚀 AI Processing Pipeline")
    
    # Step indicators
    col1, col2, col3 = st.columns(3)
    
    with col1:
        step1_status = "🟢" if st.session_state.processing_step >= 1 else "⚪"
        st.markdown(f"""
        <div class="glow-card" style="text-align: center;">
            <h2>{step1_status}</h2>
            <h4>STEP 1</h4>
            <p>Text Extraction</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        step2_status = "🟢" if st.session_state.processing_step >= 2 else "⚪"
        st.markdown(f"""
        <div class="glow-card" style="text-align: center;">
            <h2>{step2_status}</h2>
            <h4>STEP 2</h4>
            <p>AI Organization</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        step3_status = "🟢" if st.session_state.processing_step >= 3 else "⚪"
        st.markdown(f"""
        <div class="glow-card" style="text-align: center;">
            <h2>{step3_status}</h2>
            <h4>STEP 3</h4>
            <p>Results Ready</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔍 EXTRACT TEXT", type="primary", use_container_width=True):
            # Animated processing
            st.markdown("""
            <div class="loading-container">
                <div class="loader"></div>
                <h3 style="color: #667eea;">🤖 AI IS READING YOUR SCREENSHOTS...</h3>
                <p>Please wait while we extract text using OCR technology</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.session_state.extracted_data = {}
            st.session_state.organized_results = None
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.markdown(f"**⚡ Processing:** `{uploaded_file.name}`")
                
                uploaded_file.seek(0)
                extracted_text = st.session_state.ocr_processor.extract_text(uploaded_file)
                
                st.session_state.extracted_data[uploaded_file.name] = {
                    'text': extracted_text,
                    'file': uploaded_file
                }
                
                progress = (idx + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                time.sleep(0.1)  # Smooth animation
            
            st.session_state.processing_step = 1
            
            progress_bar.empty()
            status_text.empty()
            
            st.markdown("""
            <div class="success-boom">
                🎉 TEXT EXTRACTION COMPLETE!
            </div>
            """, unsafe_allow_html=True)
            
            st.balloons()
            time.sleep(1)
            st.rerun()
    
    with col_btn2:
        if st.session_state.extracted_data:
            if st.button("🤖 ORGANIZE NOW", type="secondary", use_container_width=True):
                # Animated AI processing
                st.markdown("""
                <div class="loading-container">
                    <div class="loader"></div>
                    <h3 style="color: #764ba2;">🧠 AI IS ANALYZING & ORGANIZING...</h3>
                    <p>Advanced machine learning algorithms at work</p>
                </div>
                """, unsafe_allow_html=True)
                
                progress_bar = st.progress(0)
                
                # Simulate AI thinking with progress
                for i in range(100):
                    progress_bar.progress(i / 100)
                    time.sleep(0.02)
                
                results = st.session_state.clustering_engine.organize_screenshots(
                    st.session_state.extracted_data,
                    user_tags
                )
                
                st.session_state.organized_results = results
                st.session_state.processing_step = 2
                
                progress_bar.empty()
                
                st.markdown("""
                <div class="success-boom">
                    🚀 ORGANIZATION COMPLETE!
                </div>
                """, unsafe_allow_html=True)
                
                st.balloons()
                time.sleep(1)
                st.rerun()
        else:
            st.button("🤖 ORGANIZE NOW", disabled=True, use_container_width=True)
    
    with col_btn3:
        if st.session_state.organized_results:
            results = st.session_state.organized_results
            report = {
                'total_files': len(st.session_state.extracted_data),
                'matched': results['matched'],
                'clustered': results['clustered'],
                'types': results['types']
            }
            
            st.download_button(
                label="📥 EXPORT RESULTS",
                data=json.dumps(report, indent=2),
                file_name="snapsort_results.json",
                mime="application/json",
                use_container_width=True
            )
            
            st.session_state.processing_step = 3
        else:
            st.button("📥 EXPORT RESULTS", disabled=True, use_container_width=True)

# Results display
if st.session_state.organized_results:
    st.markdown("---")
    st.markdown("## 🎯 ORGANIZATION RESULTS")
    
    results = st.session_state.organized_results
    
    # Animated stats
    st.markdown("### 📊 Statistics Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_files = len(st.session_state.extracted_data)
        st.metric("📁 TOTAL", total_files)
    
    with col2:
        total_matched = sum(len(files) for files in results['matched'].values())
        match_pct = (total_matched/total_files*100) if total_files > 0 else 0
        st.metric("✅ MATCHED", total_matched, f"{match_pct:.0f}%")
    
    with col3:
        total_clustered = sum(len(files) for files in results['clustered'].values())
        st.metric("🔮 GROUPED", total_clustered)
    
    with col4:
        accuracy = (total_matched / total_files * 100) if total_files > 0 else 0
        st.metric("🎯 ACCURACY", f"{accuracy:.0f}%")
    
    st.markdown("---")
    
    # Display results by category
    st.markdown("### 🏷️ CATEGORIZED SCREENSHOTS")
    
    for tag in user_tags:
        if results['matched'][tag]:
            st.markdown(f"#### 📁 {tag.upper()}")
            
            cols = st.columns(5)
            for idx, filename in enumerate(results['matched'][tag]):
                with cols[idx % 5]:
                    data = st.session_state.extracted_data[filename]
                    data['file'].seek(0)
                    image = Image.open(data['file'])
                    st.image(image, use_container_width=True)
                    
                    score = results['scores'][filename]
                    screenshot_type = results['types'].get(filename, 'unknown')
                    
                    st.markdown(f"**Match:** {score:.0%}")
                    st.caption(f"Type: {screenshot_type}")
            
            st.markdown("")
    
    # Auto-clustered
    if results['clustered']:
        st.markdown("---")
        st.markdown("### 🔮 SMART AUTO-GROUPS")
        
        for cluster_name, filenames in results['clustered'].items():
            with st.expander(f"📦 {cluster_name} ({len(filenames)} files)"):
                cols = st.columns(5)
                for idx, filename in enumerate(filenames):
                    with cols[idx % 5]:
                        data = st.session_state.extracted_data[filename]
                        data['file'].seek(0)
                        image = Image.open(data['file'])
                        st.image(image, use_container_width=True)
                        st.caption(filename[:20])

# Footer
st.markdown("---")
mode_text = "DARK MODE 🌙" if st.session_state.dark_mode else "LIGHT MODE ☀️"
st.markdown(f"""
<div style='text-align: center; padding: 2rem;'>
    <h3 style='margin: 0;'>SNAPSORT AI</h3>
    <p style='margin: 0.5rem 0;'>Powered by Advanced AI • {mode_text}</p>
</div>
""", unsafe_allow_html=True)