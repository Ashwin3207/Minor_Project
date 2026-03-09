# 🚀 Mistral AI Chatbot - Quick Start

## 5-Minute Setup

### Step 1: Get Free API Key (2 minutes)
```bash
# Visit https://console.mistral.ai
# 1. Sign up for free account
# 2. Create API key
# 3. Copy the key (starts with 'sk_')
```

### Step 2: Configure Environment (1 minute)
```bash
# Edit .env file or set environment variable:
export MISTRAL_API_KEY=sk_your_key_here

# Or for Windows PowerShell:
$env:MISTRAL_API_KEY="sk_your_key_here"
```

### Step 3: Install & Run (2 minutes)
```bash
# Install latest dependencies
pip install -r requirements.txt

# Run your Flask app
python run.py

# Test with verification script (optional)
python verify_mistral_integration.py
```

### Step 4: Test Chatbot
```bash
# Open in browser:
http://localhost:5000/chatbot

# Try these queries:
"Find opportunities from Google"
"Show upcoming drives"
"What's my application status?"
```

---

## ⚡ What Changed

✅ **3 AI Providers** (smart fallback):
1. **Mistral** (fastest - cloud-based)
2. **Ollama** (private - local)
3. **Keyword Fallback** (always works)

✅ **Same API** - Works like before but smarter

✅ **Better Responses** - Includes `extraction_method` field

✅ **100% Compatible** - Ollama still works if no Mistral key

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [MISTRAL_SETUP_GUIDE.md](MISTRAL_SETUP_GUIDE.md) | Complete setup guide |
| [MISTRAL_INTEGRATION_SUMMARY.md](MISTRAL_INTEGRATION_SUMMARY.md) | Technical overview |
| [MISTRAL_INTEGRATION_CHANGELOG.md](MISTRAL_INTEGRATION_CHANGELOG.md) | What was changed |

---

## 🧪 Verify Integration

```bash
# Run verification script (no Flask needed):
python verify_mistral_integration.py

# Expected output:
# ✅ MISTRAL_API_KEY configured: sk_xxx...xxx
# ✅ Mistral API responsive
# ✅ Mistral successfully extracted: search_company
```

---

## 🎯 Common Tasks

### Use Mistral (Cloud)
```python
# Automatic - just set MISTRAL_API_KEY
export MISTRAL_API_KEY=sk_your_key
python run.py
```

### Use Ollama (Local)
```bash
# 1. Install Ollama from ollama.ai
# 2. Run Ollama service
# 3. App detects and uses it automatically (or if no Mistral key)
```

### Use Keyword Fallback (Offline)
```python
# No API key? No problem!
# Keyword-based matching always works
# Performance: <100ms, Accuracy: Good for simple queries
```

---

## 🔧 Environment Variables

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| MISTRAL_API_KEY | Optional | `sk_...` | Mistral AI cloud API |
| DATABASE_URL | Optional | PostgreSQL URL | Database connection |
| FLASK_ENV | Optional | `production` | Flask environment |
| SECRET_KEY | Required | Auto-generated | Session security |

---

## 📊 Response Format

```json
{
  "success": true,
  "answer": "Found 5 opportunities...",
  "intent": "search_company",
  "confidence": "high",
  "extraction_method": "mistral",
  "data": { ... }
}
```

### New Field: `extraction_method`
- `"mistral"` - Cloud-based AI
- `"ollama"` - Local AI  
- `"keyword_fallback"` - Pattern matching

---

## ✅ Deployment Checklist

### Render.com
```
1. Dashboard → Environment
2. Add: MISTRAL_API_KEY = sk_your_key_here
3. Redeploy
```

### Heroku
```bash
heroku config:set MISTRAL_API_KEY=sk_your_key_here
git push heroku main
```

### Local
```bash
echo "MISTRAL_API_KEY=sk_your_key_here" >> .env
python run.py
```

---

## 🆘 Troubleshooting

### Problem: "Using fallback intent matching"
```bash
# Check if API key is set:
echo $MISTRAL_API_KEY

# If empty:
export MISTRAL_API_KEY=sk_your_key_here
```

### Problem: Slow responses
```bash
# Check which provider is being used:
curl -X POST http://localhost:5000/chatbot/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'

# Response will show extraction_method
```

### Problem: 401 Unauthorized
```bash
# Verify API key is valid at console.mistral.ai
# Regenerate key if needed
# Check for extra spaces or typos
```

---

## 🎮 Try It Now

### JavaScript
```javascript
fetch('/chatbot/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: "Find opportunities from Google"})
})
.then(r => r.json())
.then(data => {
  console.log('Provider:', data.extraction_method);
  console.log('Intent:', data.intent);
  console.log('Answer:', data.answer);
});
```

### Python
```python
from app.chatbot_engine import ChatbotEngine

engine = ChatbotEngine()
result = engine.process_query("Find opportunities from Microsoft")

print(f"Method: {result['extraction_method']}")  # mistral/ollama/keyword_fallback
print(f"Intent: {result['intent']}")
print(f"Answer: {result['answer']}")
```

### cURL
```bash
curl -X POST http://localhost:5000/chatbot/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Find opportunities from Google"}'
```

---

## 📈 Performance Tips

### For Speed (< 1 second)
- Use Mistral (configured)
- Keep queries short
- Close other services

### For Privacy (no cloud)
- Use Ollama (locally installed)
- Install from ollama.ai
- Run on localhost:11434

### For Offline Use (always works)
- Keyword fallback available
- No API key needed
- <100ms response time

---

## 💡 Example Queries

### Student Queries
```
"Find software engineer positions"
"Show me opportunities from Google"
"What's my application status?"
"Am I eligible for this role?"
"When are the next recruitment drives?"
```

### Admin Queries
```
"List all applicants"
"Get branch-wise analytics"
"Show me students with CGPA > 8.0"
```

---

## 🔗 Resources

- **Get API Key**: [console.mistral.ai](https://console.mistral.ai)
- **Documentation**: [docs.mistral.ai](https://docs.mistral.ai)
- **Ollama**: [ollama.ai](https://ollama.ai)
- **Status**: [status.mistral.ai](https://status.mistral.ai)

---

## ❓ FAQs

**Q: Do I need Mistral API key?**  
A: No, optional. Works with Ollama or keyword fallback.

**Q: Can I use both Mistral and Ollama?**  
A: Yes! Mistral is tried first, Ollama is fallback.

**Q: How much does Mistral cost?**  
A: Free tier available, ~$0.0001 per message for paid.

**Q: Does it work offline?**  
A: Yes, keyword fallback always works without internet.

**Q: Can I switch providers later?**  
A: Yes, just change MISTRAL_API_KEY environment variable.

---

## 🎉 You're Ready!

1. ✅ Get [free API key](https://console.mistral.ai) (5 min)
2. ✅ Set `MISTRAL_API_KEY` in environment
3. ✅ Run `pip install -r requirements.txt`
4. ✅ Run `python run.py`
5. ✅ Access chatbot at `/chatbot`
6. ✅ Enjoy AI-powered responses!

---

**Need help?** → Check [MISTRAL_SETUP_GUIDE.md](MISTRAL_SETUP_GUIDE.md)  
**Want details?** → See [MISTRAL_INTEGRATION_SUMMARY.md](MISTRAL_INTEGRATION_SUMMARY.md)  
**What changed?** → Read [MISTRAL_INTEGRATION_CHANGELOG.md](MISTRAL_INTEGRATION_CHANGELOG.md)

---

*Mistral Chatbot Integration v1.0 | March 7, 2026*
