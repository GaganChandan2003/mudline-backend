from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.services.booking_service import BookingService
from backend.schemas import (
    BookingCreate, BookingUpdate, BookingResponse, BookingStatusUpdate,
    PreloadedBookingCreate, LocationBasedBookingCreate, TraditionalBookingCreate
)
from backend.core.security import get_current_active_user
from backend.models.user import User, UserRole
from backend.models.booking import BookingStatus

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])

# Create Preloaded Booking
@router.post("/preloaded", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_preloaded_booking(
    booking_data: PreloadedBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = BookingService(db)
    booking = service.create_preloaded_booking(current_user.id, booking_data)
    return booking

# Create Location-Based Booking
@router.post("/location-based", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_location_based_booking(
    booking_data: LocationBasedBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = BookingService(db)
    booking = service.create_location_based_booking(current_user.id, booking_data)
    return booking

# Create Traditional Booking
@router.post("/traditional", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_traditional_booking(
    booking_data: TraditionalBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = BookingService(db)
    booking = service.create_traditional_booking(current_user.id, booking_data)
    return booking

# Get Bookings for Current User
@router.get("/my", response_model=List[BookingResponse])
def get_my_bookings(
    status: Optional[BookingStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = BookingService(db)
    bookings = service.get_user_bookings(current_user.id, current_user.role, status)
    return bookings

# Get Booking Details
@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking_details(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = BookingService(db)
    booking = service.get_booking_details(booking_id)
    # Optionally, check if current_user is authorized to view this booking
    if booking.customer_id != current_user.id and booking.truck_owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    return booking

# Update Booking Status (Truck Owner)
@router.patch("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: str,
    status_update: BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = BookingService(db)
    booking = service.get_booking_details(booking_id)
    if booking.truck_owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the truck owner can update status")
    updated = service.update_booking_status(booking_id, status_update)
    return updated

# Accept Booking (Truck Owner)
@router.post("/{booking_id}/accept", response_model=BookingResponse)
def accept_booking(
    booking_id: str,
    truck_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = BookingService(db)
    booking = service.accept_booking(booking_id, current_user.id, truck_id)
    return booking

# Reject Booking (Truck Owner)
@router.post("/{booking_id}/reject", response_model=BookingResponse)
def reject_booking(
    booking_id: str,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = BookingService(db)
    booking = service.reject_booking(booking_id, current_user.id, reason)
    return booking 