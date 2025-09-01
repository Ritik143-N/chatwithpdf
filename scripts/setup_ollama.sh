#!/bin/bash

echo "🦙 Setting up Ollama for local LLM usage"
echo "======================================="

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install it first:"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "✅ Ollama is installed"

# Check if Ollama service is running
if ! curl -s http://localhost:11434 > /dev/null; then
    echo "🚀 Starting Ollama service..."
    echo "Run this command in a separate terminal:"
    echo "   ollama serve"
    echo ""
    echo "Then come back and run this script again."
    exit 1
fi

echo "✅ Ollama service is running"

# Check if we have any models
available_models=$(ollama list 2>/dev/null | wc -l)

if [ "$available_models" -le 1 ]; then
    echo "📥 No models found. Downloading a lightweight model..."
    echo "This may take a few minutes..."
    
    # Try to download a lightweight model
    if ollama pull llama3.2:1b; then
        echo "✅ Successfully downloaded llama3.2:1b"
    elif ollama pull llama2; then
        echo "✅ Successfully downloaded llama2"
    else
        echo "❌ Failed to download models. Please try manually:"
        echo "   ollama pull llama3.2:1b"
        exit 1
    fi
else
    echo "✅ Models are available:"
    ollama list
fi

# Set environment variable
echo "🔧 Configuring environment..."
export USE_LOCAL_LLM=true

echo ""
echo "🎉 Setup complete! Your chat with PDF app is now configured to use local LLM."
echo ""
echo "📝 To use local LLM:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. Set environment variable: export USE_LOCAL_LLM=true"
echo "3. Restart your backend server"
echo ""
echo "💡 Available models:"
ollama list

echo ""
echo "🔗 Useful Ollama commands:"
echo "   ollama list                    # Show installed models"
echo "   ollama pull <model>           # Download a model"
echo "   ollama run <model>            # Test a model interactively"
echo "   ollama rm <model>             # Remove a model"
