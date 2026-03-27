"""
HR Resume Handler - Multi-Format Support
Handles resumes from:
- Email body text
- PDF attachments
- Word documents (.docx)
- Google Docs links
"""
from pathlib import Path
from typing import Dict, Optional, List
import re
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.hr_resume_parser import ResumeParser
from engine.logger import logger


class ResumeHandler:
    """Handle resumes from multiple sources and formats"""
    
    def __init__(self):
        """Initialize resume handler"""
        self.parser = ResumeParser()
    
    def extract_from_email(self, email_content: str, attachments: List = None) -> Dict:
        """
        Extract resume from email (body + attachments)
        
        Args:
            email_content: Full email body text
            attachments: List of attachment file paths
        
        Returns:
            Dictionary with extracted resume data
        """
        try:
            # Priority 1: Try attachments first
            if attachments:
                for attachment_path in attachments:
                    result = self.extract_from_file(attachment_path)
                    if result.get('success'):
                        logger.info(f"✅ Resume extracted from attachment: {attachment_path}")
                        return result
            
            # Priority 2: Try Google Docs link in email body
            google_docs_url = self._extract_google_docs_url(email_content)
            if google_docs_url:
                logger.info(f"📄 Found Google Docs URL: {google_docs_url}")
                # Note: Would need Google Docs API to fetch content
                # For now, fall back to email body
                logger.info("⚠️ Google Docs fetching not implemented, using email body")
            
            # Priority 3: Use email body text
            logger.info("📝 Parsing resume from email body")
            result = self.parser.parse_text(email_content, source="email_body")
            
            if result.get('success'):
                logger.info(f"✅ Resume parsed from email body")
                logger.info(f"   Name: {result.get('candidate', {}).get('name', 'Unknown')}")
                logger.info(f"   Email: {result.get('candidate', {}).get('email', 'N/A')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error extracting resume from email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_from_file(self, file_path: str) -> Dict:
        """
        Extract resume from file (PDF, DOCX, TXT, MD)
        
        Args:
            file_path: Path to resume file
        
        Returns:
            Dictionary with extracted resume data
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            file_ext = file_path.suffix.lower()
            
            # Route to appropriate parser based on file type
            if file_ext == '.pdf':
                return self._parse_pdf(file_path)
            elif file_ext in ['.docx']:
                return self._parse_docx(file_path)
            elif file_ext in ['.txt', '.md']:
                return self._parse_text_file(file_path)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_ext}'
                }
                
        except Exception as e:
            logger.error(f"❌ Error extracting resume from file: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_pdf(self, file_path: Path) -> Dict:
        """Parse PDF resume"""
        try:
            # Use existing parser
            result = self.parser.parse_file(file_path)
            
            if not result.get('success'):
                error_msg = result.get('error', 'Unknown error')
                if 'empty' in error_msg.lower() or 'no text' in error_msg.lower():
                    logger.warning(f"⚠️ PDF appears to be image-based (scanned)")
                    logger.warning(f"💡 OCR not available - please use text-based PDF or Word doc")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'PDF parsing failed: {str(e)}'
            }
    
    def _parse_docx(self, file_path: Path) -> Dict:
        """Parse Word document (.docx) resume"""
        try:
            # Check if python-docx is available
            try:
                from docx import Document
            except ImportError:
                return {
                    'success': False,
                    'error': 'python-docx not installed. Install with: pip install python-docx'
                }
            
            # Extract text from .docx
            doc = Document(file_path)
            
            # Extract all paragraphs
            paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
            
            # Join paragraphs with newlines
            text_content = '\n\n'.join(paragraphs)
            
            if not text_content or len(text_content) < 50:
                return {
                    'success': False,
                    'error': 'No text content found in Word document'
                }
            
            logger.info(f"📄 Extracted {len(text_content)} characters from DOCX")
            
            # Parse the extracted text
            result = self.parser.parse_text(text_content, source=str(file_path))
            
            if result.get('success'):
                logger.info(f"✅ DOCX resume parsed successfully")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'DOCX parsing failed: {str(e)}'
            }
    
    def _parse_text_file(self, file_path: Path) -> Dict:
        """Parse text file (.txt, .md) resume"""
        try:
            text_content = file_path.read_text(encoding='utf-8')
            
            if not text_content or len(text_content) < 50:
                return {
                    'success': False,
                    'error': 'File is empty or too short'
                }
            
            # Parse the text
            result = self.parser.parse_text(text_content, source=str(file_path))
            
            if result.get('success'):
                logger.info(f"✅ Text file resume parsed successfully")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Text file parsing failed: {str(e)}'
            }
    
    def _extract_google_docs_url(self, text: str) -> Optional[str]:
        """Extract Google Docs URL from text"""
        try:
            # Pattern for Google Docs URLs
            pattern = r'https?://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)(?:/edit)?(?:\?[^ ]*)?'
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match:
                doc_id = match.group(1)
                return f'https://docs.google.com/document/d/{doc_id}/edit'
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting Google Docs URL: {e}")
            return None
    
    def detect_resume_format(self, text: str) -> str:
        """
        Detect resume format from text
        
        Args:
            text: Resume text
        
        Returns:
            Format type: 'structured', 'narrative', 'minimal'
        """
        # Check for common resume sections
        sections = [
            'experience', 'education', 'skills', 'summary',
            'objective', 'projects', 'certifications'
        ]
        
        text_lower = text.lower()
        section_count = sum(1 for section in sections if section in text_lower)
        
        if section_count >= 3:
            return 'structured'  # Well-formatted resume
        elif section_count >= 1:
            return 'narrative'  # Some structure
        else:
            return 'minimal'  # Just text
    
    def validate_resume(self, parsed_data: Dict) -> Dict:
        """
        Validate parsed resume data
        
        Args:
            parsed_data: Parsed resume data
        
        Returns:
            Validation result with score and feedback
        """
        try:
            candidate_info = parsed_data.get('candidate', {})
            experience_info = parsed_data.get('experience', {})
            education_info = parsed_data.get('education', {})
            skills_info = parsed_data.get('skills', {})
            
            validation = {
                'valid': True,
                'score': 0,
                'feedback': [],
                'missing': []
            }
            
            # Check for required fields
            if not candidate_info.get('name') or candidate_info.get('name') == 'Unknown':
                validation['missing'].append('Name')
                validation['feedback'].append('❌ Name not found')
            else:
                validation['score'] += 20
                validation['feedback'].append('✅ Name found')
            
            if not candidate_info.get('email'):
                validation['missing'].append('Email')
                validation['feedback'].append('❌ Email not found')
            else:
                validation['score'] += 20
                validation['feedback'].append('✅ Email found')
            
            if not candidate_info.get('phone'):
                validation['missing'].append('Phone')
                validation['feedback'].append('⚠️ Phone not found (recommended)')
            else:
                validation['score'] += 10
                validation['feedback'].append('✅ Phone found')
            
            # Check experience
            if experience_info.get('total_years', 0) > 0:
                validation['score'] += 20
                validation['feedback'].append(f'✅ Experience found ({experience_info["total_years"]} years)')
            else:
                validation['missing'].append('Experience')
                validation['feedback'].append('⚠️ Experience not clearly stated')
            
            # Check education
            if education_info.get('degrees'):
                validation['score'] += 15
                validation['feedback'].append(f'✅ Education found ({len(education_info["degrees"])} degrees)')
            else:
                validation['missing'].append('Education')
                validation['feedback'].append('⚠️ Education not clearly stated')
            
            # Check skills
            tech_skills = skills_info.get('technical', [])
            if tech_skills and len(tech_skills) >= 3:
                validation['score'] += 15
                validation['feedback'].append(f'✅ Skills found ({len(tech_skills)} skills)')
            else:
                validation['missing'].append('Skills')
                validation['feedback'].append('⚠️ Skills not clearly listed')
            
            # Overall assessment
            if validation['score'] >= 80:
                validation['assessment'] = 'Excellent resume - all key information present'
            elif validation['score'] >= 60:
                validation['assessment'] = 'Good resume - some information could be clearer'
            elif validation['score'] >= 40:
                validation['assessment'] = 'Fair resume - missing important information'
            else:
                validation['assessment'] = 'Poor resume - needs significant improvement'
                validation['valid'] = False
            
            return validation
            
        except Exception as e:
            logger.error(f"❌ Error validating resume: {e}")
            return {
                'valid': False,
                'score': 0,
                'feedback': ['Error validating resume'],
                'error': str(e)
            }


# Test the handler
if __name__ == "__main__":
    handler = ResumeHandler()
    
    print("=" * 60)
    print("RESUME HANDLER TEST")
    print("=" * 60)
    
    # Test email body parsing
    test_email = """
MUHAMMAD AHMED KHAN
ahmed.khan.dev@gmail.com
+92 312 3456789

EXPERIENCE
Junior Full Stack Developer at TechNova Solutions

SKILLS
JavaScript, React, Node.js, MongoDB
"""
    
    result = handler.extract_from_email(test_email)
    print(f"\nEmail Body Test: {result.get('success', False)}")
    if result.get('success'):
        print(f"  Name: {result.get('candidate', {}).get('name', 'N/A')}")
        print(f"  Email: {result.get('candidate', {}).get('email', 'N/A')}")
    
    # Test validation
    validation = handler.validate_resume(result)
    print(f"\nValidation Score: {validation.get('score', 0)}/100")
    for feedback in validation.get('feedback', []):
        print(f"  {feedback}")
