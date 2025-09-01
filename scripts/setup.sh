#!/bin/bash

echo "🚀 Setting up Chat with PDF application..."

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing backend dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup complete!"

cd ..

echo "📦 Setting up frontend..."
cd frontend

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

echo "✅ Frontend setup complete!"

cd ..

echo "🎉 Setup complete! 

To start the application:

1. Start the backend server:
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --reload --port 8000

2. In a new terminal, start the frontend:
   cd frontend
   npm start

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

📝 Additional Scripts:
- scripts/setup_ollama.sh - Set up local LLM with Ollama
- scripts/status.sh - Check service status
- scripts/test_*.py - Test files

📝 Deployment:
- See docs/RENDER_DEPLOYMENT.md for deployment instructions
- Use 'docker-compose up --build' for Docker deployment
"
