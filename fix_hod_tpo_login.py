#!/usr/bin/env python
"""Check existing accounts and setup HOD/TPO if needed."""

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

with app.app_context():
    print("Checking existing accounts...\n")
    
    # Check if HOD account exists
    hod = User.query.filter_by(username='hod_admin').first()
    if hod:
        print(f"✓ HOD account exists: {hod.username}")
        print(f"  Email: {hod.email}")
        print(f"  Role: {hod.role}")
        print(f"  Active: {hod.is_active}")
    else:
        print("✗ HOD account does not exist, creating...")
        try:
            hod = User(
                username='hod_admin',
                email='hod@test.edu',
                password=generate_password_hash('hod@2024'),
                role='HOD',
                is_active=True,
                full_name='Head of Department'
            )
            db.session.add(hod)
            db.session.commit()
            print(f"✓ HOD account created: {hod.username}")
        except Exception as e:
            print(f"✗ Error creating HOD: {e}")
            db.session.rollback()
    
    # Check if TPO account exists
    tpo = User.query.filter_by(username='tpo_admin').first()
    if tpo:
        print(f"\n✓ TPO account exists: {tpo.username}")
        print(f"  Email: {tpo.email}")
        print(f"  Role: {tpo.role}")
        print(f"  Active: {tpo.is_active}")
    else:
        print("\n✗ TPO account does not exist, creating...")
        try:
            tpo = User(
                username='tpo_admin',
                email='tpo@test.edu',
                password=generate_password_hash('tpo@2024'),
                role='TPO',
                is_active=True,
                full_name='Training and Placement Officer'
            )
            db.session.add(tpo)
            db.session.commit()
            print(f"✓ TPO account created: {tpo.username}")
        except Exception as e:
            print(f"✗ Error creating TPO: {e}")
            db.session.rollback()
    
    # Verify login works
    print("\n" + "="*60)
    print("TESTING LOGIN")
    print("="*60)
    
    # Test HOD login
    print("\nTesting HOD login...")
    hod_test = User.query.filter_by(username='hod_admin').first()
    if hod_test:
        if check_password_hash(hod_test.password, 'hod@2024'):
            print(f"✓ HOD login test PASSED")
        else:
            print(f"✗ HOD password test FAILED")
    
    # Test TPO login
    print("Testing TPO login...")
    tpo_test = User.query.filter_by(username='tpo_admin').first()
    if tpo_test:
        if check_password_hash(tpo_test.password, 'tpo@2024'):
            print(f"✓ TPO login test PASSED")
        else:
            print(f"✗ TPO password test FAILED")
    
    # Show all users
    print("\n" + "="*60)
    print("ALL USERS IN DATABASE")
    print("="*60)
    users = User.query.all()
    for user in users:
        print(f"Username: {user.username:15} | Role: {user.role:10} | Email: {user.email:25} | Active: {user.is_active}")
    
    print("\n" + "="*60)
    print("LOGIN CREDENTIALS")
    print("="*60)
    hod_final = User.query.filter_by(username='hod_admin').first()
    tpo_final = User.query.filter_by(username='tpo_admin').first()
    
    if hod_final:
        print(f"\nHOD Login:")
        print(f"  Username: {hod_final.username}")
        print(f"  Password: hod@2024")
        print(f"  Email: {hod_final.email}")
    
    if tpo_final:
        print(f"\nTPO Login:")
        print(f"  Username: {tpo_final.username}")
        print(f"  Password: tpo@2024")
        print(f"  Email: {tpo_final.email}")
    
    print("\n" + "="*60)
