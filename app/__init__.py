from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables from .env BEFORE importing config
load_dotenv()

# Set FLASK_ENV based on .env if not already set
if 'FLASK_ENV' not in os.environ:
    os.environ['FLASK_ENV'] = 'development'

from config import config

# Extensions are created globally
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    import os
    
    # If config_name is 'default', check FLASK_ENV environment variable
    if config_name == 'default':
        env = os.environ.get('FLASK_ENV', 'development').lower()
        if env in ['production', 'prod']:
            config_name = 'production'
        elif env == 'testing':
            config_name = 'testing'
        else:
            config_name = 'development'
    
    flask_app = Flask(__name__,
                      # Important: point to root-level templates & static folders
                      template_folder='../templates',
                      static_folder='../static')
    flask_app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    # Import models AFTER initialization
    import app.models

    # Create tables
    with flask_app.app_context():
        db.create_all()

    # Register blueprints
    from app.auth import bp as auth_bp
    flask_app.register_blueprint(auth_bp)

    from app.admin import bp as admin_bp
    flask_app.register_blueprint(admin_bp)

    from app.student import bp as student_bp
    flask_app.register_blueprint(student_bp)

    from app.main import bp as main_bp
    flask_app.register_blueprint(main_bp)

    from app.chatbot import bp as chatbot_bp
    flask_app.register_blueprint(chatbot_bp)
    
    # Register new role-based blueprints
    from app.tpo import bp as tpo_bp
    flask_app.register_blueprint(tpo_bp)
    
    from app.hod import bp as hod_bp
    flask_app.register_blueprint(hod_bp)
    
    from app.principal import bp as principal_bp
    flask_app.register_blueprint(principal_bp)
    
    from app.corporate import bp as corporate_bp
    flask_app.register_blueprint(corporate_bp)
    
    # Initialize chatbot provider status
    with flask_app.app_context():
        try:
            import logging
            logger = logging.getLogger(__name__)
            logger.info('Chatbot using pure keyword-based intelligent routing system')
            logger.info('No external AI services required - 25+ specialized handlers for database queries')
            logger.info('Chatbot ready - Keyword-based, database-aware, instant responses')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f'Could not initialize chatbot provider status: {e}')
    # Context processor: inject current_user
    @flask_app.context_processor
    def inject_user():
        from flask import session
        from app.models import User

        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        return dict(current_user=user)

    # NEW: Inject current year for copyright footer
    @flask_app.context_processor
    def inject_current_year():
        from datetime import datetime
        return dict(current_year=datetime.now().strftime('%Y'))

    # Error handlers
    @flask_app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @flask_app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return flask_app
