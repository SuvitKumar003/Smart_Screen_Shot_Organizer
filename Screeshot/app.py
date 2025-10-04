import streamlit as st
from PIL import Image
import requests
import io
import json
from utils.ocr_helper import OCRProcessor
from utils.enhanced_clustering import EnhancedClusteringEngine

# Backend API URL
API_URL = "http://localhost:5000/api"

# Page config
st.set_page_config(
    page_title="SnapSort - AI Screenshot Organizer",
    page_icon="📸",
    layout="wide"
)

# Initialize session state for auth
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Initialize processors
if 'ocr_processor' not in st.session_state:
    st.session_state.ocr_processor = OCRProcessor()
if 'clustering_engine' not in st.session_state:
    st.session_state.clustering_engine = EnhancedClusteringEngine()
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'organized_results' not in st.session_state:
    st.session_state.organized_results = None
if 'drive_files' not in st.session_state:
    st.session_state.drive_files = []
if 'drive_downloaded' not in st.session_state:
    st.session_state.drive_downloaded = []

# Helper functions for API calls
def check_auth_status():
    """Check if user is authenticated"""
    try:
        response = requests.get(f"{API_URL}/auth/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('authenticated'):
                st.session_state.authenticated = True
                st.session_state.user = data.get('user')
                return True
    except:
        pass
    return False

def login(email, password):
    """Login user"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.user = data.get('user')
            return True, "Login successful!"
        else:
            return False, response.json().get('error', 'Login failed')
    except Exception as e:
        return False, str(e)

def register(name, email, password):
    """Register new user"""
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={"name": name, "email": email, "password": password}
        )
        if response.status_code == 200:
            return True, "Registration successful! Please login."
        else:
            return False, response.json().get('error', 'Registration failed')
    except Exception as e:
        return False, str(e)

def logout():
    """Logout user"""
    try:
        requests.post(f"{API_URL}/auth/logout")
    except:
        pass
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.extracted_data = {}
    st.session_state.organized_results = None
    st.session_state.drive_files = []
    st.session_state.drive_downloaded = []
    st.rerun()

def get_drive_auth_url():
    """Get Google Drive authorization URL"""
    try:
        response = requests.get(f"{API_URL}/drive/authorize")
        if response.status_code == 200:
            return response.json().get('authUrl')
    except Exception as e:
        st.error(f"Error: {e}")
    return None

def fetch_drive_screenshots():
    """Fetch screenshots from Google Drive"""
    try:
        response = requests.get(f"{API_URL}/drive/screenshots")
        if response.status_code == 200:
            data = response.json()
            return data.get('files', [])
        else:
            st.error(response.json().get('error', 'Failed to fetch files'))
    except Exception as e:
        st.error(f"Error: {e}")
    return []

def download_drive_file(file_id, file_name):
    """Download file from Google Drive"""
    try:
        response = requests.get(f"{API_URL}/drive/download/{file_id}")
        if response.status_code == 200:
            return io.BytesIO(response.content), file_name
    except Exception as e:
        st.error(f"Error downloading {file_name}: {e}")
    return None, None

# Check auth status on load
check_auth_status()

# ============= LOGIN/REGISTER PAGE =============
if not st.session_state.authenticated:
    st.title("📸 SnapSort - AI Screenshot Organizer")
    st.markdown("### Welcome! Please login or register to continue")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("Login to Your Account")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if email and password:
                    success, message = login(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill all fields")
    
    with tab2:
        with st.form("register_form"):
            st.subheader("Create New Account")
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pass")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                if not all([name, email, password, confirm_password]):
                    st.warning("Please fill all fields")
                elif password != confirm_password:
                    st.error("Passwords don't match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, message = register(name, email, password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    st.stop()

# ============= MAIN APP (After Authentication) =============

# Header with user info
col_title, col_user = st.columns([3, 1])
with col_title:
    st.title("📸 SnapSort - AI Screenshot Organizer")
with col_user:
    st.write(f"👤 **{st.session_state.user['name']}**")
    if st.button("🚪 Logout", use_container_width=True):
        logout()

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Google Drive Integration
    st.subheader("☁️ Google Drive")
    if st.session_state.user.get('googleDriveConnected'):
        st.success("✅ Connected")
        
        if st.button("📂 Fetch Screenshots from Drive", use_container_width=True):
            with st.spinner("Fetching from Google Drive..."):
                files = fetch_drive_screenshots()
                st.session_state.drive_files = files
                if files:
                    st.success(f"Found {len(files)} images!")
        
        if st.button("🔌 Disconnect Drive", use_container_width=True):
            try:
                requests.post(f"{API_URL}/drive/disconnect")
                st.success("Disconnected!")
                st.rerun()
            except:
                st.error("Failed to disconnect")
    else:
        if st.button("🔗 Connect Google Drive", use_container_width=True):
            auth_url = get_drive_auth_url()
            if auth_url:
                st.markdown(f"[Click here to authorize]({auth_url})")
                st.info("After authorizing, refresh this page")
    
    st.markdown("---")
    
    # Tags configuration
    st.subheader("🏷️ Define Your Tags")
    st.caption("Categories for organizing screenshots")
    
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
    st.info("💡 Unmatched images will be auto-clustered intelligently!")
    
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

# Main content area
tab1, tab2 = st.tabs(["📤 Upload Files", "☁️ Google Drive Files"])

with tab1:
    st.subheader("📤 Upload Screenshots")
    uploaded_files = st.file_uploader(
        "Choose screenshot images",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        key="local_upload"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} images uploaded!")
        
        # Preview
        with st.expander("🖼️ Preview Uploaded Images", expanded=True):
            cols = st.columns(4)
            for idx, file in enumerate(uploaded_files):
                with cols[idx % 4]:
                    image = Image.open(file)
                    st.image(image, caption=file.name, use_container_width=True)

with tab2:
    if st.session_state.drive_files:
        st.subheader(f"☁️ Google Drive Screenshots ({len(st.session_state.drive_files)})")
        
        # File selection
        selected_files = []
        
        cols = st.columns(4)
        for idx, file in enumerate(st.session_state.drive_files):
            with cols[idx % 4]:
                if 'thumbnailLink' in file:
                    st.image(file['thumbnailLink'], use_container_width=True)
                
                if st.checkbox(file['name'], key=f"drive_{file['id']}"):
                    selected_files.append(file)
        
        if selected_files:
            st.info(f"✅ {len(selected_files)} files selected")
            
            if st.button("⬇️ Download Selected Files", type="primary"):
                with st.spinner("Downloading files..."):
                    downloaded_files = []
                    for file in selected_files:
                        file_data, file_name = download_drive_file(file['id'], file['name'])
                        if file_data:
                            downloaded_files.append({
                                'name': file_name,
                                'data': file_data
                            })
                    
                    if downloaded_files:
                        st.session_state.drive_downloaded = downloaded_files
                        st.success(f"✅ Downloaded {len(downloaded_files)} files!")
    else:
        st.info("👆 Click 'Fetch Screenshots from Drive' in sidebar to load files")

# Status display
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📁 Local Files", len(uploaded_files) if uploaded_files else 0)

with col2:
    st.metric("☁️ Drive Downloaded", len(st.session_state.drive_downloaded))

with col3:
    st.metric("🏷️ Tags Defined", len(user_tags))

# Processing section
all_files_to_process = []
if uploaded_files:
    all_files_to_process.extend(uploaded_files)
if st.session_state.drive_downloaded:
    for df in st.session_state.drive_downloaded:
        all_files_to_process.append(df)

if all_files_to_process and user_tags:
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🔍 Step 1: Extract Text", type="primary", use_container_width=True):
            with st.spinner("🔍 Extracting text using OCR..."):
                
                st.session_state.extracted_data = {}
                st.session_state.organized_results = None
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, file_obj in enumerate(all_files_to_process):
                    # Handle both uploaded files and drive downloads
                    if isinstance(file_obj, dict):
                        file_name = file_obj['name']
                        file_data = file_obj['data']
                    else:
                        file_name = file_obj.name
                        file_data = file_obj
                    
                    status_text.text(f"Processing {file_name}...")
                    
                    # Reset file pointer if needed
                    if hasattr(file_data, 'seek'):
                        file_data.seek(0)
                    
                    extracted_text = st.session_state.ocr_processor.extract_text(file_data)
                    
                    st.session_state.extracted_data[file_name] = {
                        'text': extracted_text,
                        'file': file_data
                    }
                    
                    progress_bar.progress((idx + 1) / len(all_files_to_process))
                
                status_text.text("✅ Text extraction complete!")
                st.success("✅ Ready for Step 2!")
    
    with col_btn2:
        if st.session_state.extracted_data and st.button("🤖 Step 2: AI Organize", type="secondary", use_container_width=True):
            with st.spinner("🤖 Using enhanced AI to organize screenshots..."):
                
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
                if hasattr(data['file'], 'seek'):
                    data['file'].seek(0)
                image = Image.open(data['file'])
                st.image(image, use_container_width=True)
            
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
                        if hasattr(data['file'], 'seek'):
                            data['file'].seek(0)
                        image = Image.open(data['file'])
                        st.image(image, caption=filename, use_container_width=True)
                        
                        score = results['scores'][filename]
                        screenshot_type = results['types'].get(filename, 'unknown')
                        
                        st.caption(f"📊 Match: {score:.2%}")
                        st.caption(f"🔖 Type: {screenshot_type}")
        else:
            st.info(f"📁 {tag}: No matches found")
    
    # Display auto-clustered with intelligent grouping
    if results['clustered']:
        st.markdown("### 🔮 Intelligent Auto-Clustering")
        st.caption("Screenshots grouped by content similarity and type detection")
        
        for cluster_name, filenames in results['clustered'].items():
            with st.expander(f"📦 {cluster_name} ({len(filenames)} images)", expanded=True):
                cols = st.columns(3)
                for idx, filename in enumerate(filenames):
                    with cols[idx % 3]:
                        data = st.session_state.extracted_data[filename]
                        if hasattr(data['file'], 'seek'):
                            data['file'].seek(0)
                        image = Image.open(data['file'])
                        st.image(image, caption=filename, use_container_width=True)
                        
                        screenshot_type = results['types'].get(filename, 'unknown')
                        st.caption(f"🔖 Type: {screenshot_type}")
    
    st.markdown("---")
    st.success("🎉 Organization complete! You can now download or further process these files.")
    
    # Export options
    st.markdown("### 📥 Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export Report (JSON)", use_container_width=True):
            report = {
                'total_files': len(st.session_state.extracted_data),
                'matched': {k: v for k, v in results['matched'].items()},
                'clustered': results['clustered'],
                'types': results['types'],
                'scores': results['scores']
            }
            st.download_button(
                "⬇️ Download JSON Report",
                data=json.dumps(report, indent=2),
                file_name="snapsort_report.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        st.info("💡 Tip: Download organized folders feature coming soon!")

elif user_tags and not all_files_to_process:
    st.info("📤 Please upload files or select from Google Drive to begin organizing")

elif all_files_to_process and not user_tags:
    st.warning("🏷️ Please define at least one tag in the sidebar to organize screenshots")

# Footer
st.markdown("---")
st.caption("🔒 Your data is secure and processed locally. Made with ❤️ using Streamlit & AI")