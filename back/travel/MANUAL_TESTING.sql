-- Manual Database Testing Guide
-- Run these queries directly in psql to test the system

-- ==================== SETUP ====================

-- Check schema exists
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'booking';

-- List all procedures
\df+ booking.*

-- Check roles inserted
SELECT * FROM booking.roles;

-- ==================== USER OPERATIONS ====================

-- Test user creation
SELECT booking.create_user(
    'testuser@example.com',
    '$2b$12$...',  -- bcrypt hash of password
    'Test User',
    '+1234567890'
);

-- Get user by email
SELECT * FROM booking.get_user_by_email('testuser@example.com');

-- Get user by ID (replace 1 with actual user_id)
SELECT * FROM booking.get_user_by_id(1);

-- Get user roles
SELECT * FROM booking.get_user_roles(1);

-- Assign role
SELECT booking.assign_role_to_user(1, 'customer');

-- Update user
SELECT booking.update_user(1, 'Updated Name', '+9999999999', true);

-- ==================== PASSENGER OPERATIONS ====================

-- Create passenger profile
SELECT booking.create_passenger_profile(
    1,                          -- user_id
    'John',                     -- first_name
    'Doe',                      -- last_name
    'Michael',                  -- middle_name
    '1990-05-15'::date,        -- birth_date
    'passport',                 -- doc_type
    'AB123456',                 -- doc_number
    'USA'                       -- citizenship
);

-- Get passenger profile (replace 1 with actual profile_id)
SELECT * FROM booking.get_passenger_profile(1);

-- Get all passengers for user
SELECT * FROM booking.get_user_passengers(1);

-- ==================== BOOKING OPERATIONS ====================

-- Create booking
SELECT booking.create_booking(
    1,                                          -- user_id
    now() + interval '2 hours'                 -- hold_expires_at
);

-- Get booking (replace 1 with actual booking_id)
SELECT * FROM booking.get_booking(1);

-- Get all user bookings
SELECT * FROM booking.get_user_bookings(1, NULL);

-- Get user bookings by status
SELECT * FROM booking.get_user_bookings(1, 'TENTATIVE');

-- Update booking status
SELECT booking.update_booking_status(1, 'CONFIRMED');

-- ==================== PAYMENT OPERATIONS ====================

-- Create payment
SELECT booking.create_payment(
    1,                  -- booking_id
    199.99,            -- amount
    'EUR',             -- currency
    'stripe',          -- provider
    'ch_test_123'      -- provider_ref
);

-- Get all payments for booking
SELECT * FROM booking.get_booking_payments(1);

-- Update payment status
SELECT booking.update_payment_status(1, 'SUCCEEDED');

-- ==================== TICKET OPERATIONS ====================

-- Create ticket (requires existing trip_id and fare_id)
SELECT booking.create_ticket(
    1,                  -- booking_id
    1,                  -- passenger_id
    1,                  -- trip_id
    1,                  -- fare_id
    'A12',             -- seat_no
    'TK123456'         -- ticket_number
);

-- Get tickets for booking
SELECT * FROM booking.get_booking_tickets(1);

-- Update ticket status
SELECT booking.update_ticket_status(1, 'CHECKED_IN');

-- ==================== TRIP SEARCH OPERATIONS ====================

-- Before testing trip search, you need to add test data:

-- Insert terminal data
INSERT INTO booking.terminals (code, name, city, country, timezone)
VALUES 
    ('CDG', 'Charles de Gaulle', 'Paris', 'France', 'Europe/Paris'),
    ('LHR', 'Heathrow', 'London', 'UK', 'Europe/London')
RETURNING id;

-- Insert provider
INSERT INTO booking.providers (name, mode, iata_code)
VALUES ('Air France', 'AIR'::booking.transport_mode, 'AF')
RETURNING id;

-- Insert route
INSERT INTO booking.routes (origin_id, destination_id, mode, provider_id)
VALUES 
    (1, 2, 'AIR'::booking.transport_mode, 1)  -- Replace IDs with actual terminal IDs
RETURNING id;

-- Insert trip
INSERT INTO booking.trips (
    provider_id, route_id, code, departure_utc, arrival_utc, 
    base_currency, is_active
)
VALUES 
    (1, 1, 'AF100', now() + interval '1 day', now() + interval '1 day 3 hours', 
     'EUR'::booking.money_currency, true)
RETURNING id;

-- Insert fare
INSERT INTO booking.fares (
    trip_id, fare_code, cabin, price_amount, price_currency, 
    baggage_allowance, seats_total, seats_sold
)
VALUES 
    (1, 'Y', 'ECONOMY'::booking.cabin_class, 199.99, 'EUR'::booking.money_currency, 
     '1PC 23kg', 180, 0)
RETURNING id;

-- Now search trips
SELECT * FROM booking.search_trips(
    1,                                          -- origin_id
    2,                                          -- destination_id
    CURRENT_DATE + interval '1 day',           -- departure_date
    'AIR'                                       -- transport_mode
);

-- Get fares for trip
SELECT * FROM booking.get_trip_fares(1);

-- ==================== DATA VERIFICATION ====================

-- Count records in main tables
SELECT 
    'users' as table_name, COUNT(*) as count FROM booking.users
UNION ALL
SELECT 'bookings', COUNT(*) FROM booking.bookings
UNION ALL
SELECT 'tickets', COUNT(*) FROM booking.tickets
UNION ALL
SELECT 'payments', COUNT(*) FROM booking.payments
UNION ALL
SELECT 'passenger_profiles', COUNT(*) FROM booking.passenger_profiles;

-- View user with their roles
SELECT 
    u.id,
    u.email,
    u.full_name,
    array_agg(r.code) as roles
FROM booking.users u
LEFT JOIN booking.user_roles ur ON u.id = ur.user_id
LEFT JOIN booking.roles r ON ur.role_id = r.id
GROUP BY u.id, u.email, u.full_name;

-- View booking details with related data
SELECT 
    b.id as booking_id,
    b.status,
    u.email,
    COUNT(t.id) as ticket_count,
    SUM(p.amount) as total_paid
FROM booking.bookings b
JOIN booking.users u ON b.user_id = u.id
LEFT JOIN booking.tickets t ON b.id = t.booking_id
LEFT JOIN booking.payments p ON b.id = p.booking_id
GROUP BY b.id, b.status, u.email;

-- ==================== TRANSACTION EXAMPLE ====================

-- Complete booking transaction (run all together)
BEGIN;

-- 1. Create booking
WITH booking_created AS (
    SELECT booking.create_booking(1, now() + interval '2 hours') as booking_id
)
-- 2. Create payment
, payment_created AS (
    SELECT booking.create_payment(
        (SELECT booking_id FROM booking_created),
        299.99,
        'EUR',
        'stripe',
        'ch_test_' || floor(random() * 1000000)::text
    ) as payment_id
)
-- 3. Update payment status
, payment_confirmed AS (
    SELECT booking.update_payment_status(
        (SELECT payment_id FROM payment_created),
        'SUCCEEDED'
    ) as success
)
-- 4. Confirm booking
SELECT booking.update_booking_status(
    (SELECT booking_id FROM booking_created),
    'CONFIRMED'
) as final_status;

COMMIT;

-- ==================== INDEX USAGE ====================

-- Check if indexes are being used
EXPLAIN ANALYZE
SELECT * FROM booking.trips 
WHERE route_id = 1 AND departure_utc > now();

EXPLAIN ANALYZE
SELECT * FROM booking.fares 
WHERE trip_id = 1 AND price_amount < 300;

EXPLAIN ANALYZE
SELECT * FROM booking.bookings 
WHERE user_id = 1 AND status::text = 'CONFIRMED'
ORDER BY created_at DESC;

-- ==================== PERFORMANCE MONITORING ====================

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'booking'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check slow queries (enable if configured)
-- SELECT * FROM pg_stat_statements 
-- WHERE query LIKE '%booking%' 
-- ORDER BY mean_time DESC LIMIT 10;

-- ==================== CLEANUP ====================

-- Delete test data (optional)
-- DELETE FROM booking.payments WHERE booking_id > 0;
-- DELETE FROM booking.tickets WHERE booking_id > 0;
-- DELETE FROM booking.bookings WHERE user_id > 0;
-- DELETE FROM booking.passenger_profiles WHERE user_id > 0;
-- DELETE FROM booking.user_roles WHERE user_id > 0;
-- DELETE FROM booking.users WHERE email LIKE '%test%';

-- ==================== ERROR HANDLING TESTS ====================

-- Test duplicate email (should fail)
SELECT booking.create_user(
    'testuser@example.com',
    'hash',
    'Another User'
);
-- Should raise: duplicate key value violates unique constraint

-- Test invalid role (should return false)
SELECT booking.assign_role_to_user(1, 'invalid_role');
-- Should return: false

-- Test non-existent user (should return empty)
SELECT * FROM booking.get_user_by_id(99999);
-- Should return: (no rows)

-- ==================== USEFUL QUERIES ====================

-- Find all bookings with pending payments
SELECT b.*, p.*
FROM booking.bookings b
JOIN booking.payments p ON b.id = p.booking_id
WHERE p.status::text = 'PENDING';

-- Find bookings that are about to expire
SELECT b.*
FROM booking.bookings b
WHERE b.status::text = 'TENTATIVE' 
  AND b.hold_expires_at < now() + interval '1 hour'
  AND b.hold_expires_at > now();

-- Find most popular routes
SELECT 
    r.id,
    t.name as origin,
    t2.name as destination,
    COUNT(tr.id) as trip_count
FROM booking.routes r
JOIN booking.terminals t ON r.origin_id = t.id
JOIN booking.terminals t2 ON r.destination_id = t2.id
LEFT JOIN booking.trips tr ON r.id = tr.route_id
GROUP BY r.id, t.name, t2.name
ORDER BY trip_count DESC;

-- Find high-value bookings
SELECT 
    b.id,
    u.email,
    SUM(p.amount) as total_spent,
    COUNT(DISTINCT t.id) as ticket_count
FROM booking.bookings b
JOIN booking.users u ON b.user_id = u.id
LEFT JOIN booking.payments p ON b.id = p.booking_id
LEFT JOIN booking.tickets t ON b.id = t.booking_id
GROUP BY b.id, u.email
HAVING SUM(p.amount) > 1000
ORDER BY total_spent DESC;

-- Export booking data to CSV format
COPY (
    SELECT 
        b.id, u.email, b.status, COUNT(t.id) as tickets, 
        SUM(p.amount) as total, b.created_at
    FROM booking.bookings b
    JOIN booking.users u ON b.user_id = u.id
    LEFT JOIN booking.tickets t ON b.id = t.booking_id
    LEFT JOIN booking.payments p ON b.id = p.booking_id
    GROUP BY b.id, u.email, b.status, b.created_at
    ORDER BY b.created_at DESC
) TO '/tmp/bookings.csv' WITH CSV HEADER;
