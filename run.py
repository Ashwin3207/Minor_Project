#!/usr/bin/env python3
"""
Entry point script to run the Training & Placement Cell Portal application.

Usage:
    python run.py                  # runs in development mode (default)
    FLASK_ENV=production python run.py   # runs in production mode

Recommended development usage:
    flask run --debug              # if using Flask CLI
or simply:
    python run.py
"""

from dotenv import load_dotenv
import os

# Load environment variables first
load_dotenv()

from app import create_app
from config import config

# Choose configuration based on environment variable
# Default to development if FLASK_ENV is not set
config_name = 'development'

# You can override via environment variable
if __name__ == '__main__':
    env = os.environ.get('FLASK_ENV', 'development').lower()
    if env in ['production', 'prod']:
        config_name = 'production'
    elif env == 'testing':
        config_name = 'testing'

    print(f"Starting TPC Portal in {config_name.upper()} mode...")

app = create_app(config_name)

if __name__ == '__main__':
    # Development server (with auto-reload)
    app.run(
        host='0.0.0.0',           # accessible from network (useful for testing on phone/laptop)
        port=5000,                # default Flask port
        debug=True,               # enable debug mode & Werkzeug debugger
        use_reloader=True,        # auto-reload on code changes
        threaded=True             # better handling of multiple requests
    )