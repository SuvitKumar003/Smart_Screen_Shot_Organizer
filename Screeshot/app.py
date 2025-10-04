import streamlit as st
from PIL import Image
from utils.ocr_helper import OCRProcessor
from utils.smart_clustering import EnhancedClusteringEngine
import json

# Must be first Streamlit command
st.set_page_config(
    page_title="SnapSort AI - Smart Screenshot Organizer for Recruiters",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main theme colors - Professional Blue & Orange */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #f59e0b;
        --success-color: #10b981;
        --background: #f8fafc;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: #e0e7ff !important;
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
    }
    
    /* Stat cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border-left: 4px solid var(--primary-color);
        transition: transform 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Tag badges */
    .tag-badge {
        display: inline-block;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(245, 87, 108, 0.3);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: white;
    }
    
    /* Success message */
    .success-banner {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    /* Image containers */
    .image-container {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    
    .image-container:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        font-weight: 600;
        color: #1e293b;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize processors
if 'ocr_processor' not in st.session_state:
    with st.spinner("🔄 Initializing AI Engine..."):
        st.session_state.ocr_processor = OCRProcessor()

if 'clustering_engine' not in st.session_state:
    with st.spinner("🤖 Loading Smart Clustering AI..."):
        st.session_state.clustering_engine = EnhancedClusteringEngine()

if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}

if 'organized_results' not in st.session_state:
    st.session_state.organized_results = None

# Beautiful Header
st.markdown("""
<div class="main-header">
    <h1>🎯 SnapSort AI</h1>
    <p>⚡ AI-Powered Screenshot Organization for Busy Recruiters</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with gradient
with st.sidebar:
    st.markdown("## ⚙️ Setup Your Categories")
    
    st.markdown("""
    <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
        <p style='color: white; margin: 0;'>💡 <strong>Pro Tip:</strong> Be specific with your tags for better results!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick presets for recruiters
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
    
    with col2:
        if st.button("💼 Business", use_container_width=True):
            st.session_state.preset_tags = [
                "Invoices",
                "Contracts",
                "Reports",
                "Presentations"
            ]
    
    st.markdown("---")
    
    # Tag configuration
    st.markdown("### 🏷️ Your Categories")
    
    num_tags = st.slider("Number of categories", 1, 8, 3)
    
    user_tags = []
    
    # Use preset tags if available
    preset_tags = st.session_state.get('preset_tags', [])
    
    for i in range(num_tags):
        default_value = preset_tags[i] if i < len(preset_tags) else ""
        tag = st.text_input(
            f"Category {i+1}", 
            value=default_value,
            key=f"tag_{i}", 
            placeholder=f"e.g., LinkedIn profiles, resumes"
        )
        if tag:
            user_tags.append(tag)
    
    st.markdown("---")
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        threshold = st.slider(
            "Match Sensitivity",
            min_value=0.1,
            max_value=0.9,
            value=0.35,
            step=0.05,
            help="Higher = More strict matching"
        )
        st.session_state.clustering_engine.similarity_threshold = threshold
        
        st.markdown("**Current:** " + ("Strict ⚡" if threshold > 0.5 else "Balanced ✨" if threshold > 0.3 else "Lenient 🎯"))

# Main content area
if user_tags:
    st.markdown("### ✅ Active Categories")
    tags_html = "".join([f'<span class="tag-badge">🏷️ {tag}</span>' for tag in user_tags])
    st.markdown(tags_html, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="info-box">
        <strong>⚠️ Setup Required:</strong> Please define at least one category in the sidebar to start organizing!
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Upload Section
st.markdown("### 📤 Upload Your Screenshots")

col_upload, col_info = st.columns([2, 1])

with col_upload:
    uploaded_files = st.file_uploader(
        "Drag and drop your screenshots here",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Supports PNG, JPG, JPEG formats"
    )

with col_info:
    if uploaded_files:
        st.markdown(f"""
        <div class="success-banner">
            ✅ {len(uploaded_files)} files ready!
        </div>
        """, unsafe_allow_html=True)
        
        # File size info
        total_size = sum([f.size for f in uploaded_files]) / (1024 * 1024)
        st.info(f"📊 Total size: {total_size:.2f} MB")
    else:
        st.markdown("""
        <div style='background: #fee2e2; padding: 1rem; border-radius: 10px; border-left: 4px solid #ef4444;'>
            <p style='color: #991b1b; margin: 0;'><strong>No files uploaded yet</strong></p>
            <p style='color: #991b1b; margin: 0; font-size: 0.9rem;'>Upload screenshots to begin</p>
        </div>
        """, unsafe_allow_html=True)

# Preview uploaded images
if uploaded_files:
    st.markdown("---")
    st.markdown("### 🖼️ Preview")
    
    with st.expander("📸 View All Uploaded Screenshots", expanded=True):
        cols = st.columns(4)
        for idx, uploaded_file in enumerate(uploaded_files):
            with cols[idx % 4]:
                image = Image.open(uploaded_file)
                st.image(image, caption=uploaded_file.name, use_container_width=True)

# Processing buttons
if uploaded_files and user_tags:
    st.markdown("---")
    st.markdown("### 🚀 Process Your Screenshots")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**Step 1: Extract Text**")
        st.caption("AI reads all text from images")
    
    with col2:
        st.markdown("**Step 2: Smart Organize**")
        st.caption("AI categorizes automatically")
    
    with col3:
        st.markdown("**Step 3: Review & Export**")
        st.caption("Download organized results")
    
    st.markdown("")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn1:
        if st.button("🔍 Extract Text", type="primary", use_container_width=True):
            with st.spinner("🔍 AI is reading your screenshots..."):
                
                st.session_state.extracted_data = {}
                st.session_state.organized_results = None
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.markdown(f"**Processing:** {uploaded_file.name}")
                    
                    uploaded_file.seek(0)
                    extracted_text = st.session_state.ocr_processor.extract_text(uploaded_file)
                    
                    st.session_state.extracted_data[uploaded_file.name] = {
                        'text': extracted_text,
                        'file': uploaded_file
                    }
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                progress_bar.empty()
                status_text.empty()
                
                st.markdown("""
                <div class="success-banner">
                    ✅ Text extraction complete! Ready for Step 2
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
    
    with col_btn2:
        if st.session_state.extracted_data:
            if st.button("🤖 Organize Now", type="secondary", use_container_width=True):
                with st.spinner("🤖 AI is organizing your screenshots..."):
                    
                    results = st.session_state.clustering_engine.organize_screenshots(
                        st.session_state.extracted_data,
                        user_tags
                    )
                    
                    st.session_state.organized_results = results
                    
                    st.markdown("""
                    <div class="success-banner">
                        🎉 Organization complete! Scroll down to see results
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
        else:
            st.button("🤖 Organize Now", disabled=True, use_container_width=True)
    
    with col_btn3:
        if st.session_state.organized_results:
            if st.button("📥 Export Results", use_container_width=True):
                results = st.session_state.organized_results
                report = {
                    'total_files': len(st.session_state.extracted_data),
                    'matched': results['matched'],
                    'clustered': results['clustered'],
                    'types': results['types']
                }
                
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json.dumps(report, indent=2),
                    file_name="snapsort_results.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.button("📥 Export Results", disabled=True, use_container_width=True)

# Display extracted text preview
if st.session_state.extracted_data and not st.session_state.organized_results:
    st.markdown("---")
    st.markdown("### 📝 Extracted Text Preview")
    
    with st.expander("👁️ View extracted text from all screenshots"):
        for filename, data in st.session_state.extracted_data.items():
            with st.container():
                col_img, col_text = st.columns([1, 2])
                
                with col_img:
                    data['file'].seek(0)
                    image = Image.open(data['file'])
                    st.image(image, use_container_width=True)
                
                with col_text:
                    st.markdown(f"**{filename}**")
                    if data['text'] == "[No text detected]":
                        st.warning("⚠️ No text found in this image")
                    elif data['text'].startswith("[Error"):
                        st.error(f"❌ {data['text']}")
                    else:
                        with st.expander("📄 Show text"):
                            st.text_area(
                                "Content",
                                data['text'],
                                height=150,
                                key=f"text_{filename}",
                                label_visibility="collapsed"
                            )
                
                st.markdown("---")

# Display organized results
if st.session_state.organized_results:
    st.markdown("---")
    st.markdown("## 🎯 Organization Results")
    
    results = st.session_state.organized_results
    
    # Beautiful statistics
    st.markdown("### 📊 Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_files = len(st.session_state.extracted_data)
        st.metric("📁 Total Files", total_files, delta=None)
    
    with col2:
        total_matched = sum(len(files) for files in results['matched'].values())
        st.metric("✅ Matched", total_matched, delta=f"{(total_matched/total_files*100):.0f}%")
    
    with col3:
        total_clustered = sum(len(files) for files in results['clustered'].values())
        st.metric("🔮 Auto-Grouped", total_clustered)
    
    with col4:
        accuracy = (total_matched / total_files * 100) if total_files > 0 else 0
        st.metric("🎯 Match Rate", f"{accuracy:.0f}%")
    
    st.markdown("---")
    
    # Display matched categories
    st.markdown("### 🏷️ Your Categories")
    
    for tag in user_tags:
        if results['matched'][tag]:
            st.markdown(f"#### 📁 {tag}")
            st.caption(f"{len(results['matched'][tag])} screenshots matched")
            
            cols = st.columns(4)
            for idx, filename in enumerate(results['matched'][tag]):
                with cols[idx % 4]:
                    with st.container():
                        data = st.session_state.extracted_data[filename]
                        data['file'].seek(0)
                        image = Image.open(data['file'])
                        
                        st.image(image, use_container_width=True)
                        
                        score = results['scores'][filename]
                        screenshot_type = results['types'].get(filename, 'unknown')
                        
                        st.markdown(f"""
                        <div style='background: white; padding: 0.5rem; border-radius: 8px; margin-top: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            <p style='margin: 0; font-size: 0.8rem; color: #64748b;'>{filename[:20]}...</p>
                            <p style='margin: 0.25rem 0 0 0; font-size: 0.85rem;'>
                                <span style='color: #10b981; font-weight: 600;'>Match: {score:.0%}</span><br/>
                                <span style='color: #6366f1;'>Type: {screenshot_type}</span>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("---")
        else:
            with st.expander(f"📁 {tag} - No matches"):
                st.info("No screenshots matched this category. Try adjusting the match sensitivity in settings.")
    
    # Display auto-clustered
    if results['clustered']:
        st.markdown("### 🔮 Smart Auto-Grouping")
        st.caption("AI detected these additional groups based on content similarity")
        
        for cluster_name, filenames in results['clustered'].items():
            with st.expander(f"📦 {cluster_name} ({len(filenames)} screenshots)"):
                cols = st.columns(4)
                for idx, filename in enumerate(filenames):
                    with cols[idx % 4]:
                        data = st.session_state.extracted_data[filename]
                        data['file'].seek(0)
                        image = Image.open(data['file'])
                        st.image(image, use_container_width=True)
                        
                        screenshot_type = results['types'].get(filename, 'unknown')
                        st.caption(f"🔖 {screenshot_type}")
                        st.caption(f"📄 {filename[:25]}...")
    
    # Success message
    st.markdown("""
    <div class="success-banner" style="margin-top: 2rem;">
        🎉 <strong>Organization Complete!</strong> Your screenshots are now smartly organized. Export the results using the button above.
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem 0;'>
    <p style='margin: 0;'>Made with ❤️ by <strong>SnapSort AI</strong></p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Powered by Advanced AI & Machine Learning</p>
</div>
""", unsafe_allow_html=True)