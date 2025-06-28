from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func as sql_func
from backend.core.exceptions import (
    BookingNotFoundException, TruckNotFoundException, TruckNotAvailableException,
    InsufficientCapacityException, BookingNotAllowedException, MaterialNotFoundException,
    VehicleTypeNotFoundException
)
from backend.models.booking import Booking, BookingStatus, BookingState, BookingStatusHistory
from backend.models.truck import Truck, TruckStatus
from backend.models.material import Material, MaterialType
from backend.models.vehicle_type import VehicleType
from backend.models.user import User, UserRole
from backend.schemas.booking import (
    BookingCreate, BookingResponse, BookingUpdate, BookingStatusUpdate,
    BookingWithDetailsResponse, BookingStatusHistoryResponse, TruckAssignmentRequest
)
from backend.utils.distance_calculator import DistanceCalculator


class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def create_booking(self, user_id: str, booking_data: BookingCreate) -> Booking:
        """Create a new material booking with automatic truck assignment"""
        # Validate material exists
        material = self.db.query(Material).filter(Material.id == booking_data.material_id).first()
        if not material:
            raise MaterialNotFoundException(booking_data.material_id)

        # Validate vehicle type exists
        vehicle_type = self.db.query(VehicleType).filter(VehicleType.id == booking_data.vehicle_type_id).first()
        if not vehicle_type:
            raise VehicleTypeNotFoundException(booking_data.vehicle_type_id)

        # Create booking
        booking = Booking(
            user_id=user_id,
            material_id=booking_data.material_id,
            source=booking_data.source,
            destination=booking_data.destination,
            vehicle_type_id=booking_data.vehicle_type_id,
            quantity=booking_data.quantity,
            status=BookingStatus.PENDING,
            state=BookingState.PENDING,
            booking_time=booking_data.booking_time
        )

        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)

        # Auto-assign truck
        self._auto_assign_truck(booking)

        # Add status history
        self._add_status_history(booking.id, BookingStatus.PENDING, "Booking created")

        return booking

    def _auto_assign_truck(self, booking: Booking) -> Optional[Truck]:
        """Auto-assign the best available truck based on criteria"""
        # Find available trucks matching criteria
        available_trucks = self.db.query(Truck).filter(
            and_(
                Truck.is_available == True,
                Truck.vehicle_type_id == booking.vehicle_type_id,
                Truck.status == TruckStatus.AVAILABLE
            )
        ).all()

        if not available_trucks:
            return None

        # Filter by location proximity (source location)
        nearby_trucks = []
        for truck in available_trucks:
            # Simple location matching - can be enhanced with actual distance calculation
            if truck.current_location.lower() in booking.source.lower() or booking.source.lower() in truck.current_location.lower():
                nearby_trucks.append(truck)

        # If no nearby trucks, use all available trucks
        if not nearby_trucks:
            nearby_trucks = available_trucks

        # Select best truck (least used, same owner preference, etc.)
        best_truck = self._select_best_truck(nearby_trucks)

        if best_truck:
            # Assign truck to booking
            booking.assigned_truck_id = best_truck.id
            booking.status = BookingStatus.TRUCK_ASSIGNED
            booking.state = BookingState.ASSIGNED

            # Mark truck as unavailable
            best_truck.is_available = False
            best_truck.status = TruckStatus.BOOKED

            self.db.commit()
            self.db.refresh(booking)

            # Add status history
            self._add_status_history(booking.id, BookingStatus.TRUCK_ASSIGNED, f"Truck {best_truck.vehicle_number} assigned")

        return best_truck

    def _select_best_truck(self, trucks: List[Truck]) -> Optional[Truck]:
        """Select the best truck from available options"""
        if not trucks:
            return None

        # For now, select the first available truck
        # This can be enhanced with more sophisticated selection logic:
        # - Least used truck
        # - Same owner preference
        # - Driver rating
        # - Truck condition
        return trucks[0]

    def _add_status_history(self, booking_id: str, status: str, notes: Optional[str] = None):
        """Add entry to booking status history"""
        history = BookingStatusHistory(
            booking_id=booking_id,
            status=status,
            notes=notes
        )
        self.db.add(history)
        self.db.commit()

    def get_bookings(self, user_id: Optional[str] = None, status: Optional[BookingStatus] = None) -> List[Booking]:
        """Get all bookings with optional filtering"""
        query = self.db.query(Booking)
        
        if user_id:
            query = query.filter(Booking.user_id == user_id)
        
        if status:
            query = query.filter(Booking.status == status)
        
        return query.order_by(Booking.created_at.desc()).all()

    def get_booking_details(self, booking_id: str) -> Booking:
        """Get detailed booking information"""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise BookingNotFoundException(booking_id)
        return booking

    def get_booking_with_details(self, booking_id: str) -> BookingWithDetailsResponse:
        """Get booking with all related details"""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise BookingNotFoundException(booking_id)

        # Get related data
        user = self.db.query(User).filter(User.id == booking.user_id).first()
        material = self.db.query(Material).filter(Material.id == booking.material_id).first()
        vehicle_type = self.db.query(VehicleType).filter(VehicleType.id == booking.vehicle_type_id).first()
        
        truck = None
        if booking.assigned_truck_id:
            truck = self.db.query(Truck).filter(Truck.id == booking.assigned_truck_id).first()

        # Create response with details
        response_data = {
            "id": booking.id,
            "user_id": booking.user_id,
            "user_name": f"{user.first_name} {user.last_name}" if user else "Unknown",
            "material_id": booking.material_id,
            "material_type": material.type.value if material else "Unknown",
            "material_source": material.source if material else "Unknown",
            "source": booking.source,
            "destination": booking.destination,
            "vehicle_type_id": booking.vehicle_type_id,
            "vehicle_type_name": vehicle_type.name if vehicle_type else "Unknown",
            "quantity": booking.quantity,
            "status": booking.status,
            "state": booking.state,
            "assigned_truck_id": booking.assigned_truck_id,
            "assigned_truck_number": truck.vehicle_number if truck else None,
            "driver_name": truck.driver_name if truck else None,
            "driver_contact": truck.driver_contact if truck else None,
            "booking_time": booking.booking_time,
            "expected_delivery_time": booking.expected_delivery_time,
            "actual_delivery_time": booking.actual_delivery_time,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        }

        return BookingWithDetailsResponse(**response_data)

    def assign_truck(self, booking_id: str, assignment_data: TruckAssignmentRequest) -> Booking:
        """Assign truck to booking (manual or auto-assign)"""
        booking = self.get_booking_details(booking_id)
        
        if booking.status != BookingStatus.PENDING:
            raise BookingNotAllowedException("Can only assign truck to pending bookings")

        if assignment_data.truck_id:
            # Manual assignment
            truck = self.db.query(Truck).filter(
                and_(
                    Truck.id == assignment_data.truck_id,
                    Truck.is_available == True,
                    Truck.vehicle_type_id == booking.vehicle_type_id
                )
            ).first()
            
            if not truck:
                raise TruckNotAvailableException(assignment_data.truck_id)
        else:
            # Auto-assignment
            truck = self._auto_assign_truck(booking)
            if not truck:
                raise BookingNotAllowedException("No suitable trucks available for assignment")

        return booking

    def update_booking_status(self, booking_id: str, status_update: BookingStatusUpdate) -> Booking:
        """Update booking status and state"""
        booking = self.get_booking_details(booking_id)
        
        # Update status and state
        booking.status = status_update.status
        if status_update.state:
            booking.state = status_update.state
        
        if status_update.expected_delivery_time:
            booking.expected_delivery_time = status_update.expected_delivery_time
        
        if status_update.actual_delivery_time:
            booking.actual_delivery_time = status_update.actual_delivery_time

        # Handle truck availability based on status
        if status_update.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
            if booking.assigned_truck_id:
                truck = self.db.query(Truck).filter(Truck.id == booking.assigned_truck_id).first()
                if truck:
                    truck.is_available = True
                    truck.status = TruckStatus.AVAILABLE

        self.db.commit()
        self.db.refresh(booking)

        # Add status history
        self._add_status_history(booking_id, status_update.status.value, status_update.notes)

        return booking

    def get_booking_status_history(self, booking_id: str) -> List[BookingStatusHistoryResponse]:
        """Get booking status history"""
        history = self.db.query(BookingStatusHistory).filter(
            BookingStatusHistory.booking_id == booking_id
        ).order_by(BookingStatusHistory.updated_at.desc()).all()
        
        return [BookingStatusHistoryResponse(
            id=str(h.id),
            booking_id=str(h.booking_id),
            status=h.status,
            updated_at=h.updated_at,
            notes=h.notes
        ) for h in history]

    def get_truck_owner_trucks(self, truck_owner_id: str) -> List[Truck]:
        """Get all trucks under a truck owner"""
        return self.db.query(Truck).filter(Truck.truck_owner_id == truck_owner_id).all()

    def cancel_booking(self, booking_id: str, user_id: str) -> Booking:
        """Cancel a booking"""
        booking = self.get_booking_details(booking_id)
        
        if booking.user_id != user_id:
            raise BookingNotAllowedException("Only the booking owner can cancel the booking")
        
        if booking.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
            raise BookingNotAllowedException("Cannot cancel completed or already cancelled booking")

        # Update booking status
        booking.status = BookingStatus.CANCELLED
        booking.state = BookingState.PENDING

        # Free up truck if assigned
        if booking.assigned_truck_id:
            truck = self.db.query(Truck).filter(Truck.id == booking.assigned_truck_id).first()
            if truck:
                truck.is_available = True
                truck.status = TruckStatus.AVAILABLE

        self.db.commit()
        self.db.refresh(booking)

        # Add status history
        self._add_status_history(booking_id, BookingStatus.CANCELLED, "Booking cancelled by user")

        return booking 