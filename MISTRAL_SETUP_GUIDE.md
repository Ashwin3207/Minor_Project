# Mistral AI Chatbot Integration Guide

## Overview

Your Training & Placement Portal now includes integrated **Mistral AI** chatbot support! The system automatically detects and uses the best available AI service for intent extraction.

## Intent Extraction Priority

The chatbot uses a smart fallback system:

1. **Mistral AI** (Cloud-based - Recommended)
   - Most capable for complex queries
   - Requires API key
   - Faster for production use

2. **Ollama** (Local deployment)
   - Free, privacy-focused
   - Runs on `localhost:11434`
   - Good for development

3. **Keyword Fallback** (Built-in)
   - Always available offline
   - Pattern-matching based
   - Lower accuracy but reliable

## Quick Setup

### Option 1: Using Mistral AI (Recommended for Production)

#### 1. Get Mistral API Key

1. Visit [Mistral AI Console](https://console.mistral.ai)
2. Sign up for a free account
3. Create an API key in the console
4. You'll receive a free tier with rate limits

#### 2. Configure Environment Variable

Create or update your `.env` file:

```bash
# .env file
MISTRAL_API_KEY=your_mistral_api_key_here
```

Or set it in your deployment platform:
- **Render**: Add to Environment Variables in dashboard
- **Heroku**: `heroku config:set MISTRAL_API_KEY=your_key`
- **Local Development**: Add to `.env` file

#### 3. Verify Configuration

```python
# Quick test in Python
import os
from app.chatbot_mistral import mistral_intent_extractor

# Check if configured
api_key = os.getenv('MISTRAL_API_KEY')
print(f"Mistral configured: {bool(api_key)}")

# Test extraction
result = mistral_intent_extractor("Find opportunities from Google")
print(result)
```

### Option 2: Using Ollama (Development/Privacy)

#### 1. Install Ollama

- Download from [ollama.ai](https://ollama.ai)
- Install and run the Ollama service
- The app will auto-detect it on `localhost:11434`

#### 2. Pull a Model

```bash
ollama pull phi3
```

#### 3. Verify Setup

Ollama runs automatically when installed. The chatbot will detect it on startup.

## Configuration Options

### Environment Variables

```bash
# Required for Mistral
MISTRAL_API_KEY=sk-your-api-key-here

# Optional for customization
CHATBOT_AI_PROVIDER=mistral  # Force provider (mistral/ollama/fallback)
MISTRAL_MODEL=mistral-small-latest  # Mistral model to use
```

### Supported Mistral Models

- `mistral-small-latest` - Fast, efficient (default)
- `mistral-medium-latest` - Balanced performance
- `mistral-large-latest` - Most capable (higher cost)

## API Response Format

All chatbot API calls return the same format:

```json
{
  "success": true,
  "answer": "Here are opportunities from Google...",
  "context": "search_company",
  "intent": "search_company",
  "confidence": "high",
  "extraction_method": "mistral",
  "data": {
    "results": [...]
  }
}
```

**Key Fields:**
- `extraction_method`: Shows which AI provider was used (mistral/ollama/keyword_fallback)
- `confidence`: Reliability of the intent (high/medium/low)
- `intent`: Extracted user intent
- `answer`: Formatted response for user

## Example Usage

### JavaScript (Chat UI)

```javascript
async function sendMessage(message) {
  const response = await fetch('/chatbot/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: message})
  });
  
  const data = await response.json();
  console.log('Used AI provider:', data.extraction_method);
  console.log('Confidence:', data.confidence);
  console.log('Answer:', data.answer);
  
  return data;
}

// Example queries
sendMessage("Find senior engineer positions from Google");
sendMessage("Check my eligibility");
sendMessage("Show upcoming recruitment drives");
```

### Python (Backend)

```python
from app.chatbot_engine import ChatbotEngine

engine = ChatbotEngine()
result = engine.process_query("Find opportunities from Microsoft", user_id=user_id)

print(f"Method: {result.get('extraction_method')}")
print(f"Intent: {result.get('intent')}")
print(f"Confidence: {result.get('confidence')}")
print(f"Response: {result.get('answer')}")
```

## Supported Intents

The chatbot can handle these intents:

- **search_company** - Find opportunities from specific companies
- **check_eligibility** - Check if student meets position requirements
- **application_status** - Track application progress
- **upcoming_drives** - View recruitment schedule
- **placement_stats** - View placement statistics
- **list_applicants** - List all applicants (admin only)
- **branch_analytics** - Get branch-wise analytics (admin only)

## Example Queries

### Student Queries
- "Find opportunities from Google"
- "Show me software engineer positions"
- "What's my application status?"
- "Am I eligible for this role?"
- "When are the upcoming drives?"
- "Show placement statistics"

### Admin Queries
- "List all applicants for Microsoft"
- "Get branch-wise analytics"
- "Show applicants with CGPA above 8.0"

## Troubleshooting

### Issue: "Using fallback intent matching"

**Cause:** Both Mistral and Ollama are unavailable

**Solution:**
1. Check if `MISTRAL_API_KEY` is set: `echo $MISTRAL_API_KEY`
2. Check Ollama is running: `curl http://localhost:11434/api/tags`
3. Check internet connection for Mistral API

### Issue: Mistral API returns 401 Unauthorized

**Cause:** Invalid API key

**Solution:**
1. Verify API key in console.mistral.ai
2. Regenerate key if needed
3. Ensure no extra spaces in environment variable

### Issue: Slow responses

**Cause:** Using Ollama or fallback (slower than Mistral)

**Solution:**
1. Add `MISTRAL_API_KEY` for cloud-based processing
2. Check network connectivity
3. Mistral-small is faster; avoid mistral-large for speed

### Issue: Intents not recognized

**Cause:** Complex phrasing or accent

**Solution:**
1. Use clearer, simpler phrasing
2. Check logs for extracted intent: `extraction_method` in response
3. Consider switching to Mistral-large for complex queries

## Deployment Instructions

### Render.com (Recommended)

1. Go to Dashboard > Environment
2. Add variable: `MISTRAL_API_KEY` = your key
3. Redeploy

### Local Development

```bash
# Create .env file
echo "MISTRAL_API_KEY=your_key_here" > .env

# Install dependencies
pip install -r requirements.txt

# Run app
python run.py
```

### Docker

```dockerfile
ENV MISTRAL_API_KEY=${MISTRAL_API_KEY}
```

## Costs

### Mistral AI (Free Tier)
- Limited free tier with rate limits
- Paid plans: See [mistral.ai pricing](https://mistral.ai/pricing)
- Typical cost: < $1 per 1,000 requests for small model

### Ollama (Free)
- Completely free
- Self-hosted (privacy)
- Higher latency for users

## Performance Metrics

### Response Times (Approximate)

| Method | Time | Cost |
|--------|------|------|
| Mistral | 0.5-1.5s | ~$0.0001 per message |
| Ollama | 2-5s | Free |
| Keyword Fallback | <0.1s | Free |

## Security Considerations

1. **Mistral API Key**
   - Keep in environment variables (never commit to git)
   - Use `.gitignore` for `.env` files
   - Rotate keys periodically

2. **Rate Limiting**
   - Monitor Mistral free tier limits
   - Implement request throttling if needed
   - Consider switching to paid plan for high volume

3. **Data Privacy**
   - User queries sent to Mistral servers
   - For privacy-critical deployments, use Ollama
   - Student data is sanitized before extraction

## Monitoring

### Check Mistral Health

```bash
# View logs for Mistral errors
tail -f logs/app.log | grep mistral

# Quick health check
curl https://api.mistral.ai/v1/messages \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"mistral-small-latest","messages":[{"role":"user","content":"test"}]}'
```

### Fallback Detection

The app logs when it falls back:
```
DEBUG: Intent extracted using mistral: search_company
DEBUG: Using fallback intent matching  
DEBUG: Both Mistral and Ollama unavailable
```

## Next Steps

1. ✅ **Get Mistral API Key** from console.mistral.ai
2. ✅ **Set environment variable** `MISTRAL_API_KEY`
3. ✅ **Test the chatbot** with sample queries
4. ✅ **Monitor logs** to verify Mistral is being used
5. ✅ **Collect feedback** from users

## Resources

- [Mistral AI Docs](https://docs.mistral.ai)
- [Mistral Console](https://console.mistral.ai)
- [Ollama Documentation](https://ollama.ai)
- [Chat UI Template](templates/chatbot/chat.html)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs: `tail -f logs/app.log`
3. Test manually: Use the API endpoint `/chatbot/api/chat`
4. Check Mistral status: Visit status.mistral.ai

---

**Last Updated:** March 7, 2026  
**Version:** Mistral Integration v1.0
