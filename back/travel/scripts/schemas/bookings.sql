-- Bookings and Travel Domain Schema
-- Includes: providers, terminals, routes, trips, segments, seat_maps, fares, bookings, tickets

-- ==================== PROVIDERS TABLE ====================
CREATE TABLE IF NOT EXISTS booking.providers (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    iata_code TEXT,                    -- For airlines
    inn_external TEXT,                 -- External identifier
    mode booking.transport_mode NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_providers_mode ON booking.providers(mode);

-- Trigger for updated_at on providers
DROP TRIGGER IF EXISTS trg_providers_updated ON booking.providers;
CREATE TRIGGER trg_providers_updated
BEFORE UPDATE ON booking.providers
FOR EACH ROW EXECUTE FUNCTION booking.set_updated_at();

-- ==================== TERMINALS TABLE ====================
CREATE TABLE IF NOT EXISTS booking.terminals (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,         -- IATA/railway/bus station code
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    timezone TEXT NOT NULL,            -- IANA timezone
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_terminals_city ON booking.terminals(city);

-- ==================== ROUTES TABLE ====================
CREATE TABLE IF NOT EXISTS booking.routes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    origin_id BIGINT NOT NULL REFERENCES booking.terminals(id),
    destination_id BIGINT NOT NULL REFERENCES booking.terminals(id),
    mode booking.transport_mode NOT NULL,
    provider_id BIGINT REFERENCES booking.providers(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(origin_id, destination_id, mode, provider_id)
);
CREATE INDEX IF NOT EXISTS ix_routes_search ON booking.routes(origin_id, destination_id, mode);

-- ==================== TRIPS TABLE ====================
CREATE TABLE IF NOT EXISTS booking.trips (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider_id BIGINT NOT NULL REFERENCES booking.providers(id),
    route_id BIGINT NOT NULL REFERENCES booking.routes(id),
    code TEXT NOT NULL,                -- Flight/train/bus number
    departure_utc TIMESTAMPTZ NOT NULL,
    arrival_utc TIMESTAMPTZ NOT NULL,
    equipment_code TEXT,               -- Aircraft/train type
    seat_map_id BIGINT,
    base_currency booking.money_currency NOT NULL DEFAULT 'EUR',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(provider_id, code, departure_utc)
);
CREATE INDEX IF NOT EXISTS ix_trips_search ON booking.trips(route_id, departure_utc DESC);
CREATE INDEX IF NOT EXISTS ix_trips_date ON booking.trips(departure_utc);

-- Trigger for updated_at on trips
DROP TRIGGER IF EXISTS trg_trips_updated ON booking.trips;
CREATE TRIGGER trg_trips_updated
BEFORE UPDATE ON booking.trips
FOR EACH ROW EXECUTE FUNCTION booking.set_updated_at();

-- ==================== TRIP SEGMENTS TABLE ====================
CREATE TABLE IF NOT EXISTS booking.trip_segments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    trip_id BIGINT NOT NULL REFERENCES booking.trips(id) ON DELETE CASCADE,
    seg_no INT NOT NULL,
    origin_id BIGINT NOT NULL REFERENCES booking.terminals(id),
    destination_id BIGINT NOT NULL REFERENCES booking.terminals(id),
    dep_utc TIMESTAMPTZ NOT NULL,
    arr_utc TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(trip_id, seg_no)
);
CREATE INDEX IF NOT EXISTS ix_trip_segments_trip ON booking.trip_segments(trip_id);

-- ==================== SEAT MAPS TABLE ====================
CREATE TABLE IF NOT EXISTS booking.seat_maps (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider_id BIGINT NOT NULL REFERENCES booking.providers(id),
    equipment_code TEXT NOT NULL,
    layout_json JSONB NOT NULL,        -- JSON describing cabin layout
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(provider_id, equipment_code)
);

-- ==================== FARES TABLE ====================
CREATE TABLE IF NOT EXISTS booking.fares (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    trip_id BIGINT NOT NULL REFERENCES booking.trips(id) ON DELETE CASCADE,
    fare_code TEXT NOT NULL,           -- Y, B, M, S, etc.
    cabin booking.cabin_class NOT NULL,
    price_amount NUMERIC(12, 2) NOT NULL,
    price_currency booking.money_currency NOT NULL,
    baggage_allowance TEXT,            -- '1PC 23kg', '10kg', '0', etc.
    rules_json JSONB,                  -- Exchange, refund rules
    seats_total INT,
    seats_sold INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(trip_id, fare_code, cabin)
);
CREATE INDEX IF NOT EXISTS ix_fares_trip ON booking.fares(trip_id, price_amount);
CREATE INDEX IF NOT EXISTS ix_fares_cabin ON booking.fares(trip_id, cabin);

-- Trigger for updated_at on fares
DROP TRIGGER IF EXISTS trg_fares_updated ON booking.fares;
CREATE TRIGGER trg_fares_updated
BEFORE UPDATE ON booking.fares
FOR EACH ROW EXECUTE FUNCTION booking.set_updated_at();

-- ==================== BOOKINGS TABLE ====================
CREATE TABLE IF NOT EXISTS booking.bookings (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES booking.users(id),
    status booking.booking_status NOT NULL DEFAULT 'TENTATIVE',
    hold_expires_at TIMESTAMPTZ,       -- TTL for reservation hold
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_bookings_user ON booking.bookings(user_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_bookings_status ON booking.bookings(status, created_at DESC);

-- Trigger for updated_at on bookings
DROP TRIGGER IF EXISTS trg_bookings_updated ON booking.bookings;
CREATE TRIGGER trg_bookings_updated
BEFORE UPDATE ON booking.bookings
FOR EACH ROW EXECUTE FUNCTION booking.set_updated_at();

-- ==================== TICKETS TABLE ====================
CREATE TABLE IF NOT EXISTS booking.tickets (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    booking_id BIGINT NOT NULL REFERENCES booking.bookings(id) ON DELETE CASCADE,
    passenger_id BIGINT NOT NULL REFERENCES booking.passenger_profiles(id),
    trip_id BIGINT NOT NULL REFERENCES booking.trips(id),
    fare_id BIGINT NOT NULL REFERENCES booking.fares(id),
    seat_no TEXT,                      -- A12, 03C, 15, etc.
    status booking.ticket_status NOT NULL DEFAULT 'ISSUED',
    ticket_number TEXT UNIQUE,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(trip_id, seat_no, issued_at) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX IF NOT EXISTS ix_tickets_booking ON booking.tickets(booking_id);
CREATE INDEX IF NOT EXISTS ix_tickets_trip ON booking.tickets(trip_id, status);
CREATE INDEX IF NOT EXISTS ix_tickets_passenger ON booking.tickets(passenger_id);

-- Trigger for updated_at on tickets
DROP TRIGGER IF EXISTS trg_tickets_updated ON booking.tickets;
CREATE TRIGGER trg_tickets_updated
BEFORE UPDATE ON booking.tickets
FOR EACH ROW EXECUTE FUNCTION booking.set_updated_at();
