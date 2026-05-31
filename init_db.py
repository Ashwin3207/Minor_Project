#!/usr/bin/env python
"""Reinitialize the database schema."""

from app import create_app, db
import os

app = create_app()

with app.app_context():
    # Drop existing tables
    db.drop_all()
    print("✓ Dropped existing tables")
    
    # Create new tables
    db.create_all()
    print("✓ Created new tables")
    
    print("\n✅ Database schema initialized successfully!")
