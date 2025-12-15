"""Data Access Layer (DAL) - Service layer for database operations using stored procedures"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import text
from app.core.database import engine


class UserService:
    """User-related database operations"""
    
    @staticmethod
    def create_user(email: str, password_hash: str, full_name: str, phone: Optional[str] = None) -> int:
        """Create a new user"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM booking.create_user(:email, :password_hash, :full_name, :phone)"),
                {"email": email, "password_hash": password_hash, "full_name": full_name, "phone": phone}
            )
            conn.commit()
            return result.scalar()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM booking.get_user_by_email(:email)"),
                {"email": email}
            )
            row = result.first()
            if row:
                return dict(row._mapping)
            return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM booking.get_user_by_id(:user_id)"),
                {"user_id": user_id}
            )
            row = result.first()
            if row:
                return dict(row._mapping)
            return None
    
    @staticmethod
    def get_user_roles(user_id: int) -> List[Dict[str, Any]]:
        """Get user roles"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM booking.get_user_roles(:user_id)"),
                {"user_id": user_id}
            )
            return [dict(row._mapping) for row in result.fetchall()]
    
    @staticmethod
    def assign_role_to_user(user_id: int, role_code: str) -> bool:
        """Assign role to user"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT booking.assign_role_to_user(:user_id, :role_code)"),
                {"user_id": user_id, "role_code": role_code}
            )
            conn.commit()
            return result.scalar()
    
    @staticmethod
    def update_user(user_id: int, full_name: Optional[str] = None, phone: Optional[str] = None, 
                   is_active: Optional[bool] = None) -> bool:
        """Update user information"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT booking.update_user(:user_id, :full_name, :phone, :is_active)"),
                {"user_id": user_id, "full_name": full_name, "phone": phone, "is_active": is_active}
            )
            conn.commit()
            return result.scalar()


class PassengerService:
    """Passenger profile operations"""
    
    @staticmethod
    def create_passenger_profile(user_id: int, first_name: str, last_name: str, 
                                middle_name: Optional[str] = None, birth_date: Optional[date] = None,
                                doc_type: Optional[str] = None, doc_number: Optional[str] = None,
                                citizenship: Optional[str] = None) -> int:
        """Create passenger profile"""
        with engine.connect() as conn:
            result = conn.execute(
                text("""SELECT booking.create_passenger_profile(
                    :user_id, :first_name, :last_name, :middle_name, :birth_date, 
                    :doc_type, :doc_number, :citizenship
                )"""),
                {
                    "user_id": user_id, "first_name": first_name, "last_name": last_name,
                    "middle_name": middle_name, "birth_date": birth_date, "doc_type": doc_type,
                    "doc_number": doc_number, "citizenship": citizenship
                }
            )
            conn.commit()
            return result.scalar()
    
    @staticmethod
    def get_passenger_profile(profile_id: int) -> Optional[Dict[str, Any]]:
        """Get passenger profile"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM booking.get_passenger_profile(:profile_id)"),
                {"profile_id": profile_id}
            )
            row = result.first()
            if row:
                return dict(row._mapping)
            return None
    
    @staticmethod
    def get_user_passengers(user_id: int) -> List[Dict[str, Any]]:
        """Get all passenger profiles for a user"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM booking.get_user_passengers(:user_id)"),
                {"user_id": user_id}
            )
            return [dict(row._mapping) for row in result.fetchall()]


class BookingService:
    """Booking operations"""
    
    @staticmethod
    def create_booking(user_id: int, hold_expires_at: Optional[datetime] = None) -> int:
        """Create a new booking"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT booking.create_booking(:user_id, :hold_expires_at)"),
                {"user_id": user_id, "hold_expires_at": hold_expires_at}
            )
            conn.commit()
            return result.scalar()
    
    @staticmethod
    def get_booking(booking_id: int) -> Optional[Dict[str, Any]]:
        """Get booking details"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM booking.get_booking(:booking_id)"),
                {"booking_id": booking_id}
            )
            row = result.first()
            if row:
                return dict(row._mapping)
            return None
    
    @staticmethod
    def get_user_bookings(user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all bookings for a user"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM booking.get_user_bookings(:user_id, :status)"),
                {"user_id": user_id, "status": status}
            )
            return [dict(row._mapping) for row in result.fetchall()]
    
    @staticmethod
    def update_booking_status(booking_id: int, status: str) -> bool:
        """Update booking status"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT booking.update_booking_status(:booking_id, :status)"),
                {"booking_id": booking_id, "status": status}
            )
            conn.commit()
            return result.scalar()


class TicketService:
    """Ticket operations"""
    
    @staticmethod
    def create_ticket(booking_id: int, passenger_id: int, trip_id: int, fare_id: int,
                     seat_no: Optional[str] = None, ticket_number: Optional[str] = None) -> int:
        """Create a ticket"""
        with engine.connect() as conn:
            result = conn.execute(
                text("""SELECT booking.create_ticket(
                    :booking_id, :passenger_id, :trip_id, :fare_id, :seat_no, :ticket_number
                )"""),
                {
                    "booking_id": booking_id, "passenger_id": passenger_id, "trip_id": trip_id,
                    "fare_id": fare_id, "seat_no": seat_no, "ticket_number": ticket_number
                }
            )
            conn.commit()
            return result.scalar()
    
    @staticmethod
    def get_booking_tickets(booking_id: int) -> List[Dict[str, Any]]:
        """Get all tickets in a booking"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM booking.get_booking_tickets(:booking_id)"),
                {"booking_id": booking_id}
            )
            return [dict(row._mapping) for row in result.fetchall()]
    
    @staticmethod
    def update_ticket_status(ticket_id: int, status: str) -> bool:
        """Update ticket status"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT booking.update_ticket_status(:ticket_id, :status)"),
                {"ticket_id": ticket_id, "status": status}
            )
            conn.commit()
            return result.scalar()


class PaymentService:
    """Payment operations"""
    
    @staticmethod
    def create_payment(booking_id: int, amount: Decimal, currency: str,
                      provider: Optional[str] = None, provider_ref: Optional[str] = None) -> int:
        """Create a payment record"""
        with engine.connect() as conn:
            result = conn.execute(
                text("""SELECT booking.create_payment(
                    :booking_id, :amount, :currency, :provider, :provider_ref
                )"""),
                {
                    "booking_id": booking_id, "amount": amount, "currency": currency,
                    "provider": provider, "provider_ref": provider_ref
                }
            )
            conn.commit()
            return result.scalar()
    
    @staticmethod
    def get_booking_payments(booking_id: int) -> List[Dict[str, Any]]:
        """Get all payments for a booking"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM booking.get_booking_payments(:booking_id)"),
                {"booking_id": booking_id}
            )
            return [dict(row._mapping) for row in result.fetchall()]
    
    @staticmethod
    def update_payment_status(payment_id: int, status: str) -> bool:
        """Update payment status"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT booking.update_payment_status(:payment_id, :status)"),
                {"payment_id": payment_id, "status": status}
            )
            conn.commit()
            return result.scalar()


class TripService:
    """Trip and fare search operations"""
    
    @staticmethod
    def search_trips(origin_id: int, destination_id: int, departure_date: date,
                    transport_mode: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search available trips"""
        with engine.connect() as conn:
            result = conn.execute(
                text("""SELECT * FROM booking.search_trips(
                    :origin_id, :destination_id, :departure_date, :transport_mode
                )"""),
                {
                    "origin_id": origin_id, "destination_id": destination_id,
                    "departure_date": departure_date, "transport_mode": transport_mode
                }
            )
            return [dict(row._mapping) for row in result.fetchall()]
    
    @staticmethod
    def get_trip_fares(trip_id: int) -> List[Dict[str, Any]]:
        """Get all fares for a trip"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM booking.get_trip_fares(:trip_id)"),
                {"trip_id": trip_id}
            )
            return [dict(row._mapping) for row in result.fetchall()]
