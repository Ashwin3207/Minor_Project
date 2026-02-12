#!/usr/bin/env python
"""Test URL generation"""
from app import create_app

app = create_app()
client = app.test_client()

# Get a page to trigger the request context
response = client.get('/auth/signup')

print("URL generation test result:")
print(f"Response status: {response.status_code}")
print("\nLooking for signup URL in the HTML...")

html = response.data.decode()
if 'action="/auth/signup"' in html:
    print("✓ Form action is correct: /auth/signup")
elif 'action="/signup"' in html:
    print("✗ Form action is wrong: /signup")
else:
    print("? Could not find form action")
