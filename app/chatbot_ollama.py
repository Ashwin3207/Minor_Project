"""
Ollama-powered intent extractor for the chatbot.
Converts natural language to structured intents using TinyLlama model.
Falls back to keyword matching if Ollama is unavailable.
"""

import json
import requests
import logging
from typing import Optional, Dict
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger(__name__)


class OllamaIntentExtractor:
    """Extract structured intents from natural language using Ollama."""
    
    # Ollama API configuration
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "tinyllama"  # Lightweight default model for local inference
    TIMEOUT_SECONDS = 30  # Increased from 3 to 30 seconds for Ollama response time
    MAX_TOKENS = 200
    
    # Track if Ollama is available (to reduce log spam)
    _ollama_available = None
    _connection_error_logged = False
    
    # Intent classification prompt template - simplified for Ollama
    INTENT_PROMPT_TEMPLATE = """Extract intent from: {user_message}

Return JSON only:
{{"intent": "search_company", "parameters": {{"company": null}}, "confidence": "high"}}

Possible intents: search_company, check_eligibility, application_status, upcoming_drives, placement_stats, list_applicants, branch_analytics"""
    
    def __init__(self):
        """Initialize the intent extractor."""
        self.api_url = self.OLLAMA_API_URL
        self.model_name = self.MODEL_NAME
        self.timeout = self.TIMEOUT_SECONDS
    
    @classmethod
    def _check_ollama_available(cls) -> bool:
        """Check if Ollama service is running. Checks every time."""
        try:
            # Try a quick health check
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=2
            )
            if response.status_code == 200:
                cls._ollama_available = True
                cls._connection_error_logged = False
                return True
            cls._ollama_available = False
            return False
        except (ConnectionError, Timeout, RequestException):
            cls._ollama_available = False
            # Only log error once
            if not cls._connection_error_logged:
                logger.warning("Ollama service is not available. Using fallback intent matching. "
                             f"Make sure Ollama is running on {cls.OLLAMA_API_URL}")
                cls._connection_error_logged = True
            return False
        
    def extract_intent(self, user_message: str) -> Optional[Dict]:
        """
        Extract intent from user message using Ollama.
        Falls back to None if Ollama is unavailable.
        
        Args:
            user_message: Natural language query from user
            
        Returns:
            Dictionary with intent, parameters, and confidence, or None if extraction fails
        """
        if not user_message or not isinstance(user_message, str):
            return None
        
        # Quick check if Ollama is available
        if not self._check_ollama_available():
            return None  # Let the fallback handle it
        
        user_message = user_message.strip()[:500]  # Limit input length
        
        try:
            prompt = self.INTENT_PROMPT_TEMPLATE.format(user_message=user_message)
            
            logger.debug(f"Extracting intent with Ollama from: '{user_message[:100]}'")
            
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,  # Lower temperature for consistency
                    "num_predict": self.MAX_TOKENS,
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.debug(f"Ollama API returned status {response.status_code}")
                # Mark Ollama as unavailable if we get errors
                OllamaIntentExtractor._ollama_available = False
                return None
            
            response_data = response.json()
            response_text = response_data.get('response', '').strip()
            
            if not response_text:
                logger.debug("Empty response from Ollama")
                return None
            
            logger.debug(f"Ollama raw response: {response_text[:100]}")
            
            # Parse JSON response
            intent_data = self._parse_response(response_text)
            
            if intent_data:
                logger.debug(f"Intent extracted: {intent_data.get('intent')} (confidence: {intent_data.get('confidence')})")
            else:
                logger.debug(f"Failed to parse intent from response")
            
            return intent_data
            
        except (ConnectionError, Timeout) as e:
            # Connection errors are expected when Ollama is not running
            if not OllamaIntentExtractor._connection_error_logged:
                logger.debug(f"Cannot connect to Ollama service. Using fallback matching.")
                OllamaIntentExtractor._connection_error_logged = True
            OllamaIntentExtractor._ollama_available = False
            return None
        except RequestException as e:
            logger.debug(f"Ollama API request failed (expected if service not running)")
            OllamaIntentExtractor._ollama_available = False
            return None
        except Exception as e:
            logger.debug(f"Intent extraction error: {str(e)}")
            return None
    
    def _parse_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse JSON from Ollama response.
        
        Args:
            response_text: Raw response text from Ollama
            
        Returns:
            Parsed JSON dict with intent info, or None if parsing fails
        """
        try:
            # Try to extract JSON object
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if not json_match:
                logger.warning("No JSON found in response")
                return None
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Validate required fields
            if 'intent' not in data:
                logger.warning("Missing 'intent' field in response")
                return None
            
            intent = str(data['intent']).lower().strip()
            
            # Validate against allowed intents
            from app.chatbot_security import ALLOWED_INTENTS
            if intent not in ALLOWED_INTENTS:
                logger.warning(f"Unknown intent: {intent}")
                return None
            
            # Extract parameters
            parameters = data.get('parameters', {})
            if not isinstance(parameters, dict):
                parameters = {}
            
            confidence = data.get('confidence', 'low')
            
            # Clean up parameters
            cleaned_params = {}
            if 'company' in parameters:
                val = parameters['company']
                if val and isinstance(val, str):
                    cleaned_params['company'] = val[:100]
            
            if 'branch' in parameters:
                val = parameters['branch']
                if val and isinstance(val, str):
                    cleaned_params['branch'] = val[:50]
            
            if 'student_id' in parameters:
                try:
                    cleaned_params['student_id'] = int(parameters['student_id'])
                except (ValueError, TypeError):
                    pass
            
            if 'limit' in parameters:
                try:
                    limit = int(parameters['limit'])
                    cleaned_params['limit'] = min(limit, 100)
                except (ValueError, TypeError):
                    cleaned_params['limit'] = 10
            else:
                cleaned_params['limit'] = 10
            
            return {
                'intent': intent,
                'parameters': cleaned_params,
                'confidence': confidence
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Response parsing error: {str(e)}")
            return None


# Singleton instance
_extractor = None


def get_intent_extractor() -> OllamaIntentExtractor:
    """Get or create the intent extractor singleton."""
    global _extractor
    if _extractor is None:
        _extractor = OllamaIntentExtractor()
    return _extractor


def ollama_intent_extractor(user_message: str) -> Optional[Dict]:
    """
    Extract intent using Ollama service.
    
    Args:
        user_message: User's natural language query
        
    Returns:
        Dict with 'intent', 'parameters', 'confidence' or None
    """
    extractor = get_intent_extractor()
    return extractor.extract_intent(user_message)
