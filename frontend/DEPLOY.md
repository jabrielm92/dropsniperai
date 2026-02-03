# ProductScout AI - Frontend Deployment

## Vercel Deployment

### Prerequisites
- Vercel account
- GitHub repository connected to Vercel

### Environment Variables (Set in Vercel Dashboard)
```
REACT_APP_BACKEND_URL=https://your-railway-backend.up.railway.app
```

### Deployment Steps
1. Push code to GitHub
2. Connect repository to Vercel
3. Set the root directory to `frontend`
4. Set environment variables in Vercel dashboard
5. Deploy

### Build Settings
- Framework: Create React App
- Build Command: `yarn build`
- Output Directory: `build`
- Install Command: `yarn install`
