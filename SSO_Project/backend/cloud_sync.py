# backend/cloud_sync.py
"""
Simple helper to list and download screenshots from a Google Drive folder.
You must set up OAuth credentials and place credentials.json in the project root.
This is a skeleton - adapt scopes and file filters for your needs.
"""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"

def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    service = build('drive', 'v3', credentials=creds)
    return service

def list_images_in_folder(folder_id, service=None):
    service = service or get_drive_service()
    query = f"'{folder_id}' in parents and mimeType contains 'image/'"
    results = service.files().list(q=query, fields="files(id,name,mimeType,modifiedTime)").execute()
    return results.get('files', [])

def download_file(file_id, dest_path, service=None):
    service = service or get_drive_service()
    request = service.files().get_media(fileId=file_id)
    from googleapiclient.http import MediaIoBaseDownload
    fh = open(dest_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fh.close()
