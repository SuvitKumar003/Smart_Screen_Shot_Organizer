# utils/gdrive_manager.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import os
from PIL import Image
import streamlit as st

class GoogleDriveManager:
    """
    Manages Google Drive integration for SnapSort AI
    - Authenticate with Google Drive
    - Read screenshots from Drive folders
    - Organize and write back to Drive
    """
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    def authenticate(self, client_secrets_file='credentials.json'):
        """
        Authenticate with Google Drive using OAuth2
        
        Args:
            client_secrets_file: Path to OAuth2 credentials JSON
            
        Returns:
            bool: True if authentication successful
        """
        try:
            # Check if we have stored credentials in session state
            if 'gdrive_credentials' in st.session_state:
                creds_dict = st.session_state.gdrive_credentials
                self.credentials = Credentials.from_authorized_user_info(creds_dict, self.SCOPES)
            else:
                # New authentication flow
                flow = Flow.from_client_secrets_file(
                    client_secrets_file,
                    scopes=self.SCOPES,
                    redirect_uri='http://localhost:8501'
                )
                
                # Generate authorization URL
                auth_url, _ = flow.authorization_url(prompt='consent')
                
                return False, auth_url  # Need user to authorize
            
            # Build service
            self.service = build('drive', 'v3', credentials=self.credentials)
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def complete_authentication(self, authorization_response):
        """
        Complete OAuth flow with authorization code
        
        Args:
            authorization_response: Full callback URL with code
        """
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=self.SCOPES,
            redirect_uri='http://localhost:8501'
        )
        
        flow.fetch_token(authorization_response=authorization_response)
        self.credentials = flow.credentials
        
        # Store in session state
        st.session_state.gdrive_credentials = {
            'token': self.credentials.token,
            'refresh_token': self.credentials.refresh_token,
            'token_uri': self.credentials.token_uri,
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
            'scopes': self.credentials.scopes
        }
        
        self.service = build('drive', 'v3', credentials=self.credentials)
        return True
    
    def list_folders(self, parent_folder_id=None):
        """
        List all folders in Google Drive
        
        Args:
            parent_folder_id: Optional parent folder to list from
            
        Returns:
            list: List of folder dictionaries with id and name
        """
        try:
            query = "mimeType='application/vnd.google-apps.folder'"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            query += " and trashed=false"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=100
            ).execute()
            
            folders = results.get('files', [])
            return folders
            
        except Exception as e:
            st.error(f"Error listing folders: {str(e)}")
            return []
    
    def get_images_from_folder(self, folder_id):
        """
        Get all image files from a specific folder
        
        Args:
            folder_id: Google Drive folder ID
            
        Returns:
            list: List of image file dictionaries
        """
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            query += " and (mimeType contains 'image/')"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, size, createdTime)',
                pageSize=1000
            ).execute()
            
            images = results.get('files', [])
            return images
            
        except Exception as e:
            st.error(f"Error fetching images: {str(e)}")
            return []
    
    def download_image(self, file_id):
        """
        Download an image file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            PIL.Image or None
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_bytes = io.BytesIO()
            downloader = MediaIoBaseDownload(file_bytes, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_bytes.seek(0)
            image = Image.open(file_bytes)
            return image
            
        except Exception as e:
            st.error(f"Error downloading image: {str(e)}")
            return None
    
    def create_folder(self, folder_name, parent_folder_id=None):
        """
        Create a new folder in Google Drive
        
        Args:
            folder_name: Name of folder to create
            parent_folder_id: Optional parent folder ID
            
        Returns:
            str: New folder ID or None
        """
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except Exception as e:
            st.error(f"Error creating folder: {str(e)}")
            return None
    
    def move_file_to_folder(self, file_id, destination_folder_id):
        """
        Move a file to a different folder
        
        Args:
            file_id: File to move
            destination_folder_id: Destination folder ID
            
        Returns:
            bool: Success status
        """
        try:
            # Get current parents
            file = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()
            
            previous_parents = ",".join(file.get('parents', []))
            
            # Move file
            self.service.files().update(
                fileId=file_id,
                addParents=destination_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            return True
            
        except Exception as e:
            st.error(f"Error moving file: {str(e)}")
            return False
    
    def copy_file_to_folder(self, file_id, destination_folder_id, new_name=None):
        """
        Copy a file to a different folder
        
        Args:
            file_id: File to copy
            destination_folder_id: Destination folder ID
            new_name: Optional new name for copied file
            
        Returns:
            str: New file ID or None
        """
        try:
            body = {'parents': [destination_folder_id]}
            if new_name:
                body['name'] = new_name
            
            copied_file = self.service.files().copy(
                fileId=file_id,
                body=body
            ).execute()
            
            return copied_file.get('id')
            
        except Exception as e:
            st.error(f"Error copying file: {str(e)}")
            return None
    
    def organize_folder_by_categories(self, source_folder_id, organized_results, 
                                     create_subfolders=True, copy_not_move=False):
        """
        Organize files in a Google Drive folder based on clustering results
        
        Args:
            source_folder_id: Source folder containing screenshots
            organized_results: Results from clustering engine
            create_subfolders: Create subfolders for each category
            copy_not_move: Copy files instead of moving them
            
        Returns:
            dict: Organization statistics
        """
        stats = {
            'total_processed': 0,
            'successfully_organized': 0,
            'failed': 0,
            'categories_created': []
        }
        
        try:
            # Get all images from source folder
            images = self.get_images_from_folder(source_folder_id)
            file_id_map = {img['name']: img['id'] for img in images}
            
            # Create folders for matched categories
            for category, filenames in organized_results['matched'].items():
                if not filenames:
                    continue
                
                if create_subfolders:
                    category_folder_id = self.create_folder(
                        category,
                        parent_folder_id=source_folder_id
                    )
                    
                    if not category_folder_id:
                        continue
                    
                    stats['categories_created'].append(category)
                    
                    # Move/copy files to category folder
                    for filename in filenames:
                        if filename in file_id_map:
                            file_id = file_id_map[filename]
                            
                            if copy_not_move:
                                success = self.copy_file_to_folder(
                                    file_id,
                                    category_folder_id
                                )
                            else:
                                success = self.move_file_to_folder(
                                    file_id,
                                    category_folder_id
                                )
                            
                            if success:
                                stats['successfully_organized'] += 1
                            else:
                                stats['failed'] += 1
                            
                            stats['total_processed'] += 1
            
            # Create folders for clustered groups
            if organized_results['clustered']:
                clusters_folder_id = self.create_folder(
                    "Auto-Clustered",
                    parent_folder_id=source_folder_id
                )
                
                for cluster_name, filenames in organized_results['clustered'].items():
                    cluster_folder_id = self.create_folder(
                        cluster_name,
                        parent_folder_id=clusters_folder_id
                    )
                    
                    if not cluster_folder_id:
                        continue
                    
                    stats['categories_created'].append(cluster_name)
                    
                    for filename in filenames:
                        if filename in file_id_map:
                            file_id = file_id_map[filename]
                            
                            if copy_not_move:
                                success = self.copy_file_to_folder(
                                    file_id,
                                    cluster_folder_id
                                )
                            else:
                                success = self.move_file_to_folder(
                                    file_id,
                                    cluster_folder_id
                                )
                            
                            if success:
                                stats['successfully_organized'] += 1
                            else:
                                stats['failed'] += 1
                            
                            stats['total_processed'] += 1
            
            return stats
            
        except Exception as e:
            st.error(f"Error organizing folder: {str(e)}")
            return stats