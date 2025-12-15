# Travel Booking Backend - Implementation Guide

## Overview

This is a production-ready FastAPI backend for a travel booking system using **PostgreSQL 14 with stored procedures** for all data operations. The architecture separates business logic into stored procedures, providing atomic transactions, better performance, and improved data integrity.

## Architecture Decision: Stored Procedures vs. SQL Files

### Why Stored Procedures?

✅ **Chosen Approach: Stored Procedures**

**Benefits:**
- **Atomic Operations**: All complex operations (booking + payment + ticket creation) are atomic
- **Better Performance**: Executed server-side, reducing network roundtrips
- **Data Integrity**: Constraints and validations enforced at database level
- **Type Safety**: Clear parameter types and return values
- **Easy Maintenance**: All logic in one place, versioned with migrations
- **Transaction Control**: Full control over transaction boundaries

**Alternative (Not Chosen): SQL Files**
- Would require manual transaction management in application
- Higher network latency
- Harder to maintain version consistency
- Less suitable for complex multi-step operations

## Project Structure

```
travel/
├── alembic/
│   ├── env.py
│   └── versions/
│       ├── 001_initial_schema.py      # Tables and indexes
│       └── 002_add_procedures.py       # Stored procedures
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth_router.py          # Authentication endpoints
│   │       ├── bookings_router.py      # Booking endpoints
│   │       ├── health.py               # Health check
│   │       └── router.py               # Main router
│   ├── core/
│   │   ├── auth.py                     # JWT and auth logic
│   │   ├── config.py                   # Configuration
│   │   ├── database.py                 # Database connection
│   │   ├── logging.py                  # Logging setup
│   │   └── middleware.py               # Custom middleware
│   ├── models/
│   │   └── models.py                   # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── schemas.py                  # Pydantic models
│   ├── services/
│   │   └── dal.py                      # Data Access Layer
│   ├── utils/
│   └── main.py                         # FastAPI app entry point
├── tests/
│   └── test_booking.py                 # Comprehensive tests
├── requirements.txt                    # Python dependencies
├── alembic.ini                        # Alembic config
└── README.md                          # This file
```

## Database Schema

### Core Entities

1. **Users & Roles**
   - `users`: User accounts
   - `roles`: User roles (admin, agent, customer)
   - `user_roles`: Role assignments

2. **Passengers & Profiles**
   - `passenger_profiles`: Passenger information

3. **Travel Products**
   - `providers`: Airlines, train companies, bus operators
   - `terminals`: Airports, train stations, bus terminals
   - `routes`: Origin-destination pairs with transport mode
   - `trips`: Specific trips/flights
   - `trip_segments`: Multi-leg trip segments
   - `fares`: Price tiers and cabin classes
   - `seat_maps`: Seat layout configurations

4. **Booking Management**
   - `bookings`: Customer bookings
   - `tickets`: Individual tickets
   - `payments`: Payment transactions
   - `invoices`: Billing documents
   - `refund_requests`: Refund requests

## Stored Procedures

### User Management

```sql
-- Create user (returns user_id)
booking.create_user(email, password_hash, full_name, phone)

-- Get user by email
booking.get_user_by_email(email)

-- Get user by ID
booking.get_user_by_id(user_id)

-- Get user roles
booking.get_user_roles(user_id)

-- Assign role to user
booking.assign_role_to_user(user_id, role_code)

-- Update user
booking.update_user(user_id, full_name, phone, is_active)
```

### Passenger Management

```sql
booking.create_passenger_profile(user_id, first_name, last_name, ...)
booking.get_passenger_profile(profile_id)
booking.get_user_passengers(user_id)
```

### Booking Operations

```sql
-- Create booking (returns booking_id)
booking.create_booking(user_id, hold_expires_at)

-- Get booking details
booking.get_booking(booking_id)

-- Get user's bookings
booking.get_user_bookings(user_id, status)

-- Update booking status
booking.update_booking_status(booking_id, status)
```

### Ticket Management

```sql
booking.create_ticket(booking_id, passenger_id, trip_id, fare_id, seat_no, ticket_number)
booking.get_booking_tickets(booking_id)
booking.update_ticket_status(ticket_id, status)
```

### Payment Processing

```sql
booking.create_payment(booking_id, amount, currency, provider, provider_ref)
booking.get_booking_payments(booking_id)
booking.update_payment_status(payment_id, status)
```

### Trip & Fare Search

```sql
-- Search trips by route and date
booking.search_trips(origin_id, destination_id, departure_date, transport_mode)

-- Get all fares for a trip
booking.get_trip_fares(trip_id)
```

## API Endpoints

### Authentication

```
POST   /api/v1/auth/register       - Register new user
POST   /api/v1/auth/login          - Login and get tokens
POST   /api/v1/auth/refresh        - Refresh access token
GET    /api/v1/auth/me             - Get current user profile
```

### Bookings

```
POST   /api/v1/bookings            - Create booking
GET    /api/v1/bookings            - List user's bookings
GET    /api/v1/bookings/{id}       - Get booking details
POST   /api/v1/bookings/{id}/tickets    - Add ticket to booking
POST   /api/v1/bookings/{id}/payments   - Create payment
PUT    /api/v1/bookings/{id}/payments/{pid}/confirm - Confirm payment
```

### Passengers

```
POST   /api/v1/bookings/passengers      - Create passenger profile
GET    /api/v1/bookings/passengers      - List user's passengers
```

### Trip Search

```
POST   /api/v1/bookings/search     - Search trips
```

## Setup & Installation

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 14
- pip or poetry

### 2. Clone and Install

```bash
cd travel
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and update:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/booking_db
SECRET_KEY=your-super-secret-key-change-this
DEBUG=True
```

### 4. Initialize Database

```bash
# Create database
createdb -U postgres booking_db

# Run migrations (creates tables and procedures)
alembic upgrade head
```

### 5. Run Application

```bash
# Development
uvicorn app.main:app --reload

# Production
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## Data Access Layer (DAL)

The `app/services/dal.py` provides service classes that call stored procedures:

```python
from app.services.dal import UserService, BookingService, PaymentService

# Create user
user_id = UserService.create_user(
    email="user@example.com",
    password_hash=hash,
    full_name="John Doe"
)

# Create booking
booking_id = BookingService.create_booking(user_id=user_id)

# Create payment
payment_id = PaymentService.create_payment(
    booking_id=booking_id,
    amount=Decimal("199.99"),
    currency="EUR"
)

# Update payment status
PaymentService.update_payment_status(payment_id, "SUCCEEDED")
```

## Authentication & Authorization

### JWT Tokens

- **Access Token**: 30 minutes (configurable)
- **Refresh Token**: 7 days (configurable)
- **Algorithm**: HS256

### User Roles

- **admin**: Full system access
- **agent**: Travel agent - can manage bookings
- **customer**: End user - can manage own bookings

### Role-Based Access Control

```python
from app.core.auth import require_role, get_current_active_user

@router.post("/admin/users")
async def admin_only(current_user = Depends(require_role("admin"))):
    # Only admins can access
    pass
```

## Testing

Run comprehensive tests:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_booking.py -v

# Run with coverage
pytest --cov=app tests/
```

### Test Coverage

- User creation and management
- Passenger profiles
- Booking lifecycle
- Payment processing
- Role assignments
- Complete booking workflow

## Error Handling

Standard HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Auth required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Performance Considerations

1. **Connection Pooling**: 10 connections, max 20 overflow
2. **Database Indexes**: Created on all frequently queried columns
3. **Stored Procedures**: Executed server-side, minimal network overhead
4. **Pagination**: Recommended for list endpoints (future implementation)

## Security Best Practices

1. ✅ Passwords hashed with bcrypt
2. ✅ JWT token authentication
3. ✅ Role-based access control
4. ✅ SQL injection protection (parameterized queries)
5. ✅ CORS configuration
6. ✅ Environment variables for secrets
7. ✅ HTTPS recommended in production

## Future Enhancements

- [ ] Pagination for list endpoints
- [ ] Advanced search filters
- [ ] Refund processing procedures
- [ ] Invoice generation
- [ ] Seat availability checking
- [ ] Email notifications
- [ ] Payment gateway integration
- [ ] Multi-currency support
- [ ] Rate limiting
- [ ] API versioning

## Deployment

### Docker

```bash
docker build -t travel-api .
docker run -p 8000:8000 travel-api
```

### Kubernetes

See `Dockerfile` and deployment manifests for k8s configuration.

## Database Maintenance

### Backup

```bash
pg_dump -U user booking_db > backup.sql
```

### Restore

```bash
psql -U user booking_db < backup.sql
```

### Monitor Procedures

```sql
-- List all procedures
SELECT * FROM information_schema.routines 
WHERE routine_schema = 'booking';

-- Check procedure definition
\df+ booking.create_user
```

## Troubleshooting

### Connection Issues

```python
# Test database connection
python -c "from app.core.database import engine; print(engine.execute('SELECT 1'))"
```

### Migration Issues

```bash
# Check migration history
alembic current

# Downgrade to previous version
alembic downgrade -1

# Show SQL generated by migration
alembic upgrade --sql head
```

### Stored Procedure Issues

```sql
-- Check for syntax errors
SELECT * FROM booking.create_user('test@test.com', 'hash', 'Test');

-- View procedure definition
\df+ booking.create_user
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [PostgreSQL 14 Docs](https://www.postgresql.org/docs/14/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)

## License

Proprietary - All rights reserved

## Support

For issues or questions, contact the development team.
