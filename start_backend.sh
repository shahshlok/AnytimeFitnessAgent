#!/bin/bash

# Anytime Fitness AI Agent - Backend Startup Script

echo "Starting Anytime Fitness AI Agent Backend..."
echo "==============================================="

# Navigate to backend directory
cd ai_agent/backend

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r ../../requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please create .env file with required environment variables."
    echo "See deploy.md for configuration details."
    exit 1
fi

# Start the server
echo "Starting backend server..."
echo "Backend will be available at: http://0.0.0.0:7479"
echo "Health check: http://0.0.0.0:7479/health"
echo "Logs will be written to: /tmp/af_backend.log"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python start_server.py