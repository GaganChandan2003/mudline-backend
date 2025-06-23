from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
import enum
from app.database import Base
import uuid


class TruckStatus(str, enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    IN_TRANSIT = "in_transit"
    MAINTENANCE = "maintenance"


class PreloadedMaterialStatus(str, enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"


class Truck(Base):
    __tablename__ = "trucks"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    truck_owner_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False, index=True)
    truck_number = Column(String(20), unique=True, nullable=False, index=True)
    truck_type = Column(String(100), nullable=False)
    capacity = Column(DECIMAL(10, 2), nullable=False)
    current_location = Column(String(200))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    driver_name = Column(String(100))
    driver_contact = Column(String(20))
    driver_license = Column(String(50))
    is_preloaded = Column(Boolean, default=False)
    status = Column(Enum(TruckStatus), default=TruckStatus.AVAILABLE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    truck_owner = relationship("User", back_populates="trucks")
    preloaded_materials = relationship("PreloadedMaterial", back_populates="truck")
    bookings = relationship("Booking", back_populates="truck")



class PreloadedMaterial(Base):
    __tablename__ = "preloaded_materials"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    truck_id = Column(UUIDType(binary=False), ForeignKey("trucks.id"), nullable=False, index=True)
    material_type = Column(String(100), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    destination = Column(String(200))
    price = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text)
    status = Column(Enum(PreloadedMaterialStatus), default=PreloadedMaterialStatus.AVAILABLE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    truck = relationship("Truck", back_populates="preloaded_materials") 