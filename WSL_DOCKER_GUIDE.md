# Windows WSL Docker Setup Guide

This project requires Docker to run through WSL (Windows Subsystem for Linux) on Windows systems.

## Why WSL is Required

On Windows, Docker Desktop typically runs Docker daemon inside WSL2. All docker commands need to be executed through WSL to properly interact with the containers.

## Quick Start

### Option 1: Use the Helper Script (Recommended)

We've created a helper script that automatically handles WSL for you:

```powershell
# Instead of: docker-compose up -d
.\docker.ps1 up -d

# Instead of: docker-compose exec backend python manage.py migrate
.\docker.ps1 exec backend python manage.py migrate

# Instead of: docker-compose logs -f backend
.\docker.ps1 logs -f backend
```

### Option 2: Prefix Commands with WSL

Simply add `wsl` before any docker-compose command:

```powershell
# Start all services
wsl docker-compose up -d

# Check status
wsl docker-compose ps

# View logs
wsl docker-compose logs -f backend

# Execute commands in containers
wsl docker-compose exec backend python manage.py migrate

# Stop services
wsl docker-compose down
```

## Common Commands

### Starting the Project

```powershell
# Build and start all services
wsl docker-compose up --build -d

# Or use the helper script
.\docker.ps1 up --build -d
```

### Database Management

```powershell
# Run migrations
wsl docker-compose exec backend python manage.py migrate

# Create superuser
wsl docker-compose exec backend python manage.py createsuperuser

# Initialize modules
wsl docker-compose exec backend python manage.py init_modules
```

### Monitoring

```powershell
# View all container status
wsl docker-compose ps

# View logs for specific service
wsl docker-compose logs -f backend
wsl docker-compose logs -f celery
wsl docker-compose logs -f frontend

# View logs for all services
wsl docker-compose logs -f
```

### Restarting Services

```powershell
# Restart specific service
wsl docker-compose restart backend

# Restart multiple services
wsl docker-compose restart backend celery frontend

# Restart all services
wsl docker-compose restart
```

### Stopping and Cleanup

```powershell
# Stop all services (keeps volumes)
wsl docker-compose stop

# Stop and remove containers (keeps volumes)
wsl docker-compose down

# Stop and remove everything including volumes
wsl docker-compose down -v
```

## Troubleshooting

### WSL Not Found

If you get "wsl: command not found":

1. Install WSL:
   ```powershell
   wsl --install
   ```

2. Restart your computer

3. Verify installation:
   ```powershell
   wsl --status
   ```

### Docker Not Working in WSL

If docker commands fail even with WSL:

1. Make sure Docker Desktop is running
2. In Docker Desktop settings, ensure "Use WSL 2 based engine" is enabled
3. In Docker Desktop settings, under "Resources > WSL Integration", enable your WSL distro

### Permission Errors

If you get permission errors:

```powershell
# Run PowerShell as Administrator
wsl docker-compose up -d
```

## Integration with Scripts

All setup and maintenance scripts in this project have been updated to use WSL:

- `setup.ps1` - Initial setup script
- `fix-setup.ps1` - Fix and update script
- `docker.ps1` - Helper wrapper script

You can also use the helper script in your own scripts:

```powershell
# In your script
& .\docker.ps1 exec backend python manage.py some_command
```

## Additional Resources

- [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Docker Desktop WSL 2 Backend](https://docs.docker.com/desktop/windows/wsl/)
- [Project Docker Setup](./SETUP_GUIDE.md)

## Quick Reference

| Task | Command |
|------|---------|
| Start project | `wsl docker-compose up -d` |
| Stop project | `wsl docker-compose down` |
| View logs | `wsl docker-compose logs -f` |
| Run migrations | `wsl docker-compose exec backend python manage.py migrate` |
| Shell access | `wsl docker-compose exec backend bash` |
| Rebuild | `wsl docker-compose up --build -d` |
