#!/usr/bin/env python3
"""Comprehensive login test - without auto-reload"""

from dotenv import load_dotenv
import os
import sys

load_dotenv()
os.environ['FLASK_ENV'] = 'production'

# Prevent Flask from auto-reloading
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

print("=" * 60)
print("COMPREHENSIVE LOGIN TEST")
print("=" * 60)

with app.app_context():
    # 1. Check database
    print("\n1️⃣  DATABASE CHECK")
    user_count = User.query.count()
    print(f"   Total users: {user_count}")
    
    if user_count == 0:
        print("   ❌ No users in database!")
        sys.exit(1)
    
    # 2. Get first user
    print("\n2️⃣  USER RETRIEVAL")
    user = User.query.first()
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Role: {user.role}")
    print(f"   Password hash exists: {bool(user.password)}")
    
    # 3. Test password hashing
    print("\n3️⃣  PASSWORD HASHING TEST")
    test_password = "testpass123"
    test_hash = generate_password_hash(test_password)
    check_result = check_password_hash(test_hash, test_password)
    print(f"   Hashing works: {check_result}")
    
    # 4. Create test user with known password
    print("\n4️⃣  CREATE TEST USER")
    test_user = User.query.filter_by(username='testuser').first()
    if test_user:
        print(f"   Test user already exists")
    else:
        new_user = User(
            username='testuser',
            email='test@test.com',
            password=generate_password_hash('password123'),
            role='Student'
        )
        db.session.add(new_user)
        db.session.commit()
        print(f"   ✅ Test user created with username: testuser, password: password123")
    
    # 5. Test login with test user
    print("\n5️⃣  TEST LOGIN WITH KNOWN PASSWORD")
    test_user = User.query.filter_by(username='testuser').first()
    if test_user:
        pwd_check = check_password_hash(test_user.password, 'password123')
        print(f"   Username found: True")
        print(f"   Password check: {pwd_check}")
        if pwd_check:
            print(f"   ✅ LOGIN SUCCESSFUL!")
        else:
            print(f"   ❌ LOGIN FAILED - Wrong password")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("\nYou can now try logging in with:")
    print("   Username: testuser")
    print("   Password: password123")
    print("=" * 60)
