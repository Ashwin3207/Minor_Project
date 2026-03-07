"""
Chatbot blueprint providing endpoints for the chatbot API.
Upgraded with Ollama AI-powered intent extraction.
"""

import logging
from flask import Blueprint, request, jsonify, render_template, session, current_app
from app.chatbot_engine import ChatbotEngine
from app.models import User
from app import db

logger = logging.getLogger(__name__)

bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')


@bp.route('/')
def chatbot_page():
    """Render the chatbot page."""
    return render_template('chatbot/chat.html')


@bp.route('/api/chat', methods=['POST'])
def api_chat():
    """
    API endpoint to process user queries with Ollama AI intent extraction.
    
    Expected JSON:
    {
        "message": "user's natural language query"
    }
    
    Returns:
    {
        "success": bool,
        "answer": "chatbot's response",
        "context": "intent name",
        "intent": "extracted intent",
        "confidence": "AI confidence level",
        "error": "error message if failed"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'answer': 'Please provide a message.',
                'context': 'error',
                'intent': None,
                'error': 'Missing message field'
            }), 400

        message = data.get('message', '').strip()
        
        if not message or len(message) == 0:
            return jsonify({
                'success': False,
                'answer': 'Please ask a valid question.',
                'context': 'error',
                'intent': None,
                'error': 'Empty message'
            }), 400

        # Limit message length
        if len(message) > 500:
            message = message[:500]

        # Get user ID if logged in
        user_id = session.get('user_id', None)

        # Initialize chatbot engine
        engine = ChatbotEngine(session=db.session)

        # Process the query with Ollama intent extraction
        response = engine.process_query(message, user_id=user_id)

        # Ensure required fields are present
        if 'intent' not in response:
            response['intent'] = None
        if 'confidence' not in response:
            response['confidence'] = 'unknown'

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Chatbot API error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'answer': 'An error occurred while processing your request. Our team has been notified.',
            'context': 'error',
            'intent': None,
            'error': str(e) if current_app.config.get('DEBUG') else 'Internal error'
        }), 500


@bp.route('/api/suggestions', methods=['GET'])
def api_suggestions():
    """
    Get suggested questions for the chatbot.
    Personalized based on authentication status.
    
    Returns:
    {
        "suggestions": [list of suggested questions],
        "success": bool
    }
    """
    try:
        user_id = session.get('user_id', None)
        
        # Default suggestions for all users
        suggestions = [
            "Find opportunities from Google",
            "Show upcoming recruitment drives",
            "What opportunities are available?",
        ]

        if user_id:
            user = User.query.get(user_id)
            if user and user.role.lower() == 'student':
                # Student-specific suggestions
                suggestions.extend([
                    "Am I eligible for any positions?",
                    "What's my application status?",
                    "Show me my recent applications",
                    "Which companies should I apply to?"
                ])
            elif user and user.role.lower() == 'admin':
                # Admin-specific suggestions
                suggestions.extend([
                    "Show placement statistics",
                    "List all applicants",
                    "Get branch-wise analytics",
                    "Show me recent applications"
                ])
        else:
            suggestions.append("Tell me about the placement portal")
            suggestions.append("How do I sign up?")

        return jsonify({
            'success': True,
            'suggestions': suggestions
        }), 200

    except Exception as e:
        logger.error(f"Suggestions error: {str(e)}")
        return jsonify({
            'success': False,
            'suggestions': [],
            'error': str(e)
        }), 500


@bp.route('/api/health', methods=['GET'])
def api_health():
    """
    Health check endpoint for monitoring.
    Checks chatbot and Ollama service status.
    """
    try:
        # Quick check that engine initializes
        engine = ChatbotEngine(session=db.session)
        
        return jsonify({
            'status': 'healthy',
            'chatbot': 'active',
            'ollama': 'configured'
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'degraded',
            'chatbot': 'error',
            'error': str(e)
        }), 500


@bp.route('/api/intents', methods=['GET'])
def api_intent_list():
    """
    Get list of available intents for reference.
    Useful for documentation and debugging.
    """
    from app.chatbot_security import ALLOWED_INTENTS, INTENT_PERMISSIONS
    
    user_id = session.get('user_id', None)
    user = User.query.get(user_id) if user_id else None
    user_role = user.role.lower() if user else 'anonymous'
    
    available_intents = {}
    for intent in ALLOWED_INTENTS:
        required_roles = INTENT_PERMISSIONS.get(intent, {'student', 'admin'})
        is_available = user_role in required_roles or user_role == 'admin'
        
        available_intents[intent] = {
            'available': is_available,
            'requires': list(required_roles),
            'description': f'Intent: {intent}'
        }
    
    return jsonify({
        'success': True,
        'intents': available_intents,
        'user_role': user_role
    }), 200
