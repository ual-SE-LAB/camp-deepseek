from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Date, Table
from sqlalchemy.orm import relationship as db_relationship  # <-- ALIAS AÑADIDO AQUÍ
from sqlalchemy.sql import func
from database import Base

# Association table for parent-camper relationship
parent_camper = Table(
    'parent_camper',
    Base.metadata,
    Column('parent_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('camper_id', Integer, ForeignKey('campers.id'), primary_key=True),
    Column('relationship', String(50)),
    Column('is_primary', Boolean, default=False),
    Column('created_at', DateTime, server_default=func.now())
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    role = Column(String(20), nullable=False, default="parent")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    campers = db_relationship("Camper", secondary=parent_camper, back_populates="parents")

class Camper(Base):
    __tablename__ = "campers"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20))
    allergies = Column(Text)
    medical_conditions = Column(Text)
    medications = Column(Text)
    doctor_name = Column(String(255))
    doctor_phone = Column(String(20))
    insurance_provider = Column(String(255))
    insurance_policy_number = Column(String(100))
    special_needs = Column(Text)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    parents = db_relationship("User", secondary=parent_camper, back_populates="campers")
    emergency_contacts = db_relationship("EmergencyContact", back_populates="camper", cascade="all, delete-orphan")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    camper_id = Column(Integer, ForeignKey("campers.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(255), nullable=False)
    relationship = Column(String(50), nullable=False)
    phone_number = Column(String(20), nullable=False)
    alternate_phone = Column(String(20))
    email = Column(String(255))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships (usando el alias)
    camper = db_relationship("Camper", back_populates="emergency_contacts")