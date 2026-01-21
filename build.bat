@echo off
echo ========================================
echo  Gemini Cowork - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/4] Installing PyInstaller...
pip install pyinstaller

echo.
echo [3/4] Building executable...
pyinstaller --onefile --windowed --name "GeminiCowork" --clean main.py ^
    --hidden-import customtkinter ^
    --hidden-import google.generativeai ^
    --hidden-import PIL ^
    --hidden-import pygments

echo.
echo [4/4] Build complete!
echo.
echo ----------------------------------------
echo  Output: dist\GeminiCowork.exe
echo ----------------------------------------
echo.

if exist "dist\GeminiCowork.exe" (
    echo SUCCESS: Executable created successfully!
    echo Location: %cd%\dist\GeminiCowork.exe
) else (
    echo ERROR: Build failed. Check the output above for errors.
)

echo.
pause
