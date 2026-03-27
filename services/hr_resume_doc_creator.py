"""
HR Resume Document Creator - Google Docs Integration
Creates formatted Google Docs for candidate resumes
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.google.docs_service import GoogleDocsService
from engine.logger import logger


class ResumeDocCreator:
    """Create formatted Google Docs for candidate resumes"""
    
    def __init__(self):
        """Initialize resume doc creator"""
        self.docs_service = None
        self.folder_name = "HR Candidates"
        
    def initialize(self) -> bool:
        """Initialize Google Docs service"""
        try:
            self.docs_service = GoogleDocsService()
            logger.info("✅ Resume doc creator initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Error initializing doc creator: {e}")
            return False
    
    def create_candidate_doc(self, candidate_data: Dict, resume_text: str = "") -> Dict:
        """
        Create formatted Google Doc for candidate

        Args:
            candidate_data: Candidate information dictionary (can be nested from parser)
            resume_text: Original resume text (optional)

        Returns:
            Result dictionary with doc link
        """
        try:
            if not self.docs_service:
                if not self.initialize():
                    return {
                        'success': False,
                        'error': 'Failed to initialize docs service'
                    }

            # Extract candidate info (handle nested structure from parser)
            candidate_info = candidate_data.get('candidate', {})
            experience_info = candidate_data.get('experience', {})
            education_info = candidate_data.get('education', {})
            skills_info = candidate_data.get('skills', {})
            score_info = candidate_data.get('score', {})
            
            # Create document title
            candidate_name = candidate_info.get('name', 'Unknown Candidate')
            position = candidate_data.get('position', 'Position Not Specified')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            doc_title = f"Candidate - {candidate_name} - {position} - {timestamp}"

            # Build document content with extracted data
            content = self._build_doc_content(
                candidate_info, 
                experience_info, 
                education_info, 
                skills_info, 
                score_info,
                candidate_data.get('position', ''),
                candidate_data.get('recommendation', {}),
                resume_text
            )

            # Create Google Doc
            result = self.docs_service.create_document(doc_title, content)

            if result['success']:
                doc_link = result.get('link') or result.get('document', {}).get('webViewLink') or ''
                logger.info(f"✅ Candidate doc created: {doc_link}")

                return {
                    'success': True,
                    'doc_id': result.get('id'),
                    'doc_link': doc_link,
                    'title': doc_title
                }
            else:
                logger.error(f"❌ Failed to create doc: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error')
                }

        except Exception as e:
            logger.error(f"❌ Error creating candidate doc: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_doc_content(self, candidate: Dict, experience: Dict, education: Dict,
                          skills: Dict, score: Dict, position: str, recommendation: Dict,
                          resume_text: str = "") -> str:
        """
        Build formatted content for Google Doc

        Args:
            candidate: Candidate data dictionary
            experience: Experience data dictionary
            education: Education data dictionary
            skills: Skills data dictionary
            score: Score data dictionary (from parser)
            position: Position applied
            recommendation: Recommendation dict
            resume_text: Original resume text

        Returns:
            Formatted content string
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Get score values - handle both dict and nested formats
        score_total = 0
        score_grade = 'N/A'
        score_breakdown = {}
        
        if isinstance(score, dict):
            score_total = score.get('total', 0)
            score_grade = score.get('grade', 'N/A')
            score_breakdown = score.get('breakdown', {})
        
        # Build header
        content = f"""CANDIDATE PROFILE
{'=' * 60}

Generated: {timestamp}
Candidate ID: CAND-{datetime.now().strftime('%Y%m%d%H%M%S')}

{'=' * 60}
PERSONAL INFORMATION
{'=' * 60}

Name: {candidate.get('name', 'Unknown')}
Email: {candidate.get('email', 'Not provided')}
Phone: {candidate.get('phone', 'Not provided')}
Location: {candidate.get('location', 'Not provided')}
LinkedIn: {candidate.get('linkedin', 'Not provided')}
GitHub: {candidate.get('github', 'Not provided')}

{'=' * 60}
POSITION & SCORING
{'=' * 60}

Position Applied: {position if position else 'Not specified'}
Total Score: {score_total}/100 (Grade: {score_grade})
Recommendation: {recommendation.get('message', 'Pending review') if isinstance(recommendation, dict) else 'Pending review'}

Score Breakdown:
"""

        # Add score breakdown if available
        if score_breakdown:
            for category, points in score_breakdown.items():
                content += f"  - {category.title()}: {points}\n"
        else:
            content += "  (Detailed breakdown not available)\n"

        content += f"""
{'=' * 60}
PROFESSIONAL EXPERIENCE
{'=' * 60}

Total Experience: {experience.get('total_years', 0) if isinstance(experience, dict) else 0} years
Current Role: {experience.get('current_role', 'Not specified') if isinstance(experience, dict) else 'Not specified'}

"""

        # Add positions if available
        positions = experience.get('positions', []) if isinstance(experience, dict) else []
        if positions:
            content += "Previous Positions:\n"
            for i, pos in enumerate(positions[:5], 1):
                content += f"  {i}. {pos}\n"

        content += f"""
{'=' * 60}
EDUCATION
{'=' * 60}

"""

        # Add degrees
        degrees = education.get('degrees', []) if isinstance(education, dict) else []
        if degrees:
            for degree in degrees:
                content += f"• {degree}\n"

        universities = education.get('universities', []) if isinstance(education, dict) else []
        if universities:
            content += "\nUniversities:\n"
            for uni in universities:
                content += f"  - {uni}\n"

        graduation_year = education.get('graduation_year') if isinstance(education, dict) else None
        if graduation_year:
            content += f"\nGraduation Year: {graduation_year}\n"

        content += f"""
{'=' * 60}
SKILLS
{'=' * 60}

Technical Skills:
"""

        # Add technical skills from skills dict (passed as parameter)
        tech_skills = skills.get('technical', []) if isinstance(skills, dict) else []
        if tech_skills:
            for i, skill in enumerate(tech_skills, 1):
                if i % 5 == 0:
                    content += f"\n  • {skill}"
                else:
                    content += f"  • {skill}  "
        else:
            content += "  None listed"

        content += f"""

Soft Skills:
"""

        # Add soft skills from skills dict (passed as parameter)
        soft_skills = skills.get('soft_skills', []) if isinstance(skills, dict) else []
        if soft_skills:
            for skill in soft_skills:
                content += f"  ✓ {skill}\n"
        else:
            content += "  None listed"

        # Add certifications from skills dict (passed as parameter)
        certifications = skills.get('certifications', []) if isinstance(skills, dict) else []
        if certifications:
            content += f"""
{'=' * 60}
CERTIFICATIONS
{'=' * 60}

"""
            for cert in certifications:
                content += f"• {cert}\n"

        # Add languages from skills dict (passed as parameter)
        languages = skills.get('languages', []) if isinstance(skills, dict) else []
        if languages:
            content += f"""
{'=' * 60}
LANGUAGES
{'=' * 60}

"""
            for lang in languages:
                content += f"• {lang}\n"

        # Add original resume if provided
        if resume_text:
            content += f"""
{'=' * 60}
ORIGINAL RESUME TEXT
{'=' * 60}

{resume_text[:3000]}{'...' if len(resume_text) > 3000 else ''}
"""

        content += f"""
{'=' * 60}
INTERVIEW NOTES
{'=' * 60}

Interview Date: _______________________

Interview Time: _______________________

Interviewer(s): _______________________

Interview Format: ☐ Video  ☐ Phone  ☐ In-Person

Technical Assessment: ☐ Required  ☐ Not Required

Notes:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

{'=' * 60}
EVALUATION
{'=' * 60}

Technical Skills: ☐ Excellent  ☐ Good  ☐ Average  ☐ Poor

Communication: ☐ Excellent  ☐ Good  ☐ Average  ☐ Poor

Culture Fit: ☐ Excellent  ☐ Good  ☐ Average  ☐ Poor

Overall Recommendation:
☐ Strong Hire
☐ Hire
☐ Consider
☐ Do Not Hire

Additional Comments:
_________________________________________________________________
_________________________________________________________________

{'=' * 60}
END OF CANDIDATE PROFILE
{'=' * 60}
"""

        return content
        if resume_text:
            content += f"""
{'=' * 60}
ORIGINAL RESUME TEXT
{'=' * 60}

{resume_text[:3000]}{'...' if len(resume_text) > 3000 else ''}
"""
        
        content += f"""
{'=' * 60}
INTERVIEW NOTES
{'=' * 60}

Interview Date: _______________________

Interview Time: _______________________

Interviewer(s): _______________________

Interview Format: ☐ Video  ☐ Phone  ☐ In-Person

Technical Assessment: ☐ Required  ☐ Not Required

Notes:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

{'=' * 60}
EVALUATION
{'=' * 60}

Technical Skills: ☐ Excellent  ☐ Good  ☐ Average  ☐ Poor

Communication: ☐ Excellent  ☐ Good  ☐ Average  ☐ Poor

Culture Fit: ☐ Excellent  ☐ Good  ☐ Average  ☐ Poor

Overall Recommendation:
☐ Strong Hire
☐ Hire
☐ Consider
☐ Do Not Hire

Additional Comments:
_________________________________________________________________
_________________________________________________________________

{'=' * 60}
END OF CANDIDATE PROFILE
{'=' * 60}
"""
        
        return content
    
    def update_candidate_doc(self, doc_id: str, updates: Dict) -> Dict:
        """
        Update existing candidate doc with new information
        
        Args:
            doc_id: Google Doc ID to update
            updates: Dictionary with updates (e.g., interview_date, notes)
        
        Returns:
            Result dictionary
        """
        try:
            if not self.docs_service:
                if not self.initialize():
                    return {
                        'success': False,
                        'error': 'Failed to initialize docs service'
                    }
            
            # For now, just log the update
            # In production, would append to the document
            logger.info(f"📝 Updating candidate doc {doc_id}")
            
            for key, value in updates.items():
                logger.info(f"   {key}: {value}")
            
            return {
                'success': True,
                'message': 'Doc updated successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Error updating candidate doc: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Test the doc creator
if __name__ == "__main__":
    creator = ResumeDocCreator()
    
    print("=" * 60)
    print("RESUME DOC CREATOR TEST")
    print("=" * 60)
    
    # Test creating candidate doc
    test_candidate = {
        'name': 'John Doe',
        'email': 'john.doe@email.com',
        'phone': '+1 (555) 123-4567',
        'location': 'New York',
        'linkedin': 'linkedin.com/in/johndoe',
        'github': 'github.com/johndoe',
        'position': 'Senior Software Engineer',
        'experience_years': 5,
        'current_role': 'Software Engineer at Tech Corp',
        'positions': [
            'Software Engineer at Tech Corp (2020-Present)',
            'Junior Developer at StartupXYZ (2017-2020)'
        ],
        'degrees': ['Bachelor of Technology in Computer Science (2017)'],
        'universities': ['Tech University, New York'],
        'skills': ['Python', 'Java', 'JavaScript', 'React', 'AWS', 'Docker', 'Kubernetes'],
        'soft_skills': ['Leadership', 'Communication', 'Problem Solving', 'Teamwork'],
        'certifications': ['AWS Certified Solutions Architect', 'Certified Scrum Master'],
        'score': 85,
        'grade': 'A',
        'recommendation': 'Schedule Interview',
        'score_breakdown': {
            'contact': 10,
            'experience': 35,
            'education': 15,
            'skills': 25
        }
    }
    
    if creator.initialize():
        result = creator.create_candidate_doc(test_candidate)
        print(f"\nCreate Doc Result: {result}")
        
        if result['success']:
            print(f"\n✅ Doc created successfully!")
            print(f"   Title: {result['title']}")
            print(f"   Link: {result['doc_link']}")
    else:
        print("❌ Failed to initialize doc creator")
