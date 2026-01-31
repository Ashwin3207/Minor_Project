#!/usr/bin/env python3
"""Test PostgreSQL connection"""

from dotenv import load_dotenv
import os

load_dotenv()
os.environ['FLASK_ENV'] = 'production'

from app import create_app
from app.models import User

app = create_app()

with app.app_context():
    print("✅ Connected to PostgreSQL!")
    print(f"Users in database: {User.query.count()}")
    print("Database is ready!")
