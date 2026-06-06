@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "BACKEND_URL=http://localhost:8000"
set "FRONTEND_URL=http://localhost:3000"

echo Starting agentic-ai-fraud-investigation-azure locally...
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python is not installed or not available on PATH.
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo ERROR: npm is not installed or not available on PATH.
  exit /b 1
)

if not exist "%BACKEND_DIR%\app\main.py" (
  echo ERROR: Backend app was not found at "%BACKEND_DIR%".
  exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
  echo ERROR: Frontend package.json was not found at "%FRONTEND_DIR%".
  exit /b 1
)

echo Backend will run at  %BACKEND_URL%
echo Frontend will run at %FRONTEND_URL%
echo.

start "Fraud Investigation Backend" cmd /k "cd /d "%BACKEND_DIR%" && python -m pip install -r requirements.txt && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

start "Fraud Investigation Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && if not exist node_modules npm install && npm run dev"

echo Local startup commands launched in separate windows.
echo Keep both windows open while using the app.
echo.
echo Open: %FRONTEND_URL%

endlocal
