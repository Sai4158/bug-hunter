param(
    [ValidateSet('start', 'stop', 'status')][string]$Action = 'start',
    [ValidateRange(1024, 65535)][int]$Port = 8501,
    [switch]$NoBrowser,
    [switch]$Yes
)
$ErrorActionPreference = 'Stop'

function Find-ProjectPython {
    $candidates = @((Join-Path $PSScriptRoot '.venv\Scripts\python.exe'))
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        $path = & $launcher.Source -3 -c 'import sys; sys.exit(sys.version_info < (3,11)); print(sys.executable)' 2>$null
        if ($LASTEXITCODE -eq 0 -and $path) { $candidates += $path }
    }
    $command = Get-Command python -ErrorAction SilentlyContinue
    if ($command -and $command.Source -notmatch '\\WindowsApps\\python(3)?\.exe$') { $candidates += $command.Source }
    $pythonFolder = Join-Path $env:LOCALAPPDATA 'Programs\Python'
    if (Test-Path -LiteralPath $pythonFolder) {
        $candidates += @(Get-ChildItem -LiteralPath $pythonFolder -Directory | ForEach-Object {
            Join-Path $_.FullName 'python.exe'
        })
    }
    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (Test-Path -LiteralPath $candidate) {
            & $candidate -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)' 2>$null
            if ($LASTEXITCODE -eq 0) { return $candidate }
        }
    }
    return $null
}

function Install-Prerequisite([string]$Id, [string]$Label) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "WinGet is unavailable. Install $Label manually using README.md, then retry start.bat."
    }
    if (-not $Yes) {
        $choice = Read-Host "Install $Label for your Windows account using WinGet? Package/source terms apply. [y/N]"
        if ($choice -notmatch '^(y|yes)$') { throw "$Label installation declined. Nothing was silently installed." }
    }
    & winget install --id $Id --exact --source winget --scope user --silent --no-upgrade --accept-package-agreements --accept-source-agreements | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "$Label installation failed (WinGet exit $LASTEXITCODE). See its output above." }
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + $env:Path
}

function Invoke-BugHunterControl {
    $projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    if ($Action -ne 'start') {
        if (-not (Test-Path -LiteralPath $projectPython)) {
            Write-Host 'No project Python environment. No processes were stopped.'
            return 0
        }
        & $projectPython (Join-Path $PSScriptRoot 'control.py') $Action | Out-Host
        return $LASTEXITCODE
    }
    Write-Host 'Checking Python...'
    $python = Find-ProjectPython
    if (-not $python) {
        Install-Prerequisite 'Python.Python.3.12' 'Python 3.12'
        $python = Find-ProjectPython
        if (-not $python) { throw 'Python was not detected after installation. Reopen the terminal and retry.' }
    }
    $ready = $false
    if (Test-Path -LiteralPath $projectPython) {
        & $projectPython (Join-Path $PSScriptRoot 'setup_env.py') --check
        $ready = $LASTEXITCODE -eq 0
    }
    if (-not $ready) {
        Write-Host 'Preparing project Python packages (first run or dependency change)...'
        & $python (Join-Path $PSScriptRoot 'setup_env.py') | Out-Host
        if ($LASTEXITCODE -ne 0) { throw 'Python environment setup did not complete.' }
    }
    # The provider validates loopback-only URLs before any HTTP request is made.
    $baseUrl = & $projectPython -c 'from bug_hunter.ai.ollama_provider import OllamaProvider; print(OllamaProvider().base_url)'
    if ($LASTEXITCODE -ne 0) { throw 'Invalid local Ollama configuration.' }
    $ollamaRunning = $false
    try {
        $response = Invoke-RestMethod -Uri ($baseUrl + '/api/tags') -TimeoutSec 3
        $ollamaRunning = $null -ne $response.models
    } catch { $ollamaRunning = $false }
    $ollamaPath = $null
    if (-not $ollamaRunning) {
        $command = Get-Command ollama -ErrorAction SilentlyContinue
        if ($command) { $ollamaPath = $command.Source }
        $nativePath = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
        if (-not $ollamaPath -and (Test-Path -LiteralPath $nativePath)) { $ollamaPath = $nativePath }
        if (-not $ollamaPath) {
            Install-Prerequisite 'Ollama.Ollama' 'Ollama'
            $command = Get-Command ollama -ErrorAction SilentlyContinue
            if ($command) { $ollamaPath = $command.Source }
            elseif (Test-Path -LiteralPath $nativePath) { $ollamaPath = $nativePath }
            if (-not $ollamaPath) { throw 'Ollama was not detected after installation. Reopen the terminal and retry.' }
        }
    }
    $options = @('start', '--port', "$Port")
    if ($NoBrowser) { $options += '--no-browser' }
    if ($Yes) { $options += '--yes' }
    if ($ollamaPath) { $options += @('--ollama', $ollamaPath) }
    & $projectPython (Join-Path $PSScriptRoot 'control.py') @options | Out-Host
    return $LASTEXITCODE
}

if ($MyInvocation.InvocationName -ne '.') {
    try {
        Push-Location -LiteralPath $PSScriptRoot
        try { $result = Invoke-BugHunterControl } finally { Pop-Location }
        exit $result
    } catch {
        Write-Host ("Bug Hunter: " + $_.Exception.Message) -ForegroundColor Red
        exit 1
    }
}
