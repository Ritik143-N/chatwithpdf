#!/bin/bash

echo "🐳 Docker Build Test Script"
echo "=========================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

echo "📋 Available Dockerfiles:"
echo "1. Dockerfile (Full production with Nginx)"
echo "2. Dockerfile.simple (Single container FastAPI + React)"
echo "3. backend/Dockerfile (Backend only)"
echo "4. frontend/Dockerfile (Frontend only)"
echo "5. docker-compose.yml (Multi-container setup)"
echo ""

echo "🔨 Testing Docker builds..."

# Test simple build first
echo "Building Dockerfile.simple..."
if sudo docker build -f Dockerfile.simple -t chatwithpdf-simple . --quiet; then
    echo "✅ Dockerfile.simple - Build successful"
else
    echo "❌ Dockerfile.simple - Build failed"
fi

# Test full build
echo "Building main Dockerfile..."
if sudo docker build -t chatwithpdf-full . --quiet; then
    echo "✅ Dockerfile - Build successful"
else
    echo "❌ Dockerfile - Build failed"
fi

# Test backend build
echo "Building backend Dockerfile..."
if sudo docker build -t chatwithpdf-backend ./backend --quiet; then
    echo "✅ Backend Dockerfile - Build successful"
else
    echo "❌ Backend Dockerfile - Build failed"
fi

# Test frontend build
echo "Building frontend Dockerfile..."
if sudo docker build -t chatwithpdf-frontend ./frontend --quiet; then
    echo "✅ Frontend Dockerfile - Build successful"
else
    echo "❌ Frontend Dockerfile - Build failed"
fi

echo ""
echo "🚀 To run the containers:"
echo "Simple: sudo docker run -p 8000:8000 chatwithpdf-simple"
echo "Full: sudo docker run -p 80:80 chatwithpdf-full"
echo "Compose: sudo docker-compose up"
echo ""
echo "📊 Built images:"
sudo docker images | grep chatwithpdf
