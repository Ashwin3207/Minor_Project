from flask import render_template, redirect, url_for, flash, request, session
from datetime import datetime
from functools import wraps

from app import db
from app.models import StudentProfile, Job, Application, User
from app.student import bp


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'Student':
            flash('This area is only for students. Please log in.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


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


@bp.route('/resume')
@student_required
def resume():
    user_id = session['user_id']
    user = User.query.get(user_id)
    profile = StudentProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        flash('Please complete your profile to view resume.', 'warning')
        return redirect(url_for('student.profile'))

    return render_template('student/resume.html', user=user, profile=profile, now=datetime.utcnow()  
)