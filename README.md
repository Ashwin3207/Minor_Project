# TPC Portal - Training & Placement Cell Management System

A comprehensive Flask-based web application for managing training and placement activities within educational institutions. The system provides role-based access control for multiple stakeholders including students, TPO (Training and Placement Officer), HOD (Head of Department), principals, corporate recruiters, and administrators.

## Features

### Core Functionalities
- **Role-Based Access Control (RBAC)**: Distinct dashboards and features for different user roles
  - Students: Browse opportunities, apply for placements, view results
  - TPO: Manage opportunities, coordinate placements, generate reports
  - HOD: Approve opportunities, oversee departmental placements
  - Principal: System oversight and high-level analytics
  - Corporate: Post opportunities, manage applications
  - Admin: System management and user administration

- **Opportunity Management**: Create, post, and manage recruitment opportunities
- **Application Processing**: End-to-end application workflow with approval stages
- **Intelligent Chatbot**: Keyword-based, database-aware system with 25+ specialized handlers for instant query resolution
- **Database Context Integration**: Chatbot understands institutional data for contextual responses
- **CSV Export**: Generate reports and data exports
- **Responsive Dashboard**: Real-time analytics and metrics visualization

### Technology Stack
- **Backend**: Flask 3.0.3
- **Database**: SQLAlchemy ORM with PostgreSQL support
- **Database Migrations**: Flask-Migrate with Alembic
- **Authentication**: Werkzeug password hashing
- **API Client**: Requests library
- **Production Server**: Gunicorn
- **Environment Management**: Python-dotenv

## Project Structure

```
.
├── app/                          # Main application package
│   ├── models.py                # Database models (User, Opportunity, Application, etc.)
│   ├── auth/                    # Authentication & authorization
│   ├── student/                 # Student role features
│   ├── tpo/                     # TPO role features
│   ├── hod/                     # HOD role features
│   ├── principal/               # Principal role features
│   ├── corporate/               # Corporate recruiter features
│   ├── admin/                   # Administrator features
│   ├── main/                    # Main/shared routes
│   ├── chatbot/                 # AI chatbot system
│   │   ├── chatbot_engine.py    # Core chatbot logic
│   │   ├── chatbot_handlers.py  # Intent handlers (25+ specialized handlers)
│   │   ├── chatbot_intent_router.py # Intent detection and routing
│   │   ├── chatbot_security.py  # Security & validation
│   │   └── tpc_system_prompt.py # System prompt configuration
│   └── __init__.py              # App factory and blueprint registration
├── templates/                    # HTML templates (Jinja2)
├── static/                       # Static assets (CSS, JS, images)
├── migrations/                   # Database migration scripts
├── config.py                     # Configuration management
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
└── runtime.txt                   # Python version specification
```

## Prerequisites

- Python 3.8 or higher
- PostgreSQL (for production) or SQLite (for development)
- pip or pip3

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Minor_Project
```

### 2. Create Virtual Environment
```bash
# On Windows
python -m venv env
env\Scripts\activate

# On macOS/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the project root (see `.env.example` for reference):
```bash
cp .env.example .env
```

Update `.env` with your configuration:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///tpc_portal_dev.db  # or PostgreSQL URL for production
```

### 5. Initialize Database
```bash
python init_db.py
```

Or use Flask-Migrate:
```bash
flask db upgrade
```

## Running the Application

### Development Mode
```bash
python run.py
```

The application will be accessible at `http://localhost:5000`

### Production Mode
```bash
FLASK_ENV=production gunicorn run:app
```

### Using Flask CLI
```bash
flask run --debug
```

## API & Features Documentation

### Authentication Routes
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `POST /auth/register` - New user registration

### Student Routes
- `GET /student/dashboard` - Student dashboard
- `GET /student/opportunities` - Browse opportunities
- `POST /student/apply/<opportunity_id>` - Apply for opportunity
- `GET /student/applications` - View applications

### TPO Routes
- `GET /tpo/dashboard` - TPO dashboard
- `POST /tpo/opportunity/create` - Create new opportunity
- `GET /tpo/opportunity/<id>/edit` - Edit opportunity
- `GET /tpo/reports` - Generate reports

### HOD Routes
- `GET /hod/dashboard` - HOD dashboard
- `GET /hod/approvals` - Pending approvals
- `POST /hod/approve/<opportunity_id>` - Approve opportunity

### Chatbot API
- `POST /chatbot/query` - Submit query to chatbot
- `GET /chatbot/history` - View query history

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - Manage users
- `GET /admin/system-logs` - View system logs

## Configuration

Edit `config.py` to customize application settings:
- Database connection strings
- Secret key for sessions
- Feature flags
- Chatbot settings
- Mail configuration

### Environment Variables
- `FLASK_ENV`: Set to `development` or `production`
- `SECRET_KEY`: Secret key for session management
- `DATABASE_URL`: Database connection URL
- Additional variables documented in `.env.example`

## Database Migrations

Create a new migration after model changes:
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## Testing

Run application tests:
```bash
python -m pytest
```

For specific test file:
```bash
python -m pytest tests/test_auth.py
```

## Deployment

### Using Render.com
```bash
# Push to main branch
git push origin main

# Deployment is automatically triggered based on render.yaml
```

See `render.yaml` for deployment configuration.

### Using Heroku
```bash
heroku create your-app-name
git push heroku main
```

## Troubleshooting

### Database Issues
```bash
# Reset database (development only)
rm tpc_portal_dev.db
python init_db.py
```

### Import Errors
Ensure you're in the virtual environment:
```bash
# Windows
env\Scripts\activate

# macOS/Linux
source env/bin/activate
```

### Port Already in Use
```bash
# Change port in run.py or use:
python run.py --port 5001
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature description'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a Pull Request

## Security Considerations

- Never commit `.env` files to version control
- Use strong SECRET_KEY values in production
- Enable HTTPS in production
- Validate and sanitize all user inputs
- Implement CSRF protection for forms
- Use parameterized queries to prevent SQL injection
- Regularly update dependencies

## Performance Optimization

- Database query caching enabled for student dashboards
- Indexed queries on frequently searched columns (user_id, opportunity_id)
- Lazy loading for related entities
- CSV export optimized for large datasets

## License

This project is proprietary software for the Training & Placement Cell.

## Support

For issues, features, or questions:
- Email: amathura01@gmail.com
- Internal Portal: [Admin Dashboard](http://localhost:5000/admin)

## Authors

Development Team - Training & Placement Cell Portal Project

---

**Last Updated**: June 2026

For detailed implementation information, refer to the `TECHNICAL_INTEGRATION_GUIDE.md` in project documentation.
