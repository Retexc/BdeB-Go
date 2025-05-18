@echo off
cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
  call "venv\Scripts\activate.bat"
)

rem ─ Open the admin in the default browser
echo Opening BdeB-GTFS Manager at http://127.0.0.1:5001/ in your browser...
start "" "http://127.0.0.1:5001/"

rem ─ Serve the admin Flask app with Waitress bound to localhost
echo Starting Waitress on http://127.0.0.1:5001/
waitress-serve --host=127.0.0.1 --port=5001 admin:app

pause
