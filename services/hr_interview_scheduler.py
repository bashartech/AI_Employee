"""
HR Interview Scheduler - Google Calendar Integration
Automatically schedules interviews with Google Meet links
"""
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.google.calendar_service import GoogleCalendarService
from engine.logger import logger


class InterviewScheduler:
    """Schedule interviews with Google Calendar integration"""
    
    def __init__(self):
        """Initialize interview scheduler"""
        self.calendar_service = None
        self.interview_duration_minutes = 45
        self.buffer_minutes = 15
        self.default_timezone = 'America/New_York'
        
        # Default interview time slots (business hours)
        self.interview_slots = [
            "10:00",
            "11:00",
            "14:00",
            "15:00",
            "16:00"
        ]
        
    def initialize(self) -> bool:
        """Initialize Google Calendar service"""
        try:
            self.calendar_service = GoogleCalendarService()
            logger.info("✅ Interview scheduler initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Error initializing scheduler: {e}")
            return False
    
    def schedule_interview(self, candidate_data: Dict, preferred_dates: List[str] = None) -> Dict:
        """
        Schedule interview for candidate

        Args:
            candidate_data: Candidate information dictionary (can be nested from parser)
            preferred_dates: List of preferred date strings (YYYY-MM-DD)

        Returns:
            Result dictionary with meeting details
        """
        try:
            if not self.calendar_service:
                if not self.initialize():
                    return {
                        'success': False,
                        'error': 'Failed to initialize calendar service'
                    }

            # Extract candidate info (handle nested structure from parser)
            candidate_info = candidate_data.get('candidate', {})
            
            # Determine interview date and time
            if preferred_dates:
                # Use first available slot on preferred dates
                interview_datetime = self._find_available_slot(preferred_dates)
            else:
                # Schedule for next available slot (tomorrow or next business day)
                interview_datetime = self._get_next_available_slot()

            if not interview_datetime:
                return {
                    'success': False,
                    'error': 'No available interview slots found'
                }

            # Prepare meeting details
            candidate_name = candidate_info.get('name', 'Unknown Candidate')
            candidate_email = candidate_info.get('email', '')
            position = candidate_data.get('position', 'Position Not Specified')

            meeting_title = f"Interview: {candidate_name} - {position}"
            meeting_description = self._build_meeting_description(candidate_info)

            # Create calendar event with Google Meet
            result = self.calendar_service.create_event(
                summary=meeting_title,
                description=meeting_description,
                start_time=interview_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                end_time=(interview_datetime + timedelta(minutes=self.interview_duration_minutes)).strftime('%Y-%m-%dT%H:%M:%S'),
                attendees=[candidate_email] if candidate_email else []
            )

            if result['success']:
                meet_link = result.get('meet_link', '')
                calendar_link = result.get('html_link', '')

                logger.info(f"📅 Interview scheduled: {interview_datetime}")
                logger.info(f"🔗 Meet link: {meet_link}")
                logger.info(f"📋 Calendar link: {calendar_link}")

                return {
                    'success': True,
                    'interview_datetime': interview_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'meet_link': meet_link,
                    'calendar_link': calendar_link,
                    'event_id': result.get('id'),
                    'candidate_name': candidate_name,
                    'position': position
                }
            else:
                logger.error(f"❌ Failed to schedule interview: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error')
                }

        except Exception as e:
            logger.error(f"❌ Error scheduling interview: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_available_slot(self, preferred_dates: List[str]) -> Optional[datetime]:
        """
        Find first available time slot on preferred dates
        
        Args:
            preferred_dates: List of date strings (YYYY-MM-DD)
        
        Returns:
            datetime object or None
        """
        try:
            for date_str in preferred_dates:
                try:
                    base_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    # Try each time slot
                    for time_str in self.interview_slots:
                        hour, minute = map(int, time_str.split(':'))
                        slot_datetime = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        
                        # Check if slot is in the future
                        if slot_datetime > datetime.now():
                            # In production, would check calendar for conflicts
                            return slot_datetime
                            
                except ValueError:
                    logger.warning(f"Invalid date format: {date_str}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding available slot: {e}")
            return None
    
    def _get_next_available_slot(self, days_ahead: int = 3) -> Optional[datetime]:
        """
        Get next available interview slot
        
        Args:
            days_ahead: How many days to look ahead
        
        Returns:
            datetime object or None
        """
        try:
            # Generate next N business days
            from datetime import timedelta
            
            current_date = datetime.now()
            
            for i in range(1, days_ahead + 1):
                candidate_date = current_date + timedelta(days=i)
                
                # Skip weekends
                if candidate_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    continue
                
                # Try each time slot
                for time_str in self.interview_slots:
                    hour, minute = map(int, time_str.split(':'))
                    slot_datetime = candidate_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    if slot_datetime > datetime.now():
                        return slot_datetime
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting next available slot: {e}")
            return None
    
    def _build_meeting_description(self, candidate_data: Dict) -> str:
        """
        Build Google Meet meeting description
        
        Args:
            candidate_data: Candidate information
        
        Returns:
            Formatted description string
        """
        candidate_name = candidate_data.get('name', 'Unknown')
        position = candidate_data.get('position', 'Position Not Specified')
        email = candidate_data.get('email', '')
        phone = candidate_data.get('phone', '')
        score = candidate_data.get('score', 0)
        grade = candidate_data.get('grade', 'N/A')
        
        description = f"""INTERVIEW DETAILS
{'=' * 60}

Candidate: {candidate_name}
Position: {position}
Email: {email}
Phone: {phone}

{'=' * 60}
CANDIDATE SUMMARY
{'=' * 60}

Score: {score}/100 (Grade: {grade})
Experience: {candidate_data.get('experience_years', 0)} years
Current Role: {candidate_data.get('current_role', 'Not specified')}

Skills: {', '.join(candidate_data.get('skills', [])[:10])}

{'=' * 60}
INTERVIEW GUIDELINES
{'=' * 60}

1. Technical Assessment (20 minutes)
   - Review candidate's technical background
   - Ask about relevant projects
   - Assess problem-solving skills

2. Cultural Fit (15 minutes)
   - Team collaboration experience
   - Communication skills
   - Work style preferences

3. Q&A (10 minutes)
   - Answer candidate's questions
   - Explain next steps

{'=' * 60}
EVALUATION CRITERIA
{'=' * 60}

☐ Technical Skills (1-5)
☐ Problem Solving (1-5)
☐ Communication (1-5)
☐ Culture Fit (1-5)
☐ Overall Recommendation (Hire/No Hire)

{'=' * 60}
NEXT STEPS
{'=' * 60}

After the interview:
1. Submit evaluation form
2. Share feedback with hiring team
3. Schedule follow-up if needed

---
This interview was automatically scheduled by AI Employee Vault HR Automation
"""
        
        return description
    
    def send_interview_invitation(self, candidate_data: Dict, meeting_details: Dict) -> Dict:
        """
        Send interview invitation email to candidate
        
        Args:
            candidate_data: Candidate information
            meeting_details: Meeting details from schedule_interview()
        
        Returns:
            Result dictionary
        """
        try:
            # This would integrate with email sending service
            # For now, just log the invitation
            candidate_name = candidate_data.get('name', 'Candidate')
            candidate_email = candidate_data.get('email', '')
            
            interview_time = meeting_details.get('interview_datetime', '')
            meet_link = meeting_details.get('meet_link', '')
            
            logger.info(f"📧 Interview invitation ready to send to: {candidate_email}")
            logger.info(f"   Candidate: {candidate_name}")
            logger.info(f"   Time: {interview_time}")
            logger.info(f"   Meet Link: {meet_link}")
            
            return {
                'success': True,
                'message': 'Interview invitation prepared',
                'candidate_email': candidate_email,
                'meeting_details': meeting_details
            }
            
        except Exception as e:
            logger.error(f"❌ Error preparing invitation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_interview(self, event_id: str, reason: str = "") -> Dict:
        """
        Cancel scheduled interview
        
        Args:
            event_id: Google Calendar event ID
            reason: Cancellation reason
        
        Returns:
            Result dictionary
        """
        try:
            if not self.calendar_service:
                if not self.initialize():
                    return {
                        'success': False,
                        'error': 'Failed to initialize calendar service'
                    }
            
            # Delete event
            result = self.calendar_service.delete_event(event_id)
            
            if result['success']:
                logger.info(f"❌ Interview cancelled: {event_id}")
                if reason:
                    logger.info(f"   Reason: {reason}")
                
                return {
                    'success': True,
                    'message': 'Interview cancelled successfully'
                }
            else:
                logger.error(f"❌ Failed to cancel interview: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error')
                }
                
        except Exception as e:
            logger.error(f"❌ Error cancelling interview: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Test the scheduler
if __name__ == "__main__":
    scheduler = InterviewScheduler()
    
    print("=" * 60)
    print("INTERVIEW SCHEDULER TEST")
    print("=" * 60)
    
    # Test candidate
    test_candidate = {
        'name': 'John Doe',
        'email': 'john.doe@email.com',
        'phone': '+1 (555) 123-4567',
        'position': 'Senior Software Engineer',
        'experience_years': 5,
        'current_role': 'Software Engineer at Tech Corp',
        'skills': ['Python', 'Java', 'React', 'AWS'],
        'score': 85,
        'grade': 'A'
    }
    
    if scheduler.initialize():
        print("✅ Scheduler initialized")
        
        # Test scheduling
        result = scheduler.schedule_interview(test_candidate)
        print(f"\nSchedule Result: {result}")
        
        if result['success']:
            print(f"\n✅ Interview scheduled successfully!")
            print(f"   Time: {result['interview_datetime']}")
            print(f"   Meet Link: {result['meet_link']}")
            print(f"   Calendar Link: {result['calendar_link']}")
            
            # Test invitation
            invite_result = scheduler.send_interview_invitation(test_candidate, result)
            print(f"\nInvitation Result: {invite_result}")
    else:
        print("❌ Failed to initialize scheduler")
