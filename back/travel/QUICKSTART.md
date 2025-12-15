# Quick Start Guide

## 1. Database Setup (5 minutes)

### PostgreSQL Installation

**Windows (using chocolatey):**
```bash
choco install postgresql14
```

**macOS:**
```bash
brew install postgresql@14
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql-14
```

### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE booking_db;

# Create user (optional, for security)
CREATE USER booking_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE booking_db TO booking_user;

# Exit
\q
```

## 2. Project Setup (10 minutes)

### Install Dependencies

```bash
cd travel
pip install -r requirements.txt
```

### Configure Environment

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/booking_db

# Or with specific user:
DATABASE_URL=postgresql://booking_user:secure_password@localhost:5432/booking_db

# Security
SECRET_KEY=your-super-secret-key-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# App
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO
```

## 3. Initialize Database (5 minutes)

### Run Migrations

```bash
# Apply all migrations
alembic upgrade head

# This will:
# 1. Create schema "booking"
# 2. Create all tables
# 3. Create enum types
# 4. Create all stored procedures
# 5. Insert default roles
```

### Verify Installation

```bash
# Connect to database
psql -U postgres -d booking_db

# List procedures
\df+ booking.*

# List tables
\dt+ booking.*

# Exit
\q
```

## 4. Run Application (2 minutes)

### Development Mode

```bash
# Terminal 1: Run the app
uvicorn app.main:app --reload

# Terminal 2: Test the health endpoint
curl http://localhost:8000/api/v1/health/status
```

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 5. Test the API

### Using curl

```bash
# 1. Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password",
    "full_name": "John Doe",
    "phone": "+1234567890"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'

# Save the access_token from response

# 3. Get user profile (use token from login)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. Create booking
curl -X POST http://localhost:8000/api/v1/bookings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hold_expires_at": "2025-12-20T12:00:00Z"
  }'

# 5. Create passenger profile
curl -X POST http://localhost:8000/api/v1/bookings/passengers \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Traveler",
    "birth_date": "1990-05-15"
  }'
```

### Using Postman

1. Import the collection template (see below)
2. Set `{{base_url}}` to `http://localhost:8000/api/v1`
3. Run the requests in order

**Collection Template:**
```json
{
  "info": {
    "name": "Travel Booking API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Register",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/auth/register",
        "body": {
          "mode": "raw",
          "raw": "{\"email\":\"user@example.com\",\"password\":\"pass123\",\"full_name\":\"Test User\"}"
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/auth/login",
        "body": {
          "mode": "raw",
          "raw": "{\"email\":\"user@example.com\",\"password\":\"pass123\"}"
        }
      }
    },
    {
      "name": "Get Profile",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/auth/me",
        "header": [{"key": "Authorization", "value": "Bearer {{access_token}}"}]
      }
    }
  ]
}
```

## 6. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_booking.py::TestUserService -v

# Run with coverage
pytest --cov=app tests/

# Run in watch mode (requires pytest-watch)
ptw tests/
```

## 7. Database Inspection

### Connect to Database

```bash
psql -U postgres -d booking_db
```

### Useful Queries

```sql
-- Check created tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'booking' 
ORDER BY table_name;

-- Count users
SELECT COUNT(*) FROM booking.users;

-- View user roles
SELECT u.email, r.code 
FROM booking.user_roles ur
JOIN booking.users u ON ur.user_id = u.id
JOIN booking.roles r ON ur.role_id = r.id;

-- Check bookings
SELECT id, user_id, status, created_at FROM booking.bookings;

-- List procedures
\df booking.*

-- Show procedure code
\df+ booking.create_user
```

## 8. Troubleshooting

### Port Already in Use

```bash
# Find process on port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Database Connection Error

```bash
# Test connection
psql -U postgres -d booking_db -c "SELECT 1"

# Check PostgreSQL status (macOS)
brew services list

# Start PostgreSQL (if needed)
brew services start postgresql@14
```

### Migration Issues

```bash
# Check current migration
alembic current

# View all migrations
alembic history

# Downgrade one step
alembic downgrade -1

# Upgrade one step
alembic upgrade +1
```

### Permission Denied on Procedures

```sql
-- Grant schema permissions
GRANT USAGE ON SCHEMA booking TO booking_user;

-- Grant execute on all procedures
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA booking TO booking_user;
```

## 9. Project Structure Overview

```
travel/
├── app/                        # Main application
│   ├── api/v1/                 # API endpoints
│   │   ├── auth_router.py       # ✅ Auth endpoints
│   │   ├── bookings_router.py   # ✅ Booking endpoints
│   │   └── router.py            # ✅ Main router
│   ├── core/
│   │   ├── auth.py             # ✅ JWT & roles
│   │   ├── config.py           # ✅ Settings
│   │   └── database.py         # ✅ DB connection
│   ├── models/models.py        # ✅ ORM models
│   ├── schemas/schemas.py      # ✅ Pydantic schemas
│   ├── services/dal.py         # ✅ Data access layer
│   └── main.py                 # ✅ App entry point
├── alembic/                    # Database migrations
│   └── versions/
│       ├── 001_initial_schema.py    # ✅ Tables
│       └── 002_add_procedures.py    # ✅ Procedures
├── tests/test_booking.py       # ✅ Tests
├── requirements.txt            # ✅ Dependencies
└── alembic.ini                 # ✅ Alembic config
```

## 10. Next Steps

1. **Add Admin Panel** - FastAPI admin dashboard
2. **Add Payment Gateway** - Stripe/Adyen integration
3. **Add Notifications** - Email/SMS on booking
4. **Add Search Filters** - Advanced trip search
5. **Add Caching** - Redis for performance
6. **Add Logging** - Structured logging to files
7. **Add Monitoring** - Prometheus/Grafana
8. **Add API Documentation** - OpenAPI enhancements

## Useful Commands

```bash
# Check app version
curl http://localhost:8000/

# View OpenAPI schema
curl http://localhost:8000/openapi.json

# Run linting
pylint app/

# Format code
black app/

# Check types
mypy app/

# Create requirements-lock file
pip freeze > requirements-lock.txt

# Update all dependencies
pip install -U -r requirements.txt
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `psycopg2` installation fails | Install PostgreSQL dev packages: `sudo apt-get install libpq-dev` |
| Port 5432 in use | Change DATABASE_URL or stop other PostgreSQL instance |
| CORS errors | Check `ALLOWED_ORIGINS` in config |
| Token expired | Get new token using refresh endpoint |
| Permission denied on table | Run migrations with admin user, then grant permissions |

## Need Help?

- Check `IMPLEMENTATION_GUIDE.md` for detailed architecture
- Review `app/services/dal.py` for service usage examples
- Check `tests/test_booking.py` for integration examples
- Read FastAPI docs: https://fastapi.tiangolo.com/

Good luck! 🚀
