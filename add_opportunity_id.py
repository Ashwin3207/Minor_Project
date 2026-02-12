#!/usr/bin/env python3
"""Add opportunity_id column to applications table"""

from app import create_app, db

app = create_app('development')

with app.app_context():
    try:
        result = db.session.execute(db.text("PRAGMA table_info(applications)"))
        columns = [row[1] for row in result]
        print("Current columns in applications table:")
        for col in columns:
            print(f"  - {col}")
        
        if 'opportunity_id' not in columns:
            print()
            print("Adding opportunity_id column...")
            db.session.execute(db.text("ALTER TABLE applications ADD COLUMN opportunity_id INTEGER"))
            db.session.commit()
            print("✓ opportunity_id column added")
        else:
            print()
            print("✓ opportunity_id column already exists")
            
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
