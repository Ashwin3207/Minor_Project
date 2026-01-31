# Online SQL Database Integration - Summary

## What Was Done ✅

Your Flask TPC Portal has been configured to use **online PostgreSQL database** instead of local SQLite. Here's what changed:

### 1. **Updated `config.py`**
- Added PostgreSQL support with automatic driver detection
- Environment variables control development (SQLite) vs production (PostgreSQL)
- Production config requires `DATABASE_URL` environment variable

### 2. **Updated `requirements.txt`**
- Added `psycopg2-binary==2.9.9` for PostgreSQL connectivity
- All dependencies needed for cloud deployment included

### 3. **Created Configuration Files**

| File | Purpose |
|------|---------|
| `DATABASE_SETUP.md` | Complete deployment guide (Railway, Render, local PostgreSQL) |
| `.env.example` | Template for environment variables |
| `Procfile` | Deployment instruction for hosting platforms |
| `runtime.txt` | Python version specification for cloud platforms |
| `setup_deployment.py` | Interactive setup script |

---

## How It Works

### Local Development (SQLite - Default)
```
No change needed - still uses SQLite locally
```

### Production (PostgreSQL - Online)
```
DATABASE_URL environment variable → PostgreSQL connection
Automatically detected and configured
```

---

## Quick Deployment Steps

### For Railway (Recommended - Free)
1. Sign up at [railway.app](https://railway.app)
2. Create PostgreSQL database
3. Set environment variables:
   - `DATABASE_URL` (from Railway)
   - `SECRET_KEY` (generate random string)
4. Connect GitHub repository - automatic deploy!

### For Render (Also Free)
1. Sign up at [render.com](https://render.com)
2. Create PostgreSQL database
3. Deploy Web Service with same environment variables
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn run:app`

---

## Database Configuration Overview

```python
# config.py handles both:

# Development (automatic SQLite)
DATABASE_URL = None → Uses local tpc_portal.db

# Production (PostgreSQL)
DATABASE_URL = "postgresql://..." → Uses cloud database
```

---

## Important Files

- **[config.py](config.py)** - Database URL configuration
- **[requirements.txt](requirements.txt)** - PostgreSQL driver included
- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - Detailed setup guide
- **[setup_deployment.py](setup_deployment.py)** - Interactive setup helper

---

## Database Schema

Your existing SQLAlchemy models work unchanged:
- `User` - Login credentials and roles
- `StudentProfile` - Academic info (CGPA, skills, etc.)
- `Job` / `Internship` / `Opportunity` - Posted positions
- `Application` - Student applications

All models automatically work with both SQLite and PostgreSQL!

---

## Migration to Cloud (Step-by-Step)

### Step 1: Get Database Credentials
```
From Railway or Render dashboard, copy the DATABASE_URL
Example: postgresql://user:pass@db.railway.app:5432/railway
```

### Step 2: Set Environment Variables
```
Create .env file:
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
FLASK_ENV=production
```

### Step 3: Run Setup Script
```bash
python setup_deployment.py
# Guides you through setup interactively
```

### Step 4: Deploy
```
Push to GitHub → Your hosting platform auto-deploys
Database migrations run automatically
```

---

## Testing Locally with PostgreSQL

Optional - test cloud database locally before deploying:

```bash
# Install PostgreSQL
# Create local database
# Update .env with PostgreSQL URL
# Run: python run.py
```

Full instructions in [DATABASE_SETUP.md](DATABASE_SETUP.md)

---

## Environment Variables Needed

| Variable | Where to Get |
|----------|-------------|
| `DATABASE_URL` | From Railway/Render PostgreSQL dashboard |
| `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_ENV` | Set to `production` for deployment |

---

## Troubleshooting

**"psycopg2 not found"**
```bash
pip install -r requirements.txt
```

**"Can't connect to database"**
- Verify DATABASE_URL is correct
- Check it starts with `postgresql://`
- Verify credentials are valid

**"Migrations failed"**
```bash
flask db upgrade
```

---

## Next Actions

1. ✅ Code is updated - you're ready!
2. Choose hosting: [Railway](https://railway.app) or [Render](https://render.com)
3. Create PostgreSQL database
4. Run `python setup_deployment.py` for interactive setup
5. Deploy to GitHub
6. Monitor your application!

---

## Support Resources

- **Flask-SQLAlchemy**: [flask-sqlalchemy.palletsprojects.com](https://flask-sqlalchemy.palletsprojects.com)
- **SQLAlchemy**: [sqlalchemy.org](https://sqlalchemy.org)
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Render Docs**: [render.com/docs](https://render.com/docs)

---

## Summary

✅ Your application is now **SQL-ready for online deployment**
✅ Supports both local development and cloud production
✅ PostgreSQL driver included
✅ Configuration files created
✅ Deployment guide provided

**You're ready to go live!** 🚀
