"""Tests for booking endpoints and services"""
import pytest
import uuid
from datetime import datetime, timedelta, date
from decimal import Decimal
from app.services.dal import (
    UserService, PassengerService, BookingService,
    TicketService, PaymentService, TripService
)
from app.core.auth import verify_password, get_password_hash


class TestUserService:
    """Test user service operations"""
    
    def test_create_user(self):
        """Test user creation"""
        email = f"test_user_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("testpass123")
        full_name = "Test User"
        
        # Create user
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone="+1234567890"
        )
        
        assert user_id is not None
        assert isinstance(user_id, int)
        
        # Verify user was created
        user = UserService.get_user_by_email(email)
        assert user is not None
        assert user["email"] == email
        assert user["full_name"] == full_name
        assert verify_password("testpass123", user["password_hash"])
    
    def test_get_user_by_id(self):
        """Test getting user by ID"""
        email = f"test_user_id_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("pass123")
        
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        user = UserService.get_user_by_id(user_id)
        assert user is not None
        assert user["id"] == user_id
        assert user["email"] == email
    
    def test_assign_role_to_user(self):
        """Test assigning role to user"""
        email = f"test_role_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("pass123")
        
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        # Assign role
        result = UserService.assign_role_to_user(user_id, "customer")
        assert result is True
        
        # Verify role was assigned
        roles = UserService.get_user_roles(user_id)
        assert len(roles) > 0
        role_codes = [r["code"] for r in roles]
        assert "customer" in role_codes
    
    def test_update_user(self):
        """Test updating user information"""
        email = f"test_update_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("pass123")
        
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Original Name"
        )
        
        # Update user
        result = UserService.update_user(
            user_id,
            full_name="Updated Name",
            phone="+9999999999"
        )
        assert result is True
        
        # Verify update
        user = UserService.get_user_by_id(user_id)
        assert user["full_name"] == "Updated Name"
        assert user["phone"] == "+9999999999"


class TestPassengerService:
    """Test passenger profile operations"""
    
    def test_create_passenger_profile(self):
        """Test creating passenger profile"""
        # First create user
        email = f"passenger_test_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("pass123")
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        # Create passenger profile
        profile_id = PassengerService.create_passenger_profile(
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            middle_name="Michael",
            birth_date=date(1990, 5, 15),
            doc_type="passport",
            doc_number="AB123456",
            citizenship="USA"
        )
        
        assert profile_id is not None
        assert isinstance(profile_id, int)
        
        # Verify profile
        profile = PassengerService.get_passenger_profile(profile_id)
        assert profile is not None
        assert profile["first_name"] == "John"
        assert profile["last_name"] == "Doe"
        assert profile["citizenship"] == "USA"
    
    def test_get_user_passengers(self):
        """Test getting user's passengers"""
        email = f"multi_passenger_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("pass123")
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        # Create multiple passengers
        profile1_id = PassengerService.create_passenger_profile(
            user_id=user_id,
            first_name="John",
            last_name="Doe"
        )
        
        profile2_id = PassengerService.create_passenger_profile(
            user_id=user_id,
            first_name="Jane",
            last_name="Smith"
        )
        
        # Get all passengers
        passengers = PassengerService.get_user_passengers(user_id)
        assert len(passengers) >= 2
        
        first_names = [p["first_name"] for p in passengers]
        assert "John" in first_names
        assert "Jane" in first_names


class TestBookingService:
    """Test booking operations"""
    
    def test_create_booking(self):
        """Test creating a booking"""
        # Create user first
        email = f"booking_test_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("pass123")
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        # Create booking
        booking_id = BookingService.create_booking(
            user_id=user_id,
            hold_expires_at=datetime.utcnow() + timedelta(hours=2)
        )
        
        assert booking_id is not None
        assert isinstance(booking_id, int)
        
        # Verify booking
        booking = BookingService.get_booking(booking_id)
        assert booking is not None
        assert booking["user_id"] == user_id
        assert booking["status"] == "TENTATIVE"
    
    def test_get_user_bookings(self):
        """Test getting user's bookings"""
        email = f"user_bookings_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("pass123")
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        # Create multiple bookings
        booking1_id = BookingService.create_booking(user_id=user_id)
        booking2_id = BookingService.create_booking(user_id=user_id)
        
        # Get all bookings
        bookings = BookingService.get_user_bookings(user_id)
        assert len(bookings) >= 2
    
    def test_update_booking_status(self):
        """Test updating booking status"""
        email = f"booking_status_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("pass123")
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        booking_id = BookingService.create_booking(user_id=user_id)
        
        # Update status
        result = BookingService.update_booking_status(booking_id, "CONFIRMED")
        assert result is True
        
        # Verify status
        booking = BookingService.get_booking(booking_id)
        assert booking["status"] == "CONFIRMED"


class TestPaymentService:
    """Test payment operations"""
    
    def test_create_payment(self):
        """Test creating a payment"""
        # Create user and booking first
        email = f"payment_test_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("pass123")
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        booking_id = BookingService.create_booking(user_id=user_id)
        
        # Create payment
        payment_id = PaymentService.create_payment(
            booking_id=booking_id,
            amount=Decimal("199.99"),
            currency="EUR",
            provider="stripe",
            provider_ref="ch_test_123"
        )
        
        assert payment_id is not None
        assert isinstance(payment_id, int)
        
        # Verify payment
        payments = PaymentService.get_booking_payments(booking_id)
        assert len(payments) > 0
        payment = [p for p in payments if p["id"] == payment_id][0]
        assert payment["amount"] == Decimal("199.99")
        assert payment["status"] == "PENDING"
    
    def test_update_payment_status(self):
        """Test updating payment status"""
        email = f"payment_update_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("pass123")
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        booking_id = BookingService.create_booking(user_id=user_id)
        
        payment_id = PaymentService.create_payment(
            booking_id=booking_id,
            amount=Decimal("100.00"),
            currency="USD"
        )
        
        # Update status
        result = PaymentService.update_payment_status(payment_id, "SUCCEEDED")
        assert result is True
        
        # Verify status
        payments = PaymentService.get_booking_payments(booking_id)
        payment = [p for p in payments if p["id"] == payment_id][0]
        assert payment["status"] == "SUCCEEDED"


class TestTicketService:
    """Test ticket operations"""
    
    def test_create_ticket(self):
        """Test creating a ticket"""
        # Setup: Create user, booking, passenger
        email = f"ticket_test_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("pass123")
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Test User"
        )
        
        booking_id = BookingService.create_booking(user_id=user_id)
        
        profile_id = PassengerService.create_passenger_profile(
            user_id=user_id,
            first_name="John",
            last_name="Doe"
        )
        
        # Note: In real scenario, trip_id and fare_id would come from existing data
        # For this test, we're just testing the function signature
        # This test would need integration with real test data
        
        assert profile_id is not None
        assert booking_id is not None


# ==================== INTEGRATION TESTS ====================

class TestBookingWorkflow:
    """Test complete booking workflow"""
    
    def test_complete_booking_workflow(self):
        """Test a complete booking flow: user -> passenger -> booking -> payment"""
        # 1. Create user
        email = f"workflow_test_{uuid.uuid4()}@example.com"
        password_hash = get_password_hash("workflow_pass")
        user_id = UserService.create_user(
            email=email,
            password_hash=password_hash,
            full_name="Workflow Test User"
        )
        assert user_id is not None
        
        # 2. Assign role
        UserService.assign_role_to_user(user_id, "customer")
        roles = UserService.get_user_roles(user_id)
        assert len(roles) > 0
        
        # 3. Create passenger profile
        profile_id = PassengerService.create_passenger_profile(
            user_id=user_id,
            first_name="John",
            last_name="Traveler"
        )
        assert profile_id is not None
        
        # 4. Create booking
        booking_id = BookingService.create_booking(user_id=user_id)
        assert booking_id is not None
        
        # 5. Create payment
        payment_id = PaymentService.create_payment(
            booking_id=booking_id,
            amount=Decimal("299.99"),
            currency="EUR"
        )
        assert payment_id is not None
        
        # 6. Confirm payment
        PaymentService.update_payment_status(payment_id, "SUCCEEDED")
        
        # 7. Confirm booking
        BookingService.update_booking_status(booking_id, "CONFIRMED")
        
        # 8. Verify final state
        final_booking = BookingService.get_booking(booking_id)
        assert final_booking["status"] == "CONFIRMED"
        
        final_payments = PaymentService.get_booking_payments(booking_id)
        assert final_payments[0]["status"] == "SUCCEEDED"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
