-- Booking and Ticket Procedures
-- Includes: 7 procedures for booking and ticket management

CREATE OR REPLACE FUNCTION booking.create_booking(
    p_user_id BIGINT,
    p_hold_expires_at TIMESTAMPTZ DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    v_booking_id BIGINT;
BEGIN
    INSERT INTO booking.bookings (user_id, status, hold_expires_at)
    VALUES (p_user_id, 'TENTATIVE'::booking.booking_status, p_hold_expires_at)
    RETURNING id INTO v_booking_id;
    
    RETURN v_booking_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.get_booking(
    p_booking_id BIGINT
)
RETURNS TABLE(
    id BIGINT,
    user_id BIGINT,
    status TEXT,
    hold_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT b.id, b.user_id, b.status::TEXT, b.hold_expires_at, b.created_at, b.updated_at
    FROM booking.bookings b
    WHERE b.id = p_booking_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.get_user_bookings(
    p_user_id BIGINT,
    p_status TEXT DEFAULT NULL
)
RETURNS TABLE(
    id BIGINT,
    status TEXT,
    hold_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT b.id, b.status::TEXT, b.hold_expires_at, b.created_at, b.updated_at
    FROM booking.bookings b
    WHERE b.user_id = p_user_id
      AND (p_status IS NULL OR b.status::TEXT = p_status)
    ORDER BY b.created_at DESC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.update_booking_status(
    p_booking_id BIGINT,
    p_status TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE booking.bookings
    SET status = p_status::booking.booking_status
    WHERE id = p_booking_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.create_ticket(
    p_booking_id BIGINT,
    p_passenger_id BIGINT,
    p_trip_id BIGINT,
    p_fare_id BIGINT,
    p_seat_no TEXT DEFAULT NULL,
    p_ticket_number TEXT DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    v_ticket_id BIGINT;
BEGIN
    INSERT INTO booking.tickets 
        (booking_id, passenger_id, trip_id, fare_id, seat_no, ticket_number)
    VALUES (p_booking_id, p_passenger_id, p_trip_id, p_fare_id, p_seat_no, p_ticket_number)
    RETURNING id INTO v_ticket_id;
    
    RETURN v_ticket_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.get_booking_tickets(
    p_booking_id BIGINT
)
RETURNS TABLE(
    id BIGINT,
    passenger_id BIGINT,
    trip_id BIGINT,
    fare_id BIGINT,
    seat_no TEXT,
    status TEXT,
    ticket_number TEXT,
    issued_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT t.id, t.passenger_id, t.trip_id, t.fare_id, t.seat_no,
           t.status::TEXT, t.ticket_number, t.issued_at
    FROM booking.tickets t
    WHERE t.booking_id = p_booking_id
    ORDER BY t.issued_at DESC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.update_ticket_status(
    p_ticket_id BIGINT,
    p_status TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE booking.tickets
    SET status = p_status::booking.ticket_status
    WHERE id = p_ticket_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;
