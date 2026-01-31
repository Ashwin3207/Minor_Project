#!/usr/bin/env python3
"""Test session configuration"""

from dotenv import load_dotenv
import os

load_dotenv()
os.environ['FLASK_ENV'] = 'production'

from app import create_app

app = create_app()

print(f"SECRET_KEY set: {'SECRET_KEY' in app.config}")
print(f"SECRET_KEY length: {len(app.config.get('SECRET_KEY', ''))}")
print(f"SECRET_KEY value: {app.config.get('SECRET_KEY', '')[:50]}...")
print(f"Session permanent lifetime: {app.config.get('PERMANENT_SESSION_LIFETIME')}")
print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")

# Try simulating login
from flask import session as flask_session

@app.route('/test-login')
def test():
    return "OK"

with app.test_request_context():
    flask_session['user_id'] = 1
    flask_session['role'] = 'Admin'
    print(f"\n✅ Session can be set: {dict(flask_session)}")
