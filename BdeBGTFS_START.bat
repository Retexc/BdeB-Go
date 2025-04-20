@echo off
rem ─ Change directory to where your admin.py lives
cd /d "%~dp0"

rem ─ OPTIONAL: activate your virtualenv if you have one
if exist "%~dp0venv\Scripts\activate.bat" (
  call "%~dp0venv\Scripts\activate.bat"
)

rem ─ Serve the admin Flask app with Waitress
waitress-serve --host=0.0.0.0 --port=5001 admin:app

rem ─ Pause so you can see any errors
pause
