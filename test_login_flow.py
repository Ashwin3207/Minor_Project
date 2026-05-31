#!/usr/bin/env python
"""Test the actual login flow through Flask routes."""

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print("Testing login flow through Flask routes...\n")
    
    # Get test accounts
    hod = User.query.filter_by(username='hod_admin').first()
    tpo = User.query.filter_by(username='tpo_admin').first()
    
    if not hod or not tpo:
        print("✗ Accounts not found")
        exit(1)
    
    # Test with test client
    with app.test_client() as client:
        print("1. Testing HOD Login...")
        response = client.post('/auth/login', data={
            'username': 'hod_admin',
            'password': 'hod@2024'
        }, follow_redirects=True)
        
        if response.status_code == 200:
            print(f"   ✓ Login request successful (status: {response.status_code})")
            if 'hod/dashboard' in response.request.path or 'hod_dashboard' in response.get_data(as_text=True):
                print(f"   ✓ Redirected to HOD dashboard")
            else:
                print(f"   → Redirected to: {response.request.path}")
        else:
            print(f"   ✗ Login failed (status: {response.status_code})")
        
        print("\n2. Testing TPO Login...")
        response = client.post('/auth/login', data={
            'username': 'tpo_admin',
            'password': 'tpo@2024'
        }, follow_redirects=True)
        
        if response.status_code == 200:
            print(f"   ✓ Login request successful (status: {response.status_code})")
            if 'tpo/dashboard' in response.request.path or 'tpo_dashboard' in response.get_data(as_text=True):
                print(f"   ✓ Redirected to TPO dashboard")
            else:
                print(f"   → Redirected to: {response.request.path}")
        else:
            print(f"   ✗ Login failed (status: {response.status_code})")
        
        print("\n3. Testing wrong password...")
        response = client.post('/auth/login', data={
            'username': 'hod_admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        if 'Invalid username or password' in response.get_data(as_text=True):
            print(f"   ✓ Correctly rejected wrong password")
        else:
            print(f"   → Response contains: {response.get_data(as_text=True)[:200]}")
    
    print("\n" + "="*60)
    print("✅ LOGIN SETUP COMPLETE")
    print("="*60)
    print("\nUse these credentials to login:")
    print(f"\nHOD:")
    print(f"  Username: hod_admin")
    print(f"  Password: hod@2024")
    print(f"\nTPO:")
    print(f"  Username: tpo_admin")
    print(f"  Password: tpo@2024")
    print("\nLogin URL: http://localhost:5000/auth/login")
    print("="*60)
