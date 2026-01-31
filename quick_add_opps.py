#!/usr/bin/env python
"""Simple script to add test opportunities - run this with: python -c "exec(open('quick_add_opps.py').read())" """

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta

# Import after path setup
from app import create_app, db
from app.models import Opportunity

app = create_app()

with app.app_context():
    # Check if opportunities exist
    count = Opportunity.query.count()
    if count > 0:
        print(f"Database already has {count} opportunities.")
        sys.exit(0)
    
    # Add test opportunities
    test_data = [
        ("Senior Software Engineer", "Job", "Google", "Google", "Exciting opportunity to work on Google's core products", "Python\nJava\nSystem Design\n5+ years", 25, "CSE, IT, ECE", 3.5),
        ("Data Science Intern", "Internship", "Amazon", "Amazon", "Work on ML projects with our data science team", "Python\nML\nSQL", 500, "CSE, IT", 3.2),
        ("Web Development Workshop", "Session", "TechHub", None, "Learn React, Node.js with industry experts", "Basic JS\nHTML/CSS", None, None, None),
        ("CodeQuest 2026", "Hackathon", "Innovation Lab", None, "24-hour coding competition with amazing prizes", "Programming\nTeam of 2-4", None, None, None),
        ("Full Stack Bootcamp", "Bootcamp", "CodePath", None, "Intensive 12-week program with 100% placement", "Basic programming", None, None, None),
    ]
    
    for i, (title, opp_type, org, comp, desc, reqs, ctc_val, branches, cgpa) in enumerate(test_data):
        opp = Opportunity(
            title=title,
            type=opp_type,
            organizer=org,
            company_name=comp,
            description=desc,
            requirements=reqs,
            date=datetime.now() + timedelta(days=10+i*5),
            mode="Online/Hybrid",
        )
        
        if ctc_val:
            opp.ctc = f"{ctc_val} LPA" if ctc_val > 10 else f"Rs. {ctc_val}/day"
        if branches:
            opp.allowed_branches = branches
        if cgpa:
            opp.min_cgpa = cgpa
        if opp_type in ['Job', 'Internship']:
            opp.deadline = datetime.now() + timedelta(days=5+i)
        
        db.session.add(opp)
    
    try:
        db.session.commit()
        print(f"✓ Added {len(test_data)} test opportunities")
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error: {e}")
