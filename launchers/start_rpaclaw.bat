@echo off
REM RPAclaw Launcher — Windows
title RPAclaw - Starting...

echo.
echo  =================================
echo   RPAclaw - Nanobot + RPA Platform
echo  =================================
echo.

REM Detect Python
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PY=python
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        set PY=python3
    ) else (
        echo [ERROR] Python 3.11+ not found.
        echo Install from https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

REM Get project directory (parent of launchers/)
set SCRIPT_DIR=%~dp0..

echo [*] Installing dependencies...
%PY% -m pip install -e "%SCRIPT_DIR%"
if %errorlevel% neq 0 (
    echo [!] pip install -e failed, trying pip install from requirements...
    %PY% -m pip install typer fastapi uvicorn pydantic pydantic-settings loguru httpx
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies.
        echo Please run manually: %PY% -m pip install -e "%SCRIPT_DIR%"
        pause
        exit /b 1
    )
)

echo [*] Checking Playwright browser...
%PY% -m playwright install chromium 2>nul

REM Build frontend if needed
if not exist "%SCRIPT_DIR%\frontend\dist" (
    echo [*] Building frontend...
    where npm >nul 2>&1
    if %errorlevel% equ 0 (
        cd /d "%SCRIPT_DIR%\frontend"
        call npm install
        call npx vite build
        cd /d "%SCRIPT_DIR%"
    ) else (
        echo [!] npm not found - frontend build skipped
        echo     Install Node.js from https://nodejs.org/ to build the frontend
    )
)

set HOST=127.0.0.1
set PORT=18790
if defined RPACLAW_HOST set HOST=%RPACLAW_HOST%
if defined RPACLAW_PORT set PORT=%RPACLAW_PORT%

echo.
echo [*] RPAclaw running at http://%HOST%:%PORT%
echo     Press Ctrl+C to stop
echo.

start http://%HOST%:%PORT%

%PY% -m rpaclaw.main start --host %HOST% --port %PORT%
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] RPAclaw failed to start.
    echo Please ensure all dependencies are installed:
    echo   %PY% -m pip install -e "%SCRIPT_DIR%"
)
pause
