from sqlalchemy import Column, String, DateTime, Enum, Integer, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
import enum
from backend.database import Base
import uuid


class MaterialType(str, enum.Enum):
    SAND = "SAND"
    STONE = "STONE"


class MaterialTypeModel(Base):
    __tablename__ = "material_types"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(MaterialType), nullable=False, unique=True)
    description = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    sources = relationship("MaterialSource", back_populates="material_type")


class MaterialSource(Base):
    __tablename__ = "material_sources"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    material_type_id = Column(UUIDType(binary=False), ForeignKey("material_types.id"), nullable=False, index=True)
    source_name = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    contact_person = Column(String(100))
    contact_number = Column(String(20))
    price_per_unit = Column(DECIMAL(10, 2))
    unit = Column(String(20), default="ton")
    availability_status = Column(String(20), default="available")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    material_type = relationship("MaterialTypeModel", back_populates="sources")
    bookings = relationship("Booking", back_populates="material_source")


class Material(Base):
    __tablename__ = "materials"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    material_source_id = Column(UUIDType(binary=False), ForeignKey("material_sources.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    material_source = relationship("MaterialSource") 