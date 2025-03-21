@echo off
cd /d "%~dp0"  REM Change directory to script location

:: Check if Python is installed
where python >nul 2>nul || (
    echo Python not found! Make sure it is installed.
    pause
    exit /b
)

:: Ensure the correct Python environment is used
echo Using Python at:
python -c "import sys; print(sys.executable)"

:: Install waitress if missing
python -m pip show waitress >nul 2>nul || (
    echo Installing Waitress...
    python -m pip install waitress
)

:: Start the server
echo Starting the application...
python app.py
pause
