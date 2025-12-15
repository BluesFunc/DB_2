-- Users and Authentication Schema
-- Includes: users, roles, user_roles, passenger_profiles tables

-- ==================== USERS TABLE ====================
CREATE TABLE IF NOT EXISTS booking.users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_users_email ON booking.users(email);
CREATE INDEX IF NOT EXISTS ix_users_created ON booking.users(created_at DESC);

-- Trigger for updated_at on users
DROP TRIGGER IF EXISTS trg_users_updated ON booking.users;
CREATE TRIGGER trg_users_updated
BEFORE UPDATE ON booking.users
FOR EACH ROW EXECUTE FUNCTION booking.set_updated_at();

-- ==================== ROLES TABLE ====================
CREATE TABLE IF NOT EXISTS booking.roles (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ==================== USER ROLES JUNCTION TABLE ====================
CREATE TABLE IF NOT EXISTS booking.user_roles (
    user_id BIGINT NOT NULL REFERENCES booking.users(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES booking.roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, role_id)
);
CREATE INDEX IF NOT EXISTS ix_user_roles_role ON booking.user_roles(role_id);

-- ==================== PASSENGER PROFILES TABLE ====================
CREATE TABLE IF NOT EXISTS booking.passenger_profiles (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES booking.users(id) ON DELETE CASCADE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    middle_name TEXT,
    birth_date DATE,
    doc_type TEXT,                     -- 'passport', 'id', 'residence', etc.
    doc_number TEXT,
    citizenship TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_passenger_user ON booking.passenger_profiles(user_id);
CREATE INDEX IF NOT EXISTS ix_passenger_doc ON booking.passenger_profiles(doc_type, doc_number);

-- Trigger for updated_at on passenger_profiles
DROP TRIGGER IF EXISTS trg_passenger_profiles_updated ON booking.passenger_profiles;
CREATE TRIGGER trg_passenger_profiles_updated
BEFORE UPDATE ON booking.passenger_profiles
FOR EACH ROW EXECUTE FUNCTION booking.set_updated_at();
