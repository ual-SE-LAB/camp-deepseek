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
    - Admin: Can create camper without linking to parent (must link separately)
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
    db.flush()  # Get the camper ID without committing
    
    # Add emergency contacts
    for contact_data in camper_data.emergency_contacts:
        db_contact = models.EmergencyContact(
            camper_id=db_camper.id,
            full_name=contact_data.full_name,
            relationship=contact_data.relationship,
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
    """
    Get a specific camper by ID.
    - Admin: Can access any camper
    - Parent: Can only access their own campers
    """
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    # Check permissions
    if current_user.role != "admin":
        # Verify camper belongs to this parent
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
    """
    Update a camper's information.
    - Admin: Can update any camper
    - Parent: Can only update their own campers
    """
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    # Check permissions
    if current_user.role != "admin":
        # Verify camper belongs to this parent
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update camper fields
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
    """
    Delete a camper.
    - Admin: Can permanently delete any camper
    - Parent: Can only soft-delete (deactivate) their own campers
    """
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    if current_user.role == "admin":
        # Admin can permanently delete
        db.delete(camper)
        db.commit()
        return {"message": "Camper permanently deleted"}
    else:
        # Parents can only soft delete
        # Verify camper belongs to this parent
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
    """
    Add an emergency contact to a camper.
    - Admin: Can add to any camper
    - Parent: Can only add to their own campers
    """
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    # Check permissions
    if current_user.role != "admin":
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # If this contact is primary, unset any existing primary contacts
    if contact_data.is_primary:
        db.query(models.EmergencyContact).filter(
            models.EmergencyContact.camper_id == camper_id,
            models.EmergencyContact.is_primary == True
        ).update({"is_primary": False})
    
    # Create new contact
    db_contact = models.EmergencyContact(
        camper_id=camper_id,
        **contact_data.dict()
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
    """
    Update an emergency contact.
    - Admin: Can update any contact
    - Parent: Can only update contacts for their own campers
    """
    contact = db.query(models.EmergencyContact).filter(
        models.EmergencyContact.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Emergency contact not found")
    
    # Check permissions
    if current_user.role != "admin":
        # Verify camper belongs to this parent
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == contact.camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # If this contact is being set as primary, unset other primary contacts
    if contact_data.is_primary and not contact.is_primary:
        db.query(models.EmergencyContact).filter(
            models.EmergencyContact.camper_id == contact.camper_id,
            models.EmergencyContact.is_primary == True
        ).update({"is_primary": False})
    
    # Update contact
    for key, value in contact_data.dict().items():
        setattr(contact, key, value)
    
    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/emergency-contacts/{contact_id}")
def delete_emergency_contact(
    contact_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an emergency contact.
    - Admin: Can delete any contact
    - Parent: Can only delete contacts for their own campers
    """
    contact = db.query(models.EmergencyContact).filter(
        models.EmergencyContact.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Emergency contact not found")
    
    # Check permissions
    if current_user.role != "admin":
        # Verify camper belongs to this parent
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == contact.camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Don't allow deleting the only primary contact
    if contact.is_primary:
        primary_count = db.query(models.EmergencyContact).filter(
            models.EmergencyContact.camper_id == contact.camper_id,
            models.EmergencyContact.is_primary == True
        ).count()
        
        if primary_count <= 1:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete the only primary emergency contact"
            )
    
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
    """
    Link a camper to a parent (Admin only).
    """
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
            is_primary=is_primary
        )
    )
    db.commit()
    
    return {"message": "Camper linked to parent successfully"}

@router.delete("/{camper_id}/unlink-parent/{parent_id}")
def unlink_camper_from_parent(
    camper_id: int,
    parent_id: int,
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """
    Unlink a camper from a parent (Admin only).
    """
    # Check if link exists
    existing = db.execute(
        models.parent_camper.select().where(
            models.parent_camper.c.parent_id == parent_id,
            models.parent_camper.c.camper_id == camper_id
        )
    ).first()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Delete link
    db.execute(
        models.parent_camper.delete().where(
            models.parent_camper.c.parent_id == parent_id,
            models.parent_camper.c.camper_id == camper_id
        )
    )
    db.commit()
    
    return {"message": "Camper unlinked from parent successfully"}

@router.get("/{camper_id}/parents", response_model=List[schemas.UserResponse])
def get_camper_parents(
    camper_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all parents linked to a camper.
    - Admin: Can access any camper
    - Parent: Can only access their own campers
    """
    camper = db.query(models.Camper).filter(models.Camper.id == camper_id).first()
    if not camper:
        raise HTTPException(status_code=404, detail="Camper not found")
    
    # Check permissions
    if current_user.role != "admin":
        is_my_camper = db.query(models.parent_camper).filter(
            models.parent_camper.c.parent_id == current_user.id,
            models.parent_camper.c.camper_id == camper_id
        ).first()
        if not is_my_camper:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return camper.parents