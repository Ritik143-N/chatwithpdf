#!/bin/bash

echo "🐍 Setting up Python backend dependencies..."

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Detected Python version: $PYTHON_VERSION"

# Navigate to backend directory
cd "$(dirname "$0")/../backend" || exit 1

# Activate virtual environment
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Install based on Python version
if [[ "$PYTHON_VERSION" < "3.9" ]]; then
    echo "Using Python 3.8 compatible packages..."
    pip install -r requirements_py38.txt
else
    echo "Using standard packages..."
    pip install -r requirements.txt
fi

echo "✅ Backend dependencies installed successfully!"
echo ""
echo "To start the backend server:"
echo "cd backend"
echo "source venv/bin/activate"
echo "uvicorn app.main:app --reload"
