from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
import enum
from backend.database import Base
import uuid


class LocationStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "available"
    LIMITED = "limited"
    OUT_OF_STOCK = "out_of_stock"


class MaterialLocation(Base):
    __tablename__ = "material_locations"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    truck_owner_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False, index=True)
    location_name = Column(String(200), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    contact_person = Column(String(100))
    contact_number = Column(String(20))
    operating_hours = Column(String(100))
    rating = Column(DECIMAL(3, 2), default=0)
    status = Column(Enum(LocationStatus), default=LocationStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    truck_owner = relationship(
        "User",
        back_populates="material_locations",
        foreign_keys=[truck_owner_id],
        primaryjoin="MaterialLocation.truck_owner_id == User.id"
    )
    materials = relationship("LocationMaterial", back_populates="location")


class LocationMaterial(Base):
    __tablename__ = "location_materials"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUIDType(binary=False), ForeignKey("material_locations.id"), nullable=False, index=True)
    material_type = Column(String(100), nullable=False)
    price_per_unit = Column(DECIMAL(10, 2))
    unit = Column(String(20))
    availability_status = Column(Enum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    location = relationship("MaterialLocation", back_populates="materials") 