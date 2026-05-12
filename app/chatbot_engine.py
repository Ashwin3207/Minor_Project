"""
Intelligent Keyword-Based Chatbot Engine with comprehensive database awareness.
No external AI services - pure keyword matching with database context and instant responses.
"""

import logging
import re
from datetime import datetime
from sqlalchemy import and_, or_

from app import db
from app.models import User, StudentProfile, Opportunity, Application

logger = logging.getLogger(__name__)


def _company_label(opp):
    if not opp:
        return "Unknown Company"
    return opp.company_name or getattr(opp, "organizer", None) or "Unknown Company"


class ChatbotEngine:
    """Keyword-based chatbot with comprehensive database-aware responses."""

    def __init__(self, session=None):
        self.session = session or db.session

    def process_query(self, user_message, user_id=None, conversation_history=None):
        """Route query to appropriate handler based on keywords."""
        if not user_message or not isinstance(user_message, str):
            return self._err("Please provide a valid message.")

        user_message = user_message.strip()
        if not user_message:
            return self._err("Please provide a valid message.")

        msg_lower = user_message.lower()

        # Check greeting first
        greeting = self._check_greeting(msg_lower)
        if greeting:
            return greeting

        # Admin shortcuts
        admin_result = self._admin_shortcuts(msg_lower, user_id)
        if admin_result:
            return admin_result

        # Keyword-based routing
        return self._keyword_router(msg_lower, user_id)

    def _keyword_router(self, msg, user_id):
        """Route to appropriate handler based on message keywords."""
        
        # OPPORTUNITIES & JOBS (highest priority)
        if any(w in msg for w in ["opportunit", "job", "jobs", "opening", "opening", "hiring", "hire", "recruit", "position"]):
            return self._handle_opportunities(msg, user_id)
        
        # COMPANIES
        if any(w in msg for w in ["compan", "employer", "organization", "org", "who is", "tell me about", "list compan"]):
            return self._handle_companies(msg, user_id)
        
        # INTERNSHIPS
        if any(w in msg for w in ["intern", "internship", "trainee"]):
            return self._handle_internships(msg, user_id)
        
        # ELIGIBILITY
        if any(w in msg for w in ["eligib", "qualify", "can i apply", "suitable", "my profile", "match"]):
            if not user_id:
                return self._ok("Please log in to check eligibility.", "eligibility")
            return self._handle_eligibility(msg, user_id)
        
        # APPLICATIONS & STATUS
        if any(w in msg for w in ["application", "applied", "apply", "my application", "track", "status", "shortlist", "rejected", "selected"]):
            if not user_id:
                return self._ok("Please log in to view your applications.", "applications")
            return self._handle_applications(msg, user_id)
        
        # DEADLINES
        if any(w in msg for w in ["deadline", "due date", "when", "expire", "close", "last date", "end date"]):
            return self._handle_deadlines(msg)
        
        # UPCOMING/RECENT
        if any(w in msg for w in ["upcoming", "next", "coming", "soon", "this month", "this week", "recent", "latest", "new"]):
            return self._handle_upcoming_recent(msg)
        
        # PLACEMENT STATISTICS
        if any(w in msg for w in ["placement", "statistic", "stats", "placed", "rate", "percentage", "how many", "data", "analytics", "performance"]):
            return self._handle_placement_stats(msg, user_id)
        
        # BRANCH ANALYTICS
        if any(w in msg for w in ["branch", "branch-wise", "department", "stream", "breakdown", "analytics"]):
            return self._handle_branch_analytics(msg, user_id)
        
        # STUDENT PROFILE
        if any(w in msg for w in ["profile", "my profile", "my info", "information", "about me", "details"]):
            if not user_id:
                return self._ok("Please log in to view your profile.", "profile")
            return self._handle_student_profile(msg, user_id)
        
        # CGPA/GRADES
        if any(w in msg for w in ["cgpa", "gpa", "grade", "grades", "marks", "score", "academic"]):
            if not user_id:
                return self._ok("Please log in to view academic details.", "cgpa")
            return self._handle_cgpa(msg, user_id)
        
        # SKILLS
        if any(w in msg for w in ["skill", "skills", "expertise", "competency", "capability", "ability"]):
            if not user_id:
                return self._ok("Please log in to manage skills.", "skills")
            return self._handle_skills(msg, user_id)
        
        # RESUME
        if any(w in msg for w in ["resume", "cv", "curriculum", "upload", "download", "resume link"]):
            if not user_id:
                return self._ok("Please log in to manage resume.", "resume")
            return self._handle_resume(msg, user_id)
        
        # INTERNSHIP EXPERIENCE
        if any(w in msg for w in ["internship detail", "intern exp", "experience", "previous work"]):
            if not user_id:
                return self._ok("Please log in to view internship details.", "internship")
            return self._handle_internship_details(msg, user_id)
        
        # NPTEL COURSES
        if any(w in msg for w in ["nptel", "course", "courses", "certification"]):
            if not user_id:
                return self._ok("Please log in to view NPTEL courses.", "nptel")
            return self._handle_nptel(msg, user_id)
        
        # FINAL YEAR PROJECT
        if any(w in msg for w in ["project", "final year", "fyp", "capstone", "senior project"]):
            if not user_id:
                return self._ok("Please log in to view projects.", "project")
            return self._handle_fyp(msg, user_id)
        
        # CTC/SALARY INFO
        if any(w in msg for w in ["ctc", "salary", "package", "pay", "stipend", "lpa", "compensation", "remuneration"]):
            return self._handle_ctc(msg, user_id)
        
        # INDIVIDUAL STUDENT DETAILS (admin - for TPO to view specific student)
        if any(w in msg for w in ["view student", "show student", "student details", "get student", "student info", "student profile", "individual student"]):
            if not user_id:
                return self._denied("Admin access required.")
            return self._handle_individual_student_details(msg, user_id)
        
        # STUDENTS LIST (admin)
        if any(w in msg for w in ["list students", "show students", "all students", "student list", "students info"]):
            if not user_id:
                return self._denied("Admin access required.")
            return self._handle_students_list(msg, user_id)
        
        # APPLICANTS LIST (admin)
        if any(w in msg for w in ["applicants", "list applicants", "who applied", "all applicants", "candidates"]):
            if not user_id:
                return self._denied("Admin access required.")
            return self._handle_applicants_list(msg, user_id)
        
        # ADMIN ANALYTICS (admin - filter by criteria)
        if any(w in msg for w in ["filter students", "search students", "students by", "find students", "get students", "cgpa above", "branch-wise students", "no backlog", "backlog students", "top students", "high performers"]):
            if not user_id:
                return self._denied("Admin access required.")
            return self._handle_admin_analytics(msg, user_id)
        
        # HELP
        if any(w in msg for w in ["help", "what can", "what do you", "how to", "guide", "tutorial", "features"]):
            return self._help_text()
        
        # Default fallback
        return self._intelligent_fallback(msg, user_id)

    def _handle_opportunities(self, msg, user_id):
        """Handle opportunity/job queries."""
        try:
            opps = Opportunity.query.order_by(Opportunity.created_at.desc()).limit(10).all()
            
            if not opps:
                return self._ok("No opportunities found in the system.", "opportunities")
            
            lines = [f"Found {Opportunity.query.count()} opportunities. Here are the latest {len(opps)}:"]
            for o in opps:
                dl = o.deadline.strftime("%Y-%m-%d") if o.deadline else "N/A"
                ctc_info = f"₹ {o.ctc} LPA" if o.ctc else "Not disclosed"
                days_left = ""
                if o.deadline and o.deadline > datetime.utcnow():
                    days_left = f" ({(o.deadline - datetime.utcnow()).days}d left)"
                
                lines.append(f"• [{o.type}] {o.title} @ {_company_label(o)} | CTC: {ctc_info} | Deadline: {dl}{days_left}")
            
            return self._ok("\n".join(lines), "opportunities", "opportunity_search")
        except Exception as e:
            logger.error(f"Error in _handle_opportunities: {e}")
            return self._ok("No opportunities available.", "opportunities")

    def _handle_companies(self, msg, user_id):
        """Handle company-related queries."""
        try:
            opps = Opportunity.query.with_entities(Opportunity.company_name).distinct().limit(20).all()
            companies = [o[0] for o in opps if o[0]]
            
            if not companies:
                return self._ok("No company information available.", "companies")
            
            lines = [f"We have {len(companies)} companies recruiting:"]
            for comp in companies:
                lines.append(f"• {comp}")
            
            return self._ok("\n".join(lines), "companies")
        except Exception as e:
            logger.error(f"Error in _handle_companies: {e}")
            return self._ok("No company data available.", "companies")

    def _handle_internships(self, msg, user_id):
        """Handle internship queries."""
        try:
            internships = Opportunity.query.filter_by(type="Internship").order_by(Opportunity.created_at.desc()).limit(10).all()
            
            if not internships:
                return self._ok("No internships available right now.", "internship")
            
            lines = [f"Found {len(internships)} internship opportunities:"]
            for i in internships:
                ctc = f"₹ {i.ctc}" if i.ctc else "Unpaid/Unfunded"
                lines.append(f"• {i.title} @ {_company_label(i)} | {ctc}")
            
            return self._ok("\n".join(lines), "internship")
        except Exception as e:
            logger.error(f"Error in _handle_internships: {e}")
            return self._ok("No internship data available.", "internship")

    def _handle_eligibility(self, msg, user_id):
        """Check user eligibility for opportunities."""
        try:
            profile = StudentProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                return self._ok("Please complete your profile first.", "eligibility")
            
            eligible = Opportunity.query.filter(
                and_(
                    or_(
                        Opportunity.min_cgpa <= profile.cgpa,
                        Opportunity.min_cgpa.is_(None),
                    ),
                    or_(
                        Opportunity.allowed_branches.contains(profile.branch),
                        Opportunity.allowed_branches.is_(None),
                    ),
                    Opportunity.deadline > datetime.utcnow(),
                )
            ).all()
            
            if not eligible:
                return self._ok(f"No opportunities match your profile ({profile.branch}, CGPA: {profile.cgpa}).", "eligibility")
            
            lines = [f"You are eligible for {len(eligible)} opportunities:"]
            for o in eligible[:8]:
                lines.append(f"• {o.title} @ {_company_label(o)}")
            
            if len(eligible) > 8:
                lines.append(f"... and {len(eligible) - 8} more")
            
            return self._ok("\n".join(lines), "eligibility")
        except Exception as e:
            logger.error(f"Error in _handle_eligibility: {e}")
            return self._ok("Could not check eligibility.", "eligibility")

    def _handle_applications(self, msg, user_id):
        """Handle application status queries."""
        try:
            apps = Application.query.filter_by(student_id=user_id).order_by(Application.applied_at.desc()).all()
            
            if not apps:
                return self._ok("You haven't applied to any opportunities yet.", "applications")
            
            status_counts = {}
            lines = [f"Your applications ({len(apps)} total):"]
            
            for app in apps[:15]:
                status_counts[app.status] = status_counts.get(app.status, 0) + 1
                opp = Opportunity.query.get(app.opportunity_id)
                if opp:
                    lines.append(f"• {opp.title} @ {_company_label(opp)} → {app.status}")
            
            summary = ", ".join(f"{s}: {c}" for s, c in status_counts.items())
            lines.append(f"\nSummary: {summary}")
            
            return self._ok("\n".join(lines), "applications")
        except Exception as e:
            logger.error(f"Error in _handle_applications: {e}")
            return self._ok("Could not fetch applications.", "applications")

    def _handle_deadlines(self, msg, user_id):
        """Handle deadline queries."""
        try:
            opps = Opportunity.query.filter(
                Opportunity.deadline > datetime.utcnow()
            ).order_by(Opportunity.deadline).limit(10).all()
            
            if not opps:
                return self._ok("No active opportunities with deadlines.", "deadline")
            
            lines = ["Upcoming deadlines:"]
            for o in opps:
                dl = o.deadline.strftime("%Y-%m-%d")
                days = (o.deadline - datetime.utcnow()).days
                lines.append(f"• {o.title} @ {_company_label(o)} | {dl} ({days}d left)")
            
            return self._ok("\n".join(lines), "deadline")
        except Exception as e:
            logger.error(f"Error in _handle_deadlines: {e}")
            return self._ok("No deadline information available.", "deadline")

    def _handle_upcoming_recent(self, msg, user_id):
        """Handle upcoming/recent opportunities."""
        try:
            if "recent" in msg:
                opps = Opportunity.query.order_by(Opportunity.created_at.desc()).limit(8).all()
                title = "Recently posted opportunities:"
            else:
                opps = Opportunity.query.filter(
                    Opportunity.deadline > datetime.utcnow()
                ).order_by(Opportunity.deadline).limit(8).all()
                title = "Upcoming opportunities:"
            
            if not opps:
                return self._ok("No opportunities found.", "upcoming")
            
            lines = [title]
            for o in opps:
                lines.append(f"• {o.title} @ {_company_label(o)}")
            
            return self._ok("\n".join(lines), "upcoming")
        except Exception as e:
            logger.error(f"Error in _handle_upcoming_recent: {e}")
            return self._ok("No upcoming opportunities available.", "upcoming")

    def _handle_placement_stats(self, msg, user_id):
        """Handle placement statistics queries."""
        try:
            total_students = StudentProfile.query.count()
            placed = db.session.query(Application).filter_by(status="Selected").distinct(Application.student_id).count()
            total_apps = Application.query.count()
            applied = Application.query.filter_by(status="Applied").count()
            shortlisted = Application.query.filter_by(status="Shortlisted").count()
            rejected = Application.query.filter_by(status="Rejected").count()
            total_opps = Opportunity.query.count()
            
            rate = (placed / total_students * 100) if total_students else 0
            
            lines = [
                "📊 Placement Statistics:",
                f"• Total Students: {total_students}",
                f"• Placed: {placed}",
                f"• Placement Rate: {rate:.1f}%",
                f"• Total Opportunities: {total_opps}",
                f"",
                "Application Status:",
                f"• Applied: {applied}",
                f"• Shortlisted: {shortlisted}",
                f"• Rejected: {rejected}",
                f"• Total Applications: {total_apps}",
            ]
            
            return self._ok("\n".join(lines), "placement_stats")
        except Exception as e:
            logger.error(f"Error in _handle_placement_stats: {e}")
            return self._ok("Could not fetch statistics.", "placement_stats")

    def _handle_branch_analytics(self, msg, user_id):
        """Handle branch-wise analytics."""
        try:
            branch_data = db.session.query(
                StudentProfile.branch,
                db.func.count(StudentProfile.id),
                db.func.avg(StudentProfile.cgpa)
            ).group_by(StudentProfile.branch).all()
            
            if not branch_data:
                return self._ok("No branch data available.", "branch_analytics")
            
            lines = ["📈 Branch-wise Analytics:"]
            for branch, count, avg_cgpa in branch_data:
                lines.append(f"• {branch}: {count} students, Avg CGPA: {avg_cgpa:.2f}")
            
            return self._ok("\n".join(lines), "branch_analytics")
        except Exception as e:
            logger.error(f"Error in _handle_branch_analytics: {e}")
            return self._ok("Could not fetch branch analytics.", "branch_analytics")

    def _handle_student_profile(self, msg, user_id):
        """Handle student profile queries."""
        try:
            user = User.query.get(user_id)
            profile = StudentProfile.query.filter_by(user_id=user_id).first()
            
            if not user or not profile:
                return self._ok("Profile not found.", "profile")
            
            lines = [
                f"👤 Your Profile:",
                f"• Name: {user.username}",
                f"• Email: {user.email}",
                f"• Branch: {profile.branch}",
                f"• CGPA: {profile.cgpa}",
                f"• Skills: {profile.skills or 'Not specified'}",
                f"• Internship: {profile.internship_details or 'Not specified'}",
                f"• NPTEL: {profile.nptel or 'Not specified'}",
                f"• Final Year Project: {profile.final_year_project or 'Not specified'}",
                f"• Resume: {'Uploaded' if profile.resume_link else 'Not uploaded'}",
            ]
            
            return self._ok("\n".join(lines), "profile")
        except Exception as e:
            logger.error(f"Error in _handle_student_profile: {e}")
            return self._ok("Could not fetch profile.", "profile")

    def _handle_cgpa(self, msg, user_id):
        """Handle CGPA/grades queries."""
        try:
            profile = StudentProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                return self._ok("Academic information not available.", "cgpa")
            
            top_performers = StudentProfile.query.filter(StudentProfile.cgpa >= 8.0).count()
            rank = StudentProfile.query.filter(StudentProfile.cgpa > profile.cgpa).count() + 1
            
            lines = [
                f"📚 Academic Information:",
                f"• Your CGPA: {profile.cgpa}",
                f"• Your Rank: {rank} among all students",
                f"• Top Performers (≥8.0): {top_performers}",
            ]
            
            return self._ok("\n".join(lines), "cgpa")
        except Exception as e:
            logger.error(f"Error in _handle_cgpa: {e}")
            return self._ok("Could not fetch academic data.", "cgpa")

    def _handle_skills(self, msg, user_id):
        """Handle skills queries."""
        try:
            profile = StudentProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                return self._ok("Please complete your profile.", "skills")
            
            skills = profile.skills or "Not specified yet"
            lines = [
                f"💼 Your Skills:",
                f"{skills}",
                "",
                "Tip: Update your skills to improve job matching!"
            ]
            
            return self._ok("\n".join(lines), "skills")
        except Exception as e:
            logger.error(f"Error in _handle_skills: {e}")
            return self._ok("Could not fetch skills.", "skills")

    def _handle_resume(self, msg, user_id):
        """Handle resume queries."""
        try:
            profile = StudentProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                return self._ok("Please create your profile.", "resume")
            
            status = "✓ Uploaded" if profile.resume_link else "✗ Not uploaded"
            lines = [
                f"📄 Resume Status: {status}",
                "",
                "A resume is important for job applications!",
                "Make sure it's updated and uploaded."
            ]
            
            return self._ok("\n".join(lines), "resume")
        except Exception as e:
            logger.error(f"Error in _handle_resume: {e}")
            return self._ok("Could not fetch resume status.", "resume")

    def _handle_internship_details(self, msg, user_id):
        """Handle internship experience queries."""
        try:
            profile = StudentProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                return self._ok("Profile not found.", "internship")
            
            details = profile.internship_details or "No internship experience recorded"
            lines = [
                f"🏢 Internship Experience:",
                details
            ]
            
            return self._ok("\n".join(lines), "internship")
        except Exception as e:
            logger.error(f"Error in _handle_internship_details: {e}")
            return self._ok("Could not fetch internship details.", "internship")

    def _handle_nptel(self, msg, user_id):
        """Handle NPTEL courses queries."""
        try:
            profile = StudentProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                return self._ok("Profile not found.", "nptel")
            
            nptel = profile.nptel or "No NPTEL courses recorded"
            lines = [
                f"🎓 NPTEL Courses:",
                nptel
            ]
            
            return self._ok("\n".join(lines), "nptel")
        except Exception as e:
            logger.error(f"Error in _handle_nptel: {e}")
            return self._ok("Could not fetch NPTEL courses.", "nptel")

    def _handle_fyp(self, msg, user_id):
        """Handle final year project queries."""
        try:
            profile = StudentProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                return self._ok("Profile not found.", "project")
            
            fyp = profile.final_year_project or "No FYP information recorded"
            lines = [
                f"🚀 Final Year Project:",
                fyp
            ]
            
            return self._ok("\n".join(lines), "project")
        except Exception as e:
            logger.error(f"Error in _handle_fyp: {e}")
            return self._ok("Could not fetch project details.", "project")

    def _handle_ctc(self, msg, user_id):
        """Handle CTC/salary queries."""
        try:
            opps = Opportunity.query.filter(Opportunity.ctc.isnot(None)).order_by(Opportunity.ctc.desc()).limit(10).all()
            
            if not opps:
                return self._ok("No salary information available.", "ctc")
            
            lines = [f"💰 Top CTC Offerings (found {len(opps)} opportunities with salary info):"]
            for o in opps[:8]:
                lines.append(f"• {o.title} @ {_company_label(o)}: ₹ {o.ctc} LPA")
            
            if len(opps) > 8:
                lines.append(f"... and {len(opps) - 8} more")
            
            return self._ok("\n".join(lines), "ctc")
        except Exception as e:
            logger.error(f"Error in _handle_ctc: {e}")
            return self._ok("Could not fetch salary information.", "ctc")

    def _handle_students_list(self, msg, user_id):
        """Handle student list query (admin)."""
        try:
            user = User.query.get(user_id)
            if not user or user.role.lower() != "admin":
                return self._denied("Only admins can view student list.")
            
            students = db.session.query(
                User.username, User.email, StudentProfile.branch, StudentProfile.cgpa
            ).join(StudentProfile, StudentProfile.user_id == User.id).order_by(User.username).limit(30).all()
            
            if not students:
                return self._ok("No students found.", "students_list")
            
            lines = [f"👥 Student List ({len(students)} shown):"]
            for username, email, branch, cgpa in students:
                lines.append(f"• {username} ({email}) - {branch}, CGPA: {cgpa}")
            
            return self._ok("\n".join(lines), "students_list")
        except Exception as e:
            logger.error(f"Error in _handle_students_list: {e}")
            return self._denied("Could not fetch student list.")

    def _handle_individual_student_details(self, msg, user_id):
        """Handle individual student details query (admin/TPO)."""
        try:
            user = User.query.get(user_id)
            if not user or user.role.lower() != "admin":
                return self._denied("Only admins can view student details.")
            
            # Extract student name/username from message
            # Handle patterns like "view student <name>", "show student <name>", etc.
            student_name = self._extract_student_name(msg)
            
            if not student_name:
                return self._ok(
                    "Please specify the student name or username.\n"
                    "Example: 'View student John' or 'Show student details for gaurav'",
                    "student_details"
                )
            
            # Find student by username or name
            student = User.query.filter(
                (User.username.ilike(f"%{student_name}%")) |
                (User.email.ilike(f"%{student_name}%"))
            ).first()
            
            if not student:
                return self._ok(
                    f"Student '{student_name}' not found in the system.",
                    "student_details"
                )
            
            # Get student profile
            profile = StudentProfile.query.filter_by(user_id=student.id).first()
            
            if not profile:
                return self._ok(
                    f"Profile for student '{student.username}' not found.",
                    "student_details"
                )
            
            # Get student applications
            applications = Application.query.filter_by(student_id=student.id).all()
            app_summary = {
                'total': len(applications),
                'applied': sum(1 for a in applications if a.status == 'Applied'),
                'shortlisted': sum(1 for a in applications if a.status == 'Shortlisted'),
                'selected': sum(1 for a in applications if a.status == 'Selected'),
                'rejected': sum(1 for a in applications if a.status == 'Rejected'),
            }
            
            lines = [
                f"👤 Student Details: {student.username}",
                f"{'='*50}",
                f"\n📋 Personal Information:",
                f"• Username: {student.username}",
                f"• Email: {student.email}",
                f"• Role: {student.role}",
                f"\n🎓 Academic Information:",
                f"• Branch: {profile.branch}",
                f"• CGPA: {profile.cgpa}",
                f"• 10th Percentage: {profile.tenth_percentage if profile.tenth_percentage else 'N/A'}",
                f"• 12th Percentage: {profile.twelfth_percentage if profile.twelfth_percentage else 'N/A'}",
                f"• Backlogs: {'Yes' if profile.has_backlog else 'No'}",
                f"\n💼 Professional Information:",
                f"• Skills: {profile.skills if profile.skills else 'Not specified'}",
                f"• Internship Details: {profile.internship_details if profile.internship_details else 'Not specified'}",
                f"• NPTEL Courses: {profile.nptel if profile.nptel else 'Not specified'}",
                f"• Final Year Project: {profile.final_year_project if profile.final_year_project else 'Not specified'}",
                f"• Resume: {'✓ Uploaded' if profile.resume_link else '✗ Not uploaded'}",
                f"\n📊 Application Summary:",
                f"• Total Applications: {app_summary['total']}",
                f"• Applied: {app_summary['applied']} | Shortlisted: {app_summary['shortlisted']} | Selected: {app_summary['selected']} | Rejected: {app_summary['rejected']}",
            ]
            
            return self._ok("\n".join(lines), "student_details")
        except Exception as e:
            logger.error(f"Error in _handle_individual_student_details: {e}")
            return self._denied("Could not fetch student details.")

    def _extract_student_name(self, msg):
        """Extract student name from message."""
        # Remove common keywords
        keywords = ["view", "show", "student", "details", "for", "get", "profile", "individual", "info"]
        words = msg.lower().split()
        
        # Filter out keywords
        name_words = [w for w in words if w not in keywords and len(w) > 2]
        
        if name_words:
            return " ".join(name_words).strip()
        
        return None

    def _handle_applicants_list(self, msg, user_id):
        """Handle applicants list query (admin)."""
        try:
            user = User.query.get(user_id)
            if not user or user.role.lower() != "admin":
                return self._denied("Only admins can view applicants.")
            
            applicants = db.session.query(
                User.username, Application.status, Opportunity.title
            ).join(Application, Application.student_id == User.id).join(
                Opportunity, Opportunity.id == Application.opportunity_id, isouter=True
            ).order_by(Application.applied_at.desc()).limit(30).all()
            
            if not applicants:
                return self._ok("No applications found.", "applicants_list")
            
            lines = [f"📋 Applicants List ({len(applicants)} recent applications):"]
            for username, status, title in applicants:
                lines.append(f"• {username} - {title or 'N/A'} → {status}")
            
            return self._ok("\n".join(lines), "applicants_list")
        except Exception as e:
            logger.error(f"Error in _handle_applicants_list: {e}")
            return self._denied("Could not fetch applicants list.")

    def _handle_admin_analytics(self, msg, user_id):
        """Handle admin analytics and student filtering queries."""
        try:
            user = User.query.get(user_id)
            if not user or user.role.lower() != "admin":
                return self._denied("Only admins can access analytics.")
            
            msg_lower = msg.lower()
            
            # FILTER BY CGPA
            if "cgpa" in msg_lower and any(w in msg_lower for w in ["above", "greater", "more than", ">", "min"]):
                return self._handle_cgpa_filter(msg, user_id)
            
            # FILTER BY BRANCH
            if "branch" in msg_lower or "department" in msg_lower or "stream" in msg_lower:
                return self._handle_branch_filter(msg, user_id)
            
            # BACKLOG STATUS
            if "backlog" in msg_lower:
                return self._handle_backlog_filter(msg, user_id)
            
            # TOP PERFORMERS
            if any(w in msg_lower for w in ["top student", "high performer", "best student", "topper"]):
                return self._handle_top_performers(msg, user_id)
            
            # DEFAULT: Show overview
            return self._handle_student_analytics_overview(user_id)
        
        except Exception as e:
            logger.error(f"Error in _handle_admin_analytics: {e}")
            return self._denied("Could not fetch analytics.")

    def _handle_cgpa_filter(self, msg, user_id):
        """Filter students by CGPA threshold."""
        try:
            # Extract CGPA value from message
            import re
            cgpa_match = re.search(r'(\d+\.?\d*)', msg)
            cgpa_threshold = float(cgpa_match.group(1)) if cgpa_match else 8.0
            
            students = db.session.query(
                User.username, User.email, StudentProfile.branch, StudentProfile.cgpa
            ).join(StudentProfile, StudentProfile.user_id == User.id).filter(
                StudentProfile.cgpa >= cgpa_threshold
            ).order_by(StudentProfile.cgpa.desc()).limit(30).all()
            
            if not students:
                return self._ok(f"No students found with CGPA ≥ {cgpa_threshold}.", "cgpa_filter")
            
            lines = [f"📊 Students with CGPA ≥ {cgpa_threshold} ({len(students)} found):"]
            lines.append(f"{'Username':<20} {'Email':<30} {'Branch':<15} {'CGPA':<10}")
            lines.append("="*75)
            for username, email, branch, cgpa in students:
                lines.append(f"{username:<20} {email:<30} {branch:<15} {cgpa:<10.2f}")
            
            return self._ok("\n".join(lines), "cgpa_filter")
        except Exception as e:
            logger.error(f"Error in _handle_cgpa_filter: {e}")
            return self._denied("Could not filter by CGPA.")

    def _handle_branch_filter(self, msg, user_id):
        """Filter students by branch."""
        try:
            # Extract branch from message
            keywords = msg.lower().split()
            branch = None
            branch_keywords = ["cse", "ece", "me", "civil", "mechanical", "electrical", "electronics", "it"]
            
            for keyword in keywords:
                if any(b in keyword for b in branch_keywords):
                    branch = keyword.upper()
                    break
            
            if not branch:
                branches = db.session.query(StudentProfile.branch).distinct().all()
                branch_list = [b[0] for b in branches if b[0]]
                return self._ok(
                    f"Available branches: {', '.join(branch_list)}\n"
                    f"Try: 'Show students from CSE' or 'Filter students by ECE'",
                    "branch_filter"
                )
            
            students = db.session.query(
                User.username, User.email, StudentProfile.branch, StudentProfile.cgpa
            ).join(StudentProfile, StudentProfile.user_id == User.id).filter(
                StudentProfile.branch.ilike(f"%{branch}%")
            ).order_by(User.username).limit(50).all()
            
            if not students:
                return self._ok(f"No students found in branch: {branch}", "branch_filter")
            
            lines = [f"📚 Students in {branch} Branch ({len(students)} found):"]
            lines.append(f"{'Username':<20} {'Email':<30} {'CGPA':<10}")
            lines.append("="*60)
            for username, email, branch, cgpa in students:
                lines.append(f"{username:<20} {email:<30} {cgpa:<10.2f}")
            
            return self._ok("\n".join(lines), "branch_filter")
        except Exception as e:
            logger.error(f"Error in _handle_branch_filter: {e}")
            return self._denied("Could not filter by branch.")

    def _handle_backlog_filter(self, msg, user_id):
        """Filter students by backlog status."""
        try:
            msg_lower = msg.lower()
            
            if "no backlog" in msg_lower or "without backlog" in msg_lower or "clean" in msg_lower:
                students = db.session.query(
                    User.username, User.email, StudentProfile.branch, StudentProfile.cgpa
                ).join(StudentProfile, StudentProfile.user_id == User.id).filter(
                    StudentProfile.has_backlog == False
                ).order_by(StudentProfile.cgpa.desc()).limit(50).all()
                
                title = "Students WITHOUT Backlogs"
            else:
                students = db.session.query(
                    User.username, User.email, StudentProfile.branch, StudentProfile.cgpa
                ).join(StudentProfile, StudentProfile.user_id == User.id).filter(
                    StudentProfile.has_backlog == True
                ).order_by(User.username).limit(50).all()
                
                title = "Students WITH Backlogs"
            
            if not students:
                return self._ok(f"No students found matching the backlog criteria.", "backlog_filter")
            
            lines = [f"📋 {title} ({len(students)} found):"]
            lines.append(f"{'Username':<20} {'Email':<30} {'Branch':<15} {'CGPA':<10}")
            lines.append("="*75)
            for username, email, branch, cgpa in students:
                lines.append(f"{username:<20} {email:<30} {branch:<15} {cgpa:<10.2f}")
            
            return self._ok("\n".join(lines), "backlog_filter")
        except Exception as e:
            logger.error(f"Error in _handle_backlog_filter: {e}")
            return self._denied("Could not filter by backlog status.")

    def _handle_top_performers(self, msg, user_id):
        """Get top performing students."""
        try:
            top_count = 10
            # Check if message mentions a specific count
            import re
            count_match = re.search(r'(\d+)', msg)
            if count_match:
                top_count = min(int(count_match.group(1)), 50)
            
            students = db.session.query(
                User.username, User.email, StudentProfile.branch, StudentProfile.cgpa
            ).join(StudentProfile, StudentProfile.user_id == User.id).order_by(
                StudentProfile.cgpa.desc()
            ).limit(top_count).all()
            
            if not students:
                return self._ok("No students found.", "top_performers")
            
            lines = [f"🏆 Top {top_count} Performing Students:"]
            lines.append(f"{'Rank':<6} {'Username':<20} {'Branch':<15} {'CGPA':<10}")
            lines.append("="*51)
            for i, (username, email, branch, cgpa) in enumerate(students, 1):
                lines.append(f"{i:<6} {username:<20} {branch:<15} {cgpa:<10.2f}")
            
            return self._ok("\n".join(lines), "top_performers")
        except Exception as e:
            logger.error(f"Error in _handle_top_performers: {e}")
            return self._denied("Could not fetch top performers.")

    def _handle_student_analytics_overview(self, user_id):
        """Get overall student analytics overview."""
        try:
            total_students = User.query.filter_by(role="Student").count()
            total_profiles = StudentProfile.query.count()
            
            cgpa_stats = db.session.query(
                db.func.avg(StudentProfile.cgpa),
                db.func.min(StudentProfile.cgpa),
                db.func.max(StudentProfile.cgpa),
            ).first()
            
            backlog_count = StudentProfile.query.filter_by(has_backlog=True).count()
            no_backlog_count = StudentProfile.query.filter_by(has_backlog=False).count()
            
            branch_stats = db.session.query(
                StudentProfile.branch,
                db.func.count(StudentProfile.id)
            ).group_by(StudentProfile.branch).all()
            
            lines = [
                "📊 Student Analytics Overview",
                "="*50,
                f"\n📈 Overall Statistics:",
                f"• Total Students: {total_students}",
                f"• Profiles Completed: {total_profiles}",
                f"• Average CGPA: {cgpa_stats[0]:.2f if cgpa_stats[0] else 'N/A'}",
                f"• CGPA Range: {cgpa_stats[2]:.2f if cgpa_stats[2] else 'N/A'} - {cgpa_stats[1]:.2f if cgpa_stats[1] else 'N/A'}",
                f"\n✓ Students Without Backlogs: {no_backlog_count}",
                f"✗ Students With Backlogs: {backlog_count}",
                f"\n🎓 Branch-wise Distribution:",
            ]
            
            for branch, count in branch_stats:
                lines.append(f"• {branch}: {count} students")
            
            lines.append(f"\nℹ️ Useful commands:")
            lines.append("• 'View student [name]' - Get specific student details")
            lines.append("• 'Show students with CGPA > 8' - Filter by CGPA")
            lines.append("• 'Filter students by CSE' - Filter by branch")
            lines.append("• 'Show top 10 students' - Get top performers")
            
            return self._ok("\n".join(lines), "analytics_overview")
        except Exception as e:
            logger.error(f"Error in _handle_student_analytics_overview: {e}")
            return self._denied("Could not fetch analytics.")

    def _intelligent_fallback(self, msg, user_id):
        """Provide intelligent fallback based on available data."""
        try:
            total_opps = Opportunity.query.count()
            if total_opps > 0:
                opps = Opportunity.query.order_by(Opportunity.created_at.desc()).limit(5).all()
                lines = ["💡 Based on your query, here are recent opportunities:"]
                for o in opps:
                    lines.append(f"• {o.title} @ {_company_label(o)}")
                return self._ok("\n".join(lines), "search")
        except Exception:
            pass
        
        return self._ok(
            "I'm here to help! Try asking about:\n"
            "• Opportunities, jobs, internships\n"
            "• Companies, salary (CTC)\n"
            "• Your applications and status\n"
            "• Eligibility for positions\n"
            "• Placement statistics\n"
            "• Your profile and skills\n"
            "• Upcoming deadlines\n"
            "Type 'help' for more options!",
            "fallback"
        )

    def _check_greeting(self, msg):
        """Handle greetings."""
        greetings = {
            "hello": "Hello! 👋 I'm your Training & Placement Assistant. How can I help you today?",
            "hi": "Hi there! 😊 What would you like to know?",
            "hey": "Hey! 👋 Ask me about opportunities, applications, or anything about placements!",
            "thanks": "You're welcome! 😊 Need anything else?",
            "thank you": "Happy to help! 😊 Anything else?",
            "bye": "Goodbye! 👋 Good luck with your placements!",
            "goodbye": "See you later! 👋",
            "how are you": "I'm doing great, thanks for asking! How can I assist?",
            "ok": "Great! What else can I help?",
            "sure": "Perfect! What would you like to know?",
        }
        
        normalized = re.sub(r"[^a-z\s]", " ", msg)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        
        for key, response in greetings.items():
            if key in normalized:
                return {"answer": response, "success": True, "context": "greeting", "intent": None}
        
        return None

    def _admin_shortcuts(self, msg, user_id):
        """Handle admin-specific shortcuts."""
        if not user_id:
            return None
        
        try:
            user = User.query.get(user_id)
            if not user or user.role.lower() != "admin":
                return None
            
            if any(w in msg for w in ["cgpa", "gpa"]) and any(w in msg for w in ["student", "show", "list", "filter"]):
                threshold = self._extract_threshold(msg)
                if threshold is not None:
                    return self._students_by_cgpa_threshold(threshold)
        except Exception:
            pass
        
        return None

    def _students_by_cgpa_threshold(self, threshold):
        """Get students above CGPA threshold."""
        try:
            students = db.session.query(
                User.username, User.email, StudentProfile.branch, StudentProfile.cgpa
            ).join(StudentProfile, StudentProfile.user_id == User.id).filter(
                StudentProfile.cgpa >= threshold
            ).order_by(StudentProfile.cgpa.desc()).limit(30).all()
            
            if not students:
                return self._ok(f"No students with CGPA >= {threshold}.", "student_search")
            
            lines = [f"Students with CGPA ≥ {threshold}: ({len(students)} found)"]
            for username, email, branch, cgpa in students:
                lines.append(f"• {username} ({email}) - {branch}, CGPA: {cgpa}")
            
            return self._ok("\n".join(lines), "student_search")
        except Exception as e:
            logger.error(f"Error in _students_by_cgpa_threshold: {e}")
            return self._ok(f"Could not fetch students.", "student_search")

    @staticmethod
    def _extract_threshold(msg):
        """Extract numeric threshold from message."""
        match = re.search(r"(\d+(?:\.\d+)?)", msg.lower())
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None

    @staticmethod
    def _help_text():
        """Return help information."""
        return {
            "answer": (
                "🤖 Training & Placement Assistant - Help Guide\n\n"
                "I can help you with:\n\n"
                "🔍 **Search & Discovery**\n"
                "• Show me opportunities / jobs / internships\n"
                "• List companies / organizations\n"
                "• What's the salary (CTC)?\n"
                "• Show upcoming opportunities\n\n"
                "📋 **Your Information**\n"
                "• Show my profile / applications\n"
                "• What's my eligibility?\n"
                "• My skills / resume / projects\n"
                "• Show my CGPA / grades\n\n"
                "📊 **Statistics & Analytics**\n"
                "• Placement statistics\n"
                "• Branch-wise analytics\n"
                "• Deadlines\n\n"
                "👨‍💼 **Admin/TPO Commands** (admins only)\n"
                "📌 **Student Details:**\n"
                "• View student [name] - Get specific student details\n"
                "• Show student profile [username]\n"
                "• Get individual student info\n\n"
                "📌 **Student Filtering:**\n"
                "• Filter students by CGPA > 8\n"
                "• Show students from CSE / ECE branch\n"
                "• Students with no backlog\n"
                "• Students with backlogs\n"
                "• Show top 10 students\n\n"
                "📌 **Lists & Reports:**\n"
                "• List students\n"
                "• Show applicants\n"
                "• Student analytics overview\n\n"
                "Just ask naturally - I understand!"
            ),
            "success": True,
            "context": "help",
            "intent": "help"
        }

    @staticmethod
    def _ok(answer, context, intent=None):
        """Return success response."""
        return {
            "answer": answer,
            "success": True,
            "context": context,
            "intent": intent or context,
        }

    @staticmethod
    def _err(answer):
        """Return error response."""
        return {
            "answer": answer,
            "success": False,
            "context": "error",
            "intent": None,
        }

    @staticmethod
    def _denied(answer):
        """Return permission denied response."""
        return {
            "answer": answer,
            "success": False,
            "context": "permission_denied",
            "intent": None,
        }
