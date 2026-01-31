# ⚡ Render Deployment - START HERE

## Your TPC Portal is Ready to Go Live! 🚀

```
Your Code on GitHub
        ↓
   [RENDER.COM]
        ↓
PostgreSQL Database + Flask App (Live!)
        ↓
    https://yourapp.onrender.com
```

---

## 5-Minute Quick Start

### 1️⃣ GitHub (1 min)
```bash
git push origin main
```
Your code is ready!

### 2️⃣ Create PostgreSQL (2 min)
- Visit [render.com](https://render.com)
- New → PostgreSQL
- Copy "External Database URL"

### 3️⃣ Deploy App (2 min)
- New → Web Service
- Connect GitHub
- Add 3 Environment Variables (see below)
- Click Deploy!

---

## Environment Variables You Need

Copy and paste into Render:

```
FLASK_ENV=production

SECRET_KEY=<generate_random_string>

DATABASE_URL=<paste_from_postgresql_step>
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Files Already Set Up For You ✅

| File | Purpose | Status |
|------|---------|--------|
| `Procfile` | Tells Render how to run app | ✅ Ready |
| `requirements.txt` | All dependencies | ✅ Ready |
| `runtime.txt` | Python 3.11 | ✅ Ready |
| `config.py` | Auto-detects PostgreSQL | ✅ Ready |
| `render.yaml` | Render config | ✅ Ready |

**Zero changes needed - just deploy!**

---

## After Deployment (Verify It Works)

1. Visit your app URL
2. Login with admin account
3. Create test opportunity
4. Refresh page
5. Data still there = **Success!** ✅

---

## Detailed Guides

- 📖 [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) - Full step-by-step
- ✅ [RENDER_CHECKLIST.md](RENDER_CHECKLIST.md) - Verification checklist
- ⚡ [RENDER_QUICK_START.md](RENDER_QUICK_START.md) - Quick reference

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "psycopg2 not found" | Already in requirements.txt ✓ |
| "DATABASE_URL error" | Check environment variables |
| "App won't start" | Check Render logs |
| "Can't connect to DB" | Verify DATABASE_URL format |

---

## Costs

**Free! 🎉**
- Web service: Free tier (750 hrs/month)
- PostgreSQL: Free tier
- Total: **$0/month**

---

## You're All Set!

Everything is configured and ready. Just:
1. Push to GitHub ✅
2. Create PostgreSQL ✅
3. Deploy Web Service ✅
4. Done! 🎉

**Go to [render.com](https://render.com) and deploy now!**

Questions? Check [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
