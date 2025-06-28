from sqlalchemy import Column, String, DateTime, Integer, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from backend.database import Base
import uuid


class VehicleType(Base):
    __tablename__ = "vehicle_types"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)  # eg: "14 WHEELER - 30 TON"
    capacity_ton = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    trucks = relationship("Truck", back_populates="vehicle_type")
    bookings = relationship("Booking", back_populates="vehicle_type") 