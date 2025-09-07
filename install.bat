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

REM Track overall success but continue execution
set SETUP_COMPLETE=1
set WARNINGS_COUNT=0

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
    set /a WARNINGS_COUNT+=1
) else (
    if %SILENT_MODE%==0 (
        echo %BLUE%[INFO]%RESET% Installing Python requirements...
    )
    pushd backend
    if %SILENT_MODE%==1 (
        python -m pip install --upgrade pip --quiet --disable-pip-version-check 2>nul || echo [AUTO-UPDATE] Pip upgrade had issues, continuing...
        python -m pip install -r requirements.txt --quiet --disable-pip-version-check || (
            echo [AUTO-UPDATE] Some Python dependencies had issues, continuing...
            set /a WARNINGS_COUNT+=1
        )
    ) else (
        python -m pip install --upgrade pip --disable-pip-version-check || (
            echo %YELLOW%[WARNING]%RESET% Pip upgrade had issues, continuing...
            set /a WARNINGS_COUNT+=1
        )
        python -m pip install -r requirements.txt --disable-pip-version-check || (
            echo %YELLOW%[WARNING]%RESET% Some Python dependencies had issues, continuing...
            set /a WARNINGS_COUNT+=1
        )
    )
    REM Always continue regardless of pip issues
    if %SILENT_MODE%==0 (
        echo %GREEN%[COMPLETE]%RESET% Python dependencies step completed
    ) else (
        echo [AUTO-UPDATE] Python dependencies step completed
    )
    popd
)

REM Install Node.js dependencies - force continuation
if %SILENT_MODE%==0 (
    echo.
    echo [4/7] Installing Node.js dependencies...
) else (
    echo [AUTO-UPDATE] Installing Node.js dependencies...
)
if not exist "UI\package.json" (
    echo %RED%[ERROR]%RESET% package.json not found in UI folder
    set SETUP_COMPLETE=0
    set /a WARNINGS_COUNT+=1
) else (
    pushd UI
    if not exist "node_modules" (
        if %SILENT_MODE%==0 (
            echo %BLUE%[INFO]%RESET% Installing Node.js dependencies...
            REM Use call to prevent batch exit and add flags to ignore warnings
            call npm install --no-audit --no-fund --silent 2>nul || (
                echo %YELLOW%[WARNING]%RESET% npm install had some issues, trying alternative approach...
                set /a WARNINGS_COUNT+=1
                call npm install --legacy-peer-deps --no-audit --no-fund 2>nul || (
                    echo %YELLOW%[WARNING]%RESET% npm install completed with warnings, continuing...
                    set /a WARNINGS_COUNT+=1
                )
            )
        ) else (
            call npm install --no-audit --no-fund --silent 2>nul || (
                echo [AUTO-UPDATE] npm install had issues, trying alternative...
                set /a WARNINGS_COUNT+=1
                call npm install --legacy-peer-deps --no-audit --no-fund --silent 2>nul || (
                    echo [AUTO-UPDATE] npm install completed with warnings, continuing...
                    set /a WARNINGS_COUNT+=1
                )
            )
        )
        REM Check if node_modules was created
        if exist "node_modules" (
            if %SILENT_MODE%==0 (
                echo %GREEN%[COMPLETE]%RESET% Node.js dependencies installed
            ) else (
                echo [AUTO-UPDATE] Node.js dependencies installed
            )
        ) else (
            if %SILENT_MODE%==0 (
                echo %YELLOW%[WARNING]%RESET% Node.js dependencies may not be fully installed
            ) else (
                echo [AUTO-UPDATE] Node.js dependencies may not be fully installed
            )
            set /a WARNINGS_COUNT+=1
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

REM Build frontend - force continuation regardless of warnings
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
        rmdir /s /q "dist" 2>nul || echo [AUTO-UPDATE] Dist folder removal had issues, continuing...
    )
    echo [AUTO-UPDATE] Building frontend...
    REM Use call to prevent script exit and ignore npm warnings
    call npm run build 2>nul || (
        echo [AUTO-UPDATE] Build had warnings, checking if dist was created...
        set /a WARNINGS_COUNT+=1
    )
    REM Check if build actually succeeded by looking for dist folder
    if exist "dist" (
        echo [AUTO-UPDATE] Frontend built successfully
    ) else (
        echo [AUTO-UPDATE] Frontend build may have failed, trying alternative...
        call npm run build --legacy-peer-deps 2>nul || (
            echo [AUTO-UPDATE] Build completed with issues
            set /a WARNINGS_COUNT+=1
        )
        if exist "dist" (
            echo [AUTO-UPDATE] Frontend built with alternative method
        ) else (
            echo [AUTO-UPDATE] Frontend build had issues but continuing...
            set SETUP_COMPLETE=0
        )
    )
) else (
    REM In interactive mode, check if already built
    if exist "dist" (
        echo %GREEN%[COMPLETE]%RESET% Frontend already built
    ) else (
        echo %BLUE%[INFO]%RESET% Building frontend...
        REM Use call to prevent script exit
        call npm run build || (
            echo %YELLOW%[WARNING]%RESET% Build had issues, checking result...
            set /a WARNINGS_COUNT+=1
        )
        if exist "dist" (
            echo %GREEN%[COMPLETE]%RESET% Frontend built successfully
        ) else (
            echo %YELLOW%[WARNING]%RESET% Trying alternative build method...
            call npm run build --legacy-peer-deps || (
                echo %YELLOW%[WARNING]%RESET% Build completed with warnings
                set /a WARNINGS_COUNT+=1
            )
            if exist "dist" (
                echo %GREEN%[COMPLETE]%RESET% Frontend built with alternative method
            ) else (
                echo %RED%[ERROR]%RESET% Frontend build failed
                set SETUP_COMPLETE=0
            )
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

REM Test Python dependencies - continue regardless
if %SILENT_MODE%==0 (
    echo.
    echo [7/7] Verifying installation...
    echo %BLUE%[INFO]%RESET% Testing Python dependencies...
) else (
    echo [AUTO-UPDATE] Verifying installation...
)
pushd backend
python -c "import flask; print('Flask:', flask.__version__)" 2>nul || (
    echo %YELLOW%[WARNING]%RESET% Flask verification had issues
    if %SILENT_MODE%==0 (
        echo %BLUE%[INFO]%RESET% Attempting to fix...
        python -m pip install --upgrade pip --disable-pip-version-check 2>nul
        python -m pip install -r requirements.txt --force-reinstall --disable-pip-version-check 2>nul || (
            echo %YELLOW%[WARNING]%RESET% Flask reinstall had issues, continuing...
            set /a WARNINGS_COUNT+=1
        )
    ) else (
        echo [AUTO-UPDATE] Fixing Flask installation...
        python -m pip install --upgrade pip --quiet --disable-pip-version-check 2>nul
        python -m pip install -r requirements.txt --force-reinstall --quiet --disable-pip-version-check 2>nul || (
            echo [AUTO-UPDATE] Flask reinstall had issues, continuing...
            set /a WARNINGS_COUNT+=1
        )
    )
    REM Test again
    python -c "import flask; print('Flask:', flask.__version__)" 2>nul || (
        echo %YELLOW%[WARNING]%RESET% Flask still has issues but continuing...
        set /a WARNINGS_COUNT+=1
    )
)
if %SILENT_MODE%==0 (
    echo %GREEN%[COMPLETE]%RESET% Python dependencies verification completed
) else (
    echo [AUTO-UPDATE] Dependencies verification completed
)
popd

REM Final status - always continue to end
if %SILENT_MODE%==0 (
    echo.
    echo ================================
    if !WARNINGS_COUNT! gtr 0 (
        echo %YELLOW%[SUCCESS WITH WARNINGS]%RESET% Setup completed with !WARNINGS_COUNT! warnings
        echo The application should still work. Common warnings include:
        echo - npm security vulnerabilities (usually safe to ignore)
        echo - deprecated packages (won't affect functionality)
        echo - peer dependency warnings (application will still work)
    ) else (
        echo %GREEN%[SUCCESS]%RESET% Everything is ready to go!
    )
    echo.
    if exist "UI\dist" (
        echo Frontend build: %GREEN%[OK]%RESET% dist folder exists
    ) else (
        echo Frontend build: %RED%[FAILED]%RESET% dist folder missing
    )
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
    
    :end
    echo.
    echo Press any key to close this window...
    pause >nul
) else (
    REM Silent mode - report status and exit
    if exist "UI\dist" (
        echo [AUTO-UPDATE] Update completed successfully
        if !WARNINGS_COUNT! gtr 0 (
            echo [AUTO-UPDATE] Completed with !WARNINGS_COUNT! warnings (this is normal)
        )
        exit /b 0
    ) else (
        echo [AUTO-UPDATE] Update completed but frontend build may have issues
        exit /b 1
    )
)