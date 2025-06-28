from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    phone: str
    first_name: str
    last_name: str
    role: UserRole

    @validator('phone')
    def validate_phone(cls, v):
        if not v.isdigit() or len(v) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return v


class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
        



class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    profile_image_url: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and (not v.isdigit() or len(v) < 10):
            raise ValueError('Phone number must be at least 10 digits')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    role: UserRole


class UserResponse(BaseModel):
    id: str
    email: str
    phone: str
    first_name: str
    last_name: str
    role: UserRole
    profile_image_url: Optional[str]
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TruckOwnerProfileCreate(BaseModel):
    company_name: Optional[str] = None
    business_license: Optional[str] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    bank_details: Optional[dict] = None


class TruckOwnerProfileResponse(BaseModel):
    id: str
    user_id: str
    company_name: Optional[str]
    business_license: Optional[str]
    gst_number: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    bank_details: Optional[dict]
    rating: float
    total_trips: int
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerProfileCreate(BaseModel):
    company_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None


class CustomerProfileResponse(BaseModel):
    id: str
    user_id: str
    company_name: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    rating: float
    total_bookings: int
    created_at: datetime

    class Config:
        from_attributes = True 