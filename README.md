# 🌾 FarmBasket — Modern Farm Product Marketplace
> Shop fresh. Support Farmers. Grow Sustainably.

FarmBasket is a full‑featured ecommerce platform built using **Django + PostgreSQL**.
It allows users to browse, wishlist, add to cart, checkout, track orders, manage addresses,
and view order history — while admins manage inventory, products, and orders.
  
---
  
## 🚀 Live Demo
  
**The site is fully deployed and live!**
  
[![Deploy Status](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://farmbasket.onrender.com)
  
👉 **[Visit Live Site](https://farmbasket.onrender.com)**
  
*(Note: Initial load may take 30-50s as the free instance spins up)*

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
# 🧺 FarmBasket - The Journey

Welcome to **FarmBasket**! This isn't just another e-commerce project; it's a story of evolution, learning, and building something robust from the ground up. Here's how we grew:

### 🌱 The Seed: Local Beginnings
It started simple.
- **Localhost**: Fired up Django on a local development server.
- **SQLite**: Just a simple file-based database. No complexities, just getting the models right.
- **Development**: Basic HTML templates, no fancy UI, just raw functionality.

### 🌿 Sprouting: Adding Complexity
As the features grew, so did the stack.
- **Authentication**: Integrated secure user registration and login.
- **Media**: Initially serving images locally (and breaking them often!).
- **Email**: Tried setting up reliable emails... started with console backend, then struggled with SMTP.

### 🌳 Branching Out: The "Cloud" Era
We realized "it works on my machine" wasn't enough.
- **PostgreSQL**: Moved from SQLite to a robust Postgres database for better data integrity.
- **Cloudinary**: Images were heavy! Offloaded all media management to Cloudinary for instant optimization and delivery. 📸
- **Neon DB**: Deployed our database to the cloud using Neon (Serverless Postgres) for scalability. ☁️

### 🚀 Blooming: User Experience & Polish
We stopped building "features" and started building an "experience".
- **TailwindCSS**: Completely revamped the UI. Dark mode implementation, glassmorphism effects, and a neon-green brand identity. 🎨
- **Alpine.js**: Added reactive frontend interactions without the overhead of React. Real-time cart updates, loaders, and instant feedback. ⚡
- **Razorpay**: Integrated real payment gateways to handle transactions securely (simulated). 💳
- **SendGrid**: Finally fixed emails! Transactional emails (Welcome, Order Confirmation, OTPs) now land reliably in inboxes using the SendGrid API. 📧

---

*"Rooted With Love - Pericardium"*

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
