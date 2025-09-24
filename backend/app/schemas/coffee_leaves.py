from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class DiseaseDetection(BaseModel):
    disease: str
    confidence: float
    severity: str  # low, medium, high
    bbox: Optional[List[int]] = None

class CoffeeLeafAnalysis(BaseModel):
    diseases_detected: List[DiseaseDetection]
    health_score: float
    total_leaves: int
    infected_leaves: int
    recommendations: List[str]

class CoffeeLeafResult(BaseModel):
    id: str
    user_id: Optional[str] = None
    filename: Optional[str] = None
    analysis: CoffeeLeafAnalysis
    image_url: str
    farm_id: Optional[str] = None
    field_id: Optional[str] = None
    notes: Optional[str] = None
    timestamp: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True