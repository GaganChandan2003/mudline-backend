from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
import enum
from app.database import Base
import uuid


class BookingType(str, enum.Enum):
    PRELOADED = "preloaded"
    LOCATION_BASED = "location_based"
    TRADITIONAL = "traditional"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False, index=True)
    truck_owner_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False, index=True)
    truck_id = Column(UUIDType(binary=False), ForeignKey("trucks.id"), nullable=True, index=True)
    booking_type = Column(Enum(BookingType), nullable=False)
    pickup_location = Column(String(200), nullable=False)
    drop_location = Column(String(200), nullable=False)
    material_type = Column(String(100), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    special_requirements = Column(Text)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    booking_date = Column(DateTime(timezone=True), nullable=False)
    estimated_delivery = Column(DateTime(timezone=True))
    actual_delivery = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id], back_populates="bookings_as_customer")
    truck_owner = relationship("User", foreign_keys=[truck_owner_id], back_populates="bookings_as_owner")
    truck = relationship("Truck", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")
    ratings = relationship("Rating", back_populates="booking") 