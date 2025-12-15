-- Default Data - Initial seeding
-- Includes: Default roles

INSERT INTO booking.roles (code, name) 
VALUES ('admin', 'Administrator') ON CONFLICT (code) DO NOTHING;

INSERT INTO booking.roles (code, name) 
VALUES ('agent', 'Travel Agent') ON CONFLICT (code) DO NOTHING;

INSERT INTO booking.roles (code, name) 
VALUES ('customer', 'Customer') ON CONFLICT (code) DO NOTHING;
