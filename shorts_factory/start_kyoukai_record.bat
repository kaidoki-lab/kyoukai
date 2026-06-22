@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo KYOUKAI Shorts Factory - START RECORD
echo ========================================
echo.

:: ── Python パス解決 ──────────────────────────────────────────
set "PYTHON_EXE="
if exist "C:\Users\pc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" set "PYTHON_EXE=C:\Users\pc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "C:\Users\pc\AppData\Local\Programs\Python\Python315\python.exe" set "PYTHON_EXE=C:\Users\pc\AppData\Local\Programs\Python\Python315\python.exe"
if "%PYTHON_EXE%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_EXE=python"
)
if "%PYTHON_EXE%"=="" (
  echo ERROR: Python not found.
  pause
  exit /b 1
)

:: ── 今日のシナリオ生成（ホットスポット同期も内部で実行される） ──
echo [1/4] Generating today's scenario...
"%PYTHON_EXE%" generate_scenario.py
if errorlevel 1 (
  echo.
  echo WARNING: Scenario generation failed. Continuing anyway.
)
echo.

:: ── OBS 録画開始 ──────────────────────────────────────────────
echo [2/4] Starting OBS recording...
node tools\obs_control.js start
if errorlevel 1 (
  echo.
  echo ERROR: Could not start OBS recording.
  echo Make sure OBS is running and WebSocket is enabled.
  pause
  exit /b 1
)
echo.

:: ── Ctrl+Shift マーカーホットキー起動 ─────────────────────────
echo [3/4] Starting marker hotkey listener...
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File tools\marker_hotkey.ps1
echo.

:: ── ブラウザとシナリオを開く ──────────────────────────────────
echo [4/4] Opening KYOUKAI and today's scenario...
start "" "https://www.void-kyoukai.net/"
if exist "today_scenario.txt" (
  start "" notepad "today_scenario.txt"
)
echo.

echo ========================================
echo Recording started.
echo Follow today_scenario.txt to browse KYOUKAI.
echo Hold Ctrl+Shift (0.35s) to mark clip points.
echo Run stop_kyoukai_record.bat when done.
echo ========================================
echo.
