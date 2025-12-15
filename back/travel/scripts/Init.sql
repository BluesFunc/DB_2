-- Travel Booking System - Database Initialization Orchestrator
-- Single entry point that orchestrates schema setup, procedures, and data
-- Run on application startup - idempotent with IF NOT EXISTS checks

SET client_min_messages TO WARNING;

-- Check if schema exists and needs initialization
DO $$
DECLARE
    v_version_exists BOOLEAN;
BEGIN
    -- Check if schema_version table exists
    v_version_exists := EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'booking' AND table_name = 'schema_version'
    );
    
    IF NOT v_version_exists THEN
        -- First time setup - execute all SQL files in correct order
        -- 1. Core schema with enums, version table, audit logging
        \i scripts/schemas/core.sql
        
        -- 2. Domain-specific schemas
        \i scripts/schemas/users.sql
        \i scripts/schemas/bookings.sql
        \i scripts/schemas/payments.sql
        
        -- 3. Stored procedures organized by business logic
        \i scripts/procedures/user_procedures.sql
        \i scripts/procedures/booking_procedures.sql
        \i scripts/procedures/payment_procedures.sql
        \i scripts/procedures/search_procedures.sql
        \i scripts/procedures/logging_procedures.sql
        
        -- 4. Default data
        \i scripts/data/defaults.sql
        
        -- 5. Record version for tracking
        INSERT INTO booking.schema_version (version, notes) 
        VALUES ('1.0', 'Initial schema setup with 17 tables, 20 procedures, audit logging');
        
        RAISE NOTICE 'Database schema initialized successfully (v1.0)';
    ELSE
        RAISE NOTICE 'Database schema already initialized';
    END IF;
END $$;

SET client_min_messages TO DEFAULT;


