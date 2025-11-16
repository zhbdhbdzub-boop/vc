# Modular Platform - Setup Script
# Run this script to set up the complete development environment

Write-Host "🚀 Modular Platform Setup" -ForegroundColor Cyan
Write-Host "=" * 50

# Check prerequisites
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 20+" -ForegroundColor Red
    exit 1
}

# Check PostgreSQL
try {
    $pgVersion = psql --version 2>&1
    Write-Host "✓ PostgreSQL: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ PostgreSQL not found. Install PostgreSQL 16+ or use Docker" -ForegroundColor Yellow
}

# Check Redis
try {
    $redisVersion = redis-cli --version 2>&1
    Write-Host "✓ Redis: $redisVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ Redis not found. Install Redis 7+ or use Docker" -ForegroundColor Yellow
}

# Setup Backend
Write-Host "`n🔧 Setting up Backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment
if (!(Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Cyan
    Copy-Item .env.example .env
    Write-Host "✓ Created .env file. Please update with your settings." -ForegroundColor Green
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Cyan
python manage.py migrate

# Create superuser
$createSuperuser = Read-Host "`nCreate superuser now? (y/n)"
if ($createSuperuser -eq 'y') {
    python manage.py createsuperuser
}

Set-Location ..

# Setup Frontend
Write-Host "`n🎨 Setting up Frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
npm install

# Create .env file
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Cyan
    "VITE_API_URL=http://localhost:8000" | Out-File -FilePath .env
    Write-Host "✓ Created .env file" -ForegroundColor Green
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Set-Location ..

# Success message
Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update backend/.env with your database and API keys"
Write-Host "2. Start PostgreSQL and Redis (or use Docker)"
Write-Host "3. Run backend: cd backend && python manage.py runserver"
Write-Host "4. Run frontend: cd frontend && npm run dev"
Write-Host "5. Visit http://localhost:5173"
Write-Host "`n🐳 Or use Docker:"
Write-Host "wsl docker-compose up --build"
Write-Host "`n📚 Documentation: See README.md and docs/" -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor Cyan
