from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
import enum
from backend.database import Base
import uuid


class NotificationType(str, enum.Enum):
    BOOKING = "booking"
    PAYMENT = "payment"
    SYSTEM = "system"
    PROMOTIONAL = "promotional"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")