"""
Configuration and environment setup for Ollama-powered chatbot.
Add these settings to your Flask config.
"""

# ==================== Ollama Configuration ====================

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Ollama model to use
OLLAMA_MODEL = "phi3"

# API request timeout (seconds)
OLLAMA_TIMEOUT_SECONDS = 5

# Maximum tokens in response
OLLAMA_MAX_TOKENS = 200

# Temperature for response consistency (0.0-1.0)
# Lower = more deterministic, Higher = more creative
OLLAMA_TEMPERATURE = 0.3

# ==================== Chatbot Configuration ====================

# Enable/disable chatbot feature
CHATBOT_ENABLED = True

# Chatbot debug mode
CHATBOT_DEBUG = False

# Default number of results to return
CHATBOT_DEFAULT_LIMIT = 10

# Maximum number of results allowed
CHATBOT_MAX_RESULTS = 100

# ==================== Security Configuration ====================

# RBAC enforcement
RBAC_ENABLED = True

# Student can only access their own data
ENFORCE_STUDENT_DATA_ISOLATION = True

# Require authentication for certain intents
REQUIRE_AUTH_FOR_PERSONALIZED = True

# Log all intent executions (audit trail)
AUDIT_LOG_ENABLED = True

# ==================== Performance Configuration ====================

# Cache intent extractor instance
CACHE_INTENT_EXTRACTOR = True

# Limit input message length (characters)
MAX_MESSAGE_LENGTH = 500

# Time limit for greeting check (ms) - short circuit for speed
GREETING_CHECK_TIMEOUT = 10

# ==================== Database Configuration ====================

# Query result limits (prevent memory issues)
MAX_OPPORTUNITIES_PER_QUERY = 100
MAX_APPLICATIONS_PER_QUERY = 100
MAX_APPLICANTS_PER_QUERY = 100
MAX_DRIVES_PER_QUERY = 50

# Pagination defaults
PAGINATION_DEFAULT = 10
PAGINATION_MAX = 100

# ==================== Error Handling Configuration ====================

# Show detailed errors in DEBUG mode only
SHOW_DETAILED_ERRORS = False

# Log stack traces for errors
LOG_ERROR_STACKS = True

# Return helpful error messages vs generic
FRIENDLY_ERROR_MESSAGES = True

# ==================== Logging Configuration ====================

# Logging level
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log chatbot interactions
LOG_CHATBOT_INTERACTIONS = True

# Log intent extraction
LOG_INTENT_EXTRACTION = True

# Log database queries
LOG_DATABASE_QUERIES = False  # Can be verbose

# Log security events
LOG_SECURITY_EVENTS = True

# ==================== Feature Flags ====================

# Enable Ollama AI extraction (vs keyword matching)
ENABLE_OLLAMA_EXTRACTION = True

# Enable fallback to keyword matching if Ollama fails
ENABLE_KEYWORD_FALLBACK = True

# Enable response caching (future enhancement)
ENABLE_RESPONSE_CACHE = False

# Enable multi-turn conversations (future enhancement)
ENABLE_CONVERSATION_CONTEXT = False

# ==================== Intent Configuration ====================

# Allowed intents (read-only)
ALLOWED_INTENTS = {
    'search_company',
    'check_eligibility',
    'application_status',
    'upcoming_drives',
    'placement_stats',
    'list_applicants',
    'branch_analytics'
}

# Intent timeout (seconds)
INTENT_EXECUTION_TIMEOUT = 5

# Admin-only intents
ADMIN_ONLY_INTENTS = {
    'placement_stats',
    'list_applicants',
    'branch_analytics'
}

# ==================== Role-Based Access Control ====================

# Role definitions
VALID_ROLES = ['student', 'admin']

# Default role for new users
DEFAULT_USER_ROLE = 'student'

# Admin role name
ADMIN_ROLE = 'admin'

# Student role name
STUDENT_ROLE = 'student'

# ==================== Analytics Configuration ====================

# Enable usage analytics
ANALYTICS_ENABLED = True

# Track intent popularity
TRACK_INTENT_USAGE = True

# Track response times
TRACK_RESPONSE_TIMES = True

# ==================== Deployment Configuration ====================

# Environment
ENVIRONMENT = 'development'  # development, staging, production

# API version
API_VERSION = '1.0'

# Chatbot version
CHATBOT_VERSION = '2.0-ollama'

# ==================== Environment-Specific Overrides ====================

# Production overrides
if ENVIRONMENT == 'production':
    CHATBOT_DEBUG = False
    SHOW_DETAILED_ERRORS = False
    LOG_LEVEL = "WARNING"
    AUDIT_LOG_ENABLED = True

# Development overrides
elif ENVIRONMENT == 'development':
    CHATBOT_DEBUG = True
    SHOW_DETAILED_ERRORS = True
    LOG_LEVEL = "DEBUG"
    AUDIT_LOG_ENABLED = True

# ==================== Flask Integration Example ====================

"""
Add to your Flask config file (config.py):

class Config:
    # Existing settings...
    
    # Ollama Configuration
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    OLLAMA_MODEL = "phi3"
    OLLAMA_TIMEOUT_SECONDS = 5
    OLLAMA_MAX_TOKENS = 200
    
    # Chatbot Settings
    CHATBOT_ENABLED = True
    CHATBOT_DEBUG = False
    CHATBOT_DEFAULT_LIMIT = 10
    CHATBOT_MAX_RESULTS = 100
    
    # Security
    RBAC_ENABLED = True
    ENFORCE_STUDENT_DATA_ISOLATION = True
    AUDIT_LOG_ENABLED = True
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_CHATBOT_INTERACTIONS = True
    LOG_SECURITY_EVENTS = True


# Then in app/__init__.py or main app creation:

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Verify Ollama is reachable
def verify_ollama():
    try:
        import requests
        response = requests.get(
            f"{app.config['OLLAMA_API_URL'].rsplit('/', 1)[0]}/tags",
            timeout=2
        )
        return response.status_code == 200
    except:
        return False

if app.config['CHATBOT_ENABLED']:
    if verify_ollama():
        print("✓ Ollama service is available")
    else:
        print("⚠ Ollama service not reachable - chatbot will use fallback")
"""

# ==================== Usage Examples ====================

"""
Using configuration in your code:

from flask import current_app

# Access Ollama settings
api_url = current_app.config['OLLAMA_API_URL']
timeout = current_app.config['OLLAMA_TIMEOUT_SECONDS']
max_results = current_app.config['CHATBOT_MAX_RESULTS']

# Check if feature is enabled
if current_app.config['CHATBOT_ENABLED']:
    # Use chatbot
    pass

# Get admin-only intents
admin_intents = current_app.config['ADMIN_ONLY_INTENTS']

# Check logging
if current_app.config['LOG_CHATBOT_INTERACTIONS']:
    logger.info(f"Intent executed: {intent}")
"""

# ==================== Security Settings ====================

"""
Important security settings:

1. ENFORCE_STUDENT_DATA_ISOLATION = True
   - Students can NEVER access other student's data
   - System overrides student_id to current user's ID
   - Audit logged

2. RBAC_ENABLED = True
   - Role-based access control enforced
   - Admin intents blocked for students
   - Permission check on every request

3. AUDIT_LOG_ENABLED = True
   - Every intent execution logged
   - User ID, intent, parameters, success/failure
   - Essential for compliance and debugging

4. LOG_SECURITY_EVENTS = True
   - Permission denials logged
   - Suspicious patterns detected
   - Helps identify attacks
"""

# ==================== Performance Tuning ====================

"""
To optimize performance:

1. Increase OLLAMA_MAX_TOKENS if responses are truncated
   Current: 200 tokens - suitable for most intents
   Max recommended: 300 tokens

2. Reduce OLLAMA_TIMEOUT_SECONDS if network is fast
   Current: 5 seconds - conservative, works on slow networks
   Min recommended: 2 seconds

3. Increase result limits if you have plenty of RAM
   Current defaults: ~100 items
   Large datasets might benefit from bumping to 500

4. Enable response caching for popular queries
   Set ENABLE_RESPONSE_CACHE = True (future feature)

5. Tune database query limits
   See MAX_*_PER_QUERY settings above
   Too high = memory issues, too low = incomplete results
"""

# ==================== Monitoring ====================

"""
Monitor these metrics in production:

1. Intent extraction success rate
   - Target: > 95%
   - < 95% means Ollama might be struggling

2. Average response time
   - Target: < 2 seconds for non-AI, < 5 seconds with AI
   - > 5 seconds might indicate Ollama issues

3. Permission denials
   - Track suspicious patterns
   - Students trying to access admin intents

4. Database query times
   - Should be < 100ms for indexed queries
   - Add indexes if > 200ms

5. Ollama API uptime
   - Should be > 99%
   - Fallback works but provides degraded UX
"""

# ==================== Troubleshooting Configuration ====================

"""
If chatbot is slow or failing:

1. Check Ollama is running:
   curl http://localhost:11434/api/tags

2. Increase timeout temporarily:
   OLLAMA_TIMEOUT_SECONDS = 10  # for testing

3. Enable debug logging:
   LOG_LEVEL = "DEBUG"
   CHATBOT_DEBUG = True

4. Check database indexes exist

5. Monitor Ollama resource usage:
   Memory, CPU, disk I/O

6. Test simple queries first:
   "hello" - uses fast path
   "show jobs" - uses keyword fallback
   "show opportunities" - uses Ollama AI
"""

# ==================== Compatibility ====================

"""
Compatibility notes:

Python: 3.8+
Flask: 2.0+
SQLAlchemy: 1.4+
Ollama: Latest (supports phi3)
Requests: 2.25+

Browser compatibility:
- All modern browsers
- Mobile browsers supported
- Requires JavaScript enabled
"""

# ==================== Version History ====================

"""
Chatbot Versions:

v1.0 - Original keyword-based system
  - Keyword matching
  - Limited intelligence
  - Fast response times

v2.0 - Ollama AI integration (CURRENT)
  - AI-powered intent extraction
  - 7 structured intents
  - Role-based security
  - 5-second timeout
  - Low RAM usage
  - Production-ready

v3.0 (Future)
  - Multi-turn conversations
  - Response caching
  - Custom prompt fine-tuning
  - Advanced analytics
  - WebSocket real-time updates
"""

print("""
✓ Chatbot Configuration Loaded
  Version: 2.0-ollama
  Model: phi3
  Status: Production-Ready
""")
