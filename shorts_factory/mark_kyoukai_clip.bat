@echo off
setlocal
cd /d "%~dp0"

node tools\obs_control.js mark
if errorlevel 1 (
  echo MARK FAILED
  timeout /t 3 /nobreak >nul
  exit /b 1
)

echo CLIP MARKED
timeout /t 1 /nobreak >nul
