$ErrorActionPreference = 'Stop'
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    Write-Error 'Run setup.bat first to create the Python environment. See README.md.'
    exit 1
}
& $projectPython (Join-Path $PSScriptRoot 'launch.py') @args
exit $LASTEXITCODE
