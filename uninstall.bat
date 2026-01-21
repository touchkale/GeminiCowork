@echo off
echo Uninstalling Gemini Cowork...

set "INSTALL_DIR=%LOCALAPPDATA%\GeminiCowork"
set "SHORTCUT_FILE=%USERPROFILE%\Desktop\Gemini Cowork.bat"
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Gemini Cowork.bat"

REM Remove files
if exist "%INSTALL_DIR%" (
    rd /s /q "%INSTALL_DIR%"
    echo Removed installation directory
)

if exist "%SHORTCUT_FILE%" (
    del /q "%SHORTCUT_FILE%"
    echo Removed desktop shortcut
)

if exist "%START_MENU%" (
    del /q "%START_MENU%"
    echo Removed Start Menu entry
)

echo.
echo Gemini Cowork has been uninstalled.
echo.
pause
