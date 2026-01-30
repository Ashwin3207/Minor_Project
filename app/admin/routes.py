from flask import render_template, redirect, url_for, flash, request, session, send_file
from functools import wraps
from datetime import datetime
import csv
from io import StringIO

from app import db
from app.models import Job, StudentProfile, User, Application
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
    total_applications = Application.query.count()
    total_placed = Application.query.filter_by(status='Selected').count()
    pending_applications = Application.query.filter_by(status='Applied').count()

    stats = {
        'total_students': total_students,
        'total_jobs': total_jobs,
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