from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime
from typing import Optional, List

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "parent"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# Emergency Contact schemas
class EmergencyContactBase(BaseModel):
    full_name: str
    relationship: str
    phone_number: str
    alternate_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_primary: bool = False

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmergencyContactResponse(EmergencyContactBase):
    id: int
    camper_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Camper schemas
class CamperBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    special_needs: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('date_of_birth')
    def validate_age(cls, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age > 18:
            raise ValueError('Camper must be 18 years or younger')
        return v

class CamperCreate(CamperBase):
    emergency_contacts: Optional[List[EmergencyContactCreate]] = []
    
    @validator('emergency_contacts')
    def validate_emergency_contacts(cls, v):
        if not v:
            raise ValueError('At least one emergency contact is required')
        primary_count = sum(1 for contact in v if contact.is_primary)
        if primary_count != 1:
            raise ValueError('Exactly one primary emergency contact is required')
        return v

class CamperUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    special_needs: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class CamperResponse(CamperBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    emergency_contacts: List[EmergencyContactResponse] = []
    parent_ids: List[int] = []
    
    class Config:
        from_attributes = True

# Parent-Camper association
class ParentCamperCreate(BaseModel):
    parent_id: int
    camper_id: int
    relationship: str
    is_primary: bool = False