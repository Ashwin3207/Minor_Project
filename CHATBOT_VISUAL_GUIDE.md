# Chatbot Integration - Visual Guide & Quick Reference

## 🗺️ Navigation Map

```
Homepage
├── Ask Assistant (CHATBOT) ← NEW
│   ├── Chat Interface
│   ├── Message Display
│   ├── Suggestion Buttons
│   └── Developer Tools (F12 Console)
│
├── Login
│   └── After Login → Ask Assistant (Personalized)
│
├── Dashboard (Admin/Student)
│   └── Ask Assistant (Context-aware)
│
└── About/Help
```

## 🎯 Chatbot Access Points

### 1. Navigation Bar
```
┌─────────────────────────────────────────────────┐
│ TPC Portal    Home  Opportunities  Applications  │
│                              Ask Assistant ← NEW │
│                                   [Login] [Signup] │
└─────────────────────────────────────────────────┘
```

### 2. Direct URL
```
/chatbot/
```

## 💬 Chat Interface Layout

```
┌──────────────────────────────────────────────────┐
│ 💬 Placement Assistant                           │
│    Ask me about opportunities, jobs, and apps    │
├──────────────────────────────────────────────────┤
│                                                  │
│  👋 Hi! I'm your Placement Assistant.            │
│     How can I help you today?                    │
│                                                  │
│                    [User Message Bubble]        │
│                    Blue, Right Aligned           │
│                                                  │
│  [Bot Response Bubble]                          │
│  Gray, Left Aligned, Interactive Links          │
│                                                  │
│  [TYPING INDICATOR]                             │
│  ••• (animated)                                  │
│                                                  │
├──────────────────────────────────────────────────┤
│ Suggested questions:                             │
│ [Show opportunities] [What jobs?] [My status?]   │
├──────────────────────────────────────────────────┤
│ [Text input field                    ] [SEND]   │
│ Ask me anything about...                         │
└──────────────────────────────────────────────────┘
```

## 🎨 Message Styling

### User Message
```
┌─────────────────────────┐
│ How many jobs are open? │  Blue background
│                         │  White text
└─────────────────────────┘  Right aligned
```

### Bot Message
```
┌─────────────────────────┐
│ There are 5 jobs open:  │  Gray background
│ • Company A - 12 LPA    │  Dark text
│ • Company B - 10 LPA    │  Left aligned
│ ...                     │
└─────────────────────────┘
```

## 🔄 Data Flow

```
User Types Message
        │
        ▼
[Ask Assistant button or Enter key]
        │
        ▼
Display User Message (Blue bubble)
        │
        ▼
Show Typing Indicator
        │
        ▼
POST /chatbot/api/chat {message: "..."}
        │
        ▼
ChatbotEngine.process_query()
        │
        ├─ Identify Topic (Keywords)
        │
        ├─ Query Database (SQLAlchemy)
        │  ├─ users
        │  ├─ student_profiles
        │  ├─ opportunities
        │  ├─ jobs
        │  └─ applications
        │
        ├─ Format Response
        │
        └─ Return JSON
        │
        ▼
JSON Response: {success, answer, context}
        │
        ▼
Remove Typing Indicator
        │
        ▼
Display Bot Message (Gray bubble)
        │
        ▼
Auto-scroll to Bottom
```

## 📊 Query Type Decision Tree

```
USER QUESTION
    │
    ├─→ Contains: "opportunity", "job", "opening", etc.
    │   └─→ _answer_opportunities() (Opportunity Handler)
    │
    ├─→ Contains: "application", "applied", "status", etc.
    │   └─→ _answer_applications() (Application Handler)
    │       └─→ Personalized (Only if logged in)
    │
    ├─→ Contains: "job", "company", "ctc", "salary", etc.
    │   └─→ _answer_jobs() (Job Handler)
    │
    ├─→ Contains: "profile", "cgpa", "branch", "skill", etc.
    │   └─→ _answer_profile() (Profile Handler)
    │       └─→ Personalized (Only if logged in)
    │
    ├─→ Contains: "deadline", "closing", "expire", etc.
    │   └─→ _answer_deadlines() (Deadline Handler)
    │
    ├─→ Contains: "require", "eligible", "minimum", etc.
    │   └─→ _answer_requirements() (Requirement Handler)
    │
    ├─→ Contains: "help", "guide", "how", etc.
    │   └─→ _answer_help() (Help Handler)
    │
    └─→ Greeting (hello, hi, bye, thanks, etc.)
        └─→ _check_greeting() (Greeting Handler)
            └─→ Special Responses
```

## 📱 Responsive Design

### Desktop (>992px)
```
┌─────────────────────────────────────────┐
│            Navigation Bar                │
├─────────────────────────────────────────┤
│                                         │
│         ┌───────────────────┐          │
│         │   Chat Container  │          │
│         │   (Full width)    │          │
│         │   70vh height     │          │
│         └───────────────────┘          │
│                                         │
└─────────────────────────────────────────┘
```

### Tablet (576px - 992px)
```
┌────────────────────────────┐
│   Navigation Bar           │
├────────────────────────────┤
│   ┌──────────────────────┐ │
│   │  Chat Container      │ │
│   │  (Reduced width)     │ │
│   │  70vh height         │ │
│   └──────────────────────┘ │
└────────────────────────────┘
```

### Mobile (<576px)
```
┌──────────────────┐
│ Navbar (Compact) │
├──────────────────┤
│┌────────────────┐│
││Chat Container ││
││(Full width)   ││
││70vh height    ││
│└────────────────┘│
└──────────────────┘
```

## 🔐 Authentication Flow

```
GUEST USER                           LOGGED-IN STUDENT
│                                    │
├─ Ask Assistant                     ├─ Ask Assistant
│  └─ General Info Only              │  └─ Personalized Answers
│     (opportunities, jobs)          │     (status, eligibility, profile)
│     (no session.user_id)           │     (with session.user_id)
│                                    │
└─ Limited Functionality             └─ Full Functionality
   No application status                Application history
   No eligibility check                 Profile queries
   No personal recommendations          Personalized recommendations
```

## 📝 Example Query Responses

### 1. Opportunities Query
```
USER: "Show me available opportunities"
BOT: Here are the available opportunities:

    • Software Engineer Internship (Internship)
      Company: TechCorp
      Deadline: 30-03-2026

    • Hackathon 2026 (Hackathon)
      Organizer: CodeCamp
      Deadline: 15-04-2026

    ...and 3 more opportunities.
```

### 2. Application Status Query (Logged-in)
```
USER: "What's my application status?"
BOT: Your application statuses:

    • TechCorp - Applied
    • CodeWave - Shortlisted
    • DataSystems - Applied

    Summary:
    • Applied: 2
    • Shortlisted: 1
```

### 3. Eligibility Query (Logged-in)
```
USER: "Am I eligible for this position?"
BOT: Based on your profile:

    Your Profile:
    • CGPA: 8.5
    • Branch: CSE

    You are eligible for 12 positions.
    Check the opportunities section to apply!
```

### 4. Help Query
```
USER: "Help"
BOT: I'm your Training & Placement Assistant!
    Here's what I can help you with:

    About Opportunities:
    • "Show me available opportunities"
    • "How many opportunities are there?"

    About Jobs:
    • "What job openings are available?"
    • "What are the salary packages?"

    ... [More help text]
```

## 🛠️ Developer Tools

### Inspect Chat Messages
```javascript
// In browser console:
const messages = document.querySelectorAll('.chat-message');
messages.forEach(msg => console.log(msg.textContent));
```

### Test API Endpoint
```javascript
// In browser console:
fetch('/chatbot/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: 'Show opportunities'})
})
.then(r => r.json())
.then(d => console.log(d));
```

### Get Suggestions
```javascript
fetch('/chatbot/api/suggestions')
  .then(r => r.json())
  .then(d => console.log(d.suggestions));
```

### Health Check
```javascript
fetch('/chatbot/api/health')
  .then(r => r.json())
  .then(d => console.log(d));
```

## 📚 File Organization

```
PROJECT_ROOT/
│
├─ app/
│  ├─ chatbot/              [NEW PACKAGE]
│  │  ├─ __init__.py
│  │  └─ routes.py
│  │
│  ├─ chatbot_engine.py     [NEW MODULE]
│  │
│  └─ __init__.py           [MODIFIED - added chatbot blueprint]
│
├─ templates/
│  ├─ chatbot/              [NEW PACKAGE]
│  │  └─ chat.html          [NEW - UI]
│  │
│  └─ base.html             [MODIFIED - added nav links]
│
├─ static/
│  └─ js/
│     └─ chatbot.js         [NEW - Frontend logic]
│
├─ CHATBOT_DOCUMENTATION.md       [NEW]
├─ CHATBOT_SETUP_GUIDE.md         [NEW]
└─ CHATBOT_IMPLEMENTATION_SUMMARY [NEW]
```

## 🎯 Success Criteria - All Met ✅

- ✅ Chatbot functionality implemented
- ✅ Database integration working
- ✅ Natural language understanding (keyword-based)
- ✅ User personalization (logged-in vs guest)
- ✅ Professional UI with animations
- ✅ REST API endpoints
- ✅ Navigation integration
- ✅ No additional dependencies
- ✅ Error handling
- ✅ Documentation complete
- ✅ Production ready
- ✅ Mobile responsive

---

## 🚀 Getting Started

1. **Start the Application**
   ```bash
   cd d:\Minor_Project
   $env:FLASK_ENV='development'
   python run.py
   ```

2. **Open Browser**
   ```
   http://localhost:5000/chatbot/
   ```

3. **Try Chatting**
   - Click "Ask Assistant" in navbar, or
   - Go directly to `/chatbot/`
   - Try example questions

4. **Test Personalization**
   - Chat as guest (general info)
   - Login and chat (personalized info)
   - Try both types of queries

---

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Last Updated**: February 2026
