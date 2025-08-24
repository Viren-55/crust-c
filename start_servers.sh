#!/bin/bash

# 🎯 POC Outreach Workflow - Server Startup Script
# This script starts both the backend and frontend servers

echo "🚀 Starting POC Outreach Workflow servers..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your API keys. See README.md for details."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install backend dependencies
echo "📦 Installing backend dependencies..."
source venv/bin/activate
pip install -r poc-backend/requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd poc-frontend
npm install
cd ..

echo "✅ Dependencies installed successfully!"
echo ""
echo "🎯 Starting servers..."
echo "Backend will run on: http://localhost:8000"
echo "Frontend will run on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend in background
echo "🔧 Starting backend server..."
cd poc-backend
source ../venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend server..."
cd poc-frontend
npm start &
FRONTEND_PID=$!
cd ..

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

echo "✅ Both servers are running!"
echo "📊 Backend API docs: http://localhost:8000/docs"
echo "🌐 Frontend app: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for background processes
wait