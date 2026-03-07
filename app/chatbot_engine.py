"""
Upgraded Chatbot engine with Ollama AI integration for intent extraction.
Handles natural language processing with local phi3 model.
"""

import logging
from typing import Optional, Dict
from app.chatbot_ollama import ollama_intent_extractor
from app.chatbot_intent_router import secure_intent_router
from app.chatbot_security import (
    validate_json_response,
    ALLOWED_INTENTS
)
from app.models import User, StudentProfile, Opportunity, Application
from app import db
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatbotEngine:
    """
    Advanced chatbot engine using Ollama for intent detection.
    Combines AI-powered intent extraction with secure execution.
    """
    
    def __init__(self, session=None):
        """Initialize the upgraded chatbot engine."""
        self.session = session or db.session
        self.router = secure_intent_router(db)
    
    def process_query(self, user_message: str, user_id: int = None) -> dict:
        """
        Process user message using Ollama intent extraction.
        
        Args:
            user_message: Natural language query from user
            user_id: Optional logged-in user ID
            
        Returns:
            Dictionary with answer, success status, and context
        """
        if not user_message or not isinstance(user_message, str):
            return {
                'answer': 'Please provide a valid message.',
                'success': False,
                'context': 'error',
                'intent': None
            }
        
        user_message = user_message.strip()
        
        # Check for greeting first (faster than AI)
        greeting = self._check_greeting(user_message)
        if greeting:
            return greeting
        
        try:
            # Extract intent using Ollama
            intent_data = ollama_intent_extractor(user_message)
            
            if not intent_data:
                # Fallback to keyword matching if AI extraction fails
                logger.info("Ollama extraction failed, using fallback")
                return self._fallback_response(user_message, user_id)
            
            intent = intent_data.get('intent')
            parameters = intent_data.get('parameters', {})
            confidence = intent_data.get('confidence', 'low')
            
            # Route and execute intent
            result = self.router.route_intent(intent, parameters, user_id)
            
            if result['success']:
                # Format answer from router result
                answer = self._format_answer(result['intent'], result['data'])
                
                return {
                    'answer': answer,
                    'success': True,
                    'context': intent,
                    'intent': intent,
                    'confidence': confidence,
                    'data': result['data']
                }
            else:
                return {
                    'answer': f"I couldn't process that request: {result.get('error', 'Unknown error')}",
                    'success': False,
                    'context': 'error',
                    'intent': intent,
                    'error': result.get('error')
                }
        
        except Exception as e:
            logger.error(f"Query processing error: {str(e)}", exc_info=True)
            return {
                'answer': 'An error occurred while processing your request. Please try again.',
                'success': False,
                'context': 'error',
                'intent': None,
                'error': str(e)
            }
    
    def _check_greeting(self, message: str) -> Optional[dict]:
        """Check if message is a greeting."""
        message_lower = message.lower().strip()
        
        greetings = {
            'hello': 'Hello! I am your Training & Placement Assistant. I can help you search companies, check eligibility, track applications, and more. What would you like to know?',
            'hi': 'Hi there! How can I assist you today?',
            'hey': 'Hey! Feel free to ask me about opportunities, jobs, or your applications.',
            'thanks': "You're welcome! Feel free to ask if you need anything else.",
            'thank you': "You're welcome! Is there anything else I can help you with?",
            'bye': 'Goodbye! Good luck with your placements!',
            'goodbye': 'Goodbye! Feel free to come back anytime.',
            'help': self._get_help_text(),
        }
        
        for greeting, response in greetings.items():
            if greeting in message_lower:
                return {
                    'answer': response,
                    'success': True,
                    'context': 'greeting',
                    'intent': None
                }
        
        return None
    
    def _format_answer(self, intent: str, data: dict) -> str:
        """Format router result into readable answer."""
        if not data:
            return "I found some information but couldn't format it properly."
        
        message = data.get('message', '')
        
        if intent == 'search_company':
            results = data.get('results', [])
            if not results:
                return message or "No companies found matching your search."
            
            answer = f"{message}\n\n"
            for r in results[:5]:  # Limit to 5 results
                answer += f"• **{r['title']}** from {r['company']} ({r['type']})\n"
                if r.get('ctc'):
                    answer += f"  CTC: {r['ctc']}\n"
                if r.get('deadline'):
                    answer += f"  Deadline: {r['deadline'][:10]}\n"
            
            if len(results) > 5:
                answer += f"\n...and {len(results) - 5} more results."
            
            return answer
        
        elif intent == 'check_eligibility':
            eligible = data.get('eligible', [])
            if not eligible:
                return message or "You don't meet the criteria for available opportunities."
            
            answer = f"{message}\n\n"
            for e in eligible[:5]:
                answer += f"• **{e['title']}** from {e['company']}\n"
                if e.get('deadline'):
                    answer += f"  Deadline: {e['deadline'][:10]}\n"
            
            return answer
        
        elif intent == 'application_status':
            apps = data.get('applications', [])
            if not apps:
                return message or "No applications found."
            
            answer = f"{message}\n\n"
            status_counts = {}
            for app in apps[:10]:
                status = app.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                answer += f"• {app['company']} - **{status}**\n"
            
            answer += "\n**Summary:**\n"
            for status, count in status_counts.items():
                answer += f"• {status}: {count}\n"
            
            return answer
        
        elif intent == 'upcoming_drives':
            drives = data.get('drives', [])
            if not drives:
                return message or "No upcoming drives found."
            
            answer = f"{message}\n\n"
            for drive in drives[:10]:
                days = drive.get('days_left', 0)
                answer += f"• **{drive['title']}** from {drive['company']}\n"
                answer += f"  {days} days left, Deadline: {drive['deadline'][:10]}\n"
                if drive.get('ctc'):
                    answer += f"  CTC: {drive['ctc']}\n"
            
            return answer
        
        elif intent == 'placement_stats':
            stats = data.get('stats', {})
            answer = f"{message}\n\n**Key Stats:**\n"
            answer += f"• Total Students: {stats.get('total_students', 0)}\n"
            answer += f"• Placed Students: {stats.get('placed_students', 0)}\n"
            answer += f"• Placement Rate: {stats.get('placement_rate', 'N/A')}\n"
            answer += f"• Total Applications: {stats.get('total_applications', 0)}\n"
            
            if stats.get('by_status'):
                answer += "\n**Applications by Status:**\n"
                for status, count in stats['by_status'].items():
                    answer += f"• {status}: {count}\n"
            
            return answer
        
        elif intent == 'list_applicants':
            applicants = data.get('applicants', [])
            answer = f"{message}\n\n**Applicants (showing {min(10, len(applicants))} of {len(applicants)}):**\n"
            for app in applicants[:10]:
                answer += f"• {app['name']} ({app['email']}) - CGPA: {app['cgpa']} - Status: {app['status']}\n"
            
            return answer
        
        elif intent == 'branch_analytics':
            analytics = data.get('analytics', {})
            answer = f"{message}\n\n"
            for branch, stats in analytics.items():
                answer += f"**{branch}:**\n"
                answer += f"  • Students: {stats['students']}\n"
                answer += f"  • Avg CGPA: {stats['avg_cgpa']}\n"
                answer += f"  • Placed: {stats['placed']}/{stats['students']}\n"
                answer += f"  • Applications: {stats['applications']}\n"
            
            return answer
        
        else:
            return message or "Request processed."
    
    def _fallback_response(self, message: str, user_id: int = None) -> dict:
        """Provide helpful fallback when intent extraction fails."""
        message_lower = message.lower()
        
        # Simple keyword-based fallback
        if any(word in message_lower for word in ['opportunity', 'opportunities', 'job', 'opening']):
            opps = Opportunity.query.limit(5).all()
            answer = f"Found {Opportunity.query.count()} opportunities. Here are some:\n\n"
            for opp in opps:
                answer += f"• {opp.title} from {opp.company_name}\n"
            return {
                'answer': answer,
                'success': True,
                'context': 'search_company',
                'intent': 'search_company'
            }
        
        elif any(word in message_lower for word in ['your application', 'my application', 'status']):
            if not user_id:
                return {
                    'answer': 'Please log in to check your application status.',
                    'success': False,
                    'context': 'auth_required',
                    'intent': 'application_status'
                }
            
            apps = Application.query.filter_by(student_id=user_id).all()
            answer = f"You have {len(apps)} applications:\n\n"
            for app in apps[:5]:
                company = app.opportunity.company_name if app.opportunity else 'Unknown'
                answer += f"• {company} - {app.status}\n"
            
            return {
                'answer': answer,
                'success': True,
                'context': 'application_status',
                'intent': 'application_status'
            }
        
        elif any(word in message_lower for word in ['eligible', 'eligibility']):
            if not user_id:
                return {
                    'answer': 'Please log in to check your eligibility.',
                    'success': False,
                    'context': 'auth_required',
                    'intent': 'check_eligibility'
                }
            
            return {
                'answer': 'I can help you check eligibility. Please provide more details about the position you\'re interested in.',
                'success': True,
                'context': 'check_eligibility',
                'intent': 'check_eligibility'
            }
        
        return {
            'answer': 'I didn\'t quite understand that. Try asking about opportunities, job openings, your applications, or whether you\'re eligible for positions.',
            'success': False,
            'context': 'unknown_intent',
            'intent': None
        }
    
    def _get_help_text(self) -> str:
        """Return help text."""
        return '''I'm your AI-powered Training & Placement Assistant! Here's what I can help you with:

**Search & Explore:**
• "Search for software engineer positions"
• "Find opportunities from Google"
• "Show upcoming recruitment drives"

**Check Your Status:**
• "What's my application status?"
• "Am I eligible for any positions?"
• "What positions am I applied to?"

**Placement Analytics (Admin):**
• "Show placement statistics"
• "List all applicants"
• "Get branch-wise analytics"

**Tips:**
Ask in natural language - I use AI to understand your intent!
Examples:
- "Can I apply for senior engineer role at Microsoft?"
- "Show me upcoming internship deadlines"
- "How many companies have I applied to?"

What would you like to know?'''
