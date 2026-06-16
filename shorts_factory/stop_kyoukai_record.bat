@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo KYOUKAI Shorts Factory - STOP RECORD
echo ========================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File tools\stop_marker_hotkey.ps1

node tools\obs_control.js stop
if errorlevel 1 (
  echo.
  echo ERROR: Could not stop recording.
  echo Check OBS WebSocket connection.
  pause
  exit /b 1
)

echo.
echo Running Shorts Factory...

set "PYTHON_EXE="
if exist "C:\Users\pc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" set "PYTHON_EXE=C:\Users\pc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "C:\Users\pc\AppData\Local\Programs\Python\Python315\python.exe" set "PYTHON_EXE=C:\Users\pc\AppData\Local\Programs\Python\Python315\python.exe"
if "%PYTHON_EXE%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_EXE=python"
)
if "%PYTHON_EXE%"=="" (
  echo ERROR: Python not found.
  echo Edit PYTHON_EXE in this BAT or add Python to PATH.
  pause
  exit /b 1
)

"%PYTHON_EXE%" main.py
if errorlevel 1 (
  echo.
  echo ERROR: Shorts generation failed.
  echo Check logs\process.log.
  pause
  exit /b 1
)

echo.
echo Done.
echo output_shorts:
echo   %cd%\output_shorts
echo output_meta:
echo   %cd%\output_meta
pause
