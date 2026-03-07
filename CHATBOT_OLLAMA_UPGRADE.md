# Upgraded Chatbot System with Ollama AI Integration

Comprehensive documentation for the AI-powered chatbot system using local Ollama (phi3 model).

## Overview

The upgraded chatbot system combines:
- **Ollama AI** (phi3 model) for natural language intent extraction
- **Secure intent router** with role-based access control
- **SQLAlchemy handlers** for database operations
- **5-second timeout** for fast responses
- **Low-RAM optimized** for resource-constrained environments

## Architecture

```
User Query
    ↓
Greeting Check (fast path)
    ↓
Ollama Intent Extractor (AI-powered)
    ↓
Intent Validation & Sanitization
    ↓
Permission Check (RBAC)
    ↓
Secure Intent Router
    ↓
Database Query Handlers
    ↓
Response Formatting
    ↓
JSON Response
```

## System Components

### 1. **chatbot_ollama.py** - Intent Extractor
Uses Ollama API to convert natural language to structured intents.

**Key Features:**
- HTTP timeout: 5 seconds
- Max output: 200 tokens
- Temperature: 0.3 (deterministic)
- JSON parsing with validation
- Error handling with fallback

**Usage:**
```python
from app.chatbot_ollama import ollama_intent_extractor

result = ollama_intent_extractor("Show me opportunities from Google")
# Returns: {'intent': 'search_company', 'parameters': {'company': 'Google'}, 'confidence': 'high'}
```

### 2. **chatbot_security.py** - Security & RBAC
Handles role-based access control and input validation.

**Features:**
- 7 allowed intents
- Role-based permission matrix
- Input parameter sanitization
- Student data isolation
- Admin analytics access
- Audit logging

**Allowed Intents:**
```
- search_company           → students, admin
- check_eligibility        → students, admin
- application_status       → students, admin
- upcoming_drives          → students, admin
- placement_stats          → admin only
- list_applicants          → admin only
- branch_analytics         → admin only
```

**Usage:**
```python
from app.chatbot_security import check_intent_permission, ALLOWED_INTENTS

if check_intent_permission('placement_stats', user_id):
    # User has permission
    pass
```

### 3. **chatbot_intent_router.py** - Intent Execution
Routes intents to appropriate handlers with security checks.

**Handlers Implemented:**
- `_handle_search_company()` - Search opportunities by company
- `_handle_check_eligibility()` - Check student eligibility
- `_handle_application_status()` - Get student applications
- `_handle_upcoming_drives()` - List upcoming recruitment
- `_handle_placement_stats()` - Get overall statistics (admin)
- `_handle_list_applicants()` - List applicants (admin)
- `_handle_branch_analytics()` - Branch statistics (admin)

**Usage:**
```python
from app.chatbot_intent_router import secure_intent_router

router = secure_intent_router(db)
result = router.route_intent(
    intent='search_company',
    parameters={'company': 'Microsoft', 'limit': 10},
    user_id=user_id
)
```

### 4. **chatbot_engine.py** - Main Engine
Orchestrates the entire chatbot flow.

**Process:**
1. Validate input
2. Check for greetings (fast path)
3. Extract intent with Ollama
4. Validate and sanitize
5. Route to handler
6. Format response
7. Return JSON

**Usage:**
```python
from app.chatbot_engine import ChatbotEngine

engine = ChatbotEngine(session=db.session)
response = engine.process_query(
    user_message="Show me upcoming internships",
    user_id=user_id
)
```

### 5. **chatbot_handlers.py** - Database Access Examples
Production-ready examples for database queries.

Includes:
- Safe student profile access
- Eligibility calculations
- Search queries
- Aggregation functions
- Admin statistics
- Security best practices

## Setup & Installation

### Prerequisites
1. **Ollama Service Running**
   ```bash
   ollama pull phi3
   ollama serve
   ```
   Server must be running at `http://localhost:11434/api/generate`

2. **Python Dependencies**
   ```bash
   pip install requests flask flask-sqlalchemy
   ```

### Configuration

Add to `config.py`:
```python
# Chatbot Configuration
CHATBOT_TIMEOUT = 5  # seconds
CHATBOT_MAX_TOKENS = 200
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"
```

### Flask Blueprint Integration

The chatbot is registered as a Flask blueprint at `/chatbot`:

```python
# In app/__init__.py
from app.chatbot.routes import bp
app.register_blueprint(bp)
```

**API Endpoints:**
- `GET /chatbot/` - Chatbot UI page
- `POST /chatbot/api/chat` - Process user query
- `GET /chatbot/api/suggestions` - Get suggested questions
- `GET /chatbot/api/intents` - List available intents
- `GET /chatbot/api/health` - Health check

## API Endpoints

### POST /chatbot/api/chat
Process natural language query.

**Request:**
```json
{
  "message": "Show me opportunities from Microsoft"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Found 3 opportunities from Microsoft...",
  "context": "search_company",
  "intent": "search_company",
  "confidence": "high",
  "data": {
    "message": "Found 3 opportunities from Microsoft",
    "results": [...],
    "count": 3
  }
}
```

### GET /chatbot/api/suggestions
Get personalized suggestions.

**Response:**
```json
{
  "success": true,
  "suggestions": [
    "Find opportunities from Google",
    "Am I eligible for any positions?",
    "What's my application status?"
  ]
}
```

### GET /chatbot/api/intents
List available intents for current user.

**Response:**
```json
{
  "success": true,
  "intents": {
    "search_company": {
      "available": true,
      "requires": ["student", "admin"],
      "description": "Search opportunities by company"
    },
    "placement_stats": {
      "available": false,
      "requires": ["admin"],
      "description": "Get placement statistics"
    }
  },
  "user_role": "student"
}
```

## Security Features

### 1. Role-Based Access Control (RBAC)
```python
@role_permission_check(required_roles={'admin'})
def admin_only_function():
    pass
```

### 2. Input Sanitization
```python
sanitized = sanitize_intent_params(
    intent='search_company',
    params={'company': 'Google', 'limit': 1000},
    user_id=user_id
)
# Enforces limits: limit capped at 100
```

### 3. Student Data Isolation
```python
# Students can only access their own data
if user_role == 'student':
    sanitized['student_id'] = user_id  # Force override
```

### 4. Intent Validation
```python
if intent not in ALLOWED_INTENTS:
    return {'error': 'Unknown intent'}
```

### 5. JSON Response Validation
```python
validated = validate_json_response(response_text)
if not validated:
    return None  # Invalid or untrusted response
```

### 6. Audit Logging
```python
log_intent_action(
    intent='search_company',
    user_id=user_id,
    success=True,
    params={'company': 'Google'}
)
```

## Error Handling

### Ollama Connection Errors
- Timeout after 5 seconds
- Falls back to keyword matching
- Logs error and returns fallback response

### Invalid Intents
- Rejects unknown intents
- Returns helpful error message
- Suggests valid options

### Permission Denied
- Blocks unauthorized intent access
- Logs security event
- Returns permission error

### Database Errors
- Catches SQLAlchemy exceptions
- Returns generic error to user
- Full error in DEBUG logs

## Performance Optimization

### Timeouts
- Ollama API: 5 seconds max
- Database queries: Limited with `.limit()`
- Greeting check: Immediate (no AI)

### Memory Management
- Singleton intent extractor instance
- Limited result sets (default 10, max 100)
- No caching of full responses
- Stream-friendly response format

### Query Optimization
- Indexed queries on frequently searched fields
- Distinct queries for aggregations
- Pre-filtering before ordering

## Example Queries

### Student Queries
```
"Show me opportunities from Microsoft"
→ intent: search_company, parameters: {company: Microsoft}

"Am I eligible for internships?"
→ intent: check_eligibility

"What's my application status?"
→ intent: application_status

"Show upcoming recruitment drives"
→ intent: upcoming_drives
```

### Admin Queries
```
"Show placement statistics"
→ intent: placement_stats (requires admin role)

"List all applicants"
→ intent: list_applicants (requires admin role)

"Get CSE branch analytics"
→ intent: branch_analytics, parameters: {branch: CSE}
```

## Troubleshooting

### "Ollama API timeout after 5s"
- Make sure Ollama is running: `ollama serve`
- Check connection: `curl http://localhost:11434/api/tags`
- Verify model: `ollama list`

### "Intent extraction failed, using fallback"
- Check Ollama is responsive
- Check prompt formatting
- Verify model is phi3: `ollama show phi3`

### "Permission denied for this intent"
- Verify user is logged in
- Check user role (student/admin)
- Verify intent matches role requirements

### "Student not found"
- Ensure user_id is valid
- Check StudentProfile exists for user
- Verify user is role='Student'

## Advanced Topics

### Custom Intent Handlers
Add new intent to router:

```python
def _handle_custom_intent(self, params, user_id):
    # Your implementation
    return {'message': 'Result', 'data': []}

# Add to router
self.handlers['custom_intent'] = self._handle_custom_intent
```

### Custom Prompts
Modify in `chatbot_ollama.py`:

```python
INTENT_PROMPT_TEMPLATE = """Your custom prompt here..."""
```

### Database Integration
Use examples from `chatbot_handlers.py`:

```python
from app.chatbot_handlers import get_eligible_opportunities

opportunities = get_eligible_opportunities(student_id, limit=10)
```

## Deployment Checklist

- [ ] Ollama phi3 model downloaded and running
- [ ] Ollama API accessible at http://localhost:11434
- [ ] Flask app configured with chatbot blueprint
- [ ] Database migrations applied
- [ ] User roles set correctly (Student/Admin)
- [ ] RBAC permissions tested
- [ ] Logging configured for audit trail
- [ ] Error handling tested
- [ ] Performance tested with expected load
- [ ] Security review completed

## Monitoring & Logging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('app.chatbot')
```

### Check Ollama Logs
Monitor Ollama service output for:
- Connection errors
- Token limit hits
- Response times

### Audit Trail
All intent executions are logged with:
- Timestamp
- User ID
- Intent name
- Success/failure
- Parameters used

## Future Enhancements

1. **Caching Layer** - Cache popular queries
2. **ML Optimization** - Fine-tune phi3 for placement domain
3. **Multi-turn Conversation** - Session-based context
4. **Advanced Analytics** - Dashboard integration
5. **Real-time Updates** - WebSocket support
6. **Batch Processing** - Handle large requests
7. **A/B Testing** - Test different prompts

## Support & Contact

For issues or questions about the chatbot system:
1. Check error logs
2. Review this documentation
3. Test with simple queries first
4. Verify Ollama is running
5. Check security permissions

---

**System Status:** Production-Ready
**Last Updated:** 2025
**Model:** Ollama phi3
**Python Version:** 3.8+
