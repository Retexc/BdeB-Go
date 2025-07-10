@echo off
rem ─── Step into your repo root ─────────────────────────────────────
cd /d "%~dp0"

rem ─── (Optional) activate virtualenv ──────────────────────────────
if exist "venv\Scripts\activate.bat" (
  call "venv\Scripts\activate.bat"
)

rem ─── Tell Python where to find your package ──────────────────────
set "PYTHONPATH=%CD%\src"

rem ─── Open the browser to your admin UI ──────────────────────────
echo Opening the admin UI at http://127.0.0.1:5001/…
start "" "http://127.0.0.1:5001/"

echo Initializing DB…
python -m bdeb_gtfs.scripts.init_db
if %ERRORLEVEL% neq 0 (
  echo DB init failed—aborting.
  pause
  exit /b %ERRORLEVEL%
)

rem ─── Run Waitress on bdeb_gfts.admin:app ─────────────────────────
echo Starting Waitress on http://127.0.0.1:5001/…
python -m waitress --host=127.0.0.1 --port=5001 bdeb_gtfs.admin:app

pause
