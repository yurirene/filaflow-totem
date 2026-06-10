@echo off
setlocal

cd /d "%~dp0\.."

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate.bat

pip install -q -r requirements-build.txt

pyinstaller --clean --noconfirm totem.spec

echo.
echo Build concluido.
echo Executavel: dist\FilaflowTotem\FilaflowTotem.exe

endlocal
