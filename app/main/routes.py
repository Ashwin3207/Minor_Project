from flask import render_template, redirect, url_for, current_app
from flask import session   # if you need session access directly

from app.main import bp


@bp.route('/')
@bp.route('/home')
@bp.route('/index')
def index():
    """Landing page / home page of the portal"""
    # Optional debug print (remove in production)
    # current_app.logger.debug("Rendering main/index.html")

    # If you want to pass some dynamic data to the template
    context = {
        'page_title': 'Home - TPC Portal',
        'welcome_message': 'Welcome to Training & Placement Cell Portal'
    }

    return render_template('main/index.html', **context)


@bp.route('/about')
def about():
    """Simple about page (optional but useful)"""
    return render_template('main/about.html', page_title='About Us')


@bp.route('/contact')
def contact():
    """Contact or help page (optional)"""
    return render_template('main/contact.html', page_title='Contact')


# ────────────────────────────────────────────────
# Custom error handlers – registered on the blueprint
# These will apply only to routes handled by this blueprint
# If you want app-wide errors → register in __init__.py
# ────────────────────────────────────────────────

@bp.app_errorhandler(404)
def page_not_found(e):
    """Custom 404 handler for main blueprint routes"""
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_server_error(e):
    """Custom 500 handler – basic version"""
    # Optional: log the error in production
    # current_app.logger.error(f"500 error: {str(e)}")
    
    return render_template('errors/500.html'), 500