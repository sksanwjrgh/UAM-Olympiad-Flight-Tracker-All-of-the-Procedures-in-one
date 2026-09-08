@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"

where py >nul 2>&1
if %errorlevel%==0 (
  py -3 OpenSky_local_proxy.py
) else (
  where python >nul 2>&1
  if %errorlevel%==0 (
    python OpenSky_local_proxy.py
  ) else (
    echo Python 3가 필요합니다. https://www.python.org/downloads/ 에서 설치해 주세요.
  )
)

pause
