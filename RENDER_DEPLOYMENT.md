# Render Deployment Guide for TPC Portal

Complete step-by-step guide to deploy your Flask app on Render with PostgreSQL.

## Prerequisites
- GitHub account with your code pushed
- Render account (free at [render.com](https://render.com))

---

## Step 1: Create PostgreSQL Database on Render

1. **Sign in to Render**
   - Go to [render.com](https://render.com)
   - Sign up/login with GitHub

2. **Create New PostgreSQL Database**
   - Click **"New"** (top right)
   - Select **"PostgreSQL"**
   - Fill in details:
     - **Name**: `tpc-portal-db`
     - **Database**: `tpc_portal`
     - **User**: `tpc_user`
     - **Region**: Select nearest to your location
     - **Plan**: Free
   - Click **"Create Database"**

3. **Copy Database Credentials**
   - Wait for database to initialize (2-3 minutes)
   - Go to your database dashboard
   - Copy the **External Database URL** (looks like: `postgresql://user:password@dpg-xxx.render.com:5432/database`)
   - Save this - you'll need it in Step 3

---

## Step 2: Connect GitHub Repository

1. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Add online database configuration"
   git push origin main
   ```
   
2. **Ensure These Files Are in Root**
   - `requirements.txt` ✅
   - `Procfile` ✅
   - `runtime.txt` ✅
   - `run.py` ✅
   - `config.py` ✅

---

## Step 3: Create Web Service on Render

1. **Create New Web Service**
   - Click **"New"** → **"Web Service"**
   - Select **"Deploy an existing repository"**
   - Click **"Connect"** next to your GitHub repository
   - If not listed, click "Configure account" and authorize GitHub

2. **Configure Service**
   - **Name**: `tpc-portal` (or your preferred name)
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```
     gunicorn run:app
     ```
   - **Plan**: Free
   - **Region**: Same as database (important for performance)

3. **Set Environment Variables**
   - Click **"Advanced"** → **"Add Environment Variable"**
   
   Add these variables:
   
   | Key | Value |
   |-----|-------|
   | `FLASK_ENV` | `production` |
   | `SECRET_KEY` | Generate random string: `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `DATABASE_URL` | Paste the PostgreSQL URL from Step 1 |

4. **Deploy**
   - Click **"Create Web Service"**
   - Render automatically deploys! (5-10 minutes)
   - Watch the build log in the dashboard

---

## Step 4: Run Database Migrations

Once your app is deployed and running:

1. **Access Render Shell** (optional - for checking)
   - Go to your web service dashboard
   - Click **"Shell"** tab
   - Run migrations manually if needed:
     ```bash
     flask db upgrade
     ```

Or migrations can run automatically if you add to `run.py`:
```python
# Add at the start of create_app() in app/__init__.py
from flask_migrate import upgrade
try:
    upgrade()
except:
    pass  # First time, migrations might not exist
```

---

## Step 5: Verify Deployment

1. **Check Status**
   - Dashboard shows green status = running ✅
   - Your app URL: `https://tpc-portal.onrender.com` (or your custom name)

2. **Test Your App**
   - Click the URL in dashboard
   - Try logging in and creating a test opportunity
   - Verify data persists (refresh page)

3. **Check Logs**
   - Click **"Logs"** tab
   - Watch for errors during deployment

---

## Common Deployment Issues

### Issue: "Build failed - psycopg2 not found"
**Solution**: Ensure `psycopg2-binary` is in `requirements.txt` ✅

### Issue: "DATABASE_URL not set"
**Solution**: 
1. Go to environment variables
2. Add `DATABASE_URL` with your PostgreSQL URL
3. Redeploy (click "Manual Deploy")

### Issue: "Internal Server Error"
**Solution**:
1. Check logs for detailed error
2. Verify DATABASE_URL format: `postgresql://user:pass@host:port/database`
3. Run migrations in shell

### Issue: "413 Payload Too Large"
**Solution**: Increase max upload size in config.py (already done - 16MB)

---

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host.onrender.com:5432/db` |
| `SECRET_KEY` | Session encryption | `abc123xyz789...` (32+ chars) |
| `FLASK_ENV` | App mode | `production` |

**Important**: Use Render's secret variables (not plain text) for sensitive data!

---

## Monitoring & Maintenance

### View Live Logs
- Dashboard → Logs tab
- Search for errors in real-time

### Restart Application
- Dashboard → Manual Deploy button
- Or push new code to GitHub (auto-deploys)

### Check Database
- Go to PostgreSQL database dashboard
- View schema, tables, data
- Create backups

### Auto-Deploy on Code Push
- Already enabled by default
- Push to GitHub → Render auto-deploys within 1 minute

---

## Costs

| Service | Plan | Cost |
|---------|------|------|
| Web Service | Free | Free (includes 750 hrs/month) |
| PostgreSQL | Free | Free (until instance used) |
| **Total** | Free tier | **$0/month** |

Upgrade to paid if you need:
- Always-on service (free tier sleeps after 15 min inactivity)
- More database connections
- Better performance

---

## Next Steps After Deployment

1. ✅ Database is live
2. ✅ App is running
3. **Now do this**:
   - Test admin login
   - Post a test opportunity
   - Apply as student
   - Verify everything works

4. **Optional but recommended**:
   - Set up custom domain
   - Enable auto-deploy notifications
   - Monitor performance in Render dashboard

---

## Troubleshooting Checklist

- [ ] GitHub repo is connected
- [ ] `requirements.txt` includes `psycopg2-binary`
- [ ] `Procfile` exists with correct content
- [ ] `DATABASE_URL` is set in environment variables
- [ ] `SECRET_KEY` is generated and set
- [ ] `FLASK_ENV` is set to `production`
- [ ] PostgreSQL database is created and running
- [ ] Build logs show no errors
- [ ] App shows green "running" status

---

## Support

- **Render Docs**: [docs.render.com](https://docs.render.com)
- **PostgreSQL Docs**: [postgresql.org/docs](https://postgresql.org/docs)
- **Flask Docs**: [flask.palletsprojects.com](https://flask.palletsprojects.com)

**Your app is now production-ready! 🚀**
