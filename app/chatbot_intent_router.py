"""
Secure intent router for chatbot - handles routing and executing intents.
Implements role-based access control and input validation.
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from app.models import User, StudentProfile, Opportunity, Application, Job
from app.chatbot_security import (
    ALLOWED_INTENTS,
    INTENT_PERMISSIONS,
    check_intent_permission,
    sanitize_intent_params,
    log_intent_action
)

logger = logging.getLogger(__name__)


class SecureIntentRouter:
    """Routes and executes validated intents with role-based security."""
    
    def __init__(self, db):
        """Initialize router with database session."""
        self.db = db
        self.handlers = {
            'search_company': self._handle_search_company,
            'check_eligibility': self._handle_check_eligibility,
            'application_status': self._handle_application_status,
            'upcoming_drives': self._handle_upcoming_drives,
            'placement_stats': self._handle_placement_stats,
            'list_applicants': self._handle_list_applicants,
            'branch_analytics': self._handle_branch_analytics,
        }
    
    def route_intent(self, intent: str, parameters: dict, user_id: int = None) -> Dict:
        """
        Route and execute an intent with security checks.
        
        Args:
            intent: The intent name
            parameters: Parameters from intent extraction
            user_id: Current user's ID (None for anonymous)
            
        Returns:
            Dictionary with success status and data
        """
        # Validate intent
        if intent not in ALLOWED_INTENTS:
            return {
                'success': False,
                'error': f'Unknown intent: {intent}',
                'data': {}
            }
        
        # Check permissions
        if not check_intent_permission(intent, user_id):
            log_intent_action(intent, user_id, False, {'reason': 'permission_denied'})
            return {
                'success': False,
                'error': 'Permission denied for this intent',
                'data': {}
            }
        
        # Get handler
        handler = self.handlers.get(intent)
        if not handler:
            return {
                'success': False,
                'error': f'No handler for intent: {intent}',
                'data': {}
            }
        
        try:
            # Sanitize parameters based on user role and intent
            sanitized_params = sanitize_intent_params(intent, parameters, user_id)
            
            # Execute handler
            result = handler(sanitized_params, user_id)
            
            # Log successful intent
            log_intent_action(intent, user_id, True, sanitized_params)
            
            return {
                'success': True,
                'intent': intent,
                'data': result,
                'error': None
            }
        except Exception as e:
            logger.error(f"Intent execution error ({intent}): {str(e)}", exc_info=True)
            log_intent_action(intent, user_id, False, {'error': str(e)})
            
            return {
                'success': False,
                'intent': intent,
                'error': 'Failed to execute intent',
                'data': {}
            }
    
    # Intent Handlers
    
    def _handle_search_company(self, params: dict, user_id: int) -> Dict:
        """Search for opportunities/jobs by company name."""
        company = params.get('company', '').strip()
        limit = params.get('limit', 10)
        
        if not company:
            return {'message': 'Please specify a company name.', 'results': []}
        
        # Search opportunities
        opps = Opportunity.query.filter(
            Opportunity.company_name.ilike(f'%{company}%')
        ).limit(limit).all()
        
        results = []
        for opp in opps:
            results.append({
                'id': opp.id,
                'title': opp.title,
                'company': opp.company_name,
                'type': opp.type,
                'ctc': opp.ctc,
                'deadline': opp.deadline.isoformat() if opp.deadline else None,
                'mode': opp.mode,
            })
        
        return {
            'message': f'Found {len(results)} opportunities from {company}',
            'results': results,
            'count': len(results)
        }
    
    def _handle_check_eligibility(self, params: dict, user_id: int) -> Dict:
        """Check student's eligibility for opportunities."""
        student_id = params.get('student_id', user_id)
        
        student = User.query.get(student_id)
        if not student or student.role.lower() != 'student':
            return {'message': 'Student not found', 'eligible': []}
        
        profile = StudentProfile.query.filter_by(user_id=student_id).first()
        if not profile:
            return {'message': 'Student profile incomplete', 'eligible': []}
        
        # Find eligible opportunities
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
        ).limit(params.get('limit', 10)).all()
        
        results = []
        for opp in eligible:
            results.append({
                'id': opp.id,
                'title': opp.title,
                'company': opp.company_name,
                'type': opp.type,
                'min_cgpa': opp.min_cgpa,
                'deadline': opp.deadline.isoformat() if opp.deadline else None,
                'your_cgpa': round(profile.cgpa, 2),
            })
        
        return {
            'message': f'{student.username} is eligible for {len(results)} opportunities',
            'eligible': results,
            'count': len(results)
        }
    
    def _handle_application_status(self, params: dict, user_id: int) -> Dict:
        """Get application status for a student."""
        student_id = params.get('student_id', user_id)
        
        # Students can only check their own status
        user = User.query.get(user_id)
        if user.role.lower() == 'student' and student_id != user_id:
            return {'message': 'Cannot view other student applications', 'applications': []}
        
        applications = Application.query.filter_by(student_id=student_id).all()
        
        results = []
        for app in applications:
            opp = None
            company = None
            title = None
            ctc = None
            
            if app.opportunity_id:
                opp = Opportunity.query.get(app.opportunity_id)
                company = opp.company_name if opp else 'Unknown'
                title = opp.title if opp else 'Unknown'
                ctc = opp.ctc if opp else None
            elif app.job_id:
                job = Job.query.get(app.job_id)
                company = job.company_name if job else 'Unknown'
                title = 'Job Opening'
                ctc = job.ctc if job else None
            
            results.append({
                'id': app.id,
                'company': company,
                'title': title,
                'ctc': ctc,
                'status': app.status,
                'applied_at': app.applied_at.isoformat() if app.applied_at else None,
            })
        
        return {
            'message': f'Found {len(results)} applications',
            'applications': results,
            'count': len(results)
        }
    
    def _handle_upcoming_drives(self, params: dict, user_id: int) -> Dict:
        """Get upcoming recruitment drives."""
        days_ahead = 30  # Show next 30 days
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        drives = Opportunity.query.filter(
            and_(
                Opportunity.deadline > datetime.utcnow(),
                Opportunity.deadline <= cutoff_date,
                Opportunity.type.in_(['Job', 'Internship'])
            )
        ).order_by(Opportunity.deadline).limit(params.get('limit', 20)).all()
        
        results = []
        for drive in drives:
            days_left = (drive.deadline - datetime.utcnow()).days
            results.append({
                'id': drive.id,
                'title': drive.title,
                'company': drive.company_name,
                'type': drive.type,
                'deadline': drive.deadline.isoformat() if drive.deadline else None,
                'days_left': max(0, days_left),
                'ctc': drive.ctc,
            })
        
        return {
            'message': f'{len(results)} drives coming up in next {days_ahead} days',
            'drives': results,
            'count': len(results)
        }
    
    def _handle_placement_stats(self, params: dict, user_id: int) -> Dict:
        """Get placement statistics (admin only)."""
        user = User.query.get(user_id)
        if not user or user.role.lower() != 'admin':
            return {'message': 'Admin access required', 'stats': {}}
        
        total_students = User.query.filter_by(role='Student').count()
        total_applications = Application.query.count()
        
        # Count by status
        statuses = {}
        for status in ['Applied', 'Shortlisted', 'Selected', 'Rejected']:
            count = Application.query.filter_by(status=status).count()
            statuses[status] = count
        
        # Placed students (have at least one 'Selected' application)
        placed_query = self.db.session.query(
            Application.student_id
        ).filter(
            Application.status == 'Selected'
        ).distinct()
        
        placed_count = placed_query.count()
        
        return {
            'message': 'Placement Statistics',
            'stats': {
                'total_students': total_students,
                'placed_students': placed_count,
                'placement_rate': f"{(placed_count/total_students*100):.1f}%" if total_students > 0 else "0%",
                'total_applications': total_applications,
                'avg_applications_per_student': round(total_applications / total_students, 2) if total_students > 0 else 0,
                'by_status': statuses,
            }
        }
    
    def _handle_list_applicants(self, params: dict, user_id: int) -> Dict:
        """List applicants for an opportunity (admin only)."""
        user = User.query.get(user_id)
        if not user or user.role.lower() != 'admin':
            return {'message': 'Admin access required', 'applicants': []}
        
        # Can filter by company or limit
        limit = params.get('limit', 50)
        
        applications = Application.query.join(
            User, Application.student_id == User.id
        ).order_by(Application.applied_at.desc()).limit(limit).all()
        
        results = []
        for app in applications:
            student = User.query.get(app.student_id)
            profile = StudentProfile.query.filter_by(user_id=app.student_id).first()
            
            results.append({
                'student_id': student.id,
                'name': student.username,
                'email': student.email,
                'cgpa': profile.cgpa if profile else 'N/A',
                'status': app.status,
                'applied_at': app.applied_at.isoformat() if app.applied_at else None,
            })
        
        return {
            'message': f'Retrieved {len(results)} applicants',
            'applicants': results,
            'count': len(results)
        }
    
    def _handle_branch_analytics(self, params: dict, user_id: int) -> Dict:
        """Get analytics by branch (admin only)."""
        user = User.query.get(user_id)
        if not user or user.role.lower() != 'admin':
            return {'message': 'Admin access required', 'analytics': {}}
        
        branch = params.get('branch', '').strip()
        
        # Get all students from branch
        if branch:
            profiles = StudentProfile.query.filter_by(branch=branch).all()
        else:
            profiles = StudentProfile.query.all()
        
        branch_stats = {}
        for profile in profiles:
            b = profile.branch
            if b not in branch_stats:
                branch_stats[b] = {
                    'students': 0,
                    'avg_cgpa': 0,
                    'applications': 0,
                    'placed': 0
                }
            
            branch_stats[b]['students'] += 1
            branch_stats[b]['avg_cgpa'] += profile.cgpa
            
            # Count applications
            apps = Application.query.filter_by(student_id=profile.user_id).all()
            branch_stats[b]['applications'] += len(apps)
            
            # Count placed
            placed = any(app.status == 'Selected' for app in apps)
            if placed:
                branch_stats[b]['placed'] += 1
        
        # Average CGPA
        for b in branch_stats:
            if branch_stats[b]['students'] > 0:
                branch_stats[b]['avg_cgpa'] = round(
                    branch_stats[b]['avg_cgpa'] / branch_stats[b]['students'], 2
                )
        
        return {
            'message': 'Branch Analytics',
            'analytics': branch_stats,
            'count': len(branch_stats)
        }


def secure_intent_router(db) -> SecureIntentRouter:
    """Create and return a secure intent router instance."""
    return SecureIntentRouter(db)
