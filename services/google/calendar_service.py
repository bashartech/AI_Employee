"""
Google Calendar Service
Create and manage calendar events with Google Meet integration
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

# Add parent directory for logger import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from engine.logger import logger

class GoogleCalendarService:
    def __init__(self, token_path='token.json'):
        """Initialize Google Calendar service"""
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
        
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    def create_event(self, summary, description, start_time, end_time, attendees=None, timezone='Asia/Karachi'):
        """
        Create calendar event with Google Meet link

        Args:
            summary: Event title
            description: Event description
            start_time: datetime object or ISO string
            end_time: datetime object or ISO string
            attendees: List of email addresses
            timezone: Timezone (default: Asia/Karachi)

        Returns:
            dict with event details including Meet link
        """
        # Parse datetime strings to datetime objects
        if isinstance(start_time, str):
            # Try multiple formats
            for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M%z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
                try:
                    # Remove timezone suffix for parsing
                    clean_start = start_time.replace('+05:00', '').replace('Z', '').replace('+00:00', '')
                    start_dt = datetime.strptime(clean_start, fmt.replace('%z', '').replace('T', ' ').strip())
                    break
                except:
                    continue
            else:
                # If all formats fail, try simple parse
                clean_start = start_time.replace('T', ' ').replace('+05:00', '').replace('Z', '').replace('+00:00', '')
                start_dt = datetime.strptime(clean_start[:16], '%Y-%m-%d %H:%M')
            start_time = start_dt
        elif isinstance(start_time, (int, float)):
            start_time = datetime.fromtimestamp(start_time)
        
        if isinstance(end_time, str):
            for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M%z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
                try:
                    clean_end = end_time.replace('+05:00', '').replace('Z', '').replace('+00:00', '')
                    end_dt = datetime.strptime(clean_end, fmt.replace('%z', '').replace('T', ' ').strip())
                    break
                except:
                    continue
            else:
                clean_end = end_time.replace('T', ' ').replace('+05:00', '').replace('Z', '').replace('+00:00', '')
                end_dt = datetime.strptime(clean_end[:16], '%Y-%m-%d %H:%M')
            end_time = end_dt
        elif isinstance(end_time, (int, float)):
            end_time = datetime.fromtimestamp(end_time)

        # Format for Google Calendar API (ISO 8601 with timezone)
        start_iso = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_iso = end_time.strftime('%Y-%m-%dT%H:%M:%S')

        # Build event object
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_iso,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_iso,
                'timeZone': timezone,
            },
        }
        
        # Add attendees only if provided (avoid empty array issues)
        if attendees:
            attendee_list = [{'email': email.strip()} for email in attendees if email.strip()]
            if attendee_list:
                event['attendees'] = attendee_list

        # Add Google Meet conference data
        event['conferenceData'] = {
            'createRequest': {
                'requestId': f'meet-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        }

        try:
            logger.info(f"Creating calendar event: {summary}")
            logger.info(f"Start: {start_iso}, End: {end_iso}")
            logger.info(f"Timezone: {timezone}")
            logger.info(f"Full event object: {json.dumps(event, indent=2)}")

            # Create event with conference data
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1  # Required for Meet link generation
            ).execute()

            # Extract Meet link from conference data
            meet_link = None
            if 'conferenceData' in created_event:
                entry_points = created_event['conferenceData'].get('entryPoints', [])
                if entry_points:
                    meet_link = entry_points[0].get('uri')
                # Fallback: try meetingLink field
                if not meet_link:
                    meet_link = created_event['conferenceData'].get('meetingLink')

            logger.info(f"Event created successfully: {created_event.get('htmlLink')}")
            logger.info(f"Meet link: {meet_link}")

            return {
                'success': True,
                'id': created_event.get('id'),
                'html_link': created_event.get('htmlLink'),
                'meet_link': meet_link,
                'conference_data': created_event.get('conferenceData'),
                'status': created_event.get('status')
            }

        except Exception as e:
            logger.error(f"Calendar event creation failed: {str(e)}")
            logger.error(f"Error details: {repr(e)}")
            if hasattr(e, 'content'):
                logger.error(f"Error content: {e.content}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_upcoming_events(self, days=7, max_results=10):
        """Get upcoming events"""
        now = datetime.utcnow()
        end = now + timedelta(days=days)
        
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=end.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format events
            formatted_events = []
            for event in events:
                formatted_events.append({
                    'id': event.get('id'),
                    'summary': event.get('summary'),
                    'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date')),
                    'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date')),
                    'attendees': [a.get('email') for a in event.get('attendees', [])],
                    'meet_link': event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri')
                })
            
            return {
                'success': True,
                'events': formatted_events
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
