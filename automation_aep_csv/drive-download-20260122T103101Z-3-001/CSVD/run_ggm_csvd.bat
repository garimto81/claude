:: run_ggm_csvd.bat  — 콘솔 유지 + 실시간 로그(-u)
@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found. PATH를 확인하세요.
  pause
  exit /b 1
)

:: 콘솔을 닫지 않고 유지(cmd /k), 파이썬 출력 버퍼링 해제(-u)
cmd /k python -u ggm_csvd.py
