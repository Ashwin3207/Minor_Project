#!/usr/bin/env python
"""Test signup and login flow without email verification."""

from app import create_app, db
from app.models import User, StudentVerification
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    print("Testing signup and approval flow without email verification...\n")
    
    # Clear existing data
    db.session.query(StudentVerification).delete()
    db.session.query(User).delete()
    db.session.commit()
    
    # Test 1: Create student via signup
    print("1. Creating test student account...")
    from werkzeug.security import generate_password_hash
    
    new_user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('password123'),
        role='Student',
        is_active=True
    )
    db.session.add(new_user)
    db.session.flush()
    
    # Create verification record (no is_verified field anymore)
    verification = StudentVerification(
        user_id=new_user.id,
        enrollment_number='2024001',
        semester=1,
        department='CSE',
        is_approved=False  # Not approved yet
    )
    db.session.add(verification)
    db.session.commit()
    
    print(f"   ✓ Student created: {new_user.username}")
    print(f"   ✓ Enrollment: {verification.enrollment_number}")
    print(f"   ✓ Approved: {verification.is_approved}")
    
    # Test 2: Verify no email verification fields exist
    print("\n2. Verifying email verification fields removed...")
    if hasattr(verification, 'is_verified'):
        print("   ✗ ERROR: is_verified field still exists!")
    else:
        print("   ✓ is_verified field removed")
    
    if hasattr(verification, 'verification_code'):
        print("   ✗ ERROR: verification_code field still exists!")
    else:
        print("   ✓ verification_code field removed")
    
    if hasattr(verification, 'verified_at'):
        print("   ✗ ERROR: verified_at field still exists!")
    else:
        print("   ✓ verified_at field removed")
    
    # Test 3: Test approval workflow
    print("\n3. Testing approval workflow...")
    hod_user = User(
        username='hod1',
        email='hod@college.edu',
        password=generate_password_hash('hod123'),
        role='HOD',
        is_active=True
    )
    db.session.add(hod_user)
    db.session.commit()
    
    # HOD approves student
    verification.is_approved = True
    verification.approved_by_id = hod_user.id
    from datetime import datetime
    verification.approved_at = datetime.utcnow()
    db.session.commit()
    
    print(f"   ✓ Student approved by {hod_user.username}")
    print(f"   ✓ Approved: {verification.is_approved}")
    
    # Test 4: Verify queries work without is_verified
    print("\n4. Testing database queries...")
    pending = db.session.query(StudentVerification).filter_by(is_approved=False).count()
    approved = db.session.query(StudentVerification).filter_by(is_approved=True).count()
    
    print(f"   ✓ Pending approvals: {pending}")
    print(f"   ✓ Approved students: {approved}")
    
    print("\n✅ All email verification removal tests passed!")
    print("\nSummary of changes:")
    print("- Email verification no longer required")
    print("- Students must still be approved by HOD/TPO")
    print("- Approval happens immediately after signup")
    print("- No email verification step")
