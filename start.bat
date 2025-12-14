@echo off
echo Starting Python backend server...
cd backend
start "Backend" python server.py
cd ..

echo Starting Next.js frontend...
npm run dev