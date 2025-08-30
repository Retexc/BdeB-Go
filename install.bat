@echo off
setlocal enabledelayedexpansion
echo ================================
echo BdeB-Go Setup
echo ================================
echo.

REM Check if everything is already set up
set SETUP_COMPLETE=1

REM Check if Node.js is installed
echo [1/7] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo Download the LTS version and run the installer.
    echo After installation, restart this script.
    echo.
    pause
    exit /b 1
) else (
    echo ✓ Node.js is installed
    node --version
)

REM Check if Python is installed
echo.
echo [2/7] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo After installation, restart this script.
    echo.
    pause
    exit /b 1
) else (
    echo ✓ Python is installed
    python --version
)

REM Check if Python dependencies are installed
echo.
echo [3/7] Checking Python dependencies...
if not exist "backend\requirements.txt" (
    echo ERROR: requirements.txt not found in backend folder
    set SETUP_COMPLETE=0
) else (
    pushd backend
    pip list >nul 2>&1
    if %errorlevel% neq 0 (
        echo Installing Python requirements...
        pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo WARNING: Some Python dependencies may have failed to install
            set SETUP_COMPLETE=0
        )
    ) else (
        echo ✓ Python dependencies are available
    )
    popd
)

REM Check if Node.js dependencies are installed
echo.
echo [4/7] Checking Node.js dependencies...
if not exist "UI\package.json" (
    echo ERROR: package.json not found in UI folder
    set SETUP_COMPLETE=0
) else (
    if not exist "UI\node_modules" (
        echo Installing Node.js dependencies...
        pushd UI
        npm install
        if %errorlevel% neq 0 (
            echo WARNING: Some Node.js dependencies may have failed to install
            set SETUP_COMPLETE=0
        ) else (
            echo ✓ Node.js dependencies installed
        )
        popd
    ) else (
        echo ✓ Node.js dependencies are installed
    )
)

REM Check if frontend is built
echo.
echo [5/7] Checking frontend build...
if exist "UI\dist" (
    echo ✓ Frontend is built
) else (
    echo Building frontend...
    pushd UI
    npm run build
    if %errorlevel% neq 0 (
        echo WARNING: Frontend build failed
        set SETUP_COMPLETE=0
    ) else (
        echo ✓ Frontend built successfully
    )
    popd
)

REM Check if start.bat exists
echo.
echo [6/7] Checking start script...
if exist "start.bat" (
    echo ✓ start.bat already exists
) else (
    echo Creating start.bat...
    (
    echo @echo off
    echo echo ================================
    echo echo Bdeb-Go
    echo echo ================================
    echo echo.
    echo echo Starting application...
    echo echo.
    echo echo Backend: http://localhost:5001
    echo echo Frontend: http://localhost:4173/console
    echo echo.
    echo echo Press Ctrl+C to stop the application.
    echo echo ================================
    echo echo.
    echo.
    echo cd UI
    echo npm run start
    echo.
    echo echo.
    echo echo Application stopped.
    echo pause
    ) > start.bat
    echo Created start.bat
)

REM Final status and options
echo.
echo [7/7] Setup complete!
echo ================================
echo.

if !SETUP_COMPLETE!==1 (
    echo Everything is ready to go!
    echo.
    echo Options:
    echo   1. Start the application now
    echo   2. Exit ^(use start.bat later^)
    echo.
    set /p choice="Enter your choice (1 or 2): "
    if "!choice!"=="1" (
        echo.
        echo Starting application...
        cd UI
        npm run start
        goto :end
    ) else (
        echo.
        echo Use start.bat to launch the application anytime.
        goto :end
    )
) else (
    echo Some issues were encountered during setup.
    echo Please check the messages above and try again.
    echo.
    echo You can still try to start the application with:
    echo   cd UI
    echo   npm run start
)

:end
echo.
echo Press any key to close this window...
pause >nul