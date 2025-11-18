@echo off
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

echo Starting Edge TTS - Free Text-to-Speech...
call venv\Scripts\python.exe edge_tts_gui.py

if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
