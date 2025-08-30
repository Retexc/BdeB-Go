@echo off
echo ================================
echo Bdeb-Go
echo ================================
echo.
echo Starting application...
echo.
echo Backend: http://localhost:5001
echo Frontend: http://localhost:4173/console
echo.
echo Press Ctrl+C to stop the application.
echo ================================
echo.

cd UI
npm run start

echo.
echo Application stopped.
pause
