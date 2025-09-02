@echo off
setlocal enabledelayedexpansion

REM Check if running in silent mode (for automated updates)
set SILENT_MODE=0
if "%1"=="silent" set SILENT_MODE=1

if %SILENT_MODE%==0 (
    for /f %%A in ('echo prompt $E ^| cmd') do set "ESC=%%A"
    set "GREEN=%ESC%[32m"
    set "RED=%ESC%[31m"
    set "YELLOW=%ESC%[33m"
    set "BLUE=%ESC%[34m"
    set "RESET=%ESC%[0m"
) else (
    set "GREEN="
    set "RED="
    set "YELLOW="
    set "BLUE="
    set "RESET="
)

if %SILENT_MODE%==0 (
    echo ================================
    echo BdeB-Go Setup
    echo ================================
    echo.
) else (
    echo [AUTO-UPDATE] BdeB-Go automated update started...
)

REM Check if everything is already set up
set SETUP_COMPLETE=1

REM Check if Node.js is installed
if %SILENT_MODE%==0 (
    echo [1/7] Checking Node.js installation...
) else (
    echo [AUTO-UPDATE] Checking Node.js...
)
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%RESET% Node.js is not installed!
    if %SILENT_MODE%==0 (
        echo.
        echo Please install Node.js from: https://nodejs.org/
        echo Download the LTS version and run the installer.
        echo After installation, restart this script.
        echo.
        pause
    )
    exit /b 1
) else (
    if %SILENT_MODE%==0 (
        echo %GREEN%[OK]%RESET% Node.js is installed
        node --version
    ) else (
        echo [AUTO-UPDATE] Node.js is available
    )
)

REM Check if Python is installed
if %SILENT_MODE%==0 (
    echo.
    echo [2/7] Checking Python installation...
) else (
    echo [AUTO-UPDATE] Checking Python...
)
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%RESET% Python is not installed!
    if %SILENT_MODE%==0 (
        echo.
        echo Please install Python from: https://python.org/
        echo Make sure to check "Add Python to PATH" during installation.
        echo After installation, restart this script.
        echo.
        pause
    )
    exit /b 1
) else (
    if %SILENT_MODE%==0 (
        echo %GREEN%[OK]%RESET% Python is installed
        python --version
    ) else (
        echo [AUTO-UPDATE] Python is available
    )
)

REM Install Python dependencies
if %SILENT_MODE%==0 (
    echo.
    echo [3/7] Installing Python dependencies...
) else (
    echo [AUTO-UPDATE] Installing Python dependencies...
)
if not exist "backend\requirements.txt" (
    echo %RED%[ERROR]%RESET% requirements.txt not found in backend folder
    set SETUP_COMPLETE=0
) else (
    if %SILENT_MODE%==0 (
        echo %BLUE%[INFO]%RESET% Installing Python requirements...
    )
    pushd backend
    if %SILENT_MODE%==1 (
        python -m pip install --upgrade pip --quiet >nul 2>&1
        python -m pip install -r requirements.txt --quiet
    ) else (
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
    )
    if %errorlevel% neq 0 (
        echo %RED%[ERROR]%RESET% Python dependencies installation failed
        set SETUP_COMPLETE=0
    ) else (
        if %SILENT_MODE%==0 (
            echo %GREEN%[COMPLETE]%RESET% Python dependencies installed successfully
        ) else (
            echo [AUTO-UPDATE] Python dependencies installed
        )
    )
    popd
)

REM Check if Node.js dependencies are installed
if %SILENT_MODE%==0 (
    echo.
    echo [4/7] Installing Node.js dependencies...
) else (
    echo [AUTO-UPDATE] Installing Node.js dependencies...
)
if not exist "UI\package.json" (
    echo %RED%[ERROR]%RESET% package.json not found in UI folder
    set SETUP_COMPLETE=0
) else (
    pushd UI
    if not exist "node_modules" (
        if %SILENT_MODE%==0 (
            echo %BLUE%[INFO]%RESET% Installing Node.js dependencies...
            npm install
        ) else (
            npm install --silent >nul 2>&1
        )
        if %errorlevel% neq 0 (
            if %SILENT_MODE%==0 (
                echo %YELLOW%[WARNING]%RESET% Some Node.js dependencies may have failed to install
            ) else (
                echo [AUTO-UPDATE] Node.js dependencies installation had issues
            )
            set SETUP_COMPLETE=0
        ) else (
            if %SILENT_MODE%==0 (
                echo %GREEN%[COMPLETE]%RESET% Node.js dependencies installed
            ) else (
                echo [AUTO-UPDATE] Node.js dependencies installed
            )
        )
    ) else (
        if %SILENT_MODE%==0 (
            echo %GREEN%[COMPLETE]%RESET% Node.js dependencies already installed
        ) else (
            echo [AUTO-UPDATE] Node.js dependencies already available
        )
    )
    popd
)

REM Build frontend (always rebuild in silent mode for updates)
if %SILENT_MODE%==0 (
    echo.
    echo [5/7] Building frontend...
) else (
    echo [AUTO-UPDATE] Rebuilding frontend...
)

pushd UI
if %SILENT_MODE%==1 (
    REM In silent mode, always rebuild
    if exist "dist" (
        echo [AUTO-UPDATE] Removing old dist folder...
        rmdir /s /q "dist" >nul 2>&1
    )
    echo [AUTO-UPDATE] Building frontend...
    npm run build --silent >nul 2>&1
    if %errorlevel% neq 0 (
        echo %RED%[ERROR]%RESET% Frontend build failed
        set SETUP_COMPLETE=0
    ) else (
        echo [AUTO-UPDATE] Frontend built successfully
    )
) else (
    REM In interactive mode, check if already built
    if exist "dist" (
        echo %GREEN%[COMPLETE]%RESET% Frontend already built
    ) else (
        echo %BLUE%[INFO]%RESET% Building frontend...
        npm run build
        if %errorlevel% neq 0 (
            echo %RED%[ERROR]%RESET% Frontend build failed
            set SETUP_COMPLETE=0
        ) else (
            echo %GREEN%[COMPLETE]%RESET% Frontend built successfully
        )
    )
)
popd

REM Check if start.bat exists (skip in silent mode)
if %SILENT_MODE%==0 (
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
)

REM Test Python dependencies
if %SILENT_MODE%==0 (
    echo.
    echo [7/7] Verifying installation...
    echo %BLUE%[INFO]%RESET% Testing Python dependencies...
) else (
    echo [AUTO-UPDATE] Verifying installation...
)
pushd backend
python -c "import flask; print('Flask:', flask.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%RESET% Flask is not properly installed
    if %SILENT_MODE%==0 (
        echo %BLUE%[INFO]%RESET% Attempting to fix...
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt --force-reinstall
    ) else (
        echo [AUTO-UPDATE] Fixing Flask installation...
        python -m pip install --upgrade pip --quiet >nul 2>&1
        python -m pip install -r requirements.txt --force-reinstall --quiet >nul 2>&1
    )
    if %errorlevel% neq 0 (
        echo %RED%[ERROR]%RESET% Could not install Flask properly
        set SETUP_COMPLETE=0
    ) else (
        if %SILENT_MODE%==0 (
            echo %GREEN%[COMPLETE]%RESET% Flask installed successfully
        ) else (
            echo [AUTO-UPDATE] Flask installed successfully
        )
    )
) else (
    if %SILENT_MODE%==0 (
        echo %GREEN%[COMPLETE]%RESET% Python dependencies verified
    ) else (
        echo [AUTO-UPDATE] Dependencies verified
    )
)
popd

REM Final status and options
if %SILENT_MODE%==0 (
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
) else (
    REM Silent mode - just exit with status
    if !SETUP_COMPLETE!==1 (
        echo [AUTO-UPDATE] Update completed successfully
        exit /b 0
    ) else (
        echo [AUTO-UPDATE] Update completed with issues
        exit /b 1
    )
)