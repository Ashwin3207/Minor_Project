from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Explicitly import db from the app package
# This is safe because models are imported AFTER db.init_app()
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # hashed
    role = db.Column(db.String(20), nullable=False)       # 'Admin' or 'Student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = db.relationship('StudentProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    applications = db.relationship('Application', back_populates='student', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    tenth_percentage = db.Column(db.Float, nullable=False)
    twelfth_percentage = db.Column(db.Float, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    branch = db.Column(db.String(50), nullable=False)          # e.g. CSE, ECE, MECH
    skills = db.Column(db.Text)                                # comma separated or JSON
    has_backlog = db.Column(db.Boolean, default=False, nullable=False)
    resume_link = db.Column(db.String(255))                    # URL or path to uploaded file

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to User
    user = db.relationship('User', back_populates='student_profile')

    def __repr__(self):
        return f'<StudentProfile user_id={self.user_id} CGPA={self.cgpa}>'


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    ctc = db.Column(db.String(50), nullable=False)             # e.g. "12 LPA", "8-10 LPA"
    min_cgpa = db.Column(db.Float, nullable=False)
    allowed_branches = db.Column(db.Text, nullable=False)      # comma separated e.g. "CSE,ECE,IT"
    deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    applications = db.relationship('Application', back_populates='job', lazy='dynamic')

    def __repr__(self):
        return f'<Job {self.company_name} - {self.ctc}>'


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(30), default='Applied', nullable=False)  # Applied, Shortlisted, Selected, Rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('User', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')

    # Prevent duplicate applications
    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='unique_student_job_application'),
    )

    def __repr__(self):
        return f'<Application student={self.student_id} job={self.job_id} status={self.status}>'