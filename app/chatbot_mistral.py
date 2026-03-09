"""
Mistral AI-powered intent extractor for the chatbot.
Converts natural language to structured intents using Mistral API.
Falls back to keyword matching if Mistral is unavailable.
"""

import json
import requests
import logging
import os
from typing import Optional, Dict
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger(__name__)


class MistralIntentExtractor:
    """Extract structured intents from natural language using Mistral AI."""
    
    # Mistral API configuration
    MISTRAL_API_URL = "https://api.mistral.ai/v1/messages"
    MODEL_NAME = "mistral-small-latest"  # Fast model for intent extraction
    TIMEOUT_SECONDS = 5
    
    # Track if Mistral is available (to reduce log spam)
    _mistral_available = None
    _connection_error_logged = False
    
    # Intent classification prompt template
    INTENT_PROMPT_TEMPLATE = """You are an intent extractor for a placement portal chatbot.

User message: "{user_message}"

Extract the user's intent and parameters into valid JSON format (no markdown, pure JSON only):
{{
  "intent": "one of: search_company, check_eligibility, application_status, upcoming_drives, placement_stats, list_applicants, branch_analytics",
  "parameters": {{
    "company": "company name if mentioned",
    "branch": "branch/department if mentioned",
    "student_id": "student id if mentioned",
    "limit": "number of results if mentioned, default 10"
  }},
  "confidence": "high/medium/low"
}}

Return ONLY valid JSON. If intent is unclear, use confidence: low."""
    
    def __init__(self):
        """Initialize the Mistral intent extractor."""
        self.api_url = self.MISTRAL_API_URL
        self.model_name = self.MODEL_NAME
        self.timeout = self.TIMEOUT_SECONDS
        self.api_key = os.getenv('MISTRAL_API_KEY')
        
        if not self.api_key and not self._connection_error_logged:
            logger.warning("MISTRAL_API_KEY environment variable not set. Mistral integration will be unavailable.")
            self._connection_error_logged = True
    
    @classmethod
    def _check_mistral_available(cls) -> bool:
        """Check if Mistral service is available. Only check once per session."""
        if cls._mistral_available is not None:
            return cls._mistral_available
        
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            cls._mistral_available = False
            return False
        
        try:
            # Try a quick test call
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "user", "content": "test"}
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                "https://api.mistral.ai/v1/messages",
                headers=headers,
                json=data,
                timeout=3
            )
            
            cls._mistral_available = response.status_code in [200, 201]
            if not cls._mistral_available:
                logger.warning(f"Mistral service returned status {response.status_code}. Using fallback intent matching.")
            return cls._mistral_available
        except (ConnectionError, Timeout, RequestException) as e:
            cls._mistral_available = False
            if not cls._connection_error_logged:
                logger.warning("Mistral service is not available. Using fallback intent matching. "
                             f"Error: {str(e)}")
                cls._connection_error_logged = True
            return False
        except Exception as e:
            cls._mistral_available = False
            logger.warning(f"Error checking Mistral availability: {str(e)}")
            return False
    
    def extract_intent(self, user_message: str) -> Optional[Dict]:
        """
        Extract intent from user message using Mistral AI.
        Falls back to None if Mistral is unavailable.
        
        Args:
            user_message: Natural language query from user
            
        Returns:
            Dictionary with intent, parameters, and confidence, or None if extraction fails
        """
        if not user_message or not isinstance(user_message, str):
            return None
        
        if not self.api_key:
            return None
        
        # Quick check if Mistral is available
        if not self._check_mistral_available():
            return None
        
        user_message = user_message.strip()[:500]  # Limit input length
        
        try:
            prompt = self.INTENT_PROMPT_TEMPLATE.format(user_message=user_message)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 200,
                "temperature": 0.3  # Low temperature for consistent intent extraction
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code not in [200, 201]:
                logger.error(f"Mistral API error: {response.status_code} - {response.text}")
                return None
            
            # Parse response
            result = response.json()
            response_text = result.get('content', [{}])[0].get('text', '')
            
            if not response_text:
                logger.error("Mistral returned empty content")
                return None
            
            # Extract JSON from response (might have markdown code blocks)
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith('```'):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove trailing ```
            
            # Parse JSON
            intent_data = json.loads(response_text.strip())
            
            # Validate extracted intent
            if 'intent' not in intent_data or 'confidence' not in intent_data:
                logger.warning(f"Invalid intent structure from Mistral: {intent_data}")
                return None
            
            # Ensure confidence is one of the allowed values
            confidence = intent_data.get('confidence', 'low').lower()
            if confidence not in ['high', 'medium', 'low']:
                confidence = 'low'
            intent_data['confidence'] = confidence
            
            logger.debug(f"Mistral extracted intent: {intent_data.get('intent')} (confidence: {confidence})")
            return intent_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Mistral JSON response: {str(e)}")
            return None
        except Timeout:
            logger.error("Mistral API request timed out")
            return None
        except RequestException as e:
            logger.error(f"Mistral API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Mistral extraction: {str(e)}")
            return None


# Global instance for use across app
_mistral_extractor = None


def get_mistral_extractor() -> MistralIntentExtractor:
    """Get or create the Mistral intent extractor instance."""
    global _mistral_extractor
    if _mistral_extractor is None:
        _mistral_extractor = MistralIntentExtractor()
    return _mistral_extractor


def mistral_intent_extractor(user_message: str) -> Optional[Dict]:
    """
    Convenience function to extract intent using Mistral.
    
    Args:
        user_message: Natural language query from user
        
    Returns:
        Dictionary with intent, parameters, and confidence, or None
    """
    extractor = get_mistral_extractor()
    return extractor.extract_intent(user_message)
