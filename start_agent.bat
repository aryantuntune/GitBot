@echo off
title Git Gardener Agent - Launcher

REM Check if already running
tasklist /FI "IMAGENAME eq pythonw.exe" /FI "WINDOWTITLE eq Git Gardener*" 2>NUL | find /I /N "pythonw.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo.
    echo ===================================================
    echo   Git Gardener Agent - Already Running
    echo ===================================================
    echo.
    echo The bot is already running in the background.
    echo.
    echo To stop it, run: kill_switch.bat
    echo To change settings, run: settings_gui.bat
    echo.
    pause
    exit
)

REM Check if this is first run (install to startup)
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_NAME=GitGardenerAgent.lnk"

if not exist "%STARTUP_DIR%\%SHORTCUT_NAME%" (
    echo.
    echo ===================================================
    echo   Git Gardener Agent - First Run Setup
    echo ===================================================
    echo.
    echo Installing to Windows Startup...
    
    powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%STARTUP_DIR%\%SHORTCUT_NAME%');$s.TargetPath='%~dpnx0';$s.WorkingDirectory='%~dp0';$s.WindowStyle=7;$s.Save()"
    
    if %errorlevel% equ 0 (
        echo [SUCCESS] Bot will start automatically on next boot.
    ) else (
        echo [WARNING] Auto-startup installation failed.
    )
    echo.
    timeout /t 2
)

echo.
echo ===================================================
echo   Git Gardener Agent - Starting
echo ===================================================
echo.
echo Launching bot as a background service...

REM Create a VBScript to launch pythonw.exe invisibly
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\launch_bot.vbs"
echo WshShell.Run "pythonw.exe ""%~dp0background_agent.py""", 0, False >> "%TEMP%\launch_bot.vbs"

REM Execute the VBScript
cscript //nologo "%TEMP%\launch_bot.vbs"
del "%TEMP%\launch_bot.vbs"

echo.
echo [SUCCESS] Bot is now running in the background!
echo.
echo You can safely close this window.
echo The bot will continue running and send notifications.
echo.
echo To stop: run kill_switch.bat
echo To configure: run settings_gui.bat
echo.
timeout /t 3

