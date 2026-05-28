# TravelLuxScents — cPanel Deployment Guide
## UnlimitedWebHosting.co.uk

---

### Prerequisites
- cPanel access with Python support (Phusion Passenger)
- SSH access (recommended) or cPanel Terminal
- Domain configured in cPanel

---

### Step 1: Upload Files

**Option A — SSH/Terminal:**
```bash
cd ~
git clone <your-repo-url> perfume_decants
# OR upload via cPanel File Manager
```

**Option B — cPanel File Manager:**
Upload the project ZIP to `/home/yourusername/` and extract it.

---

### Step 2: Set Up Python Virtual Environment

```bash
cd ~/perfume_decants
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 3: Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your actual values
```

**Important settings to change:**
- `SECRET_KEY` — Generate a new one: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DEBUG=False`
- `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`
- Email settings (for order confirmations)
- Stripe keys (when ready)

---

### Step 4: Initialize Database

```bash
source venv/bin/activate
python manage.py migrate
python manage.py load_sample_data  # Loads sample products, quiz, etc.
python manage.py collectstatic --noinput
```

**Default admin login:** `admin` / `admin123` (CHANGE THIS IMMEDIATELY!)

---

### Step 5: Configure cPanel Python App

1. Go to **cPanel → Setup Python App** (or Software → Python)
2. Click **Create Application**
3. Set:
   - Python version: 3.12 (or latest available)
   - Application root: `perfume_decants`
   - Application URL: `/` (or your subdomain)
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`
4. Click **Create**

---

### Step 6: Configure .htaccess

Edit `.htaccess` and replace `yourusername` with your actual cPanel username:
```
PassengerAppRoot /home/YOURUSERNAME/perfume_decants
PassengerPython /home/YOURUSERNAME/perfume_decants/venv/bin/python
```

If your domain's document root is `/home/YOURUSERNAME/public_html/`, copy or symlink:
```bash
# Option 1: Symlink passenger_wsgi.py to public_html
ln -s ~/perfume_decants/passenger_wsgi.py ~/public_html/passenger_wsgi.py

# Option 2: Copy .htaccess to public_html
cp ~/perfume_decants/.htaccess ~/public_html/.htaccess
```

---

### Step 7: Static & Media Files

If static files aren't served by Django/WhiteNoise, configure Apache aliases:

In cPanel → **Apache Handlers** or via `.htaccess`:
```apache
Alias /static/ /home/yourusername/perfume_decants/staticfiles/
Alias /media/ /home/yourusername/perfume_decants/media/
```

Ensure proper permissions:
```bash
chmod -R 755 ~/perfume_decants/staticfiles/
chmod -R 755 ~/perfume_decants/media/
```

---

### Step 8: Verify & Restart

```bash
# Restart Passenger
touch ~/perfume_decants/tmp/restart.txt
mkdir -p ~/perfume_decants/tmp
touch ~/perfume_decants/tmp/restart.txt
```

Visit your domain to verify everything works.

---

### Admin Panel

Access at: `https://yourdomain.com/admin/`

**From admin you can manage:**
- Products, variants, images
- Fragrance notes, badges, longevity options
- Bottle sizes and colors
- Discovery sets
- Quiz questions and recommendations
- Mood collections
- Orders and order statuses
- Site settings (free delivery threshold, WhatsApp number, etc.)
- Trust badges

---

### Troubleshooting

**500 Error:**
```bash
# Check error log
tail -f ~/logs/error.log
# Or check Python app logs in cPanel
```

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
chmod -R 755 staticfiles/
```

**Database issues:**
```bash
python manage.py migrate
# Make sure db.sqlite3 is writable
chmod 664 db.sqlite3
chmod 775 $(dirname db.sqlite3)
```

**Restart app after changes:**
```bash
touch ~/perfume_decants/tmp/restart.txt
```

---

### Email Setup (Gmail)

1. Enable 2-Factor Authentication on Gmail
2. Generate an App Password: Google Account → Security → App Passwords
3. Use the app password in `.env`:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   ```

---

### Stripe Setup (When Ready)

1. Create account at https://dashboard.stripe.com
2. Get API keys from Developers → API Keys
3. Update `.env`:
   ```
   STRIPE_PUBLIC_KEY=pk_live_...
   STRIPE_SECRET_KEY=sk_live_...
   ```
4. Restart app: `touch ~/perfume_decants/tmp/restart.txt`

---

### Security Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Set `DEBUG=False`
- [ ] Change admin password
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up HTTPS (SSL certificate via cPanel)
- [ ] Configure email settings
- [ ] Secure `.env` file: `chmod 600 .env`
