"""
CV parsing and analysis services
"""
import re
import os
import json
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import PyPDF2
import docx
import openai
from django.conf import settings
from django.utils import timezone
from .models import CV, CVAnalysis, Skill, CVSkill, Experience, Education

logger = logging.getLogger(__name__)

# Lazy load spaCy model to avoid slow PyTorch initialization at startup
nlp = None

def get_nlp():
    """Lazy load spaCy model only when needed"""
    global nlp
    if nlp is None:
        try:
            import spacy
            nlp = spacy.load("en_core_web_md")
        except OSError:
            logger.warning("spaCy model 'en_core_web_md' not found. Run: python -m spacy download en_core_web_md")
            nlp = False  # Mark as attempted to avoid repeated tries
    return nlp if nlp is not False else None

# Lazy OpenAI accessor to avoid importing/initializing client at module import time
def get_openai_client():
    """Return the openai module with api key configured, or None if not available."""
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        return None

    # Configure top-level openai api_key to avoid constructing client wrappers
    try:
        openai.api_key = api_key
    except Exception:
        # Best-effort: if the openai package API differs, ignore and let calls fail later with clear errors
        pass

    return openai


class CVParser:
    """Parse CV files and extract text"""
    
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """Extract text from CV file"""
        try:
            if file_type == 'pdf':
                return CVParser._extract_pdf(file_path)
            elif file_type == 'docx':
                return CVParser._extract_docx(file_path)
            elif file_type == 'txt':
                return CVParser._extract_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise
    
    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)
    
    @staticmethod
    def _extract_docx(file_path: str) -> str:
        """Extract text from DOCX"""
        doc = docx.Document(file_path)
        text = [para.text for para in doc.paragraphs]
        return '\n'.join(text)
    
    @staticmethod
    def _extract_txt(file_path: str) -> str:
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()


class ContactExtractor:
    """Extract contact information from CV text"""
    
    EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_REGEX = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    LINKEDIN_REGEX = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
    GITHUB_REGEX = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+'
    
    @staticmethod
    def extract(text: str) -> Dict[str, str]:
        """Extract contact information"""
        contact = {
            'email': '',
            'phone': '',
            'linkedin_url': '',
            'github_url': '',
        }
        
        # Extract email
        email_match = re.search(ContactExtractor.EMAIL_REGEX, text)
        if email_match:
            contact['email'] = email_match.group()
        
        # Extract phone
        phone_match = re.search(ContactExtractor.PHONE_REGEX, text)
        if phone_match:
            contact['phone'] = phone_match.group()
        
        # Extract LinkedIn
        linkedin_match = re.search(ContactExtractor.LINKEDIN_REGEX, text, re.IGNORECASE)
        if linkedin_match:
            contact['linkedin_url'] = linkedin_match.group()
        
        # Extract GitHub
        github_match = re.search(ContactExtractor.GITHUB_REGEX, text, re.IGNORECASE)
        if github_match:
            contact['github_url'] = github_match.group()
        
        return contact


class SkillExtractor:
    """Extract skills from CV using NLP"""
    
    TECH_SKILLS = [
        # Programming Languages
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Swift', 'Kotlin',
        'TypeScript', 'Rust', 'Scala', 'R', 'MATLAB', 'SQL', 'NoSQL',
        
        # Web Technologies
        'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django', 'Flask',
        'FastAPI', 'Spring', 'ASP.NET', 'Ruby on Rails', 'Laravel',
        
        # Databases
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 'SQL Server',
        'Cassandra', 'DynamoDB', 'Firebase',
        
        # Cloud & DevOps
        'AWS', 'Azure', 'Google Cloud', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'CI/CD',
        'Terraform', 'Ansible', 'Git', 'GitHub', 'GitLab', 'Bitbucket',
        
        # Data Science & ML
        'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'TensorFlow', 'PyTorch',
        'Scikit-learn', 'Pandas', 'NumPy', 'Jupyter', 'Keras', 'OpenCV',
        
        # Mobile
        'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin',
        
        # Testing
        'Jest', 'Pytest', 'JUnit', 'Selenium', 'Cypress', 'Mocha', 'Chai',
        
        # Others
        'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum', 'JIRA', 'Confluence',
    ]
    
    SOFT_SKILLS = [
        'Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking',
        'Project Management', 'Time Management', 'Adaptability', 'Creativity',
        'Attention to Detail', 'Collaboration', 'Mentoring', 'Public Speaking',
    ]
    
    @staticmethod
    def extract(text: str, cv: CV) -> List[CVSkill]:
        """Extract skills from CV text"""
        skills_found = []
        text_lower = text.lower()
        
        # Check for tech skills
        for skill_name in SkillExtractor.TECH_SKILLS:
            if skill_name.lower() in text_lower:
                # Get or create skill
                skill, created = Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={'category': 'Technical'}
                )
                
                # Calculate confidence based on frequency
                frequency = text_lower.count(skill_name.lower())
                confidence = min(100, 50 + frequency * 10)
                
                # Create CV skill
                cv_skill, created = CVSkill.objects.get_or_create(
                    cv=cv,
                    skill=skill,
                    defaults={
                        'confidence': confidence,
                        'context': SkillExtractor._extract_context(text, skill_name)
                    }
                )
                
                if created:
                    skills_found.append(cv_skill)
        
        # Check for soft skills
        for skill_name in SkillExtractor.SOFT_SKILLS:
            if skill_name.lower() in text_lower:
                skill, created = Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={'category': 'Soft'}
                )
                
                frequency = text_lower.count(skill_name.lower())
                confidence = min(100, 40 + frequency * 15)
                
                cv_skill, created = CVSkill.objects.get_or_create(
                    cv=cv,
                    skill=skill,
                    defaults={
                        'confidence': confidence,
                        'context': SkillExtractor._extract_context(text, skill_name)
                    }
                )
                
                if created:
                    skills_found.append(cv_skill)
        
        return skills_found
    
    @staticmethod
    def _extract_context(text: str, skill: str) -> str:
        """Extract context around skill mention"""
        # Find the skill in text and grab surrounding words
        pattern = r'(.{0,50}' + re.escape(skill) + r'.{0,50})'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else ''


class ExperienceExtractor:
    """Extract work experience from CV"""
    
    @staticmethod
    def extract(text: str, cv: CV) -> List[Experience]:
        """Extract work experience using pattern matching"""
        experiences = []
        
        # Split text into lines
        lines = text.split('\n')
        
        # Find experience section
        exp_section_start = None
        for i, line in enumerate(lines):
            if re.search(r'\b(experience|employment|work history)\b', line, re.IGNORECASE):
                exp_section_start = i
                break
        
        if exp_section_start is None:
            return experiences
        
        # Extract experience entries (simplified)
        # In production, use more sophisticated NLP
        current_exp = {}
        for line in lines[exp_section_start:]:
            # Check for company/position pattern
            if re.search(r'\b(at|@)\b', line, re.IGNORECASE) and len(line) < 200:
                if current_exp:
                    # Save previous experience
                    experiences.append(ExperienceExtractor._create_experience(cv, current_exp))
                    current_exp = {}
                
                # Parse line for company and position
                parts = re.split(r'\b(at|@)\b', line, flags=re.IGNORECASE)
                if len(parts) >= 3:
                    current_exp['position'] = parts[0].strip()
                    current_exp['company'] = parts[2].strip()
            
            # Check for dates
            date_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|present|current)'
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            if date_match and current_exp:
                try:
                    start_year = int(date_match.group(1))
                    end_str = date_match.group(2).lower()
                    
                    current_exp['start_date'] = datetime(start_year, 1, 1).date()
                    
                    if end_str in ['present', 'current']:
                        current_exp['is_current'] = True
                    else:
                        end_year = int(end_str)
                        current_exp['end_date'] = datetime(end_year, 12, 31).date()
                except:
                    pass
        
        # Save last experience
        if current_exp:
            experiences.append(ExperienceExtractor._create_experience(cv, current_exp))
        
        return experiences
    
    @staticmethod
    def _create_experience(cv: CV, data: Dict) -> Experience:
        """Create Experience object"""
        return Experience.objects.create(
            cv=cv,
            company=data.get('company', 'Unknown'),
            position=data.get('position', 'Unknown'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            is_current=data.get('is_current', False),
            description=data.get('description', '')
        )


class CVAnalyzer:
    """Analyze CV and generate insights using OpenAI"""
    
    @staticmethod
    def analyze(cv: CV) -> CVAnalysis:
        """Perform comprehensive CV analysis"""
        # Extract contact info
        contact = ContactExtractor.extract(cv.raw_text)
        
        # Calculate total experience
        experiences = cv.experiences.all()
        total_months = sum(exp.duration_months or 0 for exp in experiences)
        total_years = Decimal(total_months) / Decimal(12) if total_months else Decimal(0)
        
        # Get highest degree
        education = cv.education.order_by('-degree').first()
        highest_degree = education.degree if education else ''
        
        # Calculate scores
        scores = CVAnalyzer._calculate_scores(cv)
        
        # Generate AI insights
        insights = CVAnalyzer._generate_insights(cv)
        
        # Create or update analysis
        analysis, created = CVAnalysis.objects.update_or_create(
            cv=cv,
            defaults={
                'full_name': contact.get('full_name', ''),
                'email': contact.get('email', ''),
                'phone': contact.get('phone', ''),
                'linkedin_url': contact.get('linkedin_url', ''),
                'github_url': contact.get('github_url', ''),
                'total_years_experience': total_years,
                'highest_degree': highest_degree,
                **scores,
                **insights,
            }
        )
        
        # Update CV status
        cv.status = 'analyzed'
        cv.processed_at = timezone.now()
        cv.save()
        
        return analysis
    
    @staticmethod
    def _calculate_scores(cv: CV) -> Dict[str, int]:
        """Calculate various scores for CV"""
        scores = {
            'overall_score': 0,
            'experience_score': 0,
            'education_score': 0,
            'skills_score': 0,
            'formatting_score': 0,
        }
        
        # Experience score (based on years)
        experiences = cv.experiences.all()
        total_months = sum(exp.duration_months or 0 for exp in experiences)
        total_years = total_months / 12 if total_months else 0
        scores['experience_score'] = min(100, int(total_years * 10))
        
        # Education score
        education_count = cv.education.count()
        scores['education_score'] = min(100, education_count * 25)
        
        # Skills score (based on number and confidence)
        skills = cv.skills.all()
        if skills:
            avg_confidence = sum(s.confidence for s in skills) / len(skills)
            skill_count_score = min(50, len(skills) * 2)
            scores['skills_score'] = int((avg_confidence * 0.5) + skill_count_score)
        
        # Formatting score (based on text structure)
        text = cv.raw_text
        sections = ['experience', 'education', 'skills']
        found_sections = sum(1 for s in sections if s in text.lower())
        scores['formatting_score'] = int((found_sections / len(sections)) * 100)
        
        # Overall score (weighted average)
        scores['overall_score'] = int(
            scores['experience_score'] * 0.3 +
            scores['education_score'] * 0.2 +
            scores['skills_score'] * 0.3 +
            scores['formatting_score'] * 0.2
        )
        
        return scores
    
    @staticmethod
    def _generate_insights(cv: CV) -> Dict[str, Any]:
        """Generate AI insights using OpenAI"""
        client = get_openai_client()
        if not client:
            return {
                'strengths': ['OpenAI API not configured'],
                'weaknesses': [],
                'suggestions': []
            }
        
        try:
            # Prepare CV summary
            skills = [s.skill.name for s in cv.skills.all()[:20]]
            experiences = cv.experiences.all()[:5]
            
            prompt = f"""Analyze this CV and provide brief insights:

Skills: {', '.join(skills)}
Years of Experience: {sum(exp.duration_months or 0 for exp in experiences) / 12:.1f}
Number of Jobs: {experiences.count()}

Provide:
1. Top 3 strengths (brief points)
2. Top 3 areas for improvement (brief points)
3. Top 3 actionable suggestions (brief points)

Format as JSON with keys: strengths, weaknesses, suggestions (each as array of strings)
"""
            
            # Prefer the top-level ChatCompletion API; handle different return shapes
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert CV reviewer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )

                # response may be an object or dict-like depending on openai version
                if hasattr(response, 'choices'):
                    content = None
                    try:
                        content = response.choices[0].message.content
                    except Exception:
                        try:
                            content = response.choices[0]['message']['content']
                        except Exception:
                            content = None

                else:
                    # dict-like
                    content = response.get('choices', [])[0].get('message', {}).get('content')

                import json
                insights = json.loads(content) if content else {}
                return insights
            except Exception as e:
                # Log the full exception for debugging and fall back to a safe default
                logger.exception("OpenAI call failed while generating insights")
                raise
            return insights
        
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {
                'strengths': ['Strong technical skills'],
                'weaknesses': [],
                'suggestions': ['Consider adding more quantifiable achievements']
            }


class CVProcessingService:
    """Main service to process CVs"""
    
    @staticmethod
    def process_cv(cv_id: int):
        """Process a CV: parse, extract, analyze"""
        try:
            cv = CV.objects.get(id=cv_id)
            cv.status = 'processing'
            cv.save()
            
            # 1. Extract text
            file_path = cv.file.path
            raw_text = CVParser.extract_text(file_path, cv.file_type)
            cv.raw_text = raw_text
            cv.save()
            
            # 2. Extract skills
            SkillExtractor.extract(raw_text, cv)
            
            # 3. Extract experience
            ExperienceExtractor.extract(raw_text, cv)
            
            # 4. Analyze
            analysis = CVAnalyzer.analyze(cv)
            
            logger.info(f"Successfully processed CV {cv.id}")
            return analysis
        
        except Exception as e:
            logger.error(f"Error processing CV {cv_id}: {e}")
            cv.status = 'failed'
            cv.processing_error = str(e)
            cv.save()
            raise


class CVAnalysisService:
    """
    Service for the 3 CV analysis modules using Llama 3.1
    """
    
    def __init__(self):
        self.ollama_url = getattr(settings, 'OLLAMA_API_URL', 'http://ollama:11434')
        self.model_name = "llama3.1:8b"
    
    def call_llama(self, messages: List[dict]) -> str:
        """Call Llama 3.1 via Ollama API with deterministic settings"""
        import requests
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "top_p": 0.1,
                "seed": 42,
            }
        }
        try:
            resp = requests.post(f"{self.ollama_url}/api/chat", json=payload, timeout=500)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Llama API error: {e}")
            raise
    
    def extract_json_from_llm(self, text: str) -> dict:
        """Extract JSON from LLM output"""
        try:
            # Remove markdown code blocks if present
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            start = text.index("{")
            end = text.rindex("}") + 1
            json_str = text[start:end]
            return json.loads(json_str)
        except Exception:
            return {}
    
    def calculate_ats_score(self, cv_text: str) -> dict:
        """
        Calculate ATS compatibility score using Llama 3.1
        Returns comprehensive ATS analysis with score, keywords, and suggestions
        """
        try:
            prompt = f"""You are an expert in recruitment, HR and ATS (Applicant Tracking Systems).
Analyze this CV for ATS compatibility and respond with STRICTLY VALID JSON.

⚠️ STRICT RULES:
- Detect ONLY sections that are present in the CV
- DO NOT invent keywords or sections
- If a section exists → detect it, otherwise don't mention it
- Copy quantified examples EXACTLY from the CV (don't translate or reformulate)
- Never use placeholders like X%, Y%, Z%

Analyze these aspects:
1. Overall ATS score (0-100)
2. Contact information (email, phone, LinkedIn, GitHub)
3. Sections detected (Experience, Education, Skills, etc.)
4. Keywords: technical skills, soft skills, action verbs
5. Quantified impact examples (with real numbers from CV)
6. Quick improvement suggestions (3-5 actionable items)

CV Text:
{cv_text[:5000]}

Respond in this EXACT JSON format:
{{
  "ats_score": 85,
  "contacts": {{
    "has_email": true,
    "has_phone": true,
    "has_linkedin": false,
    "has_github": false
  }},
  "sections_detected": ["Experience", "Education", "Skills"],
  "sections_missing": ["Summary/Profile", "Certifications"],
  "keyword_matches": ["Python", "JavaScript", "React", "Problem Solving", "Team Leadership"],
  "missing_keywords": ["Docker", "CI/CD", "Cloud Services"],
  "quantified_examples": ["Improved system performance by 40%", "Reduced costs by $50K annually"],
  "action_verbs": ["Developed", "Implemented", "Led", "Optimized"],
  "suggestions": [
    "Add a professional summary at the top",
    "Include LinkedIn profile URL",
    "Add measurable results with numbers for each role",
    "Include certifications section",
    "Use consistent date formatting"
  ],
  "detailed_report": "Your CV scores 85/100 for ATS compatibility. Strong points: clear section headers, good keyword density, quantified achievements. Areas to improve: add professional summary, include more contact methods, expand technical skills section."
}}"""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert ATS analyzer. Respond ONLY with valid JSON, no additional text."
                },
                {"role": "user", "content": prompt}
            ]
            
            raw_response = self.call_llama(messages)
            result = self.extract_json_from_llm(raw_response)
            
            if not result:
                logger.warning("Failed to parse Llama response, using fallback")
                return self._basic_ats_score(cv_text)
            
            # Normalize response format
            return {
                'score': result.get('ats_score', 70),
                'keyword_matches': result.get('keyword_matches', []),
                'missing_keywords': result.get('missing_keywords', []),
                'suggestions': result.get('suggestions', []),
                'detailed_report': result.get('detailed_report', ''),
                'contacts': result.get('contacts', {}),
                'sections_detected': result.get('sections_detected', []),
                'sections_missing': result.get('sections_missing', []),
                'quantified_examples': result.get('quantified_examples', []),
                'action_verbs': result.get('action_verbs', []),
            }
            
        except Exception as e:
            logger.error(f"Llama ATS analysis error: {e}")
            return self._basic_ats_score(cv_text)
    
    def _basic_ats_score(self, cv_text: str) -> dict:
        """Basic ATS scoring without AI"""
        score = 50
        keyword_matches = []
        missing_keywords = []
        
        # Check for basic sections
        if 'experience' in cv_text.lower() or 'work history' in cv_text.lower():
            score += 15
            keyword_matches.append("Experience section")
        else:
            missing_keywords.append("Experience section")
        
        if 'education' in cv_text.lower():
            score += 10
            keyword_matches.append("Education section")
        else:
            missing_keywords.append("Education section")
        
        if 'skills' in cv_text.lower():
            score += 15
            keyword_matches.append("Skills section")
        else:
            missing_keywords.append("Skills section")
        
        if '@' in cv_text:
            keyword_matches.append("Email address")
            score += 5
        
        if any(char.isdigit() for char in cv_text[:500]):
            keyword_matches.append("Phone number")
            score += 5
        
        # Look for common technical keywords
        tech_keywords = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'git']
        found_tech = [kw for kw in tech_keywords if kw in cv_text.lower()]
        keyword_matches.extend(found_tech[:5])
        
        return {
            'score': min(score, 100),
            'keyword_matches': keyword_matches,
            'missing_keywords': missing_keywords or ["Industry-specific keywords", "Technical skills", "Certifications"],
            'suggestions': [
                "Add clear section headers (Experience, Education, Skills)",
                "Include contact information at the top",
                "Use industry-specific keywords from job descriptions",
                "Add measurable achievements with numbers",
                "Include technical skills section"
            ],
            'detailed_report': f"Your CV scores {score}/100 for ATS compatibility. Basic analysis shows you have {len(keyword_matches)} key elements present. To improve your score, focus on adding missing sections and incorporating more relevant keywords from your target job descriptions."
        }
    
    def match_cv_to_job(self, cv_text: str, job_title: str, job_description: str) -> dict:
        """
        Match CV against job description
        Returns match score + analysis
        """
        openai_client = get_openai_client()
        if not openai_client:
            return self._basic_job_match(cv_text, job_description)
        
        try:
            prompt = f"""
You are a recruitment expert. Compare this CV against the job description and provide:
1. Overall match score (0-100)
2. List of matched skills/qualifications
3. List of missing skills/qualifications
4. Detailed matching report
5. Recommendations to improve match

Job Title: {job_title}

Job Description:
{job_description[:2000]}

CV Text:
{cv_text[:4000]}

Respond in JSON format:
{{
  "match_score": 75,
  "matched_skills": ["Python", "Django", "REST APIs", "5+ years experience"],
  "missing_skills": ["Kubernetes", "AWS certification", "Team leadership"],
  "matching_report": "You are a strong match for this position...",
  "recommendations": ["Obtain AWS certification", "Highlight leadership experience"]
}}
"""
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"OpenAI job matching error: {e}")
            return self._basic_job_match(cv_text, job_description)
    
    def _basic_job_match(self, cv_text: str, job_description: str) -> dict:
        """Basic job matching without AI"""
        # Simple keyword matching
        cv_lower = cv_text.lower()
        job_lower = job_description.lower()
        
        # Common tech skills
        common_skills = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes']
        matched = [skill for skill in common_skills if skill in cv_lower and skill in job_lower]
        missing = [skill for skill in common_skills if skill in job_lower and skill not in cv_lower]
        
        match_score = min(50 + len(matched) * 10, 100)
        
        return {
            'match_score': match_score,
            'matched_skills': matched,
            'missing_skills': missing,
            'matching_report': f"Based on keyword analysis, you match {match_score}% with this position. You have {len(matched)} of the key skills mentioned.",
            'recommendations': [f"Consider gaining experience with {skill}" for skill in missing[:3]]
        }
    
    def extract_skills(self, cv_text: str) -> list:
        """Extract skills from CV"""
        # Simple skill extraction
        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Angular', 'Vue', 'Node.js',
            'Django', 'Flask', 'Spring', 'SQL', 'MongoDB', 'PostgreSQL', 'MySQL',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git', 'CI/CD',
            'Agile', 'Scrum', 'REST APIs', 'GraphQL', 'Microservices'
        ]
        
        found_skills = [skill for skill in common_skills if skill.lower() in cv_text.lower()]
        return found_skills
    
    def summarize_experience(self, cv_text: str) -> str:
        """Summarize work experience"""
        openai_client = get_openai_client()
        if not openai_client:
            return "Experience summary not available without OpenAI API key."
        
        try:
            prompt = f"""
Summarize the work experience from this CV in 2-3 sentences:

{cv_text[:3000]}
"""
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except:
            return "Unable to generate experience summary."
    
    def summarize_education(self, cv_text: str) -> str:
        """Summarize education"""
        # Simple pattern matching for degrees
        degrees = ['bachelor', 'master', 'phd', 'doctorate', 'mba', 'associate']
        found = [d for d in degrees if d in cv_text.lower()]
        if found:
            return f"Education includes: {', '.join(found).title()}"
        return "Education details not clearly identified."
    
    def generate_recommendations(self, cv_text: str, ats_data: dict, match_data: dict) -> list:
        """Generate overall recommendations"""
        recommendations = []
        
        if ats_data['score'] < 80:
            recommendations.append("Improve ATS compatibility by addressing formatting issues")
        
        if match_data and match_data['match_score'] < 70:
            recommendations.extend(match_data['recommendations'][:2])
        
        recommendations.append("Keep CV concise (1-2 pages)")
        recommendations.append("Use action verbs and quantify achievements")
        
        return recommendations[:5]
    
    def analyze_advanced_cv(self, cv_text: str) -> dict:
        """
        Comprehensive AI-powered CV analysis
        Returns full analysis with strengths, weaknesses, improvements, and career recommendations
        """
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key:
            return self._basic_advanced_analysis(cv_text)
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            prompt = f"""
You are an expert career consultant and CV specialist. Perform a comprehensive analysis of this CV.

CV Content:
{cv_text}

Provide a detailed analysis in the following JSON format:
{{
    "full_analysis": "2-3 paragraph executive summary of the CV's overall quality, positioning, and potential",
    "strengths": [
        "Strength 1 with specific examples",
        "Strength 2 with specific examples",
        "Strength 3 with specific examples",
        "Strength 4 with specific examples",
        "Strength 5 with specific examples"
    ],
    "weaknesses": [
        "Weakness 1 with specific examples",
        "Weakness 2 with specific examples", 
        "Weakness 3 with specific examples",
        "Weakness 4 with specific examples"
    ],
    "improvement_suggestions": [
        "Specific actionable suggestion 1",
        "Specific actionable suggestion 2",
        "Specific actionable suggestion 3",
        "Specific actionable suggestion 4",
        "Specific actionable suggestion 5"
    ],
    "career_recommendations": [
        "Career path recommendation 1",
        "Career path recommendation 2",
        "Career path recommendation 3",
        "Industry positioning advice",
        "Skill development priority"
    ]
}}

Be specific, actionable, and professional. Use real examples from the CV.
"""
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert career consultant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            logger.info(f"Advanced CV analysis completed successfully")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in advanced analysis: {e}")
            return self._basic_advanced_analysis(cv_text)
        except Exception as e:
            logger.error(f"Advanced CV analysis error: {e}")
            return self._basic_advanced_analysis(cv_text)
    
    def _basic_advanced_analysis(self, cv_text: str) -> dict:
        """Fallback analysis when OpenAI is not available"""
        word_count = len(cv_text.split())
        
        return {
            "full_analysis": f"This CV contains approximately {word_count} words. While detailed AI analysis is currently unavailable, the CV appears to have standard professional content. For a comprehensive analysis, please ensure OpenAI API is configured.",
            "strengths": [
                "Professional formatting detected",
                "Appropriate length for industry standards",
                "Contains relevant sections"
            ],
            "weaknesses": [
                "Detailed analysis requires AI service",
                "Unable to assess content quality without full analysis"
            ],
            "improvement_suggestions": [
                "Enable AI analysis for detailed feedback",
                "Ensure clear contact information",
                "Use action verbs for achievements",
                "Quantify accomplishments with metrics"
            ],
            "career_recommendations": [
                "Comprehensive career guidance requires full AI analysis",
                "Consider industry-specific CV formats",
                "Keep skills section updated"
            ]
        }

    def chat_about_cv_llama(self, cv_text: str, user_message: str, analysis) -> str:
        """
        Chat with Llama 3.1 about CV (via Ollama)
        Provides conversational CV improvement assistance
        """
        try:
            import requests
            
            # Check if Ollama is running
            ollama_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
            
            # Get previous chat messages for context
            previous_messages = []
            for msg in analysis.chat_messages.order_by('created_at')[:10]:
                previous_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Build context from analysis
            context_parts = []
            context_parts.append(f"Full Analysis: {analysis.full_analysis}")
            
            if analysis.strengths:
                context_parts.append(f"Strengths: {', '.join(analysis.strengths[:5])}")
            
            if analysis.weaknesses:
                context_parts.append(f"Weaknesses: {', '.join(analysis.weaknesses[:3])}")
            
            system_prompt = f"""You are an expert CV consultant AI. You have analyzed the user's CV and are helping them improve it.

Analysis Context:
{chr(10).join(context_parts)}

CV Excerpt (first 1500 chars):
{cv_text[:1500]}

Provide helpful, specific, and actionable advice. Be conversational and supportive."""
            
            # Build conversation history
            messages = []
            if previous_messages:
                for msg in previous_messages[-5:]:  # Last 5 messages for context
                    messages.append(msg)
            
            # Prepare Ollama request
            payload = {
                "model": "llama3.1",
                "messages": [
                    {"role": "system", "content": system_prompt}
                ] + messages + [
                    {"role": "user", "content": user_message}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            }
            
            response = requests.post(
                f"{ollama_url}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['message']['content'].strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._fallback_chat_response(user_message)
                
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama not available, using fallback")
            return "Llama 3.1 chatbot is currently unavailable. Please ensure Ollama is running with `ollama run llama3.1`"
        except Exception as e:
            logger.error(f"Llama chat error: {e}")
            return self._fallback_chat_response(user_message)
    
    def _fallback_chat_response(self, user_message: str) -> str:
        """Fallback response when AI chat is unavailable"""
        responses = {
            "improve": "To improve your CV, focus on: 1) Quantifying achievements with metrics, 2) Using action verbs, 3) Tailoring content to target roles, 4) Keeping formatting clean and ATS-friendly.",
            "skills": "Highlight both technical and soft skills. Place the most relevant skills for your target role at the top of your skills section.",
            "experience": "Structure experience with: Company, Role, Dates, then 3-5 bullet points showcasing achievements with metrics.",
            "format": "Use a clean, single-column layout. Stick to standard fonts (Arial, Calibri). Use consistent spacing and bullet points."
        }
        
        user_lower = user_message.lower()
        for key, response in responses.items():
            if key in user_lower:
                return response
        
        return "I can help you with CV improvements, formatting, skills presentation, and experience descriptions. What specific aspect would you like to discuss?"
