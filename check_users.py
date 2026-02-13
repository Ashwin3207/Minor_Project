#!/usr/bin/env python3
"""Check existing users"""

from dotenv import load_dotenv
import os

load_dotenv()
os.environ['FLASK_ENV'] = 'production'

from app import create_app
from app.models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"Total users: {len(users)}\n")
    for user in users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print("-" * 40)
    from app import db


