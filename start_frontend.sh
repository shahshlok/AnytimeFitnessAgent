#!/bin/bash

# Anytime Fitness AI Agent - Frontend Startup Script

echo "Starting Anytime Fitness AI Agent Frontend..."
echo "=============================================="

# Navigate to frontend directory
cd ai_agent/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Check if .env.production file exists
if [ ! -f ".env.production" ]; then
    echo "WARNING: .env.production file not found!"
    echo "Please create .env.production with your VM's IP address."
    echo "See deploy.md for configuration details."
    exit 1
fi

# Build for production
echo "Building for production..."
npm run build

# Start the preview server
echo "Starting frontend server..."
echo "Frontend will be available at: http://0.0.0.0:5173"
echo ""
echo "Make sure your backend is running on the configured port!"
echo "Press Ctrl+C to stop the server"
echo ""

npm run preview -- --host 0.0.0.0 --port 5173