# TravelLuxeScent 🌿

> **Premium Fragrance Decants — E-Commerce Store**

A Django-powered online store for selling luxury perfume decants. Customers can explore fragrances, take a scent quiz, build discovery sets, and checkout securely via Stripe.

---

## Features

- 🛍️ **Product Catalogue** — 12+ premium decants with fragrance notes, longevity & gender filters
- 🧪 **Scent Quiz** — Personalised fragrance recommendations
- 📦 **Discovery Sets** — Bundle deals (Pick Any 3 / 5 / 10)
- 🛒 **Cart & Checkout** — Session-based cart with Stripe payments
- 👤 **Accounts** — Registration, login, order history
- 📱 **WhatsApp Support** — Floating chat button
- ⚙️ **Admin Panel** — Full product, order & site management

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.2 (Python 3.12+) |
| Database | SQLite (production-ready for low–medium traffic) |
| Payments | Stripe |
| Static Files | WhiteNoise |
| Hosting | cPanel / Phusion Passenger (UnlimitedWebHosting) |

---

## Local Development

### 1. Clone & enter project

```bash
git clone https://github.com/Mukhammad-develop/travelluxscents.git
cd travelluxscents
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your values (SECRET_KEY, Stripe keys, email, etc.)
```

### 5. Run migrations & start server

```bash
python manage.py migrate
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**

### 6. Create admin user (first time)

```bash
python manage.py createsuperuser
```

Admin panel: **http://127.0.0.1:8000/admin/**

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for dev, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated domains |
| `STRIPE_PUBLIC_KEY` | Stripe publishable key (`pk_live_...`) |
| `STRIPE_SECRET_KEY` | Stripe secret key (`sk_live_...`) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret (`whsec_...`) |
| `EMAIL_HOST_USER` | Gmail address for order emails |
| `EMAIL_HOST_PASSWORD` | Gmail App Password |

> ⚠️ **Never commit `.env` to git.** It is listed in `.gitignore`.

---

## Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for full cPanel / UnlimitedWebHosting instructions.

---

## Project Structure

```
travelluxscents/
├── config/             # Django settings, URLs, WSGI
├── shop/               # Products, catalogue, homepage
├── cart/               # Session cart
├── orders/             # Order management & Stripe checkout
├── accounts/           # User auth & profiles
├── quiz/               # Scent quiz & recommendations
├── templates/          # HTML templates
├── staticfiles/        # Collected static assets
├── passenger_wsgi.py   # cPanel Passenger entry point
├── .htaccess           # Apache / Passenger config
├── .env.example        # Environment variable template
└── requirements.txt    # Python dependencies
```

---

## License

Private project — All rights reserved © TravelLuxeScent
