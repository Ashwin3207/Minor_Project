# Ollama Chatbot Quick Start Guide

Get the AI-powered chatbot running in 5 minutes.

## Prerequisites

✓ Python 3.8+
✓ Flask & SQLAlchemy
✓ Ollama installed
✓ phi3 model downloaded

## Step 1: Start Ollama Service

```bash
# Terminal 1: Start Ollama server
ollama pull phi3      # Download if needed (first time only)
ollama serve          # Starts at http://localhost:11434
```

Verify it's running:
```bash
curl http://localhost:11434/api/tags
```

## Step 2: Verify Flask Integration

The chatbot blueprint is automatically registered in the Flask app.

Check `app/__init__.py`:
```python
from app.chatbot.routes import bp
app.register_blueprint(bp)  # Already done!
```

## Step 3: Test the Chatbot API

```bash
# Terminal 2: Test the endpoints
python

from app import create_app, db
from app.chatbot_engine import ChatbotEngine

app = create_app()
with app.app_context():
    engine = ChatbotEngine(session=db.session)
    
    # Test without AI (greeting)
    response = engine.process_query("hello")
    print(response)
    
    # Test with AI (requires Ollama)
    response = engine.process_query("Show me opportunities from Microsoft")
    print(response)
```

## Step 4: Test via Flask Routes

```bash
# Terminal 2: Start Flask dev server
python run.py

# Terminal 3: Test endpoints
curl -X POST http://localhost:5000/chatbot/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'

# Expected response:
# {
#   "success": true,
#   "answer": "Hello! I am your Training & Placement Assistant...",
#   "context": "greeting",
#   "intent": null
# }
```

## Step 5: Test with Database Query

Log in with a student account, then:

```bash
curl -X POST http://localhost:5000/chatbot/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my application status?"}'
```

The system will:
1. Extract intent: `application_status`
2. Check permissions: ✓ Student allowed
3. Query database for student's applications
4. Format and return results

## Test Cases

### Basic Functionality
```bash
# Test 1: Greeting (no AI needed)
curl -X POST http://localhost:5000/chatbot/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hi"}'
# Expected: Greeting response

# Test 2: Help command
curl -X POST http://localhost:5000/chatbot/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "help"}'
# Expected: Help text

# Test 3: Search companies (uses Ollama AI)
curl -X POST http://localhost:5000/chatbot/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find opportunities from Amazon"}'
# Expected: AI extracts intent, queries database
```

### Security Tests
```bash
# Test 4: Student can only see own data
# (Login as student, then)
curl -X POST http://localhost:5000/chatbot/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is student 999 application status?"}'
# Expected: System ignores student_id, uses logged-in user

# Test 5: Admin-only intent
# (Login as admin, then)
curl -X POST http://localhost:5000/chatbot/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show placement statistics"}'
# Expected: Admin sees stats

# Test 6: Student cannot access admin intent
# (Login as student, then)
curl -X POST http://localhost:5000/chatbot/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show placement statistics"}'
# Expected: Permission denied
```

## Debugging

### Check Ollama is Working
```bash
curl http://localhost:11434/api/generate \
  -d '{"model":"phi3","prompt":"What is 2+2?","stream":false}'
```

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run:
python test_ollama_chatbot.py
```

### Check Intent Extraction
```python
from app.chatbot_ollama import ollama_intent_extractor

result = ollama_intent_extractor("Find Google opportunities")
print(result)
# Should show: intent, parameters, confidence
```

### Test Database Handlers
```python
from app.chatbot_handlers import (
    search_companies,
    get_eligible_opportunities,
    get_branch_statistics
)

# Test search
results = search_companies("Microsoft", limit=5)
print(results)
```

## Common Issues & Solutions

### Issue: "Ollama API timeout after 5s"
```
Solution:
1. Check Ollama is running: ollama serve
2. Check port: curl http://localhost:11434/api/tags
3. Increase timeout if needed in chatbot_ollama.py
```

### Issue: "Intent extraction failed, using fallback"
```
Solution:
1. Verify phi3 model: ollama list
2. Check Ollama logs for errors
3. Try simpler query: "show jobs"
4. Check network connection to localhost:11434
```

### Issue: "Permission denied for this intent"
```
Solution:
1. Verify user is logged in
2. Check user role: Admin vs Student
3. Verify intent requires that role
4. Check INTENT_PERMISSIONS in chatbot_security.py
```

### Issue: "Student not found" or empty results
```
Solution:
1. Create test data: python quick_add_opps.py
2. Verify StudentProfile exists (not just User)
3. Check opportunity data has correct criteria
4. Verify user role is 'Student' (capitalized)
```

## Performance Tips

1. **Keep prompts short** - 200 token limit should be plenty
2. **Use fast greetings** - "hi", "hello" skip AI
3. **Cache Opportunities** - Frequently queried
4. **Limit results** - Default 10, max 100
5. **Monitor Ollama** - Watch for slow responses

## Example Conversation Flow

```
User: "Show opportunities from Facebook"
→ Greeting check: no
→ Ollama extracts: intent=search_company, company=Facebook
→ Permission check: ✓ student allowed
→ Database query: opportunities with company_name containing Facebook
→ Format response: list of opportunities
→ Return JSON response

User (logged-in student): "Am I eligible?"
→ Greeting check: no
→ Ollama extracts: intent=check_eligibility
→ Permission check: ✓ student allowed
→ Database query: student profile, relevant opportunities
→ Eligibility calculation: CGPA check, branch check
→ Format response: list of eligible opportunities
→ Return JSON response

User (logged-in admin): "Show statistics"
→ Greeting check: no
→ Ollama extracts: intent=placement_stats
→ Permission check: ✓ admin allowed, student NOT allowed
→ Database query: aggregate statistics across all students
→ Format response: placement rate, counts, distributions
→ Return JSON response
```

## Next Steps

1. ✅ Verify Ollama is running
2. ✅ Test basic endpoints
3. ✅ Run security tests
4. ✅ Create test data if needed
5. ✅ Monitor logs for errors
6. ✅ Adjust timeouts if needed
7. ✅ Deploy to production

## Production Checklist

- [ ] Ollama running on prod server
- [ ] OLLAMA_API_URL points to prod instance
- [ ] Timeout values appropriate for prod
- [ ] Error logging configured
- [ ] RBAC roles verified
- [ ] Database indexes added
- [ ] Rate limiting configured (optional)
- [ ] Load testing completed
- [ ] Fallback responses working

## Performance Baseline

Local testing on typical hardware:
- Greeting response: < 10ms
- Intent extraction (via Ollama): 1-3 seconds
- Database queries: < 100ms (with indexes)
- Total response time: 1-5 seconds

## Helpful Commands

```bash
# Check Ollama model
ollama list

# Pull specific model
ollama pull phi3

# Stop Ollama
pkill ollama

# View Ollama logs
ollama --verbose

# Test specific prompt
ollama run phi3 "Show me JSON: {\"intent\":\"search_company\"}"
```

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│         Flask Web Application               │
├─────────────────────────────────────────────┤
│  POST /chatbot/api/chat                     │
│    ↓                                        │
│  ChatbotEngine.process_query()              │
│    ↓                                        │
│  _check_greeting() → (fast path)            │
│    ↓ (if not greeting)                      │
│  ollama_intent_extractor()                  │
│    ↓                                        │
│  OllamaIntentExtractor.extract_intent()     │
│    ↓                                        │
│  HTTP POST → Ollama API (localhost:11434)   │
│    ↓                                        │
│  Parse JSON response                        │
│    ↓                                        │
│  validate_json_response()                   │
│    ↓                                        │
│  SecureIntentRouter.route_intent()          │
│    ↓                                        │
│  check_intent_permission() → RBAC check     │
│    ↓                                        │
│  sanitize_intent_params()                   │
│    ↓                                        │
│  Handler (database query)                   │
│    ↓                                        │
│  _format_answer()                           │
│    ↓                                        │
│  Return JSON response                       │
└─────────────────────────────────────────────┘
```

---

**Status:** Ready to Deploy
**Model:** Ollama phi3
**Timeout:** 5 seconds
**Max Tokens:** 200
