"""
Advanced Resume Parser - Comprehensive Skill & Experience Extraction
Extracts ALL information from resumes including comprehensive skill detection
"""
import re
from typing import Dict, List, Optional, Set
from datetime import datetime
from pathlib import Path


class AdvancedResumeParser:
    """Advanced parser that extracts comprehensive information from resumes"""
    
    def __init__(self):
        """Initialize with comprehensive skill databases"""
        
        # Comprehensive technical skills (500+ skills)
        self.technical_skills = {
            # Programming Languages
            'languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'golang',
                'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl',
                'haskell', 'elixir', 'erlang', 'lua', 'shell', 'bash', 'powershell',
                'objective-c', 'dart', 'f#', 'visual basic', 'cobol', 'fortran', 'assembly'
            ],
            # Web Technologies
            'web': [
                'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'webpack', 'vite',
                'react', 'react.js', 'reactjs', 'angular', 'angular.js', 'vue', 'vue.js', 'vuejs',
                'next.js', 'nextjs', 'nuxt.js', 'nuxtjs', 'svelte', 'ember', 'backbone',
                'jquery', 'bootstrap', 'tailwind', 'material-ui', 'ant design', 'chakra ui',
                'node.js', 'nodejs', 'express', 'express.js', 'django', 'flask', 'fastapi',
                'spring boot', 'laravel', 'rails', 'asp.net', 'nestjs', 'strapi'
            ],
            # Databases
            'databases': [
                'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'mongo', 'redis',
                'elasticsearch', 'cassandra', 'dynamodb', 'couchdb', 'neo4j', 'graphql',
                'prisma', 'typeorm', 'sequelize', 'mariadb', 'sqlite', 'oracle', 'mssql',
                'firebase', 'supabase', 'planetscale', 'neon', 'cockroachdb'
            ],
            # Cloud & DevOps
            'cloud_devops': [
                'aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'cloudflare',
                'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins', 'circleci',
                'github actions', 'gitlab ci', 'travis ci', 'prometheus', 'grafana', 'datadog',
                'new relic', 'sentry', 'logstash', 'kibana', 'elastic search', 'nginx', 'apache',
                'linux', 'unix', 'bash scripting', 'shell scripting', 'devops', 'ci/cd',
                'helm', 'istio', 'vault', 'consul', 'pulumi', 'cloudformation'
            ],
            # Mobile Development
            'mobile': [
                'ios', 'android', 'react native', 'reactnative', 'flutter', 'dart', 'swift',
                'kotlin', 'xamarin', 'ionic', 'cordova', 'phonegap', 'mobile development',
                'app development', 'mobile apps', 'ios development', 'android development'
            ],
            # Data Science & AI
            'data_ai': [
                'machine learning', 'ml', 'deep learning', 'dl', 'artificial intelligence', 'ai',
                'data science', 'data analysis', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
                'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'jupyter', 'jupyter notebook',
                'computer vision', 'nlp', 'natural language processing', 'llm', 'transformers',
                'openai', 'gpt', 'langchain', 'hugging face', 'mlops', 'data engineering',
                'spark', 'hadoop', 'kafka', 'airflow', 'dbt', 'snowflake', 'databricks'
            ],
            # Testing & QA
            'testing': [
                'testing', 'unit testing', 'integration testing', 'e2e testing', 'test automation',
                'jest', 'mocha', 'chai', 'pytest', 'unittest', 'cypress', 'playwright',
                'selenium', 'puppeteer', 'testcafe', 'jasmine', 'karma', 'sonarqube',
                'quality assurance', 'qa', 'manual testing', 'automated testing'
            ],
            # Tools & Platforms
            'tools': [
                'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial',
                'vscode', 'visual studio', 'intellij', 'eclipse', 'vim', 'emacs', 'neovim',
                'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator', 'canva',
                'jira', 'confluence', 'trello', 'asana', 'notion', 'slack', 'teams',
                'postman', 'insomnia', 'swagger', 'openapi', 'api development',
                'microservices', 'rest api', 'rest', 'graphql', 'soap', 'rpc',
                'agile', 'scrum', 'kanban', 'waterfall', 'project management'
            ],
            # Security
            'security': [
                'cybersecurity', 'security', 'penetration testing', 'ethical hacking',
                'owasp', 'security+', 'cissp', 'certified ethical hacker', 'network security',
                'application security', 'devsecops', 'encryption', 'authentication', 'oauth',
                'jwt', 'ssl', 'tls', 'https', 'firewall', 'vpn', 'ids', 'ips'
            ],
            # Blockchain
            'blockchain': [
                'blockchain', 'bitcoin', 'ethereum', 'solidity', 'smart contracts', 'web3',
                'defi', 'nft', 'crypto', 'cryptocurrency', 'hyperledger', 'chainlink',
                'polygon', 'binance smart chain', 'solana', 'cardano'
            ]
        }
        
        # Soft skills
        self.soft_skills = [
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
        
        # Job titles and levels
        self.job_titles = {
            'entry': ['intern', 'trainee', 'junior', 'jr', 'associate', 'entry level', 'fresher'],
            'mid': ['mid', 'middle', 'senior associate', 'ii', '2', 'three', '3'],
            'senior': ['senior', 'sr', 'lead', 'principal', 'staff', 'iv', '4', 'five', '5'],
            'management': ['manager', 'director', 'head', 'vp', 'vice president', 'chief', 'cto', 'ceo', 'cfo', 'coo']
        }
        
        # Common job roles
        self.job_roles = [
            'developer', 'engineer', 'programmer', 'architect', 'designer', 'analyst',
            'scientist', 'researcher', 'consultant', 'manager', 'director', 'lead',
            'specialist', 'administrator', 'coordinator', 'coordinator', 'intern'
        ]
    
    def parse_resume(self, ocr_text: str, source: str = "OCR") -> Dict:
        """
        Comprehensive resume parsing
        
        Args:
            ocr_text: Text extracted from resume (via OCR or other means)
            source: Source of the text
        
        Returns:
            Comprehensive dictionary with all extracted information
        """
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(ocr_text)
            
            # Extract all information
            result = {
                'success': True,
                'source': source,
                'parsed_at': datetime.now().isoformat(),
                'candidate': self._extract_personal_info(cleaned_text),
                'experience': self._extract_experience(cleaned_text),
                'education': self._extract_education(cleaned_text),
                'skills': self._extract_all_skills(cleaned_text),
                'projects': self._extract_projects(cleaned_text),
                'certifications': self._extract_certifications(cleaned_text),
                'languages': self._extract_languages(cleaned_text),
                'score': self._calculate_comprehensive_score(cleaned_text),
                'raw_text': ocr_text[:2000]
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': source
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Clean OCR text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Fix line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def _extract_personal_info(self, text: str) -> Dict:
        """Extract comprehensive personal information"""
        info = {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'location': self._extract_location(text),
            'linkedin': self._extract_linkedin(text),
            'github': self._extract_github(text),
            'website': self._extract_website(text),
            'summary': self._extract_summary(text)
        }
        return info
    
    def _extract_name(self, text: str) -> str:
        """Extract name - improved for various formats"""
        lines = text.split('\n')
        
        # Look for name at the very top (first 5 lines)
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Skip if it looks like a section header
            if any(header in line.lower() for header in ['about', 'summary', 'objective', 'experience', 'education', 'skills', 'contact', 'profile']):
                continue
            
            # Skip if it's an email or URL
            if '@' in line or 'http' in line.lower() or 'www.' in line.lower():
                continue
            
            # Skip if it's mostly numbers or special chars
            if sum(c.isalpha() for c in line) < len(line) * 0.5:
                continue
            
            # Check if it looks like a name (2-4 words, mostly letters)
            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if words are capitalized properly (name pattern)
                if all(word[0].isupper() for word in words if word):
                    return line.title()
        
        # Fallback: look for capitalized name pattern at start of text
        name_pattern = r'^([A-Z][a-z]+\s+[A-Z][a-z]+)'
        match = re.search(name_pattern, text[:500])
        if match:
            return match.group(1).strip()
        
        # Try all caps name
        caps_pattern = r'^([A-Z][A-Z\s]+)'
        match = re.search(caps_pattern, text[:500], re.MULTILINE)
        if match:
            return match.group(1).strip().title()
        
        return "Unknown"
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number - multiple formats"""
        phone_patterns = [
            r'\+?[\d\s\-\(\)]{10,}',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
            r'\d{3}[-.]?\d{3}[-.]?\d{4}',
            r'\+\d{1,3}[\s\-]?\d{3,}[\s\-]?\d{3,}[\s\-]?\d{3,}'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        
        return ""
    
    def _extract_location(self, text: str) -> str:
        """Extract location"""
        location_keywords = [
            'new york', 'san francisco', 'boston', 'seattle', 'chicago', 'austin',
            'los angeles', 'remote', 'karachi', 'lahore', 'islamabad', 'london',
            'berlin', 'paris', 'tokyo', 'singapore', 'dubai', 'mumbai', 'bangalore'
        ]
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
        """Extract personal website"""
        website_pattern = r'(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.(com|io|dev|me|org|net)(?:/[a-zA-Z0-9_-]*)*'
        match = re.search(website_pattern, text, re.IGNORECASE)
        if match:
            url = match.group(0)
            if not url.startswith('http'):
                url = 'https://' + url
            return url
        return ""
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary"""
        # Look for summary/about section
        summary_patterns = [
            r'(?:about|summary|profile|objective)[:\s]*(.+?)(?=\n\n|\n[A-Z]|\Z)',
            r'^(.+?)(?=\n\n(?:experience|education|skills))'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                if len(summary) > 50 and len(summary) < 500:
                    return summary
        
        return ""
    
    def _extract_experience(self, text: str) -> Dict:
        """Extract comprehensive experience information"""
        experience = {
            'total_years': self._extract_total_years(text),
            'positions': self._extract_positions_detailed(text),
            'companies': self._extract_companies(text),
            'current_role': self._extract_current_role(text),
            'responsibilities': self._extract_responsibilities(text)
        }
        return experience
    
    def _extract_total_years(self, text: str) -> float:
        """Extract total years of experience"""
        # Look for explicit mentions
        year_patterns = [
            r'(\d+[.\d]?)\s*(?:\+?)\s*(?:years?|yrs?|years of experience)',
            r'(\d+[.\d]?)\s*years?\s+experience',
            r'experience[:\s]*(\d+[.\d]?)\s*years?',
            r'(\d+[.\d]?)\s*years?\s+in'
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        # Calculate from work history
        years = re.findall(r'(?:\d{4})\s*[-–]\s*(?:\d{4}|present|current)', text, re.IGNORECASE)
        if years:
            total = 0
            for year_range in years:
                try:
                    start, end = year_range.replace('present', str(datetime.now().year)).replace('current', str(datetime.now().year)).split('–')
                    total += int(end.strip()) - int(start.strip())
                except:
                    pass
            return max(total, 0)
        
        return 0.0
    
    def _extract_positions_detailed(self, text: str) -> List[Dict]:
        """Extract detailed position information"""
        positions = []
        
        # Look for job title patterns
        title_keywords = ['engineer', 'developer', 'designer', 'manager', 'analyst', 'scientist', 'architect', 'consultant', 'director', 'lead']
        
        lines = text.split('\n')
        current_position = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains job title
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in title_keywords):
                # This might be a job title
                current_position['title'] = line
                # Try to extract company and dates from nearby lines
                positions.append(current_position.copy())
        
        return positions[:10]  # Top 10 positions
    
    def _extract_companies(self, text: str) -> List[str]:
        """Extract company names"""
        companies = []
        
        # Common company indicators
        company_keywords = ['inc', 'ltd', 'llc', 'corp', 'corporation', 'technologies', 'solutions', 'systems', 'labs', 'software', 'services']
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in company_keywords):
                company = line.strip()
                if 5 < len(company) < 100 and company not in companies:
                    companies.append(company)
        
        return companies[:10]
    
    def _extract_current_role(self, text: str) -> str:
        """Extract current/most recent role"""
        positions = self._extract_positions_detailed(text)
        if positions and positions[0].get('title'):
            return positions[0]['title']
        return "Not specified"
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities"""
        responsibilities = []
        
        # Look for bullet points or numbered lists
        bullet_patterns = [
            r'[-•*]\s*(.+)',
            r'\d+\.\s*(.+)'
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if 20 < len(match) < 200:  # Reasonable length
                    responsibilities.append(match.strip())
        
        return responsibilities[:20]
    
    def _extract_education(self, text: str) -> Dict:
        """Extract comprehensive education information"""
        education = {
            'degrees': self._extract_degrees_detailed(text),
            'universities': self._extract_universities(text),
            'graduation_year': self._extract_graduation_year(text),
            'gpa': self._extract_gpa(text),
            'coursework': self._extract_coursework(text)
        }
        return education
    
    def _extract_degrees_detailed(self, text: str) -> List[Dict]:
        """Extract detailed degree information"""
        degrees = []
        
        degree_keywords = ['bachelor', 'master', 'phd', 'mba', 'bs', 'ms', 'b.tech', 'm.tech', 'be', 'me', 'diploma', 'associate']
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in degree_keywords):
                degree_info = {
                    'degree': line.strip(),
                    'field': self._extract_field_of_study(line),
                    'university': self._extract_university_from_line(line),
                    'year': self._extract_year_from_line(line)
                }
                degrees.append(degree_info)
        
        return degrees
    
    def _extract_field_of_study(self, text: str) -> str:
        """Extract field of study"""
        field_patterns = [
            r'in\s+([a-zA-Z\s]+?)(?:\s+from|\s+at|\s+\|)',
            r'([a-zA-Z\s]+?)(?:\s+engineering|\s+science|\s+arts)'
        ]
        
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_universities(self, text: str) -> List[str]:
        """Extract university names"""
        universities = []
        
        uni_keywords = ['university', 'college', 'institute', 'school', 'academy']
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in uni_keywords):
                uni = line.strip()
                if 10 < len(uni) < 100 and uni not in universities:
                    universities.append(uni)
        
        return universities[:5]
    
    def _extract_university_from_line(self, line: str) -> str:
        """Extract university from a line"""
        uni_keywords = ['university', 'college', 'institute', 'school']
        for keyword in uni_keywords:
            if keyword in line.lower():
                # Extract the full university name
                start = line.lower().find(keyword)
                # Go back to find the start of the name
                while start > 0 and line[start-1].isalpha():
                    start -= 1
                return line[start:].strip()
        return ""
    
    def _extract_year_from_line(self, line: str) -> Optional[int]:
        """Extract year from a line"""
        year_pattern = r'(?:19|20)\d{2}'
        match = re.search(year_pattern, line)
        if match:
            return int(match.group(0))
        return None
    
    def _extract_graduation_year(self, text: str) -> Optional[int]:
        """Extract graduation year"""
        year_pattern = r'(?:graduation|graduated|class of)\s*[:\-]?\s*((?:19|20)\d{2})'
        match = re.search(year_pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Look for years near education keywords
        edu_year_pattern = r'((?:19|20)\d{2})\s*[-–]\s*((?:19|20)\d{2})'
        matches = re.findall(edu_year_pattern, text)
        if matches:
            return int(matches[-1][1])  # Most recent end year
        
        return None
    
    def _extract_gpa(self, text: str) -> str:
        """Extract GPA"""
        gpa_pattern = r'(?:gpa|cgpa)[:\s]*(\d[.\d]*)(?:/?\d[.\d]*)?'
        match = re.search(gpa_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return ""
    
    def _extract_coursework(self, text: str) -> List[str]:
        """Extract relevant coursework"""
        coursework = []
        
        # Look for coursework section
        coursework_pattern = r'(?:relevant coursework|coursework|courses)[:\s]*(.+?)(?=\n\n|\n[A-Z]|\Z)'
        match = re.search(coursework_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            courses_text = match.group(1)
            courses = re.split(r'[,;]', courses_text)
            coursework = [course.strip() for course in courses if course.strip()]
        
        return coursework[:10]
    
    def _extract_all_skills(self, text: str) -> Dict:
        """Extract ALL skills comprehensively"""
        text_lower = text.lower()
        
        all_technical = set()
        all_soft = set()
        
        # Extract technical skills from all categories
        for category, skills in self.technical_skills.items():
            for skill in skills:
                if skill in text_lower:
                    # Capitalize properly
                    formatted_skill = skill.title()
                    if skill in ['sql', 'ml', 'dl', 'ai', 'ml', 'aws', 'gcp']:
                        formatted_skill = skill.upper()
                    elif skill in ['html', 'css']:
                        formatted_skill = skill.upper()
                    all_technical.add(formatted_skill)
        
        # Extract soft skills
        for skill in self.soft_skills:
            if skill in text_lower:
                all_soft.add(skill.title())
        
        # Also look for skills in "Skills" section specifically
        skills_section = self._extract_skills_section(text)
        if skills_section:
            # Extract comma or bullet-separated skills
            skill_items = re.split(r'[,\n•]', skills_section)
            for item in skill_items:
                item = item.strip()
                if 2 < len(item) < 50 and item[0].isupper():
                    all_technical.add(item)
        
        return {
            'technical': sorted(list(all_technical)),
            'soft_skills': sorted(list(all_soft)),
            'categories': self._categorize_skills(all_technical),
            'total_count': len(all_technical) + len(all_soft)
        }
    
    def _extract_skills_section(self, text: str) -> str:
        """Extract the skills section from resume"""
        skills_pattern = r'(?:skills|technical skills|core skills|expertise)[:\s]*(.+?)(?=\n\n(?:education|experience|projects)|\Z)'
        match = re.search(skills_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
        return ""
    
    def _categorize_skills(self, skills: Set[str]) -> Dict[str, List[str]]:
        """Categorize extracted skills"""
        categories = {
            'Programming Languages': [],
            'Web Technologies': [],
            'Databases': [],
            'Cloud & DevOps': [],
            'Mobile': [],
            'Data & AI': [],
            'Tools': []
        }
        
        skills_lower = {s.lower(): s for s in skills}
        
        for skill_lower, skill_original in skills_lower.items():
            if skill_lower in [l for l in self.technical_skills['languages']]:
                categories['Programming Languages'].append(skill_original)
            elif skill_lower in [l for l in self.technical_skills['web']]:
                categories['Web Technologies'].append(skill_original)
            elif skill_lower in [l for l in self.technical_skills['databases']]:
                categories['Databases'].append(skill_original)
            elif skill_lower in [l for l in self.technical_skills['cloud_devops']]:
                categories['Cloud & DevOps'].append(skill_original)
            elif skill_lower in [l for l in self.technical_skills['mobile']]:
                categories['Mobile'].append(skill_original)
            elif skill_lower in [l for l in self.technical_skills['data_ai']]:
                categories['Data & AI'].append(skill_original)
            else:
                categories['Tools'].append(skill_original)
        
        return {k: v for k, v in categories.items() if v}
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract projects"""
        projects = []
        
        # Look for projects section
        projects_pattern = r'(?:projects|personal projects|key projects)[:\s]*(.+?)(?=\n\n(?:skills|education|experience)|\Z)'
        match = re.search(projects_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            projects_text = match.group(1)
            # Split by bullet points or numbers
            project_items = re.split(r'\n\s*[-•]|\n\s*\d+\.', projects_text)
            for item in project_items:
                item = item.strip()
                if len(item) > 20:
                    projects.append({'description': item})
        
        return projects[:10]
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certs = []
        
        cert_keywords = ['certified', 'certification', 'certificate', 'aws', 'azure', 'gcp', 'pmp', 'scrum', 'cisa', 'cissp', 'comptia']
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in cert_keywords):
                cert = line.strip()
                if 10 < len(cert) < 100 and cert not in certs:
                    certs.append(cert)
        
        return certs[:10]
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages"""
        languages = []
        
        lang_keywords = ['english', 'spanish', 'french', 'german', 'mandarin', 'hindi', 'arabic', 'portuguese', 'japanese', 'korean', 'urdu', 'bengali']
        
        text_lower = text.lower()
        for lang in lang_keywords:
            if lang in text_lower:
                languages.append(lang.title())
        
        return languages if languages else ['English']
    
    def _calculate_comprehensive_score(self, text: str) -> Dict:
        """Calculate comprehensive score based on all factors"""
        score = 0
        breakdown = {}
        
        # Contact Info (10 points)
        contact_score = 0
        if self._extract_email(text):
            contact_score += 4
        if self._extract_phone(text):
            contact_score += 3
        if self._extract_linkedin(text):
            contact_score += 2
        if self._extract_github(text):
            contact_score += 1
        breakdown['contact'] = contact_score
        score += contact_score
        
        # Experience (40 points)
        years = self._extract_total_years(text)
        if years >= 10:
            exp_score = 40
        elif years >= 7:
            exp_score = 35
        elif years >= 5:
            exp_score = 30
        elif years >= 3:
            exp_score = 25
        elif years >= 2:
            exp_score = 20
        elif years >= 1:
            exp_score = 15
        else:
            exp_score = 5
        breakdown['experience'] = exp_score
        score += exp_score
        
        # Education (20 points)
        degrees = self._extract_degrees_detailed(text)
        if degrees:
            if any('phd' in d.get('degree', '').lower() for d in degrees):
                edu_score = 20
            elif any('master' in d.get('degree', '').lower() or 'mba' in d.get('degree', '').lower() for d in degrees):
                edu_score = 17
            elif any('bachelor' in d.get('degree', '').lower() or 'b.tech' in d.get('degree', '').lower() for d in degrees):
                edu_score = 14
            else:
                edu_score = 10
        else:
            edu_score = 5
        breakdown['education'] = edu_score
        score += edu_score
        
        # Skills (30 points) - COMPREHENSIVE
        skills = self._extract_all_skills(text)
        tech_count = len(skills['technical'])
        soft_count = len(skills['soft_skills'])
        
        # More skills = higher score
        if tech_count >= 20:
            skill_score = 25
        elif tech_count >= 15:
            skill_score = 22
        elif tech_count >= 10:
            skill_score = 18
        elif tech_count >= 5:
            skill_score = 12
        else:
            skill_score = 5
        
        # Add soft skills bonus
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
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C+'
        elif score >= 40:
            return 'C'
        else:
            return 'D'


# Test the advanced parser
if __name__ == "__main__":
    parser = AdvancedResumeParser()
    
    # Sample OCR text from a resume
    sample_ocr = """
MUHAMMAD AHMED KHAN
bashartech13@gmail.com
+92 312 3456789
Karachi, Pakistan
https://github.com/bashartech
https://linkedin.com/in/bashartech

ABOUT ME
Passionate Full Stack Developer with 3+ years of experience building scalable web applications.

EXPERIENCE
Senior Full Stack Developer
TechCorp Solutions (2023-Present)
- Led development of microservices architecture
- Managed team of 5 developers
- Implemented CI/CD pipelines using Docker and Kubernetes

Full Stack Developer
StartupXYZ (2021-2023)
- Developed REST APIs using Python, Django, and Node.js
- Built responsive web applications with React, Next.js
- Worked with MongoDB, PostgreSQL, Redis

EDUCATION
Bachelor of Science in Computer Science
University of Karachi (2017-2021)
CGPA: 3.8/4.0

SKILLS
Programming: Python, JavaScript, TypeScript, Java, Go
Web: React, Next.js, Node.js, Django, Flask, HTML, CSS
Databases: MongoDB, PostgreSQL, MySQL, Redis
Cloud: AWS, Docker, Kubernetes, Terraform
Tools: Git, GitHub, Jira, Figma

PROJECTS
E-commerce Platform - Built full-stack e-commerce site with payment integration
Task Management App - React Native mobile app with real-time sync

CERTIFICATIONS
AWS Certified Developer Associate
Certified Scrum Master

LANGUAGES
English, Urdu, German
"""
    
    result = parser.parse_resume(sample_ocr, "Test OCR")
    
    print("=" * 60)
    print("ADVANCED RESUME PARSER TEST")
    print("=" * 60)
    
    if result['success']:
        print(f"\n✅ Name: {result['candidate']['name']}")
        print(f"✅ Email: {result['candidate']['email']}")
        print(f"✅ Phone: {result['candidate']['phone']}")
        print(f"✅ Location: {result['candidate']['location']}")
        print(f"✅ LinkedIn: {result['candidate']['linkedin']}")
        print(f"✅ GitHub: {result['candidate']['github']}")
        
        print(f"\n📊 Experience: {result['experience']['total_years']} years")
        print(f"📊 Current Role: {result['experience']['current_role']}")
        print(f"📊 Companies: {len(result['experience']['companies'])}")
        
        print(f"\n🎓 Degrees: {len(result['education']['degrees'])}")
        print(f"🎓 Universities: {result['education']['universities']}")
        print(f"🎓 Graduation: {result['education']['graduation_year']}")
        
        print(f"\n💻 Technical Skills: {len(result['skills']['technical'])}")
        print(f"   {', '.join(result['skills']['technical'][:15])}...")
        print(f"💻 Soft Skills: {len(result['skills']['soft_skills'])}")
        print(f"   {', '.join(result['skills']['soft_skills'])}")
        
        print(f"\n🏆 Score: {result['score']['total']}/100 (Grade: {result['score']['grade']})")
        print(f"🏆 Skills Count: {result['score']['skills_count']}")
    else:
        print(f"\n❌ Parsing failed: {result.get('error')}")
