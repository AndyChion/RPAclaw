# RPAclaw Launcher — Windows PowerShell
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  🤖 RPAclaw — Starting..." -ForegroundColor Cyan
Write-Host ""

# Detect Python
$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" }
      elseif (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" }
      else {
          Write-Host "❌ Python 3.11+ not found." -ForegroundColor Red
          Write-Host "   Install from https://www.python.org/downloads/"
          Read-Host "Press Enter to exit"
          exit 1
      }

$pyVer = & $py -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "   Python: $py ($pyVer)"

$scriptDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Write-Host "   Project: $scriptDir"

# Install deps
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
& $py -m pip install -e $scriptDir --quiet 2>$null

Write-Host "🌐 Checking Playwright browser..." -ForegroundColor Yellow
& $py -m playwright install chromium 2>$null

# Build frontend if needed
if (-not (Test-Path "$scriptDir\frontend\dist")) {
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        Write-Host "🔨 Building frontend..." -ForegroundColor Yellow
        Push-Location "$scriptDir\frontend"
        npm install
        npx vite build
        Pop-Location
    }
}

$host_addr = if ($env:RPACLAW_HOST) { $env:RPACLAW_HOST } else { "127.0.0.1" }
$port = if ($env:RPACLAW_PORT) { $env:RPACLAW_PORT } else { "18790" }

Write-Host ""
Write-Host "🚀 RPAclaw running at http://${host_addr}:${port}" -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop"
Write-Host ""

Start-Process "http://${host_addr}:${port}"

& $py -m rpaclaw.main start --host $host_addr --port $port
