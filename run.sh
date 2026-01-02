#!/bin/bash

# Simple run script for SEO-GEO-AEO API with Frontend

echo "🚀 Starting SEO-GEO-AEO API with Frontend..."
echo ""

# Navigate to the correct directory
cd "$(dirname "$0")/project/project"

# Check if we're in the right place
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found!"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Installing dependencies..."
    pip install --user -r ../requirements.txt
fi

# Start the server
echo "✅ Starting server on http://localhost:8001"
echo "📱 Frontend will be available at http://localhost:8001"
echo "📚 API docs at http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
