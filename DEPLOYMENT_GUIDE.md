# DropSniper AI - Complete Deployment Guide

## Prerequisites
- GitHub account
- Vercel account (free tier works)
- Railway account (free tier works)
- MongoDB Atlas account (free tier works)

---

## Step 1: MongoDB Atlas Setup (5 minutes)

### 1.1 Create Account
1. Go to https://cloud.mongodb.com
2. Click "Try Free" → Sign up with Google or email
3. Verify your email

### 1.2 Create Cluster
1. Click "Build a Database"
2. Select **M0 FREE** tier
3. Choose provider: **AWS**
4. Choose region: **N. Virginia (us-east-1)** (closest to Railway)
5. Cluster name: `dropsniper-cluster`
6. Click "Create"

### 1.3 Create Database User
1. Go to "Database Access" in left sidebar
2. Click "Add New Database User"
3. Username: `dropsniper_admin`
4. Password: Generate a secure password → **COPY THIS**
5. Built-in Role: "Read and write to any database"
6. Click "Add User"

### 1.4 Network Access
1. Go to "Network Access" in left sidebar
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (0.0.0.0/0)
4. Click "Confirm"

### 1.5 Get Connection String
1. Go to "Database" in left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. Replace `<password>` with your database user password
6. **Save this string** - you'll need it for Railway

Example: `mongodb+srv://dropsniper_admin:YOUR_PASSWORD@dropsniper-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority`

---

## Step 2: Railway Backend Deployment (10 minutes)

### 2.1 Create Project
1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Connect your GitHub account if prompted
6. Select your repository

### 2.2 Configure Service
1. Click on the deployed service
2. Go to "Settings" tab
3. Set **Root Directory**: `backend`
4. Set **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`

### 2.3 Add Environment Variables
1. Go to "Variables" tab
2. Click "New Variable" and add each:

```
MONGO_URL = mongodb+srv://dropsniper_admin:PASSWORD@dropsniper-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME = dropsniper
JWT_SECRET = [generate: openssl rand -hex 32]
STRIPE_SECRET_KEY = sk_live_...
STRIPE_PUBLISHABLE_KEY = pk_live_...
STRIPE_WEBHOOK_SECRET = whsec_...
RESEND_API_KEY = re_...
FRONTEND_URL = https://dropsniperai.arisolutionsinc.com
```

### 2.4 Deploy
1. Railway auto-deploys on variable changes
2. Wait for deployment to complete (2-3 minutes)
3. Click "Settings" → find your domain: `dropsniper-production.up.railway.app`
4. **Copy this URL** - you'll need it for Vercel

### 2.5 Test Backend
Open in browser: `https://your-railway-url.up.railway.app/api/health`
Should show: `{"status":"healthy",...}`

---

## Step 3: Vercel Frontend Deployment (5 minutes)

### 3.1 Import Project
1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "Add New..." → "Project"
4. Import your GitHub repository

### 3.2 Configure Build
1. **Framework Preset**: Create React App
2. **Root Directory**: Click "Edit" → Enter `frontend`
3. **Build Command**: `yarn build`
4. **Output Directory**: `build`

### 3.3 Add Environment Variable
1. Expand "Environment Variables"
2. Add:
```
REACT_APP_BACKEND_URL = https://your-railway-url.up.railway.app
```

### 3.4 Configure Custom Domain (Optional)
1. Go to Project Settings → Domains
2. Add `dropsniperai.arisolutionsinc.com`
3. Add DNS records as instructed by Vercel:
   - Type: CNAME
   - Name: dropsniperai
   - Value: cname.vercel-dns.com

### 3.4 Deploy
1. Click "Deploy"
2. Wait 2-3 minutes for build
3. Your app is live at: `https://your-project.vercel.app`

---

## Step 4: Stripe Webhook Setup (2 minutes)

### 4.1 Create Webhook
1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. **Endpoint URL**: `https://your-railway-url.up.railway.app/api/payments/webhook`
4. **Events to send**: Select:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
5. Click "Add endpoint"

### 4.2 Get Webhook Secret
1. Click on your new webhook
2. Click "Reveal" under Signing secret
3. Copy the `whsec_...` value
4. Update `STRIPE_WEBHOOK_SECRET` in Railway

---

## Step 5: Final Configuration

### 5.1 Update Railway FRONTEND_URL
1. Go back to Railway
2. Update `FRONTEND_URL` variable with your Vercel URL
3. Service will redeploy automatically

### 5.2 Create Admin Account
1. Go to your Vercel URL
2. Click "Get Started" → Register
3. Use email: `jabriel@arisolutionsinc.com`
4. This email automatically gets admin access

---

## Verification Checklist

- [ ] MongoDB Atlas cluster running
- [ ] Railway backend responding at `/api/health`
- [ ] Vercel frontend loads landing page
- [ ] Can register new account
- [ ] Can login
- [ ] Dashboard loads with sample data
- [ ] Stripe checkout opens (test with Sniper tier)
- [ ] Admin panel accessible at `/admin`

---

## Environment Variables Summary

### Railway (Backend)
| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/...` |
| `DB_NAME` | Database name | `dropsniper` |
| `JWT_SECRET` | 64-char random string for auth | `openssl rand -hex 32` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_live_...` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | `pk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | `whsec_...` |
| `RESEND_API_KEY` | Resend API key for emails | `re_...` |
| `FRONTEND_URL` | Your Vercel app URL | `https://dropsniperai.arisolutionsinc.com` |

### Vercel (Frontend)
| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_BACKEND_URL` | Your Railway backend URL | `https://dropsniper-production.up.railway.app` |

### Optional (User-provided via Settings)
| Variable | Description |
|----------|-------------|
| OpenAI API Key | Users add their own for AI browser features |
| Telegram Bot Token | Users add their own for personal alerts |

---

## Troubleshooting

### Backend not starting
- Check Railway logs for Python errors
- Verify MONGO_URL is correct
- Ensure all required variables are set

### Frontend blank page
- Check browser console for errors
- Verify REACT_APP_BACKEND_URL is correct
- Ensure backend is responding

### Stripe checkout not working
- Verify Stripe keys are correct
- Check webhook endpoint is reachable
- Ensure webhook secret matches

### MongoDB connection failed
- Check IP whitelist includes 0.0.0.0/0
- Verify password in connection string
- Ensure cluster is deployed (not paused)

---

## Cost Estimates (Monthly)

| Service | Free Tier | Paid |
|---------|-----------|------|
| MongoDB Atlas | 512MB free | $9/mo for 2GB |
| Railway | 500 hours free | $5/mo base + usage |
| Vercel | 100GB bandwidth | $20/mo Pro |

**Total for low traffic**: $0-15/month
**Total for medium traffic**: $30-50/month
