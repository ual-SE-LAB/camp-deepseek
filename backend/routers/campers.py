from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
import auth

router = APIRouter(prefix="/campers", tags=["campers"])

@router.get("/", response_model=List[schemas.CamperResponse])
def get_all_campers(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all campers with pagination.
    - Admin: Can see all campers
    - Parent: Can only see their own campers
    """
    if current_user.role == "admin":
        campers = db.query(models.Camper).offset(skip).limit(limit).all()
    else:
        # Parents can only see their own campers
        campers = current_user.campers
    return campers

@router.post("/", response_model=schemas.CamperResponse)
def create_camper(
    camper_data: schemas.CamperCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new camper.
    - Admin: Can create camper without linking to parent
    - Parent: Creates camper and automatically links to themselves
    """
    # Validate emergency contacts
    if not camper_data.emergency_contacts:
        raise HTTPException(status_code=400, detail="At least one emergency contact is required")
    
    primary_count = sum(1 for contact in camper_data.emergency_contacts if contact.is_primary)
    if primary_count != 1:
        raise HTTPException(status_code=400, detail="Exactly one primary emergency contact is required")
    
    # Create camper
    db_camper = models.Camper(
        first_name=camper_data.first_name,
        last_name=camper_data.last_name,
        date_of_birth=camper_data.date_of_birth,
        gender=camper_data.gender,
        allergies=camper_data.allergies,
        medical_conditions=camper_data.medical_conditions,
        medications=camper_data.medications,
        doctor_name=camper_data.doctor_name,
        doctor_phone=camper_data.doctor_phone,
        insurance_provider=camper_data.insurance_provider,
        insurance_policy_number=camper_data.insurance_policy_number,
        special_needs=camper_data.special_needs,
        notes=camper_data.notes
    )
    db.add(db_camper)
    db.flush() 
    
    # Add emergency contacts
    for contact_data in camper_data.emergency_contacts:
        # CHANGE: Mapeo de relationship a contact_relationship
        db_contact = models.EmergencyContact(
            camper_id=db_camper.id,
            full_name=contact_data.full_name,
            contact_relationship=contact_data.relationship,
            phone_number=contact_data.phone_number,
            alternate_phone=contact_data.alternate_phone,
            email=contact_data.email,
            is_primary=contact_data.is_primary
        )
        db.add(db_contact)
    
    # If parent is creating, automatically link them
    if current_user.role == "parent":
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

@router.get("/{camper_id}", response_model=schemas.CamperResponse)
def get_camper(
    camper_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    if current_user.role != "admin":
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return camper

@router.put("/{camper_id}", response_model=schemas.CamperResponse)
def update_camper(
    camper_id: int,
    camper_data: schemas.CamperUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    if current_user.role != "admin":
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    for key, value in camper_data.dict(exclude_unset=True).items():
        setattr(camper, key, value)
    
    db.commit()
    db.refresh(camper)
    return camper

@router.delete("/{camper_id}")
def delete_camper(
    camper_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    if current_user.role == "admin":
        db.delete(camper)
        db.commit()
        return {"message": "Camper permanently deleted"}
    else:
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        camper.is_active = False
        db.commit()
        return {"message": "Camper deactivated successfully"}

@router.post("/{camper_id}/emergency-contacts", response_model=schemas.EmergencyContactResponse)
def add_emergency_contact(
    camper_id: int,
    contact_data: schemas.EmergencyContactCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    if current_user.role != "admin":
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if contact_data.is_primary:
        db.query(models.EmergencyContact).filter(
            models.EmergencyContact.camper_id == camper_id,
            models.EmergencyContact.is_primary == True
        ).update({"is_primary": False})
    
    # CHANGE: Constructor manual para evitar el error de keyword 'relationship'
    db_contact = models.EmergencyContact(
        camper_id=camper_id,
        full_name=contact_data.full_name,
        contact_relationship=contact_data.relationship,
        phone_number=contact_data.phone_number,
        alternate_phone=contact_data.alternate_phone,
        email=contact_data.email,
        is_primary=contact_data.is_primary
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.put("/emergency-contacts/{contact_id}", response_model=schemas.EmergencyContactResponse)
def update_emergency_contact(
    contact_id: int,
    contact_data: schemas.EmergencyContactCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    contact = db.query(models.EmergencyContact).filter(models.EmergencyContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Emergency contact not found")
    
    if current_user.role != "admin":
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == contact.camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if contact_data.is_primary and not contact.is_primary:
        db.query(models.EmergencyContact).filter(
            models.EmergencyContact.camper_id == contact.camper_id,
            models.EmergencyContact.is_primary == True
        ).update({"is_primary": False})
    
    # CHANGE: Mapeo manual de campos para asegurar contact_relationship
    contact.full_name = contact_data.full_name
    contact.contact_relationship = contact_data.relationship
    contact.phone_number = contact_data.phone_number
    contact.alternate_phone = contact_data.alternate_phone
    contact.email = contact_data.email
    contact.is_primary = contact_data.is_primary
    
    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/emergency-contacts/{contact_id}")
def delete_emergency_contact(
    contact_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    contact = db.query(models.EmergencyContact).filter(models.EmergencyContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Emergency contact not found")
    
    if current_user.role != "admin":
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == contact.camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if contact.is_primary:
        primary_count = db.query(models.EmergencyContact).filter(
            models.EmergencyContact.camper_id == contact.camper_id,
            models.EmergencyContact.is_primary == True
        ).count()
        if primary_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the only primary contact")
    
    db.delete(contact)
    db.commit()
    return {"message": "Emergency contact deleted successfully"}

@router.post("/{camper_id}/link-parent/{parent_id}")
def link_camper_to_parent(
    camper_id: int,
    parent_id: int,
    relationship: str = "parent",
    is_primary: bool = False,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    parent = db.query(models.User).filter(models.User.id == parent_id, models.User.role == "parent").first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    
    existing = db.execute(models.parent_camper.select().where(
        models.parent_camper.c.parent_id == parent_id,
        models.parent_camper.c.camper_id == camper_id
    )).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Link already exists")
    
    db.execute(models.parent_camper.insert().values(
        parent_id=parent_id,
        camper_id=camper_id,
        relationship=relationship,
        is_primary=is_primary
    ))
    db.commit()
    return {"message": "Camper linked successfully"}

@router.delete("/{camper_id}/unlink-parent/{parent_id}")
def unlink_camper_from_parent(
    camper_id: int,
    parent_id: int,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    existing = db.execute(models.parent_camper.select().where(
        models.parent_camper.c.parent_id == parent_id,
        models.parent_camper.c.camper_id == camper_id
    )).first()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.execute(models.parent_camper.delete().where(
        models.parent_camper.c.parent_id == parent_id,
        models.parent_camper.c.camper_id == camper_id
    ))
    db.commit()
    return {"message": "Camper unlinked successfully"}

@router.get("/{camper_id}/parents", response_model=List[schemas.UserResponse])
def get_camper_parents(
    camper_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    if current_user.role != "admin":
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return camper.parents