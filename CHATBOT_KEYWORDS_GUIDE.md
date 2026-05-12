# 🤖 Chatbot Keywords & Features Guide

## Overview
The TPC Portal chatbot now includes comprehensive keyword support for TPO/Admin to view individual student details and perform advanced analytics queries.

---

## 📌 NEW FEATURES FOR TPO/ADMIN

### 1. **View Individual Student Details**
**Keywords:**
- "View student [name]"
- "Show student [name]"
- "Student details [username]"
- "Get student [name]"
- "Student info [name]"
- "Student profile [name]"
- "Individual student [name]"

**What it does:**
- Displays complete student profile including:
  - Personal information (username, email)
  - Academic details (CGPA, branch, 10th/12th percentage, backlogs)
  - Professional information (skills, internships, NPTEL, FYP)
  - Resume upload status
  - Application summary (total applied, shortlisted, selected, rejected)

**Example queries:**
```
"View student John"
"Show student profile for gaurav"
"Get individual student details - akshay"
"Student info: priya"
```

---

### 2. **Filter Students by CGPA**
**Keywords:**
- "Filter students by CGPA > [number]"
- "Show students with CGPA above [number]"
- "CGPA greater than [number]"
- "Students with CGPA >= [number]"

**What it does:**
- Lists all students meeting the CGPA threshold
- Displays username, email, branch, and CGPA in table format
- Sorted by CGPA in descending order

**Example queries:**
```
"Filter students by CGPA > 8"
"Show students with CGPA above 8.5"
"CGPA greater than 7.5"
"Students with CGPA >= 9"
```

---

### 3. **Filter Students by Branch**
**Keywords:**
- "Show students from [branch]"
- "Filter students by [branch]"
- "Students in [branch] branch"
- "List [branch] department students"
- "Branch-wise students: [branch]"

**Supported branches:**
- CSE (Computer Science & Engineering)
- ECE (Electronics & Communication Engineering)
- ME (Mechanical Engineering)
- Civil
- Electrical
- Electronics
- IT (Information Technology)

**Example queries:**
```
"Show students from CSE"
"Filter students by ECE"
"List ME department students"
"Students in IT branch"
```

---

### 4. **Filter by Backlog Status**
**Keywords:**
- "Show students with no backlog"
- "Students without backlog"
- "Clean records"
- "Show students with backlogs"
- "Students with active backlogs"

**What it does:**
- Lists students with or without backlogs
- Displays username, email, branch, and CGPA
- Helps identify eligible candidates

**Example queries:**
```
"Show students with no backlog"
"Students without backlogs"
"Show all students with backlogs"
"Filter clean records"
```

---

### 5. **View Top Performers**
**Keywords:**
- "Show top [number] students"
- "Top performers"
- "Best students"
- "Top 10 students"
- "High performers"

**What it does:**
- Lists top-performing students by CGPA
- Displays rank, username, branch, and CGPA
- Default shows top 10, but can specify any number

**Example queries:**
```
"Show top 10 students"
"Top 5 performers"
"Best 15 students"
"High performers list"
```

---

### 6. **Student Analytics Overview**
**Keywords:**
- Just ask for any filter without specifying details
- "Show me student analytics"
- "Analytics overview"
- "Student statistics"

**What it does:**
- Overall statistics about students
- Total students and completed profiles
- Average CGPA and CGPA range
- Backlog distribution
- Branch-wise distribution
- Suggested commands for further queries

**Example queries:**
```
"Analytics overview"
"Student statistics"
"Show me the overview"
"Give analytics"
```

---

## 📋 EXISTING KEYWORDS (Still Available)

### Student Lists
- **"List students"** - Show all students with basic info
- **"Show students"** - Similar to list students
- **"All students"** - Full student listing

### Applicants
- **"Show applicants"** - Recent applications
- **"Who applied"** - List of applicants
- **"Applicants list"** - All applicants

### General Queries
- **"Show opportunities"** - List opportunities
- **"List companies"** - List recruiting companies
- **"Placement statistics"** - Placement stats
- **"Branch analytics"** - Branch-wise breakdown

---

## 🔒 Access Control

### Admin-Only Features:
All the following features require admin/TPO login:
- ✓ View individual student details
- ✓ Filter students by any criteria
- ✓ View top performers
- ✓ Access student analytics
- ✓ List applicants
- ✓ Filter by CGPA/branch/backlog

### Student Features (After Login):
- ✓ View own profile
- ✓ Check own applications
- ✓ Check eligibility
- ✓ View own skills, CGPA, etc.

### Public Features (No Login Required):
- ✓ Browse opportunities
- ✓ Check companies
- ✓ View deadlines
- ✓ General placement stats

---

## 📊 Command Examples by Use Case

### Use Case 1: Find High-CGPA Students for Premium Companies
```
"Show students with CGPA > 9"
"Filter students by CGPA >= 8.5"
"Top 20 students"
```

### Use Case 2: Get Students from Specific Branch
```
"Show students from CSE"
"Filter students by ECE"
"List IT department students"
```

### Use Case 3: View Eligible Candidates (No Backlogs)
```
"Show students with no backlog"
"Students without active backlogs"
"Filter clean records"
```

### Use Case 4: Get Details of Specific Student
```
"View student John"
"Show student profile for gaurav"
"Get individual student details - akshay"
"Student info: priya"
```

### Use Case 5: Get Overall Dashboard
```
"Analytics overview"
"Student statistics"
"Show student analytics"
```

---

## 🎯 Best Practices for TPO

1. **For Quick Overview:**
   - Start with "Analytics overview" to get the dashboard

2. **For Targeted Recruitment:**
   - Use CGPA filters + Branch filters combined
   - "Show students from CSE with CGPA > 8.5"

3. **For Pre-Interview Selection:**
   - View individual student details
   - Check academic background and skills

4. **For Placement Drive Planning:**
   - Use top performers list
   - Check backlog status to ensure eligibility

5. **For Data Export:**
   - Use filter commands and note down the lists
   - Can be exported to CSV from the system

---

## 📝 Tips & Tricks

### Natural Language Support
The chatbot understands various phrasings:
- "Show me students from CSE"
- "Filter by CSE branch"
- "List CSE department"
- "CSE students"
All work similarly!

### Combining Queries
While chatbot processes one query at a time, you can sequence them:
1. "Show top 10 students"
2. "View student John"
3. "Filter by CSE"

### Default Values
- Default CGPA threshold: 8.0
- Default top students shown: 10
- Can customize with specific numbers

---

## 🆘 Troubleshooting

### Issue: "Student not found"
**Solution:** Try different variations:
- Use full username
- Use email address
- Check spelling

### Issue: "No students found with CGPA > X"
**Solution:** Lower the threshold:
- Try "CGPA > 7" instead of "CGPA > 9"
- Use "Top 10 students" to see range

### Issue: "Only admins can view..."
**Solution:** Ensure you're logged in as Admin/TPO
- Check your login status
- Admin role is required for these features

---

## 📞 Support

For issues or feature requests, contact the system administrator or development team.

**Version:** 2.0 (Updated May 2026)
**Last Updated:** May 12, 2026
