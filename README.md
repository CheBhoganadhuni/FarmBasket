# 🌾 FarmBasket — Modern Farm Product Marketplace
> Shop fresh. Support Farmers. Grow Sustainably.

FarmBasket is a full‑featured ecommerce platform built using **Django + PostgreSQL**.
It allows users to browse, wishlist, add to cart, checkout, track orders, manage addresses,
and view order history — while admins manage inventory, products, and orders.

---

## ✨ Highlights
- Organic ecommerce platform with a clean UI
- Built using Django REST + TailwindCSS frontend
- Razorpay Payment Gateway integration (Test/Live Support)
- Fully responsive + Dark/Light mode switch

---

## ✨ Key Features

### 🧑‍🤝‍🧑 User Features
- JWT Authentication (Signup / Login / Forgot Password)
- Email verification & welcome email
- Profile dashboard: avatar upload, addresses, orders, change password, delete account
- Wishlist + Add to Cart
- Checkout with Razorpay (UPI / Cards / NetBanking / COD)
- Order tracking with progress statuses
- Theme Support: Dark Mode / Light Mode toggle

### 🛠 Admin Features (Super User)
- Custom Admin Dashboard (not Django default)
- View Products (Inventory Is Managed By Seeding Code As Of Now)
- Manage orders (Pending → Confirmed → Shipped → Delivered)
- Manage users, view user orders, deactivate accounts
- Role‑based access protection

### 💳 Razorpay Payments
- Supports UPI / Cards / Wallets / NetBanking
- Works in Test Mode until deployed to production

### 🔐 Authentication & Security
- **Google / Social Auth** (OAuth2) — allow users to sign up / login using Google (future: Facebook / Apple).
- Harden authentication flows and token rotation for smoother JWT + session handling.

### ⚡ UX Improvements & Performance
- **Skeleton loaders & page transition skeletons** while APIs load to improve perceived performance.
- Add optimized lazy-loading for images and product lists.
- Disable repeated clicks / navigation during critical flows (e.g., while payment or order confirmation is processing) to avoid duplicate orders.

### 🧾 Orders & Wallets
- **Order tracking UI** with timeline (Order placed → Confirmed → Shipped → Out for delivery → Delivered).
- **Order cancellation / refund** flows with automatic credit to user wallet (where applicable).
- Add backend endpoints to credit/debit user wallets and show wallet balance on profile.

---

## 🧱 Tech Stack

| Component | Tech |
|----------|------|
| Backend  | Django 5, Django REST Framework, Django Ninja |
| Frontend | TailwindCSS, Alpine.js |
| Database | PostgreSQL |
| Auth     | JWT (SimpleJWT) + Django Sessions |
| Payment  | Razorpay |
| Email Service | mail SMTP |

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repo
```bash
git clone https://github.com/CheBhoganadhuni/FarmBasket.git
cd FarmBasket
```

### 2️⃣ Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate       # macOS/Linux
.\venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

### 3️⃣ Setup PostgreSQL
```sql
CREATE DATABASE farmbasket;
CREATE USER farmuser WITH PASSWORD 'farm_pass123';
GRANT ALL PRIVILEGES ON DATABASE farmbasket TO farmuser;
```

### 4️⃣ Environment Variables (.env)

```
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=farmbasket
DB_USER=farmuser
DB_PASSWORD=farm_pass123
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-mail-sample-@gmail.com
EMAIL_HOST_PASSWORD=your-password-here
DEFAULT_FROM_EMAIL=FarmBasket <noreply@farmbasket.com>

ACCESS_TOKEN_EXPIRE_MINUTES=your-value-sample-30
REFRESH_TOKEN_EXPIRE_DAYS=your-value-sample-7
ALGORITHM=HS256

RAZORPAY_KEY_ID=xxxx
RAZORPAY_KEY_SECRET=xxxx
```

### 5️⃣ Apply Migrations
```bash
python manage.py migrate
```

### 6️⃣ Create Superuser
```bash
python manage.py createsuperuser
```

- Use super user credentials to access admin panel

### 7️⃣ Run Server
```bash
python manage.py runserver
```
Visit → `http://localhost:8000`

---

## 🤝 Contributing
PRs welcome — fork the repo, create a feature branch, and submit a PR.
---

## 📄 License
MIT License - free to use, modify, and distribute.

**Built with caffeine by Chetan Bhoganadhuni @**
**🍃 FarmBasket**
---

## 🚧 Next Development / Roadmap

Planned improvements and features for upcoming development cycles:

### 🎟 Promotions & Loyalty
- **Coupon system**: create, validate, and apply discount codes (percentage / fixed / min-order rules / expiry).
- **Loyalty / XP system**: track user points for purchases, show tiers, and enable redeemable rewards.

### 🧪 Payments & Deployment
- Move Razorpay to **Live mode** after domain & SSL setup; implement webhook verification for payment success/failure.
- Deployment guides: Render / Railway / Heroku / AWS (CI/CD pipelines, environment management).

### Open to bug fixes, UI improvements, optimizations, etc.
---
