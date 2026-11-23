@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 홈핏 메이트 exe 만들기

set PY=
where py >nul 2>nul && set PY=py
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo 파이썬을 먼저 설치해주세요: https://www.python.org/downloads/
  pause
  exit /b
)

echo exe 파일을 만드는 중이에요. 1~2분 걸려요...
%PY% -m pip install -q -r requirements.txt pyinstaller
%PY% -m PyInstaller --noconfirm --onefile --name HomeFitMate --icon static\icon.ico --add-data "templates;templates" --add-data "static;static" --add-data "data\exercises.json;data" launcher.py

if exist dist\HomeFitMate.exe (
  echo.
  echo 완성! dist 폴더의 HomeFitMate.exe를 더블클릭하면 실행돼요.
  explorer dist
) else (
  echo exe 만들기에 실패했어요. 위의 오류 메시지를 확인해주세요.
)
pause
