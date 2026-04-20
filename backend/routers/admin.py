from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
import auth

router = APIRouter(prefix="/admin", tags=["admin"])

# Parent Management
@router.get("/parents", response_model=List[schemas.UserResponse])
def get_all_parents(
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get all parents"""
    parents = db.query(models.User).filter(models.User.role == "parent").all()
    return parents

@router.post("/parents", response_model=schemas.UserResponse)
def create_parent(
    parent_data: schemas.UserCreate,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Create a new parent account"""
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.email == parent_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new parent
    hashed_password = auth.get_password_hash(parent_data.password)
    db_user = models.User(
        email=parent_data.email,
        hashed_password=hashed_password,
        full_name=parent_data.full_name,
        phone_number=parent_data.phone_number,
        role="parent"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/parents/{parent_id}", response_model=schemas.UserResponse)
def update_parent(
    parent_id: int,
    parent_data: schemas.UserBase,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Update parent information"""
    parent = db.query(models.User).filter(
        models.User.id == parent_id,
        models.User.role == "parent"
    ).first()
    
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    
    for key, value in parent_data.dict(exclude_unset=True).items():
        setattr(parent, key, value)
    
    db.commit()
    db.refresh(parent)
    return parent

@router.delete("/parents/{parent_id}")
def delete_parent(
    parent_id: int,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Delete a parent"""
    parent = db.query(models.User).filter(
        models.User.id == parent_id,
        models.User.role == "parent"
    ).first()
    
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    
    db.delete(parent)
    db.commit()
    
    return {"message": "Parent deleted successfully"}

# Camper Management (Admin)
@router.get("/campers", response_model=List[schemas.CamperResponse])
def get_all_campers(
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get all campers"""
    campers = db.query(models.Camper).all()
    return campers

@router.post("/campers", response_model=schemas.CamperResponse)
def create_camper(
    camper_data: schemas.CamperCreate,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Create a new camper and link to a parent"""
    # Create camper
    db_camper = models.Camper(**camper_data.dict(exclude={'emergency_contacts'}))
    db.add(db_camper)
    db.flush()
    
    # Add emergency contacts
    for contact_data in camper_data.emergency_contacts:
        db_contact = models.EmergencyContact(**contact_data.dict(), camper_id=db_camper.id)
        db.add(db_contact)
    
    db.commit()
    db.refresh(db_camper)
    return db_camper

@router.put("/campers/{camper_id}", response_model=schemas.CamperResponse)
def update_camper(
    camper_id: int,
    camper_data: schemas.CamperUpdate,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Update any camper's information"""
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    for key, value in camper_data.dict(exclude_unset=True).items():
        setattr(camper, key, value)
    
    db.commit()
    db.refresh(camper)
    return camper

@router.delete("/campers/{camper_id}")
def delete_camper(
    camper_id: int,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Permanently delete a camper"""
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    db.delete(camper)
    db.commit()
    
    return {"message": "Camper deleted successfully"}

@router.post("/campers/{camper_id}/link-parent/{parent_id}")
def link_camper_to_parent(
    camper_id: int,
    parent_id: int,
    relationship: str = "parent",
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Link a camper to a parent"""
    # Verify camper exists
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    # Verify parent exists
    parent = db.query(models.User).filter(
        models.User.id == parent_id,
        models.User.role == "parent"
    ).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    
    # Check if link already exists
    existing = db.execute(
        models.parent_camper.select().where(
            models.parent_camper.c.parent_id == parent_id,
            models.parent_camper.c.camper_id == camper_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Link already exists")
    
    # Create link
    db.execute(
        models.parent_camper.insert().values(
            parent_id=parent_id,
            camper_id=camper_id,
            relationship=relationship,
            is_primary=False
        )
    )
    db.commit()
    
    return {"message": "Camper linked to parent successfully"}