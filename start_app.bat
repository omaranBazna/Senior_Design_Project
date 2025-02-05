@echo off
cd /d %~dp0
start cmd /k "python index.py"
timeout /t 3 /nobreak >nul
start http://localhost:8000
