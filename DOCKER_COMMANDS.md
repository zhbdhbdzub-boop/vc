# Docker Commands for CV Modules Setup

# 1. Make migrations for the new CV analysis models
wsl docker-compose exec backend python manage.py makemigrations cv_analysis

# 2. Apply the migrations to the database
wsl docker-compose exec backend python manage.py migrate

# 3. Initialize the 3 new CV modules in the marketplace
wsl docker-compose exec backend python manage.py init_modules

# 4. (Optional) Create a superuser if you don't have one
wsl docker-compose exec backend python manage.py createsuperuser

# 5. Restart the backend to pick up changes
wsl docker-compose restart backend

# 6. Check logs if there are any issues
wsl docker-compose logs -f backend
