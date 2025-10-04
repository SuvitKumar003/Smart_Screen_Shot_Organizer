import streamlit as st
from PIL import Image
import os
from utils.ocr_helper import OCRProcessor
from utils.smart_clustering import SmartClusteringEngine
from utils.file_manager import FileManager

# Page config
st.set_page_config(
    page_title="SnapSort - AI Screenshot Organizer",
    page_icon="📸",
    layout="wide"
)

# Initialize processors in session state
if 'ocr_processor' not in st.session_state:
    with st.spinner("🔄 Initializing OCR engine..."):
        st.session_state.ocr_processor = OCRProcessor()

if 'clustering_engine' not in st.session_state:
    with st.spinner("🧠 Loading Smart AI models..."):
        st.session_state.clustering_engine = SmartClusteringEngine()

if 'file_manager' not in st.session_state:
    st.session_state.file_manager = FileManager()

if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}

if 'organized_results' not in st.session_state:
    st.session_state.organized_results = None

if 'organized_dir' not in st.session_state:
    st.session_state.organized_dir = None

# Title
st.title("📸 SnapSort - Smart AI Screenshot Organizer")
st.markdown("*Intelligently organize screenshots with semantic understanding*")
st.markdown("---")

# Sidebar for user inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # User defined tags
    st.subheader("Define Your Tags")
    st.caption("AI understands context! Try: linkedin, twitter, code, receipts, emails")
    
    num_tags = st.number_input("Number of tags", min_value=1, max_value=10, value=3)
    
    user_tags = []
    for i in range(num_tags):
        tag = st.text_input(f"Tag {i+1}", key=f"tag_{i}", 
                           placeholder=f"e.g., linkedin, code, receipts")
        if tag:
            user_tags.append(tag)
    
    st.markdown("---")
    st.info("💡 AI detects: LinkedIn, Twitter, Code, Receipts, Emails, WhatsApp & more!")
    
    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        threshold = st.slider(
            "Similarity Threshold",
            min_value=0.1,
            max_value=0.9,
            value=0.30,
            step=0.05,
            help="Lower = more flexible matching"
        )
        st.session_state.clustering_engine.similarity_threshold = threshold
        
        st.markdown("**🧠 Smart Features:**")
        st.write("✅ Text cleaning (removes noise)")
        st.write("✅ Keyword detection")
        st.write("✅ Semantic understanding")
        st.write("✅ Context-aware matching")

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Upload Screenshots")
    uploaded_files = st.file_uploader(
        "Choose screenshot images",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} images uploaded!")

with col2:
    st.subheader("📊 Your Tags")
    if user_tags:
        for tag in user_tags:
            # Show if it's a recognized domain
            if tag.lower() in st.session_state.clustering_engine.domain_patterns:
                st.write(f"🎯 {tag} (Smart Match Enabled)")
            else:
                st.write(f"🏷️ {tag}")
    else:
        st.warning("⚠️ Please define at least one tag")

# Display uploaded images
if uploaded_files:
    st.markdown("---")
    st.subheader("🖼️ Uploaded Images Preview")
    
    cols = st.columns(4)
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx % 4]:
            image = Image.open(uploaded_file)
            st.image(image, caption=uploaded_file.name, width=200)

# Process buttons
if uploaded_files and user_tags:
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔍 Step 1: Extract Text", type="primary"):
            with st.spinner("🔍 Extracting text using OCR..."):
                
                # Clear previous results
                st.session_state.extracted_data = {}
                st.session_state.organized_results = None
                st.session_state.organized_dir = None
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process each image
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    uploaded_file.seek(0)
                    extracted_text = st.session_state.ocr_processor.extract_text(uploaded_file)
                    
                    st.session_state.extracted_data[uploaded_file.name] = {
                        'text': extracted_text,
                        'file': uploaded_file
                    }
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                status_text.text("✅ Text extraction complete!")
                st.success("✅ Ready for Smart AI Organization!")
    
    with col_btn2:
        if st.session_state.extracted_data and st.button("🧠 Step 2: Smart AI Organize"):
            with st.spinner("🧠 Using Smart AI to understand and organize..."):
                
                # Organize using smart clustering
                results = st.session_state.clustering_engine.organize_screenshots(
                    st.session_state.extracted_data,
                    user_tags
                )
                
                st.session_state.organized_results = results
                st.balloons()
                st.success("✅ Smart organization complete!")
    
    with col_btn3:
        if st.session_state.organized_results and st.button("💾 Step 3: Export Files"):
            with st.spinner("💾 Creating organized folders..."):
                
                organized_dir = st.session_state.file_manager.organize_files(
                    st.session_state.extracted_data,
                    st.session_state.organized_results
                )
                
                st.session_state.organized_dir = organized_dir
                st.success("✅ Files organized! Ready for download!")

# Display statistics
if st.session_state.organized_results:
    st.markdown("---")
    st.subheader("📊 Smart Organization Statistics")
    
    stats = st.session_state.file_manager.get_statistics(st.session_state.organized_results)
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("Total Images", stats['total_images'])
    
    with col_stat2:
        st.metric("Smart Matched", stats['total_matched'], 
                 help="Matched using AI understanding")
    
    with col_stat3:
        st.metric("Auto-Clustered", stats['total_clustered'])
    
    with col_stat4:
        st.metric("Clusters Found", stats['clusters_created'])
    
    # Show match methods breakdown
    results = st.session_state.organized_results
    if 'methods' in results:
        st.markdown("### 🎯 Matching Intelligence Breakdown")
        methods_count = {}
        for method in results['methods'].values():
            methods_count[method] = methods_count.get(method, 0) + 1
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Keyword Match", methods_count.get('keyword_match', 0),
                     help="Matched using domain-specific keywords")
        with col_m2:
            st.metric("Semantic Match", methods_count.get('semantic_match', 0),
                     help="Matched using AI semantic understanding")
        with col_m3:
            st.metric("No Text", methods_count.get('no_text', 0),
                     help="Images with no detectable text")

# Download section
if st.session_state.organized_dir:
    st.markdown("---")
    st.subheader("⬇️ Download Organized Files")
    
    with st.spinner("📦 Creating ZIP file..."):
        zip_path = st.session_state.file_manager.create_zip(st.session_state.organized_dir)
        
        with open(zip_path, 'rb') as f:
            st.download_button(
                label="📥 Download Smart Organized Screenshots (ZIP)",
                data=f,
                file_name=os.path.basename(zip_path),
                mime="application/zip",
                type="primary"
            )
    
    st.success("🎉 All done! Your screenshots are intelligently organized!")

# Display organized results
if st.session_state.organized_results:
    st.markdown("---")
    st.subheader("🎯 Smart AI Organization Results")
    
    results = st.session_state.organized_results
    
    # Display matched tags
    st.markdown("### 🏷️ Matched to Your Tags (AI Understanding)")
    
    for tag in user_tags:
        if results['matched'][tag]:
            with st.expander(f"📁 {tag} ({len(results['matched'][tag])} images)", expanded=False):
                cols = st.columns(4)
                for idx, filename in enumerate(results['matched'][tag]):
                    with cols[idx % 4]:
                        data = st.session_state.extracted_data[filename]
                        data['file'].seek(0)
                        image = Image.open(data['file'])
                        st.image(image, width=150)
                        
                        score = results['scores'][filename]
                        method = results['methods'][filename]
                        
                        # Show match details
                        if method == 'keyword_match':
                            st.caption(f"🎯 {filename}")
                            st.caption(f"✨ {score:.1%} (Keyword Match)")
                        else:
                            st.caption(f"🧠 {filename}")
                            st.caption(f"✨ {score:.1%} (Semantic Match)")
                        
                        # Show cleaned text in expander
                        if filename in results['cleaned_texts']:
                            with st.expander("📝 See extracted text", expanded=False):
                                st.text(results['cleaned_texts'][filename][:200])
    
    # Display auto-clustered
    if results['clustered']:
        st.markdown("### 🔮 Auto-Discovered Smart Clusters")
        
        for cluster_name, filenames in results['clustered'].items():
            # Better cluster names
            display_name = cluster_name.replace('_auto', ' (Auto-detected)')
            display_name = display_name.replace('_', ' ').title()
            
            with st.expander(f"📦 {display_name} ({len(filenames)} images)", expanded=False):
                cols = st.columns(4)
                for idx, filename in enumerate(filenames):
                    with cols[idx % 4]:
                        data = st.session_state.extracted_data[filename]
                        data['file'].seek(0)
                        image = Image.open(data['file'])
                        st.image(image, caption=filename, width=150)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <p>🧠 Powered by Smart AI: Keyword Detection + Semantic Understanding</p>
    <p>📸 SnapSort - Making screenshot organization intelligent & context-aware</p>
    </div>
    """,
    unsafe_allow_html=True
)