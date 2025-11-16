# Llama 3.1 Chatbot Setup Guide

## ✅ Docker Setup (Recommended - Already Done!)

Llama 3.1 is now integrated into your Docker setup! Everything is ready to use.

### What Was Configured:
1. ✅ Added Ollama service to `docker-compose.yml`
2. ✅ Pulled Llama 3.1 8B model (~5GB)
3. ✅ Connected backend to Ollama via internal Docker network
4. ✅ All services running and tested

### Quick Test:
```bash
# Check Ollama is running
wsl docker compose ps ollama

# Check model is available
wsl docker compose exec ollama ollama list

# Test API
wsl curl http://localhost:11434/api/tags
```

### Start Using Right Now:
1. Go to `http://localhost:3000/cv-analysis/advanced-analyzer`
2. Upload a CV and analyze it
3. Click the **chat icon** 💬
4. Ask: "How can I improve my CV?"
5. Llama 3.1 responds in 2-5 seconds! 🎉

---

## Overview
The Advanced CV Analyzer module now includes an AI-powered chatbot using **Meta's Llama 3.1** via Ollama. This provides conversational CV improvement assistance with privacy and cost benefits.

## Why Llama 3.1?
- **Free & Local**: Runs on your machine, no API costs
- **Privacy**: Your CV data never leaves your system
- **Fast**: Instant responses with local deployment
- **Smart**: Llama 3.1 8B model is highly capable for CV consulting

## Installation Options

### Option 1: Ollama (Recommended - Easiest)

#### Step 1: Install Ollama
**Windows:**
```powershell
# Download and install from: https://ollama.ai/download
# Or use winget:
winget install Ollama.Ollama
```

**Linux/WSL:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Mac:**
```bash
brew install ollama
```

#### Step 2: Pull Llama 3.1 Model
```bash
ollama run llama3.1
```

This will:
- Download Llama 3.1 8B model (~4.7GB)
- Start the Ollama server on `http://localhost:11434`
- Run a test conversation (type `/bye` to exit)

#### Step 3: Verify Installation
```bash
curl http://localhost:11434/api/tags
```

You should see `llama3.1` in the list of models.

#### Step 4: Configure Backend (Optional)
By default, the backend expects Ollama at `http://localhost:11434`. To customize:

**Edit `backend/.env` or `docker-compose.yml`:**
```env
OLLAMA_API_URL=http://localhost:11434
```

For Docker:
```yaml
services:
  backend:
    environment:
      - OLLAMA_API_URL=http://host.docker.internal:11434
```

### Option 2: Groq API (Cloud - Faster)

Groq offers blazing-fast Llama 3.1 inference via API.

#### Step 1: Get API Key
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Get API key from dashboard

#### Step 2: Install Groq Python SDK
```bash
wsl docker compose exec backend pip install groq
```

#### Step 3: Update Service Code

**Edit `backend/apps/cv_analysis/services.py`:**

Add this method:
```python
def chat_about_cv_groq(self, cv_text: str, user_message: str, analysis) -> str:
    """Chat using Groq's Llama 3.1"""
    try:
        from groq import Groq
        import os
        
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        # Build context
        context = f"Full Analysis: {analysis.full_analysis}\n"
        if analysis.strengths:
            context += f"Strengths: {', '.join(analysis.strengths[:5])}\n"
        
        system_prompt = f"""You are an expert CV consultant. {context}"""
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq error: {e}")
        return self._fallback_chat_response(user_message)
```

**Update `views_new.py`:**
```python
# In AdvancedCVAnalyzerViewSet.chat()
ai_response = service.chat_about_cv_groq(  # Changed from chat_about_cv_llama
    analysis.cv.raw_text,
    user_message,
    analysis
)
```

**Add to `.env`:**
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Option 3: Replicate API (Cloud - Easiest)

#### Step 1: Get API Token
1. Visit [replicate.com](https://replicate.com)
2. Sign up and get API token

#### Step 2: Install Replicate SDK
```bash
wsl docker compose exec backend pip install replicate
```

#### Step 3: Update Service Code

**Edit `backend/apps/cv_analysis/services.py`:**
```python
def chat_about_cv_replicate(self, cv_text: str, user_message: str, analysis) -> str:
    """Chat using Replicate's Llama 3.1"""
    try:
        import replicate
        import os
        
        os.environ['REPLICATE_API_TOKEN'] = os.getenv('REPLICATE_API_TOKEN')
        
        context = f"Full Analysis: {analysis.full_analysis}\n"
        if analysis.strengths:
            context += f"Strengths: {', '.join(analysis.strengths[:5])}"
        
        prompt = f"{context}\n\nUser: {user_message}\nAssistant:"
        
        output = replicate.run(
            "meta/meta-llama-3.1-8b-instruct",
            input={"prompt": prompt, "max_tokens": 500}
        )
        
        return ''.join(output)
    except Exception as e:
        logger.error(f"Replicate error: {e}")
        return self._fallback_chat_response(user_message)
```

**Add to `.env`:**
```env
REPLICATE_API_TOKEN=your_replicate_token_here
```

## Usage

### Testing the Chatbot

1. **Upload CV** to Advanced CV Analyzer
2. **Wait for analysis** to complete
3. **Click chat icon** in the analysis view
4. **Ask questions** like:
   - "How can I improve my technical skills section?"
   - "What are the biggest weaknesses in my CV?"
   - "Should I include my education at the top or bottom?"
   - "How can I make my experience more quantifiable?"

### Example Conversation

```
User: "How can I improve my CV's impact?"

Llama 3.1: "Based on your CV analysis, here are 3 key improvements:

1. Quantify achievements - Instead of 'Led development team', 
   say 'Led team of 5 developers, delivering 3 major releases 
   that increased user engagement by 40%'

2. Strengthen your leadership narrative - Your weaknesses show 
   limited leadership examples. Add 2-3 bullet points showcasing 
   team collaboration or mentorship.

3. Update skills section - Your career recommendations suggest 
   cloud technologies. Add AWS/Azure certifications if you have them.

Would you like me to help rewrite any specific sections?"
```

## Monitoring

### Check Ollama Status
```bash
# List running models
ollama list

# View logs
ollama logs

# Check API health
curl http://localhost:11434/api/tags
```

### Performance Tips

**For Ollama:**
- **GPU**: Llama 3.1 runs faster with NVIDIA GPU (CUDA support)
- **RAM**: Minimum 8GB, recommended 16GB for 8B model
- **CPU**: Modern multi-core CPU (4+ cores recommended)

**Speed Comparison:**
- Ollama (GPU): ~50-100 tokens/sec ⚡
- Ollama (CPU): ~10-20 tokens/sec
- Groq API: ~500+ tokens/sec ⚡⚡⚡
- Replicate API: ~30-50 tokens/sec

## Troubleshooting

### Issue: "Ollama not available"

**Check if Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

**Start Ollama service:**
```bash
# Windows: Ollama runs as system service (auto-starts)
# Linux/WSL:
ollama serve
```

### Issue: "Model not found"

**Pull the model:**
```bash
ollama pull llama3.1
```

### Issue: Slow responses

**Options:**
1. Use smaller model: `ollama pull llama3.1:7b`
2. Switch to Groq API (much faster)
3. Upgrade hardware (add GPU)

### Issue: Docker can't reach Ollama

**Update docker-compose.yml:**
```yaml
services:
  backend:
    environment:
      - OLLAMA_API_URL=http://host.docker.internal:11434
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

## Comparison: Ollama vs Cloud APIs

| Feature | Ollama (Local) | Groq API | Replicate API |
|---------|----------------|----------|---------------|
| **Cost** | Free ✅ | Free tier, then paid | Pay per use |
| **Privacy** | 100% local ✅ | Data sent to cloud | Data sent to cloud |
| **Speed** | Medium (CPU) / Fast (GPU) | Very fast ⚡⚡⚡ | Fast |
| **Setup** | Easy | Very easy | Very easy |
| **Requirements** | 8GB+ RAM | API key | API key |
| **Best For** | Privacy-focused, local dev | Production, speed critical | Prototyping |

## Next Steps

1. ✅ **Install Ollama** and pull Llama 3.1
2. ✅ **Test chatbot** in Advanced CV Analyzer
3. 🔄 **Monitor performance** and adjust model if needed
4. 🚀 **Go production** with Groq API for maximum speed

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Llama 3.1 Model Card](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)
- [Groq API Docs](https://console.groq.com/docs)
- [Replicate Llama 3.1](https://replicate.com/meta/meta-llama-3.1-8b-instruct)
