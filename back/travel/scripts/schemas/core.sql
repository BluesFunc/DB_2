-- Core Schema - Foundation layer
-- Includes: Schema, ENUM types, version tracking, audit logging, triggers

-- Create booking schema
CREATE SCHEMA IF NOT EXISTS booking;
SET search_path TO booking;

-- ==================== ENUM TYPES ====================
CREATE TYPE booking.money_currency AS ENUM ('EUR', 'USD', 'BYN');
CREATE TYPE booking.booking_status AS ENUM ('TENTATIVE', 'CONFIRMED', 'CANCELLED', 'EXPIRED');
CREATE TYPE booking.ticket_status AS ENUM ('ISSUED', 'VOIDED', 'REFUNDED', 'CHECKED_IN');
CREATE TYPE booking.payment_status AS ENUM ('PENDING', 'SUCCEEDED', 'FAILED', 'REFUNDED', 'PARTIALLY_REFUNDED');
CREATE TYPE booking.transport_mode AS ENUM ('AIR', 'RAIL', 'BUS');
CREATE TYPE booking.cabin_class AS ENUM ('ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST');

-- ==================== VERSION TRACKING ====================
CREATE TABLE IF NOT EXISTS booking.schema_version (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    version TEXT NOT NULL UNIQUE,
    deployed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes TEXT
);

-- ==================== AUDIT LOGGING ====================
CREATE TABLE IF NOT EXISTS booking.audit_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT,
    action TEXT NOT NULL,              -- 'CREATE', 'READ', 'UPDATE', 'DELETE'
    resource_type TEXT NOT NULL,       -- 'user', 'booking', 'payment', 'ticket', etc.
    resource_id BIGINT,
    method TEXT NOT NULL,              -- 'GET', 'POST', 'PUT', 'DELETE', 'PATCH'
    status_code INT,
    details_json JSONB,                -- error messages, changed fields, metadata
    ip_address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_audit_user ON booking.audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_audit_resource ON booking.audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS ix_audit_action ON booking.audit_logs(action, created_at DESC);

-- ==================== TRIGGER FUNCTIONS ====================
DROP FUNCTION IF EXISTS booking.set_updated_at() CASCADE;

CREATE OR REPLACE FUNCTION booking.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
