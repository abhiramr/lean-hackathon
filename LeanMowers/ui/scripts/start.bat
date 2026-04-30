@echo off
chcp 65001 >nul 2>&1

echo.
echo  ================================================================
echo    VERIFIED EDA - Starting Application
echo  ================================================================
echo.

cd /d "%~dp0\.."

echo Checking Python dependencies...
pip install -r backend\requirements.txt -q 2>nul
echo   Python ready

echo Checking Node.js dependencies...
if not exist node_modules (
    echo   Installing frontend packages...
    call npm install --silent
)
echo   Node.js ready

echo.
echo Starting servers...
echo   Backend:  http://localhost:8420
echo   Frontend: http://localhost:5173
echo.

start "VerifiedEDA-Backend" cmd /c "python backend\server.py"
timeout /t 3 /nobreak >nul
start "VerifiedEDA-Frontend" cmd /c "npx vite --host"
timeout /t 3 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo  ================================================================
echo   Verified EDA is running!
echo   Press any key to shut down.
echo  ================================================================
pause

taskkill /fi "WINDOWTITLE eq VerifiedEDA-Backend" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq VerifiedEDA-Frontend" /f >nul 2>&1
