#!/usr/bin/env python
"""Test that the database queries work without ambiguous foreign key errors."""

from app import create_app, db
from app.models import User, StudentVerification

app = create_app()

with app.app_context():
    print("Testing database queries for approve_students...\n")
    
    try:
        print("1. Testing HOD pending verifications query...")
        pending = db.session.query(StudentVerification).join(
            User, StudentVerification.user_id == User.id
        ).filter(
            StudentVerification.is_approved == False
        ).all()
        print(f"   ✓ Query succeeded - Found {len(pending)} pending approvals")
        
        print("\n2. Testing HOD approved verifications query...")
        approved = db.session.query(StudentVerification).join(
            User, StudentVerification.user_id == User.id
        ).filter(
            StudentVerification.is_approved == True
        ).order_by(StudentVerification.approved_at.desc()).limit(20).all()
        print(f"   ✓ Query succeeded - Found {len(approved)} approved students")
        
        print("\n3. Testing TPO queries...")
        pending = db.session.query(StudentVerification).join(
            User, StudentVerification.user_id == User.id
        ).filter(
            StudentVerification.is_approved == False
        ).all()
        print(f"   ✓ Query succeeded - Found {len(pending)} pending approvals")
        
        approved = db.session.query(StudentVerification).join(
            User, StudentVerification.user_id == User.id
        ).filter(
            StudentVerification.is_approved == True
        ).order_by(StudentVerification.approved_at.desc()).limit(20).all()
        print(f"   ✓ Query succeeded - Found {len(approved)} approved students")
        
        print("\n" + "="*60)
        print("✅ ALL QUERIES FIXED - NO AMBIGUOUS FOREIGN KEY ERRORS")
        print("="*60)
        print("\nFix Applied:")
        print("  Changed: .join(User)")
        print("  To:      .join(User, StudentVerification.user_id == User.id)")
        print("\nThis explicitly specifies which foreign key to use (user_id)")
        print("and prevents ambiguity with the approved_by_id foreign key.")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
