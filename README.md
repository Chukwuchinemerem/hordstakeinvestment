# 🚀 Hordstake — Crypto Investment Platform

A fully functional Django crypto investment platform with user and admin dashboards.

## ⚡ Quick Start (Local)

### 1. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment (optional)
```bash
cp .env.example .env
# Edit .env with your values if needed
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create superuser
```bash
python manage.py createsuperuser
```
Or use the auto-seeded admin:
- **Email:** `admin@hordstake.com`
- **Password:** `Admin@12345`

### 6. Seed demo data (optional but recommended)
```bash
python manage.py shell < seed_script.py
```

### 7. Start the server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 📌 URL Reference

| URL | Description |
|-----|-------------|
| `/` | Landing page |
| `/auth/login/` | User login |
| `/auth/register/` | User registration |
| `/dashboard/` | User dashboard |
| `/transactions/deposit/` | Deposit funds |
| `/transactions/withdraw/` | Withdraw funds |
| `/transactions/history/` | Transaction history |
| `/dashboard/plans/` | Investment plans |
| `/dashboard/my-investments/` | My investments |
| `/referrals/` | Referral program |
| `/notifications/` | Notifications |
| `/dashboard/profile/` | Profile settings |
| `/admin-panel/` | Admin dashboard |
| `/admin-panel/users/` | User management |
| `/admin-panel/deposits/` | Deposit approvals |
| `/admin-panel/withdrawals/` | Withdrawal approvals |
| `/admin-panel/plans/` | Investment plan management |
| `/admin-panel/wallets/` | Crypto wallet addresses |
| `/admin-panel/content/` | Site content management |
| `/django-admin/` | Django built-in admin |

---

## 🚀 Deploy on Render

1. Push this project to a GitHub repo
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`
5. Add environment variables:
   - `SECRET_KEY` — a long random string
   - `DEBUG` — `False`
6. Deploy!

The `build.sh` script will:
- Install dependencies
- Collect static files
- Run migrations
- Create default admin user
- Seed default investment plans & wallets

---

## 🔧 Admin Defaults (change immediately!)

- **URL:** `/admin-panel/`
- **Email:** `admin@hordstake.com`
- **Password:** `Admin@12345`

---

## 🎨 Colour Palette

| Colour | Hex |
|--------|-----|
| Background | `#060f22` |
| Card Background | `#0a1628` / `#0d1c35` |
| Primary Blue | `#2563eb` |
| Blue Hover | `#3b82f6` |
| Text | `#e2e8f0` |
| Muted | `#64748b` |

---

## 📦 Tech Stack

- **Backend:** Django 4.2
- **Frontend:** Tailwind CSS (CDN) + Vanilla JS
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Static files:** WhiteNoise
- **Deployment:** Render

---

## ✅ Features

- ✅ Landing page with 8-slide carousel
- ✅ Live crypto price ticker (20+ coins)
- ✅ Language selector
- ✅ WhatsApp live support widget
- ✅ Investment plans with auto profit calculation
- ✅ Multi-crypto deposit system (BTC, ETH, USDT, TON, SOL)
- ✅ Withdrawal request system
- ✅ Transaction history
- ✅ Referral system with earnings
- ✅ Notifications system
- ✅ Full user dashboard with charts
- ✅ Full admin panel with all controls
- ✅ Partner logos slider
- ✅ Testimonials section
- ✅ FAQ section
- ✅ Newsletter subscription
- ✅ Fully mobile responsive
- ✅ Dark navy + electric blue theme
