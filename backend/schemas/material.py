from pydantic import BaseModel, field_serializer, model_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from backend.models.material import MaterialType
import uuid


class MaterialTypeBase(BaseModel):
    type: MaterialType
    description: Optional[str] = None


class MaterialTypeCreate(MaterialTypeBase):
    pass


class MaterialTypeUpdate(BaseModel):
    type: Optional[MaterialType] = None
    description: Optional[str] = None


class MaterialTypeResponse(MaterialTypeBase):
    id: str
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def convert_uuids(cls, data):
        if isinstance(data, dict):
            if isinstance(data.get("id"), uuid.UUID):
                data["id"] = str(data["id"])
        return data

    class Config:
        from_attributes = True


class MaterialSourceBase(BaseModel):
    material_type_id: str
    source_name: str
    location: str
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    price_per_unit: Optional[Decimal] = None
    unit: str = "ton"
    availability_status: str = "available"


class MaterialSourceCreate(MaterialSourceBase):
    pass


class MaterialSourceUpdate(BaseModel):
    material_type_id: Optional[str] = None
    source_name: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    price_per_unit: Optional[Decimal] = None
    unit: Optional[str] = None
    availability_status: Optional[str] = None


class MaterialSourceResponse(MaterialSourceBase):
    id: str
    material_type: MaterialTypeResponse
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def convert_uuids(cls, data):
        if isinstance(data, dict):
            for key in ["id", "material_type_id"]:
                if isinstance(data.get(key), uuid.UUID):
                    data[key] = str(data[key])
            # Also handle nested material_type
            mt = data.get("material_type")
            if mt and isinstance(mt, dict) and isinstance(mt.get("id"), uuid.UUID):
                mt["id"] = str(mt["id"])
        return data

    class Config:
        from_attributes = True


class MaterialBase(BaseModel):
    material_source_id: str


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    material_source_id: Optional[str] = None


class MaterialResponse(MaterialBase):
    id: str
    material_source: MaterialSourceResponse
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def convert_uuids(cls, data):
        if isinstance(data, dict):
            if isinstance(data.get("id"), uuid.UUID):
                data["id"] = str(data["id"])
            if isinstance(data.get("material_source_id"), uuid.UUID):
                data["material_source_id"] = str(data["material_source_id"])
        return data

    class Config:
        from_attributes = True 