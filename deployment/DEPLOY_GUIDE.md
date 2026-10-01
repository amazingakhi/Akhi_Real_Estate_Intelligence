# 🚀 Deployment Guide — Akhi Real Estate Intelligence (AREI™)

## Quick Start: Which Platform to Choose?

| Platform | Free Tier | Custom Domain | Best For |
|---|---|---|---|
| **Streamlit Cloud** | ✅ Yes | ✅ (paid) | Fastest deploy, no config needed |
| **Railway** | ✅ $5 credit | ✅ Yes | Best performance, scales auto |
| **Render** | ✅ Yes (sleeps) | ✅ Yes | Good free tier, persistent disk |

---

## Option 1 — Streamlit Community Cloud (Recommended for Start)

1. Push your project to GitHub (public or private repo).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Set:
   - **Repository**: `your-username/Gurugram_Real_Estate_Analysis`
   - **Branch**: `main`
   - **Main file path**: `src/app.py`
4. Click **Advanced settings** → paste all your `.env` variables into the **Secrets** box in TOML format:
   ```toml
   AKHI_ADMIN_EMAIL = "iamakv01@gmail.com"
   AKHI_ADMIN_PASSWORD = "YourSecurePassword"
   JWT_SECRET_KEY = "your-64-char-secret"
   RAZORPAY_KEY_ID = "rzp_live_xxx"
   RAZORPAY_KEY_SECRET = "your_secret"
   SMTP_USER = "your@gmail.com"
   SMTP_PASSWORD = "your_app_password"
   NOTIFY_EMAIL = "iamakv01@gmail.com"
   ```
5. Click **Deploy!**

> **Note:** Streamlit Cloud's free tier has a 1 GB memory limit. The app fits comfortably within this.

---

## Option 2 — Railway

1. Install Railway CLI: `npm install -g @railway/cli`
2. `railway login && railway init`
3. `railway up` from the project root.
4. Set environment variables in the Railway dashboard under **Variables**.
5. Railway auto-detects the `Procfile` and sets the start command.
6. Add a custom domain under **Settings → Domains**.

---

## Option 3 — Render

1. Connect your GitHub repo at [render.com](https://render.com).
2. Render auto-detects `render.yaml` and creates the service.
3. Set secret environment variables (`AKHI_ADMIN_PASSWORD`, `RAZORPAY_*`, `SMTP_*`) manually in the Render dashboard under **Environment**.
4. Deploy — Render handles SSL, CDN, and restarts.

> **Free tier note:** Render free web services spin down after 15 min of inactivity. Upgrade to Starter ($7/mo) for always-on hosting.

---

## Pre-Deployment Checklist

- [ ] `.env` file created from `.env.example` with all real values filled in
- [ ] `AKHI_ADMIN_PASSWORD` set to a strong password (min 12 chars, mixed case + symbols)
- [ ] `JWT_SECRET_KEY` is a 64-char random string (run: `python -c "import secrets; print(secrets.token_urlsafe(64))"`)
- [ ] Razorpay Live keys added (test with `rzp_test_*` first)
- [ ] Gmail App Password created (not your regular Gmail password)
- [ ] `data/akhi_properties.db` is either in the repo or regenerates on first run
- [ ] `models/property_price_model.joblib` is in the repo (it is pre-trained)
- [ ] `data/raw/gurugram_real_estate.csv` is in the repo

---

## Post-Deploy Steps

1. Open your deployed URL and login with admin credentials.
2. Go to **Admin → Settings → API Keys** to verify Razorpay is configured.
3. Go to **Admin → Settings → Email Config** to verify SMTP is connected.
4. Submit a test inquiry to confirm lead email arrives in your inbox.
5. Test the **💎 Pricing** page → checkout flow with a Razorpay test key.
6. Add your Google Analytics ID in `.env` under `GA_MEASUREMENT_ID` for traffic tracking.

---

## Running Locally

```bash
cd Gurugram_Real_Estate_Analysis
pip install -r requirements.txt
cp .env.example .env        # then fill in your values
streamlit run src/app.py
```

App will be available at http://localhost:8501

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `AKHI_ADMIN_EMAIL` | ✅ | Admin login email |
| `AKHI_ADMIN_PASSWORD` | ✅ | Admin login password |
| `JWT_SECRET_KEY` | ✅ | 64-char random secret for JWT |
| `RAZORPAY_KEY_ID` | For payments | Razorpay live/test key |
| `RAZORPAY_KEY_SECRET` | For payments | Razorpay secret |
| `SMTP_USER` | For emails | Gmail/SMTP username |
| `SMTP_PASSWORD` | For emails | Gmail App Password |
| `NOTIFY_EMAIL` | For emails | Where lead alerts are sent |
| `GA_MEASUREMENT_ID` | Optional | Google Analytics 4 ID |
| `REDIS_URL` | Optional | Redis for multi-worker rate limiting |
| `DATABASE_URL` | Optional | PostgreSQL URL (leave blank for SQLite) |
