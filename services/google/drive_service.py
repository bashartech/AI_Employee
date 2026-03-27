"""
Google Drive Service
Manage files and folders in Google Drive
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json
import os
from pathlib import Path

class GoogleDriveService:
    def __init__(self, token_path='token.json'):
        """Initialize Google Drive service"""
        # Load credentials from token.json
        token_file = Path(token_path)
        if not token_file.exists():
            token_file = Path(__file__).parent.parent.parent / token_path
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        self.creds = Credentials(
            token=token_data['token'],
            refresh_token=token_data['refresh_token'],
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )
        
        self.service = build('drive', 'v3', credentials=self.creds)
    
    def create_folder(self, name, parent_id=None):
        """Create folder in Drive"""
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        try:
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            return {
                'success': True,
                'id': folder.get('id'),
                'name': folder.get('name'),
                'link': folder.get('webViewLink')
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_file(self, file_path, name=None, parent_id=None, mime_type=None):
        """Upload file to Drive"""
        if not name:
            name = os.path.basename(file_path)
        
        file_metadata = {'name': name}
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        # Determine MIME type
        if not mime_type:
            mime_type = self._get_mime_type(file_path)
        
        try:
            media = MediaFileUpload(file_path, mimetype=mime_type)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            return {
                'success': True,
                'id': file.get('id'),
                'name': file.get('name'),
                'link': file.get('webViewLink')
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_mime_type(self, file_path):
        """Get MIME type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def move_file_to_folder(self, file_id, folder_id):
        """Move file to folder"""
        try:
            self.service.files().update(
                fileId=file_id,
                addParents=folder_id,
                removeParents='root',
                fields='id, parents'
            ).execute()
            
            return {
                'success': True,
                'message': 'File moved successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_folder_by_name(self, folder_name):
        """Get folder ID by name"""
        try:
            results = self.service.files().list(
                q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'",
                fields="files(id, name, webViewLink)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                return {
                    'success': True,
                    'id': folders[0].get('id'),
                    'name': folders[0].get('name'),
                    'link': folders[0].get('webViewLink')
                }
            else:
                return {
                    'success': False,
                    'error': 'Folder not found'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
