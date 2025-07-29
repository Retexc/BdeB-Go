@echo off
cd /d "%~dp0"

rem ── Start the Python backend in its own window
start "Backend" cmd /k "python tray_launcher.py"

rem ── Start the Vue dev server in its own window
start "Frontend" cmd /k "cd admin-frontend && npm run dev"

rem ── Wait a couple seconds then open the Vue console page
timeout /t 3 /nobreak >nul
start "" "http://localhost:5173/console"

exit
