@echo off
echo ========================================
echo   Multi-Engine TTS - Installation Script
echo   FREE Text-to-Speech Application
echo   Edge TTS (Online) + Piper TTS (Offline)
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found!
echo.

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
call venv\Scripts\pip.exe install --upgrade pip
call venv\Scripts\pip.exe install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Downloading Bundled Piper Voices
echo ========================================
echo.

:: Create models directory
if not exist "models\piper" mkdir models\piper

:: Download bundled voices using Python script
echo Downloading high-quality Piper voices (this may take a few minutes)...
call venv\Scripts\python.exe -c "from tts_engines import PiperTTSEngine; e = PiperTTSEngine(); [e.download_voice(v, lambda p, s: print(f'  {s}')) for v in e.get_bundled_voices()]"

if errorlevel 1 (
    echo WARNING: Some voices may not have downloaded successfully
    echo You can download them later from the application
    echo.
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Features:
echo   - Edge TTS: Microsoft Neural Voices (Online)
echo   - Piper TTS: High-Quality Local Voices (Offline)
echo.
echo To run the application, double-click: run.bat
echo.
pause
