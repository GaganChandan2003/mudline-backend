from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas import VehicleTypeCreate, VehicleTypeResponse, VehicleTypeUpdate
from backend.core.security import get_current_active_user
from backend.models.user import User, UserRole
from backend.models.vehicle_type import VehicleType

router = APIRouter(prefix="/api/v1/vehicle-types", tags=["Vehicle Types"])

# GET /vehicle-types - List all vehicle types (Public)
@router.get("/", response_model=List[VehicleTypeResponse])
def get_vehicle_types(
    db: Session = Depends(get_db)
):
    """Get all vehicle types (Public)"""
    vehicle_types = db.query(VehicleType).all()
    return vehicle_types

# GET /vehicle-types/:id - Get vehicle type details (Public)
@router.get("/{vehicle_type_id}", response_model=VehicleTypeResponse)
def get_vehicle_type(
    vehicle_type_id: str,
    db: Session = Depends(get_db)
):
    """Get vehicle type details (Public)"""
    vehicle_type = db.query(VehicleType).filter(VehicleType.id == vehicle_type_id).first()
    if not vehicle_type:
        raise HTTPException(status_code=404, detail="Vehicle type not found")
    return vehicle_type

# POST /vehicle-types - Create new vehicle type (Admin only)
@router.post("/", response_model=VehicleTypeResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle_type(
    vehicle_type_data: VehicleTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new vehicle type (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can create vehicle types")
    
    vehicle_type = VehicleType(**vehicle_type_data.dict())
    db.add(vehicle_type)
    db.commit()
    db.refresh(vehicle_type)
    return vehicle_type

# PUT /vehicle-types/:id - Update vehicle type (Admin only)
@router.put("/{vehicle_type_id}", response_model=VehicleTypeResponse)
def update_vehicle_type(
    vehicle_type_id: str,
    vehicle_type_data: VehicleTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update vehicle type (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can update vehicle types")
    
    vehicle_type = db.query(VehicleType).filter(VehicleType.id == vehicle_type_id).first()
    if not vehicle_type:
        raise HTTPException(status_code=404, detail="Vehicle type not found")
    
    for field, value in vehicle_type_data.dict(exclude_unset=True).items():
        setattr(vehicle_type, field, value)
    
    db.commit()
    db.refresh(vehicle_type)
    return vehicle_type

# DELETE /vehicle-types/:id - Delete vehicle type (Admin only)
@router.delete("/{vehicle_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle_type(
    vehicle_type_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete vehicle type (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can delete vehicle types")
    
    vehicle_type = db.query(VehicleType).filter(VehicleType.id == vehicle_type_id).first()
    if not vehicle_type:
        raise HTTPException(status_code=404, detail="Vehicle type not found")
    
    db.delete(vehicle_type)
    db.commit()
    return None 