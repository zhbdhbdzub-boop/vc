# 🚀 Quick Setup Guide for New Features

## Prerequisites
- Project already running (if not, run `./setup.ps1` first)
- Backend and frontend services operational

---

## Step 1: Install New Dependencies

### Frontend Dependencies:
```powershell
cd frontend
npm install lucide-react
```

---

## Step 2: Backend Configuration

### Add Code Assessment App:
Edit `backend/config/settings.py` and add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'apps.code_assessment',  # Add this line
]
```

### Run Migrations:
```powershell
cd backend
python manage.py makemigrations code_assessment
python manage.py migrate
```

---

## Step 3: Install Docker (for Code Execution)

The Code Assessment module uses Docker for safe code execution. If you don't have Docker installed:

### Windows:
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Verify installation: `docker --version`

### Alternative (Development):
If you can't install Docker, the code executor will use a mock execution mode (less secure, for dev only).

---

## Step 4: Pull Required Docker Images (Optional)

For faster first-time code execution:

```powershell
docker pull python:3.11-alpine
docker pull node:18-alpine
docker pull openjdk:17-alpine
```

---

## Step 5: Create Sample Data

### 1. Create a Coding Problem (via Django Admin):

```powershell
# Access admin panel at http://localhost:8000/admin
```

Navigate to: **Code Assessment > Coding Problems > Add Coding Problem**

**Example Problem:**
- Title: "Two Sum"
- Slug: "two-sum"
- Description: "Given an array of integers and a target, return indices of two numbers that add up to target."
- Difficulty: Easy
- Category: Arrays
- Max Score: 100
- Time Limit: 300 seconds

**Add Test Cases:**
- Input: `[2,7,11,15], 9`
- Expected Output: `[0,1]`
- Is Sample: ✓

### 2. Create Interview Templates:

Already available from Sprint 9-10 backend. Access via:
- http://localhost:8000/api/interviews/templates/

### 3. Test CV Upload:

Prepare a sample CV (PDF, DOCX, or TXT) to test the upload feature.

---

## Step 6: Access New Features

### CV Analysis:
- **Upload**: http://localhost:3000/cv-analysis/upload
- **My CVs**: http://localhost:3000/cv-analysis/cvs

### Interview Simulation:
- **Interviews**: http://localhost:3000/interviews

### Code Assessment (Admin):
- **Problems**: http://localhost:8000/admin/code_assessment/codingproblem/

---

## Step 7: Test the Features

### Test CV Analysis:
1. Go to CV Upload page
2. Drag and drop a CV file (or click to browse)
3. Wait for processing (status will update automatically)
4. Click "View Analysis" when complete
5. Explore skills, experience, education tabs
6. Click "Match Jobs" to find relevant positions

### Test Interview:
1. Go to Interviews page
2. Click "Start Interview" on any template
3. Answer questions (timer starts automatically)
4. Submit answers and progress through questions
5. Complete interview to see detailed results
6. View AI-generated feedback and recommendations

### Test Code Assessment (Backend):
1. Go to Django Admin
2. Create a coding problem with test cases
3. API is ready at `/api/code-assessment/problems/`
4. Frontend integration coming in next sprint

---

## Troubleshooting

### Issue: React errors about missing modules
**Solution:**
```powershell
cd frontend
npm install
```

### Issue: Django migration errors
**Solution:**
```powershell
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Issue: Docker not available
**Solution:** The code executor will fall back to mock mode (less secure). Install Docker for production use.

### Issue: CV processing stuck in "processing"
**Solution:** 
- Check Celery worker is running
- Check Redis is running
- Check OpenAI API key is set in `.env`

### Issue: Interview questions not loading
**Solution:**
- Ensure you have interview templates created
- Check backend logs for errors
- Verify API is accessible at http://localhost:8000/api/interviews/

---

## Environment Variables Checklist

Ensure these are set in `backend/.env`:

```env
# Required for AI features
OPENAI_API_KEY=sk-...

# Required for billing
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://redis:6379/0
```

---

## Next Steps

After setup:

1. **Create test data** through Django admin
2. **Test each feature** to ensure everything works
3. **Review the code** to understand the architecture
4. **Continue to Sprint 15-16** (Code Assessment Frontend)

---

## Quick Commands Reference

### Start Services:
```powershell
docker-compose up -d
```

### View Logs:
```powershell
# Backend
docker-compose logs -f backend

# Frontend
docker-compose logs -f frontend

# Celery
docker-compose logs -f celery
```

### Restart Services:
```powershell
docker-compose restart
```

### Stop Services:
```powershell
docker-compose down
```

### Access Django Shell:
```powershell
docker-compose exec backend python manage.py shell
```

---

## Support

If you encounter any issues:

1. Check the logs: `docker-compose logs -f`
2. Verify all services are running: `docker-compose ps`
3. Check the documentation in `/docs`
4. Review `IMPLEMENTATION_STATUS.md` for feature details

---

**Ready to continue with more sprints!** 🚀
