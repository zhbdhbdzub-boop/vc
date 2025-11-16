# CV-Job Matcher with Real Job Scraping

## Overview

The CV-Job Matcher module now includes advanced functionality that:
1. **Analyzes your CV** using Llama 3.1 AI to extract possible job titles
2. **Scrapes real job postings** from Google Jobs via SerpAPI
3. **Matches jobs by country** - you select which country to search

## How It Works

### Step 1: CV Analysis with Llama 3.1
- Reads your CV (PDF, DOCX, or TXT)
- Uses Llama 3.1 AI (local Ollama) to identify 5-15 possible job titles
- Extracts domain, seniority level, and confidence score for each job

### Step 2: Job Scraping with SerpAPI
- Takes the identified job titles
- Searches Google Jobs for real openings in your selected country
- Returns actual job postings with:
  - Company name
  - Location
  - Job description
  - Apply link
  - Posting date

### Step 3: Smart Filtering
- Only searches for jobs with confidence score ≥ 70%
- Removes duplicate postings
- Returns up to 5 jobs per job title

## API Endpoint

**POST** `/api/cv/{cv_id}/find_jobs/`

### Request Body
```json
{
  "country": "Tunisia",           // Required: Target country
  "min_confidence": 70,           // Optional: Minimum confidence (default: 70)
  "max_jobs_per_title": 5         // Optional: Max jobs per title (default: 5)
}
```

### Supported Countries
- **North Africa**: Tunisia, Morocco, Algeria
- **Europe**: France, Germany, Spain, Italy, Belgium, Switzerland, UK
- **Middle East**: Qatar, Saudi Arabia, UAE
- **North America**: USA, Canada

### Response Example
```json
{
  "possible_jobs": [
    {
      "title": "Python Developer",
      "domain": "Software Development",
      "seniority": "Intermediate",
      "confidence": 85
    },
    {
      "title": "Data Analyst",
      "domain": "Data Science",
      "seniority": "Junior",
      "confidence": 78
    }
  ],
  "job_postings": [
    {
      "title": "Python Backend Developer",
      "company": "Tech Company",
      "location": "Tunis, Tunisia",
      "via": "LinkedIn",
      "posted": "2 days ago",
      "short_description": "Looking for a Python developer...",
      "full_description": "Full job requirements and description...",
      "apply_link": "https://...",
      "google_job_url": "https://...",
      "source_title": "Python Developer",
      "source_domain": "Software Development",
      "source_seniority": "Intermediate",
      "source_confidence": 85
    }
  ],
  "summary": {
    "total_possible_jobs": 8,
    "jobs_scraped": 6,
    "total_postings_found": 24,
    "country": "Tunisia",
    "min_confidence": 70
  }
}
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# SerpAPI Key (get from https://serpapi.com/)
SERPAPI_API_KEY=your_serpapi_key_here

# Ollama URL (default: http://ollama:11434)
OLLAMA_API_URL=http://ollama:11434
```

### Get SerpAPI Key
1. Sign up at https://serpapi.com/
2. Free tier includes 100 searches/month
3. Paid plans start at $50/month for 5000 searches

## Usage Example

### Using curl
```bash
curl -X POST http://localhost:8000/api/cv/123/find_jobs/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "country": "Tunisia",
    "min_confidence": 75,
    "max_jobs_per_title": 3
  }'
```

### Using Python
```python
import requests

url = "http://localhost:8000/api/cv/123/find_jobs/"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "country": "Tunisia",
    "min_confidence": 75,
    "max_jobs_per_title": 3
}

response = requests.post(url, headers=headers, json=data)
results = response.json()

print(f"Found {results['summary']['total_postings_found']} jobs!")
for job in results['job_postings'][:5]:
    print(f"- {job['title']} at {job['company']}")
```

## Features

### 🎯 Smart Job Extraction
- AI analyzes your CV to identify realistic job opportunities
- Considers your skills, experience, and education
- Provides confidence scores for each job match

### 🌍 Global Job Search
- Search in 20+ countries
- Get localized job results
- Real-time job postings from Google Jobs

### 📊 Detailed Results
- Full job descriptions
- Direct apply links
- Company information
- Location and posting date

### 🔒 Privacy & Security
- Your CV is analyzed locally (Ollama)
- Only job titles are sent to SerpAPI
- Your full CV text never leaves your server

## Error Handling

### Common Errors

**"Country is required"**
- You must provide a country parameter

**"CV file not found or inaccessible"**
- The CV file may have been deleted or moved
- Re-upload the CV

**"SERPAPI_API_KEY not configured"**
- Add your SerpAPI key to the .env file
- Restart the backend

**"Country 'XYZ' not supported"**
- Check the supported countries list above
- Use country name in English

## Performance

- CV Analysis: ~10-30 seconds (Llama 3.1)
- Job Scraping: ~2-5 seconds per job title
- Total: ~30-60 seconds for complete analysis

## Limitations

- SerpAPI has rate limits (100 free searches/month)
- Llama 3.1 requires Ollama to be running
- Job results depend on Google Jobs availability in your country

## Pricing

This feature is included in the **CV-Job Matcher** module:
- **Monthly**: $9.99/month
- **Annual**: $99.90/year
- **Lifetime**: $199.00 one-time

Includes:
- 1 FREE job match
- Unlimited CV-to-job matching
- Real-time job search
- AI-powered analysis

## Next Steps

1. Ensure Ollama is running with Llama 3.1:
   ```bash
   wsl docker compose exec ollama ollama pull llama3.1:8b
   ```

2. Add SerpAPI key to `.env`:
   ```bash
   SERPAPI_API_KEY=your_key_here
   ```

3. Restart backend:
   ```bash
   wsl docker compose restart backend
   ```

4. Test the endpoint with your CV!
