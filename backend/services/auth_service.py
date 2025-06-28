from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.core.security import get_password_hash, authenticate_user, create_access_token
from backend.core.exceptions import UserNotFoundException, ValidationException
from backend.models.user import User, UserRole
from backend.models.profile import TruckOwnerProfile
from backend.models.profile import CustomerProfile
from backend.schemas.user import UserCreate, UserLogin, TokenResponse, TruckOwnerProfileCreate, CustomerProfileCreate
from backend.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: dict) -> User:
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            (User.email == user_data.get('email')) | 
            (User.phone == user_data.get('phone'))
        ).first()
        
        if existing_user:
            raise ValidationException("User with this email or phone already exists")

        try:
            # Create the user from the dictionary
            user = User(
                id=user_data.get('id'),
                email=user_data.get('email'),
                phone=user_data.get('phone'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role'),
                is_verified=False,
                is_active=True
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"User registration failed: {str(e)}")

    def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate and login user"""
        user = authenticate_user(self.db, login_data.email, login_data.password)
        
        if not user:
            raise ValidationException("Invalid email or password")

        if not user.is_active:
            raise ValidationException("User account is deactivated")

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value},
            expires_delta=access_token_expires
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=str(user.id),
            role=user.role
        )

    def create_truck_owner_profile(self, user_id: str, profile_data: TruckOwnerProfileCreate) -> TruckOwnerProfile:
        """Create truck owner profile"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException(user_id)

        if user.role != UserRole.TRUCK_OWNER:
            raise ValidationException("User is not a truck owner")

        # Check if profile already exists
        existing_profile = self.db.query(TruckOwnerProfile).filter(
            TruckOwnerProfile.user_id == user_id
        ).first()
        
        if existing_profile:
            raise ValidationException("Truck owner profile already exists")

        profile = TruckOwnerProfile(
            user_id=user_id,
            **profile_data.dict(exclude_unset=True)
        )

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def create_customer_profile(self, user_id: str, profile_data: CustomerProfileCreate) -> CustomerProfile:
        """Create customer profile"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException(user_id)

        if user.role != UserRole.CUSTOMER:
            raise ValidationException("User is not a customer")

        # Check if profile already exists
        existing_profile = self.db.query(CustomerProfile).filter(
            CustomerProfile.user_id == user_id
        ).first()
        
        if existing_profile:
            raise ValidationException("Customer profile already exists")

        profile = CustomerProfile(
            user_id=user_id,
            **profile_data.dict(exclude_unset=True)
        )

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def verify_user(self, user_id: str) -> User:
        """Verify user account"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException(user_id)

        user.is_verified = True
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException(user_id)

        # Verify current password
        if not authenticate_user(self.db, user.email, current_password):
            raise ValidationException("Current password is incorrect")

        # Update password
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        return True 