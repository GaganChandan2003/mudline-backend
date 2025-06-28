from pydantic import BaseModel, validator, field_serializer
from typing import Optional
from datetime import datetime
from decimal import Decimal


class VehicleTypeBase(BaseModel):
    name: str
    capacity_ton: Decimal

    @validator('capacity_ton')
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError('Capacity must be greater than 0')
        return v


class VehicleTypeCreate(VehicleTypeBase):
    pass


class VehicleTypeUpdate(BaseModel):
    name: Optional[str] = None
    capacity_ton: Optional[Decimal] = None

    @validator('capacity_ton')
    def validate_capacity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Capacity must be greater than 0')
        return v


class VehicleTypeResponse(VehicleTypeBase):
    id: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("id")
    def serialize_id(self, v):
        return str(v)

    class Config:
        from_attributes = True 