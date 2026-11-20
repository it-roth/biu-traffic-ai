@echo off
cd /d "%~dp0"
echo [BIU Traffic AI] Starting Django Backend on http://localhost:8000 with Python 3.13...
.\django\Scripts\python.exe manage.py runserver 0.0.0.0:8000

