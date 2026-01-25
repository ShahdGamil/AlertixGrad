@echo off
echo Starting InstaGuard AI Application...

REM Check MongoDB
echo Checking MongoDB...
net start MongoDB 2>nul
if errorlevel 1 echo MongoDB already running

REM Start AI Service
echo Starting AI Service (Docker)...
cd "C:\Users\acer\Desktop\App Grad H\ai-service"
start "AI Service" docker-compose up

REM Wait for AI service to load
echo Waiting 30 seconds for AI models to load...
timeout /t 30 /nobreak

REM Start Backend
echo Starting Backend...
cd "C:\Users\acer\Desktop\App Grad H\backend"
start "Backend" npm run dev

echo.
echo ================================
echo All services started!
echo ================================
echo.
echo Backend: http://localhost:5000
echo AI Service: http://localhost:5001
echo.
echo Press any key to open health checks...
pause

REM Open health checks
start http://localhost:5000/api/health
start http://localhost:5001/health
