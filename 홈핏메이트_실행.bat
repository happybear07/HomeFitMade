@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 홈핏 메이트

set PY=
where py >nul 2>nul && set PY=py
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo 파이썬이 설치되어 있지 않아요.
  echo 열리는 페이지에서 Python을 설치할 때 "Add python.exe to PATH"를 꼭 체크하세요.
  start https://www.python.org/downloads/
  pause
  exit /b
)

echo 필요한 프로그램을 확인하는 중...
%PY% -m pip install -q -r requirements.txt
%PY% launcher.py
pause
