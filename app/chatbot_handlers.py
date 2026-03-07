"""
Example SQLAlchemy handlers for chatbot intent execution.
Demonstrating proper database queries for the placement portal.
"""

from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from app.models import User, StudentProfile, Opportunity, Application, Job
from app import db


# ==================== Example Security Handlers ====================

def get_student_profile(student_id: int) -> dict:
    """
    Get student profile safely.
    Example of secure database access.
    """
    student = User.query.get(student_id)
    if not student or student.role.lower() != 'student':
        return {'error': 'Student not found', 'data': None}
    
    profile = StudentProfile.query.filter_by(user_id=student_id).first()
    if not profile:
        return {'error': 'Profile incomplete', 'data': None}
    
    return {
        'error': None,
        'data': {
            'student_id': student.id,
            'username': student.username,
            'cgpa': profile.cgpa,
            'branch': profile.branch,
            'skills': profile.skills,
            'resume_link': profile.resume_link,
        }
    }


def get_eligible_opportunities(student_id: int, limit: int = 10) -> list:
    """
    Get opportunities student is eligible for.
    Example of filtered query with business logic.
    """
    profile = StudentProfile.query.filter_by(user_id=student_id).first()
    if not profile:
        return []
    
    # Find opportunities matching criteria
    eligible = Opportunity.query.filter(
        and_(
            or_(
                Opportunity.min_cgpa <= profile.cgpa,
                Opportunity.min_cgpa.is_(None)
            ),
            or_(
                Opportunity.allowed_branches.contains(profile.branch),
                Opportunity.allowed_branches.is_(None)
            ),
            Opportunity.deadline > datetime.utcnow()
        )
    ).limit(limit).all()
    
    return [
        {
            'id': opp.id,
            'title': opp.title,
            'company': opp.company_name,
            'ctc': opp.ctc,
            'deadline': opp.deadline.isoformat() if opp.deadline else None,
            'type': opp.type,
        }
        for opp in eligible
    ]


def count_applications_by_status(student_id: int) -> dict:
    """
    Count student's applications grouped by status.
    Example of aggregation query.
    """
    applications = Application.query.filter_by(student_id=student_id).all()
    
    status_counts = {}
    for app in applications:
        status = app.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        'total': len(applications),
        'by_status': status_counts,
        'placement_status': 'Placed' if any(app.status == 'Selected' for app in applications) else 'Not Placed'
    }


def search_companies(company_name: str, limit: int = 10) -> list:
    """
    Search for companies by name.
    Example of text search query.
    """
    companies = db.session.query(Opportunity).filter(
        Opportunity.company_name.ilike(f'%{company_name}%')
    ).limit(limit).all()
    
    results = []
    for opp in companies:
        results.append({
            'company': opp.company_name,
            'opportunity': opp.title,
            'type': opp.type,
            'ctc': opp.ctc,
            'deadline': opp.deadline.isoformat() if opp.deadline else None,
        })
    
    return results


def get_branch_statistics(branch: str = None) -> dict:
    """
    Get statistics for a branch.
    Example of complex aggregation.
    """
    if branch:
        profiles = StudentProfile.query.filter_by(branch=branch).all()
    else:
        profiles = StudentProfile.query.all()
    
    if not profiles:
        return {'message': 'No students found', 'stats': {}}
    
    total_students = len(profiles)
    total_cgpa = sum(p.cgpa for p in profiles)
    avg_cgpa = total_cgpa / total_students if total_students > 0 else 0
    
    # Calculate placements
    placed_count = 0
    total_applications = 0
    
    for profile in profiles:
        applications = Application.query.filter_by(student_id=profile.user_id).all()
        total_applications += len(applications)
        if any(app.status == 'Selected' for app in applications):
            placed_count += 1
    
    return {
        'branch': branch or 'All Branches',
        'stats': {
            'total_students': total_students,
            'avg_cgpa': round(avg_cgpa, 2),
            'placed_students': placed_count,
            'placement_rate': f"{(placed_count/total_students*100):.1f}%" if total_students > 0 else "0%",
            'total_applications': total_applications,
            'avg_applications': round(total_applications / total_students, 2) if total_students > 0 else 0,
        }
    }


def get_upcoming_drives(days_ahead: int = 30, limit: int = 20) -> list:
    """
    Get upcoming recruitment drives.
    Example of date-based filtering.
    """
    now = datetime.utcnow()
    future_date = now + timedelta(days=days_ahead)
    
    drives = Opportunity.query.filter(
        and_(
            Opportunity.deadline > now,
            Opportunity.deadline <= future_date
        )
    ).order_by(Opportunity.deadline).limit(limit).all()
    
    results = []
    for drive in drives:
        days_left = (drive.deadline - now).days
        results.append({
            'company': drive.company_name,
            'title': drive.title,
            'type': drive.type,
            'ctc': drive.ctc,
            'deadline': drive.deadline.isoformat(),
            'days_left': max(0, days_left),
        })
    
    return results


# ==================== Admin-Only Handlers ====================

def get_admin_dashboard_stats() -> dict:
    """
    Get overall placement statistics.
    ADMIN ONLY - Must enforce role check before calling.
    """
    total_students = User.query.filter_by(role='Student').count()
    total_companies = Opportunity.query.distinct(Opportunity.company_name).count()
    total_applications = Application.query.count()
    
    # Count by status
    statuses = {}
    for status in ['Applied', 'Shortlisted', 'Selected', 'Rejected']:
        statuses[status] = Application.query.filter_by(status=status).count()
    
    # Calculate placement rate
    placed_count = db.session.query(
        Application.student_id
    ).filter(
        Application.status == 'Selected'
    ).distinct().count()
    
    placement_rate = (placed_count / total_students * 100) if total_students > 0 else 0
    
    return {
        'total_students': total_students,
        'total_companies': total_companies,
        'total_applications': total_applications,
        'placement_rate': f"{placement_rate:.1f}%",
        'placed_students': placed_count,
        'applications_by_status': statuses,
    }


def get_recent_applications(limit: int = 50) -> list:
    """
    Get recent applications across all students.
    ADMIN ONLY - Must enforce role check before calling.
    """
    applications = Application.query.order_by(
        Application.applied_at.desc()
    ).limit(limit).all()
    
    results = []
    for app in applications:
        student = User.query.get(app.student_id)
        profile = StudentProfile.query.filter_by(user_id=app.student_id).first()
        
        company = None
        if app.opportunity:
            company = app.opportunity.company_name
        elif app.job:
            company = app.job.company_name
        
        results.append({
            'student_name': student.username if student else 'Unknown',
            'company': company,
            'status': app.status,
            'applied_at': app.applied_at.isoformat() if app.applied_at else None,
            'cgpa': profile.cgpa if profile else 'N/A',
        })
    
    return results


# ==================== Query Safety Notes ====================
"""
SECURITY REMINDERS:

1. Never use raw SQL - Always use ORM models
2. Always validate user_id matches session user for students
3. Admin role required for cross-student queries
4. Limit query results to prevent memory issues
5. Use ilike() for case-insensitive searches
6. Always check for None values when accessing relationships
7. Log all data access for audit trails
8. Use datetime.utcnow() for UTC consistency
9. Never expose database structure in error messages
10. Sanitize all user input before queries

Example of WRONG:
    db.engine.execute(f"SELECT * FROM opportunities WHERE company = '{company}'")
    # SQL INJECTION VULNERABILITY!

Example of RIGHT:
    Opportunity.query.filter(
        Opportunity.company_name.ilike(f'%{company}%')
    ).all()
"""
