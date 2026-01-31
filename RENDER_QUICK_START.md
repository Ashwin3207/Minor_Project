# Render Deployment - Quick Start Guide

Your TPC Portal is ready to deploy on Render! Here's the fastest path to get live.

## 3-Step Deployment

### Step 1: Push to GitHub (2 min)
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Create Database on Render (3 min)
1. Go to [render.com](https://render.com) → Sign in with GitHub
2. Click **New** → **PostgreSQL**
3. Name: `tpc-portal-db`
4. Region: Pick closest to you
5. Plan: **Free**
6. Click **Create Database**
7. **Copy External Database URL** (you'll need this in Step 3)

### Step 3: Deploy Web Service (5 min)
1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Fill in:
   - **Name**: `tpc-portal`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
   - **Region**: Same as your database
   - **Plan**: Free

4. Click **Advanced** and add 3 environment variables:

   ```
   FLASK_ENV = production
   SECRET_KEY = [GENERATE]: python -c "import secrets; print(secrets.token_hex(32))"
   DATABASE_URL = [PASTE from Step 2]
   ```

5. Click **Create Web Service**

**Done! Your app deploys automatically (5-10 min)** ✅

---

## Wait... What's Happening?

- Render is building your app from GitHub
- Installing dependencies from `requirements.txt`
- Starting with `gunicorn run:app`
- Connecting to your PostgreSQL database
- Creating tables automatically

**Status**: Check dashboard → Green = Ready!

---

## Test Your Live App

1. Go to your app URL: `https://tpc-portal.onrender.com` (or your custom name)
2. Try admin login
3. Create a test opportunity  
4. Refresh → Data should still be there (proof it's using database!)
5. Success! 🎉

---

## If Deployment Fails

| Issue | Solution |
|-------|----------|
| Build error | Check Render "Build Logs" - usually missing dependency |
| Can't connect to DB | Verify DATABASE_URL in environment variables |
| App crashes | Check Render "Logs" tab for error details |
| Migrations failed | Go to Shell, run: `flask db upgrade` |

---

## Files Already Prepared for You ✅

- ✅ `requirements.txt` - Has psycopg2-binary
- ✅ `Procfile` - Tells Render how to start app
- ✅ `runtime.txt` - Specifies Python 3.11
- ✅ `config.py` - Auto-detects PostgreSQL
- ✅ `render.yaml` - Optional config file

**You don't need to change anything!**

---

## Deployment URLs

| Resource | URL |
|----------|-----|
| Your App | `https://tpc-portal.onrender.com` |
| Dashboard | [render.com/dashboard](https://render.com/dashboard) |
| Logs | In your service dashboard |

---

## Costs: $0/month 🎉

Render free tier includes:
- 750 hours/month web service (plenty for always-on app)
- Free PostgreSQL database
- Auto-scaling included

Upgrade only if you need premium features.

---

## Support Files

- 📄 [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) - Full detailed guide
- 📋 [RENDER_CHECKLIST.md](RENDER_CHECKLIST.md) - Step-by-step checklist
- 📚 [DATABASE_SETUP.md](DATABASE_SETUP.md) - General database setup

---

## Next: Monitor Your App

After deployment, in Render dashboard:
- **Logs** - Real-time app output
- **Metrics** - CPU, memory, requests
- **Events** - Deployment history
- **Environment** - Manage variables

---

**You're ready! Go to [render.com](https://render.com) and deploy now!** 🚀
