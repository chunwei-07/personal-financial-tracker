@echo off
echo Starting Financial Tracker...

REM This command changes to the target backend directory reliably
pushd "C:\Users\User\Desktop\Random Projects\financial_tracker\backend"

REM Check if the directory change was successful. If not, exit.
if %errorlevel% neq 0 (
    echo ERROR: Could not navigate to the project directory.
    echo Please check the path in the batch file.
    pause
    exit
)

echo Successfully navigated to backend directory.
echo Activating environment and starting server...

REM The path to 'activate' now starts with '..\' to go up one level from 'backend'
start "Financial Tracker Server" cmd /k "..\.venv\Scripts\activate && uvicorn app.main:app"

timeout /t 5 /nobreak > nul
start http://127.0.0.1:8000
exit