# Resolva - Initial Setup Script

Write-Host ""
Write-Host "Setting up Resolva..." -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

# 1. Create Python venv
Write-Host "[1/4] Creating Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path (Join-Path $ProjectRoot ".venv"))) {
    python -m venv (Join-Path $ProjectRoot ".venv")
}

# 2. Install Python dependencies
Write-Host "[2/4] Installing Python dependencies..." -ForegroundColor Yellow
$pip = Join-Path $ProjectRoot ".venv\Scripts\pip.exe"
& $pip install -r (Join-Path $ProjectRoot "apps\backend\requirements.txt")

# 3. Install Node dependencies
Write-Host "[3/4] Installing Node.js dependencies..." -ForegroundColor Yellow
Set-Location (Join-Path $ProjectRoot "apps\desktop")
npm install

# 4. Copy .env
Write-Host "[4/4] Setting up environment..." -ForegroundColor Yellow
$envFile = Join-Path $ProjectRoot ".env"
$envExample = Join-Path $ProjectRoot ".env.example"
if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-Host "  Created .env from .env.example" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Setup complete! Run '.\scripts\dev.ps1' to start development." -ForegroundColor Green
Write-Host ""
