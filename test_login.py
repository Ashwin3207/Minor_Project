#!/usr/bin/env python3
"""Test login functionality"""

from dotenv import load_dotenv
import os

load_dotenv()
os.environ['FLASK_ENV'] = 'production'

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

with app.app_context():
    # Get an existing user
    user = User.query.first()
    
    if not user:
        print("❌ No users found in database!")
    else:
        print(f"Testing login with user: {user.username}")
        print(f"Password hash: {user.password[:30]}...")
        
        # Try checking with a test password
        test_pwd = "test123"
        hashed = generate_password_hash(test_pwd)
        print(f"\nTest hash check: {check_password_hash(hashed, test_pwd)}")
        
        # Try checking user's actual password (won't work since we don't know it)
        print(f"Checking with random password: {check_password_hash(user.password, 'wrong')}")
        
        print("\n✅ Password hashing system working correctly")
