from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class FarmerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    farm_id: str
    farm_name: Optional[str] = None
    field_id: Optional[str] = None
    field_name: Optional[str] = None
    section_id: Optional[str] = None
    section_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    farmer_code: Optional[str] = None

class FarmerCreate(FarmerBase):
    pass

class FarmerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    farm_id: Optional[str] = None
    farm_name: Optional[str] = None
    field_id: Optional[str] = None
    field_name: Optional[str] = None

class Farmer(FarmerBase):
    id: str
    face_enrolled: Optional[bool] = Field(default=False, alias="has_face_enrolled")
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    
    @validator('name', pre=True, always=True)
    def name_from_full_name(cls, v, values, **kwargs):
        # If name is not provided but full_name exists in raw data
        if not v and hasattr(values, 'get'):
            return values.get('full_name', v)
        return v
    
    @validator('updated_at', pre=True, always=True)
    def updated_at_from_updatedAt(cls, v, values, **kwargs):
        # Handle different field names for updated_at
        if not v and hasattr(values, 'get'):
            return values.get('updatedAt', v)
        return v

    class Config:
        from_attributes = True
        populate_by_name = True