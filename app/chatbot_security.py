"""
Security module for chatbot - handles role-based access control and validation.
"""

import json
import re
from functools import wraps
from flask import session, jsonify, current_app
from app.models import User


# Allowed intents in the system
ALLOWED_INTENTS = {
    'search_company',
    'check_eligibility',
    'application_status',
    'upcoming_drives',
    'placement_stats',
    'list_applicants',
    'branch_analytics'
}

# Role-based permissions: intent -> required roles
INTENT_PERMISSIONS = {
    'search_company': {'student', 'admin'},
    'check_eligibility': {'student', 'admin'},
    'application_status': {'student', 'admin'},
    'upcoming_drives': {'student', 'admin'},
    'placement_stats': {'admin'},
    'list_applicants': {'admin'},
    'branch_analytics': {'admin'}
}

# Intents that don't require authentication
ANON_ALLOWED_INTENTS = {
    'search_company',      # Anyone can search opportunities
    'upcoming_drives'      # Anyone can see upcoming drives
}


def role_permission_check(required_roles=None):
    """
    Decorator to check if user has required role.
    
    Args:
        required_roles: Set of allowed roles. If None, no auth required.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            
            # If no roles required, allow access
            if required_roles is None:
                return f(*args, **kwargs)
            
            # Otherwise, user must be logged in
            if not user_id:
                return {
                    'success': False,
                    'error': 'Authentication required',
                    'intent': None,
                    'data': {}
                }
            
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found',
                    'intent': None,
                    'data': {}
                }
            
            user_role = user.role.lower()
            if user_role not in required_roles:
                return {
                    'success': False,
                    'error': f'Permission denied. Required role: {required_roles}',
                    'intent': None,
                    'data': {}
                }
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_json_response(response_text: str) -> dict:
    """
    Validate and parse JSON response from Ollama.
    
    Args:
        response_text: Raw response from AI model
        
    Returns:
        Parsed JSON dict or None if invalid
    """
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            return None
        
        json_str = json_match.group(0)
        data = json.loads(json_str)
        
        # Validate structure
        if not isinstance(data, dict):
            return None
        
        # Must have 'intent' field
        if 'intent' not in data:
            return None
        
        intent = data['intent'].lower().strip()
        
        # Intent must be in allowed list
        if intent not in ALLOWED_INTENTS:
            return None
        
        return data
    except (json.JSONDecodeError, AttributeError, ValueError):
        return None


def sanitize_intent_params(intent: str, params: dict, user_id: int = None) -> dict:
    """
    Sanitize and enforce security on intent parameters.
    
    Args:
        intent: The requested intent
        params: Parameters from AI
        user_id: Current user ID (None for anonymous)
        
    Returns:
        Sanitized parameters dict
    """
    user = None
    user_role = None
    
    # If user is authenticated, get their role
    if user_id:
        user = User.query.get(user_id)
        if user:
            user_role = user.role.lower()
    
    sanitized = {}
    
    # Enforce user-specific constraints for authenticated users
    if user_role == 'student':
        # Students can only access their own data
        sanitized['student_id'] = user_id
        sanitized['user_id'] = user_id
    elif user_role == 'admin':
        # Admin can query other student IDs if provided
        if 'student_id' in params and isinstance(params['student_id'], int):
            sanitized['student_id'] = params['student_id']
        if 'branch' in params and isinstance(params['branch'], str):
            sanitized['branch'] = params['branch'][:50]  # Limit length
    
    # Generic parameters (allowed for all users)
    if 'company' in params and isinstance(params['company'], str):
        sanitized['company'] = params['company'][:100]
    
    if 'limit' in params and isinstance(params['limit'], int):
        sanitized['limit'] = min(params['limit'], 100)  # Cap at 100
    else:
        sanitized['limit'] = 10
    
    return sanitized


def check_intent_permission(intent: str, user_id: int = None) -> bool:
    """
    Check if user has permission for this intent.
    
    Args:
        intent: Intent name
        user_id: Current user ID (None for anonymous)
        
    Returns:
        True if allowed, False otherwise
    """
    if intent not in ALLOWED_INTENTS:
        return False
    
    # Check if intent is allowed for anonymous users
    if user_id is None:
        return intent in ANON_ALLOWED_INTENTS
    
    # For authenticated users, check their role
    required_roles = INTENT_PERMISSIONS.get(intent, {'student', 'admin'})
    
    user = User.query.get(user_id)
    if not user:
        return False
    
    user_role = user.role.lower()
    return user_role in required_roles


def log_intent_action(intent: str, user_id: int, success: bool, params: dict = None):
    """
    Log intent execution for audit purposes.
    
    Args:
        intent: Intent executed
        user_id: User who executed it
        success: Whether it was successful
        params: Parameters used (sanitized)
    """
    try:
        # In production, write to audit log/database
        if current_app.config.get('DEBUG'):
            print(f"[AUDIT] Intent={intent} User={user_id} Success={success}")
    except Exception as e:
        print(f"[AUDIT ERROR] {str(e)}")
