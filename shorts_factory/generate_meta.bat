@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo KYOUKAI Shorts Factory - GENERATE META
echo ========================================
echo.
echo finished_shorts/ に完成した動画を入れてから実行してください。
echo.

python generate_meta.py
if errorlevel 1 (
  echo ERROR: メタ生成に失敗しました。
  pause
  exit /b 1
)

echo.
echo output_meta/ を開きます。
start "" "%~dp0output_meta"
pause
