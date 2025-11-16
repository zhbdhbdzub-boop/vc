# WSL Docker Configuration - Changes Summary

This document summarizes all changes made to ensure Docker commands work properly on Windows using WSL.

## 🎯 Problem Fixed

**Issue**: Docker commands were failing on Windows because they weren't being executed through WSL (Windows Subsystem for Linux).

**Solution**: Updated all Docker commands throughout the project to use the `wsl` prefix, and created a helper script for convenience.

---

## 📝 Files Modified

### PowerShell Scripts

1. **setup.ps1**
   - Changed: `docker-compose up --build` → `wsl docker-compose up --build`
   - Location: Line 113

2. **fix-setup.ps1**
   - Changed: `docker-compose restart backend celery frontend` → `wsl docker-compose restart backend celery frontend`
   - Location: Line 53

### Documentation Files

3. **DOCKER_COMMANDS.md**
   - Updated all 6 docker commands to use `wsl` prefix
   - Commands: makemigrations, migrate, init_modules, createsuperuser, restart, logs

4. **QUICK_START_FIX.md**
   - Updated restart command in Step 3
   - Changed: `docker-compose restart` → `wsl docker-compose restart`

5. **SETUP_GUIDE.md**
   - Updated Quick Start section with `wsl docker-compose up --build`
   - Updated superuser creation command with `wsl` prefix

6. **backend/README.md**
   - Updated Docker section with `wsl` prefix for:
     - `docker-compose up --build`
     - `docker-compose exec backend python manage.py migrate`
     - `docker-compose exec backend python manage.py createsuperuser`

7. **COMPLETE_FIX_GUIDE.md**
   - Updated service restart commands: `docker-compose down/up` → `wsl docker-compose down/up`
   - Updated log viewing commands with `wsl` prefix

8. **ATS_CHECKER_IMPLEMENTATION.md**
   - Updated test commands with `wsl docker compose` prefix
   - Updated module setup command

9. **README.md**
   - Added Quick Start section with WSL instructions
   - Added link to WSL_DOCKER_GUIDE.md
   - Added reference to helper script

### New Files Created

10. **docker.ps1** (NEW)
    - Helper script that automatically prefixes docker-compose with `wsl`
    - Includes error handling for when WSL is not available
    - Simplifies command usage: `.\docker.ps1 up -d` instead of `wsl docker-compose up -d`

11. **WSL_DOCKER_GUIDE.md** (NEW)
    - Comprehensive guide for Windows users
    - Explains why WSL is needed
    - Provides troubleshooting steps
    - Includes common commands reference
    - Quick reference table

---

## 🚀 How to Use

### Option 1: Helper Script (Recommended)

```powershell
# Start services
.\docker.ps1 up -d

# Run migrations
.\docker.ps1 exec backend python manage.py migrate

# View logs
.\docker.ps1 logs -f backend
```

### Option 2: Direct WSL Commands

```powershell
# Start services
wsl docker-compose up -d

# Run migrations
wsl docker-compose exec backend python manage.py migrate

# View logs
wsl docker-compose logs -f backend
```

---

## 🔍 Changed Command Patterns

### Before (Not Working on Windows)
```powershell
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose restart backend
docker-compose logs -f backend
```

### After (Working on Windows)
```powershell
wsl docker-compose up -d
wsl docker-compose exec backend python manage.py migrate
wsl docker-compose restart backend
wsl docker-compose logs -f backend
```

### Or Using Helper Script
```powershell
.\docker.ps1 up -d
.\docker.ps1 exec backend python manage.py migrate
.\docker.ps1 restart backend
.\docker.ps1 logs -f backend
```

---

## 📋 Common Commands Updated

| Task | Old Command | New Command |
|------|-------------|-------------|
| Start project | `docker-compose up -d` | `wsl docker-compose up -d` |
| Stop project | `docker-compose down` | `wsl docker-compose down` |
| Run migrations | `docker-compose exec backend python manage.py migrate` | `wsl docker-compose exec backend python manage.py migrate` |
| Create superuser | `docker-compose exec backend python manage.py createsuperuser` | `wsl docker-compose exec backend python manage.py createsuperuser` |
| View logs | `docker-compose logs -f backend` | `wsl docker-compose logs -f backend` |
| Restart services | `docker-compose restart backend` | `wsl docker-compose restart backend` |

---

## ✅ Testing the Fix

1. **Test Docker Access**
   ```powershell
   wsl docker --version
   wsl docker-compose --version
   ```

2. **Test Project Startup**
   ```powershell
   wsl docker-compose up -d
   ```

3. **Test Container Access**
   ```powershell
   wsl docker-compose ps
   wsl docker-compose exec backend python manage.py --version
   ```

4. **Test Helper Script**
   ```powershell
   .\docker.ps1 ps
   ```

---

## 🛠️ Prerequisites

Before using these commands, ensure:

1. **WSL is installed**:
   ```powershell
   wsl --install
   ```

2. **Docker Desktop is running**:
   - Ensure "Use WSL 2 based engine" is enabled in Docker Desktop settings

3. **WSL integration is enabled**:
   - In Docker Desktop > Settings > Resources > WSL Integration
   - Enable integration with your WSL distro

---

## 📚 Additional Resources

- [WSL Docker Guide](./WSL_DOCKER_GUIDE.md) - Detailed Windows setup
- [Setup Guide](./SETUP_GUIDE.md) - Complete project setup
- [Docker Commands](./DOCKER_COMMANDS.md) - Common operations

---

## 🎉 Summary

All Docker commands in the project now work correctly on Windows by using WSL. You can either:
1. Use the convenient `docker.ps1` helper script
2. Prefix all docker-compose commands with `wsl`

The project is now fully compatible with Windows development environments!
