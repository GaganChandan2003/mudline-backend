from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
import enum
from app.database import Base
import uuid


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUIDType(binary=False), ForeignKey("bookings.id"), nullable=False, index=True)
    reviewer_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False, index=True)
    reviewee_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    booking = relationship("Booking", back_populates="ratings")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="ratings_given")
    reviewee = relationship("User", foreign_keys=[reviewee_id], back_populates="ratings_received") 