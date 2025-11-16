"""
Job scraping service using SerpAPI for Google Jobs
Matches CV skills with real job postings
"""
import os
import re
import json
import logging
import requests
import urllib.parse
from typing import List, Dict, Any, Optional
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger(__name__)

# Country mapping for Google Jobs (gl parameter)
COUNTRY_GL = {
    "tunisia": "tn", "tunisie": "tn",
    "maroc": "ma", "morocco": "ma",
    "algeria": "dz", "algerie": "dz", "algérie": "dz",
    "france": "fr",
    "canada": "ca",
    "usa": "us", "united states": "us",
    "germany": "de", "allemagne": "de",
    "spain": "es", "espagne": "es",
    "italy": "it", "italie": "it",
    "belgium": "be", "belgique": "be",
    "switzerland": "ch", "suisse": "ch",
    "qatar": "qa",
    "saudi arabia": "sa", "arabie saoudite": "sa",
    "uae": "ae", "emirates": "ae",
    "england": "gb", "uk": "gb",
    "united kingdom": "gb", "royaume-uni": "gb",
}


class JobScraperService:
    """Service for scraping job postings from Google Jobs via SerpAPI"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'SERPAPI_API_KEY', None)
        self.base_url = "https://serpapi.com/search.json"
        self.ollama_url = getattr(settings, 'OLLAMA_API_URL', 'http://localhost:11434')
        self.model_name = "llama3.1:8b"
    
    @staticmethod
    def get_gl_code(country: str) -> Optional[str]:
        """Get Google location code for country"""
        if not country:
            return None
        return COUNTRY_GL.get(country.lower().strip(), None)
    
    def build_query_text(self, job_title: str, seniority: str = "", country: str = "") -> str:
        """Build search query text for job search"""
        # Clean job title
        job_title = (job_title or "").replace("/", " ").replace("  ", " ").strip()
        
        # Clean seniority
        if isinstance(seniority, str) and "|" in seniority:
            seniority_clean = seniority.split("|")[-1].strip()
        else:
            seniority_clean = (seniority or "").strip()
        
        # Build query
        parts = [job_title]
        if seniority_clean:
            parts.append(f"| {seniority_clean}")
        if country:
            parts.append(country)
        
        query_text = " ".join(p for p in parts if p).strip()
        return query_text
    
    def scrape_google_jobs(
        self, 
        job_title: str, 
        country: str, 
        seniority: str = "",
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Scrape Google Jobs for a specific job title and country"""
        
        gl = self.get_gl_code(country)
        if not gl:
            logger.warning(f"Country '{country}' not supported")
            return []
        
        if not self.api_key:
            logger.error("SERPAPI_API_KEY not configured")
            return []
        
        query_text = self.build_query_text(job_title, seniority, country)
        
        params = {
            "engine": "google_jobs",
            "q": query_text,
            "hl": "fr",
            "gl": gl,
            "api_key": self.api_key,
        }
        
        try:
            resp = requests.get(self.base_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            jobs = data.get("jobs_results", [])[:max_results]
            results = []
            
            for j in jobs:
                # Extract full description from highlights
                highlights = []
                if isinstance(j.get("job_highlights"), list):
                    for block in j["job_highlights"]:
                        if "items" in block:
                            highlights.extend(block["items"])
                
                full_description = "\n".join(highlights) if highlights else None
                
                # Get apply link
                apply_link = None
                if isinstance(j.get("apply_options"), list) and j["apply_options"]:
                    apply_link = j["apply_options"][0].get("link")
                
                # Google job URL
                google_job_url = None
                if j.get("job_id"):
                    google_job_url = f"https://www.google.com/search?gl={gl}&q=google+job+{j['job_id']}"
                
                results.append({
                    "title": j.get("title"),
                    "company": j.get("company_name"),
                    "location": j.get("location"),
                    "via": j.get("via"),
                    "posted": j.get("detected_extensions", {}).get("posted_at"),
                    "short_description": j.get("description"),
                    "full_description": full_description,
                    "apply_link": apply_link,
                    "google_job_url": google_job_url,
                    "query_used": query_text,
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error scraping jobs: {e}")
            return []
    
    def call_llama(self, messages: List[Dict[str, str]]) -> str:
        """Call Llama 3.1 via Ollama API"""
        url = f"{self.ollama_url}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            
            if isinstance(data, dict) and "message" in data:
                return data["message"]["content"]
            return str(data)
        except Exception as e:
            logger.error(f"Error calling Llama: {e}")
            raise
    
    def extract_json_from_llm(self, content: str) -> Dict[str, Any]:
        """Extract JSON from LLM output"""
        try:
            return json.loads(content)
        except Exception:
            pass
        
        # Try to isolate JSON block
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = content[start : end + 1]
            try:
                return json.loads(json_str)
            except Exception:
                pass
        
        return {}
    
    def extract_jobs_from_cv_fallback(self, cv_text: str) -> List[Dict[str, Any]]:
        """Fallback method: Extract job titles from CV without AI"""
        jobs = []
        
        # Common job title patterns
        job_patterns = [
            r"(?i)\b(software|web|mobile|backend|frontend|full[\s-]?stack|data|machine learning|ai|devops|cloud)\s+(developer|engineer|architect|specialist)\b",
            r"(?i)\b(product|project|program)\s+manager\b",
            r"(?i)\b(data|business|financial|system)\s+analyst\b",
            r"(?i)\b(ui|ux|graphic|web)\s+designer\b",
            r"(?i)\b(marketing|sales|hr|operations)\s+(manager|specialist|coordinator)\b",
            r"(?i)\btech(?:nical)?\s+lead\b",
            r"(?i)\bscrum\s+master\b",
            r"(?i)\bqa\s+engineer\b",
        ]
        
        # Extract all potential job titles
        found_titles = set()
        for pattern in job_patterns:
            matches = re.finditer(pattern, cv_text)
            for match in matches:
                title = match.group(0).strip()
                found_titles.add(title.title())
        
        # Analyze experience level from CV
        cv_lower = cv_text.lower()
        years_match = re.search(r"(\d+)\+?\s*(?:years?|ans?)\s+(?:of\s+)?(?:experience|exp)", cv_lower)
        years_exp = int(years_match.group(1)) if years_match else 0
        
        if years_exp >= 5:
            seniority = "Senior"
            confidence = 85
        elif years_exp >= 2:
            seniority = "Intermediate"
            confidence = 80
        else:
            seniority = "Junior"
            confidence = 75
        
        # Determine domain from skills
        domain = "Technology"
        if any(word in cv_lower for word in ["python", "java", "javascript", "react", "django"]):
            domain = "Software Development"
        elif any(word in cv_lower for word in ["data", "analytics", "sql", "tableau"]):
            domain = "Data & Analytics"
        elif any(word in cv_lower for word in ["marketing", "seo", "social media"]):
            domain = "Marketing"
        
        # Create job entries from found titles
        for title in found_titles:
            jobs.append({
                "title": title,
                "domain": domain,
                "seniority": seniority,
                "confidence": confidence
            })
        
        # If no titles found, create generic ones based on keywords
        if not jobs:
            if "developer" in cv_lower or "engineer" in cv_lower:
                jobs.append({
                    "title": "Software Developer",
                    "domain": "Software Development",
                    "seniority": seniority,
                    "confidence": 70
                })
            if "data" in cv_lower and ("analyst" in cv_lower or "science" in cv_lower):
                jobs.append({
                    "title": "Data Analyst",
                    "domain": "Data & Analytics",
                    "seniority": seniority,
                    "confidence": 70
                })
        
        return jobs[:15]  # Limit to 15 jobs
    
    def get_possible_jobs_from_cv(self, cv_text: str, max_chars: int = 8000) -> List[Dict[str, Any]]:
        """Analyze CV and extract possible job titles using Llama (with fallback)"""
        
        # Truncate CV text if too long
        cv_text = cv_text[:max_chars]
        
        # Try Llama first
        system_msg = {
            "role": "system",
            "content": (
                "You are an expert in recruitment, HR and career guidance. "
                "You analyze CVs and suggest only realistic job titles "
                "that the person can do NOW based on their skills and experience."
            ),
        }
        
        user_msg = {
            "role": "user",
            "content": f"""
Analyze the following CV and suggest a list of possible jobs/positions
that this person can occupy NOW (based on their skills, experience, education).

IMPORTANT INSTRUCTIONS:
- Give between 5 and 15 job titles maximum.
- Vary the titles but stay realistic and coherent.
- Don't invent jobs that have no relation to the profile.
- Indicate seniority level (Junior / Intermediate / Senior).
- Give a confidence score between 0 and 100.

Return STRICTLY a JSON in this format:

{{
  "possible_jobs": [
    {{
      "title": "Job title",
      "domain": "Domain or sector (e.g., Data, Backend, Marketing...)",
      "seniority": "Junior | Intermediate | Senior",
      "confidence": 0-100
    }}
  ]
}}

CV TO ANALYZE:
\"\"\"{cv_text}\"\"\"
""",
        }
        
        messages = [system_msg, user_msg]
        
        try:
            llm_output = self.call_llama(messages)
            data = self.extract_json_from_llm(llm_output)
            jobs = data.get("possible_jobs", [])
            
            if not isinstance(jobs, list):
                logger.warning("LLM output doesn't contain valid 'possible_jobs' list")
                return []
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting possible jobs from CV: {e}")
            logger.info("Falling back to rule-based extraction...")
            return self.extract_jobs_from_cv_fallback(cv_text)
    
    def scrape_jobs_for_cv(
        self,
        cv_text: str,
        country: str,
        min_confidence: int = 70,
        max_jobs_per_title: int = 5
    ) -> Dict[str, Any]:
        """
        Main function: Analyze CV, get possible jobs, and scrape real job postings
        
        Returns:
            {
                'possible_jobs': [...],  # Jobs extracted from CV
                'job_postings': [...],   # Real job postings found
                'summary': {...}         # Statistics
            }
        """
        
        # Step 1: Get possible jobs from CV using Llama
        logger.info("Analyzing CV to extract possible job titles...")
        possible_jobs = self.get_possible_jobs_from_cv(cv_text)
        
        if not possible_jobs:
            return {
                'possible_jobs': [],
                'job_postings': [],
                'summary': {
                    'total_possible_jobs': 0,
                    'total_postings_found': 0,
                    'country': country
                }
            }
        
        # Step 2: Scrape job postings for each possible job
        logger.info(f"Found {len(possible_jobs)} possible jobs. Scraping postings...")
        all_postings = []
        jobs_scraped = 0
        
        for job in possible_jobs:
            title = job.get("title")
            seniority = job.get("seniority", "")
            domain = job.get("domain", "")
            confidence = job.get("confidence", 0)
            
            if not title or confidence < min_confidence:
                continue
            
            logger.info(f"Scraping: {title} [{domain} | {seniority}] (confidence={confidence})")
            
            postings = self.scrape_google_jobs(
                job_title=title,
                country=country,
                seniority=seniority,
                max_results=max_jobs_per_title
            )
            
            # Add context from CV analysis
            for posting in postings:
                posting["source_title"] = title
                posting["source_domain"] = domain
                posting["source_seniority"] = seniority
                posting["source_confidence"] = confidence
            
            all_postings.extend(postings)
            jobs_scraped += 1
        
        # Remove duplicates
        unique_postings = []
        seen = set()
        for posting in all_postings:
            key = (posting.get("title"), posting.get("company"), posting.get("location"))
            if key not in seen:
                seen.add(key)
                unique_postings.append(posting)
        
        return {
            'possible_jobs': possible_jobs,
            'job_postings': unique_postings,
            'summary': {
                'total_possible_jobs': len(possible_jobs),
                'jobs_scraped': jobs_scraped,
                'total_postings_found': len(unique_postings),
                'country': country,
                'min_confidence': min_confidence
            }
        }
