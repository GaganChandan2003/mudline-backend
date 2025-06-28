from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.booking import BookingType, BookingStatus


class BookingBase(BaseModel):
    pickup_location: str
    drop_location: str
    material_type: str
    quantity: Decimal
    unit: str
    total_price: Decimal
    special_requirements: Optional[str] = None
    booking_date: datetime

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

    @validator('total_price')
    def validate_total_price(cls, v):
        if v <= 0:
            raise ValueError('Total price must be greater than 0')
        return v


class PreloadedBookingCreate(BaseModel):
    truck_id: str
    pickup_location: str
    drop_location: str
    quantity: Decimal
    special_requirements: Optional[str] = None
    booking_date: datetime

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class LocationBasedBookingCreate(BaseModel):
    location_id: str
    material_type: str
    quantity: Decimal
    unit: str
    drop_location: str
    special_requirements: Optional[str] = None
    booking_date: datetime

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class TraditionalBookingCreate(BaseModel):
    truck_owner_id: str
    pickup_location: str
    drop_location: str
    material_type: str
    quantity: Decimal
    unit: str
    total_price: Decimal
    special_requirements: Optional[str] = None
    booking_date: datetime

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

    @validator('total_price')
    def validate_total_price(cls, v):
        if v <= 0:
            raise ValueError('Total price must be greater than 0')
        return v


class BookingCreate(BookingBase):
    booking_type: BookingType
    truck_owner_id: Optional[str] = None
    truck_id: Optional[str] = None


class BookingUpdate(BaseModel):
    pickup_location: Optional[str] = None
    drop_location: Optional[str] = None
    material_type: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    total_price: Optional[Decimal] = None
    special_requirements: Optional[str] = None
    estimated_delivery: Optional[datetime] = None

    @validator('quantity')
    def validate_quantity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

    @validator('total_price')
    def validate_total_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Total price must be greater than 0')
        return v


class BookingStatusUpdate(BaseModel):
    status: BookingStatus
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None


class BookingResponse(BookingBase):
    id: str
    customer_id: str
    truck_owner_id: str
    truck_id: Optional[str]
    booking_type: BookingType
    status: BookingStatus
    estimated_delivery: Optional[datetime]
    actual_delivery: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingWithDetailsResponse(BookingResponse):
    customer_name: str
    truck_owner_name: str
    truck_number: Optional[str] = None

    class Config:
        from_attributes = True


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