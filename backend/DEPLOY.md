# ProductScout AI - Backend Deployment

## Railway Deployment

### Prerequisites
- Railway account
- GitHub repository

### Environment Variables (Set in Railway Dashboard)
```
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=productscout
JWT_SECRET=your-secure-random-string-min-32-chars

# API Keys (Optional - users can add their own)
OPENAI_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=...

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Frontend URL (for CORS and redirects)
FRONTEND_URL=https://your-vercel-app.vercel.app
```

### Deployment Steps
1. Push code to GitHub
2. Create new project in Railway
3. Connect your GitHub repository
4. Set root directory to `backend`
5. Add environment variables
6. Railway will auto-detect Python and deploy

### Post-Deployment
1. Copy the Railway deployment URL
2. Update `REACT_APP_BACKEND_URL` in Vercel frontend
3. Set up Stripe webhook to point to `https://your-railway-url/api/payments/webhook`

## MongoDB Atlas Setup

### Create Cluster
1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a free M0 cluster
3. Create a database user with read/write permissions
4. Whitelist IP `0.0.0.0/0` for Railway access (or use VPC peering for production)

### Connection String
```
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

### Collections Created Automatically
- `users` - User accounts and settings
- `products` - Discovered products
- `launch_kits` - Generated launch kits
- `competitors` - Monitored competitor stores
- `competitor_products` - Products from competitors
- `competitor_alerts` - Alerts for competitor changes
- `scan_history` - Scan logs
- `daily_reports` - Daily intelligence reports
- `boards` - User product boards
- `exports` - Export history
- `payment_events` - Stripe payment events
