#!/usr/bin/env python
"""Test the Flask app can start without errors."""

from app import create_app
import sys

try:
    app = create_app()
    
    # Test that the app is configured correctly
    with app.app_context():
        print("✓ Flask app created successfully")
        print(f"✓ App name: {app.name}")
        print(f"✓ Debug mode: {app.debug}")
        print(f"✓ Testing mode: {app.testing}")
        
        # Test a basic request
        with app.test_client() as client:
            response = client.get('/auth/signup')
            if response.status_code == 200:
                print("✓ GET /auth/signup route works (returns 200)")
            else:
                print(f"✗ GET /auth/signup route returned {response.status_code}")
                sys.exit(1)
    
    print("\n✅ Flask app is fully functional - NO ERRORS!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
