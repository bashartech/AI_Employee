"""
Google Docs Service
Create and manage Google Documents
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
from pathlib import Path
import re

class GoogleDocsService:
    def __init__(self, token_path='token.json'):
        """Initialize Google Docs service"""
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

        self.service = build('docs', 'v1', credentials=self.creds)

    def create_document(self, title, content):
        """Create Google Doc with content"""
        try:
            # Create document
            doc = self.service.documents().create(
                body={'title': title}
            ).execute()

            doc_id = doc.get('documentId')

            # Insert content
            if content:
                self.service.documents().batchUpdate(
                    documentId=doc_id,
                    body={
                        'requests': [{
                            'insertText': {
                                'location': {'index': 1},
                                'text': content
                            }
                        }]
                    }
                ).execute()

            # Get document link
            doc_info = self.service.documents().get(documentId=doc_id).execute()

            return {
                'success': True,
                'id': doc_id,
                'title': doc_info.get('title'),
                'link': doc_info.get('webViewLink')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_document_content(self, doc_id):
        """
        Get full content of a Google Doc by ID
        
        Args:
            doc_id: Google Document ID
        
        Returns:
            dict with success status and content
        """
        try:
            # Get document with full content
            document = self.service.documents().get(
                documentId=doc_id
            ).execute()
            
            # Extract text from document structure
            content = []
            body_content = document.get('body', {}).get('content', [])
            
            for element in body_content:
                if 'paragraph' in element:
                    for run in element['paragraph'].get('elements', []):
                        if 'textRun' in run:
                            content.append(run['textRun'].get('content', ''))
            
            full_text = ''.join(content)
            
            return {
                'success': True,
                'content': full_text,
                'title': document.get('title', 'Untitled')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to fetch document: {str(e)}'
            }
    
    def fetch_from_url(self, doc_url):
        """
        Fetch Google Doc content from URL
        
        Args:
            doc_url: Google Docs URL (e.g., https://docs.google.com/document/d/DOC_ID/edit)
        
        Returns:
            dict with success status and content
        """
        try:
            # Extract doc ID from URL
            # Pattern: https://docs.google.com/document/d/DOC_ID/edit or /view
            doc_id_match = re.search(r'/document/d/([a-zA-Z0-9_-]+)', doc_url)
            
            if not doc_id_match:
                return {
                    'success': False,
                    'error': 'Invalid Google Docs URL - could not extract document ID'
                }
            
            doc_id = doc_id_match.group(1)
            
            # Fetch document content
            result = self.get_document_content(doc_id)
            
            if result['success']:
                return {
                    'success': True,
                    'content': result['content'],
                    'title': result.get('title', 'Untitled'),
                    'doc_id': doc_id,
                    'source': f'Google Docs: {doc_url}'
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to fetch Google Doc: {str(e)}'
            }

    def append_to_document(self, doc_id, content):
        """Append content to existing document"""
        try:
            self.service.documents().batchUpdate(
                documentId=doc_id,
                body={
                    'requests': [{
                        'insertText': {
                            'location': {'index': 1},
                            'text': f'\n\n{content}'
                        }
                    }]
                }
            ).execute()
            
            return {
                'success': True,
                'message': 'Content appended successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_document(self, doc_id):
        """Get document info"""
        try:
            doc = self.service.documents().get(documentId=doc_id).execute()
            
            return {
                'success': True,
                'id': doc.get('documentId'),
                'title': doc.get('title'),
                'link': doc.get('webViewLink'),
                'content': doc.get('body', {}).get('content', [])
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
