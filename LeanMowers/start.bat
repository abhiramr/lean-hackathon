@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo  ================================================================
echo    VERIFIED EDA - Python x Lean 4 x Agentic AI
echo  ================================================================
echo.

cd /d "%~dp0"

REM == Step 1: Python venv ==
echo [1/5] Setting up Python virtual environment...
if not exist ".venv" (
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Python 3.11+ is required.
        echo Download from https://python.org
        pause
        exit /b 1
    )
)
call ".venv\Scripts\activate.bat"

REM == Step 2: Python packages ==
echo [2/5] Installing Python packages...
pip install -e ".[dev]" -q 2>nul
pip install -r "ui\backend\requirements.txt" -q 2>nul
python -c "import verified_eda; print('  verified_eda v' + verified_eda.__version__ + ' loaded')"
if errorlevel 1 (
    echo ERROR: Failed to install verified_eda
    pause
    exit /b 1
)



REM == Step 4: Node.js ==
echo [4/5] Setting up frontend...
pushd ui
if not exist "node_modules" (
    echo   Installing npm packages - first run may take a minute...
    call npm install --silent 2>nul
)
popd
echo   Node.js ready

REM == Step 5: Lean check ==
echo [5/5] Checking Lean 4...
where lean >nul 2>&1
if %errorlevel%==0 (
    echo   Lean 4 found
) else (
    echo   Lean 4 not installed - optional
)

echo.
echo  ================================================================
echo   Starting servers...
echo   Backend:  http://localhost:8420
echo   Frontend: http://localhost:5173
echo  ================================================================
echo.

REM == Start backend in a new window ==
start "VerifiedEDA-Backend" cmd /c "call .venv\Scripts\activate.bat && python ui\backend\server.py"

REM == Wait for backend ==
echo Waiting for backend to start...
set tries=0
:waitloop
timeout /t 1 /nobreak >nul
curl -s http://localhost:8420/api/health >nul 2>&1
if not errorlevel 1 (
    echo   Backend is ready
    goto :backendok
)
set /a tries+=1
if %tries% lss 20 goto :waitloop
echo   WARNING: Backend may not have started
:backendok

REM == Start frontend in a new window ==
start "VerifiedEDA-Frontend" cmd /c "cd ui && npx vite --host"

REM == Wait then open browser ==
timeout /t 5 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo  ================================================================
echo   Verified EDA is live at http://localhost:5173
echo.
echo   Two windows are running in the background:
echo     VerifiedEDA-Backend   (FastAPI on port 8420)
echo     VerifiedEDA-Frontend  (Vite on port 5173)
echo.
echo   Press any key here to shut down both servers.
echo  ================================================================
echo.
pause

REM == Cleanup ==
echo Shutting down...
taskkill /fi "WINDOWTITLE eq VerifiedEDA-Backend" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq VerifiedEDA-Frontend" /f >nul 2>&1
echo Done.
