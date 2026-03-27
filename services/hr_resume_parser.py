"""
HR Resume Parser Service
Extracts candidate information from resumes/CVs
Supports: .txt, .md, .pdf, .docx (Word)
"""
import re
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Try to import PDF and DOCX libraries
PDF_SUPPORT = False
PDF_LIB = None
DOCX_SUPPORT = False

try:
    import pdfplumber
    PDF_SUPPORT = True
    PDF_LIB = 'pdfplumber'
    print("✅ Using pdfplumber for PDF parsing (better extraction)")
except ImportError:
    try:
        import PyPDF2
        PDF_SUPPORT = True
        PDF_LIB = 'PyPDF2'
        print("✅ Using PyPDF2 for PDF parsing")
    except ImportError:
        print("⚠️  No PDF library available. Install with: pip install pdfplumber")

try:
    from docx import Document
    DOCX_SUPPORT = True
    print("✅ DOCX support enabled (Word documents)")
except ImportError:
    print("⚠️  DOCX support not available. Install with: pip install python-docx")

class ResumeParser:
    """Parse and extract information from resumes/CVs"""

    def __init__(self):
        """Initialize resume parser"""
        # Common skill keywords
        self.tech_skills = {
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'fastapi', 'next.js', 'nuxt.js'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd', 'devops'],
            'data': ['machine learning', 'data science', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'ai'],
            'mobile': ['ios', 'android', 'react native', 'flutter', 'swift', 'kotlin'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'project management', 'agile', 'scrum']
        }

        # Job title keywords
        self.job_levels = {
            'junior': ['junior', 'jr', 'entry level', 'associate', 'intern'],
            'mid': ['mid', 'middle', 'senior associate'],
            'senior': ['senior', 'sr', 'lead', 'principal'],
            'management': ['manager', 'director', 'head', 'vp', 'chief', 'cto', 'ceo']
        }

    def parse_file(self, file_path: Path) -> Dict:
        """
        Parse resume file (supports .txt, .md, .pdf, .docx, images)

        Args:
            file_path: Path to resume file

        Returns:
            Dictionary with extracted candidate information
        """
        try:
            # Check file extension
            file_ext = file_path.suffix.lower()

            if file_ext == '.pdf':
                if not PDF_SUPPORT:
                    return {
                        'success': False,
                        'error': 'PDF support not available. Install pdfplumber: pip install pdfplumber',
                        'file': str(file_path)
                    }
                # Parse PDF
                text = self._extract_text_from_pdf(file_path)

                # If PDF extraction failed, try to get filename clues
                if not text or len(text.strip()) < 10:
                    logger_text = f"⚠️  PDF text extraction returned empty/short result ({len(text.strip())} chars)"
                    print(f"  {logger_text}")
                    print(f"  💡 This might be an image-based PDF (scanned document)")
                    print(f"  💡 Trying OCR...")
                    
                    # Try OCR for image-based PDF
                    from services.hr_ocr_parser import OCRParser
                    ocr_parser = OCRParser()
                    
                    if ocr_parser.is_image_based_pdf(file_path):
                        print(f"  📷 Detected image-based PDF, using OCR")
                        ocr_result = ocr_parser.parse_file(file_path)
                        
                        if ocr_result.get('success'):
                            text = ocr_result['text']
                            print(f"  ✅ OCR extracted {len(text)} characters")
                        else:
                            print(f"  ⚠️  OCR failed: {ocr_result.get('error')}")
                            text = f"Resume File: {file_path.name}"
                    else:
                        text = f"Resume File: {file_path.name}"
            
            elif file_ext in ['.docx', '.doc']:
                if not DOCX_SUPPORT:
                    return {
                        'success': False,
                        'error': 'DOCX support not available. Install with: pip install python-docx',
                        'file': str(file_path)
                    }
                # Parse Word document
                text = self._extract_text_from_docx(file_path)
                
                if not text or len(text.strip()) < 10:
                    print(f"  ⚠️  DOCX extraction returned empty/short result")
                    text = f"Resume File: {file_path.name}"
            
            elif file_ext in ['.txt', '.md']:
                # Parse text/markdown
                text = file_path.read_text(encoding='utf-8')
            
            elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
                # Image file - use OCR
                print(f"  📷 Image file detected, using OCR: {file_path.name}")
                from services.hr_ocr_parser import OCRParser
                ocr_parser = OCRParser()
                
                ocr_result = ocr_parser.parse_file(file_path)
                
                if ocr_result.get('success'):
                    text = ocr_result['text']
                    print(f"  ✅ OCR extracted {len(text)} characters from image")
                else:
                    return {
                        'success': False,
                        'error': f'OCR failed: {ocr_result.get("error")}',
                        'file': str(file_path)
                    }
            
            else:
                # Try to read as text for unknown extensions
                try:
                    text = file_path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    return {
                        'success': False,
                        'error': f'Unsupported file format: {file_ext}. Please use PDF, DOCX, TXT, or image files',
                        'file': str(file_path)
                    }

            return self.parse_text(text, str(file_path))

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file': str(file_path)
            }

    def _extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from Word document (.docx)"""
        try:
            doc = Document(file_path)

            # Extract all paragraphs
            paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]

            # Join paragraphs with newlines
            text = '\n\n'.join(paragraphs)

            print(f"  📄 DOCX extracted: {len(text)} characters from {len(paragraphs)} paragraphs")
            return text

        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")

    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file using pdfplumber (preferred) or PyPDF2"""
        try:
            text_parts = []

            if PDF_LIB == 'pdfplumber':
                # Use pdfplumber (better extraction)
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"--- Page {page_num + 1} ---\n")
                            text_parts.append(page_text)
            elif PDF_LIB == 'PyPDF2':
                # Fallback to PyPDF2
                import PyPDF2
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"--- Page {page_num + 1} ---\n")
                            text_parts.append(page_text)

            result = '\n'.join(text_parts)
            print(f"  📄 PDF extracted: {len(result)} characters")
            return result

        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

            result = '\n'.join(text_parts)
            print(f"  📄 PDF extracted: {len(result)} characters")
            return result

        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def parse_text(self, text: str, source: str = "Unknown") -> Dict:
        """
        Parse resume text content - Uses ROBUST parser for OCR text
        
        Args:
            text: Resume text content
            source: Source file path or email
        
        Returns:
            Dictionary with extracted information
        """
        try:
            # Use ROBUST parser for OCR text (handles formatting issues better)
            from services.hr_robust_ocr_parser import RobustOCRParser
            robust_parser = RobustOCRParser()
            
            # Parse with robust parser
            robust_result = robust_parser.parse_resume(text)
            
            if robust_result.get('success'):
                # Convert to standard format
                return {
                    'success': True,
                    'source': source,
                    'parsed_at': datetime.now().isoformat(),
                    'candidate': robust_result['candidate'],
                    'experience': robust_result['experience'],
                    'education': robust_result['education'],
                    'skills': robust_result['skills'],
                    'score': robust_result['score'],
                    'recommendation': self._get_recommendation(
                        robust_result['score'],
                        robust_result['experience'],
                        robust_result['skills']
                    ),
                    'raw_text': text[:1000]
                }
            else:
                # Fallback to basic parser
                return self._parse_text_basic(text, source)
                
        except Exception as e:
            # Fallback to basic parser on error
            return self._parse_text_basic(text, source)
    
    def _parse_text_basic(self, text: str, source: str) -> Dict:
        """Basic text parsing fallback"""
        try:
            # Preprocess OCR text - clean up common OCR artifacts
            text = self._preprocess_ocr_text(text)
            
            # Extract basic information
            candidate_info = {
                'name': self._extract_name(text),
                'email': self._extract_email(text),
                'phone': self._extract_phone(text),
                'location': self._extract_location(text),
                'linkedin': self._extract_linkedin(text),
                'github': self._extract_github(text),
                'website': self._extract_website(text)
            }

            # Extract experience
            experience = {
                'total_years': self._extract_total_experience(text),
                'positions': self._extract_positions(text),
                'companies': self._extract_companies(text),
                'current_role': self._extract_current_role(text)
            }

            # Extract education
            education = {
                'degrees': self._extract_degrees(text),
                'universities': self._extract_universities(text),
                'graduation_year': self._extract_graduation_year(text)
            }

            # Extract skills
            skills = {
                'technical': self._extract_skills(text, 'technical'),
                'soft_skills': self._extract_skills(text, 'soft'),
                'certifications': self._extract_certifications(text),
                'languages': self._extract_languages(text)
            }

            # Calculate candidate score
            score = self._calculate_score(candidate_info, experience, education, skills)

            # Determine recommendation
            recommendation = self._get_recommendation(score, experience, skills)

            return {
                'success': True,
                'source': source,
                'parsed_at': datetime.now().isoformat(),
                'candidate': candidate_info,
                'experience': experience,
                'education': education,
                'skills': skills,
                'score': score,
                'recommendation': recommendation,
                'raw_text': text[:1000]
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': source
            }
    
    def _preprocess_ocr_text(self, text: str) -> str:
        """
        Clean up OCR text artifacts
        
        Args:
            text: Raw OCR text
        
        Returns:
            Cleaned text
        """
        import re
        
        # Fix common OCR mistakes
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'([a-z])\s*([A-Z])', r'\1 \2', text)  # Fix broken words
        text = re.sub(r'(\w)\s*-\s*(\w)', r'\1-\2', text)  # Fix hyphenated words
        
        # Fix common OCR character substitutions
        replacements = {
            '0': 'O',  # Zero to O (in names)
            '1': 'l',  # One to l (in names)
            '3': 'B',  # Three to B (in names)
            '5': 'S',  # Five to S (in names)
        }
        
        # Be careful with replacements - only in certain contexts
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Only fix obvious OCR errors in skill lists
            if any(keyword in line.lower() for keyword in ['skill', 'experience', 'education']):
                line = line.replace('0', 'O').replace('1', 'l')
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name"""
        # Look for name patterns (usually at the beginning)
        lines = text.split('\n')
        if lines:
            first_line = lines[0].strip()
            # Check if it looks like a name (all caps or proper case, no special chars)
            if first_line and len(first_line) > 3 and len(first_line) < 50:
                # Skip lines with URLs, emails, or special formatting
                if not any(x in first_line.lower() for x in ['http', 'www.', '@', 'linkedin', 'github']):
                    # Check if it's mostly letters and spaces
                    if sum(c.isalpha() or c.isspace() for c in first_line) > len(first_line) * 0.7:
                        return first_line

        # Try to find name pattern (all caps name at start)
        name_pattern = r'^([A-Z][A-Z\s]+)$'
        match = re.search(name_pattern, text[:500], re.MULTILINE)
        if match:
            return match.group(1).strip().title()
        
        # Fallback: look for proper name pattern
        name_pattern = r'([A-Z][a-z]+\s+[A-Z][A-Z\s]+[a-z]+)'
        match = re.search(name_pattern, text[:500])
        if match:
            return match.group(1)

        return "Unknown"
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_patterns = [
            r'\+?[\d\s-]{10,}',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
            r'\d{3}[-.]?\d{3}[-.]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        
        return ""
    
    def _extract_location(self, text: str) -> str:
        """Extract location/city"""
        location_keywords = ['new york', 'san francisco', 'boston', 'seattle', 'chicago', 'austin', 'los angeles', 'remote']
        text_lower = text.lower()
        
        for location in location_keywords:
            if location in text_lower:
                return location.title()
        
        return ""
    
    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn URL"""
        linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9_-]+'
        match = re.search(linkedin_pattern, text, re.IGNORECASE)
        return f"https://{match.group(0)}" if match else ""
    
    def _extract_github(self, text: str) -> str:
        """Extract GitHub URL"""
        github_pattern = r'github\.com/[a-zA-Z0-9_-]+'
        match = re.search(github_pattern, text, re.IGNORECASE)
        return f"https://{match.group(0)}" if match else ""
    
    def _extract_website(self, text: str) -> str:
        """Extract personal website/portfolio"""
        website_pattern = r'(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.(com|io|dev|me|org)(?:/[a-zA-Z0-9_-]*)*'
        match = re.search(website_pattern, text, re.IGNORECASE)
        if match:
            url = match.group(0)
            if not url.startswith('http'):
                url = 'https://' + url
            return url
        return ""
    
    def _extract_total_experience(self, text: str) -> float:
        """Extract total years of experience"""
        # Look for patterns like "5 years", "5+ years", "5 yrs"
        exp_patterns = [
            r'(\d+[.\d]?)\s*(?:\+?)\s*(?:years?|yrs?|years of experience)',
            r'(\d+[.\d]?)\s*(?:\+?)\s*years? of experience'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        # Estimate from graduation year
        grad_year = self._extract_graduation_year(text)
        if grad_year:
            current_year = datetime.now().year
            return max(0, current_year - grad_year - 4)  # Assuming 4 years college
        
        return 0.0
    
    def _extract_positions(self, text: str) -> List[str]:
        """Extract job positions/roles"""
        positions = []
        
        # Look for common position patterns
        position_keywords = ['engineer', 'developer', 'designer', 'manager', 'analyst', 'scientist', 'architect', 'consultant']
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in position_keywords):
                # Clean up the line
                position = line.strip()
                if len(position) < 100 and position not in positions:
                    positions.append(position)
        
        return positions[:5]  # Top 5 positions
    
    def _extract_companies(self, text: str) -> List[str]:
        """Extract company names"""
        companies = []
        
        # Common company indicators
        company_keywords = ['inc', 'ltd', 'llc', 'corp', 'corporation', 'technologies', 'solutions', 'systems', 'labs']
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in company_keywords):
                company = line.strip()
                if len(company) < 100 and company not in companies:
                    companies.append(company)
        
        return companies[:5]  # Top 5 companies
    
    def _extract_current_role(self, text: str) -> str:
        """Extract current/most recent role"""
        positions = self._extract_positions(text)
        return positions[0] if positions else "Unknown"
    
    def _extract_degrees(self, text: str) -> List[str]:
        """Extract degrees/qualifications"""
        degrees = []
        degree_keywords = ['bachelor', 'master', 'phd', 'mba', 'bs', 'ms', 'b.tech', 'm.tech', 'be', 'me', 'diploma']
        
        text_lower = text.lower()
        for keyword in degree_keywords:
            if keyword in text_lower:
                # Find the full degree mention
                pattern = rf'({keyword}[^\n\.]*)'
                match = re.search(pattern, text_lower)
                if match:
                    degree = match.group(1).strip().title()
                    if degree not in degrees:
                        degrees.append(degree)
        
        return degrees
    
    def _extract_universities(self, text: str) -> List[str]:
        """Extract university/college names"""
        universities = []
        uni_keywords = ['university', 'college', 'institute', 'school']
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in uni_keywords):
                uni = line.strip()
                if len(uni) < 100 and uni not in universities:
                    universities.append(uni)
        
        return universities[:3]  # Top 3
    
    def _extract_graduation_year(self, text: str) -> Optional[int]:
        """Extract graduation year"""
        year_pattern = r'(?:graduation|graduated|class of)\s*[:\-]?\s*(\d{4})'
        match = re.search(year_pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Look for 4-digit years near education keywords
        edu_year_pattern = r'(?:\d{4})\s*[-–]\s*(\d{4})'
        matches = re.findall(edu_year_pattern, text)
        if matches:
            return int(matches[-1])  # Most recent end year
        
        return None
    
    def _extract_skills(self, text: str, skill_type: str = 'technical') -> List[str]:
        """Extract skills from resume"""
        found_skills = []
        text_lower = text.lower()
        
        if skill_type == 'technical':
            for category, skills in self.tech_skills.items():
                if category != 'soft_skills':
                    for skill in skills:
                        if skill in text_lower:
                            found_skills.append(skill.title())
        elif skill_type == 'soft':
            for skill in self.tech_skills['soft_skills']:
                if skill in text_lower:
                    found_skills.append(skill.title())
        
        return list(set(found_skills))  # Remove duplicates
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certs = []
        cert_keywords = ['certified', 'certification', 'certificate', 'aws', 'azure', 'gcp', 'pmp', 'scrum', 'cisa', 'cissp']
        
        text_lower = text.lower()
        for keyword in cert_keywords:
            if keyword in text_lower:
                # Find certification mention
                pattern = rf'({keyword}[^\n\.]*)'
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    cert = match.group(1).strip().title()
                    if cert not in certs:
                        certs.append(cert)
        
        return certs[:5]  # Top 5
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages spoken"""
        languages = []
        lang_keywords = ['english', 'spanish', 'french', 'german', 'mandarin', 'hindi', 'arabic', 'portuguese', 'japanese']
        
        text_lower = text.lower()
        for lang in lang_keywords:
            if lang in text_lower:
                languages.append(lang.title())
        
        return languages if languages else ['English']  # Default to English
    
    def _calculate_score(self, candidate: Dict, experience: Dict, education: Dict, skills: Dict) -> Dict:
        """
        Calculate candidate score (0-100)
        
        Returns:
            Dictionary with score breakdown
        """
        score = 0
        breakdown = {}
        
        # Email/Contact (10 points)
        if candidate.get('email'):
            score += 5
        if candidate.get('phone'):
            score += 3
        if candidate.get('linkedin'):
            score += 2
        breakdown['contact'] = score
        
        # Experience (40 points)
        exp_years = experience.get('total_years', 0)
        if exp_years >= 10:
            exp_score = 40
        elif exp_years >= 5:
            exp_score = 30
        elif exp_years >= 3:
            exp_score = 20
        elif exp_years >= 1:
            exp_score = 10
        else:
            exp_score = 0
        score += exp_score
        breakdown['experience'] = exp_score
        
        # Education (20 points)
        degrees = education.get('degrees', [])
        if any('phd' in d.lower() for d in degrees):
            edu_score = 20
        elif any('master' in d.lower() or 'mba' in d.lower() for d in degrees):
            edu_score = 15
        elif any('bachelor' in d.lower() or 'b.tech' in d.lower() for d in degrees):
            edu_score = 10
        else:
            edu_score = 5
        score += edu_score
        breakdown['education'] = edu_score
        
        # Skills (30 points)
        tech_skills = len(skills.get('technical', []))
        soft_skills = len(skills.get('soft_skills', []))
        
        skill_score = min(tech_skills * 3, 25) + min(soft_skills * 5, 5)
        score += skill_score
        breakdown['skills'] = skill_score
        
        return {
            'total': min(score, 100),
            'breakdown': breakdown,
            'grade': self._get_grade(min(score, 100))
        }
    
    def _get_grade(self, score: int) -> str:
        """Convert score to grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C'
        else:
            return 'D'
    
    def _get_recommendation(self, score: Dict, experience: Dict, skills: Dict) -> Dict:
        """
        Get hiring recommendation based on score
        
        Returns:
            Dictionary with recommendation details
        """
        total_score = score.get('total', 0)
        
        if total_score >= 80:
            return {
                'action': 'interview',
                'priority': 'high',
                'message': 'Excellent candidate - Schedule interview immediately',
                'auto_approve': False  # Still needs human approval
            }
        elif total_score >= 60:
            return {
                'action': 'review',
                'priority': 'normal',
                'message': 'Good candidate - Review and consider for interview',
                'auto_approve': False
            }
        else:
            return {
                'action': 'reject',
                'priority': 'low',
                'message': 'Does not meet minimum requirements',
                'auto_approve': False
            }


# Test the parser
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Sample resume text
    sample_resume = """
JOHN DOE
john.doe@email.com
+1 (555) 123-4567
New York

EXPERIENCE
Senior Software Engineer at Tech Corp (2020-Present)
- Led development of microservices architecture
- Managed team of 5 developers
- Implemented CI/CD pipelines using Jenkins and Docker

Software Engineer at StartupXYZ (2017-2020)
- Developed REST APIs using Python and Django
- Built responsive web applications with React

EDUCATION
Bachelor of Technology in Computer Science
Graduation: 2017

SKILLS
Python, Java, JavaScript, React, Django, AWS, Docker, Kubernetes, SQL, MongoDB
Leadership, Communication, Problem Solving

CERTIFICATIONS
AWS Certified Solutions Architect
Certified Scrum Master
"""
    
    result = parser.parse_text(sample_resume, "Test Resume")
    
    print("=" * 60)
    print("RESUME PARSER TEST")
    print("=" * 60)
    print(f"\nCandidate: {result['candidate']['name']}")
    print(f"Email: {result['candidate']['email']}")
    print(f"Phone: {result['candidate']['phone']}")
    print(f"Location: {result['candidate']['location']}")
    print(f"\nExperience: {result['experience']['total_years']} years")
    print(f"Current Role: {result['experience']['current_role']}")
    print(f"\nEducation: {result['education']['degrees']}")
    print(f"\nSkills: {result['skills']['technical'][:5]}...")
    print(f"\nScore: {result['score']['total']}/100 (Grade: {result['score']['grade']})")
    print(f"Recommendation: {result['recommendation']['message']}")
    print(f"\nPDF Support: {'✅ Enabled' if PDF_SUPPORT else '❌ Disabled'}")
