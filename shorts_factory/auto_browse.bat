@echo off
cd /d "%~dp0"

echo [1/2] Generating today's scenario...
python generate_scenario.py
if errorlevel 1 (
  echo.
  echo ERROR: Scenario generation failed.
  pause
  exit /b 1
)

echo.
echo [2/2] Starting auto browse and recording...
python auto_browse.py
pause
