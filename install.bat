@echo off
setlocal
cd /d "%~dp0"
py -m venv .venv
if errorlevel 1 (
  echo Не удалось создать виртуальное окружение.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m pip install -U pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Не удалось установить зависимости.
  pause
  exit /b 1
)
echo.
echo Установка завершена.
echo Запуск: run.bat
pause
