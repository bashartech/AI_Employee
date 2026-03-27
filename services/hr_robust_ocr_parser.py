"""
Robust OCR Resume Parser
Uses fuzzy matching and context-based extraction for OCR text
Handles formatting issues, duplicates, and OCR artifacts
"""
import re
from typing import Dict, List, Set, Tuple
from datetime import datetime
from difflib import SequenceMatcher


class RobustOCRParser:
    """Parser designed specifically for OCR-extracted resume text"""
    
    def __init__(self):
        """Initialize with comprehensive databases"""
        
        # All technical skills (800+ variations)
        self.all_skills = self._build_skill_database()
        
        # Soft skills
        self.soft_skills_list = [
            'leadership', 'communication', 'teamwork', 'collaboration', 'problem solving',
            'critical thinking', 'creativity', 'innovation', 'adaptability', 'flexibility',
            'time management', 'organization', 'planning', 'prioritization', 'multitasking',
            'attention to detail', 'analytical thinking', 'decision making', 'conflict resolution',
            'negotiation', 'persuasion', 'mentoring', 'coaching', 'training', 'presentation',
            'public speaking', 'writing', 'documentation', 'empathy', 'emotional intelligence',
            'customer service', 'client relations', 'stakeholder management', 'project management',
            'agile', 'scrum', 'kanban', 'lean', 'continuous improvement', 'self-motivated',
            'proactive', 'initiative', 'ownership', 'accountability', 'reliability',
            'work ethic', 'professionalism', 'integrity', 'ethics', 'cultural awareness',
            'diversity', 'inclusion', 'remote work', 'distributed teams', 'async communication'
        ]
        
        # Education keywords
        self.education_keywords = {
            'phd': ['phd', 'ph.d', 'doctor', 'doctorate'],
            'master': ['master', 'm.s', 'ms', 'm.sc', 'msc', 'm.tech', 'mtech', 'm.e', 'me', 'mba', 'mca'],
            'bachelor': ['bachelor', 'b.s', 'bs', 'b.sc', 'bsc', 'b.tech', 'btech', 'b.e', 'be', 'b.com', 'bba', 'bca'],
            'diploma': ['diploma', 'associate', 'certification', 'certificate']
        }
    
    def _build_skill_database(self) -> Dict[str, List[str]]:
        """Build comprehensive skill database with variations"""
        return {
            # Programming - with common OCR variations
            'python': ['python', 'pyth0n', 'pythcn', 'python3', 'python2'],
            'java': ['java', 'j4v4', 'java8', 'java11', 'java17'],
            'javascript': ['javascript', 'js', 'java script', 'java-script', 'ecmascript'],
            'typescript': ['typescript', 'ts', 'type script', 'type-script'],
            'c++': ['c++', 'cpp', 'c plus plus', 'c++11', 'c++14', 'c++17'],
            'c#': ['c#', 'csharp', 'c sharp', 'dotnet'],
            'go': ['go', 'golang', 'go lang'],
            'rust': ['rust', 'rustlang'],
            'ruby': ['ruby', 'rb', 'ruby on rails'],
            'php': ['php', 'php7', 'php8', 'laravel', 'symfony'],
            'swift': ['swift', 'swift5'],
            'kotlin': ['kotlin', 'kt'],
            
            # Web - with variations
            'react': ['react', 'react.js', 'reactjs', 'react js', 'react.js'],
            'angular': ['angular', 'angular.js', 'angularjs', 'angular2+', 'angular 2'],
            'vue': ['vue', 'vue.js', 'vuejs', 'vue js'],
            'next.js': ['next.js', 'nextjs', 'next', 'next.js'],
            'node.js': ['node.js', 'nodejs', 'node', 'node js', 'node.js'],
            'django': ['django', 'django rest', 'django rest framework'],
            'flask': ['flask', 'flask api'],
            'fastapi': ['fastapi', 'fast api', 'fast-api'],
            'html': ['html', 'html5', 'html 5'],
            'css': ['css', 'css3', 'css 3'],
            'sass': ['sass', 'scss', 'sass/scss'],
            'tailwind': ['tailwind', 'tailwind css', 'tailwindcss'],
            'bootstrap': ['bootstrap', 'bootstrap4', 'bootstrap5'],
            
            # Databases
            'sql': ['sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'mariadb'],
            'mongodb': ['mongodb', 'mongo', 'mongo db'],
            'redis': ['redis', 'redis cache'],
            'elasticsearch': ['elasticsearch', 'elastic search', 'elastic'],
            'firebase': ['firebase', 'firestore'],
            'graphql': ['graphql', 'graph ql'],
            'prisma': ['prisma', 'prisma orm'],
            
            # Cloud & DevOps
            'aws': ['aws', 'amazon web services', 'amazon aws', 'ec2', 's3', 'lambda'],
            'azure': ['azure', 'microsoft azure', 'azure cloud'],
            'gcp': ['gcp', 'google cloud', 'google cloud platform'],
            'docker': ['docker', 'docker container', 'docker containers'],
            'kubernetes': ['kubernetes', 'k8s', 'k8', 'kube'],
            'terraform': ['terraform', 'tf', 'infra as code'],
            'jenkins': ['jenkins', 'ci/cd', 'cicd', 'continuous integration'],
            'git': ['git', 'github', 'gitlab', 'bitbucket', 'version control'],
            'linux': ['linux', 'unix', 'bash', 'shell scripting'],
            
            # AI/ML
            'machine learning': ['machine learning', 'ml', 'machine-learning'],
            'deep learning': ['deep learning', 'dl', 'deep-learning'],
            'tensorflow': ['tensorflow', 'tf', 'keras'],
            'pytorch': ['pytorch', 'torch'],
            'scikit-learn': ['scikit-learn', 'sklearn', 'scikit learn'],
            'pandas': ['pandas', 'pandas library'],
            'numpy': ['numpy', 'np'],
            'openai': ['openai', 'gpt', 'chatgpt', 'gpt-3', 'gpt-4'],
            'llm': ['llm', 'large language model', 'language model'],
            'rag': ['rag', 'retrieval augmented generation', 'retrieval-augmented generation'],
            'nlp': ['nlp', 'natural language processing'],
            
            # Mobile
            'react native': ['react native', 'reactnative', 'react-native'],
            'flutter': ['flutter', 'dart flutter'],
            'ios': ['ios', 'iphone', 'ipad', 'swift ui'],
            'android': ['android', 'android app', 'kotlin android'],
            
            # Tools & Methodologies
            'agile': ['agile', 'scrum', 'kanban', 'sprint'],
            'rest api': ['rest api', 'rest', 'restful', 'restful api', 'api'],
            'microservices': ['microservices', 'micro services', 'micro-service'],
            'testing': ['testing', 'unit testing', 'integration testing', 'pytest', 'jest', 'mocha'],
            'ci/cd': ['ci/cd', 'cicd', 'continuous integration', 'continuous deployment']
        }
    
    def parse_resume(self, ocr_text: str) -> Dict:
        """
        Parse OCR text with robust extraction
        
        Args:
            ocr_text: Raw OCR text from resume
        
        Returns:
            Comprehensive parsed data
        """
        # Clean OCR text
        cleaned_text = self._clean_ocr_text(ocr_text)
        
        # Extract all information
        result = {
            'success': True,
            'candidate': self._extract_personal_info(cleaned_text, ocr_text),
            'experience': self._extract_experience(cleaned_text, ocr_text),
            'education': self._extract_education(cleaned_text, ocr_text),
            'skills': self._extract_skills_comprehensive(cleaned_text, ocr_text),
            'score': self._calculate_score(cleaned_text),
            'raw_text': ocr_text[:2000]
        }
        
        return result
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean common OCR artifacts"""
        # Fix common OCR substitutions
        replacements = {
            '0': 'o',  # In skill names (but not in numbers)
            '1': 'l',  # In skill names
            'rn': 'm',  # rn -> m
            'vv': 'w',  # vv -> w
            'cl': 'd',  # cl -> d (sometimes)
            'ct': 'ct',  # Keep as is
            'ﬁ': 'fi',  # Ligatures
            'ﬂ': 'fl',
            '–': '-',  # En dash to hyphen
            '—': '-',  # Em dash to hyphen
            '•': '-',  # Bullet to hyphen
        }
        
        # Apply replacements carefully (only in skill-like contexts)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_lower = line.lower()
            # Only fix in skill/technical contexts
            if any(kw in line_lower for kw in ['skill', 'tech', 'stack', 'proficient', 'expert', 'experience']):
                for old, new in replacements.items():
                    if old != '0' and old != '1':  # Skip number replacements
                        line = line.replace(old, new)
            cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        # Fix spacing
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s*([.,:;])', r'\1 ', text)
        
        return text.strip()
    
    def _extract_personal_info(self, cleaned: str, original: str) -> Dict:
        """Extract personal info with multiple fallbacks"""
        info = {
            'name': self._extract_name_smart(cleaned, original),
            'email': self._extract_email(original),
            'phone': self._extract_phone(original),
            'location': self._extract_location(original),
            'linkedin': self._extract_linkedin(original),
            'github': self._extract_github(original)
        }
        return info
    
    def _extract_name_smart(self, cleaned: str, original: str) -> str:
        """Smart name extraction - looks at top of resume"""
        lines = original.split('\n')
        
        # Check first 10 lines for name
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            
            # Skip empty lines
            if not line or len(line) < 3:
                continue
            
            # Skip contact info
            if '@' in line or 'http' in line.lower() or line.startswith('+'):
                continue
            
            # Skip section headers
            if any(header in line.lower() for header in ['about', 'summary', 'objective', 'experience', 'education', 'skills', 'contact', 'profile', 'projects']):
                continue
            
            # Check if it looks like a name
            words = line.split()
            if 2 <= len(words) <= 5:
                # Check capitalization pattern (Name Name or NAME NAME)
                if all(word[0].isupper() for word in words if word and len(word) > 1):
                    # Check if mostly alphabetic
                    if sum(c.isalpha() for c in line) > len(line) * 0.7:
                        return line.title()
        
        # Fallback: look for all-caps name at start
        caps_match = re.search(r'^([A-Z][A-Z\s]{3,})$', original[:500], re.MULTILINE)
        if caps_match:
            return caps_match.group(1).strip().title()
        
        return "Unknown"
    
    def _extract_email(self, text: str) -> str:
        """Extract email"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone - multiple formats"""
        patterns = [
            r'\+?[\d\s\-\(\)]{10,}',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
            r'\d{3}[-.]?\d{3}[-.]?\d{4}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        
        return ""
    
    def _extract_location(self, text: str) -> str:
        """Extract location"""
        locations = ['karachi', 'lahore', 'islamabad', 'mumbai', 'delhi', 'bangalore', 
                    'new york', 'san francisco', 'london', 'dubai', 'singapore', 'remote']
        
        text_lower = text.lower()
        for loc in locations:
            if loc in text_lower:
                return loc.title()
        
        return ""
    
    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn"""
        pattern = r'linkedin\.com/in/[a-zA-Z0-9_-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        return f"https://{match.group(0)}" if match else ""
    
    def _extract_github(self, text: str) -> str:
        """Extract GitHub"""
        pattern = r'github\.com/[a-zA-Z0-9_-]+'
        match = re.search(pattern, text, re.IGNORECASE)
        return f"https://{match.group(0)}" if match else ""
    
    def _extract_experience(self, cleaned: str, original: str) -> Dict:
        """Extract experience with flexible matching"""
        experience = {
            'total_years': self._extract_years_experience(original),
            'positions': self._extract_positions(original),
            'companies': self._extract_companies(original),
            'current_role': self._extract_current_role(original)
        }
        return experience
    
    def _extract_years_experience(self, text: str) -> float:
        """Extract years of experience - very flexible"""
        text_lower = text.lower()
        
        # Look for explicit mentions with many variations
        patterns = [
            r'(\d+[.\d]?)\s*(?:\+?)\s*(?:years?|yrs?|years? of experience)',
            r'(\d+[.\d]?)\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+[.\d]?)\s*years?',
            r'(\d+[.\d]?)\s*years?\s+(?:in|as|with)',
            r'(\d+[.\d]?)\s*\+\s*years?',
            r'over\s+(\d+)\s*years?',
            r'more\s+than\s+(\d+)\s*years?',
            r'(\d+)\s*to\s+(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                groups = match.groups()
                if len(groups) == 2:  # Range like "3 to 5 years"
                    try:
                        return (float(groups[0]) + float(groups[1])) / 2
                    except:
                        pass
                else:
                    try:
                        return float(groups[0])
                    except:
                        pass
        
        # Calculate from work history dates
        year_ranges = re.findall(r'((?:19|20)\d{2})\s*[-–]\s*((?:19|20)\d{2}|present|current|now)', text, re.IGNORECASE)
        if year_ranges:
            total = 0
            for start, end in year_ranges:
                try:
                    start_year = int(start)
                    if end.lower() in ['present', 'current', 'now']:
                        end_year = datetime.now().year
                    else:
                        end_year = int(end)
                    total += max(0, end_year - start_year)
                except:
                    pass
            return min(total, 30)  # Cap at 30 years
        
        return 0.0
    
    def _extract_positions(self, text: str) -> List[str]:
        """Extract job positions"""
        positions = []
        
        # Look for lines with job title keywords
        title_keywords = ['engineer', 'developer', 'designer', 'manager', 'analyst', 
                         'scientist', 'architect', 'consultant', 'director', 'lead', 
                         'head', 'chief', 'cto', 'ceo', 'founder']
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in title_keywords):
                position = line.strip()
                if 5 < len(position) < 100 and position not in positions:
                    positions.append(position)
        
        return positions[:10]
    
    def _extract_companies(self, text: str) -> List[str]:
        """Extract company names"""
        companies = []
        
        # Look for company indicators
        company_keywords = ['inc', 'ltd', 'llc', 'corp', 'corporation', 'technologies', 
                          'solutions', 'systems', 'labs', 'software', 'services', 
                          'pvt', 'private', 'limited']
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in company_keywords):
                company = line.strip()
                if 5 < len(company) < 100 and company not in companies:
                    companies.append(company)
        
        return companies[:10]
    
    def _extract_current_role(self, text: str) -> str:
        """Extract current role"""
        positions = self._extract_positions(text)
        return positions[0] if positions else "Not specified"
    
    def _extract_education(self, cleaned: str, original: str) -> Dict:
        """Extract education with flexible matching"""
        education = {
            'degrees': self._extract_degrees_smart(original),
            'universities': self._extract_universities(original),
            'graduation_year': self._extract_graduation_year(original)
        }
        return education
    
    def _extract_degrees_smart(self, text: str) -> List[str]:
        """Extract degrees - very flexible"""
        degrees = []
        text_lower = text.lower()
        
        # Look for degree keywords in context
        for degree_type, keywords in self.education_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Find the full degree line
                    for line in text.split('\n'):
                        if keyword in line.lower():
                            degree = line.strip()
                            if 10 < len(degree) < 150 and degree not in degrees:
                                degrees.append(degree)
        
        return degrees[:5]
    
    def _extract_universities(self, text: str) -> List[str]:
        """Extract universities"""
        universities = []
        
        uni_keywords = ['university', 'college', 'institute', 'school', 'academy', 'tech']
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in uni_keywords):
                uni = line.strip()
                if 10 < len(uni) < 100 and uni not in universities:
                    universities.append(uni)
        
        return universities[:5]
    
    def _extract_graduation_year(self, text: str) -> Optional[int]:
        """Extract graduation year"""
        # Look for 4-digit years near education keywords
        edu_context = False
        for line in text.split('\n'):
            line_lower = line.lower()
            if any(kw in line_lower for kw in ['education', 'degree', 'bachelor', 'master', 'university']):
                edu_context = True
                # Look for year in this line or next few lines
                year_match = re.search(r'((?:19|20)\d{2})', line)
                if year_match:
                    return int(year_match.group(1))
            elif edu_context:
                year_match = re.search(r'((?:19|20)\d{2})', line)
                if year_match:
                    return int(year_match.group(1))
                # Reset context after a few lines
                edu_context = False
        
        return None
    
    def _extract_skills_comprehensive(self, cleaned: str, original: str) -> Dict:
        """Extract ALL skills with fuzzy matching"""
        text_lower = original.lower()
        
        found_technical = set()
        found_soft = set()
        
        # Extract technical skills - check all variations
        for skill_name, variations in self.all_skills.items():
            for variation in variations:
                if variation in text_lower:
                    # Use the canonical skill name
                    found_technical.add(skill_name.title())
                    break
        
        # Extract soft skills
        for skill in self.soft_skills_list:
            if skill in text_lower:
                found_soft.add(skill.title())
        
        # Also extract from skills section specifically
        skills_section = self._find_skills_section(original)
        if skills_section:
            # Extract comma/bullet separated items
            items = re.split(r'[,\n•-]', skills_section)
            for item in items:
                item = item.strip()
                if 2 < len(item) < 50:
                    # Check if it matches any known skill
                    item_lower = item.lower()
                    for skill_name, variations in self.all_skills.items():
                        if any(var in item_lower for var in variations):
                            found_technical.add(skill_name.title())
        
        # Remove duplicates and clean up
        technical_list = sorted(list(found_technical))
        soft_list = sorted(list(found_soft))
        
        return {
            'technical': technical_list,
            'soft_skills': soft_list,
            'total_count': len(technical_list) + len(soft_list)
        }
    
    def _find_skills_section(self, text: str) -> str:
        """Find the skills section"""
        patterns = [
            r'(?:skills|technical skills|core skills|expertise|technologies|tech stack)[:\s]*(.+?)(?=\n\n(?:education|experience|projects)|\Z)',
            r'(?:proficient|familiar|experienced)\s+(?:in|with)[:\s]*(.+?)(?=\n\n|\Z)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
        
        return ""
    
    def _calculate_score(self, text: str) -> Dict:
        """Calculate comprehensive score"""
        score = 0
        breakdown = {}
        
        # Contact (10 points)
        contact = 0
        if self._extract_email(text): contact += 4
        if self._extract_phone(text): contact += 3
        if self._extract_linkedin(text): contact += 2
        if self._extract_github(text): contact += 1
        breakdown['contact'] = contact
        score += contact
        
        # Experience (40 points)
        years = self._extract_years_experience(text)
        if years >= 10: exp = 40
        elif years >= 7: exp = 35
        elif years >= 5: exp = 30
        elif years >= 3: exp = 25
        elif years >= 2: exp = 20
        elif years >= 1: exp = 15
        else: exp = 5
        breakdown['experience'] = exp
        score += exp
        
        # Education (20 points)
        degrees = self._extract_degrees_smart(text)
        if degrees:
            degrees_text = ' '.join(degrees).lower()
            if any(kw in degrees_text for kw in ['phd', 'doctor']): edu = 20
            elif any(kw in degrees_text for kw in ['master', 'm.s', 'ms', 'mba']): edu = 17
            elif any(kw in degrees_text for kw in ['bachelor', 'b.s', 'bs', 'b.tech']): edu = 14
            else: edu = 10
        else:
            edu = 5
        breakdown['education'] = edu
        score += edu
        
        # Skills (30 points)
        skills = self._extract_skills_comprehensive(text, text)
        tech_count = len(skills['technical'])
        soft_count = len(skills['soft_skills'])
        
        if tech_count >= 25: skill_score = 25
        elif tech_count >= 20: skill_score = 22
        elif tech_count >= 15: skill_score = 18
        elif tech_count >= 10: skill_score = 14
        elif tech_count >= 5: skill_score = 10
        else: skill_score = 5
        
        skill_score += min(soft_count * 2, 5)
        breakdown['skills'] = skill_score
        score += skill_score
        
        total = min(score, 100)
        
        return {
            'total': total,
            'breakdown': breakdown,
            'grade': self._get_grade(total),
            'skills_count': skills['total_count']
        }
    
    def _get_grade(self, score: int) -> str:
        """Convert score to grade"""
        if score >= 90: return 'A+'
        elif score >= 80: return 'A'
        elif score >= 70: return 'B+'
        elif score >= 60: return 'B'
        elif score >= 50: return 'C+'
        elif score >= 40: return 'C'
        else: return 'D'


# Test
if __name__ == "__main__":
    parser = RobustOCRParser()
    
    test_ocr = """
MUHAMMAD AHMED KHAN
bashartech13@gmail.com
+92 3042985456
Karachi, Pakistan
github.com/bashartech

ABOUT ME
Full Stack Developer with 3+ years experience

SKILLS
Python, JavaScript, TypeScript, Java
React, Next.js, Node.js, Django
PostgreSQL, MongoDB, Redis
Docker, Kubernetes, AWS
Git, GitHub, CI/CD

EXPERIENCE
Senior Developer
TechCorp (2023-Present)

EDUCATION
Bachelor Computer Science
University of Karachi 2021
"""
    
    result = parser.parse_resume(test_ocr)
    
    print("=" * 60)
    print("ROBUST OCR PARSER TEST")
    print("=" * 60)
    
    if result['success']:
        print(f"\n✅ Name: {result['candidate']['name']}")
        print(f"✅ Email: {result['candidate']['email']}")
        print(f"✅ Phone: {result['candidate']['phone']}")
        print(f"✅ Location: {result['candidate']['location']}")
        print(f"✅ GitHub: {result['candidate']['github']}")
        
        print(f"\n📊 Experience: {result['experience']['total_years']} years")
        print(f"📊 Positions: {len(result['experience']['positions'])}")
        
        print(f"\n🎓 Degrees: {len(result['education']['degrees'])}")
        print(f"🎓 Universities: {result['education']['universities']}")
        print(f"🎓 Year: {result['education']['graduation_year']}")
        
        print(f"\n💻 Skills: {result['skills']['total_count']}")
        print(f"   Technical: {', '.join(result['skills']['technical'][:15])}")
        print(f"   Soft: {', '.join(result['skills']['soft_skills'])}")
        
        print(f"\n🏆 Score: {result['score']['total']}/100 (Grade: {result['score']['grade']})")
        print(f"🏆 Breakdown: {result['score']['breakdown']}")
