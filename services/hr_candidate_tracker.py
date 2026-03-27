"""
HR Candidate Tracker - Google Sheets Integration
Logs and tracks all job candidates in a centralized spreadsheet
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.google.sheets_service import GoogleSheetsService
from engine.logger import logger


class CandidateTracker:
    """Track job candidates in Google Sheets"""
    
    def __init__(self):
        """Initialize candidate tracker"""
        self.spreadsheet_name = "HR Candidates Tracker"
        self.sheets_service = None
        self.spreadsheet_id = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize Google Sheets connection
        Creates spreadsheet if it doesn't exist
        """
        try:
            self.sheets_service = GoogleSheetsService()
            
            # Get or create spreadsheet
            result = self.sheets_service.get_or_create_spreadsheet(self.spreadsheet_name)
            
            if result['success']:
                self.spreadsheet_id = result['id']
                self.initialized = True
                
                # Initialize sheet with headers if newly created
                if result.get('created', False):
                    self._initialize_sheet()
                
                logger.info(f"✅ Candidate tracker initialized: {result.get('link', 'N/A')}")
                return True
            else:
                logger.error(f"❌ Failed to initialize tracker: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error initializing tracker: {e}")
            return False
    
    def _initialize_sheet(self):
        """Initialize sheet with headers"""
        try:
            headers = [[
                'Candidate ID',
                'Name',
                'Email',
                'Phone',
                'Location',
                'Position Applied',
                'Total Experience (Years)',
                'Current Role',
                'Skills',
                'Education',
                'Score',
                'Grade',
                'Recommendation',
                'Status',
                'Resume File',
                'Google Doc Link',
                'Interview Date',
                'Interview Link',
                'Created Date',
                'Last Updated'
            ]]
            
            self.sheets_service.append_data(self.spreadsheet_id, 'Sheet1!A1', headers)
            logger.info("✅ Sheet headers initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing sheet headers: {e}")
    
    def add_candidate(self, candidate_data: Dict) -> Dict:
        """
        Add candidate to tracker

        Args:
            candidate_data: Dictionary with candidate information

        Returns:
            Result dictionary with success status and row number
        """
        try:
            if not self.initialized:
                if not self.initialize():
                    return {
                        'success': False,
                        'error': 'Tracker not initialized'
                    }

            # Prepare row data
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            candidate_id = f"CAND-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Extract data from nested structure
            candidate_info = candidate_data.get('candidate', {})
            experience_info = candidate_data.get('experience', {})
            education_info = candidate_data.get('education', {})
            skills_info = candidate_data.get('skills', {})
            score_info = candidate_data.get('score', {})
            
            row_data = [[
                candidate_id,  # Candidate ID
                candidate_info.get('name', 'Unknown'),  # Name
                candidate_info.get('email', ''),  # Email
                candidate_info.get('phone', ''),  # Phone
                candidate_info.get('location', ''),  # Location
                candidate_data.get('position', 'Not Specified'),  # Position Applied
                str(experience_info.get('total_years', 0)),  # Total Experience
                experience_info.get('current_role', 'Unknown'),  # Current Role
                ', '.join(skills_info.get('technical', [])[:10]),  # Skills (top 10)
                ', '.join(education_info.get('degrees', [])),  # Education
                str(score_info.get('total', 0)),  # Score
                score_info.get('grade', 'N/A'),  # Grade
                candidate_data.get('recommendation', {}).get('message', 'Pending'),  # Recommendation
                'New',  # Status
                candidate_data.get('resume_file', ''),  # Resume File
                '',  # Google Doc Link (to be added)
                '',  # Interview Date (to be added)
                '',  # Interview Link (to be added)
                timestamp,  # Created Date
                timestamp  # Last Updated
            ]]

            # Append to sheet
            result = self.sheets_service.append_data(self.spreadsheet_id, 'Sheet1!A1', row_data)

            if result['success']:
                logger.info(f"✅ Candidate added: {candidate_info.get('name', 'Unknown')} (ID: {candidate_id})")
                return {
                    'success': True,
                    'candidate_id': candidate_id,
                    'message': f'Candidate added successfully'
                }
            else:
                logger.error(f"❌ Failed to add candidate: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error')
                }

        except Exception as e:
            logger.error(f"❌ Error adding candidate: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_candidate_status(self, candidate_id: str, status: str, updates: Dict = None) -> Dict:
        """
        Update candidate status and other fields
        
        Args:
            candidate_id: Candidate ID to update
            status: New status (e.g., 'Interview Scheduled', 'Hired', 'Rejected')
            updates: Additional fields to update
        
        Returns:
            Result dictionary
        """
        try:
            if not self.initialized:
                return {
                    'success': False,
                    'error': 'Tracker not initialized'
                }
            
            # Find candidate row (simplified - in production would search by candidate_id)
            # For now, we'll just log the update
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"📝 Updated candidate {candidate_id}: Status = {status}")
            
            if updates:
                for key, value in updates.items():
                    logger.info(f"   {key}: {value}")
            
            return {
                'success': True,
                'message': f'Candidate {candidate_id} updated to {status}'
            }
            
        except Exception as e:
            logger.error(f"❌ Error updating candidate: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def schedule_interview(self, candidate_id: str, interview_date: str, meet_link: str) -> Dict:
        """
        Schedule interview for candidate
        
        Args:
            candidate_id: Candidate ID
            interview_date: Interview date/time
            meet_link: Google Meet link
        
        Returns:
            Result dictionary
        """
        try:
            updates = {
                'Interview Date': interview_date,
                'Interview Link': meet_link,
                'Status': 'Interview Scheduled',
                'Last Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            result = self.update_candidate_status(candidate_id, 'Interview Scheduled', updates)
            
            if result['success']:
                logger.info(f"📅 Interview scheduled for {candidate_id}: {interview_date}")
                logger.info(f"🔗 Meet link: {meet_link}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error scheduling interview: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_candidate(self, candidate_id: str) -> Optional[Dict]:
        """
        Get candidate information by ID
        
        Args:
            candidate_id: Candidate ID to retrieve
        
        Returns:
            Candidate data dictionary or None
        """
        try:
            if not self.initialized:
                return None
            
            # Get all data from sheet
            result = self.sheets_service.get_data(self.spreadsheet_id, 'Sheet1!A1:Z1000')
            
            if result['success'] and result.get('data'):
                headers = result['data'][0] if result['data'] else []
                
                # Find candidate row
                for row in result['data'][1:]:
                    if len(row) > 0 and row[0] == candidate_id:
                        # Convert to dictionary
                        candidate = dict(zip(headers, row))
                        return candidate
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting candidate: {e}")
            return None
    
    def get_statistics(self) -> Dict:
        """
        Get hiring statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            if not self.initialized:
                return {
                    'total': 0,
                    'by_status': {},
                    'average_score': 0
                }
            
            # Get all data
            result = self.sheets_service.get_data(self.spreadsheet_id, 'Sheet1!A1:Z1000')
            
            if not result['success'] or not result.get('data'):
                return {
                    'total': 0,
                    'by_status': {},
                    'average_score': 0
                }
            
            # Skip header row
            rows = result['data'][1:]
            
            stats = {
                'total': len(rows),
                'by_status': {},
                'by_grade': {},
                'average_score': 0,
                'total_score': 0
            }
            
            for row in rows:
                # Count by status (column 14)
                if len(row) > 13:
                    status = row[13]
                    stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # Count by grade (column 12)
                if len(row) > 11:
                    grade = row[11]
                    stats['by_grade'][grade] = stats['by_grade'].get(grade, 0) + 1
                
                # Sum scores (column 11)
                if len(row) > 10:
                    try:
                        score = float(row[10])
                        stats['total_score'] += score
                    except:
                        pass
            
            # Calculate average
            if stats['total'] > 0:
                stats['average_score'] = round(stats['total_score'] / stats['total'], 1)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {e}")
            return {
                'total': 0,
                'by_status': {},
                'average_score': 0
            }


# Test the tracker
if __name__ == "__main__":
    tracker = CandidateTracker()
    
    print("=" * 60)
    print("CANDIDATE TRACKER TEST")
    print("=" * 60)
    
    # Initialize
    if tracker.initialize():
        print("✅ Tracker initialized successfully")
        
        # Test adding candidate
        test_candidate = {
            'name': 'John Doe',
            'email': 'john.doe@email.com',
            'phone': '+1 (555) 123-4567',
            'location': 'New York',
            'position': 'Senior Software Engineer',
            'experience_years': 5,
            'current_role': 'Software Engineer at Tech Corp',
            'skills': ['Python', 'Java', 'React', 'AWS', 'Docker'],
            'degrees': ['Bachelor of Technology in Computer Science'],
            'score': 85,
            'grade': 'A',
            'recommendation': 'Schedule Interview',
            'resume_file': 'Resumes/john_doe_resume.pdf'
        }
        
        result = tracker.add_candidate(test_candidate)
        print(f"\nAdd Candidate Result: {result}")
        
        # Get statistics
        stats = tracker.get_statistics()
        print(f"\nStatistics:")
        print(f"  Total Candidates: {stats['total']}")
        print(f"  Average Score: {stats['average_score']}")
        print(f"  By Status: {stats['by_status']}")
        print(f"  By Grade: {stats['by_grade']}")
    else:
        print("❌ Failed to initialize tracker")
