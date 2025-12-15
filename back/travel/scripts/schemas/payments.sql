-- Payments and Financial Domain Schema
-- Includes: payment_methods, payments, invoices, refund_requests

-- ==================== PAYMENT METHODS TABLE ====================
CREATE TABLE IF NOT EXISTS booking.payment_methods (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES booking.users(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,                -- 'card', 'apple_pay', 'sbp', 'wallet', etc.
    details_json JSONB NOT NULL,       -- Tokenized payment details
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_payment_methods_user ON booking.payment_methods(user_id);
CREATE INDEX IF NOT EXISTS ix_payment_methods_default ON booking.payment_methods(user_id, is_default);

-- Trigger for updated_at on payment_methods
DROP TRIGGER IF EXISTS trg_payment_methods_updated ON booking.payment_methods;
CREATE TRIGGER trg_payment_methods_updated
BEFORE UPDATE ON booking.payment_methods
FOR EACH ROW EXECUTE FUNCTION booking.set_updated_at();

-- ==================== PAYMENTS TABLE ====================
CREATE TABLE IF NOT EXISTS booking.payments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    booking_id BIGINT NOT NULL REFERENCES booking.bookings(id) ON DELETE CASCADE,
    amount NUMERIC(12, 2) NOT NULL,
    currency booking.money_currency NOT NULL,
    status booking.payment_status NOT NULL DEFAULT 'PENDING',
    provider TEXT,                     -- PSP: Stripe, Adyen, YooKassa, etc.
    provider_ref TEXT,                 -- External transaction ID
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    captured_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_payments_booking ON booking.payments(booking_id, status);
CREATE INDEX IF NOT EXISTS ix_payments_status ON booking.payments(status, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_payments_created ON booking.payments(created_at DESC);

-- Trigger for updated_at on payments
DROP TRIGGER IF EXISTS trg_payments_updated ON booking.payments;
CREATE TRIGGER trg_payments_updated
BEFORE UPDATE ON booking.payments
FOR EACH ROW EXECUTE FUNCTION booking.set_updated_at();

-- ==================== INVOICES TABLE ====================
CREATE TABLE IF NOT EXISTS booking.invoices (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    booking_id BIGINT NOT NULL REFERENCES booking.bookings(id) ON DELETE CASCADE,
    total_amount NUMERIC(12, 2) NOT NULL,
    currency booking.money_currency NOT NULL,
    tax_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    details_json JSONB,                -- Line items, discounts, fees
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(booking_id)
);
CREATE INDEX IF NOT EXISTS ix_invoices_booking ON booking.invoices(booking_id);
CREATE INDEX IF NOT EXISTS ix_invoices_issued ON booking.invoices(issued_at DESC);

-- ==================== REFUND REQUESTS TABLE ====================
CREATE TABLE IF NOT EXISTS booking.refund_requests (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticket_id BIGINT NOT NULL REFERENCES booking.tickets(id) ON DELETE CASCADE,
    reason TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',  -- 'PENDING', 'APPROVED', 'REJECTED', 'PROCESSED'
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_refund_requests_ticket ON booking.refund_requests(ticket_id);
CREATE INDEX IF NOT EXISTS ix_refund_requests_status ON booking.refund_requests(status, requested_at DESC);

-- Trigger for updated_at on refund_requests
DROP TRIGGER IF EXISTS trg_refund_requests_updated ON booking.refund_requests;
CREATE TRIGGER trg_refund_requests_updated
BEFORE UPDATE ON booking.refund_requests
FOR EACH ROW EXECUTE FUNCTION booking.set_updated_at();
