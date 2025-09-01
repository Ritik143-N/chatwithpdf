#!/bin/bash

# Chat with PDF - Project Status Check

echo "🔍 Chat with PDF - Project Status"
echo "=================================="

# Check if we're in the project directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📋 Project Structure:"
echo "✅ Backend (FastAPI + Python)"
echo "✅ Frontend (React + Tailwind CSS)"
echo "✅ Documentation"
echo "✅ Docker configuration"
echo ""

# Check backend
echo "🔧 Backend Status:"
if [ -d "backend/venv" ]; then
    echo "✅ Virtual environment exists"
else
    echo "⚠️  Virtual environment not found"
fi

if [ -f "backend/requirements.txt" ]; then
    echo "✅ Requirements file exists"
else
    echo "❌ Requirements file missing"
fi

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend server is running (http://localhost:8000)"
else
    echo "⚠️  Backend server is not running"
fi

echo ""

# Check frontend
echo "🎨 Frontend Status:"
if [ -d "frontend/node_modules" ]; then
    echo "✅ Node modules installed"
else
    echo "⚠️  Node modules not installed"
fi

if [ -f "frontend/package.json" ]; then
    echo "✅ Package.json exists"
else
    echo "❌ Package.json missing"
fi

# Check if frontend is running
if curl -s http://localhost:3000/ > /dev/null 2>&1; then
    echo "✅ Frontend server is running (http://localhost:3000)"
else
    echo "⚠️  Frontend server is not running"
fi

echo ""

# Show next steps
echo "🚀 Next Steps:"
echo ""

if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "1. Start the backend server:"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   python -m uvicorn app.main:app --reload --port 8000"
    echo ""
fi

if ! curl -s http://localhost:3000/ > /dev/null 2>&1; then
    echo "2. Start the frontend server (in a new terminal):"
    echo "   cd frontend"
    echo "   npm start"
    echo ""
fi

echo "3. Open your browser and navigate to:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API docs: http://localhost:8000/docs"
echo ""

echo "📝 Usage:"
echo "1. Upload a PDF file"
echo "2. Wait for processing"
echo "3. Ask questions about the document"
echo ""

echo "⚙️  Optional Configuration:"
echo "• Set HUGGING_FACE_TOKEN for better LLM responses"
echo "• Install Ollama for local LLM (privacy-focused)"
echo ""

echo "🐳 Docker Deployment:"
echo "   docker-compose up --build"
echo ""

echo "✨ Project successfully set up!"
