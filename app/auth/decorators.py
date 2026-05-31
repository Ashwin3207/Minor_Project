"""
Role-based access control decorators and utilities.
"""
from functools import wraps
from flask import flash, redirect, url_for, session
from app.models import User, CorporateProfile

ADMIN_PRIVILEGE_ROLES = {'Admin', 'TPO', 'HOD'}


def login_required(f):
    """Require user to be logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Require user to have one of the specified roles.
    Usage: @role_required('Admin', 'TPO')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if session.get('role') not in roles:
                flash(f'Access denied. Required role(s): {", ".join(roles)}', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def student_required(f):
    """Require user to be a Student."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'Student':
            flash('This area is only for students. Please log in.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Require a user with full admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') not in ADMIN_PRIVILEGE_ROLES:
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def tpo_required(f):
    """Require user to be TPO."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'TPO':
            flash('TPO access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def hod_required(f):
    """Require user to be HOD."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'HOD':
            flash('HOD access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def principal_required(f):
    """Require user to be Principal."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'Principal':
            flash('Principal access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def corporate_required(f):
    """Require user to be Corporate with valid access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'Corporate':
            flash('Corporate access required.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check if corporate access is still valid
        corporate_profile = CorporateProfile.query.filter_by(user_id=session['user_id']).first()
        if not corporate_profile or not corporate_profile.is_access_valid():
            flash('Your corporate access has expired or been revoked.', 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_or_tpo_required(f):
    """Require user to be Admin, TPO, or HOD."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') not in ADMIN_PRIVILEGE_ROLES:
            flash('Admin, TPO, or HOD access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def hod_or_principal_required(f):
    """Require user to be HOD or Principal."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') not in ['HOD', 'Principal', 'Admin']:
            flash('HOD/Principal access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get the current logged-in user object."""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])


def get_current_role():
    """Get the current user's role."""
    return session.get('role')


def has_role(role):
    """Check if current user has specific role."""
    return session.get('role') == role


def has_any_role(*roles):
    """Check if current user has any of the specified roles."""
    return session.get('role') in roles
