# Render Deployment Checklist

Quick reference to deploy your TPC Portal on Render.

## Pre-Deployment (Do These First)

- [ ] Code is committed to GitHub
- [ ] `git push origin main` completed
- [ ] Files present in repo root:
  - [ ] `requirements.txt` (with `psycopg2-binary`)
  - [ ] `Procfile` (contains: `web: gunicorn run:app`)
  - [ ] `runtime.txt` (contains: `python-3.11.0`)
  - [ ] `run.py`
  - [ ] `config.py`

## Render Setup

### Create Database (5 min)
- [ ] Sign in to [render.com](https://render.com)
- [ ] New → PostgreSQL
- [ ] Fill details (name, region, free plan)
- [ ] Copy **External Database URL**
- [ ] Save for next step

### Deploy App (10 min)
- [ ] New → Web Service
- [ ] Connect GitHub repository
- [ ] Name: `tpc-portal`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `gunicorn run:app`
- [ ] Select Region (same as database)
- [ ] Plan: Free

### Environment Variables (3 min)
- [ ] Add `FLASK_ENV` = `production`
- [ ] Add `SECRET_KEY` = [generate random: `python -c "import secrets; print(secrets.token_hex(32))"`]
- [ ] Add `DATABASE_URL` = [paste PostgreSQL URL from database step]
- [ ] Click "Create Web Service"

## Post-Deployment (Verify)

- [ ] Dashboard shows green "running" status
- [ ] Build completed without errors (check logs)
- [ ] App loads at provided URL
- [ ] Can login with admin account
- [ ] Can create test opportunity
- [ ] Data persists on refresh
- [ ] Database connection working (no 500 errors)

## If Something Fails

### Build Failed
- [ ] Check "Build Logs"
- [ ] Ensure `requirements.txt` has all dependencies
- [ ] Ensure `psycopg2-binary` is listed

### App Won't Start
- [ ] Check "Logs" tab for errors
- [ ] Verify start command: `gunicorn run:app`
- [ ] Check `Procfile` syntax

### Can't Connect to Database
- [ ] Verify `DATABASE_URL` is correct
- [ ] Check PostgreSQL database is running
- [ ] Try manual deploy (button in dashboard)

### Database Error on First Load
- [ ] Expected - migrations need to run
- [ ] Go to Shell tab, run: `flask db upgrade`
- [ ] Or restart service

---

## Your Deployment URLs

**Web App**: `https://tpc-portal.onrender.com`

**PostgreSQL Connection**: `postgresql://user:pass@host.onrender.com:5432/database`

---

## Time Estimate
- Setup: 5 min
- Database creation: 2 min  
- Deploy: 8 min
- Total: ~15 minutes

**You'll be live in 15 minutes!** 🚀
