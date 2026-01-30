# config.py
"""
Central configuration file for the Training & Placement Cell Portal.
Use environment variables in production for sensitive values.
"""

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this-in-production-2026'

    # Session lifetime (optional - good security practice)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)

    # SQLAlchemy / Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'tpc_portal.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,          # helps detect stale connections
        'pool_recycle': 3600,           # recycle connections every hour
    }

    # Flask-DebugToolbar (optional - only in development)
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # File upload / resume storage (if you add file upload later)
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

    # Other settings
    ITEMS_PER_PAGE = 10                 # default pagination size
    REMEMBER_COOKIE_DURATION = timedelta(days=14)


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    ENV = 'development'

    # Use a simple SQLite file in dev
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'tpc_portal_dev.db')

    # Show detailed error pages
    PROPAGATE_EXCEPTIONS = True


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False            # disable CSRF for easier testing

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory DB for fast tests


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    ENV = 'production'

    # Force HTTPS in production (if behind proxy)
    PREFERRED_URL_SCHEME = 'https'

    # Use a strong secret key from environment
    SECRET_KEY = os.environ.get('SECRET_KEY')  # must be set in production!

    # Use PostgreSQL or MySQL in production (example)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # e.g. postgres://...

    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Logging level (can be adjusted)
    LOG_LEVEL = 'INFO'


# Dictionary to easily select config by environment
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}