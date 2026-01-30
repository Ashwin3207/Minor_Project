# Resume Upload & Management Feature

## Overview
Students can now upload, update, and manage their resumes directly through the portal. Admins can view and download student resumes when reviewing applications.

## Features Implemented

### 1. **Student Features**

#### Resume Upload Page (`/student/resume`)
- **File Upload**: Students can upload PDF, DOC, or DOCX files (max 16MB)
- **File Storage**: Resumes are stored in `uploads/student_{user_id}/` directory
- **Update**: Students can upload new resumes anytime (old ones are automatically replaced)
- **Download**: Students can download their own resume
- **Resume Tips**: Helpful guidelines for creating professional resumes

#### Profile Page Integration
- Resume status indicator on student profile page
- Quick link to upload/manage resume
- Shows whether resume is uploaded or not

### 2. **Admin Features**

#### View Student Resumes
- Admins can see resume links in student profile modals
- Direct download option for each student's resume
- Access from job applicants page

#### Download Route
- Route: `GET /admin/download-student-resume/<student_id>`
- Allows admins to download any student's resume

### 3. **Database**
- `StudentProfile.resume_link` field stores file path
- `updated_at` timestamp tracks when profile was last updated

## API Routes

### Student Routes
```
POST   /student/resume              - Upload resume
GET    /student/resume              - View resume page
GET    /student/download-resume     - Download own resume
```

### Admin Routes
```
GET    /admin/download-student-resume/<student_id>  - Download student resume
```

## File Structure

### Upload Directory
```
uploads/
├── student_1/
│   └── 20260130_174208_resume.pdf
├── student_2/
│   └── 20260130_174215_resume.docx
└── ...
```

### Configuration
```python
# config.py
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

## Security Features

1. **File Validation**
   - Only allows PDF, DOC, DOCX formats
   - File size limited to 16MB
   - Secure filename generation

2. **Access Control**
   - Students can only access their own resumes
   - Admins can download any student's resume
   - Resume routes protected with `@student_required` and `@admin_required` decorators

3. **File Storage**
   - Files stored outside public web root (in `uploads/` directory)
   - Unique filenames with timestamps to prevent collisions
   - User-specific folders for organization

## Error Handling

- File not found handling
- Invalid file type detection
- File size validation
- Directory creation if doesn't exist
- Old resume cleanup when new one is uploaded

## Templates

### Student Resume Page
- File: `templates/student/resume.html`
- Features:
  - Upload form with drag-and-drop support
  - Current resume status indicator
  - Download button for existing resume
  - Resume tips section
  - Back to profile link

### Profile Page Updates
- File: `templates/student/profile.html`
- Added resume status card with upload link

### Admin Job Applicants Page
- File: `templates/admin/job_applicants.html`
- Already shows resume links in student modals
- Works with new file storage system

## Usage

### For Students:
1. Go to "My Profile" → "Upload Resume" button
2. Choose a PDF, DOC, or DOCX file
3. Click "Upload"
4. View/download your resume anytime
5. Upload new resume to replace old one

### For Admins:
1. Go to "View Jobs" → Click job → View Applicants
2. Click "View Profile" on any applicant
3. See resume link in profile modal
4. Click to download student's resume

## Future Enhancements

- Resume templates/samples
- Resume preview functionality
- Multiple resume support (resume versioning)
- Resume parsing and skill extraction
- Resume score/quality feedback
- Email notifications on resume updates
