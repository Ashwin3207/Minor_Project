╔════════════════════════════════════════════════════════════════════════════════╗
║                   OPPORTUNITIES & JOBS APPLICATION SYSTEM                       ║
║                          ✓ FULLY IMPLEMENTED & WORKING                          ║
╚════════════════════════════════════════════════════════════════════════════════╝

CURRENT DATABASE STATUS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ 5 Students registered
  ✓ 1 Job posted
  ✓ 4 Opportunities created
  ✓ 2 Active applications from students

═════════════════════════════════════════════════════════════════════════════════

COMPLETE STUDENT APPLICATION FLOW:
══════════════════════════════════════════════════════════════════════════════

1. STUDENT LOGS IN
   └─ Route: /auth/login
   └─ Creates session with user_id and role='Student'

2. STUDENT COMPLETES PROFILE
   └─ Route: /student/profile
   └─ Saves: CGPA, Branch, Skills, Has Backlog status
   └─ Required before applying to any job

3. STUDENT BROWSES JOBS
   └─ Route: /student/apply (if jobs exist)
   └─ Shows all posted jobs with:
      • Company name, CTC, Min CGPA, Branches, Deadline
      • Eligibility status (Green=Eligible, Red=Not Eligible, Gray=Already Applied)
      • View button to see full job description
      • Apply button (visible only if eligible)

4. STUDENT APPLIES FOR A JOB
   └─ Route: /student/apply (POST with job_id)
   └─ Validations:
      • Profile must be completed
      • CGPA >= job's min_cgpa
      • Branch must be in allowed_branches
      • No active backlogs
      • Application deadline not passed
      • Not already applied
   └─ Database saved:
      └─ student_id
      └─ job_id
      └─ status = 'Applied'
      └─ applied_at = current timestamp
      └─ updated_at = current timestamp

5. STUDENT BROWSES OPPORTUNITIES
   └─ Route: /student/opportunities
   └─ Shows all opportunities grouped by type:
      • Jobs
      • Internships
      • Sessions
      • Hackathons
      • Bootcamps
      • Seminars
   └─ Each opportunity shows:
      • Title, Organizer, Type, Description
      • Eligibility status badges
      • Key details (CTC, CGPA, Branches, Deadline)
      • View Details + Apply Now buttons

6. STUDENT APPLIES FOR OPPORTUNITY
   └─ Route: /student/opportunity/<id>/apply (POST)
   └─ Same validations as job applications
   └─ Database saved:
      └─ student_id
      └─ opportunity_id
      └─ status = 'Applied'
      └─ applied_at = current timestamp

7. STUDENT VIEWS MY APPLICATIONS
   └─ Route: /student/applications
   └─ Shows all submitted applications:
      • Company/Opportunity name
      • Application type (Job/Opportunity)
      • Status badge
      • Applied date/time
      • View button to see details
      • Pagination for many applications

═════════════════════════════════════════════════════════════════════════════════

COMPLETE ADMIN MANAGEMENT FLOW:
═══════════════════════════════════════════════════════════════════════════════

1. ADMIN LOGS IN
   └─ Route: /admin/dashboard
   └─ Sees quick stats:
      • Total students
      • Total jobs posted
      • Total applications
      • Students placed (Selected status)
      • Placement rate %

2. ADMIN POSTS A NEW JOB
   └─ Route: /admin/post_job (GET/POST)
   └─ Form fields:
      • Company Name (required)
      • Job Description (required)
      • CTC (required)
      • Min CGPA (required)
      • Allowed Branches (required)
      • Deadline (required)
   └─ Job saved to database
   └─ Automatically becomes available to eligible students

3. ADMIN MANAGES POSTED JOBS
   └─ Route: /admin/view_jobs
   └─ Shows all jobs in table:
      • Company Name
      • CTC
      • Min CGPA
      • Deadline (with expired indicator)
      • Applicant count badge
      • Posted date
      • Actions: View Applicants button
   └─ Pagination support for many jobs

4. ADMIN VIEWS JOB APPLICANTS
   └─ Route: /admin/job_applicants/<job_id>
   └─ Displays:
      • Job details at top
      • Summary stats (Total, Applied, Shortlisted, Selected, Rejected)
      • Filter by status dropdown
      • Table of all applicants:
         - Username, Email, CGPA, Branch
         - Application date
         - Current status with color coding
         - View Profile button
         - Action buttons (Shortlist/Select/Reject)

5. ADMIN UPDATES APPLICATION STATUS
   └─ Route: /admin/confirm_application/<app_id> (POST)
   └─ Available statuses:
      • Applied → Can shortlist or reject
      • Shortlisted → Can select or reject
      • Selected/Rejected → No more actions
   └─ Status update is:
      • Saved immediately to database
      • Shown with updated_at timestamp
      • Visible to student in their applications list

6. ADMIN MANAGES OPPORTUNITIES (NEW!)
   └─ Route: /admin/opportunities
   └─ Shows all created opportunities:
      • Title, Type, Organizer
      • Description preview
      • CTC, Min CGPA, Branches, Deadline (for Jobs/Internships)
      • Edit, Delete buttons
      • NEW: View Applicants button
   └─ Create new opportunity by type

7. ADMIN VIEWS OPPORTUNITY APPLICANTS (NEW!)
   └─ Route: /admin/opportunity_applicants/<opp_id>
   └─ Similar to job applicants view:
      • Opportunity details at top
      • Summary stats
      • Filter by status
      • Applicants table
      • Status update actions
      • Resume download

═════════════════════════════════════════════════════════════════════════════════

ELIGIBILITY VALIDATION LOGIC:
═══════════════════════════════════════════════════════════════════════════════

When student applies for Job/Internship/Opportunity:

✓ Student must have a profile (CGPA, Branch, etc.)
✓ Student CGPA >= Min CGPA required
✓ Student Branch must be in Allowed Branches list
✓ Student must not have any backlogs
✓ Current date/time must be before deadline
✓ Student must not have already applied

If any check fails: Application rejected with error message
If all checks pass: Application approved and saved

═════════════════════════════════════════════════════════════════════════════════

DATABASE SCHEMA:
══════════════════════════════════════════════════════════════════════════════

APPLICATIONS TABLE:
  id                    INTEGER PRIMARY KEY
  student_id            INTEGER NOT NULL FK(users.id)
  job_id                INTEGER FK(jobs.id)          [Null for opportunities]
  opportunity_id        INTEGER FK(opportunities.id) [Null for jobs]
  status                VARCHAR(30) DEFAULT 'Applied'
  applied_at            DATETIME (when applied)
  updated_at            DATETIME (when status changed)

  Unique Constraints:
    (student_id, job_id) - prevent duplicate job applications
    (student_id, opportunity_id) - prevent duplicate opportunity applications

JOBS TABLE:
  id, company_name, job_description, ctc
  min_cgpa, allowed_branches, deadline, created_at

OPPORTUNITIES TABLE:
  id, title, type, organizer, company_name
  description, ctc, min_cgpa, allowed_branches
  deadline, date, mode, created_at

═════════════════════════════════════════════════════════════════════════════════

QUICK REFERENCE - ROUTES:
═════════════════════════════════════════════════════════════════════════════════

STUDENT ROUTES:
  GET  /student/apply                          Browse/filter jobs
  POST /student/apply?job_id=X                 Apply for a job
  GET  /student/opportunities                  Browse all opportunities
  GET  /student/opportunity/<id>               View opportunity details
  POST /student/opportunity/<id>/apply         Apply for opportunity
  GET  /student/applications                   My applications list

ADMIN ROUTES:
  GET  /admin/dashboard                        Admin dashboard
  GET  /admin/post_job                         Post new job form
  POST /admin/post_job                         Save new job
  GET  /admin/view_jobs                        View all posted jobs
  GET  /admin/job_applicants/<id>              View job applicants
  POST /admin/confirm_application/<id>         Update app status (jobs)
  GET  /admin/opportunities                    Manage opportunities
  GET  /admin/opportunity_applicants/<id>      View opp applicants
  POST /admin/confirm_opportunity_application  Update app status (opps)

═════════════════════════════════════════════════════════════════════════════════

TESTING THE SYSTEM:
═════════════════════════════════════════════════════════════════════════════════

1. Start the server: python run.py
2. Open browser: http://localhost:5000

3. TEST STUDENT FLOW:
   a. Login as student (22151144008 / student123)
   b. Go to profile page - verify data is there
   c. Click "Browse More Opportunities"
   d. See jobs and opportunities with eligibility badges
   e. Click "Apply Now" on an eligible job
   f. Check "My Applications" - see the new application

4. TEST ADMIN FLOW:
   a. Login as admin (admin / admin123)
   b. Go to dashboard - see stats
   c. Click "View Jobs & Applicants"
   d. Click "View Applicants" on a job
   e. See the student applications
   f. Click "Shortlist", "Select", or "Reject"
   g. See status updated in the table

═════════════════════════════════════════════════════════════════════════════════

✓ SYSTEM COMPLETE AND READY FOR USE
✓ ALL FEATURES IMPLEMENTED
✓ DATABASE SCHEMA UPDATED
✓ ROUTES REGISTERED
✓ TEMPLATES CREATED
✓ VALIDATIONS IN PLACE

═════════════════════════════════════════════════════════════════════════════════
