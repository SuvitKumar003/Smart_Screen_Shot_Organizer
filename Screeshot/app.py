import streamlit as st
from PIL import Image
from utils.ocr_helper import OCRProcessor
from utils.smart_clustering import EnhancedClusteringEngine

# Page config
st.set_page_config(
    page_title="SnapSort - Screenshot Organizer",
    page_icon="📸",
    layout="wide"
)

# Initialize processors in session state
if 'ocr_processor' not in st.session_state:
    with st.spinner("🔄 Initializing OCR engine..."):
        st.session_state.ocr_processor = OCRProcessor()

if 'clustering_engine' not in st.session_state:
    with st.spinner("🔄 Loading AI models..."):
        st.session_state.clustering_engine = EnhancedClusteringEngine()

if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}

if 'organized_results' not in st.session_state:
    st.session_state.organized_results = None

# Title
st.title("📸 SnapSort - AI Screenshot Organizer")
st.markdown("**✨ Enhanced with Smart Clustering**")
st.markdown("---")

# Sidebar for user inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # User defined tags
    st.subheader("Define Your Tags")
    st.caption("Enter categories you want to organize screenshots into")
    
    num_tags = st.number_input("Number of tags", min_value=1, max_value=10, value=3)
    
    user_tags = []
    for i in range(num_tags):
        tag = st.text_input(
            f"Tag {i+1}", 
            key=f"tag_{i}", 
            placeholder=f"e.g., LinkedIn recruiter, code, receipts"
        )
        if tag:
            user_tags.append(tag)
    
    st.markdown("---")
    st.info("💡 Images that don't fit will be auto-clustered smartly!")
    
    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        threshold = st.slider(
            "Similarity Threshold",
            min_value=0.1,
            max_value=0.9,
            value=0.35,
            step=0.05,
            help="Higher = stricter matching"
        )
        st.session_state.clustering_engine.similarity_threshold = threshold

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
    st.subheader("📊 Status")
    if user_tags:
        st.write("**Your Tags:**")
        for tag in user_tags:
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

# Process button
if uploaded_files and user_tags:
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🔍 Step 1: Extract Text", type="primary", use_container_width=True):
            with st.spinner("🔍 Extracting text using OCR..."):
                
                # Clear previous results
                st.session_state.extracted_data = {}
                st.session_state.organized_results = None
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process each image
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Extract text
                    extracted_text = st.session_state.ocr_processor.extract_text(uploaded_file)
                    
                    # Store in session state
                    st.session_state.extracted_data[uploaded_file.name] = {
                        'text': extracted_text,
                        'file': uploaded_file
                    }
                    
                    # Update progress
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                status_text.text("✅ Text extraction complete!")
                st.success("✅ Ready for Step 2!")
    
    with col_btn2:
        if st.session_state.extracted_data and st.button("🤖 Step 2: AI Organize", type="secondary", use_container_width=True):
            with st.spinner("🤖 Using enhanced AI to organize screenshots..."):
                
                # Organize using clustering engine
                results = st.session_state.clustering_engine.organize_screenshots(
                    st.session_state.extracted_data,
                    user_tags
                )
                
                st.session_state.organized_results = results
                st.balloons()
                st.success("✅ Organization complete!")

# Display extracted text
if st.session_state.extracted_data and not st.session_state.organized_results:
    st.markdown("---")
    st.subheader("📝 Extracted Text Results")
    
    for filename, data in st.session_state.extracted_data.items():
        with st.expander(f"📄 {filename}", expanded=False):
            col_img, col_text = st.columns([1, 2])
            
            with col_img:
                data['file'].seek(0)
                image = Image.open(data['file'])
                st.image(image, width=250)
            
            with col_text:
                st.markdown("**Extracted Text:**")
                if data['text'] == "[No text detected]":
                    st.warning(data['text'])
                elif data['text'].startswith("[Error"):
                    st.error(data['text'])
                else:
                    st.text_area(
                        "Text content",
                        data['text'],
                        height=200,
                        key=f"text_{filename}",
                        label_visibility="collapsed"
                    )

# Display organized results
if st.session_state.organized_results:
    st.markdown("---")
    st.subheader("🎯 Enhanced AI Organization Results")
    
    results = st.session_state.organized_results
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        total_matched = sum(len(files) for files in results['matched'].values())
        st.metric("✅ Matched to Tags", total_matched)
    with col2:
        total_clustered = sum(len(files) for files in results['clustered'].values())
        st.metric("🔮 Auto-Clustered", total_clustered)
    with col3:
        st.metric("📊 Total Processed", len(st.session_state.extracted_data))
    
    # Display matched tags
    st.markdown("### 🏷️ Matched to Your Tags")
    
    for tag in user_tags:
        if results['matched'][tag]:
            with st.expander(f"📁 {tag} ({len(results['matched'][tag])} images)", expanded=True):
                cols = st.columns(3)
                for idx, filename in enumerate(results['matched'][tag]):
                    with cols[idx % 3]:
                        data = st.session_state.extracted_data[filename]
                        data['file'].seek(0)
                        image = Image.open(data['file'])
                        st.image(image, caption=filename, width=200)
                        
                        score = results['scores'][filename]
                        screenshot_type = results.get('types', {}).get(filename, 'unknown')
                        
                        st.caption(f"📊 Match Score: {score:.2%}")
                        st.caption(f"🔖 Detected Type: {screenshot_type}")
    
    # Display auto-clustered
    if results['clustered']:
        st.markdown("### 🔮 Smart Auto-Clustering")
        st.caption("✨ Intelligently grouped by content type and similarity")
        
        for cluster_name, filenames in results['clustered'].items():
            with st.expander(f"📦 {cluster_name} ({len(filenames)} images)", expanded=True):
                cols = st.columns(3)
                for idx, filename in enumerate(filenames):
                    with cols[idx % 3]:
                        data = st.session_state.extracted_data[filename]
                        data['file'].seek(0)
                        image = Image.open(data['file'])
                        st.image(image, caption=filename, width=200)
                        
                        screenshot_type = results.get('types', {}).get(filename, 'unknown')
                        st.caption(f"🔖 Type: {screenshot_type}")
    
    st.success("🎉 Organization complete!")
    
    # Show what's improved
    with st.expander("✨ What's New in Enhanced Version?"):
        st.markdown("""
        **🎯 Smarter Clustering:**
        - Automatically detects screenshot types (LinkedIn, code, receipts, etc.)
        - Keyword extraction for better matching
        - Focuses only on relevant text portions
        - Multi-factor similarity scoring
        
        **📊 Better Results:**
        - More accurate tag matching
        - Intelligent grouping of unmatched screenshots
        - Shows detected screenshot types
        - Improved match scores
        """)

# Footer
st.markdown("---")
st.caption("Made with ❤️ using Streamlit, EasyOCR & AI • Enhanced Clustering Active ✨")