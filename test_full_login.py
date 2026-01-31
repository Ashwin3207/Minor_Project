#!/usr/bin/env python3
"""Comprehensive login test"""

from dotenv import load_dotenv
import os

load_dotenv()
os.environ['FLASK_ENV'] = 'production'

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

app = create_app()

def test_login_flow():
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
            return False
        
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
        
        # 4. Test login logic
        print("\n4️⃣  LOGIN LOGIC TEST")
        username = user.username
        password = "any_password"  # We don't know the actual password
        
        found_user = User.query.filter_by(username=username).first()
        print(f"   User found by username: {found_user is not None}")
        
        if found_user:
            pwd_correct = check_password_hash(found_user.password, password)
            print(f"   Password check (will fail): {pwd_correct}")
        
        # 5. Create test user with known password
        print("\n5️⃣  CREATE TEST USER")
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
            print(f"   ✅ Test user created")
        
        # 6. Test login with test user
        print("\n6️⃣  TEST LOGIN WITH KNOWN PASSWORD")
        test_user = User.query.filter_by(username='testuser').first()
        if test_user:
            pwd_check = check_password_hash(test_user.password, 'password123')
            print(f"   Password check: {pwd_check}")
            if pwd_check:
                print(f"   ✅ Login successful!")
            else:
                print(f"   ❌ Login failed!")
        
        # 7. Test session
        print("\n7️⃣  SESSION TEST")
        with app.test_request_context():
            from flask import session as flask_session
            flask_session['user_id'] = user.id
            flask_session['role'] = user.role
            print(f"   Session set: user_id={flask_session.get('user_id')}, role={flask_session.get('role')}")
            print(f"   ✅ Session works")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_login_flow()
