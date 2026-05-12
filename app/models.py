from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# Explicitly import db from the app package
# This is safe because models are imported AFTER db.init_app()
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # hashed
    role = db.Column(db.String(20), nullable=False)  # Student, HOD, Principal, Corporate, TPO, Admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student_profile = db.relationship('StudentProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    applications = db.relationship('Application', back_populates='student', lazy='dynamic')
    student_verification = db.relationship('StudentVerification', back_populates='user', uselist=False, cascade='all, delete-orphan')
    corporate_profile = db.relationship('CorporateProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    corporate_access_tokens = db.relationship('CorporateAccessToken', back_populates='created_by', lazy='dynamic')

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
        # Properly parse job requirements as list of skills
        job_reqs = set(skill.strip().lower() for skill in self.get_requirements_list() if skill.strip())
        
        # Properly parse student skills (comma-separated)
        # Clean up: strip whitespace, punctuation, and normalize
        if student_profile.skills:
            skills_text = student_profile.skills.strip().rstrip('.,;')  # Remove trailing punctuation
            student_skills_raw = set(
                skill.strip().lower() 
                for skill in skills_text.split(',') 
                if skill.strip()
            )
        else:
            student_skills_raw = set()
        
        # Smart matching: check if any job requirement contains or is contained in student skill
        matched_skills = set()
        for job_req in job_reqs:
            for student_skill in student_skills_raw:
                # Check for exact match or substring match (case-insensitive)
                if job_req == student_skill or student_skill in job_req or job_req in student_skill:
                    matched_skills.add(job_req)
                    break
        
        missing_skills = job_reqs - matched_skills
        
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


class StudentVerification(db.Model):
    """
    Stores student verification details.
    Students must be verified before their accounts are fully activated.
    """
    __tablename__ = 'student_verifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Enrollment details
    enrollment_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    college_email = db.Column(db.String(120), index=True)  # e.g., student@college.edu
    semester = db.Column(db.Integer)  # 1-8
    department = db.Column(db.String(50))  # CSE, ECE, MECH, etc.
    
    # Verification status
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_code = db.Column(db.String(100))  # OTP or verification token
    verification_sent_at = db.Column(db.DateTime)
    verified_at = db.Column(db.DateTime)
    
    # Approval status (by HOD/Admin)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # HOD/Admin who approved
    approved_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship('User', back_populates='student_verification', foreign_keys=[user_id])

    def __repr__(self):
        return f'<StudentVerification user_id={self.user_id} enrollment={self.enrollment_number} verified={self.is_verified}>'


class CorporateProfile(db.Model):
    """
    Corporate/Recruiter account details.
    Created by TPO when giving temporary access to companies.
    """
    __tablename__ = 'corporate_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Company details
    company_name = db.Column(db.String(150), nullable=False)
    company_website = db.Column(db.String(200))
    company_email = db.Column(db.String(120))
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    # Authorization
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # TPO who created
    authorized_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Admin/Principal who authorized
    
    # Access details
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    access_from = db.Column(db.DateTime, nullable=False)  # Start date of access
    access_until = db.Column(db.DateTime, nullable=False)  # Expiry date of access
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship('User', back_populates='corporate_profile', foreign_keys=[user_id])

    def is_access_valid(self):
        """Check if access is still valid (active and not expired)."""
        now = datetime.utcnow()
        return self.is_active and self.access_from <= now <= self.access_until

    def days_until_expiry(self):
        """Get number of days until access expires."""
        if not self.access_until:
            return None
        days = (self.access_until - datetime.utcnow()).days
        return max(days, 0)

    def __repr__(self):
        return f'<CorporateProfile user_id={self.user_id} company={self.company_name} valid={self.is_access_valid()}>'


class CorporateAccessToken(db.Model):
    """
    Tracks temporary access tokens given to corporates by TPO.
    Allows audit trail and revocation of access.
    """
    __tablename__ = 'corporate_access_tokens'

    id = db.Column(db.Integer, primary_key=True)
    corporate_id = db.Column(db.Integer, db.ForeignKey('corporate_profiles.id'), nullable=False)
    
    # Token details
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    purpose = db.Column(db.String(255))  # e.g., "Job posting", "Candidate access"
    
    # Authorization
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # TPO
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Validity
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime)
    
    # Tracking
    last_used_at = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)

    # Relationship
    created_by = db.relationship('User', back_populates='corporate_access_tokens', foreign_keys=[created_by_id])

    def is_valid(self):
        """Check if token is still valid and not expired."""
        now = datetime.utcnow()
        return self.is_active and self.revoked_at is None and now <= self.expires_at

    def __repr__(self):
        return f'<CorporateAccessToken corporate_id={self.corporate_id} valid={self.is_valid()}>'