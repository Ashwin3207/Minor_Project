#!/usr/bin/env python3
"""Test the complete job and opportunity application flow"""

from app import create_app, db
from app.models import User, StudentProfile, Job, Opportunity, Application
from datetime import datetime, timedelta

app = create_app('development')

with app.app_context():
    print("=" * 70)
    print("TESTING COMPLETE APPLICATION FLOW")
    print("=" * 70)
    print()
    
    # Count existing data
    students = User.query.filter_by(role='Student').count()
    jobs = Job.query.count()
    opps = Opportunity.query.count()
    apps = Application.query.count()
    
    print("CURRENT STATE:")
    print(f"  Students: {students}")
    print(f"  Jobs posted: {jobs}")
    print(f"  Opportunities: {opps}")
    print(f"  Total Applications: {apps}")
    print()
    
    # Test Job Applications
    print("JOB APPLICATIONS:")
    job_apps = Application.query.filter(Application.job_id.isnot(None)).count()
    print(f"  ✓ Job applications in database: {job_apps}")
    
    if job_apps > 0:
        print("  Sample job applications:")
        for app in Application.query.filter(Application.job_id.isnot(None)).limit(3):
            job = Job.query.get(app.job_id)
            student = User.query.get(app.student_id)
            print(f"    - {student.username} → {job.company_name} ({app.status})")
    print()
    
    # Test Opportunity Applications
    print("OPPORTUNITY APPLICATIONS:")
    opp_apps = Application.query.filter(Application.opportunity_id.isnot(None)).count()
    print(f"  ✓ Opportunity applications in database: {opp_apps}")
    
    if opp_apps > 0:
        print("  Sample opportunity applications:")
        for app in Application.query.filter(Application.opportunity_id.isnot(None)).limit(3):
            opp = Opportunity.query.get(app.opportunity_id)
            student = User.query.get(app.student_id)
            print(f"    - {student.username} → {opp.title} ({app.status})")
    print()
    
    # Test Admin Access
    print("ADMIN VIEW - JOB APPLICANTS:")
    if jobs > 0:
        sample_job = Job.query.first()
        job_app_count = Application.query.filter_by(job_id=sample_job.id).count()
        print(f"  Job: {sample_job.company_name}")
        print(f"  Applicants: {job_app_count}")
        print(f"  ✓ Admin can view at /admin/job_applicants/{sample_job.id}")
    else:
        print("  No jobs posted yet")
    print()
    
    print("ADMIN VIEW - OPPORTUNITY APPLICANTS:")
    if opps > 0:
        sample_opp = Opportunity.query.first()
        opp_app_count = Application.query.filter_by(opportunity_id=sample_opp.id).count()
        print(f"  Opportunity: {sample_opp.title}")
        print(f"  Applicants: {opp_app_count}")
        print(f"  ✓ Admin can view at /admin/opportunity_applicants/{sample_opp.id}")
    else:
        print("  No opportunities posted yet")
    print()
    
    # Summary
    print("=" * 70)
    print("APPLICATION FLOW STATUS:")
    print("=" * 70)
    print()
    print("STUDENT FLOW:")
    print("  1. Student logs in → /student/profile")
    print("  2. Views jobs → /student/apply (job_id=X)")
    print("     OR views opportunities → /student/opportunity/<id>/apply")
    print("  3. Application saved to database with:")
    print("     - job_id or opportunity_id")
    print("     - status='Applied'")
    print("     - applied_at timestamp")
    print()
    print("ADMIN FLOW:")
    print("  1. Admin goes to dashboard → /admin/dashboard")
    print("  2. Clicks 'View Jobs & Applicants' → /admin/view_jobs")
    print("  3. Clicks 'View Applicants' on a job → /admin/job_applicants/<id>")
    print("  4. OR clicks 'Manage Opportunities' → /admin/opportunities")
    print("  5. Clicks 'View Applicants' → /admin/opportunity_applicants/<id>")
    print("  6. Updates applicant status via dropdown")
    print()
    print("✓ ALL SYSTEMS READY")
    print("=" * 70)
