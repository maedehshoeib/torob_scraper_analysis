#!/bin/bash

# Torob Dashboard Startup Script

echo "🚀 Starting Torob Market Geographical Dashboard..."

# Check if we're in the right directory
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the torob_dashboard directory"
    exit 1
fi

# Function to check if port is available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check ports
echo "🔍 Checking ports..."
if ! check_port 8000; then
    echo "Backend port 8000 is occupied. Please stop the service or change the port."
fi

if ! check_port 3000; then
    echo "Frontend port 3000 is occupied. Please stop the service or change the port."
fi

# Start Backend
echo "🐍 Starting FastAPI Backend..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait a bit for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
    echo "📊 API Documentation: http://localhost:8000/docs"
else
    echo "❌ Backend failed to start"
fi

cd ..

# Start Frontend (if npm is available)
if command -v npm &> /dev/null; then
    echo "⚛️  Starting React Frontend..."
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing dependencies..."
        npm install
    fi
    
    npm start &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    
    echo "✅ Frontend will be available at http://localhost:3000"
    cd ..
else
    echo "⚠️  npm not found. Please install Node.js to run the frontend."
    echo "You can still use the API at http://localhost:8000"
fi

echo ""
echo "🎉 Dashboard Setup Complete!"
echo ""
echo "📱 Services:"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
if command -v npm &> /dev/null; then
    echo "   - Frontend: http://localhost:3000"
fi
echo ""
echo "🛑 To stop services:"
echo "   kill $BACKEND_PID"
if command -v npm &> /dev/null; then
    echo "   kill $FRONTEND_PID"
fi
echo ""
echo "📊 Test the API:"
echo "   curl http://localhost:8000/api/health"
echo "   curl http://localhost:8000/api/analytics/overview"

# Keep script running
wait
