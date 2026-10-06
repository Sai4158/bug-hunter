@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0control.ps1" -Action stop
exit /b %errorlevel%
