# Complete Setup Script for Fixing All Issues
# Run this from the project root directory

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Modular Platform - Complete Fix   " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install Python Dependencies
Write-Host "[1/6] Installing Python dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install openai stripe spacy python-docx PyPDF2
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install Python packages" -ForegroundColor Red
    exit 1
}

# Step 2: Download spaCy Model
Write-Host "[2/6] Downloading spaCy language model..." -ForegroundColor Yellow
python -m spacy download en_core_web_md
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to download spaCy model" -ForegroundColor Red
    exit 1
}

# Step 3: Create Migrations
Write-Host "[3/6] Creating database migrations..." -ForegroundColor Yellow
python manage.py makemigrations
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create migrations" -ForegroundColor Red
    exit 1
}

# Step 4: Apply Migrations
Write-Host "[4/6] Applying database migrations..." -ForegroundColor Yellow
python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to apply migrations" -ForegroundColor Red
    exit 1
}

# Step 5: Initialize Modules
Write-Host "[5/6] Initializing marketplace modules..." -ForegroundColor Yellow
python manage.py init_modules
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to initialize modules" -ForegroundColor Red
    exit 1
}

# Step 6: Restart Services
Write-Host "[6/6] Restarting Docker services..." -ForegroundColor Yellow
Set-Location ..
wsl docker-compose restart backend celery frontend

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  Setup Complete!                    " -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Edit backend/.env and add OPENAI_API_KEY" -ForegroundColor White
Write-Host "2. Visit http://localhost:3000" -ForegroundColor White
Write-Host "3. Create new user and test free plan" -ForegroundColor White
Write-Host "4. Go to Marketplace and start a free trial" -ForegroundColor White
Write-Host ""
Write-Host "All issues are now fixed! 🎉" -ForegroundColor Green
