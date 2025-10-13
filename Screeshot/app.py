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

# Initialize session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
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

# Dark/Light mode CSS with improved design
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 50%, #0f1628 100%);
            font-family: 'Inter', sans-serif;
            color: #e0e7ff;
        }
        
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 200% 200%;
            animation: gradientShift 5s ease infinite;
            padding: 2.5rem;
            border-radius: 25px;
            margin-bottom: 2rem;
            box-shadow: 0 25px 80px rgba(102, 126, 234, 0.5);
            border: 2px solid rgba(255,255,255,0.15);
            text-align: center;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .main-header h1 {
            color: white !important;
            font-family: 'Orbitron', sans-serif !important;
            font-size: 2.8rem !important;
            font-weight: 900 !important;
            margin: 0 !important;
            text-shadow: 0 0 30px rgba(255,255,255,0.6);
            letter-spacing: 3px;
        }
        
        .main-header p {
            color: rgba(255,255,255,0.95) !important;
            font-size: 1.1rem !important;
            margin-top: 0.5rem !important;
            font-weight: 300;
            letter-spacing: 1px;
        }
        
        .glow-card {
            background: rgba(15, 12, 41, 0.6);
            backdrop-filter: blur(20px);
            padding: 1.5rem;
            border-radius: 20px;
            border: 2px solid rgba(102, 126, 234, 0.4);
            box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        
        .glow-card:hover {
            transform: translateY(-8px) scale(1.01);
            border-color: rgba(102, 126, 234, 0.9);
            box-shadow: 0 25px 70px rgba(102, 126, 234, 0.5);
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            border: 2px solid #667eea !important;
            border-radius: 15px;
            padding: 0.8rem 2rem;
            font-weight: 700;
            font-size: 1rem;
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 1px;
            transition: all 0.3s;
            box-shadow: 0 0 25px rgba(102, 126, 234, 0.5);
            text-transform: uppercase;
        }
        
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 50px rgba(102, 126, 234, 0.8);
            border-color: #f093fb !important;
        }
        
        .tag-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.6rem 1.3rem;
            border-radius: 20px;
            margin: 0.3rem;
            font-weight: 700;
            font-size: 0.95rem;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.6);
            border: 1px solid rgba(255,255,255,0.3);
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .metric-box {
            background: rgba(102, 126, 234, 0.1);
            border: 2px solid rgba(102, 126, 234, 0.3);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 900;
            color: #667eea;
            font-family: 'Orbitron', sans-serif;
        }
        
        .metric-label {
            color: #a5b4fc;
            font-size: 0.9rem;
            margin-top: 0.5rem;
            font-weight: 600;
        }
        
        .success-box {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            font-weight: 700;
            font-size: 1.3rem;
            animation: slideIn 0.5s ease-out;
            box-shadow: 0 0 40px rgba(16, 185, 129, 0.6);
            border: 2px solid rgba(255,255,255,0.3);
        }
        
        @keyframes slideIn {
            from { transform: translateY(-30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .category-section {
            background: rgba(102, 126, 234, 0.08);
            border-left: 5px solid #667eea;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1.5rem 0;
        }
        
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .image-item {
            border-radius: 15px;
            overflow: hidden;
            border: 2px solid rgba(102, 126, 234, 0.3);
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .image-item:hover {
            transform: scale(1.05);
            box-shadow: 0 0 30px rgba(102, 126, 234, 0.6);
            border-color: #667eea;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f0c29 0%, #1a1a3e 100%) !important;
            border-right: 2px solid rgba(102, 126, 234, 0.3) !important;
        }
        
        p, span, div {
            color: #e0e7ff !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #f8fafb 0%, #f0f4f8 100%);
            font-family: 'Poppins', sans-serif;
        }
        
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem;
            border-radius: 25px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
            text-align: center;
        }
        
        .main-header h1 {
            color: white !important;
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
        }
        
        .main-header p {
            color: rgba(255,255,255,0.95) !important;
            font-size: 1.1rem !important;
            margin-top: 0.5rem !important;
        }
        
        .glow-card {
            background: white;
            padding: 1.5rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
            border: 1px solid rgba(102, 126, 234, 0.1);
        }
        
        .glow-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.2);
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            border: none !important;
            border-radius: 15px;
            padding: 0.8rem 2rem;
            font-weight: 700;
            transition: all 0.3s;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }
    </style>
    """, unsafe_allow_html=True)

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🎯 SNAPSORT AI</h1>
    <p>⚡ Intelligent Screenshot Organization with Smart Clustering</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ CONFIGURATION")
    st.markdown("---")
    
    # Dark mode toggle
    col1, col2 = st.columns(2)
    with col1:
        if st.button("☀️ Light", use_container_width=True, key="light_btn"):
            st.session_state.dark_mode = False
            st.rerun()
    with col2:
        if st.button("🌙 Dark", use_container_width=True, key="dark_btn"):
            st.session_state.dark_mode = True
            st.rerun()
    
    st.markdown("---")
    
    # Tags configuration
    st.markdown("### 🏷️ Define Your Categories")
    st.markdown("*Enter tags to organize screenshots. If no tag matches, auto-clustering will group them.*")
    
    num_tags = st.slider("Number of categories", 1, 10, 3, label_visibility="collapsed")
    
    user_tags = []
    for i in range(num_tags):
        tag = st.text_input(
            f"Category {i+1}",
            key=f"tag_{i}",
            placeholder="e.g., LinkedIn Recruiter",
            label_visibility="collapsed"
        )
        if tag and tag.strip():
            user_tags.append(tag.strip())
    
    st.markdown("---")
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        threshold = st.slider(
            "Matching Sensitivity",
            min_value=0.1,
            max_value=0.95,
            value=0.45,
            step=0.05
        )
        st.session_state.clustering_engine.similarity_threshold = threshold
        
        if threshold > 0.7:
            sens = "🔥 Very Strict - Only perfect matches"
        elif threshold > 0.5:
            sens = "⚖️ Strict - Close matches only"
        elif threshold > 0.3:
            sens = "🎯 Balanced - Good for most cases"
        else:
            sens = "🌊 Lenient - Flexible matching"
        
        st.caption(sens)

# Main content area
st.markdown("### 📤 UPLOAD SCREENSHOTS")

uploaded_files = st.file_uploader(
    "Drag & drop screenshots or click to browse",
    type=['png', 'jpg', 'jpeg'],
    accept_multiple_files=True,
    key="file_uploader"
)

# Show active categories
if user_tags:
    st.markdown("### 🎯 ACTIVE CATEGORIES")
    cols = st.columns(len(user_tags))
    for idx, tag in enumerate(user_tags):
        with cols[idx]:
            st.markdown(f"""
            <div class="tag-badge">
                🏷️ {tag}
            </div>
            """, unsafe_allow_html=True)

# Files uploaded message
if uploaded_files:
    st.markdown(f"""
    <div class="success-box">
        ✅ {len(uploaded_files)} SCREENSHOT(S) LOADED
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("👁️ PREVIEW UPLOADS", expanded=False):
        cols = st.columns(5)
        for idx, file in enumerate(uploaded_files):
            with cols[idx % 5]:
                img = Image.open(file)
                st.image(img, use_container_width=True)
                st.caption(file.name[:25])

# Processing pipeline
if uploaded_files and user_tags:
    st.markdown("---")
    st.markdown("### ⚙️ PROCESSING PIPELINE")
    
    # Process steps indicator
    col1, col2, col3 = st.columns(3)
    
    with col1:
        step_icon = "✅" if st.session_state.processing_step >= 1 else "⭕"
        st.markdown(f"""
        <div class="glow-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{step_icon}</div>
            <div style="font-weight: 700; color: #667eea;">STEP 1</div>
            <div>Extract Text</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        step_icon = "✅" if st.session_state.processing_step >= 2 else "⭕"
        st.markdown(f"""
        <div class="glow-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{step_icon}</div>
            <div style="font-weight: 700; color: #667eea;">STEP 2</div>
            <div>Match & Cluster</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        step_icon = "✅" if st.session_state.processing_step >= 3 else "⭕"
        st.markdown(f"""
        <div class="glow-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{step_icon}</div>
            <div style="font-weight: 700; color: #667eea;">STEP 3</div>
            <div>Display Results</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Process buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔍 EXTRACT TEXT", type="primary", use_container_width=True, key="extract_btn"):
            with st.spinner("🤖 Extracting text from screenshots..."):
                st.session_state.extracted_data = {}
                progress_bar = st.progress(0)
                
                for idx, file in enumerate(uploaded_files):
                    file.seek(0)
                    text = st.session_state.ocr_processor.extract_text(file)
                    st.session_state.extracted_data[file.name] = {
                        'text': text,
                        'file': file
                    }
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                st.session_state.processing_step = 1
                st.markdown('<div class="success-box">✅ TEXT EXTRACTION COMPLETE!</div>', unsafe_allow_html=True)
                time.sleep(0.5)
                st.rerun()
    
    with col_btn2:
        if st.session_state.extracted_data:
            if st.button("🧠 MATCH & CLUSTER", type="secondary", use_container_width=True, key="cluster_btn"):
                with st.spinner("🤖 AI is analyzing and organizing..."):
                    results = st.session_state.clustering_engine.organize_screenshots(
                        st.session_state.extracted_data,
                        user_tags
                    )
                    st.session_state.organized_results = results
                    st.session_state.processing_step = 2
                    st.markdown('<div class="success-box">✅ MATCHING & CLUSTERING COMPLETE!</div>', unsafe_allow_html=True)
                    time.sleep(0.5)
                    st.rerun()
        else:
            st.button("🧠 MATCH & CLUSTER", disabled=True, use_container_width=True)
    
    with col_btn3:
        if st.session_state.organized_results:
            report = {
                'total_files': len(st.session_state.extracted_data),
                'matched': st.session_state.organized_results['matched'],
                'clustered': st.session_state.organized_results['clustered'],
                'scores': st.session_state.organized_results['scores']
            }
            st.download_button(
                label="📥 EXPORT JSON",
                data=json.dumps(report, indent=2),
                file_name="snapsort_results.json",
                mime="application/json",
                use_container_width=True
            )
            st.session_state.processing_step = 3
        else:
            st.button("📥 EXPORT JSON", disabled=True, use_container_width=True)

# Results display
if st.session_state.organized_results:
    st.markdown("---")
    st.markdown("## 📊 RESULTS DASHBOARD")
    
    results = st.session_state.organized_results
    
    # Statistics
    st.markdown("### 📈 STATISTICS")
    
    total_files = len(st.session_state.extracted_data)
    total_matched = sum(len(files) for files in results['matched'].values())
    total_clustered = sum(len(files) for files in results['clustered'].values())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{total_files}</div>
            <div class="metric-label">Total Processed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value" style="color: #10b981;">{total_matched}</div>
            <div class="metric-label">Category Matched</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value" style="color: #f59e0b;">{total_clustered}</div>
            <div class="metric-label">Auto-Grouped</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        accuracy = (total_matched / total_files * 100) if total_files > 0 else 0
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value" style="color: #8b5cf6;">{accuracy:.0f}%</div>
            <div class="metric-label">Match Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Matched categories
    st.markdown("### 📁 MATCHED TO CATEGORIES")
    
    for tag in user_tags:
        matched_files = results['matched'][tag]
        if matched_files:
            st.markdown(f"#### 🏷️ {tag}")
            cols = st.columns(5)
            for idx, filename in enumerate(matched_files):
                with cols[idx % 5]:
                    data = st.session_state.extracted_data[filename]
                    data['file'].seek(0)
                    img = Image.open(data['file'])
                    st.image(img, use_container_width=True)
                    
                    score = results['scores'][filename]
                    st.caption(f"Match: {score:.0%}\n{filename[:20]}")
            st.markdown("")
    
    # Auto-clustered
    if results['clustered']:
        st.markdown("### 🔮 AUTO-CLUSTERED GROUPS")
        
        for cluster_name, filenames in results['clustered'].items():
            st.markdown(f"#### 🔗 {cluster_name} ({len(filenames)} items)")
            cols = st.columns(5)
            for idx, filename in enumerate(filenames):
                with cols[idx % 5]:
                    data = st.session_state.extracted_data[filename]
                    data['file'].seek(0)
                    img = Image.open(data['file'])
                    st.image(img, use_container_width=True)
                    st.caption(filename[:20])
            st.markdown("")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; opacity: 0.8;'>
    <p style='margin: 0;'>🎯 <strong>SnapSort AI</strong> • Intelligent Screenshot Organization</p>
    <p style='margin: 0.5rem 0; font-size: 0.9rem;'>Powered by Advanced ML • Smart Clustering Engine</p>
</div>
""", unsafe_allow_html=True)