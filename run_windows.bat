@echo off
setlocal
cd /d "%~dp0"
py -3.12 -m venv .venv
if errorlevel 1 (echo Python 3.12 x64 is required.& pause & exit /b 1)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 (pause & exit /b 1)
python -m pip install -r requirements.txt
if errorlevel 1 (pause & exit /b 1)
python -m streamlit run app.py
pause
