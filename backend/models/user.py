import uuid
from sqlalchemy import Column, String, Boolean, Enum, DateTime, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base
from backend.models.user_role import UserRole  # Make sure this Enum exists
from .profile import TruckOwnerProfile, CustomerProfile

class User(Base):
    __tablename__ = "users"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, native_enum=False, length=20), nullable=False, index=True)
    profile_image_url = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False, server_default='0')
    is_active = Column(Boolean, default=True, server_default='1')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    truck_owner_profile = relationship("TruckOwnerProfile", back_populates="user", uselist=False)
    customer_profile = relationship("CustomerProfile", back_populates="user", uselist=False)
    trucks = relationship("Truck", back_populates="truck_owner")
    material_locations = relationship("MaterialLocation", back_populates="truck_owner")
    bookings_as_customer = relationship(
        "Booking",
        foreign_keys="Booking.user_id",
        back_populates="user"
    )
    ratings_given = relationship(
        "Rating",
        foreign_keys="Rating.reviewer_id",
        back_populates="reviewer"
    )
    ratings_received = relationship(
        "Rating",
        foreign_keys="Rating.reviewee_id",
        back_populates="reviewee"
    )
    notifications = relationship(
        "Notification",
        back_populates="user"
    )
