#!/usr/bin/env python
"""Create HOD and TPO accounts and test login."""

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

with app.app_context():
    print("Setting up HOD and TPO accounts...\n")
    
    # Delete existing accounts to start fresh
    User.query.filter_by(username='hod_admin').delete()
    User.query.filter_by(username='tpo_admin').delete()
    db.session.commit()
    
    # Create HOD account
    hod = User(
        username='hod_admin',
        email='hod@college.edu',
        password=generate_password_hash('hod@2024'),
        role='HOD',
        is_active=True,
        full_name='Head of Department'
    )
    db.session.add(hod)
    db.session.flush()
    
    # Create TPO account
    tpo = User(
        username='tpo_admin',
        email='tpo@college.edu',
        password=generate_password_hash('tpo@2024'),
        role='TPO',
        is_active=True,
        full_name='Training and Placement Officer'
    )
    db.session.add(tpo)
    db.session.commit()
    
    print("✓ Accounts created\n")
    
    # Test HOD login
    print("Testing HOD login...")
    hod_test = User.query.filter_by(username='hod_admin').first()
    if hod_test:
        print(f"  ✓ HOD account found")
        print(f"    Username: {hod_test.username}")
        print(f"    Email: {hod_test.email}")
        print(f"    Role: {hod_test.role}")
        print(f"    Active: {hod_test.is_active}")
        
        # Test password
        if check_password_hash(hod_test.password, 'hod@2024'):
            print(f"    ✓ Password verification works")
        else:
            print(f"    ✗ Password verification failed")
    else:
        print("  ✗ HOD account not found")
    
    # Test TPO login
    print("\nTesting TPO login...")
    tpo_test = User.query.filter_by(username='tpo_admin').first()
    if tpo_test:
        print(f"  ✓ TPO account found")
        print(f"    Username: {tpo_test.username}")
        print(f"    Email: {tpo_test.email}")
        print(f"    Role: {tpo_test.role}")
        print(f"    Active: {tpo_test.is_active}")
        
        # Test password
        if check_password_hash(tpo_test.password, 'tpo@2024'):
            print(f"    ✓ Password verification works")
        else:
            print(f"    ✗ Password verification failed")
    else:
        print("  ✗ TPO account not found")
    
    print("\n" + "="*60)
    print("LOGIN CREDENTIALS")
    print("="*60)
    print("\nHOD Account:")
    print("  Username: hod_admin")
    print("  Password: hod@2024")
    print("  URL: http://localhost:5000/auth/login")
    
    print("\nTPO Account:")
    print("  Username: tpo_admin")
    print("  Password: tpo@2024")
    print("  URL: http://localhost:5000/auth/login")
    print("="*60)
