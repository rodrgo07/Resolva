# Resolva - Development Script
# Starts both backend and frontend for development

Write-Host ""
Write-Host "  ██████╗ ███████╗███████╗ ██████╗ ██╗    ██╗   ██╗ █████╗ " -ForegroundColor Magenta
Write-Host "  ██╔══██╗██╔════╝██╔════╝██╔═══██╗██║    ██║   ██║██╔══██╗" -ForegroundColor Magenta
Write-Host "  ██████╔╝█████╗  ███████╗██║   ██║██║    ██║   ██║███████║" -ForegroundColor Magenta
Write-Host "  ██╔══██╗██╔══╝  ╚════██║██║   ██║██║    ╚██╗ ██╔╝██╔══██║" -ForegroundColor Magenta
Write-Host "  ██║  ██║███████╗███████║╚██████╔╝███████╗╚████╔╝ ██║  ██║" -ForegroundColor Magenta
Write-Host "  ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝ ╚═══╝  ╚═╝  ╚═╝" -ForegroundColor Magenta
Write-Host ""
Write-Host "  Seu centro de comando pessoal." -ForegroundColor DarkGray
Write-Host ""

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$BackendDir = Join-Path $ProjectRoot "apps\backend"
$DesktopDir = Join-Path $ProjectRoot "apps\desktop"
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

# Check prerequisites
if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] Python venv not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Start Backend
Write-Host "[BACKEND] Starting FastAPI on port 8700..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    param($python, $dir)
    Set-Location $dir
    & $python -m uvicorn app.main:app --host 127.0.0.1 --port 8700 --reload
} -ArgumentList $VenvPython, $BackendDir

# Wait for backend to start
Start-Sleep -Seconds 3

# Start Frontend (Vite dev server)
Write-Host "[FRONTEND] Starting Vite on port 1420..." -ForegroundColor Green
Set-Location $DesktopDir
npm run dev

# Cleanup
Write-Host ""
Write-Host "[SHUTDOWN] Stopping backend..." -ForegroundColor Yellow
Stop-Job $backendJob
Remove-Job $backendJob
Write-Host "[DONE] Resolva stopped." -ForegroundColor DarkGray
