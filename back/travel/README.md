# travel

A FastAPI application created with fastapi-init.

## Features

- 🔐 JWT Authentication
- 🗄️ SQLAlchemy ORM with Alembic migrations
- 📝 Automatic API documentation
- 🧪 Comprehensive testing setup
- 🐳 Docker support
- 📊 Health checks
- 🔒 CORS configuration
- 📝 Structured logging

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Database Setup

```bash
# Initialize database
alembic upgrade head
```

### Running the Application

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Project Structure

```
travel/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth_router.py
│   │       ├── health.py
│   │       └── router.py
│   ├── core/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── middleware.py
│   ├── models/
│   │   └── models.py
│   ├── schemas/
│   │   └── schemas.py
│   └── main.py
├── tests/
├── alembic/
├── logs/
└── requirements.txt
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py -v
```

## Docker

```bash
# Build image
docker build -t travel .

# Run container
docker run -p 8000:8000 travel
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: Database connection string
- `DEBUG`: Enable debug mode
- `ALLOWED_ORIGINS`: CORS allowed origins