from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.services.booking_service import BookingService
from backend.schemas import (
    BookingCreate, BookingResponse, BookingUpdate, BookingStatusUpdate,
    BookingWithDetailsResponse, BookingStatusHistoryResponse, TruckAssignmentRequest
)
from backend.core.security import get_current_active_user
from backend.models.user import User, UserRole
from backend.models.booking import BookingStatus

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])

# POST /bookings - Create a new material booking
@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new material booking with automatic truck assignment"""
    service = BookingService(db)
    booking = service.create_booking(current_user.id, booking_data)
    return booking

# GET /bookings - List all bookings
@router.get("/", response_model=List[BookingResponse])
def get_bookings(
    status: Optional[BookingStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all bookings with optional status filtering"""
    service = BookingService(db)
    bookings = service.get_bookings(current_user.id, status)
    return bookings

# GET /bookings/:id - Get booking details + status history
@router.get("/{booking_id}", response_model=BookingWithDetailsResponse)
def get_booking_details(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed booking information with all related data"""
    service = BookingService(db)
    booking = service.get_booking_with_details(booking_id)
    
    # Check if user is authorized to view this booking
    if booking.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    
    return booking

# GET /bookings/:id/status-history - Get booking status history
@router.get("/{booking_id}/status-history", response_model=List[BookingStatusHistoryResponse])
def get_booking_status_history(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get booking status history"""
    service = BookingService(db)
    booking = service.get_booking_details(booking_id)
    
    # Check if user is authorized to view this booking
    if booking.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    
    history = service.get_booking_status_history(booking_id)
    return history

# PATCH /bookings/:id/assign-truck - Auto-assign best truck
@router.patch("/{booking_id}/assign-truck", response_model=BookingResponse)
def assign_truck(
    booking_id: str,
    assignment_data: TruckAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Assign truck to booking (manual or auto-assign)"""
    service = BookingService(db)
    booking = service.assign_truck(booking_id, assignment_data)
    return booking

# PATCH /bookings/:id/status - Update booking state/status
@router.patch("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: str,
    status_update: BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update booking status and state"""
    service = BookingService(db)
    booking = service.update_booking_status(booking_id, status_update)
    return booking

# DELETE /bookings/:id - Cancel booking
@router.delete("/{booking_id}", response_model=BookingResponse)
def cancel_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a booking"""
    service = BookingService(db)
    booking = service.cancel_booking(booking_id, current_user.id)
    return booking 