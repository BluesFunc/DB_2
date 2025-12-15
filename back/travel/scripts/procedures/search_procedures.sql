-- Search and Discovery Procedures
-- Includes: 2 procedures for trip and fare search

CREATE OR REPLACE FUNCTION booking.search_trips(
    p_origin_id BIGINT,
    p_destination_id BIGINT,
    p_departure_date DATE,
    p_transport_mode TEXT DEFAULT NULL
)
RETURNS TABLE(
    trip_id BIGINT,
    provider_name TEXT,
    trip_code TEXT,
    departure_utc TIMESTAMPTZ,
    arrival_utc TIMESTAMPTZ,
    available_seats INT,
    base_currency TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        pr.name,
        t.code,
        t.departure_utc,
        t.arrival_utc,
        COALESCE(SUM(f.seats_total - f.seats_sold), 0)::INT,
        t.base_currency::TEXT
    FROM booking.trips t
    JOIN booking.providers pr ON t.provider_id = pr.id
    JOIN booking.routes r ON t.route_id = r.id
    LEFT JOIN booking.fares f ON t.id = f.trip_id
    WHERE r.origin_id = p_origin_id
      AND r.destination_id = p_destination_id
      AND DATE(t.departure_utc) = p_departure_date
      AND t.is_active = TRUE
      AND (p_transport_mode IS NULL OR r.mode::TEXT = p_transport_mode)
    GROUP BY t.id, pr.name, t.code, t.departure_utc, t.arrival_utc, t.base_currency
    ORDER BY t.departure_utc ASC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION booking.get_trip_fares(
    p_trip_id BIGINT
)
RETURNS TABLE(
    fare_id BIGINT,
    fare_code TEXT,
    cabin TEXT,
    price_amount NUMERIC,
    price_currency TEXT,
    baggage_allowance TEXT,
    available_seats INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id,
        f.fare_code,
        f.cabin::TEXT,
        f.price_amount,
        f.price_currency::TEXT,
        f.baggage_allowance,
        (COALESCE(f.seats_total, 0) - f.seats_sold)::INT
    FROM booking.fares f
    WHERE f.trip_id = p_trip_id
    ORDER BY f.price_amount ASC;
END;
$$ LANGUAGE plpgsql;
