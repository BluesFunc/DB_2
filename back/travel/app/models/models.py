from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Date, Numeric, BigInteger, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.sql import func
from datetime import datetime, date
from decimal import Decimal
from app.core.database import Base


# Enums
money_currency_enum = ENUM('EUR', 'USD', 'BYN', name='money_currency', create_type=False)
booking_status_enum = ENUM('TENTATIVE', 'CONFIRMED', 'CANCELLED', 'EXPIRED', name='booking_status', create_type=False)
ticket_status_enum = ENUM('ISSUED', 'VOIDED', 'REFUNDED', 'CHECKED_IN', name='ticket_status', create_type=False)
payment_status_enum = ENUM('PENDING', 'SUCCEEDED', 'FAILED', 'REFUNDED', 'PARTIALLY_REFUNDED', name='payment_status', create_type=False)
transport_mode_enum = ENUM('AIR', 'RAIL', 'BUS', name='transport_mode', create_type=False)
cabin_class_enum = ENUM('ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST', name='cabin_class', create_type=False)


class User(Base):
    __tablename__ = "users"
    __table_args__ = ({"schema": "booking"},)
    
    id = Column(BigInteger, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = ({"schema": "booking"},)
    
    id = Column(BigInteger, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = ({"schema": "booking"},)
    
    user_id = Column(BigInteger, ForeignKey("booking.users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(BigInteger, ForeignKey("booking.roles.id", ondelete="CASCADE"), primary_key=True)


class PassengerProfile(Base):
    __tablename__ = "passenger_profiles"
    __table_args__ = (Index('ix_passenger_user', 'user_id'), {"schema": "booking"})
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("booking.users.id", ondelete="CASCADE"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    doc_type = Column(String, nullable=True)
    doc_number = Column(String, nullable=True)
    citizenship = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Provider(Base):
    __tablename__ = "providers"
    __table_args__ = ({"schema": "booking"},)
    
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    iata_code = Column(String, nullable=True)
    inn_external = Column(String, nullable=True)
    mode = Column(transport_mode_enum, nullable=False)
    active = Column(Boolean, default=True, nullable=False)


class Terminal(Base):
    __tablename__ = "terminals"
    __table_args__ = (UniqueConstraint('code'), {"schema": "booking"})
    
    id = Column(BigInteger, primary_key=True)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    timezone = Column(String, nullable=False)


class Route(Base):
    __tablename__ = "routes"
    __table_args__ = (
        UniqueConstraint('origin_id', 'destination_id', 'mode', 'provider_id'),
        Index('ix_routes_search', 'origin_id', 'destination_id', 'mode'),
        {"schema": "booking"}
    )
    
    id = Column(BigInteger, primary_key=True)
    origin_id = Column(BigInteger, ForeignKey("booking.terminals.id"), nullable=False)
    destination_id = Column(BigInteger, ForeignKey("booking.terminals.id"), nullable=False)
    mode = Column(transport_mode_enum, nullable=False)
    provider_id = Column(BigInteger, ForeignKey("booking.providers.id"), nullable=True)


class SeatMap(Base):
    __tablename__ = "seat_maps"
    __table_args__ = (
        UniqueConstraint('provider_id', 'equipment_code'),
        {"schema": "booking"}
    )
    
    id = Column(BigInteger, primary_key=True)
    provider_id = Column(BigInteger, ForeignKey("booking.providers.id"), nullable=False)
    equipment_code = Column(String, nullable=False)
    layout_json = Column(JSONB, nullable=False)


class Trip(Base):
    __tablename__ = "trips"
    __table_args__ = (
        UniqueConstraint('provider_id', 'code', 'departure_utc'),
        Index('ix_trips_search', 'route_id', 'departure_utc'),
        {"schema": "booking"}
    )
    
    id = Column(BigInteger, primary_key=True)
    provider_id = Column(BigInteger, ForeignKey("booking.providers.id"), nullable=False)
    route_id = Column(BigInteger, ForeignKey("booking.routes.id"), nullable=False)
    code = Column(String, nullable=False)
    departure_utc = Column(DateTime(timezone=True), nullable=False)
    arrival_utc = Column(DateTime(timezone=True), nullable=False)
    equipment_code = Column(String, nullable=True)
    seat_map_id = Column(BigInteger, ForeignKey("booking.seat_maps.id"), nullable=True)
    base_currency = Column(money_currency_enum, default='EUR', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class TripSegment(Base):
    __tablename__ = "trip_segments"
    __table_args__ = (
        UniqueConstraint('trip_id', 'seg_no'),
        {"schema": "booking"}
    )
    
    id = Column(BigInteger, primary_key=True)
    trip_id = Column(BigInteger, ForeignKey("booking.trips.id", ondelete="CASCADE"), nullable=False)
    seg_no = Column(Integer, nullable=False)
    origin_id = Column(BigInteger, ForeignKey("booking.terminals.id"), nullable=False)
    destination_id = Column(BigInteger, ForeignKey("booking.terminals.id"), nullable=False)
    dep_utc = Column(DateTime(timezone=True), nullable=False)
    arr_utc = Column(DateTime(timezone=True), nullable=False)


class Fare(Base):
    __tablename__ = "fares"
    __table_args__ = (
        UniqueConstraint('trip_id', 'fare_code', 'cabin'),
        Index('ix_fares_trip', 'trip_id', 'price_amount'),
        {"schema": "booking"}
    )
    
    id = Column(BigInteger, primary_key=True)
    trip_id = Column(BigInteger, ForeignKey("booking.trips.id", ondelete="CASCADE"), nullable=False)
    fare_code = Column(String, nullable=False)
    cabin = Column(cabin_class_enum, nullable=False)
    price_amount = Column(Numeric(12, 2), nullable=False)
    price_currency = Column(money_currency_enum, nullable=False)
    baggage_allowance = Column(String, nullable=True)
    rules_json = Column(JSONB, nullable=True)
    seats_total = Column(Integer, nullable=True)
    seats_sold = Column(Integer, default=0, nullable=False)


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        Index('ix_bookings_user', 'user_id', 'status', 'created_at'),
        {"schema": "booking"}
    )
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("booking.users.id"), nullable=False)
    status = Column(booking_status_enum, default='TENTATIVE', nullable=False)
    hold_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint('ticket_number'),
        UniqueConstraint('trip_id', 'seat_no', 'issued_at'),
        Index('ix_tickets_trip', 'trip_id', 'status'),
        {"schema": "booking"}
    )
    
    id = Column(BigInteger, primary_key=True)
    booking_id = Column(BigInteger, ForeignKey("booking.bookings.id", ondelete="CASCADE"), nullable=False)
    passenger_id = Column(BigInteger, ForeignKey("booking.passenger_profiles.id"), nullable=False)
    trip_id = Column(BigInteger, ForeignKey("booking.trips.id"), nullable=False)
    fare_id = Column(BigInteger, ForeignKey("booking.fares.id"), nullable=False)
    seat_no = Column(String, nullable=True)
    status = Column(ticket_status_enum, default='ISSUED', nullable=False)
    ticket_number = Column(String, unique=True, nullable=True)
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    __table_args__ = ({"schema": "booking"},)
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("booking.users.id", ondelete="CASCADE"), nullable=False)
    kind = Column(String, nullable=False)
    details_json = Column(JSONB, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        Index('ix_payments_booking', 'booking_id', 'status'),
        {"schema": "booking"}
    )
    
    id = Column(BigInteger, primary_key=True)
    booking_id = Column(BigInteger, ForeignKey("booking.bookings.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(money_currency_enum, nullable=False)
    status = Column(payment_status_enum, default='PENDING', nullable=False)
    provider = Column(String, nullable=True)
    provider_ref = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    captured_at = Column(DateTime(timezone=True), nullable=True)


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint('booking_id'),
        {"schema": "booking"}
    )
    
    id = Column(BigInteger, primary_key=True)
    booking_id = Column(BigInteger, ForeignKey("booking.bookings.id", ondelete="CASCADE"), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(money_currency_enum, nullable=False)
    tax_amount = Column(Numeric(12, 2), default=0, nullable=False)
    details_json = Column(JSONB, nullable=True)
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RefundRequest(Base):
    __tablename__ = "refund_requests"
    __table_args__ = ({"schema": "booking"},)
    
    id = Column(BigInteger, primary_key=True)
    ticket_id = Column(BigInteger, ForeignKey("booking.tickets.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default='PENDING', nullable=False)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)