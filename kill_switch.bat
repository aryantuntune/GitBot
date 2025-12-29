@echo off
echo ===================================================
echo   Git Gardener V4 - EMERGENCY KILL SWITCH
echo ===================================================
echo.
echo Stopping all bot instances...

:: Kill by Window Title (Background Agent Windows)
taskkill /F /FI "WINDOWTITLE eq Git Gardener V4 [Background]" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Git Gardener Bot V4 - Persistent Mode" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Git Gardener Agent - Headless Mode" /T >nul 2>&1

:: Kill Python Processes running the bot (both python.exe and pythonw.exe)
powershell -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -eq 'python.exe' -or $_.Name -eq 'pythonw.exe') -and ($_.CommandLine -like '*git_gardener_core_v4.py*' -or $_.CommandLine -like '*background_agent.py*') } | Stop-Process -Force"


:: Kill Ollama processes that are children of our bot
:: This targets only Ollama instances spawned by the bot's Python process
powershell -Command "$botPids = (Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*background_agent.py*' -or $_.CommandLine -like '*git_gardener_core_v4.py*' }).ProcessId; if ($botPids) { Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'ollama.exe' -and $botPids -contains $_.ParentProcessId } | Stop-Process -Force }"

echo.
echo [DONE] All bot systems terminated.
echo You can close this window.
pause

