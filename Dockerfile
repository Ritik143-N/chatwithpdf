# Multi-stage Dockerfile for Chat with PDF application
# This builds both backend and frontend in a single container

# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source code
COPY frontend/ ./

# Build the React application
RUN npm run build

# Stage 2: Setup Backend and Final Image
FROM python:3.11-slim AS final

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first for better caching
COPY backend/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/app/ ./app/

# Create directory for ChromaDB
RUN mkdir -p ./chroma_db

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/build /var/www/html

# Configure Nginx to serve frontend and proxy API calls
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    \
    # Serve React frontend \
    location / { \
        root /var/www/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Proxy API requests to FastAPI backend \
    location /api/ { \
        proxy_pass http://localhost:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    # Health check endpoint \
    location /health { \
        proxy_pass http://localhost:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
}' > /etc/nginx/sites-available/default

# Create supervisor configuration to run both services
RUN echo '[supervisord] \
nodaemon=true \
\
[program:nginx] \
command=nginx -g "daemon off;" \
autostart=true \
autorestart=true \
stderr_logfile=/var/log/nginx.err.log \
stdout_logfile=/var/log/nginx.out.log \
\
[program:fastapi] \
command=uvicorn app.main:app --host 0.0.0.0 --port 8000 \
directory=/app \
autostart=true \
autorestart=true \
stderr_logfile=/var/log/fastapi.err.log \
stdout_logfile=/var/log/fastapi.out.log' > /etc/supervisor/conf.d/supervisord.conf

# Expose port 80 (Nginx will handle both frontend and API routing)
EXPOSE 80

# Use supervisor to run both nginx and FastAPI
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
