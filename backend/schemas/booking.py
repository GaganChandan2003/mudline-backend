from pydantic import BaseModel, validator, field_serializer
from typing import Optional
from datetime import datetime
from decimal import Decimal
from backend.models.booking import BookingStatus, BookingState


class BookingBase(BaseModel):
    material_source_id: str
    destination: str
    vehicle_type_id: str
    quantity: Decimal
    booking_time: datetime

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    destination: Optional[str] = None
    vehicle_type_id: Optional[str] = None
    quantity: Optional[Decimal] = None
    expected_delivery_time: Optional[datetime] = None

    @validator('quantity')
    def validate_quantity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class BookingStatusUpdate(BaseModel):
    status: BookingStatus
    state: Optional[BookingState] = None
    expected_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    notes: Optional[str] = None


class BookingResponse(BookingBase):
    id: str
    user_id: str
    status: BookingStatus
    state: BookingState
    assigned_truck_id: Optional[str]
    expected_delivery_time: Optional[datetime]
    actual_delivery_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @field_serializer("id")
    def serialize_id(self, v):
        return str(v)

    @field_serializer("user_id")
    def serialize_user_id(self, v):
        return str(v)

    @field_serializer("material_source_id")
    def serialize_material_source_id(self, v):
        return str(v)

    @field_serializer("vehicle_type_id")
    def serialize_vehicle_type_id(self, v):
        return str(v)

    @field_serializer("assigned_truck_id")
    def serialize_assigned_truck_id(self, v):
        return str(v) if v else None

    class Config:
        from_attributes = True


class BookingWithDetailsResponse(BookingResponse):
    user_name: str
    material_type: str
    material_source: str
    vehicle_type_name: str
    assigned_truck_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None

    class Config:
        from_attributes = True


class BookingStatusHistoryResponse(BaseModel):
    id: str
    booking_id: str
    status: str
    updated_at: datetime
    notes: Optional[str] = None

    @field_serializer("id")
    def serialize_id(self, v):
        return str(v)

    @field_serializer("booking_id")
    def serialize_booking_id(self, v):
        return str(v)

    class Config:
        from_attributes = True


class TruckAssignmentRequest(BaseModel):
    truck_id: Optional[str] = None  # If not provided, auto-assign best truck


class NearbyTruckSearch(BaseModel):
    latitude: Decimal
    longitude: Decimal
    radius_km: float = 50
    material_type: Optional[str] = None
    capacity_min: Optional[Decimal] = None
    capacity_max: Optional[Decimal] = None

    @validator('latitude')
    def validate_latitude(cls, v):
        if v < -90 or v > 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if v < -180 or v > 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v

    @validator('radius_km')
    def validate_radius(cls, v):
        if v <= 0 or v > 500:
            raise ValueError('Radius must be between 0 and 500 km')
        return v 