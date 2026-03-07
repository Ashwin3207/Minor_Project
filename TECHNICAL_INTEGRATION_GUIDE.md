# Technical Integration Guide - Ollama Chatbot System

Detailed technical documentation for developers integrating the Ollama chatbot into the Flask placement portal.

## System Architecture

### Module Organization

```
app/
├── __init__.py                    # Flask app initialization
├── models.py                      # Database models
├── chatbot/
│   ├── __init__.py
│   └── routes.py                  # API endpoints
├── chatbot_engine.py              # Main orchestration (NEW - UPGRADED)
├── chatbot_ollama.py              # Ollama integration (NEW)
├── chatbot_security.py            # RBAC & validation (NEW)
└── chatbot_intent_router.py        # Intent routing & handlers (NEW)

chatbot_handlers.py               # Database handler examples (NEW)
```

## Data Flow Diagram

```
User Message
    ↓
Flask POST /chatbot/api/chat
    ↓
ChatbotEngine.process_query()
    ├─→ Greeting Check (fast)
    │   └─→ Return greeting
    │
    └─→ Ollama Intent Extraction
        ├─→ HTTP to localhost:11434
        ├─→ Parse JSON response
        ├─→ Validate intent
        │
        ├─→ SecureIntentRouter.route_intent()
        │   ├─→ Permission check
        │   ├─→ Sanitize parameters
        │   ├─→ Execute handler
        │   │   ├─→ Query database
        │   │   ├─→ Format results
        │   │   └─→ Return data
        │   │
        │   └─→ Log action
        │
        ├─→ ChatbotEngine._format_answer()
        ├─→ Build JSON response
        │
        └─→ Return to client

Client receives JSON with answer, intent, confidence, data
```

## Class Hierarchy

```
OllamaIntentExtractor
├── extract_intent(user_message: str) → Dict
├── _parse_response(response_text: str) → Dict
└── get_intent_extractor() → OllamaIntentExtractor

SecureIntentRouter
├── route_intent(intent, params, user_id) → Dict
├── _handle_search_company(params, user_id) → Dict
├── _handle_check_eligibility(params, user_id) → Dict
├── _handle_application_status(params, user_id) → Dict
├── _handle_upcoming_drives(params, user_id) → Dict
├── _handle_placement_stats(params, user_id) → Dict
├── _handle_list_applicants(params, user_id) → Dict
└── _handle_branch_analytics(params, user_id) → Dict

ChatbotEngine
├── process_query(user_message, user_id) → Dict
├── _check_greeting(message) → Dict | None
├── _format_answer(intent, data) → str
├── _fallback_response(message, user_id) → Dict
└── _get_help_text() → str

Security Functions
├── role_permission_check(required_roles) → decorator
├── validate_json_response(response_text) → Dict | None
├── sanitize_intent_params(intent, params, user_id) → Dict
├── check_intent_permission(intent, user_id) → bool
└── log_intent_action(intent, user_id, success, params) → None
```

## API Contract

### Request Format

**Endpoint:** `POST /chatbot/api/chat`

**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "message": "Natural language query (1-500 characters)"
}
```

**Optional Session Data:**
- `session['user_id']` - Logged-in user ID (optional)
- User role retrieved from database based on user_id

### Response Format

**Success Response (HTTP 200):**
```json
{
  "success": true,
  "answer": "Formatted human-readable response",
  "context": "search_company",
  "intent": "search_company",
  "confidence": "high|medium|low",
  "data": {
    "message": "Message from handler",
    "results": [],
    "count": 0
  }
}
```

**Error Response (HTTP 200 - still JSON):**
```json
{
  "success": false,
  "answer": "Error explanation in friendly terms",
  "context": "error",
  "intent": null,
  "error": "Technical error details"
}
```

**Validation Error (HTTP 400):**
```json
{
  "success": false,
  "answer": "Please provide a message.",
  "context": "error",
  "intent": null,
  "error": "Missing message field"
}
```

**Server Error (HTTP 500):**
```json
{
  "success": false,
  "answer": "An error occurred while processing your request.",
  "context": "error",
  "intent": null,
  "error": "Internal error details (in DEBUG mode only)"
}
```

## Intent Specification

### Intent: search_company

**User Query Examples:**
- "Show opportunities from Microsoft"
- "Find Google internships"
- "Companies hiring now"

**Ollama Extraction Output:**
```json
{
  "intent": "search_company",
  "parameters": {
    "company": "Microsoft",
    "limit": 10
  },
  "confidence": "high"
}
```

**Permissions:** student, admin

**Handler Logic:**
```python
def _handle_search_company(self, params, user_id):
    company = params.get('company', '').strip()
    limit = params.get('limit', 10)
    
    opps = Opportunity.query.filter(
        Opportunity.company_name.ilike(f'%{company}%')
    ).limit(limit).all()
    
    return {
        'message': f'Found {len(opps)} opportunities from {company}',
        'results': [...],
        'count': len(opps)
    }
```

### Intent: check_eligibility

**User Query Examples:**
- "Am I eligible for internships?"
- "What positions can I apply for?"
- "Check my eligibility"

**Ollama Extraction Output:**
```json
{
  "intent": "check_eligibility",
  "parameters": {
    "limit": 10
  },
  "confidence": "high"
}
```

**Permissions:** student, admin

**Security Note:** For students, automatically uses their own user_id. Admins can query other students.

### Intent: application_status

**User Query Examples:**
- "What's my application status?"
- "Where are my applications?"
- "Show my applications"

**Ollama Extraction Output:**
```json
{
  "intent": "application_status",
  "parameters": {
    "limit": 20
  },
  "confidence": "high"
}
```

**Permissions:** student, admin

**Security Note:** Students can ONLY see their own applications. System forces student_id override.

### Intent: upcoming_drives

**User Query Examples:**
- "Show upcoming drives"
- "What's coming next?"
- "Next recruitment drives"

**Ollama Extraction Output:**
```json
{
  "intent": "upcoming_drives",
  "parameters": {
    "limit": 20
  },
  "confidence": "high"
}
```

**Permissions:** student, admin

**Special Handling:** Filters by deadline > now and deadline <= (now + 30 days)

### Intent: placement_stats

**User Query Examples:**
- "Show placement statistics"
- "How many students placed?"
- "Placement numbers"

**Ollama Extraction Output:**
```json
{
  "intent": "placement_stats",
  "parameters": {},
  "confidence": "high"
}
```

**Permissions:** admin ONLY

**Security Note:** Returns system-wide statistics. Students receive permission denied error.

### Intent: list_applicants

**User Query Examples:**
- "List applicants"
- "Show me all applications"
- "Who has applied?"

**Ollama Extraction Output:**
```json
{
  "intent": "list_applicants",
  "parameters": {
    "limit": 50
  },
  "confidence": "high"
}
```

**Permissions:** admin ONLY

**Security Note:** Only admins can see full applicant list.

### Intent: branch_analytics

**User Query Examples:**
- "Get CSE analytics"
- "Show branch statistics"
- "Branch-wise breakdown"

**Ollama Extraction Output:**
```json
{
  "intent": "branch_analytics",
  "parameters": {
    "branch": "CSE",
    "limit": 10
  },
  "confidence": "high"
}
```

**Permissions:** admin ONLY

**Security Note:** Admin can specify branch parameter.

## Database Query Patterns

### Safe Query Pattern (with ORM)

**CORRECT - Safe from SQL injection:**
```python
opportunities = Opportunity.query.filter(
    Opportunity.company_name.ilike(f'%{company}%')
).limit(limit).all()
```

**WRONG - DO NOT USE - SQL injection vulnerability:**
```python
query = f"SELECT * FROM opportunities WHERE company_name LIKE '%{company}%'"
db.engine.execute(query)  # VULNERABLE!
```

### Parameter Validation Pattern

```python
def sanitize_intent_params(intent, params, user_id):
    # 1. Validate intent permission
    if intent not in ALLOWED_INTENTS:
        return {}
    
    # 2. Check user role
    user = User.query.get(user_id)
    user_role = user.role.lower()
    
    # 3. Enforce role-based filtering
    sanitized = {}
    
    # 4. Override student_id for students
    if user_role == 'student':
        sanitized['student_id'] = user_id  # Force current user
    
    # 5. Limit numeric parameters
    if 'limit' in params:
        sanitized['limit'] = min(params['limit'], 100)
    
    # 6. Sanitize string parameters
    if 'company' in params:
        sanitized['company'] = params['company'][:100]  # Limit length
    
    return sanitized
```

## Error Handling Strategy

### Graceful Degradation

```python
# Try Ollama AI first
intent_data = ollama_intent_extractor(user_message)

if not intent_data:
    # Fall back to simple keyword matching
    logger.warning("Ollama extraction failed, using fallback")
    response = _fallback_response(user_message, user_id)
    return response
```

### Structured Error Returns

```python
{
    'success': False,
    'answer': 'User-friendly error message',
    'context': 'error',
    'intent': 'attempted_intent_name',
    'error': 'Technical error details (DEBUG only)'
}
```

### Timeout Handling

```python
try:
    response = requests.post(
        OLLAMA_API_URL,
        json=payload,
        timeout=TIMEOUT_SECONDS  # 5 seconds
    )
except Timeout:
    logger.error(f"Ollama timeout after {TIMEOUT_SECONDS}s")
    return None  # Triggers fallback
except RequestException as e:
    logger.error(f"Ollama request error: {str(e)}")
    return None  # Triggers fallback
```

## Performance Optimization

### Fast Path - Greetings

```python
def _check_greeting(self, message):
    greetings = {'hello', 'hi', 'hey', 'help', 'bye'}
    for greeting in greetings:
        if greeting in message.lower():
            return GREETING_RESPONSE  # No AI needed
    return None
```

**Result:** < 10ms response time

### AI Path - Intent Extraction

```python
intent_data = ollama_intent_extractor(user_message)
```

**Expected:** 1-5 seconds (depends on Ollama)

### Database Queries

```python
# Use indexes for common queries
opportunities = Opportunity.query.filter(
    Opportunity.company_name.ilike(f'%{company}%')
).limit(10).all()  # Limit prevents memory issues
```

**Expected:** < 100ms (with proper indexes)

## Logging Strategy

### Audit Trail

```python
log_intent_action(
    intent='search_company',
    user_id=user_id,
    success=True,
    params={'company': 'Microsoft', 'limit': 10}
)
```

### Debug Logging

```python
logger.debug(f"Processing query: {user_message}")
logger.debug(f"Extracted intent: {intent_data}")
logger.debug(f"Query result count: {len(results)}")
```

### Error Logging

```python
logger.error(f"Query execution error: {str(e)}", exc_info=True)
```

### Performance Logging

```python
import time
start = time.time()
result = handler(params, user_id)
elapsed = time.time() - start
logger.info(f"Intent {intent} took {elapsed:.2f}s")
```

## Testing Strategy

### Unit Tests

```python
def test_greeting_detection():
    engine = ChatbotEngine(session=db.session)
    response = engine._check_greeting("hello")
    assert response['context'] == 'greeting'

def test_intent_validation():
    assert 'search_company' in ALLOWED_INTENTS
    assert 'invalid_intent' not in ALLOWED_INTENTS

def test_permission_check():
    assert check_intent_permission('search_company', user_id=1)
    assert not check_intent_permission('placement_stats', user_id=1)  # Student
```

### Integration Tests

```python
def test_search_company_flow():
    engine = ChatbotEngine(session=db.session)
    response = engine.process_query(
        "Find Google internships",
        user_id=student_id
    )
    assert response['success'] == True
    assert response['intent'] == 'search_company'
    assert len(response['data']['results']) > 0
```

### Security Tests

```python
def test_student_data_isolation():
    # Student tries to access other student's data
    response = router.route_intent(
        'application_status',
        {'student_id': 999},  # Another student
        user_id=1  # Current student
    )
    # System forces student_id=1, not 999
    assert response['data']['applications'] == student_1_apps

def test_admin_only_access():
    # Student tries to access admin intent
    response = router.route_intent(
        'placement_stats',
        {},
        user_id=1  # Student
    )
    assert response['success'] == False
    assert 'Permission denied' in response['error']
```

## Deployment Considerations

### Prerequisites

1. Python 3.8+ 
2. Ollama service running
3. phi3 model available
4. Database migrations applied
5. Flask app configured

### Configuration

```python
# config.py
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"
OLLAMA_TIMEOUT_SECONDS = 5
CHATBOT_ENABLED = True
RBAC_ENABLED = True
AUDIT_LOG_ENABLED = True
```

### Health Checks

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check chatbot endpoint
curl http://app-url:5000/chatbot/api/health
```

### Monitoring

Track these metrics:
- Intent extraction success rate (should be > 95%)
- Average response time (should be < 5s)
- Database query times (should be < 100ms)
- Permission denial rate (watch for anomalies)
- Ollama API uptime

---

**Document Version:** 1.0
**Updated:** 2025-02-13
**Status:** Production-Ready
