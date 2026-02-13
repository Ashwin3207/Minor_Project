"""
Chatbot blueprint providing endpoints for the chatbot API.
"""

from flask import Blueprint, request, jsonify, render_template, session
from app.chatbot_engine import ChatbotEngine
from app.models import User
from app import db

bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')


@bp.route('/')
def chatbot_page():
    """Render the chatbot page."""
    return render_template('chatbot/chat.html')


@bp.route('/api/chat', methods=['POST'])
def api_chat():
    """
    API endpoint to process user queries.
    
    Expected JSON:
    {
        "message": "user's question"
    }
    
    Returns:
    {
        "success": bool,
        "answer": "chatbot's response",
        "context": "topic of answer"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'answer': 'Please provide a message.',
                'context': 'error'
            }), 400

        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'answer': 'Please ask a valid question.',
                'context': 'error'
            }), 400

        # Get user ID if logged in
        user_id = session.get('user_id', None)

        # Initialize chatbot engine
        engine = ChatbotEngine(session=db.session)

        # Process the query
        response = engine.process_query(message, user_id=user_id)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'answer': f'An unexpected error occurred: {str(e)}',
            'context': 'error'
        }), 500


@bp.route('/api/suggestions', methods=['GET'])
def api_suggestions():
    """
    Get suggested questions for the chatbot.
    
    Returns:
    {
        "suggestions": [list of suggested questions]
    }
    """
    try:
        user_id = session.get('user_id', None)
        
        suggestions = [
            "Show available opportunities",
            "What job openings are available?",
            "What's my application status?",
        ]

        if user_id:
            suggestions.append("Which positions am I eligible for?")
            suggestions.append("How many opportunities have I applied to?")
        else:
            suggestions.append("Tell me more about the platform")

        return jsonify({
            'success': True,
            'suggestions': suggestions
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'suggestions': [],
            'error': str(e)
        }), 500


@bp.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'chatbot': 'active'
    }), 200
