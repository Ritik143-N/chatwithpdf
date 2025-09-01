# Alternative Render Deployment Options

If the Blueprint deployment with `render.yaml` fails, you can deploy each service manually:

## Option 1: Manual Deployment (Recommended if Blueprint fails)

### Backend Service

1. **Create Web Service**:
   - Go to Render Dashboard → "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `chatwithpdf-backend`
     - **Environment**: `Docker`
     - **Root Directory**: `backend`
     - **Docker Command**: Leave empty (uses Dockerfile CMD)
     - **Plan**: Free or Starter

2. **Environment Variables**:
   - No additional variables needed (PORT is set automatically)

3. **Add Persistent Disk**:
   - In service settings → "Disks"
   - **Name**: `chroma-data`
   - **Mount Path**: `/app/chroma_db`
   - **Size**: `1 GB`

### Frontend Service

1. **Create Web Service**:
   - Go to Render Dashboard → "New" → "Web Service"  
   - Connect your GitHub repository
   - Configure:
     - **Name**: `chatwithpdf-frontend`
     - **Environment**: `Docker`
     - **Root Directory**: `frontend`
     - **Docker Command**: Leave empty (uses Dockerfile CMD)
     - **Plan**: Free or Starter

2. **Environment Variables**:
   - **REACT_APP_BACKEND_URL**: `https://chatwithpdf-backend.onrender.com/api/v1`
   
   (Replace `chatwithpdf-backend` with your actual backend service name)

## Option 2: Fix Blueprint Deployment

The issue might be with the YAML syntax. Try this updated render.yaml:

```yaml
services:
  - type: web
    name: chatwithpdf-backend
    env: docker
    dockerfilePath: backend/Dockerfile
    dockerContext: backend
    plan: starter
    envVars:
      - key: PORT
        value: 8000
    disk:
      name: chroma-data
      mountPath: /app/chroma_db
      sizeGB: 1
    
  - type: web
    name: chatwithpdf-frontend
    env: docker
    dockerfilePath: frontend/Dockerfile
    dockerContext: frontend
    plan: starter
    envVars:
      - key: REACT_APP_BACKEND_URL
        value: https://chatwithpdf-backend.onrender.com/api/v1
```

## Option 3: Traditional Build (No Docker)

If Docker continues to fail, you can deploy without containers:

### Backend (Python)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Root Directory**: `backend`

### Frontend (Node.js)
- **Environment**: `Node`  
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npx serve -s build -l $PORT`
- **Root Directory**: `frontend`

## Troubleshooting

1. **Check logs** in Render dashboard for specific error messages
2. **Verify file paths** in your repository match the configuration
3. **Test Docker builds locally**:
   ```bash
   cd backend && docker build -t backend .
   cd frontend && docker build -t frontend .
   ```

## Current Issue Resolution

The error "open Dockerfile: no such file or directory" suggests Render is looking for Dockerfile in the wrong location. Try:

1. **Manual deployment** (Option 1 above) - most reliable
2. **Updated render.yaml** syntax (Option 2)
3. **Contact Render support** if issues persist
