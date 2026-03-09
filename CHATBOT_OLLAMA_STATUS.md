# Chatbot Ollama Configuration & Fallback

## Overview

The chatbot system now includes intelligent fallback handling for when Ollama (AI intent extraction) is unavailable. The system will automatically work with keyword-based matching when Ollama service is not running.

## Status Check

On application startup, the system checks if Ollama is available:

```
✓ Ollama service is available - AI intent extraction enabled
OR
⚠ Ollama service unavailable - Using keyword-based fallback for intent matching
```

## How It Works

### With Ollama (AI-Powered, Preferred)
- Uses Ollama's phi3 model for natural language intent extraction
- Better understanding of user queries
- Extracts structured parameters from queries
- Confidence levels: high/medium/low

### Without Ollama (Fallback, Still Functional)
- Automatic fallback to keyword matching
- Detects intents based on keywords in user message
- Examples:
  - "find companies" → `search_company`
  - "am I eligible?" → `check_eligibility`
  - "application status" → `application_status`
  - "placement statistics" → `placement_stats`
  - "when are recruitment drives?" → `upcoming_drives`
- Confidence level: always "low" for fallback

## Enabling Ollama

### Prerequisites
- Windows, macOS, or Linux
- At least 4GB RAM
- Port 11434 available

### Installation & Running

1. **Download & Install Ollama**
   - Download from: https://ollama.ai
   - Follow installation instructions for your OS

2. **Pull the phi3 Model**
   ```bash
   ollama pull phi3
   ```

3. **Run Ollama Service**
   ```bash
   ollama serve
   ```
   - On Windows: Ollama may run as a system service (check system tray)
   - Service will be available at: `http://localhost:11434`

4. **Verify Installation**
   ```bash
   curl http://localhost:11434/api/tags
   ```
   - Should return a JSON response with available models

### Restarting the Application
Once Ollama is running, restart your Flask application. The system will automatically detect and enable AI intent extraction.

## Testing the Chatbot

### Test Queries

**With Ollama:**
```
"Find software engineer positions from Microsoft"
→ Intent: search_company
→ Parameters: {company: "Microsoft"}
→ Confidence: high

"Am I eligible for this internship?"
→ Intent: check_eligibility
→ Confidence: medium
```

**Without Ollama (Fallback):**
```
"Find jobs"
→ Intent: search_company (from keyword matching)
→ Confidence: low

"Check my application status"
→ Intent: application_status (from keyword matching)
→ Confidence: low
```

## Logging

### Log Levels

- **INFO**: "✓ Ollama service is available" - Ollama detected and working
- **WARNING**: "⚠ Ollama service unavailable" - Fallback to keyword matching
- **DEBUG**: Detailed intent extraction messages (only in development)

### Log Output Location
- Console output during development
- `logs/` directory (if configured) in production

### Reducing Log Spam

The system only logs Ollama unavailability **ONCE per application start** to avoid cluttering logs. Subsequent requests use fallback silently.

## Performance

### With Ollama
- First request: ~200-500ms (includes Ollama processing)
- Subsequent requests: ~100-300ms (cached model)

### Without Ollama
- All requests: ~10-50ms (simple keyword matching)

## Troubleshooting

### Ollama Not Detected
**Problem**: System shows "⚠ Ollama service unavailable" on startup
**Solution**:
1. Ensure Ollama is installed from https://ollama.ai
2. Run `ollama serve` in terminal
3. Verify port 11434 is not blocked
4. Restart the Flask application

### Slow Chatbot Responses
**Problem**: Chatbot taking too long to respond
**Solution**:
1. Check if Ollama service is running
2. Verify system RAM (Ollama needs ~2GB for phi3 model)
3. Check network/localhost connection
4. Consider using lighter model if available

### High Memory Usage
**Problem**: System running out of memory when Ollama is active
**Solution**:
1. Ollama caches models in memory (~2-4GB for phi3)
2. Close other applications
3. Configure Ollama to unload models when idle (optional)

## Model Information

**Current Model**: phi3
- **Size**: ~2.3GB
- **RAM Required**: ~4GB during operation
- **Speed**: Fast (relative to larger models)
- **Accuracy**: Good for task-specific intent extraction

**Alternative Models** (if needed):
- `mistral`: Larger, slower, potentially more accurate
- `neural-chat`: Specialized for chat tasks
- Custom fine-tuned models

To switch models:
```bash
ollama pull <model_name>
# Then modify app/chatbot_ollama.py: MODEL_NAME = "<model_name>"
```

## Configuration

### Default Settings (app/chatbot_ollama.py)

```python
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"
TIMEOUT_SECONDS = 3  # Fallback timeout
MAX_TOKENS = 200
```

### Customization

To change Ollama configuration, edit `app/chatbot_ollama.py`:

```python
class OllamaIntentExtractor:
    # Change these values:
    OLLAMA_API_URL = "http://your-host:port/api/generate"
    MODEL_NAME = "your-model-name"
    TIMEOUT_SECONDS = 5  # Increase if timeouts occur
```

## API Response Format

Whether using Ollama or fallback, the API response includes:

```json
{
  "success": true,
  "answer": "Here are the software engineer positions...",
  "intent": "search_company",
  "confidence": "high",  // or "low" for fallback
  "context": "search_company"
}
```

## Summary

| Feature | With Ollama | Without Ollama |
|---------|-------------|----------------|
| Intent Detection | AI (Accurate) | Keywords (Basic) |
| Speed | 100-500ms | 10-50ms |
| Memory | 2-4GB | Minimal |
| Confidence | High/Medium/Low | Low |
| Parameter Extraction | Advanced | Basic |
| User Experience | Optimal | Functional |

The chatbot remains **fully functional** in both scenarios!
