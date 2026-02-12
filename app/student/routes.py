from flask import render_template, redirect, url_for, flash, request, session, send_file
from datetime import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename

from app import db
from app.models import StudentProfile, Job, Application, User, Opportunity
from app.student import bp


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'Student':
            flash('This area is only for students. Please log in.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed"""
    from flask import current_app
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_resume(file, user_id):
    """Save uploaded resume and return the file path"""
    from flask import current_app
    
    if not file or file.filename == '':
        raise ValueError('No file selected')
    
    if not allowed_file(file.filename):
        raise ValueError('Only PDF, DOC, and DOCX files are allowed')
    
    # Create uploads folder if it doesn't exist
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Create user-specific folder
    user_folder = os.path.join(upload_folder, f'student_{user_id}')
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    # Generate secure filename
    filename = secure_filename(file.filename)
    # Add timestamp to make filename unique
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename
    
    filepath = os.path.join(user_folder, filename)
    file.save(filepath)
    
    return filepath


@bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    user_id = session['user_id']
    profile = StudentProfile.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        try:
            tenth = float(request.form.get('tenth_percentage', 0))
            twelfth = float(request.form.get('twelfth_percentage', 0))
            cgpa = float(request.form.get('cgpa', 0))
            branch = request.form.get('branch', '').strip().upper()
            skills = request.form.get('skills', '').strip()
            has_backlog = 'has_backlog' in request.form
            resume_link = request.form.get('resume_link', '').strip()

            if cgpa < 0 or cgpa > 10:
                flash('CGPA must be between 0 and 10.', 'danger')
                return redirect(url_for('student.profile'))

            if profile:
                # Update existing
                profile.tenth_percentage = tenth
                profile.twelfth_percentage = twelfth
                profile.cgpa = cgpa
                profile.branch = branch
                profile.skills = skills
                profile.has_backlog = has_backlog
                profile.resume_link = resume_link
                profile.updated_at = datetime.utcnow()
            else:
                # Create new
                profile = StudentProfile(
                    user_id=user_id,
                    tenth_percentage=tenth,
                    twelfth_percentage=twelfth,
                    cgpa=cgpa,
                    branch=branch,
                    skills=skills,
                    has_backlog=has_backlog,
                    resume_link=resume_link
                )
                db.session.add(profile)

            db.session.commit()
            flash('Profile saved successfully!', 'success')

        except ValueError as ve:
            flash(f'Invalid number format: {str(ve)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving profile: {str(e)}', 'danger')

        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', profile=profile)





from datetime import datetime

@bp.route('/applications')
@student_required
def applications():
    page = request.args.get('page', 1, type=int)
    user_id = session['user_id']

    apps = Application.query.filter_by(student_id=user_id)\
                            .order_by(Application.applied_at.desc())\
                            .paginate(page=page, per_page=10, error_out=False)

    return render_template(
        'student/application.html',
        applications=apps,
        now=datetime.utcnow()  
    )


@bp.route('/resume', methods=['GET', 'POST'])
@student_required
def resume():
    user_id = session['user_id']
    user = User.query.get(user_id)
    profile = StudentProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        flash('Please complete your profile to upload resume.', 'warning')
        return redirect(url_for('student.profile'))

    if request.method == 'POST':
        try:
            if 'resume' not in request.files:
                flash('No file selected. Please choose a file to upload.', 'danger')
                return redirect(url_for('student.resume'))
            
            file = request.files['resume']
            
            if file.filename == '':
                flash('Please select a file.', 'danger')
                return redirect(url_for('student.resume'))
            
            if not allowed_file(file.filename):
                flash('Only PDF, DOC, and DOCX files are allowed.', 'danger')
                return redirect(url_for('student.resume'))
            
            # Save the resume
            filepath = save_resume(file, user_id)
            
            # Delete old resume if exists
            if profile.resume_link and os.path.exists(profile.resume_link):
                try:
                    os.remove(profile.resume_link)
                except Exception as e:
                    print(f"Could not delete old resume: {e}")
            
            # Update profile with new resume path
            profile.resume_link = filepath
            profile.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('Resume uploaded successfully!', 'success')
            return redirect(url_for('student.resume'))
        
        except ValueError as ve:
            flash(f'Upload error: {str(ve)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading resume: {str(e)}', 'danger')
        
        return redirect(url_for('student.resume'))

    return render_template('student/resume.html', user=user, profile=profile, now=datetime.utcnow())


@bp.route('/download-resume')
@student_required
def download_resume():
    """Download user's own resume"""
    user_id = session['user_id']
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    if not profile or not profile.resume_link or not os.path.exists(profile.resume_link):
        flash('No resume found. Please upload a resume first.', 'danger')
        return redirect(url_for('student.resume'))
    
    try:
        filename = os.path.basename(profile.resume_link)
        directory = os.path.dirname(profile.resume_link)
        return send_file(profile.resume_link, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f'Error downloading resume: {str(e)}', 'danger')
        return redirect(url_for('student.resume'))


@bp.route('/apply', methods=['GET', 'POST'])
@student_required
def apply():
    """Apply for a job"""
    job_id = request.args.get('job_id')
    
    if not job_id:
        flash('Invalid job ID.', 'danger')
        return redirect(url_for('student.applications'))
    
    job = Job.query.get_or_404(job_id)
    user_id = session['user_id']
    
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('student.profile'))
    
    # Check eligibility
    allowed_branches = [b.strip().upper() for b in (job.allowed_branches or '').split(',') if b.strip()]
    
    if profile.cgpa < job.min_cgpa:
        flash(f'You do not meet the minimum CGPA requirement of {job.min_cgpa}.', 'danger')
        return redirect(request.referrer or url_for('student.applications'))
    
    if allowed_branches and profile.branch not in allowed_branches:
        flash(f'Your branch ({profile.branch}) is not eligible for this job.', 'danger')
        return redirect(request.referrer or url_for('student.applications'))
    
    if profile.has_backlog:
        flash('You cannot apply while having a backlog.', 'danger')
        return redirect(request.referrer or url_for('student.applications'))
    
    if datetime.utcnow() >= job.deadline:
        flash('Application deadline has passed.', 'danger')
        return redirect(request.referrer or url_for('student.applications'))
    
    # Check if already applied
    existing = Application.query.filter_by(student_id=user_id, job_id=job_id).first()
    if existing:
        flash('You have already applied to this job.', 'info')
        return redirect(url_for('student.applications'))
    
    # Create application
    application = Application(
        student_id=user_id,
        job_id=job_id,
        status='Applied'
    )
    db.session.add(application)
    db.session.commit()
    
    flash(f'Successfully applied to {job.company_name}!', 'success')
    return redirect(url_for('student.applications'))


@bp.route('/opportunities')
@student_required
def browse_opportunities():
    """Browse all opportunities grouped by type"""
    page = request.args.get('page', 1, type=int)
    user_id = session['user_id']
    
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        flash('Please complete your profile before browsing opportunities.', 'warning')
        return redirect(url_for('student.profile'))

    opportunities = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
    
    # Add eligibility and application status info
    opp_list = []
    for opp in opportunities:
        eligible = True
        already_applied = False
        
        # Check eligibility for Job/Internship types
        if opp.type in ['Job', 'Internship']:
            allowed = [b.strip().upper() for b in (opp.allowed_branches or '').split(',') if b.strip()]
            is_deadline_valid = not opp.deadline or datetime.utcnow() < opp.deadline
            
            if opp.min_cgpa:
                eligible = (profile.cgpa >= opp.min_cgpa and 
                           (not allowed or profile.branch in allowed) and
                           not profile.has_backlog and
                           is_deadline_valid)
            
            # Check if already applied
            already_applied = Application.query.filter_by(
                student_id=user_id,
                opportunity_id=opp.id
            ).first() is not None
        
        opp_list.append({
            'opportunity': opp,
            'eligible': eligible,
            'applied': already_applied
        })
    
    return render_template('student/opportunities.html', 
                          opportunities=opportunities,
                          opp_list=opp_list,
                          profile=profile,
                          now=datetime.utcnow())


@bp.route('/opportunity/<int:opp_id>')
@student_required
def view_opportunity(opp_id):
    """View details of a single opportunity"""
    opp = Opportunity.query.get_or_404(opp_id)
    user_id = session['user_id']
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    # Check eligibility for Job/Internship
    eligible = True
    if opp.type in ['Job', 'Internship']:
        allowed = [b.strip().upper() for b in (opp.allowed_branches or '').split(',') if b.strip()]
        is_deadline_valid = not opp.deadline or datetime.utcnow() < opp.deadline
        
        if opp.min_cgpa:
            eligible = (profile and 
                       profile.cgpa >= opp.min_cgpa and 
                       (not allowed or profile.branch in allowed) and
                       not profile.has_backlog and
                       is_deadline_valid)
    
    # Check if already applied
    already_applied = Application.query.filter_by(
        student_id=user_id,
        opportunity_id=opp_id
    ).first() is not None
    
    return render_template(
        'student/opportunity_detail.html',
        opportunity=opp,
        student_profile=profile,
        eligible=eligible,
        already_applied=already_applied,
        now=datetime.utcnow()
    )


@bp.route('/opportunity/<int:opp_id>/apply', methods=['POST'])
@student_required
def apply_for_opportunity(opp_id):
    """Apply for any opportunity (jobs, internships, etc.)"""
    opp = Opportunity.query.get_or_404(opp_id)
    user_id = session['user_id']
    
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('student.profile'))
    
    # Check eligibility for Job/Internship types
    if opp.type in ['Job', 'Internship']:
        allowed_branches = [b.strip().upper() for b in (opp.allowed_branches or '').split(',') if b.strip()]
        
        if opp.deadline and datetime.utcnow() >= opp.deadline:
            flash('Application deadline has passed.', 'danger')
            return redirect(url_for('student.view_opportunity', opp_id=opp_id))
        
        if opp.min_cgpa and profile.cgpa < opp.min_cgpa:
            flash(f'You do not meet the minimum CGPA requirement of {opp.min_cgpa}.', 'danger')
            return redirect(url_for('student.view_opportunity', opp_id=opp_id))
        
        if allowed_branches and profile.branch not in allowed_branches:
            flash(f'Your branch is not eligible for this opportunity.', 'danger')
            return redirect(url_for('student.view_opportunity', opp_id=opp_id))
        
        if profile.has_backlog:
            flash('You cannot apply while having a backlog.', 'danger')
            return redirect(url_for('student.view_opportunity', opp_id=opp_id))
    
    # Check if already applied
    existing = Application.query.filter_by(student_id=user_id, opportunity_id=opp_id).first()
    if existing:
        flash('You have already applied to this opportunity.', 'info')
        return redirect(url_for('student.view_opportunity', opp_id=opp_id))
    
    # Create application
    application = Application(
        student_id=user_id,
        opportunity_id=opp_id,
        status='Applied'
    )
    db.session.add(application)
    db.session.commit()
    
    flash(f'Successfully applied to {opp.title}!', 'success')
    return redirect(url_for('student.applications'))