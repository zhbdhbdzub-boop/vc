# Docker Helper Script for Windows with WSL
# This script automatically prefixes docker-compose commands with 'wsl'
# Usage: .\docker.ps1 up -d
#        .\docker.ps1 exec backend python manage.py migrate
#        .\docker.ps1 logs -f backend

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Check if WSL is available
try {
    $wslCheck = wsl --status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠ WSL is not available or not running" -ForegroundColor Yellow
        Write-Host "Attempting to run docker-compose directly..." -ForegroundColor Yellow
        & docker-compose @Arguments
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "⚠ WSL command not found" -ForegroundColor Yellow
    Write-Host "Attempting to run docker-compose directly..." -ForegroundColor Yellow
    & docker-compose @Arguments
    exit $LASTEXITCODE
}

# Run docker-compose through WSL
Write-Host "🐳 Running: wsl docker-compose $($Arguments -join ' ')" -ForegroundColor Cyan
wsl docker-compose @Arguments
exit $LASTEXITCODE
