#!/bin/bash
# Start script for Coffee Grounds Container Designer web application

echo "==================================================="
echo "Coffee Grounds Container Designer"
echo "==================================================="
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed or not in PATH"
    exit 1
fi

# Check if cq environment exists
if ! conda env list | grep -q "^cq "; then
    echo "Error: conda environment 'cq' not found"
    echo "Please create it with: conda create -n cq -c conda-forge cadquery"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if backend dependencies are installed
echo "Checking backend dependencies..."
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment for backend..."
    python3 -m venv backend/venv
    source backend/venv/bin/activate
    pip install -r backend/requirements.txt
else
    source backend/venv/bin/activate
fi

# Check if frontend dependencies are installed
echo "Checking frontend dependencies..."
if [ ! -d "webapp/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd webapp
    npm install
    cd ..
fi

echo ""
echo "==================================================="
echo "Starting servers..."
echo "==================================================="
echo ""

# Start backend server in background
echo "Starting Flask backend on http://localhost:5000..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend server
echo "Starting React frontend on http://localhost:3000..."
cd webapp
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "==================================================="
echo "Servers started successfully!"
echo "==================================================="
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
