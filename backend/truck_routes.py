from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.schemas import TruckCreate, TruckResponse, TruckUpdate
from backend.core.security import get_current_active_user
from backend.models.user import User, UserRole
from backend.models.truck import Truck, TruckStatus
from backend.services.booking_service import BookingService

router = APIRouter(prefix="/api/v1/trucks", tags=["Trucks"])

# GET /trucks - List all trucks (Admin only)
@router.get("/", response_model=List[TruckResponse])
def get_trucks(
    status: Optional[TruckStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all trucks (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can view all trucks")
    
    query = db.query(Truck)
    if status:
        query = query.filter(Truck.status == status)
    
    trucks = query.all()
    return trucks

# GET /trucks/:id - Get truck details
@router.get("/{truck_id}", response_model=TruckResponse)
def get_truck(
    truck_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get truck details"""
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    
    # Check if user is authorized to view this truck
    if truck.truck_owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to view this truck")
    
    return truck

# GET /truck-owners/:id/trucks - List all trucks under an owner
@router.get("/owner/{truck_owner_id}", response_model=List[TruckResponse])
def get_truck_owner_trucks(
    truck_owner_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all trucks under a truck owner"""
    # Check if user is authorized to view these trucks
    if truck_owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to view these trucks")
    
    service = BookingService(db)
    trucks = service.get_truck_owner_trucks(truck_owner_id)
    return trucks

# POST /trucks - Create new truck (Truck Owner only)
@router.post("/", response_model=TruckResponse, status_code=status.HTTP_201_CREATED)
def create_truck(
    truck_data: TruckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new truck (Truck Owner only)"""
    if current_user.role != UserRole.TRUCK_OWNER:
        raise HTTPException(status_code=403, detail="Only truck owners can create trucks")
    
    # Set the truck owner to the current user
    truck_data_dict = truck_data.dict()
    truck_data_dict["truck_owner_id"] = current_user.id
    
    truck = Truck(**truck_data_dict)
    db.add(truck)
    db.commit()
    db.refresh(truck)
    return truck

# PUT /trucks/:id - Update truck
@router.put("/{truck_id}", response_model=TruckResponse)
def update_truck(
    truck_id: str,
    truck_data: TruckUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update truck"""
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    
    # Check if user is authorized to update this truck
    if truck.truck_owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to update this truck")
    
    for field, value in truck_data.dict(exclude_unset=True).items():
        setattr(truck, field, value)
    
    db.commit()
    db.refresh(truck)
    return truck

# DELETE /trucks/:id - Delete truck
@router.delete("/{truck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_truck(
    truck_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete truck"""
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    
    # Check if user is authorized to delete this truck
    if truck.truck_owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this truck")
    
    db.delete(truck)
    db.commit()
    return None 