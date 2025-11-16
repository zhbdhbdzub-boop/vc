# Modular Platform - Backend Setup

Complete Django backend with authentication, module marketplace, and API infrastructure.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- Redis 7+

### Installation

1. **Create virtual environment**
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```powershell
   copy .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations**
   ```powershell
   python manage.py migrate
   ```

5. **Create superuser**
   ```powershell
   python manage.py createsuperuser
   ```

6. **Load sample data (optional)**
   ```powershell
   python manage.py loaddata fixtures/modules.json
   ```

7. **Run server**
   ```powershell
   python manage.py runserver
   ```

### Celery Worker (For async tasks)
```powershell
# In a new terminal
celery -A config worker --loglevel=info --pool=solo
```

### Celery Beat (For scheduled tasks)
```powershell
# In another terminal
celery -A config beat --loglevel=info
```

## 📁 Project Structure

```
backend/
├── apps/
│   ├── core/           # Tenant management, shared models
│   ├── accounts/       # User authentication, JWT
│   ├── modules/        # Module marketplace
│   ├── billing/        # Stripe payments, subscriptions
│   ├── cv_analysis/    # CV Analysis module
│   ├── interviews/     # Interview Simulation module
│   └── integrations/   # Module connectors, workflows
├── config/             # Django settings, URLs, Celery
├── manage.py
└── requirements.txt
```

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login (returns JWT tokens)
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/` - Update profile
- `POST /api/auth/change-password/` - Change password
- `GET /api/auth/dashboard/` - Dashboard data

### Modules
- `GET /api/modules/marketplace/` - List available modules
- `GET /api/modules/marketplace/{id}/` - Module details
- `GET /api/modules/my-modules/` - User's active modules

### API Documentation
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

## 🔧 Management Commands

```powershell
# Create sample modules
python manage.py shell
>>> from apps.modules.models import Module
>>> Module.objects.create(
...     code='cv-analysis',
...     name='CV Analysis',
...     description='AI-powered CV parsing and job matching',
...     category='Recruitment',
...     price_monthly=49.00,
...     trial_days=14
... )
```

## 🧪 Testing

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific app tests
pytest apps/accounts/tests/
```

## 🐳 Docker

```powershell
# Build and run with Docker Compose
wsl docker-compose up --build

# Run migrations in container
wsl docker-compose exec backend python manage.py migrate

# Create superuser in container
wsl docker-compose exec backend python manage.py createsuperuser
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (required) |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `STRIPE_SECRET_KEY` | Stripe secret key | (optional) |
| `OPENAI_API_KEY` | OpenAI API key | (optional) |
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 | (optional) |

## 🔐 Security

- JWT authentication with token refresh
- CORS configured for frontend
- HTTPS redirect in production
- CSRF protection enabled
- SQL injection protection (Django ORM)
- XSS protection headers

## 📊 Database Schema

Main tables:
- `tenants` - Multi-tenant organizations
- `users` - Custom user model with tenant relationship
- `modules` - Available modules in marketplace
- `module_licenses` - User/tenant module access
- `purchases` - Purchase history
- `subscriptions` - Subscription management

## 🛠️ Development

```powershell
# Format code
black .

# Lint code
flake8

# Sort imports
isort .

# Type checking
mypy apps/
```

## 📚 Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🆘 Troubleshooting

**Database connection errors:**
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Run migrations: `python manage.py migrate`

**Celery not processing tasks:**
- Ensure Redis is running
- Check CELERY_BROKER_URL in .env
- Start worker: `celery -A config worker --loglevel=info --pool=solo`

**Import errors:**
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`
