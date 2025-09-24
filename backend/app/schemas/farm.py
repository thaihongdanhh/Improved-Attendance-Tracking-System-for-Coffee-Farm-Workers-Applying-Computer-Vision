from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class Coordinates(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Field(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    area: Optional[float] = None  # hectares

class FarmBase(BaseModel):
    name: str
    location: str
    plus_code: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    area_hectares: Optional[float] = None
    elevation: Optional[int] = None  # meters
    coffee_varieties: Optional[List[str]] = []
    established_year: Optional[int] = None
    owner: Optional[str] = None
    contact: Optional[str] = None
    fields: Optional[List[Field]] = []

class FarmCreate(FarmBase):
    pass

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    plus_code: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    area_hectares: Optional[float] = None
    elevation: Optional[int] = None
    coffee_varieties: Optional[List[str]] = None
    established_year: Optional[int] = None
    owner: Optional[str] = None
    contact: Optional[str] = None
    fields: Optional[List[Field]] = None

class Farm(FarmBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True