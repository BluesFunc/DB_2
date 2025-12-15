from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ==================== ENUMS ====================
class TransportMode(str, Enum):
    AIR = "AIR"
    RAIL = "RAIL"
    BUS = "BUS"


class CabinClass(str, Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"


class MoneyCurrency(str, Enum):
    EUR = "EUR"
    USD = "USD"
    BYN = "BYN"


class BookingStatus(str, Enum):
    TENTATIVE = "TENTATIVE"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class TicketStatus(str, Enum):
    ISSUED = "ISSUED"
    VOIDED = "VOIDED"
    REFUNDED = "REFUNDED"
    CHECKED_IN = "CHECKED_IN"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"


# ==================== AUTH SCHEMAS ====================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


# ==================== USER SCHEMAS ====================
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    roles: List[str] = []
    
    class Config:
        from_attributes = True


# ==================== PASSENGER PROFILES ====================
class PassengerProfileBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    birth_date: Optional[date] = None
    doc_type: Optional[str] = None
    doc_number: Optional[str] = None
    citizenship: Optional[str] = None


class PassengerProfileCreate(PassengerProfileBase):
    pass


class PassengerProfileResponse(PassengerProfileBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== PROVIDER SCHEMAS ====================
class ProviderBase(BaseModel):
    name: str
    mode: TransportMode
    iata_code: Optional[str] = None
    inn_external: Optional[str] = None


class ProviderCreate(ProviderBase):
    pass


class ProviderResponse(ProviderBase):
    id: int
    active: bool
    
    class Config:
        from_attributes = True


# ==================== TERMINAL SCHEMAS ====================
class TerminalBase(BaseModel):
    code: str
    name: str
    city: str
    country: str
    timezone: str


class TerminalCreate(TerminalBase):
    pass


class TerminalResponse(TerminalBase):
    id: int
    
    class Config:
        from_attributes = True


# ==================== FARE SCHEMAS ====================
class FareBase(BaseModel):
    fare_code: str
    cabin: CabinClass
    price_amount: Decimal
    price_currency: MoneyCurrency
    baggage_allowance: Optional[str] = None


class FareCreate(FareBase):
    trip_id: int
    seats_total: Optional[int] = None


class FareResponse(FareBase):
    id: int
    trip_id: int
    available_seats: int = 0
    
    class Config:
        from_attributes = True


# ==================== TRIP SCHEMAS ====================
class TripBase(BaseModel):
    code: str
    departure_utc: datetime
    arrival_utc: datetime
    equipment_code: Optional[str] = None


class TripCreate(TripBase):
    provider_id: int
    route_id: int


class TripResponse(TripBase):
    id: int
    provider_id: int
    route_id: int
    base_currency: MoneyCurrency
    is_active: bool
    
    class Config:
        from_attributes = True


class TripSearchRequest(BaseModel):
    origin_id: int
    destination_id: int
    departure_date: date
    transport_mode: Optional[TransportMode] = None


class TripSearchResult(BaseModel):
    trip_id: int
    provider_name: str
    trip_code: str
    departure_utc: datetime
    arrival_utc: datetime
    available_seats: int
    base_currency: str
    fares: List[FareResponse] = []


# ==================== BOOKING SCHEMAS ====================
class BookingCreate(BaseModel):
    hold_expires_at: Optional[datetime] = None


class BookingResponse(BaseModel):
    id: int
    user_id: int
    status: BookingStatus
    hold_expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tickets: List['TicketResponse'] = []
    payments: List['PaymentResponse'] = []
    
    class Config:
        from_attributes = True


# ==================== TICKET SCHEMAS ====================
class TicketCreate(BaseModel):
    passenger_id: int
    trip_id: int
    fare_id: int
    seat_no: Optional[str] = None


class TicketResponse(BaseModel):
    id: int
    booking_id: int
    passenger_id: int
    trip_id: int
    fare_id: int
    seat_no: Optional[str]
    status: TicketStatus
    ticket_number: Optional[str]
    issued_at: datetime
    
    class Config:
        from_attributes = True


# ==================== PAYMENT SCHEMAS ====================
class PaymentCreate(BaseModel):
    amount: Decimal
    currency: MoneyCurrency
    provider: Optional[str] = None
    provider_ref: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    provider: Optional[str]
    provider_ref: Optional[str]
    created_at: datetime
    captured_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== INVOICE SCHEMAS ====================
class InvoiceResponse(BaseModel):
    id: int
    booking_id: int
    total_amount: Decimal
    currency: str
    tax_amount: Decimal
    issued_at: datetime
    
    class Config:
        from_attributes = True