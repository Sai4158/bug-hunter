@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0control.ps1" -Action start %*
set "taskExit=%errorlevel%"
if not "%taskExit%"=="0" (
    echo Start did not complete. Read the error above.
    pause
)
exit /b %taskExit%
