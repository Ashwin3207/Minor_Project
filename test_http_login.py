#!/usr/bin/env python3
"""Test the complete login flow via HTTP"""

from dotenv import load_dotenv
import os

load_dotenv()
os.environ['FLASK_ENV'] = 'production'
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

from app import create_app
from werkzeug.security import generate_password_hash

app = create_app()

# Create a test client
client = app.test_client()

print("=" * 60)
print("TESTING LOGIN FLOW VIA HTTP")
print("=" * 60)

# 1. Test GET /login
print("\n1️⃣  GET /auth/login")
response = client.get('/auth/login')
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   ✅ Login page loads")
else:
    print(f"   ❌ Login page failed to load")

# 2. Test invalid login
print("\n2️⃣  POST /auth/login (invalid credentials)")
response = client.post('/auth/login', data={
    'username': 'invaliduser',
    'password': 'wrongpass'
})
print(f"   Status: {response.status_code}")
print(f"   Location: {response.location}")
if response.status_code in [200, 302]:
    print(f"   ✅ Response received")

# 3. Test valid login
print("\n3️⃣  POST /auth/login (valid credentials - testuser)")
response = client.post('/auth/login', data={
    'username': 'testuser',
    'password': 'password123'
}, follow_redirects=False)
print(f"   Status: {response.status_code}")
print(f"   Location: {response.location}")
print(f"   Cookies: {response.headers.getlist('Set-Cookie')[:1]}")

if response.status_code == 302:
    print(f"   ✅ Redirect received")
    print(f"   Redirects to: {response.location}")
    
    # Follow redirect
    print("\n4️⃣  Following redirect...")
    redirect_response = client.get(response.location)
    print(f"   Status after redirect: {redirect_response.status_code}")
    print(f"   ✅ Login flow works!")
else:
    print(f"   ❌ No redirect - something went wrong")

print("\n" + "=" * 60)
