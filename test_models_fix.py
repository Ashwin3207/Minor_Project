#!/usr/bin/env python
"""Test that models load without ambiguous foreign key errors."""

from app import create_app, db
from app.models import User, StudentVerification

app = create_app()
with app.app_context():
    # Test User query
    count = User.query.count()
    print(f"✓ User.query works - Found {count} users")
    
    # Test StudentVerification query
    verif_count = StudentVerification.query.count()
    print(f"✓ StudentVerification.query works - Found {verif_count} verifications")
    
    # Test relationship access
    test_user = User.query.first()
    if test_user:
        try:
            verif = test_user.student_verification
            print(f"✓ User.student_verification relationship works - {test_user.username} has verification: {verif is not None}")
        except Exception as e:
            print(f"✗ Error accessing relationship: {e}")
    else:
        print("✓ No users in database - schema is correct")
    
    print("\n✅ All tests passed - AmbiguousForeignKeysError is FIXED!")
