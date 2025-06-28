from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from backend.database import get_db
from backend.schemas.material import (
    MaterialTypeCreate, MaterialTypeResponse, MaterialTypeUpdate,
    MaterialSourceCreate, MaterialSourceResponse, MaterialSourceUpdate,
    MaterialCreate, MaterialResponse, MaterialUpdate
)
from backend.core.security import get_current_active_user
from backend.models.user import User, UserRole
from backend.models.material import MaterialTypeModel, MaterialSource, Material
from backend.models.material import MaterialType
from backend.utils.uuid_to_str import uuid_to_str

router = APIRouter(prefix="/api/v1/materials", tags=["Materials"])

# Material Types Routes
@router.get("/types", response_model=List[MaterialTypeResponse])
def get_material_types(db: Session = Depends(get_db)):
    """Get all material types (Public)"""
    material_types = db.query(MaterialTypeModel).all()
    return [MaterialTypeResponse.model_validate(uuid_to_str(mt)) for mt in material_types]


@router.get("/types/{material_type_id}", response_model=MaterialTypeResponse)
def get_material_type(material_type_id: str, db: Session = Depends(get_db)):
    """Get a specific material type by ID (Public)"""
    material_type = db.query(MaterialTypeModel).filter(MaterialTypeModel.id == material_type_id).first()
    if not material_type:
        raise HTTPException(status_code=404, detail="Material type not found")
    return MaterialTypeResponse.model_validate(uuid_to_str(material_type))


@router.post("/types", response_model=MaterialTypeResponse)
def create_material_type(
    material_type: MaterialTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new material type (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can create material types")
    
    # Check if material type already exists
    existing = db.query(MaterialTypeModel).filter(MaterialTypeModel.type == material_type.type).first()
    if existing:
        raise HTTPException(status_code=400, detail="Material type already exists")
    
    db_material_type = MaterialTypeModel(**material_type.model_dump())
    db.add(db_material_type)
    db.commit()
    db.refresh(db_material_type)
    return MaterialTypeResponse.model_validate(uuid_to_str(db_material_type))


@router.put("/types/{material_type_id}", response_model=MaterialTypeResponse)
def update_material_type(
    material_type_id: str,
    material_type: MaterialTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a material type (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can update material types")
    
    db_material_type = db.query(MaterialTypeModel).filter(MaterialTypeModel.id == material_type_id).first()
    if not db_material_type:
        raise HTTPException(status_code=404, detail="Material type not found")
    
    for field, value in material_type.model_dump(exclude_unset=True).items():
        setattr(db_material_type, field, value)
    
    db.commit()
    db.refresh(db_material_type)
    return MaterialTypeResponse.model_validate(uuid_to_str(db_material_type))


# Material Sources Routes
@router.get("/sources", response_model=List[MaterialSourceResponse])
def get_material_sources(
    material_type: Optional[MaterialType] = None,
    db: Session = Depends(get_db)
):
    """Get all material sources with optional type filtering (Public)"""
    query = db.query(MaterialSource).options(joinedload(MaterialSource.material_type))
    
    if material_type:
        query = query.join(MaterialTypeModel).filter(MaterialTypeModel.type == material_type)
    
    material_sources = query.all()
    return [MaterialSourceResponse.model_validate(uuid_to_str(ms)) for ms in material_sources]


@router.get("/sources/{source_id}", response_model=MaterialSourceResponse)
def get_material_source(source_id: str, db: Session = Depends(get_db)):
    """Get a specific material source by ID (Public)"""
    material_source = db.query(MaterialSource).options(joinedload(MaterialSource.material_type)).filter(MaterialSource.id == source_id).first()
    if not material_source:
        raise HTTPException(status_code=404, detail="Material source not found")
    return MaterialSourceResponse.model_validate(uuid_to_str(material_source))


@router.post("/sources", response_model=MaterialSourceResponse)
def create_material_source(
    material_source: MaterialSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new material source (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can create material sources")
    
    # Verify material type exists
    material_type = db.query(MaterialTypeModel).filter(MaterialTypeModel.id == material_source.material_type_id).first()
    if not material_type:
        raise HTTPException(status_code=404, detail="Material type not found")
    
    db_material_source = MaterialSource(**material_source.model_dump())
    db.add(db_material_source)
    db.commit()
    db.refresh(db_material_source)
    return MaterialSourceResponse.model_validate(uuid_to_str(db_material_source))


@router.put("/sources/{source_id}", response_model=MaterialSourceResponse)
def update_material_source(
    source_id: str,
    material_source: MaterialSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a material source (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can update material sources")
    
    db_material_source = db.query(MaterialSource).filter(MaterialSource.id == source_id).first()
    if not db_material_source:
        raise HTTPException(status_code=404, detail="Material source not found")
    
    for field, value in material_source.model_dump(exclude_unset=True).items():
        setattr(db_material_source, field, value)
    
    db.commit()
    db.refresh(db_material_source)
    return MaterialSourceResponse.model_validate(uuid_to_str(db_material_source))


# Legacy Materials Routes (for backward compatibility)
@router.get("/", response_model=List[MaterialResponse])
def get_materials(db: Session = Depends(get_db)):
    """Get all materials (Public) - Legacy endpoint"""
    materials = db.query(Material).all()
    return [MaterialResponse.model_validate(uuid_to_str(m)) for m in materials]


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(material_id: str, db: Session = Depends(get_db)):
    """Get a specific material by ID (Public) - Legacy endpoint"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return MaterialResponse.model_validate(uuid_to_str(material))


@router.post("/", response_model=MaterialResponse)
def create_material(
    material: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new material (Admin only) - Legacy endpoint"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can create materials")
    
    # Verify material source exists
    material_source = db.query(MaterialSource).filter(MaterialSource.id == material.material_source_id).first()
    if not material_source:
        raise HTTPException(status_code=404, detail="Material source not found")
    
    db_material = Material(**material.model_dump())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return MaterialResponse.model_validate(uuid_to_str(db_material))


@router.put("/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: str,
    material: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a material (Admin only) - Legacy endpoint"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can update materials")
    
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    for field, value in material.model_dump(exclude_unset=True).items():
        setattr(db_material, field, value)
    
    db.commit()
    db.refresh(db_material)
    return MaterialResponse.model_validate(uuid_to_str(db_material))

# DELETE /materials/:id - Delete material (Admin only)
@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete material (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can delete materials")
    
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    db.delete(material)
    db.commit()
    return None 