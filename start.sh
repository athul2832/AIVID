#!/bin/bash

# Start the Python backend server
echo "Starting Python backend server..."
cd backend
python server.py &
BACKEND_PID=$!
cd ..

# Start the Next.js frontend
echo "Starting Next.js frontend..."
npm run dev

# Kill the backend when the frontend exits
kill $BACKEND_PID