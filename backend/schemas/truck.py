from pydantic import BaseModel, validator, field_serializer
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from backend.models.truck import TruckStatus, PreloadedMaterialStatus


class TruckBase(BaseModel):
    truck_number: str
    truck_type: str
    capacity: Decimal
    current_location: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None
    driver_license: Optional[str] = None
    is_preloaded: bool = False

    @validator('capacity')
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError('Capacity must be greater than 0')
        return v

    @validator('latitude')
    def validate_latitude(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError('Longitude must be between -180 and 180')
        return v


class TruckCreate(TruckBase):
    pass


class TruckUpdate(BaseModel):
    truck_type: Optional[str] = None
    capacity: Optional[Decimal] = None
    current_location: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None
    driver_license: Optional[str] = None
    is_preloaded: Optional[bool] = None
    status: Optional[TruckStatus] = None

    @validator('capacity')
    def validate_capacity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Capacity must be greater than 0')
        return v

    @validator('latitude')
    def validate_latitude(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError('Longitude must be between -180 and 180')
        return v


class TruckResponse(TruckBase):
    id: str
    truck_owner_id: str
    status: TruckStatus
    created_at: datetime
    updated_at: datetime

    @field_serializer("id")
    def serialize_id(self, v):
        return str(v)

    @field_serializer("truck_owner_id")
    def serialize_truck_owner_id(self, v):
        return str(v)

    class Config:
        from_attributes = True


class PreloadedMaterialBase(BaseModel):
    material_type: str
    quantity: Decimal
    unit: str
    destination: Optional[str] = None
    price: Decimal
    description: Optional[str] = None

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v


class PreloadedMaterialCreate(PreloadedMaterialBase):
    pass


class PreloadedMaterialUpdate(BaseModel):
    material_type: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    destination: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    status: Optional[PreloadedMaterialStatus] = None

    @validator('quantity')
    def validate_quantity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v


class PreloadedMaterialResponse(PreloadedMaterialBase):
    id: str
    truck_id: str
    status: PreloadedMaterialStatus
    created_at: datetime

    @field_serializer("id")
    def serialize_id(self, v):
        return str(v)

    @field_serializer("truck_id")
    def serialize_truck_id(self, v):
        return str(v)

    class Config:
        from_attributes = True


class TruckWithMaterialsResponse(TruckResponse):
    preloaded_materials: List[PreloadedMaterialResponse] = []

    class Config:
        from_attributes = True 