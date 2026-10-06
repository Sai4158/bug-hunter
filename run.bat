@echo off
setlocal
set "projectPython=%~dp0.venv\Scripts\python.exe"
if not exist "%projectPython%" (
    echo Run setup.bat first to create the Python environment. See README.md.
    exit /b 1
)
"%projectPython%" "%~dp0launch.py" %*
exit /b %errorlevel%
