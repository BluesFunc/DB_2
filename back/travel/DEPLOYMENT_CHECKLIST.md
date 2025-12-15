# Deployment Checklist

## Pre-Deployment Verification

### ✅ Code Review Checklist
- [x] All imports are correct and available
- [x] No hardcoded credentials in code
- [x] Error handling in place
- [x] Logging configured
- [x] Type hints throughout
- [x] Docstrings present
- [x] No TODO/FIXME comments left
- [x] Tests passing
- [x] No circular imports
- [x] Database migrations tested

### ✅ Security Checklist
- [x] Passwords hashed with bcrypt
- [x] JWT tokens with proper expiration
- [x] Role-based access control implemented
- [x] SQL injection protection (parameterized queries)
- [x] CORS properly configured
- [x] Secrets in environment variables
- [x] HTTPS recommended in production
- [x] Rate limiting ready to add
- [x] Input validation on all endpoints
- [x] User ownership validated

### ✅ Database Checklist
- [x] PostgreSQL 14 compatible
- [x] Migrations tested
- [x] All tables created
- [x] All indexes created
- [x] All procedures created
- [x] Relationships verified
- [x] Constraints in place
- [x] Triggers working
- [x] Default data inserted
- [x] Backup strategy documented

### ✅ API Checklist
- [x] All endpoints implemented
- [x] Request validation working
- [x] Response serialization correct
- [x] Error messages user-friendly
- [x] Status codes appropriate
- [x] Documentation complete
- [x] OpenAPI schema generated
- [x] Swagger UI working
- [x] CORS headers set
- [x] Health check endpoint working

### ✅ Testing Checklist
- [x] Unit tests written
- [x] Integration tests written
- [x] Tests passing locally
- [x] Test coverage adequate
- [x] Error cases tested
- [x] Edge cases covered
- [x] Fixtures working
- [x] Mock data valid
- [x] Test database isolated
- [x] Tests are deterministic

### ✅ Documentation Checklist
- [x] QUICKSTART.md complete
- [x] IMPLEMENTATION_GUIDE.md complete
- [x] IMPLEMENTATION_SUMMARY.md complete
- [x] COMPLETION_CHECKLIST.md complete
- [x] MANUAL_TESTING.sql complete
- [x] Code comments present
- [x] API endpoints documented
- [x] Error codes documented
- [x] Database schema documented
- [x] Procedures documented

### ✅ Configuration Checklist
- [x] .env.example created
- [x] requirements.txt updated
- [x] alembic.ini configured
- [x] pytest.ini configured
- [x] logging configured
- [x] CORS configured
- [x] Database pooling configured
- [x] JWT settings configured
- [x] All env vars documented
- [x] Defaults sensible

## Deployment Steps

### 1. Prepare Production Server

```bash
# Install Python 3.10+
python --version

# Install PostgreSQL 14
pg_version

# Create dedicated database user
sudo useradd -m -s /bin/bash booking-api

# Create application directory
sudo mkdir -p /opt/travel-api
sudo chown booking-api:booking-api /opt/travel-api
```

### 2. Clone and Setup Application

```bash
# Clone repository
cd /opt/travel-api
git clone <repository-url> .

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with production settings
cat > .env << 'EOF'
DATABASE_URL=postgresql://booking_user:SECURE_PASSWORD@db.example.com:5432/booking_db
SECRET_KEY=generate-long-random-string-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=False
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["https://yourapp.com"]
EOF

chmod 600 .env
```

### 3. Setup Database

```bash
# Create database and user
psql -U postgres << 'EOF'
CREATE DATABASE booking_db;
CREATE USER booking_user WITH PASSWORD 'SECURE_PASSWORD';
ALTER ROLE booking_user SET client_encoding TO 'utf8';
ALTER ROLE booking_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE booking_user SET default_transaction_deferrable TO on;
ALTER ROLE booking_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE booking_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE booking_db TO booking_user;
EOF

# Run migrations
alembic upgrade head

# Verify migrations
alembic current
```

### 4. Configure Web Server

#### Using Gunicorn + Nginx

**Create systemd service file:**
```bash
sudo cat > /etc/systemd/system/travel-api.service << 'EOF'
[Unit]
Description=Travel Booking API
After=network.target postgresql.service

[Service]
Type=notify
User=booking-api
WorkingDirectory=/opt/travel-api
Environment="PATH=/opt/travel-api/venv/bin"
ExecStart=/opt/travel-api/venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/travel-api/access.log \
    --error-logfile /var/log/travel-api/error.log
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
sudo mkdir -p /var/log/travel-api
sudo chown booking-api:booking-api /var/log/travel-api

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable travel-api
sudo systemctl start travel-api
```

**Configure Nginx:**
```nginx
upstream travel_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;
    client_max_body_size 10M;

    location / {
        proxy_pass http://travel_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://travel_api;
        access_log off;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    # ... rest of configuration
}
```

#### Using Docker

```dockerfile
# See Dockerfile in repository
docker build -t travel-api:latest .
docker run -d \
    -p 8000:8000 \
    -e DATABASE_URL="postgresql://user:pass@db:5432/booking_db" \
    -e SECRET_KEY="your-secret-key" \
    --name travel-api \
    travel-api:latest
```

### 5. Setup Monitoring

```bash
# Install and configure logging
sudo apt-get install rsyslog

# Configure log rotation
sudo cat > /etc/logrotate.d/travel-api << 'EOF'
/var/log/travel-api/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 booking-api booking-api
    sharedscripts
    postrotate
        systemctl reload travel-api
    endscript
}
EOF
```

### 6. Run Tests in Production

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_booking.py -v

# Run with coverage
pytest --cov=app tests/

# Test database connection
python -c "from app.core.database import engine; print(engine.execute('SELECT 1'))"
```

### 7. Health Checks

```bash
# Check application is running
curl -s http://localhost:8000/api/v1/health/status | jq

# Check database is connected
curl -s http://localhost:8000/api/v1/health/status | grep -q "database" && echo "DB OK"

# Monitor logs
tail -f /var/log/travel-api/error.log
tail -f /var/log/travel-api/access.log
```

### 8. Backup Strategy

```bash
# Daily database backup
cat > /usr/local/bin/backup-booking-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/booking-db"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="booking_db_$DATE.sql.gz"

mkdir -p $BACKUP_DIR
pg_dump -U booking_user booking_db | gzip > $BACKUP_DIR/$FILENAME

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $FILENAME"
EOF

chmod +x /usr/local/bin/backup-booking-db.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-booking-db.sh") | crontab -
```

## Post-Deployment Verification

### ✅ Verify API is Running
```bash
# Check health endpoint
curl -s http://localhost:8000/api/v1/health/status

# Expected response:
# {"status":"healthy","database":"connected"}
```

### ✅ Test Authentication
```bash
# Register test user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

### ✅ Check Logs
```bash
# Check for errors
grep ERROR /var/log/travel-api/error.log

# Check recent activity
tail -20 /var/log/travel-api/access.log
```

### ✅ Database Verification
```bash
# Connect to production database
psql -U booking_user -d booking_db -h localhost

# Verify tables exist
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'booking';

# Verify procedures exist
SELECT COUNT(*) FROM information_schema.routines 
WHERE routine_schema = 'booking';

# Check for data
SELECT COUNT(*) FROM booking.users;
```

## Monitoring & Alerts

### Application Monitoring
```bash
# Monitor process
watch -n 5 'systemctl status travel-api'

# Monitor database connections
watch -n 5 'psql -U booking_user -d booking_db -c "SELECT count(*) FROM pg_stat_activity;"'

# Monitor disk space
watch -n 60 'df -h | grep -E "^/dev|^Filesystem"'
```

### Set Up Alerts
- Database connection pool saturation
- High error rate in application
- Slow queries in database
- Disk space below 10%
- API response time > 5 seconds

## Rollback Plan

If deployment fails:

```bash
# Stop application
sudo systemctl stop travel-api

# Rollback to previous version
cd /opt/travel-api
git checkout previous-tag
source venv/bin/activate
pip install -r requirements.txt

# Rollback database (if needed)
alembic downgrade -1

# Start application
sudo systemctl start travel-api

# Verify
curl http://localhost:8000/api/v1/health/status
```

## Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Database Backup | Daily | cron job |
| Log Rotation | Daily | logrotate |
| Security Updates | Weekly | `apt update && apt upgrade` |
| Database Optimization | Monthly | `VACUUM ANALYZE;` |
| Dependency Updates | Monthly | `pip list --outdated` |
| Certificate Renewal | Auto | Let's Encrypt |

## Support Contacts

- Database Administrator: [contact]
- Application Owner: [contact]
- DevOps Team: [contact]
- On-Call: [contact]

## Sign-Off

- [ ] Code review passed
- [ ] Tests passed
- [ ] Database migrations verified
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Backup strategy verified
- [ ] Monitoring configured
- [ ] Documentation reviewed

**Deployment approved by:** _______________  
**Date:** _______________  
**Version:** _______________
