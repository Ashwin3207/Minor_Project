from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

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
    
    # New professional development fields
    internship_details = db.Column(db.Text)                    # Internship experience details
    nptel = db.Column(db.Text)                                 # NPTEL courses completed
    final_year_project = db.Column(db.Text)                    # FYP details and description

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


class Opportunity(db.Model):
    __tablename__ = 'opportunities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g. Job, Internship, Session, Hackathon, Bootcamp, Seminar
    organizer = db.Column(db.String(150))
    company_name = db.Column(db.String(150))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)  # JSON string or newline-separated list
    date = db.Column(db.DateTime)
    mode = db.Column(db.String(50))
    # Job/Internship specific fields
    ctc = db.Column(db.String(50))  # e.g. "12 LPA", "500/month"
    min_cgpa = db.Column(db.Float)  # Minimum CGPA required
    allowed_branches = db.Column(db.Text)  # comma-separated
    deadline = db.Column(db.DateTime)  # Application deadline
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_requirements_list(self):
        """Return requirements as a list if stored as JSON or newline-separated text."""
        if not self.requirements:
            return []

        try:
            import json
            data = json.loads(self.requirements)
            if isinstance(data, list):
                return data
        except Exception:
            pass

        # fallback split by newlines
        return [r.strip() for r in self.requirements.splitlines() if r.strip()]

    def get_deadline_status(self):
        """
        Calculate deadline status and return color info.
        Returns: {
            'color': 'success'|'warning'|'danger'|'secondary',
            'text': 'Open'|'Closing Soon'|'Very Soon'|'Closed',
            'days_left': int,
            'is_closed': bool
        }
        """
        if not self.deadline:
            return {
                'color': 'secondary',
                'text': 'No Deadline',
                'days_left': None,
                'is_closed': False
            }
        
        now = datetime.utcnow()
        time_diff = self.deadline - now
        days_left = time_diff.days if time_diff.total_seconds() >= 0 else -1
        
        # Closed: deadline passed
        if days_left < 0:
            return {
                'color': 'dark',
                'text': 'Closed',
                'days_left': 0,
                'is_closed': True
            }
        
        # Very Soon: less than 1 day
        if days_left < 1:
            return {
                'color': 'danger',
                'text': 'Very Soon',
                'days_left': 0,
                'is_closed': False
            }
        
        # Urgent: 1-3 days
        if days_left <= 3:
            return {
                'color': 'warning',
                'text': 'Closing Soon',
                'days_left': days_left,
                'is_closed': False
            }
        
        # Open: more than 3 days
        return {
            'color': 'success',
            'text': 'Open',
            'days_left': days_left,
            'is_closed': False
        }

    def calculate_match_score(self, student_profile):
        """
        Calculate job match percentage for a student profile.
        Returns: {
            'score': 0-100,
            'cgpa_match': bool,
            'branch_match': bool,
            'skills_match': int (matched skill count),
            'has_internship': bool,
            'has_fyp': bool,
            'matched_skills': [list of matched skills],
            'missing_skills': [list of missing skills],
            'recommendation': 'Apply'|'Prepare'|'Not Ready'
        }
        """
        if not student_profile:
            return None
        
        score = 0
        
        # 1. CGPA Match (25 points) - Most important
        cgpa_match = student_profile.cgpa >= (self.min_cgpa or 0)
        if cgpa_match:
            score += 25
        
        # 2. Branch Match (15 points)
        branch_match = False
        if self.allowed_branches:
            allowed = [b.strip().upper() for b in self.allowed_branches.split(',')]
            branch_match = student_profile.branch.upper() in allowed
        else:
            branch_match = True  # No restriction = match
        
        if branch_match:
            score += 15
        
        # 3. Skills Match (40 points) - Check overlap
        job_reqs = set(str(self.get_requirements_list()).lower().split())
        student_skills = set(str(student_profile.skills).lower().split())
        
        matched_skills = job_reqs & student_skills
        missing_skills = job_reqs - student_skills
        
        skills_coverage = len(matched_skills) / max(len(job_reqs), 1) if job_reqs else 0
        score += int(skills_coverage * 40)
        
        # 4. Internship Experience (10 points)
        has_internship = bool(student_profile.internship_details and student_profile.internship_details.strip())
        if has_internship:
            score += 10
        
        # 5. FYP Project (10 points)
        has_fyp = bool(student_profile.final_year_project and student_profile.final_year_project.strip())
        if has_fyp:
            score += 10
        
        # Determine recommendation
        if score >= 75:
            recommendation = 'Apply'
        elif score >= 50:
            recommendation = 'Prepare'
        else:
            recommendation = 'Not Ready'
        
        return {
            'score': min(score, 100),
            'cgpa_match': cgpa_match,
            'branch_match': branch_match,
            'skills_match': len(matched_skills),
            'total_skills_needed': len(job_reqs),
            'has_internship': has_internship,
            'has_fyp': has_fyp,
            'matched_skills': list(matched_skills)[:5],  # Top 5
            'missing_skills': list(missing_skills)[:3],   # Top 3
            'recommendation': recommendation
        }

    def __repr__(self):
        return f'<Opportunity {self.title} ({self.type})>'


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), nullable=True)
    status = db.Column(db.String(30), default='Applied', nullable=False)  # Applied, Shortlisted, Selected, Rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('User', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')
    opportunity = db.relationship('Opportunity', foreign_keys=[opportunity_id])

    # Prevent duplicate applications (allow both job_id and opportunity_id)
    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='unique_student_job_application'),
        db.UniqueConstraint('student_id', 'opportunity_id', name='unique_student_opportunity_application'),
    )

    def __repr__(self):
        if self.job_id:
            return f'<Application student={self.student_id} job={self.job_id} status={self.status}>'
        return f'<Application student={self.student_id} opportunity={self.opportunity_id} status={self.status}>'