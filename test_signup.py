#!/usr/bin/env python
"""Test signup functionality"""
from app import db, create_app
from app.models import User

app = create_app()

with app.app_context():
    print("Testing signup...")
    
    # Try to create a test user
    try:
        test_user = User(
            username='testuser123',
            email='test@example.com',
            password='hashed_password_here',
            role='Student'
        )
        db.session.add(test_user)
        db.session.commit()
        print("✓ User creation successful")
        
        # Try to query the user
        user = User.query.filter_by(username='testuser123').first()
        if user:
            print(f"✓ User found: {user.username} ({user.role})")
        else:
            print("✗ User not found")
            
        # Clean up
        db.session.delete(user)
        db.session.commit()
        print("✓ Test user deleted")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.session.rollback()
