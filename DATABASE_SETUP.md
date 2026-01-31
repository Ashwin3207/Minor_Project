# Online Database Setup Guide

This guide helps you move your TPC Portal from SQLite to a cloud-hosted PostgreSQL database.

## Overview

Your application is now configured to support both:
- **Local Development**: SQLite (default)
- **Production**: PostgreSQL (cloud-hosted)

## Quick Start: Deploy to Railway (Recommended - Free)

### Step 1: Sign Up for Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub/Google
3. Create a new project

### Step 2: Create PostgreSQL Database
1. Click "New" → "Database" → "PostgreSQL"
2. Railway will create a PostgreSQL instance
3. Copy your `DATABASE_URL` (looks like: `postgresql://user:password@host:port/database`)

### Step 3: Update Environment Variables
1. In your Railway project, go to "Variables"
2. Add these variables:
   ```
   DATABASE_URL = postgresql://user:password@host:port/database
   SECRET_KEY = your-very-secret-key-here
   FLASK_ENV = production
   ```

### Step 4: Deploy Your App
1. Connect your GitHub repository to Railway
2. Railway automatically detects Flask and deploys
3. Your app now runs with PostgreSQL!

---

## Alternative: Deploy to Render (Also Free)

### Step 1: Create PostgreSQL Database
1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Click "New" → "PostgreSQL"
4. Fill in details (free tier available)
5. Copy the `External Database URL`

### Step 2: Deploy Flask App
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Set Environment:
   ```
   FLASK_ENV: production
   SECRET_KEY: your-very-secret-key-here
   DATABASE_URL: [paste PostgreSQL URL here]
   ```
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn run:app`

---

## Local Development with PostgreSQL (Optional)

If you want to test locally with PostgreSQL:

### Install PostgreSQL
- **Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- **macOS**: `brew install postgresql`
- **Linux**: `sudo apt install postgresql`

### Create Local Database
```bash
# Start PostgreSQL
# (varies by OS, often starts automatically)

# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE tpc_portal;
CREATE USER tpc_user WITH PASSWORD 'your_password';
ALTER ROLE tpc_user SET client_encoding TO 'utf8';
ALTER ROLE tpc_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE tpc_user SET default_transaction_deferrable TO on;
ALTER ROLE tpc_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE tpc_portal TO tpc_user;
\q
```

### Set Local Environment Variable
Create a `.env` file in your project root:
```
DATABASE_URL=postgresql://tpc_user:your_password@localhost:5432/tpc_portal
FLASK_ENV=development
SECRET_KEY=dev-key-local
```

### Run Application
```bash
# Activate virtual environment
source env/Scripts/activate  # Windows
# or
source env/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run migrations
flask db upgrade

# Start application
python run.py
```

---

## Running Database Migrations

After connecting to PostgreSQL, initialize your database schema:

### First Time Setup
```bash
# Activate environment
source env/Scripts/activate

# Create migration folder (if not exists)
flask db init

# Generate migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### Future Changes
```bash
# After modifying models.py
flask db migrate -m "Add new field to User model"
flask db upgrade
```

---

## Data Migration (SQLite → PostgreSQL)

To migrate existing data from SQLite to PostgreSQL:

### Option 1: Using Python Script (Simple)
Create `migrate_data.py`:
```python
from app import create_app, db
from config import config
import os

# Export from SQLite
app_sqlite = create_app('development')
with app_sqlite.app_context():
    from app.models import User, StudentProfile, Opportunity, Application
    users = User.query.all()
    print(f"Found {len(users)} users to migrate")

# Create PostgreSQL app
os.environ['DATABASE_URL'] = 'postgresql://user:password@host:port/database'
app_pg = create_app('production')
with app_pg.app_context():
    # Data transfer happens here
    for user in users:
        new_user = User(
            username=user.username,
            email=user.email,
            password=user.password,
            role=user.role
        )
        db.session.add(new_user)
    db.session.commit()
    print("Migration complete!")
```

Run: `python migrate_data.py`

### Option 2: Using pg_dump (Advanced)
```bash
# Export SQLite to SQL file
sqlite3 tpc_portal.db .dump > sqlite_dump.sql

# Clean file and import to PostgreSQL
psql -U tpc_user -d tpc_portal < sqlite_dump.sql
```

---

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Flask session encryption | `randomstringhere123!@#` |
| `FLASK_ENV` | Application mode | `production` or `development` |
| `UPLOAD_FOLDER` | File storage location | `/uploads` |

---

## Troubleshooting

### "Module psycopg2 not found"
```bash
pip install psycopg2-binary
# or if issues: pip install --upgrade psycopg2-binary
```

### "Lost connection to database"
- Check DATABASE_URL is correct
- Ensure credentials are valid
- Check firewall allows connection
- Check pool_recycle in config.py

### "Column not found" error
- Run migrations: `flask db upgrade`
- Check migrations folder is up to date

### Can't connect to Railway/Render DB
- Copy full DATABASE_URL from provider
- Ensure URL starts with `postgresql://`
- Check no spaces or special chars

---

## Database Performance Tips

1. **Add Indexes** to frequently queried columns (already done in models)
2. **Connection Pooling** configured automatically in config.py
3. **Monitor Resource Usage** in Railway/Render dashboard
4. **Regular Backups** - Enable in database provider settings

---

## Next Steps

1. Choose hosting (Railway/Render recommended)
2. Create PostgreSQL database
3. Set environment variables
4. Deploy application
5. Run migrations: `flask db upgrade`
6. Monitor application at your provider's dashboard

Need help? Check your hosting provider's documentation or Flask-SQLAlchemy docs.
