@echo off
title Git Gardener - Settings

echo ===================================================
echo   Git Gardener - Settings Manager
echo ===================================================
echo.
echo Launching settings interface...
echo.

python git_gardener_core_v4.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to launch settings GUI.
    echo Make sure Python is installed and bot_ui.py exists.
    pause
)
