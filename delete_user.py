#!/usr/bin/env python3
"""
Delete all users and related student profiles safely
"""

from dotenv import load_dotenv
import os
from sqlalchemy import text

# Load environment variables
load_dotenv()
os.environ['FLASK_ENV'] = 'production'

# Import app factory and db
from app import create_app, db

app = create_app()

with app.app_context():
    try:
        # Truncate both tables and reset identity
        db.session.execute(
            text("TRUNCATE TABLE student_profiles, users RESTART IDENTITY CASCADE;")
        )
        db.session.commit()

        print("✅ All users and related student profiles deleted successfully.")
        print("🔄 ID counters reset.")

    except Exception as e:
        db.session.rollback()
        print("❌ Error occurred while deleting users:")
        print(e)
