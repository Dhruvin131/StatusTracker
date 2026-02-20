@echo off
setlocal

set VENV_DIR=env

echo ============================================
echo   Service Status Tracker - Environment Setup
echo ============================================

REM Check if virtual environment exists
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
call %VENV_DIR%\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ============================================
echo   Setup completed successfully.
echo ============================================

endlocal
pause