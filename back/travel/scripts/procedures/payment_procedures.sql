-- Payment and Invoice Procedures
-- Includes: 3 procedures for payment management

CREATE OR REPLACE FUNCTION booking.create_payment(
    p_booking_id BIGINT,
    p_amount NUMERIC,
    p_currency TEXT,
    p_provider TEXT DEFAULT NULL,
    p_provider_ref TEXT DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    v_payment_id BIGINT;
BEGIN
    INSERT INTO booking.payments (booking_id, amount, currency, provider, provider_ref)
    VALUES (p_booking_id, p_amount, p_currency::booking.money_currency, p_provider, p_provider_ref)
    RETURNING id INTO v_payment_id;
    
    RETURN v_payment_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.get_booking_payments(
    p_booking_id BIGINT
)
RETURNS TABLE(
    id BIGINT,
    amount NUMERIC,
    currency TEXT,
    status TEXT,
    provider TEXT,
    provider_ref TEXT,
    created_at TIMESTAMPTZ,
    captured_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.amount, p.currency::TEXT, p.status::TEXT,
           p.provider, p.provider_ref, p.created_at, p.captured_at
    FROM booking.payments p
    WHERE p.booking_id = p_booking_id
    ORDER BY p.created_at DESC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.update_payment_status(
    p_payment_id BIGINT,
    p_status TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE booking.payments
    SET status = p_status::booking.payment_status,
        captured_at = CASE WHEN p_status = 'SUCCEEDED' THEN now() ELSE captured_at END
    WHERE id = p_payment_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;
