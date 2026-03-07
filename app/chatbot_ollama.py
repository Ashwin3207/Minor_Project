"""
Ollama-powered intent extractor for the chatbot.
Converts natural language to structured intents using phi3 model.
"""

import json
import requests
import logging
from typing import Optional, Dict
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)


class OllamaIntentExtractor:
    """Extract structured intents from natural language using Ollama."""
    
    # Ollama API configuration
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "phi3"
    TIMEOUT_SECONDS = 5
    MAX_TOKENS = 200
    
    # Intent classification prompt template
    INTENT_PROMPT_TEMPLATE = """You are an intent extractor for a placement portal chatbot.

User message: "{user_message}"

Extract the user's intent and parameters into valid JSON format (no markdown, pure JSON):
{{
  "intent": "one_of: search_company, check_eligibility, application_status, upcoming_drives, placement_stats, list_applicants, branch_analytics",
  "parameters": {{
    "company": "company name if mentioned",
    "branch": "branch/department if mentioned",
    "student_id": "student id if mentioned",
    "limit": "number of results if mentioned, default 10"
  }},
  "confidence": "high/medium/low"
}}

Only return valid JSON. If intent is unclear, use confidence: low."""
    
    def __init__(self):
        """Initialize the intent extractor."""
        self.api_url = self.OLLAMA_API_URL
        self.model_name = self.MODEL_NAME
        self.timeout = self.TIMEOUT_SECONDS
        
    def extract_intent(self, user_message: str) -> Optional[Dict]:
        """
        Extract intent from user message using Ollama.
        
        Args:
            user_message: Natural language query from user
            
        Returns:
            Dictionary with intent, parameters, and confidence, or None if extraction fails
        """
        if not user_message or not isinstance(user_message, str):
            return None
        
        user_message = user_message.strip()[:500]  # Limit input length
        
        try:
            prompt = self.INTENT_PROMPT_TEMPLATE.format(user_message=user_message)
            
            logger.info(f"Extracting intent from: '{user_message}'")
            
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
                logger.warning(f"Ollama API returned status {response.status_code}")
                return None
            
            response_data = response.json()
            response_text = response_data.get('response', '').strip()
            
            if not response_text:
                logger.warning("Empty response from Ollama")
                return None
            
            logger.debug(f"Ollama raw response: {response_text[:200]}")
            
            # Parse JSON response
            intent_data = self._parse_response(response_text)
            
            if intent_data:
                logger.info(f"Intent extracted: {intent_data.get('intent')} (confidence: {intent_data.get('confidence')})")
            else:
                logger.warning(f"Failed to parse intent from response")
            
            return intent_data
            
        except Timeout:
            logger.error(f"Ollama API timeout after {self.timeout}s")
            return None
        except RequestException as e:
            logger.error(f"Ollama API request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Intent extraction error: {str(e)}")
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
