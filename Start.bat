@echo off
cd /d "%~dp0\src\bdeb_gtfs"

waitress-serve --host=127.0.0.1 --port=5001 bdeb_gtfs.admin:app
