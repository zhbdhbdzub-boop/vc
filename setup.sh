#!/bin/bash
# Modular Platform - Setup Script (Linux/macOS)

echo "🚀 Modular Platform Setup"
echo "=================================================="

# Check prerequisites
echo -e "\n📋 Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION"
else
    echo "✗ Python not found. Please install Python 3.11+"
    exit 1
fi

# Check Node
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Node.js: $NODE_VERSION"
else
    echo "✗ Node.js not found. Please install Node.js 20+"
    exit 1
fi

# Check PostgreSQL
if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version)
    echo "✓ $PG_VERSION"
else
    echo "⚠ PostgreSQL not found. Install PostgreSQL 16+ or use Docker"
fi

# Check Redis
if command -v redis-cli &> /dev/null; then
    REDIS_VERSION=$(redis-cli --version)
    echo "✓ $REDIS_VERSION"
else
    echo "⚠ Redis not found. Install Redis 7+ or use Docker"
fi

# Setup Backend
echo -e "\n🔧 Setting up Backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ Created .env file. Please update with your settings."
else
    echo "✓ .env file already exists"
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser
read -p "Create superuser now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

cd ..

# Setup Frontend
echo -e "\n🎨 Setting up Frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "VITE_API_URL=http://localhost:8000" > .env
    echo "✓ Created .env file"
else
    echo "✓ .env file already exists"
fi

cd ..

# Success message
echo -e "\n=================================================="
echo "✅ Setup Complete!"
echo -e "\n📝 Next Steps:"
echo "1. Update backend/.env with your database and API keys"
echo "2. Start PostgreSQL and Redis (or use Docker)"
echo "3. Run backend: cd backend && python manage.py runserver"
echo "4. Run frontend: cd frontend && npm run dev"
echo "5. Visit http://localhost:5173"
echo -e "\n🐳 Or use Docker:"
echo "docker-compose up --build"
echo -e "\n📚 Documentation: See README.md and docs/"
echo "=================================================="
