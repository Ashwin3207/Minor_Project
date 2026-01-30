#!/usr/bin/env python
"""Add test opportunities to the database for development/testing."""

from datetime import datetime, timedelta
from app import create_app, db
from app.models import Opportunity

# Create app context
app = create_app()

with app.app_context():
    # Clear existing opportunities (optional)
    # Opportunity.query.delete()
    
    test_opportunities = [
        # Jobs
        Opportunity(
            title="Senior Software Engineer",
            type="Job",
            organizer="Google",
            company_name="Google",
            description="We are looking for experienced software engineers to join our team. Work on cutting-edge technologies and solve complex problems.",
            requirements="Python\nJava\nSystem Design\n5+ years experience",
            date=datetime.now() + timedelta(days=30),
            mode="Online",
            ctc="25 LPA",
            min_cgpa=3.5,
            allowed_branches="CSE, IT, ECE",
            deadline=datetime.now() + timedelta(days=14)
        ),
        Opportunity(
            title="Data Science Intern",
            type="Internship",
            organizer="Amazon",
            company_name="Amazon",
            description="Join our data science team and work on machine learning projects that impact millions of customers.",
            requirements="Python\nMachine Learning\nSQL",
            date=datetime.now() + timedelta(days=25),
            mode="Hybrid",
            ctc="500/day",
            min_cgpa=3.2,
            allowed_branches="CSE, IT",
            deadline=datetime.now() + timedelta(days=10)
        ),
        
        # Sessions
        Opportunity(
            title="Web Development Workshop",
            type="Session",
            organizer="TechHub",
            company_name="TechHub",
            description="Learn modern web development with React and Node.js. Hands-on workshop with industry experts.",
            requirements="Basic JavaScript knowledge\nHTML/CSS basics",
            date=datetime.now() + timedelta(days=7),
            mode="Online",
        ),
        Opportunity(
            title="Cloud Computing Seminar",
            type="Session",
            organizer="AWS Community",
            company_name="AWS",
            description="Discover AWS services and cloud architecture best practices.",
            requirements="None",
            date=datetime.now() + timedelta(days=14),
            mode="Hybrid",
        ),
        
        # Hackathon
        Opportunity(
            title="CodeQuest 2026",
            type="Hackathon",
            organizer="Innovation Lab",
            company_name="Innovation Lab",
            description="24-hour hackathon with prizes worth Rs. 5 lakhs. Build something amazing!",
            requirements="Programming knowledge\nTeam of 2-4 people",
            date=datetime.now() + timedelta(days=45),
            mode="Offline",
        ),
        
        # Bootcamp
        Opportunity(
            title="Full Stack Development Bootcamp",
            type="Bootcamp",
            organizer="CodePath",
            company_name="CodePath",
            description="Intensive 12-week program to become a full-stack developer. 100% job guarantee.",
            requirements="Basic programming knowledge",
            date=datetime.now() + timedelta(days=20),
            mode="Hybrid",
        ),
        
        # Seminar
        Opportunity(
            title="AI and Ethics Discussion Panel",
            type="Seminar",
            organizer="AI Society",
            company_name="AI Society",
            description="Discuss ethical implications of AI with industry leaders and researchers.",
            requirements="Interest in AI and ethics",
            date=datetime.now() + timedelta(days=10),
            mode="Online",
        ),
    ]
    
    # Add test opportunities
    for opp in test_opportunities:
        # Check if opportunity already exists
        existing = Opportunity.query.filter_by(title=opp.title).first()
        if not existing:
            db.session.add(opp)
            print(f"Added: {opp.title}")
        else:
            print(f"Skipped (already exists): {opp.title}")
    
    try:
        db.session.commit()
        print("\nTest opportunities added successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
