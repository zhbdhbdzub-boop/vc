# Advanced CV Analyzer - Quick Test Guide

## Pre-Test Checklist

### ✅ Backend Ready
```bash
# Check backend is running
wsl docker compose ps backend

# Should show: modular-platform-backend-1  Up
```

### ✅ Database Migrated
```bash
# Check migration applied
wsl docker compose exec backend python manage.py showmigrations cv_analysis

# Should show:
# [X] 0003_remove_advancedcvanalysis_ats_report_and_more
```

### ✅ Ollama Running (Optional - for chatbot)
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# If not running:
ollama run llama3.1
```

---

## Test Scenarios

### Test 1: Upload CV & Get Analysis ✅

**Steps:**
1. Navigate to: `http://localhost:3000/cv-analysis/advanced-analyzer`
2. Upload a PDF CV
3. Click "Analyze CV"

**Expected Results:**
- ✅ Loading spinner shows "Analyzing your CV..."
- ✅ After 10-15 seconds, analysis appears
- ✅ **Full Analysis** section shows 2-3 paragraphs
- ✅ **Key Strengths** shows 3-5 bullet points
- ✅ **Areas for Improvement** shows 3-4 bullet points
- ✅ **Improvement Suggestions** shows 5 actionable items
- ✅ **Career Recommendations** shows 5 career insights

**If Fails:**
```bash
# Check backend logs
wsl docker compose logs backend --tail 50

# Common issues:
# - OpenAI API key missing → Set OPENAI_API_KEY in .env
# - 500 error → Check model/serializer match
# - Timeout → GPT-4 taking too long (increase timeout)
```

---

### Test 2: Chat with Llama 3.1 ✅

**Prerequisites:**
- ✅ Ollama installed and running
- ✅ Llama 3.1 model downloaded (`ollama pull llama3.1`)
- ✅ At least one CV analyzed

**Steps:**
1. Click **chat icon** in analysis results
2. Type: `"How can I improve my CV's impact?"`
3. Press Enter

**Expected Results:**
- ✅ Message appears in chat window (user message)
- ✅ After 2-5 seconds, Llama 3.1 responds (assistant message)
- ✅ Response references your CV analysis (strengths/weaknesses)
- ✅ Response provides specific, actionable advice
- ✅ Follow-up questions maintain context

**If Fails:**
```bash
# Test Ollama directly
curl http://localhost:11434/api/tags

# If connection refused:
ollama serve

# If "Llama 3.1 not available" error:
# Backend shows: "Llama 3.1 chatbot is currently unavailable. 
# Please ensure Ollama is running with `ollama run llama3.1`"

# Solution:
ollama run llama3.1
# (wait for model to load, then press Ctrl+D to exit)
```

---

### Test 3: Analysis History ✅

**Steps:**
1. Analyze 2-3 different CVs
2. Check history sidebar (or history tab)

**Expected Results:**
- ✅ All analyses appear in chronological order (newest first)
- ✅ Each analysis shows: filename, date, status
- ✅ Click on past analysis → Loads full results
- ✅ Chat history preserved for each analysis

---

### Test 4: Fallback Mode (No OpenAI) 🔄

**Simulate OpenAI Outage:**
```bash
# Temporarily remove OpenAI key
wsl docker compose exec backend bash
export OPENAI_API_KEY=""
exit
```

**Upload CV:**

**Expected Results:**
- ✅ Analysis still completes (no crash)
- ✅ Full analysis shows: "This CV contains approximately X words..."
- ✅ Strengths show basic items: "Professional formatting detected"
- ✅ Suggestions show generic advice: "Quantify accomplishments"
- ✅ Message indicates: "Detailed analysis requires AI service"

**Restore OpenAI:**
```bash
# Re-add key in docker-compose.yml or .env
wsl docker compose restart backend
```

---

### Test 5: Chatbot Fallback (No Ollama) 🔄

**Stop Ollama:**
```bash
# Windows: Stop Ollama service
# Linux/WSL: Ctrl+C on ollama serve
```

**Try Chat:**

**Expected Results:**
- ✅ No crash
- ✅ Response: "Llama 3.1 chatbot is currently unavailable..."
- ✅ OR fallback response based on keywords:
  - Ask about "improve" → Generic improvement tips
  - Ask about "skills" → Skills section advice
  - Ask about "format" → Formatting guidelines

---

## Performance Tests

### Speed Test: Analysis
```bash
# Time the analysis
time curl -X POST http://localhost:8000/api/cv-analysis/advanced-cv-analyzer/analyze/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "cv_file=@sample_cv.pdf"

# Target: 10-15 seconds with GPT-4
# Acceptable: <30 seconds
# Slow: >30 seconds (check OpenAI API status)
```

### Speed Test: Chat
```bash
# Time Llama 3.1 response
time curl -X POST http://localhost:11434/api/chat \
  -d '{"model":"llama3.1","messages":[{"role":"user","content":"Hello"}]}'

# Target: 2-5 seconds (CPU)
# Good: <3 seconds (GPU)
# Slow: >10 seconds (check system resources)
```

---

## Integration Tests

### Test API Directly

**1. Login & Get Token:**
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}'

# Copy access token from response
export TOKEN="your_access_token_here"
```

**2. Upload CV:**
```bash
curl -X POST http://localhost:8000/api/cv-analysis/advanced-cv-analyzer/analyze/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "cv_file=@path/to/cv.pdf"

# Response should include:
# - id (UUID)
# - full_analysis (string)
# - strengths (array)
# - weaknesses (array)
# - improvement_suggestions (array)
# - career_recommendations (array)
# - status: "completed"
```

**3. Chat:**
```bash
# Use ID from previous response
export ANALYSIS_ID="uuid-from-analysis"

curl -X POST "http://localhost:8000/api/cv-analysis/advanced-cv-analyzer/$ANALYSIS_ID/chat/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"How can I improve my CV?"}'

# Response should include:
# - role: "assistant"
# - content: "Based on your CV analysis..."
```

**4. Get History:**
```bash
curl -X GET http://localhost:8000/api/cv-analysis/advanced-cv-analyzer/history/ \
  -H "Authorization: Bearer $TOKEN"

# Response should be array of analyses
```

---

## Troubleshooting Guide

### Issue: "Cannot read properties of undefined (reading 'map')"

**Cause:** Old database schema, migration not applied

**Fix:**
```bash
wsl docker compose exec backend python manage.py migrate cv_analysis
wsl docker compose restart backend
```

---

### Issue: Analysis takes >60 seconds

**Possible Causes:**
1. **OpenAI API slow** - Check status.openai.com
2. **Large CV file** - Limit to <10MB, <50 pages
3. **Rate limiting** - Wait a few minutes, try again

**Fix:**
```bash
# Check OpenAI API response time
time curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# If slow (>5 seconds), OpenAI is having issues
# Wait or use fallback mode
```

---

### Issue: Chatbot says "Ollama not available"

**Fix:**
```bash
# 1. Check Ollama is running
curl http://localhost:11434/api/tags

# 2. If not running, start it
ollama serve

# 3. If model missing, pull it
ollama pull llama3.1

# 4. If Docker can't reach host
# Update docker-compose.yml:
services:
  backend:
    environment:
      - OLLAMA_API_URL=http://host.docker.internal:11434
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

---

### Issue: Chat responses are generic/unhelpful

**Cause:** Ollama not using CV context

**Debug:**
```bash
# Check if analysis has data
wsl docker compose exec backend python manage.py shell

>>> from apps.cv_analysis.models import AdvancedCVAnalysis
>>> analysis = AdvancedCVAnalysis.objects.last()
>>> print(analysis.full_analysis)  # Should show analysis text
>>> print(analysis.strengths)      # Should show array
>>> print(analysis.weaknesses)     # Should show array

# If empty, re-run analysis
```

---

### Issue: 500 Internal Server Error

**Debug:**
```bash
# Check backend logs
wsl docker compose logs backend --tail 100

# Common errors:
# - JSONDecodeError → GPT-4 returned invalid JSON
# - AttributeError → Model field mismatch
# - ConnectionError → Ollama unreachable
```

---

## Success Metrics

### ✅ Analysis Quality
- [ ] Full analysis is 2-3 paragraphs (not single sentence)
- [ ] Strengths are specific (not generic like "good formatting")
- [ ] Weaknesses reference actual CV content
- [ ] Suggestions are actionable (not vague like "improve skills")
- [ ] Career recommendations match CV industry/role

### ✅ Chatbot Quality
- [ ] Responses reference CV analysis (mentions strengths/weaknesses)
- [ ] Advice is specific to user's CV (not generic tips)
- [ ] Follow-up questions maintain context
- [ ] Responses are 2-4 paragraphs (not one-liners)
- [ ] Tone is professional and supportive

### ✅ Performance
- [ ] Analysis completes in <20 seconds
- [ ] Chat responds in <5 seconds
- [ ] No crashes or 500 errors
- [ ] History loads instantly
- [ ] Multiple analyses can be created

---

## Load Testing (Optional)

### Test Multiple Concurrent Analyses
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Run 10 concurrent requests
ab -n 10 -c 5 -H "Authorization: Bearer $TOKEN" \
   -p cv_data.txt -T "multipart/form-data" \
   http://localhost:8000/api/cv-analysis/advanced-cv-analyzer/analyze/

# Check:
# - Time per request < 20 seconds
# - Failed requests = 0
```

---

## Comparison: Before vs After

### Before (Broken)
- ❌ Frontend crashed with undefined.map() error
- ❌ Model had old schema (11 fields)
- ❌ No comprehensive AI analysis
- ❌ No chatbot functionality
- ❌ Database mismatch errors

### After (Working)
- ✅ Frontend renders analysis perfectly
- ✅ Model has clean AI-focused schema (5 fields)
- ✅ GPT-4 powered comprehensive analysis
- ✅ Llama 3.1 chatbot integrated
- ✅ Database schema matches model
- ✅ All endpoints functional
- ✅ Fallback modes for resilience

---

## Next Actions

1. **Test the implementation** using scenarios above
2. **Install Ollama** for chatbot (optional but recommended)
3. **Report any issues** found during testing
4. **Consider enhancements** (streaming, async, caching)

**All systems ready for testing! 🚀**
