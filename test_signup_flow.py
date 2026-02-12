#!/usr/bin/env python
"""Test the signup route"""
from app import create_app

app = create_app()
client = app.test_client()

print("Testing signup flow...\n")

# Test 1: GET request to signup page
print("1. Testing GET request to signup page...")
response = client.get('/signup')
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✓ Signup page loads successfully")
else:
    print(f"   ✗ Error loading signup page: {response.status_code}")

# Test 2: POST request with valid data
print("\n2. Testing POST request with valid student signup data...")
data = {
    'username': 'newstudent',
    'email': 'newstudent@example.com',
    'password': 'SecurePass123!',
    'role': 'Student'
}

response = client.post('/signup', data=data, follow_redirects=False)
print(f"   Status: {response.status_code}")
if response.status_code in [200, 302]:
    print(f"   ✓ Request accepted (Status: {response.status_code})")
    if response.status_code == 302:
        print(f"   Redirects to: {response.location}")
else:
    print(f"   ✗ Error: {response.status_code}")
    print(f"   Response: {response.data.decode()[:500]}")

# Test 3: Verify user was created in database
print("\n3. Verifying user was created in database...")
from app.models import User
with app.app_context():
    user = User.query.filter_by(username='newstudent').first()
    if user:
        print(f"   ✓ User created successfully!")
        print(f"     Username: {user.username}")
        print(f"     Email: {user.email}")
        print(f"     Role: {user.role}")
        # Cleanup
        from app import db
        db.session.delete(user)
        db.session.commit()
        print("   ✓ Test user cleaned up")
    else:
        print("   ✗ User not found in database")

print("\n✓ Signup flow test completed!")
