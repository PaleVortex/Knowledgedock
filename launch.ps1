# Knowledgedock Application Launcher (PowerShell)
# This script launches the Knowledgedock application

Write-Host ""
Write-Host "========================================"
Write-Host " Knowledgedock Application Launcher"
Write-Host "========================================"
Write-Host ""

# Get the directory of this script
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# Build the path to the executable
$EXE_PATH = Join-Path $SCRIPT_DIR "dist\Knowledgedock.exe"

# Check if executable exists
if (-not (Test-Path $EXE_PATH)) {
    Write-Host ""
    Write-Host "ERROR: Knowledgedock.exe not found!" -ForegroundColor Red
    Write-Host "Please ensure the application has been built." -ForegroundColor Yellow
    Write-Host "Run: python build_app.py" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Launch the application
Write-Host "Launching Knowledgedock..." -ForegroundColor Green
& $EXE_PATH

Write-Host "Application started successfully!" -ForegroundColor Green
Write-Host ""
