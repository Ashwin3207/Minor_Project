from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

from app import db
from app.models import User, StudentVerification
from app.auth import bp


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator to require specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if session.get('role') not in roles:
                flash(f'Access denied. Required roles: {", ".join(roles)}', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))

        # Check if account is active
        if not user.is_active:
            flash('Your account has been deactivated. Contact support.', 'danger')
            return redirect(url_for('auth.login'))

        # For students, check if approved
        if user.role == 'Student':
            verification = StudentVerification.query.filter_by(user_id=user.id).first()
            if not verification or not verification.is_approved:
                flash('Your account is pending approval from your HOD/Admin. Please try again later.', 'info')
                return redirect(url_for('auth.login'))

        session.clear()
        session['user_id'] = user.id
        session['role'] = user.role
        session['username'] = user.username
        session.permanent = True

        flash(f'Welcome back, {user.username}!', 'success')

        # Route based on role
        role_routes = {
            'Admin': 'admin.dashboard',
            'TPO': 'tpo.dashboard',  # Will create TPO routes
            'HOD': 'hod.dashboard',  # Will create HOD routes
            'Principal': 'principal.dashboard',  # Will create Principal routes
            'Corporate': 'corporate.dashboard',  # Will create Corporate routes
            'Student': 'student.profile'
        }

        return redirect(url_for(role_routes.get(user.role, 'main.index')))

    return render_template('auth/login.html')


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Student registration with verification."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        enrollment_number = request.form.get('enrollment_number', '').strip()
        semester = request.form.get('semester', type=int)
        department = request.form.get('department', '').strip()

        # Validate inputs
        if not all([username, email, password, enrollment_number, semester, department]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.signup'))

        if password != password_confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.signup'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('auth.signup'))

        # Check email format
        if '@' not in email:
            flash('Invalid email format.', 'danger')
            return redirect(url_for('auth.signup'))

        # Check uniqueness
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('auth.signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.signup'))

        if StudentVerification.query.filter_by(enrollment_number=enrollment_number).first():
            flash('Enrollment number already registered.', 'danger')
            return redirect(url_for('auth.signup'))

        try:
            # Create user with Student role
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                role='Student',
                is_active=True  # Active, but verification required
            )
            db.session.add(new_user)
            db.session.flush()  # Get the user ID

            # Create verification record
            student_verification = StudentVerification(
                user_id=new_user.id,
                enrollment_number=enrollment_number,
                semester=semester,
                department=department,
                is_approved=False
            )
            db.session.add(student_verification)
            db.session.commit()

            flash('Account created! Your account is pending approval from your HOD.', 'success')
            # TODO: Send verification email with link: /verify/<verification_code>
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'danger')

    return render_template('auth/signup.html')





@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))