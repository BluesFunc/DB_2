-- User Management Procedures
-- Includes: 6 procedures for user CRUD and role management

CREATE OR REPLACE FUNCTION booking.create_user(
    p_email TEXT,
    p_password_hash TEXT,
    p_full_name TEXT,
    p_phone TEXT DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    v_user_id BIGINT;
BEGIN
    INSERT INTO booking.users (email, password_hash, full_name, phone)
    VALUES (p_email, p_password_hash, p_full_name, p_phone)
    RETURNING id INTO v_user_id;
    
    RETURN v_user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.get_user_by_email(
    p_email TEXT
)
RETURNS TABLE(
    id BIGINT,
    email TEXT,
    password_hash TEXT,
    full_name TEXT,
    phone TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.email, u.password_hash, u.full_name, u.phone, u.is_active, u.created_at
    FROM booking.users u
    WHERE u.email = p_email;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.get_user_by_id(
    p_user_id BIGINT
)
RETURNS TABLE(
    id BIGINT,
    email TEXT,
    full_name TEXT,
    phone TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.email, u.full_name, u.phone, u.is_active, u.created_at
    FROM booking.users u
    WHERE u.id = p_user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.get_user_roles(
    p_user_id BIGINT
)
RETURNS TABLE(
    role_id BIGINT,
    code TEXT,
    name TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT r.id, r.code, r.name
    FROM booking.user_roles ur
    JOIN booking.roles r ON ur.role_id = r.id
    WHERE ur.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.assign_role_to_user(
    p_user_id BIGINT,
    p_role_code TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_role_id BIGINT;
BEGIN
    SELECT id INTO v_role_id FROM booking.roles WHERE code = p_role_code;
    
    IF v_role_id IS NULL THEN
        RETURN FALSE;
    END IF;
    
    INSERT INTO booking.user_roles (user_id, role_id)
    VALUES (p_user_id, v_role_id)
    ON CONFLICT DO NOTHING;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.update_user(
    p_user_id BIGINT,
    p_full_name TEXT DEFAULT NULL,
    p_phone TEXT DEFAULT NULL,
    p_is_active BOOLEAN DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE booking.users
    SET 
        full_name = COALESCE(p_full_name, full_name),
        phone = COALESCE(p_phone, phone),
        is_active = COALESCE(p_is_active, is_active)
    WHERE id = p_user_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.create_passenger_profile(
    p_user_id BIGINT,
    p_first_name TEXT,
    p_last_name TEXT,
    p_middle_name TEXT DEFAULT NULL,
    p_birth_date DATE DEFAULT NULL,
    p_doc_type TEXT DEFAULT NULL,
    p_doc_number TEXT DEFAULT NULL,
    p_citizenship TEXT DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    v_profile_id BIGINT;
BEGIN
    INSERT INTO booking.passenger_profiles 
        (user_id, first_name, last_name, middle_name, birth_date, doc_type, doc_number, citizenship)
    VALUES (p_user_id, p_first_name, p_last_name, p_middle_name, p_birth_date, p_doc_type, p_doc_number, p_citizenship)
    RETURNING id INTO v_profile_id;
    
    RETURN v_profile_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.get_passenger_profile(
    p_profile_id BIGINT
)
RETURNS TABLE(
    id BIGINT,
    user_id BIGINT,
    first_name TEXT,
    last_name TEXT,
    middle_name TEXT,
    birth_date DATE,
    doc_type TEXT,
    doc_number TEXT,
    citizenship TEXT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT pp.id, pp.user_id, pp.first_name, pp.last_name, pp.middle_name,
           pp.birth_date, pp.doc_type, pp.doc_number, pp.citizenship, pp.created_at
    FROM booking.passenger_profiles pp
    WHERE pp.id = p_profile_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.get_user_passengers(
    p_user_id BIGINT
)
RETURNS TABLE(
    id BIGINT,
    first_name TEXT,
    last_name TEXT,
    middle_name TEXT,
    birth_date DATE,
    doc_type TEXT,
    doc_number TEXT,
    citizenship TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT pp.id, pp.first_name, pp.last_name, pp.middle_name,
           pp.birth_date, pp.doc_type, pp.doc_number, pp.citizenship
    FROM booking.passenger_profiles pp
    WHERE pp.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;
