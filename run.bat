@echo off
setlocal

set VENV_DIR=env

if not exist %VENV_DIR% (
    echo Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b
)

call %VENV_DIR%\Scripts\activate

echo Starting Service Status Tracker...
python StatusTracker.py

endlocal
pause