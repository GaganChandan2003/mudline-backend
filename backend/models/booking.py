from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
import enum
from backend.database import Base
import uuid


class BookingType(str, enum.Enum):
    PRELOADED = "preloaded"
    LOCATION_BASED = "location_based"
    TRADITIONAL = "traditional"


class BookingStatus(str, enum.Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    TRUCK_ASSIGNED = "Truck Assigned"
    LOADING = "Loading"
    IN_TRANSIT = "In Transit"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class BookingState(str, enum.Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    ASSIGNED = "Assigned"
    LOADING = "Loading"
    TRANSIT = "Transit"
    DELIVERED = "Delivered"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False, index=True)
    material_source_id = Column(UUIDType(binary=False), ForeignKey("material_sources.id"), nullable=False, index=True)
    destination = Column(String(200), nullable=False)
    vehicle_type_id = Column(UUIDType(binary=False), ForeignKey("vehicle_types.id"), nullable=False, index=True)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    assigned_truck_id = Column(UUIDType(binary=False), ForeignKey("trucks.id"), nullable=True, index=True)
    booking_time = Column(DateTime(timezone=True), nullable=False)
    expected_delivery_time = Column(DateTime(timezone=True))
    actual_delivery_time = Column(DateTime(timezone=True))
    state = Column(Enum(BookingState), default=BookingState.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="bookings_as_customer")
    material_source = relationship("MaterialSource", back_populates="bookings")
    vehicle_type = relationship("VehicleType", back_populates="bookings")
    assigned_truck = relationship("Truck", foreign_keys=[assigned_truck_id], back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")
    ratings = relationship("Rating", back_populates="booking")


class BookingStatusHistory(Base):
    __tablename__ = "booking_status_history"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUIDType(binary=False), ForeignKey("bookings.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)

    booking = relationship("Booking", backref="status_history") 