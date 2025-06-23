# 🚛 MudlineX - Complete Booking System Backend

A comprehensive backend system for truck booking and material transportation management, built with FastAPI and PostgreSQL.

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Development Setup](#-development-setup)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [Database Setup](#-database-setup)
- [Testing](#-testing)
- [Contributing](#-contributing)

## ✨ Features

### 🚚 **Three Booking Methods**
- **Pre-loaded Truck Booking**: Direct booking of trucks with pre-loaded materials
- **Location-based Booking**: Book materials from specific locations with nearby truck matching
- **Traditional Booking**: Custom booking requests with truck owner approval

### 👥 **User Management**
- User registration and authentication (JWT)
- Role-based access (Truck Owner / Customer)
- Profile management for both user types

### 🗺️ **Location Services**
- GPS-based truck tracking
- Nearby truck discovery
- Material location management

### 💳 **Payment System**
- Multiple payment methods (Online, Cash, UPI)
- Payment status tracking
- Transaction history

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL
- **Authentication**: JWT + OAuth2
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Logging**: Structlog

## 📋 Prerequisites

Before running this application, ensure you have the following installed:

- **Python 3.11+**
- **PostgreSQL** (for database)
- **Git**

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone <repository-url>
cd mudline-backend
```

### 2. Create and activate virtual environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (Git Bash):
source venv/Scripts/activate
# On Linux/Mac:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your database settings
# Update DATABASE_URL with your PostgreSQL credentials
```

### 5. Set up PostgreSQL database
```bash
# Create database and user (run in PostgreSQL)
CREATE DATABASE mudlinex_dev;
CREATE USER mudlinex_user WITH PASSWORD 'mudlinex_password';
GRANT ALL PRIVILEGES ON DATABASE mudlinex_dev TO mudlinex_user;
```

### 6. Run the application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Access the application
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## 🔧 Development Setup

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://mudlinex_user:mudlinex_password@localhost:5432/mudlinex_dev

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Settings
DEBUG=true
APP_NAME=MudlineX
APP_VERSION=1.0.0

# CORS Origins
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000
```

### Database Setup

1. **Install PostgreSQL** (if not already installed)
   - Windows: Download from https://www.postgresql.org/download/windows/
   - Mac: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql postgresql-contrib`

2. **Create database and user**
   ```sql
   CREATE DATABASE mudlinex_dev;
   CREATE USER mudlinex_user WITH PASSWORD 'mudlinex_password';
   GRANT ALL PRIVILEGES ON DATABASE mudlinex_dev TO mudlinex_user;
   ```

3. **Test connection**
   ```bash
   psql -h localhost -U mudlinex_user -d mudlinex_dev
   ```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Key API Endpoints

#### Health Check
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint

#### Authentication (Coming Soon)
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token

#### Users (Coming Soon)
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile

#### Trucks (Coming Soon)
- `GET /api/v1/trucks` - List trucks
- `POST /api/v1/trucks` - Add truck
- `GET /api/v1/trucks/nearby` - Find nearby trucks

#### Bookings (Coming Soon)
- `GET /api/v1/bookings` - List bookings
- `POST /api/v1/bookings` - Create booking
- `POST /api/v1/bookings/{id}/accept` - Accept booking

## 📁 Project Structure

```
mudline-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── truck.py
│   │   ├── booking.py
│   │   ├── location.py
│   │   ├── payment.py
│   │   ├── rating.py
│   │   └── notification.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── truck.py
│   │   ├── booking.py
│   │   └── ...
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── booking_service.py
│   │   └── ...
│   ├── core/                   # Core functionality
│   │   ├── security.py
│   │   └── exceptions.py
│   └── utils/                  # Utility functions
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables example
└── README.md                   # This file
```

## 🔐 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `DEBUG` | Debug mode | No | `true` |
| `APP_NAME` | Application name | No | `MudlineX` |
| `APP_VERSION` | Application version | No | `1.0.0` |

## 🗄️ Database Setup

The application uses SQLAlchemy with PostgreSQL. Tables are automatically created when the application starts in debug mode.

### Manual Database Setup

If you need to manually create tables:

```python
from app.database import engine, Base
from app.models import *  # Import all models

# Create all tables
Base.metadata.create_all(bind=engine)
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_auth.py            # Authentication tests
├── test_users.py           # User management tests
├── test_trucks.py          # Truck management tests
├── test_bookings.py        # Booking tests
└── test_locations.py       # Location tests
```

## 🚀 Running the Application

### Development Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Python directly
```bash
python -m app.main
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Contact the development team

## 🔄 Changelog

### v1.0.0 (Current)
- Initial release
- FastAPI backend with PostgreSQL
- User authentication and authorization
- Basic project structure
- Health check endpoints

---

**Happy coding! 🚛💻** 