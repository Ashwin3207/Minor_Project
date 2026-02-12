from flask import render_template, redirect, url_for, flash, request, session, send_file
from functools import wraps
from datetime import datetime
import csv
import os
from io import StringIO

from app import db
from app.models import Job, StudentProfile, User, Application, Opportunity
from app.admin import bp


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'Admin':
            flash('You must be an admin to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/dashboard')
@admin_required
def dashboard():
    total_students = User.query.filter_by(role='Student').count()
    total_jobs = Job.query.count()
    total_opportunities = Opportunity.query.count()
    total_applications = Application.query.count()
    total_placed = Application.query.filter_by(status='Selected').count()
    pending_applications = Application.query.filter_by(status='Applied').count()

    stats = {
        'total_students': total_students,
        'total_jobs': total_jobs,
        'total_opportunities': total_opportunities,
        'total_applications': total_applications,
        'total_placed': total_placed,
        'pending_applications': pending_applications,
    }

    return render_template('admin/dashboard.html', stats=stats)


@bp.route('/post_job', methods=['GET', 'POST'])
@admin_required
def post_job():
    if request.method == 'POST':
        try:
            company_name = request.form.get('company_name', '').strip()
            job_description = request.form.get('job_description', '').strip()
            ctc = request.form.get('ctc', '').strip()
            min_cgpa = float(request.form.get('min_cgpa', 0))
            allowed_branches = request.form.get('allowed_branches', '').strip()
            deadline_str = request.form.get('deadline', '')

            if not all([company_name, job_description, ctc, allowed_branches, deadline_str]):
                flash('All fields are required.', 'danger')
                return redirect(url_for('admin.post_job'))

            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')

            new_job = Job(
                company_name=company_name,
                job_description=job_description,
                ctc=ctc,
                min_cgpa=min_cgpa,
                allowed_branches=allowed_branches,
                deadline=deadline
            )

            db.session.add(new_job)
            db.session.commit()

            flash('Job posted successfully!', 'success')
            return redirect(url_for('admin.dashboard'))

        except ValueError as e:
            flash(f'Invalid input format: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error posting job: {str(e)}', 'danger')

    return render_template('admin/post_job.html')


@bp.route('/view_students')
@admin_required
def view_students():
    page = request.args.get('page', 1, type=int)
    branch_filter = request.args.get('branch', '').strip()
    min_cgpa_filter = request.args.get('min_cgpa', type=float)

    query = StudentProfile.query.join(User).filter(User.role == 'Student')

    if branch_filter:
        query = query.filter(StudentProfile.branch.ilike(f'%{branch_filter}%'))

    if min_cgpa_filter is not None:
        query = query.filter(StudentProfile.cgpa >= min_cgpa_filter)

    students = query.order_by(StudentProfile.cgpa.desc())\
                    .paginate(page=page, per_page=15, error_out=False)

    return render_template('admin/view_students.html', students=students)


@bp.route('/view_jobs')
@admin_required
def view_jobs():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '').strip()

    query = Job.query.order_by(Job.created_at.desc())

    jobs = query.paginate(page=page, per_page=10, error_out=False)

    return render_template('admin/view_jobs.html', jobs=jobs, status_filter=status_filter,  now=datetime.utcnow())


@bp.route('/job_applicants/<int:job_id>')
@admin_required
def job_applicants(job_id):
    job = Job.query.get_or_404(job_id)
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '').strip()

    query = Application.query.filter_by(job_id=job_id).join(User)

    if status_filter:
        query = query.filter(Application.status == status_filter)

    applications = query.order_by(Application.applied_at.desc()).paginate(page=page, per_page=15, error_out=False)

    return render_template('admin/job_applicants.html', job=job, applications=applications, status_filter=status_filter)


@bp.route('/opportunities')
@admin_required
def opportunities():
    page = request.args.get('page', 1, type=int)
    query = Opportunity.query.order_by(Opportunity.created_at.desc())
    opps = query.paginate(page=page, per_page=15, error_out=False)

    # Render the admin applications template which now expects `opportunities`
    return render_template('admin/applications.html', opportunities=opps.items)


@bp.route('/opportunity/<int:opp_id>')
@admin_required
def view_opportunity(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)
    return render_template('admin/opportunity_detail.html', opportunity=opp)


@bp.route('/delete_opportunity/<int:opp_id>', methods=['POST', 'GET'])
@admin_required
def delete_opportunity(opp_id):
    try:
        opp = Opportunity.query.get_or_404(opp_id)
        db.session.delete(opp)
        db.session.commit()
        flash('Opportunity deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting opportunity: {str(e)}', 'danger')

    return redirect(url_for('admin.opportunities'))


@bp.route('/create_opportunity/<opp_type>', methods=['GET', 'POST'])
@admin_required
def create_opportunity(opp_type):
    valid_types = ['Job', 'Internship', 'Session', 'Hackathon', 'Bootcamp', 'Seminar']
    if opp_type not in valid_types:
        flash('Invalid opportunity type.', 'danger')
        return redirect(url_for('admin.post_job'))

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
                return redirect(url_for('admin.create_opportunity', opp_type=opp_type))

            try:
                opp_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid date format.', 'danger')
                return redirect(url_for('admin.create_opportunity', opp_type=opp_type))

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
                    return redirect(url_for('admin.create_opportunity', opp_type=opp_type))

                try:
                    new_opp.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('Invalid deadline format.', 'danger')
                    return redirect(url_for('admin.create_opportunity', opp_type=opp_type))

                new_opp.ctc = ctc
                new_opp.allowed_branches = allowed_branches
                new_opp.min_cgpa = float(min_cgpa_str) if min_cgpa_str else 0.0

            db.session.add(new_opp)
            db.session.commit()

            flash(f'{opp_type} posted successfully!', 'success')
            return redirect(url_for('admin.opportunities'))

        except ValueError as e:
            flash(f'Invalid input format: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error posting {opp_type}: {str(e)}', 'danger')

    return render_template('admin/create_opportunity.html', opp_type=opp_type)


@bp.route('/edit_opportunity/<int:opp_id>', methods=['GET', 'POST'])
@admin_required
def edit_opportunity(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)

    if request.method == 'POST':
        try:
            opp.title = request.form.get('title', '').strip()
            opp.organizer = request.form.get('organizer', '').strip()
            opp.description = request.form.get('description', '').strip()
            opp.requirements = request.form.get('requirements', '').strip()
            mode = request.form.get('mode', '').strip()
            date_str = request.form.get('date', '')

            if not all([opp.title, opp.organizer, opp.description, date_str]):
                flash('Title, organizer, description, and date are required.', 'danger')
                return redirect(url_for('admin.edit_opportunity', opp_id=opp_id))

            try:
                opp.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid date format.', 'danger')
                return redirect(url_for('admin.edit_opportunity', opp_id=opp_id))

            opp.mode = mode

            # Handle job/internship specific fields
            if opp.type in ['Job', 'Internship']:
                ctc = request.form.get('ctc', '').strip()
                allowed_branches = request.form.get('allowed_branches', '').strip()
                deadline_str = request.form.get('deadline', '')
                min_cgpa_str = request.form.get('min_cgpa', '')

                if not all([ctc, allowed_branches, deadline_str]):
                    flash('CTC, allowed branches, and deadline are required for jobs/internships.', 'danger')
                    return redirect(url_for('admin.edit_opportunity', opp_id=opp_id))

                try:
                    opp.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('Invalid deadline format.', 'danger')
                    return redirect(url_for('admin.edit_opportunity', opp_id=opp_id))

                opp.ctc = ctc
                opp.allowed_branches = allowed_branches
                opp.min_cgpa = float(min_cgpa_str) if min_cgpa_str else 0.0

            db.session.commit()

            flash(f'{opp.type} updated successfully!', 'success')
            return redirect(url_for('admin.opportunities'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating opportunity: {str(e)}', 'danger')

    return render_template('admin/create_opportunity.html', opp_type=opp.type, opportunity=opp)


@bp.route('/opportunity_applicants/<int:opp_id>')
@admin_required
def opportunity_applicants(opp_id):
    """View all applicants for a specific opportunity"""
    opp = Opportunity.query.get_or_404(opp_id)
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '').strip()

    query = Application.query.filter_by(opportunity_id=opp_id).join(User)

    if status_filter:
        query = query.filter(Application.status == status_filter)

    applications = query.order_by(Application.applied_at.desc()).paginate(page=page, per_page=15, error_out=False)

    return render_template('admin/opportunity_applicants.html', opportunity=opp, applications=applications, status_filter=status_filter)


@bp.route('/confirm_opportunity_application/<int:application_id>', methods=['POST'])
@admin_required
def confirm_opportunity_application(application_id):
    """Update status of an opportunity application"""
    try:
        application = Application.query.get_or_404(application_id)
        new_status = request.form.get('status', '').strip()

        # Validate status
        valid_statuses = ['Applied', 'Shortlisted', 'Selected', 'Rejected']
        if new_status not in valid_statuses:
            flash('Invalid status provided.', 'danger')
            return redirect(url_for('admin.opportunity_applicants', opp_id=application.opportunity_id))

        application.status = new_status
        application.updated_at = datetime.utcnow()
        db.session.commit()

        status_message = f"Application status updated to {new_status}!"
        flash(status_message, 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating application: {str(e)}', 'danger')

    return redirect(url_for('admin.opportunity_applicants', opp_id=application.opportunity_id))


@bp.route('/confirm_application/<int:application_id>', methods=['POST'])
@admin_required
def confirm_application(application_id):
    try:
        application = Application.query.get_or_404(application_id)
        new_status = request.form.get('status', '').strip()

        # Validate status
        valid_statuses = ['Shortlisted', 'Selected', 'Rejected']
        if new_status not in valid_statuses:
            flash('Invalid status provided.', 'danger')
            return redirect(url_for('admin.job_applicants', job_id=application.job_id))

        application.status = new_status
        application.updated_at = datetime.utcnow()
        db.session.commit()

        status_message = f"Application {new_status.lower()} successfully!"
        flash(status_message, 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating application: {str(e)}', 'danger')

    return redirect(url_for('admin.job_applicants', job_id=application.job_id))


@bp.route('/export_students')
@admin_required
def export_students():
    students = StudentProfile.query.join(User).filter(User.role == 'Student').all()

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Username', 'Email', '10th %', '12th %', 'CGPA', 'Branch',
        'Skills', 'Has Backlog', 'Resume Link', 'Last Updated'
    ])

    for profile in students:
        user = profile.user
        writer.writerow([
            user.username,
            user.email,
            profile.tenth_percentage,
            profile.twelfth_percentage,
            profile.cgpa,
            profile.branch,
            profile.skills or '',
            'Yes' if profile.has_backlog else 'No',
            profile.resume_link or '',
            profile.updated_at.strftime('%Y-%m-%d %H:%M') if profile.updated_at else ''
        ])

    output.seek(0)

    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'students_export_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    )


@bp.route('/download-student-resume/<int:student_id>')
@admin_required
def download_student_resume(student_id):
    """Download a student's resume"""
    try:
        profile = StudentProfile.query.filter_by(user_id=student_id).first()
        
        if not profile or not profile.resume_link or not os.path.exists(profile.resume_link):
            flash('Resume not found for this student.', 'danger')
            return redirect(request.referrer or url_for('admin.view_students'))
        
        filename = os.path.basename(profile.resume_link)
        return send_file(profile.resume_link, as_attachment=True, download_name=filename)
    
    except Exception as e:
        flash(f'Error downloading resume: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('admin.view_students'))