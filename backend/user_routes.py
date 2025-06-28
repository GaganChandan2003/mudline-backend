import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from typing import List, Optional

from backend.database import get_db
from backend.services.auth_service import AuthService
from backend.models.user import User, UserRole, TruckOwnerProfile, CustomerProfile
from backend.schemas.user import (
    UserCreate, UserResponse, UserLogin, TokenResponse, UserUpdate,
    TruckOwnerProfileCreate, TruckOwnerProfileResponse, CustomerProfileCreate, CustomerProfileResponse
)
from backend.core.security import get_current_active_user, get_password_hash
from backend.core.exceptions import UserNotFoundException, ValidationException

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        print(f"Received registration data: {user_data}")  # Debug log
        
        # Create user data dictionary with hashed password
        user_dict = user_data.dict()
        print(f"User dict before pop: {user_dict}")  # Debug log
        
        if 'password' not in user_dict:
            print("Password field is missing from user_dict")  # Debug log
            print(f"Available keys: {user_dict.keys()}")  # Debug log
            raise ValueError("Password field is required")
            
        password = user_dict.pop('password')
        print(f"Password extracted: {password}")  # Debug log
        
        # Add required fields
        user_dict['password_hash'] = get_password_hash(password)
        user_dict['id'] = str(uuid.uuid4())  # Generate new UUID
        
        print(f"Final user dict: {user_dict}")  # Debug log
        
        # Create the user using the service
        service = AuthService(db)
        user = service.register_user(user_dict)
        db.commit()
        
        # Convert user to response model
        return UserResponse.from_orm(user)
    except ValidationError as e:
        db.rollback()
        print(f"Validation error: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {str(e)}")  # Debug log
        import traceback
        traceback.print_exc()  # Print full traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    service = AuthService(db)
    token = service.login_user(login_data)
    return token


@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_users_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = AuthService(db)
    updated_user = service.update_user(current_user.id, user_update)
    return updated_user


@router.post("/me/truck_owner_profile", response_model=TruckOwnerProfileResponse, status_code=status.HTTP_201_CREATED)
def create_my_truck_owner_profile(
    profile_data: TruckOwnerProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.TRUCK_OWNER:
        raise HTTPException(status_code=403, detail="Only truck owners can create this profile")
    service = AuthService(db)
    profile = service.create_truck_owner_profile(current_user.id, profile_data)
    return profile


@router.post("/me/customer_profile", response_model=CustomerProfileResponse, status_code=status.HTTP_201_CREATED)
def create_my_customer_profile(
    profile_data: CustomerProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can create this profile")
    service = AuthService(db)
    profile = service.create_customer_profile(current_user.id, profile_data)
    return profile


@router.get("/me/truck_owner_profile", response_model=TruckOwnerProfileResponse)
def get_my_truck_owner_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.TRUCK_OWNER:
        raise HTTPException(status_code=403, detail="Only truck owners have this profile")
    service = AuthService(db)
    profile = service.get_truck_owner_profile(current_user.id)
    if not profile:
        raise UserNotFoundException("Truck owner profile not found")
    return profile


@router.get("/me/customer_profile", response_model=CustomerProfileResponse)
def get_my_customer_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers have this profile")
    service = AuthService(db)
    profile = service.get_customer_profile(current_user.id)
    if not profile:
        raise UserNotFoundException("Customer profile not found")
    return profile 