#!/bin/bash

echo "🔧 Setting up Mistral API integration for Chat with PDF"
echo "======================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "📄 .env file already exists"
fi

# Function to update or add environment variable
update_env_var() {
    local var_name=$1
    local var_value=$2
    local env_file=".env"
    
    if grep -q "^${var_name}=" "$env_file"; then
        # Variable exists, update it
        sed -i "s/^${var_name}=.*/${var_name}=${var_value}/" "$env_file"
        echo "✅ Updated ${var_name} in .env"
    else
        # Variable doesn't exist, add it
        echo "${var_name}=${var_value}" >> "$env_file"
        echo "✅ Added ${var_name} to .env"
    fi
}

# Check if MISTRAL_API_KEY is provided as argument
if [ "$1" ]; then
    echo "🔑 Setting up Mistral API key..."
    update_env_var "MISTRAL_API_KEY" "$1"
    update_env_var "LLM_PROVIDER" "mistral"
    echo "✅ Mistral API key configured"
else
    echo "⚠️  No API key provided"
    echo "📝 To configure Mistral API:"
    echo "   1. Get your API key from: https://console.mistral.ai/"
    echo "   2. Run: ./setup_mistral.sh YOUR_API_KEY"
    echo "   3. Or manually edit .env file and set MISTRAL_API_KEY=your_key_here"
fi

echo ""
echo "🧪 Testing Mistral API connection..."
cd backend

# Test if the API key works (only if provided)
if [ "$1" ]; then
    python3 -c "
import os
os.environ['MISTRAL_API_KEY'] = '$1'

try:
    from app.services.mistral_service import MistralService
    mistral = MistralService()
    result = mistral.test_connection()
    
    if result['success']:
        print('✅ Mistral API connection successful!')
        print(f'   Model: {result.get(\"model\", \"unknown\")}')
        print(f'   Response: {result.get(\"response\", \"No response\")}')
    else:
        print('❌ Mistral API connection failed:')
        print(f'   Error: {result.get(\"error\", \"Unknown error\")}')
        exit(1)
        
except Exception as e:
    print(f'❌ Error testing Mistral API: {e}')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        echo "✅ Mistral integration setup completed successfully!"
        echo ""
        echo "🚀 Available Mistral models:"
        echo "   • mistral-tiny: Fastest and cheapest"
        echo "   • mistral-small-latest: Good balance (default)"
        echo "   • mistral-medium-latest: Better performance"
        echo "   • mistral-large-latest: Best performance"
        echo ""
        echo "💡 The system will automatically use Mistral API when available"
        echo "   You can also switch providers at runtime using the API endpoints"
        echo ""
        echo "🔗 Next steps:"
        echo "   1. Start the backend: cd backend && uvicorn main:app --reload"
        echo "   2. Test the /health endpoint to verify LLM provider"
        echo "   3. Upload a document and start chatting!"
    else
        echo "❌ Setup failed. Please check your API key and try again."
    fi
else
    echo "⏭️  Skipping connection test (no API key provided)"
    echo ""
    echo "📋 Setup summary:"
    echo "   • Enhanced LangChain agent with Mistral support: ✅"
    echo "   • Environment file: ✅"
    echo "   • API key: ⚠️  (needs to be configured)"
    echo ""
    echo "🔑 To complete setup:"
    echo "   1. Get API key from https://console.mistral.ai/"
    echo "   2. Run: ./setup_mistral.sh YOUR_API_KEY"
fi

cd ..

echo ""
echo "📖 Available API endpoints for Mistral:"
echo "   • POST /api/v1/mistral/test - Test Mistral connection"
echo "   • POST /api/v1/llm/switch - Switch LLM provider"
echo "   • GET  /api/v1/llm/providers - List available providers"
echo "   • GET  /api/v1/health - Check system health with LLM info"
