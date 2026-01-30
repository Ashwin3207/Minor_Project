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


@bp.route('/jobs')
@student_required
def jobs():
    """List of available jobs with eligibility check"""
    page = request.args.get('page', 1, type=int)
    user_id = session['user_id']

    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        flash('Please complete your profile before applying to jobs.', 'warning')
        return redirect(url_for('student.profile'))

    jobs_query = Job.query.filter(Job.deadline > datetime.utcnow())\
                          .order_by(Job.created_at.desc())

    pagination = jobs_query.paginate(page=page, per_page=10, error_out=False)

    job_list = []
    for job in pagination.items:
        allowed = [b.strip().upper() for b in job.allowed_branches.split(',') if b.strip()]
        is_eligible = (
            profile.cgpa >= job.min_cgpa and
            profile.branch in allowed and
            not profile.has_backlog and
            datetime.utcnow() < job.deadline
        )
        already_applied = Application.query.filter_by(
            student_id=user_id,
            job_id=job.id
        ).first() is not None

        job_list.append({
            'job': job,
            'eligible': is_eligible,
            'applied': already_applied
        })

    return render_template('student/jobs.html',
                           job_list=job_list,
                           pagination=pagination,
                           profile=profile,
                            now=datetime.utcnow()  
)


@bp.route('/apply/<int:job_id>')
@student_required
def apply(job_id):
    user_id = session['user_id']
    profile = StudentProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        flash('Complete your profile first.', 'warning')
        return redirect(url_for('student.profile'))

    job = Job.query.get_or_404(job_id)

    if datetime.utcnow() >= job.deadline:
        flash('Application deadline has passed.', 'danger')
        return redirect(url_for('student.jobs'))

    allowed_branches = [b.strip().upper() for b in job.allowed_branches.split(',') if b.strip()]

    if (profile.cgpa < job.min_cgpa or
        profile.branch not in allowed_branches or
        profile.has_backlog):
        flash('You do not meet the eligibility criteria for this job.', 'danger')
        return redirect(url_for('student.jobs'))

    existing = Application.query.filter_by(student_id=user_id, job_id=job_id).first()
    if existing:
        flash('You have already applied to this job.', 'info')
        return redirect(url_for('student.jobs'))

    application = Application(
        student_id=user_id,
        job_id=job_id,
        status='Applied'
    )
    db.session.add(application)
    db.session.commit()

    flash('Application submitted successfully!', 'success')
    return redirect(url_for('student.applications'))


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


@bp.route('/opportunities')
@student_required
def browse_opportunities():
    """Browse all opportunities grouped by type"""
    opportunities = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
    return render_template('student/opportunities.html', opportunities=opportunities)


@bp.route('/opportunity/<int:opp_id>')
@student_required
def view_opportunity(opp_id):
    """View details of a single opportunity"""
    opp = Opportunity.query.get_or_404(opp_id)
    user_id = session['user_id']
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    # For now, opportunities don't have direct application tracking
    # (unless they're job/internship types which map to Job table)
    already_applied = False
    
    return render_template(
        'student/opportunity_detail.html',
        opportunity=opp,
        student_profile=profile,
        already_applied=already_applied
    )


@bp.route('/opportunity/<int:opp_id>/apply', methods=['POST'])
@student_required
def apply_for_opportunity(opp_id):
    """Apply for a job/internship opportunity"""
    opp = Opportunity.query.get_or_404(opp_id)
    user_id = session['user_id']
    
    # Only jobs/internships support applications for now
    if opp.type not in ['Job', 'Internship']:
        flash('You can only apply for jobs and internships.', 'warning')
        return redirect(url_for('student.view_opportunity', opp_id=opp_id))
    
    # For now, opportunities don't have direct application support
    # This feature requires additional database schema updates
    flash('Application feature for opportunities is coming soon.', 'info')
    return redirect(url_for('student.view_opportunity', opp_id=opp_id))