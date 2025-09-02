@echo off
setlocal enabledelayedexpansion

for /f %%A in ('echo prompt $E ^| cmd') do set "ESC=%%A"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "RESET=%ESC%[0m"

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
    echo %RED%[ERROR]%RESET% Node.js is not installed!
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo Download the LTS version and run the installer.
    echo After installation, restart this script.
    echo.
    pause
    exit /b 1
) else (
    echo %GREEN%[OK]%RESET% Node.js is installed
    node --version
)

REM Check if Python is installed
echo.
echo [2/7] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%RESET% Python is not installed!
    echo.
    echo Please install Python from: https://python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo After installation, restart this script.
    echo.
    pause
    exit /b 1
) else (
    echo %GREEN%[OK]%RESET% Python is installed
    python --version
)

REM Install Python dependencies
echo.
echo [3/7] Installing Python dependencies...
if not exist "backend\requirements.txt" (
    echo %RED%[ERROR]%RESET% requirements.txt not found in backend folder
    set SETUP_COMPLETE=0
) else (
    echo %BLUE%[INFO]%RESET% Installing Python requirements...
    pushd backend
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo %RED%[ERROR]%RESET% Python dependencies installation failed
        set SETUP_COMPLETE=0
    ) else (
        echo %GREEN%[COMPLETE]%RESET% Python dependencies installed successfully
    )
    popd
)

REM Check if Node.js dependencies are installed
echo.
echo [4/7] Installing Node.js dependencies...
if not exist "UI\package.json" (
    echo %RED%[ERROR]%RESET% package.json not found in UI folder
    set SETUP_COMPLETE=0
) else (
    pushd UI
    if not exist "node_modules" (
        echo %BLUE%[INFO]%RESET% Installing Node.js dependencies...
        npm install
        if %errorlevel% neq 0 (
            echo %YELLOW%[WARNING]%RESET% Some Node.js dependencies may have failed to install
            set SETUP_COMPLETE=0
        ) else (
            echo %GREEN%[COMPLETE]%RESET% Node.js dependencies installed
        )
    ) else (
        echo %GREEN%[COMPLETE]%RESET% Node.js dependencies already installed
    )
    popd
)

REM Build frontend
echo.
echo [5/7] Building frontend...
if exist "UI\dist" (
    echo %GREEN%[COMPLETE]%RESET% Frontend already built
) else (
    echo %BLUE%[INFO]%RESET% Building frontend...
    pushd UI
    npm run build
    if %errorlevel% neq 0 (
        echo %RED%[ERROR]%RESET% Frontend build failed
        set SETUP_COMPLETE=0
    ) else (
        echo %GREEN%[COMPLETE]%RESET% Frontend built successfully
    )
    popd
)

REM Check if start.bat exists
echo.
echo [6/7] Creating start script...
if exist "start.bat" (
    echo %GREEN%[COMPLETE]%RESET% start.bat already exists
) else (
    echo %BLUE%[INFO]%RESET% Creating start.bat...
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
    echo %GREEN%[COMPLETE]%RESET% Created start.bat
)

REM Test Python dependencies
echo.
echo [7/7] Verifying installation...
echo %BLUE%[INFO]%RESET% Testing Python dependencies...
pushd backend
python -c "import flask; print('Flask:', flask.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%RESET% Flask is not properly installed
    echo %BLUE%[INFO]%RESET% Attempting to fix...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt --force-reinstall
    if %errorlevel% neq 0 (
        echo %RED%[ERROR]%RESET% Could not install Flask properly
        set SETUP_COMPLETE=0
    ) else (
        echo %GREEN%[COMPLETE]%RESET% Flask installed successfully
    )
) else (
    echo %GREEN%[COMPLETE]%RESET% Python dependencies verified
)
popd

REM Final status and options
echo.
echo ================================
if !SETUP_COMPLETE!==1 (
    echo %GREEN%[SUCCESS]%RESET% Everything is ready to go!
    echo.
    echo Options:
    echo   1. Start the application now
    echo   2. Exit (use start.bat later)
    echo.
    set /p choice="Enter your choice (1 or 2): "
    if "!choice!"=="1" (
        echo.
        echo %BLUE%[INFO]%RESET% Starting application...
        call start.bat
        goto :end
    ) else (
        echo.
        echo %GREEN%[INFO]%RESET% Use start.bat to launch the application anytime.
        goto :end
    )
) else (
    echo %YELLOW%[WARNING]%RESET% Some issues were encountered during setup.
    echo Please check the messages above and try again.
    echo.
    echo You can still try to start the application with:
    echo   %BLUE%start.bat%RESET%
    echo.
    echo Or manually install dependencies:
    echo   %BLUE%cd backend%RESET%
    echo   %BLUE%pip install -r requirements.txt%RESET%
)

:end
echo.
echo Press any key to close this window...
pause >nul