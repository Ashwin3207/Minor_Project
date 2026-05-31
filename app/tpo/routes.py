"""TPO routes for managing corporate access and student verification."""
from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import secrets

from app import db
from app.models import User, StudentVerification, CorporateProfile, CorporateAccessToken, Opportunity, Application
from app.tpo import bp
from app.auth.decorators import tpo_required, role_required, admin_or_tpo_required, hod_or_principal_required


@bp.route('/dashboard')
@tpo_required
def dashboard():
    """TPO dashboard - redirect to admin dashboard for comprehensive analytics."""
    return redirect(url_for('admin.dashboard'))


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
        
        if verification.is_approved:
            flash('Student already approved.', 'info')
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


@bp.route('/post_opportunity')
@tpo_required
def new_opportunity():
    """Select opportunity type before creating"""
    types = ['Job', 'Internship', 'Session', 'Hackathon', 'Bootcamp', 'Seminar']
    return render_template('tpo/select_opportunity_type.html', types=types)


@bp.route('/create_opportunity/<opp_type>', methods=['GET', 'POST'])
@tpo_required
def create_opportunity(opp_type):
    """Create a new opportunity (job, internship, seminar, etc.)"""
    valid_types = ['Job', 'Internship', 'Session', 'Hackathon', 'Bootcamp', 'Seminar']
    if opp_type not in valid_types:
        flash('Invalid opportunity type.', 'danger')
        return redirect(url_for('tpo.new_opportunity'))

    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            organizer = request.form.get('organizer', '').strip()
            description = request.form.get('description', '').strip()
            requirements = request.form.get('requirements', '').strip()
            date_str = request.form.get('date', '')
            mode = request.form.get('mode', '').strip()

            if not all([title, organizer, description, date_str]):
                flash('Title, organizer, description, and date are required.', 'danger')
                return redirect(url_for('tpo.create_opportunity', opp_type=opp_type))

            try:
                opp_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid date format.', 'danger')
                return redirect(url_for('tpo.create_opportunity', opp_type=opp_type))

            new_opp = Opportunity(
                title=title,
                type=opp_type,
                organizer=organizer,
                description=description,
                requirements=requirements,
                date=opp_date,
                mode=mode
            )

            # Handle job/internship specific fields
            if opp_type in ['Job', 'Internship']:
                ctc = request.form.get('ctc', '').strip()
                allowed_branches = request.form.get('allowed_branches', '').strip()
                deadline_str = request.form.get('deadline', '')
                min_cgpa_str = request.form.get('min_cgpa', '')

                if not all([ctc, allowed_branches, deadline_str]):
                    flash('CTC, allowed branches, and deadline are required for jobs/internships.', 'danger')
                    return redirect(url_for('tpo.create_opportunity', opp_type=opp_type))

                try:
                    new_opp.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('Invalid deadline format.', 'danger')
                    return redirect(url_for('tpo.create_opportunity', opp_type=opp_type))

                new_opp.ctc = ctc
                new_opp.allowed_branches = allowed_branches
                new_opp.min_cgpa = float(min_cgpa_str) if min_cgpa_str else 0.0

            db.session.add(new_opp)
            db.session.commit()

            flash(f'{opp_type} posted successfully!', 'success')
            return redirect(url_for('tpo.opportunities'))

        except ValueError as e:
            flash(f'Invalid input format: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error posting {opp_type}: {str(e)}', 'danger')

    return render_template('tpo/create_opportunity.html', opp_type=opp_type)


@bp.route('/opportunities')
@tpo_required
def opportunities():
    """View all posted opportunities"""
    page = request.args.get('page', 1, type=int)
    query = Opportunity.query.order_by(Opportunity.created_at.desc())
    opps = query.paginate(page=page, per_page=15, error_out=False)
    
    # Create a dictionary mapping opportunity IDs to their deadline status
    deadline_statuses = {}
    for opp in opps.items:
        deadline_statuses[opp.id] = opp.get_deadline_status() if hasattr(opp, 'get_deadline_status') else 'Open'

    return render_template('tpo/opportunities.html', 
                          opportunities=opps.items,
                          deadline_statuses=deadline_statuses,
                          page=page)


@bp.route('/opportunity/<int:opp_id>')
@tpo_required
def view_opportunity(opp_id):
    """View details of a specific opportunity"""
    opp = Opportunity.query.get_or_404(opp_id)
    return render_template('tpo/opportunity_detail.html', opportunity=opp)


@bp.route('/opportunity_applicants/<int:opp_id>')
@tpo_required
def opportunity_applicants(opp_id):
    """View all applicants for a specific opportunity"""
    opp = Opportunity.query.get_or_404(opp_id)
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '').strip()

    query = Application.query.filter_by(opportunity_id=opp_id).join(User)

    if status_filter:
        query = query.filter(Application.status == status_filter)

    applications = query.order_by(Application.applied_at.desc()).paginate(page=page, per_page=15, error_out=False)

    return render_template('tpo/opportunity_applicants.html', 
                          opportunity=opp, 
                          applications=applications, 
                          status_filter=status_filter)


@bp.route('/confirm_opportunity_application/<int:application_id>', methods=['POST'])
@tpo_required
def confirm_opportunity_application(application_id):
    """Update status of an opportunity application"""
    try:
        application = Application.query.get_or_404(application_id)
        new_status = request.form.get('status', '').strip()

        # Validate status
        valid_statuses = ['Applied', 'Shortlisted', 'Selected', 'Rejected']
        if new_status not in valid_statuses:
            flash('Invalid status provided.', 'danger')
            return redirect(url_for('tpo.opportunity_applicants', opp_id=application.opportunity_id))

        application.status = new_status
        application.updated_at = datetime.utcnow()
        db.session.commit()

        status_message = f"Application status updated to {new_status}!"
        flash(status_message, 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating application: {str(e)}', 'danger')

    return redirect(url_for('tpo.opportunity_applicants', opp_id=application.opportunity_id))


@bp.route('/view_all_students')
@tpo_required
def view_all_students():
    """View all approved students"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    branch = request.args.get('branch', '').strip()
    
    query = db.session.query(User, StudentVerification).join(
        StudentVerification, User.id == StudentVerification.user_id
    ).filter(
        User.role == 'Student',
        StudentVerification.is_approved == True
    )
    
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (StudentVerification.enrollment_number.ilike(f'%{search}%'))
        )
    
    if branch:
        query = query.filter(StudentVerification.department.ilike(f'%{branch}%'))
    
    students = query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('tpo/view_all_students.html', 
                          students=students,
                          search=search,
                          branch=branch)
