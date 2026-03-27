"""
Google Sheets Service
Create and manage Google Spreadsheets
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
from pathlib import Path

class GoogleSheetsService:
    def __init__(self, token_path='token.json'):
        """Initialize Google Sheets service"""
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
        
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    def list_spreadsheets(self):
        """List all spreadsheets in Google Drive"""
        try:
            results = self.drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=100,
                fields="files(id, name, webViewLink)"
            ).execute()
            
            spreadsheets = results.get('files', [])
            
            return {
                'success': True,
                'spreadsheets': spreadsheets
            }
            
        except Exception as e:
            # If Drive API fails, return empty list
            return {
                'success': False,
                'error': str(e),
                'spreadsheets': []
            }

    def get_or_create_spreadsheet(self, title):
        """Get spreadsheet by title or create if doesn't exist"""
        # First try to find existing spreadsheet
        result = self.list_spreadsheets()
        
        if result.get('success') and result.get('spreadsheets'):
            for spreadsheet in result['spreadsheets']:
                if spreadsheet.get('name') == title:
                    return {
                        'success': True,
                        'id': spreadsheet['id'],
                        'title': spreadsheet['name'],
                        'link': spreadsheet.get('webViewLink', ''),
                        'created': False
                    }
        
        # Create new spreadsheet if not found
        return self.create_spreadsheet(title)

    def create_spreadsheet(self, title, data=None):
        """Create Google Sheet with optional data"""
        try:
            spreadsheet = self.service.spreadsheets().create(
                body={
                    'properties': {
                        'title': title
                    }
                }
            ).execute()
            
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            
            # Add headers if creating new sheet
            headers = [['Ticket ID', 'Email', 'Subject', 'Category', 'Priority', 'Created', 'Status', 'Doc Link']]
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='A1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()
            
            # Add data if provided
            if data:
                self.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range='A2',
                    valueInputOption='RAW',
                    body={'values': data}
                ).execute()
            
            return {
                'success': True,
                'id': spreadsheet_id,
                'title': spreadsheet.get('properties', {}).get('title'),
                'link': spreadsheet.get('spreadsheetUrl'),
                'created': True
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def append_data(self, spreadsheet_id, range_name, values):
        """Append data to sheet"""
        try:
            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': values}
            ).execute()
            
            return {
                'success': True,
                'message': 'Data appended successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_data(self, spreadsheet_id, range_name='Sheet1!A1:Z100'):
        """Get data from sheet"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            return {
                'success': True,
                'data': values
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
