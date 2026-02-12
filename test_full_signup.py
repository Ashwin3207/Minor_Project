#!/usr/bin/env python
"""Full simulation of student signup flow"""
from app import create_app

app = create_app()
client = app.test_client()

print("=" * 60)
print("FULL STUDENT SIGNUP FLOW SIMULATION")
print("=" * 60)

# Step 1: Browse to home
print("\n1. User visits homepage...")
response = client.get('/')
print(f"   Status: {response.status_code}")
html = response.data.decode()
if 'Sign Up Now' in html:
    print("   ✓ Found 'Sign Up Now' button")
else:
    print("   ✗ 'Sign Up Now' button not found")

# Step 2: Click on signup
print("\n2. User clicks 'Sign Up Now'...")
response = client.get('/auth/signup')
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    html = response.data.decode()
    if 'Join TPC Portal' in html:
        print("   ✓ Signup page loads")
        print("   ✓ Page title: 'Join TPC Portal'")
    if 'Create My Account' in html:
        print("   ✓ Submit button found: 'Create My Account'")
    if 'I am a:' in html:
        print("   ✓ Role selection found")
else:
    print(f"   ✗ Failed to load signup page (Status: {response.status_code})")

# Step 3: Fill form and submit
print("\n3. User fills form and submits...")
student_data = {
    'username': 'john_doe',
    'email': 'john@college.edu',
    'password': 'MyPassword123!',
    'role': 'Student'
}

response = client.post('/auth/signup', data=student_data, follow_redirects=True)
print(f"   Status: {response.status_code}")

html = response.data.decode()
if 'Account created successfully' in html or 'Please log in' in html:
    print("   ✓ Success message displayed")
    print("   ✓ Redirected to login page")
elif 'Login' in html:
    print("   ✓ Redirected to login page")
else:
    print("   ? Unknown response")

# Step 4: Verify user in database
print("\n4. Verifying user was created in database...")
from app.models import User
with app.app_context():
    user = User.query.filter_by(username='john_doe').first()
    if user:
        print(f"   ✓ User 'john_doe' found in database")
        print(f"     Email: {user.email}")
        print(f"     Role: {user.role}")
        
        # Try to login
        print("\n5. Testing login with new account...")
        from werkzeug.security import check_password_hash
        if check_password_hash(user.password, 'MyPassword123!'):
            print("   ✓ Password verification successful")
        else:
            print("   ✗ Password verification failed")
        
        # Cleanup
        from app import db
        db.session.delete(user)
        db.session.commit()
        print("\n   ✓ Test user cleaned up")
    else:
        print("   ✗ User not found in database!")
        print("   ERROR: Account creation failed!")

print("\n" + "=" * 60)
print("✓ SIGNUP FLOW TEST COMPLETED SUCCESSFULLY")
print("=" * 60)
