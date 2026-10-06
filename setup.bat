@echo off
setlocal
where py >nul 2>nul
if not errorlevel 1 (
    py -3 "%~dp0setup_env.py" %*
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Install Python 3.11+ from python.org, then reopen this terminal.
        exit /b 1
    )
    python "%~dp0setup_env.py" %*
)
exit /b %errorlevel%
