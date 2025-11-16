#!/bin/bash

echo "🧪 Testing Llama 3.1 Integration in Docker"
echo "=========================================="
echo ""

echo "✅ Step 1: Check Ollama service status"
docker compose ps ollama
echo ""

echo "✅ Step 2: Check Llama 3.1 model is installed"
docker compose exec ollama ollama list
echo ""

echo "✅ Step 3: Test Ollama API endpoint"
curl -s http://localhost:11434/api/tags | python -m json.tool
echo ""

echo "✅ Step 4: Test simple chat request"
curl -s http://localhost:11434/api/chat -d '{
  "model": "llama3.1",
  "messages": [{"role": "user", "content": "Say hello in 5 words"}],
  "stream": false
}' | python -m json.tool
echo ""

echo "✅ Step 5: Verify backend can reach Ollama"
docker compose exec backend python -c "
import requests
try:
    response = requests.get('http://ollama:11434/api/tags', timeout=5)
    print('✅ Backend → Ollama: Connected')
    print(f'   Models: {len(response.json()[\"models\"])} available')
except Exception as e:
    print(f'❌ Backend → Ollama: Failed - {e}')
"
echo ""

echo "=========================================="
echo "🎉 All tests complete!"
echo ""
echo "Next steps:"
echo "1. Go to: http://localhost:3000/cv-analysis/advanced-analyzer"
echo "2. Upload a CV and analyze it"
echo "3. Click the chat icon 💬"
echo "4. Ask: 'How can I improve my CV?'"
echo "5. Llama 3.1 will respond!"
