from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
import auth

router = APIRouter(prefix="/parents", tags=["parents"])

@router.get("/me/campers", response_model=List[schemas.CamperResponse])
def get_my_campers(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Parent: Get all campers linked to my account"""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can access this")
    
    return current_user.campers

@router.post("/me/campers", response_model=schemas.CamperResponse)
def add_camper(
    camper_data: schemas.CamperCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Parent: Add a new camper and link to my account"""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can add campers")
    
    # Create camper
    db_camper = models.Camper(**camper_data.dict(exclude={'emergency_contacts'}))
    db.add(db_camper)
    db.flush()
    
    # Add emergency contacts
    for contact_data in camper_data.emergency_contacts:
        db_contact = models.EmergencyContact(**contact_data.dict(), camper_id=db_camper.id)
        db.add(db_contact)
    
    # Link parent to camper
    db.execute(
        models.parent_camper.insert().values(
            parent_id=current_user.id,
            camper_id=db_camper.id,
            relationship="parent",
            is_primary=True
        )
    )
    
    db.commit()
    db.refresh(db_camper)
    return db_camper

@router.put("/me/campers/{camper_id}", response_model=schemas.CamperResponse)
def update_my_camper(
    camper_id: int,
    camper_data: schemas.CamperUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Parent: Update my camper's information"""
    # Verify camper belongs to parent
    camper = db.query(models.Camper).join(
        models.parent_camper
    ).filter(
        models.Camper.id == camper_id,
        models.parent_camper.c.parent_id == current_user.id
    ).first()
    
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found or not linked to you")
    
    # Update camper
    for key, value in camper_data.dict(exclude_unset=True).items():
        setattr(camper, key, value)
    
    db.commit()
    db.refresh(camper)
    return camper

@router.delete("/me/campers/{camper_id}")
def delete_my_camper(
    camper_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Parent: Remove my camper (soft delete by setting inactive)"""
    # Verify camper belongs to parent
    camper = db.query(models.Camper).join(
        models.parent_camper
    ).filter(
        models.Camper.id == camper_id,
        models.parent_camper.c.parent_id == current_user.id
    ).first()
    
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found or not linked to you")
    
    # Soft delete
    camper.is_active = False
    db.commit()
    
    return {"message": "Camper removed successfully"}