"""TPO routes for managing corporate access and student verification."""
from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import secrets

from app import db
from app.models import User, StudentVerification, CorporateProfile, CorporateAccessToken
from app.tpo import bp
from app.auth.decorators import tpo_required, role_required, admin_or_tpo_required, hod_or_principal_required


@bp.route('/dashboard')
@tpo_required
def dashboard():
    """TPO dashboard with overview of students and corporate access."""
    total_students = User.query.filter_by(role='Student').count()
    verified_students = db.session.query(StudentVerification).filter_by(is_verified=True).count()
    pending_approvals = db.session.query(StudentVerification).filter_by(
        is_verified=True, is_approved=False
    ).count()
    active_corporates = CorporateProfile.query.filter_by(is_active=True).count()
    
    stats = {
        'total_students': total_students,
        'verified_students': verified_students,
        'pending_approvals': pending_approvals,
        'active_corporates': active_corporates,
    }
    
    # Recent pending verifications
    pending = db.session.query(StudentVerification).filter_by(
        is_verified=True, is_approved=False
    ).order_by(StudentVerification.verified_at.desc()).limit(10).all()
    
    return render_template('tpo/dashboard.html', stats=stats, pending_verifications=pending)


@bp.route('/approve_students', methods=['GET', 'POST'])
@tpo_required
def approve_students():
    """Approve pending student verifications."""
    if request.method == 'POST':
        verification_id = request.form.get('verification_id', type=int)
        action = request.form.get('action')  # approve or reject
        
        verification = StudentVerification.query.get(verification_id)
        if not verification:
            flash('Student verification not found.', 'danger')
            return redirect(url_for('tpo.approve_students'))
        
        if not verification.is_verified:
            flash('Student email not verified yet.', 'warning')
            return redirect(url_for('tpo.approve_students'))
        
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
    
    # Show pending verifications
    pending = db.session.query(StudentVerification).join(User).filter(
        StudentVerification.is_verified == True,
        StudentVerification.is_approved == False
    ).all()
    
    approved = db.session.query(StudentVerification).join(User).filter(
        StudentVerification.is_approved == True
    ).order_by(StudentVerification.approved_at.desc()).limit(20).all()
    
    return render_template('tpo/approve_students.html', 
                          pending_verifications=pending, 
                          approved_verifications=approved)


@bp.route('/create_corporate', methods=['GET', 'POST'])
@tpo_required
def create_corporate():
    """Create temporary corporate account with access."""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            company_name = request.form.get('company_name', '').strip()
            company_website = request.form.get('company_website', '').strip()
            contact_person = request.form.get('contact_person', '').strip()
            phone = request.form.get('phone', '').strip()
            access_days = request.form.get('access_days', type=int)
            
            if not all([username, email, password, company_name, contact_person, access_days]):
                flash('All required fields must be filled.', 'danger')
                return redirect(url_for('tpo.create_corporate'))
            
            if access_days <= 0 or access_days > 365:
                flash('Access duration must be between 1 and 365 days.', 'danger')
                return redirect(url_for('tpo.create_corporate'))
            
            # Check uniqueness
            if User.query.filter_by(username=username).first():
                flash('Username already taken.', 'danger')
                return redirect(url_for('tpo.create_corporate'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'danger')
                return redirect(url_for('tpo.create_corporate'))
            
            # Create corporate user
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                role='Corporate',
                is_active=True
            )
            db.session.add(new_user)
            db.session.flush()
            
            # Create corporate profile
            now = datetime.utcnow()
            access_until = now + timedelta(days=access_days)
            
            corporate_profile = CorporateProfile(
                user_id=new_user.id,
                company_name=company_name,
                company_website=company_website,
                company_email=email,
                contact_person=contact_person,
                phone=phone,
                created_by_id=session['user_id'],
                is_active=True,
                access_from=now,
                access_until=access_until
            )
            db.session.add(corporate_profile)
            db.session.commit()
            
            flash(f'Corporate account created for {company_name}. Access valid for {access_days} days.', 'success')
            return redirect(url_for('tpo.manage_corporates'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating corporate account: {str(e)}', 'danger')
    
    return render_template('tpo/create_corporate.html')


@bp.route('/manage_corporates', methods=['GET', 'POST'])
@tpo_required
def manage_corporates():
    """Manage existing corporate accounts."""
    if request.method == 'POST':
        corporate_id = request.form.get('corporate_id', type=int)
        action = request.form.get('action')  # extend, revoke, or deactivate
        
        corporate = CorporateProfile.query.get(corporate_id)
        if not corporate:
            flash('Corporate account not found.', 'danger')
            return redirect(url_for('tpo.manage_corporates'))
        
        if action == 'extend':
            extend_days = request.form.get('extend_days', type=int)
            if extend_days and extend_days > 0:
                corporate.access_until = corporate.access_until + timedelta(days=extend_days)
                db.session.commit()
                flash(f'Access extended by {extend_days} days until {corporate.access_until.date()}.', 'success')
        
        elif action == 'revoke':
            corporate.is_active = False
            db.session.commit()
            flash(f'Corporate access for {corporate.company_name} revoked.', 'info')
        
        elif action == 'deactivate':
            corporate.user.is_active = False
            db.session.commit()
            flash(f'Corporate user account deactivated.', 'info')
    
    # Get active corporates
    active_corporates = CorporateProfile.query.filter_by(is_active=True).order_by(
        CorporateProfile.access_until.desc()
    ).all()
    
    # Get expired/inactive corporates
    inactive_corporates = CorporateProfile.query.filter_by(is_active=False).order_by(
        CorporateProfile.access_until.desc()
    ).limit(20).all()
    
    return render_template('tpo/manage_corporates.html',
                          active_corporates=active_corporates,
                          inactive_corporates=inactive_corporates)


@bp.route('/generate_access_token/<int:corporate_id>')
@tpo_required
def generate_access_token(corporate_id):
    """Generate a temporary access token for corporate account."""
    try:
        corporate = CorporateProfile.query.get(corporate_id)
        if not corporate:
            flash('Corporate account not found.', 'danger')
            return redirect(url_for('tpo.manage_corporates'))
        
        # Create access token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)  # 7-day token validity
        
        access_token = CorporateAccessToken(
            corporate_id=corporate_id,
            token=token,
            purpose='Job posting and candidate access',
            created_by_id=session['user_id'],
            is_active=True,
            expires_at=expires_at
        )
        db.session.add(access_token)
        db.session.commit()
        
        flash(f'Access token generated. Valid until {expires_at.date()}.', 'success')
        return redirect(url_for('tpo.manage_corporates'))
    
    except Exception as e:
        flash(f'Error generating token: {str(e)}', 'danger')
        return redirect(url_for('tpo.manage_corporates'))


@bp.route('/view_students_by_department')
@tpo_required
def view_students_by_department():
    """View students filtered by department."""
    department = request.args.get('department', '').strip()
    
    query = db.session.query(User, StudentVerification).join(
        StudentVerification, User.id == StudentVerification.user_id
    ).filter(
        User.role == 'Student',
        StudentVerification.is_approved == True
    )
    
    if department:
        query = query.filter(StudentVerification.department.ilike(f'%{department}%'))
    
    students = query.all()
    
    # Get unique departments
    departments = db.session.query(StudentVerification.department).distinct().all()
    departments = [d[0] for d in departments if d[0]]
    
    return render_template('tpo/view_students.html', 
                          students=students, 
                          selected_department=department,
                          departments=departments)
