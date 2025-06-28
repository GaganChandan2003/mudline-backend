from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from backend.core.exceptions import (
    BookingNotFoundException, TruckNotFoundException, TruckNotAvailableException,
    InsufficientCapacityException, BookingNotAllowedException, LocationNotFoundException
)
from backend.models.booking import Booking, BookingType, BookingStatus
from backend.models.truck import Truck, TruckStatus, PreloadedMaterial, PreloadedMaterialStatus
from backend.models.location import MaterialLocation, LocationMaterial, AvailabilityStatus
from backend.models.user import User, UserRole
from backend.schemas.booking import (
    BookingCreate, BookingResponse, BookingUpdate, BookingStatusUpdate, PreloadedBookingCreate,
    LocationBasedBookingCreate, TraditionalBookingCreate, NearbyTruckSearch
)
from backend.utils.distance_calculator import DistanceCalculator


class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def create_preloaded_booking(self, customer_id: str, booking_data: PreloadedBookingCreate) -> Booking:
        """Create a booking for a pre-loaded truck"""
        # Get the truck and verify it's available
        truck = self.db.query(Truck).filter(Truck.id == booking_data.truck_id).first()
        if not truck:
            raise TruckNotFoundException(booking_data.truck_id)

        if truck.status != TruckStatus.AVAILABLE:
            raise TruckNotAvailableException(booking_data.truck_id)

        if not truck.is_preloaded:
            raise BookingNotAllowedException("Truck is not pre-loaded")

        # Get preloaded material
        material = self.db.query(PreloadedMaterial).filter(
            and_(
                PreloadedMaterial.truck_id == booking_data.truck_id,
                PreloadedMaterial.status == PreloadedMaterialStatus.AVAILABLE
            )
        ).first()

        if not material:
            raise BookingNotAllowedException("No available pre-loaded material found")

        # Check capacity
        if booking_data.quantity > material.quantity:
            raise InsufficientCapacityException(float(material.quantity), float(booking_data.quantity))

        # Create booking
        booking = Booking(
            customer_id=customer_id,
            truck_owner_id=truck.truck_owner_id,
            truck_id=truck.id,
            booking_type=BookingType.PRELOADED,
            pickup_location=material.destination or truck.current_location,
            drop_location=booking_data.drop_location,
            material_type=material.material_type,
            quantity=booking_data.quantity,
            unit=material.unit,
            total_price=material.price * (booking_data.quantity / material.quantity),
            special_requirements=booking_data.special_requirements,
            booking_date=booking_data.booking_date,
            status=BookingStatus.ACCEPTED  # Pre-loaded bookings are auto-accepted
        )

        # Update truck and material status
        truck.status = TruckStatus.BOOKED
        material.status = PreloadedMaterialStatus.BOOKED

        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def create_location_based_booking(self, customer_id: str, booking_data: LocationBasedBookingCreate) -> Booking:
        """Create a booking based on material location"""
        # Get the location and verify it's active
        location = self.db.query(MaterialLocation).filter(
            and_(
                MaterialLocation.id == booking_data.location_id,
                MaterialLocation.status == "active"
            )
        ).first()

        if not location:
            raise LocationNotFoundException(booking_data.location_id)

        # Get material availability
        material = self.db.query(LocationMaterial).filter(
            and_(
                LocationMaterial.location_id == booking_data.location_id,
                LocationMaterial.material_type == booking_data.material_type,
                LocationMaterial.availability_status == AvailabilityStatus.AVAILABLE
            )
        ).first()

        if not material:
            raise BookingNotAllowedException(f"Material {booking_data.material_type} not available at this location")

        # Find nearby available trucks
        nearby_trucks = self.get_nearby_trucks(
            latitude=location.latitude,
            longitude=location.longitude,
            radius_km=50
        )

        if not nearby_trucks:
            raise BookingNotAllowedException("No available trucks found near the location")

        # Create booking (will be assigned to the first available truck owner)
        booking = Booking(
            customer_id=customer_id,
            truck_owner_id=nearby_trucks[0].truck_owner_id,
            booking_type=BookingType.LOCATION_BASED,
            pickup_location=location.address,
            drop_location=booking_data.drop_location,
            material_type=booking_data.material_type,
            quantity=booking_data.quantity,
            unit=booking_data.unit,
            total_price=material.price_per_unit * booking_data.quantity if material.price_per_unit else 0,
            special_requirements=booking_data.special_requirements,
            booking_date=booking_data.booking_date,
            status=BookingStatus.PENDING
        )

        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def create_traditional_booking(self, customer_id: str, booking_data: TraditionalBookingCreate) -> Booking:
        """Create a traditional booking request"""
        # Verify truck owner exists and is a truck owner
        truck_owner = self.db.query(User).filter(
            and_(
                User.id == booking_data.truck_owner_id,
                User.role == UserRole.TRUCK_OWNER
            )
        ).first()

        if not truck_owner:
            raise BookingNotAllowedException("Invalid truck owner")

        # Create booking
        booking = Booking(
            customer_id=customer_id,
            truck_owner_id=booking_data.truck_owner_id,
            booking_type=BookingType.TRADITIONAL,
            pickup_location=booking_data.pickup_location,
            drop_location=booking_data.drop_location,
            material_type=booking_data.material_type,
            quantity=booking_data.quantity,
            unit=booking_data.unit,
            total_price=booking_data.total_price,
            special_requirements=booking_data.special_requirements,
            booking_date=booking_data.booking_date,
            status=BookingStatus.PENDING
        )

        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def get_nearby_trucks(self, latitude: Decimal, longitude: Decimal, radius_km: float = 50) -> List[Truck]:
        """Find trucks within specified radius"""
        trucks = self.db.query(Truck).filter(
            and_(
                Truck.status == TruckStatus.AVAILABLE,
                Truck.latitude.isnot(None),
                Truck.longitude.isnot(None)
            )
        ).all()

        # Filter trucks by distance
        nearby_trucks = []
        for truck in trucks:
            distance = DistanceCalculator.haversine_distance(
                float(latitude), float(longitude),
                float(truck.latitude), float(truck.longitude)
            )
            if distance <= radius_km:
                truck.distance = distance
                nearby_trucks.append(truck)

        # Sort by distance
        return sorted(nearby_trucks, key=lambda x: x.distance)

    def accept_booking(self, booking_id: str, truck_owner_id: str, truck_id: Optional[str] = None) -> Booking:
        """Accept a booking request"""
        booking = self.db.query(Booking).filter(
            and_(
                Booking.id == booking_id,
                Booking.truck_owner_id == truck_owner_id,
                Booking.status == BookingStatus.PENDING
            )
        ).first()

        if not booking:
            raise BookingNotFoundException(booking_id)

        # If truck_id is provided, verify it belongs to the truck owner
        if truck_id:
            truck = self.db.query(Truck).filter(
                and_(
                    Truck.id == truck_id,
                    Truck.truck_owner_id == truck_owner_id,
                    Truck.status == TruckStatus.AVAILABLE
                )
            ).first()

            if not truck:
                raise TruckNotFoundException(truck_id)

            booking.truck_id = truck_id
            truck.status = TruckStatus.BOOKED

        booking.status = BookingStatus.ACCEPTED
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def reject_booking(self, booking_id: str, truck_owner_id: str, reason: str = None) -> Booking:
        """Reject a booking request"""
        booking = self.db.query(Booking).filter(
            and_(
                Booking.id == booking_id,
                Booking.truck_owner_id == truck_owner_id,
                Booking.status == BookingStatus.PENDING
            )
        ).first()

        if not booking:
            raise BookingNotFoundException(booking_id)

        booking.status = BookingStatus.REJECTED
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def update_booking_status(self, booking_id: str, status_update: BookingStatusUpdate) -> Booking:
        """Update booking status"""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise BookingNotFoundException(booking_id)

        booking.status = status_update.status
        if status_update.estimated_delivery:
            booking.estimated_delivery = status_update.estimated_delivery
        if status_update.actual_delivery:
            booking.actual_delivery = status_update.actual_delivery

        # If completed, update truck status
        if status_update.status == BookingStatus.COMPLETED and booking.truck_id:
            truck = self.db.query(Truck).filter(Truck.id == booking.truck_id).first()
            if truck:
                truck.status = TruckStatus.AVAILABLE

        self.db.commit()
        self.db.refresh(booking)
        return booking

    def get_user_bookings(self, user_id: str, role: UserRole, status: Optional[BookingStatus] = None) -> List[Booking]:
        """Get bookings for a user based on their role"""
        query = self.db.query(Booking)

        if role == UserRole.CUSTOMER:
            query = query.filter(Booking.customer_id == user_id)
        else:
            query = query.filter(Booking.truck_owner_id == user_id)

        if status:
            query = query.filter(Booking.status == status)

        return query.order_by(Booking.created_at.desc()).all()

    def get_booking_details(self, booking_id: str) -> Booking:
        """Get detailed booking information"""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise BookingNotFoundException(booking_id)
        return booking 