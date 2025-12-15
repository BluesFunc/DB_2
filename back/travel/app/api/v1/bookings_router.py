"""Booking endpoints"""
from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import List
import json
import logging
from app.schemas.schemas import (
    BookingCreate, BookingResponse, TicketCreate, TicketResponse,
    PaymentCreate, PaymentResponse, TripSearchRequest, TripSearchResult,
    FareResponse, PassengerProfileCreate, PassengerProfileResponse
)
from app.services.dal import (
    BookingService, TicketService, PaymentService, TripService,
    PassengerService
)
from app.core.auth import get_current_active_user
from app.utils.logging_util import log_operation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    request: BookingCreate,
    current_user = Depends(get_current_active_user),
    req: Request = None
):
    """Create a new booking"""
    try:
        booking_id = BookingService.create_booking(
            user_id=current_user.user_id,
            hold_expires_at=request.hold_expires_at
        )
        
        booking = BookingService.get_booking(booking_id)
        
        # Log successful booking creation
        await log_operation(
            user_id=current_user.user_id,
            action="CREATE",
            resource_type="booking",
            resource_id=booking_id,
            method="POST",
            status_code=201,
            details_json=json.dumps({"hold_expires_at": str(request.hold_expires_at)}),
            ip_address=req.client.host if req else None
        )
        
        return BookingResponse(**booking)
    except Exception as e:
        logger.error(f"Create booking error: {str(e)}")
        await log_operation(
            user_id=current_user.user_id,
            action="CREATE",
            resource_type="booking",
            resource_id=None,
            method="POST",
            status_code=500,
            details_json=json.dumps({"error": str(e)}),
            ip_address=req.client.host if req else None
        )
        raise HTTPException(status_code=500, detail="Failed to create booking")


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    current_user = Depends(get_current_active_user),
    req: Request = None
):
    """Get booking details"""
    try:
        booking = BookingService.get_booking(booking_id)
        if not booking:
            await log_operation(
                user_id=current_user.user_id,
                action="READ",
                resource_type="booking",
                resource_id=booking_id,
                method="GET",
                status_code=404,
                details_json=json.dumps({"error": "Booking not found"}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Check ownership
        if booking["user_id"] != current_user.user_id and "admin" not in current_user.roles:
            await log_operation(
                user_id=current_user.user_id,
                action="READ",
                resource_type="booking",
                resource_id=booking_id,
                method="GET",
                status_code=403,
                details_json=json.dumps({"error": "Not authorized"}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this booking"
            )
        
        # Get tickets and payments
        tickets = TicketService.get_booking_tickets(booking_id)
        payments = PaymentService.get_booking_payments(booking_id)
        
        # Log successful read
        await log_operation(
            user_id=current_user.user_id,
            action="READ",
            resource_type="booking",
            resource_id=booking_id,
            method="GET",
            status_code=200,
            details_json=json.dumps({"tickets_count": len(tickets), "payments_count": len(payments)}),
            ip_address=req.client.host if req else None
        )
        
        return BookingResponse(
            **booking,
            tickets=[TicketResponse(**t) for t in tickets],
            payments=[PaymentResponse(**p) for p in payments]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get booking error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=List[BookingResponse])
async def list_user_bookings(
    current_user = Depends(get_current_active_user),
    status: str = None,
    req: Request = None
):
    """List user's bookings"""
    try:
        bookings = BookingService.get_user_bookings(current_user.user_id, status)
        
        # Log successful list
        await log_operation(
            user_id=current_user.user_id,
            action="READ",
            resource_type="booking",
            resource_id=None,
            method="GET",
            status_code=200,
            details_json=json.dumps({"filter_status": status, "count": len(bookings)}),
            ip_address=req.client.host if req else None
        )
        
        return [BookingResponse(**b) for b in bookings]
    except Exception as e:
        logger.error(f"List bookings error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{booking_id}/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def add_ticket_to_booking(
    booking_id: int,
    request: TicketCreate,
    current_user = Depends(get_current_active_user),
    req: Request = None
):
    """Add a ticket to booking"""
    try:
        # Verify booking ownership
        booking = BookingService.get_booking(booking_id)
        if not booking:
            await log_operation(
                user_id=current_user.user_id,
                action="CREATE",
                resource_type="ticket",
                resource_id=None,
                method="POST",
                status_code=404,
                details_json=json.dumps({"error": "Booking not found"}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        if booking["user_id"] != current_user.user_id and "admin" not in current_user.roles:
            await log_operation(
                user_id=current_user.user_id,
                action="CREATE",
                resource_type="ticket",
                resource_id=None,
                method="POST",
                status_code=403,
                details_json=json.dumps({"error": "Not authorized"}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        # Create ticket
        ticket_id = TicketService.create_ticket(
            booking_id=booking_id,
            passenger_id=request.passenger_id,
            trip_id=request.trip_id,
            fare_id=request.fare_id,
            seat_no=request.seat_no
        )
        
        ticket = TicketService.get_booking_tickets(booking_id)[0]
        
        # Log ticket creation
        await log_operation(
            user_id=current_user.user_id,
            action="CREATE",
            resource_type="ticket",
            resource_id=ticket_id,
            method="POST",
            status_code=201,
            details_json=json.dumps({"booking_id": booking_id, "seat_no": request.seat_no}),
            ip_address=req.client.host if req else None
        )
        
        return TicketResponse(**ticket)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add ticket error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create ticket")


@router.post("/{booking_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    booking_id: int,
    request: PaymentCreate,
    current_user = Depends(get_current_active_user),
    req: Request = None
):
    """Create payment for booking"""
    try:
        booking = BookingService.get_booking(booking_id)
        if not booking:
            await log_operation(
                user_id=current_user.user_id,
                action="CREATE",
                resource_type="payment",
                resource_id=None,
                method="POST",
                status_code=404,
                details_json=json.dumps({"error": "Booking not found"}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        if booking["user_id"] != current_user.user_id and "admin" not in current_user.roles:
            await log_operation(
                user_id=current_user.user_id,
                action="CREATE",
                resource_type="payment",
                resource_id=None,
                method="POST",
                status_code=403,
                details_json=json.dumps({"error": "Not authorized"}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        # Create payment
        payment_id = PaymentService.create_payment(
            booking_id=booking_id,
            amount=request.amount,
            currency=request.currency.value,
            provider=request.provider,
            provider_ref=request.provider_ref
        )
        
        payments = PaymentService.get_booking_payments(booking_id)
        payment = [p for p in payments if p["id"] == payment_id][0]
        
        # Log payment creation
        await log_operation(
            user_id=current_user.user_id,
            action="CREATE",
            resource_type="payment",
            resource_id=payment_id,
            method="POST",
            status_code=201,
            details_json=json.dumps({"booking_id": booking_id, "amount": float(request.amount), "currency": request.currency.value}),
            ip_address=req.client.host if req else None
        )
        
        return PaymentResponse(**payment)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create payment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create payment")


@router.put("/{booking_id}/payments/{payment_id}/confirm")
async def confirm_payment(
    booking_id: int,
    payment_id: int,
    current_user = Depends(get_current_active_user),
    req: Request = None
):
    """Confirm payment (mark as SUCCEEDED)"""
    try:
        booking = BookingService.get_booking(booking_id)
        if not booking:
            await log_operation(
                user_id=current_user.user_id,
                action="UPDATE",
                resource_type="payment",
                resource_id=payment_id,
                method="PUT",
                status_code=404,
                details_json=json.dumps({"error": "Booking not found"}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        if booking["user_id"] != current_user.user_id and "admin" not in current_user.roles:
            await log_operation(
                user_id=current_user.user_id,
                action="UPDATE",
                resource_type="payment",
                resource_id=payment_id,
                method="PUT",
                status_code=403,
                details_json=json.dumps({"error": "Not authorized"}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        # Update payment status
        success = PaymentService.update_payment_status(payment_id, "SUCCEEDED")
        
        if success:
            # Update booking status to CONFIRMED
            BookingService.update_booking_status(booking_id, "CONFIRMED")
            
            # Log payment confirmation
            await log_operation(
                user_id=current_user.user_id,
                action="UPDATE",
                resource_type="payment",
                resource_id=payment_id,
                method="PUT",
                status_code=200,
                details_json=json.dumps({"booking_id": booking_id, "new_status": "CONFIRMED"}),
                ip_address=req.client.host if req else None
            )
            
            return {"message": "Payment confirmed and booking confirmed"}
        else:
            await log_operation(
                user_id=current_user.user_id,
                action="UPDATE",
                resource_type="payment",
                resource_id=payment_id,
                method="PUT",
                status_code=400,
                details_json=json.dumps({"error": "Failed to confirm payment"}),
                ip_address=req.client.host if req else None
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to confirm payment"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Confirm payment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== PASSENGER PROFILES ====================

@router.post("/passengers", response_model=PassengerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_passenger_profile(
    request: PassengerProfileCreate,
    current_user = Depends(get_current_active_user),
    req: Request = None
):
    """Create passenger profile"""
    try:
        profile_id = PassengerService.create_passenger_profile(
            user_id=current_user.user_id,
            first_name=request.first_name,
            last_name=request.last_name,
            middle_name=request.middle_name,
            birth_date=request.birth_date,
            doc_type=request.doc_type,
            doc_number=request.doc_number,
            citizenship=request.citizenship
        )
        
        profile = PassengerService.get_passenger_profile(profile_id)
        
        # Log passenger profile creation
        await log_operation(
            user_id=current_user.user_id,
            action="CREATE",
            resource_type="passenger",
            resource_id=profile_id,
            method="POST",
            status_code=201,
            details_json=json.dumps({"first_name": request.first_name, "last_name": request.last_name}),
            ip_address=req.client.host if req else None
        )
        
        return PassengerProfileResponse(**profile)
    except Exception as e:
        logger.error(f"Create passenger profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create passenger profile")


@router.get("/passengers", response_model=List[PassengerProfileResponse])
async def list_passenger_profiles(
    current_user = Depends(get_current_active_user)
):
    """List user's passenger profiles"""
    profiles = PassengerService.get_user_passengers(current_user.user_id)
    return [PassengerProfileResponse(**p) for p in profiles]


# ==================== TRIP SEARCH ====================

@router.post("/search", response_model=List[TripSearchResult])
async def search_trips(request: TripSearchRequest):
    """Search available trips"""
    trips = TripService.search_trips(
        origin_id=request.origin_id,
        destination_id=request.destination_id,
        departure_date=request.departure_date,
        transport_mode=request.transport_mode.value if request.transport_mode else None
    )
    
    # Fetch fares for each trip
    results = []
    for trip in trips:
        fares = TripService.get_trip_fares(trip["trip_id"])
        results.append(TripSearchResult(
            **trip,
            fares=[FareResponse(**f) for f in fares]
        ))
    
    return results
