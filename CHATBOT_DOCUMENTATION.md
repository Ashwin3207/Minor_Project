# Chatbot Feature Documentation

## Overview

A comprehensive AI-powered chatbot assistant has been integrated into the Training & Placement Cell Portal. The chatbot can answer questions about:

- **Opportunities**: Available job openings, internships, hackathons, bootcamps, seminars, and sessions
- **Jobs**: Job listings with company information, CTC packages, and eligibility criteria
- **Applications**: User's personal application status and history
- **Student Profile**: CGPA, branch, skills, and profile management
- **Deadlines**: Upcoming opportunity and job deadlines
- **Requirements**: Eligibility criteria and skill requirements for various positions
- **General Help**: Guidance on using the platform

## Architecture

### Components

1. **Chatbot Engine** (`app/chatbot_engine.py`)
   - Core intelligence for processing natural language queries
   - Interfaces with the database to retrieve relevant information
   - Supports personalized responses based on user login status

2. **Chatbot Blueprint** (`app/chatbot/routes.py`)
   - Flask REST API endpoints for chat functionality
   - Endpoints:
     - `POST /chatbot/api/chat` - Process user messages
     - `GET /chatbot/api/suggestions` - Get suggested questions
     - `GET /chatbot/api/health` - Health check

3. **User Interface** (`templates/chatbot/chat.html`)
   - Modern chat interface built with Bootstrap 5
   - Real-time message display
   - Typing indicators for better UX

4. **Frontend Logic** (`static/js/chatbot.js`)
   - Handles chat interactions
   - Manages API communication
   - Implements message formatting and animations

## Key Features

### Natural Language Understanding

The chatbot uses keyword-based topic identification to understand user queries. It recognizes various phrasings for the same intent:

- "Show me available opportunities" ≈ "What opportunities are there?" ≈ "List all openings"
- "What's my status?" ≈ "Where are my applications?" ≈ "Check my applications"
- "Am I eligible?" ≈ "Can I apply?" ≈ "What are my requirements?"

### Personalization

- **Logged-in Users**: Get personalized responses including:
  - Personal application status
  - Eligibility information based on their profile
  - Recommendations based on their CGPA and branch
  
- **Guest Users**: Get general information about:
  - Available opportunities
  - Job listings
  - Platform features
  - Help and guidance

### Database Integration

The chatbot queries the following models:

```
User
├── StudentProfile (for CGPA, branch, skills)
└── Application (for application status)

Job (for job openings)

Opportunity (for all opportunity types)
```

## Usage Examples

### For Students

**Query**: "Show me available opportunities"
**Response**: Lists all opportunities with titles, types, companies, and deadlines

**Query**: "What's my application status?"
**Response**: Shows personalized application statuses with summary counts

**Query**: "Which positions am I eligible for?"
**Response**: Lists positions matching student's CGPA and branch

**Query**: "What are the upcoming deadlines?"
**Response**: Shows opportunities and jobs with approaching deadlines

### For All Users

**Query**: "How many job openings are available?"
**Response**: "There are X job openings currently."

**Query**: "What are the salary packages?"
**Response**: Lists all unique CTC packages offered

**Query**: "Tell me about this internship"
**Response**: Shows detailed information about requirements and details

## API Endpoints

### POST /chatbot/api/chat

Processes user messages and returns chatbot responses.

**Request**:
```json
{
  "message": "What are the available opportunities?"
}
```

**Response**:
```json
{
  "success": true,
  "answer": "Here are the available opportunities:\n\n...",
  "context": "opportunities"
}
```

### GET /chatbot/api/suggestions

Returns suggested questions based on login status.

**Response**:
```json
{
  "success": true,
  "suggestions": [
    "Show available opportunities",
    "What job openings are available?",
    "What's my application status?"
  ]
}
```

### GET /chatbot/api/health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "chatbot": "active"
}
```

## Implementation Details

### ChatbotEngine Class

**Methods**:

- `process_query(question, user_id=None)` - Main method to process user questions
- `_identify_topic(question_lower)` - Identifies the topic from keywords
- `_check_greeting(question)` - Handles greetings
- `_answer_opportunities()` - Handles opportunity-related queries
- `_answer_jobs()` - Handles job-related queries
- `_answer_applications()` - Handles application queries (personalized)
- `_answer_profile()` - Handles profile-related queries
- `_answer_deadlines()` - Handles deadline queries
- `_answer_requirements()` - Handles requirement queries
- `_answer_help()` - Provides help and guidance
- `_fallback_answer()` - Fallback response for unrecognized queries

### Message Formatting

Messages support:
- **Bold text**: `**text**` → `<strong>text</strong>`
- **Line breaks**: `\n` → `<br>`
- **Links**: URLs are automatically converted to clickable links

### UI Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Animations**: Smooth fade-in and slide-in animations for messages
- **Typing Indicators**: Shows that the chatbot is processing
- **Suggested Questions**: Quick buttons for common queries
- **Loading States**: Visual feedback during API calls

## Navigation Integration

The chatbot is accessible from:
1. **For Logged-in Users**: "Ask Assistant" link in the navigation bar
2. **For Guests**: "Ask Assistant" link available before login
3. **Direct URL**: `/chatbot/`

## Future Enhancements

Potential improvements:

1. **Advanced NLP**: Integrate with ML services for better understanding
2. **FAQ Database**: Create custom FAQ module for common questions
3. **Application Assistance**: Help students draft applications
4. **Resume Suggestions**: Provide resume improvement tips based on opportunities
5. **Notification Integration**: Alert users about upcoming deadlines
6. **Chat History**: Store and retrieve previous conversations
7. **Analytics**: Track common queries and user interactions
8. **Multi-language Support**: Support for regional languages
9. **Voice Input**: Speech-to-text for easier interaction
10. **Admin Dashboard**: Analytics about chatbot usage and effectiveness

## Testing

To test the chatbot:

1. View `/chatbot/` page
2. Try various queries like:
   - "Hello"
   - "Show available opportunities"
   - "What job openings are available?"
   - "What's my application status?" (when logged in)
   - "Help"

## File Structure

```
app/
├── chatbot/
│   ├── __init__.py
│   └── routes.py
├── chatbot_engine.py

templates/
└── chatbot/
    └── chat.html

static/
└── js/
    └── chatbot.js

CHATBOT_DOCUMENTATION.md (this file)
```

## Dependencies

The chatbot relies on:
- Flask (existing)
- SQLAlchemy database models (existing)
- Bootstrap 5 (existing)
- No additional PyPI packages required

## Code Quality

- Clean, documented code with docstrings
- Error handling for database queries
- Session-based authentication integration
- RESTful API design
- Responsive and accessible UI

## Security Considerations

- Query string sanitization to prevent XSS
- Session-based user identification (no sensitive data in requests)
- Database query builders prevent SQL injection
- CORS considerations handled through blueprint prefix

## Performance

- Lightweight queries using SQLAlchemy indexing
- Message processing is instantaneous
- No heavy computations
- Suitable for databases with thousands of opportunities and users

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Status**: Production Ready
