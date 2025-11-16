# Script to initialize database with modules
Write-Host "Initializing database with modules..." -ForegroundColor Green

# Run migrations first
Write-Host "`nRunning migrations..." -ForegroundColor Yellow
python manage.py migrate

# Initialize modules
Write-Host "`nCreating default modules..." -ForegroundColor Yellow
python manage.py init_modules

Write-Host "`nDatabase initialization complete!" -ForegroundColor Green
