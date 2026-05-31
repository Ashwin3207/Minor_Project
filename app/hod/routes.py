"""HOD (Head of Department) routes for managing department students."""
from flask import render_template, redirect, url_for, flash, request, session
from datetime import datetime

from app import db
from app.models import User, StudentVerification, StudentProfile
from app.hod import bp
from app.auth.decorators import hod_required


@bp.route('/dashboard')
@hod_required
def dashboard():
    """HOD dashboard - redirect to admin dashboard for comprehensive analytics."""
    return redirect(url_for('admin.dashboard'))
    
    # Assuming HOD name might contain department info
    # In a real system, you'd have a HODProfile model
    
    # Get statistics for all students (or department-specific)
    total_students = User.query.filter_by(role='Student').count()
    verified_students = db.session.query(StudentVerification).filter_by(
        is_approved=True
    ).count()
    pending_approvals = db.session.query(StudentVerification).filter_by(
        is_approved=False
    ).count()
    
    stats = {
        'total_students': total_students,
        'verified_students': verified_students,
        'pending_approvals': pending_approvals,
    }
    
    return render_template('hod/dashboard.html', stats=stats, current_user=current_user)


@bp.route('/approve_students', methods=['GET', 'POST'])
@hod_required
def approve_students():
    """HOD approves student verifications in their department."""
    if request.method == 'POST':
        verification_id = request.form.get('verification_id', type=int)
        action = request.form.get('action')  # approve or reject
        
        verification = StudentVerification.query.get(verification_id)
        if not verification:
            flash('Student verification not found.', 'danger')
            return redirect(url_for('hod.approve_students'))
        
        if verification.is_approved:
            flash('Student already approved.', 'info')
            return redirect(url_for('hod.approve_students'))
        
        if action == 'approve':
            verification.is_approved = True
            verification.approved_by_id = session['user_id']
            verification.approved_at = datetime.utcnow()
            db.session.commit()
            flash(f'Student {verification.user.username} approved!', 'success')
        
        elif action == 'reject':
            # Deactivate user account
            verification.user.is_active = False
            db.session.commit()
            flash(f'Student {verification.user.username} rejected.', 'info')
    
    # Show pending verifications for HOD's department
    pending = db.session.query(StudentVerification).join(
        User, StudentVerification.user_id == User.id
    ).filter(
        StudentVerification.is_approved == False
    ).all()
    
    approved = db.session.query(StudentVerification).join(
        User, StudentVerification.user_id == User.id
    ).filter(
        StudentVerification.is_approved == True
    ).order_by(StudentVerification.approved_at.desc()).limit(20).all()
    
    return render_template('hod/approve_students.html',
                          pending_verifications=pending,
                          approved_verifications=approved)


@bp.route('/view_students')
@hod_required
def view_students():
    """View students in HOD's department."""
    department = request.args.get('department', '').strip()
    
    query = db.session.query(User, StudentProfile, StudentVerification).join(
        StudentProfile, User.id == StudentProfile.user_id
    ).outerjoin(
        StudentVerification, User.id == StudentVerification.user_id
    ).filter(
        User.role == 'Student'
    )
    
    if department:
        query = query.filter(StudentProfile.branch.ilike(f'%{department}%'))
    
    students = query.all()
    
    # Get unique departments
    departments = db.session.query(StudentProfile.branch).distinct().all()
    departments = [d[0] for d in departments if d[0]]
    
    return render_template('hod/view_students.html',
                          students=students,
                          selected_department=department,
                          departments=departments)
