@echo off
setlocal enabledelayedexpansion

echo.
echo  ========================================
echo   Gemini Cowork - Windows Installer
echo  ========================================
echo.
echo  This will install Gemini Cowork on your system.
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo  Note: Running without admin rights.
    echo  Installation will be for current user only.
    echo.
)

REM Check Python
echo  [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python is not installed!
    echo  Please install Python 3.10 or later from:
    echo  https://www.python.org/downloads/
    echo.
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYVER=%%V
echo  Found Python %PYVER%

REM Set installation directory
set "INSTALL_DIR=%LOCALAPPDATA%\GeminiCowork"
echo.
echo  [2/5] Creating installation directory...
echo  Location: %INSTALL_DIR%

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\src" mkdir "%INSTALL_DIR%\src"
if not exist "%INSTALL_DIR%\src\ui" mkdir "%INSTALL_DIR%\src\ui"
if not exist "%INSTALL_DIR%\src\services" mkdir "%INSTALL_DIR%\src\services"
if not exist "%INSTALL_DIR%\src\tools" mkdir "%INSTALL_DIR%\src\tools"

REM Copy files
echo.
echo  [3/5] Copying application files...
copy /Y "main.py" "%INSTALL_DIR%\" >nul
copy /Y "requirements.txt" "%INSTALL_DIR%\" >nul
copy /Y "src\__init__.py" "%INSTALL_DIR%\src\" >nul
copy /Y "src\ui\*.py" "%INSTALL_DIR%\src\ui\" >nul
copy /Y "src\services\*.py" "%INSTALL_DIR%\src\services\" >nul
copy /Y "src\tools\*.py" "%INSTALL_DIR%\src\tools\" >nul

REM Install dependencies
echo.
echo  [4/5] Installing Python packages...
echo  This may take a few minutes...
pip install -q customtkinter google-generativeai Pillow pygments

REM Create launcher
echo.
echo  [5/5] Creating desktop shortcut...

set "SHORTCUT_FILE=%USERPROFILE%\Desktop\Gemini Cowork.bat"
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo pythonw main.py
) > "%SHORTCUT_FILE%"

REM Create Start Menu entry
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Gemini Cowork.bat"
copy /Y "%SHORTCUT_FILE%" "%START_MENU%" >nul 2>&1

echo.
echo  ========================================
echo   Installation Complete!
echo  ========================================
echo.
echo  Gemini Cowork has been installed to:
echo  %INSTALL_DIR%
echo.
echo  A shortcut has been created on your Desktop.
echo.
echo  To run: Double-click "Gemini Cowork" on your Desktop
echo.
echo  ----------------------------------------
echo.

REM Ask to run now
set /p "RUN_NOW=Would you like to run Gemini Cowork now? (Y/N): "
if /i "%RUN_NOW%"=="Y" (
    echo.
    echo  Starting Gemini Cowork...
    cd /d "%INSTALL_DIR%"
    start pythonw main.py
)

echo.
pause
