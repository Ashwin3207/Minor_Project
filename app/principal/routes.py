"""Principal routes for high-level oversight."""
from flask import render_template, redirect, url_for, flash, request, session
from datetime import datetime

from app import db
from app.models import User, StudentVerification, Application, CorporateProfile
from app.principal import bp
from app.auth.decorators import principal_required


@bp.route('/dashboard')
@principal_required
def dashboard():
    """Principal dashboard with college-wide statistics."""
    total_students = User.query.filter_by(role='Student').count()
    total_corporates = CorporateProfile.query.filter_by(is_active=True).count()
    total_applications = Application.query.count()
    placed_students = Application.query.filter_by(status='Selected').count()
    
    approved_students = db.session.query(StudentVerification).filter_by(
        is_approved=True
    ).count()
    
    # Placement percentage
    placement_percentage = (placed_students / total_students * 100) if total_students > 0 else 0
    
    stats = {
        'total_students': total_students,
        'approved_students': approved_students,
        'total_corporates': total_corporates,
        'total_applications': total_applications,
        'placed_students': placed_students,
        'placement_percentage': round(placement_percentage, 2),
    }
    
    return render_template('principal/dashboard.html', stats=stats)


@bp.route('/authorize_corporates', methods=['GET', 'POST'])
@principal_required
def authorize_corporates():
    """Authorize corporate access requests."""
    if request.method == 'POST':
        corporate_id = request.form.get('corporate_id', type=int)
        action = request.form.get('action')  # authorize or deny
        
        corporate = CorporateProfile.query.get(corporate_id)
        if not corporate:
            flash('Corporate profile not found.', 'danger')
            return redirect(url_for('principal.authorize_corporates'))
        
        if action == 'authorize':
            corporate.authorized_by_id = session['user_id']
            db.session.commit()
            flash(f'{corporate.company_name} authorized!', 'success')
        
        elif action == 'deny':
            corporate.is_active = False
            db.session.commit()
            flash(f'{corporate.company_name} access denied.', 'info')
    
    # Show pending authorizations
    pending = CorporateProfile.query.filter_by(authorized_by_id=None).all()
    authorized = CorporateProfile.query.filter(
        CorporateProfile.authorized_by_id != None
    ).order_by(CorporateProfile.updated_at.desc()).limit(20).all()
    
    return render_template('principal/authorize_corporates.html',
                          pending_corporates=pending,
                          authorized_corporates=authorized)


@bp.route('/view_all_students')
@principal_required
def view_all_students():
    """View all students in the college."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    verified_only = request.args.get('verified_only', 'false') == 'true'
    
    query = db.session.query(User, StudentVerification).outerjoin(
        StudentVerification, User.id == StudentVerification.user_id
    ).filter(User.role == 'Student')
    
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (StudentVerification.enrollment_number.ilike(f'%{search}%'))
        )
    
    students = query.paginate(page=page, per_page=50)
    
    return render_template('principal/view_students.html',
                          students=students,
                          search=search,
                          verified_only=verified_only)


@bp.route('/placement_report')
@principal_required
def placement_report():
    """Generate placement report."""
    # Get placement statistics by department
    placement_stats = db.session.query(
        StudentVerification.department,
        db.func.count(User.id).label('total_students'),
        db.func.count(Application.id).label('total_applications'),
        db.func.count(db.case((Application.status == 'Selected', 1))).label('placed_students')
    ).join(User, StudentVerification.user_id == User.id).outerjoin(
        Application, User.id == Application.student_id
    ).group_by(StudentVerification.department).all()
    
    # Placement by company
    company_stats = db.session.query(
        CorporateProfile.company_name,
        db.func.count(Application.id).label('applications'),
        db.func.count(db.case((Application.status == 'Selected', 1))).label('selected')
    ).join(
        Application
    ).group_by(CorporateProfile.company_name).all()
    
    return render_template('principal/placement_report.html',
                          placement_stats=placement_stats,
                          company_stats=company_stats)
