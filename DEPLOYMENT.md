# 🚀 FarmBasket Deployment Guide (Vercel + Neon)

This guide will walk you through deploying your site to Vercel (Frontend/Backend) and Neon (Database) for free.

## 1. Prerequisites (Accounts)
*   **Vercel Account**: Sign up at [vercel.com](https://vercel.com) using GitHub.
*   **Neon Account**: Sign up at [neon.tech](https://neon.tech) (Free Postgres).
*   **Cloudinary Account**: Sign up at [cloudinary.com](https://cloudinary.com) (Free Media/Image Hosting).

## 2. Database Setup (Neon)
1.  Create a new Project in Neon (e.g., `farmbasket-prod`).
2.  Copy the **Connection String** from the Dashboard (looks like `postgres://user:pass@ep-xyz.us-east-2.aws.neon.tech/neondb`).
3.  **Save this URL**, you'll need it later.

## 3. Media Setup (Cloudinary)
Since Vercel is "read-only", uploaded images (like avatars) will disappear unless we use Cloudinary.
1.  Log in to Cloudinary.
2.  Go to Dashboard.
3.  Copy: `Cloud Name`, `API Key`, `API Secret`.

## 4. Deploying Code (Vercel)
1.  Go to Vercel Dashboard -> **Add New Project**.
2.  Import your `FarmBasket` repository.
3.  **IMPORTANT**: In the "Environment Variables" section, add these (copy from your `.env` or new accounts):
    *   `SECRET_KEY`: (Generate a random string)
    *   `DEBUG`: `False`
    *   `ALLOWED_HOSTS`: `.vercel.app`
    *   `DATABASE_URL`: (The Neon Connection String)
    *   `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
    *   `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`

4.  Click **Deploy**.

## 5. Post-Deployment Setup (One Time)
After deploy, your database is empty. Migrate and seed it from your **Local Terminal** pointing to **Prod DB**:

```bash
# Windows PowerShell (paste your real Neon URL)
$env:DATABASE_URL="postgres://user:pass@..." 
python manage.py migrate
python manage.py seed_products
```

## 6. Workflow (Dev vs Main)
1.  **Work in `dev`**: `git checkout dev`. Code, Commit, Push.
2.  **Preview**: Vercel deploys `dev` to a temporary URL for testing.
3.  **Release**: Merge to `main`. Vercel deploys to Production.
