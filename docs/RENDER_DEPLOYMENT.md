# Deployment Guide for Render

This guide explains how to deploy your Chat with PDF application to Render.

## Prerequisites

1. Create a [Render account](https://render.com)
2. Connect your GitHub repository to Render
3. Push your code to GitHub

## Method 1: Using Infrastructure as Code (render.yaml)

The project includes a `render.yaml` file for automatic deployment.

### Steps:
1. Push your code to GitHub
2. In Render dashboard, click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file and deploy both services

## Method 2: Manual Deployment

### Backend Deployment

1. **Create Web Service**:
   - Go to Render dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Set the following:
     - **Name**: `chatwithpdf-backend`
     - **Environment**: `Docker`
     - **Root Directory**: `backend`
     - **Region**: Choose your preferred region
     - **Plan**: Start with Free tier

2. **Environment Variables**:
   - `PORT`: `8000` (automatically set by Render)

3. **Disk Storage** (for ChromaDB persistence):
   - In service settings, go to "Disks"
   - Add disk: Name: `chroma-data`, Mount Path: `/app/chroma_db`, Size: `1 GB`

### Frontend Deployment

1. **Create Web Service**:
   - Go to Render dashboard  
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Set the following:
     - **Name**: `chatwithpdf-frontend`
     - **Environment**: `Docker`
     - **Root Directory**: `frontend`
     - **Region**: Same as backend
     - **Plan**: Start with Free tier

2. **Environment Variables**:
   - `REACT_APP_BACKEND_URL`: `https://your-backend-service.onrender.com/api/v1`
   
   Replace `your-backend-service` with your actual backend service name.

## Important Configuration Notes

### Backend Configuration
- The backend Dockerfile has been updated to use the `PORT` environment variable
- ChromaDB data will persist using Render's disk storage
- CORS is configured to allow all origins (you may want to restrict this in production)

### Frontend Configuration
- The API service has been updated to use `REACT_APP_BACKEND_URL` environment variable
- Falls back to localhost for local development

### CORS and Environment
Make sure your backend CORS configuration allows your frontend domain. You may want to update the CORS settings in `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-service.onrender.com"],  # Replace with your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Deployment Process

1. **Push to GitHub**: Ensure all your code is committed and pushed
2. **Deploy Backend First**: Deploy the backend service and note the URL
3. **Update Frontend Environment**: Set the `REACT_APP_BACKEND_URL` to your backend URL
4. **Deploy Frontend**: Deploy the frontend service

## Monitoring and Logs

- Check deployment logs in Render dashboard
- Monitor service health and performance
- Set up alerts for service downtime

## Scaling and Production Considerations

1. **Upgrade Plans**: Move from Free tier to paid plans for better performance
2. **Environment-specific CORS**: Restrict CORS to your frontend domain
3. **Database**: Consider using a managed database instead of ChromaDB files
4. **Monitoring**: Set up proper monitoring and alerting
5. **Custom Domain**: Configure custom domains for your services

## Troubleshooting

### Common Issues:
1. **Build failures**: Check logs for missing dependencies or build errors
2. **CORS errors**: Ensure backend CORS allows your frontend domain  
3. **API connection**: Verify the backend URL is correctly set in frontend environment variables
4. **Port issues**: Render automatically sets PORT environment variable

### Health Checks:
- Backend: `https://your-backend.onrender.com/` should return `{"msg": "Chat with PDF API is running"}`
- Frontend: Should load the React application

## Cost Optimization

- Start with Free tier for testing
- Upgrade to paid plans for production workloads
- Monitor usage and optimize based on traffic patterns
