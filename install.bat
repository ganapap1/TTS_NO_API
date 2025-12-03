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

:: Create virtual environment (check if already exists)
if exist "venv\" (
    echo Virtual environment already exists.
) else (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo.
echo Installing dependencies...
call venv\Scripts\pip.exe install --upgrade pip
call venv\Scripts\pip.exe install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Failed to install dependencies
    echo ========================================
    echo.
    echo Common solutions:
    echo 1. Check your internet connection
    echo 2. Run as Administrator
    echo 3. Disable antivirus temporarily
    echo 4. Try: venv\Scripts\pip.exe install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo Verifying installations...
echo Checking edge-tts...
call venv\Scripts\python.exe -c "import edge_tts; print('  ✓ edge-tts installed successfully')" 2>nul
if errorlevel 1 (
    echo   ✗ WARNING: edge-tts not found. Attempting to fix...
    call venv\Scripts\pip.exe install edge-tts
    call venv\Scripts\python.exe -c "import edge_tts; print('  ✓ Fixed! edge-tts now working')" 2>nul
    if errorlevel 1 (
        echo   ✗ FAILED: edge-tts still not working
    )
)

echo Checking customtkinter...
call venv\Scripts\python.exe -c "import customtkinter; print('  ✓ customtkinter installed successfully')" 2>nul
if errorlevel 1 (
    echo   ✗ WARNING: customtkinter not found. Attempting to fix...
    call venv\Scripts\pip.exe install customtkinter
    call venv\Scripts\python.exe -c "import customtkinter; print('  ✓ Fixed! customtkinter now working')" 2>nul
    if errorlevel 1 (
        echo   ✗ FAILED: customtkinter still not working
    )
)

echo Checking piper-tts...
call venv\Scripts\python.exe -c "import piper; print('  ✓ piper-tts installed successfully')" 2>nul
if errorlevel 1 (
    echo   ✗ WARNING: piper-tts not found or failed to load
    echo.
    echo   Attempting to fix piper-tts installation...
    echo   Trying method 1: Standard install
    call venv\Scripts\pip.exe install piper-tts

    echo   Verifying fix...
    call venv\Scripts\python.exe -c "import piper; print('  ✓ Fixed! piper-tts now working')" 2>nul
    if errorlevel 1 (
        echo   ✗ Method 1 failed. Trying method 2: Force reinstall with no cache
        call venv\Scripts\pip.exe install piper-tts --no-cache-dir --force-reinstall

        echo   Verifying fix...
        call venv\Scripts\python.exe -c "import piper; print('  ✓ Fixed! piper-tts now working')" 2>nul
        if errorlevel 1 (
            echo.
            echo   ✗ FAILED: Unable to install piper-tts automatically
            echo.
            echo   This is a critical component for offline TTS.
            echo   Please check:
            echo   1. Python version: python --version (requires 3.8+)
            echo   2. Internet connection
            echo   3. Antivirus/Firewall blocking installation
            echo   4. Run as Administrator and try again
            echo.
            set PIPER_INSTALL_FAILED=1
        )
    )
)

echo Checking langdetect...
call venv\Scripts\python.exe -c "import langdetect; print('  ✓ langdetect installed successfully')" 2>nul
if errorlevel 1 (
    echo   ✗ WARNING: langdetect not found. Attempting to fix...
    call venv\Scripts\pip.exe install langdetect
    call venv\Scripts\python.exe -c "import langdetect; print('  ✓ Fixed! langdetect now working')" 2>nul
    if errorlevel 1 (
        echo   ✗ FAILED: langdetect still not working
    )
)

echo.
echo ========================================
echo   Downloading Bundled Piper Voices
echo ========================================
echo.

:: Create models directory
if not exist "models\piper" mkdir models\piper

:: Skip voice download if piper-tts installation failed
if defined PIPER_INSTALL_FAILED (
    echo.
    echo SKIPPING: Voice download because piper-tts is not installed
    echo Fix piper-tts installation first, then download voices from the app
    echo.
    goto :skip_voice_download
)

:: Download bundled voices using Python script
echo Downloading high-quality Piper voices (this may take a few minutes)...
call venv\Scripts\python.exe -c "from tts_engines import PiperTTSEngine; e = PiperTTSEngine(); [e.download_voice(v, lambda p, s: print(f'  {s}')) for v in e.get_bundled_voices()]"

if errorlevel 1 (
    echo.
    echo WARNING: Some voices may not have downloaded successfully
    echo You can download them later from the application
    echo.
)

:skip_voice_download

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.

:: Show final status
if defined PIPER_INSTALL_FAILED (
    echo STATUS: Partial installation
    echo   ✓ Edge TTS is ready (Online)
    echo   ✗ Piper TTS needs fixing (Offline)
    echo.
    echo ACTION REQUIRED:
    echo   Please fix piper-tts installation manually:
    echo   1. Open Command Prompt as Administrator
    echo   2. Run: cd "%CD%"
    echo   3. Run: venv\Scripts\pip.exe install piper-tts
    echo   4. Run: venv\Scripts\python.exe -c "import piper"
    echo.
) else (
    echo STATUS: Full installation successful!
    echo   ✓ Edge TTS: Microsoft Neural Voices (Online)
    echo   ✓ Piper TTS: High-Quality Local Voices (Offline)
    echo   ✓ Multi-language support (90+ languages)
    echo.
)

echo To run the application, double-click: run.bat
echo For troubleshooting, check README.md
echo.
pause
