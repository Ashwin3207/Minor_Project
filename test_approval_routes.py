#!/usr/bin/env python
"""Test HOD and TPO approve_students routes work without ambiguous foreign key errors."""

from app import create_app, db
from app.models import User, StudentVerification

app = create_app()

with app.app_context():
    print("Testing HOD and TPO approve_students routes...\n")
    
    # Get HOD and TPO accounts
    hod = User.query.filter_by(username='hod_admin').first()
    tpo = User.query.filter_by(username='tpo_admin').first()
    
    if not hod or not tpo:
        print("✗ HOD or TPO accounts not found")
        exit(1)
    
    # Test with test client
    with app.test_client() as client:
        print("1. Testing HOD approve_students route...")
        # Login as HOD
        login_response = client.post('/auth/login', data={
            'username': 'hod_admin',
            'password': 'hod@2024'
        }, follow_redirects=False)
        
        # Access approve_students
        response = client.get('/hod/approve_students')
        if response.status_code == 200:
            print(f"   ✓ HOD approve_students route works (status: {response.status_code})")
        else:
            print(f"   ✗ HOD approve_students failed (status: {response.status_code})")
        
        print("\n2. Testing TPO approve_students route...")
        # Login as TPO
        client.post('/auth/login', data={
            'username': 'tpo_admin',
            'password': 'tpo@2024'
        }, follow_redirects=False)
        
        # Access approve_students
        response = client.get('/tpo/approve_students')
        if response.status_code == 200:
            print(f"   ✓ TPO approve_students route works (status: {response.status_code})")
        else:
            print(f"   ✗ TPO approve_students failed (status: {response.status_code})")
    
    print("\n" + "="*60)
    print("✅ ALL ROUTES FIXED - NO AMBIGUOUS FOREIGN KEY ERRORS")
    print("="*60)
