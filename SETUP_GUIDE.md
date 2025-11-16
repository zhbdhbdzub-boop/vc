# 🎯 Modular Platform - Complete Setup Guide

This guide will help you get the Modular Platform up and running on your machine.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Docker)](#quick-start-docker)
3. [Manual Setup](#manual-setup)
4. [Environment Configuration](#environment-configuration)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Windows | Linux/macOS |
|----------|---------|---------|-------------|
| Python | 3.11+ | [Download](https://python.org) | `apt install python3` / `brew install python3` |
| Node.js | 20+ | [Download](https://nodejs.org) | `apt install nodejs` / `brew install node` |
| PostgreSQL | 16+ | [Download](https://postgresql.org) | `apt install postgresql` / `brew install postgresql` |
| Redis | 7+ | [Download](https://redis.io) | `apt install redis` / `brew install redis` |
| Docker (Optional) | Latest | [Download](https://docker.com) | [Install Guide](https://docs.docker.com/install/) |

### Check Installations

```powershell
# Windows (PowerShell)
python --version    # Should be 3.11+
node --version      # Should be 20+
psql --version      # Should be 16+
redis-cli --version # Should be 7+
```

```bash
# Linux/macOS
python3 --version
node --version
psql --version
redis-cli --version
```

---

## Quick Start (Docker)

**Easiest way to get started! No manual setup required.**

### 1. Clone Repository

```powershell
git clone <repository-url>
cd modular-platform
```

### 2. Start All Services

```powershell
wsl docker-compose up --build
```

This will start:
- PostgreSQL database on port 5432
- Redis cache on port 6379
- Django backend on port 8000
- Celery worker
- React frontend on port 5173

### 3. Create Superuser

In a new terminal:

```powershell
wsl docker-compose exec backend python manage.py createsuperuser
```

### 4. Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

---

## Manual Setup

### Step 1: Clone Repository

```powershell
git clone <repository-url>
cd modular-platform
```

### Step 2: Backend Setup

#### 2.1 Create Virtual Environment

**Windows:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
```

**Linux/macOS:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 Install Python Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.3 Configure Environment

```powershell
# Create .env from example
copy .env.example .env    # Windows
# OR
cp .env.example .env      # Linux/macOS
```

Edit `.env` file with your settings:

```env
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/modular_platform
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
OPENAI_API_KEY=sk-your-openai-api-key
```

#### 2.4 Create Database

**PostgreSQL:**
```sql
-- In psql or pgAdmin
CREATE DATABASE modular_platform;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE modular_platform TO postgres;
```

#### 2.5 Run Migrations

```powershell
python manage.py migrate
```

#### 2.6 Create Superuser

```powershell
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Step 3: Frontend Setup

#### 3.1 Install Node Dependencies

```powershell
cd frontend
npm install
```

#### 3.2 Configure Environment

```powershell
# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
```

Or manually create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

### Step 4: Start Services

#### 4.1 Start PostgreSQL

**Windows:**
- PostgreSQL should start automatically as a service
- Or use pgAdmin to start the server

**Linux/macOS:**
```bash
# Linux
sudo service postgresql start

# macOS
brew services start postgresql
```

#### 4.2 Start Redis

**Windows:**
```powershell
# If installed with chocolatey
redis-server
```

**Linux/macOS:**
```bash
# Linux
sudo service redis-server start

# macOS
brew services start redis
```

---

## Running the Application

### Terminal 1: Backend Server

```powershell
cd backend
.\venv\Scripts\Activate    # Windows
# OR
source venv/bin/activate    # Linux/macOS

python manage.py runserver
```

Backend will be available at: http://localhost:8000

### Terminal 2: Celery Worker (Optional but recommended)

```powershell
cd backend
.\venv\Scripts\Activate    # Windows
# OR
source venv/bin/activate    # Linux/macOS

# Windows
celery -A config worker --loglevel=info --pool=solo

# Linux/macOS
celery -A config worker --loglevel=info
```

### Terminal 3: Celery Beat (Optional)

```powershell
cd backend
.\venv\Scripts\Activate

celery -A config beat --loglevel=info
```

### Terminal 4: Frontend Server

```powershell
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## Environment Configuration

### Backend Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key | ✅ | `django-insecure-key` |
| `DEBUG` | Debug mode | ✅ | `True` |
| `DATABASE_URL` | PostgreSQL connection | ✅ | `postgresql://user:pass@localhost:5432/db` |
| `REDIS_URL` | Redis connection | ✅ | `redis://localhost:6379/0` |
| `STRIPE_SECRET_KEY` | Stripe API key | ⚠️ | `sk_test_...` |
| `OPENAI_API_KEY` | OpenAI API key | ⚠️ | `sk-...` |
| `AWS_ACCESS_KEY_ID` | AWS S3 credentials | ❌ | `AKIA...` |

✅ Required | ⚠️ Required for features | ❌ Optional

### Frontend Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `VITE_API_URL` | Backend API URL | ✅ | `http://localhost:8000` |

---

## Automated Setup Script

We provide setup scripts for quick installation:

### Windows (PowerShell)

```powershell
.\setup.ps1
```

### Linux/macOS (Bash)

```bash
chmod +x setup.sh
./setup.sh
```

These scripts will:
- ✅ Check prerequisites
- ✅ Create virtual environments
- ✅ Install all dependencies
- ✅ Create .env files
- ✅ Run database migrations
- ✅ Prompt for superuser creation

---

## Troubleshooting

### Backend Issues

#### "ModuleNotFoundError: No module named 'django'"

**Solution:** Activate virtual environment first
```powershell
cd backend
.\venv\Scripts\Activate
pip install -r requirements.txt
```

#### "psycopg2.OperationalError: connection refused"

**Solution:** 
1. Ensure PostgreSQL is running
2. Check DATABASE_URL in .env
3. Verify database exists: `psql -l`

#### "Redis connection refused"

**Solution:**
1. Start Redis: `redis-server`
2. Check REDIS_URL in .env
3. Test connection: `redis-cli ping`

#### Celery on Windows: "NotImplementedError"

**Solution:** Use solo pool
```powershell
celery -A config worker --loglevel=info --pool=solo
```

### Frontend Issues

#### "Cannot find module 'react'"

**Solution:** Install dependencies
```powershell
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### API requests fail with CORS error

**Solution:**
1. Check CORS_ALLOWED_ORIGINS in backend settings
2. Ensure backend is running on port 8000
3. Verify VITE_API_URL in frontend/.env

#### TypeScript errors

**Solution:**
```powershell
npm run build
```

### Database Issues

#### "database 'modular_platform' does not exist"

**Solution:** Create database
```sql
-- In psql
CREATE DATABASE modular_platform;
```

#### Migration conflicts

**Solution:**
```powershell
python manage.py migrate --run-syncdb
```

---

## Verifying Installation

### 1. Check Backend

```powershell
curl http://localhost:8000/api/schema/
```

Should return OpenAPI schema JSON.

### 2. Check Frontend

Visit http://localhost:5173
- Should show login page
- No console errors
- Can navigate to register page

### 3. Check Database

```powershell
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.count()
1  # Your superuser
```

### 4. Check Celery

```powershell
celery -A config inspect ping
```

Should return pong from worker.

---

## Next Steps

After successful setup:

1. **Explore Admin Panel**: http://localhost:8000/admin/
2. **Read API Docs**: http://localhost:8000/api/docs/
3. **Create Test User**: Register at http://localhost:5173/register
4. **Browse Marketplace**: http://localhost:5173/marketplace
5. **Read Documentation**: See [docs/](../docs/) folder

---

## Additional Resources

- **[Backend README](../backend/README.md)** - Detailed Django documentation
- **[Frontend README](../frontend/README.md)** - React app documentation
- **[API Design](../docs/api/API_DESIGN.md)** - API endpoint reference
- **[Database Schema](../docs/database/README.md)** - Database documentation

---

## Getting Help

- **Documentation**: [docs/](../docs/)
- **Issues**: GitHub Issues
- **Email**: support@modular-platform.com

---

**Happy Coding! 🚀**
